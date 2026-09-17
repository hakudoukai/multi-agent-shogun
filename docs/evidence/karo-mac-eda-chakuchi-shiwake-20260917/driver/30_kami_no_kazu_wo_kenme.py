#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★紙に焼いた数を raw から引き直して検める★(裁 325884 提出前)。
紙が己の臺帳の数を書けぬのと同じく、此の器は ★己の出力を数へぬ★。README.md と raw のみを見る。
"""
import re, subprocess, collections

R = open('README.md', encoding='utf-8').read()
rows = [l.rstrip('\n').split('\t') for l in open('raw/10_sokutei.tsv', encoding='utf-8')][1:]
kou = [r for r in rows if int(r[5]) > 0]
otsu = [r for r in rows if int(r[5]) == 0]
bad = []

def chk(na, jissoku, kami):
    ok = (jissoku == kami)
    print('  %s %-30s 實測=%s 紙=%s' % ('通' if ok else '★違★', na, jissoku, kami))
    if not ok:
        bad.append(na)

chk('残', len(rows), 45)
chk('甲', len(kou), 10)
chk('乙', len(otsu), 35)
chk('丙(cat-file rc非零)', sum(1 for r in rows if r[2] != '0'), 0)
chk('鎖の対', len([l for l in open('raw/20_kusari.tsv', encoding='utf-8')]) - 1, 0)

# 甲の表の 10 行が悉く raw に在り、四つの数が一致するか
tbl = re.findall(r'^\| *\d+ *\| *([^|]+?) *\| *`([0-9a-f]{12})` *\| *(\d+) *\| *(\d+) *\| *(\d+) *\| *(\d+) *\|', R, re.M)
chk('甲の表の行数', len(tbl), 10)
by = {r[0]: r for r in kou}
for na, sha12, n1, n2, nk, nc in tbl:
    r = by.get(na)
    if r is None:
        print('  ★違★ 紙の枝が raw に無: %s' % na); bad.append(na); continue
    got = (r[1][:12], r[3], r[4], r[5], r[6])
    want = (sha12, n1, n2, nk, nc)
    if got != want:
        print('  ★違★ %s 實測=%s 紙=%s' % (na[:40], got, want)); bad.append(na)
print('  甲の表 突合=%d行 一致=%d' % (len(tbl), len(tbl) - sum(1 for b in bad if b in by)))

# 五 幹の数
def g(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd='../../..')
    return p.returncode, p.stdout
_, c = g('rev-list', '--count', '4be3ee19e1c5..363d5fb06084')
chk('幹 commit', int(c.strip()), 16)
_, d = g('diff', '--name-only', '4be3ee19e1c5...363d5fb06084')
fs = [x for x in d.split('\n') if x]
chk('幹 file', len(fs), 464)
top = collections.Counter(x.split('/')[0] if '/' in x else '(直下)' for x in fs)
chk('幹 docs', top.get('docs', 0), 398)
chk('幹 queue', top.get('queue', 0), 52)
chk('幹 scripts', top.get('scripts', 0), 4)

# 基の分布
moto = collections.Counter(r[7].split('(')[0] for r in rows)   # 欄7=jizen_moto(欄8 は領域)
chk('基=km-gate-kou-otsu', moto['karo-mac/km-gate-kou-otsu-20260917'], 27)
chk('基=km-gate4-kou-otsu', moto['karo-mac/km-gate4-kou-otsu-20260917'], 9)
chk('基=km-shikii-yokotenkai', moto['karo-mac/km-shikii-yokotenkai-20260917'], 4)
chk('基=manifest-verify-20260909', moto['karo-mac/manifest-verify-20260909'], 3)

# 六 重なり
t = collections.defaultdict(list)
for r in kou:
    for f in r[9].split(';'):
        if f:
            t[f].append(r[0])
chk('重なり dasumae_gate', len(t['scripts/checks/karo_mac_dasumae_gate.sh']), 4)
chk('重なり manifest_verify', len(t['scripts/checks/karo_mac_manifest_verify.py']), 4)
chk('重なり stop_hook_inbox', len(t['scripts/stop_hook_inbox.sh']), 2)
chk('器の名(重複除)', len(t), 9)

# 乙 で紙に名指した枝が悉く乙に在るか
otsu_na = {r[0] for r in otsu}
sonzai = [n for n in ('karo-mac/km-88-a3-20260917', 'karo-mac/km-89-a2-20260917',
                      'karo-mac/km-90-a1-20260917', 'karo-mac/km-91-a3-20260917',
                      'karo-mac/km-76-repogai-no-ichikasho-wo-nushi-he-watasu-20260917',
                      'karo-mac/km-kansa-daikou-20260913-wo-ref-he-todokeru-20260917')
          if n not in otsu_na]
chk('紙が乙に名指した枝で乙に無い物', len(sonzai), 0)

print('\n★検め %s★ 疵=%d %s' % ('通' if not bad else '落', len(bad), ' '.join(sorted(set(bad)))[:200]))
raise SystemExit(0 if not bad else 1)
