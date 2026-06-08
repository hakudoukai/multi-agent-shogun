#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fukuincho_report_poke_bundle.py — 段階3 direct-poke bundle (報告 INSERT + poke 同期発火)

設計章節正本: docs/08-ops/fukuincho-stage3-direct-poke-design.md
  - commit ba9c7281 (方針転換設計、検知層廃止)
  - commit 21a87964 (§2 hook 注記追記、4軸調査 FKI-NO-DUP 第4条 PASS)
  - 副院長令 FINAL DIRECTIVE phase ② 実装 (新 SLA 02:14:29、karo-third msg_011802 (α) GO)

担当層: ★報告者能動 poke trigger bundle★ (universal canonical)
        全 origin_pc 一律 cover (Commander third_pc + main_pc 将軍 + second_pc 将軍)

実装方針 (FKI-NO-DUP 順守):
  - 報告 INSERT 経路 = ★scripts/inbox_write.sh 再利用★ (新規 writer 新設禁)
  - poke 実行 = ★fukuincho_desktop_poke.poke_fire 再利用★ (段階2 207bcdd 経路、新規 send loop 不新設)
  - ack リトライ = ★fukuincho_desktop_poke.backoff_seconds + ACK_N_SEC + RETRY_M_MAX 再利用★
                  (ae8083dd 全方向エンジン、新規 retry loop 不新設)
  - 連動経路 = ★既存 SSH endpoint (ALL-SSH-NO-NEW-ENDPOINT-01 3 確定接続先のみ)★

bundle 構造 (要件 §2 atomic):
  1. correlation_id 1 報告 1 poke (flock atomic check-and-mark)
  2. 報告 INSERT (inbox_write.sh shell out、Supabase pc_handshake cross-PC bridge 自動同梱)
  3. INSERT rc=0 確認 → poke 同期呼出 (rc!=0 時は poke せず — 報告なき poke 禁、§2 verbatim)
  4. poke 失敗 → ack リトライ (N=30s/M=3/backoff 30-60-120s)
  5. 窓不在/title 不一致時は ★type せず異常記録★ (poke_fire 内 v5_guard / no_edit_candidates 委譲)

絶対前提順守:
  - V5 (handshake 8012f18c) 触接ゼロ (refined_v5_guard 委譲)
  - 機密 2 件 (hermes_ro PW + Supabase token) 触接禁 (env 経由のみ、redact 順守)
  - DD-157 役職名のみ (戦国 persona 名禁)
  - FKI-NO-DUP 第4条: 新規 transport / poller / retry loop ゼロ (本 bundle = 結線のみ)
  - 止血B (commit e0e98b7) 保護範囲 touch 0 通算維持確約 (本 file 新規、inbox_watcher.sh 触接 0)
  - unit-green ≠ runtime-green 厳守 (本 module = pure orchestration、runtime 実証は別 phase)

★Note (透明性、e3c6baff 整合)★:
  本 file = third_pc 本 repo canonical source。実 deploy = D-lane 別 task (理事長承認後 main_pc 反映)。
  third_pc 上で本 file を import すると `fukuincho_desktop_poke.poke_fire` lazy import が
  pywinauto ImportError になる (Windows native のみ) — これは仕様。
  ロジック層 (orchestration / dedupe / strict_title_verify) は third_pc 上でも import 可能。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional, Callable

# ───────────────────────────────────────────────────────────
# 既存 fukuincho_desktop_poke 再利用 import (FKI-NO-DUP)
# ─ pywinauto は lazy ゆえ third_pc 上でも import 可能 ─
# ───────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from fukuincho_desktop_poke import (  # noqa: E402
    ACK_N_SEC,
    RETRY_M_MAX,
    BACKOFF_SCHEDULE_SEC,
    DEDUPE_T_SEC,
    SKIP_MAX,
    POKE_PAYLOAD,
    DedupeWindow,
    SkipCounter,
    BusyDetection,
    backoff_seconds,
    refined_v5_guard,
    emit_event as _poke_emit_event,
)

# ───────────────────────────────────────────────────────────
# 構造化ログ (correlation_id 貫通、error-design §14 整合)
# ★機密フィールド (clipboard 実値 / Supabase token / 報告 raw body) は ログ非出力★
# ───────────────────────────────────────────────────────────
LOG = logging.getLogger("fukuincho_report_poke_bundle")
if not LOG.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    LOG.addHandler(_h)
    LOG.setLevel(logging.INFO)


_FORBIDDEN_LOG_KEYS = frozenset({
    "report_body", "report_raw",
    "clipboard_value", "clipboard_content",
    "payload_value", "payload_text",
    "token", "secret", "password", "api_key",
    "supabase_token", "supabase_key",
})


def _sanitize_log_fields(fields: dict) -> dict:
    """機密 key を log payload から除去 (実値混入の事故防止、error-design §14)。"""
    return {k: v for k, v in fields.items() if k not in _FORBIDDEN_LOG_KEYS}


def emit_event(event: str, correlation_id: str, **fields) -> None:
    """構造化 JSON 1 行を stdout に emit。"""
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "correlation_id": correlation_id,
        "event": event,
        "component": "fukuincho_report_poke_bundle",
    }
    payload.update(_sanitize_log_fields(fields))
    LOG.info(json.dumps(payload, ensure_ascii=False))


# ───────────────────────────────────────────────────────────
# 厳密 window title verify (要件 §3 — ブラウザ誤認防止)
# ─ デスクトップ版 claude.ai window のみ受理、ブラウザ tab title は reject ─
# ─ cycle2 HIGH-1 prefix 認可教訓継承: 完全一致 (substring でない) ─
# ───────────────────────────────────────────────────────────

