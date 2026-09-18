# -*- coding: utf-8 -*-
"""★打ち様十通りを二基底で★ ―― km-159 ㋒(緩い側の実害)を新基底で問ひ直す。
旧基底では 10 通りの内 8 が ★意図(閾50)より緩い既定へ倒れて通つた★。新基底で同じ 10 通りを打ち、
「通つた」が幾つ残るかを数へる。★rc=2 は『通つた』ではない★ ―― 之を判の欄で分ける。
四札: 刻=冠 / 根=cwd / rc=returncode(★管を通さず★) / 陽性対照=「正しく打つ」(両基底とも鳴る筈)。"""
import os
import sys
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); hz = import_module("05_hashiraseru")
kaku, kaku_tsv, mieru = kaki_m.kaku, kaki_m.kaku_tsv, hz.mieru

KYUU = sys.argv[1] if len(sys.argv) > 1 else "scripts/checks/karo_mac_dasumae_gate.sh"
SHIN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BUNDLE, "_fx", "shin_kitei", "karo_mac_dasumae_gate.sh")
assert os.path.exists(SHIN), "新基底が束に無い ―― driver/75 を先に走らせよ: %s" % SHIN
FX = os.path.join(BUNDLE, "_fx", "kiyoi.txt")
T = os.path.getsize(FX)
IKO = "50"   # 意図した閾(和 85 > 50 ゆゑ意図通りなら必ず鳴る)

def hashiru(gate, val):
    e = dict(os.environ)
    e["DASUMAE_MAX_BYTES"] = val
    p = subprocess.run(["bash", gate, "--", FX], env=e,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    err = p.stderr.decode("utf-8", "replace")
    lines = [l for l in err.split("\n") if l.strip()]
    mochiita = "-"
    for l in lines:
        if "條⑤ 寸法" in l and "閾 " in l:
            mochiita = l.split("閾 ")[1].split("未満")[0].split("・")[0].replace("★", "").strip()
    return p.returncode, mochiita

UCHI = [
    ("★陽性対照★ 正しく打つ", "50"),
    ("英字Oと零の取違へ", "5O"),
    ("単位を添へた", "50MB"),
    ("全角数字", "５０"),
    ("下線で桁を区切つた", "5_0"),
    ("指数で書いた", "5e1"),
    ("十六進で書いた", "0x32"),
    ("末尾に空白が付いた", "50 "),
    ("改行が紛れた", "50\n"),
    ("空文字(消し損ね)", ""),
]

rows = []
k_yurui = s_yurui = k_ikou = s_ikou = s_tomari = 0
for na, val in UCHI:
    rc_k, m_k = hashiru(KYUU, val)
    rc_s, m_s = hashiru(SHIN, val)
    han_k = "意図の通り(鳴つた)" if rc_k == 1 else ("★緩い側へ倒れ通つた★" if rc_k == 0 else "止まつた(rc=%d)" % rc_k)
    han_s = "意図の通り(鳴つた)" if rc_s == 1 else ("★緩い側へ倒れ通つた★" if rc_s == 0 else "★止まつた(rc=2 ―― 通して居らぬ)★")
    k_yurui += 1 if rc_k == 0 else 0
    s_yurui += 1 if rc_s == 0 else 0
    k_ikou += 1 if rc_k == 1 else 0
    s_ikou += 1 if rc_s == 1 else 0
    s_tomari += 1 if rc_s == 2 else 0
    rows.append([na, mieru(val), IKO, m_k, rc_k, han_k, m_s, rc_s, han_s,
                 ("★閉ぢた★" if (rc_k == 0 and rc_s != 0) else ("不動" if rc_k == rc_s else "変つた"))])
kaku_tsv(os.path.join(BUNDLE, "raw", "95_uchiyou_futatsu.tsv"), rows,
         header=["打ち様", "与へた値", "意図した閾", "旧が用ゐた閾", "旧 rc", "旧の判",
                 "新が用ゐた閾", "新 rc", "新の判", "基底の間で"])
kaku(os.path.join(BUNDLE, "raw", "96_uchiyou_sengen.txt"),
     "as-of %s(UTC)\n根=%s\nbyte和 T=%d / 意図した閾=%s(和>閾 ゆゑ意図通りなら必ず鳴る)\n"
     "母數=打ち様 %d 通り(★網羅に非ず ―― 現に測つた標本★)\n"
     "旧基底: 緩い側へ倒れ通つた=%d / 意図の通り鳴つた=%d / 止まつた=%d\n"
     "新基底: 緩い側へ倒れ通つた=%d / 意図の通り鳴つた=%d / 止まつた(rc=2)=%d\n"
     "陽性対照=「正しく打つ」 ―― 両基底とも閾50 で現に鳴る(rc=1)\n"
     "此の數が意味せぬ事: ⑴新基底で『止まつた』は ★通した★ のではない(rc=2 は数を出さぬ)。\n"
     "  ⑵打ち様 %d 通りは網羅ではない。⑶『閉ぢた』は此の %d 標本に於てであり、全ての綴りに就いてではない。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT, T, IKO,
        len(UCHI), k_yurui, k_ikou, len(UCHI) - k_yurui - k_ikou,
        s_yurui, s_ikou, s_tomari, len(UCHI), len(UCHI)))
print("旧: 通つた=%d 鳴つた=%d / 新: 通つた=%d 鳴つた=%d 止=%d" % (k_yurui, k_ikou, s_yurui, s_ikou, s_tomari))
