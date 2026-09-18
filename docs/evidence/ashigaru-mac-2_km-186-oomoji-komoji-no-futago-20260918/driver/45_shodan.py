# -*- coding: utf-8 -*-
"""45 ―― 初段(00_shodan.md)を ★測つた紙からのみ★ 組む。手で數を打たぬ。
表は raw/*.tsv の逐語、〆は raw/*_shime.txt の逐語を其の儘 引く。
★己(45)と初段は臺帳の中に入る★ ―― 臺帳は此の後に建てる。
"""
import io
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402
R = os.path.join(KI, "raw")


def tsv(name):
    ls = [l for l in io.open(os.path.join(R, name), encoding="utf-8").read().split("\n") if l.strip()]
    return ls[0].split("\t"), [l.split("\t") for l in ls[1:]]


def hyou(name, retsu=None):
    h, rows = tsv(name)
    idx = range(len(h)) if retsu is None else retsu
    h2 = [h[i] for i in idx]
    o = [u"| " + u" | ".join(h2) + u" |", u"|" + u"---|" * len(h2)]
    for r in rows:
        r = r + [u""] * (len(h) - len(r))
        o.append(u"| " + u" | ".join((r[i].replace(u"|", u"｜") or u"―") for i in idx) + u" |")
    return u"\n".join(o)


def yomu(name):
    return io.open(os.path.join(R, name), encoding="utf-8").read().rstrip("\n")


# ★數は悉く紙から建てる★
h15, r15 = tsv("15_ref.tsv")
ref_hon = len(r15)
ki_hon = len(set(r[1] for r in r15))
# ★「組=1 の儘」は「悉くの樹に双子が在る」の意ではない★ ―― 三つに分けて数へる
kumi_ichi = sum(1 for r in r15 if r[4] == u"組=1")
kumi_zero = sum(1 for r in r15 if r[4] == u"組=0")
kumi_futa = sum(1 for r in r15 if r[4] not in (u"組=1", u"組=0"))
h20, r20 = tsv("20_kata.tsv")
md_oo = sum(int(r[1]) for r in r20 if r[4].endswith(u"True") and r[3] != u"悉く小文字")
md_ko = sum(int(r[1]) for r in r20 if r[4].endswith(u"True") and r[3] == u"悉く小文字")
code_oo = sum(int(r[1]) for r in r20 if r[4].endswith(u"False") and r[3] != u"悉く小文字")
code_ko = sum(int(r[1]) for r in r20 if r[4].endswith(u"False") and r[3] == u"悉く小文字")
h95, r95 = tsv("95_yomikaeshi.tsv")
bin_hon = len(r95)
bin_maru = sum(1 for r in r95 if u"丸ごと" in r[5])
okuri = [l for l in io.open(os.path.join(R, "90_okuri.txt"), encoding="utf-8").read().split("\n") if l.strip()]
okuri_karo = sum(1 for l in okuri if l.split("\t")[1] == u"karo-mac")
okuri_gunshi = sum(1 for l in okuri if l.split("\t")[1] == u"gunshi-mac")

