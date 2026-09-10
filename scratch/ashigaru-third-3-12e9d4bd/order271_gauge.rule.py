# -*- coding: utf-8 -*-
# order271 検算器 ―― 拡張 patch の 甲 hunk を取り出し、合成値(gousei)の selftest を焚く。
# 註: 本器は「常設器」ではない。常設器は ~/bin/cdrive_autoguard.sh の拡張(patch)であり
#     本器は其の patch を検算する為だけの一回限りの器である(新常設器は作つて居らぬ)。
# 註: mode=gousei の行は 合成値 であり 実測ではない(陽性対照・order128 の型)。
import io, os, sys, hashlib, subprocess
TAB = chr(9)
P = "scratch/ashigaru-third-3-12e9d4bd/order271_extend.patch"
raw = io.open(P, "rb").read()
print("patch sha16 =", hashlib.sha256(raw).hexdigest()[:16], " B =", len(raw))
lines = raw.decode("utf-8").split(chr(10))

# 甲 hunk = 一本目の @@ から 二本目の diff --git まで
i0 = None; i1 = len(lines)
for i, x in enumerate(lines):
    if x.startswith("@@") and i0 is None:
        i0 = i
    elif x.startswith("diff --git") and i0 is not None:
        i1 = i; break
blk = [x[1:] for x in lines[i0+1:i1] if x.startswith("+")]
print("kou hunk no + gyou =", len(blk))

# 門一: 禁の command が器に無い事
KIN = ["Optimize-VHD", "diskpart", "wsl --shutdown", "rm -rf", "Compact-VHD"]
for k in KIN:
    n = sum(1 for x in blk if k in x)
    print("kinshi", k, "=", n)
    assert n == 0, k

# 門二: 二つの註が現に在る事
need = [u"vhdx が現に無い", u"実測ではない", u"none"]
for w in need:
    assert any(w in x for x in blk), w
print("chuu 3 hon = genni aru")

# 門三: 合成値の selftest を焚く(標準入力へ直流・一時 file 0)
src = chr(10).join(blk) + chr(10)
r = subprocess.run(["bash", "-s", "--", "--gauge-selftest"],
                   input=src.encode("utf-8"),
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("selftest rc =", r.returncode)
err = r.stderr.decode("utf-8", "replace").strip()
if err:
    print("stderr =", err[:400])
out = r.stdout.decode("utf-8").split(chr(10))
out = [x for x in out if x != ""]
for x in out:
    print("out| " + x.replace(TAB, "<TAB>"))
assert r.returncode == 0
assert len(out) == 2, len(out)
assert u"実測ではない" in out[0]
f = out[1].split(TAB)
print("retsu suu =", len(f))
assert len(f) == 14, len(f)
assert f[0] == "gousei", f[0]
assert f[12] == "none", f[12]
assert f[13] == "", repr(f[13])

# 門四: 実測の TSV へ一字も書いて居らぬ事
T = "/home/hakudoukai/.local/share/dentalbi/cdrive_gauge.tsv"
print("jissoku TSV =", ("genni aru" if os.path.exists(T) else "genni nashi"))
assert not os.path.exists(T)

# 門五: 頭の欄名の数が 14 である事
hdr = [x for x in blk if x.find("#mode") >= 0]
assert len(hdr) == 1, len(hdr)
h = hdr[0]
h = h[h.find("#mode"):]
h = h[:h.rfind('"')]
print("hedda ran suu =", h.count("GAUGE_TAB") + 1)
assert h.count("GAUGE_TAB") + 1 == 14

print("KEKKA: mon itsutsu = genni aru (subete tootta)")
