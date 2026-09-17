# -*- coding: utf-8 -*-
"""㋐の補三: ★~/bin の器は repo の外に在る★ を、名でも版でも確かめる。

則: 器 K(~/bin 常駐・㋑が拾つた物)に付き
  ⑸ 同名の file が ★repo の全 ref のどの path にも★ 在るか(basename 一致・path は問はぬ)
  ⑹ disk の内容の blob sha1 を持つ object が在るか(`git cat-file -e`)
  ★⑸=0 かつ ⑹≠0 なら、其の器は「版の何処にも無い」。disk が失せれば消える。★
  ★之は「器が悪い」の意では無い。★置き場の話である。
出目: raw/57_hbin.tsv
"""
import os, subprocess, hashlib
os.chdir('/Users/momizimac/multi-agent-shogun')
BD = 'docs/evidence/ashigaru-mac-2_km-104-ki-no-arika-to-unpan-20260917'
OUT = os.path.join(BD, 'raw')
refs = [ln for ln in subprocess.run(['git', 'for-each-ref', '--format=%(refname)'],
                                    capture_output=True, text=True).stdout.split('\n') if ln]
names = []
for i, ln in enumerate(open(os.path.join(OUT, '40_arika.tsv'), encoding='utf-8')):
    if i == 0:
        continue
    a = ln.rstrip('\n').split('\t')
    if int(a[7]) > 0 and a[1] == '~/bin':
        names.append(a[0])
print('~/bin の甲=%d: %s' % (len(names), ' '.join(sorted(names))))
# 全 ref の basename 表を一度だけ作る
base = {}
for r in refs:
    p = subprocess.run(['git', 'ls-tree', '-r', '--name-only', r + '^{commit}'], capture_output=True, text=True)
    if p.returncode != 0:
        continue
    for path in p.stdout.split('\n'):
        if path:
            base.setdefault(path.rsplit('/', 1)[-1], set()).add(path)
print('全 ref の basename 相異=%d' % len(base))
rows = []
for n in sorted(names):
    p = os.path.join('/Users/momizimac/bin', n)
    b = open(p, 'rb').read()
    d = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
    paths = sorted(base.get(n, ()))
    rc = subprocess.run(['git', 'cat-file', '-e', d]).returncode
    rows.append((n, d[:12], str(len(paths)), ';'.join(paths) if paths else '-', str(rc)))
with open(os.path.join(OUT, '57_hbin.tsv'), 'w', encoding='utf-8') as f:
    f.write('ki_mei\tdisk_blob12\t(5)dou_mei_path_suu\tpath\t(6)object_rc\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
for r in rows:
    print('%-24s blob=%s 同名 path=%s %s object_rc=%s' % r)
print('★版の何處にも無い(⑸=0 かつ ⑹≠0)=%d / %d★' % (
    sum(1 for r in rows if r[2] == '0' and r[4] != '0'), len(rows)))
