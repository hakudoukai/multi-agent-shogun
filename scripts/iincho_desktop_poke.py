#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iincho_desktop_poke.py — 段階3 全自動ループ poke actuator (委員長席 retarget 版、third_pc 本 repo canonical source)

★複製元 = scripts/fukuincho_desktop_poke.py (P0 修正2・理事長GO seq119215・parent_cmd=
  cmd_thirdpc_P0_actuator_shusei2_poke_replicate_iincho_20260711)。
★TARGET seat retarget★: 副院長席 → 委員長 (iincho) Claude Desktop 席。
  根拠 = 元副院長席と同一物理窓 (理事長証言、2026-07-11)。ゆえ TARGET_WINDOW_TITLE_RE (window title 正規表現)
  自体は複製元と不変 (同一窓を指すため)。busy 検知対象・human_required 通知の宛先文言のみ 委員長 へ retarget。
★scope 限定★: 本 retarget は (a)(b)(c) のみ (複製/retarget/systemd unit 作成)。ライブ送信・実 poke 発火は禁
  (leg2 監査+ライブ着弾テストは修正1 GREEN 待ちで別 task)。

設計章節正本 (複製元由来、履歴の承認記録として保持・書換禁): docs/08-ops/fukuincho-stage3-auto-loop-design.md
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
  本 file = third_pc 本 repo canonical source (委員長席 retarget 版)。実 deploy = D-lane 別 task (理事長承認後 main_pc 反映)。
  third_pc 上で本 file を import すると pywinauto は ImportError になる (Windows native のみ) — これは仕様。
  syntax check (python -m py_compile) は third_pc 上で可能。
  ★旧レーン scripts/iincho_desktop_actuator.py (§4.1 hybrid) は本 file と無関係=流用禁・凍結保管 (理事長裁定)★。
