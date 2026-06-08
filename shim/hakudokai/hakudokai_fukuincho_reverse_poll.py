#!/usr/bin/env python3
"""Single poll iteration for reverse watcher (shogun -> fukuincho).

Processes unacknowledged pc_handshake messages addressed to fukuincho,
writes them to fukuincho's inbox, and sends a tmux nudge.
ACK only after confirmed inbox write (ACK-after-confirm).
"""
import sys, json, os, subprocess, time

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = sys.argv[5]
fukuincho_pane = sys.argv[6] if len(sys.argv) > 6 else "fukuincho:0.0"

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[fukuincho_reverse][{ts}] {msg}", file=sys.stderr)

try:
    with open(response_file) as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
    log(f"response parse error: {e}")
    sys.exit(0)

if not data:
    sys.exit(0)

with open(processed_file) as f:
    processed = set(line.strip() for line in f if line.strip())

new_msgs = [m for m in data if m.get("id") and m["id"] not in processed]
if not new_msgs:
    sys.exit(0)

success_count = 0
fail_count = 0
MAX_RETRY = 5

# Retry tracking (persistent across polls) — Watcher Design Principles 必須項目
RETRY_TRACKER_FILE = "/tmp/hakudokai_fukuincho_reverse_retry_tracker.json"

def load_retry_tracker():
    try:
        with open(RETRY_TRACKER_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_retry_tracker(tracker):
    with open(RETRY_TRACKER_FILE, "w") as f:
        json.dump(tracker, f)

def dead_letter_message(msg_id, last_error):
    """Mark message as dead-lettered in Supabase (stop retrying)."""
    try:
        import urllib.request
        from datetime import datetime, timezone
        dl_url = f"{api_url}/rest/v1/pc_handshake?id=eq.{msg_id}"
        dl_data = json.dumps({
            "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "acknowledged_by": "dead_letter",
            "context_data": json.dumps({"close_reason": "max_retry_exceeded", "last_error": last_error[:200]})
        }).encode()
        req = urllib.request.Request(dl_url, data=dl_data, method="PATCH")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("apikey", api_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        with urllib.request.urlopen(req, timeout=10) as _resp:
            pass
        log(f"DEAD-LETTERED: {msg_id[:8]} — {last_error}")
        return True
    except Exception as e:
        log(f"dead_letter ACK failed for {msg_id[:8]}: {e}")
        return False

retry_tracker = load_retry_tracker()

# Determine inbox path - fukuincho uses the standard inbox system
inbox_dir = os.path.join(script_dir, "queue", "inbox")
fukuincho_inbox = os.path.join(inbox_dir, "fukuincho.yaml")

for msg in new_msgs:
    msg_id = msg["id"]
    topic = msg.get("topic", "unknown")
    content = msg.get("content", "")
    priority = msg.get("priority", "normal")
    from_pc = msg.get("from_pc", "unknown")
    to_pc = msg.get("to_pc", "unknown")
    msg_type = msg.get("message_type", "status_update")

    log(f"NEW: {msg_id[:8]} {topic} from {from_pc} to {to_pc}")

    # Retry cap enforcement (must come BEFORE self-send check to handle stuck retries)
    retry_count = retry_tracker.get(msg_id, 0)
    if retry_count >= MAX_RETRY:
        log(f"RETRY CAP exceeded ({retry_count}/{MAX_RETRY}): {msg_id[:8]} — dead-lettering")
        if dead_letter_message(msg_id, f"max_retry_exceeded_after_{retry_count}_attempts"):
            with open(processed_file, "a") as f:
                f.write(msg_id + "\n")
            retry_tracker.pop(msg_id, None)
            save_retry_tracker(retry_tracker)
        continue

    # Self-send detection: if from_pc == to_pc, ACK immediately and skip
    if from_pc == to_pc or (from_pc == "main_pc" and to_pc == "main_pc"):
        log(f"SELF-SEND detected: {msg_id[:8]} from={from_pc} to={to_pc} — immediate ACK")
        try:
            import urllib.request
            from datetime import datetime, timezone
            ack_url = f"{api_url}/rest/v1/pc_handshake?id=eq.{msg_id}"
            ack_data = json.dumps({
                "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "acknowledged_by": "system",
                "context_data": json.dumps({"close_reason": "self_send_rejected"})
            }).encode()
            req = urllib.request.Request(ack_url, data=ack_data, method="PATCH")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("apikey", api_key)
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "return=minimal")
            with urllib.request.urlopen(req, timeout=10) as _resp:
                pass
            success_count += 1
        except Exception as e:
            log(f"SELF-SEND ACK failed for {msg_id[:8]}: {e}")
            fail_count += 1
        # Record as processed regardless (prevent infinite retry)
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
        continue

    summary = f"[{from_pc}][{priority}] {topic}: {content[:500]}"

    # Determine escalation level based on content
    escalation_hint = ""
    if msg_type == "urgent_stop":
        escalation_hint = " [L5:URGENT]"
    elif priority == "urgent":
        escalation_hint = " [L4:APPROVAL_REQUIRED]"
    elif "requires_response" in msg and msg.get("requires_response"):
        escalation_hint = " [L3:RESPONSE_NEEDED]"

    # Write to fukuincho inbox via inbox_write.sh
    inbox_cmd = [
        "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
        "fukuincho", summary + escalation_hint, "shogun_report", from_pc
    ]
    write_ok = False
    try:
        result = subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
        write_ok = True
    except subprocess.CalledProcessError as e:
        log(f"inbox_write FAILED: exit={e.returncode} stderr={e.stderr.decode()[:200]}")
    except Exception as e:
        log(f"inbox_write FAILED: {e}")

    # Read-back verify
    if write_ok:
        try:
            with open(fukuincho_inbox) as f:
                inbox_content = f.read()
            if topic[:20] not in inbox_content:
                log(f"VERIFY FAILED: {msg_id[:8]} not in fukuincho.yaml, retrying")
                try:
                    subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
                except Exception:
                    write_ok = False
        except FileNotFoundError:
            log(f"fukuincho.yaml not found at {fukuincho_inbox}")
        except Exception as e:
            log(f"verify read error (non-fatal): {e}")

    # ACK in Supabase (only after confirmed write)
    if write_ok:
        try:
            import urllib.request
            from datetime import datetime, timezone
            ack_url = f"{api_url}/rest/v1/pc_handshake?id=eq.{msg_id}"
            ack_data = json.dumps({
                "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "acknowledged_by": "fukuincho"
            }).encode()
            req = urllib.request.Request(ack_url, data=ack_data, method="PATCH")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("apikey", api_key)
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "return=minimal")
            with urllib.request.urlopen(req, timeout=10) as _resp:
                pass
            success_count += 1
        except Exception as e:
            log(f"ACK failed for {msg_id[:8]}: {e}")
            fail_count += 1
    else:
        fail_count += 1

    # Record as processed only if write succeeded (ACK-after-confirm)
    if write_ok:
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
        # Clear retry counter on success
        if msg_id in retry_tracker:
            retry_tracker.pop(msg_id, None)
            save_retry_tracker(retry_tracker)
    else:
        # Increment retry counter (will dead-letter at MAX_RETRY)
        retry_tracker[msg_id] = retry_count + 1
        save_retry_tracker(retry_tracker)
        log(f"SKIPPED recording {msg_id[:8]} (write failed, retry {retry_count+1}/{MAX_RETRY})")

