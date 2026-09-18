# -*- coding: utf-8 -*-
"""★臺帳を積み、門を二走させる★(km-175 ㋖) ―― 端末で組まず器で行ふ。
條: 臺帳は ★束内相対★(裁 seq322699 ―― cd <束> してから append)／門は `KM_GATE_MANIFEST_BASE=.`
    (門の usage 冠は此の env を書かぬ ―― 書かねば條①が悉く落ちる)／
    ★二走・對照の名を走り毎に別にせよ★(家老mac 條)／出目は kaki 経由 ∴ 0byte を産まぬ(裁 seq310228⑶)。
★本弾は宣して除く札が 0 本★ ―― 0byte も無く、直せぬ陽性対照の紙も無い ∴ 臺帳 = 門の argv(同数)。
四札: 刻=各紙の冠 / 根=cwd(★束★) / rc=subprocess の returncode(★管を通さず★) / 對照=走り毎の汚れ紙。"""
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

os.chdir(BUNDLE)
GA = "_gate"
os.makedirs(GA, exist_ok=True)


def hashiru(args, cwd=".", env_add=None, tmo=600):
    e = dict(os.environ)
    if env_add:
        e.update(env_add)
    p = subprocess.run(args, cwd=cwd, env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=tmo)
    return (p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), p.returncode)


def okusu(na, out, err, rc):
    kaku(os.path.join(GA, na + ".out"), out)
    kaku(os.path.join(GA, na + ".err"), err)
    kaku(os.path.join(GA, na + ".rc"), str(rc))
    return rc


def aruku():
    """★臺帳へ載せる紙★ を束内相対で歩く ―― 除くのは MANIFEST.txt 自身・_gate/(員外)・__pycache__。
    ★S_ISREG を要る★ ―― symlink/FIFO を歩けば open() で止まる(km-64 の疵)。"""
    kami = []
    for d, ds, fs in os.walk("."):
        ds[:] = sorted(x for x in ds if x != "__pycache__" and os.path.join(d, x) != os.path.join(".", GA))
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(d, f), ".")
            if rel == "MANIFEST.txt" or rel.startswith(GA + os.sep):
                continue
            if not os.path.isfile(rel) or os.path.islink(rel):
                continue
            kami.append(rel)
    return sorted(kami)


KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
KAMI = aruku()

# ―― ★0byte の掃討(先に測る ―― 門の條④が鳴る形である)★ ――
ZERO = [p for p in KAMI if os.path.getsize(p) == 0]
KARA_GYOU = kaki_m.KARA + "\n"
kara = [p for p in KAMI if os.path.getsize(p) == len(KARA_GYOU.encode("utf-8"))
        and open(p, encoding="utf-8", errors="replace").read() == KARA_GYOU]
assert not ZERO, "★0byte が %d 本 ―― 源の形へ直してから門へ掛けよ★ %s" % (len(ZERO), ZERO[:5])
NOKEru = []                       # ★本弾は宣して除く紙が 0 本(直せぬ陽性対照の紙が無い)★
ARGV = [p for p in KAMI if p not in NOKEru]
assert len(ARGV) == len(KAMI), "★除いた數と argv が合はぬ★"

kaku(os.path.join(GA, "10_daichou_taishou.txt"),
     "刻=%s\n根=%s(★束★)\n"
     "臺帳へ載せる紙=%d 本／門の argv=%d 本(★宣して除く紙 0 本 ∴ 同数★)\n"
     "0byte=%d 本(掃討済)／KARA 一行=%d 本(初めから書き器を通した出目)\n"
     "★此の紙自身は _gate/ に在り 員外★(臺帳に載らず・門も見ぬ)\n\n%s"
     % (KOKU, os.getcwd(), len(KAMI), len(ARGV), len(ZERO), len(kara), "\n".join(KAMI)))

# ―― ① 臺帳を積む ――
if os.path.exists("MANIFEST.txt"):
    os.remove("MANIFEST.txt")
o, e, rc = hashiru(["python3", "-B", TSUMI, "MANIFEST.txt"] + KAMI)
okusu("20_daichou_tsumi", o, e, rc)
assert rc == 0, "★臺帳の積みが rc=%d ―― 止める★\n%s" % (rc, e)
dai = open("MANIFEST.txt", encoding="utf-8").read().split("\n")
dai_gyou = [l for l in dai if l.startswith("path=")]
assert len(dai_gyou) == len(KAMI), "★臺帳 %d 行 ≠ 歩いた %d 本★" % (len(dai_gyou), len(KAMI))
mon_gyou = [l for l in dai_gyou if re.search(r"path=(?:\./)?%s/" % re.escape(GA), l) or "mon_" in l]

