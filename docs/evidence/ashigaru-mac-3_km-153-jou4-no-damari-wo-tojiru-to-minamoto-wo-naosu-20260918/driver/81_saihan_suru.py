# -*- coding: utf-8 -*-
"""★22 行を一件づつ今日の眼で再判する★(家老令 km-153 ㋒ 後段)
80 弾の候補(過去の束 22 行)を ★一行も落さず★ 三つに分ける:
  甲_断に非ず(器の出目・控の行・引用) / 乙_今も立つ / 丙_改めた
判は下の SAIHAN に逐語の錨付きで書く ―― ★錨が其の行に無ければ何も書かず落ちる(fail-closed)★。
行の数と ★断の実体の数★ は別物ゆゑ両方刷る(同じ断が表の 9 行に複製されて居る為)。
四札: 刻=冠 / 根=docs/evidence/ashigaru-mac-3_* / rc=本器の returncode / 対照=80 弾の候補表(母數 22)と突き合はせ、差が出たら落ちる。"""
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv
NE = os.path.join("docs", "evidence")

# (束の頭, 紙, 行, 逐語の錨, 判, 断の実体の名, 理由)
SAIHAN = [
 ("km-103", "README.md", 69, "器の疵として", "乙_今も立つ", "d1_己の器の緩い錨",
  "名指したのは ★當席自身の器★ の疵であり、責を他へ移して居らぬ。初版が別の行を引いた事は本日も事実。"),
 ("km-113", "raw/50_taishou.tsv", 3, "計数器を疑へ", "甲_断に非ず", "-",
  "器が刷つた ★対照表の一行★(指図)であり、紙の疵を器の所為にした断ではない。"),
 ("km-113", "raw/50_taishou_origin.tsv", 3, "計数器を疑へ", "甲_断に非ず", "-",
  "同上 ―― 同じ表の別走りの控。"),
 ("km-119", "00_shodan.md", 157, "現に濡れ衣を出して居る", "乙_今も立つ", "d2_dd169 の濡れ衣",
  "dd169 の番人は ★命令の字面★ に当たる造りゆゑ濡れ衣を出す ―― 本日も立つ。且つ『何件が誤つて止まるかは測れぬ』と限界も併せ書いて居る。"),
 ("km-123", "00_shodan.md", 241, "濡れ衣・既知", "丙_改めた", "d3_NUL の紙に條②が鳴る",
  "今日の眼: ★濡れ衣ではない★。門の契約は『字の紙』であり、NUL を含む紙を門へ渡した事が疵である。"
  "門の grep は其の紙を binary として扱ひ、當席の計数器は byte で数へた ∴ ★二器は違ふ物を数へて居た★ ―― "
  "『器の疵』でも『紙が汚い』でもなく ★契約外の紙を渡した側の疵(宣して除くか字へ直す)★ と改める。"),
 ("km-130", "00_shodan.md", 77, "己の器の疵を名指す", "乙_今も立つ", "d4_己の器の丙=16 の誤り",
  "己の器の疵を己で名指した断 ―― 責を移して居らぬ。本日も是。"),
 ("km-147", "00_shodan.md", 238, "器の性であり本紙の疵ではない", "丙_改めた", "d5_0byte は器の性",
  "km-150 §4 で當席が既に破つた ―― 門は正しく鳴り、0byte の因は捕りを殻の `>` で書いた當席に在る。本日も其の自訂を是とする(本弾 ㋑ の 71 表が同じ事を再測)。"),
 ("km-150", "00_shodan.md", 78, "器の性であり本紙の疵ではない", "甲_断に非ず", "-",
  "自訂の中の ★逐語引用★(km-147 の一文を引いた行)であり、新たな断ではない。"),
 ("km-150", "00_shodan.md", 84, "器は正しく、疵は當席に在る", "乙_今も立つ", "d6_自訂の断",
  "d5 を破つた自訂そのもの ―― 本日も立つ。"),
 ("km-159", "00_shodan.md", 158, "器を疑へ", "乙_今も立つ", "d7_陰性対照が通れば器を疑へ",
  "本弾 raw/51 で同じ器の疵(素の走りは判ぜぬ)を再現 ―― 教訓として立つ。"),
 ("km-159", "00_shodan.md", 192, "濡れ衣で落ちる", "乙_今も立つ", "d8_兄弟器無しの濡れ衣",
  "本弾 raw/30 で兄弟器を隣に置いて走らせ、置かねば條②④が『測れぬ』で落ちる事を再測した ―― 立つ。"),
 ("km-159", "_letters/02_osame_2of2.txt", 1, "器の不調に非ず", "乙_今も立つ", "d9_丙が当たる故 器は働く",
  "本弾 raw/50 で丙(陽性対照)が新基底へ rc=0 で当たる事を再現 ―― 立つ。"),
 ("km-159", "raw/87_atenashi_dan.txt", 18, "濡れ衣で落ちる", "乙_今も立つ", "d8_兄弟器無しの濡れ衣",
  "d8 と同一の断の控(便へ出した紙) ―― 行は別、断は同じ。"),
]
# ―― 表の 9 行(同一の断 d3 の複製)―― 行番のみ列べる ――
for gy in (86, 104, 137, 171, 178, 393, 396, 399, 401):
    SAIHAN.append(("km-123", "raw/20_nari_shindan.tsv", gy, "濡れ衣★ の形(既知)", "丙_改めた", "d3_NUL の紙に條②が鳴る",
                   "d3 と同一の断が器の表へ複製された行 ―― 判も同じく『改めた』。行は 9 本、断は 1 件。"))

