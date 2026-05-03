#!/usr/bin/env python3
"""Single poll iteration for fukuincho watcher. Called by the shell wrapper."""
import sys, json, os, subprocess

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = sys.argv[5]

try:
    with open(response_file) as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError, ValueError):
    sys.exit(0)

if not data:
    sys.exit(0)

with open(processed_file) as f:
    processed = set(line.strip() for line in f if line.strip())

new_msgs = [m for m in data if m.get("id") and m["id"] not in processed]
if not new_msgs:
    sys.exit(0)

for msg in new_msgs:
    msg_id = msg["id"]
    topic = msg.get("topic", "unknown")
    content = msg.get("content", "")
    priority = msg.get("priority", "normal")

    summary = f"[fukuincho][{priority}] {topic}: {content[:300]}"
    print(f"[fukuincho_watcher] NEW: {msg_id[:8]} {topic}", file=sys.stderr)

    # Write to shogun inbox
    inbox_cmd = [
        "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
        "shogun", summary, "fukuincho_instruction", "fukuincho"
    ]
    try:
        subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
    except Exception as e:
        print(f"[fukuincho_watcher] inbox_write failed: {e}", file=sys.stderr)

    # ACK in Supabase
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
    except Exception as e:
        print(f"[fukuincho_watcher] ACK failed for {msg_id[:8]}: {e}", file=sys.stderr)

    with open(processed_file, "a") as f:
        f.write(msg_id + "\n")

print(f"[fukuincho_watcher] dispatched {len(new_msgs)} messages", file=sys.stderr)