"""

from __future__ import annotations

import argparse
import contextlib
import copy
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
def _build_logger(name: str = "iincho_desktop_poke") -> logging.Logger:
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
# ★F2 是正 (leg2 fail-fix)★ 状態永続化 — DedupeWindow/SkipCounter を
# systemd Type=oneshot timer の毎tick新規プロセス間で持続させる。
#
# 旧実装の根因は二重: (1) main() が dedupe/skip_counter を毎起動 in-memory 新規生成
# (状態が tick 間で消滅)。(2) dedupe_key/skip キーが correlation_id 由来
# (--correlation-id 未指定時は main() が `f"poke-{int(time.time())}-{os.getpid()}"` で
# 毎回一意生成) だったため、★(1)を仮に永続化しても★キー自体が tick 毎に変わり
# dedupe/skip_max は依然として実効化されない。
# 本 fix は両方を是正: (a) キーを poke 対象 (本 actuator は単一 target=委員長席固定)
# 単位の固定値 POKE_TARGET_KEY に変更、(b) 状態を JSON ファイルへ flock 経由で
# atomic 永続化。flock パターンは scripts/fukuincho_report_poke_bundle.py の
# _portable_lock_acquire/_release 系を本 file 専用に最小移植 (FKI-NO-DUP §4:
# 新規 transport/poller/retry loop はゼロ、既存 orchestration 入れ子のみ)。
# ───────────────────────────────────────────────────────────
POKE_TARGET_KEY = "iincho_desktop_poke:iincho_seat"

STATE_DIR_DEFAULT = os.path.expanduser("~/.local/share/iincho_desktop_poke")
STATE_PATH_DEFAULT = os.path.join(STATE_DIR_DEFAULT, "state.json")

try:
    import fcntl  # POSIX only — third_pc systemd --user timer 実行環境は Linux
except ImportError:  # pragma: no cover — Windows 側で本 CLI を直接叩く場合の fallback
    fcntl = None  # type: ignore


def _state_lock(fp, exclusive: bool) -> None:
    if fcntl is None:
        return
    fcntl.flock(fp.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)


def _state_unlock(fp) -> None:
    if fcntl is None:
        return
    fcntl.flock(fp.fileno(), fcntl.LOCK_UN)


class StateCorruptionError(RuntimeError):
    """state.json 破損 (デコード失敗/schema不正/IO失敗)。

    ★F2 是正 (leg2 再々監査 seq119790 是正2)★: 旧実装はこれを握り潰して fresh
    default へ fail-open していたが、それは dedupe/skip_counter 履歴の消失を
    「今から再計測」で誤魔化すに等しく、履歴消失直後の再発火を許してしまう
    (旧コメントの「fail-safe」表記は誤り)。呼出側 (main()) は本例外を捕捉し、
    fire を拒否した上で human_required へ escalation すること。
    """


class PersistIOError(RuntimeError):
    """state 永続化 I/O 失敗 (lock dir/lock open/flock/tmp write/flush/fsync/replace)。

    ★F2-IO 是正 (leg2 seq120505 再監査 FAIL 是正)★: 旧実装は save_persisted_state
    内の OSError を無変換のまま呼出側へ伝播させていた。main() は load 時の
    StateCorruptionError しか捕捉していなかったため、save 側の I/O 失敗
    (disk-full/permission/read-only fs/rename失敗等) は不可逆な Enter 送出の
    ★後★に無捕捉例外として露出しうる欠陥があった。本例外は state_transaction()
    (lock directory 作成/lock file open/flock 取得) と save_persisted_state()
    (tmp書込/flush/fsync/os.replace/dir fsync) 双方の I/O 失敗を統一的に
    fail-closed 信号化し、呼出側で human_required へ escalation させる
    (fail-open で握り潰し・無捕捉例外のいずれも禁)。
    """


def _fsync_dir(dir_path: str) -> None:
    """directory entry (rename 後の名前解決) を durable 化する。

    os.replace() 直後でも、親 directory 自体の metadata が fsync されるまでは
    突然の電源断/crash で rename が消失しうる (POSIX 既知の落とし穴)。
    本 helper は directory を読取専用で open し fsync するのみ (書込は行わない)。
    """
    fd = os.open(dir_path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def state_transaction(path: str = STATE_PATH_DEFAULT):
    """load→判定(poke_fire)→save を単一排他区間に閉じ込める (F2 是正: RMW非原子性の解消)。

    旧実装は load 時に state file 自身への共有ロックを短時間だけ取り、save 時は
    別の `.lock` ファイルへ排他ロックを取る、という 2 つの独立ロック区間だった
    ため、load〜save の間隙で他プロセスが割込むと lost update が起き得た。
    本 transaction は `.lock` ファイルへの排他ロックを load〜save 全体に渡って
    保持し続けることで、並行起動時の read-modify-write を単一 critical section
    にする。区間内の load_persisted_state/save_persisted_state は各々ロックを
    取らない (同一プロセスで同一 lock file に対し flock を二重に取ると、BSD
    flock は fd 単位管理のためデッドロックする — 二重ロック禁止)。

    ★F2-IO 是正★: lock directory 作成 (os.makedirs)・lock file open・flock 取得
    のいずれかが失敗した場合は PersistIOError を送出する (呼出側 main() は
    human_required へ escalation すること。区間をスキップして fail-open で
    先へ進んではならない)。
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError as e:
        raise PersistIOError(
            f"state lock directory 作成失敗: {type(e).__name__}: {e}"
        ) from e

    lock_path = f"{path}.lock"
    try:
        lock_fp = open(lock_path, "a+", encoding="utf-8")
    except OSError as e:
        raise PersistIOError(
            f"state lock file open 失敗: {type(e).__name__}: {e}"
        ) from e

    try:
        try:
            _state_lock(lock_fp, exclusive=True)
        except OSError as e:
            raise PersistIOError(
                f"state lock (flock) 取得失敗: {type(e).__name__}: {e}"
            ) from e
        yield
    finally:
        _state_unlock(lock_fp)
        lock_fp.close()