# ―― 錨を其の行で確かめる(★行番を信ぜず逐語で当てる★) ――
rows = []
for atama, kami, gy, iki, han, mi, riyu in SAIHAN:
    taba = [d for d in sorted(os.listdir(NE)) if d.startswith("ashigaru-mac-3_" + atama + "-")]
    assert len(taba) == 1, "束『%s』が %d 個 ―― 一意でなければ判ぜぬ" % (atama, len(taba))
    p = os.path.join(NE, taba[0], kami)
    L = open(p, encoding="utf-8").read().split("\n")
    assert gy <= len(L), "%s に %d 行目が無い" % (p, gy)
    assert iki in L[gy - 1], "★錨『%s』が %s:%d に無い ―― 紙が動いた。判を止める★" % (iki, p, gy)
    rows.append([taba[0][:46], kami, gy, han, mi, L[gy - 1].strip()[:70], riyu])

# ―― 80 弾の候補表(母數)と突き合はせる ――
kouho = []
for ln in open(os.path.join(BUNDLE, "raw", "80_utsuwa_no_sei_kouho.tsv"), encoding="utf-8").read().split("\n")[1:]:
    c = ln.split("\t")
    if len(c) >= 4 and c[0] == "過去":
        kouho.append((c[1], c[2], int(c[3])))
mine = set((r[0], r[1], r[2]) for r in rows)
nuke = [k for k in kouho if k not in mine]
assert not nuke and len(kouho) == len(rows), \
    "★母數 %d 行に対し判 %d 行 ―― 落ちた行 %s(一行も落さぬのが條)★" % (len(kouho), len(rows), nuke[:3])

kaku_tsv(os.path.join(BUNDLE, "raw", "81_saihan.tsv"),
         sorted(rows, key=lambda r: (r[0], r[1], r[2])),
         header=["束", "紙", "行", "今日の判", "断の実体", "逐語(70字で截つ)", "理由"])
han_kazu = {}
for r in rows:
    han_kazu[r[3]] = han_kazu.get(r[3], 0) + 1
mi_kazu = {}
for r in rows:
    if r[4] != "-":
        mi_kazu.setdefault(r[3], set()).add(r[4])
kaku_tsv(os.path.join(BUNDLE, "raw", "81_saihan_kazu.tsv"),
         [[h, han_kazu.get(h, 0), len(mi_kazu.get(h, ()))] for h in ("甲_断に非ず", "乙_今も立つ", "丙_改めた")]
         + [["★計★", sum(han_kazu.values()), sum(len(v) for v in mi_kazu.values())]],
         header=["今日の判", "行", "断の実体(重複を畳んだ数)"])

kaku(os.path.join(BUNDLE, "raw", "82_saihan_dan.txt"),
     "as-of %s(UTC)\n根=%s/ashigaru-mac-3_*／母數=80 弾の過去 22 行(一行も落して居らぬ)\n\n"
     "【今日の判】\n"
     "・甲_断に非ず %d 行 ―― 器の出目・控・引用。\n"
     "・乙_今も立つ %d 行(断の実体 %d 件) ―― 内 %s は本弾で ★再測して★ 立てた。\n"
     "・丙_改めた   %d 行(断の実体 %d 件) ―― d3(NUL の紙に條②が鳴るは濡れ衣)と d5(0byte は器の性)。\n\n"
     "【改めた二件の要】\n"
     "d5: ★既に km-150 §4 で己の手で破つて在る★ ―― 本弾 ㋑ の實測(raw/71)が同じ事を數で示した。\n"
     "    0byte の因は器ではなく ★捕りを殻の `>` で書いた當席★ に在り、治めは源で一行書く形である。\n"
     "d3: ★本弾で新たに改める★ ―― NUL を含む紙に條②が鳴るのを『濡れ衣(器の疵)』と書いたのは誤り。\n"
     "    門の契約は字の紙であり、NUL を含む紙は ★契約外★。契約外の紙を渡した側に疵が在る。\n"
     "    ∴ 正しい書き方は「器の疵」でも「紙が汚い」でもなく ★『門の出目は此の紙に対して定義されて居らぬ ―― 宣して除くか字へ直す』★ である。\n\n"
     "【己に課す形 ―― 之が㋒の実である】\n"
     "・疵を器へ移す時は ★①器の何行目が★ ②★何の入力で★ ③★何と出たか★ の三つを逐語で並べる。三つ揃はぬ時は『測れぬ』と書く。\n"
     "・『器の性であり本紙の疵ではない』の如き ★一文で責を移す形★ は用ゐぬ(km-147 の一文が現に誤つて居た)。\n\n"
     "【之が意味せぬ事】\n"
     "・22 行は ★語で引いた上限★ である ―― 方言表(raw/80)に無い言ひ方で責を移した断は此の數に入つて居らぬ。\n"
     "・『改めた 2 件』は過去の紙を ★書き換へた事ではない★(提出済の紙は直さぬ) ―― 本紙に自訂として残す形である。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), NE,
        han_kazu.get("甲_断に非ず", 0), han_kazu.get("乙_今も立つ", 0), len(mi_kazu.get("乙_今も立つ", ())),
        "d7/d8/d9", han_kazu.get("丙_改めた", 0), len(mi_kazu.get("丙_改めた", ()))))
print("母數 %d 行 = 判 %d 行(落ち 0)" % (len(kouho), len(rows)))
for h in ("甲_断に非ず", "乙_今も立つ", "丙_改めた"):
    print("  %s %d 行 / 断の実体 %d 件" % (h, han_kazu.get(h, 0), len(mi_kazu.get(h, ()))))
