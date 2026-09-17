# -*- coding: utf-8 -*-
"""㋑の前段: origin の mac 枝 60 本から ★45 本★ を切り出す。
母數の宣: 「mac 枝」= refs/heads/{karo-mac,ashigaru-mac-1,ashigaru-mac-2,ashigaru-mac-3}/ の前置を持つ枝。
  (tools/karo-mac-gate7-20260908 は ★席前置で無い★ ゆゑ 母數の外。除いたのであつて、無いのではない。)
「不要」= 其の tip が ★他の枝の tip の真の祖先★ である枝(呑まれて居る)。
  ★同 sha の対は「真の祖先」に非ず★(A==B は祖先判定 rc=0 に成るが、呑みでは無い)。
出目: raw/20_eda60.tsv (全 60 本・呑み判定付き) / raw/20_eda45.txt (45 本のみ)
"""
import subprocess, os, sys, collections
os.chdir('/Users/momizimac/multi-agent-shogun')
OUT = os.path.join('docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917', 'raw')
SRC = os.path.join(OUT, '00_lsremote.txt')
PRE = ('karo-mac/', 'ashigaru-mac-1/', 'ashigaru-mac-2/', 'ashigaru-mac-3/')

eda = []
for ln in open(SRC, encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln:
        continue
    sha, ref = ln.split('\t', 1)
    if not ref.startswith('refs/heads/'):
        continue
    name = ref[len('refs/heads/'):]
    if name.startswith(PRE):
        eda.append((name, sha))
print('mac 枝 母數=%d' % len(eda))
assert len(eda) == 60, len(eda)
print('相異なる sha=%d' % len(set(s for _, s in eda)))

# 手許に物が在るか(無ければ祖先判定が出来ぬ ―― 「測れぬ」と書く)
teheart = {}
for name, sha in eda:
    r = subprocess.run(['git', 'cat-file', '-e', sha + '^{commit}'])
    teheart[sha] = r.returncode
print('手許に物 rc=0 の枝=%d / 60' % sum(1 for _, s in eda if teheart[s] == 0))

rows, nomareta = [], []
for name, sha in eda:
    if teheart[sha] != 0:
        rows.append((name, sha, '測れぬ', '', 'cat-file rc=%d' % teheart[sha]))
        continue
    nomu = []
    for n2, s2 in eda:
        if s2 == sha:          # ★同 sha は呑みに非ず★
            continue
        if teheart[s2] != 0:
            continue
        r = subprocess.run(['git', 'merge-base', '--is-ancestor', sha, s2])
        if r.returncode == 0:
            nomu.append(n2)
    if nomu:
        rows.append((name, sha, '不要', ';'.join(sorted(nomu)), '呑む枝=%d' % len(nomu)))
        nomareta.append(name)
    else:
        rows.append((name, sha, '残', '', ''))

with open(os.path.join(OUT, '20_eda60.tsv'), 'w', encoding='utf-8') as f:
    f.write('eda\tsha\thantei\tnomu_eda\tbiko\n')
    for r in rows:
        # ★空欄は `-` で埋める★ ―― 空の儘だと行末が TAB に成り、門の條②(末尾空白)が鳴る。
        # (「空の欄」と「- と書いた欄」は別物である ∴ 紙に宣する。)
        f.write('\t'.join(x if x else '-' for x in r) + '\n')
nokori = [(n, s) for n, s, h, _, _ in rows if h == '残']
with open(os.path.join(OUT, '20_eda45.txt'), 'w', encoding='utf-8') as f:
    for n, s in nokori:
        f.write('%s\t%s\n' % (s, n))
print('不要(呑まれ)=%d / 残=%d / 測れぬ=%d' % (len(nomareta), len(nokori),
      sum(1 for r in rows if r[2] == '測れぬ')))
