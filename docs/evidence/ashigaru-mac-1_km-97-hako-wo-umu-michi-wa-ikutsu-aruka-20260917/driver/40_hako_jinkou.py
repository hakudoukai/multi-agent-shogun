#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""40_hako_jinkou.py ―― queue/inbox/*.yaml の人口調査(㋓)。読むだけ・書かぬ・読印を触らぬ。
名を 正名/異名(読点・空白・未知) に分ける。未知=白名簿(生 pane の @agent_id)に無い名。
項数は messages 鍵の要素数(字面で数へぬ)。未読は entry の read 鍵が False の数。
用法: python3 40_hako_jinkou.py <出力dir>"""
import os, sys, glob, subprocess, datetime, re
import yaml
out = sys.argv[1]
toki = datetime.datetime.now().astimezone().isoformat()
tm = subprocess.run(['tmux', 'list-panes', '-a', '-F', '#{@agent_id}'], capture_output=True, text=True)
panes = sorted({l for l in tm.stdout.splitlines() if l.strip()})
rows = []
for p in sorted(glob.glob('queue/inbox/*.yaml')):
    name = os.path.basename(p)[:-5]
    st = os.stat(p)
    mt = datetime.datetime.fromtimestamp(st.st_mtime).astimezone().isoformat(timespec='seconds')
    if re.search(r'[,\s]', name): kind = '異名:読点/空白'
    elif name in panes: kind = '正名(pane有)'
    else: kind = '異名:未知(pane無)'
    n = un = -1; err = ''
    try:
        with open(p, encoding='utf-8') as f: d = yaml.safe_load(f)
        ms = d.get('messages') if isinstance(d, dict) else None
        if ms is None: ms = []
        n = len(ms); un = sum(1 for m in ms if isinstance(m, dict) and m.get('read') is False)
    except Exception as e:
        err = type(e).__name__ + ':' + str(e)[:60].replace('\n', ' ')
    rows.append((kind, name, mt, st.st_size, n, un, err))
with open(os.path.join(out, '40_hako_jinkou.tsv'), 'w', encoding='utf-8') as f:
    f.write(f"# 刻={toki} tmux_rc={tm.returncode} 生pane数={len(panes)} 箱数={len(rows)} 走査根=queue/inbox 深さ=1 pattern=*.yaml\n")
    f.write("kind\tname\tmtime\tbytes\tentries(messages鍵)\tunread(read==False)\terr\n")
    for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
with open(os.path.join(out, '40_panes.txt'), 'w') as f: f.write('\n'.join(panes) + '\n')
print(f"刻={toki} tmux_rc={tm.returncode} panes={len(panes)} boxes={len(rows)}")
for r in rows: print('\t'.join(str(x) for x in r))
