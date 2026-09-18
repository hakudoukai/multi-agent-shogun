# -*- coding: utf-8 -*-
"""★臺帳を積み、門を二走させる★ ―― 端末で組まず器で行ふ(km-159 疵⑵ の治めの延長)。
條: 臺帳は ★束内相対★(裁 seq322699 ―― cd <束> してから append)／門は `KM_GATE_MANIFEST_BASE=.`／
    ★二走・對照の名を走り毎に別にせよ★(家老mac 條)／出目は 0byte を産まぬ(裁 seq310228⑶・kaki 経由)。
四札: 刻=各紙の冠 / 根=cwd(★束★) / rc=subprocess の returncode(★管を通さず★) / 對照=走り毎の汚れ紙(下記)。
★宣★ raw/fx/ の 7本は門の argv から除く(raw/20_fx.sengen.txt ―― 直せぬ陽性対照に限る第四の道)。臺帳には悉く載せる。"""
import os
import re
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

GATE = os.path.join(ROOT, "scripts", "checks", "karo_mac_dasumae_gate.sh")
TSUMI = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_append.py")
for p in (GATE, TSUMI):
    assert os.path.isfile(p), "★器が無し★ %s" % p

os.chdir(BUNDLE)                      # ★束を根とする ―― 之が束内相対の唯一の作法★
GA = "_gate"
os.makedirs(GA, exist_ok=True)


def hashiru(args, cwd=".", env_add=None, tmo=300):
    e = dict(os.environ)
    if env_add:
        e.update(env_add)
    p = subprocess.run(args, cwd=cwd, env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return (p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), p.returncode)


def okusu(na, out, err, rc):
    """出目を三紙へ ★kaki を通して★ 置く(0byte を産まぬ)。rc は十進一行。"""
    kaku(os.path.join(GA, na + ".out"), out)
    kaku(os.path.join(GA, na + ".err"), err)
    kaku(os.path.join(GA, na + ".rc"), str(rc))
    return rc


def aruku():
    """★臺帳へ載せる紙★ を束内相対で歩く ―― 除くのは MANIFEST.txt 自身・_gate/(員外)・__pycache__。"""
    kami = []
    for d, ds, fs in os.walk("."):
        ds[:] = sorted(x for x in ds if x != "__pycache__" and os.path.join(d, x) != os.path.join(".", GA))
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(d, f), ".")
            if rel == "MANIFEST.txt" or rel.startswith(GA + os.sep):
                continue
            if not os.path.isfile(rel) or os.path.islink(rel):
                continue      # ★symlink と FIFO は歩かぬ(FIFO は open で止まる)★
            kami.append(rel)
    return sorted(kami)


KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
KAMI = aruku()
FX = [p for p in KAMI if p.startswith(os.path.join("raw", "fx") + os.sep)]
assert len(FX) == 7, "★宣した札が %d 本 ―― 7 本で無ければ宣を書き直せ★" % len(FX)

# ―― ★0byte を先に治める(裁 seq310228⑶ ―― 本弾 ㋑ を己の束へ當てる)★ ――
#   門の條④は 0byte に鳴る。鳴つた紙を argv から除けば通るが、★之は治めではない★。
#   ∴ 二つに分ける: ⒜對照ゆゑ 0byte で在らねばならぬ紙 = 宣して argv から除く(直せぬ紙に限る第四の道)
#                  ⒝當席が殻の `>` で作つた捕り = ★源の形(空である旨の一行)へ直す★
ZERO = [p for p in KAMI if os.path.getsize(p) == 0]
TAISHOU_ZERO = [p for p in ZERO if p in FX or p.startswith(os.path.join("raw", "70_minamoto") + os.sep)]
NAOSU = [p for p in ZERO if p not in TAISHOU_ZERO]
nao_rows = []
for rel in NAOSU:
    kaku(rel, "")          # ★KARA 一行 ―― 0byte を産まぬ書き器を通す★
    nao_rows.append([rel, 0, os.path.getsize(rel), "★源の形(空である旨の一行)へ直した★",
                     "端末で組んだ頃の捕り(殻の `>` で 0byte を作つた)"])
for rel in TAISHOU_ZERO:
    nao_rows.append([rel, 0, 0, "★直さぬ(宣して門の argv から除く)★",
                     "0byte で在る事が對照の中身ゆゑ ―― 通せば對照に成らぬ"])
# ★此の器は冪等ゆゑ、二度目の走りでは「前 byte=0」を己の目で見られぬ★ ――
#   已に直つた紙(中身が KARA 一行だけの紙)を第三の類として ★名指しで★ 挙げ、前 byte は『測れぬ』と書く。
#   (『直した』と『0 を見た』は別事 ―― 見て居らぬ數を 0 と書けば偽の實測に成る)
KARA_GYOU = kaki_m.KARA + "\n"
sude = [p for p in KAMI if p not in ZERO and os.path.getsize(p) == len(KARA_GYOU.encode("utf-8"))
        and open(p, encoding="utf-8", errors="replace").read() == KARA_GYOU]
