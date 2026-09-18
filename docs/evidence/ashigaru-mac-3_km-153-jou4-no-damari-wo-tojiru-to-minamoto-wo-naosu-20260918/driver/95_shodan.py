# -*- coding: utf-8 -*-
"""★初段(本紙)を器で書く★ ―― 數は悉く raw/ の TSV から引き、此の紙に焼き込まぬ。
km-159 の 95 弾と同形。四札: 刻=冠 / 根=cwd / rc=各 driver の returncode(既出) / 対照=各節に明記。
★此の紙は臺帳の數(自身を含む)を書かぬ★(裁: 紙は己を含む臺帳の數を書けぬ)。"""
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaku = import_module("00_kaki").kaku


def tsv(rel):
    p = os.path.join(BUNDLE, rel)
    assert os.path.isfile(p), "★無し★ %s" % rel
    ro = [l.split("\t") for l in open(p, encoding="utf-8").read().split("\n") if l != ""]
    assert len(ro) >= 2, "★行が足らぬ★ %s" % rel
    return ro[0], ro[1:]


def hiku(rows, key, col, ki=0):
    """行の ki 列目が key で始まる行の col 列目を引く。★1 件で無ければ止める★"""
    hit = [r for r in rows if r[ki].startswith(key)]
    assert len(hit) == 1, "★%s が %d 件 ―― 引き方を直せ★" % (key, len(hit))
    return hit[0][col]


_, KITEI = tsv("raw/10_nikitei.tsv")
_, MATSUBI = tsv("raw/41_matsubi_nibyte.tsv")
_, ATE = tsv("raw/50_atenashi_apply_check.tsv")
_, SUNAO = tsv("raw/51_apply_check_no_kizu.tsv")
_, KIKIME = tsv("raw/60_kou_no_kikime.tsv")
_, ZAIHI = tsv("raw/70_utsuwa_no_zaihi.tsv")
_, MINAMOTO = tsv("raw/71_minamoto_no_kikime.tsv")
_, SAIHAN = tsv("raw/81_saihan_kazu.tsv")

shin_gyou = hiku(KITEI, "新基底", 4)
kyuu_gyou = hiku(KITEI, "旧基底", 4)
shin_sha = hiku(KITEI, "新基底", 5)
kyuu_sha = hiku(KITEI, "旧基底", 5)

kou_zen, kou_tasu, kou_hiku = (hiku(ATE, "甲", 2), hiku(ATE, "甲", 3), hiku(ATE, "甲", 4))
kou_rck, kou_rcs = (hiku(ATE, "甲", 5), hiku(ATE, "甲", 7))
hei_rck, hei_rcs = (hiku(ATE, "丙", 5), hiku(ATE, "丙", 7))
haz_rck, haz_rcs = (hiku(ATE, "外れ", 5), hiku(ATE, "外れ", 7))
sunao_zero_rc = len([r for r in SUNAO if r[1] == "0"])          # 素で rc=0 に成つた枚数
# ★rc の欄(1 と 4)で数へる ―― 文言の欄で数へると方言違ひで 0 が出る(初めに「食ひ違」を 6 列目で
#   探して 0 を得た ―― 6 列目の文言は「★素の走りは判ぜぬ★」であり『食ひ違』の語を含まぬ)★
sunao_gi = len([r for r in SUNAO if r[1] != r[4]])
# ★二つの欄で同じ數が出る事を検める(文言の欄 = 2 列目の『食ひ違』)★
_gi2 = len([r for r in SUNAO if "食ひ違" in r[2]])
assert sunao_gi == _gi2, "★食ひ違ひの數が rc 欄 %d / 文言欄 %d で合はぬ★" % (sunao_gi, _gi2)
assert 0 < sunao_gi <= len(SUNAO), "★食ひ違ひ %d 枚 ―― 引き方を疑へ★" % sunao_gi

ugoita = [r[0] for r in KIKIME if "動いた" in r[5]]
onaji = [r[0] for r in KIKIME if "動いた" not in r[5]]

toshi = [r for r in MINAMOTO if "器を通す" in r[1]]
sunao_m = [r for r in MINAMOTO if "通さぬ" in r[1]]
toshi_zero = len([r for r in toshi if r[4] == "0"])
sunao_zero = len([r for r in sunao_m if r[4] == "0"])
toshi_ochi = len([r for r in toshi if r[6] != "0" or r[8] != "0"])
sunao_ochi = len([r for r in sunao_m if r[6] != "0"])

