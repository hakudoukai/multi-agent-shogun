# -*- coding: utf-8 -*-
"""★吐き口の讀手★(第55弾 ㋑ 補二)

10/12 は「四本の ★名★ を呼ぶ行」を歩いた。然し watchdog の札は
`log()` 経由で ★log file★ へ落ちる ∴ ★四本の名を一度も書かずに札を讀む器★ が在り得る。
本器は ★語★ を argv で受け、其の語を含む file を挙げ、file 全体の byte 切りを数へる。
使ひ方: python3 13_hakikuchi.py <出力tsv> --go <語...> -- <根...>
★零の四札★: 陽性対照(10 で済)・根と深さ(下に刷る)・rc(呼び手が刷る)・刻(下に刷る)。
"""
import sys, os, re, stat, time

D = [('cut_b', re.compile(r'\bcut\b[^|;&\n]*?(?:-b(?=[0-9 ])|--bytes)')),
     ('cut_c', re.compile(r'\bcut\b[^|;&\n]*?(?:-c(?=[0-9 ])|--characters)')),
     ('bash_sl', re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[0-9$][^}]*:[^}]*\}')),
     ('pf_prec', re.compile(r'printf\b[^\n]*%[-+ #0]*\.[0-9]+s')),
     ('head_c', re.compile(r'\bhead\b[^|;&\n]*?(?:-c(?=[0-9 ])|--bytes)')),
     ('dd_bs', re.compile(r'\bdd\b[^|;&\n]*?\bbs=')),
     ('awk_sub', re.compile(r'\bsubstr\s*\('))]

a = sys.argv[1:]
out = a[0]
g = a.index('--go'); s = a.index('--', g)
go, roots = a[g + 1:s], a[s + 1:]

files, skipped = [], []
for r in roots:
    if os.path.isfile(r):
        files.append(r); continue
    for dp, dns, fns in os.walk(r, followlinks=False):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__', 'node_modules')]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                st = os.lstat(p)
            except OSError:
                skipped.append((p, 'lstat不可')); continue
            if not stat.S_ISREG(st.st_mode):
                skipped.append((p, '通常fileに非ず')); continue
            if st.st_size > 2_000_000:
                skipped.append((p, '2MB超')); continue
            files.append(p)
files = sorted(set(files))

nam, cuts = [], []
for p in files:
    try:
        txt = open(p, encoding='utf-8', errors='surrogateescape').read()
    except Exception as e:
        skipped.append((p, '讀めぬ:%s' % e)); continue
    ls = txt.split('\n')
    hit = [(i, l) for i, l in enumerate(ls, 1) if any(w in l for w in go)]
    if not hit:
        continue
    nam.append((p, len(hit)))
    for i, l in enumerate(ls, 1):
        for nm, rx in D:
            if rx.search(l):
                cuts.append((p, i, nm, l.strip()[:140]))

w = open(out, 'w', encoding='utf-8')
w.write('刻=%s\n' % time.strftime('%Y-%m-%dT%H:%M:%S'))
w.write('語=%s\n' % ' '.join(go))
w.write('根(逐語)=%s\n' % ' '.join(roots))
w.write('歩いた深さ=無限(os.walk・symlink 辿らず・通常fileのみ・2MB超は跳ぶ)\n')
w.write('母數(歩いた file)=%d  跳ばした=%d\n' % (len(files), len(skipped)))
w.write('語を含む file=%d\n' % len(nam))
w.write('其の file 群の中の byte 切り=%d\n\n' % len(cuts))
w.write('#colspec\t語を含むfile\t当り行數\n')
for p, n in nam:
    w.write('%s\t%d\n' % (p, n))
w.write('\n#colspec\tbyte切り\t行\t形\t逐語\n')
for c in cuts:
    w.write('%s\t%d\t%s\t%s\n' % c)
w.close()
sys.stderr.write('語含file=%d byte切り=%d 歩=%d 跳=%d\n' % (len(nam), len(cuts), len(files), len(skipped)))
