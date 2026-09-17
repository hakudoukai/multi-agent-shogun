#!/usr/bin/env python3 -B
# -*- coding: utf-8 -*-
"""30_taishou.py ―― ㋒ 己の檢出子への對照(陽性/陰性/rc/刻) と、二版の讀み手を ★同じ行★ に當てる。
対照の紙は raw/taishou/ に置き、名に 'manifest' を含めぬ(己の母數 定義A に入らぬ爲・刻の函数を避ける)。
讀み手 旧 = git blob b19ec9ea…(cat-file -p で raw/14 へ写す) / 直 = disk の scripts/checks/karo_mac_manifest_verify.py。
「正」= paths_of(行)[0] == 名(inner)。"""
import os, sys, subprocess, datetime, ast, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gai, K
from importlib.machinery import SourceFileLoader
REPO = "/Users/momizimac/multi-agent-shogun"
BUN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(BUN)
now = lambda: datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
GREP = shutil.which("grep")
Z = "0" * 64
out = ["# 32_taishou_totals ―― ㋒ 對照(km-107)", "刻(始)=%s" % now()]

# --- 讀み手 二版 ---
OLD = "b19ec9ea259653d9e65d052459128c635a44e93f"
r = subprocess.run(["git", "-C", REPO, "cat-file", "-p", OLD], capture_output=True)
open("raw/14_verify_old_%s.py.txt" % OLD[:8], "wb").write(r.stdout)
old = SourceFileLoader("v_old", "raw/14_verify_old_%s.py.txt" % OLD[:8]).load_module()
NEWP = os.path.join(REPO, "scripts/checks/karo_mac_manifest_verify.py")
new = SourceFileLoader("v_new", NEWP).load_module()
new_blob = subprocess.run(["git", "-C", REPO, "hash-object", NEWP], capture_output=True).stdout.decode().strip()
out += ["讀み手 旧=blob %s (cat-file rc=%d, %d bytes)" % (OLD, r.returncode, len(r.stdout)), "讀み手 直=disk %s blob=%s" % (NEWP, new_blob)]

# --- 對照の紙(己の檢出子) ---
os.makedirs("raw/taishou", exist_ok=True)
fx = {
  "yousei_kou.txt":  "# 陽性 甲\npath=\"a b/c.txt\" sha256=%s bytes=1 lines=1\npath=q/r.txt sha256=%s bytes=1 lines=1\n" % (Z, Z),
  "yousei_otsu.txt": "# 陽性 乙\npath=a b/c.txt sha256=%s bytes=1 lines=1\n" % Z,
  "insei.txt":       "# 陰性(空白無)\npath=a/b.txt sha256=%s bytes=1 lines=1\n'x/y.txt' sha256=%s\nregistry = f/g.txt sha256=%s\n" % (Z, Z, Z),
  "u2028.txt":       "path=a\u2028b/c.txt sha256=%s bytes=1 lines=1\n" % Z,   # U+2028 を名に含む・改行は一つ
}
kitai = {"yousei_kou.txt": (1, 0), "yousei_otsu.txt": (0, 1), "insei.txt": (0, 0), "u2028.txt": (0, 0)}
ok = True
out += ["", "## 己の檢出子 對照: 紙\t甲\t乙\t期待\t判\t行[python b'\\n']\t行[grep -c '']\tsplitlines()\t刻"]
for n, body in fx.items():
    p = "raw/taishou/" + n
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)          # 對照は意圖した byte を其の儘置く(K.kaku の整形を通さぬ・宣)
    b = open(p, "rb").read()
    c, kz = gai.file_wake(b)
    g = subprocess.run([GREP, "-c", "", p], capture_output=True).stdout.decode().strip()
    sl = len(b.decode("utf-8").splitlines())
    han = (c["甲"], c["乙"]) == kitai[n]
    ok &= han
    out.append("%s\t%d\t%d\t%s\t%s\t%d\t%s\t%d\t%s" % (n, c["甲"], c["乙"], kitai[n], "通" if han else "★落★", c["行總"], g, sl, now()))
out.append("對照 rc=%d (0=四紙悉く期待通り)" % (0 if ok else 1))

# --- 二版の讀み手を對照の行に當てる ---
out += ["", "## 讀み手 二版 × 對照の行: 行\t名\t旧[0]\t直[0]\t旧判\t直判"]
for line, name in (('path="a b/c.txt" sha256=%s bytes=1 lines=1' % Z, "a b/c.txt"),
                   ("path=a b/c.txt sha256=%s bytes=1 lines=1" % Z, "a b/c.txt"),
                   ("path=a/b.txt sha256=%s bytes=1 lines=1" % Z, "a/b.txt")):
    o = (old.paths_of(line) or [""])[0]; nw = (new.paths_of(line) or [""])[0]
    out.append("%s\t%r\t%r\t%r\t%s\t%s" % (line[:24], name, o, nw, "正" if o == name else "誤", "正" if nw == name else "誤"))

# --- 二版の讀み手を ★現に在る害行★ に當てる ---
def ateru(src, tag, path_col, seg_col, kind_col, line_col):
    cnt = collections.Counter(); rows = []
    for l in open(src, encoding="utf-8").read().split("\n")[1:]:
        if not l:
            continue
        f = l.split("\t")
        seg = ast.literal_eval(f[seg_col]); line = ast.literal_eval(f[line_col]); kind = f[kind_col]
        name = seg[1:-1] if len(seg) >= 2 and seg[0] == seg[-1] and seg[0] in "\"'" else seg
        o = (old.paths_of(line) or [""])[0]; nw = (new.paths_of(line) or [""])[0]
        ko, kn = ("正" if o == name else "誤"), ("正" if nw == name else "誤")
        cnt[(kind, "旧", ko)] += 1; cnt[(kind, "直", kn)] += 1
        rows.append("%s\t%s\t%s\t%r\t%r\t%r\t%s\t%s" % (f[path_col], f[path_col + 1], kind, name, o, nw, ko, kn))
    K.kaku("raw/31_%s_yomite.tsv" % tag, "path(repr)\t行番\t種\t名\t旧[0]\t直[0]\t旧判\t直判\n" + "\n".join(rows) + "\n")
    return cnt
for src, tag, pc, sc, kc, lc in (("raw/21_disk_kizu_rows.tsv", "disk", 0, 3, 2, 4), ("raw/28_refs_union_kizu_rows.tsv", "refs", 1, 4, 3, 5)):
    cnt = ateru(src, tag, pc, sc, kc, lc)
    out += ["", "## 現に在る害行 × 二版の讀み手 (%s → raw/31_%s_yomite.tsv): 種\t版\t判\t行" % (src, tag)]
    out += ["%s\t%s\t%s\t%d" % (k[0], k[1], k[2], v) for k, v in sorted(cnt.items())]
out.append("刻(終)=%s" % now())
K.kaku("raw/32_taishou_totals.txt", "\n".join(out) + "\n")
print(open("raw/32_taishou_totals.txt", encoding="utf-8").read())
sys.exit(0 if ok else 1)
