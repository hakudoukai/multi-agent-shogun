#!/usr/bin/env python3
"""km-217: 全帳(queue/tasks, queue/inbox) safe_load census. Read-only. Paper evidence only."""
import sys
import hashlib
import yaml

def sha256_bytes(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def line_count(p):
    with open(p, "rb") as f:
        data = f.read()
    if not data:
        return 0
    n = data.count(b"\n")
    if not data.endswith(b"\n"):
        n += 1
    return n

def main():
    listfile = sys.argv[1]
    with open(listfile) as f:
        paths = [l.rstrip("\n") for l in f if l.strip()]
    results = []
    for p in paths:
        try:
            with open(p, "rb") as f:
                raw = f.read()
            byte_n = len(raw)
            line_n = line_count(p)
            sha = sha256_bytes(p)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
                results.append((p, "OK", byte_n, line_n, sha, "", "", ""))
            except yaml.YAMLError as e:
                etype = type(e).__name__
                mark = getattr(e, "problem_mark", None)
                if mark is not None:
                    ln = mark.line + 1
                    col = mark.column + 1
                else:
                    ln = ""
                    col = ""
                problem = getattr(e, "problem", "") or ""
                results.append((p, "DEAD", byte_n, line_n, sha, etype, str(ln), str(col) + "|" + problem.replace("\n", " ")))
        except Exception as e:
            results.append((p, "ERR_OTHER", "", "", "", type(e).__name__, "", str(e)))
    for r in results:
        print("\t".join(str(x) for x in r))

if __name__ == "__main__":
    main()