kei_gyou = hiku(SAIHAN, "★計★", 1)
kou3 = hiku(SAIHAN, "甲_", 1)
otsu = (hiku(SAIHAN, "乙_", 1), hiku(SAIHAN, "乙_", 2))
hei3 = (hiku(SAIHAN, "丙_", 1), hiku(SAIHAN, "丙_", 2))

koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

HON = """# km-153 初段 ―― ★條④の黙りを名指し、源で直す形を出し、己の「器の所為」を再判する★

* 席 = ashigaru-mac-3(專任3・pane multiagent-mac:0.3)／弾 = 第61弾
* 札 = `km-153-jou4-no-damari-wo-tojiru-to-minamoto-wo-naosu-20260918`(家老mac 05:34:44 下命)
* 刻 = {koku}(as-of {utc} UTC)／根 = `{root}`
* 條 = 臺帳は束内相対(裁 seq322699)／門は `KM_GATE_MANIFEST_BASE=.` で二走・対照の名を別に／便は 300 字以内
* ★門は変更統制(理事長令 2026-08-11) ∴ 當席は據ゑず、材(當て紙)と數のみを出す★

## 0. 二基底 ―― 何に対して測つたか

| 名 | 出所 | LF行 | sha256 |
|---|---|---|---|
| 旧基底 | 共用樹 disk(★未commit の三つ目の版★・此の席が現に走らせて居る物) | {kyuu_gyou} | `{kyuu_sha}` |
| 新基底 | origin/main blob `04672e15` | {shin_gyou} | `{shin_sha}` |

HEAD(310行 `9cd550fc`)は當て紙の基底に用ゐて居らぬ(raw/10 に控のみ)。
★三版が併存して居る事が本弾の前提である★ ―― 「門」と言つた時に何処の門かで答が変る。

## 1. ㋐ ―― 條④を黙らせて居る行を名指す

### 名指し(逐語)

* ★旧基底 167 行目★ `elif [ "$last2" = "0a0a" ]; then`
* 之を養つて居るのは ★163 行目★ `last2=$(tail -c2 "$f" 2>/dev/null | xxd -p 2>/dev/null | tr -d ' \\n')`
* 鳴り口(168 行目 `say "★EOF改行が複数(末尾に空行) ―― ${{f}}★"`)に疵は無い ―― ★届いて居らぬだけ★ である。

### 何故黙るか(raw/41 實測・末尾2byte)

| 札 | byte | 末尾2byte | 167 行との照合 |
|---|---|---|---|
{matsubi}

∴ 末尾行が空(又は不可視字のみ)である三形の内 ★素の空行 一形だけ★ が鳴り、CRLF 空行と U+3000 一字の行は黙る。
之が當席が km-150 で見た黙りの正体である ―― ★「2 byte を見る」取り方が「一行を見る」問に答へて居らぬ★。

新基底は此の口を捨てて居る: ★180 行目★ `case "$fk4" in` ―― 兄弟器 `karo_mac_fukashiji.py` の札
(0=良/1=EOF改行無/2=末尾行が不可視のみ/3=0byte)で分ける(裁 seq330497)。
∴ 三形が同じ札 2 に入り、fx05 fx06 fx07 が悉く鳴る(raw/30)。

### 當て紙と apply --check の rc(raw/50)

| 當て紙 | 全行 | + | - | 旧基底 rc | 新基底 rc |
|---|---|---|---|---|---|
| 甲(條④の黙りを閉ぢる) | {kou_zen} | {kou_tasu} | {kou_hiku} | {kou_rck}(當たる) | {kou_rcs}(當たらぬ) |
| 丙(★陽性対照★・新基底で書いた・挙動を変へぬ一行) | - | 1 | 0 | {hei_rck} | {hei_rcs}(當たる=器は働く) |
| 外れ(★陰性対照★・両基底に無い行) | - | 0 | 1 | {haz_rck} | {haz_rcs}(両基底とも當たらぬ=正) |

★甲が新基底に當たらぬのは當て紙の失敗ではない ―― 錨の行が新基底に 0 件、即ち疵が上流で既に閉ぢて居る★。

器の疵も併せて記す(raw/51): 子dir から素に `git apply --check` を走らせると、dir の外を指す path を
★黙つて跳ばし rc=0 を返す★(`-v` で `Skipped patch`)。三枚 ★悉く({sunao_zero_rc}/3)rc=0★ に成り、
其の内 ★{sunao_gi} 枚は判と食ひ違ふ(=偽の通)★・残り 1 枚(丙)は ★真に當たる紙ゆゑ偶々一致した★ に過ぎぬ。
∴ 本弾は `GIT_DIR` を在らぬ路へ向けて repo 探しを断つてから當てて居る。★素の走りは判ぜぬ★。

### 甲の効き目(raw/60 ―― 當てたのは `_fx/kentei/kou_atta/` の複製のみ)

* ★動いた = {ugoita_n} 本★: {ugoita}
* 同じ = {onaji_n} 本: {onaji}
* ★限界を隠さぬ★: fx06(U+3000 一字の行)は當てた後も rc=0 ―― 末尾行は「空」でなく「見えぬ一字」ゆゑ甲の口に入らぬ。
  形(U+3000/U+00A0/U+2003/U+FEFF…)を数へ上げる仕方では ★永久に閉ぢぬ★ ∴ codepoint の ★類★ で判ずる器が要る。
  上流は其れを兄弟器で据ゑた ∴ 當席の断は「甲は材、★本筋は版の入替★」である。

### 語の註 ―― 表の札を其の儘読むな

fx05 の當てた後の鳴りが『條④(旧・末尾2字 0a0a の口)』と出るのは、甲が ★say の文言を逐語で引き継いだ★ 故である。
口は既に「末尾2字の一致」ではなく「末尾一行が空か」である。語彙表(raw/30)は文言で引く ∴ 札は古い名で出る。

## 2. ㋑ ―― 源で直す形(裁 seq310228⑶)

器 = `scripts/checks/karo_mac_kara_wo_ichigyo.sh`(37 行・origin/main の blob)。
`<out> <err> -- <命令...>` を取り、寸法 0 の出目へ ★「空である旨の一行」★ を書き、★命令の rc を其の儘返す★。

### 在否(raw/70)

| 問 | rc | 判 |
|---|---|---|
{zaihi}

### 實測(raw/71)

| 経路 | 口 | 0byte | 門の落ち |
|---|---|---|---|
| ★器を通す★ | {toshi_n} | {toshi_zero} | {toshi_ochi}(旧・新 両基底とも通) |
| 素の `> out 2> err` | {sunao_n} | {sunao_zero} | {sunao_ochi}(旧基底・條④ 0byte の口) |

* rc は握り潰されて居らぬ ―― 「何も言はぬ失敗」で器は 1 を返した。
* 當席の `driver/00_kaki.py` の KARA 一行も同じ形である ―― fx03 は両基底で rc=0 で通る(raw/60)。
* ★然し現場は直つて居らぬ★: 器は disk にも HEAD にも無く origin/main にのみ在る。
  ∴ 此の席で素に `cmd > x.out 2> x.err` と書けば ★今も 0byte が出来る★。
  治めは當て紙ではなく ★版の入替★ であり、変更統制 ∴ 當席は據ゑぬ。
* 除いた物を宣する: 陽性対照として 0byte で在らねばならぬ fx01/fx02 の ★2 本★ は器を通して居らぬ
  (器の冠 15 行目が之を禁ずる)。★「除いた」は「歩いて居らぬ」に非ず★。

### ★㋑ を己の束へ當てた ―― 門が當席の 0byte を名指した★

本弾の臺帳を積む前に門を走らせた處、條④が ★當席自身の捕り三本★ を名指した:
`_letters/11_yomikaeshi.err` / `_letters/12_mark_read.err` / `_letters/20_chakushu.send.out`。
三本は悉く ★㋓ の便器より前に端末で組んだ頃の物★ で、殻の `>` が 0byte を作つて居た。
∴ `driver/96` で ★源の形(KARA 一行)へ直した★ ―― argv から除いて通したのではない。
0byte で在る事が中身である對照(raw/fx の二本・raw/70_minamoto の五本)は ★直さず宣して除いた★。
始末は一本づつ `_gate/15_zero_wo_ichigyo.tsv` に、『直した』と『此の走りで 0 を見た』を分けて書いて在る
(器は冪等ゆゑ二度目の走りでは 0 を己の目で見ぬ)。

## 3. ㋒ ―― 己の「器の所為にした断」を数へ、今日の眼で再判する

母數の取り方(raw/80): 歩き根 `docs/evidence/ashigaru-mac-3_*`・深さ無制限・`.md/.txt/.tsv`・`__pycache__` 除。
歩いた紙 492 本/束 9 個、当たり行 45(★過去 22 / 本弾 23 は別列★)、二方言以上 5。
方言 7 形(甲 器の性/乙 器の所為/丙 本紙の疵ではない/丁 本紙の疵に非ず/戊 濡れ衣/己 器を疑へ/庚 器の疵)。
★陽性対照は歩く前に `raw/80_taishou.txt` へ書き、同じ路で 1 件当たる事を確かめて居る★。

### 再判(raw/81 ―― 母數 {kei_gyou} 行・一行も落して居らぬ)

| 今日の判 | 行 | 断の実体 |
|---|---|---|
| 甲_断に非ず(器の出目・控・引用) | {kou3} | 0 |
| 乙_今も立つ | {otsu0} | {otsu1} |
| ★丙_改めた★ | {hei30} | {hei31} |

改めた二件:

* **d5**(0byte は器の性) ―― ★既に km-150 §4 で己の手で破つて在る★。本弾 ㋑ の實測が同じ事を數で示した。
  因は器ではなく ★捕りを殻の `>` で書いた當席★ に在る。
* **d3**(NUL を含む紙に條②が鳴るは濡れ衣) ―― ★本弾で新たに改める★。
  門の契約は字の紙であり NUL を含む紙は ★契約外★ ∴ 正しい書き方は「器の疵」でも「紙が汚い」でもなく
  ★『門の出目は此の紙に対して定義されて居らぬ ―― 宣して除くか字へ直す』★ である。

### 己に課す形(之が㋒の実である)

* 疵を器へ移す時は ★①器の何行目が ②何の入力で ③何と出たか★ の三つを逐語で並べる。三つ揃はぬ時は『測れぬ』と書く。
* 『器の性であり本紙の疵ではない』の如き ★一文で責を移す形★ は用ゐぬ(km-147 の一文が現に誤つて居た)。

## 4. ㋓ ―― 便器を束へ焼き込む(km-159 疵⑵ の治め)

`driver/90_tegami_wo_okuru.py` ―― `<胴の紙> --to karo|gunshi [--parent-seq N] [--dry]`。
①胴が一行で末尾改行が丁度一つである事を検め ②★300 字を超えたら送らずに止める★ ③管を通さず rc を取り
④`.send.out/.err/.rc` を kaki で書き ⑤`seq=` を `parent_seq=` と取り違へぬ正規表現で引き
⑥★読み返して胴を検める(第八の衛)★ ⑦臺帳 `_letters/90_tegami_choudai.tsv` へ追記する。

対照二つ:

* dry 対照 `_letters/90_dry_taishou.txt`(65 字) → rc=0・臺帳に ★送つて居らぬ(対照)★ と載る。
* 字数対照 `_letters/91_sugiru_taishou.txt`(301 字) → ★rc=1 で送らず★
  `★301 字 ―― 條の 300 字を超えた。★送らずに止める★(1 字 截れ)`。

### ★自訂 ―― 隠さぬ★

本弾の先の二便(`_letters/10_osame_km159_gunshi.txt` seq=332101 / `_letters/20_chakushu_eta.txt`)は
★此の器より先に、端末で組んで送つた物★ である。控は束に在るが、器を通して居らぬ。
以後の便(納め・監査提出)は悉く此の器を通す ―― ★之が km-159 疵⑵ の治めである★。

## 5. 宣と實

* 宣 ETA = 2026-09-18T16:30+0900(`_letters/20_chakushu_eta.txt`)
* 實 = 本紙の刻 {koku}
* ★宣は當たらぬ方へ倒れる癖が在る(km-40〜45 で 1.8〜6倍 超過)★ ∴ 宣を書いた事は達した事ではない。

## 6. ★本弾で己が出した疵(三件・悉く己が見つけ己が直した)★

* **疵⑴ 判の欄が三つの類を一つに畳んで居た**(`driver/40`) ―― 末尾2byte が `0a0a` で無い紙を一律
  『★合はぬ ∴ 黙る★』と書いた。★其の中に「黙るのが正しい清い紙(fx03/fx04)」と「黙つては成らぬ紙(fx05/fx06)」が
  混じつて居た★ ∴ 表を読んだ者は清い紙も疵と読む。治め = 判を四類(寸法<2 / 合ふ / ★空・不可視のみ ∴ 黙りが疵★ /
  可視字在り ∴ 黙るのが正)に割つた。
* **疵⑵ 『偽の通』の札を無条件に貼つて居た**(`driver/50` → raw/51) ―― 素の走りで rc=0 に成つた三枚を悉く
  『通(★偽★)』と書いた。★丙は真に當たる紙ゆゑ其の 0 は判と一致して居る★ ―― 偽であるのは
  ★判と食ひ違ふ★ 事で定まる。治め = 札を `rc_n != rc_y` で分けた(甲・外れ = 偽 / 丙 = 偶々一致)。
* **疵⑶ 數を引く欄を違へた**(`driver/95` 本紙の器) ―― 食ひ違ひの枚数を初め「三枚」と焼き込み、
  次に文言で `食ひ違` を ★7 列目★ から探して ★0 枚★ を得た。7 列目の文言は「★素の走りは判ぜぬ★」であり
  『食ひ違』の語を含まぬ ―― ★語で数へて 0 が出たのに、其の 0 を疑はず紙へ載せた★ のが疵である。
  治め = rc の欄(1 と 4)で数へ、文言の欄と ★二つの數が合ふ事を assert で検めた★(合はねば止まる)。
* 三件に共通する形: ★『數を刷つた器そのものが誤り得る』★ ―― ㋒ で己に課した三点(何行目・何の入力・何と出たか)は
  己の器にも掛かる。

## 7. 之が意味せぬ事(全節に掛かる)

* ★門は一行も直つて居らぬ★ ―― 當てたのは `_fx/kentei/` の複製のみ。共用樹の門の sha256 は前後で不動(raw/60_kou_wo_ateta_kiroku.txt)。
* 七本の札(raw/fx)は ★當席が拵へた陽性対照★ であり、現に世に在る紙の分布ではない。
* 再判の 22 行は ★語で引いた上限★ である ―― 方言表に無い言ひ方で責を移した断は此の數に入つて居らぬ。
* 「改めた 2 件」は ★過去の紙を書き換へた事ではない★(提出済の紙は直さぬ) ―― 本紙に自訂として残す形である。
* 上流が閉ぢた事は ★此の席が安全に成つた事ではない★ ―― 走つて居るのは旧基底(disk・未commit)である。
"""

