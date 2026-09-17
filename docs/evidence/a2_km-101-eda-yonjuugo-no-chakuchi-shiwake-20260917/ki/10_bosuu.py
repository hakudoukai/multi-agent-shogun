# -*- coding: utf-8 -*-
"""㋐ 母數を宣する器。
  甲: 割当 13 本 ―― ★札(raw/00_fuda.yaml の eda_warimochi)から逐語で読む★(手打ちせぬ)。
  乙: 60 本の mac 枝 tip ―― ★raw/00_lsremote.txt(origin の生の写し)から読む★。
  丙: 手許に物が在るか ―― `git cat-file -e <sha>^{commit}` の rc を一本づつ書く。
出: raw/10_bosuu_warimochi.tsv / raw/10_bosuu_mac60.tsv / raw/10_bosuu_koku.txt
"""
import os, subprocess, sys, re
ROOT = '/Users/momizimac/multi-agent-shogun'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

def g(*a):
    r = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

# ---- 甲: 札から割当を読む(逐語) ----
s = open('raw/00_fuda.yaml', encoding='utf-8').read()
m = re.search(r'^eda_warimochi:\s*\|\s*$(.*?)(?=^\S|\Z)', s, re.M | re.S)
assert m, '★札に eda_warimochi が無い★'
war = []
for line in m.group(1).split(chr(10)):
    if not line.strip():
        continue
    p = line.split()
    assert len(p) == 2, '★札の行が二語でない: %r★' % line
    assert re.fullmatch(r'[0-9a-f]{40}', p[0]), '★sha が40桁hexでない: %r★' % p[0]
    war.append((p[0], p[1]))
assert len(war) == 13, '★割当は13本の筈が %d★' % len(war)

# ---- 乙: origin の mac 枝 60 本 ----
mac60 = []
for line in open('raw/00_lsremote.txt', encoding='utf-8'):
    line = line.rstrip(chr(10))
    if not line:
        continue
    sha, ref = line.split('\t', 1)
    name = ref[len('refs/heads/'):] if ref.startswith('refs/heads/') else ref
    if re.match(r'^(ashigaru-mac-[0-9]+|karo-mac|gunshi-mac)/', name):
        mac60.append((sha, name))
print('origin の mac 枝 = %d 本 / 相異なる sha = %d' % (len(mac60), len(set(x[0] for x in mac60))))

# ---- 丙: 手許に物が在るか ----
def aru(sha):
    rc, _, _ = g('cat-file', '-e', sha + '^{commit}')
    return rc

rows = []
for sha, name in war:
    rc = aru(sha)
    on60 = [n for s2, n in mac60 if s2 == sha]
    rows.append((name, sha, rc, ';'.join(on60) if on60 else '-'))
with open('raw/10_bosuu_warimochi.tsv', 'w', encoding='utf-8') as f:
    f.write('枝名\tsha40\tcat_file_rc\torigin側の同sha枝名\n')
    for r in rows:
        f.write('%s\t%s\t%d\t%s\n' % r)

n_aru = sum(1 for r in rows if r[2] == 0)
rows60 = []
for sha, name in sorted(mac60, key=lambda x: x[1]):
    rows60.append((name, sha, aru(sha)))
with open('raw/10_bosuu_mac60.tsv', 'w', encoding='utf-8') as f:
    f.write('枝名\tsha40\tcat_file_rc\n')
    for r in rows60:
        f.write('%s\t%s\t%d\n' % r)
n60_aru = sum(1 for r in rows60 if r[2] == 0)

rc_m, out_m, _ = g('rev-parse', '4be3ee19e1c5^{commit}')
with open('raw/10_bosuu_koku.txt', 'w', encoding='utf-8') as f:
    f.write('割当=%d本 / 手許に物在り(rc=0)=%d本 / 欠(rc!=0)=%d本\n' % (len(rows), n_aru, len(rows) - n_aru))
    f.write('origin mac 枝=%d本 / 相異なる sha=%d / 手許に物在り=%d本 / 欠=%d本\n'
            % (len(mac60), len(set(x[0] for x in mac60)), n60_aru, len(mac60) - n60_aru))
    f.write('origin/main の基点 4be3ee19e1c5 rev-parse rc=%d sha=%s\n' % (rc_m, out_m.strip()))
print(open('raw/10_bosuu_koku.txt', encoding='utf-8').read(), end='')