def load_persisted_state(path: str = STATE_PATH_DEFAULT) -> tuple[DedupeWindow, SkipCounter]:
    """state.json から DedupeWindow/SkipCounter を復元。

    呼出側は state_transaction() の排他区間内で呼ぶこと (単独呼出は非atomic、
    テスト等の単発検証用途に限る)。

    ファイル未存在 (初回起動、正当な「履歴なし」) は fresh default を返す。
    デコード失敗・schema不正・IO失敗は StateCorruptionError を送出する
    (fail-open で握り潰さない — 呼出側で fire 拒否 + human_required とすること)。
    """
    dedupe = DedupeWindow()
    skip_counter = SkipCounter()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        return dedupe, skip_counter
    except (OSError, json.JSONDecodeError) as e:
        raise StateCorruptionError(
            f"state.json 読取/デコード失敗: {type(e).__name__}: {e}"
        ) from e

    try:
        if not isinstance(raw, dict):
            raise ValueError("state.json top-level は object 必須")
        dedupe.last_fire = {
            tuple(json.loads(k)): float(v) for k, v in raw.get("last_fire", {}).items()
        }
        skip_counter.counts = {
            str(k): int(v) for k, v in raw.get("skip_counts", {}).items()
        }
    except (ValueError, TypeError, AttributeError, json.JSONDecodeError) as e:
        raise StateCorruptionError(
            f"state.json schema不正: {type(e).__name__}: {e}"
        ) from e

    return dedupe, skip_counter


