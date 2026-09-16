# -*- coding: utf-8 -*-
"""問三の第二の器 81(第56弾・80 の厳しさを疑ふ為)。「N度目」(二度目〜十度目・再犯)の語は ★知つて居て直さなかつた★ の別の顔である ―― 同じ疵を二度踏んだと自書した行は、一度目で知り二度目までに直さなかつた事の證。
数へ方は 80 と同じ(母數 = 渡した根の下の通常 file・行ごと・己の系譜 8[01]_ を除く)。型 = [二三四五六七八九十]度目 。陽性対照 = 第55弾 raw/00_start.txt の「三度目」。陰性対照 = kaki.py。argv: <根> ...。讀むのみ。"""
import os, re, sys
from collections import Counter
PAT = re.compile(r'[二三四五六七八九十]度目')
roots = sys.argv[1:]; N = 0; L = 0; hits = []; skipped_self = 0
for r in roots:
    walk = [(os.path.dirname(r), None, [os.path.basename(r)])] if os.path.isfile(r) else os.walk(r)
    for d, ds, fs in walk:
        for f in sorted(fs):
            p = os.path.join(d, f)
            if os.path.islink(p) or not os.path.isfile(p): continue
            if re.match(r'8[01]_', os.path.basename(p)): skipped_self += 1; continue
            N += 1
            for i, ln in enumerate(open(p, encoding='utf-8', errors='replace'), 1):
                L += 1
                for m in PAT.finditer(ln):
                    s = max(0, m.start() - 60); hits.append((p, i, m.group(0), ln[s:m.end() + 60].strip().replace('\t', ' ')))
pos = [h for h in hits if h[0].endswith('00_start.txt') and 'km-55' in h[0] and h[2] == '三度目']
neg = [h for h in hits if os.path.basename(h[0]) == 'kaki.py']
print(f'# 81 「N度目」で拾ふ / 母數 = file {N} 本・行 {L} / 己の系譜を除いた {skipped_self} 本 / ★候補 {len(hits)}★ / 陽性対照(r55 00_start の 三度目)= {"当たつた" if pos else "★当たらぬ★"} {len(pos)} / 陰性対照(kaki.py)= {len(neg)}')
print('## 語ごと: ' + ' / '.join(f'{k} {v}' for k, v in Counter(h[2] for h in hits).most_common()))
print('## 候補の列(file:行 | 語 | 前後):')
for p, i, k, ctx in hits: print(f'  {os.path.relpath(p, "queue/reports")[:70]}:{i} | {k} | {ctx}')
