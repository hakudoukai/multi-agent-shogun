#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-219: worktree census + ff-only decidability measurement (read-only)."""
import subprocess, json, sys, datetime

REPO = "/Users/momizimac/multi-agent-shogun"
import os
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")  # 専任2: 他席の index を掴まぬ
BASE_REF = sys.argv[1]  # 専任2: 固定 sha を argv で受ける

def run(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=ENV)
    return p.returncode, p.stdout, p.stderr

def parse_porcelain(text):
    records = []
    cur = {}
    for line in text.splitlines():
        if line.startswith("worktree "):
            if cur:
                records.append(cur)
            cur = {"path": line[len("worktree "):], "branch": None,
                   "head": None, "detached": False, "prunable": None, "locked": False}
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD "):]
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):]
        elif line == "detached":
            cur["detached"] = True
        elif line.startswith("prunable"):
            cur["prunable"] = line
        elif line.startswith("locked"):
            cur["locked"] = True
    if cur:
        records.append(cur)
    return records

def main():
    ts0 = datetime.datetime.now().astimezone().isoformat()
    rc, out, err = run(["git", "worktree", "list", "--porcelain"], cwd=REPO)
    ts1 = datetime.datetime.now().astimezone().isoformat()
    print(f"### 実射: git worktree list --porcelain (rc={rc}) 刻前={ts0} 刻後={ts1}", file=sys.stderr)
    records = parse_porcelain(out)
    print(f"母數(worktree 行の本数)={len(records)}", file=sys.stderr)

    base_sha = run(["git", "rev-parse", BASE_REF], cwd=REPO)[1].strip()
    print(f"{BASE_REF}={base_sha}", file=sys.stderr)

    for r in records:
        path = r["path"]
        # status -uall
        srrc, srout, srerr = run(["git", "status", "--porcelain", "-uall"], cwd=path)
        r["status_rc"] = srrc
        r["status_lines"] = len(srout.splitlines())
        r["status_err"] = srerr.strip()
        head = r["head"]
        # ahead/behind both directions vs origin/main
        rc1, out1, err1 = run(["git", "rev-list", "--count", f"{head}..{BASE_REF}"], cwd=path)
        rc2, out2, err2 = run(["git", "rev-list", "--count", f"{BASE_REF}..{head}"], cwd=path)
        r["head_ahead_of_origin"] = out2.strip()  # BASE..HEAD = commits HEAD has beyond base
        r["origin_ahead_of_head"] = out1.strip()  # HEAD..BASE = commits base has beyond HEAD
        r["revlist_rc"] = [rc1, rc2]
        r["revlist_err"] = (err1 + err2).strip()
        # is_ancestor decision procedure (never executes a merge)
        rc3, out3, err3 = run(["git", "merge-base", "--is-ancestor", head, BASE_REF], cwd=path)
        r["is_ancestor_rc"] = rc3
        r["is_ancestor_err"] = err3.strip()

    result = {
        "measured_at_start": ts0,
        "measured_at_end": ts1,
        "porcelain_rc": rc,
        "base_ref": BASE_REF,
        "base_sha": base_sha,
        "total": len(records),
        "records": records,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