# Send tmux nudge to fukuincho pane if we delivered messages
if success_count > 0:
    try:
        nudge = f"inbox{success_count}"
        subprocess.run(
            ["tmux", "send-keys", "-t", fukuincho_pane, nudge, ""],
            capture_output=True, timeout=5
        )
        time.sleep(0.3)
        subprocess.run(
            ["tmux", "send-keys", "-t", fukuincho_pane, "Enter", ""],
            capture_output=True, timeout=5
        )
        log(f"nudge sent to {fukuincho_pane}: {nudge}")
    except Exception as e:
        log(f"nudge failed: {e}")

# ────────────────────────────────────────────────────────────────────────────
# ★最後の配線 — 副院長殿御差配 c7e7f17a (理事長承認、Commander msg_131050) 拝命★
# dormant fukuincho_desktop_poke (ad486b57 既 land 実装) を本 reverse_poll から呼出統合。
# 既存 tmux nudge (上記) は維持、追加で Windows デスクトップ claude.ai アプリへ自動投稿
# 「確認依頼、コマンダーより」(副院長令 86e4ad23 + 理事長令、手動入力との区別可能化)。
#
# ★緊急止血 4 項目 (P0、副院長令 74eb45ac、Commander msg_132919 — 連投暴走 11 件)★:
#   (1) dedup 厳格化     : msg_id 単位 poked tracker、同一 msg は永久 1 回限定 poke。
#   (2) rate-limit 5 分  : 最終 poke 時刻記録、5min 未満 elapsed 時は skip。
#   (3) bundle merge     : 1 polling = 最大 1 poke、複数 NEW でも 1 回にまとめる。
#   (4) priority filter  : enter_restart heartbeat (topic に "enter_restart" 含む msg_type
#                          =status_update) を poke 経路から除外。tmux nudge は維持。
#
# ★gunshi 三者監査 RED 3 件 cure (msg_132755、副院長殿御差配後 案 B 採用)★:
#   - fix1 RED1+RED2 (排他不足 + FKI-NO-DUP 迂回): bundle 補助関数 import 流用 —
#       validate_correlation_id (allowlist) + already_poked / mark_poked (flock + dedupe)。
#       inline orchestration 維持は third_pc local Claude Desktop poke 用途 (bundle の
#       fire_poke_via_origin は main_pc 上 poke 設計ゆえ本用途と不整合)、ただし bundle
#       内 dedupe + flock 機構を import で再利用し double-poke 排除 + corr_id 検査。
#   - fix2 RED3 (Ubuntu-24.04 hardcode): wslpath -w で UNC 動的解決
#       (memory FKI-SECOND-PC-SINGLE-DISTRO-01 一般原則順守、distro 名 hardcode 禁)。
#
# 流れ: 返事 INSERT 検知 → tmux nudge (維持) + ★poke gate (止血 4 項目) 通過時のみ★
#        validate_correlation_id (allowlist) → already_poked (flock dedupe) check →
#        wslpath -w 動的 UNC → Win python.exe interop → fukuincho_desktop_poke
#        .safe_clipboard_poke 発火 → ^Claude$ (Chrome 排除) → 「確認依頼、コマンダーより」自動投稿
#        → mark_poked (flock コミット)。
#
# FKI-NO-DUP: 差配3 実証済機構 (correlation_id=runtime-actual-strict-1780884262) と
#             同等経路 + bundle 補助関数 (validate_correlation_id, already_poked,
#             mark_poked) 流用、再実装ゼロ。
# 障害時安全側: subprocess.TimeoutExpired + window 不在全捕捉、log のみで暴走禁。
# ack リトライ: polling 周期で自動継続 (新規 INSERT 検出時のみ再発火)。
# V5 guard  : refined_v5_guard で window title 検査、(8012f18c) 等検出時即停止。
# ────────────────────────────────────────────────────────────────────────────
# ★cycle5 fix2 (gunshi RED med cure、家老 msg_142921)★: /tmp 非永続 (reboot reset) →
#   $HOME/.cache 永続化で reboot 後も dedup 状態保持。
_POKED_DIR = os.path.join(os.path.expanduser("~"), ".cache", "hakudokai_fukuincho_reverse")
try:
    os.makedirs(_POKED_DIR, exist_ok=True)