# ブラウザプロセス名 (case-insensitive substring match で reject)
# (Chrome / Edge / Firefox / Brave / Opera / Vivaldi 系)
_BROWSER_PROCESS_TOKENS = (
    "chrome.exe", "msedge.exe", "firefox.exe",
    "brave.exe", "opera.exe", "vivaldi.exe",
    "chromium.exe",
)

# デスクトップアプリ正規プロセス名 (Anthropic Claude.exe)
_DESKTOP_APP_PROCESS_TOKENS = ("claude.exe",)

# デスクトップアプリ window title 正規パターン
# 段階2 207bcdd で実証された title pattern を厳密化:
# 「Claude」単独 or 「Claude - ...」prefix のいずれか、case-sensitive
# (ブラウザ tab は通常「... - Google Chrome」「Claude - Anthropic」のような suffix を持つ)
_DESKTOP_APP_TITLE_RE = re.compile(
    r"^Claude(\s*[-–—]\s*.+)?$"
)


def strict_window_title_verify(
    title: Optional[str],
    process_name: Optional[str] = None,
) -> tuple[bool, str]:
    """要件 §3 — window title + process 名の厳密一致 verify。

    Args:
        title: window title (取得失敗時 None)
        process_name: process basename (取得失敗時 None、ブラウザ判定の補強)

    Returns:
        (accepted, reason)
        accepted: True = poke 対象として受理可
        reason: 受理/拒否 の理由 (log + audit 用)

    判定順 (厳密):
      1. title が None / 空 → reject ("no_title")
      2. process_name がブラウザ token に含まれる → reject ("browser_process") 【cycle2 HIGH-1 cure】
      3. process_name がデスクトップアプリ token と一致しない (None 以外) → reject ("non_desktop_process")
      4. title が _DESKTOP_APP_TITLE_RE 完全一致しない → reject ("title_pattern_mismatch")
      5. refined_v5_guard 違反 (V5 / Playwright / etc) → reject ("v5_guard_block")
      6. 全 pass → accept ("strict_match")

    ★cycle2 HIGH-1 教訓: prefix/部分一致禁、完全一致のみ★
    ★ブラウザ厳禁 (副院長令 FINAL DIRECTIVE): process_name 取得不可でも title pattern で reject 寄せ★
    """
    if not title:
        return False, "no_title"

    if process_name:
        low_proc = process_name.lower()
        # ブラウザプロセス検出 → 即 reject
        for tok in _BROWSER_PROCESS_TOKENS:
            if tok in low_proc:
                return False, "browser_process"
        # デスクトップアプリでない process → reject
        # (process_name が取得できている場合のみ、None 時は title pattern fallback)
        if not any(tok in low_proc for tok in _DESKTOP_APP_PROCESS_TOKENS):
            return False, "non_desktop_process"

    if not _DESKTOP_APP_TITLE_RE.match(title):
        return False, "title_pattern_mismatch"

    if refined_v5_guard(title):
        return False, "v5_guard_block"

    return True, "strict_match"


# ───────────────────────────────────────────────────────────
# correlation_id 単位の flock atomic 冪等 (要件 §4)
# ─ 同一 correlation_id で二重 poke を禁ずる ─
# ─ flock + on-disk marker で multi-process race safe ─
# ─ ★cycle2 RED-G cure (cross-platform)★: stdlib fcntl (POSIX) / msvcrt (Windows) で
#   全 origin_pc (Linux third/second + Windows main) 真 cover、tempfile.gettempdir で
#   /tmp hardcode 排除 (6 要件 (1) universal canonical 順守) ─
# ─ ★cycle2 B2 cure (cycle2 med)★: marker/lock path は sha256(corr_id) で
#   truncate collision を排除 (誤 skip 防止) ─
# ───────────────────────────────────────────────────────────

# Portable file-lock wrapper (cycle2 RED-G cure)
# POSIX 系は fcntl.flock、Windows は msvcrt.locking を採用 (どちらも stdlib、追加 dep なし)
if sys.platform == "win32":
    try:
        import msvcrt as _msvcrt  # type: ignore[import-not-found]
    except ImportError:
        _msvcrt = None  # 安全側 fallback (best-effort、ロックは効かないが crash しない)
    _fcntl = None
else:
    try:
        import fcntl as _fcntl  # type: ignore[import-not-found]
    except ImportError:
        _fcntl = None
    _msvcrt = None


def _portable_lock_acquire(fd: int, timeout_sec: float) -> bool:
    """LOCK_EX | LOCK_NB を timeout_sec まで retry。獲得=True / timeout=False。"""
    deadline = time.time() + timeout_sec
    while True:
        try:
            if _fcntl is not None:
                _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                return True
            if _msvcrt is not None:
                # msvcrt.locking は file pos から N byte を lock
                os.lseek(fd, 0, os.SEEK_SET)
                _msvcrt.locking(fd, _msvcrt.LK_NBLCK, 1)
                return True
            # 両方無い (極稀な platform) → ロックなしで進む (best-effort)
            return True
        except (BlockingIOError, OSError):
            if time.time() >= deadline:
                return False
            time.sleep(0.05)


def _portable_lock_release(fd: int) -> None:
    try:
        if _fcntl is not None:
            _fcntl.flock(fd, _fcntl.LOCK_UN)
        elif _msvcrt is not None:
            os.lseek(fd, 0, os.SEEK_SET)
            _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
    except OSError:
        pass


_LOCK_DIR_DEFAULT = os.path.join(
    tempfile.gettempdir(), "fukuincho_report_poke_bundle"
)


