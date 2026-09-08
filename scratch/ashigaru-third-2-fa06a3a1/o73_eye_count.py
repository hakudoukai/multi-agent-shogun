#!/usr/bin/env python3
"""order73 の規: v3 の目と CI の目で 追跡簿の file が何本入るかを数へる (讀取のみ)。
1 = path 1 本 (git の追跡簿 `git ls-files` の 1 行)。DB へは触れぬ。"""
import subprocess, fnmatch, sys

REPO = "/mnt/c/DentalBI"

V3_INCLUDE = ["frontend/src/**/*.tsx","frontend/src/**/*.ts","backend/**/*.py","tests/**/*.py",
 "tools/**/*.py","scripts/**/*.py","scripts/**/*.ps1","scripts/**/*.sh","scripts/git-hooks/*",
 "infra/**/*.tf","infra/**/*.ps1","infra/**/*.md","supabase/migrations/*.sql",
 "supabase/functions/**/*.ts","supabase/seed/*.sql","supabase/policies/*.sql",
 "docs/audits/**/*.md","docs/audits/**/*.txt","docs/audits/**/*.patch",
 "docs/codex_audits/**/*.md","docs/codex_audits/**/*.txt","docs/gemini_audits/**/*.md",
 "docs/gemini_audits/**/*.txt","CLAUDE.md",".claude/rules/*.md",".claude/agents/*.md",
 ".claude/commands/*.md",".claude/skills/**/*.md","docs/audits/**/*.log",
 ".cache/audit_redo/**/*.md",".cache/audit_redo/**/*.txt"]
V3_EXCLUDE = ["**/__pycache__/**","**/node_modules/**","**/dist/**","**/.git/**",
 "frontend/src/vite-env.d.ts"]
CI_ONLY_EXCLUDE = ["**/*.test.*","**/*.spec.*","**/test_*"]
V3_EXCLUDE_DIRS = {"node_modules","__pycache__","dist",".git",".venv",".venv-linux","venv",".codex_audit"}

def tracked():
    r = subprocess.run(["git","-C",REPO,"ls-files"], capture_output=True, text=True, timeout=300)
    return [x for x in r.stdout.split("\n") if x]

def hit(p, pats):
    return any(fnmatch.fnmatch(p, q) for q in pats)

def main():
    t = tracked()
    inc = [p for p in t if hit(p, V3_INCLUDE)]
    dirok = [p for p in inc if not any(part in V3_EXCLUDE_DIRS for part in p.split("/"))]
    v3 = [p for p in dirok if not hit(p, V3_EXCLUDE)]
    ci_drop = [p for p in v3 if hit(p, CI_ONLY_EXCLUDE)]
    print("tracked_paths=%d" % len(t))
    print("v3_include_hit=%d" % len(inc))
    print("v3_after_exclude=%d" % len(v3))
    print("dropped_by_CI_only_excludes=%d" % len(ci_drop))
    head = {}
    for p in ci_drop:
        k = p.split("/")[0]
        head[k] = head.get(k, 0) + 1
    for k in sorted(head, key=lambda x: -head[x]):
        print("  %s=%d" % (k, head[k]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
