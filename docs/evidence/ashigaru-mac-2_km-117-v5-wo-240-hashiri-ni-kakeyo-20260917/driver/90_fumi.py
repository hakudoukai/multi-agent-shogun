# -*- coding: utf-8 -*-
"""★便の数は紙の産物から引く★ ―― 手で打ち直さぬ(memory「Letter numbers must be extracted from the paper」)。
   己(此の器)の出目も kaki を通す。"""
import io, os, re, sys, time
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(B, "driver"))
from kaki import kaku

def rd(p):
    return io.open(os.path.join(B, p), encoding="utf-8").read()

hou = rd("raw/20_hougen.txt")
bet = rd("raw/11_hougen_betsu.txt")
shi = rd("raw/99_shimai.txt")

# ―― ㋑ 母數と ②a を★行から引く★
def hiku(seiki, moto, nani):
    m = re.search(seiki, moto, re.M | re.S)
    assert m, "★引けぬ★ %s (%s)" % (nani, seiki)
    return m

g = hiku(r"^甲\+乙\(己束の外\)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)$", hou, "甲+乙の行").groups()
ichi, nia, nib, san, yon, kei = g
b_jitsu = hiku(r"②b.*?= (\d+) 行 / 其の内 ★B が disk に実在★ = (\d+) 行", hou, "②b の実在").groups()
bos = hiku(r"母數甲.*?= (\d+) 本 / 母數乙.*?= (\d+) 本 / 丙己束 = (\d+) 本", hou, "母數").groups()

# ―― ㋒ 方言甲の器別 偽の通/偽の赤 を★表から数へる★
def houhen(name):
    blk = bet.split("## " + name)[1].split("## ")[0]
    rows = [l.split("\t") for l in blk.strip().split("\n") if l.startswith("区\t") or re.match(r"^[甲乙丙丁戊己庚辛]", l)]
    atama = rows[0][2:]
    tsuu = [0] * len(atama); aka = [0] * len(atama)
    for r in rows[1:]:
        for i, c in enumerate(r[2:]):
            if "偽の通" in c: tsuu[i] += 1
            elif "偽の赤" in c: aka[i] += 1
    return atama, tsuu, aka, len(rows) - 1

atama, t_kou, a_kou, ku = houhen("方言甲")
def hiki(nm, t, a):
    i = atama.index(nm)
    return "%s %d/%d" % (nm, t[i], a[i])

# ―― ㋕ 門と臺帳
gyo = hiku(r"path= の行\(★母數★\)\t(\d+)", shi, "臺帳の母數").group(1)
mon = hiku(r"★mon_ の行\(門控\)★\t★(\d+)★", shi, "mon_ の行").group(1)
ingai = hiku(r"員外 = (\d+) 本", shi, "員外").group(1)

