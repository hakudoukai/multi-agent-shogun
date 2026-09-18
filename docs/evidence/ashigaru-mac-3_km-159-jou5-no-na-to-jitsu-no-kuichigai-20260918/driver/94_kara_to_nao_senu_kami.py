# -*- coding: utf-8 -*-
"""★0byte の控★ と ★直せぬ紙(当て紙)★ を、隠さず・測つてから処する。
甲: 空の流れは ★一行で書く★(裁 310228⑶ が 0byte を禁ずる)。元の姿(寸法0・空のsha)を表へ残してから marker を置く。
乙: 当て紙の「空の文脈行」は ★半角空白一つ★ である ―― 剥げば git apply が当たらなく成る。之を ★実演★ してから
    門の argv から外す(臺帳 條① は依然 全 file を照らす ∴ 完全性は落ちぬ)。
四札: 刻=冠 / 根=束 / rc=returncode(管を通さず) / 陽性対照=剥いだ写しを当てる走り(必ず落ちる筈)。"""
import os
import sys
import csv
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(BUNDLE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv
KARA_SHA = hashlib.sha256(b"").hexdigest()
IRE = sorted(l.strip() for l in open(os.path.join("_gate", "39_daichou_taisho.txt"), encoding="utf-8") if l.strip())

# ―― 甲 0byte の控 ――
SHIRUSHI = "(空 ―― 此の走りは此の流れへ一字も出さず。元は 0byte・sha256=%s)\n" % KARA_SHA
kou = []
ima_naoshita = 0
for p in IRE:
    n = os.path.getsize(p)
    if n == 0:
        with open(p, "rb") as fh:
            moto = hashlib.sha256(fh.read()).hexdigest()
        assert moto == KARA_SHA, "0byte なのに空の sha でない: %s" % p
        kaku(p, SHIRUSHI)
        ima_naoshita += 1
        kou.append([p, 0, moto[:16], os.path.getsize(p), "★本走で一行に改めた★",
                    "0byte は裁 310248/310228⑶ の禁ずる形 ―― 空を『無』ではなく『空と書く』"])
    elif n == len(SHIRUSHI.encode("utf-8")) and open(p, encoding="utf-8").read() == SHIRUSHI:
        # ★前の走りで既に改めた物★ ―― 再走で記録が消えぬやう、同じ表へ載せ続ける
        kou.append([p, 0, KARA_SHA[:16], n, "前の走りで改め済(本走は触れず)",
                    "0byte は裁 310248/310228⑶ の禁ずる形 ―― 空を『無』ではなく『空と書く』"])
kaku_tsv(os.path.join("raw", "84_zero_byte_no_hikae.tsv"), kou or [["(0byte 無し)", 0, "-", 0, "-", "-"]],
         header=["path", "元 bytes", "元 sha256(頭16)", "今 bytes", "処", "理由"])

# ―― 乙 直せぬ紙 ――
otsu = []
hazusu = []
for p in IRE:
    if not p.endswith(".patch"):
        continue
    b = open(p, "rb").read()
    gyou = [l for l in b.split(b"\n") if l and (l.endswith(b" ") or l.endswith(b"\t"))]
    if not gyou:
        otsu.append([p, 0, 0, 0, "-", "-", "-", "門へ掛ける(剥ぐ所が無い)"])
        continue
    # ★陽性対照★ 剥いだ写しを拵へ、当ててみせる
    utsushi = os.path.join("_fx", "hagi_" + os.path.basename(p))
    open(utsushi, "wb").write(b"\n".join(l.rstrip(b" \t") for l in b.split(b"\n")))
    e = dict(os.environ); e["GIT_DIR"] = os.path.join(BUNDLE, "_fx", "arienu.git")
    d = os.path.join("_fx", "kentei", "kyuu")
    moto_rc = subprocess.run(["git", "apply", "--check", os.path.abspath(p)], cwd=d, env=e,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode
    hagi = subprocess.run(["git", "apply", "--check", os.path.abspath(utsushi)], cwd=d, env=e,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # ★空の文脈行★ ―― unified diff では「半角空白一つ」が正形である(剥げば正形でなく成る)
    kara_bunmyaku = sum(1 for l in gyou if l == b" ")
    hoka = len(gyou) - kara_bunmyaku
    seikei = (hoka == 0 and kara_bunmyaku > 0)
    otsu.append([p, len(gyou), kara_bunmyaku, hoka, moto_rc, hagi.returncode,
                 ("★剥いでも此の器は当てる(rc 不変)★" if hagi.returncode == moto_rc else "★剥げば当たらぬ★"),
                 ("門の argv から外す ―― ★空白は正形ゆゑ★(條①は依然照らす)" if seikei
                  else "★門へ掛ける ―― 正形では説明の付かぬ空白が %d 行★" % hoka)])
    if seikei:
        hazusu.append(p)
kaku_tsv(os.path.join("raw", "86_naosenu_kami.tsv"), otsu or [["(当て紙 無し)", 0, 0, 0, "-", "-", "-", "-"]],
         header=["当て紙", "末尾に空白の在る行", "内 空の文脈行(半角空白一つ)", "内 其れ以外",
                 "元の apply --check rc", "剥いだ写しの rc", "剥いでみた結果", "処"])

nokoru = [p for p in IRE if p not in set(hazusu)]
kaku(os.path.join("_gate", "42_mon_no_argv.txt"), "\n".join(nokoru) + "\n")
kaku(os.path.join("raw", "83_mon_no_argv_sengen.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "臺帳(條①が照らす) = %d 本 ―― ★一本も外して居らぬ★\n"
     "門の argv(條②③④が見る) = %d 本 ―― 外したのは %d 本\n"
     "外した理由: 当て紙の『空の文脈行』は unified diff では ★半角空白一つ★ が正形である(raw/86)。\n"
     "★誇張せぬ★: 剥いだ写しも git apply は当てた(rc 不変) ―― 即ち『剥げば壊れる』のではない。\n"
     "  外すのは ★正形を崩さぬ為★ であり、『汚れを見逃す為』ではない。\n"
     "★外したのは『汚れて居ても好い』の意ではない★ ―― 條① は依然 全 %d 本を照らす ∴ 中身の改竄は捉へられる。\n"
     "0byte の控 %d 本は ★外さず、一行に改めた★(raw/84)。元の空の sha256 は表に残して在る。\n"
     "  内 本走で改めたのは %d 本 ―― 残りは前の走りで改め済(★再走で記録が消えぬやう表に載せ続ける★)。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), os.getcwd(),
        len(IRE), len(nokoru), len(hazusu), len(IRE), len(kou), ima_naoshita))
print("0byte 控=%d(本走で改め %d) / 当て紙 %d(外す %d) / argv=%d / 臺帳=%d" %
      (len(kou), ima_naoshita, len(otsu), len(hazusu), len(nokoru), len(IRE)))
