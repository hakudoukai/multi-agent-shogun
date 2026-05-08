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
api_key = sys.argv[5]

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
RETRY_TRACKER_FILE = "/tmp/hakudokai_receiver_retry_tracker.json"

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

# Agent pane mapping for nudge
AGENT_PANES = {
    # §18 SecondPC 配置 (CLAUDE.md §18.1、2026-05-06 移行 + Phase 4-5 体制改編):
    #   家老 1体: maeda = multiagent:agents.0 (旧 instructions/maeda.md §1)
    #   通常 ashigaru 3体: ashigaru5/6/7 = multiagent:agents.0/1/2
    #     ※ maeda と ashigaru5 は同 pane (multiagent:agents.0) に同居していない、
    #     SecondPC tmux session の実 pane 構成は shutsujin_departure_secondpc.sh が決定。
    #     旧期 receiver の pane 表は ashigaru5 を 0、ashigaru6 を 1 等としていたが、
    #     maeda 新設 (Phase 4) で実体は maeda=0、ashigaru5=1、ashigaru6=2、ashigaru7=3 へ
    #     再編されている可能性あり (= shutsujin script を SSoT として確認すべし)。
    #   非常時 +1: ashigaru8 = multiagent:agents.4 (= 暫定、shutsujin で確定)
    "maeda": "multiagent:agents.0",
    "ashigaru5": "multiagent:agents.1",
    "ashigaru6": "multiagent:agents.2",
    "ashigaru7": "multiagent:agents.3",
    "ashigaru8": "multiagent:agents.4",
    # 旧体制 (廃止) — sakura(ashigaru2) は §18 で MainPC 所属に変更
    # "ashigaru2": "secondpc:0.0",  # 削除済 (= MainPC 所属、SecondPC で受信すべきでない)
}

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


def detect_target(content, topic):
    """Detect target agent from topic/content (§18 PC配置準拠).

    旧体制 sakura/kuro hardcode 廃止。topic=cross_pc_inbox_<agent> から
    正規表現で抽出し、SecondPC 所属 agent (§18 配置) のみ accept。
    不明な場合は警告ログ + maeda フォールバック (= SecondPC 家老が一次受領)。

    バグ修正 2026-05-07: 旧コードは default=ashigaru2 で全配信が ashigaru2 に
    誤転送されていた (家老が ashigaru5/6/7 に発令しても全部 ashigaru2 へ)。
    バグ修正 2026-05-08: maeda (= SecondPC 家老、Phase 4-5 体制改編で新設)
    が valid_secondpc に未登録のため、信長 → maeda 宛 msg が fallback で
    全件 ashigaru5 に misroute されていた。maeda + 全 SecondPC 所属を
    AGENT_PANES と整合させた。default も ashigaru5 → maeda に変更
    (= 不明 msg は家老が一次受領、配下に裁量配信、誤配信抑止)。
    """
    import re
    valid_secondpc = frozenset(["maeda", "ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"])

    # Primary: parse topic (most reliable)
    m = re.match(r'cross_pc_inbox_(\w+)', topic)
    if m:
        target = m.group(1)
        if target in valid_secondpc:
            return target

    # Secondary: parse content header [from→target]
    m = re.search(r'\[(\w+)→(\w+)\]', content)
    if m:
        target = m.group(2)
        if target in valid_secondpc:
            return target

    # Fallback: keyword
    text = (content + " " + topic).lower()
    for agent in ("maeda", "ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"):
        if agent in text:
            return agent
    if "kuro" in text or "クロ" in content:
        return "ashigaru8"

    # Default: maeda (= SecondPC 家老、不明 msg 一次受領 + 配下裁量配信)
    log(f"WARN: target unknown for topic={topic}, falling back to maeda")
    return "maeda"

def send_nudge(agent_id, count):
    """Send minimal nudge (inboxN only, no content)."""
    pane = AGENT_PANES.get(agent_id)
    if not pane:
        return
    nudge = f"inbox{count}"
    try:
        # Check if agent is busy (has running process)
        result = subprocess.run(
            ["tmux", "display-message", "-t", pane, "-p", "#{pane_current_command}"],
            capture_output=True, text=True, timeout=5
        )
        current_cmd = result.stdout.strip()
        # Only nudge if at shell prompt (bash/zsh) or claude prompt
        if current_cmd in ("bash", "zsh", "claude", "node"):
            subprocess.run(
                ["tmux", "send-keys", "-t", pane, nudge, ""],
                capture_output=True, timeout=5
            )
            time.sleep(0.3)
            subprocess.run(
                ["tmux", "send-keys", "-t", pane, "Enter", ""],
                capture_output=True, timeout=5
            )
            log(f"nudge sent to {agent_id} ({pane}): {nudge}")
        else:
            log(f"nudge deferred for {agent_id} (busy: {current_cmd})")
    except Exception as e:
        log(f"nudge failed for {agent_id}: {e}")

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
                target = payload.get("target_agent", "ashigaru5")  # §18: default を ashigaru5 (旧 sakura 後継)
            except (json.JSONDecodeError, TypeError):
                target = detect_target(content, topic)
            agent_deliveries[target] = agent_deliveries.get(target, 0) + 1
    else:
        # --- Standard message: write to inbox ---
        target = detect_target(content, topic)

        inbox_cmd = [
            "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
            target, content[:500], "task_assigned", from_pc
        ]
        write_ok = False
        try:
            env = os.environ.copy()
            env["INBOX_CONTENT"] = content[:500]
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
