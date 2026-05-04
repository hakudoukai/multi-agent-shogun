#!/usr/bin/env python3
"""Daily summary generator for fukuincho (副医院長).

Generates a morning summary of overnight activity and sends it to Supabase
so the 理事長 can review via Claude Desktop or ntfy.

Usage:
  python3 hakudokai_daily_summary.py generate   # Generate and INSERT
  python3 hakudokai_daily_summary.py preview     # Preview only (no INSERT)
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def get_env():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        env_file = os.path.expanduser("~/.hakudokai/env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip().replace("\r", "")
                    if line.startswith("SUPABASE_URL="):
                        url = line.split("=", 1)[1]
                    elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                        key = line.split("=", 1)[1]
    return url, key


def get_recent_handshakes(url, key, hours=24):
    """Get pc_handshake messages from the last N hours."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = (
        f"{url}/rest/v1/pc_handshake"
        f"?created_at=gte.{cutoff}"
        f"&order=created_at.desc&limit=100"
    )
    try:
        req = urllib.request.Request(query)
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("apikey", key)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Failed to fetch handshakes: {e}", file=sys.stderr)
        return []


def get_git_log(hours=24):
    """Get git commits from the last N hours."""
    since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
            capture_output=True, cwd=PROJECT_ROOT, timeout=10
        )
        return result.stdout.decode().strip().split("\n") if result.stdout else []
    except Exception:
        return []


def get_unpushed_commits():
    """Check for commits not yet pushed."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "origin/main..HEAD"],
            capture_output=True, cwd=PROJECT_ROOT, timeout=10
        )
        lines = result.stdout.decode().strip().split("\n") if result.stdout.strip() else []
        return [l for l in lines if l.strip()]
    except Exception:
        return []


def get_watcher_health():
    """Read watcher health files."""
    health = {}
    health_files = [
        ("/tmp/hakudokai_health_dashboard.json", "watchdog"),
        ("/tmp/hakudokai_fukuincho_watcher_health.json", "fukuincho_watcher"),
        ("/tmp/hakudokai_fukuincho_reverse_health.json", "reverse_watcher"),
    ]
    for path, name in health_files:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                health[name] = "running" if data.get("status") == "running" else "unknown"
            except Exception:
                health[name] = "error_reading"
        else:
            health[name] = "not_running"
    return health


def get_pending_approvals(url, key):
    """Check for L4 items waiting for 理事長 approval."""
    query = (
        f"{url}/rest/v1/pc_handshake"
        f"?to_pc=eq.fukuincho&requires_response=eq.true&acknowledged_at=is.null"
        f"&order=created_at.desc&limit=10"
    )
    try:
        req = urllib.request.Request(query)
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("apikey", key)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except Exception:
        return []


def generate_summary():
    """Generate the daily summary."""
    url, key = get_env()

    # Gather data
    handshakes = get_recent_handshakes(url, key) if url else []
    git_commits = get_git_log()
    unpushed = get_unpushed_commits()
    health = get_watcher_health()
    pending = get_pending_approvals(url, key) if url else []

    # Classify handshakes by type
    from_shogun = [h for h in handshakes if h.get("from_pc") == "main_pc"]
    from_fukuincho = [h for h in handshakes if h.get("from_pc") == "fukuincho"]
    urgent = [h for h in handshakes if h.get("priority") == "urgent" or h.get("message_type") == "urgent_stop"]

    # Build summary
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# 日次サマリー ({now})",
        "",
        "## 夜間活動",
        f"- 将軍→副医院長 メッセージ: {len(from_shogun)}件",
        f"- 副医院長→将軍 メッセージ: {len(from_fukuincho)}件",
        f"- 緊急アラート: {len(urgent)}件",
        "",
        "## Git",
        f"- 過去24hのコミット: {len(git_commits)}件",
    ]

    if git_commits:
        for c in git_commits[:5]:
            lines.append(f"  - {c}")
        if len(git_commits) > 5:
            lines.append(f"  - ... 他 {len(git_commits)-5}件")

    lines.append(f"- Push未済コミット: {len(unpushed)}件")
    if unpushed:
        for c in unpushed:
            lines.append(f"  - {c}")

    lines.extend([
        "",
        "## Watcher状態",
    ])
    for name, status in health.items():
        icon = "OK" if status == "running" else "NG"
        lines.append(f"- {name}: {icon} ({status})")

    if pending:
        lines.extend([
            "",
            "## 承認待ち (L4)",
        ])
        for p in pending:
            lines.append(f"- [{p.get('topic', '?')}] {p.get('content', '')[:100]}")

    if urgent:
        lines.extend([
            "",
            "## 緊急アラート",
        ])
        for u in urgent:
            lines.append(f"- [{u.get('topic', '?')}] {u.get('content', '')[:100]}")

    lines.extend([
        "",
        "## 異常検出",
        "- " + ("なし" if not urgent and all(v == "running" for v in health.values()) else "あり (上記参照)"),
    ])

    return "\n".join(lines)


def insert_summary(summary):
    """Insert summary into Supabase pc_handshake."""
    url, key = get_env()
    if not url or not key:
        print("ERROR: Supabase credentials required", file=sys.stderr)
        return False

    data = json.dumps({
        "message_type": "status_update",
        "from_pc": "main_pc",
        "to_pc": "fukuincho",
        "topic": f"daily_summary_{datetime.now().strftime('%Y%m%d')}",
        "content": summary[:2000],
        "requires_response": False,
        "priority": "normal",
        "clinic_id": CLINIC_ID,
        "bypass_5round_limit": False,
        "is_meta_only": False,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/pc_handshake",
            data=data, method="POST"
        )
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("apikey", key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        urllib.request.urlopen(req, timeout=15)
        print("Daily summary inserted to Supabase.", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Insert failed: {e}", file=sys.stderr)
        return False


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "preview"
    summary = generate_summary()

    if action == "preview":
        print(summary)
    elif action == "generate":
        print(summary)
        insert_summary(summary)
        # Also send ntfy
        try:
            subprocess.run(
                ["python3", os.path.join(SCRIPT_DIR, "hakudokai_escalation.py"),
                 "notify", "--level", "L2", "--summary", "日次サマリー生成完了"],
                capture_output=True, timeout=10
            )
        except Exception:
            pass
    else:
        print(f"Usage: {sys.argv[0]} {{preview|generate}}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
