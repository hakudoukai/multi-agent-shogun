# -*- coding: utf-8 -*-
"""★己の札を己の手で翻す器★ ―― km-175 を done へ、km-153 の項へ board_task を据ゑる

★此の器が守る事★
  ⑴ 錨は★逐語★。行番号を一つも用ひぬ(行番号は版で動く)。
  ⑵ 当てる前に ★当たりが丁度1箇所★ である事を assert する(0 でも 2 でも落ちる)。
  ⑶ 触るのは ★己の帳 queue/tasks/ashigaru-mac-3.yaml のみ★。他席の帳・板・共有樹の index は触らぬ。
  ⑷ 家老が書いた行を ★消さぬ★ ―― ban_id_b1/b3/b2 は旧形(裁332455)として残し、註を添へて board_task を足す。
  ⑸ 前後の写しと差分を束へ置く(★/tmp に證を置かぬ★)。生の text は悉く kaki を通す。
  ⑹ 書いた後 ★yaml として読み直せるか★ を測る(safe_load)。読めねば戻す。
"""
import io, os, re, subprocess, sys, datetime, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _iu
_s = _iu.spec_from_file_location("kaki_m", os.path.join(os.path.dirname(os.path.abspath(__file__)), "00_kaki.py"))
kaki_m = _iu.module_from_spec(_s); _s.loader.exec_module(kaki_m)
kaku = kaki_m.kaku

ROOT   = "/Users/momizimac/multi-agent-shogun"
BUNDLE = os.path.join(ROOT, "docs/evidence/ashigaru-mac-3_km-175-b1-b3-hantei-teishutsu-to-b2-1wa-20260918")
CHOU   = os.path.join(ROOT, "queue/tasks/ashigaru-mac-3.yaml")
F      = os.path.join(BUNDLE, "_fuda")

koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
koku = koku[:-2] + koku[-2:]

moto = io.open(CHOU, encoding="utf-8").read()
kaku(os.path.join(F, "00_chou_mae.yaml"), moto)
print("★前★ %d byte / %d 行" % (len(moto.encode("utf-8")), moto.count("\n")))

# ───────── 当て紙 其の一 ―― km-175 を done へ ─────────
MAE1 = """tsugi_no_tama_175_20260918T1336:
  task_id: km-175-b1-b3-no-chakuchi-wo-gunshi-he-hantei-teishutsu-shi-b2-no-1wa-wo-kiru-20260918
  status: assigned
"""
ATO1 = """tsugi_no_tama_175_20260918T1336:
  task_id: km-175-b1-b3-no-chakuchi-wo-gunshi-he-hantei-teishutsu-shi-b2-no-1wa-wo-kiru-20260918
  status: done
  completed_at: %s
  completed_at_no_ne: 束内 最新 mtime(_letters/95_osame_karo_2.send.rc ―― 納め二便の着弾)=2026-09-18T17:39:02+0900。★此の completed_at は札を翻した刻であつて、工の終つた刻ではない★。
  done_ni_aratameta_kiroku: |-
    ★專任3 自らが改めた(改めた刻=%s)★ ―― 家老の許しを待たず己の札を己で翻すのは席の職分である。
    紙 = _b2/00_ukeire_kei_ichiwa.md 15166 byte / ★192 行(wc -l = grep -c '' = 臺帳の lines= 欄 悉く 192・split(LF) は 193 を返すが之は末尾 LF を数へた贅であり外へは一度も出して居らぬ)★
          sha256 55900890f5964004b9632625d5e5f848cece4a163a29ee36b602e279ee5df213
    臺帳 = MANIFEST.txt 102 行(path= 欄)/ 104 行(冠2行込)/ sha256 b80be88e0a8ad29f4393afeabb4b2cfce68181384b6962f19f656fff5f0b1da5
          ★mon_ 行 0・宣して除いた紙 0 本・0byte 0 本★
    門 = ★二走 悉く rc=0★(_gate/30_mon_hatsubashiri.rc=0 / 40_mon_nibashiri.rc=0)。
          對照は走る毎に別名を立て ★二度とも rc=1 で鳴つた★(31=行末空白一つ / 41=CR混入+末尾空行)。
          鳴らねば「器を疑へ」であつた ―― 鳴つた故、門は現に測つて居る。
    commit = 36b88f93(★己の束 123 本のみ・束外 0 本★)。先住の staged 959 本は ★不触★
          ―― `git commit --only ... -- <束>` で彫り、reset は一度も打たぬ(共用樹の條)。
          臺帳 102 と commit 123 の差 21 = 員外 _gate/ 20 + 臺帳自身 1 ★丸めず突合し 0 本の食ひ違ひ★。
    監査提出 = 軍師mac 直送 6 便 seq=332973/332974/332975/332976/332977/332978(悉く parent 332152・rc=0・
          206/249/286/269/285/193 字 ―― ★300字の條を送る前に己の器で測り、初版の 438 字と 387 字は送らずに落とした★)。
    納め = 家老mac 箱へ 2 便(300 字 / 217 字・rc=0・箱の尾で胴を読み返して一致)。
    宣ETA 2026-09-18T17:30 に対し 實測 2026-09-18T17:36 = ★+6 分 超過★(丸めず書く)。
    ★閉ぢたのは ㋐㋑㋒㋔㋖㋗。㋓(二便)は B1/B3 の判定提出を以て果たす★。
    ★残 116 話は次弾へ残す(下命の逐語)★。板 6caf8ca2/40d8e26a/38dcde86 の記帳は ★家老と委員長の手★ ゆゑ
    當席は path と sha256 を供すのみ。押しても居らぬ(固定 ref を家老へ告げるまでが席の仕事・裁332510㋔)。
  board_task: 6caf8ca2
  board_task_zen: 6caf8ca2(B2・本弾で一話切つた板) / 40d8e26a(B1) / 38dcde86(B3)
  board_task_no_ne: 裁332455「次弾から uuid8桁 board_task に統一」∴ 下の ban_id_b1/b3/b2(家老の手・13:36 記)は
    ★旧形として残し消さぬ(他者の書いた行を消すのは席の分を越える)★。當席は以後 board_task 形で書く。
""" % (koku, koku)

