# -*- coding: utf-8 -*-
"""20 川下の比較器(第56弾 km-78 ㋑の判定材料)
口の値が ★何に食はれるか★ を同 file 内で引く。之が札①②③を分ける。
分類(排他・上から先に当る):
  数比 = test/[[ ]] の -ge -gt -le -lt -eq -ne の項に居る    → 非数で ★rc=2★ に成り得る
  算術 = (( )) 又は $(( )) の中に居る                        → bash 算術誤り
  字比 = test の = == != の項に居る                           → ★rc=2 に成らぬ(乙の形)★
  他食 = sleep/awk/printf/代入/比較器以外
★排他性を刷る★(memory 30「form-counter must show exclusivity」): 一行が二類に当る事が在るゆゑ
重複行数を別に数へ、分類は ★行ごと★ でなく ★(口,行,類)★ の三つ組で出す。"""
import os, re, sys, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'
live = [l.split('\t') for l in open(D + '/raw/11_live.tsv', encoding='utf-8').read().splitlines()[1:]]
src = {}
NUM = r'-(?:ge|gt|le|lt|eq|ne)\b'
rows, per = [], collections.defaultdict(set)
for f, ln, name, dflt, ban, gen in live:
    if f not in src:
        src[f] = open(os.path.join(M, f), encoding='utf-8', errors='replace').read().splitlines()
    ref = re.compile(r'\$\{?' + re.escape(name) + r'\b')
    for i, l in enumerate(src[f], 1):
        if not ref.search(l): continue
        seg = l
        kinds = []
        if re.search(NUM, seg) and re.search(r'\$\{?' + re.escape(name), seg):
            # 名が比較器の項に隣接して居るか(粗い近接判定・紙に明記する)
            if re.search(r'\$\{?' + re.escape(name) + r'[^\s]*"?\s*' + NUM, seg) or \
               re.search(NUM + r'\s*"?\$\{?' + re.escape(name), seg):
                kinds.append('数比')
        if re.search(r'\(\([^)]*\b' + re.escape(name) + r'\b', seg) or \
           re.search(r'\$\(\([^)]*\b' + re.escape(name) + r'\b', seg):
            kinds.append('算術')
        if re.search(r'\$\{?' + re.escape(name) + r'[^\s]*"?\s*(?:==|!=|=)(?!=)\s', seg) or \
           re.search(r'(?:==|!=)\s*"?\$\{?' + re.escape(name), seg):
            kinds.append('字比')
        if not kinds: kinds = ['他食']
        for k in kinds:
            rows.append((f, name, ln, i, k, l.strip()[:110])); per[(f, name)].add(k)
K.kaku_tsv(D + '/raw/20_kawashimo.tsv', rows,
           header=['file', 'name', 'port_line', 'use_line', 'kind', 'genbun'])
c = collections.Counter(r[4] for r in rows)
out = ['# 20 川下 / 口 %d / 引いた(口,行,類)三つ組= %d' % (len(live), len(rows))]
out.append('# 類ごとの三つ組: ' + ' '.join('%s=%d' % (k, v) for k, v in sorted(c.items())))
dup = sum(1 for k, v in per.items() if len(v) > 1)
out.append('# ★排他性★ 一つの口が二類以上へ当つた= %d 口 / 全 %d 口(∴類の和は口数を超える)' % (dup, len(per)))
num = sorted({k for k, v in per.items() if '数比' in v})
ari = sorted({k for k, v in per.items() if '算術' in v and '数比' not in v})
out.append('★数比に入る口= %d★(rc=2 の目が在る ―― 之のみが札①の候補)' % len(num))
for f, n in num: out.append('    %s\t%s' % (f, n))
out.append('算術のみに入る口= %d' % len(ari))
for f, n in ari: out.append('    %s\t%s' % (f, n))
out.append('★数比にも算術にも入らぬ口= %d(札②「比較器に入らぬゆゑ疵でない」の候補)★'
           % sum(1 for k, v in per.items() if not ({'数比', '算術'} & v)))
K.kaku(D + '/raw/20_kawashimo_summary.txt', '\n'.join(out))
print('\n'.join(out))
