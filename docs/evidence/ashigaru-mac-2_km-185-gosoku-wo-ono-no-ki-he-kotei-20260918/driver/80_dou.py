# -*- coding: utf-8 -*-
"""80 ―― 便の胴を書く。★臺帳が凍る前に書く★(凍つた後に書けば札が動き門が鳴る)。
★字は書込の前に測り、超えたら書かずに止める★(裁333131②・家老の疵の形を踏まぬ)。
★識別子は略さぬ★(總監督326424)ゆゑ 40桁も枝名も切らず、入り切らねば便を分ける。
數は ★raw/*.tsv から引く★ ―― 手で打たぬ。
"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402
R = os.path.join(KI, "raw")


def tsv(n):
    ls = [l for l in io.open(os.path.join(R, n), encoding="utf-8").read().split("\n") if l.strip()]
    return [l.split("\t") for l in ls[1:]]


horu = tsv("30_horu.tsv")
kazu = {r[0]: r for r in tsv("40_kazu.tsv")}
shime10 = tsv("10_shime.tsv")
soui = tsv("40_soui.tsv")
mon = tsv("35_mon.tsv")

D = []
D.append(("a1", u"""km-185 着地報①/総論。追跡外であつた五束314本に己の樹で固定commitを与へた。
枝は三本・悉く origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から切つた。
★當席が『打てぬ』と断じた三因の内二つは己の樹で消え、三つ目は git add -f で越えた ―― 解禁の令は要らなんだ。當席の断が誤りであつた。★
共用樹の HEAD・index・porcelain は前後で不動。push せず・main に触れず・gh を叩いて居らぬ。"""))

for r in horu:
    ki, eda, oya, sha, tree, hon, zou = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
    D.append(("b_" + ki, u"""km-185㋐ 枝={eda}／
固定commit={sha}／
tree={tree}／
紙={hon}本／{zou}／親=origin/main {oya}
未push遠方0行(陽性対照 refs/heads/main=1行・負=0行)""".format(
        eda=eda, sha=sha, tree=tree, hon=hon, zou=zou, oya=oya)))

D.append(("c_kami", u"""km-185㋑ 紙の數。當席が己で歩き直した數は家老の宣と★一本も違はぬ★:
{a}(計{kei}本・全歩き)。★差を消して揃へた物は無い。★
★pycache 一本★=…uke-ire-no-jimen-wo-404-he…束の driver/__pycache__。臺帳は之を除く方言ゆゑ臺帳31行 対 disk71本。
㋓『元の束は一指も触れるな』に従ひ★消さず其の儘 commit に入れた★。""".format(
    a=u"／".join(r[1] for r in shime10), kei=sum(int(r[1]) for r in shime10))))

D.append(("d_utsushi", u"""km-185㋒ 写しの證。控は写す前に採り、★樹の外★=docs/evidence/ashigaru-mac-2_km-185-gosoku-wo-ono-no-ki-he-kotei-20260918/raw/10_hikae.tsv へ置いた(/tmp は用ゐて居らぬ)。
母數314に対し ⑴宛に實體=314 ⑵bytes一致=314 ⑶sha256一致=314 ⑷悪い行=0。
★三つを別々に数へた譯★=一つに畳むと『實體無』が『sha 相違』に紛れる。"""))

D.append(("e_fudou", u"""km-185㋓ 不動。元の五束を彫りの前後で歩き直し ★増えた0・消えた0・中身が動いた0★(母數314)。
共用樹 /Users/momizimac/multi-agent-shogun は HEAD=d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11 不動・
index(git ls-files -s の sha256)不動・porcelain 1036行 前後同一。
docs/runbooks の 1行(M err-ekarte-001.md)は前から在る物で當席は触れて居らぬ。"""))

nari = [r for r in mon if r[3] != "0"]
D.append(("f_mon1", u"""km-185㋕ ★門は四束で rc=1 ―― 隠さぬ★。走りは五束×二度=10回、rc=1 は{n}回。
落ちたのは★悉く條①(臺帳と disk の差)★で、條②③④⑤ は五束とも通つた。二度の byte和 は五束とも同値。
rc=0 は ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918 の一束のみ(一致32/32)。""".format(n=len(nari))))

shu = {}
for r in soui:
    shu[r[1]] = shu.get(r[1], 0) + 1
D.append(("g_mon2", u"""km-185㋕続 鳴つた札は★七本・三種★: {s}。
束の別(何れの束の何れの札か)は本束の 00_shodan.md の表と raw/40_soui.tsv に逐語で置いた ―― 便に入り切らぬ故 略さず紙へ回す。""".format(
    s=u"／".join(u"%s=%d束" % (k, v) for k, v in sorted(shu.items())))))
D.append(("g_mon2b", u"""km-185㋕続 ★因★=臺帳は建てた刻の disk を凍らせる。然るに其の後
⑴raw/90_okuri.txt は便を出す度に追記され ⑵raw/95_yomikaeshi.tsv は読み返しで書かれ
⑶driver/60_daichougai.py は當席が己の疵を直して書き換へた(km-171-toi 束の oi4 便で申した通り)。
∴★臺帳を建てた後に動いた札である★。紙は己より後に生まれる物を書けぬ。"""))

D.append(("h_mon3", u"""km-185㋕続 ★直さなかつた譯★=直すには臺帳を建て直す事に成り、㋓『元の束は一指も触れるな』と下命の『既に在る五束を其の儘固定・新しい紙は作らず』に反する。∴食ひ違ひごと固定した。
★此の rc=1 が意味せぬ事★=束の中身が誤りである意ではなく、彫りが失敗した意でもない(commit --only は五束とも rc=0・彫つた紙と disk は一本もずれぬ)。"""))

D.append(("i_taba", u"""km-185 束=docs/evidence/ashigaru-mac-2_km-185-gosoku-wo-ono-no-ki-he-kotei-20260918/(初段=00_shodan.md)。
★正直に一事★=本束自身は未だ追跡外である ―― 下命の枝は三本と定められて居る故、四本目を勝手に増やさなんだ。
本束の固定を望まれるなら別枝を切る(己の樹・push せず)。★御下知を仰ぐ。★"""))

rows = []
for k, t in D:
    dou = u"".join(t.split(u"\n"))
    ji = len(dou)
    print(u"%-10s 字(unicode文字)=%d" % (k, ji))
    assert ji <= 300, u"★%s が %d字 ―― 書かずに止めた。分けよ(略すな)。★" % (k, ji)
    K.kaku(os.path.join(R, "80_src_%s.txt" % k), dou)
    rows.append((k, ji))
K.kaku_tsv(os.path.join(R, "80_ji.tsv"), rows, header=("bin", "ji_unicode_moji"))
print(u"★便=%d 通・最長=%d字★" % (len(rows), max(r[1] for r in rows)))
