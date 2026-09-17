# -*- coding: utf-8 -*-
"""★byte 切りの探索器★(第55弾 ㋑ ―― 專任1 第73弾 ㋓ を己の台で検む)

問ひ(逐語・家老 第55弾 ㋑): 「當席が据ゑた版(15ac9f97 等)の ★下流に byte 切りが現に在るか★・
在れば幾本か・母數は何か。無ければ『無い』を陽性対照付きで示せ」

★母數の宣★(此の器が何を歩き、何を数へるか ―― 先に宣す):
  母數A = 生器四本の ★全行★(grep -c "" の行數)。此の中で byte 切り 七形 を数へる。
  母數B = 母數A の内、★印(␊␍␉)の下流★ に在る物。
          下流の定義 = ★其の行に _ft_vp / _ft_v の名が現れる事★(行單位・上限)。
          ★行番の前後では判じぬ★(函数は呼ばれる場所で走る故)。
          之は superset ゆゑ ★0 と出れば「本當に無い」の側へ強い★。
  母數C = 吐き口を讀む器。吐き口 = ①stderr(三本) ②log file(watchdog 一本・tee ゆゑ stdout も)。
          根は argv で受ける(己の台の外を勝手に歩かぬ)。其の中で 四本の名 か LOG path を
          呼ぶ/讀む行を挙げ、其の行(及び同じ pipeline)に byte 切りが在るかを数へる。

七形(★名を付けて数へる ―― 形の排他性も刷る★):
  ①cut_b   cut -b           ②cut_c   cut -c
  ③bash_sl ${V:o:n}         ④pf_prec printf %.Ns
  ⑤head_c  head -c          ⑥dd_bs   dd bs=
  ⑦awk_sub substr(
使ひ方: python3 10_byte_giri.py <出力dir> <生器...> -- <讀手の根...>
"""
import sys, os, re, hashlib

DIALECTS = [
    ('cut_b',   re.compile(r'\bcut\b[^|;&\n]*?(?:-b(?=[0-9 ])|--bytes)')),
    ('cut_c',   re.compile(r'\bcut\b[^|;&\n]*?(?:-c(?=[0-9 ])|--characters)')),
    ('bash_sl', re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[0-9$][^}]*:[^}]*\}')),
    ('pf_prec', re.compile(r'printf\b[^\n]*%[-+ #0]*\.[0-9]+s')),
    ('head_c',  re.compile(r'\bhead\b[^|;&\n]*?(?:-c(?=[0-9 ])|--bytes)')),
    ('dd_bs',   re.compile(r'\bdd\b[^|;&\n]*?\bbs=')),
    ('awk_sub', re.compile(r'\bsubstr\s*\(')),
]
# 下流の被演算子(印を帯びる變數 ―― 生器四本の逐語より)
SHIMO = ('_ft_vp', '_ft_v')


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def lines(p):
    with open(p, encoding='utf-8', errors='surrogateescape') as fh:
        return fh.read().split('\n')


def scan(path):
    """一本を歩き、七形の当りを返す。"""
    out = []
    for i, ln in enumerate(lines(path), 1):
        for name, rx in DIALECTS:
            for m in rx.finditer(ln):
                operand = m.group(1) if (name == 'bash_sl' and m.groups()) else ''
                # ★下流の判定は「行に印の變數が現れるか」の ★上限★★。
                #   逐語(m.group(0))だけを見ると `| cut -b` の形で變數名が入らず、
                #   ★数へ落す★(陽性対照 raw/taisho で二本中一本しか鳴らなんだ)。
                #   ∴ 行單位へ広げる。之は ★上限(superset)★ であり、
                #   「切つて居らぬが同じ行に名が在る」も ★下流★ と数へる。
                #   「無い」を言ふ側にとつては ★安全な向き★ の誤りである。
                shimo = operand in SHIMO or any(s in ln for s in SHIMO)
                out.append((path, i, name, m.group(0), operand, shimo))
    return out


