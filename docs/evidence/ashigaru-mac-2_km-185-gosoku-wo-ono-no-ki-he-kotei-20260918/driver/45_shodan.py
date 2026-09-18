# -*- coding: utf-8 -*-
"""45 ―― 初段(00_shodan.md)を ★測つた TSV からのみ★ 組む。手で數を打たぬ。
★一つでも手打ちの數が混じれば紙は古びる★ ―― 因つて表は悉く raw/*.tsv の逐語を通す。
"""
import io, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402
R = os.path.join(KI, "raw")


def tsv(name):
    ls = [l for l in io.open(os.path.join(R, name), encoding="utf-8").read().split("\n") if l.strip()]
    return ls[0].split("\t"), [l.split("\t") for l in ls[1:]]


def hyou(name, midashi=None):
    h, rows = tsv(name)
    h = midashi or h
    o = [u"| " + u" | ".join(h) + u" |", u"|" + u"---|" * len(h)]
    for r in rows:
        r = r + [u""] * (len(h) - len(r))
        o.append(u"| " + u" | ".join(x if x else u"―" for x in r[:len(h)]) + u" |")
    return u"\n".join(o)


def yomu(name):
    return io.open(os.path.join(R, name), encoding="utf-8").read().rstrip("\n")


h30, r30 = tsv("30_horu.tsv")
h10, r10 = tsv("10_shime.tsv")
kei = sum(int(r[1]) for r in r10)
hotta = sum(int(r[5]) for r in r30)