def save_persisted_state(
    dedupe: DedupeWindow,
    skip_counter: SkipCounter,
    path: str = STATE_PATH_DEFAULT,
) -> None:
    """DedupeWindow/SkipCounter を state.json へ durable atomic 保存 (tmp+fsync+rename+dir fsync)。

    呼出側は state_transaction() の排他区間内で呼ぶこと (単独呼出は非atomic、
    テスト等の単発検証用途に限る)。

    ★F2-IO 是正★: tmp書込後の f.flush()/os.fsync() (ページキャッシュのみでなく
    ディスクへ確実反映) と os.replace() 後の親 directory fsync (rename の
    metadata durable 化) を追加。mkdir/open/write/flush/fsync/replace/dir-fsync
    いずれの OSError も PersistIOError へ変換して呼出側に fail-closed 信号化する
    (旧実装は無変換のまま伝播させ、main() 側で無捕捉例外化する欠陥があった)。
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        raw = {
            "last_fire": {json.dumps(list(k)): v for k, v in dedupe.last_fire.items()},
            "skip_counts": dict(skip_counter.counts),
        }
        tmp_path = f"{path}.tmp.{os.getpid()}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(raw, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # 同一 filesystem 上 atomic rename
        _fsync_dir(os.path.dirname(path))
    except OSError as e:
        raise PersistIOError(
            f"state.json 永続化失敗: {type(e).__name__}: {e}"
        ) from e


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
    # ★F1 是正 (leg2 fail-fix)★: 実 UI introspection で測定済みか否かを明示するフラグ。
    # 旧実装は本フィールドが存在せず、call site が未測定のまま BusyDetection() を
    # そのまま poke_fire() へ渡すと、全 default 値の組合せが is_busy()=True に評価される
    # (is_ready_for_submission() 既定 False → is_submission_inflight()=True) にも関わらず
    # main() 側コメントは「default = 非busy」と誤記していた。この結果、CLI 単発実行の
    # --auto-poke は常に skipped_busy を繰返し、skip_max=5 到達で human_required
    # (「委員長殿が長時間入力中」という★虚偽★alert) に陥っていた。
    # measured=False の場合は poke_fire() 冒頭で skip_counter/human_required 系列を
    # 汚染しない fail-closed 早期 return (skipped_unmeasured) を行う (既定値が busy を
    # 偽装しない = 既定値 busy 偽装禁の要求充足)。
    measured: bool = False

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
    payload: str = POKE_PAYLOAD,
    state_path: str = STATE_PATH_DEFAULT,
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

    # ── ★F1 是正★: 未測定 busy state は skip_counter/human_required 系列を汚染しない
    # fail-closed 早期 return (skipped_unmeasured)。call site が実 UI introspection を
    # 未配線のまま BusyDetection() の default 値を「非busy」の代用として使うと、
    # 常時 busy 判定 (旧欠陥) または恒久 non-busy 誤認 (別の危険な欠陥) のいずれかを
    # 偽装してしまう。本 fix は「未測定」を独立した第三の状態として扱い、それを
    # 素直に skip (skip_max 非算入・human_required 誤警報なし) することで両欠陥を排除する。
    if not busy.measured:
        emit_event(
            "busy_unmeasured_fail_closed",
            correlation_id,
            note="実測 busy state 未提供 (call site 未配線)。fail-closed skip、skip_max 非算入",
        )
        return {"status": "skipped_unmeasured", "reason": "busy_state_not_measured"}

    # ── 誤爆抑制: 応答中 skip ──
    # ★F2 是正★: キーは correlation_id (毎起動一意採番) ではなく POKE_TARGET_KEY
    # (本 actuator は単一 target=委員長席固定) を用いる。correlation_id をキーに使うと
    # dedupe/skip_max の状態をファイル永続化しても、キー自体が tick 毎に変わるため
    # 実効化されない (leg2 F2 根因の一部)。
    if busy.is_busy():
        n = skip_counter.increment(POKE_TARGET_KEY)
        if skip_counter.exceeded(POKE_TARGET_KEY):
            emit_event(
                "human_required",
                correlation_id,
                cause="skip_max_exceeded",
                skip_count=n,
                # ★委員長殿長時間入力中 skip 上限到達の可能性を併記 (Boy-Scout C1、iincho retarget 反映)★
                hint="委員長殿が長時間入力中で応答中 skip が上限 (skip_max=5) に到達した可能性",
            )
            return {
                "status": "human_required",
                "reason": "skip_max_exceeded",
                "skip_count": n,
            }
        emit_event("skip_busy", correlation_id, skip_count=n)
        return {"status": "skipped_busy", "skip_count": n}

    # 誤爆抑制 リセット (busy 解除 = 正常 poke 候補)
    skip_counter.reset(POKE_TARGET_KEY)

    # ── 誤爆抑制: dedupe (last-fire TTL sliding window) ──
    # ★F2 是正★: 同上理由でキーは POKE_TARGET_KEY 固定 (correlation_id 不使用)。
    dedupe_key = (POKE_TARGET_KEY,)
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

    # descendants(control_type=Edit) 経路 (段階2 a3-3 実証済)
    # ★F5 是正★: 0件は従来通り拒否、★複数件も拒否★ (window 同定を一意 identity に束縛。
    # 旧実装は len(cands)>1 でも cands[0] を無条件採用しており、複数候補が返る window
    # レイアウトでは誤った Edit control に貼付するリスクがあった。cands[0] の無条件採用は禁)。
    try:
        cands = win.descendants(control_type="Edit")
        if len(cands) == 0:
            emit_event("no_edit_candidates", correlation_id)
            return {"status": "error", "reason": "no_edit_candidates"}
        if len(cands) > 1:
            emit_event(
                "ambiguous_edit_candidates",
                correlation_id,
                candidate_count=len(cands),
            )
            return {
                "status": "error",
                "reason": "ambiguous_edit_candidates",
                "candidate_count": len(cands),
            }
        edit = cands[0]
        edit.set_focus()
    except Exception as e:
        emit_event(
            "edit_lookup_failed",
            correlation_id,
            error_type=type(e).__name__,
        )
        return {"status": "error", "reason": "edit_lookup_failed"}

    # ★F2-IO 是正★: Enter (不可逆) 送出前に durable reservation を fsync 済で書込む。
    # reservation 書込 (mkdir/lock/tmp書込/flush/fsync/replace/dir fsync のいずれか)
    # に失敗した場合は Enter を一切送出せず human_required とする (fail-closed)。
    # reservation 内容 = 「あたかも本 poke が成功した場合」の dedupe 状態
    # (mark_fired 適用済) を予め持続化しておくことで、Enter 送出後に fsync 済
    # ディスク上の抑止マークが既に存在する状態を作る。これにより送信後の
    # finalization 永続化が失敗しても、reservation がそのまま重複抑止を継続する
    # ため、追加のロールバック機構なしに保守的に安全側へ倒れる。
    reservation_dedupe = copy.deepcopy(dedupe)
    reservation_dedupe.mark_fired(dedupe_key, now=now)
    try:
        save_persisted_state(reservation_dedupe, skip_counter, path=state_path)
    except PersistIOError as e:
        emit_event(
            "human_required",
            correlation_id,
            cause="reservation_persist_failed",
            error=str(e),
            hint=(
                "Enter (不可逆) 送出前の durable reservation 書込に失敗したため、"
                "Enter を一切送出せず拒否した (fail-closed)。人手による state.json/"
                "state dir の書込可否確認を要する。"
            ),
        )
        return {"status": "human_required", "reason": "reservation_persist_failed"}
    dedupe.mark_fired(dedupe_key, now=now)

    # clipboard 経由 set + Enter (safe wrapper、save→set→Enter→restore)
    def _send_enter() -> bool:
        from pywinauto.keyboard import send_keys  # type: ignore
        # clipboard 内容を Ctrl+V で edit に paste、続けて Enter
        send_keys("^v")
        time.sleep(0.1)
        send_keys("{ENTER}")
        return True

    ok, restore_status = safe_clipboard_poke(
        payload=payload,
        set_clip=pyperclip.copy,
        get_clip=pyperclip.paste,
        send_enter=_send_enter,
        correlation_id=correlation_id,
    )

    if ok:
        emit_event(
            "poke_fired",
            correlation_id,
            window_handle_redacted="[REDACTED]",
            payload_length=len(payload),
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
# ★本送信は --auto-poke flag + 理事長明示GO+委員長 D-lane 承認下のみ (iincho retarget)★
# ───────────────────────────────────────────────────────────
def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="iincho_desktop_poke 段階3 全自動ループ actuator (委員長席 retarget、複製元=fukuincho_desktop_poke)"
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
        help="本送信モード (理事長明示GO+委員長 D-lane 承認下のみ、iincho retarget)",
    )
    parser.add_argument(
        "--correlation-id",
        default=None,
        help="correlation_id (省略時は自動採番、ae8083dd §2.4 順守)",
    )
    parser.add_argument(
        "--payload",
        default=POKE_PAYLOAD,
        help="poke 文言 (既定=コマンダーより。中継時=エルメスより/環境部長から 等。実値はログ非出力)",
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

    # ★F3 是正★: platform guard — auto-poke は Windows native (pywinauto) 専用。
    # 実査結果 (leg2 fail-fix): 本 actuator の本番起動経路は third_pc Linux/WSL2 側から
    # 直接 --auto-poke するのではなく、WSL2 interop 経由で Windows 側 python.exe を
    # 起動する経路 (scripts/fukuincho_report_poke_bundle.py fire_poke_local()、
    # 副院長令 6c4793fa/理事長承認/Commander msg_134241 で既承認済の前例)。
    # systemd .service の ExecStart を将来 --dry-run→--auto-poke に単純書換すると
    # Linux python3 上で pywinauto ImportError に落ちる欠陥があったため、
    # busy/dedupe 等の状態を汚染する前に本 guard で即座に拒否する (fail-closed)。
    if args.auto_poke and platform.system() != "Windows":
        emit_event(
            "platform_guard_block",
            corr_id,
            os_platform=platform.system(),
            reason=(
                "auto-poke は Windows native (pywinauto) 実行環境専用。third_pc の "
                "systemd --user timer は Linux/WSL2 側で稼働するため本 CLI への直接 "
                "--auto-poke 指定は禁。本番起動は WSL2 interop 経由 Windows python.exe "
                "(fukuincho_report_poke_bundle.py fire_poke_local() 前例準拠) を要する。"
            ),
        )
        return 2

    # 段階3 単発実行 mode (cron/timer が invoke する想定)
    # ★F2 是正 (leg2 再々監査 seq119790 是正2)★: load→判定(poke_fire)→save 全体を
    # state_transaction() の単一排他区間に閉じ込め、並行起動時の lost update を防ぐ。
    # state.json 破損時は StateCorruptionError を fail-open で握り潰さず、
    # fire 拒否 + human_required へ escalation する。
    # ★F2-IO 是正★: state_transaction() 自体 (lock directory 作成/lock file open/
    # flock 取得) の I/O 失敗は PersistIOError として送出される。fail-open で
    # 区間をスキップせず human_required へ escalation する (outer try/except)。
    try:
        with state_transaction():
            try:
                dedupe, skip_counter = load_persisted_state()
            except StateCorruptionError as e:
                emit_event(
                    "human_required",
                    corr_id,
                    cause="state_corrupted",
                    error=str(e),
                    hint=(
                        "state.json 破損検出。fail-open で fresh default 復帰すると "
                        "dedupe/skip_counter 履歴消失直後の再発火を許すため、実行を拒否し "
                        "人手による state.json 復旧/隔離を要する (F2 是正、fail-open禁)。"
                    ),
                )
                return 3

            # ★F1 是正★: busy state は「実測」か「未測定 (fail-closed)」の二択のみを許す。
            # 旧コメント「CLI 単発実行では default (非busy) を使う」は誤りだった —
            # BusyDetection() の全 default 値は実際には常時 is_busy()=True と評価され、
            # --dry-run/--diagnose も含め毎回 skipped_busy → 恒久 human_required 誤警報に
            # 陥る欠陥があった (leg2 F1 根因)。
            #
            # --diagnose / --dry-run は window に一切触れない安全な rehearsal であり、実 UI
            # introspection の有無に関わらず pipeline 到達性 (到達性テスト要件) を保証すべき
            # ため、明示的な「測定済・非busy」状態を与えて busy/dedupe ゲートを実地検証する。
            # --auto-poke (本送信) は call site (Windows native pywinauto introspection) が
            # 未配線の限り測定不能であり、実測なしに fire してはならない (fail-closed)。
            if args.diagnose or not args.auto_poke:
                # rehearsal path (diagnose/dry-run): 測定済 + 非busy を明示 (submit_enabled=True
                # は「送信可能=非 inflight」を表す。全項目を意図的に非busy側へ揃える)。
                busy = BusyDetection(
                    measured=True,
                    ime_active=False,
                    edit_nonempty=False,
                    focused=False,
                    submit_enabled=True,
                    spinner_hidden=True,
                    progress_inactive=True,
                )
            else:
                # 本番 auto-poke: 実測配線なしの CLI 単発実行では fail-closed skip
                # (poke_fire() 側の skipped_unmeasured へ委ねる。skip_max 非算入)。
                busy = BusyDetection(measured=False)

            result = poke_fire(
                correlation_id=corr_id,
                dedupe=dedupe,
                skip_counter=skip_counter,
                busy=busy,
                dry_run=not args.auto_poke,
                diagnose=args.diagnose,
                payload=args.payload,
            )

            # ★F2 是正★: dedupe/skip_counter の変化 (mark_fired/increment/reset) を次tickへ
            # 持ち越す。load〜save を同一 transaction 区間内で行うことで atomic にする。
            # ★F2-IO 是正★: finalization 書込失敗時は保守的に reservation (poke_fire 内で
            # 既に fsync 済で書込済) を維持したまま human_required へ escalation する
            # (fail-open で握り潰し禁。次tickの再発火は reservation により抑止済)。
            try:
                save_persisted_state(dedupe, skip_counter)
            except PersistIOError as e:
                emit_event(
                    "human_required",
                    corr_id,
                    cause="finalization_persist_failed",
                    error=str(e),
                    hint=(
                        "actuation後の finalization 永続化に失敗した。Enter 送出前の "
                        "durable reservation が既に fsync 済で残存しているため、次tickの "
                        "再発火は抑止される (保守的 fail-closed)。人手による state.json/"
                        "state dir の書込可否確認と reconciliation を要する。"
                    ),
                )
                return 3
    except PersistIOError as e:
        emit_event(
            "human_required",
            corr_id,
            cause="state_lock_unavailable",
            error=str(e),
            hint=(
                "state_transaction() の lock directory 作成/lock file open/flock 取得に "
                "失敗したため、実行を拒否した (fail-closed)。人手による state dir/lock "
                "file の書込可否・権限確認を要する。"
            ),
        )
        return 3

    status = result.get("status", "error")
    if status in ("fired", "diagnosed", "dry_run_only"):
        return 0
    if status in ("skipped_dedupe", "skipped_busy", "skipped_v5_guard", "skipped_unmeasured"):
        return 0
    if status == "human_required":
        return 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
