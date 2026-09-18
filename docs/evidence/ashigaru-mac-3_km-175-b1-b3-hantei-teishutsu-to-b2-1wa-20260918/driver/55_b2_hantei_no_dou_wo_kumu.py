# -*- coding: utf-8 -*-
"""★B2 判定提出と納めの胴を組む器★(km-175 ㋓/㋗) ―― 端末で組まず器で組む。
條: 一行・300 字の條(100 字は註)・★識別子を略さぬ★(總監督令 326424)・胴は kaki を通す。
★初版は 56 が 438 字・95 が 387 字で此の器に落とされた(送る前の對照が現に働いた)★ ∴ B2 を 6 便・納めを 2 便へ割る。
四札: 刻=帳 / 根=本束 / rc=本器 / 對照=字数を送る前に数へ、超えたら ★組んだ所で落ちる★。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku = kaki_m.kaku

SHA_KAMI = "55900890f5964004b9632625d5e5f848cece4a163a29ee36b602e279ee5df213"
SHA_DAI = "b80be88e0a8ad29f4393afeabb4b2cfce68181384b6962f19f656fff5f0b1da5"
SHA_MD = "c9ad47d2e6ab71f2ef0889e1085f43c67cf091009f5648aebc1967e0752c2a00"
SHA_JS = "699c6fae562cc5de8c009f27af24198e23a72aeb6f542acdf78ac89a67efd062"
EP = "frontend/src/features/child-passport/story-engine/episodes"

BIN = [
 ("55_hantei_b2_1",
  "專任3 km-175 B2判定提出(1/6・B1/B3とは別物ゆゑ畳まず・識別子は略さぬ=總監督令326424)。板6caf8ca2。"
  "①受入形の項目=18行(型と★唯一の出所★をfile:lineで名指し・★新たに定めた規則0条=既存門へ委ねた★)。"
  "★板38dcde86の註31と當席18は数へた階が違ふのみ★=再帰乙32−封筒の鍵episode1=31／甲(参照毎)34／宣言のみ6。★差1を丸めず名指した★。"),
 ("56_hantei_b2_2",
  "專任3 B2判定提出(2/6)。②実データ1話=S3-EP1 ―― ★見本を作らず現に書かれた現物を使つた★。"
  "脚本=%s/scripts/S3-EP1.md 2396byte sha256=%s。★製品樹へは一字も書かず★本束_b2/へ同byteで写して通した。" % (EP, SHA_MD)),
 ("57_hantei_b2_3",
  "專任3 B2判定提出(3/6)。写しを製品樹のCLI(npm run validate:episode-md ―― tools/md2scene.tsがprocess.argv[2]から取る故樹外の紙も通る)へ→★rc=0★。"
  "既載の%s/S3-EP1.json 5308byte sha256=%s と★場3/3・行14/14 一致★。" % (EP, SHA_JS)),
 ("58_hantei_b2_4",
  "專任3 B2判定提出(4/6)。陰性対照=%s/scripts/_sample/authoring-sample-broken-cap.md rc=1『at=0のeffect束がcap(3)を超える(実測4)』∴★門は現に噛む★。"
  "★残117話の脚本は此のmacに0本★(出所=Box『てりはキョウリュウおうこく_物語制作』)∴118話目を実データで埋める事は出来ぬ ―― ★不在を黙つて埋めず宣した★。残116話は次弾へ残す。" % EP),
 ("59_hantei_b2_5",
  "專任3 B2判定提出(5/6)。③『保護者解説1:1維持』は★app自身の解決器resolveParentExplanationと既存test %s/__tests__/episodes.test.tsx★で測る=rc=0／26本通(母數26)／skip0・内蔵陽性對照が空表で未解決15を戻す。"
  "己のregexは鍵の在否のみの二の器(isS3S4EntryEmptyが空をnullへ落とす故『鍵在る』は『解決する』に非ず)。話15／鍵15／未解決0／孤児0。" % EP),
 ("60_hantei_b2_6",
  "專任3 B2判定提出(6/6)★己の疵3件(報ずる前に己で捕へた)★。"
  "⑴driver/61のfield regexが行末;を要求したが此の樹のTSに;は無くfield悉く0をrc=0の儘刷つた ⑵負対照の檢出子が行単位でANDを取り現に在る對照を『見えぬ』と刷つた(itの塊で切り直した) "
  "⑶testの出目を一度/tmpへ採つた(證を/tmpに置く禁を踏んだ)→器で束の中へ積み直した。"),
 ("95_osame_karo_1",
  "專任3 km-175 着地(1/2)。宣ETA 2026-09-18T17:30に対し實測2026-09-18T17:36 ―― ★+6分 超過★(丸めず書く)。"
  "㋔B2一話=_b2/00_ukeire_kei_ichiwa.md 15166byte sha256=%s。臺帳102行=歩いた102本(0byte0・宣して除いた紙0)sha256=%s。" % (SHA_KAMI, SHA_DAI)),
 ("95_osame_karo_2",
  "專任3 km-175 着地(2/2)。門二走悉くrc=0・對照は走り毎別名の汚れ紙で二度ともrc=1に鳴つた。"
  "commit=36b88f93(★己の束123本のみ・束外0本★・先住の staged 959本は不触=--onlyで彫りresetは打たず)。臺帳102と commit123の差21=員外_gate/20+臺帳自身1。"
  "監査提出=軍師mac 6便。板の記帳は家老の手ゆゑpath+sha256のみ供す。★残116話は次弾★。"),
]

JOU = 300
warui = []
for na, dou in BIN:
    assert "\n" not in dou, "★胴は一行★ %s" % na
    ji = len(dou)
    kaku(os.path.join(BUNDLE, "_letters", na + ".txt"), dou + "\n")
    print("%-18s %3d 字 %s" % (na, ji, "★條の300字を超えた ―― 截れ★" if ji > JOU else ("(註100字超・條内)" if ji > 100 else "")))
    if ji > JOU:
        warui.append((na, ji))
assert not warui, "★%s ―― 送る前に落ちる(條)★" % warui
print("★%d 通 悉く條内★" % len(BIN))