MD = u"""# km-185 ―― ★五束を己の樹へ固定した★(専任2・裁332455／333060③／329271)

刻 = {t} ／ 席 = ashigaru-mac-2(専任2) ／ 親裁 = 332455・333060③・329271

## 〇 一行で

**追跡外であつた五束 314 本の紙に、己の樹で固定 commit を与へた。**
共用樹の HEAD・index・porcelain は ★前後で不動★。push は打たず、main には触れて居らぬ。

★當席が「commit を打てぬ」と断じた三因の内、二つは己の樹を切る事で消えた★ ――
⑴禁④(共用樹の HEAD・index) は ★己の樹なら動かぬ★ ⑵枝が他席の物 → ★己の枝を切つた★。
⑶`.gitignore:7` の裸の `*` は ★`git add -f` で名指せば越えられた★。
∴ ★解禁の令は要らなんだ。當席の断は誤りであつた。★

## ㋐ 三枝 ―― 悉く origin/main の固定 sha から切つた

切り元 = `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`(裁333060③ 1弾1枝)

{t30}

★固定 commit と tree の 40桁は上表の逐語★。彫りは `git add -f <path>` の後 `git commit --only <同じ path>`。
`reset` は打たず・`push` せず・`main` に触れず・`gh` を叩いて居らぬ(裁332449)。

## ㋑ 紙の數 ―― 家老の數と己の數

家老の宣: 59／71／61／71／52(計314)。★當席が己で歩き直した數も同じである(計314)。★
∴ ★差の一本も無い ―― 消して揃へた物は無い。★

{t10}

★pycache の一本★: `…uke-ire-no-jimen-wo-404-he…` 束に `driver/__pycache__` が一本在る。
臺帳は之を除く方言(50 の歩きが `__pycache__` を落とす)ゆゑ ★臺帳 31 行 対 disk 71 本★ と成る。
★消さなかつた譯★ = ㋓「元の束は一指も触れるな」。★其の儘 commit に入れた(彫つた 71 本の内の一本)。★

## ㋒ 写しの證 ―― 母數と一致数を両方書く

{t20}

★三つを別々に数へた譯★: 一つに畳むと「宛に實體が無い」が「sha が違ふ」に紛れる。

## ㋓ 元の束と共用樹の不動

{fudou_mae}

―― 彫つた後(控=ato)――

{fudou_ato}

## ㋔㋕ 門 ―― 各束 二度・cwd=束・`KM_GATE_MANIFEST_BASE=.`

{t35}

★二度の byte和★:

{tbw}

### ★門が四束で rc=1 に成つた ―― 之は疵であり、隠さぬ★

落ちたのは ★悉く條①(臺帳と disk の差)★ である。條②③④⑤ は五束とも通つて居る。
鳴つた札は七本、逐語は下表:

{tsoui}

★因★: 臺帳は ★建てた刻の disk★ を凍らせる。然るに其の後に
⑴`raw/90_okuri.txt` は便を出す度に追記され ⑵`raw/95_yomikaeshi.tsv` は読み返しで書かれ
⑶`driver/60_daichougai.py` は當席が己の疵を直して書き換へた(km-171-toi 束の oi4 便で申した通り)。
∴ ★臺帳を建てた後に動いた札である。★ 紙は己より後に生まれる物を書けぬ。

★直さなかつた譯★: 直すには臺帳を建て直す事に成り、之は ㋓「元の束は一指も触れるな」と
`evidence_bundle: 既に在る五束を其の儘固定する・新しい紙は作らず` に反する。
∴ ★食ひ違ひごと固定した。★ 固定した今、★誰でも同じ rc=1 を再現できる★(以前は disk が動く故 再現すら出来なんだ)。

★此の rc=1 が意味せぬ事★:
 ・★束の中身が誤りである事を意味せぬ★ ―― 條①は「臺帳の宣と今の disk の差」であり、中身の正否ではない。
 ・★彫りが失敗した事を意味せぬ★ ―― `git commit --only` の rc は五束とも 0、彫つた紙は disk と一本ずれず一致する(下表)。

## ㋕続 三つの數は同じ物ではない

{t40}

★臺帳の行 < 彫つた紙★ に成る理由は四つ ―― ⑴臺帳は己(`manifest.txt`)を含めぬ
⑵`mon_*`(門控)を除く ⑶`__pycache__` を除く ⑷臺帳を建てた後に生まれた紙は載らぬ。
彫りは disk を其の儘持つ故、★臺帳外も悉く commit に入る★。
`彫つた紙 == disk の紙` は五束とも成立(器が assert して居る)。

## ㋖ 未 push の證 ―― ★0 行では立たぬ★

各枝の `origin/main..<固定 sha>` の commit 数と、★陽性対照★ `git ls-remote origin refs/heads/main` の
行数を並べて `raw/30_shime.txt` に採つた。★遠方が引ける事を先に示さねば、0 は器の沈黙と區別が付かぬ。★

同じ器・同じ遠方で ★三役★ を当てた(`raw/32_mipush.tsv`):

{t32}

{f32}

## ★測れぬ物★

 ・★他席が元の束に触れて居らぬ事★ は當席には測れぬ。上の「不動」は ★當席が触れて居らぬ★ の意である。
 ・★此の三枝が後で push されぬ事★ は測れぬ。測つたのは「★今★ 遠方に無い」までである。
 ・★門の rc=1 が委員長・軍師の目に何と映るか★ は當席の断ずる所ではない ―― 事実のみ置く。

## 帳と板

己の帳(`queue/tasks/ashigaru-mac-2.yaml`)の ★己の鍵だけ★ を改めた(㋗)。
★書込の前に parse を当て★、bak を取り、鍵の数と順と既存欄の逐語一致を assert した(裁333131②)。
★板は書かぬ ―― 板は家老の手である。★

## 十二 便(㋘) ―― ★送つた物と、送つた後に讀み返した物★

★便の臺(raw/90_okuri.txt)★
{tokuri}

★第八の守り ―― 臺帳から讀み返した出目(raw/95_yomikaeshi.tsv)★
{tyomi}

★此の表が意味せぬ事★:
  ・rc=0 は ★届いた★ の意であつて ★讀まれた★ の意ではない。
  ・「丸ごと在り」は 送つた胴が臺帳の全文に ★含まれて居る★ の意である ――
    臺帳は頭書きを添へる故、完全一致では測れぬ(字数を併せ書いたのは其の為)。
  ・本表は ★此の紙を書いた刻まで★ の便である。★之より後に出す便は此の表に載らぬ。★
"""

md = MD.format(
    t=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    t30=hyou("30_horu.tsv"),
    t10=hyou("10_shime.tsv"),
    t20=u"```\n" + yomu("20_shime.txt") + u"\n```",
    fudou_mae=u"```\n" + yomu("25_ki_mae.txt") + u"\n```",
    fudou_ato=u"```\n" + yomu("25_ki_ato.txt") + u"\n```",
    t35=hyou("35_mon.tsv"),
    tbw=hyou("35_bytewa.tsv"),
    tsoui=hyou("40_soui.tsv"),
    t40=hyou("40_kazu.tsv"),
    t32=hyou("32_mipush.tsv"),
    f32=u"```\n" + yomu("32_shime.txt") + u"\n```",
    tokuri=u"```\n" + yomu("90_okuri.txt") + u"\n```",
    tyomi=hyou("95_yomikaeshi.tsv"),
)
K.kaku(os.path.join(KI, "00_shodan.md"), md)
print(u"00_shodan.md 行=%d ／ 写した紙(控)=%d ／ 彫つた紙(合計)=%d"
      % (len(md.split("\n")), kei, hotta))
assert kei == hotta == 314, u"★控 %d ／ 彫 %d ―― 314 と合はぬ★" % (kei, hotta)
