# -*- coding: utf-8 -*-
"""㋓ byte和の母數 ―― ★何を足し、何を足さぬか★ を、読むのではなく ★走らせて★ 決める。
実装(L244-253)は `for f in "${files[@]}"` ―― 即ち ★argv の file だけ★ を足す。
臺帳は第一引数(manifest)として渡る限り files[] に入らぬ ∴ ★和の外★。
之を三つの走りで示す: 甲 台帳無し / 乙 台帳を第一引数へ / 丙 台帳を ★file としても★ 渡す。
四札: 刻=冠 / 根=cwd / rc=returncode(管を通さず) / 陽性対照=丙(足せば和が増える事を見せる)。"""
import os
import sys
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); hz = import_module("05_hashiraseru")
kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

FX = os.path.join(BUNDLE, "_fx", "kiyoi.txt")
FXREL = os.path.relpath(FX, ROOT)
T = os.path.getsize(FX)
b = open(FX, "rb").read()
sha = hashlib.sha256(b).hexdigest()
DAI = os.path.join(BUNDLE, "_fx", "tame_no_daichou.txt")
with open(DAI, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("# repo=%s\n# 之は㋓を測る為の ★試しの臺帳★ であり、本弾の納めの臺帳では無い。\n"
             "path=%s sha256=%s bytes=%d lines=%d\n#\n件数=1\n"
             % (ROOT, FXREL, sha, T, b.decode("utf-8").count("\n")))
M = os.path.getsize(DAI)

def hitohashiri(args):
    out, err, rc = hz.hashiru(args, env_name="DASUMAE_MAX_BYTES", env_val="10485760")
    lines = [l for l in err.split("\n") if l.strip()]
    jou5 = " / ".join(l for l in lines if "條⑤ 寸法" in l) or "-"
    wa = "-"
    if "byte和 " in jou5:
        wa = jou5.split("byte和 ")[1].split("(")[0].strip()
    jou1 = " / ".join(l for l in lines if "條①" in l) or "-"
    return wa, jou1, rc

rows = []
for na, args, yosou in [
        ("甲 臺帳無し(--)と file 一本", ["--", FX], T),
        ("乙 臺帳を第一引数へ・file 一本", [DAI, FX], T),
        ("丙 ★陽性対照★ 臺帳を file としても渡す", ["--", FX, DAI], T + M)]:
    wa, jou1, rc = hitohashiri(args)
    atari = "合ふ" if wa == str(yosou) else "★合はぬ★"
    rows.append([na, " ".join(os.path.basename(a) if os.sep in a else a for a in args),
                 yosou, wa, atari, rc, jou1[:60]])
kaku_tsv(os.path.join(BUNDLE, "raw", "40_bogen.tsv"), rows,
         header=["走り", "渡した引数", "予想した和", "門が刷つた和", "予想と實", "rc", "條①"])

kaku(os.path.join(BUNDLE, "raw", "41_bogen_sengen.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "★和の母數(本弾が宣する定義)★\n"
     "  足す = 門の argv のうち ★第二引数以降の file★ (実装 L244-253 の files[])。寸法は safe_size(=stat・開かぬ)。\n"
     "  足さぬ = ⑴第一引数へ渡した臺帳 ⑵argv に無い file(束の中に在つても) ⑶dir 其の物 ⑷器自身(門・driver)。\n"
     "  ∴ 『byte和』は ★束の大きさ★ では無く ★其の走りで名指した file の和★ である。\n"
     "_fx/kiyoi.txt = %d byte / _fx/tame_no_daichou.txt = %d byte / 二つの和 = %d byte\n"
     "母數 = 走り 3 本(甲乙丙)\n"
     "此の數が意味せぬ事: 束全体の byte 数ではない。臺帳を file としても渡せば(丙)和に入る ―― \n"
     "  即ち『臺帳は和の外』は ★渡し方の函数★ であつて、器の不変則ではない。"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ROOT, T, M, T + M))
print("T=%d M=%d" % (T, M))
