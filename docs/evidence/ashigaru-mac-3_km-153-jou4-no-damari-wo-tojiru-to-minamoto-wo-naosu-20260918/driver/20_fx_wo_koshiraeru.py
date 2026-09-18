# -*- coding: utf-8 -*-
"""陽性対照の紙(fx)を byte で拵へる ―― 條④の口を一つづつ叩く為の紙。
★之等は門を鳴らす為に在る紙(陽性対照)ゆゑ、門の argv からは宣して除く(第四の道)。
臺帳には載せる ―― 「除いた」は「歩いて居らぬ」に非ず。★
km-150 の fx 01/02/03/04/05 を継ぎ、06(U+3000 一字の行)07(素の末尾空行)を足す。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from importlib import import_module

K = import_module("00_kaki")
TABA = os.path.abspath(os.path.join(HERE, ".."))
FX = os.path.join(TABA, "raw", "fx")

# (名, bytes, 狙ひ, 旧基底で鳴るべきか(當席の見立て ―― 測る前の宣))
KAMI = [
    ("01_zero.txt", b"", "0byte 其の物(km-150 fx01 と同形)", "鳴る(條④ 0byte の口)"),
    ("02_zero_kaimei.md", b"", "★名を変へただけ★の 0byte(陽性対照 ―― 名は効かぬ事の證)", "鳴る"),
    ("03_kaki_kara.txt", (K.KARA + "\n").encode("utf-8"), "★源を直した形★=空なら一行(裁 seq310228⑶)", "鳴らぬ"),
    ("04_kiyoi.txt", b"a\n", "負対照 ―― 清い紙", "鳴らぬ"),
    ("05_crlf_kuugyou.txt", b"a\r\n\r\n", "CRLF+末尾空行 ―― ★末尾2字=0d0a★(當席が km-150 で掘つた黙り)", "條④は黙り 條③のみ鳴る"),
    ("06_u3000_kuugyou.txt", b"a\n\xe3\x80\x80\n", "末尾行が U+3000 一字のみ(不可視の空行)", "黙る(見立て)"),
    ("07_sunao_kuugyou.txt", b"a\n\n", "素の末尾空行 ―― 末尾2字=0a0a", "鳴る(旧の口に当る)"),
]


def main():
    os.makedirs(FX, exist_ok=True)
    rows = []
    for na, b, nerai, mitate in KAMI:
        p = os.path.join(FX, na)
        with open(p, "wb") as fh:
            fh.write(b)
        last2 = b[-2:].hex() if len(b) >= 2 else (b.hex() if b else "(無)")
        rows.append((na, str(len(b)), last2, str(b.count(b"\n")), nerai, mitate))
    K.kaku_tsv(os.path.join(TABA, "raw", "20_fx.tsv"), rows,
               header=("fx 名", "bytes", "末尾2字(hex)", "LF数", "狙ひ", "★測る前の見立て★(旧基底)"))
    K.kaku(os.path.join(TABA, "raw", "20_fx.sengen.txt"),
           "★宣★ raw/fx/ の 7本は ★門を鳴らす為に在る紙(陽性対照)★ である。\n"
           "∴ 門の argv からは ★宣して除く★(km-147/150 と同じ第四の道 ―― 直せぬ紙に限る)。\n"
           "★臺帳には 7本 悉く載せる★ ―― 條① は現に之等へ当たる。「除いた」は「歩いて居らぬ」に非ず。\n"
           "此の宣が意味せぬ事: 除いた事は「門が之等を通した」の意ではない ―― 門は之等を ★見て居らぬ★。")
    print("拵へた=%d本" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
