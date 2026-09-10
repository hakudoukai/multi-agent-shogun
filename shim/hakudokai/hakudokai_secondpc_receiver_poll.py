#!/usr/bin/env python3
"""SecondPC bridge receiver poll processor (v3).

v3 improvements:
  - file_sync support: message_type=file_sync → write files to local filesystem
    (task YAML, context files, CLAUDE.md synced from MainPC via Supabase)

v2 improvements:
  - processed_file で二重処理防止（ACK済みでも再ポーリングで拾う問題を解消）
  - inbox_write 失敗時はACKしない（メッセージ消失防止）
  - nudge は短い "inboxN" のみ送信（文章混入防止）
  - content は環境変数経由で inbox_write に渡す（quote injection防止）
  - from を正しい送信元に設定（固定 "karo" ではなく実際の from_pc）
"""
import sys, json, os, subprocess, time, pathlib

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not api_key:
    raise SystemExit("SUPABASE_SERVICE_ROLE_KEY env is required")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[receiver][{ts}] {msg}", file=sys.stderr)

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

# Retry tracking file (persistent across polls)
RETRY_TRACKER_FILE = os.environ.get(
    "SECONDPC_RECEIVER_RETRY_TRACKER_FILE",
    "/tmp/hakudokai_receiver_retry_tracker.json",
)

# ff5c9068: unroutable 通知の一度性は ★此の file★ が持つ。
# 之まで docstring は "once per handshake id" と名乗り乍ら 函の内に dedupe が無く、
# 一度性は呼手の processed_file に頼つて居た (argv[2] にて外から渡る = 別 path を渡さるれば再び通知)。
# 通知の store と 処理済の store を分けず一つに寄せる。
UNROUTABLE_NOTIFIED_FILE = os.environ.get(
    "SECONDPC_RECEIVER_UNROUTABLE_NOTIFIED_FILE",
    os.path.join(script_dir, "queue", "inbox", "_unroutable_notified_second.txt"),
)


