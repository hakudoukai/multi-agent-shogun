#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_ps_utsushi.py ―― 稼働 process の写し。己の系譜(自 pid とその先祖)を ★pid で★ 除く(字面では除けぬ)。
用法: python3 20_ps_utsushi.py <出力dir>"""
import os, subprocess, sys, re, datetime
out = sys.argv[1]
ps = subprocess.run(['ps', '-axo', 'pid=,ppid=,lstart=,command='], capture_output=True, text=True)
rows = []
for ln in ps.stdout.splitlines():
    m = re.match(r'\s*(\d+)\s+(\d+)\s+(.*)$', ln)
    if m: rows.append((int(m.group(1)), int(m.group(2)), m.group(3)))
ppid = {p: pp for p, pp, _ in rows}
anc = set(); p = os.getpid()
while p in ppid and p not in anc:
    anc.add(p); p = ppid[p]
pat = re.compile(r'inbox|watcher|orphan|idle_backlog|stop_hook|supervisor|ntfy|periodic_push|health_check|overload|standby', re.I)
hits = [(p, pp, c) for p, pp, c in rows if pat.search(c) and p not in anc]
with open(os.path.join(out, '20_ps_all.txt'), 'w') as f:
    f.write(ps.stdout)
with open(os.path.join(out, '20_ps_hits.txt'), 'w') as f:
    f.write(f"# 刻={datetime.datetime.now().astimezone().isoformat()} ps_rc={ps.returncode} 母數={len(rows)} 己の系譜(除)={sorted(anc)} hits={len(hits)}\n")
    for p, pp, c in hits: f.write(f"{p}\t{pp}\t{c}\n")
print(f"ps_rc={ps.returncode} rows={len(rows)} self_anc={sorted(anc)} hits={len(hits)}")