def walk(root, exts=('.sh', '.py', '.yaml', '.yml', '.json', '.plist', '.md', '')):
    """根を歩く。★symlink は辿らぬ・通常 file のみ(FIFO で止まらぬ為)★"""
    hit, skipped = [], []
    if os.path.isfile(root):
        return [root], []
    for dp, dns, fns in os.walk(root, followlinks=False):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__', 'node_modules')]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                st = os.lstat(p)
            except OSError:
                skipped.append((p, 'lstat不可')); continue
            import stat as _s
            if not _s.S_ISREG(st.st_mode):
                skipped.append((p, '通常fileに非ず')); continue
            if st.st_size > 2_000_000:
                skipped.append((p, '2MB超')); continue
            if os.path.splitext(fn)[1] in exts:
                hit.append(p)
    return hit, skipped


def main():
    a = sys.argv[1:]
    outdir = a[0]
    rest = a[1:]
    sep = rest.index('--')
    namaki, roots = rest[:sep], rest[sep + 1:]
    os.makedirs(outdir, exist_ok=True)
    W = lambda n, s: open(os.path.join(outdir, n), 'w', encoding='utf-8').write(s)

    # ── 母數A/B: 生器四本 ──
    rowsA, bodenA = [], 0
    for p in namaki:
        n = len(lines(p)) - (1 if lines(p) and lines(p)[-1] == '' else 0)
        bodenA += n
        rowsA.append(('#器', p, sha16(p), str(n)))
    hits = []
    for p in namaki:
        hits += scan(p)
    tsvA = ['#colspec\t生器\tsha16\t行數(grep -c "")']
    for r in rowsA:
        tsvA.append('\t'.join(r[1:]))
    tsvA.append('')
    tsvA.append('母數A(生器四本の全行)=%d' % bodenA)
    tsvA.append('byte切り 当り 總數=%d' % len(hits))
    tsvA.append('')
    tsvA.append('#colspec\t器\t行\t形\t逐語\t被演算子\t印の下流か')
    for h in hits:
        tsvA.append('%s\t%d\t%s\t%s\t%s\t%s' % (h[0], h[1], h[2], h[3], h[4] or '-', '★下流★' if h[5] else '非'))
    shimo_n = sum(1 for h in hits if h[5])
    tsvA.append('')
    tsvA.append('母數B(印の下流の byte 切り)=%d' % shimo_n)
    # 形の排他性(一つの当りが二形に数へられて居らぬか)
    per = {}
    for h in hits:
        per.setdefault((h[0], h[1], h[3]), set()).add(h[2])
    dup = [k for k, v in per.items() if len(v) > 1]
    tsvA.append('形の排他性: 同じ逐語が二形以上に当つた件數=%d' % len(dup))
    for k in dup:
        tsvA.append('  重複\t%s:%d\t%s\t形=%s' % (k[0], k[1], k[2], ','.join(sorted(per[k]))))
    W('10_namaki.tsv', '\n'.join(tsvA) + '\n')

    # ── 母數C: 讀手 ──
    names = [os.path.basename(p) for p in namaki]
    files, skipped = [], []
    for r in roots:
        f, s = walk(r)
        files += f; skipped += s
    files = sorted(set(files))
    callers, cutters = [], []
    for p in files:
        try:
            ls = lines(p)
        except Exception as e:
            skipped.append((p, '讀めぬ:%s' % e)); continue
        for i, ln in enumerate(ls, 1):
            if any(nm in ln for nm in names):
                cut = [nm for nm, rx in DIALECTS if rx.search(ln)]
                callers.append((p, i, ln.strip()[:160], ','.join(cut) or '-'))
                if cut:
                    cutters.append((p, i, ln.strip()[:160], ','.join(cut)))
    tsvC = ['#colspec\t讀手file\t行\t逐語(160字迄)\t同行のbyte切り形']
    tsvC.append('母數C(歩いた file)=%d  跳ばした=%d' % (len(files), len(skipped)))
    tsvC.append('四本の名を呼ぶ行=%d' % len(callers))
    tsvC.append('其の内 同行に byte 切りが在る行=%d' % len(cutters))
    tsvC.append('')
    for c in callers:
        tsvC.append('%s\t%d\t%s\t%s' % c)
    tsvC.append('')
    tsvC.append('#跳ばした')
    for s in skipped:
        tsvC.append('%s\t%s' % s)
    W('11_yomite.tsv', '\n'.join(tsvC) + '\n')

    sys.stderr.write('母數A=%d行 当り=%d 下流=%d / 母數C=%dfile 呼ぶ行=%d 切る行=%d\n'
                     % (bodenA, len(hits), shimo_n, len(files), len(callers), len(cutters)))
    return 0


sys.exit(main())
