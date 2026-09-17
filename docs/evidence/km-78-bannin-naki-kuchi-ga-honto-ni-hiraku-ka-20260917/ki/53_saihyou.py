# -*- coding: utf-8 -*-
"""53 ★札の引き直し★ ―― 番人を三形 悉く数へ、序列(㋔)まで建てる
當席は番人を ★三度 見落した★。其の度に札が動いた ―― 之が本弾の實である:
  形A 直書 `fix_threshold NAME 既定 受皿`            … 點呼器が初めから見て居た形
  形B 輪   `for _t in NAME:既定 …; do fix_threshold …` … 見落し其の一(52 で写しを走らせ確めた)
  形C 場合 `case "$NAME" in ''|*[!0-9]*) NAME=既定;; esac` … 見落し其の二
★形C は形B と効きが違ふ★: 字でない形(空白のみ/改行入り/既に␊)は悉く捕へるが、
  ★二十桁は全て數字ゆゑ素通りする★。∴ 形C の口は ★四形でなく一形だけ★ 開く。
  之が家老の甲の正体であり、★「番人が無い」ではなく「番人が桁を見て居らぬ」★ である。
★序列の目★: 開く形の数ではなく ★誰の手で引けるか★ で並べる。
  外来=人が env を誤れば引ける / 内生=命令の出目が崩れれば ★誰も触らずとも★ 引ける。"""
import os, re, sys, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
R = '/Users/momizimac/multi-agent-shogun/'
live = [l.split('\t') for l in open(D+'/raw/11_live.tsv',encoding='utf-8').read().splitlines()[1:]]
fuda = {}
for c in [l.split('\t') for l in open(D+'/raw/50_fuda.tsv',encoding='utf-8').read().splitlines()[1:]]:
    fuda[(c[0], c[1], c[2])] = c
k41 = {}
for c in [l.split('\t') for l in open(D+'/raw/41_kuchi.tsv',encoding='utf-8').read().splitlines()[1:]]:
    k41[(c[0], c[1])] = [c[9+i] for i in range(8)]
FN = ['1未設定','2空文字','3空白のみ','4二十桁','5正常値7','6負数','7改行入り','8既存␊']
srcs = {f: open(R+f, encoding='utf-8', errors='replace').read().splitlines() for f in sorted({c[0] for c in live})}
def case_guard(f, name):
    """形C の番人が在るか ―― `case "$NAME" in` の後 8 行内に `*[!0-9]*` が在れば在り"""
    for i, l in enumerate(srcs[f]):
        if re.search(r'case\s+"?\$\{?' + re.escape(name) + r'[:\-}"]*\s+in', l):
            if any('*[!0-9]*' in x for x in srcs[f][i:i+8]): return i + 1
    return 0
rows = []
for c in live:
    f, ln, name, dflt, ban, gen = c
    prev = fuda[(f, ln, name)]
    yurai, fd, riyu = prev[5], prev[6], prev[7]
    cg = case_guard(f, name)
    if fd == '①fail-open' and cg:
        res = k41.get((f, name)) or []
        # 形C を通した後に残る穴は ★二十桁のみ★(全て數字ゆゑ case を素通りする)
        fd, riyu = '①fail-open', '4二十桁 のみ(形C の番人 %s行 が他三形を捕へる ―― ★桁を見て居らぬ★)' % cg
    rows.append([f, ln, name, dflt, yurai, ('形C:%d' % cg) if cg else '無', fd, riyu])
c1 = [r for r in rows if r[6] == '①fail-open']
cnt = collections.Counter(r[6] for r in rows)
hitokata = [r for r in c1 if r[7].startswith('4二十桁 のみ')]
yonkata  = [r for r in c1 if not r[7].startswith('4二十桁 のみ')]
sm = ['# 53 札の引き直し / 母數= %d 口 / %d file' % (len(rows), len({r[0] for r in rows}))]
for k in sorted(cnt): sm.append('    %-12s %2d 口' % (k, cnt[k]))
sm.append('    合計 %d (母數 %d と %s)' % (sum(cnt.values()), len(rows),
          '一致' if sum(cnt.values()) == len(rows) else '★不一致★'))
sm.append('')
sm.append('# ①の内訳 ―― ★開く形の数で分つ★')
sm.append('    一形のみ開く(形C の番人在り・桁だけ抜ける)= %d 口' % len(hitokata))
sm.append('    四形開く(番人 無し)                     = %d 口' % len(yonkata))
sm.append('')
sm.append('# ★序列(㋔)★ 目= 誰の手で引けるか / 何が抜けるか / 気付く路')
sm.append('#   上ほど「人が誤らずとも開く」')
rank = sorted(c1, key=lambda r: (0 if r[4].startswith('内生(命令') else (1 if r[4].startswith('内生') else 2), r[0], int(r[1])))
for i, r in enumerate(rank, 1):
    sm.append('  %2d %-44s:%-5s %-24s %-16s %s' % (i, r[0], r[1], r[2], r[4], r[7][:40]))
K.kaku_tsv(D+'/raw/53_saihyou.tsv', rows,
           header=['file','line','name','default','由来','形C番人','札','理由/何が抜けるか'])
K.kaku(D+'/raw/53_saihyou_summary.txt', '\n'.join(sm))
print('\n'.join(sm[:14]))
print('...(序列は raw/53_saihyou_summary.txt)')
