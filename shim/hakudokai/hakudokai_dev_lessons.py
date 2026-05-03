#!/usr/bin/env python3
"""DD-142 SS7 dev_lessons auto-INSERT + improvement_proposal auto-dispatch.

Layer 1 of the self-improvement loop:
  1. Record errors to dev_lessons table (called by watchdog/agents on failure)
  2. Check recurrence count; if >= 3, auto-dispatch improvement_proposal

Usage:
  # Record a lesson
  python3 hakudokai_dev_lessons.py record \
    --error-pattern "fukuincho_watcher_crash" \
    --root-cause "SUPABASE_URL env missing after /clear" \
    --resolution "Added auto-source from ~/.openclaw/env"

  # Check recurrence and dispatch proposals if needed
  python3 hakudokai_dev_lessons.py check-recurrence

  # Both in one call
  python3 hakudokai_dev_lessons.py record-and-check \
    --error-pattern "..." --root-cause "..." --resolution "..."

Prerequisites: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY env vars
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")
RECURRENCE_THRESHOLD = 3


def get_env():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        env_file = os.path.expanduser("~/.openclaw/env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip().replace("\r", "")
                    if line.startswith("SUPABASE_URL="):
                        url = line.split("=", 1)[1]
                    elif line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                        key = line.split("=", 1)[1]
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
        sys.exit(1)
    return url, key


def api_request(url, key, path, method="GET", data=None):
    full_url = f"{url}/rest/v1/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(full_url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("apikey", key)
    req.add_header("Content-Type", "application/json")
    if method in ("POST", "PATCH"):
        req.add_header("Prefer", "return=representation")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode()) if resp.status == 200 or resp.status == 201 else []
    except Exception as e:
        print(f"API error ({method} {path}): {e}", file=sys.stderr)
        return None


def record_lesson(url, key, error_pattern, root_cause, resolution):
    """Insert a dev_lesson record."""
    data = {
        "error_pattern": error_pattern,
        "root_cause": root_cause,
        "resolution_attempted": resolution,
        "source": "agent",
        "clinic_id": CLINIC_ID,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    result = api_request(url, key, "dev_lessons", method="POST", data=data)
    if result is not None:
        print(f"dev_lesson recorded: {error_pattern}", file=sys.stderr)
        return True
    else:
        print(f"dev_lesson INSERT failed (table may not exist)", file=sys.stderr)
        return False


def check_recurrence_and_dispatch(url, key):
    """Check dev_lessons for patterns with recurrence >= threshold, dispatch proposals."""
    # Get all lessons grouped by error_pattern (last 30 days)
    path = f"dev_lessons?select=error_pattern,root_cause,resolution_attempted&clinic_id=eq.{CLINIC_ID}&order=created_at.desc&limit=200"
    lessons = api_request(url, key, path)
    if not lessons:
        print("No dev_lessons found or table missing", file=sys.stderr)
        return

    # Count occurrences per pattern
    pattern_counts = {}
    pattern_details = {}
    for lesson in lessons:
        p = lesson.get("error_pattern", "unknown")
        pattern_counts[p] = pattern_counts.get(p, 0) + 1
        if p not in pattern_details:
            pattern_details[p] = lesson

    # Check existing proposals to avoid duplicates
    existing_proposals = api_request(
        url, key,
        f"improvement_proposals?select=error_pattern&clinic_id=eq.{CLINIC_ID}&status=eq.pending&limit=100"
    )
    existing_patterns = set()
    if existing_proposals:
        existing_patterns = {p.get("error_pattern", "") for p in existing_proposals}

    dispatched = 0
    for pattern, count in pattern_counts.items():
        if count >= RECURRENCE_THRESHOLD and pattern not in existing_patterns:
            details = pattern_details[pattern]
            proposal = {
                "error_pattern": pattern,
                "recurrence_count": count,
                "root_cause_summary": details.get("root_cause", ""),
                "proposed_fix": f"Auto-generated: Pattern '{pattern}' occurred {count} times. Last resolution: {details.get('resolution_attempted', 'unknown')}. Requires structural fix.",
                "status": "pending",
                "clinic_id": CLINIC_ID,
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            result = api_request(url, key, "improvement_proposals", method="POST", data=proposal)
            if result is not None:
                print(f"Improvement proposal dispatched: {pattern} (recurrence={count})", file=sys.stderr)
                dispatched += 1

    print(f"Recurrence check done: {dispatched} new proposals dispatched", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="DD-142 dev_lessons manager")
    parser.add_argument("action", choices=["record", "check-recurrence", "record-and-check"])
    parser.add_argument("--error-pattern", default="")
    parser.add_argument("--root-cause", default="")
    parser.add_argument("--resolution", default="")
    args = parser.parse_args()

    url, key = get_env()

    if args.action in ("record", "record-and-check"):
        if not args.error_pattern:
            print("ERROR: --error-pattern required for record", file=sys.stderr)
            sys.exit(1)
        record_lesson(url, key, args.error_pattern, args.root_cause, args.resolution)

    if args.action in ("check-recurrence", "record-and-check"):
        check_recurrence_and_dispatch(url, key)


if __name__ == "__main__":
    main()
