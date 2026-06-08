#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fukuincho_desktop_poke.py — 段階3 全自動ループ poke actuator (third_pc 本 repo canonical source)

設計章節正本: docs/08-ops/fukuincho-stage3-auto-loop-design.md
  - commit f1c268d (SHA256=fcf49731df98d812ad83a3d078e01afff306c13e6b867cbc033f3541ab95fb1b)
  - 副院長令 77bd5c6e P0 + 理事長殿 D-lane 承認 (2026-06-07)
  - parent_handshake: 副院長令 341654e4 (4 件全承認反映 — N=30s / main_pc paint / clipboard test / Boy-Scout)
  - governing audit: subtask_thirdpc_p1_fukuincho_stage3_design_governing_audit_001 (Boy-Scout G1)

担当層: ② poke 自動発火層 (段階2 a3-3 実証済 actuator、stage3-poke-engine 再利用)
         + ④ 誤爆抑制層 (dedupe + 応答中 skip + skip_max)

実装方針 (FKI-NO-DUP 順守):
  - 段階2 19:36:37 実証経路 = descendants(control_type=Edit) cands[0] + clipboard+Enter + refined V5 guard
  - main_pc 側 source paint 済 (副院長殿御差配 341654e4 (b) 承認、設計章節 §1.4)
  - ack リトライ N=30s/M=3/backoff 30-60-120s (素案値 50a1b936 + 341654e4 (a) 承認)
  - 誤爆抑制 dedupe T=60s sliding window (last-fire timestamp、固定 bucket 不使用 — Codex cycle2 B1 是正)
  - 応答中 skip = editing 3条件AND + submission inflight 3条件AND (a3-3 mitigation_a/d)
  - skip_max=5 (無限 re-enqueue 防止、Codex cycle1 B1 是正)
  - clipboard test 観点 (§5.1 #12/#13/#14、341654e4 (c) 承認):
      * save→set→Enter→restore 正常系
      * Enter 失敗時 finally restore
      * 構造化ログに clipboard 実値非混入 (error-design §14)

絶対前提順守:
  - V5 (handshake 8012f18c) 触接ゼロ (window title 'V5' / 'Claude' / 'Playwright' 検出時即停止)
  - WSL Python 介在禁 (Windows Python 3.13 only)
  - 機密 2 件 (hermes_ro PW + Supabase token) 触接禁
  - DD-157 役職名のみ (戦国 persona 名禁、persona_name_guard.sh hook 通過必達)
  - FKI-NO-DUP 第4条: 新規 transport / poller / retry loop ゼロ (orchestration 入れ子のみ)

★Note (透明性、e3c6baff 整合)★:
  本 file = third_pc 本 repo canonical source。実 deploy = D-lane 別 task (理事長承認後 main_pc 反映)。
  third_pc 上で本 file を import すると pywinauto は ImportError になる (Windows native のみ) — これは仕様。
  syntax check (python -m py_compile) は third_pc 上で可能。
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

# ───────────────────────────────────────────────────────────
# 素案値 verbatim (50a1b936 + 副院長令 341654e4 承認)
# ───────────────────────────────────────────────────────────
CRON_INTERVAL_SEC = 60          # cron 検知 polling 間隔
STALE_THRESHOLD_SEC = 120       # response_by_time 超過 stale 判定閾値
ACK_N_SEC = 30                  # ack Stage A confirm 間隔 (旧 15s → 副院長令 341654e4 承認)
RETRY_M_MAX = 3                 # 層② GUI actuator retry 上限
BACKOFF_SCHEDULE_SEC = (30, 60, 120)  # M=1/2/3 各間隔
DEDUPE_T_SEC = 60               # 層④ dedupe last-fire TTL sliding window
SKIP_MAX = 5                    # 層④ 応答中 skip 連続上限 (Codex cycle1 B1 是正)

# 段階2 実証経路定数
POKE_PAYLOAD = "確認依頼、コマンダーより"  # 副院長令 24a47356 + 理事長令: 読点+「より」で判別性向上 (旧「確認依頼コマンダー」「確認して」)
TARGET_WINDOW_TITLE_RE = r".*[Cc]laude.*"

# refined V5 guard tokens (case-insensitive substring match)
V5_GUARD_TOKENS = ("v5", "handshake 8012f18c", "commander カルテ", "playwright")


# ───────────────────────────────────────────────────────────
# 構造化ログ (correlation_id 貫通、error-design §14 整合)
# ★clipboard 実値・payload 実値はログ出力禁 (機密混入防止)★
# ───────────────────────────────────────────────────────────
def _build_logger(name: str = "fukuincho_desktop_poke") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


LOG = _build_logger()


def emit_event(event: str, correlation_id: str, **fields) -> None:
    """構造化 JSON 1 行を stdout に emit。

    機密フィールド (clipboard 実値、payload 実値) は ★絶対に渡さない★。
    上位が誤って渡しても _sanitize で除去する。
    """
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "correlation_id": correlation_id,
        "event": event,
    }
    payload.update(_sanitize_log_fields(fields))
    LOG.info(json.dumps(payload, ensure_ascii=False))


