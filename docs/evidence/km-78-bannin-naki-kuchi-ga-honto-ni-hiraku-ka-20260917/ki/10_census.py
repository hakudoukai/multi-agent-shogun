# -*- coding: utf-8 -*-
"""10 口の census(第56弾 km-78 ㋐の前段)
★定義(機械が判れる形のみ)★
  口 = 字面 ${IDENT:-D} 又は ${IDENT-D} であつて D が十進整数(符号可)である物。一出現=一口。
       ∴ 同じ名が二箇所に出れば ★二口★ と数へる。
  番人在り = ★同じ file の中に★ `fix_threshold <IDENT>` の行が在る事。
  歩き根 = scripts/ と .claude/(再帰・.git と __pycache__ を除く・S_ISREG のみ)。
★本器が意味せぬ事★: 「D が数」は ★閾らしさ★ の代理であつて閾である証ではない。
  ∴ 非閾(retry 回数・port 番号等)も母數に入る。狭めれば己の都合で母數が動くゆゑ広く取る。"""
import os, re, sys, stat
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'
ROOTS = ['scripts', '.claude']
PORT = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):?-([+-]?[0-9]+)\}')
GUARD = re.compile(r'^\s*fix_threshold\s+([A-Za-z_][A-Za-z0-9_]*)', re.M)
DEFN = re.compile(r'^\s*fix_threshold\s*\(\s*\)', re.M)

files, nonreg = [], []
for r in ROOTS:
    for dp, dn, fn in os.walk(os.path.join(M, r)):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__')]
        for f in sorted(fn):
            p = os.path.join(dp, f)
            st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode):
                nonreg.append(os.path.relpath(p, M)); continue
            files.append(p)

rows, guarded_files, defn_files = [], {}, []
for p in files:
    try:
        s = open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    rel = os.path.relpath(p, M)
    g = set(GUARD.findall(s))
    if g: guarded_files[rel] = g
    if DEFN.search(s): defn_files.append(rel)
    for i, ln in enumerate(s.splitlines(), 1):
        for m in PORT.finditer(ln):
            rows.append((rel, i, m.group(1), m.group(2),
                         '番人在' if m.group(1) in g else '★番人無★',
                         ln.strip()[:100]))

K.kaku_tsv(D + '/raw/10_census.tsv', rows,
           header=['file', 'line', 'name', 'default', 'bannin', 'genbun'])
fset = sorted({r[0] for r in rows})
sub = [r for r in rows if r[4] == '★番人無★']
nofix = sorted({r[0] for r in sub if r[0] not in defn_files})
mixed = sorted({r[0] for r in sub if r[0] in defn_files})
sm = ['# 10 口の census / 歩き根= scripts .claude(再帰) / 走査 file 数= %d / 非常体(S_ISREG 外)= %d' % (len(files), len(nonreg))]
sm.append('# 定義: ${IDENT:-D} 又は ${IDENT-D} で D が十進整数。一出現=一口。')
sm.append('★口 総数= %d 口 / %d file★' % (len(rows), len(fset)))
sm.append('★番人在りの口= %d / 番人無しの口= %d★' % (len(rows) - len(sub), len(sub)))
sm.append('fix_threshold の定義を持つ file= %d 本: %s' % (len(defn_files), ' '.join(sorted(defn_files))))
sm.append('★番人を一本も持たぬ file(口在り)= %d 本★: %s' % (len(nofix), ' '.join(nofix)))
sm.append('★番人在る file の中の 守られぬ名★: ' + (' '.join('%s' % x for x in mixed) if mixed else '(無)'))
for f in mixed:
    sm.append('    %s : %s' % (f, ' '.join(sorted({r[2] for r in sub if r[0] == f}))))
sm.append('# 非常体: ' + (' '.join(nonreg) if nonreg else '(無)'))
K.kaku(D + '/raw/10_census_summary.txt', '\n'.join(sm))
print('\n'.join(sm))