def _ensure_lock_dir(lock_dir: str) -> None:
    os.makedirs(lock_dir, exist_ok=True)


def _corr_id_hash(correlation_id: str) -> str:
    """sha256 hex digest (★B2 cure★: truncate collision 完全排除、path traversal 防止)。"""
    return hashlib.sha256(correlation_id.encode("utf-8")).hexdigest()


def _marker_path(lock_dir: str, correlation_id: str) -> str:
    return os.path.join(lock_dir, f"{_corr_id_hash(correlation_id)}.poked")


def _lock_path(lock_dir: str, correlation_id: str) -> str:
    return os.path.join(lock_dir, f"{_corr_id_hash(correlation_id)}.lock")


def acquire_correlation_lock(
    correlation_id: str,
    lock_dir: str = _LOCK_DIR_DEFAULT,
    timeout_sec: float = 5.0,
):
    """correlation_id 単位の portable lock を獲得し file descriptor を返す。

    Returns:
        int fd (lock 獲得成功) / None (timeout)

    ★cross-platform (POSIX fcntl / Windows msvcrt)★
    ★呼出側責任で release_correlation_lock(fd) を必ず呼ぶこと★
    """
    _ensure_lock_dir(lock_dir)
    lock_p = _lock_path(lock_dir, correlation_id)
    fd = os.open(lock_p, os.O_RDWR | os.O_CREAT, 0o644)
    if _portable_lock_acquire(fd, timeout_sec):
        return fd
    try:
        os.close(fd)
    except OSError:
        pass
    return None


def release_correlation_lock(fd: Optional[int]) -> None:
    if fd is None:
        return
    try:
        _portable_lock_release(fd)
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def already_poked(correlation_id: str, lock_dir: str = _LOCK_DIR_DEFAULT) -> bool:
    """correlation_id が既に poke 済みか確認 (marker file 存在判定)。"""
    return os.path.exists(_marker_path(lock_dir, correlation_id))


def mark_poked(correlation_id: str, lock_dir: str = _LOCK_DIR_DEFAULT) -> None:
    """correlation_id を poke 済みとして mark (atomic write)。"""
    _ensure_lock_dir(lock_dir)
    p = _marker_path(lock_dir, correlation_id)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(time.time()))
    os.replace(tmp, p)


# ───────────────────────────────────────────────────────────
# 報告 INSERT 実行 (要件 §2 — INSERT 経路は inbox_write.sh 再利用)
# ─ FKI-NO-DUP: 新規 Supabase writer 新設禁 ─
# ───────────────────────────────────────────────────────────


@dataclass
class ReportInsertResult:
    rc: int
    stderr: str
    elapsed_sec: float


# inbox_write.sh に content を stdin で渡すための placeholder + env (S2 cure)
_INBOX_WRITE_STDIN_PLACEHOLDER = "__VIA_STDIN__"
_INBOX_WRITE_STDIN_ENV = "INBOX_WRITE_CONTENT_STDIN"


def report_insert_via_inbox_write(
    target_agent: str,
    content: str,
    msg_type: str,
    from_agent: str,
    inbox_write_path: Optional[str] = None,
    runner: Optional[Callable] = None,
    timeout_sec: float = 30.0,
) -> ReportInsertResult:
    """既存 inbox_write.sh 経由で報告 INSERT を実行 (FKI-NO-DUP 順守)。

    Args:
        target_agent: 報告先 agent id (例: "fukuincho", "shogun-third")
        content: 報告本文 (★raw body はログ非出力 + ★cycle2 S2 cure★ argv 不経由 = stdin 渡し★)
        msg_type: メッセージタイプ (例: "report_received", "task_completed")
        from_agent: 送信元 agent id
        inbox_write_path: scripts/inbox_write.sh への absolute path (省略時=本 file と同 dir)
        runner: テスト注入用の subprocess.run 互換 callable (省略時=subprocess.run)
        timeout_sec: subprocess timeout

    Returns:
        ReportInsertResult(rc, stderr, elapsed_sec)
        rc=0 → INSERT 成功 (Supabase cross-PC bridge は inbox_write.sh 内 background 実行)
        rc!=0 → INSERT 失敗 (呼出側で poke せず終了する判定材料)

    ★FKI-NO-DUP★: 直接 Supabase REST 叩かない。inbox_write.sh が唯一の正規 writer。
    ★機密★: content (報告 raw body) はログに出さない。エラー時 stderr のみ。
    ★cycle2 S2 cure★: content を argv ($2) でなく stdin で渡す (process inspection 機密
       露出 cure)。env INBOX_WRITE_CONTENT_STDIN=1 で inbox_write.sh が stdin を受領、$2
       には placeholder (__VIA_STDIN__) を渡し空文字 reject を avoid。
    """
    if inbox_write_path is None:
        inbox_write_path = os.path.join(HERE, "inbox_write.sh")
    if runner is None:
        runner = subprocess.run

    # ★S2 cure★: env + stdin 経路 (process inspection 機密露出 cure)
    env = dict(os.environ)
    env[_INBOX_WRITE_STDIN_ENV] = "1"

    start = time.time()
    try:
        proc = runner(
            [
                "bash", inbox_write_path,
                target_agent,
                _INBOX_WRITE_STDIN_PLACEHOLDER,  # $2 はダミー placeholder、bash が stdin で上書き
                msg_type,
                from_agent,
            ],
            input=content,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
        )
        elapsed = time.time() - start
        rc = getattr(proc, "returncode", 1)
        stderr = getattr(proc, "stderr", "") or ""
        return ReportInsertResult(rc=rc, stderr=stderr, elapsed_sec=elapsed)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return ReportInsertResult(
            rc=124,
            stderr="inbox_write.sh timeout",
            elapsed_sec=elapsed,
        )
    except Exception as e:
        elapsed = time.time() - start
        return ReportInsertResult(
            rc=1,
            stderr=f"{type(e).__name__}: {e}",
            elapsed_sec=elapsed,
        )


