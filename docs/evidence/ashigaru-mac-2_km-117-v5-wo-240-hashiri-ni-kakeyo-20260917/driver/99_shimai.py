#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-117 仕舞ひ ―― ★紙が己について書けぬ数★ を器に書かせる。
出 = raw/99_shimai.txt(★此の器と此の出目は 臺帳が凍つた後に生れる ∴ 員外である★)
"""
import hashlib, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(B)
L = []
A = L.append
A("# km-117 仕舞ひ ―― 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"))
A("# 歩き根 = " + B)
A("")
A("== 臺帳 manifest.txt ==")
mb = open("manifest.txt", "rb").read()
rows = [l for l in mb.decode("utf-8").split("\n") if l.startswith("path=")]
A("行(LF数)\t%d" % mb.count(b"\n"))
A("path= の行\t%d" % len(rows))
A("註(# 始まり)の行\t%d" % len([l for l in mb.decode("utf-8").split("\n") if l.startswith("#")]))
A("sha256\t" + hashlib.sha256(mb).hexdigest())
A("bytes\t%d" % len(mb))
A("★臺帳の中の mon_ を含む行(自数)\t%d★  ―― 門の控は臺帳へ入れて居らぬ"
  % len([l for l in rows if "mon_" in l]))
A("")
A("== 門の走り(★控は走り毎に別名★・古い走りも消さずに残す) ==")
errs = sorted(f for f in os.listdir(".") if f.startswith("mon_") and f.endswith(".err"))
tsuu = []
for h in errs:
    base = h[:-4]
    err = open(base + ".err", encoding="utf-8").read()
    rc = 0 if "★出す前 門 通。出してよい。★" in err else 1
    if rc == 0:
        tsuu.append(base)
    A("控\t%s\trc=%d\terr行=%d\tout行=%d" % (
        base, rc, err.count("\n"),
        open(base + ".out", encoding="utf-8").read().count("\n")))
A("★通つた走り=%d / 落ちた走り=%d / 計=%d★" % (len(tsuu), len(errs) - len(tsuu), len(errs)))
A("★納めの二走(受取条件⑷)★ = %s" % " / ".join(tsuu[-2:]))
A("★二つの控名は違ふか★ = %s" % ("違ふ" if len(set(tsuu[-2:])) == 2 else "★同じ ―― 條を満たさぬ★"))
for base in tsuu[-2:]:
    A("-- %s の條 --" % base)
    for ln in open(base + ".err", encoding="utf-8").read().split("\n"):
        if ln.startswith("條"):
            A("\t" + ln)
A("★門の出目は悉く stderr ∴ .out に判定は無い★")
A("")
A("== 員外(★臺帳に載せたが門へ渡さなんだ物★・9本) ==")
ING = [
    ("driver/__pycache__/kaki.cpython-314.pyc", "python が生む binary。條②2行・條③CR7行・條④EOF改行0 に鳴る"),
    ("raw/10_menseki.err", "0byte ―― 條④が 0byte に鳴る(器は一行も吐かなんだ)"),
    ("raw/10_menseki.stderr", "0byte ―― 同上"),
    ("raw/13_otori.stderr", "0byte ―― 同上"),
    ("raw/30_genbutsu.err", "0byte ―― 同上"),
    ("raw/31_genbutsu.stderr", "0byte ―― 同上"),
    ("raw/32_otsu.stderr", "0byte ―― 同上"),
    ("raw/31_daini_for.tsv", "★NUL を含む ∴ 條②が濡れ衣を着せる(下の實測)★"),
    ("raw/40_naoshi.diff", "★unified diff の文脈行は「空白一字の行」∴ 末尾空白 2 行が要る(除けば git apply が落ちる)★"),
]
for p, why in ING:
    st = os.stat(p)
    A("%s\tbytes=%d\t%s" % (p, st.st_size, why))
A("")
A("== 門の控 其れ自身(★臺帳にも門にも載らぬ★) ==")
for f in sorted(os.listdir(".")):
    if f.startswith("mon_"):
        A("%s\tbytes=%d" % (f, os.stat(f).st_size))
A("註: mon_ichi_20260917_195616.* は ★落ちた一走り目★(rc=1)。員外を切る前の走り。消さずに残す。")
A("")
A("== 此の器と此の出目(★臺帳が凍つた後に生れた物★) ==")
for f in ("driver/99_shimai.py", "raw/99_shimai.txt",
          "driver/__pycache__/99_shimai.cpython-314.pyc"):
    A(f + "\t―― 臺帳に無い(★己を数へる器は己を臺帳へ入れられぬ★)")
A("")
A("== raw/31_daini_for.tsv の 條② 濡れ衣 ―― 陽性/陰性対照付 ==")
b = open("raw/31_daini_for.tsv", "rb").read()
segs = b.split(b"\n")
A("byte で行末が空白/TAB の行\t%d\t(python・母數 %d 行)" % (
    len([1 for l in segs if l.endswith(b" ") or l.endswith(b"\t")]), len(segs)))
r = subprocess.run(["bash", "-c",
                    "grep -cE $'[ \\t]+\\r?$' raw/31_daini_for.tsv"],
                   capture_output=True, text=True)
A("門と同じ形の grep(BSD)\t%s\t(rc=%d)" % (r.stdout.strip(), r.returncode))
A("NUL を含む行\t%d" % len([1 for l in segs if b"\x00" in l]))
A("★因★ = ★空白/TAB の直後に NUL が来ると鳴る★(下の六対照で当てた)。字の直後の NUL では鳴らぬ ∴「NUL が在るから」ではない")
for nm, byt, expect in (("陽性対照(真に末尾空白)", b"abc \n", 1),
                        ("陰性対照(清い行)", b"abc\n", 0),
                        ("陰性対照(TAB 在るが行末でない)", b"abc\tdef\tghi\n", 0),
                        ("★陽性対照(TAB の直後に NUL)★", b"abc\tdef\t\x00ghi\n", 1),
                        ("★陽性対照(空白の直後に NUL)★", b"abc def \x00ghi\n", 1),
                        ("★陰性対照(字の直後に NUL)★", b"abc\tdef\x00ghi\n", 0)):
    p = "/private/tmp/km117_shimai_probe.txt"
    open(p, "wb").write(byt)
    rr = subprocess.run(["bash", "-c", "grep -cE $'[ \\t]+\\r?$' " + p],
                        capture_output=True, text=True)
    A("%s\t出目=%s\trc=%d\t期待=%d" % (nm, rr.stdout.strip(), rr.returncode, expect))
    os.unlink(p)
A("")
A("== 此の数が意味せぬ事 ==")
A("・「員外 9 本」は「9 本が疵物」ではない ―― ★門の條が其の形の file に当たらぬ★だけである。")
A("  9 本悉く 條①(臺帳と disk の一致)は通つて居る(母數 68 の内)。")
A("・「門 rc=0 二度」は「紙の中身が正しい」を言はぬ ―― ★出す前の五條を満たす★の一事のみ。")
A("・「臺帳 68 行」は束の file 総数ではない ―― 此の器・此の出目・門の控 6 本は後から生れた。")
mon_n = len([f for f in os.listdir(".") if f.startswith("mon_")])
A("  ★歩き直せば本数は増える。★ 増分 = 器1 + 出目1 + 其の .pyc 1 + 門の控 %d 本 = %d 本(此の刻)。"
  % (mon_n, 3 + mon_n))
A("・「mon_ 行 0」は grep rc=1(不一致)で得た零である。rc=2 なら測れて居らぬ。")
K.kaku("raw/99_shimai.txt", "\n".join(L))
print("書いた raw/99_shimai.txt 行=%d" % len(L))
