# -*- coding: utf-8 -*-
"""㋐の補二: ★「path を抱へる ref 本数」と「disk の版を抱へる ref 本数」は別の數である★。

則: 器 K(scripts/checks 常駐)に付き
  ⑷a path 本数   = 其の ref の tree に path が在る
  ⑷b 版 本数     = 其の ref の tree の blob sha が ★disk の内容の sha1★ と一致する
  ⑷c object 有無 = `git cat-file -e <disk blob sha>` の rc (0=object 在／其の内容は何処かに commit された事が在る)
  ★⑷a>0 でも ⑷b=0 なら「名は版に在るが、今使つて居る物は版に無い」である。★
  ★⑷c=0 は「ref から辿れる」の意では★ない★(dangling・他 ref の途中・reflog 等が在り得る)。★
出目: raw/56_ban.tsv
"""
import os, subprocess, hashlib
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
refs = [ln.split(' ')[0] for ln in subprocess.run(
    ['git', 'for-each-ref', '--format=%(refname)'], capture_output=True, text=True).stdout.split('\n') if ln]
print('手許 ref 母數=%d' % len(refs))
tree = {}
for r in refs:
    p = subprocess.run(['git', 'ls-tree', '-r', r + '^{commit}', '--', 'scripts/checks/'],
                       capture_output=True, text=True)
    m = {}
    if p.returncode == 0:
        for ln in p.stdout.split('\n'):
            if not ln:
                continue
            meta, path = ln.split('\t', 1)
            m[path] = meta.split()[2]
    tree[r] = m
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
    b = open(p, 'rb').read()
    d = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
    a_ = sum(1 for m in tree.values() if p in m)
    b_ = sum(1 for m in tree.values() if m.get(p) == d)
    c_ = subprocess.run(['git', 'cat-file', '-e', d]).returncode
    rows.append((n, d[:12], str(a_), str(b_), str(c_)))
with open(os.path.join(OUT, '56_ban.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\tdisk_blob12\t(4a)path_ref\t(4b)ban_ref\t(4c)object_rc\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
for r in rows:
    print('%-32s blob=%s  path_ref=%-3s 版_ref=%-3s object_rc=%s' % r)
print('★path は在るが版が一本も無い器=%d★' % sum(1 for r in rows if int(r[2]) > 0 and int(r[3]) == 0))
print('★object すら無い器=%d★' % sum(1 for r in rows if r[4] != '0'))
