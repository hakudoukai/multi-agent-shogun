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

# Agent pane mapping for delivery metadata. Direct worker-pane send-keys is disabled by R2.
AGENT_PANES = {
    "karo-second": "multiagent-second:0.0",
    "shogun-second": "shogun-second:0.0",
    "ashigaru1": "multiagent-second:0.1",
    "ashigaru2": "multiagent-second:0.2",
    "ashigaru3": "multiagent-second:0.3",
    "ashigaru4": "multiagent-second:0.4",
    "ashigaru5": "multiagent-second:0.5",
    "ashigaru6": "multiagent-second:0.6",
    "ashigaru7": "multiagent-second:0.7",
    # R2 (FUKUINCHO 裁定 seq96053): gunshi-second を 0.8 に swap (最終正本 map)。
    "gunshi-second": "multiagent-second:0.8",
    # 2026-08-03 委員長(canon guardian): 本部長を受信allowlistへ追加。未登録により委員長→本部長のDB配送が
    #     missing_or_invalid_target_agent で構造的に全通落ちしていた(将軍second実測 seq137504)。
    "honbucho": "hermes-honbucho:0.0",
    # 注: ashigaru1-7 の最終 pane (0.1-0.7) 反映は R3-R9 の各 swap 段で更新予定。
    #     旧 ashigaru8@0.9 は登録撤回 (R0 seq96053) につき AGENT_PANES からも除外。
}
VALID_SECONDPC_TARGETS = frozenset(AGENT_PANES)

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
    """Escalate unresolved routing to FUKUINCHO/Commander once per handshake id."""
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
        log(f"ESCALATED unroutable {msg.get('id','')[:8]} reason={reason}")
    except Exception as e:
        log(f"ESCALATE failed for {msg.get('id','')[:8]}: {e}")


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

    # Self-send detection: from_pc == to_pc → immediate dead-letter
    if from_pc == to_pc:
        log(f"SELF-SEND detected: {msg_id[:8]} from={from_pc} to={to_pc} — dead-lettering")
        dead_letter_message(msg_id, "self_send_rejected")
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
        continue

    # Retry cap enforcement
    retry_count = retry_tracker.get(msg_id, 0)
    if retry_count >= MAX_RETRY:
        log(f"RETRY CAP exceeded ({retry_count}/{MAX_RETRY}): {msg_id[:8]} — dead-lettering")
        if dead_letter_message(msg_id, f"max_retry_exceeded_after_{retry_count}_attempts"):
            with open(processed_file, "a") as f:
                f.write(msg_id + "\n")
            # Clean up tracker entry
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
        if not target:
            reason = "missing_or_invalid_target_agent"
            append_dead_letter(msg, reason)
            escalate_unroutable(msg, reason)
            with open(processed_file, "a") as f:
                f.write(msg_id + "\n")
            retry_tracker.pop(msg_id, None)
            save_retry_tracker(retry_tracker)
            log(f"BLOCKED unroutable message without ACK: {msg_id[:8]} {topic}")
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