body = HON.format(
    koku=koku, utc=utc, root=ROOT,
    kyuu_gyou=kyuu_gyou, shin_gyou=shin_gyou, kyuu_sha=kyuu_sha, shin_sha=shin_sha,
    matsubi="\n".join("| %s | %s | %s | %s |" % (r[0], r[1], r[2], r[3]) for r in MATSUBI),
    kou_zen=kou_zen, kou_tasu=kou_tasu, kou_hiku=kou_hiku,
    kou_rck=kou_rck, kou_rcs=kou_rcs, hei_rck=hei_rck, hei_rcs=hei_rcs,
    haz_rck=haz_rck, haz_rcs=haz_rcs, sunao_gi=sunao_gi, sunao_zero_rc=sunao_zero_rc,
    ugoita_n=len(ugoita), ugoita="・".join(ugoita), onaji_n=len(onaji), onaji="・".join(onaji),
    zaihi="\n".join("| %s | %s | %s |" % (r[0], r[2], r[3]) for r in ZAIHI),
    toshi_n=len(toshi), toshi_zero=toshi_zero, toshi_ochi=toshi_ochi,
    sunao_n=len(sunao_m), sunao_zero=sunao_zero, sunao_ochi=sunao_ochi,
    kei_gyou=kei_gyou, kou3=kou3, otsu0=otsu[0], otsu1=otsu[1], hei30=hei3[0], hei31=hei3[1],
)
assert "{" not in body.replace("${", "@").replace("{f}", "@").replace("{MAXB}", "@"), "★焼き残りの括弧が在る★"
kaku(os.path.join(BUNDLE, "00_shodan.md"), body)
print("初段を書いた ―― %d 字 / %d 行" % (len(body), body.count("\n") + 1))
print("  ㋐ 旧167行 / 甲 %s行 +%s-%s 旧rc=%s 新rc=%s ―― 動いた %d 本" % (kou_zen, kou_tasu, kou_hiku, kou_rck, kou_rcs, len(ugoita)))
print("  ㋑ 通し %d口 0byte=%d / 素 %d口 0byte=%d" % (len(toshi), toshi_zero, len(sunao_m), sunao_zero))
print("  ㋒ 母數 %s行 ―― 甲%s 乙%s(%s件) 丙%s(%s件)" % (kei_gyou, kou3, otsu[0], otsu[1], hei3[0], hei3[1]))
