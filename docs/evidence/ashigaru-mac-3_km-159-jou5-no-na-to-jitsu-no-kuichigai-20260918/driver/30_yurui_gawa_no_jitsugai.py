# -*- coding: utf-8 -*-
"""㋐の実害 ―― 「既定へ倒す」が ★緩い側★ である事を、数で言ふ。
立て方: 打つ者は ★厳しい閾(50)★ を掛けたつもりで居る。然るに綴りを誤ると門は既定 10485760 へ倒れ、
        ★意図なら止まつた束が通る★。倒した事を刷つては居るが、rc は 0 であり ★通行は許される★。
∴ fail-closed の名に反す ―― 真に閉ぢるなら rc!=0 で止めるか、既定より ★厳しい側★ へ倒すかである。
四札: 刻=冠 / 根=cwd / rc=returncode(管を通さず) / 陽性対照=「意図した閾 50 を正しく打つた走り」。"""
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
T = os.path.getsize(FX)
ITO = 50  # 打つ者が掛けたつもりの厳しい閾(和 85 ゆゑ 意図通りなら★鳴る★)

def hitohashiri(val):
    out, err, rc = hz.hashiru(["--", FX], env_name="DASUMAE_MAX_BYTES", env_val=val)
    lines = [l for l in err.split("\n") if l.strip()]
    jou5 = " / ".join(l for l in lines if "條⑤" in l) or "-"
    tsukatta = "-"
    for l in lines:
        if "條⑤ 寸法" in l:
            if "閾 " in l:
                tsukatta = l.split("閾 ")[1].split("未満")[0].split("・")[0].strip()
    taoshita = "刷つた" if any("既定" in l for l in lines) else "刷らず"
    return jou5, tsukatta, taoshita, rc

rows = []
KEI = [("★陽性対照★ 正しく打つ", "50"),
       ("英字Oと零の取違へ", "5O"),
       ("単位を添へた", "50MB"),
       ("全角数字", "５０"),
       ("下線で桁を区切つた", "5_0"),
       ("指数で書いた", "5e1"),
       ("十六進で書いた", "0x32"),
       ("末尾に空白が付いた", "50 "),
       ("改行が紛れた", "50\n"),
       ("空文字(消し損ね)", "")]
for na, val in KEI:
    jou5, tsukatta, taoshita, rc = hitohashiri(val)
    # ★器の疵(己で踏み、己で直した)★ ―― 初版は「鳴る」(予想)と「鳴つた」(實)を
    #   ★字面で★ 較べて居た ∴ 悉く不一致と成り、陽性対照までが「厳しい側へ倒れた」と出た。
    #   ∴ 較べるのは ★真偽★ であつて語ではない。語は人の為、判は真偽で採る。
    ito_b = (T >= ITO)
    jitsu_b = (rc != 0)
    ito_nara = "鳴る" if ito_b else "鳴らず"
    jitsu = "鳴つた" if jitsu_b else "鳴らず"
    if jitsu_b == ito_b:
        han = "意図の通り"
    elif not jitsu_b:
        han = "★緩い側へ倒れた(通つた)★"
    else:
        han = "厳しい側へ倒れた"
    rows.append([na, hz.mieru(val), ITO, tsukatta, ito_nara, jitsu, rc, taoshita, han])

kaku_tsv(os.path.join(BUNDLE, "raw", "30_yurui_gawa.tsv"), rows,
         header=["打ち様", "与へた値", "意図した閾", "門が用ゐた閾", "意図通りなら", "實", "rc", "倒した事を", "判"])

yurui = sum(1 for r in rows if "緩い側" in r[-1])
kaku(os.path.join(BUNDLE, "raw", "31_yurui_gawa_shudai.txt"),
     "as-of %s(UTC)\n根=%s\nbyte和=%d / 意図した閾=%d(和>閾 ゆゑ意図通りなら必ず鳴る)\n"
     "母數=打ち様 %d 通り。内 ★緩い側へ倒れた=%d★ / 意図の通り=%d\n"
     "陽性対照=「正しく打つ」の行 ―― 閾 50 で現に鳴る(rc=1)事を先に見せた\n"
     "此の數が意味せぬ事: ⑴門が『黙つて』倒れたとは言つて居らぬ(倒した事は stderr へ刷つて居る)。\n"
     "  ⑵打ち様 %d 通りは網羅に非ず ―― 「比較器が扱へぬ綴り」の全体ではなく、現に測つた標本である。\n"
     "  ⑶既定 10485760 が不当だとは言つて居らぬ。言ふのは ★其れが fail-closed の名に値せぬ★ 事のみ。"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        ROOT, T, ITO, len(rows), yurui, len(rows) - yurui, len(rows)))
print("母數=%d 緩い側=%d" % (len(rows), yurui))