# ―― ② 對照(走り毎に ★名を別にした★ 汚れ紙) ――
TAISHOU = [("hatsubashiri", "60_taishou_ichi_matsubi_kuuhaku.txt", "汚れ=行末の空白一つ", "a \n"),
           ("nibashiri", "61_taishou_ni_crlf_to_kuugyou.txt", "汚れ=CR混入+末尾空行", "a\r\n\n")]
for _, na, _, body in TAISHOU:
    with open(os.path.join(GA, na), "w", encoding="utf-8", newline="") as fh:
        fh.write(body)     # ★kaki を通さぬ ―― 通せば汚れが落ちて對照に成らぬ★

# ―― ③ 門を二走 ――
rows = []
for i, (na, t_na, t_imi, _) in enumerate(TAISHOU, 1):
    o, e, rc = hashiru(["bash", GATE, "MANIFEST.txt"] + ARGV, env_add={"KM_GATE_MANIFEST_BASE": "."})
    okusu("%d0_mon_%s" % (i + 2, na), o, e, rc)
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
zero_i = [p for p in ingai if os.path.getsize(p) == 0]
kaku(os.path.join(GA, "80_ingai_sengen.txt"),
     "刻=%s(此の紙を書いた時)\n根=%s(★束★)\n\n"
     "【臺帳の數 ―― 己が数へた】\n"
     "・臺帳の path= 行 = %d 行／歩いた紙 = %d 本(★一致★)\n"
     "・臺帳 sha256 = %s\n"
     "・★mon_ 行 = %d 行★(門の出目が臺帳へ混ざつて居らぬ事の數)\n"
     "・門の argv = %d 本 ―― ★本弾は宣して除いた紙が 0 本★ ∴ 臺帳と同数。\n"
     "  (先弾は『直せぬ陽性対照の紙』を宣して除いたが、本弾には其の類の紙が無い。)\n"
     "・0byte = %d 本(門の條④が鳴る形 ―― 掃討して 0)／KARA 一行 = %d 本(初めから書き器を通した出目)\n\n"
     "【員外(臺帳の後に出来た紙)】\n"
     "・則 = ★`_gate/` の下に出来る紙は悉く員外★(門の出目・對照の汚れ紙・此の宣そのもの)。\n"
     "  臺帳は門の ★前★ に凍る ∴ 門の出目を臺帳へ載せれば臺帳が己の後の紙を指す事に成る。\n"
     "・員外の本数 = %d 本(下に悉く名と寸法を挙げる ―― 『員外』は『数へて居らぬ』に非ず)\n"
     "・員外の内 0byte = %d 本(出目は悉く kaki を通す ∴ 0 で在るべし)\n"
     "・★對照の汚れ紙 2 本だけは kaki を通して居らぬ★ ―― 通せば汚れが落ち對照に成らぬ故。\n\n%s\n\n"
     "【之が意味せぬ事】\n"
     "・門が通つた事は ★紙の中身が正しい事ではない★ ―― 門は形(臺帳一致・不可視字・CR・EOF改行・寸法)のみを見る。\n"
     "・員外を宣した事は ★員外が検められた事ではない★ ―― 此の宣は名と寸法と 0byte の數のみを保つ。\n"
     % (datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"), os.getcwd(),
        len(dai_gyou), len(KAMI), sha("MANIFEST.txt"), len(mon_gyou), len(ARGV),
        len(ZERO), len(kara), len(ingai), len(zero_i),
        "\n".join("  %-46s %7d byte" % (p, os.path.getsize(p)) for p in ingai)))

print("臺帳 %d 行(歩いた %d 本・mon_ 行 %d)／門 argv %d 本(除いた %d)" % (len(dai_gyou), len(KAMI), len(mon_gyou), len(ARGV), len(NOKEru)))
print("臺帳 sha256= %s" % sha("MANIFEST.txt"))
for r in rows:
    print("  走り%s %s ―― 本走り rc=%s / 對照(%s) rc=%s %s" % (r[0], r[1], r[4], r[2], r[6], r[7]))
print("員外 %d 本(0byte %d 本)" % (len(ingai), len(zero_i)))
