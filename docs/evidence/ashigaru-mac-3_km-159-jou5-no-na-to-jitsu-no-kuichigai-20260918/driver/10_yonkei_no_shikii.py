# -*- coding: utf-8 -*-
"""㋐ 閾の四形 ―― 門が何を刷り、rc が何であるかを ★並べて★ 見る。
問: 「既定へ倒す(fail-closed)」と刷るが、既定 10485760 へ倒れるは ★緩い側★ ではないか。
四札: 刻=各表の冠 / 根=cwd / rc=subprocess の returncode(管を通さず) / 陽性対照=閾1 の走り。"""
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)

from importlib import import_module
kaki_m = import_module("00_kaki")
hz = import_module("05_hashiraseru")
kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

FX = os.path.join(BUNDLE, "_fx", "kiyoi.txt")
with open(FX, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("清き紙 ―― 條②③④を満たす(末尾空白0・CR0・EOF改行丁度1)。\n")
FXB = os.path.getsize(FX)

KEI = [
    ("正 数(既定と同じ)", "10485760"),
    ("正 数(小・★陽性対照★)", "1"),
    ("形0 未設定", None),
    ("形1 非数", "abc"),
    ("形2 空文字", ""),
    ("形3 空白のみ(半角)", "   "),
    ("形3' 空白のみ(全角U+3000)", "　"),
    ("形4 2^63-1(比較器の上限内)", "9223372036854775807"),
    ("形4' 2^63(比較器が倒れる)", "9223372036854775808"),
    ("形4'' 2^64以上", "99999999999999999999"),
    ("参考 010(八進に非ず十進)", "010"),
]

rows, chiku = [], []
for na, val in KEI:
    out, err, rc = hz.hashiru(["--", FX], env_name="DASUMAE_MAX_BYTES", env_val=val)
    lines = [l for l in err.split("\n") if l.strip()]
    shikii = " / ".join(l for l in lines if "閾 DASUMAE_MAX_BYTES" in l) or "-"
    jou5 = " / ".join(l for l in lines if "條⑤" in l) or "-"
    ketsu = " / ".join(l for l in lines if "出す前 門" in l) or "-"
    tsukatta = "-"
    for l in lines:
        if "條⑤ 寸法" in l and "閾 " in l:
            tsukatta = l.split("閾 ")[1].split("未満")[0].split("・")[0].strip()
    nari = "鳴つた" if rc != 0 else "鳴らず"
    rows.append([na, hz.mieru(val), shikii, jou5, ketsu, rc, nari, tsukatta])
    chiku.append("### %s  与へた値=%s\n[stderr 逐語]\n%s\n[stdout 逐語]\n%s\nrc: %d" % (
        na, hz.mieru(val), err.rstrip("\n") or "(空)", out.rstrip("\n") or "(空)", rc))

kaku_tsv(os.path.join(BUNDLE, "raw", "10_yonkei_no_shikii.tsv"), rows,
         header=["形", "与へた値", "閾の報せ行", "條⑤の行", "結語", "rc", "門は", "條⑤が実際に用ゐた閾"])
kaku(os.path.join(BUNDLE, "raw", "11_yonkei_chikugo.txt"),
     "as-of %s(UTC)\n根=%s\n對象=%s (sha256 は臺帳に在り)\n陽性対照=「正 数(小)」の走り ―― 閾1 で條⑤が鳴る事を先に見せる\n母數=形 %d\n\n%s"
     % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        "scripts/checks/karo_mac_dasumae_gate.sh", len(KEI), "\n\n".join(chiku)))
print("fixture_bytes=%d" % FXB)
print("形の母數=%d" % len(rows))