except Exception:
    pass
POKED_MSG_IDS_FILE = os.path.join(_POKED_DIR, "poked_msg_ids.txt")
LAST_POKE_TS_FILE = os.path.join(_POKED_DIR, "last_poke_ts")
POKE_RATE_LIMIT_SEC = 300  # ★止血 (2) 5 分間隔★

# fcntl: POSIX のみ。本 reverse_poll は Linux 専用ゆえ fcntl のみで十分だが import 失敗時は
# no-op fallback で暴走禁。cycle5 fix3 で _poke_path_lock は bundle primitive 流用に移行、
# fcntl は LOCK_SH/LOCK_EX の poked_ids tracker 整合性保護のみに使用。
try:
    import fcntl as _fcntl_module  # noqa: E402
except ImportError:
    _fcntl_module = None

# ★案 A (副院長令 6c4793fa 理事長承認、Commander msg_134241)★:
#   bundle に新規追加された fire_poke_local (third_pc local Claude Desktop 直接 poke
#   entrypoint) を import 流用。inline orchestration は廃止し bundle entrypoint 1 本に統合
#   = RED1 排他不足 + RED2 FKI-NO-DUP 迂回 + 連投 axis1/4/6 全件根治。
#   cycle5 fix3 (gunshi RED2 cure、FKI-NO-DUP 真順守): poke 経路全体保護用の lock も
#   bundle primitive (acquire_correlation_lock/release_correlation_lock) を流用、
#   独自 _poke_path_lock 機構を廃止。
#   import 失敗時は安全側 fallback (None) で全 poke skip、暴走禁。
_BUNDLE_FIRE_POKE_LOCAL = None
_BUNDLE_ACQUIRE_LOCK = None
_BUNDLE_RELEASE_LOCK = None
try:
    _bundle_scripts_path = os.path.join(script_dir, "scripts")
    if _bundle_scripts_path not in sys.path:
        sys.path.insert(0, _bundle_scripts_path)
    from fukuincho_report_poke_bundle import (  # noqa: E402
        fire_poke_local as _BUNDLE_FIRE_POKE_LOCAL,
        acquire_correlation_lock as _BUNDLE_ACQUIRE_LOCK,
        release_correlation_lock as _BUNDLE_RELEASE_LOCK,
    )
