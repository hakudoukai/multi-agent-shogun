#!/usr/bin/env python3
"""DD-142 Layer 3: Resistance pattern eradication guard.

Functions:
  1. Validate agent instructions contain mandatory FKI directives
  2. Auto-inject missing directives into instruction files
  3. Sync instructions across generated files (build_instructions wrapper)

FKI Directives enforced:
  - FKI-NO-CHOICE-OFFER-01: Never offer choices to the user; execute autonomously
  - FKI-MAX-STRENGTH-01: Use maximum capability, no hedging or weakening

Usage:
  python3 hakudokai_resistance_guard.py validate   # Check all instruction files
  python3 hakudokai_resistance_guard.py inject      # Auto-inject missing directives
  python3 hakudokai_resistance_guard.py sync        # Run build_instructions.sh after injection
"""
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Mandatory FKI directives that must exist in instruction files
FKI_DIRECTIVES = {
    "FKI-NO-CHOICE-OFFER-01": {
        "description": "Autonomous execution without offering choices",
        "marker": "FKI-NO-CHOICE-OFFER-01",
        "injection_text": """
## FKI-NO-CHOICE-OFFER-01: Autonomous Execution

- Do NOT offer choices or ask "which approach?" — decide and execute.
- Do NOT list options for the user to pick from.
- If multiple valid approaches exist, pick the best one and proceed.
- Report what you DID, not what you COULD do.
- Exception: genuinely ambiguous requirements where wrong choice = wasted work.
""",
    },
    "FKI-MAX-STRENGTH-01": {
        "description": "Maximum capability, no hedging",
        "marker": "FKI-MAX-STRENGTH-01",
        "injection_text": """
## FKI-MAX-STRENGTH-01: Maximum Capability

- Execute at full capability. No hedging, no weakening, no unnecessary caveats.
- Do NOT say "I can't" when you can. Do NOT add disclaimers that reduce usefulness.
- Complete the entire task, not a partial version.
- If blocked, find an alternative path. Only report "blocked" after 3 attempts.
- Quality bar: production-ready output, not drafts or outlines.
""",
    },
}

# Instruction files to check/inject
INSTRUCTION_FILES = [
    "instructions/shogun.md",
    "instructions/karo.md",
    "instructions/ashigaru.md",
    "instructions/gunshi.md",
]


def check_file(filepath):
    """Check if a file contains all mandatory FKI directives."""
    full_path = os.path.join(PROJECT_ROOT, filepath)
    if not os.path.exists(full_path):
        return {"exists": False, "missing": list(FKI_DIRECTIVES.keys())}

    with open(full_path, encoding="utf-8") as f:
        content = f.read()

    missing = []
    for directive_id, directive in FKI_DIRECTIVES.items():
        if directive["marker"] not in content:
            missing.append(directive_id)

    return {"exists": True, "missing": missing}


def validate_all():
    """Validate all instruction files. Returns True if all pass."""
    all_pass = True
    for filepath in INSTRUCTION_FILES:
        result = check_file(filepath)
        if not result["exists"]:
            print(f"MISSING FILE: {filepath}", file=sys.stderr)
            all_pass = False
        elif result["missing"]:
            print(f"MISSING DIRECTIVES in {filepath}: {', '.join(result['missing'])}", file=sys.stderr)
            all_pass = False
        else:
            print(f"OK: {filepath}", file=sys.stderr)
    return all_pass


def inject_directives():
    """Inject missing FKI directives into instruction files."""
    injected_count = 0
    for filepath in INSTRUCTION_FILES:
        result = check_file(filepath)
        if not result["exists"]:
            print(f"SKIP (file missing): {filepath}", file=sys.stderr)
            continue

        if not result["missing"]:
            continue

        full_path = os.path.join(PROJECT_ROOT, filepath)
        with open(full_path, encoding="utf-8") as f:
            content = f.read()

        for directive_id in result["missing"]:
            directive = FKI_DIRECTIVES[directive_id]
            content += "\n" + directive["injection_text"]
            print(f"INJECTED {directive_id} into {filepath}", file=sys.stderr)
            injected_count += 1

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Injection complete: {injected_count} directives added", file=sys.stderr)
    return injected_count


def sync_instructions():
    """Run build_instructions.sh to sync generated files after injection."""
    build_script = os.path.join(PROJECT_ROOT, "scripts", "build_instructions.sh")
    if not os.path.exists(build_script):
        print("WARN: build_instructions.sh not found, skipping sync", file=sys.stderr)
        return False

    try:
        result = subprocess.run(
            ["bash", build_script],
            cwd=PROJECT_ROOT,
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("Instruction sync complete", file=sys.stderr)
            return True
        else:
            print(f"Instruction sync failed: {result.stderr.decode()[:300]}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Instruction sync error: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: hakudokai_resistance_guard.py [validate|inject|sync]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    if action == "validate":
        ok = validate_all()
        sys.exit(0 if ok else 1)
    elif action == "inject":
        inject_directives()
    elif action == "sync":
        inject_directives()
        sync_instructions()
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
