#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓ ★案を三つ・数で評す★ ―― 「戸が開けば入る物」を案毎に切り、危険品を併記する。

案⑴何も焼かぬ(★既定★) / 案⑵己の三束のみ / 案⑶配下悉く。
本数・byte和・戻し方 を併書し、各案に★入る危険品★を数で書く。
「入る物」= disk に在つて git の index に無い物(= 戸が開いて初めて commit し得る物)。
歩き根=argv[1](repo 根) 出先=argv[2]
"""
import os
import re
import stat
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv, esc  # noqa: E402

NE = "docs/evidence"
AN2 = ("ashigaru-mac-2_km-117-v5-wo-240-hashiri-ni-kakeyo-20260917",
       "ashigaru-mac-2_km-120-hougen-hei-no-kyuumen-20260917",
       "ashigaru-mac-2_km-122-pr24-ga-akeru-to-no-mukou-20260917")

HIMITSU = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----"
    r"|\b(?:AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA)[0-9A-Z]{16}\b"
    r"|\bsk-ant-[A-Za-z0-9_\-]{20,}"
    r"|\bsk-(?!ant-)[A-Za-z0-9]{20,}"
    r"|\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b"
    r"|\bxox[abprs]-[A-Za-z0-9\-]{10,}"
    r"|\bAIza[0-9A-Za-z_\-]{35}\b"
    r"|\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")
MAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
KOUKAI = ("@github.com", "@users.noreply.github.com", "@anthropic.com",
          "@example.com", "@example.org", "@example.invalid", "@MomiziMac-mini.local")
F = "KM122ZQ"
# ★己の器が己の罠に成る★ ―― 対照を素で書けば、此の file 自身が「秘の形」を持つ 1 本に成る
# (実測: 直前の走で 30_an.py が案⑵の「秘の形=1本」であつた)。∴ 実行時に組む。
# 隣り合ふ字面は CPython が畳み込む ∴ `+` ではなく `%` を使ふ(畳まれぬ)。
PEM = "-%s-%s %s PRIVATE KEY-%s-" % ("----", "BEGIN", "RSA", "----")
TAI = [("対_秘の形", PEM + F, HIMITSU),
       ("対_実在宛", "taro." + F + "@somewhere.jp", MAIL)]
OOKII = 1048576


def main():
    repo = os.path.abspath(sys.argv[1])
    outdir = os.path.abspath(sys.argv[2])
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    naranu = 0
    trows = []
    for na, s, r in TAI:
        ok = r.search(s) is not None
        trows.append([na, "鳴つた" if ok else "★鳴らぬ★", "<伏:%d字>" % len(s)])
        if not ok:
            naranu += 1

    p = subprocess.run(["git", "-C", repo, "ls-files", "-z", "--", NE],
                       capture_output=True)
    if p.returncode != 0:
        sys.stderr.write("★git ls-files rc=%d ∴ 測らず終る★\n" % p.returncode)
        return 3
    tracked = set(x for x in p.stdout.decode("utf-8", "replace").split("\0") if x)

    root = os.path.join(repo, NE)
    hairu = []           # (rel_from_repo, size, 束, flags)
    nfile = yomenu = 0
    for dp, dn, fns in os.walk(root):
        for fn in fns:
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, repo)
            try:
                st = os.lstat(fp)
            except OSError:
                yomenu += 1
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            nfile += 1
            if rel in tracked:
                continue
            try:
                t = open(fp, "rb").read().decode("utf-8", "replace")
            except OSError:
                yomenu += 1
                t = ""
            fl = set()
            if HIMITSU.search(t):
                fl.add("秘の形")
            for m in MAIL.finditer(t):
                if not any(m.group(0).endswith(x) for x in KOUKAI):
                    fl.add("実在らしき宛")
                    break
            if fn.endswith(".b64") or fn.endswith(".sh"):
                fl.add("器の写し")
            if st.st_size >= OOKII:
                fl.add("巨大(1MiB以上)")
            if "__pycache__" in rel or rel.endswith(".pyc"):
                fl.add("__pycache__")
            tab = rel.split("/")[2] if rel.count("/") >= 2 else rel
            hairu.append((rel, st.st_size, tab, fl))

    def shime(sel):
        n = sum(1 for r in hairu if sel(r))
        b = sum(r[1] for r in hairu if sel(r))
        tb = set(r[2] for r in hairu if sel(r))
        ki = {}
        for r in hairu:
            if sel(r):
                for f in r[3]:
                    ki[f] = ki.get(f, 0) + 1
        return n, b, len(tb), ki

    an = [
        ("案⑴ 何も焼かぬ(★既定★)", lambda r: False,
         "戻し方= ★不要★(何も動かさぬ)"),
        ("案⑵ 己の三束のみ(km-117/120/122)", lambda r: r[2] in AN2,
         "戻し方= `git rm -r --cached docs/evidence/<束>` 一行 + .gitignore を元へ。commit 一本ゆゑ revert 一本でも戻る。"),
        ("案⑶ docs/evidence 配下 悉く", lambda r: True,
         "戻し方= 同じ形だが ★82束・7千本★ を一度に戻す事に成る。★push 後は戻せぬ★(公開された物は消せぬ)。"),
    ]

    L = []
    L.append("== ㋓ 案を三つ・数で評す(★『焼け』の下命ではない★) ==")
    L.append("repo 根= %s" % repo)
    L.append("刻(始)= %s  刻(終)= %s" % (t0, time.strftime("%Y-%m-%dT%H:%M:%S%z")))
    L.append("歩いた file(S_ISREG)= %d  読めぬ= %d  陽性対照 鳴らぬ= %d" % (nfile, yomenu, naranu))
    for r in trows:
        L.append("    %s %s %s" % (r[0], r[1], r[2]))
    L.append("git index に在る docs/evidence の file= %d 本" % len(tracked))
    L.append("★戸が開いて初めて commit し得る物(disk に在り index に無い)= %d 本 / %d byte★"
             % (len(hairu), sum(r[1] for r in hairu)))
    L.append("")
    for na, sel, modo in an:
        n, b, tb, ki = shime(sel)
        L.append("-- %s --" % na)
        L.append("   本数= %d  byte和= %d (%.2f MB)  束= %d" % (n, b, b / 1e6, tb))
        if ki:
            L.append("   ★入る危険品★: " + "  ".join("%s=%d本" % (k, v) for k, v in sorted(ki.items())))
        else:
            L.append("   ★入る危険品★: 無し(0本 ―― 一本も入らぬゆゑ)")
        L.append("   " + modo)
        L.append("")
    kaku(os.path.join(outdir, "30_an.txt"), "\n".join(L))
    kaku_tsv(os.path.join(outdir, "30_hairu.tsv"),
             [[esc(r[0]), r[1], esc(r[2]), "|".join(sorted(r[3]))] for r in sorted(hairu)],
             ["path(repo 根から)", "byte", "束", "札"])
    sys.stderr.write("30_an rc=0 file=%d 入る=%d 鳴らぬ対照=%d 読めぬ=%d\n"
                     % (nfile, len(hairu), naranu, yomenu))
    return 0


sys.exit(main())
