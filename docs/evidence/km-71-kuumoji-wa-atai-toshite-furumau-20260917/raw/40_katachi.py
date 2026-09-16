# -*- coding: utf-8 -*-
"""40 形と「空文字が通す判定」(第71弾 ㋒㋓)―― 六つの形 A〜F を ★評価して★ 示す(言ふのでなく走らせる): 各形に 空文字(陽性)と 'A'(陰性)を入れ、判定の出目を刷る。
加へて 20_bosu.tsv から 形A・形B・危=high の現物行を逐語で引く(手写しでない)。"""
import os, sys, re, time
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
m_none = None
FORMS = [
 ('A', '包含 in(右が str 定数)', "s[:1] in 'AM'", lambda s: s[:1] in 'AM', "空文字は如何なる文字列にも含まれる('' in x は常に True)∴ 空要素が『A か M』として通る"),
 ('B', "等価 == と ''", "s == ''", lambda s: s == '', "空文字を番兵に使ふ判定は、値の欠と『空といふ値』を見分けぬ(None と '' が別の意味でも同じ枝へ)"),
 ('C', '既定落ち x or 定数', "s or 'default'", lambda s: s or 'default', "空文字は falsy ゆゑ既定へ黙つて落ちる ―― 『空と測れた』が『既定と同じ』に化ける"),
 ('D', '真偽 if x / if not x(裸)', "bool(s)", lambda s: bool(s), "空文字は False ―― 『無い』と『空である』が同じ枝へ(0byte と「空である旨の一行」の別が消える)"),
 ('E', '三項 … if m else 定数', "s if s else '?'", lambda s: s if s else '?', "空文字は else へ落ち定数(例 '?')に化ける ―― 測れた空が『引けぬ』の顔を着る"),
 ('F', "startswith('') / endswith('')", "s.startswith('')", lambda s: s.startswith(''), "空文字の接頭辞は全てに合ふ(常に True)∴ 篩が篩でなくなる"),
]
out = [f'# 40 形と「空文字が通す判定」/ 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 各形を 陽性 \'\'(空文字)と 陰性 \'A\' で評価(python {sys.version.split()[0]})',
       '| 形 | 名 | 式 | 空文字 \'\' の出目 | \'A\' の出目 | 空文字が通す判定(一行) |', '|---|---|---|---|---|---|']
for k, name, expr, fn, line in FORMS: out.append(f"| {k} | {name} | `{expr}` | `{fn('')!r}` | `{fn('A')!r}` | {line} |")
rows = [l.rstrip('\n').split('\t') for l in open(RAW + '/20_bosu.tsv', encoding='utf-8')][1:]
pick = [r for r in rows if r[2] == '現物' and (r[4] in ('A', 'B') or r[5] == 'high')]
out.append(f'## 現物の 形A・形B・危=high の行(20_bosu.tsv から・{len(pick)} 行): 束 / file / 行 / 形 / 危 / 逐語')
for r in pick: out.append(f'  {r[0][:8]} / {r[1]} / L{r[3]} / {r[4]} / {r[5]} / {r[6]}')
cnt = {k: sum(1 for r in rows if r[2] == '現物' and r[4] == k) for k, *_ in FORMS}
out.append('## 形別 M(現物・20 と同じ tsv から数へ直し): ' + ' / '.join(f'{k} {v}' for k, v in cnt.items()) + f' / 計 {sum(cnt.values())}')
out.append('## 註: M は「効き得る箇所」であつて疵の数ではない。D/E の多くは欠を扱ふ設計(m が None なら…)であり、空文字が★其處へ来るか★は器では判ぜぬ(値の来歴は静的に決まらぬ)。∴ M は上界。危=high は「左が slice(空を産む)」か F(常に真)で、来歴に依らず空が通る形。')
K.kaku(RAW + '/40_katachi.txt', '\n'.join(out)); print('\n'.join(out))
