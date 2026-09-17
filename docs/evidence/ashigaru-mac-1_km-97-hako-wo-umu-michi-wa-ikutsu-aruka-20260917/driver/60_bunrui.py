#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""60_bunrui.py ―― 歩きの hit を 器/控/紙/試 に分ける(規則は此処に刷る・手で数へぬ)。
 控 = .bak* / .orig / .new.* / .pre* / -bak- / backups/ / archive/ / __pycache__ / file-history / .claude/worktrees / .hermes / state/ / tasks json
 紙 = docs/ / *.md / instructions/ / skills/ / reports/ / memory/ / .gitignore / .github / specs / fixtures / history.jsonl / shared-orders / *.yaml(fixture) / *.log / *.db / *.jsonl
 試 = tests/ / scripts/tests/
 器 = 其れ以外(.sh .py .json .bats 等の実行物・設定)
用法: python3 60_bunrui.py <出力dir> <根名> <hitfile> ..."""
import re, sys, os, collections
out, root = sys.argv[1], sys.argv[2]
HIKAE = re.compile(r'(\.bak[^/]*$|\.orig$|\.new\.[^/]*$|\.pre[0-9][^/]*$|-bak-|/backups/|/archive/|__pycache__|/file-history/|/\.claude/worktrees/|/\.hermes/|/state/|/\.claude/tasks/)')
KAMI = re.compile(r'(^\./docs/|\.md$|/instructions/|/skills/|/reports/|^\./memory/|\.gitignore$|/\.github/|/specs/|/fixtures/|history\.jsonl$|/shared-orders/|\.log$|\.db$|\.jsonl$|/education/|/current-role-backup)')
SHI = re.compile(r'(^\./tests/|^\./scripts/tests/)')
c = collections.Counter(); members = collections.defaultdict(list)
for hf in sys.argv[3:]:
    for ln in open(hf, encoding='utf-8'):
        p = ln.rstrip('\n')
        if not p: continue
        if HIKAE.search(p): k = '控'
        elif SHI.search(p): k = '試'
        elif KAMI.search(p): k = '紙'
        else: k = '器'
        c[k] += 1; members[k].append(p)
with open(os.path.join(out, f'60_bunrui_{root}.txt'), 'w', encoding='utf-8') as f:
    f.write(f"# 根={root} 入力={sys.argv[3:]} 合計={sum(c.values())} 器={c['器']} 控={c['控']} 紙={c['紙']} 試={c['試']}\n")
    for k in ('器', '試', '控', '紙'):
        f.write(f"## {k} ({c[k]})\n")
        for p in members[k]: f.write(p.replace(os.path.expanduser('~'), '~') + '\n')
print(f"{root}: 合計={sum(c.values())} 器={c['器']} 試={c['試']} 控={c['控']} 紙={c['紙']}")
