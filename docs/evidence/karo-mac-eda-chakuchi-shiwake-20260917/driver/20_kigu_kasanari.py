#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""甲(着地候補)の器の変更を ★幹★ と突き合はせる（★読取のみ★）。
問ひは二つ ―― ⑴同じ器 file を二本以上の枝が触るか(衝突の種) ⑵其の変更は既に幹に入つて居るか。
幹 = karo-mac/km-gate-kou-otsu-20260917 = 363d5fb06084(手許 main・不要15 の一・commits は 27 本の枝が持つ)。
"""
import subprocess, collections

MIKI = '363d5fb06084'
MAIN = '4be3ee19e1c5'

def g(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout

def kaki(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(l.replace('\r', '').rstrip() for l in lines) + '\n')

rows = [l.rstrip('\n').split('\t') for l in open('raw/10_sokutei.tsv', encoding='utf-8')][1:]
kou = [r for r in rows if int(r[5]) > 0]

out, touch = [], collections.defaultdict(list)
for r in kou:
    name, sha = r[0], r[1]
    for f in r[9].split(';'):
        if not f:
            continue
        touch[f].append(name)
        # 幹 と 枝 で blob が一致するか(=既に幹に在る変更か)
        rc_m, hm = g('rev-parse', '%s:%s' % (MIKI, f))
        rc_b, hb = g('rev-parse', '%s:%s' % (sha, f))
        rc_o, ho = g('rev-parse', '%s:%s' % (MAIN, f))
        st_miki = ('幹に無' if rc_m else ('幹と同' if hm.strip() == hb.strip() else '幹と異'))
        st_main = ('main に無' if rc_o else ('main と同' if ho.strip() == hb.strip() else 'main と異'))
        out.append([name, sha[:12], f, st_miki, st_main])

kaki('raw/40_kigu_vs_miki.tsv',
     ['eda\tsha12\tkigu\tvs_miki\tvs_origin_main'] + ['\t'.join(x) for x in out])
kaki('raw/50_kasanari.tsv',
     ['kigu\teda_suu\teda'] + ['%s\t%d\t%s' % (k, len(v), '|'.join(v))
                               for k, v in sorted(touch.items(), key=lambda x: -len(x[1]))])
print('甲=%d / 器の行=%d / 器の名(重複除)=%d' % (len(kou), len(out), len(touch)))
print('幹と異=%d / 幹と同=%d / 幹に無=%d'
      % (sum(1 for x in out if x[3] == '幹と異'),
         sum(1 for x in out if x[3] == '幹と同'),
         sum(1 for x in out if x[3] == '幹に無')))
print('★二本以上が触る器★:')
for k, v in sorted(touch.items(), key=lambda x: -len(x[1])):
    if len(v) > 1:
        print('  %-48s %d本' % (k, len(v)))
