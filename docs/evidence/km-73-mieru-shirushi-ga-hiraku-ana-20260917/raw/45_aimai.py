# -*- coding: utf-8 -*-
"""㋔ 印の曖昧性 45 ―― 値に元から ␊ が在る時、下流の讀手は「注入された改行の印」と「値その物の ␊」を区別できるか。
対: (A 1\\n2, B 1␊2) (C 1\\r2, D 1␍2) (E 1\\n␊2, F 1␊\\n2)。乙 と 乙′(escape の escape) で stderr の sha16 を比べる。陽性対照 = A と abc(必ず違ふ)。"""
import sys, time
D = sys.argv[1]; E = D + '/raw'; sys.path.insert(0, E); import kaki as K, dai73 as T
PAIRS = [('A 1\\n2', '1\n2', 'B 1␊2', '1␊2'), ('C 1\\r2', '1\r2', 'D 1␍2', '1␍2'), ('E 1\\n␊2', '1\n␊2', 'F 1␊\\n2', '1␊\n2'), ('G \\\\n', '\\n', 'H 1\\n2 (対照 A と同値)', '1\n2')]
rows = []; out = [f'# 45 印の曖昧性 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
for key, rel in T.TGT:
    for an in ('乙', '乙′'):
        p = T.dai_path(E + '/dai', key, an)
        for n1, v1, n2, v2 in PAIRS:
            s1 = T.hashi(p, v1)[2]; s2 = T.hashi(p, v2)[2]
            rows.append((rel, an, n1, n2, T.sha16(s1), T.sha16(s2), '★同(区別できぬ)★' if s1 == s2 else '異(区別できる)', T.esc(s1)[:90], T.esc(s2)[:90]))
        s1 = T.hashi(p, '1\n2')[2]; s2 = T.hashi(p, 'abc')[2]; rows.append((rel, an, 'A 1\\n2', '陽性対照 abc', T.sha16(s1), T.sha16(s2), '異(区別できる)' if s1 != s2 else '★同 ―― 讀手が死んで居る★', T.esc(s1)[:90], T.esc(s2)[:90]))
K.kaku_tsv(E + '/45_aimai.tsv', rows, ['生器', '案', '値1', '値2', 'sha16(札1)', 'sha16(札2)', '判', '札1(esc)', '札2(esc)'])
for an in ('乙', '乙′'):
    same = [r for r in rows if r[1] == an and r[6].startswith('★同')]; out.append(f'{an}: 区別できぬ対 {len(same)}/{sum(1 for r in rows if r[1]==an)}: ' + ' / '.join(f'{r[0].split("/")[-1]} {r[2]}⇔{r[3]}' for r in same))
out.append('乙′ の逐語(當席の試案・据ゑず): ' + T.OTSU2.split('\n')[0].strip())
K.kaku(E + '/45_aimai.txt', '\n'.join(out)); print('\n'.join(out))
