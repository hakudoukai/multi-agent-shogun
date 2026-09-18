# -*- coding: utf-8 -*-
"""★B2 受入形 一話の紙を組む器★(km-175 ㋔)
★数を手で打たぬ★ ―― 悉く raw/*.tsv から引いて表へ流す(打てば臺帳と紙が離れる)。
四札: 刻=冠 / 根=本束 / rc=本器の returncode / 対照=引けなんだ欄は ★『引けぬ』と刷る★(空欄にせぬ)。"""
import os
import sys
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku = kaki_m.kaku

KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
R = lambda n: os.path.join(BUNDLE, "raw", n)


def tsv(n):
    """戻り= (header, rows)。★行末の空欄は kaki が剥ぐ故、読む側で均す★"""
    gyou = open(R(n), encoding="utf-8").read().rstrip("\n").split("\n")
    h = gyou[0].split("\t")
    rows = [(x.split("\t") + [""] * len(h))[:len(h)] for x in gyou[1:]]
    return h, rows


def hyou(h, rows):
    """markdown の表へ。★| は潰す(表が割れる)★"""
    esc = lambda s: s.replace("|", "\\|")
    o = ["| " + " | ".join(esc(x) for x in h) + " |",
         "|" + "|".join(["---"] * len(h)) + "|"]
    for r in rows:
        o.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(o)


def hiku(n, key, col=1):
    """臺帳の一行を鍵で引く。★引けねば『引けぬ』と返す(黙つて空にせぬ)★"""
    _, rows = tsv(n)
    for r in rows:
        if key in r[0]:
            return r[col]
    return "★引けぬ(臺帳に鍵『%s』が無い)★" % key


h60, r60 = tsv("60_b2_kyakuhon_no_arika.tsv")
h61, r61 = tsv("61_b2_ukeire_no_koumoku.tsv")
h63, r63 = tsv("63_b2_hogosha_1to1.tsv")
h65, r65 = tsv("65_b2_kaisou_no_tsukiawase.tsv")
h67, r67 = tsv("67_1to1_app_no_ki.tsv")
h72, r72 = tsv("72_b2_ichiwa_no_hakari.tsv")

rc_cli = hiku("72_b2_ichiwa_no_hakari.tsv", "CLI 本走り rc", 2)
rc_neg = hiku("72_b2_ichiwa_no_hakari.tsv", "陰性対照", 2)
rc_test = hiku("67_1to1_app_no_ki.tsv", "rc(", 1)
hon_test = hiku("67_1to1_app_no_ki.tsv", "走つた本数", 1)
skip_test = hiku("67_1to1_app_no_ki.tsv", "skip", 1)
n_kyaku = hiku("60_b2_kyakuhon_no_arika.tsv", "脚本 md", 1)
n_nokori = hiku("60_b2_kyakuhon_no_arika.tsv", "残 117 話", 1)
n_wa = hiku("63_b2_hogosha_1to1.tsv", "話の数", 1)
n_kagi = hiku("63_b2_hogosha_1to1.tsv", "解説の鍵の数", 1)
n_miki = hiku("63_b2_hogosha_1to1.tsv", "未解決", 1)
n_koji = hiku("63_b2_hogosha_1to1.tsv", "孤児", 1)
tatsu = hiku("63_b2_hogosha_1to1.tsv", "1:1 か", 1)
ba = hiku("72_b2_ichiwa_no_hakari.tsv", "場の数", 2)
gyo = hiku("72_b2_ichiwa_no_hakari.tsv", "行の数", 2)
sha_md = hiku("72_b2_ichiwa_no_hakari.tsv", "脚本 md(現物)", 3)
sha_js = hiku("72_b2_ichiwa_no_hakari.tsv", "載つて居る data", 3)