# ───────── 当て紙 其の二 ―― km-153 の項へ board_task を据ゑる(裁332510㋑) ─────────
MAE2 = """tsugi_no_tama_km153_2026-09-18T05:34:44+0900:
  task_id: km-153-jou4-no-damari-wo-tojiru-to-minamoto-wo-naosu-20260918
  status: done
"""
ATO2 = """tsugi_no_tama_km153_2026-09-18T05:34:44+0900:
  task_id: km-153-jou4-no-damari-wo-tojiru-to-minamoto-wo-naosu-20260918
  status: done
  board_task: eb67444f
  board_row_full: eb67444f-89bc-474b-9ca5-403c0f260604
  board_task_suete_kiroku: 裁 seq332510(親 332476)で板行が★新設★された故、★後から★此の項へ据ゑた(据ゑた刻=%s・專任3 の手)。
    ★板そのものは書いて居らぬ ―― 記帳は家老と委員長の手である(裁332510㋓)★。
    板の fixed=9af1a96c は ★當席の枝の先が既に動いて居る故 古びて居る★(先=4e4cfeeb・origin 75aa92f2 に対し 4 進み)。
    此の食ひ違ひは家老が seq332963〜332965 で委員長へ上げた ―― ★當席は判ぜぬ★。
""" % koku

ate = [("其の一 km-175→done", MAE1, ATO1), ("其の二 km-153へ board_task", MAE2, ATO2)]
s = moto
for na, mae, ato in ate:
    n = s.count(mae)
    print("当て %s ―― 当たり %d 箇所" % (na, n))
    assert n == 1, "★当たりが 1 でない(%d) ―― 直さぬ★ %s" % (n, na)
    s = s.replace(mae, ato, 1)

assert s != moto, "★一字も動いて居らぬ★"
kaku(os.path.join(F, "01_chou_ato.yaml"), s)

# ───────── 読み直せるか(yaml として) ─────────
try:
    import yaml
    d = yaml.safe_load(s)
    print("★yaml 読み直し 成 ―― 頂の鍵 %d 本★" % len(d))
    k175 = d["tsugi_no_tama_175_20260918T1336"]
    k153 = d["tsugi_no_tama_km153_2026-09-18T05:34:44+0900"]
    assert k175["status"] == "done", k175["status"]
    assert k175["board_task"] == "6caf8ca2", k175["board_task"]
    assert k175["ban_id_b1"].startswith("40d8e26a"), "★家老の旧形行が消えて居る★"
    assert k153["board_task"] == "eb67444f", k153["board_task"]
    print("  km-175 status=%s board_task=%s ban_id_b1=%s(残存)" % (k175["status"], k175["board_task"], k175["ban_id_b1"][:8]))
    print("  km-153 board_task=%s board_row_full=%s" % (k153["board_task"], k153["board_row_full"]))
except ImportError:
    print("★yaml module 無し ―― 読み直しは ★測れぬ★(据ゑぬ)★")
    raise SystemExit(3)

# ───────── 据ゑる ─────────
io.open(CHOU, "w", encoding="utf-8", newline="\n").write(s)
print("★据ゑた★ %s  %d byte / %d 行" % (CHOU, len(s.encode("utf-8")), s.count("\n")))

o = subprocess.run(["git", "diff", "--", "queue/tasks/ashigaru-mac-3.yaml"], cwd=ROOT,
                   capture_output=True, text=True)
kaku(os.path.join(F, "02_chou_sabun.diff"), o.stdout if o.stdout.strip() else kaki_m.KARA)
print("差分 = %d 行(rc=%d)" % (o.stdout.count("\n"), o.returncode))
