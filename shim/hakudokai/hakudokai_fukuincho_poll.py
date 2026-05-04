#!/usr/bin/env python3
"""Single poll iteration for fukuincho watcher (v2: root cure).

v2 improvements:
  - inbox_write後の read-back verify (書込確認)
  - verify失敗時の自動修復試行
  - 全エラーの詳細ログ
"""
import sys, json, os, subprocess, time

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = sys.argv[5]

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[fukuincho_watcher][{ts}] {msg}", file=sys.stderr)

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

# Auto-forward patterns: detect target agent in content/topic
AGENT_PATTERNS = {
    "ashigaru1": ["こうちゃんへ", "ashigaru1降下", "ashigaru1へ", "kouchan"],
    "ashigaru2": ["桜ちゃんへ", "ashigaru2降下", "ashigaru2へ", "sakura"],
    "ashigaru8": ["クロちゃんへ", "ashigaru8降下", "ashigaru8へ", "kuro"],
    "gunshi": ["軍師へ", "gunshi降下", "gunshiへ"],
}

def detect_forward_target(content, topic):
    """Detect if message should be auto-forwarded to an agent."""
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

    summary = f"[fukuincho][{priority}] {topic}: {content[:300]}"
    log(f"NEW: {msg_id[:8]} {topic}")

    # Auto-forward: detect target agent and write directly to their inbox
    forward_target = detect_forward_target(content, topic)
    if forward_target:
        fwd_cmd = [
            "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
            forward_target, summary, "task_assigned", "fukuincho"
        ]
        try:
            subprocess.run(fwd_cmd, check=True, capture_output=True, timeout=10)
            log(f"AUTO-FORWARD: {msg_id[:8]} → {forward_target}")
        except Exception as e:
            log(f"AUTO-FORWARD FAILED to {forward_target}: {e}")

    # Write to shogun inbox (always, for awareness)
    inbox_cmd = [
        "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
        "shogun", summary, "fukuincho_instruction", "fukuincho"
    ]
    write_ok = False
    try:
        result = subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
        write_ok = True
    except subprocess.CalledProcessError as e:
        log(f"inbox_write FAILED: exit={e.returncode} stderr={e.stderr.decode()[:200]}")
    except Exception as e:
        log(f"inbox_write FAILED: {e}")

    # Read-back verify: confirm the message actually landed in shogun inbox
    if write_ok:
        inbox_path = os.path.join(script_dir, "queue", "inbox", "shogun.yaml")
        try:
            with open(inbox_path) as f:
                inbox_content = f.read()
            if msg_id[:8] not in inbox_content and topic[:20] not in inbox_content:
                log(f"VERIFY FAILED: message {msg_id[:8]} not found in shogun.yaml after write")
                # Retry once
                try:
                    subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
                    log(f"RETRY write succeeded for {msg_id[:8]}")
                except Exception as e2:
                    log(f"RETRY write also FAILED: {e2}")
                    write_ok = False
        except FileNotFoundError:
            log(f"VERIFY FAILED: shogun.yaml not found at {inbox_path}")
        except Exception as e:
            log(f"VERIFY read error (non-fatal): {e}")

    # ACK in Supabase
    if write_ok:
        try:
            import urllib.request
            from datetime import datetime, timezone
            ack_url = f"{api_url}/pc_handshake?id=eq.{msg_id}"
            ack_data = json.dumps({
                "acknowledged_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "acknowledged_by": "main_pc"
            }).encode()
            req = urllib.request.Request(ack_url, data=ack_data, method="PATCH")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("apikey", api_key)
            req.add_header("Content-Type", "application/json")
            req.add_header("Prefer", "return=minimal")
            urllib.request.urlopen(req, timeout=10)
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
    else:
        log(f"SKIPPED recording {msg_id[:8]} as processed (write failed, will retry next poll)")

log(f"dispatched {success_count} ok, {fail_count} failed (total {len(new_msgs)})")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