M = []
A = M.append
A("# B2 ―― 残 117 話の ★演出テンプレ受入形★ を「一話だけ」切る")
A("")
A("> **一話しか切らぬ。★残 116 話は次弾へ残す★**(家老令 km-175 ㋔ 逐語)。")
A("> 刻 `%s` ／ 席=專任3(ashigaru-mac-3) ／ 板 `6caf8ca2`(B2) ／ 親裁 `332152`。" % KOKU)
A("")
A("**★此の紙が新たに定めた規則は 0 条である★** ―― 受入の門は既に製品樹に在り、本紙は其れを")
A("**名指して並べ、一話を実際に通した出目を置いた**だけである(Anti-Duplication Rule 順守)。")
A("")
A("## 四札(此の紙の数が何處から来たか)")
A("")
A(hyou(["札", "実"], [
    ["刻", KOKU + "(器 driver/60・61・62・65 の走りは各 raw/*.tsv の刻)"],
    ["根と深さ", "`/Users/momizimac/DentalBI/frontend/src/features/child-passport/story-engine/`(読取のみ)＋本束 `_b2/`"],
    ["rc", "CLI 本走り **%s** ／ 陰性対照 **%s** ／ app の test **%s**(悉く subprocess の returncode ―― ★管を通さぬ★)" % (rc_cli, rc_neg, rc_test)],
    ["対照", "⑴陰性= `authoring-sample-broken-cap.md`(必ず落ちる紙)⑵suite 内蔵の陽性對照(空表→未解決 15)⑶『%s 本現に走つた』(0 本の緑は緑に非ず)" % hon_test],
]))
A("")
A("---")
A("")
A("## 一 ①受入形の ★項目と型★(18 行)")
A("")
A("各行の「定義の在処」が **★唯一の出所★** である ―― 本紙は写しを持たぬ(写せば二重定義に成る)。")
A("")
A(hyou(h61, r61))
A("")
A("### 一.二 ★『項目の数』は数へた階で変はる★(板の註 31 との突合)")
A("")
A("板 `38dcde86` は「全階層 再帰= episode.\\* 9 + scenes.\\* 22 = 31／scene 階のみなら 6」と記す。")
A("當席の表は **18 行**。★之は矛盾ではなく、数へた階が違ふ★ ―― 器 `driver/61` で並べた:")
A("")
A(hyou(h65, r65))
A("")
A("**★差 1 を丸めず名指す★**: 板の 31 と當席の再帰(乙)32 の差は **封筒の鍵 `episode` を項目に")
A("数へるか否か** の一点であり、他に食ひ違ひは無い。甲(参照毎)なら 34/24 に成る ―― ")
A("`choices?: [SceneChoiceOption, SceneChoiceOption]` の同型 2 参照を二度展開する故。")
A("**∴ 『31』も『22』も『18』も『6』も正しく、★足してはならぬ★。**")
A("")
A("---")
A("")
A("## 二 ②実データを ★1 話だけ★ 流し込んだ見本")
A("")
A("**★見本は作らず、現に書かれた 1 話を使つた★** ―― 脚本 md は此の mac に **%s 本**(15 話分)在り、" % n_kyaku)
A("其の内 `S3-EP1` を **本束へ写して** 製品樹の CLI に通した。**製品樹へは一字も書いて居らぬ**。")
A("")
A("```")
A("cd /Users/momizimac/DentalBI/frontend")
A("npm run --silent validate:episode-md -- <本束の写し>/_b2/S3-EP1.md")
A("```")
A("")
A("(`tools/md2scene.ts:414` が `process.argv[2]` から path を取る故、★製品樹の外の紙でも通る★ ―― ")
A("之が「他席の生きた樹へ書かずに実データを通す」道である。)")
A("")
A(hyou(h72, r72))
A("")
A("**読み方**: 変換の出目と ★現に載つて居る `S3-EP1.json`★ が **場 %s・行 %s** で一致した。" % (ba, gyo))
A("∴ 受入形は「絵に描いた型」ではなく、**★現に 15 話が通つて居る型★** である。")
A("脚本 md `sha256=%s` ／ 載つて居る data `sha256=%s`。" % (sha_md, sha_js))
A("")
A("陰性対照 `authoring-sample-broken-cap.md` は **rc=%s** で落ち、門番の文言は" % rc_neg)
A("`at=0 の effect 束が cap(3) を超える(実測 4)` であつた ―― **★門は現に噛んで居る★**。")
A("")
A("### 二.二 ★118 話目を実データで埋める事は出来ぬ★(不在を黙つて埋めぬ)")
A("")
A(hyou(h60, r60))
A("")
A("残 117 話の脚本は **%s 本** ―― 出所は Box『てりはキョウリュウおうこく_物語制作』であり、" % n_nokori)
A("此の mac の disk に無い。**∴ 『117 話分の受入形を通した』とは書けぬ。書けるのは")
A("『受入形は 15 話で現に立ち、118 話目も同じ CLI で受かる』までである。**")
A("")
A("---")
A("")
A("## 三 ③『保護者解説 1:1 維持』を ★何で測るか(一行)★")
A("")
A("> **★`episodes/*.json` の `parent_explanation_ref` を app 自身の解決器 `resolveParentExplanation` に")
A("> 掛け、①話数=鍵数 ②未解決 0 ③孤児 0 ④ref の重なり 0 ―― の四条が同時に立つ事で測る")
A("> (器= 製品樹の既存 test `episodes/__tests__/episodes.test.tsx`・實測 rc=%s / %s 本通 / skip %s)。★**" % (rc_test, hon_test, skip_test))
A("")
A("**★器は二つ在り、上下が在る★**:")
A("")
A(hyou(h67, r67))
A("")
A("**一の器(app の解決器)が上である理由**: `hooks/useParentExplanationLink.ts` の `isS3S4EntryEmpty` が")
A("**★空の雛形を fail-closed で null にする★** ―― ∴ **「鍵が在る」は「解決する」の證に成らぬ**。")
A("己の regex(二の器)は鍵の在否しか見ぬ故、單独で 1:1 を宣してはならぬ。")
A("")
A("**實測**: 話 %s ／ 解説の鍵 %s ／ 未解決 %s ／ 孤児 %s ―― **1:1 は %s**。" % (n_wa, n_kagi, n_miki, n_koji, tatsu))
A("")
A(hyou(h63, r63))
A("")
A("---")
A("")
A("## 四 ★二重実装を作らなんだ證★(受入の門は既に在る)")
A("")
A(hyou(["受入の何を", "既に在る門(★唯一の出所★)", "當席が足した物"], [
    ["脚本 md の書式", "`episodes/AUTHORING.md` §1 書式(4段)・§3 cap 宣言・§4 演出行・§5 禁則", "**0 行**"],
    ["md→JSON 変換と型の当否", "`tools/md2scene.ts` → 動的 import で `validateEpisode`(`md2scene.ts:376`)", "**0 行**"],
    ["schema へ丸投げ出来ぬ検め", "`validator.ts` の `checkSceneStaticGate`(`md2scene.ts:428`)", "**0 行**"],
    ["場の中身の可否", "a2 の `validateScene`(`validateEpisode.ts` が委ねる・二重定義を作らぬ)", "**0 行**"],
    ["1 話を足す手順", "`episodes/README.md` §9.2「10分手順」", "**0 行**"],
    ["受入形の雛形", "`episodes/TEMPLATE.json`(既存 test『TEMPLATE.json は そのままで valid』が守る)", "**0 行**"],
    ["1:1 の断", "`episodes/__tests__/episodes.test.tsx` 2.(1:1) / 3.(未解決0) / 4.(空表→15)", "**0 行**"],
]))
A("")
A("**∴ B2 の『受入形』は ★新たに設計する物ではなく、既に在る物を一話で實證する物★ であつた。**")
A("")
A("---")
A("")
A("## 五 ★此の紙が意味せぬ事★")
A("")
A(hyou(["書いた事", "★意味せぬ事★"], [
    ["受入形の項目 18 行を並べた", "18 が『全ての field』ではない(再帰なら 32・板の数へ方なら 31)"],
    ["S3-EP1 が CLI rc=%s で通つた" % rc_cli, "残 117 話が通る證に成らぬ(★脚本が此の mac に無い★)。通るのは『同じ書式で書かれた 1 話』のみ"],
    ["場 %s・行 %s が一致した" % (ba, gyo), "画で正しく再生される證に成らぬ ―― ★通し再生の實視は browser を要し、本弾の外★"],
    ["1:1 が立つ(話 %s / 鍵 %s)" % (n_wa, n_kagi), "S5 以降・118 話目の解説が書かれて居る證に成らぬ。立つのは ★今 在る 15 話の範★"],
    ["app の test が rc=%s / %s 本通つた" % (rc_test, hon_test), "frontend 全 suite の青を意味せぬ ―― ★先住の赤(6 file / 20 落ち)は名指すのみで触れて居らぬ★(家老令 ㋑)"],
    ["門が陰性対照で rc=%s と落ちた" % rc_neg, "門が悉くの誤りを捕へる證に成らぬ(捕へたのは cap 束 一種)"],
]))
A("")
A("---")
A("")
A("## 六 ★己の疵(報ずる前に己で捕へた)★")
A("")
A(hyou(["疵", "何が起きたか", "如何に直したか"], [
    ["⑴ 器が 0 を刷つて rc=0 の儘だつた",
     "`driver/61` 初版の field regex が行末 `;` を要求したが、此の樹の TS に `;` は無く、Episode/EpisodeMeta/Scene 悉く ★field 0★ と刷つた",
     "regex を `;?` へ改め、源の形を `grep -n` で先に見た。★『rc=0』は『測れた』の證に成らぬ★"],
    ["⑵ 負対照の檢出子が行單位で AND を取つた",
     "`emptyTable` と `unresolved` は別行ゆゑ、現に在る對照を ★『対照が見えぬ』★ と刷つた",
     "`it(` の塊で切り直し『★対照在り★』を得た。★對照の不在は對照の不在を意味せぬ★"],
    ["⑶ test の出目を一度 `/tmp` へ置いた",
     "`--reporter=basic` が此の版に無く落ちた折、出目を `/tmp/.vt.out` へ採つた(證を /tmp に置く禁を踏んだ)",
     "器 `driver/62` に積み直し、out/err/rc を kaki で ★束の中へ★ 収めた"],
]))
A("")
A("---")
A("")
A("## 七 次弾へ残す物")
A("")
A("- **★残 116 話★**(家老令 逐語「残116話は次弾へ残せ」) ―― 脚本の入手(Box)が先。")
A("- **通し再生の實視** ―― browser を要す(板 `6caf8ca2` の『通し再生の実視(AI6h)』)。")
A("- **S5 以降の保護者解説** ―― 1:1 の範を広げる時は `parentExplanations.S3S4.ts` へ貼る(★埋めるな★の註が在る)。")
A("")
kami = "\n".join(M) + "\n"
p = os.path.join(BUNDLE, "_b2", "00_ukeire_kei_ichiwa.md")
kaku(p, kami)
b = open(p, "rb").read()
print("紙= %s" % os.path.relpath(p, BUNDLE))
print("%d byte / %d 行 / sha256=%s" % (len(b), kami.count("\n"), hashlib.sha256(b).hexdigest()))