# ───────────────────────────────────────────────────────────
# poke 呼出 (origin_pc 別連動経路、要件 §7、ALL-SSH-NO-NEW-ENDPOINT-01)
# ─ origin=third_pc → SSH 経由 main_pc 上 fukuincho_desktop_poke 発火 ─
# ─ origin=main_pc  → 同一 host 直接呼出 ─
# ─ origin=second_pc → SSH 経由 main_pc 発火 ─
# ─ ★既存 SSH endpoint (3 確定接続先) のみ、新設禁★ ─
# ───────────────────────────────────────────────────────────

# ALL-SSH-NO-NEW-ENDPOINT-01 (project_documents a9b266a6 第3部)
# main_pc 確定 endpoint
_MAIN_PC_SSH_HOST = "192.168.11.11"
_MAIN_PC_SSH_USER = "user"
_MAIN_PC_SSH_PORT = 2222
_SSH_KEY_PATH = os.path.expanduser("~/.ssh/daishogun_cef2002e5d")

# main_pc 側の poke script absolute path (D-lane 別 task で deploy)
_MAIN_PC_POKE_SCRIPT = "scripts/fukuincho_desktop_poke.py"


# ★cycle2 RED-S1 cure (high)★: correlation_id allowlist matrix
# 設計 §2(2) 完全一致 reject: ASCII alphanumeric + '.' '_' '-' のみ、1〜200 文字
# 拒否: ';' '&' '|' '$' '`' '(' ')' '<' '>' 改行 空白 \" \' \\ 等の shell meta 全件
_VALID_CORR_ID_RE = re.compile(r"^[A-Za-z0-9._\-]{1,200}$")


def validate_correlation_id(correlation_id: str) -> bool:
    """RED-S1 cure: SSH path remote_cmd 内文字列補間に対する injection 防止。

    allowlist 完全一致 reject (cycle2 HIGH-1 prefix 認可教訓継承)。
    main_pc 直接 path も argv 安全だが、defense-in-depth で同 validate を入口で適用する。

    Returns:
        True = 安全 (poke 進行可)
        False = 不正 (poke せず error 返却、raw value は log に出さない)
    """
    if not isinstance(correlation_id, str):
        return False
    return bool(_VALID_CORR_ID_RE.match(correlation_id))


