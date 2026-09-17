# -*- coding: utf-8 -*-
"""初段(表紙)を書く。★己を含む臺帳の數は書かぬ★(紙は己を含む臺帳の總數を言へぬ)。"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki
B = os.path.dirname(HERE)
ima = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"], capture_output=True, text=True).stdout.strip()

t = """# 第109弾 初段 ―― ★素の空白名は「実体無」ではなく「偽の通」を生む★

席      ashigaru-mac-2 (pane %7)
task_id km-109-suna-no-kuuhaku-mei-ga-nise-no-tsuu-wo-umu-ka-20260917
親裁    委員長裁 seq326873(PR#22 が main へ着地 4f591fc0)／裁 seq326674⑵ の続き
刻(此の紙を書いた時) {ima}
束      docs/evidence/ashigaru-mac-2_km-109-suna-no-kuuhaku-mei-20260917/
禁の遵守 scripts/ 配下へ一指も触れず(讀取のみ)／枝・refs・他席へ触れず／git add も commit も push もせず／證は /tmp に置かず束の下

## 結 ―― 一行で

★真である。素の空白名 `path=a b.txt` の行は、切り落された先頭語 `a` が disk に在る限り
  讀み手を ★一致★ と刷らせ、rc=0 を返させる。疵は「數を少なく言ふ」ではなく
  ★「一度も見て居らぬ file を『通つた』と言ふ」★ である。★

## ㋐ 器の版(raw/00_utsuwa_no_han.txt)

  走らせた實体 = 作業樹の scripts/checks/karo_mac_manifest_verify.py
    full blob sha ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579 / 198行 / 10965B
    sha256(内容)  a507c998c7bd648543a8dcb8643ba1188254800b039cdad76f4953ef34d5fa41
  突合 `git diff --quiet origin/main -- <器>` → ★rc=0★ = ★origin/main(4f591fc0) と逐語同一★
  ★注進★ ―― 裸の `main`(local ref)は 363d5fb で止まつて居り、其處からは b19ec9ea/127行(旧版)が出る。
          `git diff --quiet main -- <器>` は rc=1。★以後「main の版」は origin/main を指せ。★

## ㋑ 則の到達可能性(raw/10_soku_no_toutatsu.txt・綴り14種)

  則は ★ast で逐語抜き★(行番を焼き込まず)。己の写しで再現し、
  ★写しの出目 == 生器 paths_of() の出目 : 不合 0 / 14 綴り★ を先に立ててから表を出した。
  当たつた則の数 ―― 則① 9件 ／ 則② 3件 ／ 則③ 1件 ／ 一本も当たらず 1件。

  ★到達せぬ理由(機構)★: 則① `(?:^|\\s)path=([^\\s"\\']+)` が外れるのは
  `path=` の直後の一字が ★空白か引用符★ の時だけである。素の空白名 `path=a b.txt` は
  直後が `a` ゆゑ ★必ず則①が先に当たり★、素の空白名の為に書かれた則②へは ★到達し得ぬ★。

## ㋒ 偽の通の實測(raw/20_nise_no_tsuu.txt・fixtures/ 五條)

  全條 同じ一行 `path=a b.txt sha256=533dc9d8… bytes=36 lines=1`(sha は★実物から★取つた)。

  | 條 | disk に在る物 | 出目 | rc |
  |---|---|---|---|
  | ⑴ c4_onaji     `a`(同内容) と `a b.txt` 両方 | ★一致 1★ | ★0★ |
  | ⑴'c1_chigau    `a`(別内容) と `a b.txt` 両方 | 相違 1 ―― ★`a` を名指す★ | 1 |
  | ⑵ c2_saki_dake `a` だけ(`a b.txt` は ★無い★) | ★一致 1★ | ★0★ |
  | ⑶ c3_nashi     どちらも無い | 実体無 1 ―― ★`a` を名指す★ | 1 |
  | ＋ c5_kuuhaku_dake `a b.txt` だけ | 実体無 1 ―― ★`a` を名指す★ | 1 |

  ★c2 が本件の核である★ ―― 臺帳が名指した `a b.txt` は ★disk の何處にも無い★ のに
  讀み手は「一致1・相違0・実体無0」と刷り ★rc=0★ を返す。
  ★之は『通つた』ではない。『見て居らぬ』である。★
  併せて c1/c3/c5 では、器は ★臺帳に一度も書かれて居らぬ名 `a`★ を疵として名指す。
  即ち ⑴通す時は黙り ⑵落とす時は別人を指す。

## ㋓ 害の広さ(raw/30_gai_no_hirosa.txt・集め方は其の紙に逐語)

  刻 2026-09-17T17:24:24+0900 ／ 根 /Users/momizimac/multi-agent-shogun ／ 深さ限り無し(`.git/` のみ除く・S_ISREG のみ)
  臺帳らしき紙の判じ方 = ★b"sha256=" を含む★(名では判ぜぬ) → 5067 紙 / 歩いた常体 file 46015

  | 欄 | 甲(広:則①②の出目が違ふ) | ★乙(狭:真の空白名)★ | 丙(括つた空白名) | 測れぬ |
  |---|---|---|---|---|
  | disk(當席の束を除く) | 1239 行 | ★376 行★ | 34867 行 | 220 行 |
  | 樹 origin/main (4f591fc0 / 臺帳 blob 8) | 0 | ★0 行★ | 0 | 0 |
  | 樹 HEAD (75aa92f2 / 臺帳 blob 115) | 0 | ★46 行★ | 50 | 0 |
  | disk・當席の束(★陽性対照の實物★) | 0 | 10 | 2 | 0 |

  ★己の除外は「歩いて居らぬ」ではない★ ―― 當席の束も歩いた上で ★別欄に分けた★。
  陽性対照は ★檢出子其の物に・測る路へ乗せて★ 通した(四綴り → 乙/甲/丙/― と正しく分かれた)。
  讀めなんだ file 1 本・測れぬ行 220 行は ★0 に混ぜて居らぬ★。

## ㋔ 塞ぎ方の案(raw/40_fusagikata.txt・★五案・一つも据ゑて居らぬ★)

  ★推す案 = 案三(第五の數「両義の行」)★。
  | 案 | 何を直すか | 何を壊し得るか | 戻し方 |
  |---|---|---|---|
  | 一 則の順を ②→①→③ へ | 素の空白名が則②へ到達する | `path=<名> bytes=… sha256=…` の行(則②が過剰に呑む)。其の行數 = 甲−乙 = 863 行 | 順を①②③へ戻す(一行の入替) |
  | 三 ★第五の數「両義の行」★(①と②の出目が違ふ行を別に數へる) | ★通す時に黙る事★を止める。c2 が rc で鳴る | 強形(rc を赤に)は 376 行を一斉に赤くし得る(裁321353⑴の懸念) | 弱形(數へるだけ)から入れ、赤化は別裁で |
  其の他 案二(三則を一本の正規表現へ)／案四(書き手+門で封じる=封であつて治療に非ず)／案五(一致の時も当たつた path を刷る=見えるが止まらぬ)。
  ★器は共有物ゆゑ提案に留めた(変更統制)。★

## ㋕ 此の數が意味せぬ事(raw/50_imi_senu.txt・七項)

  ⒈ 「乙 376 行」は ★偽の通が 376 件在る★ の意ではない。偽の通が成るには更に
     「切り落された先頭語が disk に実在する」事が要る ―― 本弾は其の掛け算を測つて居らぬ。
     逆に下限でもない(甲の内 乙でない 863 行にも偽の通は潜り得る)。
  ⒉ ★「origin/main の乙 0 行」は「器が健全」の意ではない★。臺帳 blob が 8 本しか無いだけで、
     器の疵は blob の数と無関係に生きて居る。c2 は其れを一行で示した。
  ⒊ ★rc=0 は「検めた」の意ではない★ ―― c2 は名指した file が ★無い★ 儘 rc=0 を返した。
  ⒋ ㋑の「則② 3件」は當席が選んだ綴り14種の性質であつて、現物の分布ではない。
  ⒌ disk 欄と樹 欄は ★同じ集合を二度數へた物ではない★(追跡外の紙が disk には在る)。
  ⒍ 乙(狭)は ★疑ひ★ であつて證ではない。名に空白が在ると断ずるには disk に当てる要が在る。
  ⒎ 當席が本弾で作つた試験臺帳 5 本は現物の害ではない ―― ★歩いた上で分けた★。

## 紙の一覧(★此の紙は己を含む臺帳の總數を書かぬ★)

  raw/00_utsuwa_no_han.txt          ㋐ 器の版と突合
  raw/10_sokutei_soku.py / 10_soku_no_toutatsu.txt   ㋑ 則の到達可能性(写しの證つき)
  raw/20_nise_no_tsuu.py / 20_nise_no_tsuu.txt       ㋒ 偽の通 五條の實測
  raw/30_gai_no_hirosa.py / 30_gai_no_hirosa.txt / 31_daichou_rashiki_kami.list  ㋓ 害の広さ
  raw/40_fusagikata.py / 40_fusagikata.txt           ㋔ 塞ぎ方 五案
  raw/50_imi_senu.py / 50_imi_senu.txt               ㋕ 數が意味せぬ事
  raw/60_kin_no_junshu.py / 60_kin_no_junshu.txt     ★禁の遵守を數で示す(五つの示し方)★
  raw/90_shodan.py                                   本紙を書いた器
  fixtures/c1_chigau .. c5_kuuhaku_dake              ㋒ の五條の實物
  manifest.txt                                       束内相対の臺帳(append.py のみが足した)
  mon_<HHMMSS>.log                                   門の控(★臺帳へ入れて居らぬ・走る毎に別名★・二本在る)
""".format(ima=ima)
kaki.kaku(os.path.join(B, "00_shodan.md"), t)
print("wrote 00_shodan.md")
