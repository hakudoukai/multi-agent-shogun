#!/usr/bin/env python3
"""Poll processor for Desktop kuro (Claude.ai) bidirectional bridge.

Handles two directions:
  inbound:  Desktop kuro → main_pc (write to shogun inbox + auto-forward)
  outbound: main_pc → Desktop kuro (ntfy notification + ACK)
"""
import sys, json, os, subprocess, time

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = sys.argv[5]
direction = sys.argv[6] if len(sys.argv) > 6 else "inbound"

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[kuro_desktop][{direction}][{ts}] {msg}", file=sys.stderr)

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
MAX_RETRY = 3

# Retry tracking (persistent across polls)
RETRY_TRACKER_FILE = f"/tmp/hakudokai_kuro_desktop_{direction}_retry_tracker.json"

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
        log(f"DEAD-LETTERED: {msg_id[:8]} — {last_error}")
        return True
    except Exception as e:
        log(f"dead_letter ACK failed for {msg_id[:8]}: {e}")
        return False

retry_tracker = load_retry_tracker()

# Auto-forward patterns (same as fukuincho_poll.py)
AGENT_PATTERNS = {
    "ashigaru1": ["こうちゃんへ", "ashigaru1降下", "ashigaru1へ", "kouchan"],
    "ashigaru2": ["桜ちゃんへ", "ashigaru2降下", "ashigaru2へ", "sakura"],
    "ashigaru8": ["クロちゃんへ", "ashigaru8降下", "ashigaru8へ", "kuro"],
    "gunshi": ["軍師へ", "gunshi降下", "gunshiへ"],
}

def detect_forward_target(content, topic):
    text = (content + " " + topic).lower()
    for agent_id, patterns in AGENT_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text:
                return agent_id
    return None

for msg in new_msgs:
    msg_id = msg["id"]
    topic = msg.get("topic", "unknown")
    content = msg.get("content", "")
    priority = msg.get("priority", "normal")
    from_pc = msg.get("from_pc", "unknown")
    to_pc = msg.get("to_pc", "unknown")

    log(f"NEW: {msg_id[:8]} {topic} from {from_pc}")

    # Self-send detection
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
            retry_tracker.pop(msg_id, None)
            save_retry_tracker(retry_tracker)
        continue

    if direction == "inbound":
        # Desktop kuro → main_pc: write to shogun inbox + auto-forward
        summary = f"[kuro_desktop][{priority}] {topic}: {content[:300]}"

        # Auto-forward to target agent if detected
        forward_target = detect_forward_target(content, topic)
        if forward_target:
            fwd_cmd = [
                "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
                forward_target, summary, "task_assigned", "kuro_desktop"
            ]
            try:
                subprocess.run(fwd_cmd, check=True, capture_output=True, timeout=10)
                log(f"AUTO-FORWARD: {msg_id[:8]} -> {forward_target}")
            except Exception as e:
                log(f"AUTO-FORWARD FAILED to {forward_target}: {e}")

        # Always write to shogun inbox for awareness
        inbox_cmd = [
            "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
            "shogun", summary, "kuro_desktop_instruction", "kuro_desktop"
        ]
        write_ok = False
        try:
            subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
            write_ok = True
        except Exception as e:
            log(f"inbox_write FAILED: {e}")

    elif direction == "outbound":
        # main_pc → Desktop kuro: ntfy notification
        # FIX: Do NOT ACK on ntfy failure (prevents message loss)
        write_ok = False
        try:
            result = subprocess.run([
                "python3", os.path.join(script_dir, "shim", "hakudokai", "hakudokai_escalation.py"),
                "notify", "--level", "L2", "--summary", f"クロちゃんDesktop宛メッセージ: {topic[:50]}"
            ], capture_output=True, timeout=10)
            if result.returncode == 0:
                write_ok = True
                log(f"ntfy sent for {msg_id[:8]}")
            else:
                log(f"ntfy FAILED (exit={result.returncode}) for {msg_id[:8]}")
        except Exception as e:
            log(f"ntfy FAILED: {e}")

    # ACK in Supabase (only after confirmed delivery)
    if write_ok:
        try:
            import urllib.request
            from datetime import datetime, timezone
            ack_url = f"{api_url}/pc_handshake?id=eq.{msg_id}"
            ack_data = json.dumps({
                "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "acknowledged_by": "kuro_desktop_watcher"
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
        # Increment retry counter
        retry_tracker[msg_id] = retry_tracker.get(msg_id, 0) + 1
        save_retry_tracker(retry_tracker)
        log(f"will retry {msg_id[:8]} next poll ({retry_tracker[msg_id]}/{MAX_RETRY})")
        continue  # Do NOT record as processed

    # Record as processed + clean retry tracker
    if write_ok:
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
        if msg_id in retry_tracker:
            del retry_tracker[msg_id]
            save_retry_tracker(retry_tracker)

log(f"dispatched {success_count} ok, {fail_count} failed (total {len(new_msgs)})")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
