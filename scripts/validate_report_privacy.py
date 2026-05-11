#!/usr/bin/env python3
"""
validate_report_privacy.py — PII/secret scanner for report YAML files.
Runs before outbound cross-PC sync (Gate G3 in cross_pc_trust_gate.md §PII/Secret Scan).

Exit codes:
  0: SCAN_PASS  (clean, or field-name warnings only)
  1: SCAN_FAIL  (PII values or secrets detected — line numbers printed)
  2: SCAN_ERROR (file not found, unreadable, or I/O error)
"""

import os
import re
import sys

ALLOWLIST_PATH = ".validate_privacy_allowlist.yaml"

# Exempt fields per cross_pc_trust_gate.md §PII/Secret Scan → "スキャン対象外"
EXEMPT_FIELDS = frozenset({
    "verdict", "evidence_state", "completion_gate",
    "task_id", "audit_id", "timestamp", "log_path",
    "commit_hash", "transfer_id", "assigned_at", "audited_at",
    "report_file", "source_hash", "target_hash",
})

# Secret patterns — searched in the value portion of any non-exempt line.
# Negative lookahead (?![A-Z_]{4,}) skips ALL_CAPS placeholder values like
# PLACEHOLDER_UNSET, UNSET, YOUR_KEY_HERE that appear in audit finding strings.
SECRET_PATTERNS = [
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"),   "Anthropic API key (sk-ant-)"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{48,}"),        "OpenAI-style API key (sk-)"),
    (re.compile(r"\bxai-[A-Za-z0-9_\-]{20,}"),       "xAI API key (xai-)"),
    (re.compile(r"\bghp_[A-Za-z0-9]{36,}"),          "GitHub PAT (ghp_)"),
    (re.compile(r"\bglpat-[A-Za-z0-9_\-]{20,}"),     "GitLab PAT (glpat-)"),
    (re.compile(r"(?i)\bpassword\s*[:=]\s*(?![A-Z_]{4,})[^\s]{6,}"), "password with value"),
    (re.compile(r"(?i)\bsecret\s*[:=]\s*(?![A-Z_]{4,})[a-z][A-Za-z0-9_\-\.]{5,}"), "secret with value"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{20,}"), "Bearer token"),
]

# YAML key fields whose name alone signals a credential — checked by field_name match
SECRET_KEY_NAMES = frozenset({
    "api_key", "apikey", "api_token", "access_token",
    "auth_token", "secret_key", "private_key",
})

# Universal PII patterns — searched in value text regardless of field name
EMAIL_RE   = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,6}\b")
SSN_RE     = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")            # US SSN
PHONE_RE   = re.compile(r"\b0\d{1,4}[-\s]\d{1,4}[-\s]\d{4}\b")  # Japanese phone

# Field-specific PII value patterns (field name → value regex)
# Only applied when the YAML *key* matches the field name.
FIELD_PII = {
    "patient_id":   re.compile(r"\b\d{2}_\d{4,6}\b|\b\d{5,8}\b"),
    "birth_date":   re.compile(r"\b(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b"),
    "phone_number": PHONE_RE,
    "phone":        PHONE_RE,
    "email":        EMAIL_RE,
}

# YAML simple key-value line: "  key: value rest..."
YAML_KV_RE = re.compile(r"^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)")

NULL_VALUES = frozenset({"", "null", "none", "~", '""', "''"})


# ---------------------------------------------------------------------------
# Allowlist loading
# ---------------------------------------------------------------------------

