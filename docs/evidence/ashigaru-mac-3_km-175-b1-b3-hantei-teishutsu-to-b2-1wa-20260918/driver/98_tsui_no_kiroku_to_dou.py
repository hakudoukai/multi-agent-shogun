# -*- coding: utf-8 -*-
"""★追の記録を帳へ足し、追の便の胴を組む器★(km-175 ㋗ 締め ―― 裁332510㋔『固定 ref を家老へ告げよ』)

條: ⑴帳へは ★追記のみ★(先に書いた done の記録は ★書き換へぬ★ ―― 已に外へ出した値である)。
    ⑵錨は逐語・当たり丁度1・据ゑた後に yaml で読み直す(97 と同じ作法)。
    ⑶胴は ★送る前に★ 字を数へ、300字を超えたら ★組んだ所で落ちる★。
    ⑷生の text は悉く kaki 経由。★rc を管に通さぬ★。"""
import io, os, sys, subprocess, datetime
import importlib.util as iu

ROOT   = "/Users/momizimac/multi-agent-shogun"
BUNDLE = os.path.join(ROOT, "docs/evidence/ashigaru-mac-3_km-175-b1-b3-hantei-teishutsu-to-b2-1wa-20260918")
CHOU   = os.path.join(ROOT, "queue/tasks/ashigaru-mac-3.yaml")
s_ = iu.spec_from_file_location("kaki_m", os.path.join(BUNDLE, "driver", "00_kaki.py"))
kaki_m = iu.module_from_spec(s_); s_.loader.exec_module(kaki_m)
kaku = kaki_m.kaku

koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

