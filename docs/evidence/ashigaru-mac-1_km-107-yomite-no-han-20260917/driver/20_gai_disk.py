#!/usr/bin/env python3 -B
# -*- coding: utf-8 -*-
"""20_gai_disk.py ―― disk 定義A の各紙を讀み、甲/乙/丙/平/讀めぬ を數へる(km-107 ㋑)。
入=raw/10_disk_A.nul(NUL 區切・改行を含む名も壊さぬ) 出=raw/20_disk_files.tsv / 21_disk_kizu_rows.tsv / 22_disk_totals.txt
定義B = A ∧ basename が大小文字を區別せず '.txt' で終はる。
定義C = A ∧ path行(sha256=<64hex> を含む註でない行) が 1 以上 ―― 讀み手が實際に讀む行を持つ紙。
行數は ★二器★: 器甲 = python で b'\\n' を數へ最後の改行無し塊を +1 / 器乙 = grep -c '' (subprocess・alias 無し)。
非正規(FIFO/device/symlink)は open() せぬ(「止」防止)。"""
import os, stat, sys, subprocess, hashlib, shutil, datetime, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import gai, K

REPO = "/Users/momizimac/multi-agent-shogun"
BUN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(BUN)
GREP = shutil.which("grep")
t0 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

data = open("raw/10_disk_A.nul", "rb").read()
names = data.split(b"\0")
if names and names[-1] == b"":
    names.pop()
paths = [n.decode("utf-8", "surrogateescape") for n in names]

rows, kizu, hi_seiki = [], [], []
tot = {k: 0 for k in ("行總", "註", "讀めぬ", "path行", "甲", "乙", "丙", "平", "丁")}
nB = nC = 0
files_kou = files_otsu = 0
own = 0
kuichigai = 0
topdir = {}
for p in paths:
    rel = os.path.relpath(p, REPO)
    if rel.startswith("docs/evidence/ashigaru-mac-1_km-107-yomite-no-han-20260917"):
        own += 1
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        hi_seiki.append((rel, oct(st.st_mode)))
        continue
    isB = rel.lower().endswith(".txt")
    nB += isB
    with open(p, "rb") as fh:
        b = fh.read()
    c, kz = gai.file_wake(b)
    r = subprocess.run([GREP, "-c", "", p], capture_output=True)
    g = r.stdout.decode().strip()
    gy_grep = int(g) if g.isdigit() else -1
    kui = c["行總"] - gy_grep
    kuichigai += (kui != 0)
    isC = c["path行"] >= 1
    nC += isC
    files_kou += c["甲"] > 0
    files_otsu += c["乙"] > 0
    for k in tot:
        tot[k] += c[k]
    td = rel.split("/")[0] if "/" in rel else "."
    d = topdir.setdefault(td, {"A": 0, "C": 0, "甲": 0, "乙": 0})
    d["A"] += 1; d["C"] += isC; d["甲"] += c["甲"]; d["乙"] += c["乙"]
    rows.append("\t".join(str(x) for x in (
        repr(rel), int(isB), int(isC), st.st_size, c["行總"], gy_grep, r.returncode, kui,
        c["註"], c["讀めぬ"], c["path行"], c["甲"], c["乙"], c["丙"], c["平"], c["丁"],
        hashlib.sha256(b).hexdigest())))
    for no, sh, seg, line in kz:
        kizu.append("\t".join((repr(rel), str(no), sh, repr(seg), repr(line))))

hdr = "path(repr)\tB(.txt)\tC(path行>=1)\tbytes\t行總[python b'\\n']\t行[grep -c '']\tgrep_rc\t食違(python-grep)\t註\t讀めぬ\tpath行\t甲\t乙\t丙\t平\t丁\tsha256"
K.kaku("raw/20_disk_files.tsv", hdr + "\n" + "\n".join(rows) + "\n")
K.kaku("raw/21_disk_kizu_rows.tsv", "path(repr)\t行番\t種\tseg(repr)\t行(repr)\n" + "\n".join(kizu) + "\n")
t1 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
out = [
    "# 22_disk_totals ―― disk 定義A の集計(km-107 ㋐㋑)",
    "刻(始)=%s" % t0, "刻(終)=%s" % t1,
    "歩き根=%s" % REPO, "grep(器乙)=%s" % GREP,
    "入=raw/10_disk_A.nul NUL 區切 本數=%d" % len(paths),
    "非正規(open せず)=%d" % len(hi_seiki),
    "定義A(regular)=%d" % len(rows),
    "定義B(A ∧ .txt)=%d" % nB,
    "定義C(A ∧ path行>=1)=%d" % nC,
    "己の束(docs/evidence/ashigaru-mac-1_km-107-…)に當たつた本數=%d" % own,
    "行總[python b'\\n']=%d" % tot["行總"],
    "行數 食ひ違ひ(python≠grep)の紙=%d" % kuichigai,
    "註=%d 讀めぬ=%d path行=%d" % (tot["註"], tot["讀めぬ"], tot["path行"]),
    "★甲(括つた空白名)行=%d★ 紙=%d" % (tot["甲"], files_kou),
    "★乙(括らぬ空白名)行=%d★ 紙=%d" % (tot["乙"], files_otsu),
    "丙(括つた・空白無=旧形)行=%d" % tot["丙"],
    "平(括らぬ・空白無=本形)行=%d" % tot["平"],
    "丁(' ' '\\t' 以外の unicode 空白を名に含む path行)=%d" % tot["丁"],
    "",
    "## 上位 dir 別: dir\tA\tC\t甲\t乙",
] + ["%s\t%d\t%d\t%d\t%d" % (k, v["A"], v["C"], v["甲"], v["乙"]) for k, v in sorted(topdir.items())] + \
    ["", "## 非正規: rel\tmode"] + ["%s\t%s" % x for x in hi_seiki]
K.kaku("raw/22_disk_totals.txt", "\n".join(out) + "\n")
print(open("raw/22_disk_totals.txt", encoding="utf-8").read())
