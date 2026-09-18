# -*- coding: utf-8 -*-
"""㋑ 境目の三点(和=閾-1 / 和=閾 / 和=閾+1) と ㋒ 十進か八進か。
㋑ 門の比較は L254 `[ "$total" -ge "$MAXB" ]` = ★以上★。然るに刷る語 L255 は「超」= ★より大きい★。
   ∴ 和=閾 の一点で ★語が實より一つ厳しい側へずれる★ ―― 其の一点を数で示す。
㋒ `[ ]` は 010 を十進で讀む。八進(=8)と十進(=10)で ★出目が分かれる閾★ を選べば決着する。
四札: 刻=冠 / 根=cwd / rc=returncode(管を通さず) / 陽性対照=閾1 の走り(表の末尾に同梱)。"""
import os
import sys
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
T = os.path.getsize(FX)   # byte和(file 一本ゆゑ 和=其の寸法)

def hitohashiri(val):
    out, err, rc = hz.hashiru(["--", FX], env_name="DASUMAE_MAX_BYTES", env_val=val)
    lines = [l for l in err.split("\n") if l.strip()]
    jou5 = " / ".join(l for l in lines if "條⑤" in l) or "-"
    go = "超" if "超" in jou5 else ("未満" if "未満" in jou5 else "-")
    return jou5, go, rc

# ―― ㋑ 境目の三点 ――
saka = []
for na, shikii in [("和=閾-1", T + 1), ("和=閾", T), ("和=閾+1", T - 1)]:
    jou5, go, rc = hitohashiri(str(shikii))
    kikitori = {"超": "閾より★大きい★と読める", "未満": "閾より小さいと読める", "-": "-"}[go]
    saka.append([na, T, shikii, ("和>閾" if T > shikii else ("和=閾" if T == shikii else "和<閾")),
                 go, kikitori, rc, ("鳴つた" if rc else "鳴らず"),
                 ("★語と實が食ひ違ふ★" if (T == shikii and go == "超") else "語と實は合ふ")])
kaku_tsv(os.path.join(BUNDLE, "raw", "20_sakaime_santen.tsv"), saka,
         header=["点", "byte和", "閾", "實の関係", "門が刷る語", "其の語の意味", "rc", "門は", "名と實"])

# ―― ㋒ 十進か八進か ――
# 閾 "0100": 十進=100(和85 は未満→通る) / 八進=64(和85 は以上→鳴る)。出目が分かれる。
ji = []
for val, ju, hachi in [("010", 10, 8), ("0100", 100, 64), ("077", 77, 63)]:
    jou5, go, rc = hitohashiri(val)
    yosou_ju = "鳴る" if T >= ju else "鳴らず"
    yosou_ha = "鳴る" if T >= hachi else "鳴らず"
    jitsu = "鳴つた" if rc else "鳴らず"
    if yosou_ju == yosou_ha:
        han = "分かれぬ(此の値では決せぬ)"
    else:
        han = "★十進★" if jitsu == yosou_ju else "★八進★"
    ji.append([val, ju, hachi, yosou_ju, yosou_ha, jitsu, rc, han, jou5])
kaku_tsv(os.path.join(BUNDLE, "raw", "21_jisshin_ka_hasshin.tsv"), ji,
         header=["与へた閾", "十進と讀めば", "八進と讀めば", "十進の予想", "八進の予想", "實", "rc", "判", "條⑤の行"])

kaku(os.path.join(BUNDLE, "raw", "22_sakaime_chikugo.txt"),
     "as-of %s(UTC)\n根=%s\nbyte和 T=%d(_fx/kiyoi.txt 一本のみ ―― 和の母數は ★argv の file だけ★)\n"
     "陽性対照=閾1 の走り(raw/10 の『正 数(小)』行)で條⑤が現に鳴る事を先に見せた\n"
     "比較器=L254 `[ \"$total\" -ge \"$MAXB\" ]` / 刷る語=L255「超」\n"
     "母數: 境目 %d 点 / 十進八進 %d 値" % (
         datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
         ROOT, T, len(saka), len(ji)))
print("T=%d saka=%d ji=%d" % (T, len(saka), len(ji)))
