#!/usr/bin/env python3
"""Single poll iteration for secondpc_watcher.

Processes messages from SecondPC (from_pc=second_pc) arriving on main PC.
Parses topic/content to detect target agent, writes to their inbox.
"""
import sys, json, os, subprocess, time, re, pathlib

response_file = sys.argv[1]
processed_file = sys.argv[2]
script_dir = sys.argv[3]
api_url = sys.argv[4]
api_key = sys.argv[5]

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[secondpc_watcher][{ts}] {msg}", file=sys.stderr)

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

def handle_reverse_file_sync(msg, project_root):
    """Handle file_sync from SecondPC → MainPC (reverse direction).

    Writes synced files to MainPC filesystem.
    Whitelist: exact paths for SecondPC agents (ashigaru2/8) only.
    Returns True only if ALL files were written successfully.
    """
    content = msg.get("content", "")
    try:
        payload = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        log("reverse_file_sync: invalid JSON payload")
        return False

    files = payload.get("files", [])
    if not files:
        log("reverse_file_sync: no files in payload")
        return False

    # SR1 fix: exact whitelist only — no prefix matching
    ALLOWED_EXACT = frozenset((
        "queue/reports/ashigaru2_report.yaml",
        "queue/reports/ashigaru8_report.yaml",
        "queue/tasks/ashigaru2.yaml",
        "queue/tasks/ashigaru8.yaml",
    ))

    real_root = os.path.realpath(project_root)
    written = 0
    failed = 0
    for entry in files:
        rel_path = entry.get("path", "")
        file_content = entry.get("content", "")

        # Security: prevent path traversal
        if ".." in rel_path:
            log(f"reverse_file_sync: REJECTED path traversal: {rel_path}")
            failed += 1
            continue

        # Security: exact whitelist check
        if rel_path not in ALLOWED_EXACT:
            log(f"reverse_file_sync: REJECTED path outside whitelist: {rel_path}")
            failed += 1
            continue

        target_path = os.path.join(project_root, rel_path)

        # Security: verify resolved path stays within project root
        if not os.path.realpath(target_path).startswith(real_root + os.sep):
            log(f"reverse_file_sync: REJECTED symlink escape: {rel_path}")
            failed += 1
            continue

        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)

        # Atomic write (tmp + rename)
        tmp_path = target_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            os.replace(tmp_path, target_path)
            written += 1
            log(f"reverse_file_sync: wrote {rel_path} ({len(file_content)} chars)")
        except Exception as e:
            log(f"reverse_file_sync: FAILED to write {rel_path}: {e}")
            failed += 1
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # SR5 fix: only return True if ALL files succeeded (no partial ACK)
    return written > 0 and failed == 0


def detect_target_agent(content, topic):
    """Detect target agent from cross_pc_inbox topic or content patterns.

    inbox_write.sh sets topic as 'cross_pc_inbox_{target_agent}'.
    Content format: [{from}→{target}][{type}] {message}
    """
    # Primary: parse topic (most reliable)
    m = re.match(r'cross_pc_inbox_(\w+)', topic)
    if m:
        return m.group(1)

    # Secondary: parse content header [from→target]
    m = re.search(r'\[(\w+)→(\w+)\]', content)
    if m:
        return m.group(2)

    # Fallback: keyword matching
    patterns = {
        "shogun": ["将軍へ", "shogunへ"],
        "karo": ["家老へ", "karoへ"],
        "gunshi": ["軍師へ", "gunshiへ"],
        "ashigaru1": ["こうちゃんへ", "ashigaru1へ"],
        "ashigaru3": ["ashigaru3へ"],
        "ashigaru4": ["ashigaru4へ"],
        "ashigaru5": ["ashigaru5へ"],
    }
    text = (content + " " + topic).lower()
    for agent_id, kws in patterns.items():
        for kw in kws:
            if kw.lower() in text:
                return agent_id

    # Default: send to karo (chain of command)
    return "karo"

for msg in new_msgs:
    msg_id = msg["id"]
    topic = msg.get("topic", "unknown")
    content = msg.get("content", "")
    priority = msg.get("priority", "normal")
    from_pc = msg.get("from_pc", "second_pc")

    message_type = msg.get("message_type", "")

    log(f"NEW: {msg_id[:8]} type={message_type} topic={topic}")

    # --- file_sync from SecondPC: write files to MainPC filesystem ---
    if message_type == "file_sync" or topic.startswith("reports_sync"):
        write_ok = handle_reverse_file_sync(msg, project_root=script_dir)
        if write_ok:
            ack_ok = False
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
                ack_ok = True
            except Exception as e:
                log(f"ACK failed for {msg_id[:8]}: {e}")
                fail_count += 1
            # SR4 fix: only record as processed after successful ACK
            if ack_ok:
                with open(processed_file, "a") as f:
                    f.write(msg_id + "\n")
            else:
                log(f"SKIPPED recording {msg_id[:8]} (ACK failed, will retry)")
        else:
            fail_count += 1
            log(f"SKIPPED ACK for {msg_id[:8]} (file_sync write failed)")
        continue

    target = detect_target_agent(content, topic)
    summary = f"[SecondPC][{priority}] {content[:500]}"

    log(f"  → target={target}")

    # Determine sender from content (e.g. [ashigaru2→gunshi])
    sender = "second_pc"
    m = re.search(r'\[(\w+)→', content)
    if m:
        sender = m.group(1)

    # Write to target agent's inbox
    inbox_cmd = [
        "bash", os.path.join(script_dir, "scripts", "inbox_write.sh"),
        target, summary, "cross_pc_delivery", sender
    ]
    write_ok = False
    try:
        result = subprocess.run(inbox_cmd, check=True, capture_output=True, timeout=10)
        write_ok = True
    except subprocess.CalledProcessError as e:
        log(f"inbox_write FAILED: exit={e.returncode} stderr={e.stderr.decode()[:200]}")
    except Exception as e:
        log(f"inbox_write FAILED: {e}")

    # ACK in Supabase (only after confirmed write)
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

    # Record as processed only if write succeeded
    if write_ok:
        with open(processed_file, "a") as f:
            f.write(msg_id + "\n")
    else:
        log(f"SKIPPED recording {msg_id[:8]} (write failed, will retry)")

if success_count or fail_count:
    log(f"dispatched {success_count} ok, {fail_count} failed (total {len(new_msgs)})")
sys.exit(1 if fail_count > 0 and success_count == 0 else 0)