_FORBIDDEN_LOG_KEYS = frozenset({
    "clipboard_value", "clipboard_content",
    "payload_value", "payload_text",
    "token", "secret", "password", "api_key",
})


def _sanitize_log_fields(fields: dict) -> dict:
    """構造化ログから機密 key を除去 (実値混入の事故防止、§5.1 #14)。"""
    return {k: v for k, v in fields.items() if k not in _FORBIDDEN_LOG_KEYS}


# ───────────────────────────────────────────────────────────
# refined V5 guard (case-insensitive substring)
# ★window title / process name / CommandLine 由来文字列を check★
# ───────────────────────────────────────────────────────────
def refined_v5_guard(title: str) -> bool:
    """True = guard 違反検出 (即停止すべき)、False = pass。"""
    if not title:
        return False
    low = title.lower()
    return any(tok in low for tok in V5_GUARD_TOKENS)


# ───────────────────────────────────────────────────────────
# dedupe (層④) — last-fire TTL sliding window (固定 bucket 不使用)
# I2 不変条件: now - last_fire_ts < T で抑止、境界 T=60 は厳密未満
# ───────────────────────────────────────────────────────────
@dataclass
class DedupeWindow:
    ttl_sec: int = DEDUPE_T_SEC
    # key = (window_handle, poke_kind) → last_fire_ts (epoch)
    last_fire: dict = field(default_factory=dict)

    def should_fire(self, key: tuple, now: Optional[float] = None) -> bool:
        """True = 発火可、False = dedupe で抑止。

        境界: now - last_fire_ts < ttl → 抑止 (59s=抑止、60s=発火許容、61s=発火許容、§5.1 #3)
        """
        now = now if now is not None else time.time()
        last = self.last_fire.get(key)
        if last is None:
            return True
        return (now - last) >= self.ttl_sec

    def mark_fired(self, key: tuple, now: Optional[float] = None) -> None:
        self.last_fire[key] = now if now is not None else time.time()


# ───────────────────────────────────────────────────────────
# skip_max counter (層④) — correlation_id 単位の応答中 skip 連続計数
# I3 不変条件: skip_max=5 到達で human_required (永久 re-enqueue 排除)
# ───────────────────────────────────────────────────────────
@dataclass
class SkipCounter:
    skip_max: int = SKIP_MAX
    counts: dict = field(default_factory=dict)

    def increment(self, corr_id: str) -> int:
        self.counts[corr_id] = self.counts.get(corr_id, 0) + 1
        return self.counts[corr_id]

    def reset(self, corr_id: str) -> None:
        self.counts.pop(corr_id, None)

    def exceeded(self, corr_id: str) -> bool:
        return self.counts.get(corr_id, 0) >= self.skip_max