MD = u"""# km-186 ―― ★大文字・小文字の双子を数へ、消す順を実射で確かめた★(専任2・裁332455／補正333611)

刻 = {t} ／ 席 = ashigaru-mac-2(專任2) ／ 親裁 = 332455 ／ 補正 = hosei_186_sai_333611
固定 commit = `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`(母數も canon も悉く此の樹で測つた)

## 〇 一行で

**双子は ★1 組だけ★。canon は ★小文字の名しか指して居らぬ★。然るに此の Mac では
其の名を開くと ★旧版 2596 bytes★ が出る ―― 二つの名が ★同じ実体(inode 10724954)★ を指して居る故である。**

∴ 「消す順が正本の生死を決める」は ★言葉ではなく数で確かめた★(下 ㋔)。
正順(⑴`rm --cached` → ⑵`checkout -- <小文字>`)で彫り、★共用樹は前後不動・push 0・gh 0★。

★命の字義から一つだけ外れた★ ―― ⑷の `git commit --only` は ★此の双子では彫れぬ★ 事を二度実測し、
素の `git commit` を用ゐた(下 ㋓續・便 f_only186)。★隠さず名指しし、御下知を仰いで居る。★

## ㋐ 母數 ―― 己で建てた

{s10}

### 全 ref も歩いた(他の双子が在るか)

ref = ★{ref} 本★ ／ 別々の樹 = ★{ki} 本★。★組が 2 以上に成つた ref = {kf} 本★。
内訳 ―― 組=1 の ref = {k1} 本 ／ ★組=0 の ref = {k0} 本(其の樹に双子が一本も無い ―― 古い枝・別系統)★。
★「1 組の儘」は「悉くの樹に双子が在る」の意ではない★。新たな双子が ★一組も出なかつた★ の意である。

{s15}

## ㋑ 二つの blob と、disk の一本

### git の側(固定 commit)

{t10k}

### disk の側(★同じ刻に同じ根で★)

{t10d}

★見よ★ ―― 大文字の名は ★親 dir の listdir に無い★のに ★開ける★。inode は二つとも同じ。
∴ ★実体は一本であり、其の中身は大文字の blob(2596 bytes)★。
★小文字の blob(3471 bytes)は此の Mac の disk に一度も現れて居らぬ。★

## ㋒ canon は孰れの名を指して居るか

`.md` 付き(= file を指して居る): ★大文字 {md_oo} 当り／小文字 {md_ko} 当り★
`.md` 無し(= error code を指して居る): 大文字 {code_oo} 当り／小文字 {code_ko} 当り ―― ★別に数へた★

{t20k}

{t20s}

{s20}

### 索引の一行と実体の食ひ違ひ ―― 名指し

{s25}

{t25}

## ㋔ 逆順の実射 ―― ★己の使ひ捨て worktree の中だけで撃つた★

{t35}

{s35}

## ㋓續 ⑷ の呪文 ―― ★字義通りでは彫れぬ★

{s40}

{s41}

## ㋓ 正順の彫り

{t50}

{s50}

## ㋔ 直しの案と ★戻し方★

紙 = `60_teian.md`(束の頂) ―― 何を／何故／★如何に戻すか(三通り)★／此の案が直さぬ事／判定と merge の路。

## ㋕ ★測れぬ物★

{s65}

## ㋖ 便 ―― {bin_hon} 通(家老 {ok} 通・軍師 {og} 通)

{t95}

★丸ごと在り = {maru}／{bin_hon}★ ―― 「rc=0」は届いた事しか言はぬ故、★臺帳から読み返して★ 胴の逐語を突き合はせた。
控 = `raw/90_okuri.txt`(送り)／`raw/95_yomikaeshi.tsv`(読み返し)／`raw/90_dou_<便>.txt`(送つた胴)。

## ★境★ の證 ―― 共用樹は不動

{s99}

## ★此の紙の數が意味せぬ事★

 ・母數 548 と 組 1 は ★固定 commit 6bde7170… の樹★ の話である。★disk の數でも、歴史の數でもない。★
 ・ref {ref}／樹 {ki} で組が 1 の儘なのは ★tip のみ★ を歩いた結果である。★過去の commit は一つも歩いて居らぬ。★
 ・★組=0 の {k0} 本は「双子が消された」の意ではない★ ―― 其の樹に元から此の紙が無いだけである(因は未測)。
 ・canon の {md_ko} 当りは ★字面の數★ であり、★書き手の意図を測つた物ではない★(㋕ 五参照)。
 ・彫り rc=0 は ★己の枝に載つた★ の意であり、★merge された事も・PR が在る事も意味せぬ★(remote は 0 行)。
 ・共用樹の porcelain 1036 行の一致は ★行の數の一致★ であり、★中身の一致を証して居らぬ★(99 の紙に明記)。
 ・★Linux(case を区別する側)で此の双子が如何に見えるかは、當席の器では測れぬ。★
"""

K.kaku(os.path.join(KI, "00_shodan.md"), MD.format(
    t=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    s10=yomu("10_shime.txt"), s15=yomu("15_shime.txt"), s20=yomu("20_shime.txt"),
    s25=yomu("25_shime.txt"), s35=yomu("35_shime.txt"), s40=yomu("40_shime.txt"),
    s41=yomu("41_shime.txt"), s50=yomu("50_shime.txt"), s65=yomu("65_hakarenu.txt"),
    s99=yomu("99_fudou.txt"),
    ref=ref_hon, ki=ki_hon, k1=kumi_ichi, k0=kumi_zero, kf=kumi_futa,
    md_oo=md_oo, md_ko=md_ko, code_oo=code_oo, code_ko=code_ko,
    t10k=hyou("10_kumi_git.tsv"), t10d=hyou("10_disk.tsv"),
    t20k=hyou("20_kata.tsv"), t20s=hyou("20_sasu_file.tsv"),
    t25=hyou("25_kuichigai.tsv"), t35=hyou("35_gyaku.tsv"),
    t50=hyou("50_hori.tsv"), t95=hyou("95_yomikaeshi.tsv"),
    bin_hon=bin_hon, maru=bin_maru, ok=okuri_karo, og=okuri_gunshi))

assert kumi_futa == 0, u"★組が 2 以上の ref が %d 本 ―― 他の双子が在る★" % kumi_futa
print(u"ref=%d 樹=%d 組=1の行=%d ／ .md 大=%d 小=%d ／ code 大=%d 小=%d ／ 便=%d(丸=%d 家老=%d 軍師=%d)"
      % (ref_hon, ki_hon, kumi_ichi, md_oo, md_ko, code_oo, code_ko,
         bin_hon, bin_maru, okuri_karo, okuri_gunshi))
assert bin_maru == bin_hon, u"★読み返しで欠けた便が %d 通★" % (bin_hon - bin_maru)
assert okuri_karo + okuri_gunshi == bin_hon, u"★送りと読み返しの本数が合はぬ★"