# ―― 宣と實(ETA)
import datetime
hajime = datetime.datetime(2026, 9, 17, 18, 47, 51)
sen = hajime + datetime.timedelta(minutes=75)
ima = datetime.datetime.now().replace(microsecond=0)
keika = int((ima - hajime).total_seconds() // 60)

L = []
A = L.append
A("專任2、km-114 ㋐〜㋕ 悉く数で閉じ、家老殿の直し v4 を★叩いた★。束=docs/evidence/ashigaru-mac-2_km-114-nori-no-jun-wo-kazu-de-kimeyo-20260917/ 紙=00_shodan.md")
A("")
A("【㋐ 疵の面積】10区×3方言×8器=240走。★v4 も rc0/偽の通★ ―― 方言甲 区甲(前綴が実在file・宣sha=前綴の物)と区己。家老殿の自省は正しい。")
A("  ★因は則の順ではなく構への方★: v4 の main は候補を★列べて isfile() の先頭勝ち★ゆゑ、実在する前綴が真の path に勝つ ―― ★列べる形は順を変へても fail-open が残る★(案甲列・案丙も同じく偽の通)。塞いだのは★鎖★(if not m で一本だけ持つ)の形のみ。")
A("  ★v4 第二の疵★: 方言甲 区戊(正当な空白名の行＋無縁の前綴が実在)で ★偽の赤★ ―― 直さうとした其の場合が、前綴が在る時に落ちる。")
A("  ★v4 の功は残る★: 区丁二・戊二 は v1/v2 が偽の赤、v4 が正。案甲鎖も此を保つ。")
A("")
A("【㋑ 則②を先へやると何行壊れるか】歩き根1本=docs/evidence(深さ10・8662file・rc0・刻 2026-09-17T19:00:15+0900)。母數甲%s本/母數乙%s本(己束%s本は別勘定)。" % bos)
A("  ①隣接%s / ★②a食ひ過ぎ %s★ / ②b空白名%s / ③sha無%s / ④sha先%s / 計%s 行" % (ichi, nia, nib, san, yon, kei))
A("  ★断 ②a = %s 行★ ―― 「則②を先へ」で壊れる現物は★零★。因は append.py:114 が path= の直後に必ず sha256= を書く事(構造)。" % nia)
A("  零の札四つ=陽性対照(21_taishou 己で建てた一行で全方言1と数へた)/根と深さ/rc0/刻。")
A("  ★之が意味せぬ事★: 「永久に0」ではない。③が%s行在る=別の書き手が居た證ゆゑ、手書きの臺帳が ②a を生む事は在り得る ―― 其は★測れぬ★。" % san)
A("  功の側: ②b=%s行、其の内 B が disk に実在=%s行(16臺帳/9臺帳)。★此の行は今日の門の判定が誤つて居る★ ―― v4 では治らぬ。" % b_jitsu)
A("")
A("【㋒ 三案を実に走らせた】方言甲%d区の(偽の通/偽の赤): %s / %s / %s / %s / %s / v4 2/1 / v1 2/3" % (
    ku, hiki("案甲鎖", t_kou, a_kou), hiki("案乙", t_kou, a_kou), hiki("案丁", t_kou, a_kou),
    hiki("案甲列", t_kou, a_kou), hiki("案丙", t_kou, a_kou)))
A("  案乙(sha256= 在る時のみ則②を先)は★240走 悉く案甲鎖と同値★ ―― 数は乙を選ぶ根拠を与へぬ。")
A("  案丙(曖昧鳴り)は狙ひが外れて居る: fail-open は候補が★一つだけ実在する時★に起きるゆゑ、二つ以上を見る番は鳴らぬ。加へて区戊の正当な行に鳴る。")
A("")
A("【㋓ 陽性対照】区丙(前綴不在)・区庚(空白無・真に不在) × 8器 × 3方言 = ★48/48 rc1・判定 正★。区辛(清い行)は8器悉く rc0 ―― 何にでも鳴る器ではない。")
A("")
A("【㋔ 一案だけ薦める】★案甲鎖(鎖・②→①→③)★。拠: 方言甲で0/0、其の方言が現物の13443/13887=96.8%。壊す形(②a)は0行(対照付)。②b 164行(実在90)を治す。案乙と同値ゆゑ枝の少ない方。")
A("  ★塞がらぬ穴(悉く治るとは書かぬ)★: ①方言丙(sha先)は八器悉く 2偽の通/3偽の赤で★どの案も動かせぬ★ ―― 真の治療は則ではなく★書き手を縛る事★。②方言乙 区辛 = 案甲鎖が新たに壊す清い行(現物0行だが手書きなら生きる)。③③sha無 %s行は順に関らず一切照合されぬ。④名に改行=行単位の読み手(私の器も含む)では★測れぬ★。⑤rc は臺帳単位ゆゑ rc表は疵の本数を数へて居らぬ。⑥v4 の功(区丁二・戊二)を落とすな。" % san)
A("")
A("【㋕ 門】束内相対の臺帳(4欄 lines= 付)=%s行。門を★名を別にして二走★: mon_ichi_20260917T190826 rc=0 / mon_ni_20260917T190838 rc=0(KM_GATE_MANIFEST_BASE=. で束の中から)。★臺帳の mon_ 行 = %s 行(己で数へた)★。員外は★門の後も増える★ゆゑ二度歩いた: 一度目%s本(門控のみ)→二度目9本(便の器と紙が加はつた)。名は raw/99_shimai.txt と raw/91_ingai.txt に悉く記した ―― ★臺帳を追ひ掛けて建て直すのは受入⑷と衝つゆゑ、数を合はせず食ひ違ひを名で出した★。" % (gyo, mon, ingai))
A("  ★rc0 が二度出た事は「数が正しい」を意味せぬ★ ―― 門は臺帳とdiskの一致と字面だけを見る。")
A("")
A("【禁の守り】commit・push・枝作り・refs書込 ★一切せず★。scripts/ 配下★不触★(五案は束内の _an/ に写して走らせた)。束に空白名の実体★0★(型見は /private/tmp に建て、手順を紙に記した)。他席の束・worktree 不触。")
A("【疵の記】己の誤り6件を紙に書いた(歩き根1階層落として0を刷つた件を含む ―― ★之が陽性対照の要る理由★)。")
A("【宣と實】宣=+75分(〜%s)。實=%d分(此の便まで)。" % (sen.strftime("%H:%M:%S"), keika))
A("軍師mac は死箱(rc=68)ゆゑ、監査の回付を家老殿にお願ひ申す。PR#23 の最終形は上の数で決まる。")

fumi = "\n".join(L)
kaku(os.path.join(B, "raw", "90_fumi.txt"), fumi)
print("=== 便 字数=%d 行=%d ===" % (len(fumi), len(L)))
print(fumi)
