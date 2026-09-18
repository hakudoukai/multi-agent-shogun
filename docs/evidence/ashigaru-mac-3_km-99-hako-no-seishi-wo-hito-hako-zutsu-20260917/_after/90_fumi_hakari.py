# -*- coding: utf-8 -*-
"""便の丈を測る器(㋔ の「300字が條・python3 len で測れ」)。

★宣(先に述べる)★
  ・「字」= python3 の `len(str)`(★codepoint 数★)である。byte でも 書記素 でもない。
    macOS の `awk length()` は byte を返す ∴ 用ゐぬ。`wc -m` は locale 次第 ∴ 用ゐぬ。
  ・測る胴は ★送る物そのもの★(改行を含まぬ一本の文)。器が前置する物(wrapper の宛名等)は
    ★此の器の外★ ゆゑ数へて居らぬ ―― 之を数へぬ事を、此処に宣する。
  ・條 = 300 字以下。超えたら ★書き直す★(切り詰めて送らぬ)。
出目: 91_fumi.json / 92_sai_bun.txt / 93_osame_bun.txt
"""
import io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K

JOU = 300

SAI = (
    "白名簿から外すべきは異名「karo-mac,gunshi-mac」1つのみ。讀み手なき8箱を外すのは誤である。"
    "rc=69は「知らぬ名ゆゑ箱を作らぬ」と告げるが、karoには現に659通が積まれ、"
    "且つ69は正しい路を一字も刷らぬ。路を刷るのはrc=68(_IW_DEAD_LIST)である。"
    "∴ gunshi-mac以外の讀み手なき箱を_IW_DEAD_LISTへ加ふる裁を仰ぐ。生器改修は禁ゆゑ吾は手を觸れて居らぬ。"
)

OSAME = (
    "專任3 km-99 納。紙=docs/evidence/ashigaru-mac-3_km-99-hako-no-seishi-wo-hito-hako-zutsu-20260917/"
    "(門rc=0 母數33本 條①一致)。母數19箱・白名簿18名・paneが足した名0(∴條2⑴は零)。"
    "既読0の箱9、内3は生paneあり。⑶⑷齟齬1=ashigaru-mac-7(+687148秒)。"
    "外すは異名1のみ。讀み手なき8箱はIW_DEAD_LIST行き ∴裁を仰ぐ。軍師mac死箱に付き監査代送を請ふ。宣ETA15:35。"
)


def hakaru(na, s):
    return {
        "名": na,
        "字(len)": len(s),
        "byte(utf-8)": len(s.encode("utf-8")),
        "行": s.count("\n") + 1,
        "條300以下": len(s) <= JOU,
        "残り字": JOU - len(s),
    }


def main():
    d = os.path.dirname(os.path.abspath(__file__))
    K.kaku(os.path.join(d, "92_sai_bun.txt"), SAI)
    K.kaku(os.path.join(d, "93_osame_bun.txt"), OSAME)
    out = {
        "宣_字の定義": "python3 len() = codepoint 数(byte でも書記素でもない)",
        "條": JOU,
        "測": [hakaru("裁を仰ぐ一文(㋔)", SAI), hakaru("納め便(家老mac 宛)", OSAME)],
        "註": "92/93 は kaki 経由ゆゑ末尾に改行 1 つが付く。上の字数は ★改行を含まぬ胴★ の数である。",
    }
    K.kaku(os.path.join(d, "91_fumi.json"), json.dumps(out, ensure_ascii=False, indent=2))
    for m in out["測"]:
        print("%s 字=%d byte=%d 條300=%s 残=%d" % (m["名"], m["字(len)"], m["byte(utf-8)"], m["條300以下"], m["残り字"]))
    return 0 if all(m["條300以下"] for m in out["測"]) else 1


sys.exit(main())