# ★此の器が現に 0byte から直した 3 本(本弾の先の走りで門の條④が名指した紙)★ ――
#   出所: 門の鳴り「★EOF改行 ―― <紙> は空file(0byte)★」。端末で組んだ頃の捕りである。
#   残りの KARA 一行の紙は ★初めから書き器(00_kaki)を通した物★ で、0byte で在つた事が無い。
NAOSHITA_KIROKU = ["_letters/11_yomikaeshi.err", "_letters/12_mark_read.err", "_letters/20_chakushu.send.out"]
for rel in NAOSHITA_KIROKU:
    assert rel in sude, "★控の %s が KARA 一行で無い ―― 控を直せ★" % rel
for rel in sude:
    if rel in NAOSHITA_KIROKU:
        nao_rows.append([rel, "0(門が名指した ―― 此の走りでは已に直つて居る)", os.path.getsize(rel),
                         "★源の形へ直した(本弾)★", "端末で組んだ頃の捕り ―― 殻の `>` が 0byte を作つた"])
    else:
        nao_rows.append([rel, "0 で在つた事が無い", os.path.getsize(rel),
                         "★初めから源の形★", "書き器(00_kaki)を通して書いた出目"])
kaku_tsv(os.path.join(GA, "15_zero_wo_ichigyo.tsv"), nao_rows,
         header=["紙(束内相対)", "前 byte", "後 byte", "始末", "由"])

# ★除いた紙は「札 7」と「對照の 0byte 7」の ★和集合★ である ―― fx01/fx02 は両方に属す ∴ 足すと二重に数へる。
NOKEru = sorted(set(FX) | set(TAISHOU_ZERO))
ARGV = [p for p in KAMI if p not in NOKEru]
assert len(KAMI) - len(NOKEru) == len(ARGV), "★除いた數と argv が合はぬ★"

kaku(os.path.join(GA, "10_daichou_taishou.txt"),
     "刻=%s\n根=%s(★束★)\n臺帳へ載せる紙=%d 本／内 門の argv から宣して除く札=%d 本／argv=%d 本\n"
     "除く理由=raw/20_fx.sengen.txt(陽性対照ゆゑ直せぬ紙・第四の道)\n"
     "★此の紙自身は _gate/ に在り 員外★(臺帳に載らず・門も見ぬ)\n\n%s"
     % (KOKU, os.getcwd(), len(KAMI), len(FX), len(ARGV), "\n".join(KAMI)))

# ―― ① 臺帳を積む(束内相対・唯一の書き手を通す) ――
if os.path.exists("MANIFEST.txt"):
    os.remove("MANIFEST.txt")
o, e, rc = hashiru(["python3", "-B", TSUMI, "MANIFEST.txt"] + KAMI)
okusu("20_daichou_tsumi", o, e, rc)
assert rc == 0, "★臺帳の積みが rc=%d ―― 止める★\n%s" % (rc, e)
dai = open("MANIFEST.txt", encoding="utf-8").read().split("\n")
dai_gyou = [l for l in dai if l.startswith("path=")]
assert len(dai_gyou) == len(KAMI), "★臺帳 %d 行 ≠ 歩いた %d 本★" % (len(dai_gyou), len(KAMI))
# ★己が数へる ―― mon_ 行(門の出目が臺帳へ混ざつて居らぬか)★
mon_gyou = [l for l in dai_gyou if re.search(r"path=(?:\./)?%s/" % re.escape(GA), l) or "mon_" in l]

# ―― ② 對照 ―― 走り毎に ★名を別にした汚れ紙★ で門が現に鳴る事を見せる ――
TAISHOU = [("hatsubashiri", "60_taishou_ichi_matsubi_kuuhaku.txt", "汚れ=行末の空白一つ", "a \n"),
           ("nibashiri", "61_taishou_ni_crlf_to_kuugyou.txt", "汚れ=CR混入+末尾空行", "a\r\n\n")]
for _, na, _, body in TAISHOU:
    with open(os.path.join(GA, na), "w", encoding="utf-8", newline="") as fh:
        fh.write(body)     # ★kaki を通さぬ ―― 通せば汚れが落ちて對照に成らぬ★

# ―― ③ 門を二走 ――
rows = []
for i, (na, t_na, t_imi, _) in enumerate(TAISHOU, 1):
    # (a) 本走り: 臺帳と argv・★rc=0 を要求する★
    o, e, rc = hashiru(["bash", GATE, "MANIFEST.txt"] + ARGV, env_add={"KM_GATE_MANIFEST_BASE": "."})
    okusu("%d0_mon_%s" % (i + 2, na), o, e, rc)
    # (b) 對照走り: 同じ argv へ ★其の走り専用の名の汚れ紙★ を一枚足す ―― ★鳴らねば器ではない★
    t_rel = os.path.join(GA, t_na)
    to, te, trc = hashiru(["bash", GATE, "--"] + ARGV + [t_rel], env_add={"KM_GATE_MANIFEST_BASE": "."})
    okusu("%d1_taishou_%s" % (i + 2, na), to, te, trc)
    nari = [l for l in te.split("\n") if t_na in l]
    rows.append([i, na, t_na, t_imi, rc, ("★通★" if rc == 0 else "落ち"),
                 trc, ("★鳴つた(=器である)★" if trc != 0 and nari else "★鳴らず ―― 器を疑へ★"),
                 (nari[0][:58] if nari else "-")])
    assert rc == 0, "★%s の本走りが rc=%d ―― 止める★\n%s" % (na, rc, e)
    assert trc != 0 and nari, "★%s の對照が鳴らず(rc=%d) ―― 門か對照を疑へ★\n%s" % (na, trc, te)