# ───────────────────────────────────────────────────────────
# 応答中 skip 検出 (S1/S4 緩和、a3-3 mitigation_a/d)
# editing 3条件AND: IME composition active ∧ Edit get_value() 非空 ∧ focused
# submission inflight 3条件AND: submit button enabled ∧ spinner 非表示 ∧ progress indicator 非active
# ───────────────────────────────────────────────────────────
@dataclass
class BusyDetection:
    ime_active: bool = False
    edit_nonempty: bool = False
    focused: bool = False
    submit_enabled: bool = False
    spinner_hidden: bool = True
    progress_inactive: bool = True

    def is_editing(self) -> bool:
        """3 条件 AND (OR 誤検知率回避、S1 mitigation_a)。"""
        return self.ime_active and self.edit_nonempty and self.focused

    def is_ready_for_submission(self) -> bool:
        """ready (送信可能、idle) 検出 — 3 条件 AND (a3-3 mitigation_d 元文言の literal 解釈)。

        UI 状態: submit button enabled ∧ spinner 非表示 ∧ progress indicator 非active。
        = 入力欄が安定して新規 submit を受け付け得る状態 (busy ではない)。
        """
        return self.submit_enabled and self.spinner_hidden and self.progress_inactive

    def is_submission_inflight(self) -> bool:
        """submission 進行中検出 (redo_002 fix4: 意味反転是正、gunshi-third RED-MED-B3 cure)。

        前 impl の致命誤りは ready 条件を inflight と返し is_busy に OR 連結 → idle を busy 誤判定。
        正しい意味: ★ready 条件が満たされない (= 進行中)★ を True とする。
        """
        return not self.is_ready_for_submission()

    def is_busy(self) -> bool:
        return self.is_editing() or self.is_submission_inflight()


# ───────────────────────────────────────────────────────────
# clipboard test 観点 (§5.1 #12/#13/#14、副院長令 341654e4 (c) 承認)
# save → set → Enter → restore (Enter 失敗時 finally restore)
# 構造化ログに clipboard 実値非混入
# ───────────────────────────────────────────────────────────
def _is_textlike_clipboard(value) -> bool:
    """fix6 (redo_002): clipboard 内容が text 系か判定。

    pyperclip.paste() は通常 str を返すが、image/binary 系を含む場合の clipboard では
    raise or 別 type を返す実装差異がある。str かつ surrogate-free を text 系として扱う。
    bytes / None / non-str は非テキストと判定 (save/restore skip)。
    """
    if value is None:
        return False
    if isinstance(value, (bytes, bytearray)):
        return False
    if not isinstance(value, str):
        return False
    # surrogate を含む場合は明示的に skip (一部 OS で binary 経由 surrogate が混入する)
    try:
        value.encode("utf-8")
    except (UnicodeError, ValueError):
        return False
    return True


