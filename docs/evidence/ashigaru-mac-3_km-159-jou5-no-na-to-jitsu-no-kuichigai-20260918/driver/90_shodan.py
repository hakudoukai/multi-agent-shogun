# -*- coding: utf-8 -*-
"""初段を書く ―― ★數は悉く raw/*.tsv から引く。打たぬ。★
四札: 刻=冠 / 根=cwd / rc=各表の rc 欄(悉く returncode・管を通さず) / 陽性対照=各節に明記。"""
import os
import sys
import csv
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaku = import_module("00_kaki").kaku

def tsv(name):
    with open(os.path.join(BUNDLE, "raw", name), encoding="utf-8") as f:
        r = list(csv.reader(f, delimiter="\t"))
    return r[0], r[1:]

def bun(name):
    return open(os.path.join(BUNDLE, "raw", name), encoding="utf-8").read()

def hyou(head, rows, keep):
    i = [head.index(k) for k in keep]
    o = ["| " + " | ".join(keep) + " |", "|" + "|".join(["---"] * len(keep)) + "|"]
    for r in rows:
        o.append("| " + " | ".join((r[j] if j < len(r) else "").replace("|", "\\|") for j in i) + " |")
    return "\n".join(o)

# ―― 引く ――
h65, r65 = tsv("65_kitei.tsv")
h76, r76 = tsv("76_futatsu_no_kitei_naoshi.tsv")
h77, r77 = tsv("77_sakaime_naoshi.tsv")
h21, r21 = tsv("21_jisshin_ka_hasshin.tsv")
h75, r75 = tsv("75_kyoudai_ki.tsv")
h78, r78 = tsv("78_kyoudai_no_umu.tsv")
h85, r85 = tsv("85_atenashi_futatsu_no_kitei.tsv")
h88, r88 = tsv("88_apply_check_no_kizu.tsv")
h95, r95 = tsv("95_uchiyou_futatsu.tsv")
h92, r92 = tsv("92_bundle_no_uchiwake.tsv")
h94, r94 = tsv("94_nozoku_mono_no_joudaku.tsv")

def gun_hyou(head, rows):
    """★手打ちの數を廃す★ ―― raw/92 の一行づつを頭の群へ畳んで数へる。
    此の數が意味せぬ事: 束の最終形ではない(raw/92 の歩きの刻の物。_gate は臺帳より後に出来る)。"""
    ci, cn = head.index("臺帳に"), head.index("除く理由")
    ki, mi = [], {}
    for r in rows:
        g = r[0].split("/")[0]
        if g not in mi:
            ki.append(g); mi[g] = [0, r[ci], r[cn]]
        mi[g][0] += 1
    o = ["| 群 | 本数 | 臺帳に | 理由 |", "|---|---|---|---|"]
    for g in sorted(ki):
        n, noseru, wake = mi[g]
        o.append("| `%s` | %d | %s | %s |" % (g, n, noseru, wake.replace("|", "\\|")))
    o.append("| ★和★ | %d | ―― | 歩いた全 file(__pycache__ を除く) |" % sum(v[0] for v in mi.values()))
    return "\n".join(o)


def hiku(rows, head, key, col):
    c = head.index(col)
    for r in rows:
        if r[0].startswith(key):
            return r[c]
    return "-"

KYUU = hiku(r65, h65, "★旧基底★", "値")
SHIN = hiku(r65, h65, "★新基底★", "値")
kawa = sum(1 for r in r76 if "変つた" in r[h76.index("判")])
fudo = len(r76) - kawa
k_yurui = sum(1 for r in r95 if r[h95.index("旧 rc")] == "0")
s_yurui = sum(1 for r in r95 if r[h95.index("新 rc")] == "0")
s_tomari = sum(1 for r in r95 if r[h95.index("新 rc")] == "2")
tou = len(r95)
kizu_nise = sum(1 for r in r88 if r[h88.index("素の rc")] == "0")
GATE = "scripts/checks/karo_mac_dasumae_gate.sh"
ima = datetime.datetime.now(datetime.timezone.utc)
jst = ima + datetime.timedelta(hours=9)

