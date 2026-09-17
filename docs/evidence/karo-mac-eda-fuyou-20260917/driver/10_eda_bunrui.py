#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_eda_bunrui.py ―― origin の mac 系枝を歩き、★他枝に悉く含まれる枝(=不要候補)★を出す。
消さぬ。読取のみ。母數・rc・刻を悉く刷る(裁 seq325493「消すな・名指しで報せ」)。
出: raw/10_lsremote.txt / raw/20_mac_eda.tsv / raw/30_hoyuu.tsv / raw/40_fuyou.tsv / raw/50_summary.txt
"""
import subprocess, sys, os, datetime

def run(a):
    p = subprocess.run(a, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(B, 'raw')
os.makedirs(R, exist_ok=True)
koku = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

rc, out, err = run(['git', 'ls-remote', '--heads', 'origin'])
open(os.path.join(R, '10_lsremote.txt'), 'w', encoding='utf-8').write(out)
zen = [l for l in out.split('\n') if l.strip()]

rows = []
for l in zen:
    sha, ref = l.split('\t')
    n = ref[len('refs/heads/'):]
    if n.startswith('karo-mac/') or n.startswith('ashigaru-mac-'):
        rows.append((sha, n))
rows.sort(key=lambda x: x[1])
with open(os.path.join(R, '20_mac_eda.tsv'), 'w', encoding='utf-8') as f:
    f.write('sha40\tbranch\n')
    for s, n in rows:
        f.write('%s\t%s\n' % (s, n))

# 物が手許に在るか(無ければ測れぬ ―― 0 と書かぬ)
kake = [n for s, n in rows if run(['git', 'cat-file', '-e', s + '^{commit}'])[0] != 0]

anc = {}
for i, (s, n) in enumerate(rows):
    hs = []
    for j, (s2, n2) in enumerate(rows):
        if i == j:
            continue
        if run(['git', 'merge-base', '--is-ancestor', s, s2])[0] == 0:
            hs.append(n2)
    anc[n] = (s, hs)

fuyou = {n for n, (s, h) in anc.items() if h}
nokori = {n for s, n in rows} - fuyou
minashigo = [n for n in sorted(fuyou) if not (set(anc[n][1]) & nokori)]

with open(os.path.join(R, '30_hoyuu.tsv'), 'w', encoding='utf-8') as f:
    f.write('branch\thoyuu_su\thoyuu_ichiran\n')
    for n in sorted(anc):
        s, h = anc[n]
        f.write('%s\t%d\t%s\n' % (n, len(h), ','.join(h) if h else '-'))

rc_m, mainsha, _ = run(['git', 'rev-parse', 'refs/remotes/origin/main'])
mainsha = mainsha.strip()
main_torikomi = [n for s, n in rows if run(['git', 'merge-base', '--is-ancestor', s, mainsha])[0] == 0]

with open(os.path.join(R, '40_fuyou.tsv'), 'w', encoding='utf-8') as f:
    f.write('sha12\tbranch\thoji_saki_nokori_eda\tonaji_sha_no_eda\n')
    for n in sorted(fuyou):
        s, h = anc[n]
        surv = sorted(set(h) & nokori)
        same = sorted(x for x in h if dict(((b, a) for a, b in rows)).get(x) == s)
        f.write('%s\t%s\t%s\t%s\n' % (s[:12], n, surv[0] if surv else '-', ','.join(same) if same else '-'))

with open(os.path.join(R, '50_summary.txt'), 'w', encoding='utf-8') as f:
    f.write('刻=%s\n' % koku)
    f.write('ls-remote rc=%d  origin 全枝=%d\n' % (rc, len(zen)))
    f.write('mac 系 母數=%d (karo-mac/* + ashigaru-mac-*/*)\n' % len(rows))
    f.write('手許に物の無い枝=%d\n' % len(kake))
    f.write('★不要(他枝に悉く含まれる)=%d★  残=%d\n' % (len(fuyou), len(nokori)))
    f.write('★残枝に保持先を持たぬ不要枝=%d★ (0 なら15本悉く消しても内容は失はれぬ)\n' % len(minashigo))
    f.write('origin/main=%s  其に取り込まれた mac 枝=%d/%d\n' % (mainsha[:12], len(main_torikomi), len(rows)))
    f.write('  ―― ∴「不要」は「main に入つた」の意に非ず。「内容が origin の他枝に在る」の意である。\n')
print('done')