kaku_tsv(os.path.join(GA, "70_mon_futabashiri.tsv"), rows,
         header=["走り", "名", "對照の紙(★走り毎に別名★)", "對照の汚れ", "本走り rc", "本走り",
                 "對照走り rc", "對照の判", "對照の鳴り(58字で截つ)"])


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


ingai = sorted(os.path.join(GA, f) for f in os.listdir(GA) if os.path.isfile(os.path.join(GA, f)))
zero = [p for p in ingai if os.path.getsize(p) == 0]
kaku(os.path.join(GA, "80_ingai_sengen.txt"),
     "刻=%s(此の紙を書いた時)\n根=%s(★束★)\n\n"
     "【臺帳の數 ―― 己が数へた】\n"
     "・臺帳の path= 行 = %d 行／歩いた紙 = %d 本(★一致★)\n"
     "・臺帳 sha256 = %s\n"
     "・★mon_ 行 = %d 行★(門の出目が臺帳へ混ざつて居らぬ事の數)\n"
     "・門の argv = %d 本(= 臺帳 %d − 宣して除いた紙 %d)\n"
     "  ★除いた紙は『札(raw/fx 7本)』と『對照の 0byte(7本)』の ★和集合★★ ―― fx01/fx02 は両方に属す ∴ 足せば二重に数へる。\n\n"
     "【員外(臺帳の後に出来た紙)】\n"
     "・則 = ★`_gate/` の下に出来る紙は悉く員外★(門の出目・對照の汚れ紙・此の宣そのもの)。\n"
     "  臺帳は門の ★前★ に凍る ∴ 門の出目を臺帳へ載せれば臺帳が己の後の紙を指す事に成る。\n"
     "・員外の本数 = %d 本(下に悉く名と寸法を挙げる ―― 『員外』は『数へて居らぬ』に非ず)\n"
     "・員外の内 0byte = %d 本(出目は悉く kaki を通す ∴ 0 で在るべし)\n"
     "・★對照の汚れ紙 2 本だけは kaki を通して居らぬ★ ―― 通せば汚れが落ち對照に成らぬ故(宣して除く第四の道)。\n\n"
     "【0byte の始末(_gate/15_zero_wo_ichigyo.tsv)】\n"
     "・此の走りで見た 0byte = %d 本 ―― 内 ★%d 本を源の形(空である旨の一行)へ直し★、%d 本は對照ゆゑ直さず宣して除いた。\n"
     "・★KARA 一行で在る紙 = %d 本★ ―― 内 ★3 本は本弾で 0byte から直した捕り★(門の條④が名指した紙)、\n"
     "  残りは初めから書き器を通した出目で ★0byte で在つた事が無い★(名と由は _gate/15 に一本づつ)。\n"
     "  器は冪等ゆゑ二度目の走りでは 0 を己の目で見ぬ ∴ 『直した』と『此の走りで 0 を見た』を分けて書く。\n"
     "・★除いた %d 本は臺帳には悉く載る★(條①は現に之等へ当たる) ―― 『除いた』は『歩いて居らぬ』に非ず。\n\n%s\n\n"
     "【之が意味せぬ事】\n"
     "・門が通つた事は ★紙の中身が正しい事ではない★ ―― 門は形(臺帳一致・不可視字・CR・EOF改行・寸法)のみを見る。\n"
     "・員外を宣した事は ★員外が検められた事ではない★ ―― 此の宣は名と寸法と 0byte の數のみを保つ。\n"
     % (datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"), os.getcwd(),
        len(dai_gyou), len(KAMI), sha("MANIFEST.txt"), len(mon_gyou), len(ARGV), len(KAMI),
        len(NOKEru), len(ingai), len(zero),
        len(ZERO), len(NAOSU), len(TAISHOU_ZERO), len(sude), len(NOKEru),
        "\n".join("  %-46s %7d byte" % (p, os.path.getsize(p)) for p in ingai)))

print("0byte %d 本 ―― 直した %d / 宣して除いた %d / 已に KARA 一行 %d 本" % (len(ZERO), len(NAOSU), len(TAISHOU_ZERO), len(sude)))
print("臺帳 %d 行(歩いた %d 本・mon_ 行 %d)／門 argv %d 本" % (len(dai_gyou), len(KAMI), len(mon_gyou), len(ARGV)))
for r in rows:
    print("  走り%s %s ―― 本走り rc=%s / 對照(%s) rc=%s %s" % (r[0], r[1], r[4], r[2], r[6], r[7]))
print("員外 %d 本(0byte %d 本)" % (len(ingai), len(zero)))
