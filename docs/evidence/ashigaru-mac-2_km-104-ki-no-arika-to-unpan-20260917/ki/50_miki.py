# -*- coding: utf-8 -*-
"""㋒: ★幹 68b6e07b が運ぶ器★を列べ、㋑の欠と引き算する。

引き算の則(先に宣する):
  欠 = ㋐の表で ★⑵origin/main=0★ の甲。(=版の上に無い器)
  幹が運ぶ = `git ls-tree -r --name-only 68b6e07b -- scripts/checks/` に其の path が在る。
  残る欠 = 欠 − 幹が運ぶ。★之が「幹が着地しても尚 欠ける器」＝次の小PR の中身★。
  ★~/bin の器は幹に載り様が無い(repo の外)★ ゆゑ、引き算の外に別立てで書く。
  ★「幹が運ぶ」は「幹が origin/main に着く」の意では無い。★幹は今 origin/karo-mac/km-gate-kou-otsu に在るのみ。
出目: raw/50_miki.tsv / raw/50_hikizan.tsv
"""
import os, subprocess
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
MIKI = '68b6e07ba6ef9c765c29a95f8d42ad6cbedb7328'
MAIN_O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'

def tree(sha, sub):
    r = subprocess.run(['git', 'ls-tree', '-r', '--name-only', sha + '^{commit}', '--', sub],
                       capture_output=True, text=True)
    assert r.returncode == 0, (sha, r.returncode)
    return set(x for x in r.stdout.split('\n') if x)

mk = tree(MIKI, 'scripts/checks/')
om = tree(MAIN_O, 'scripts/checks/')
print('幹の scripts/checks/=%d本 / origin/main の=%d本' % (len(mk), len(om)))
with open(os.path.join(OUT, '50_miki.tsv'), 'w', encoding='utf-8') as f:
    f.write('path\tmiki\torigin_main\tsa\n')
    for p in sorted(mk | om):
        a, b = int(p in mk), int(p in om)
        f.write('%s\t%d\t%d\t%s\n' % (p, a, b, '幹のみ' if a and not b else ('main のみ' if b and not a else '両方')))
print('幹のみ=%d / main のみ=%d / 両方=%d' % (len(mk - om), len(om - mk), len(mk & om)))

rows = []
for i, ln in enumerate(open(os.path.join(OUT, '40_arika.tsv'), encoding='utf-8')):
    if i == 0:
        continue
    a = ln.rstrip('\n').split('\t')
    if int(a[7]) == 0:            # ㋑で拾はれて居らぬ器は「紙を焼くのに要る」の證が無い
        continue
    name, okiba, om_f = a[0], a[1], int(a[3])
    if om_f == 1:
        rows.append((name, okiba, '在', '-', '-', '版の上に在る'))
        continue
    if okiba == '~/bin':
        rows.append((name, okiba, '無', '運べぬ', '残る', '★repo の外★ ゆゑ幹に載り様が無い'))
        continue
    p = okiba + '/' + name
    if p in mk:
        rows.append((name, okiba, '無', '運ぶ', '消える', '幹が着けば版に載る'))
    else:
        rows.append((name, okiba, '無', '運ばぬ', '残る', '★次の小PR の中身★'))
with open(os.path.join(OUT, '50_hikizan.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\tokiba\torigin_main\tmiki\tnokoru_ketsu\tbiko\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
n_ketsu = sum(1 for r in rows if r[2] == '無')
n_nokoru = sum(1 for r in rows if r[4] == '残る')
print('㋑の甲=%d / 内 欠(origin/main 無)=%d / 幹が運ぶ=%d / ★残る欠=%d★' % (
    len(rows), n_ketsu, sum(1 for r in rows if r[3] == '運ぶ'), n_nokoru))
