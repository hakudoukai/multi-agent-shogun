# -*- coding: utf-8 -*-
"""★B2 ―― 残117話の演出テンプレ受入形を「一話だけ」切る★(km-175 ㋔)
命: ①型と項目 ②実データを1話 ③『保護者解説1:1 維持』を何で測るか一行。★残116話は次弾へ残す★。
二重実装を作らぬ: 受入の門は ★既に製品樹に在る★(tools/md2scene.ts の CLI・validateEpisode・
checkSceneStaticGate・episodes/README.md §9.2)。本器は ★其れを呼ぶだけ★ で、判定規則を書き直さぬ。
製品樹へは一行も書かぬ(現物は読むのみ・写しは本束へ置く)。
四札: 刻=冠 / 根=下表 / rc=CLI の returncode(★管を通さず★) / 対照=陰性 sample(cap 束を仕込んだ物)。"""
import os
import re
import sys
import json
import shutil
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

DENTAL = "/Users/momizimac/DentalBI"
FE = os.path.join(DENTAL, "frontend")
SE = os.path.join(FE, "src/features/child-passport/story-engine")
EP = os.path.join(SE, "episodes")
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def sha256_of(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hashiru(args, cwd, tmo=900):
    p = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return (p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"))


# ―― ⑴ 117話の脚本は此の mac に在るか(★不在を黙つて埋めぬ★) ――
kyakuhon = sorted(x for x in os.listdir(os.path.join(EP, "scripts")) if x.endswith(".md"))
kaita = sorted(x for x in os.listdir(EP) if re.match(r"^S\d+-EP\d+\.json$", x))
rows_ari = [["脚本 md(episodes/scripts)", len(kyakuhon), ", ".join(kyakuhon[:4]) + " …"],
            ["話の data(episodes/*.json)", len(kaita), ", ".join(kaita[:4]) + " …"],
            ["★残 117 話の脚本★", 0, "★此の mac に無し★(Box 『てりはキョウリュウおうこく_物語制作』が出所・"
             "find で *物語* 0 件・∴ ★118 話目を実データで埋める事は出来ぬ★)"]]
kaku_tsv(os.path.join(BUNDLE, "raw", "60_b2_kyakuhon_no_arika.tsv"), rows_ari,
         header=["何を", "本数", "言"])

# ―― ⑵ 受入形の項目と型 ―― ★製品樹の定義から引く(書き写さず・行を名指す)★ ――
def gyou_wo_sagasu(path, pat):
    for i, l in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if re.search(pat, l):
            return i, l.strip()
    return 0, "★見えぬ★"

KOUMOKU = []
epts = os.path.join(EP, "episode.ts")
tyts = os.path.join(SE, "types.ts")
vats = os.path.join(EP, "validateEpisode.ts")
for na, typ, path, pat, jou in [
    ("episode.id", "string", epts, r"^  id: string", "『S<数>-EP<数>』・file 名と一致(EPISODE_ID_RE)"),
    ("episode.title", "string", epts, r"^  title: string", "空でない string"),
    ("episode.visit", "number", epts, r"^  visit: number", "★1 以上の整数★"),
    ("episode.season", "string", epts, r"^  season: string", "'S3' 等の season 記号"),
    ("episode.audience", "string", epts, r"^  audience: string", "'5-6' 等の年齢帯"),
    ("episode.mission", "string", epts, r"^  mission: string", "脚本の 🦷 行 をそのまま"),
    ("episode.badge", "string", epts, r"^  badge: string", "脚本の 🏅 行 をそのまま"),
    ("episode.parent_explanation_ref", "string", epts, r"parent_explanation_ref: string",
     "★保護者解説の id('S3-EP1' 形)★ ―― 1:1 の鍵"),
    ("scenes[]", "Scene[]", epts, r"^  scenes: Scene\[\]", "★1 場 以上★・場 id は 'episode.id-' で始まる・id 重複禁"),
    ("scene.background", "string", tyts, r"^  background: string", "同じ場所は同じ名を使ひ回す"),
    ("scene.actors[].id", "ActorId(10 値)", tyts, r"^export const ACTOR_IDS", "you/papa_dino/koron/… の 10 値のみ"),
    ("scene.actors[].anim", "AnimName?(5 値)", tyts, r"^export const ANIM_NAMES", "idle/blink/walk/joy/surprise・既定 idle"),
    ("scene.actors[].position", "Position(3 値)", tyts, r"^export const POSITIONS", "left/center/right"),
    ("scene.lines[].speaker", "SpeakerId(11 値)", tyts, r"^export const SPEAKER_IDS", "actor 10 値 + narrator"),
    ("scene.lines[].choices", "[opt,opt]?", tyts, r"^export const CHOICE_OPTION_COUNT", "★丁度 2 択★・label ≤20 字"),
    ("scene.effects[].type", "EffectType(10 値)", tyts, r"^export const EFFECT_TYPES", "enter/exit/pause/… transition_mp4"),
    ("scene.effects[].at", "number", tyts, r"^  at: number", "同 scene の lines index"),
    ("(門)未知 key", "―", vats, r"未知の key", "★封筒・top-level とも 未知 key は赤★"),
]:
    i, l = gyou_wo_sagasu(path, pat)
    KOUMOKU.append([na, typ, "%s:%d" % (os.path.relpath(path, DENTAL), i), jou])
kaku_tsv(os.path.join(BUNDLE, "raw", "61_b2_ukeire_no_koumoku.tsv"), KOUMOKU,
         header=["項目", "型", "定義の在処(★唯一の出所★)", "條"])

# ―― ⑶ 実データ 1 話を門へ通す(★製品樹へは書かず、写しを本束へ置いて path を渡す★) ――
ICHIWA = "S3-EP1"
md_moto = os.path.join(EP, "scripts", ICHIWA + ".md")
js_moto = os.path.join(EP, ICHIWA + ".json")
utsushi = os.path.join(BUNDLE, "_b2", ICHIWA + ".md")
shutil.copyfile(md_moto, utsushi)
CLI = ["npm", "run", "--silent", "validate:episode-md", "--", utsushi]
rc_h, out_h, err_h = hashiru(CLI, FE)
HANTAI = os.path.join(EP, "scripts", "_sample", "authoring-sample-broken-cap.md")
rc_n, out_n, err_n = hashiru(["npm", "run", "--silent", "validate:episode-md", "--", HANTAI], FE)
for na, body in (("70_cli_honban.out", out_h), ("70_cli_honban.err", err_h), ("70_cli_honban.rc", str(rc_h) + "\n"),
                 ("71_cli_inseitaishou.out", out_n), ("71_cli_inseitaishou.err", err_n),
                 ("71_cli_inseitaishou.rc", str(rc_n) + "\n")):
    kaku(os.path.join(BUNDLE, "raw", na), body)

# 変換の出目と現に載つて居る json を突き合はせる(★同じか否かを数で言ふ★)
try:
    henkan = json.loads(out_h)
except Exception as e:
    henkan = None
    kaku(os.path.join(BUNDLE, "raw", "72_henkan_yomenu.txt"), "json に成らぬ: %s\n" % e)
noru = json.load(open(js_moto, encoding="utf-8"))
kaku_tsv(os.path.join(BUNDLE, "raw", "72_b2_ichiwa_no_hakari.tsv"),
         [["脚本 md(現物)", os.path.relpath(md_moto, DENTAL), os.path.getsize(md_moto), sha256_of(md_moto)],
          ["写し(本束)", os.path.relpath(utsushi, BUNDLE), os.path.getsize(utsushi), sha256_of(utsushi)],
          ["載つて居る data", os.path.relpath(js_moto, DENTAL), os.path.getsize(js_moto), sha256_of(js_moto)],
          ["CLI 本走り rc", " ".join(CLI[:4]) + " <写し>", rc_h, "出目 %d 字" % len(out_h)],
          ["★陰性対照★ cap 束 rc", os.path.relpath(HANTAI, DENTAL), rc_n,
           ("★落ちた(正)★ " + (err_n.strip().split("\n")[-1][:70] if err_n.strip() else "")) if rc_n else "★通つた ―― 対照が効いて居らぬ★"],
          ["場の数(変換 / 載つて居る)", "scenes", "%s / %d" % (len(henkan["scenes"]) if henkan else "-", len(noru["scenes"])),
           "一致" if (henkan and len(henkan["scenes"]) == len(noru["scenes"])) else "★食ひ違ふ★"],
          ["行の数(変換 / 載つて居る)", "lines",
           "%s / %d" % (sum(len(s["lines"]) for s in henkan["scenes"]) if henkan else "-",
                        sum(len(s["lines"]) for s in noru["scenes"])),
           "一致" if (henkan and sum(len(s["lines"]) for s in henkan["scenes"]) == sum(len(s["lines"]) for s in noru["scenes"])) else "★食ひ違ふ★"]],
         header=["何を", "在処", "数 or rc", "言"])

# ―― ⑷ 『保護者解説 1:1 維持』を何で測るか ―― 現に測る ――
refs = {}
for f in kaita:
    j = json.load(open(os.path.join(EP, f), encoding="utf-8"))
    refs[j["episode"]["id"]] = j["episode"]["parent_explanation_ref"]
kagi = set()
for pe in ("parentExplanations.ts", "parentExplanations.S3S4.ts"):
    p = os.path.join(FE, "src/features/teriha-passport/story", pe)
    src = open(p, encoding="utf-8").read()
    kagi |= set(re.findall(r"^  '([^']+)': explanation\(", src, re.M))
mikaiketsu = sorted(v for v in refs.values() if v not in kagi)
koji = sorted(k for k in kagi if k not in set(refs.values()))
kasanari = len(refs.values()) - len(set(refs.values()))
kaku_tsv(os.path.join(BUNDLE, "raw", "63_b2_hogosha_1to1.tsv"),
         [["話の数", len(refs), "episodes/*.json の episode.id"],
          ["ref の数(重複除く)", len(set(refs.values())), "★重なり %d 件★(1:1 ゆゑ 0 が條)" % kasanari],
          ["解説の鍵の数", len(kagi), "parentExplanations.ts + .S3S4.ts の 'S3-EP1': explanation( 行"],
          ["★未解決(ref→解説が無い)★", len(mikaiketsu), ", ".join(mikaiketsu) or "0 件"],
          ["★孤児(解説→話が無い)★", len(koji), ", ".join(koji) or "0 件"],
          ["1:1 か", ("★立つ★" if (len(refs) == len(kagi) and not mikaiketsu and not koji and kasanari == 0) else "★立たぬ★"),
           "條= 話数=鍵数 かつ 未解決0 かつ 孤児0 かつ 重なり0"]],
         header=["何を", "数", "言"])
print("117話の脚本= 此の mac に 0 本(書かれた 15 話の md は %d 本)" % len(kyakuhon))
print("受入形の項目= %d 件(定義の在処を悉く名指した)" % len(KOUMOKU))
print("実データ 1 話= %s CLI rc=%d / 陰性対照 rc=%d" % (ICHIWA, rc_h, rc_n))
print("保護者解説 1:1= 話 %d / 鍵 %d / 未解決 %d / 孤児 %d / 重なり %d"
      % (len(refs), len(kagi), len(mikaiketsu), len(koji), kasanari))
