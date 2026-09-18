# -*- coding: utf-8 -*-
"""80 ―― ★便の胴を悉く先に建て、悉く測つてから書く★(一通でも條を超えたら ★一通も書かぬ★)。
★識別子は略さず・便を分けよ★(總監督 326424)。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

JOU = 300
TABA = "ashigaru-mac-2_km-186-oomoji-komoji-no-futago-20260918"
KOTEI = "6bde7170ce574090a6139ba2dfe3aa4cb6db8634"
HORI = "4cb05b976ec0060796840e02dd579f1551d89841"
EDA = "ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918"

DOU = {}

DOU["a_census186"] = u"""km-186 ㋐ 母數は己で建て申した。固定 commit = {kotei}／`git ls-tree -r --name-only -z` rc=0・path = ★548 本★／casefold の組 = ★1 組★。
全 ref も歩き、ref 378 本・別々の樹 306 本(rc=0)でも ★1 組の儘★。∴ 他の双子 = ★0★(家老の測りと一致)。刻 = 20:32。
★歩いたのは ref の先のみ ―― history は未踏(測れぬ)★。""".format(kotei=KOTEI)

DOU["b_disk186"] = u"""km-186 ㋑ 双子の blob と disk(共に docs/runbooks/ 下)。
大文字 ERR-EKARTE-001.md = blob e6de627bd62eb9a4b417155f40748390f49369fe／2596 bytes。
小文字 err-ekarte-001.md = blob de00cbd99d9909f4a923041ae17f0d2cbb587668／3471 bytes。
disk は ★一本★ ―― 二名が同 inode 10724954・真名は小文字・中身は ★2596 bytes の方★。
★3471 bytes は此の Mac に無し。★"""

DOU["c_canon186"] = u"""km-186 ㋒ canon の側を歩き申した(固定 commit の全 blob 548 本・rc=0)。
`.md` 付きで名を指す当り = ★小文字 4 当り(CLAUDE.md 2 行)／大文字 ★0★★。
`.md` 無しの `ERR-EKARTE-001` = 19 当り(5 file) ―― 是は ★error code であつて file 名ではない★ 故 分けて数へ申した。
★食ひ違ひ★: 索引は正しく小文字を指すのに、此の Mac で其の名を開くと ★旧版 2596 bytes★ が出る。link は壊れて居らぬ故 ★誰も気付かぬ★。"""

DOU["d_gyaku186"] = u"""km-186 補㋔ 逆順を ★己の使ひ捨て worktree★ で撃ち申した(共有樹では一発も撃つて居らぬ)。
素の `git rm docs/runbooks/ERR-EKARTE-001.md` の後、dirent は ★無★・小文字の名も ★開けぬ★。
続けて `git add -A` を打つと ★index からも正本の行が消え★、`git checkout -- <小文字>` は rc=1 で戻らず、
`git checkout HEAD -- <両名>` で漸く 3471 bytes が戻り申した。
∴ ★害は「消えた事」ではなく「気付かぬ儘 commit する事」★。"""

DOU["e_hori186"] = u"""km-186 ㋓ 命の順で彫り申した。★⑴と⑵を入れ替へず・⑵を飛ばさず★。
⑴`git rm --cached <大文字>` = disk 不動(同 inode・2596 bytes)。⑵`git checkout -- <小文字>` = 3471 bytes、
blob sha1 を己で計算し de00cbd9… と一致。⑶ porcelain = ★大文字の D 一行のみ・小文字の M は消滅★
(陽性対照 = ⑵の前は M を刷つた)。⑷ rc=0・commit = {hori}・79 deletions。""".format(eda=EDA, hori=HORI)

DOU["f_only186"] = u"""km-186 ㋓⑷ ★御下知を仰ぎ申す★。命の字義「`git add -f` の後 `git commit --only <同じ path>`」は
★此の双子では彫れませなんだ★ ―― `--only` も `add -f`+`--only` も ★rc=1「no changes added to commit」・HEAD 不動★(二本実測)。
因 = `--only` は worktree の其の path を読み直すが、case を畳む disk では ★大文字の名がまだ開ける★。
∴ ⑷ のみ ★素の commit★。index が D 一行のみと先に assert 仕り候。"""

DOU["g_teian186"] = u"""km-186 ㋔ 案を紙に致し候(束 60_teian.md)。何を = 大文字 ERR-EKARTE-001.md を樹から外す(79 行削除)・小文字は不触。
★戻し方★ ⑴PR 前 = 枝を捨てるのみ(remote 0 行) ⑵merge 後 = `git revert {hori}`
⑶手で戻す時 ★`git checkout <固定> -- <大文字>` を単独で打つな★ ―― 小文字の実体を 2596 bytes で上書き致す。必ず後に `git checkout -- <小文字>`。""".format(hori=HORI)

DOU["h_hakarenu186"] = u"""km-186 ㋕ ★測れぬ物★ を名指し申す(推し量りで埋めて居らぬ)。
一 case を区別する Linux 側で双子が如何に見えるか ―― ★當席は Mac の disk しか持たぬ★。
二 共用樹が旧版 2596 bytes を抱く因 ―― ★未測★(鮮な checkout では 3471 bytes が勝つと実測した故、鮮な checkout の結果ではない)。
三 他席の作業樹の未 commit ―― 禁により触れぬ。
四 ref の先より奥の history ―― 歩いて居らぬ。
五 `.md` 無し 19 当りの「意図」―― 字から出ぬ。"""

DOU["i_fudou186"] = u"""km-186 ★境★ の證。共用樹は ★不動★ ―― HEAD = d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11(前後同じ)、
index の sha256 = 7425522328c8eca4efa6f25c0bc3657bdff208dea4331ab4200862eaaa562738(前後同じ)、porcelain 1036 行(前後同じ)。
撃つたのは ★己が切つた worktree 7 本★ の中のみ。★push 0・gh 0・main 不触・reset 不打★(陽性対照 main = 1 行)。"""

DOU["i_pr186"] = u"""km-186 ㋗ ★壁を報じ申す★。「PR は貴席が出す」と承りながら、同じ命が ★gh を叩くな・main へ直押しするな★ と定め、
km-172 ㋕⑶ は ★push 禁★ に候。∴ 當席が出来申したのは ★枝と commit まで★ ―― {hori}(枝 {eda})。
remote には一行も無し(陽性対照 main = 1 行)。★出し方の御下知を仰ぎ申す★(km-185 の便 seq333805 と同じ壁に候)。""".format(hori=HORI, eda=EDA)

DOU["kansa186a"] = u"""軍師mac 殿 ―― 專任2、km-186 監査 其の一(母數と実体)。
固定 commit = {kotei}／path 548 本／組 1 組／全 ref 378 本・樹 306 本でも 1 組。
双子 = e6de627b…(2596 bytes)と de00cbd9…(3471 bytes)、disk は ★一本(inode 10724954)★・中身は 2596 の方。
束 = docs/evidence/{taba}""".format(kotei=KOTEI, taba=TABA)

DOU["kansa186b"] = u"""軍師mac 殿 ―― 專任2、km-186 監査提出 其の二(実射と彫り)。
逆順(素の `git rm <大文字>`)を ★己の使ひ捨て★ で撃ち、実体が消え index からも落ちる事を数で示し申した。
正順は ⑴rm --cached ⑵checkout -- <小文字> ⑶検め ⑷彫りで rc=0、commit = {hori}、枝の樹の双子 = ★1 本・中身 de00cbd9…★。
★共有樹の HEAD・index・porcelain は前後不動★。push 0・gh 0。""".format(hori=HORI)

DOU["kansa186c"] = u"""軍師mac 殿 ―― 專任2、km-186 監査提出 其の三(疵と測れぬ)。
★疵★: 40 の紙の初版に「甲(commit --only <大文字>)で足りる」と ★測る前に断を書き申した★。実際は甲も乙も rc=1 で彫れず、41 で測り直し訂し候(紙に両方残して御座る)。
★測れぬ★: Linux 側の姿・共用樹が旧版を抱く因・他席の樹・history・`.md` 無し 19 当りの意図 ―― 五件、推さずに名指し申した。"""

nagasa = {k: len(v.replace(u"\n", u"")) for k, v in DOU.items()}
kome = {k: len(v) for k, v in DOU.items()}
# ★書く前に悉く測る★ ―― 一通でも超えたら一通も書かぬ
koeta = {k: v for k, v in kome.items() if v > JOU}
for k in sorted(kome):
    print(u"%-14s 字(改行込)=%3d 字(改行除)=%3d %s" % (k, kome[k], nagasa[k], u"★條超★" if kome[k] > JOU else u""))
assert not koeta, u"★條 %d 字を超えた便が %d 通 ―― %s★" % (JOU, len(koeta), koeta)
for k, v in DOU.items():
    K.kaku(os.path.join(BUNDLE, "raw", "89_dou_%s.txt" % k), v)
print("★%d 通 建て申した(悉く %d 字以下)★" % (len(DOU), JOU))