except Exception as _bundle_import_err:
    log(f"bundle fire_poke_local import failed (poke disabled, safely): {type(_bundle_import_err).__name__}: {_bundle_import_err}")
    _BUNDLE_FIRE_POKE_LOCAL = None
    _BUNDLE_ACQUIRE_LOCK = None
    _BUNDLE_RELEASE_LOCK = None


def _load_poked_ids():
    """poked_msg_ids tracker を読込 (LOCK_SH で並行 read 許可、write 中は wait)。"""
    try:
        with open(POKED_MSG_IDS_FILE) as f:
            if _fcntl_module is not None:
                _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_SH)
            try:
                return set(line.strip() for line in f if line.strip())
            finally:
                if _fcntl_module is not None:
                    _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_UN)
    except FileNotFoundError:
        return set()


def _record_poked_ids(ids):
    """poked_msg_ids tracker に append (LOCK_EX + fsync で atomic、race 根絶)。"""
    if not ids:
        return
    try:
        with open(POKED_MSG_IDS_FILE, "a") as f:
            if _fcntl_module is not None:
                _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_EX)
            try:
                for mid in ids:
                    f.write(mid + "\n")
                f.flush()
                os.fsync(f.fileno())
            finally:
                if _fcntl_module is not None:
                    _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_UN)
    except Exception as e:
        log(f"poked_ids record failed (non-fatal): {e}")


def _load_last_poke_ts():
    try:
        with open(LAST_POKE_TS_FILE) as f:
            if _fcntl_module is not None:
                _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_SH)
            try:
                return float(f.read().strip())
            finally:
                if _fcntl_module is not None:
                    _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_UN)
    except (FileNotFoundError, ValueError):
        return 0.0


def _record_last_poke_ts(ts):
    try:
        with open(LAST_POKE_TS_FILE, "w") as f:
            if _fcntl_module is not None:
                _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_EX)
            try:
                f.write(str(ts))
                f.flush()
                os.fsync(f.fileno())
            finally:
                if _fcntl_module is not None:
                    _fcntl_module.flock(f.fileno(), _fcntl_module.LOCK_UN)
    except Exception as e:
        log(f"last_poke_ts record failed (non-fatal): {e}")


# ★cycle5 fix3 (gunshi RED2 cure、FKI-NO-DUP 真順守、家老 msg_142921)★:
#   poke 経路全体保護用の lock を bundle primitive (acquire_correlation_lock /
#   release_correlation_lock) で実装、独自 _poke_path_lock 機構廃止。
#   correlation_id は process scoped な固定値 "reverse-poll-path-guard" を使用、
#   bundle 内部で _portable_lock_acquire (LOCK_EX) → corr_id 単位 flock。
#   並列 process 起動時は別 process が保持中 → bundle が timeout_sec=0 で None 返却
#   (= skip 安全側、tmux nudge は既送済ゆえ ack-after-confirm 不変)。
_POKE_PATH_GUARD_CORR_ID = "reverse-poll-path-guard"


def _poke_path_lock_acquire():
    """★cycle5 fix3 (FKI-NO-DUP 真順守)★: bundle primitive 流用で poke 経路全体保護。"""
    if _BUNDLE_ACQUIRE_LOCK is None:
        return None  # bundle primitive 不在 = skip 安全側
    try:
        # timeout 0.0 = LOCK_NB 等価、別 process 保持中なら即 None
        return _BUNDLE_ACQUIRE_LOCK(_POKE_PATH_GUARD_CORR_ID, timeout_sec=0.0)
    except Exception as e:
        log(f"poke_path_lock acquire (bundle primitive) failed (safely skipped): {e}")
        return None


def _poke_path_lock_release(fd):
    if fd is None or _BUNDLE_RELEASE_LOCK is None:
        return
    try:
        _BUNDLE_RELEASE_LOCK(fd)
    except Exception as e:
        log(f"poke_path_lock release (bundle primitive) failed (non-fatal): {e}")


def _is_heartbeat(msg):
    """★止血 (4) priority filter★: enter_restart heartbeat を poke 経路から除外。"""
    topic = (msg.get("topic") or "")
    mt = (msg.get("message_type") or "")
    return ("enter_restart" in topic) and (mt == "status_update")


