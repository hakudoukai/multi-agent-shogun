
import importlib.util, fnmatch
from pathlib import Path

V3 = Path("scratch/ashigaru-third-2-fa06a3a1/o78_v3_originmain.py").resolve()
spec = importlib.util.spec_from_file_location("v3", str(V3))
v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)

repo = Path("/mnt/c/DentalBI")
local = set(v3.collect_files(repo))          # glob + git 追跡索引 (DB へ 0 回)
print("== 実 repo (讀取のみ・DB へ 0 回) ==")
print("  repo =", repo, " collect_files (glob 網) =", len(local))
print("  INCLUDE_PATTERNS の本数 =", len(v3.INCLUDE_PATTERNS))

# 二段目 (fnmatch 網) を現樹の path に当てる
def hits(p):
    for pat in v3.INCLUDE_PATTERNS:
        if fnmatch.fnmatch(p, pat): return pat
    return None

pass2 = {p for p in local if hits(p)}
miss  = local - pass2
print("\n== 二段の網の差 (元素 = path 1 本) ==")
print("  一段目 glob が拾ふ (collect_files)      =", len(local))
print("  二段目 fnmatch も通る (消し得る)        =", len(pass2))
print("  二段目で落ちる (glob は拾ふが消せぬ)    =", len(miss))
print("  比 = %.4f" % (len(pass2)/len(local)))

from collections import Counter
c = Counter(p.split("/")[0] for p in miss)
print("\n  落ちる分の先頭階層 (上位 12):")
for k,n in c.most_common(12): print("    %-24s %d" % (k,n))

d1 = Counter("/".join(p.split("/")[:2]) for p in miss)
print("\n  落ちる分の先頭 2 階層 (上位 12):")
for k,n in d1.most_common(12): print("    %-32s %d" % (k,n))

# 落ちる形の見本 (直下 file か否か)
depth_top = sum(1 for p in miss if p.count("/")==1)
print("\n  落ちる分のうち ★1 階層目の直下 file★ =", depth_top, "/", len(miss))
print("  見本 (先頭 8):", sorted(miss)[:8])
