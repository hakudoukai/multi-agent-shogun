# -*- coding: utf-8 -*-
"""㋐の補: ★「版の上に在る」は「disk の物と同じ」の意では無い★ を測る。

則: 器 K に付き、disk の内容の blob sha1 を ★hash-object せず★ 自前で算(sha1("blob N\\0"+bytes))し、
    origin/main / local main / 幹 の tree が持つ blob sha と突合せる。
    (hash-object は object を書き得る ―― ★読取のみ★の禁を守る為 自前で算ずる。)
出目: raw/55_dohitsu.tsv
"""
import os, subprocess, hashlib
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
REFS = [('origin_main', '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'),
        ('local_main', '363d5fb060845171338c067ef42bfcbef8ad9188'),
        ('miki', '68b6e07ba6ef9c765c29a95f8d42ad6cbedb7328')]

def blob_of_disk(p):
    b = open(p, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()

def blob_in(sha, path):
    r = subprocess.run(['git', 'ls-tree', sha + '^{commit}', '--', path], capture_output=True, text=True)
    assert r.returncode == 0
    s = r.stdout.strip()
    return s.split()[2] if s else None

names = []
for i, ln in enumerate(open(os.path.join(OUT, '40_arika.tsv'), encoding='utf-8')):
    if i == 0:
        continue
    a = ln.rstrip('\n').split('\t')
    if int(a[7]) > 0 and a[1] == 'scripts/checks':
        names.append(a[0])
rows = []
for n in sorted(names):
    p = 'scripts/checks/' + n
    d = blob_of_disk(p)
    cells = []
    for lbl, sha in REFS:
        b = blob_in(sha, p)
        cells.append('無' if b is None else ('同' if b == d else '異'))
    rows.append((n, d[:12]) + tuple(cells))
with open(os.path.join(OUT, '55_dohitsu.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\tdisk_blob12\torigin_main\tlocal_main\tmiki\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
for r in rows:
    print('%-32s disk=%s origin/main=%s local main=%s 幹=%s' % r)
print('★「在」の内 disk と異なる版=%d★' % sum(1 for r in rows if r[2] == '異'))
