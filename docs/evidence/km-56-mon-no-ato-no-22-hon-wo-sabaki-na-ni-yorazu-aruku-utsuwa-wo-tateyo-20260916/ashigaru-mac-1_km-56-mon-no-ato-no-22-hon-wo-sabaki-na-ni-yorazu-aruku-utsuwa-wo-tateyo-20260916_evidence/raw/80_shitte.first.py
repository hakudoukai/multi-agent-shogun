# -*- coding: utf-8 -*-
"""問三の器 80(第56弾)。「知つて居て直さなかつた」の候補を ★語で★ 拾ふ(数へ方を先に紙に書き、然る後に走らせる)。
数へ方: ⑴ 母數 = 渡した根の下の lstat 通常 file 悉く(utf-8・errors=replace で讀む)⑵ 行ごとに下の型に当てる ⑶ 当たつた行を「file:行 / 型 / 前後 160 字」で刷る ⑷ 一本の file の同じ行は一度 ⑸ 己の系譜(此の器の名 80_ を含む path)は除く・除いた数を刷る。
型(正規表現): 直さ(ず|なかつた|ぬ)|直して居らぬ|未だ直|知りながら|知つて居|変へるべき|直すべき|改めるべき|残る疵|其の儘に ―― ★語で拾ふ器は緩い ∴ 出目は候補であつて数ではない。数は紙で一本毎に裁いた後に書く。★
陽性対照 = 第55弾 raw/63b_sent.txt の「25_eta で日付落ちを知りながら 30/64 を直さず」の行(之が当たらねば器ではない)。陰性対照 = 語を含まぬ file(kaki.py)が 0 で出る事。
argv: <根> ... 。讀むのみ。"""
import os, re, sys
PAT = re.compile(r'直さ(ず|なかつた|ぬ)|直して居らぬ|未だ直|知りながら|知つて居|変へるべき|直すべき|改めるべき|残る疵|其の儘に')
roots = sys.argv[1:]; N = 0; L = 0; hits = []; skipped_self = 0; per = []
for r in roots:
    n0 = N
    for d, ds, fs in os.walk(r):
        for f in sorted(fs):
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p): continue
            if '80_' in os.path.basename(p): skipped_self += 1; continue
            N += 1
            for i, ln in enumerate(open(p, encoding='utf-8', errors='replace'), 1):
                L += 1; m = PAT.search(ln)
                if m:
                    s = max(0, m.start() - 70); hits.append((p, i, m.group(0), ln[s:m.end() + 90].strip().replace('\t', ' ')))
    per.append((r, N - n0))
pos = [h for h in hits if '63b_sent.txt' in h[0] and '知りながら' in h[2]]
neg = [h for h in hits if os.path.basename(h[0]) == 'kaki.py']
print(f'# 80 知つて居て直さなかつた の候補 / 母數 = file {N} 本・行 {L} / 己の系譜を除いた {skipped_self} 本 / ★候補(当たつた行){len(hits)}★ / 型の種 {len(set(h[2] for h in hits))} / 陽性対照(63b の 知りながら)= {"当たつた" if pos else "★当たらぬ ―― 器ではない★"} {len(pos)} / 陰性対照(kaki.py)= {len(neg)} {"(0 = 正)" if not neg else "★鳴つた★"}')
for r, k in per: print(f'  根 {r} → {k} 本')
from collections import Counter
print('## 型ごと: ' + ' / '.join(f'{k} {v}' for k, v in Counter(h[2] for h in hits).most_common()))
print('## file ごと: ' + ' / '.join(f'{os.path.relpath(k, "queue/reports")[:60]} {v}' for k, v in Counter(h[0] for h in hits).most_common()))
print('## 候補の列(file:行 | 型 | 前後):')
for p, i, k, ctx in hits: print(f'  {os.path.relpath(p, "queue/reports")}:{i} | {k} | {ctx}')