def g(*a):
    p = subprocess.run(["git"] + list(a), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert p.returncode == 0, "★git %s rc=%d★ %s" % (a, p.returncode, p.stderr.decode())
    return p.stdout.decode().strip()

TIP  = g("rev-parse", "HEAD")
TREE = g("rev-parse", "HEAD^{tree}")
EDA  = g("rev-parse", "--abbrev-ref", "HEAD")
OM   = g("rev-parse", "origin/main")
cher = g("cherry", "origin/main", "HEAD").split("\n")
plus  = sum(1 for l in cher if l.startswith("+"))
minus = sum(1 for l in cher if l.startswith("-"))
DAI  = "895461d57e7ba27ccf9a62ec9305ad2ac57b8b42f11b4764f4bf869ee788179a"

# ───────── ① 帳へ追記(先の記録は一字も書き換へぬ) ─────────
MAE = """  board_task: 6caf8ca2
  board_task_zen: 6caf8ca2(B2・本弾で一話切つた板) / 40d8e26a(B1) / 38dcde86(B3)
"""
ATO = """  board_task: 6caf8ca2
  board_task_zen: 6caf8ca2(B2・本弾で一話切つた板) / 40d8e26a(B1) / 38dcde86(B3)
  tsui_no_kiroku: |-
    ★追記(%s)―― 上の done の記録は ★書き換へぬ★(已に外へ出した値である)。下は其の後に足した事のみ★
    追の彫り = 1df72e96(69 本・★束外 0 本★・先住の staged 959 本 不触)。
      内訳 = 臺帳凍結後に生れた紙 46 本(_letters/55〜60・95_1・95_2 とその送り控と読み返し・
      _fuda/ の帳の前後と差分・driver/55・driver/97)＋ 追の門の出目 20 本 ＋ 書き足した 3 本
      (MANIFEST.txt・_letters/90_tegami_choudai.tsv 12→28 行・driver/96)。
    臺帳を積み直した = ★102 行 → 148 行★(歩いた 148・mon_ 行 0・除いた 0・0byte 0)。
      sha256 b80be88e… → ★%s★。
      現物 188 本 = 臺帳 148 + 員外 _gate/ 39 + 臺帳自身 1 ―― ★0 本の食ひ違ひ★。
    追の門 = 二走とも rc=0。控は ★先の走りと別名★(尾 _tsui)で二度とも rc=1 に鳴つた。
      控の名が衝つ故 driver/96 に KM_RUN_SUFFIX を当てた(既定は空 ∴ 先の走りの振舞ひは不変・当たり6箇所)。
    ★帳は git の追跡外★(.gitignore 7行目の裸の `*`・check-ignore rc=0 / ls-files rc=1。
      陽性対照 CLAUDE.md は rc=1 / rc=0 と逆の出目)∴ `git diff` の 0 行は「動いて居らぬ」の意ではない。
      前後の写しと差分は _fuda/ に在る(足した 32 行・消した 1 行 = `status: assigned`)。
    ★己の疵(追)★= ⑴帳の差分を生の `>` で採り kaki を後から通した(剥がれた行は 0 行であつたが、
      作法としては初めから器を通すべきであつた)。⑵`git ls-files` の rc を一度 `| head` に通して
      拾ひ、head の rc=0 を帳の rc と見誤つた ―― 管を通さず採り直して rc=1 と確かめた(己で捕へた)。
    固定 ref(家老へ告げた値) = 枝 %s / tip %s / tree %s。
      origin/main %s に対し ★SHA の数で 28 進み★だが `git cherry` では ★+%d / -%d★
      ―― 之は「変更の数が 28」ではない。★押して居らぬ(押す手は委員長・裁332510㋔)★。
""" % (koku, DAI, EDA, TIP, TREE, OM, plus, minus)

moto = io.open(CHOU, encoding="utf-8").read()
n = moto.count(MAE)
assert n == 1, "★当たりが 1 でない(%d) ―― 直さぬ★" % n
atarashii = moto.replace(MAE, ATO, 1)
import yaml
d = yaml.safe_load(atarashii)
k = d["tsugi_no_tama_175_20260918T1336"]
assert k["status"] == "done" and "tsui_no_kiroku" in k and TIP[:8] in k["tsui_no_kiroku"]
io.open(CHOU, "w", encoding="utf-8", newline="\n").write(atarashii)
kaku(os.path.join(BUNDLE, "_fuda", "03_chou_tsui.yaml"), atarashii)
print("★帳へ追記した★ %d byte / %d 行(前 %d 行)" % (len(atarashii.encode()), atarashii.count("\n"), moto.count("\n")))

# ───────── ② 追の便の胴(組む所で字を数へる) ─────────
BIN = [
 ("96_kotei_ref_karo",
  "karo-mac 殿 專任3 追 ―― ★裁332510㋔の固定 ref を告ぐ。押して居らぬ★。"
  "枝=ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917 "
  "tip=%s tree=%s。追の彫り 1df72e96(69本・束外0・先住staged959本 不触)。"
  "臺帳 102→148行 sha256=%s。門 追二走 rc=0・控は別名(_tsui)で二度 rc=1 鳴。"
  "km-175 の札は己の手で done へ、km-153 の項へ board_task=eb67444f 据ゑた。板は書いて居らぬ。" % (TIP[:12], TREE[:12], DAI[:16])),
 ("97_tsui_kansa_gunshi",
  "軍師mac 殿 專任3 追の監査提出(km-175 親裁332152・先の6便 seq332973〜332978 の続)。"
  "追で足した物=㋗の締め。臺帳 102→148行 sha256=%s(歩いた148・mon_行0・除いた0・0byte0)。"
  "門 追二走 rc=0、控は先の走りと★別名(_tsui)★で二度 rc=1 に鳴つた。彫り 1df72e96(69本・束外0)。"
  "帳は git 追跡外(check-ignore rc=0/ls-files rc=1・陽性対照 CLAUDE.md は逆)故 git diff 0行は不動の證に非ず。" % DAI[:16]),
 ("98_onore_no_kizu_gunshi",
  "軍師mac 殿 專任3 追2/2 ―― ★追で己が捕へた疵 2 件★。"
  "⑴帳の差分を生の `>` で採り kaki を後から通した(剥がれた行は 0 行であつたが作法違ひ)。"
  "⑵`git ls-files` の rc を `| head` に通して拾ひ head の rc=0 を帳の rc と見誤つた ―― "
  "管を通さず採り直し rc=1 と確かめた(報ずる前に己で捕へた)。"
  "紙は _b2/00_ukeire_kei_ichiwa.md 15166byte/192行 sha256=55900890f5964004(残116話は次弾)。"),
]
JOU = 300
warui = []
for na, dou in BIN:
    assert "\n" not in dou, "★胴は一行★ %s" % na
    ji = len(dou)
    kaku(os.path.join(BUNDLE, "_letters", na + ".txt"), dou + "\n")
    print("%-24s %3d 字 %s" % (na, ji, "★條の300字を超えた ―― 截れ★" if ji > JOU else ("(註の100字超・條は満たす)" if ji > 100 else "")))
    if ji > JOU:
        warui.append((na, ji))
assert not warui, "★%s ―― 送る前に落ちる(條)★" % warui
print("★三便 悉く條を満たす★")
