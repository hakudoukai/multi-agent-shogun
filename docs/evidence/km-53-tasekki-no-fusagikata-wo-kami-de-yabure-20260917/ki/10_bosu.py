# -*- coding: utf-8 -*-
"""usage: 10_bosu.py <paper.md> <outdir>
母數を先に出す ―― ⑴案イ diff 行 N ⑵案ロ diff 行 M ⑶二案が当たる路 K。
K の数へ方は ★呼ぶ器を実際に通したか・宣だけか★ を欄で分けて刷る。
行の数へ方: '+++'/'---' を除き、先頭 1 字が '+'/'-'/' ' で分ける(空の追加行を落とさぬ)。
"""
import sys, os, re, subprocess, json

paper, outdir = sys.argv[1], sys.argv[2]
s = open(paper, encoding='utf-8').read()

# diff 塊を題で取る
blocks = {}
for name, head in (('i', '## 2. 案イ'), ('ro', '## 3. 案ロ')):
    i = s.index(head)
    j = s.index('```diff', i) + len('```diff\n')
    k = s.index('```', j)
    blocks[name] = s[j:k]

rows = []
for name in ('i', 'ro'):
    body = blocks[name]
    lines = body.split('\n')
    if lines and lines[-1] == '':
        lines = lines[:-1]
    add = [l for l in lines if l.startswith('+') and not l.startswith('+++')]
    rem = [l for l in lines if l.startswith('-') and not l.startswith('---')]
    ctx = [l for l in lines if not (l.startswith('+') or l.startswith('-'))]
    rows.append((name, len(lines), len(add), len(rem), len(ctx)))

out = []
out.append('=== ㋐-1 二案の diff 行(紙 %s から抜いた) ===' % os.path.basename(paper))
out.append('#colspec\t案\t総行\t追(+)\t除(-)\t文脈')
for r in rows:
    out.append('%s\t%d\t%d\t%d\t%d' % r)
out.append('N(案イ 総行)=%d  M(案ロ 総行)=%d' % (rows[0][1], rows[1][1]))
out.append('註: 紙 §4 の表は「変更の行数(概算) イ +9 −6 / ロ +10 −6」と宣す。實測の追/除と照らせ。')

# ―― K: 門を呼ぶ路 ――
root = os.getcwd()
GATE = 'karo_mac_dasumae_gate.sh'
ENV = 'KM_GATE_MANIFEST_BASE'

tracked = subprocess.run(['git', 'ls-files', '-z'], capture_output=True)
names = [n.decode('utf-8', 'surrogateescape') for n in tracked.stdout.split(b'\0') if n]

def hits(paths, label):
    g, e, unread = [], [], 0
    for p in paths:
        try:
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            if os.path.getsize(p) > 4_000_000:
                unread += 1
                continue
            t = open(p, 'rb').read().decode('utf-8', 'replace')
        except Exception:
            unread += 1
            continue
        if GATE in t:
            g.append(p)
        if ENV in t:
            e.append(p)
    return g, e, unread

g_t, e_t, unread_t = hits(names, 'tracked')

# 未追跡の路: ~/bin と scripts/ 配下の実体
extra = []
for base in (os.path.expanduser('~/bin'), os.path.join(root, 'scripts'), os.path.join(root, '.claude')):
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__')]
        for f in fn:
            extra.append(os.path.join(dp, f))
extra = [p for p in extra if os.path.relpath(p, root) not in set(names)]
g_x, e_x, unread_x = hits(extra, 'untracked')

out.append('')
out.append('=== ㋐-2 K ―― 二案が当たる路(門 %s を呼ぶ/名を持つ file) ===' % GATE)
out.append('母集合: git 追跡 %d 本 + 未追跡(~/bin, scripts/, .claude/) %d 本 = %d 本' % (len(names), len(extra), len(names)+len(extra)))
out.append('讀めなんだ(4MB超・open 不能): 追跡 %d / 未追跡 %d' % (unread_t, unread_x))
out.append('門の名を持つ file: 追跡 %d / 未追跡 %d' % (len(g_t), len(g_x)))
out.append('%s の名を持つ file: 追跡 %d / 未追跡 %d' % (ENV, len(e_t), len(e_x)))
out.append('')
out.append('--- %s を持つ file(全件) ---' % ENV)
for p in sorted(e_t) + sorted(e_x):
    out.append('  ' + p)
out.append('')
out.append('--- 門の名を持つ file の内、docs/evidence/ の外(=器らしき物) ---')
for p in sorted(g_t) + sorted(g_x):
    if not p.startswith('docs/evidence/'):
        out.append('  ' + p)

open(os.path.join(outdir, '10_bosu.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