def load_allowlist(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        import yaml  # optional import — allowlist is optional feature
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return [re.compile(p) for p in data.get("patterns", [])]
    except Exception:
        return []


def is_allowlisted(text: str, allowlist: list) -> bool:
    return any(p.search(text) for p in allowlist)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_file(filepath: str) -> dict:
    """
    Returns:
      status   : 'pass' | 'fail' | 'error'
      failures : [(lineno, description, matched_text)]
      warnings : [(lineno, description)]
      error_msg: str | None
    """
    result: dict = {"status": "pass", "failures": [], "warnings": [], "error_msg": None}

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as exc:
        result["status"] = "error"
        result["error_msg"] = str(exc)
        return result

    allowlist = load_allowlist(ALLOWLIST_PATH)

    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        stripped = line.strip()

        # Skip blank lines and full-line comments
        if not stripped or stripped.startswith("#"):
            continue

        # Parse YAML key-value if present
        kv = YAML_KV_RE.match(line)
        field_name = kv.group(2).lower() if kv else None
        value_part = kv.group(3).strip() if kv else None

        # Skip exempt metadata fields
        if field_name in EXEMPT_FIELDS:
            continue

        # text to scan: value portion for keyed lines, stripped line for others
        scan_text = value_part if kv else stripped
        if not scan_text:
            continue

        # ----------------------------------------------------------------
        # Secret patterns — search in scan_text
        # ----------------------------------------------------------------
        for pattern, desc in SECRET_PATTERNS:
            m = pattern.search(scan_text)
            if m and not is_allowlisted(m.group(0), allowlist):
                result["failures"].append((lineno, f"SECRET: {desc}", m.group(0)[:80]))

        # Secret-named key with long non-trivial value
        if field_name in SECRET_KEY_NAMES and value_part:
            val_clean = value_part.strip("'\" ")
            if len(val_clean) >= 16 and re.match(r"^[A-Za-z0-9_\-\.]+$", val_clean):
                if not is_allowlisted(val_clean, allowlist):
                    result["failures"].append((
                        lineno,
                        f"SECRET: credential-named field '{field_name}' with long value",
                        val_clean[:60],
                    ))

        # ----------------------------------------------------------------
        # Field-specific PII value check (key name → value pattern)
        # ----------------------------------------------------------------
        if field_name in FIELD_PII:
            val_raw = value_part or ""
            val_clean = val_raw.strip("'\" ")
            if val_clean.lower() in NULL_VALUES:
                result["warnings"].append((
                    lineno,
                    f"PII field name found with null/empty value: {field_name}",
                ))
            elif FIELD_PII[field_name].search(val_clean):
                if not is_allowlisted(val_clean, allowlist):
                    result["failures"].append((
                        lineno,
                        f"PII: real value detected in field '{field_name}'",
                        val_clean[:60],
                    ))
            else:
                result["warnings"].append((
                    lineno,
                    f"PII field name found but value not a PII pattern: "
                    f"{field_name}={val_clean[:40]}",
                ))

        # ----------------------------------------------------------------
        # Universal PII: email (anywhere in scan_text, avoid double-report)
        # ----------------------------------------------------------------
        if field_name != "email":
            em = EMAIL_RE.search(scan_text)
            if em and not is_allowlisted(em.group(0), allowlist):
                result["failures"].append((lineno, "PII: email address", em.group(0)))

        # ----------------------------------------------------------------
        # Universal PII: US SSN
        # ----------------------------------------------------------------
        ssn = SSN_RE.search(scan_text)
        if ssn and not is_allowlisted(ssn.group(0), allowlist):
            result["failures"].append((lineno, "PII: SSN-format number", ssn.group(0)))

        # ----------------------------------------------------------------
        # Universal PII: phone number (avoid double-report for phone fields)
        # ----------------------------------------------------------------
        if field_name not in ("phone_number", "phone"):
            ph = PHONE_RE.search(scan_text)
            if ph and not is_allowlisted(ph.group(0), allowlist):
                result["failures"].append((lineno, "PII: phone number", ph.group(0)))

    if result["failures"]:
        result["status"] = "fail"

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: validate_report_privacy.py <report_yaml_file>", file=sys.stderr)
        print("       validate_report_privacy.py --allowlist-sample", file=sys.stderr)
        sys.exit(2)

    if sys.argv[1] == "--allowlist-sample":
        print(
            "# .validate_privacy_allowlist.yaml\n"
            "# Add regex patterns to suppress SCAN_FAIL for known-safe values.\n"
            "patterns:\n"
            "  - 'example\\\\.com'        # test email domain\n"
            "  - '\\\\b000-00-0000\\\\b'  # dummy SSN\n"
        )
        sys.exit(0)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"SCAN_ERROR: file not found: {filepath}")
        sys.exit(2)

    result = scan_file(filepath)

    for lineno, msg in result["warnings"]:
        print(f"WARNING line {lineno}: {msg}")

    if result["status"] == "error":
        print(f"SCAN_ERROR: {result['error_msg']}")
        sys.exit(2)

    if result["status"] == "fail":
        for lineno, desc, matched in result["failures"]:
            print(f"SCAN_FAIL line {lineno}: {desc} → matched: {matched!r}")
        sys.exit(1)

    print(f"SCAN_PASS: {filepath} — no PII or secrets detected")
    if result["warnings"]:
        print(f"  ({len(result['warnings'])} warning(s): PII field names present but no PII values)")
    sys.exit(0)


if __name__ == "__main__":
    main()
