#!/usr/bin/env python3
"""km-217 ⒟: detector for '括られぬ値に colon+space' defect (同型の疵).
Read-only. Scans raw text lines (not via yaml parser) for a plain (unquoted)
scalar value on a `key: value` line that itself contains a literal ': '
(colon followed by space) outside of quotes/flow brackets — the exact shape
that breaks yaml.safe_load with a Scanner/Parser error, because YAML reads
the embedded ': ' as the start of a nested mapping.
"""
import re
import sys

KEYVAL_RE = re.compile(r'^(?P<indent>[ \t]*)(?:- )?(?P<key>[^\s:#][^:]*):[ \t]+(?P<val>\S.*)$')

def is_quoted(val: str) -> bool:
    v = val.strip()
    if not v:
        return False
    if v[0] in ("'", '"'):
        return True
    if v[0] in ("[", "{", "|", ">", "&", "*"):
        return True
    if v in ("null", "~", "true", "false") or re.match(r'^-?\d', v):
        return True
    return False

def scan_file(path):
    hits = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            raw = line.rstrip("\n")
            if raw.lstrip().startswith("#"):
                continue
            m = KEYVAL_RE.match(raw)
            if not m:
                continue
            val = m.group("val")
            if is_quoted(val):
                continue
            if ": " in val:
                hits.append((i, len(raw), m.group("key").strip(), val))
    return hits

def main():
    for path in sys.argv[1:]:
        hits = scan_file(path)
        for (ln, ln_len, key, val) in hits:
            print(f"{path}\tSUSPECT\tline={ln}\tlen={ln_len}\tkey={key}\tval={val}")
        if not hits:
            print(f"{path}\tCLEAN")

if __name__ == "__main__":
    main()
