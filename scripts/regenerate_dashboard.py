#!/usr/bin/env python3
"""regenerate_dashboard.py — cmd_020 Stage 2: dashboard.md / dashboard_supabase_preflight.yaml generator.

Single canonical writer for dashboard.md. Karo and Gunshi must NOT hand-edit
dashboard.md; they update state sources (queue/reports/, queue/tasks/, memory/MEMORY.md)
and this generator reflects them deterministically.

Design reference: docs/dashboard_design_v0.2.md (黒田 audit
kuroda_dashboard_design_v0_2_reaudit_20260511 反映). v0.3 が公開された場合は
Stage 2 中断 + AC 差分照合 → 再開 (= v0_3_stop_and_sync_gate)。

Implementation contract (AC1-7):
  AC1 Supabase REST + ETag cache + diff fetch (anon+RLS)
      `--preflight` writes queue/reports/dashboard_supabase_preflight.yaml.
  AC2 Local file read: queue/tasks/ashigaru*.yaml + queue/reports/*.yaml + git log.
      dashboard.md is EXCLUDED from inputs (= 自己参照防止、黒田 P0 ②).
  AC3 Memory MCP read_graph wrap: memory/MEMORY.md snapshot fallback for timer.
  AC4 Jinja2 template → dashboard.md, generator is sole writer.
      Header carries generated_at / source_commit / stale warning.
      Legacy hand-edited dashboards must be moved to archive/dashboard_legacy_YYYYMMDD.md.
  AC5 Progress formula (fixed evaluation order, see _progress_for_leaf docstring).
      Fallback (黒田 P0 残④):
          shogun_verified=false  -> cap at 75
          evidence incomplete    -> cap at 50
          status=blocked         -> 0
          unknown                -> excluded from aggregation
          stale (mtime > N days) -> 0
          parse_error            -> 0
  AC6 Two-PC SoT: MC primary writer, SC verify-only.
      HEAD/hash 一致 gate + flock generation_lock_file.
  AC7 Tests live in tests/test_regenerate_dashboard.py (SKIP=0 mandatory).
      See AC18 of design v0.2.

Anti-duplication (AC0):
  - dashboard-viewer.py = HTTP markdown viewer (read-only). We are the writer.
  - sync_to_supabase.sh = source_code_cache UPSERT (write-only). Independent.
  - lib/audit_via_supabase.sh = audit pipeline. Independent.

Invocation:
  python3 scripts/regenerate_dashboard.py [--preflight] [--dry-run] [--writer-pc {mainpc,secondpc}]
                                          [--verify] [--output PATH] [--no-supabase]
                                          [--memory-snapshot PATH]

Exit codes:
  0 = success
  1 = lock contention / HEAD mismatch / verify failed
  2 = preflight detected blocking permission denial
  3 = unexpected error
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import jinja2
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUEUE_TASKS_DIR = PROJECT_ROOT / "queue" / "tasks"
QUEUE_REPORTS_DIR = PROJECT_ROOT / "queue" / "reports"
MEMORY_FILE = PROJECT_ROOT / "memory" / "MEMORY.md"
DASHBOARD_FILE = PROJECT_ROOT / "dashboard.md"
ARCHIVE_DIR = PROJECT_ROOT / "archive"
PREFLIGHT_REPORT = QUEUE_REPORTS_DIR / "dashboard_supabase_preflight.yaml"
LOCK_FILE = PROJECT_ROOT / ".dashboard_generation.lock"
CACHE_DIR = Path(os.environ.get("DASHBOARD_CACHE_DIR", str(Path.home() / ".cache" / "dentalbi-dashboard")))

DEFAULT_TABLES: list[dict[str, Any]] = [
    {"name": "development_progress",      "strategy": "full",     "select": "id,phase,status,updated_at"},
    {"name": "legal_sources",             "strategy": "diff",     "select": "id,title,updated_at"},
    {"name": "legal_source_linkages",     "strategy": "diff",     "select": "id,source_id,updated_at"},
    {"name": "inspection_checklists",     "strategy": "diff",     "select": "id,title,updated_at"},
    {"name": "inspection_findings",       "strategy": "full",     "select": "id,checklist_id,severity,status"},
    {"name": "procedure_codes_audit",     "strategy": "full",     "select": "id,code,status"},
    {"name": "project_documents",         "strategy": "metadata", "select": "id,title,version"},
    {"name": "design_decisions",          "strategy": "full",     "select": "id,title,status"},
    {"name": "form_templates",            "strategy": "full",     "select": "id,name"},
]

# Canonical status set (= instructions/common/task_flow.md "assigned/blocked/done/failed"
# 規範 + de-facto audit lifecycle statuses observed in queue/tasks/*.yaml).
# F2 cycle2 fix: kuroda_cmd020_regenerate_dashboard_py_audit_20260511 — 監査待ち系を
# unknown に丸めると dashboard 進捗が実態を落とす。明示段階値を持つ。
STATUS_ENUM = {
    # task_flow.md canonical (4)
    "assigned", "blocked", "done", "failed",
    # de-facto lifecycle (audit / verification waiting)
    "in_progress", "not_started", "pending",
    "drafted_pending_kuroda_pre_audit",
    "ready_for_audit",
    "audit_pending",
    "completed_pending_audit",
    "done_pending_audit",
    "audit_pending_verification",
    "unknown",
}

# Stage-based base score for non-done statuses. 監査待ちは 0% でなく明示段階値
# (= 黒田 cycle2 F2 推奨)。
STATUS_STAGE_PCT: dict[str, float] = {
    "blocked": 0.0,
    "not_started": 0.0,
    "failed": 0.0,
    "pending": 10.0,
    "drafted_pending_kuroda_pre_audit": 15.0,
    "assigned": 25.0,
    "in_progress": 50.0,
    "ready_for_audit": 70.0,
    "audit_pending": 80.0,
    "completed_pending_audit": 85.0,
    "done_pending_audit": 90.0,
    "audit_pending_verification": 95.0,
}

STALE_THRESHOLD_DAYS = 14

# cycle3: 6 Layer (A-F) 構想〜規範 + G 統合 — dashboard_layer_{a-g}_*.md anchor mapping。
# 各 entry は dashboard.md の「6 Layer 構造」section と HTML drill-down accordion に流す。
LAYER_DEFINITIONS: list[dict[str, str]] = [
    {
        "code": "A", "name": "構想層",
        "summary": "5 階層 + 10 柱 + 蜘蛛の糸",
        "doc": "docs/dashboard_layer_a_kousou.md",
        "data_source": "DD-054 anchor / project_documents (Supabase)",
    },
    {
        "code": "B", "name": "Phase 層",
        "summary": "3 区分 (完了 / 進行中 / 未着手)",
        "doc": "docs/dashboard_layer_b_phase.md",
        "data_source": "Supabase development_progress + queue/tasks/*.yaml",
    },
    {
        "code": "C", "name": "機能層",
        "summary": "cmd_004 二大戦線 dossier (会計待ちゼロ + 小児恐竜王国)",
        "doc": "docs/dashboard_layer_c_function.md",
        "data_source": "queue/reports/ + cmd_004 design docs",
    },
    {
        "code": "D", "name": "頭脳層 (蜘蛛の糸)",
        "summary": "法令 8,000+ records + design_decisions",
        "doc": "docs/dashboard_layer_d_zunou.md",
        "data_source": "Supabase legal_sources / linkages / checklists / findings",
    },
    {
        "code": "E", "name": "運用層",
        "summary": "MC/SC pane + systemd timer + 通信規範",
        "doc": "docs/dashboard_layer_e_unyou.md",
        "data_source": "tmux + systemd + CLAUDE.md + auto-git-sync log",
    },
    {
        "code": "F", "name": "規範層",
        "summary": "memory MCP 18 entities + forbidden actions",
        "doc": "docs/dashboard_layer_f_kihan.md",
        "data_source": "memory MCP read_graph / memory/MEMORY.md / instructions/",
    },
    {
        "code": "G", "name": "統合層 (Stage 3-5)",
        "summary": "HTML drill-down + systemd timer + 検証 plan",
        "doc": "docs/dashboard_layer_g_integration_drill_down.md",
        "data_source": "本 generator (regenerate_dashboard.py) + dashboard-viewer.py",
    },
]

# cycle3: 色分け 4 段階 (= dashboard_design_v0.2.md §3.6 retain) — progress %
# tier を emoji + class で表示する。HTML drill-down + 大 progress bar に流す。
PROGRESS_COLOR_TIERS: list[dict[str, Any]] = [
    {"min_pct": 80.0, "emoji": "🟢", "label": "verified", "css_class": "tier-green"},
    {"min_pct": 50.0, "emoji": "🟡", "label": "in_flight", "css_class": "tier-yellow"},
    {"min_pct": 25.0, "emoji": "🟠", "label": "early",     "css_class": "tier-orange"},
    {"min_pct":  0.0, "emoji": "🔴", "label": "stalled",   "css_class": "tier-red"},
]


# cycle4: Layer 子項目 — 各 Layer の sub-item として render する。
# 計画書 v0.2 §4.1 + cycle4 詳細指示書 docs/cmd_020_cycle4_drill_down_detail.md §2/§4。
# 各 child は機械 evidence (= commit / test / audit / shogun_verified / 参照) を持つ。
# kind="w9_stage" / "w9_batch" は aggregate_w9_*_progress() の集計値を流用する特殊扱い。
LAYER_CHILDREN: list[dict[str, Any]] = [
    # Layer A 構想層 — 5 階層 + 10 柱
    {"layer": "A", "id": "A-1", "label": "第 0 層 憲法",
     "ref": "DD-010/037/048/054/061", "supabase_table": "design_decisions"},
    {"layer": "A", "id": "A-2", "label": "第 1 層 診療コア",
     "ref": "DD-036 nigo_sheet + 2 号用紙カルテ"},
    {"layer": "A", "id": "A-3", "label": "第 2 層 周辺診療",
     "ref": "予約 + 画像 + 問診 + CRM"},
    {"layer": "A", "id": "A-4", "label": "第 3 層 患者接点",
     "ref": "PWA + AI チャット + 会計"},
    {"layer": "A", "id": "A-5", "label": "第 4 層 AI 統合",
     "ref": "AI 副院長 + 画像 AI"},
    {"layer": "A", "id": "A-6", "label": "第 5 層 事業推進",
     "ref": "AI 副社長"},
    {"layer": "A", "id": "A-7", "label": "10 柱 P1-P10",
     "ref": "1 画像 AI / 2 歯 DB / 3 治療計画 / 4 患者アプリ / 5 AI 副院長 / 6 処置セット / 7 会計 / 8 蜘蛛の糸 / 9 AI 副院長+事務長 / 10 AI 副社長"},
    # Layer B Phase 層 — Supabase development_progress
    {"layer": "B", "id": "B-1", "label": "完了 phase",
     "ref": "Supabase development_progress WHERE status='done'",
     "supabase_table": "development_progress"},
    {"layer": "B", "id": "B-2", "label": "進行中 phase",
     "ref": "Supabase development_progress WHERE status='in_progress'",
     "supabase_table": "development_progress"},
    {"layer": "B", "id": "B-3", "label": "未着手 phase",
     "ref": "Supabase development_progress WHERE status='not_started'",
     "supabase_table": "development_progress"},
    {"layer": "B", "id": "B-4", "label": "各 phase 詳細",
     "ref": "week + phase_code + title + pc"},
    # Layer C 機能層 — cmd_004 二大戦線 (会計待ちゼロ 7 + 小児恐竜王国 3 + 共通基盤 3 + 申し送り 1 = 14)
    {"layer": "C", "id": "C-1", "label": "領収書 PDF + cycle6",
     "design_doc": "docs/cmd004_kartetto_pdf_v0_2_spec.md",
     "audit_id_pattern": "kuroda_receipt", "shogun_target_pattern": "receipt",
     "ref": "queue/tasks/ashigaru6.yaml subtask_cmd004_receipt_cycle6_p1_residual"},
    {"layer": "C", "id": "C-2", "label": "PDF v0.2 hardening + form fix",
     "design_doc": "docs/cmd004_kartetto_pdf_v0_2_spec.md",
     "audit_id_pattern": "kuroda_pdf_v02", "shogun_target_pattern": "pdf_v02",
     "ref": "queue/tasks/ashigaru2.yaml subtask_cmd004_pdf_v02_hardening_and_form_fix"},
    {"layer": "C", "id": "C-3", "label": "AI チャット + 同意",
     "design_doc": "docs/cmd004_ai_chat_spec.md",
     "audit_id_pattern": "kuroda_aichat", "shogun_target_pattern": "aichat",
     "ref": "queue/tasks/ashigaru5.yaml subtask_cmd004_aichat_consent_impl"},
    {"layer": "C", "id": "C-4", "label": "QR kanban impl",
     "design_doc": "docs/cmd004_qr_kanban_spec.md",
     "audit_id_pattern": "kuroda_cmd004_qr_kanban", "shogun_target_pattern": "qr_kanban",
     "ref": "queue/tasks/ashigaru3.yaml subtask_cmd004_qr_kanban_impl"},
    {"layer": "C", "id": "C-5", "label": "保護者同意 + dinosaur 連動",
     "design_doc": "docs/cmd004_dinosaur_100enemies_spec.md",
     "audit_id_pattern": "kuroda_cmd004_individual_audit_dinosaur_100enemies",
     "shogun_target_pattern": "dinosaur"},
    {"layer": "C", "id": "C-6", "label": "handover_notes_anon + /api/handover",
     "ref": "DentalBI 本体既装備 + Supabase handover_notes_anon table",
     "supabase_table": "handover_notes_anon"},
    {"layer": "C", "id": "C-7", "label": "engagement analytics dashboard",
     "design_doc": "docs/cmd004_engagement_analytics_design.md",
     "audit_id_pattern": "kuroda_cmd004_individual_audit_engagement_analytics",
     "shogun_target_pattern": "engagement_analytics"},
    {"layer": "C", "id": "C-8", "label": "100 敵 spec + 実装",
     "design_doc": "docs/cmd004_dinosaur_100enemies_spec.md",
     "audit_id_pattern": "kuroda_cmd004_individual_audit_dinosaur_100enemies",
     "shogun_target_pattern": "dinosaur"},
    {"layer": "C", "id": "C-9", "label": "PWA 実装",
     "design_doc": "docs/cmd004_patient_app_pwa_design.md",
     "audit_id_pattern": "kuroda_cmd004_individual_audit_patient_app_pwa",
     "shogun_target_pattern": "patient_app_pwa"},
    {"layer": "C", "id": "C-10", "label": "push_vapid management",
     "design_doc": "docs/cmd004_push_vapid_management.md",
     "audit_id_pattern": "kuroda_cmd004_push_vapid", "shogun_target_pattern": "push_vapid",
     "ref": "queue/reports/ashigaru3_cmd004_push_vapid_*.yaml"},
    {"layer": "C", "id": "C-11", "label": "notification facade",
     "design_doc": "docs/cmd004_notification_facade_design.md",
     "ref": "queue/reports/ashigaru3_cmd004_notification_facade_*.yaml"},
    {"layer": "C", "id": "C-12", "label": "observability",
     "design_doc": "docs/cmd004_observability_design.md",
     "ref": "queue/reports/ashigaru3_cmd004_observability_*.yaml"},
    {"layer": "C", "id": "C-13", "label": "security hardening",
     "design_doc": "docs/cmd004_security_hardening_design.md",
     "ref": "queue/reports/ashigaru3_cmd004_security_hardening_*.yaml"},
    {"layer": "C", "id": "C-14", "label": "申し送りエンジン (touch panel)",
     "design_doc": "docs/cmd004_moushi_engine_stage1_design.md",
     "audit_id_pattern": "kuroda_moushi", "shogun_target_pattern": "moushi",
     "ref": "Stage 1 完遂 + Stage 2 blocked (直政 anti-dup fail)"},
    # Layer C W9 蜘蛛の糸 算定チェック — aggregate (= aggregate_w9_*_progress 流用)
    # cycle11: shogun_target_pattern 追加 — 信長殿 verify ledger entries の target
    # 文字列と一致させ、shogun_verified=true → pct bump (= compute_child_machine_state).
    {"layer": "C", "id": "C-15-A", "label": "W9 Stage A foundation 9 件",
     "kind": "w9_stage", "stage": "A",
     "shogun_target_pattern": "stage_a_foundation",
     "ref": "queue/manifests/w9_design_tasks_169.yaml Stage A"},
    {"layer": "C", "id": "C-15-B1", "label": "W9 batch1 算定チェック 42",
     "kind": "w9_batch", "batch": "1",
     "shogun_target_pattern": "stage_b_batch1",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=1]"},
    {"layer": "C", "id": "C-15-B2", "label": "W9 batch2 ui_logic 28",
     "kind": "w9_batch", "batch": "2",
     "shogun_target_pattern": "stage_b_batch2",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=2]"},
    {"layer": "C", "id": "C-15-B3", "label": "W9 batch3 check_logic 26",
     "kind": "w9_batch", "batch": "3",
     "shogun_target_pattern": "stage_b_batch3",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=3]"},
    {"layer": "C", "id": "C-15-B4", "label": "W9 batch4 validation 18",
     "kind": "w9_batch", "batch": "4",
     "shogun_target_pattern": "stage_b_batch4",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=4]"},
    {"layer": "C", "id": "C-15-B5", "label": "W9 batch5 data_quality + 処置セット 20",
     "kind": "w9_batch", "batch": "5",
     "shogun_target_pattern": "stage_b_batch5",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=5]"},
    {"layer": "C", "id": "C-15-B6", "label": "W9 batch6 補綴系 19",
     "kind": "w9_batch", "batch": "6",
     "shogun_target_pattern": "stage_b_batch6",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=6]"},
    {"layer": "C", "id": "C-15-B7", "label": "W9 batch7 alert 残 15",
     "kind": "w9_batch", "batch": "7",
     "shogun_target_pattern": "stage_b_batch7",
     "ref": "queue/manifests/w9_design_tasks_169.yaml batches[batch_id=7]"},
    # Layer D 頭脳層 蜘蛛の糸 — 法令 8,000+ records
    {"layer": "D", "id": "D-1", "label": "legal_sources 1,600 件",
     "ref": "Supabase legal_sources SELECT category, COUNT",
     "supabase_table": "legal_sources"},
    {"layer": "D", "id": "D-2", "label": "inspection_checklists 2,495 件",
     "ref": "Supabase inspection_checklists",
     "supabase_table": "inspection_checklists"},
    {"layer": "D", "id": "D-3", "label": "inspection_findings 621 件",
     "ref": "Supabase inspection_findings",
     "supabase_table": "inspection_findings"},
    {"layer": "D", "id": "D-4", "label": "procedure_codes_audit 250 件",
     "ref": "Supabase procedure_codes_audit (算定可否分布)",
     "supabase_table": "procedure_codes_audit"},
    {"layer": "D", "id": "D-5", "label": "design_tasks 169 件 W9 蜘蛛の糸",
     "ref": "Supabase design_tasks WHERE category 全 21",
     "supabase_table": "design_tasks"},
    # Layer E 運用層 — MC/SC pane + systemd + 通信規範 + auto-git-sync
    {"layer": "E", "id": "E-1", "label": "MC pane 状態",
     "ref": "tmux capture-pane + pid count"},
    {"layer": "E", "id": "E-2", "label": "SC pane 状態",
     "ref": "ssh secondpc tmux + pid"},
    {"layer": "E", "id": "E-3", "label": "systemd unit 全",
     "ref": "systemctl --user list-units"},
    {"layer": "E", "id": "E-4", "label": "通信規範 (inbox_watcher / watcher_supervisor)",
     "design_doc": "scripts/inbox_watcher.sh",
     "ref": "inbox_watcher.sh + watcher_supervisor.sh"},
    {"layer": "E", "id": "E-5", "label": "auto-git-sync",
     "design_doc": "scripts/auto_git_sync.sh",
     "audit_id_pattern": "kuroda_audit_auto_git_sync", "shogun_target_pattern": "auto_git_sync",
     "ref": "queue/reports/auto_sync_log.yaml + docs/auto_git_sync_design.md"},
    # Layer F 規範層 — memory MCP + forbidden_actions + persona
    {"layer": "F", "id": "F-1", "label": "memory MCP 26 entities",
     "ref": "mcp__memory__read_graph"},
    {"layer": "F", "id": "F-2", "label": "F001-F005 forbidden_actions",
     "design_doc": "instructions/shogun.md",
     "ref": "instructions/shogun.md F001-F005"},
    {"layer": "F", "id": "F-3", "label": "shogun_privileges P001-P002",
     "design_doc": "instructions/shogun.md",
     "ref": "instructions/shogun.md P001-P002"},
    {"layer": "F", "id": "F-4", "label": "persona 規範",
     "design_doc": "instructions/ashigaru.md",
     "ref": "instructions/{shogun,karo,ashigaru,gunshi}.md"},
    {"layer": "F", "id": "F-5", "label": "規範 audit chain",
     "audit_id_pattern": "kuroda_active_verify",
     "shogun_target_pattern": "active_verify",
     "ref": "task_directive_pre_audit_rule + pre_emit_sot_check_rule + eta_machine_evidence_rule"},
    # Layer G 統合層 — Stage 3-5 + 監査 chain
    {"layer": "G", "id": "G-1", "label": "HTML drill-down (cycle 3 完遂 + cycle 4 子・孫装着)",
     "design_doc": "scripts/regenerate_dashboard.py",
     "audit_id_pattern": "kuroda_cmd020_regenerate_dashboard",
     "shogun_target_pattern": "cmd020_dashboard",
     "ref": "本 generator + tests/test_regenerate_dashboard.py"},
    {"layer": "G", "id": "G-2", "label": "mermaid 統合",
     "design_doc": "docs/dashboard_layer_a_kousou.md",
     "ref": "docs/dashboard_layer_a_kousou.md §4 graph TD + v0.2 §4.2 children"},
    {"layer": "G", "id": "G-3", "label": "systemd dashboard-update.timer",
     "ref": "(未装着、Stage 5 予定)"},
    {"layer": "G", "id": "G-4", "label": "shogun_active_verify_queue (= ashigaru7 cycle 1 完遂)",
     "design_doc": "scripts/shogun_active_verify_queue.py",
     "audit_id_pattern": "kuroda_active_verify",
     "ref": "queue/reports/active_verify_queue_candidate_log.yaml"},
    {"layer": "G", "id": "G-5", "label": "検証 24h 運用",
     "ref": "(未装着、Stage 6 予定)"},
]


# cycle6: Layer C verify list 拡張 — 信長殿 16:02 能動 verify 50 件全件抜け漏れ反映
# (= 黒田事前監査 kuroda_cmd020_dashboard_cycle6_layer_c_extension_preaudit 条件 1 + 2 整合)。
# 各 row は Supabase development_progress を SoT として明示 (= 捏造禁、source 列含む)。
# Row 形式: (id_seq, label, status, week, phase_code, pc, commit_hash)
# status ∈ {completed, in_progress, not_started} を kind=supabase_phase で 90/50/0 pct 化。
LAYER_C_SUPABASE_VERIFY_ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    # 基盤 W1-W2 (4 件)
    ("V01-W1DB",      "W1 DB拡張+API(7 テーブル+9 API)",                              "completed",  "W1",        "phase1",                   "second", ""),
    ("V02-W1KARTE",   "W1 カルテ画面 v2.0 骨格+デザイントークン+SKILL.md",            "completed",  "W1",        "phase2w1",                 "main",   "4d56e6d"),
    ("V03-W2COMP",    "W2 コンポーネント接続+ロール別+SOAP UI",                       "completed",  "W2",        "phase2w2",                 "main",   "5b6811d"),
    ("V04-W2AIIMG",   "W2 AI 画像判定 API+所見提案 API",                              "completed",  "W2",        "phase3",                   "second", ""),
    # W3-W5 機能 (6 件)
    ("V05-W3AIUI",    "W3 AI 判定 UI(黄バッジ)+確認訂正 UI",                          "completed",  "W3",        "phase3",                   "main",   "097bb29"),
    ("V06-W3SPID",    "W3 蜘蛛の糸 BE+日計表+受付ダッシュボード+Quartetto",           "completed",  "W3",        "phase4",                   "second", "5aaa5dc"),
    ("V07-W4FE",      "W4 FE 結線(歯式→処置セット制御+日計表 FE+受付 FE)",            "completed",  "W4",        "phase4",                   "main",   "b37a5ee"),
    ("V08-W4YOYAKU",  "W4 phaseB 予約ソフト BE 改修(次回予約提案+脱落 AI+カルテ橋渡し)", "completed", "W4",        "phaseB",                   "second", "a07c834"),
    ("V09-W5YOYFE",   "W5 phaseB 予約⇔カルテ⇔受付シームレス FE 結線",                "completed",  "W5",        "phaseB",                   "main",   "cd5e3df"),
    ("V10-W5KEIEI",   "W5 phaseD 経営分析+AI メール+CTI 基盤",                        "completed",  "W5",        "phaseD",                   "second", "4051e26"),
    # W6-W9 患者+AI (10 件)
    ("V11-W6PWABE",   "W6 phaseC 患者アプリ BE(PWA API+AI チャット+電子明細書+高速会計)", "completed", "W6",       "phaseC",                   "second", "f0b5fed"),
    ("V12-W6PWAUI",   "W6 phaseC 患者アプリ UI(PWA+歯式+治療選択肢+電子明細書+AI チャット)", "completed", "W6",     "phaseC",                   "main",   "b753f1e"),
    ("V13-W7LEARN",   "W7 学習ループ(contributor 設定+精度測定)",                      "completed",  "W7",        "phase5",                   "second", "ed6cb5c"),
    ("V14-W7KEIEIUI", "W7 phaseD 経営分析ダッシュボード UI+AI メール設定画面",         "completed",  "W7",        "phaseD",                   "main",   "fad02dd"),
    ("V15-W8TCUI",    "W8 TC カウンセリング画面+治療計画 UI",                          "completed",  "W8",        "phase6",                   "main",   "48dca02"),
    ("V16-W8TPNAVI",  "W8 治療計画ナビ BE(治療計画 AI+TC カウンセリング API)",         "completed",  "W8",        "phase6",                   "second", "156749d"),
    ("V17-W9AIK",     "W9 P1-karte 2 号用紙 AI 清書配線(DD-036→v2 UI 接続)",          "completed",  "W9",        "P1-karte",                 "main",   "9beb61b"),
    ("V18-W9KARTE",   "W9 P1-karte カルテ履歴画面(患者別時系列 SOAP 一覧)",            "completed",  "W9",        "P1-karte",                 "main",   "cb02e50"),
    ("V19-W9TENKI",   "W9 P1-karte カルテ転記(清書変換+整理+プレビュー)",              "completed",  "W9",        "P1-karte",                 "main",   "021b492"),
    ("V20-W9MOKB",    "W9 P1-karte 申し送りカンバン連動(SOAP 確定→自動記載)",          "completed",  "W9",        "P1-karte",                 "main",   "77ebed6"),
    # W9 補強 + SEC-1 (3 件)
    ("V21-W9TENSU",   "W9 P2-engine R8 施行前の全処置セット点数確認",                  "not_started","W9",        "P2-engine",                "either", ""),
    ("V22-W9SPIDCHK", "W9 P2-engine 蜘蛛の糸 算定チェック+バリデーション(design_tasks 169 件)", "not_started", "W9", "P2-engine",            "either", ""),
    ("V23-W9SEC1",    "W9 SEC-1: datetime 統一+CORS+SECRET+API_BASE 集約",            "completed",  "W9",        "P4-security",              "second", "7c2e567"),
    # W10 (4 件)
    ("V24-W10CNV2",   "W10 P1-karte CNV2 連動(A 欄確定→処置セット自動反映)",          "completed",  "W10",       "P1-karte",                 "main",   "cb02e50"),
    ("V25-W10PDFP",   "W10 P1-karte カルテ印刷 PDF 出力",                              "completed",  "W10",       "P1-karte",                 "main",   "b22a368"),
    ("V26-W10DATE",   "W10 P1-karte 日付管理(同日複数回・日付またぎ)",                  "completed",  "W10",       "P1-karte",                 "main",   "e866946"),
    ("V27-W10JIHI",   "W10 P1-karte 自費カルテ欄(保険/自費分離記載)",                  "completed",  "W10",       "P1-karte",                 "main",   "892be39"),
    # W11 (4 件)
    ("V28-W11HOMON",  "W11 訪問 Phase5(申し送り+画像+AI 清書)",                       "completed",  "W11",       "P6-visit",                 "either", "967474a6"),
    ("V29-W11DDA",    "W11 DD-054 Phase A: ID 体系統一(meisai_receipt_renderer→患者番号/医院 ID 複合キー)", "in_progress", "W11", "phase_a_id_unification", "main", ""),
    ("V30-W11DDB",    "W11 DD-054 Phase B: カルテ TAB→karte_visits/karte_visit_items 同時投入ローダー新設", "in_progress", "W11", "phase_b_karte_loader", "main", ""),
    ("V31-W11CHOREI", "W11 朝礼フル版 Phase1-4",                                       "not_started","W11",       "POST-deploy",              "either", ""),
    # W12 (2 件)
    ("V32-W12TPL",    "W12 書式テンプレート Lv2",                                      "completed",  "W12",       "P5-docs",                  "either", "56cb6dbe"),
    ("V33-W12CLNUI",  "W12 臨床ナレッジ UI",                                           "not_started","W12",       "POST-deploy",              "either", ""),
    # W13 (2 件)
    ("V34-W13VISIT",  "W13 訪問 Phase4-7(中期残)",                                    "not_started","W13",       "P6-visit",                 "either", ""),
    ("V35-W13RTE",    "W13 訪問ルート最適化",                                          "not_started","W13",       "P6-visit",                 "either", ""),
    # W14 (4 件) — 信長殿 directive 16:00 C-NEW-2 を V38 で明示
    ("V36-W14PAY",    "W14 ペイライト 実 API 接続",                                    "not_started","W14",       "P3-patient",               "either", ""),
    ("V37-W14CTI",    "W14 CTI 実接続(VALTEC MOT/TEL)",                                "not_started","W14",       "POST-deploy",              "either", ""),
    ("V38-W14LINE",   "W14 外部 API 統合(LINE 通知+Web 予約実接続) ※C-NEW-2",         "not_started","W14",       "POST-deploy",              "either", ""),
    ("V39-W14YOSHI3", "W14 書式 Lv3+唾液検査",                                        "not_started","W14",       "POST-deploy",              "either", ""),
    # W15 (3 件)
    ("V40-W15VAL",    "W15 D-1 全文書バリデーション",                                  "completed",  "W15",       "P5-docs",                  "either", "9e7d838c"),
    ("V41-W15DEP",    "W15 D-2 デプロイ手順書+実データテスト+Tailscale",               "not_started","W15",       "P7-deploy",                "either", ""),
    ("V42-W15MAN",    "W15 D-3 操作マニュアル",                                        "not_started","W15",       "P7-deploy",                "either", ""),
    # W16-W17 (2 件)
    ("V43-W16MAT",    "W16 材料管理(QR スキャン+納品 OCR+棚 AI+理論消費量)",          "not_started","W16",       "POST-deploy",              "either", ""),
    ("V44-W17JINJI",  "W17 人事+DTF アダプター+全院展開",                              "not_started","W17",       "POST-deploy",              "either", ""),
    # 2026-W17 RM-003e/f (2 件)
    ("V45-RM3E",      "RM-003e queuer.py(Step 5-5 receipt_mail_queue INSERT)",         "completed",  "2026-W17",  "P8-receipt-mail",          "second", "7cb76588"),
    ("V46-RM3F",      "RM-003f processor.enqueue 統合(Step 5-6 watcher→extract→stamp→match→rename→queue)", "completed", "2026-W17", "P8-receipt-mail", "second", "ca69c8c9"),
    # week-null (5 件 grouped)
    ("V47-AIVICE",    "AI 副院長 Phase3: ViceDirectorChat.tsx 音声フック接続",         "completed",  "(week=null)", "ai_vice",                "main",   ""),
    ("V48-KVERIFY",   "患者 02 照合 Day16〜再開",                                       "completed",  "(week=null)", "karte_verify",           "either", ""),
    ("V49-RMGROUP",   "RM-001〜RM-003d 領収書メール処理(queue/watcher/extract/stamp/rename/match 完遂 8 件)", "completed", "(week=null)", "P8-receipt-mail", "second", "292de49e+b4c24baf+e441e6eb+c433cdc0+cae1abaa+99c819cc+073174fd"),
    ("V50-QUALITY",   "品質改善 A/B/C+デザイントークン 340+dental-ui+BE/FE 監査+TS_DENTURE_NEW+疑義解釈 18 件(week-null quality cluster 完遂)", "completed", "(week=null)", "quality+shochi_set", "main+second", "15bf356+06f41296+3983ac90+cff2966+d325863+c4f7615+35ad8c1"),
]


def _build_supabase_phase_child(
    seq: str, label: str, status: str, week: str, phase_code: str, pc: str, commit_hash: str,
    *, layer: str = "C", note: str = "",
) -> dict[str, Any]:
    """Build a LAYER_CHILDREN entry from a Supabase development_progress row.

    kind=supabase_phase で compute_child_machine_state が status→pct を 90/50/0 に
    決定する。捏造禁 (黒田 cycle6 条件 2): status 不明時は呼出側が source_unavailable
    経路へ振る分岐責務、本関数は機械抽出値のみ封入する。
    """
    source = (
        f"Supabase development_progress (week={week}, phase_code={phase_code}, pc={pc})"
    )
    ref_parts = ["信長殿 16:02 verify list", source]
    if note:
        ref_parts.append(note)
    return {
        "layer": layer,
        "id": f"{layer}-{seq}",
        "label": label,
        "kind": "supabase_phase",
        "external_status": status,
        "external_source": source,
        "external_commit": commit_hash,
        "supabase_table": "development_progress",
        "ref": " / ".join(ref_parts),
    }


# Layer C を 50 件 verify list で拡張 (= 22 → 72)。
LAYER_CHILDREN.extend(
    _build_supabase_phase_child(*row) for row in LAYER_C_SUPABASE_VERIFY_ROWS
)

# cycle6: Layer B Phase 層 完了 phase 子項目 list (= 計画書 v0.1 §4.1 mockup 整合、
# Layer C と grouping 整合)。phaseB 予約ソフト / phaseC 患者アプリ / phaseD 経営分析。
LAYER_CHILDREN.extend([
    _build_supabase_phase_child(
        "5-PHASEB", "phaseB 予約ソフト 完遂(W4 BE a07c834 + W5 FE cd5e3df)",
        "completed", "W4+W5", "phaseB", "second+main", "a07c834+cd5e3df",
        layer="B",
        note="Layer C V08-W4YOYAKU + V09-W5YOYFE と grouping 整合 (= 信長殿 directive C-NEW-1)",
    ),
    _build_supabase_phase_child(
        "6-PHASEC", "phaseC 患者アプリ 延伸 完遂(W6 BE f0b5fed + UI b753f1e)",
        "completed", "W6", "phaseC", "second+main", "f0b5fed+b753f1e",
        layer="B",
        note="PWA+歯式+AI チャット+電子明細書+高速会計連携 (Layer C V11/V12 と整合)",
    ),
    _build_supabase_phase_child(
        "7-PHASED", "phaseD 経営分析+AI メール+CTI 基盤 完遂(W5 BE 4051e26 + W7 UI fad02dd)",
        "completed", "W5+W7", "phaseD", "second+main", "4051e26+fad02dd",
        layer="B",
        note="BE 経営分析+AI メール+CTI 基盤 (W5) + UI 経営分析 dashboard+AI メール設定 (W7)",
    ),
])


# cycle4: mermaid v0.2 §4.2 — Layer C 機能層 → 会計待ちゼロ / 小児恐竜王国 / 申し送り
# children 接続図。第 1 mermaid (= Layer A 5 階層 + 10 柱) と別 block で表示する。
LAYER_C_CHILDREN_MERMAID = """```mermaid
graph LR
    LC[Layer C 機能層]
    LC --> KZ[会計待ちゼロ作戦]
    LC --> SK[小児恐竜王国アプリ]
    LC --> MO[申し送りエンジン]
    LC --> W9[W9 蜘蛛の糸 算定]
    KZ --> KZ1[領収書 PDF + cycle6]
    KZ --> KZ2[PDF v0.2 hardening]
    KZ --> KZ3[AI チャット + 同意]
    KZ --> KZ4[QR kanban]
    KZ --> KZ5[handover_notes_anon]
    KZ --> KZ6[engagement analytics]
    SK --> SK1[100 敵 spec]
    SK --> SK2[PWA]
    SK --> SK3[push_vapid]
    SK --> SK4[保護者同意]
    MO --> MO1[Stage 1 設計完遂]
    MO --> MO2[Stage 2 blocked]
    W9 --> W9A[Stage A foundation 9]
    W9 --> W9B[Stage B batch1-7]
```"""


def progress_color_tier(pct: float) -> dict[str, str]:
    """Map a progress percentage to the highest-priority color tier."""
    for tier in PROGRESS_COLOR_TIERS:
        if pct >= tier["min_pct"]:
            return tier  # type: ignore[return-value]
    return PROGRESS_COLOR_TIERS[-1]  # type: ignore[return-value]


def children_for_layer(layer_code: str) -> list[dict[str, Any]]:
    """Return all children entries declared for a given Layer code (A-G)."""
    return [c for c in LAYER_CHILDREN if c.get("layer") == layer_code]


def progress_bar_html(pct: float, *, width_px: int = 200, height_px: int = 14) -> str:
    """Render an HTML5 <progress> bar with color-tier emoji prefix.

    Markdown viewers that strip inline HTML still render the emoji + text;
    viewers that honor HTML (GitHub, dashboard-viewer.py) get the bar.
    """
    tier = progress_color_tier(pct)
    style = f"width:{width_px}px;height:{height_px}px"
    return (
        f"{tier['emoji']} "
        f"<progress class=\"{tier['css_class']}\" "
        f"value=\"{pct:.1f}\" max=\"100\" style=\"{style}\"></progress> "
        f"**{pct:.1f}%**"
    )


# cycle3: cmd_004 W9 Stage / batch 識別 — task_id から Stage A/B + batch_id を抽出する。
# example task_id:
#   subtask_cmd004_w9_batch1_stage_a_foundation       -> stage=A, batch=1
#   subtask_cmd004_w9_stage_b_batch3_check_logic_26   -> stage=B, batch=3
#   subtask_cmd004_w9_batch1_keisan_check_42_v2       -> stage=None, batch=1
_W9_BATCH_RE = re.compile(r"w9_(?:stage_(?P<sa>[ab])_)?batch(?P<bid>\d+)(?:_stage_(?P<sb>[ab]))?", re.IGNORECASE)


def _extract_w9_meta(task_id: str) -> dict[str, str | None]:
    """Extract W9 stage + batch identifiers from a task_id, if present."""
    match = _W9_BATCH_RE.search(task_id or "")
    if not match:
        return {"stage": None, "batch": None}
    stage = (match.group("sa") or match.group("sb") or "").upper() or None
    batch = match.group("bid")
    return {"stage": stage, "batch": batch}


def aggregate_w9_stage_progress(tasks: Iterable[TaskEntry]) -> list[dict[str, Any]]:
    """Aggregate cmd_004 W9 progress grouped by Stage (A/B/未分類)."""
    buckets: dict[str, list[float]] = {"A": [], "B": [], "未分類": []}
    counts: dict[str, int] = {"A": 0, "B": 0, "未分類": 0}
    for task in tasks:
        if "cmd004_w9" not in (task.task_id or ""):
            continue
        meta = _extract_w9_meta(task.task_id)
        key = meta["stage"] or "未分類"
        if key not in buckets:
            continue
        counts[key] += 1
        score = progress_for_task(task)
        if score is not None:
            buckets[key].append(score)
    rows: list[dict[str, Any]] = []
    for key in ("A", "B", "未分類"):
        scores = buckets[key]
        avg = (sum(scores) / len(scores)) if scores else 0.0
        rows.append({
            "stage": key,
            "task_count": counts[key],
            "scored_count": len(scores),
            "avg_pct": round(avg, 1),
        })
    return rows


def aggregate_w9_batch_progress(tasks: Iterable[TaskEntry]) -> list[dict[str, Any]]:
    """Aggregate cmd_004 W9 progress grouped by batch_id 1-7."""
    buckets: dict[str, list[tuple[float, TaskEntry]]] = {}
    for task in tasks:
        if "cmd004_w9" not in (task.task_id or ""):
            continue
        meta = _extract_w9_meta(task.task_id)
        batch = meta["batch"]
        if not batch:
            continue
        score = progress_for_task(task)
        buckets.setdefault(batch, []).append((score if score is not None else 0.0, task))
    rows: list[dict[str, Any]] = []
    for batch in sorted(buckets.keys(), key=lambda b: int(b)):
        entries = buckets[batch]
        scored = [s for s, _ in entries if s is not None]
        avg = (sum(scored) / len(scored)) if scored else 0.0
        rows.append({
            "batch": batch,
            "task_count": len(entries),
            "avg_pct": round(avg, 1),
            "task_ids": [t.task_id for _, t in entries],
        })
    return rows

# ---------------------------------------------------------------------------
# cycle4: 子項目 evidence extraction (= 5 項固定 grandchildren template)
#   commit / test / audit / shogun_verified / 参照
# 機械抽出のみ。捏造禁 (= 黒田 cycle4 事前監査 条件 1)、data 不在は fallback。
# ---------------------------------------------------------------------------


KURODA_REPORT_FILE = QUEUE_REPORTS_DIR / "kuroda_mainpc_report.yaml"
SHOGUN_VERIFICATION_FILE = QUEUE_REPORTS_DIR / "shogun_verification_mainpc_log.yaml"


def load_kuroda_index(report_path: Path | None = None) -> list[dict[str, Any]]:
    """Read kuroda_mainpc_report.yaml and return a flat list of audit entries."""
    path = report_path if report_path is not None else KURODA_REPORT_FILE
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    reports = data.get("reports") or []
    return [r for r in reports if isinstance(r, dict)]


def load_shogun_verification_index(log_path: Path | None = None) -> list[dict[str, Any]]:
    """Read shogun_verification_mainpc_log.yaml and return all entries flat.

    cycle11: the log carries two top-level sections — 'verifications' (=
    legacy朝の手動 migration entries) and 'entries' (= recent bulk + per-task
    additions). Both are merged into a single flat list so the global
    reflection logic can scan the entire ledger, not just the legacy half.
    """
    path = log_path if log_path is not None else SHOGUN_VERIFICATION_FILE
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    merged: list[dict[str, Any]] = []
    for key in ("verifications", "entries"):
        section = data.get(key) or []
        if isinstance(section, list):
            merged.extend(v for v in section if isinstance(v, dict))
    return merged


def _is_active_shogun_entry(entry: dict[str, Any]) -> bool:
    """cycle11 黒田 6 条件 #1 + #5 — eligibility filter for shogun verify match.

    shogun_verified must be the boolean True (= "true" string / truthy types
    excluded). entries marked migration_note=legacy_migrated (= 旧 log 朝の
    手動 append から机上 migrate された pre-2026-05-11 履歴) も除外する。
    cycle10 で陛下が御自認の通り legacy 期 verify は規範外 evidence ゆえ
    緑化判定の base にしない。
    """
    if entry.get("shogun_verified") is not True:
        return False
    if entry.get("migration_note") == "legacy_migrated":
        return False
    return True


def find_latest_audit_for_pattern(
    kuroda_entries: list[dict[str, Any]], pattern: str
) -> dict[str, Any] | None:
    """Return the newest kuroda audit entry whose audit_id contains pattern (case-insensitive)."""
    if not pattern:
        return None
    needle = pattern.lower()
    matches = [
        e for e in kuroda_entries
        if needle in str(e.get("audit_id", "")).lower()
        or needle in str(e.get("target_id", "")).lower()
    ]
    if not matches:
        return None
    return max(matches, key=lambda e: str(e.get("audited_at", "")))


def find_latest_shogun_verified(
    shogun_entries: list[dict[str, Any]], pattern: str
) -> dict[str, Any] | None:
    """Return the newest active shogun_verified entry matching pattern.

    cycle11: matching now scans BOTH 'target' and 'audit_id_ref' fields so
    bulk-appended entries (= chain that records audit_id_ref instead of a
    canonical target token, e.g. subtask_cmd020_dashboard_cycle9_v2 +
    audit_id_ref=kuroda_cmd020_dashboard_cycle9_v2_*) are reachable for
    child mapping. Eligibility = _is_active_shogun_entry (boolean true 限定
    + legacy_migrated 除外)。
    """
    if not pattern:
        return None
    needle = pattern.lower()
    matches = [
        v for v in shogun_entries
        if _is_active_shogun_entry(v)
        and (
            needle in str(v.get("target", "")).lower()
            or needle in str(v.get("audit_id_ref", "")).lower()
        )
    ]
    if not matches:
        return None
    return max(matches, key=lambda v: str(v.get("verified_at", "")))


def git_log_for_path(path: str, repo: Path = PROJECT_ROOT) -> dict[str, str]:
    """Return {hash,subject,author_date} for the newest commit touching path, or {}.

    author_date は ISO 形式 (= %ai)。relative age (%ar) は時刻 drift で snapshot/verify
    test を不安定にするため (cycle4 で複数 child の commit が render されると秒境界で
    age 表記が "X seconds ago"→"Y seconds ago" にずれて再現性が消える) ISO 化する。
    """
    if not path:
        return {}
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "log", "-1",
             "--pretty=format:%h|%s|%ai", "--", path],
            stderr=subprocess.DEVNULL, timeout=5,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    if not out:
        return {}
    parts = out.split("|", 2)
    if len(parts) != 3:
        return {}
    return {"hash": parts[0], "subject": parts[1], "author_date": parts[2]}


# Fallback strings — cycle4 §3-2 規範 (= 「捏造禁、data 不在時は明示」)
FALLBACK_COMMIT = "(未 commit)"
FALLBACK_TEST = "(test 未実行)"
FALLBACK_AUDIT = "(黒田監査未)"
FALLBACK_SHOGUN_FALSE = "false"
FALLBACK_REF = "(参照 doc 未起案)"

# cycle7: 1 行 inline 表示用 短縮 fallback (= 文字量圧縮、p element 1 行 fit 用)。
# 既存 FALLBACK_* は machine state evidence dict 用 retain (= cycle4-6 test 整合)。
# 横一列 render 時のみ INLINE_FALLBACK_MAP で「(未)」に短縮。
INLINE_FALLBACK_SHORT = "(未)"
INLINE_FALLBACK_MAP = {
    FALLBACK_COMMIT: INLINE_FALLBACK_SHORT,
    FALLBACK_TEST: INLINE_FALLBACK_SHORT,
    FALLBACK_AUDIT: INLINE_FALLBACK_SHORT,
    FALLBACK_REF: INLINE_FALLBACK_SHORT,
}


def shorten_inline_value(value: str) -> str:
    """cycle7: 1 行 inline 表示で fallback 文字列を「(未)」に短縮 (= 文字量圧縮)。

    fallback 以外の値 (= 実 commit hash / verdict / audit_id / ref 等) はそのまま返す。
    """
    return INLINE_FALLBACK_MAP.get(value, value)


def build_inline_evidence(evidence: dict[str, str]) -> dict[str, str]:
    """cycle7: evidence dict を 1 行 inline 表示用に短縮 (= 黒田 cycle4 evidence retain + 視認圧縮)。

    cycle 4-6 既装備の evidence dict 5 field (commit/test/audit/shogun_verified/ref) を
    そのまま受け取り、fallback 検出時のみ INLINE_FALLBACK_SHORT に置換した dict を返す。
    """
    return {
        "commit": shorten_inline_value(evidence.get("commit", "")),
        "test": shorten_inline_value(evidence.get("test", "")),
        "audit": shorten_inline_value(evidence.get("audit", "")),
        "shogun_verified": evidence.get("shogun_verified", ""),
        "ref": shorten_inline_value(evidence.get("ref", "")),
    }


def _audit_evidence_pytest(audit_entry: dict[str, Any]) -> str | None:
    """Pull machine_evidence.pytest.observed from a kuroda audit entry, if present."""
    if not isinstance(audit_entry, dict):
        return None
    me = audit_entry.get("machine_evidence")
    if not isinstance(me, dict):
        return None
    pytest_block = me.get("pytest")
    if isinstance(pytest_block, dict):
        observed = pytest_block.get("observed")
        if isinstance(observed, str) and observed.strip():
            return observed.strip()
    return None


def extract_child_evidence(
    child: dict[str, Any],
    *,
    kuroda_entries: list[dict[str, Any]],
    shogun_entries: list[dict[str, Any]],
    w9_batches: list[dict[str, Any]] | None = None,
    w9_stages: list[dict[str, Any]] | None = None,
    repo: Path = PROJECT_ROOT,
) -> dict[str, str]:
    """Resolve 5-fixed grandchildren evidence for a single child entry.

    Returns dict with keys: commit / test / audit / shogun_verified / ref.
    Missing data → fallback strings (黒田 cycle4 条件 1 整合、捏造禁)。
    """
    kind = child.get("kind")

    # cycle6: Supabase development_progress 直接参照 children (= 50 件 verify list).
    # 黒田 cycle6 条件 2 整合 — status は Supabase 抽出値、捏造禁。
    if kind == "supabase_phase":
        status = str(child.get("external_status", ""))
        commit = str(child.get("external_commit", "")) or "(commit_hash unrecorded)"
        source = str(child.get("external_source", ""))
        audit_label = f"Supabase development_progress: {status or 'unknown'}"
        shogun_label = "Supabase 完了記録" if status == "completed" else FALLBACK_SHOGUN_FALSE
        ref_parts: list[str] = [str(child.get("ref", FALLBACK_REF))]
        return {
            "commit": commit,
            "test": f"status={status} ({source})" if source else f"status={status}",
            "audit": audit_label,
            "shogun_verified": shogun_label,
            "ref": ref_parts[0] if ref_parts else FALLBACK_REF,
        }

    # W9 batch / stage children — reuse aggregate stats as machine evidence.
    if kind == "w9_batch":
        batch_id = str(child.get("batch", ""))
        match = next(
            (r for r in (w9_batches or []) if str(r.get("batch", "")) == batch_id),
            None,
        )
        if match:
            return {
                "commit": f"(集計値、{match['task_count']} 件)",
                "test": f"task_count={match['task_count']}",
                "audit": f"batch{batch_id} 平均進捗 {match['avg_pct']}%",
                "shogun_verified": f"{match['avg_pct']}%",
                "ref": str(child.get("ref", FALLBACK_REF)),
            }
        return _fallback_evidence(child)
    if kind == "w9_stage":
        stage = str(child.get("stage", ""))
        match = next(
            (r for r in (w9_stages or []) if str(r.get("stage", "")) == stage),
            None,
        )
        if match:
            return {
                "commit": f"(集計値、{match['task_count']} 件)",
                "test": f"scored={match['scored_count']}/{match['task_count']}",
                "audit": f"Stage {stage} 平均進捗 {match['avg_pct']}%",
                "shogun_verified": f"{match['avg_pct']}%",
                "ref": str(child.get("ref", FALLBACK_REF)),
            }
        return _fallback_evidence(child)

    # Standard child — derive from design_doc git log + kuroda + shogun_verified.
    design_doc = str(child.get("design_doc", ""))
    audit_pattern = str(child.get("audit_id_pattern", ""))
    shogun_pattern = str(child.get("shogun_target_pattern", "")) or audit_pattern

    commit_info = git_log_for_path(design_doc) if design_doc else {}
    if commit_info:
        commit_str = f"`{commit_info['hash']}` {commit_info['subject']} ({commit_info['author_date']})"
    else:
        commit_str = FALLBACK_COMMIT

    audit_match = find_latest_audit_for_pattern(kuroda_entries, audit_pattern)
    if audit_match:
        verdict = str(audit_match.get("verdict", "")) or "(verdict 不在)"
        audit_str = f"`{audit_match.get('audit_id', '')}` → {verdict}"
        test_observed = _audit_evidence_pytest(audit_match)
        test_str = test_observed if test_observed else FALLBACK_TEST
    else:
        audit_str = FALLBACK_AUDIT
        test_str = FALLBACK_TEST

    verif_match = find_latest_shogun_verified(shogun_entries, shogun_pattern)
    if verif_match:
        verified_at = str(verif_match.get("verified_at", ""))
        shogun_str = f"true ({verified_at})"
    else:
        shogun_str = FALLBACK_SHOGUN_FALSE

    ref_parts: list[str] = []
    if design_doc:
        ref_parts.append(design_doc)
    if child.get("ref"):
        ref_parts.append(str(child["ref"]))
    if child.get("supabase_table"):
        ref_parts.append(f"Supabase `{child['supabase_table']}`")
    ref_str = " / ".join(ref_parts) if ref_parts else FALLBACK_REF

    return {
        "commit": commit_str,
        "test": test_str,
        "audit": audit_str,
        "shogun_verified": shogun_str,
        "ref": ref_str,
    }


def _fallback_evidence(child: dict[str, Any]) -> dict[str, str]:
    return {
        "commit": FALLBACK_COMMIT,
        "test": FALLBACK_TEST,
        "audit": FALLBACK_AUDIT,
        "shogun_verified": FALLBACK_SHOGUN_FALSE,
        "ref": str(child.get("ref") or FALLBACK_REF),
    }


# ---------------------------------------------------------------------------
# cycle8: cmd_004 audit 状態 alert section (= 黒田 17:00 9 件 audit 結果 visible)
#   verdict 軸 SoT — 各 target_doc.verdict を pass/fail/None で 3 軸分類。
#   audit_id 有無のみの判定は禁 (= 黒田 v2 preaudit 条件 1 整合)。
# ---------------------------------------------------------------------------

CMD004_AUDIT_ALERT_AUDIT_ID = "kuroda_cmd004_remaining_9_design_docs_audit_20260512"

# verdict 状態表示 (= 黒田 v2 preaudit 条件 3 整合、engagement pass_with_concerns 明示)
_ALERT_STATUS_FAIL = "privacy修正待ち"
_ALERT_STATUS_UNAUDIT = "未監査"


def classify_verdict_for_alert(verdict: Any) -> str:
    """Map a target_doc verdict to alert tier (= 'pass' | 'wait' | 'unaudit').

    Verdict 軸 SoT (= 黒田 v2 preaudit 条件 1 整合):
      - pass / pass_with_concerns → 'pass' (= 通行可)
      - fail* (privacy sanitization 等) → 'wait' (= 修正待ち)
      - None / 空 → 'unaudit' (= 未監査 placeholder)
    audit_id 有無のみの分類は禁。
    """
    if not verdict:
        return "unaudit"
    v = str(verdict).strip().lower()
    if v.startswith("pass"):
        return "pass"
    if v.startswith("fail"):
        return "wait"
    return "unaudit"


def _alert_status_display(verdict: Any) -> str:
    """Render verdict as a short status label for the alert table."""
    if not verdict:
        return _ALERT_STATUS_UNAUDIT
    v = str(verdict).strip().lower()
    if v == "pass":
        return "pass"
    if v == "pass_with_concerns":
        return "pass_with_concerns"
    if v.startswith("fail"):
        return _ALERT_STATUS_FAIL
    return str(verdict)


def _alert_doc_size_label(path_str: str, root: Path = PROJECT_ROOT) -> str:
    """Format relative-path doc size as e.g. '8.4KB' / '29KB'."""
    if not path_str:
        return ""
    full = root / path_str
    try:
        size_bytes = full.stat().st_size
    except OSError:
        return ""
    kb = size_bytes / 1024
    return f"{kb:.1f}KB" if kb < 10 else f"{kb:.0f}KB"


def _alert_relative_path(path_str: str) -> str:
    """Coerce a doc path to repo-relative form (= 黒田 v2 preaudit 条件 4 整合).

    Absolute paths leaked into audit data are stripped to relative form
    via PROJECT_ROOT resolution; if outside the repo, return the basename
    only so the alert section never renders absolute paths.
    """
    if not path_str:
        return ""
    p = path_str.strip()
    if not p.startswith("/"):
        return p
    try:
        rel = Path(p).resolve().relative_to(PROJECT_ROOT)
        return str(rel)
    except (ValueError, OSError):
        return Path(p).name


def build_cmd004_audit_alert_section(
    kuroda_entries: list[dict[str, Any]],
    audit_id: str = CMD004_AUDIT_ALERT_AUDIT_ID,
    docs_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Build cmd_004 9-doc audit alert section data for the template.

    Each target_doc is classified by its verdict (SoT axis) — pass /
    pass_with_concerns → 通行可、fail* → 修正待ち、無 → 未監査. The
    section data carries counts + per-tier rows; the template renders
    counts + tables under the '🚨 cmd_004 audit 状態 alert' heading.
    """
    audit = find_latest_audit_for_pattern(kuroda_entries, audit_id)
    if not audit:
        return {
            "audit_id": audit_id,
            "audit_present": False,
            "audit_timestamp": "",
            "audit_verdict": "",
            "wait_count": 0, "pass_count": 0, "unaudit_count": 0,
            "wait_rows": [], "pass_rows": [], "unaudit_rows": [],
        }
    target_docs = audit.get("target_docs") or []
    wait_rows: list[dict[str, Any]] = []
    pass_rows: list[dict[str, Any]] = []
    unaudit_rows: list[dict[str, Any]] = []
    for doc in target_docs:
        if not isinstance(doc, dict):
            continue
        verdict_raw = doc.get("verdict")
        category = classify_verdict_for_alert(verdict_raw)
        rel_path = _alert_relative_path(str(doc.get("path") or ""))
        size_label = _alert_doc_size_label(rel_path, docs_root)
        row = {
            "id": str(doc.get("id") or ""),
            "path": rel_path,
            "size_label": size_label,
            "verdict": str(verdict_raw or ""),
            "status_display": _alert_status_display(verdict_raw),
        }
        if category == "pass":
            pass_rows.append(row)
        elif category == "wait":
            wait_rows.append(row)
        else:
            unaudit_rows.append(row)
    return {
        "audit_id": audit.get("audit_id", audit_id),
        "audit_present": True,
        "audit_timestamp": str(audit.get("timestamp", "")),
        "audit_verdict": str(audit.get("verdict", "")),
        "wait_count": len(wait_rows),
        "pass_count": len(pass_rows),
        "unaudit_count": len(unaudit_rows),
        "wait_rows": wait_rows,
        "pass_rows": pass_rows,
        "unaudit_rows": unaudit_rows,
    }