def safe_clipboard_poke(
    payload: str,
    set_clip,
    get_clip,
    send_enter,
    correlation_id: str,
) -> tuple[bool, str]:
    """clipboard save/set/Enter/restore を安全実行 (redo_002 fix5/fix6 適用)。

    Args:
        payload: poke ペイロード (実値はログに出さない)
        set_clip: callable(str) -> None  — clipboard セット
        get_clip: callable() -> Any      — clipboard 取得 (非テキスト時も raise しない API 想定)
        send_enter: callable() -> bool   — Enter 送出 (True=成功)
        correlation_id: 構造化ログ correlation_id

    Returns:
        (success, restore_status)
        success: True = Enter 送出成功
        restore_status (final):
            "restored"            — original 退避+復元成功 (set 成功時のみ)
            "restore_failed"      — 復元試行で例外 (set 成功時のみ)
            "no_original_text"    — original が非テキスト (fix6) ゆえ復元 skip
            "save_failed"         — original 取得自体に失敗
            "set_failed"          — payload set 失敗 (Enter 未実行、restore は試行されるが status は set_failed 保持)
            "set_failed_restore_failed" — set 失敗 ∧ restore 失敗 (両 fail を顕在化、cycle3 fix5 MED-3 cure)

    ★fix5 (redo_002)★: restore 結果を finally で最終確定し戻り値に反映する
    (前 impl は send_enter 直後に "pending_restore" を返し、finally の実 restore 結果が
     呼出側に伝達されない欠陥があった。本実装は nonlocal pattern で最終状態を返す)。
    ★fix6 (redo_002)★: 非テキスト clipboard 時の save/restore を skip + log で堅牢化。
    ★cycle3 fix5 (MED-3 cure)★: set 失敗時に restore 成功が "set_failed" を "restored" に
      上書きする欠陥を是正。set 失敗は呼出側に顕在化させる必要があるため (Enter 未実行を
      hide してはならない)、restore 結果に関わらず set_failed を保持する。両 fail 時は
      "set_failed_restore_failed" で両事象を表現。
    ★§5.1 #13/#14★: Enter 失敗時も finally で復元、ログに clipboard 実値・payload 実値非混入。
    """
    original = None
    saved_textlike = False
    final_restore_status = "save_failed"
    result_ok = False
    set_failed = False

    try:
        # ── 退避 (fix6: 非テキスト時 skip) ──
        try:
            raw = get_clip()
        except Exception as e:
            emit_event(
                "clipboard_save_failed",
                correlation_id,
                error_type=type(e).__name__,
            )
            raw = None

        if _is_textlike_clipboard(raw):
            original = raw
            saved_textlike = True
            final_restore_status = "pending"
        elif raw is None:
            final_restore_status = "save_failed"
        else:
            emit_event(
                "clipboard_non_textlike_skipped",
                correlation_id,
                raw_type=type(raw).__name__,
            )
            final_restore_status = "no_original_text"

        # ── set ──
        try:
            set_clip(payload)
        except Exception as e:
            emit_event(
                "clipboard_set_failed",
                correlation_id,
                error_type=type(e).__name__,
            )
            set_failed = True
            final_restore_status = "set_failed"

        # ── Enter 送出 (set 成功時のみ) ──
        if not set_failed:
            try:
                result_ok = bool(send_enter())
            except Exception as e:
                emit_event(
                    "enter_send_failed",
                    correlation_id,
                    error_type=type(e).__name__,
                )
                result_ok = False
    finally:
        # ★finally で必ず復元 試行 (§5.1 #13)、結果を final_restore_status に反映★
        # ★cycle3 fix5 (MED-3 cure)★: set 失敗時は restore 成否に関わらず set_failed を保持
        #   (旧 impl は restore 成功で "set_failed" を "restored" に上書き → Enter 未実行を hide
        #    する設計欠陥。新 impl は set 失敗を顕在化、両 fail 時は set_failed_restore_failed)。
        if saved_textlike and original is not None:
            try:
                set_clip(original)
                emit_event("clipboard_restored", correlation_id)
                if set_failed:
                    # set 失敗 ∧ restore 成功 → set_failed 保持 (Enter 未実行を顕在化)
                    final_restore_status = "set_failed"
                else:
                    # 正常系 (set 成功) → restore 成功で restored 確定
                    final_restore_status = "restored"
            except Exception as e:
                emit_event(
                    "clipboard_restore_failed",
                    correlation_id,
                    error_type=type(e).__name__,
                )
                if set_failed:
                    # 両 fail → 両事象を表現する複合 status
                    final_restore_status = "set_failed_restore_failed"
                else:
                    final_restore_status = "restore_failed"
        # 非テキスト / save_failed / no_original_text は据置 (復元対象なし、set_failed も据置)

    # ★fix5 (redo_002)★: return を try/finally の外に置き、finally 更新後の状態を返す
    return result_ok, final_restore_status


# ───────────────────────────────────────────────────────────
# ack リトライ N=30s / M=3 / backoff (30/60/120s)
# ★ae8083dd 全方向エンジン再利用 (FKI-NO-DUP、新規 retry loop 不新設)★
# 本 file はパラメータ宣言 + backoff schedule 公開のみ。実 retry orchestration は
# omni engine (層③) が担う。本 actuator は単発 fire 関数を提供する。
# ───────────────────────────────────────────────────────────
def backoff_seconds(attempt: int) -> int:
    """1-based attempt → backoff sec (30/60/120)。out-of-range は最後の値。"""
    if attempt < 1:
        return BACKOFF_SCHEDULE_SEC[0]
    idx = min(attempt - 1, len(BACKOFF_SCHEDULE_SEC) - 1)
    return BACKOFF_SCHEDULE_SEC[idx]