md = """# 初段 ―― km-159 條⑤ ★名と實の食ひ違ひ★(專任3 第60弾)

- 刻: as-of %s(UTC) = %s(JST)
- 根: `%s`
- 札: `km-159-jou5-no-na-to-jitsu-no-kuichigai-20260918`
- 束: `docs/evidence/ashigaru-mac-3_km-159-jou5-no-na-to-jitsu-no-kuichigai-20260918/`
- 的: 出す前 門 `%s` の條⑤(寸法)
- ★據ゑて居らぬ★: 当て紙と `git apply --check` の rc までで止めた(変更統制)。共用樹の file は ★一つも触つて居らぬ★(読むのみ)。

## 〇 本弾の結論を先に三行

1. ★當席が km-159 で問うた疵は、二つとも origin/main では既に閉ぢて居る★(裁 seq330497)。之を「当て紙が失敗した」とは書かぬ。
2. ㋐ 閾の壊れた綴りは、旧基底では ★%d 形が「fail-closed」と刷りつつ rc=0 で通り★、新基底では ★rc=2 で止まる★(形 %d 件が変り %d 件は不動)。
3. ㋑ 「超」は新基底で「★以上★(比べは -ge ゆゑ「超」に非ず)」へ直つて居る ―― rc は三点とも不動。

## 一 基底を引き直した ―― 何に当てるべきかが変つた

家老 09:00:05 の命により、当て紙の相手を ★origin/main★ へ引き直した(PR#27 merge 済)。

%s

- ★新基底★ = origin/main の blob を byte 忠実に束へ引いた `base_gate.sh`。★kaki を通さぬ唯一の出目★(通せば sha が動き、`git apply` が当たらなく成る)。
- ★旧基底★ = 共用樹 disk の門。commit にも main にも一致せぬ ★未commit の三つ目の版★。触らず、読むのみ。
- 旧基底で書いた当て紙 `raw/60`・`raw/61` は ★捨てず★、「旧基底で書いた物」と明記して残した(命の逐語)。

## 二 ㋐ 閾の四形(實は十一形) ―― rc 0→2 へ

母數 = 形 %d(★網羅に非ず ―― 現に測つた標本★)。陽性対照 = 「正 数(小)」= 閾1 で現に鳴る(rc=1)。

%s

- 旧基底: 此の %d 形は「既定 10485760 へ倒す(★fail-closed★)」と刷りながら ★rc=0 で通した★ ―― 名と實の食ひ違ひ。
- 新基底: 同じ %d 形が `fix_threshold` で止まり ★rc=2★。数を出さぬ ∴ ★通して居らぬ★。
- ★形0 未設定は新基底でも既定へ倒れ rc=0 で通る。之は穴ではないと断ずる★ ―― 「未設定」=値を与へて居らぬ / 「空文字」=値を与へ損ねた、の別物。未設定まで止めれば閾を設けぬ全ての呼び手で門が死ぬ。main の分け方を是とする。

## 三 ㋑ 境目の三点 ―― 語が一つ厳しい側へずれて居た

byte和 85。比較器は `[ "$total" -ge "$MAXB" ]` = ★以上★。

%s

∴ ★和=閾★ の一点だけで、旧基底は「超(=より大きい)」と刷りながら鳴つて居た。新基底は「以上」と刷る ―― ★rc は三点とも不動★(挙動は元より正しく、誤つて居たのは語のみ)。

## 四 ㋒ `[ ]` は 010 を十進で讀む

%s

八進なら 010=8 で和85は以上→鳴る、十進なら 010=10 で同じく鳴る ―― ★此の値では分かれぬ★。分かれる値(0100 は 十進100 で鳴らず/八進64 で鳴る)で決した。
★∴ 真の fail-open は八進誤読ではなく、2^63以上 → 比較器が倒れる → 既定へ落ちる、の路である★(旧基底のみ)。

## 五 ㋒' 打ち様 十通り ―― 緩い側へ倒れた %d が %d に成つた

意図した閾=50(和85>50 ∴ 意図通りなら必ず鳴る)。陽性対照=「正しく打つ」。

%s

- 旧基底: ★%d/%d が緩い側(既定 10485760)へ倒れて通つた★ ―― 打つ者は「閾50を効かせた」と信じたまま、実際は 10MB で通つて居た。
- 新基底: 同じ %d が ★rc=2 で止まる★。★「止まつた」は「通した」ではない★。

## 六 ㋓ byte和の母數(本弾が宣する定義)

%s

## 七 ㋕ 当て紙 ―― 二基底へ当てた(據ゑて居らぬ)

%s

- 甲(語「超」→「以上」)・乙(倒した閾で通すな)は ★旧基底にのみ当たる★。錨の行が新基底に 0 件 ―― ★疵が上流で閉ぢて居るから★。
- 丙 = ★新基底から書いた陽性対照★。新基底に当たる(rc=0)∴ 「当たらぬ」は器の不調ではない。
- 外れ = 陰性対照。両基底とも当たらぬ(rc=1)。
- ★∴ 新基底に対して當席が出すべき当て紙は無い。★

## 八 己の疵 三つ ―― 捨てず残す

### 疵㋐ 新基底を兄弟器無しで走らせた(當席の据ゑ方の疵・門の疵に非ず)

門は `$(dirname "$0")/karo_mac_fukashiji.py` を名指す。門一本だけ束へ置いて走らせた第一走は、正しい閾でも rc=1 と成つた ―― 逐語「條②④ 測れぬ(不可視字の判じ手 rc=2)」。

%s

陽性対照として ★兄弟器を抜いた走りを故意に再現★ した:

%s

`raw/70`・`raw/71` は其の儘残す(捨てず)。正しい対照は `raw/76`・`raw/77`。

### 疵㋑ `git apply --check` が repo の子dir から走ると ★黙つて跳ばし rc=0★

%s

- 素の走りでは ★%d 枚が悉く rc=0「通」★ ―― 陰性対照(器に無い行)まで「通」と出た。`-v` を付けて初めて `Skipped patch '...'` が見えた。
- `GIT_DIR` を在らぬ path へ向け repo 探しを断つと、初めて判ずる。
- ★教訓: 陰性対照が「通」と出たら、器を疑へ。★ 之が無ければ當席は「甲乙は新基底にも当たる」と誤つて書いた。

### 疵㋒ 節十一の群表を ★手で打つて居た★ ―― 束が育つても數が動かなんだ

當初 `driver/90` は群の本数を本文へ直に書いて居た(`_fx` 13 / `driver` 14 / `raw` 63)。
束が育つた後も其の數は動かず、`raw/92` の實(14 / 15 / 68)と食ひ違つた。
更に `MANIFEST.txt`(1) と `_gate`(11) の二群を ★表から落として居た★ ∴ 和が歩きの 113 に届かなんだ。

| 群 | 手打ちの數 | raw/92 の實 | 差 |
|---|---|---|---|
| `_fx` | 13 | 14 | +1 |
| `driver` | 14 | 15 | +1 |
| `raw` | 63 | 68 | +5 |
| `MANIFEST.txt` | (表に無し) | 1 | ★落ちて居た★ |
| `_gate` | (表に無し) | 11 | ★落ちて居た★ |

直し: `gun_hyou()` を据ゑ、`raw/92` の一行づつを頭の群へ畳んで数へる ―― ★和の行も刷る★(落ちを見える化)。
★教訓: 器が数へられる物を本文へ手で書くな。★ 手打ちの數は束が育つた刹那に嘘へ変はる。

## 九 ㋔ 四札

| 札 | 本弾での立て方 |
|---|---|
| 刻 | 各 raw/*.txt の冠に as-of(UTC)。本紙冠に UTC/JST 両刻 |
| 根 | `%s`(全 driver が `os.chdir(ROOT)`) |
| rc | 悉く `subprocess.run(...).returncode`。★管を通さぬ★ |
| 陽性対照 | 閾1(節二)/ 「正しく打つ」(節五)/ 丙 当て紙(節七)/ 兄弟器抜き(節八)/ 在らぬ ref(節一) |
| 陰性対照 | 外れ当て紙(節七)・在らぬ ref 128(節一) |

## 十 此の數が意味せぬ事

1. 形 %d・打ち様 %d は ★網羅ではない★ ―― 「比較器が扱へぬ綴り」の全体ではなく、現に測つた標本。
2. 新基底で「止まつた(rc=2)」は ★通した★ ではない。数を出さずに止めて居る。
3. 「疵が閉ぢた」は ★此の標本に於て★ であり、條⑤の全ての入力に就いてではない。
4. ★新基底は此の樹では其の儘走らぬ★ ―― `karo_mac_fukashiji.py` が共用樹 disk にも本枝 HEAD にも無い。merge 前に門だけ差し替へると條②④が ★濡れ衣で落ちる★。
5. 束の byte和は ★束の大きさ★ ではなく ★其の走りで argv に名指した file の和★ である。

## 十一 臺帳の及ぶ範囲 ―― ★除く物も歩いてから除いた★

束の全 file を歩き、載す/除くを一本づつ宣した(`raw/92`)。

%s

除く物は ★除く前に門へ掛けて汚濁を測つた★:

%s

- ★四本とも鳴らず(rc=0)★ ―― 除いたのは「汚れて居るから」ではなく、★當席が書いた紙ではない / 己を己で照らせぬ★ からである。
- 之は「_fx が悉く清い」の意ではない。門へ掛けたのは此の四本のみで、`_fx/atenashi/` 等は掛けて居らぬ。
- 器は己の産物を数へられぬ ∴ ★歩きを二度行ひ、差を刷つた★(`raw/97`・`raw/98`):

%s

## 十二 宣ETA と 實測

- 宣ETA = ★2026-09-18 11:00(JST)★(`_letters/00_sengen_eta.txt`)
- 實測 = ★%s(JST)★
- ★超過の因★: 09:08 頃に API 断で走りが止まり、総監督より 12:21 復した旨の報せを受けて再開した。★停まつた間は測つて居らぬ★ ―― 之を「作業して居た」と数へぬ。
- 因は其れだけではない: 家老 09:00 の命で ★基底を引き直した★(当て紙の相手が変つた)為、測りを旧基底から二基底の対照へ組み直した。之は宣ETA を立てた時点で見えて居なかつた。
""" % (
    ima.strftime("%Y-%m-%d %H:%M:%S"), jst.strftime("%Y-%m-%d %H:%M:%S"), ROOT, GATE,
    kawa, kawa, fudo,
    hyou(h65, r65, ["物", "値", "rc", "判", "註"]),
    len(r76),
    hyou(h76, r76, ["形", "与へた値", "旧基底 rc", "新基底 rc", "新は何が鳴つたか", "判"]),
    kawa, kawa,
    hyou(h77, r77, ["点", "byte和", "閾", "實の関係", "旧が刷る語", "旧 rc", "新が刷る語", "新 rc", "名と實"]),
    hyou(h21, r21, ["与へた閾", "十進と讀めば", "八進と讀めば", "實", "rc", "判"]),
    k_yurui, s_yurui,
    hyou(h95, r95, ["打ち様", "与へた値", "旧 rc", "旧の判", "新 rc", "新の判", "基底の間で"]),
    k_yurui, tou, s_tomari,
    bun("41_bogen_sengen.txt").strip(),
    hyou(h85, r85, ["当て紙", "旧基底 rc", "旧基底", "新基底 rc", "新基底", "意"]),
    hyou(h75, r75, ["兄弟器(main より)", "byte", "共用樹 disk", "本枝 HEAD", "門との関はり"]),
    hyou(h78, r78, ["据ゑ方", "rc", "何が鳴つたか"]),
    hyou(h88, r88, ["当て紙", "素の rc", "素の判", "GIT_DIR を断つた rc", "其の判", "食ひ違ひ"]),
    kizu_nise, ROOT, len(r76), tou,
    gun_hyou(h92, r92),
    hyou(h94, r94, ["除く path", "何か", "門の rc", "判"]),
    "\n".join("  " + l for l in bun("98_aruki_no_sa.txt").strip().split("\n")[2:]),
    jst.strftime("%Y-%m-%d %H:%M"),
)
kaku(os.path.join(BUNDLE, "00_shodan.md"), md)
print("初段 %d 字 / 形 %d(変%d 不動%d) / 打ち様 %d(旧通%d→新通%d 止%d) / 偽の通 %d" %
      (len(md), len(r76), kawa, fudo, tou, k_yurui, s_yurui, s_tomari, kizu_nise))