if success_count > 0:
    # ★二重投稿止血 (副院長令 24a47356、Commander msg_141451)★:
    #   poke 経路全体を単一 flock で保護。複数 watcher / 並列 process 同時発火時も
    #   1 つのみが poke を実行、他は LOCK_NB で即座 skip (race 根絶)。
    #   ★load_poked → check_candidates → fire_poke_local → record_poked → record_ts★
    #   全区間を単一 flock 区間で連続保持で atomic 保証。
    _poke_path_fd = _poke_path_lock_acquire()
    if _poke_path_fd is None:
        log(f"poke skip: poke_path_lock contended (other process holds, safely skipped, success_count={success_count})")
    else:
        try:
            # ★止血 (1)(4) dedup + priority filter★: poked 済 / heartbeat を除外した残候補
            _poked_ids = _load_poked_ids()
            _poke_candidates = [
                m for m in new_msgs
                if m.get("id")
                and m["id"] not in _poked_ids
                and not _is_heartbeat(m)
            ]

            if not _poke_candidates:
                log(f"poke skip: no eligible candidates (all heartbeat/already-poked, success_count={success_count})")
            elif _BUNDLE_FIRE_POKE_LOCAL is None:
                log(f"poke skip: bundle fire_poke_local unavailable (FKI-NO-DUP fallback, safely skipped)")
            else:
                # ★止血 (2) rate-limit 5 分★
                _last_ts = _load_last_poke_ts()
                _elapsed = time.time() - _last_ts
                if _elapsed < POKE_RATE_LIMIT_SEC:
                    log(f"poke skip: rate-limit elapsed={_elapsed:.1f}s < {POKE_RATE_LIMIT_SEC}s (will retry next polling)")
                else:
                    # ★止血 (3) bundle merge★: 1 polling = 1 poke、複数 candidates をまとめて 1 発火
                    _bundle_size = len(_poke_candidates)
                    corr_id = f"reverse-poll-poke-{int(time.time())}-bundle{_bundle_size}"
                    # ★案 A: bundle entrypoint fire_poke_local 直接呼出 (orchestration inline 廃止)★
                    #   bundle 内で validate_correlation_id + already_poked (flock) + wslpath
                    #   動的解決 + Win python.exe interop + safe_clipboard_poke + refined_v5_guard
                    #   + mark_poked (flock 永続化) 一式実行 = RED1/RED2/連投 axis1/4/6 全件根治。
                    result = _BUNDLE_FIRE_POKE_LOCAL(correlation_id=corr_id, timeout_sec=15.0)
                    _result_status = result.get("status")
                    log(
                        f"desktop_poke result (bundle={_bundle_size} corr={corr_id}): "
                        f"status={_result_status} rc={result.get('rc')} "
                        f"elapsed={result.get('elapsed_sec'):.3f}s"
                    )
                    # ★cycle5 fix1 (gunshi RED1 cure、家老 msg_142921)★: status==fired gate。
                    #   失敗 poke (v5_guard / no_edit / timeout / error 等) は mark せず
                    #   次 polling で retry 復活 (理事長/副院長 desktop 通知 lost 解消)。
                    #   skipped_dedupe (bundle 内 atomic dedupe hit) も mark で次回 skip OK。
                    if _result_status in ("fired", "skipped_dedupe"):
                        # ★止血 (1) bundle 内 candidates を poked にマーク (同一 msg 1 回限定)★
                        _record_poked_ids([m["id"] for m in _poke_candidates])
                        # ★止血 (2) last_poke_ts 更新 (次回 5 min 経過まで skip)★
                        _record_last_poke_ts(time.time())
                    else:
                        log(
                            f"poke not marked (status={_result_status}, will retry next polling): "
                            f"corr={corr_id} candidates_count={_bundle_size}"
                        )
        except subprocess.TimeoutExpired:
            log(f"desktop_poke TIMEOUT (Windows side stuck) — safely skipped, tmux nudge already sent")
        except Exception as e:
            # 障害時安全側: 全例外捕捉、log のみで暴走禁。tmux nudge は既送済ゆえ ack-after-confirm 不変。
            log(f"desktop_poke FAILED (safely skipped): {type(e).__name__}: {str(e)[:200]}")
        finally:
            # ★二重投稿止血 終端: poke_path_lock 解放 (例外時も release 保証)★
            _poke_path_lock_release(_poke_path_fd)

log(f"dispatched {success_count} ok, {fail_count} failed (total {len(new_msgs)})")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
