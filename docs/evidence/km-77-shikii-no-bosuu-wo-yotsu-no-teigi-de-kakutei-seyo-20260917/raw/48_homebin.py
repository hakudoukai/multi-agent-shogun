# -*- coding: utf-8 -*-
"""48 ―― ~/bin(repo 外・持ち主= 環境部長・裁 seq324404 ゆゑ本弾の的ではない)の ${NAME:-數} を ★別表★ で数へる丈。讀むのみ・触らぬ。深さ 1・.sh .py。"""
import os, sys, re, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
H = os.path.expanduser('~/bin'); RE = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):-([0-9]+)\}'); rows = []; n = 0; nf = 0
for f in sorted(os.listdir(H)):
    q = os.path.join(H, f)
    if not os.path.isfile(q) or not f.endswith(('.sh', '.py')): continue
    nf += 1
    for i, ln in enumerate(open(q, encoding='utf-8', errors='replace'), 1):
        for m in RE.finditer(ln): n += 1; rows.append((f, i, m.group(1), m.group(2), ln.strip().startswith('#') and '註' or '-', ln.strip()[:70]))
K.kaku_tsv(D + '/raw/48_homebin.tsv', rows, ['file', 'line', 'name', 'default', 'note', 'text'])
neg = sum(1 for f in os.listdir(H) if 'ZZ_KM77_NEGATIVE_9x7q' in f)
K.kaku(D + '/raw/48_homebin.txt', f'# 48 ~/bin 別表(★的ではない・持ち主= 環境部長・触らぬ★) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 根 {H} 深さ 1 / 母數 .sh .py {nf} 本 / ${{NAME:-數}} の口 {n} / file {len(set(r[0] for r in rows))} / 器= python re(git grep は repo 外で使へぬ) / 陽性対照= 同じ re が repo の scripts/inbox_watcher.sh で {len(RE.findall(open("/Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh", encoding="utf-8").read()))} 口 / 陰性対照 {neg}')
print(open(D + '/raw/48_homebin.txt', encoding='utf-8').read()); print('\n'.join('\t'.join(map(str, r)) for r in rows))
