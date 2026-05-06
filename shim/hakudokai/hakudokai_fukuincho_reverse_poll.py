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

log(f"dispatched {success_count} ok, {fail_count} failed (total {len(new_msgs)})")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
