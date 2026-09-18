# -*- coding: utf-8 -*-
"""★追の便の胴を組む器★ ―― 98 で 326字に落ちた家老便を二便へ截る。
條: 胴は一行・300字は條(送る前に此の器が落とす)・識別子を略さぬ(總監督令 326424)。帳へは触らぬ(98 が已に足した)。"""
import os, sys, subprocess
import importlib.util as iu
ROOT   = "/Users/momizimac/multi-agent-shogun"
BUNDLE = os.path.join(ROOT, "docs/evidence/ashigaru-mac-3_km-175-b1-b3-hantei-teishutsu-to-b2-1wa-20260918")
s_ = iu.spec_from_file_location("kaki_m", os.path.join(BUNDLE, "driver", "00_kaki.py"))
kaki_m = iu.module_from_spec(s_); s_.loader.exec_module(kaki_m); kaku = kaki_m.kaku

TIP  = "1df72e969a1b0b76d5892c7ff283d1ea876d0961"
TREE = "8aafd7350f47b7faa244accdb886f4bb2e0a8af7"
EDA  = "ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917"
DAI  = "895461d57e7ba27ccf9a62ec9305ad2ac57b8b42f11b4764f4bf869ee788179a"

BIN = [
 ("96_kotei_ref_karo_1",
  "karo-mac 殿 專任3 追1/2 ―― ★裁332510㋔の固定 ref を告ぐ。★押して居らぬ★。"
  "枝=%s tip=%s tree=%s。origin/main 6bde7170 に対し SHA で 28 進みだが git cherry は +26/-2 "
  "―― ★之は変更が 28 の意ではない★。" % (EDA, TIP[:12], TREE[:12])),
 ("96_kotei_ref_karo_2",
  "karo-mac 殿 專任3 追2/2 ―― km-175 締め。追の彫り 1df72e96(69本・★束外0★・先住staged959本 不触)。"
  "臺帳 102→148行 sha256=%s。門 追二走 rc=0・控は別名(尾_tsui)で二度 rc=1 鳴。"
  "札は己の手で done へ、km-153 の項へ board_task=eb67444f 据ゑた。★板は書いて居らぬ★。"
  "km-178/km-179 受領、次弾へ入る。" % DAI[:16]),
 ("97_tsui_kansa_gunshi",
  "軍師mac 殿 專任3 追の監査提出(km-175 親裁332152・先の6便 seq332973〜332978 の続)。"
  "追で足した物=㋗の締め。臺帳 102→148行 sha256=%s(歩いた148・mon_行0・除いた0・0byte0)。"
  "門 追二走 rc=0、控は先の走りと★別名(尾_tsui)★で二度 rc=1 に鳴つた。彫り 1df72e96(69本・束外0)。"
  "帳は git 追跡外(check-ignore rc=0/ls-files rc=1・陽性対照 CLAUDE.md は逆)故 git diff 0行は不動の證に非ず。" % DAI[:16]),
 ("98_onore_no_kizu_gunshi",
  "軍師mac 殿 專任3 追2/2 ―― ★追で己が捕へた疵 2 件★。"
  "⑴帳の差分を生の `>` で採り kaki を後から通した(剥がれた行は 0 行であつたが作法違ひ)。"
  "⑵`git ls-files` の rc を `| head` に通して拾ひ head の rc=0 を帳の rc と見誤つた ―― "
  "管を通さず採り直し rc=1 と確かめた(報ずる前に己で捕へた)。"
  "紙は _b2/00_ukeire_kei_ichiwa.md 15166byte/192行 sha256=55900890f5964004(★残116話は次弾★)。"),
]
JOU, warui = 300, []
for na, dou in BIN:
    assert "\n" not in dou, "★胴は一行★ %s" % na
    ji = len(dou)
    kaku(os.path.join(BUNDLE, "_letters", na + ".txt"), dou + "\n")
    print("%-24s %3d 字 %s" % (na, ji, "★300字の條を超えた ―― 截れ★" if ji > JOU else ""))
    if ji > JOU: warui.append((na, ji))
assert not warui, "★%s ―― 送る前に落ちる(條)★" % warui
print("★四便 悉く條を満たす(組む所で数へた ―― 送る前である)★")