# ───────────────────────────────────────────────────────────
# poke actuator entrypoint (descendants/Edit/clipboard+Enter 経路)
# ★段階2 実証経路 = descendants(control_type=Edit) cands[0]★
# ★pywinauto は Windows native ゆえ third_pc では import 不可 = lazy import★
# ───────────────────────────────────────────────────────────
def poke_fire(
    correlation_id: str,
    dedupe: DedupeWindow,
    skip_counter: SkipCounter,
    busy: BusyDetection,
    dry_run: bool = True,
    diagnose: bool = False,
) -> dict:
    """単発 poke 発火 (層② actuator)。

    Returns:
        dict with keys: status, reason, dedupe_key, attempts
        status ∈ {"fired", "skipped_dedupe", "skipped_busy",
                   "skipped_v5_guard", "human_required", "error",
                   "diagnosed", "dry_run_only"}
    """
    # ── refined V5 guard 先行評価 (touch する前に確認) ──
    # (実体は Windows API 経由で取得、ここでは call site から渡される想定)
    # 本 entrypoint は guard 結果を呼出側に依存させず conservative に進む。

    # ── 誤爆抑制: 応答中 skip ──
    if busy.is_busy():
        n = skip_counter.increment(correlation_id)
        if skip_counter.exceeded(correlation_id):
            emit_event(
                "human_required",
                correlation_id,
                cause="skip_max_exceeded",
                skip_count=n,
                # ★副院長殿長時間入力中 skip 上限到達の可能性を併記 (Boy-Scout C1)★
                hint="副院長殿が長時間入力中で応答中 skip が上限 (skip_max=5) に到達した可能性",
            )
            return {
                "status": "human_required",
                "reason": "skip_max_exceeded",
                "skip_count": n,
            }
        emit_event("skip_busy", correlation_id, skip_count=n)
        return {"status": "skipped_busy", "skip_count": n}

    # 誤爆抑制 リセット (busy 解除 = 正常 poke 候補)
    skip_counter.reset(correlation_id)

    # ── 誤爆抑制: dedupe (last-fire TTL sliding window) ──
    dedupe_key = (correlation_id, "fukuincho_desktop_poke")
    now = time.time()
    if not dedupe.should_fire(dedupe_key, now=now):
        emit_event("skip_dedupe", correlation_id, ttl_sec=DEDUPE_T_SEC)
        return {"status": "skipped_dedupe", "dedupe_key": dedupe_key}

    # ── --diagnose: 偵察のみ (送信禁) ──
    if diagnose:
        emit_event("diagnose_only", correlation_id)
        return {"status": "diagnosed", "dedupe_key": dedupe_key}

    # ── --dry-run: focus まで (本送信禁) ──
    if dry_run:
        emit_event("dry_run_no_enter", correlation_id)
        return {"status": "dry_run_only", "dedupe_key": dedupe_key}

    # ── 実 actuator (pywinauto descendants/Edit/clipboard+Enter) ──
    # lazy import (third_pc では失敗するが canonical source 化のため意図的)
    try:
        from pywinauto import Desktop  # type: ignore
        import pyperclip  # type: ignore
    except ImportError as e:
        emit_event(
            "import_error",
            correlation_id,
            module=str(e),
            os_platform=platform.system(),
        )
        return {
            "status": "error",
            "reason": f"pywinauto/pyperclip ImportError on {platform.system()}",
        }

    try:
        win = Desktop(backend="uia").window(title_re=TARGET_WINDOW_TITLE_RE)
        win_title = win.window_text()
    except Exception as e:
        emit_event(
            "window_lookup_failed",
            correlation_id,
            error_type=type(e).__name__,
        )
        return {"status": "error", "reason": "window_lookup_failed"}

    # refined V5 guard (window title check)
    if refined_v5_guard(win_title):
        emit_event(
            "v5_guard_block",
            correlation_id,
            window_title_redacted="[REDACTED]",
        )
        return {"status": "skipped_v5_guard", "reason": "v5_guard_block"}

    # descendants(control_type=Edit) cands[0] 経路 (段階2 a3-3 実証済)
    try:
        cands = win.descendants(control_type="Edit")
        if not cands:
            emit_event("no_edit_candidates", correlation_id)
            return {"status": "error", "reason": "no_edit_candidates"}
        edit = cands[0]
        edit.set_focus()
    except Exception as e:
        emit_event(
            "edit_lookup_failed",
            correlation_id,
            error_type=type(e).__name__,
        )
        return {"status": "error", "reason": "edit_lookup_failed"}

    # clipboard 経由 set + Enter (safe wrapper、save→set→Enter→restore)
    def _send_enter() -> bool:
        from pywinauto.keyboard import send_keys  # type: ignore
        # clipboard 内容を Ctrl+V で edit に paste、続けて Enter
        send_keys("^v")
        time.sleep(0.1)
        send_keys("{ENTER}")
        return True

    ok, restore_status = safe_clipboard_poke(
        payload=POKE_PAYLOAD,
        set_clip=pyperclip.copy,
        get_clip=pyperclip.paste,
        send_enter=_send_enter,
        correlation_id=correlation_id,
    )

    if ok:
        dedupe.mark_fired(dedupe_key, now=now)
        emit_event(
            "poke_fired",
            correlation_id,
            window_handle_redacted="[REDACTED]",
            payload_length=len(POKE_PAYLOAD),
            restore_status=restore_status,
        )
        return {"status": "fired", "dedupe_key": dedupe_key}
    else:
        emit_event(
            "poke_failed",
            correlation_id,
            restore_status=restore_status,
        )
        return {"status": "error", "reason": "enter_send_failed"}


