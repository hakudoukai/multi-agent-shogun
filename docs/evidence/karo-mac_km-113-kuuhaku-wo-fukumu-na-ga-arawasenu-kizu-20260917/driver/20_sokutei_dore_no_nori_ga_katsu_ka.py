# -*- coding: utf-8 -*-
"""★三つの則を一本ずつ當て、旧の連鎖が何を採るかを示す★

行番を焼かず、則の字面は ★照合器の file から逐語で抜く★(手打ちせぬ)。
引数= 抜く元の照合器(既定= 束の _ver/v3_worktree.py)。
"""
import os, re, sys

HEAD, TAIL = "re.search(", ", line)"

def nori_wo_nuku(path):
    """★則を逐語で抜く★ ―― 生文字列の中に逃げた引用符が在る故、
    正規表現で切らず ``re.search(`` と ``, line)`` の間で切る。"""
    lines = open(path, encoding="utf-8").read().split("\n")
    i0 = [i for i, l in enumerate(lines)
          if l.lstrip().startswith("m = re.search") and "本形" in l]
    i1 = [i for i, l in enumerate(lines) if l.strip() == "out.append(_dequote(m.group(1)))"]
    if len(i0) == 1 and len(i1) == 1:          # 旧形(if-not-m の連鎖)
        rng = range(i0[0], i1[0] + 1)
    else:                                       # 直した形(for の列)
        j0 = [i for i, l in enumerate(lines) if l.lstrip().startswith("for _pat in (")]
        j1 = [i for i, l in enumerate(lines) if l.strip() == "m = re.search(_pat, line)"]
        if len(j0) != 1 or len(j1) != 1:
            raise SystemExit("★錨が一意でない ―― 測れぬ★")
        rng = range(j0[0], j1[0])
    out = []
    for k in rng:
        l = lines[k]
        if "path=" in l and (HEAD in l or l.lstrip().startswith("r")):
            s = l.index(HEAD) + len(HEAD) if HEAD in l else l.index("r")
            e = l.index(TAIL, s) if TAIL in l else (l.index(",", s) if "," in l[s:] else len(l))
            e = l.rindex(")", s) if (TAIL not in l and l.rstrip().endswith("):")) else e
            out.append(l[s:e].rstrip(",").rstrip())
    return out

MIHON = [
    ("s_A 素の空白名", 'path=c d.txt sha256=' + "a" * 64 + ' bytes=4 lines=1'),
    ("s_B 括つた舊形", 'path="e.txt" sha256=' + "b" * 64 + ' bytes=4 lines=1'),
    ("s_C 清い名",     'path=kiyoi.txt sha256=' + "c" * 64 + ' bytes=4 lines=1'),
]

def main(argv):
    src = argv[1] if argv[1:] else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_ver", "v3_worktree.py")
    pats = nori_wo_nuku(src)
    print("★則の字面 逐語(%s より抜いた・手打ちに非ず)★ = %d 本" % (os.path.basename(src), len(pats)))
    for i, p in enumerate(pats, 1):
        print("    則%d  %s" % (i, p))
    print()
    for nm, ln in MIHON:
        print("--- %s" % nm)
        for i, p in enumerate(pats, 1):
            m = re.search(eval(p), ln)
            print("      則%d -> %s" % (i, ("★當る★ 捕= %r" % m.group(1)) if m else "當らず"))
        for i, p in enumerate(pats, 1):
            m = re.search(eval(p), ln)
            if m:
                print("      ★旧の連鎖が採るのは 則%d の %r ―― 以下の則は試されぬ★" % (i, m.group(1)))
                break
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
