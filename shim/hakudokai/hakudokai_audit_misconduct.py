#!/usr/bin/env python3
"""Task D-3: detect_audit_misconduct trigger + continuous monitoring.

Detects resistance patterns in agent behavior:
  1. Choice offering (agent offers options instead of executing)
  2. Hedging/weakening (adding unnecessary caveats)
  3. Task refusal (claiming inability without attempting)
  4. Scope creep (doing less than assigned)
  5. Unauthorized delegation (passing work back to user)

Usage:
  # Scan a report YAML for misconduct patterns
  python3 hakudokai_audit_misconduct.py scan --file queue/reports/ashigaru1_report.yaml

  # Scan all recent reports
  python3 hakudokai_audit_misconduct.py scan-all

  # Record detection to dev_lessons for improvement loop
  python3 hakudokai_audit_misconduct.py scan-and-record --file <path>

Integrates with DD-142 SS7 self-improvement loop via dev_lessons auto-INSERT.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Resistance patterns to detect
RESISTANCE_PATTERNS = [
    {
        "id": "RP-001",
        "name": "choice_offering",
        "description": "Agent offers choices instead of executing",
        "patterns": [
            r"(?:which|how would you like|do you want|shall I|should I|would you prefer)",
            r"(?:option\s*[A-C]|approach\s*[12]|alternative\s*[12])",
            r"(?:choose|select|pick)\s+(?:one|from|between)",
        ],
        "severity": "high",
    },
    {
        "id": "RP-002",
        "name": "hedging",
        "description": "Unnecessary caveats weakening output",
        "patterns": [
            r"(?:I'm not sure|I cannot guarantee|this might not|I'm unable to verify)",
            r"(?:please note that|it's worth mentioning|caveat|disclaimer)",
        ],
        "severity": "medium",
    },
    {
        "id": "RP-003",
        "name": "task_refusal",
        "description": "Claiming inability without attempting",
        "patterns": [
            r"(?:I cannot|I'm unable|I don't have access|beyond my capabilities)",
            r"(?:not possible|cannot be done|impossible to)",
        ],
        "severity": "high",
    },
    {
        "id": "RP-004",
        "name": "scope_reduction",
        "description": "Delivering less than assigned scope",
        "patterns": [
            r"(?:partial|incomplete|only part|simplified version|basic version)",
            r"(?:for now|as a start|initial version|placeholder)",
        ],
        "severity": "medium",
    },
    {
        "id": "RP-005",
        "name": "unauthorized_delegation",
        "description": "Passing work back to user/lord",
        "patterns": [
            r"(?:please review|you might want to|I recommend you|you should)",
            r"(?:up to you|your decision|your call)",
        ],
        "severity": "high",
    },
]


def scan_text(text):
    """Scan text for resistance patterns. Returns list of detections."""
    detections = []
    for rp in RESISTANCE_PATTERNS:
        for pattern in rp["patterns"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detections.append({
                    "pattern_id": rp["id"],
                    "pattern_name": rp["name"],
                    "severity": rp["severity"],
                    "matches": matches[:5],
                    "description": rp["description"],
                })
                break  # One detection per pattern type is enough
    return detections


def scan_file(filepath):
    """Scan a YAML/text file for resistance patterns."""
    full_path = filepath if os.path.isabs(filepath) else os.path.join(PROJECT_ROOT, filepath)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}", file=sys.stderr)
        return []

    with open(full_path, encoding="utf-8") as f:
        content = f.read()

    detections = scan_text(content)
    if detections:
        print(f"DETECTED {len(detections)} resistance pattern(s) in {filepath}:", file=sys.stderr)
        for d in detections:
            print(f"  [{d['severity'].upper()}] {d['pattern_id']} {d['pattern_name']}: {d['matches'][:2]}", file=sys.stderr)
    else:
        print(f"CLEAN: {filepath}", file=sys.stderr)

    return detections


def scan_all_reports():
    """Scan all report YAMLs in queue/reports/."""
    reports_dir = os.path.join(PROJECT_ROOT, "queue", "reports")
    if not os.path.exists(reports_dir):
        print(f"Reports directory not found: {reports_dir}", file=sys.stderr)
        return {}

    all_detections = {}
    for fname in os.listdir(reports_dir):
        if fname.endswith(".yaml") or fname.endswith(".yml"):
            filepath = os.path.join(reports_dir, fname)
            detections = scan_file(filepath)
            if detections:
                all_detections[fname] = detections

    total = sum(len(v) for v in all_detections.values())
    print(f"\nScan complete: {total} detection(s) in {len(all_detections)} file(s)", file=sys.stderr)
    return all_detections


def record_to_dev_lessons(detections, source_file):
    """Record detections to dev_lessons via hakudokai_dev_lessons.py."""
    dev_lessons_script = os.path.join(SCRIPT_DIR, "hakudokai_dev_lessons.py")
    if not os.path.exists(dev_lessons_script):
        print("WARN: hakudokai_dev_lessons.py not found, skipping recording", file=sys.stderr)
        return

    for d in detections:
        try:
            subprocess.run(
                [
                    "python3", dev_lessons_script, "record-and-check",
                    "--error-pattern", f"resistance_{d['pattern_name']}",
                    "--root-cause", f"Agent exhibited {d['description']} in {source_file}",
                    "--resolution", f"Detected by audit. Pattern: {d['pattern_id']}. Matches: {d['matches'][:2]}",
                ],
                capture_output=True,
                timeout=15,
            )
        except Exception as e:
            print(f"Failed to record dev_lesson: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="D-3 Audit misconduct detector")
    parser.add_argument("action", choices=["scan", "scan-all", "scan-and-record"])
    parser.add_argument("--file", default="")
    args = parser.parse_args()

    if args.action == "scan":
        if not args.file:
            print("ERROR: --file required for scan", file=sys.stderr)
            sys.exit(1)
        scan_file(args.file)

    elif args.action == "scan-all":
        scan_all_reports()

    elif args.action == "scan-and-record":
        if not args.file:
            print("ERROR: --file required for scan-and-record", file=sys.stderr)
            sys.exit(1)
        detections = scan_file(args.file)
        if detections:
            record_to_dev_lessons(detections, args.file)


if __name__ == "__main__":
    main()