# ───────────────────────────────────────────────────────────
# CLI entrypoint (--diagnose / --dry-run / --no-enter / --auto-poke)
# ★本送信は --auto-poke flag + 副院長殿御差配 D-lane 承認下のみ★
# ───────────────────────────────────────────────────────────
def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="fukuincho_desktop_poke 段階3 全自動ループ actuator"
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="偵察のみ (送信禁)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="focus まで (本送信禁)",
    )
    parser.add_argument(
        "--no-enter",
        action="store_true",
        help="Enter 送出抑止 (dry-run と同義)",
    )
    parser.add_argument(
        "--auto-poke",
        action="store_true",
        help="本送信モード (副院長殿御差配 D-lane 承認下のみ)",
    )
    parser.add_argument(
        "--correlation-id",
        default=None,
        help="correlation_id (省略時は自動採番、ae8083dd §2.4 順守)",
    )
    args = parser.parse_args(argv)

    corr_id = args.correlation_id or f"poke-{int(time.time())}-{os.getpid()}"

    if args.diagnose and args.auto_poke:
        emit_event(
            "cli_invalid_flags",
            corr_id,
            error="--diagnose と --auto-poke は同時指定不可",
        )
        return 2

    # 段階3 単発実行 mode (cron が invoke する想定)
    dedupe = DedupeWindow()
    skip_counter = SkipCounter()
    # busy detection は call site (main_pc 側 pywinauto introspection) から渡される想定。
    # CLI 単発実行では default (非 busy) を使う。
    busy = BusyDetection()

    result = poke_fire(
        correlation_id=corr_id,
        dedupe=dedupe,
        skip_counter=skip_counter,
        busy=busy,
        dry_run=not args.auto_poke,
        diagnose=args.diagnose,
    )

    status = result.get("status", "error")
    if status in ("fired", "diagnosed", "dry_run_only"):
        return 0
    if status in ("skipped_dedupe", "skipped_busy", "skipped_v5_guard"):
        return 0
    if status == "human_required":
        return 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