# ---------------------------------------------------------------------------
# cycle5: 子項目 summary line 一目視認 format
#   各子項目の machine state から pct + 1 行現状 を計算し、全体進捗 § と同形式の
#   progress bar (= progress_bar_html、4 色 tier 80/50/25/0 retain) を summary 行に流す。
#   詳細 5 項 grandchildren は <details> 既装備で default collapsed (= cycle4 retain)。
# ---------------------------------------------------------------------------


def compute_child_machine_state(
    child: dict[str, Any],
    *,
    kuroda_entries: list[dict[str, Any]] | None = None,
    shogun_entries: list[dict[str, Any]] | None = None,
    w9_batches: list[dict[str, Any]] | None = None,
    w9_stages: list[dict[str, Any]] | None = None,
    repo: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Resolve child progress-pct + raw machine state used by summary line.

    pct は audit/shogun_verified/commit の有無から段階決定 (= 黒田推奨 80/50/25/0 tier 整合)。
    w9_batch/w9_stage は aggregate avg_pct を直接流用。data 不在は捏造禁 (= 黒田 cycle4 条件 1)。
    """
    kuroda_entries = kuroda_entries if kuroda_entries is not None else []
    shogun_entries = shogun_entries if shogun_entries is not None else []
    kind = child.get("kind")

    # cycle6: Supabase development_progress 直接参照 (= 50 件 verify list).
    # status → pct: completed=90 / in_progress=50 / not_started=0、捏造禁。
    if kind == "supabase_phase":
        status = str(child.get("external_status", ""))
        if status == "completed":
            pct = 90.0
        elif status == "in_progress":
            pct = 50.0
        elif status == "not_started":
            pct = 0.0
        else:
            pct = 0.0  # unknown / blank → 0、source_unavailable 経路
        return {
            "kind": "supabase_phase",
            "pct": pct,
            "external_status": status,
            "external_source": str(child.get("external_source", "")),
            "external_commit": str(child.get("external_commit", "")),
        }

    if kind == "w9_batch":
        batch_id = str(child.get("batch", ""))
        match = next(
            (r for r in (w9_batches or []) if str(r.get("batch", "")) == batch_id),
            None,
        )
        if match:
            base_pct = float(match.get("avg_pct") or 0.0)
            sv = find_latest_shogun_verified(
                shogun_entries,
                str(child.get("shogun_target_pattern", "")),
            )
            sv_pct = _shogun_verified_pct(sv)
            return {
                "kind": "w9_batch",
                "pct": max(base_pct, sv_pct) if sv else base_pct,
                "task_count": int(match.get("task_count") or 0),
                "batch": batch_id,
                "shogun_verified": sv is not None,
                "verified_at": str(sv.get("verified_at", "")) if sv else "",
            }
        return {"kind": "w9_batch_missing", "pct": 0.0, "batch": batch_id}

    if kind == "w9_stage":
        stage = str(child.get("stage", ""))
        match = next(
            (r for r in (w9_stages or []) if str(r.get("stage", "")) == stage),
            None,
        )
        if match:
            base_pct = float(match.get("avg_pct") or 0.0)
            sv = find_latest_shogun_verified(
                shogun_entries,
                str(child.get("shogun_target_pattern", "")),
            )
            sv_pct = _shogun_verified_pct(sv)
            return {
                "kind": "w9_stage",
                "pct": max(base_pct, sv_pct) if sv else base_pct,
                "task_count": int(match.get("task_count") or 0),
                "scored_count": int(match.get("scored_count") or 0),
                "stage": stage,
                "shogun_verified": sv is not None,
                "verified_at": str(sv.get("verified_at", "")) if sv else "",
            }
        return {"kind": "w9_stage_missing", "pct": 0.0, "stage": stage}

    design_doc = str(child.get("design_doc", ""))
    audit_pattern = str(child.get("audit_id_pattern", ""))
    shogun_pattern = str(child.get("shogun_target_pattern", "")) or audit_pattern

    commit_info = git_log_for_path(design_doc, repo=repo) if design_doc else {}
    audit_match = find_latest_audit_for_pattern(kuroda_entries, audit_pattern) if audit_pattern else None
    verif_match = find_latest_shogun_verified(shogun_entries, shogun_pattern) if shogun_pattern else None

    audit_verdict = str(audit_match.get("verdict", "")) if audit_match else ""
    has_commit = bool(commit_info)
    has_audit = bool(audit_match)
    has_shogun_verified = bool(verif_match)

    # tier 段階 (= 80/50/25/0 整合):
    #   shogun_verified=true (no concerns)        → 100.0 (🟢 信長殿 verify pure pass)
    #   shogun_verified=true (pass_with_concerns) →  90.0 (🟢 信長殿 verify w/ concerns)
    #   audit pass/pass_with_concerns             →  60.0 (🟡 進行中、黒田 PASS 受領済)
    #   audit fail/その他                          →  30.0 (🟠 着手、黒田 fail で要 redo)
    #   commit のみ                                →  25.0 (🟠 着手中、未監査)
    #   何もなし                                   →   0.0 (🔴 未着手)
    # cycle11 黒田条件 #4: 100% vs 90% semantics 整理 — shogun verify が clean pass
    # の場合 100% (新)、pass_with_concerns 等が記録されている場合 90% (cycle9 v2 retain)。
    if has_shogun_verified:
        pct = _shogun_verified_pct(verif_match)
    elif has_audit and audit_verdict in ("pass", "pass_with_concerns"):
        pct = 60.0
    elif has_audit:
        pct = 30.0
    elif has_commit:
        pct = 25.0
    else:
        pct = 0.0

    return {
        "kind": "standard",
        "pct": pct,
        "commit_hash": commit_info.get("hash", "") if commit_info else "",
        "audit_verdict": audit_verdict,
        "audit_id": str(audit_match.get("audit_id", "")) if audit_match else "",
        "shogun_verified": has_shogun_verified,
        "verified_at": str(verif_match.get("verified_at", "")) if verif_match else "",
    }


def _shogun_verified_pct(verif_match: dict[str, Any] | None) -> float:
    """cycle11 100%/90% split for an active shogun_verified entry.

    Default = 100.0 (= 信長殿 verify clean pass). When the entry retains a
    kuroda_verdict_original 含む "concerns" / "conditions" 文言 (= 黒田監査が
    pass_with_concerns / pass_with_conditions だった事実が ledger に残っている)、
    あるいは entry 自身の verdict / overall_verdict に "concerns" が含まれる場合
    のみ 90.0 に落とす。cycle9 v2 既装備 helper (= find_latest_shogun_verified)
    の戻り値を直接受け取る方式ゆえ重複実装無し (= 黒田条件 #3 整合)。
    """
    if not verif_match:
        return 0.0
    haystack = " ".join(
        str(verif_match.get(k, "") or "").lower()
        for k in ("kuroda_verdict_original", "verdict", "overall_verdict")
    )
    if "concerns" in haystack or "conditions" in haystack:
        return 90.0
    return 100.0


def compute_shogun_reflection_stats(
    children: list[dict[str, Any]],
    shogun_entries: list[dict[str, Any]],
    *,
    kuroda_entries: list[dict[str, Any]] | None = None,
    w9_batches: list[dict[str, Any]] | None = None,
    w9_stages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """cycle11 黒田条件 #2 — global shogun_verified reflection coverage stats.

    Returns the 5-axis report required for cycle 11 acceptance plus an
    aggregate 緑化率 across all children (= pct >= 80 = 🟢 tier、
    supabase_phase completed 等の 90% も含む):

      children_total            — sum of LAYER_CHILDREN count (=全 Layer 子項目)
      mapped_count              — children with shogun_target_pattern /
                                  audit_id_pattern (= verify match 可能側)
      matched_count             — mapped children that resolved an active
                                  shogun_verified=true entry
      green_count               — children with computed pct >= 80 across
                                  all tiers (= supabase completed + audit pass
                                  以上 + shogun_verified pure pass を合算)
      green_pct                 — green_count / children_total * 100 (= 緑化率)
      children_without_match    — mapped child IDs with no shogun match
      unmatched_verified_targets — active entries whose target/audit_id_ref
                                  matches no child pattern (= 対外 verify 等)
      active_entries_total       — total entries surviving _is_active filter

    既存 helper (find_latest_shogun_verified / _is_active_shogun_entry /
    compute_child_machine_state) を経由 (= 黒田条件 #3 既存 helper 再利用、
    重複実装禁)。
    """
    kuroda_entries = kuroda_entries if kuroda_entries is not None else []
    active_entries = [v for v in shogun_entries if _is_active_shogun_entry(v)]

    mapped_children: list[dict[str, Any]] = []
    matched_children: list[dict[str, Any]] = []
    children_without_match: list[str] = []
    eligible_count = 0
    green_count = 0

    _trackable_kinds = {"supabase_phase", "w9_batch", "w9_stage"}
    for child in children:
        shogun_pat = str(child.get("shogun_target_pattern", ""))
        audit_pat = str(child.get("audit_id_pattern", ""))
        effective_pat = shogun_pat or audit_pat
        kind = str(child.get("kind", "") or "")
        # 子項目が verification mechanism を持つか否か (= 緑化率分母 eligible)
        # mechanism = pattern 装着 or supabase_phase / w9_* kind。Layer A/D 等の
        # 構造 placeholder は eligible から除外し、空評価 children を緑化率分母から外す。
        is_eligible = bool(effective_pat) or kind in _trackable_kinds
        if is_eligible:
            eligible_count += 1
        if effective_pat:
            mapped_children.append(child)
            match = find_latest_shogun_verified(active_entries, effective_pat)
            if match:
                matched_children.append(child)
            else:
                children_without_match.append(str(child.get("id", "")))
        # Green tier = pct >= 80, computed via existing state helper
        # (= 既存 helper 再利用、重複実装禁)。supabase_phase completed (90%)
        # + shogun_verified clean (100%) + with_concerns (90%) を含む。
        state = compute_child_machine_state(
            child,
            kuroda_entries=kuroda_entries,
            shogun_entries=shogun_entries,
            w9_batches=w9_batches,
            w9_stages=w9_stages,
        )
        if float(state.get("pct", 0.0) or 0.0) >= 80.0:
            green_count += 1

    # Unmatched entries: scan every active entry, mark "matched" iff any
    # mapped child's pattern is a substring of target/audit_id_ref.
    unmatched: list[dict[str, str]] = []
    for v in active_entries:
        target = str(v.get("target", "")).lower()
        audit_id_ref = str(v.get("audit_id_ref", "")).lower()
        matched_by_any = False
        for child in mapped_children:
            shogun_pat = str(child.get("shogun_target_pattern", "")).lower()
            audit_pat = str(child.get("audit_id_pattern", "")).lower()
            effective_pat = shogun_pat or audit_pat
            if not effective_pat:
                continue
            if effective_pat in target or effective_pat in audit_id_ref:
                matched_by_any = True
                break
        if not matched_by_any:
            unmatched.append({
                "target": str(v.get("target", "")),
                "audit_id_ref": str(v.get("audit_id_ref", "")),
                "verified_at": str(v.get("verified_at", "")),
            })

    children_total = len(children)
    # 緑化率 = 🟢 tier 子項目 / verification mechanism を持つ子項目 (= eligible)。
    # Layer A/D 等の純粋構造 placeholder (= mechanism 不在) は分母から外す事で、
    # 「verify 可能 children のうち green tier 達成割合」という意味的に正しい指標化。
    # children_total に対する overall 率も別 field で報告 (= green_pct_overall)。
    green_pct = (green_count / eligible_count * 100.0) if eligible_count else 0.0
    green_pct_overall = (green_count / children_total * 100.0) if children_total else 0.0

    return {
        "children_total": children_total,
        "eligible_count": eligible_count,
        "mapped_count": len(mapped_children),
        "matched_count": len(matched_children),
        "green_count": green_count,
        "green_pct": round(green_pct, 1),
        "green_pct_overall": round(green_pct_overall, 1),
        "children_without_match": children_without_match,
        "unmatched_verified_targets": unmatched,
        "active_entries_total": len(active_entries),
    }


def format_child_status_line(state: dict[str, Any]) -> str:
    """Render the 1-line current-status string for a child summary row.

    Mapping (= karo task spec):
      🟢 完成監査済 → "commit <hash>, 黒田 <verdict>"
      🟡 進行中    → "進行中 (黒田 <verdict>)"
      🟠 着手     → "着手 (commit <hash>)"
      🔴 未着     → "未着手"
    w9_batch/w9_stage は集計値 (avg_pct + 件数) を流用。捏造禁。
    """
    kind = str(state.get("kind", ""))
    pct = float(state.get("pct") or 0.0)

    if kind == "supabase_phase":
        status = str(state.get("external_status", ""))
        if status == "completed":
            return "完成 (Supabase development_progress)"
        if status == "in_progress":
            return "進行中 (Supabase development_progress)"
        if status == "not_started":
            return "未着手 (Supabase development_progress)"
        return "未照合 (Supabase status_unknown)"

    if kind == "w9_batch":
        return f"batch{state.get('batch', '?')} 平均 {pct:.1f}% ({state.get('task_count', 0)} 件)"
    if kind == "w9_stage":
        return (
            f"Stage {state.get('stage', '?')} 平均 {pct:.1f}% "
            f"({state.get('scored_count', 0)}/{state.get('task_count', 0)} 件)"
        )
    if kind in ("w9_batch_missing", "w9_stage_missing"):
        return "未着 (集計値不在)"

    # standard child
    if pct >= 80.0:
        h = state.get("commit_hash") or "(未 commit)"
        v = state.get("audit_verdict") or "(verdict 不在)"
        return f"完成監査済 (commit `{h}`, 黒田 {v})"
    if pct >= 50.0:
        v = state.get("audit_verdict") or "監査待ち"
        return f"進行中 (黒田 {v})"
    if pct >= 25.0:
        h = state.get("commit_hash") or "未 commit"
        return f"着手 (commit `{h}`、監査未)"
    return "未着手"


def build_layer_render_entries(
    *,
    kuroda_entries: list[dict[str, Any]] | None = None,
    shogun_entries: list[dict[str, Any]] | None = None,
    w9_stages: list[dict[str, Any]] | None = None,
    w9_batches: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build layer dicts (= LAYER_DEFINITIONS extended with children + evidence) for template."""
    kuroda_entries = kuroda_entries if kuroda_entries is not None else []
    shogun_entries = shogun_entries if shogun_entries is not None else []
    entries: list[dict[str, Any]] = []
    for layer in LAYER_DEFINITIONS:
        children = children_for_layer(layer["code"])
        rendered_children = []
        for child in children:
            evidence = extract_child_evidence(
                child,
                kuroda_entries=kuroda_entries,
                shogun_entries=shogun_entries,
                w9_batches=w9_batches,
                w9_stages=w9_stages,
            )
            state = compute_child_machine_state(
                child,
                kuroda_entries=kuroda_entries,
                shogun_entries=shogun_entries,
                w9_batches=w9_batches,
                w9_stages=w9_stages,
            )
            pct = float(state.get("pct") or 0.0)
            rendered_children.append({
                "id": child["id"],
                "label": child["label"],
                "evidence": evidence,
                "evidence_inline": build_inline_evidence(evidence),
                "pct": pct,
                "progress_bar": progress_bar_html(pct, width_px=180, height_px=12),
                "status_line": format_child_status_line(state),
            })
        entries.append({
            **layer,
            "children": rendered_children,
            "child_count": len(rendered_children),
        })
    return entries


# F3 cycle2 fix: privacy gate 語彙統一 — WARN 残存は CLEAN ではない。
PRIVACY_CLEAN = "clean"
PRIVACY_WARNED = "warned"
PRIVACY_BLOCKED = "blocked"


def classify_privacy_result(reports: Any) -> str:
    """Map validate_report_privacy.py JSON output to a canonical verdict.

    'clean' iff HIGH 0 AND WARN 0. WARN-only results are 'warned', NOT 'clean'.
    'blocked' iff any HIGH > 0. Accepts a list of per-file result dicts or a
    single dict (mirrors validate_report_privacy.py --format json shape).
    """
    if isinstance(reports, dict):
        reports = [reports]
    high_total = 0
    warn_total = 0
    for r in reports or []:
        high_total += len(r.get("high") or [])
        warn_total += len(r.get("warn") or [])
    if high_total > 0:
        return PRIVACY_BLOCKED
    if warn_total > 0:
        return PRIVACY_WARNED
    return PRIVACY_CLEAN


# ---------------------------------------------------------------------------
# Lock primitives (AC6)
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def generation_lock(lock_path: Path = LOCK_FILE, timeout_sec: float = 0.0):
    """Acquire an exclusive flock; raise BlockingIOError if contended.

    timeout_sec=0 means "fail fast" — Stage 2 timer must not queue overlapping runs.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "w")
    deadline = time.monotonic() + timeout_sec
    while True:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                fh.close()
                raise
            time.sleep(0.1)
    try:
        fh.write(f"{os.getpid()} {_dt.datetime.now().isoformat()}\n")
        fh.flush()
        yield fh
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


# ---------------------------------------------------------------------------
# Git helpers (AC2, AC6)
# ---------------------------------------------------------------------------


def git_head_short(repo: Path = PROJECT_ROOT) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=5,
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


def git_recent_log(repo: Path = PROJECT_ROOT, limit: int = 20) -> list[dict[str, str]]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "log", f"-{limit}",
             "--pretty=format:%h|%s|%ar"],
            stderr=subprocess.DEVNULL, timeout=10,
        ).decode()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []
    entries: list[dict[str, str]] = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            entries.append({"hash": parts[0], "subject": parts[1], "age": parts[2]})
    return entries


def git_head_match(mainpc_head: str, secondpc_head_hint: str | None) -> bool:
    """When running on SC verify mode, both heads must agree.

    secondpc_head_hint may be None when SC head is unknown — in that case the
    gate is informational only (returns True) but the caller should record it.
    """
    if not secondpc_head_hint:
        return True
    return mainpc_head == secondpc_head_hint


# ---------------------------------------------------------------------------
# Local YAML / state source loading (AC2)
# ---------------------------------------------------------------------------


@dataclass
class TaskEntry:
    task_id: str
    assigned_to: str
    status: str
    parent_cmd: str = ""
    bloom_level: str = ""
    persona: str = ""
    verdict: str = ""
    completion_gate: str = ""
    evidence_state: str = ""
    audit_passed: bool = False
    shogun_verified: bool = False
    source_file: str = ""
    raw_status: str = ""


@dataclass
class LoadedState:
    tasks: list[TaskEntry] = field(default_factory=list)
    reports_snapshot: dict[str, dict[str, Any]] = field(default_factory=dict)
    git_log: list[dict[str, str]] = field(default_factory=list)
    source_commit: str = ""
    parse_errors: list[str] = field(default_factory=list)


_PATH_REDACT_RE = re.compile(r"(/home/[^\s\"']+|/mnt/c/[^\s\"']+)")


def _redact_paths(text: str) -> str:
    """Strip absolute Linux / WSL paths from a message to keep privacy gate green."""
    return _PATH_REDACT_RE.sub("<redacted-path>", text)


def _safe_load_all(path: Path) -> list[Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return list(yaml.safe_load_all(fh))
    except (yaml.YAMLError, OSError) as exc:
        return [{"__parse_error__": _redact_paths(f"{path.name}: {exc}")}]


def _rel_to_repo(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _coerce_task(raw: Any, source_file: Path) -> TaskEntry | None:
    if not isinstance(raw, dict):
        return None
    block = raw.get("task")
    if not isinstance(block, dict):
        return None
    raw_status = str(block.get("status", "unknown"))
    status = raw_status if raw_status in STATUS_ENUM else "unknown"
    verification = block.get("verification_layer") or {}
    return TaskEntry(
        task_id=str(block.get("task_id", "unknown")),
        assigned_to=str(block.get("assigned_to", "")),
        status=status,
        raw_status=raw_status,
        parent_cmd=str(block.get("parent_cmd", "")),
        bloom_level=str(block.get("bloom_level", "")),
        persona=str(block.get("persona", "")),
        verdict=str(block.get("verdict", "")),
        completion_gate=str(block.get("completion_gate", "")),
        evidence_state=str(block.get("evidence_state", "")),
        audit_passed=bool(verification.get("audit_passed", False) or block.get("audit_passed", False)),
        shogun_verified=bool(verification.get("shogun_verified", False) or block.get("shogun_verified", False)),
        source_file=_rel_to_repo(source_file),
    )


def load_local_state(
    tasks_dir: Path | None = None,
    reports_dir: Path | None = None,
) -> LoadedState:
    """Load queue/tasks + queue/reports + git log.

    dashboard.md is intentionally excluded — its content is generator output, not input.
    """
    tasks_dir = tasks_dir if tasks_dir is not None else QUEUE_TASKS_DIR
    reports_dir = reports_dir if reports_dir is not None else QUEUE_REPORTS_DIR
    state = LoadedState(source_commit=git_head_short(), git_log=git_recent_log())

    if tasks_dir.is_dir():
        for path in sorted(tasks_dir.glob("ashigaru*.yaml")):
            for doc in _safe_load_all(path):
                if isinstance(doc, dict) and "__parse_error__" in doc:
                    state.parse_errors.append(doc["__parse_error__"])
                    continue
                entry = _coerce_task(doc, path)
                if entry is not None:
                    state.tasks.append(entry)

    if reports_dir.is_dir():
        for path in sorted(reports_dir.glob("*.yaml")):
            if path.name == DASHBOARD_FILE.name:
                continue  # safety belt — dashboard.md never appears here, but be explicit.
            try:
                stat = path.stat()
            except OSError:
                continue
            state.reports_snapshot[path.name] = {
                "size": stat.st_size,
                "mtime": _dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "stale": _is_stale(stat.st_mtime),
            }

    return state


def _is_stale(mtime_epoch: float, threshold_days: int = STALE_THRESHOLD_DAYS) -> bool:
    age = _dt.datetime.now().timestamp() - mtime_epoch
    return age > threshold_days * 86400


# ---------------------------------------------------------------------------
# Memory MCP fallback (AC3)
# ---------------------------------------------------------------------------


def load_memory_snapshot(snapshot_path: Path | None = None, max_chars: int = 4000) -> dict[str, Any]:
    """Read memory/MEMORY.md snapshot as MCP read_graph fallback.

    Timer-driven systemd units cannot reach the Claude MCP server, so the snapshot
    file is the only durable source.
    """
    if snapshot_path is None:
        snapshot_path = MEMORY_FILE
    if not snapshot_path.exists():
        return {"available": False, "reason": "memory_snapshot_missing", "head_lines": []}
    try:
        text = snapshot_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"available": False, "reason": f"read_failed:{exc}", "head_lines": []}
    head = "\n".join(text.splitlines()[:80])
    return {
        "available": True,
        "byte_size": len(text.encode("utf-8")),
        "head_lines": head[:max_chars].splitlines(),
        "source": _rel_to_repo(snapshot_path),
    }


# ---------------------------------------------------------------------------
# Supabase REST + ETag cache (AC1)
# ---------------------------------------------------------------------------


@dataclass
class FetchResult:
    table: str
    status: int
    cache_hit: bool
    row_count: int | None
    error: str | None
    permission_denied: bool
    bytes_received: int
    cache_path: str


def _cache_paths(table: str) -> tuple[Path, Path]:
    base = CACHE_DIR / table
    return base.with_suffix(".json"), base.with_suffix(".etag")


def fetch_table(
    table: dict[str, Any],
    base_url: str,
    anon_key: str,
    timeout: float = 8.0,
    opener: Any | None = None,
) -> FetchResult:
    """Single-table REST GET + ETag negotiation.

    On 304: return cached payload (cache_hit=True).
    On 200: write cache + new ETag.
    On 401/403: permission_denied=True.
    On network timeout or 5xx: fall back to cache when available, else error.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path, etag_path = _cache_paths(table["name"])

    params = {"select": table["select"]}
    if table["strategy"] == "diff":
        params["order"] = "updated_at.desc"
        params["limit"] = "200"
    elif table["strategy"] == "metadata":
        params["limit"] = "100"
    url = f"{base_url.rstrip('/')}/rest/v1/{table['name']}?{urllib.parse.urlencode(params)}"

    headers = {"apikey": anon_key, "Authorization": f"Bearer {anon_key}", "Accept": "application/json"}
    if etag_path.exists():
        headers["If-None-Match"] = etag_path.read_text(encoding="utf-8").strip()

    req = urllib.request.Request(url, headers=headers, method="GET")
    open_fn = opener.open if opener is not None else urllib.request.urlopen
    try:
        resp = open_fn(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and cache_path.exists():
            return FetchResult(table["name"], 304, True, _count_rows(cache_path), None, False, 0, str(cache_path))
        if exc.code in (401, 403):
            return FetchResult(table["name"], exc.code, False, None, f"HTTP {exc.code}", True, 0, str(cache_path))
        if cache_path.exists():
            return FetchResult(table["name"], exc.code, True, _count_rows(cache_path), f"HTTP {exc.code} (stale cache used)", False, 0, str(cache_path))
        return FetchResult(table["name"], exc.code, False, None, f"HTTP {exc.code}", False, 0, str(cache_path))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        if cache_path.exists():
            return FetchResult(table["name"], 0, True, _count_rows(cache_path), f"network:{exc} (stale cache used)", False, 0, str(cache_path))
        return FetchResult(table["name"], 0, False, None, f"network:{exc}", False, 0, str(cache_path))

    body = resp.read()
    new_etag = resp.headers.get("ETag")
    try:
        cache_path.write_bytes(body)
        if new_etag:
            etag_path.write_text(new_etag, encoding="utf-8")
    except OSError:
        pass
    rows = _count_rows_from_bytes(body)
    return FetchResult(table["name"], resp.status, False, rows, None, False, len(body), str(cache_path))


def _count_rows(path: Path) -> int | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return len(data) if isinstance(data, list) else None


def _count_rows_from_bytes(blob: bytes) -> int | None:
    try:
        data = json.loads(blob.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return len(data) if isinstance(data, list) else None


def supabase_preflight(
    tables: Iterable[dict[str, Any]] | None = None,
    base_url: str | None = None,
    anon_key: str | None = None,
    timeout: float = 8.0,
    opener: Any | None = None,
) -> dict[str, Any]:
    base_url = base_url or os.environ.get("SUPABASE_URL", "")
    anon_key = anon_key or os.environ.get("SUPABASE_ANON_KEY", "")
    tables = list(tables) if tables is not None else DEFAULT_TABLES

    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_commit": git_head_short(),
        "tables": [],
        "blocking": False,
    }

    if not base_url or not anon_key:
        report["blocking"] = True
        report["blocker_reason"] = "SUPABASE_URL または SUPABASE_ANON_KEY が不在"
        for tbl in tables:
            report["tables"].append({
                "name": tbl["name"], "status": 0, "cache_hit": False,
                "row_count": None, "permission_denied": True,
                "error": "認証情報不在", "bytes_received": 0,
                "cache_path": str(_cache_paths(tbl["name"])[0]),
            })
        return report

    for tbl in tables:
        result = fetch_table(tbl, base_url, anon_key, timeout=timeout, opener=opener)
        if result.permission_denied:
            report["blocking"] = True
        report["tables"].append({
            "name": result.table, "status": result.status,
            "cache_hit": result.cache_hit, "row_count": result.row_count,
            "permission_denied": result.permission_denied,
            "error": result.error, "bytes_received": result.bytes_received,
            "cache_path": result.cache_path,
        })
    return report


def write_preflight_report(report: dict[str, Any], path: Path = PREFLIGHT_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Progress formula (AC5)
# ---------------------------------------------------------------------------


def progress_for_task(task: TaskEntry) -> float | None:
    """Compute progress percent for a single leaf task.

    Evaluation order is FIXED (black-box tests pin it):
      1. raw_status == 'unknown' or status == 'unknown'  -> None (excluded)
      2. status == 'done':
           a) shogun_verified=true AND completion_gate=open
              AND evidence_state=complete                 -> 100
           b) verdict.startswith('pass') and not 'pass_with'
                                                          -> 100 (verified) / 75 (unverified)
           c) verdict.startswith('pass_with')             -> 75
           d) verdict empty (audit awaits)                -> 75 (capped further by gates)
      3. status in STATUS_STAGE_PCT                       -> stage value
      4. status == 'assigned' AND task_id missing         -> 0 (degenerate)
      5. otherwise                                        -> 0

    Then apply caps:
      - evidence_state in {blocked_env, missing,
        schema_unsupported, cross_pc_missing}             -> min(score, 50)
      - shogun_verified=false                             -> min(score, 75)

    F2 cycle2 fix (黒田 audit): 監査待ち系 (audit_pending /
    completed_pending_audit / done_pending_audit / ready_for_audit) を
    unknown に丸めず、STATUS_STAGE_PCT 経由で明示段階値に。
    """
    if task.raw_status == "unknown" or task.status == "unknown":
        return None

    base: float
    if task.status == "done":
        if (task.shogun_verified
                and task.completion_gate == "open"
                and task.evidence_state == "complete"):
            base = 100.0
        elif task.verdict.startswith("pass") and not task.verdict.startswith("pass_with"):
            base = 100.0 if task.shogun_verified else 75.0
        elif task.verdict.startswith("pass_with"):
            base = 75.0
        else:
            # done without verdict yet — treat as awaiting audit, not 0%.
            base = 75.0
    elif task.status == "assigned":
        # degenerate: assigned without task_id is a placeholder, not progress.
        base = 25.0 if task.task_id else 0.0
    elif task.status in STATUS_STAGE_PCT:
        base = STATUS_STAGE_PCT[task.status]
    else:
        base = 0.0

    if task.evidence_state in {"blocked_env", "missing", "schema_unsupported", "cross_pc_missing"}:
        base = min(base, 50.0)
    # shogun_verified=false cap only blocks 'done' from claiming 100% — stage
    # values 80/85/90/95 are explicit "awaiting verification" markers and must
    # surface as-is (cycle1 universally capped them at 75 which hid progress).
    if task.status == "done" and not task.shogun_verified:
        base = min(base, 75.0)
    return base


def aggregate_progress(tasks: Iterable[TaskEntry]) -> dict[str, Any]:
    weighted_sum = 0.0
    total_weight = 0
    excluded = 0
    per_agent: dict[str, list[float]] = {}
    for task in tasks:
        score = progress_for_task(task)
        if score is None:
            excluded += 1
            continue
        weighted_sum += score
        total_weight += 1
        per_agent.setdefault(task.assigned_to or "unassigned", []).append(score)
    overall = (weighted_sum / total_weight) if total_weight else 0.0
    per_agent_avg = {k: (sum(v) / len(v) if v else 0.0) for k, v in per_agent.items()}
    return {
        "overall_pct": round(overall, 1),
        "leaf_count": total_weight,
        "excluded_count": excluded,
        "per_agent_pct": {k: round(v, 1) for k, v in per_agent_avg.items()},
    }


# ---------------------------------------------------------------------------
# Jinja2 template (AC4)
# ---------------------------------------------------------------------------


DASHBOARD_TEMPLATE = """<!-- auto-generated by scripts/regenerate_dashboard.py — do not hand-edit -->
# DentalBI ダッシュボード (自動生成)

> ⚠️ 本ファイルは `scripts/regenerate_dashboard.py` が単独 writer。
> Karo / Gunshi / Shogun の手動編集は禁止 — state source (queue/reports/, queue/tasks/, memory/MEMORY.md) を更新せよ。
> 手動編集された旧版は `archive/dashboard_legacy_YYYYMMDD.md` へ退避すること。

- 生成時刻 (generated_at): `{{ generated_at }}`
- ソースコミット (source_commit): `{{ source_commit }}`
- 書込PC (writer_pc): `{{ writer_pc }}`
- Supabase接続状態 (supabase_blocking): `{{ supabase.blocking }}`
{% if stale_warning -%}
- ⚠️ 古い report 警告 (stale_warning): {{ stale_warning }}
{%- endif %}

## 🚀 全体進捗 (一目視認)

{{ overall_bar }}

| 末端タスク数 | 除外件数 (不明/古い) |
|---|---|
| {{ progress.leaf_count }} | {{ progress.excluded_count }} |

### エージェント別 進捗

| エージェント | 進捗 | タスク数 |
|---|---|---|
{% for agent, pct in progress.per_agent_pct.items() %}
| {{ agent }} | {{ per_agent_bars.get(agent, pct ~ '%') }} | {{ task_counts.get(agent, 0) }} |
{% endfor %}

## 🚨 cmd_004 audit 状態 alert (= {{ cmd004_audit_alert.wait_count + cmd004_audit_alert.pass_count + cmd004_audit_alert.unaudit_count }} 件)

{% if cmd004_audit_alert.audit_present -%}
> ⚠️ 黒田 audit 完遂結果 (`{{ cmd004_audit_alert.audit_id }}`): **修正待ち {{ cmd004_audit_alert.wait_count }} 件 (privacy sanitization 要)** / **通行可 {{ cmd004_audit_alert.pass_count }} 件** / 未監査 {{ cmd004_audit_alert.unaudit_count }} 件、本日中完遂目標。
{%- else -%}
> ⚠️ 黒田 audit (`{{ cmd004_audit_alert.audit_id }}`) 未検出 — kuroda_mainpc_report.yaml に対象 audit 不在。
{%- endif %}

### 🟠 修正待ち {{ cmd004_audit_alert.wait_count }} 件 (= privacy HIGH 絶対パス/疑似 secret、sanitization 後再監査要)

{% if cmd004_audit_alert.wait_count > 0 -%}
| 優先 | 子項目 | 状態 | 関連 doc |
|---|---|---|---|
{% for row in cmd004_audit_alert.wait_rows -%}
| {{ loop.index }} | 🟠 {{ row.id }} | {{ row.status_display }} | `{{ row.path }}`{% if row.size_label %} ({{ row.size_label }}){% endif %} |
{% endfor %}
{%- else -%}
(修正待ち 0 件)
{%- endif %}

### 🟢 通行可 {{ cmd004_audit_alert.pass_count }} 件 (= 黒田 audit pass、信長殿 verify ledger 待ち)

{% if cmd004_audit_alert.pass_count > 0 -%}
| 優先 | 子項目 | 状態 | 関連 doc |
|---|---|---|---|
{% for row in cmd004_audit_alert.pass_rows -%}
| {{ loop.index }} | 🟢 {{ row.id }} | {{ row.status_display }} | `{{ row.path }}`{% if row.size_label %} ({{ row.size_label }}){% endif %} |
{% endfor %}
{%- else -%}
(通行可 0 件)
{%- endif %}

### 🔴 未監査 {{ cmd004_audit_alert.unaudit_count }} 件

{% if cmd004_audit_alert.unaudit_count > 0 -%}
| 優先 | 子項目 | 関連 doc |
|---|---|---|
{% for row in cmd004_audit_alert.unaudit_rows -%}
| {{ loop.index }} | 🔴 {{ row.id }} | `{{ row.path }}`{% if row.size_label %} ({{ row.size_label }}){% endif %} |
{% endfor %}
{%- else -%}
(現在 0 件、将来 cmd_004 新 design doc 追加時用 placeholder)
{%- endif %}

## 🟢 信長殿 verify ledger 反映状況 (= cycle11 global reflection)

> 信長殿 verify ledger (= `queue/reports/shogun_verification_mainpc_log.yaml`) を全 Layer 子項目に反映。
> shogun_verified=true 子項目は 🟢 緑化 (= clean pass 100% / pass_with_concerns 90%)。legacy_migrated 除外。

- 全 Layer 子項目: **{{ shogun_reflection_stats.children_total }} 件**
- verify mechanism 装着 (= eligible、緑化率分母): **{{ shogun_reflection_stats.eligible_count }} 件**
- shogun_target_pattern / audit_id_pattern 装着 (= mapped): **{{ shogun_reflection_stats.mapped_count }} 件**
- shogun_verified=true match (= matched、緑化対象): **{{ shogun_reflection_stats.matched_count }} 件**
- 🟢 tier 達成 (= pct >= 80、supabase completed + shogun verified を合算): **{{ shogun_reflection_stats.green_count }} 件**
- 🟢 **緑化率: {{ shogun_reflection_stats.green_pct }}%** (= green_count / eligible_count、verify 可能 children 中の達成率)
- 🟢 全体 overall 率: {{ shogun_reflection_stats.green_pct_overall }}% (= green_count / children_total、構造 placeholder 含む)
- active 信長 verify entry 総数: {{ shogun_reflection_stats.active_entries_total }} 件
- mapped 子項目で match 無し: {{ shogun_reflection_stats.children_without_match | length }} 件
- 子項目 mapping 無し verify entry: {{ shogun_reflection_stats.unmatched_verified_targets | length }} 件

## 🗂 6 Layer 構造 (A〜F 構想〜規範 + G 統合)

cmd_020 dashboard 設計 v0.1 / v0.2 の **6 Layer** (= A 構想 / B Phase / C 機能 / D 頭脳蜘蛛の糸 / E 運用 / F 規範) に
Layer **G 統合 (Stage 3-5)** を加えた 7 sub-section が、本 dashboard の全体像。
各 Layer は単一責任 sub-section として `docs/dashboard_layer_<code>_*.md` に anchor を持つ。
HTML drill-down は `<details>` accordion で expand する (= Layer G 仕様準拠)。

{% for layer in layers %}
<details>
<summary><b>Layer {{ layer.code }}:</b> {{ layer.name }} — {{ layer.summary }}</summary>

- 設計 doc anchor: `{{ layer.doc }}`
- data source: {{ layer.data_source }}
- 子項目: {{ layer.child_count }} 件

{% for child in layer.children %}
<details>
<summary>📦 {{ child.id }} {{ child.label }}: {{ child.progress_bar }} — {{ child.status_line }}</summary>

<p><b>commit:</b> {{ child.evidence_inline.commit }} | <b>test:</b> {{ child.evidence_inline.test }} | <b>audit (黒田):</b> {{ child.evidence_inline.audit }} | <b>shogun_verified:</b> {{ child.evidence_inline.shogun_verified }}</p>
<p><b>参照:</b> {{ child.evidence_inline.ref }}</p>

</details>
{% endfor %}

</details>
{% endfor %}

## 🕸 Layer C children mermaid (v0.2 §4.2)

`docs/dashboard_design_v0.2.md §4.2` 整合 — Layer C 機能層 から 会計待ちゼロ作戦 / 小児恐竜王国 / 申し送りエンジン / W9 蜘蛛の糸 への children 接続図。

{{ layer_c_children_mermaid }}

## 🌳 階層 mermaid tree (5 階層 + 10 柱 + 蜘蛛の糸)

`docs/dashboard_layer_a_kousou.md` §4 graph TD を Layer A 構想の機械可視 anchor として転載 (= 縦軸=5 階層、横軸=10 柱、破線=Layer D 蜘蛛の糸接続)。

```mermaid
graph TD
    DD054[DD-054 anchor<br/>5 階層 + 10 柱 原典]
    DD054 --> L0[第 0 層 憲法<br/>DD-010/037/048/054/061]
    L0 --> L1[第 1 層 診療コア<br/>2 号用紙カルテ DD-036]
    L1 --> L2[第 2 層 周辺診療<br/>予約/画像/問診/CRM]
    L2 --> L3[第 3 層 患者接点<br/>PWA/AI チャット/会計]
    L3 --> L4[第 4 層 AI 統合<br/>AI 副院長/画像 AI]
    L4 --> L5[第 5 層 事業推進<br/>AI 副社長]

    P1[1 画像 AI]
    P2[2 歯の状態 DB]
    P3[3 治療計画ナビ]
    P4[4 患者アプリ + AI チャット]
    P5[5 AI 副院長]
    P6[6 処置セット]
    P7[7 リアルタイム会計]
    P8[8 蜘蛛の糸]
    P9[9 AI 副院長+AI 事務長]
    P10[10 AI 副社長]

    L1 --- P2
    L1 --- P6
    L2 --- P1
    L2 --- P3
    L3 --- P4
    L3 --- P7
    L4 --- P5
    L4 --- P8
    L5 --- P9
    L5 --- P10

    P8 -. 蜘蛛の糸 .-> LD[Layer D 頭脳層<br/>法令 8,000+ records]
    P1 -. 蜘蛛の糸 .-> LD
    P3 -. 蜘蛛の糸 .-> LD
    P4 -. 蜘蛛の糸 .-> LD
    P7 -. 蜘蛛の糸 .-> LD
```

## 🎯 cmd_004 W9 Stage 別進捗

cmd_004 W9 タスク群を Stage A (基盤) / Stage B (batch 残) で集計。

| Stage | 平均進捗 | タスク数 |
|---|---|---|
{% for row in w9_stages %}
| Stage {{ row.stage }} | {{ row.bar }} | {{ row.task_count }} |
{% endfor %}

## 📦 cmd_004 W9 batch 別進捗

W9 batch_id 単位の集計 (= batch1 keisan_check / batch2 ui_logic / batch3 check_logic / batch4 validation / batch5 data_quality / batch6 prosthesis / batch7 alert)。

| batch_id | 平均進捗 | タスク数 |
|---|---|---|
{% for row in w9_batches %}
| batch{{ row.batch }} | {{ row.bar }} | {{ row.task_count }} |
{% endfor %}

## タスク一覧 (状態源)

| エージェント | タスクID | 状態 | 判定 | 関門 | 証拠 | 進捗 |
|---|---|---|---|---|---|---|
{% for task in tasks %}
| {{ task.assigned_to }} | `{{ task.task_id }}` | {{ task.status }} | {{ task.verdict }} | {{ task.completion_gate }} | {{ task.evidence_state }} | {{ task_progress.get(task.task_id, 'n/a') }} |
{% endfor %}

## Supabase 接続事前確認

{% if supabase.blocking -%}
🚨 **接続障害**: {{ supabase.get('blocker_reason', '権限拒否を検出') }}
{% endif %}

| テーブル | 状態コード | キャッシュ | 件数 | 備考 |
|---|---|---|---|---|
{% for tbl in supabase.tables %}
| {{ tbl.name }} | {{ tbl.status }} | {{ 'HIT' if tbl.cache_hit else 'MISS' }} | {{ tbl.row_count if tbl.row_count is not none else 'n/a' }} | {{ tbl.error or '' }} |
{% endfor %}

## メモリ取込 (memory MCP フォールバック)

- 取得可: `{{ memory.available }}`
{% if memory.available -%}
- 取得元: `{{ memory.source }}`
- サイズ: {{ memory.byte_size }} バイト
{% else -%}
- 理由: {{ memory.reason }}
{%- endif %}

## 直近コミット

| ハッシュ | 概要 | 経過 |
|---|---|---|
{% for commit in git_log %}
| `{{ commit.hash }}` | {{ commit.subject }} | {{ commit.age }} |
{% endfor %}

## 解析エラー / 品質フラグ

{% if parse_errors -%}
{% for err in parse_errors %}
- {{ err }}
{% endfor %}
{% else -%}
(なし)
{%- endif %}

---
*家老所管 systemd サービスが dashboard.md を書き込み、各エージェント書き込み禁止 — scripts/regenerate_dashboard.py*
"""


def render_dashboard(context: dict[str, Any]) -> str:
    env = jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
    )
    template = env.from_string(DASHBOARD_TEMPLATE)
    return template.render(**context)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_context(
    state: LoadedState,
    supabase_report: dict[str, Any],
    memory_snapshot: dict[str, Any],
    writer_pc: str,
) -> dict[str, Any]:
    task_progress: dict[str, str] = {}
    task_counts: dict[str, int] = {}
    for task in state.tasks:
        score = progress_for_task(task)
        task_progress[task.task_id] = "excluded" if score is None else f"{round(score, 0):.0f}%"
        task_counts[task.assigned_to or "unassigned"] = task_counts.get(task.assigned_to or "unassigned", 0) + 1

    stale_reports = [name for name, info in state.reports_snapshot.items() if info["stale"]]
    stale_warning = (
        f"{len(stale_reports)} 件の report が {STALE_THRESHOLD_DAYS} 日以上未更新: " + ", ".join(stale_reports[:5])
        if stale_reports else ""
    )

    progress = aggregate_progress(state.tasks)
    overall_bar = progress_bar_html(progress["overall_pct"], width_px=420, height_px=24)
    per_agent_bars = {
        agent: progress_bar_html(pct, width_px=180, height_px=12)
        for agent, pct in progress["per_agent_pct"].items()
    }

    w9_stage_rows = aggregate_w9_stage_progress(state.tasks)
    for row in w9_stage_rows:
        row["bar"] = progress_bar_html(row["avg_pct"], width_px=180, height_px=12)
    w9_batch_rows = aggregate_w9_batch_progress(state.tasks)
    for row in w9_batch_rows:
        row["bar"] = progress_bar_html(row["avg_pct"], width_px=180, height_px=12)

    # cycle4: Layer 子項目 + 孫項目 (= 5 項固定 grandchildren) を機械抽出。
    # 不在時は fallback (= "(黒田監査未)" / "false" 等)、捏造禁。
    kuroda_entries = load_kuroda_index()
    shogun_entries = load_shogun_verification_index()
    layers_with_children = build_layer_render_entries(
        kuroda_entries=kuroda_entries,
        shogun_entries=shogun_entries,
        w9_stages=w9_stage_rows,
        w9_batches=w9_batch_rows,
    )
    cmd004_audit_alert = build_cmd004_audit_alert_section(kuroda_entries)
    # cycle11: global shogun_verified reflection stats (= 黒田条件 #2)。
    # LAYER_CHILDREN (= 静的 SoT) を直接 source とする — build_layer_render_entries の
    # rendered_children は audit_id_pattern 等を含まないため、stats 計測は raw 子項目
    # 定義側で行う (= 既存 helper 流用、黒田条件 #3 整合)。
    shogun_reflection_stats = compute_shogun_reflection_stats(
        LAYER_CHILDREN, shogun_entries,
        kuroda_entries=kuroda_entries,
        w9_batches=w9_batch_rows,
        w9_stages=w9_stage_rows,
    )

    return {
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_commit": state.source_commit,
        "writer_pc": writer_pc,
        "stale_warning": stale_warning,
        "progress": progress,
        "overall_bar": overall_bar,
        "per_agent_bars": per_agent_bars,
        "task_counts": task_counts,
        "task_progress": task_progress,
        "tasks": state.tasks,
        "supabase": supabase_report,
        "memory": memory_snapshot,
        "git_log": state.git_log,
        "parse_errors": state.parse_errors,
        "layers": layers_with_children,
        "layer_c_children_mermaid": LAYER_C_CHILDREN_MERMAID,
        "w9_stages": w9_stage_rows,
        "w9_batches": w9_batch_rows,
        "cmd004_audit_alert": cmd004_audit_alert,
        "shogun_reflection_stats": shogun_reflection_stats,
    }


# F4 cycle2 fix: 初回本番 write 前に手動編集 dashboard.md を archive へ退避。
# auto-generated header の有無で legacy 判定 (idempotent — generator output には
# 再 archive しない)。
_LEGACY_HEADER_MARKERS = ("auto-generated", "scripts/regenerate_dashboard.py")


def _archive_legacy_dashboard(target: Path, archive_dir: Path | None = None) -> Path | None:
    """Archive a hand-edited dashboard.md before the generator overwrites it.

    Returns the archive destination if archiving happened, else None.
    Subsequent runs (where target already carries the auto-generated banner)
    are no-ops, so the archive is created at most once per legacy file per day.
    """
    if archive_dir is None:
        archive_dir = ARCHIVE_DIR
    if not target.exists():
        return None
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if all(marker in text for marker in _LEGACY_HEADER_MARKERS):
        return None  # already generator output
    archive_dir.mkdir(parents=True, exist_ok=True)
    today = _dt.datetime.now().strftime("%Y%m%d")
    base_name = f"dashboard_legacy_{today}.md"
    dest = archive_dir / base_name
    n = 1
    while dest.exists():
        dest = archive_dir / f"dashboard_legacy_{today}_{n}.md"
        n += 1
    dest.write_text(text, encoding="utf-8")
    return dest


def write_output(rendered: str, output_path: Path, archive_dir: Path | None = None) -> None:
    archived = _archive_legacy_dashboard(output_path, archive_dir)
    if archived is not None:
        print(f"[regenerate_dashboard] archived legacy {output_path.name} -> {archived}",
              file=sys.stderr)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(output_path)


# F1 cycle2 fix (kuroda audit verify_time_delta): rendered 全文比較は
# generated_at と git_log の relative age が時刻 drift で必ず割れるため
# AC6 verify-only mode が運用不能。verify 直前に非決定値を mask する。
_VERIFY_VOLATILE_PATTERNS = (
    # ヘッダ 生成時刻 (generated_at): `2026-05-11T22:00:00+09:00`
    # cycle3 (i18n): 旧 "- generated_at: `..`" / 新 "- 生成時刻 (generated_at): `..`" 双方対応。
    re.compile(r"^- (?:generated_at|生成時刻 \(generated_at\)): `[^`]+`\s*$", re.MULTILINE),
    # 表行 | hash | subject | 5 minutes ago | (最終列が age)
    re.compile(r"^(\| `[0-9a-fA-F]+` \| [^|\n]+ \|)([^|\n]*)\|\s*$", re.MULTILINE),
)


def _normalize_for_verify(text: str) -> str:
    """Strip wall-clock / relative-age values so verify is time-stable.

    Reproducer (kuroda 21:47 audit): write tmp output → sleep 2 → --verify
    → previously rc=1 (generated_at 2 sec apart). After normalization both
    sides hash identically because the volatile span is masked.
    """
    out = _VERIFY_VOLATILE_PATTERNS[0].sub("- 生成時刻 (generated_at): `<volatile>`", text)
    out = _VERIFY_VOLATILE_PATTERNS[1].sub(r"\1 <volatile> |", out)
    return out


def verify_dashboard(expected: str, actual_path: Path) -> bool:
    if not actual_path.exists():
        return False
    actual = actual_path.read_text(encoding="utf-8")
    expected_n = _normalize_for_verify(expected)
    actual_n = _normalize_for_verify(actual)
    return (
        hashlib.sha256(expected_n.encode("utf-8")).hexdigest()
        == hashlib.sha256(actual_n.encode("utf-8")).hexdigest()
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate dashboard.md from state sources")
    parser.add_argument("--preflight", action="store_true", help="Only run Supabase preflight + write report")
    parser.add_argument("--dry-run", action="store_true", help="Render to stdout / tmp without overwriting dashboard.md")
    parser.add_argument("--writer-pc", default="mainpc", choices=["mainpc", "secondpc"],
                        help="Identify writer PC (MC primary, SC verify-only)")
    parser.add_argument("--verify", action="store_true", help="Verify-only mode (SC): compare existing dashboard.md hash")
    parser.add_argument("--output", default=str(DASHBOARD_FILE), help="Override output path")
    parser.add_argument("--no-supabase", action="store_true", help="Skip Supabase fetch (use cache only)")
    parser.add_argument("--memory-snapshot", default=str(MEMORY_FILE), help="Override MEMORY.md path")
    parser.add_argument("--secondpc-head", default=None,
                        help="Optional SC HEAD hint; mismatched HEAD fails the generator")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.writer_pc == "secondpc" and not args.verify:
        print("[regenerate_dashboard] SC must run with --verify; MC is primary writer", file=sys.stderr)
        return 1

    if args.preflight:
        report = supabase_preflight()
        write_preflight_report(report)
        print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
        return 2 if report["blocking"] else 0

    try:
        with generation_lock():
            state = load_local_state()
            mainpc_head = state.source_commit
            if args.secondpc_head and not git_head_match(mainpc_head, args.secondpc_head):
                print(f"[regenerate_dashboard] HEAD mismatch MC={mainpc_head} SC={args.secondpc_head}", file=sys.stderr)
                return 1

            if args.no_supabase:
                supabase_report = {
                    "schema_version": 1,
                    "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                    "source_commit": state.source_commit,
                    "tables": [], "blocking": False, "skipped": True,
                }
            else:
                supabase_report = supabase_preflight()
                write_preflight_report(supabase_report)

            memory = load_memory_snapshot(Path(args.memory_snapshot))
            context = build_context(state, supabase_report, memory, args.writer_pc)
            rendered = render_dashboard(context)

            if args.verify:
                ok = verify_dashboard(rendered, Path(args.output))
                print("verify: ok" if ok else "verify: mismatch", file=sys.stderr)
                return 0 if ok else 1

            if args.dry_run:
                sys.stdout.write(rendered)
                return 0

            write_output(rendered, Path(args.output))
            print(f"[regenerate_dashboard] wrote {args.output} ({len(rendered)} bytes, head={state.source_commit})")
            stats = context.get("shogun_reflection_stats", {})
            if stats:
                print(
                    "[regenerate_dashboard] shogun_reflection: "
                    f"children_total={stats.get('children_total', 0)} "
                    f"eligible={stats.get('eligible_count', 0)} "
                    f"mapped={stats.get('mapped_count', 0)} "
                    f"matched={stats.get('matched_count', 0)} "
                    f"green_count={stats.get('green_count', 0)} "
                    f"green_pct={stats.get('green_pct', 0.0)}% "
                    f"green_pct_overall={stats.get('green_pct_overall', 0.0)}% "
                    f"active_entries={stats.get('active_entries_total', 0)} "
                    f"unmatched_verified_targets={len(stats.get('unmatched_verified_targets', []))} "
                    f"children_without_match={len(stats.get('children_without_match', []))}",
                    file=sys.stderr,
                )
            return 0
    except BlockingIOError:
        print("[regenerate_dashboard] generation_lock contended", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