def fire_poke_via_origin(
    correlation_id: str,
    origin_pc: str,
    runner: Optional[Callable] = None,
    timeout_sec: float = 30.0,
) -> dict:
    """origin_pc 別連動経路で poke を発火する。

    Args:
        correlation_id: 報告 → poke 連動 ID
        origin_pc: "third_pc" / "main_pc" / "second_pc"
        runner: テスト注入用 subprocess.run 互換 callable
        timeout_sec: poke 呼出 timeout

    Returns:
        dict: {"status": ..., "rc": ..., "stderr": ..., "elapsed_sec": ...}
        status ∈ {"fired", "skipped_dedupe", "skipped_busy", "skipped_v5_guard",
                  "human_required", "error", "unsupported_origin"}

    ★ALL-SSH-NO-NEW-ENDPOINT-01 順守: 既存 endpoint のみ★
    ★cycle2 RED-S1 cure (high)★: SSH path remote_cmd に corr_id を unescaped 補間しない。
       (a) 入口で allowlist 完全一致 reject、(b) defense-in-depth で shlex.quote 経由補間。
    """
    if runner is None:
        runner = subprocess.run

    # ★RED-S1 cure (cycle2 HIGH)★: 入口で allowlist 完全一致 reject (SSH path/main_pc 直接両方)
    if not validate_correlation_id(correlation_id):
        emit_event(
            "poke_corr_id_invalid",
            correlation_id="(redacted)",  # raw 不正値は log に出さない
            origin_pc=origin_pc,
        )
        return {
            "status": "error",
            "rc": 22,
            "stderr": "invalid correlation_id (allowlist mismatch)",
            "elapsed_sec": 0.0,
        }

    start = time.time()

    if origin_pc == "main_pc":
        # 同一 host 直接呼出 (Windows host)
        # argv 渡しゆえ shell 補間されない (subprocess は shell=False default)
        cmd = [
            "python3", _MAIN_PC_POKE_SCRIPT,
            "--auto-poke",
            "--correlation-id", correlation_id,
        ]
    elif origin_pc in ("third_pc", "second_pc"):
        # SSH 経由 main_pc 上 poke script 発火
        # ★既存 endpoint daishogun key 経由、新 endpoint 不作成★
        # ★RED-S1 cure (cycle2 HIGH)★: corr_id + script path を shlex.quote で escape。
        # allowlist は通っているので metacharacter は含まれないが、defense-in-depth で適用。
        q_corr = shlex.quote(correlation_id)
        q_script = shlex.quote(_MAIN_PC_POKE_SCRIPT)
        remote_cmd = (
            f"python3 {q_script} "
            f"--auto-poke --correlation-id {q_corr}"
        )
        cmd = [
            "ssh", "-i", _SSH_KEY_PATH,
            "-p", str(_MAIN_PC_SSH_PORT),
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=10",
            f"{_MAIN_PC_SSH_USER}@{_MAIN_PC_SSH_HOST}",
            remote_cmd,
        ]
    else:
        return {
            "status": "unsupported_origin",
            "rc": 2,
            "stderr": f"unknown origin_pc={origin_pc}",
            "elapsed_sec": 0.0,
        }

    try:
        proc = runner(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        elapsed = time.time() - start
        rc = getattr(proc, "returncode", 1)
        stdout = getattr(proc, "stdout", "") or ""
        stderr = getattr(proc, "stderr", "") or ""

        # poke_fire entrypoint の rc → status マッピング (fukuincho_desktop_poke main 互換)
        if rc == 0:
            status = "fired"
        elif rc == 3:
            status = "human_required"
        else:
            status = "error"
        return {
            "status": status,
            "rc": rc,
            "stdout_redacted": "[OK]" if stdout else "",
            "stderr": stderr[:500],
            "elapsed_sec": elapsed,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "rc": 124,
            "stderr": "poke invocation timeout",
            "elapsed_sec": time.time() - start,
        }
    except Exception as e:
        return {
            "status": "error",
            "rc": 1,
            "stderr": f"{type(e).__name__}: {e}",
            "elapsed_sec": time.time() - start,
        }


# ───────────────────────────────────────────────────────────
# ★案 A — 副院長令 6c4793fa (理事長承認、Commander msg_134241)★
# fire_poke_local: third_pc local Claude Desktop App へ Win python.exe interop で直接 poke。
# fire_poke_via_origin は origin_pc=third_pc 時 ★SSH 経由 main_pc 上 poke★ 設計ゆえ、
# 副院長殿の third_pc Windows host 上 Claude Desktop には届かない。本 entrypoint は
# 同一 third_pc 上の Windows interop (subprocess + python.exe + pywinauto) で直接 poke する。
#
# FKI-NO-DUP: validate_correlation_id (allowlist) + already_poked/mark_poked (flock dedupe) +
#             safe_clipboard_poke (差配3 実証済) + refined_v5_guard 一式既存機構流用、
#             新規実装は subprocess invoke + wslpath 動的解決のみ。
# 設計拘束 : strict title `^Claude$` で Chrome ブラウザ排除、Ubuntu-24.04 hardcode 禁
#             (memory FKI-SECOND-PC-SINGLE-DISTRO-01 一般原則、wslpath -w 動的解決)。
# 障害時安全側: TimeoutExpired + 全 Exception 捕捉、log のみで暴走禁。
# ────────────────────────────────────────────────────────────
_DEFAULT_WIN_PYTHON = "/mnt/c/Users/user/AppData/Local/Programs/Python/Python313/python.exe"


def fire_poke_local(
    correlation_id: str,
    win_python_path: str = _DEFAULT_WIN_PYTHON,
    timeout_sec: float = 15.0,
    runner: Optional[Callable] = None,
    lock_dir: str = _LOCK_DIR_DEFAULT,
) -> dict:
    """third_pc local Claude Desktop App へ Win python.exe interop 経由 poke 発火。

    Args:
        correlation_id: 報告 → poke 連動 ID (allowlist 検査)。
        win_python_path: Windows python.exe path (subprocess 経由実行)。
        timeout_sec: subprocess timeout。
        runner: テスト注入用 subprocess.run 互換 callable。
        lock_dir: flock dedupe 用 lock dir (デフォルト bundle 標準)。

    Returns:
        dict: {"status": ..., "rc": ..., "stdout_redacted": ..., "stderr": ...,
                "elapsed_sec": ...}
        status ∈ {"fired", "skipped_dedupe", "v5_guard_block", "no_edit_candidates",
                   "error"}
    """
    if runner is None:
        runner = subprocess.run

    # ★validate_correlation_id allowlist (atomic span 外で OK、副作用無)★
    if not validate_correlation_id(correlation_id):
        emit_event(
            "fire_poke_local_corr_id_invalid",
            correlation_id="(redacted)",
        )
        return {
            "status": "error",
            "rc": 22,
            "stderr": "invalid correlation_id (allowlist mismatch)",
            "elapsed_sec": 0.0,
        }

    # ★cycle4 RED1 root-cure (副院長令 atomic span mandate、gunshi cycle3 三者全一致 RED 受領)★:
    #   acquire_correlation_lock → already_poked check → poke → mark_poked → release を
    #   ★単一 flock 区間で連続保持★ で TOCTOU を完全排除 (run_bundle 同型 root-cure)。
    #   bundle 既存 primitive (acquire/release_correlation_lock) を wrap、再実装ゼロ。
    fd = acquire_correlation_lock(
        correlation_id,
        lock_dir=lock_dir,
        timeout_sec=5.0,
    )
    if fd is None:
        emit_event(
            "fire_poke_local_lock_timeout",
            correlation_id=correlation_id,
        )
        return {
            "status": "skipped_lock_timeout",
            "rc": 0,
            "stderr": "acquire_correlation_lock timeout (5s)",
            "elapsed_sec": 0.0,
        }

    start = time.time()
    try:
        # ★atomic 区間 (1): flock 保持下で dedupe check (TOCTOU 排除)★
        if already_poked(correlation_id, lock_dir=lock_dir):
            emit_event("fire_poke_local_skip_dedupe", correlation_id=correlation_id)
            return {
                "status": "skipped_dedupe",
                "rc": 0,
                "stderr": "already poked (atomic dedupe)",
                "elapsed_sec": time.time() - start,
            }

        # ★atomic 区間 (2): wslpath -w で SCRIPTS UNC 動的解決 (RED3 MEDIUM cure)★
        try:
            scripts_unc = subprocess.check_output(
                ["wslpath", "-w", HERE],
                text=True,
                timeout=5,
            ).strip()
        except Exception as e:
            emit_event(
                "fire_poke_local_wslpath_fail",
                correlation_id=correlation_id,
                error_type=type(e).__name__,
            )
            return {
                "status": "error",
                "rc": 1,
                "stderr": f"wslpath resolve failed: {type(e).__name__}: {e}",
                "elapsed_sec": time.time() - start,
            }
        if not scripts_unc.startswith(("\\\\", "//")):
            return {
                "status": "error",
                "rc": 1,
                "stderr": f"wslpath returned non-UNC: {scripts_unc!r}",
                "elapsed_sec": time.time() - start,
            }

        # ★atomic 区間 (3): Win python.exe subprocess + safe_clipboard_poke 経路★
        poke_script = (
            "import sys, json, time\n"
            f"sys.path.insert(0, r'{scripts_unc}')\n"
            "try:\n"
            "    import fukuincho_desktop_poke as p\n"
            "    from pywinauto import Desktop\n"
            "    from pywinauto.keyboard import send_keys\n"
            "    import pyperclip\n"
            "    win = Desktop(backend='uia').window(title_re=r'^Claude$')\n"
            "    title = win.window_text()\n"
            "    if p.refined_v5_guard(title):\n"
            "        print(json.dumps({'status': 'v5_guard_block'}))\n"
            "        sys.exit(0)\n"
            "    cands = win.descendants(control_type='Edit')\n"
            "    if not cands:\n"
            "        print(json.dumps({'status': 'no_edit_candidates'}))\n"
            "        sys.exit(0)\n"
            "    # ★入力中ガード (副院長令 4346f3d2、Commander msg_143742)★:\n"
            "    # 入力欄に1文字でもあれば投稿延期 (理事長/副院長 入力上書き防止)。\n"
            "    # 空欄なら投稿、reverse_poll fix1 gate により skipped_user_typing は\n"
            "    # mark せず retry 復活 → 空欄化後の次 poll で再評価。\n"
            "    # ★cycle7 placeholder 除外 (gunshi cycle6 Codex axisD 真陽性確定、msg_145023)★:\n"
            "    # runtime fixture で edit.window_text() が placeholder 'メッセージを入力\\u2026\\n'\n"
            "    # (len=10, stripped 9) を返すことが実機立証された。既知 placeholder は空扱い\n"
            "    # に正規化し poke 永久延期 (自己破壊) を回避する。\n"
            "    _KNOWN_PLACEHOLDERS = ('\\u30e1\\u30c3\\u30bb\\u30fc\\u30b8\\u3092\\u5165\\u529b\\u2026', 'Message Claude...', 'How can I help you today?')\n"
            "    try:\n"
            "        _current_text = cands[0].window_text() or ''\n"
            "    except Exception:\n"
            "        _current_text = ''\n"
            "    _stripped = _current_text.strip()\n"
            "    if _stripped and _stripped not in _KNOWN_PLACEHOLDERS:\n"
            "        print(json.dumps({'status': 'skipped_user_typing', 'reason': 'edit nonempty', 'edit_len': len(_current_text), 'is_placeholder': False}))\n"
            "        sys.exit(0)\n"
            "    cands[0].set_focus()\n"
            "    def _send_enter():\n"
            "        send_keys('^v'); time.sleep(0.1); send_keys('{ENTER}'); return True\n"
            "    ok, restore = p.safe_clipboard_poke(\n"
            "        payload=p.POKE_PAYLOAD,\n"
            "        set_clip=pyperclip.copy,\n"
            "        get_clip=pyperclip.paste,\n"
            "        send_enter=_send_enter,\n"
            f"        correlation_id='{correlation_id}',\n"
            "    )\n"
            "    print(json.dumps({'status': 'fired' if ok else 'failed', 'restore': restore}))\n"
            "except Exception as e:\n"
            "    print(json.dumps({'status': 'error', 'error_type': type(e).__name__, 'error': str(e)[:200]}))\n"
        )

        try:
            proc = runner(
                [win_python_path, "-c", poke_script],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            elapsed = time.time() - start
            rc = getattr(proc, "returncode", 1)
            stdout = (getattr(proc, "stdout", "") or "").strip()
            stderr = (getattr(proc, "stderr", "") or "")

            # poke_script stdout JSON parse
            try:
                data = json.loads(stdout) if stdout else {}
                status = data.get("status", "error")
            except (json.JSONDecodeError, ValueError):
                status = "fired" if rc == 0 else "error"

            # ★atomic 区間 (4): mark_poked を ★同一 flock 区間内★ で実行 (TOCTOU 完全排除)★
            if status == "fired":
                try:
                    mark_poked(correlation_id, lock_dir=lock_dir)
                except Exception as mp_err:
                    emit_event(
                        "fire_poke_local_mark_failed",
                        correlation_id=correlation_id,
                        error_type=type(mp_err).__name__,
                    )

            emit_event(
                "fire_poke_local_result",
                correlation_id=correlation_id,
                status=status,
                rc=rc,
                elapsed_sec=round(elapsed, 3),
            )
            return {
                "status": status,
                "rc": rc,
                "stdout_redacted": "[OK]" if status == "fired" else stdout[:200],
                "stderr": stderr[:500],
                "elapsed_sec": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "rc": 124,
                "stderr": "fire_poke_local timeout",
                "elapsed_sec": time.time() - start,
            }
        except Exception as e:
            return {
                "status": "error",
                "rc": 1,
                "stderr": f"{type(e).__name__}: {e}",
                "elapsed_sec": time.time() - start,
            }
    finally:
        # ★atomic 区間 終端: flock 解放 (例外時も release 保証、run_bundle 同型)★
        release_correlation_lock(fd)


# ───────────────────────────────────────────────────────────
# ack リトライ wiring (要件 §4 — ae8083dd N=30s/M=3/backoff)
# ─ ★既存 fukuincho_desktop_poke.backoff_seconds 再利用★ ─
# ─ ★新規 retry loop 不新設 (FKI-NO-DUP)★ ─
# ───────────────────────────────────────────────────────────


def poke_with_ack_retry(
    correlation_id: str,
    origin_pc: str,
    runner: Optional[Callable] = None,
    sleeper: Optional[Callable] = None,
    max_attempts: int = RETRY_M_MAX,
) -> dict:
    """poke を発火、失敗時は ae8083dd backoff schedule で M 回まで再送。

    Args:
        correlation_id: 報告 ↔ poke 連動 ID
        origin_pc: "third_pc" / "main_pc" / "second_pc"
        runner: subprocess.run 互換 callable (テスト注入)
        sleeper: time.sleep 互換 callable (テスト注入で 0 sleep 化)
        max_attempts: 再送上限 (default = RETRY_M_MAX = 3)

    Returns:
        dict: 最終 attempt の {"status": ..., "attempts": ..., "history": [...]}

    ★fired / human_required は終了 (再送せず)★
    ★skipped_dedupe / skipped_busy / skipped_v5_guard は終了 (誤爆抑止が働いた = 再送禁)★
    ★error 時のみ backoff_seconds(attempt) で再送、attempts >= max_attempts で打切り★
    """
    if sleeper is None:
        sleeper = time.sleep

    history: list[dict] = []
    final = None
    for attempt in range(1, max_attempts + 1):
        result = fire_poke_via_origin(
            correlation_id=correlation_id,
            origin_pc=origin_pc,
            runner=runner,
        )
        history.append({"attempt": attempt, **result})
        final = result
        status = result.get("status")

        # 確定終了系 (fired / human_required / skipped_*)
        if status in ("fired", "human_required", "skipped_dedupe",
                      "skipped_busy", "skipped_v5_guard"):
            break
        # unsupported origin は再送無意味
        if status == "unsupported_origin":
            break

        # error → backoff 後再送 (最終 attempt 後は sleep 不要)
        if attempt < max_attempts:
            sleep_sec = backoff_seconds(attempt)
            emit_event(
                "ack_retry_backoff",
                correlation_id,
                attempt=attempt,
                backoff_sec=sleep_sec,
                next_attempt=attempt + 1,
            )
            sleeper(sleep_sec)

    return {
        "status": (final or {}).get("status", "error"),
        "attempts": len(history),
        "history": history,
    }


# ───────────────────────────────────────────────────────────
# universal canonical bundle entrypoint
# ─ 報告 INSERT + 同期 poke 発火 を 1 動作に bundle ─
# ─ correlation_id 1 報告 1 poke (flock atomic check-and-mark) ─
# ───────────────────────────────────────────────────────────


@dataclass
class BundleResult:
    status: str
    correlation_id: str
    report_insert: Optional[ReportInsertResult] = None
    poke: Optional[dict] = None
    elapsed_sec: float = 0.0
    note: str = ""


def report_and_poke(
    correlation_id: str,
    target_agent: str,
    content: str,
    msg_type: str,
    from_agent: str,
    origin_pc: str,
    *,
    inbox_write_path: Optional[str] = None,
    lock_dir: str = _LOCK_DIR_DEFAULT,
    insert_runner: Optional[Callable] = None,
    poke_runner: Optional[Callable] = None,
    sleeper: Optional[Callable] = None,
) -> BundleResult:
    """universal canonical entry — 報告 INSERT 成功 → 同期 poke 発火を bundle。

    Args:
        correlation_id: 1 報告 1 poke の連動 ID (二重 poke 防止 key)
        target_agent: 報告先 agent id
        content: 報告本文 (raw body はログ非出力)
        msg_type: メッセージタイプ
        from_agent: 送信元 agent id
        origin_pc: "third_pc" / "main_pc" / "second_pc" (連動経路の選択)
        inbox_write_path: inbox_write.sh path (省略時=本 file 同 dir)
        lock_dir: flock + marker dir (省略時=/tmp/fukuincho_report_poke_bundle)
        insert_runner: テスト注入用 INSERT runner
        poke_runner: テスト注入用 poke runner
        sleeper: テスト注入用 sleep (backoff 0 化)

    Returns:
        BundleResult

    フロー:
      1. flock acquire (correlation_id 単位)
      2. already_poked → status="skipped_already_poked" で早期 return (★二重 poke 禁★)
      3. inbox_write.sh で報告 INSERT
      4. rc!=0 → status="report_insert_failed"、poke せず終了 (★報告なき poke 禁★)
      5. rc=0 → poke_with_ack_retry 同期呼出 (ae8083dd N=30s/M=3/backoff)
      6. fired → mark_poked + status="fired"
      7. lock release

    ★flock acquire 失敗 → status="lock_timeout" で早期 return★
    """
    start = time.time()
    fd = acquire_correlation_lock(correlation_id, lock_dir=lock_dir, timeout_sec=5.0)
    if fd is None:
        emit_event(
            "bundle_lock_timeout",
            correlation_id,
            origin_pc=origin_pc,
        )
        return BundleResult(
            status="lock_timeout",
            correlation_id=correlation_id,
            elapsed_sec=time.time() - start,
            note="flock acquire timeout (parallel run suspected)",
        )

    try:
        # 冪等性: 既に poke 済みなら early return
        if already_poked(correlation_id, lock_dir=lock_dir):
            emit_event(
                "bundle_skip_already_poked",
                correlation_id,
                origin_pc=origin_pc,
            )
            return BundleResult(
                status="skipped_already_poked",
                correlation_id=correlation_id,
                elapsed_sec=time.time() - start,
                note="correlation_id marker exists",
            )

        # 報告 INSERT (FKI-NO-DUP: inbox_write.sh 再利用)
        insert_result = report_insert_via_inbox_write(
            target_agent=target_agent,
            content=content,
            msg_type=msg_type,
            from_agent=from_agent,
            inbox_write_path=inbox_write_path,
            runner=insert_runner,
        )

        if insert_result.rc != 0:
            # ★報告なき poke 禁★ (§2 verbatim)
            emit_event(
                "bundle_report_insert_failed",
                correlation_id,
                origin_pc=origin_pc,
                rc=insert_result.rc,
                stderr=insert_result.stderr[:200],
                elapsed_sec=insert_result.elapsed_sec,
            )
            return BundleResult(
                status="report_insert_failed",
                correlation_id=correlation_id,
                report_insert=insert_result,
                elapsed_sec=time.time() - start,
                note="report INSERT rc!=0 — poke skipped per §2 verbatim",
            )

        # ★cycle2 RED-B1 cure (high)★: INSERT 成功直後 (poke 前) に marker を立てる。
        # 旧版は fired 時のみ mark していたため、INSERT 成功 + poke error/human_required
        # の rerun で同一 corr_id が再 INSERT される (冪等性違反、dup-INSERT) 欠陥があった。
        # 本順序変更で poke 結果に関わらず marker 残存 → rerun は skipped_already_poked で
        # INSERT 0 件 + poke 0 件、運用は別 corr_id で再起票 = 仕様。
        mark_poked(correlation_id, lock_dir=lock_dir)
        emit_event(
            "bundle_marker_set_post_insert",
            correlation_id,
            origin_pc=origin_pc,
        )

        # 報告 INSERT → poke 発火 latency 計測 (verify (i))
        latency_before_poke_sec = time.time() - start
        emit_event(
            "bundle_insert_to_poke_latency",
            correlation_id,
            origin_pc=origin_pc,
            insert_elapsed_sec=insert_result.elapsed_sec,
            latency_sec=latency_before_poke_sec,
        )

        # poke 同期発火 + ack リトライ (ae8083dd N=30s/M=3)
        poke_result = poke_with_ack_retry(
            correlation_id=correlation_id,
            origin_pc=origin_pc,
            runner=poke_runner,
            sleeper=sleeper,
        )

        if poke_result.get("status") == "fired":
            emit_event(
                "bundle_fired",
                correlation_id,
                origin_pc=origin_pc,
                attempts=poke_result.get("attempts"),
                total_elapsed_sec=time.time() - start,
            )
            return BundleResult(
                status="fired",
                correlation_id=correlation_id,
                report_insert=insert_result,
                poke=poke_result,
                elapsed_sec=time.time() - start,
            )

        # 非 fired (human_required / error / skipped_v5_guard / skipped_busy / etc)
        emit_event(
            "bundle_non_fired_terminal",
            correlation_id,
            origin_pc=origin_pc,
            poke_status=poke_result.get("status"),
            attempts=poke_result.get("attempts"),
        )
        return BundleResult(
            status=poke_result.get("status", "error"),
            correlation_id=correlation_id,
            report_insert=insert_result,
            poke=poke_result,
            elapsed_sec=time.time() - start,
        )
    finally:
        release_correlation_lock(fd)


# ───────────────────────────────────────────────────────────
# CLI entrypoint (--dry-run / --auto-poke / --diagnose)
# ───────────────────────────────────────────────────────────


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="fukuincho_report_poke_bundle — 報告 INSERT + 同期 poke 発火"
    )
    parser.add_argument("--target-agent", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--msg-type", default="report_received")
    parser.add_argument("--from-agent", required=True)
    parser.add_argument(
        "--origin-pc",
        choices=("third_pc", "main_pc", "second_pc"),
        required=True,
    )
    parser.add_argument(
        "--correlation-id",
        default=None,
        help="省略時は自動採番 (ae8083dd §2.4 順守)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="poke を実行せず INSERT のみ (検証用)",
    )
    args = parser.parse_args(argv)

    corr_id = args.correlation_id or f"bundle-{int(time.time())}-{os.getpid()}"

    if args.dry_run:
        # dry-run: poke を no-op runner で差し替え
        def _noop_runner(*a, **kw):
            class _P:
                returncode = 0
                stdout = ""
                stderr = ""
            return _P()
        result = report_and_poke(
            correlation_id=corr_id,
            target_agent=args.target_agent,
            content=args.content,
            msg_type=args.msg_type,
            from_agent=args.from_agent,
            origin_pc=args.origin_pc,
            poke_runner=_noop_runner,
            sleeper=lambda s: None,
        )
    else:
        result = report_and_poke(
            correlation_id=corr_id,
            target_agent=args.target_agent,
            content=args.content,
            msg_type=args.msg_type,
            from_agent=args.from_agent,
            origin_pc=args.origin_pc,
        )

    print(json.dumps({
        "status": result.status,
        "correlation_id": result.correlation_id,
        "elapsed_sec": result.elapsed_sec,
        "note": result.note,
        "poke_attempts": (result.poke or {}).get("attempts") if result.poke else None,
    }, ensure_ascii=False))

    return 0 if result.status in ("fired", "skipped_already_poked") else 1


if __name__ == "__main__":
    sys.exit(main())