def load_unroutable_notified():
    """Return the set of handshake ids whose unroutable notice already went out."""
    try:
        with open(UNROUTABLE_NOTIFIED_FILE, encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except (FileNotFoundError, NotADirectoryError):
        return set()


def record_unroutable_notified(msg_id):
    """Record one handshake id as notified. Called ONLY after a confirmed POST."""
    if not msg_id:
        return
    path = pathlib.Path(UNROUTABLE_NOTIFIED_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(msg_id + "\n")


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
        dl_url = f"{api_url}/pc_handshake?id=eq.{msg_id}"
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
        log(f"DEAD-LETTERED: {msg_id[:8]} after {MAX_RETRY} retries")
        return True
    except Exception as e:
        log(f"dead_letter ACK failed for {msg_id[:8]}: {e}")
        return False

retry_tracker = load_retry_tracker()

# Receiver routing identity.  Do not pin roles to a physical pane index: the live
# fleet can be reshuffled and an old index can point at a different worker.  The
# @agent_id form is resolved from the pane title only for diagnostic metadata;
# R2 keeps direct send-keys disabled.
AGENT_PANES = {
    "karo-second": "@karo-second",
    # Current tmux user options are the receiver's live identity source; their
    # names are intentionally independent of the legacy ashigaru1-7 aliases.
    "ashigaru1": "@ashigaru-second-1",
    "ashigaru2": "@ashigaru-second-2",
    "ashigaru3": "@ashigaru-second-3",
}
# These seats own their own downlink.  The generic receiver must neither write
# their inbox nor change any acknowledgement field: doing so creates a false
# read mark when their dedicated pane/receiver is unavailable.
DOWNLINK_OWNED_TARGETS = frozenset({"gunshi-second", "honbucho", "dr-s"})
VALID_SECONDPC_TARGETS = frozenset(AGENT_PANES) | DOWNLINK_OWNED_TARGETS

DELIVERY_STATE_FILE = os.environ.get(
    "SECONDPC_RECEIVER_DELIVERY_STATE_FILE",
    os.path.join(script_dir, "queue", "inbox", "_delivery_state_second.yaml"),
)
DELIVERY_STATE_NOTIFIED_FILE = os.environ.get(
    "SECONDPC_RECEIVER_DELIVERY_STATE_NOTIFIED_FILE",
    os.path.join(script_dir, "queue", "inbox", "_delivery_state_notified_second.txt"),
)

def resolve_agent_pane(agent_id, pane_lines=None):
    """Resolve a worker by its current @agent_id identity, never a pane index.

    This is diagnostic-only while R2 disables direct worker-pane send-keys.
    ``pane_lines`` is injectable so the contract can be tested without tmux.
    """
    identity = AGENT_PANES.get(agent_id)
    if not identity:
        return None
    if pane_lines is None:
        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_index}.#{pane_index}|#{@agent_id}"],
                capture_output=True, text=True, timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        pane_lines = result.stdout.splitlines()
    role = identity[1:]
    for line in pane_lines:
        target, sep, agent_id = line.partition("|")
        if sep and agent_id.strip() == role:
            return target
    return None

def _already_delivery_notified(msg_id):
    try:
        with open(DELIVERY_STATE_NOTIFIED_FILE, encoding="utf-8") as f:
            return msg_id in {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return False

def record_delivery_state(msg, state, reason):
    """Preserve a failed delivery locally without mutating handshake ACK fields."""
    path = pathlib.Path(DELIVERY_STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    msg_id = str(msg.get("id", ""))
    existing = path.read_text(encoding="utf-8") if path.exists() else "messages:\n"
    if msg_id and f"_handshake_id: {msg_id}\n" in existing:
        return
    entry = (
        f"  - _handshake_id: {msg_id}\n"
        f"    delivery_state: {state}\n"
        f"    reason: {json.dumps(reason, ensure_ascii=False)}\n"
        f"    from_pc: {json.dumps(str(msg.get('from_pc', 'unknown')), ensure_ascii=False)}\n"
        f"    target_agent: {json.dumps(str(detect_target(msg) or ''), ensure_ascii=False)}\n"
        "    acknowledged_mutation: false\n"
    )
    path.write_text(existing.rstrip("\n") + "\n" + entry, encoding="utf-8")

def notify_delivery_failure(msg, reason):
    """Return a single failure notice to the sender; never PATCH the original row."""
    msg_id = str(msg.get("id", ""))
    if not msg_id or _already_delivery_notified(msg_id):
        return True
    sender = str(msg.get("from_pc", "") or "")
    if not sender or sender == "second_pc":
        return False
    try:
        import urllib.request
        payload = json.dumps({
            "message_type": "status_update", "from_pc": "second_pc", "to_pc": sender,
            "topic": "receiver_delivery_failed",
            "content": f"SecondPC receiver delivery pending: source_id={msg_id}; reason={reason}; original ACK unchanged.",
            "requires_response": False, "priority": "high", "clinic_id": "hakudoukai_main",
        }, ensure_ascii=False).encode()
        req = urllib.request.Request(f"{api_url}/pc_handshake", data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("apikey", api_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        with urllib.request.urlopen(req, timeout=10):
            pass
        pathlib.Path(DELIVERY_STATE_NOTIFIED_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(DELIVERY_STATE_NOTIFIED_FILE, "a", encoding="utf-8") as f:
            f.write(msg_id + "\n")
        return True
    except Exception as exc:
        log(f"delivery failure notice failed for {msg_id[:8]}: {exc}")
        return False

def preserve_delivery_failure(msg, reason):
    record_delivery_state(msg, "delivery_failed", reason)
    notify_delivery_failure(msg, reason)
    log(f"delivery pending without ACK mutation: {msg.get('id', '')[:8]} reason={reason}")

VALID_SECONDPC_TARGETS = frozenset(AGENT_PANES) | DOWNLINK_OWNED_TARGETS

def handle_file_sync(msg, script_dir):
    """Handle file_sync messages: write synced files to local filesystem.

    Content is JSON: {"target_agent": "ashigaru2", "files": [{"path": "queue/tasks/ashigaru2.yaml", "content": "..."}]}
    Allowed paths: queue/tasks/*.yaml, context/*.md, CLAUDE.md
    """
    content = msg.get("content", "")
    try:
        payload = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        log(f"file_sync: invalid JSON payload")
        return False

    files = payload.get("files", [])
    if not files:
        log("file_sync: no files in payload")
        return False

    # Whitelist of allowed path patterns (security: prevent arbitrary file writes)
    ALLOWED_PREFIXES = ("queue/tasks/", "context/", "CLAUDE.md")

    written = 0
    for entry in files:
        rel_path = entry.get("path", "")
        file_content = entry.get("content", "")

        # Security: only allow whitelisted paths
        if not any(rel_path.startswith(prefix) or rel_path == prefix for prefix in ALLOWED_PREFIXES):
            log(f"file_sync: REJECTED path outside whitelist: {rel_path}")
            continue

        # Security: prevent path traversal
        if ".." in rel_path:
            log(f"file_sync: REJECTED path traversal: {rel_path}")
            continue

        target_path = os.path.join(script_dir, rel_path)
        target_dir = os.path.dirname(target_path)

        # Ensure directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Write file atomically (tmp + rename)
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            os.replace(tmp_path, target_path)
            written += 1
            log(f"file_sync: wrote {rel_path} ({len(file_content)} chars)")
        except Exception as e:
            log(f"file_sync: FAILED to write {rel_path}: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    return written > 0


def _target_from_json_content(content):
    stripped = (content or "").strip()
    if not stripped.startswith("{"):
        return None
    try:
        payload = json.loads(stripped)
    except (json.JSONDecodeError, TypeError):
        return None
    target = payload.get("target_agent")
    return target if target in VALID_SECONDPC_TARGETS else None


def _target_from_context_data(msg):
    context_data = msg.get("context_data")
    if not context_data:
        return None
    if isinstance(context_data, str):
        try:
            context_data = json.loads(context_data)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(context_data, dict):
        return None
    target = context_data.get("target_agent")
    return target if target in VALID_SECONDPC_TARGETS else None


def _sender_agent_from_context_data(msg):
    """Return the declared sending role, or None when identity is absent/ambiguous."""
    context_data = msg.get("context_data")
    if isinstance(context_data, str):
        try:
            context_data = json.loads(context_data)
        except (json.JSONDecodeError, TypeError):
            return None
    if not isinstance(context_data, dict):
        return None
    sender = context_data.get("sender_agent")
    return sender if isinstance(sender, str) and sender else None


def is_same_agent_send(msg):
    """Reject only a same-PC row whose declared sender equals its resolved target.

    Same-PC delivery between different canonical roles is valid.  If the sender
    role is missing, fail closed because equality cannot be established safely.
    """
    if msg.get("from_pc") != msg.get("to_pc"):
        return False
    sender = _sender_agent_from_context_data(msg)
    target = detect_target(msg)
    return sender is None or target is None or sender == target


def detect_target(msg):
    """Resolve SecondPC target agent deterministically.

    R2 rules:
      - accept only structured target_agent or topic cross_pc_inbox_<agent>;
      - support hyphenated role ids such as karo-second and shogun-second;
      - never infer from free-text keyword substrings;
      - never fall back to maeda/default agent.
    """
    import re
    content = msg.get("content", "") or ""
    topic = msg.get("topic", "") or ""

    target = _target_from_context_data(msg)
    if target:
        return target

    m = re.match(r"cross_pc_inbox_([\w-]+)", topic)  # 2026-08-03 委員長: prefix許容(接尾辞で全落ちする欠陥是正・将軍second seq137513/CLAUDE.md規約はprefix)
    if m:
        target = m.group(1)
        if target in VALID_SECONDPC_TARGETS:
            return target
        log(f"BLOCK: invalid cross_pc_inbox target={target} topic={topic}")
        return None

    target = _target_from_json_content(content)
    if target:
        return target

    log(f"BLOCK: missing structured target_agent for topic={topic}")
    return None


def append_dead_letter(msg, reason):
    """Append unresolved message to local dead-letter YAML without ACK-as-progress semantics."""
    path = pathlib.Path(script_dir) / "queue" / "inbox" / "_dead_letter_second.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    msg_id = msg.get("id", "")
    existing = path.read_text(encoding="utf-8") if path.exists() else "messages:\n"
    if msg_id and msg_id in existing:
        return
    content_head = (msg.get("content", "") or "")[:240].replace("\n", "\\n").replace('"', '\\"')
    topic = (msg.get("topic", "") or "").replace('"', '\\"')
    entry = (
        f"  - id: dead_{int(time.time())}_{msg_id[:8]}\n"
        f"    _handshake_id: {msg_id}\n"
        f"    from: {msg.get('from_pc', 'unknown')}\n"
        f"    type: unroutable\n"
        f"    reason: {reason}\n"
        f"    topic: \"{topic}\"\n"
        f"    content_head: \"{content_head}\"\n"
        f"    read: false\n"
    )
    if not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + entry, encoding="utf-8")


def escalate_unroutable(msg, reason):
    """Escalate unresolved routing to FUKUINCHO/Commander once per handshake id.

    ff5c9068: the once-per-id promise is now ENFORCED HERE (UNROUTABLE_NOTIFIED_FILE),
    not assumed from the caller's processed_file.

    Returns True when the recipient has the notice (sent now, or sent on an earlier
    scan). Returns False when the POST failed — the caller must NOT record the
    message as processed, so the bounce is retained and retried under MAX_RETRY.
    """
    msg_id = msg.get("id", "")
    if msg_id and msg_id in load_unroutable_notified():
        log(f"unroutable notice already sent for {msg_id[:8]} - dedupe, not resending")
        return True
    try:
        import urllib.request
        payload = json.dumps({
            "message_type": "status_update",
            "from_pc": "second_pc",
            "to_pc": "fukuincho",
            "topic": "wrong_recipient_or_unroutable",
            "content": (
                f"SecondPC receiver BLOCKED unroutable message. "
                f"reason={reason}; source_id={msg.get('id','')}; "
                f"topic={msg.get('topic','')}; no fallback/keyword/default routing used."
            ),
            "requires_response": False,
            "priority": "high",
            "clinic_id": "hakudoukai_main",
        }, ensure_ascii=False).encode()
        req = urllib.request.Request(f"{api_url}/pc_handshake", data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("apikey", api_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        with urllib.request.urlopen(req, timeout=10):
            pass
        record_unroutable_notified(msg_id)
        log(f"ESCALATED unroutable {msg_id[:8]} reason={reason}")
        return True
    except Exception as e:
        # no-silent-failure: the notice did NOT land. Do not record it as sent,
        # and tell the caller so the row is not buried as processed.
        log(f"ESCALATE failed for {msg_id[:8]}: {e}")
        return False


def send_nudge(agent_id, count):
    """R2: direct worker-pane send-keys disabled; watcher/inotify handles delivery."""
    log(f"nudge disabled by R2 for {agent_id} count={count}")


# Track per-agent delivery counts for nudge
agent_deliveries = {}

for msg in new_msgs:
    msg_id = msg["id"]
    topic = msg.get("topic", "unknown")
    content = msg.get("content", "")
    from_pc = msg.get("from_pc", "unknown")
    to_pc = msg.get("to_pc", "unknown")
    message_type = msg.get("message_type", "")

    log(f"NEW: {msg_id[:8]} type={message_type} topic={topic} from {from_pc}")

    # Same-PC delivery is valid across distinct roles.  Reject only a proven
    # same-role send; missing/invalid sender identity fails closed.
    if is_same_agent_send(msg):
        log(f"SELF-SEND detected: {msg_id[:8]} from={from_pc} to={to_pc} — dead-lettering")
        dead_letter_message(msg_id, "self_send_rejected")
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
        continue

    # Retry cap must not fabricate a recipient read. Preserve failure locally and
    # notify the sender; the original handshake row stays unacknowledged.
    retry_count = retry_tracker.get(msg_id, 0)
    if retry_count >= MAX_RETRY:
        reason = f"max_retry_exceeded_after_{retry_count}_attempts"
        preserve_delivery_failure(msg, reason)
        retry_tracker.pop(msg_id, None)
        save_retry_tracker(retry_tracker)
        continue

    # --- file_sync: write files to local filesystem (no inbox_write needed) ---
    if message_type == "file_sync" or topic.startswith("file_sync"):
        write_ok = handle_file_sync(msg, script_dir)
        if write_ok:
            # Determine target agent for nudge
            try:
                payload = json.loads(content)
                target = payload.get("target_agent")
            except (json.JSONDecodeError, TypeError):
                target = None
            if target in VALID_SECONDPC_TARGETS:
                agent_deliveries[target] = agent_deliveries.get(target, 0) + 1
    else:
        # --- Standard message: write to inbox ---
        target = detect_target(msg)
        if target in DOWNLINK_OWNED_TARGETS:
            # Dedicated downlink owns its recipient ACK.  The generic receiver
            # must not write, retry, or mutate this source row.
            preserve_delivery_failure(msg, "target_owned_by_dedicated_downlink")
            continue
        if not target:
            # Preserve an invalid target locally without mutating the original
            # recipient ACK.  Keep the established one-time escalation so the
            # sender-side control plane sees the fault; only the source row is
            # never PATCHed as read/dead_letter.
            reason = "missing_or_invalid_target_agent"
            append_dead_letter(msg, reason)
            if not escalate_unroutable(msg, reason):
                fail_count += 1
                retry_tracker[msg_id] = retry_tracker.get(msg_id, 0) + 1
                save_retry_tracker(retry_tracker)
                log(f"BLOCKED unroutable {msg_id[:8]} and NOTICE FAILED - "
                    f"not recorded as processed (retry {retry_tracker[msg_id]}/{MAX_RETRY})")
                continue
            with open(processed_file, "a") as f:
                f.write(msg_id + "\n")
            retry_tracker.pop(msg_id, None)
            save_retry_tracker(retry_tracker)
            log(f"LOCAL DEAD-LETTER without ACK mutation: {msg_id[:8]} {topic}")
            continue

        inbox_cmd = [
            "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
            target, content, (message_type or "task_assigned"), from_pc
        ]
        write_ok = False
        try:
            env = os.environ.copy()
            env["INBOX_CONTENT"] = content
            result = subprocess.run(inbox_cmd, capture_output=True, timeout=10, env=env)
            if result.returncode == 0:
                write_ok = True
            else:
                log(f"inbox_write FAILED for {target}: exit={result.returncode} stderr={result.stderr.decode()[:200]}")
        except Exception as e:
            log(f"inbox_write FAILED for {target}: {e}")

    # ACK only after confirmed write
    if write_ok:
        try:
            import urllib.request
            from datetime import datetime, timezone
            ack_url = f"{api_url}/pc_handshake?id=eq.{msg_id}"
            ack_data = json.dumps({
                "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "acknowledged_by": "second_pc"
            }).encode()
            req = urllib.request.Request(ack_url, data=ack_data, method="PATCH")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("apikey", api_key)
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "return=minimal")
            with urllib.request.urlopen(req, timeout=10) as _resp:
                pass
            success_count += 1
            agent_deliveries[target] = agent_deliveries.get(target, 0) + 1
            log(f"delivered to {target}+ACK: {msg_id[:8]} {topic}")
        except Exception as e:
            log(f"ACK failed for {msg_id[:8]}: {e}")
            fail_count += 1
    else:
        fail_count += 1
        # Increment retry counter for next poll
        retry_tracker[msg_id] = retry_tracker.get(msg_id, 0) + 1
        save_retry_tracker(retry_tracker)
        log(f"SKIPPED ACK for {msg_id[:8]} (failed, retry {retry_tracker[msg_id]}/{MAX_RETRY})")
        continue  # Do NOT record as processed

    # Record as processed + clean retry tracker
    with open(processed_file, "a") as f:
        f.write(msg_id + "\n")
    if msg_id in retry_tracker:
        del retry_tracker[msg_id]
        save_retry_tracker(retry_tracker)

# Send nudge per agent (one nudge with total count, not per message)
for agent_id, count in agent_deliveries.items():
    send_nudge(agent_id, count)

log(f"total: {success_count} ok, {fail_count} failed (of {len(new_msgs)} new)")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
