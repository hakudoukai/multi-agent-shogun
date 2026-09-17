# -*- coding: utf-8 -*-
"""㋔ ★着地の順★ を機械で組む器。
形: 各枝の ⑵基準枝B で束ね、★B が先に着いて居れば PR は ⑵ だけで済む★事を数で示す。
   B が割当13本の中に在るか外に在るかも書く(外なら ★他 lot への依存★)。
出: raw/60_jun.tsv
"""
import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def rows(p):
    return [l.split('\t') for l in open(p, encoding='utf-8').read().split(chr(10))[1:] if l.strip()]
sashi = rows('raw/20_sashi.tsv')
shiwake = {r[0]: r[6] for r in rows('raw/40_shiwake.tsv')}
mine = set(r[0] for r in sashi)

grp = {}
for r in sashi:
    grp.setdefault(r[6], []).append(r)

with open('raw/60_jun.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(['段', '基準枝B', 'Bは割当13本の内か', '此のBに乗る枝数',
                       '枝名', '甲乙丙', 'B着地後のPR規模=⑵file数', 'B未着地時のPR規模=⑴file数']) + chr(10))
    for i, (B, rs) in enumerate(sorted(grp.items(), key=lambda kv: (-len(kv[1]), kv[0])), 1):
        for r in rs:
            f.write('\t'.join(['%d' % i, B, '内' if B in mine else '★外(他 lot 依存)★',
                               '%d' % len(rs), r[0], shiwake[r[0]], r[4], r[2]]) + chr(10))
    tot2 = sum(int(r[4]) for r in sashi if r[4] != '測れぬ')
    tot1 = sum(int(r[2]) for r in sashi)
print('基準枝B の異なり=%d / ⑵の総和=%d file / ⑴の総和=%d file'
      % (len(grp), sum(int(r[4]) for r in sashi if r[4] != '測れぬ'), sum(int(r[2]) for r in sashi)))
for B, rs in sorted(grp.items(), key=lambda kv: -len(kv[1])):
    print('  B=%-55s 乗る枝=%2d 本 (割当の%s)' % (B[:55], len(rs), '内' if B in mine else '★外★'))
