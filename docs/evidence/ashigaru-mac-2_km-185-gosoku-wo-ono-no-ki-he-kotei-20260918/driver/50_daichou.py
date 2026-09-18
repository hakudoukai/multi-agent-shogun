# -*- coding: utf-8 -*-
"""50 ―― 臺帳を建てる。★根は束内相対★(裁 seq322699)ゆゑ cwd=束 で追記器を呼ぶ。

★己(50)も束の紙である★ ―― 数へる側に己を入れる。
臺帳自身と、此の後に出る門控は ★臺帳外★ に成る(紙は己を含む數を書けぬ・門控は後に出る)。
★mon_ の行は臺帳に一つも在つてはならぬ★ ―― 数へて刷る(0 を宣する)。
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

OZOTO = "manifest.txt"
# ★臺帳より後に書かれる紙は臺帳に載せられぬ★ ―― 載せると 條① が必ず鳴る(km-186 実測 相違 2)。
#   ⑴raw/50_daichou_shime.txt = 本器が ★追記器を呼んだ後★ に書く己の〆
# ∴ ★意図して除き、名を挙げて宣する★。條②③④⑤ は 55 が argv で別に当てる。
ATO = ("raw/50_daichou_shime.txt",)
kami = []
for dp, dn, fn in os.walk(BUNDLE):
    dn[:] = sorted(d for d in dn if d != "__pycache__")
    for f in sorted(fn):
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, BUNDLE)
        if rel == OZOTO or rel.startswith("mon_") or rel in ATO:
            continue
        if not os.path.isfile(p) or os.path.islink(p):
            continue
        kami.append(rel)
kami.sort()

# ★追記器は「追記」である ―― 二度走らせると行が倍に成る(km-186 実測 71→144 行)。★
# ∴ 建て直す時は ★先に古い臺帳を退け、其の姿(行數と sha256)を控へてから★ 建てる。
import hashlib
furui = os.path.join(BUNDLE, OZOTO)
if os.path.exists(furui):
    b = io.open(furui, "rb").read()
    FURUI = u"行=%d ／ sha256=%s ／ bytes=%d" % (
        b.count(b"\npath=") + (1 if b.startswith(b"path=") else 0),
        hashlib.sha256(b).hexdigest(), len(b))
    os.unlink(furui)
else:
    FURUI = u"★無し(初めて建てる)★"

TOOL = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_append.py")
p = subprocess.run([sys.executable, "-B", TOOL, OZOTO] + kami, cwd=BUNDLE,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
rc = p.returncode
out = p.stdout.decode("utf-8", "replace")
err = p.stderr.decode("utf-8", "replace")

man = io.open(os.path.join(BUNDLE, OZOTO), encoding="utf-8").read()
path_gyou = [l for l in man.split("\n") if l.startswith("path=")]
# ★mon_ を三つの数で見る★(km-185 で一つ足した ―― 二つでは偽に鳴つた)
#   ⑴行頭が path=mon_        …… 束の根に置いた門控
#   ⑵★basename が mon_ で始まる★ …… 下層 dir に紛れた門控(例 path=raw/mon_x)も拾ふ ―― ★之が禁の實體★
#   ⑶行の何處かに mon_ が在る   …… ★禁ではない★。参考に数へるのみ。
# ★⑶で禁じては成らぬ譯(km-185 実測)★: 本束は五束の門控を raw/35_mon_<束>_<回>.out 等の名で持つ。
#   之は ★己の門控ではなく、測つた対象の出目★ であり、臺帳に載るべき紙である。
#   旧 50 は ⑶で assert して居た故 30 行に鳴り、★偽の鳴り★ と成つた。
#   ―― 加へて旧 50 は ★assert を書込の後に置いて居た★。鳴つても臺帳は既に書かれて居る。★書込の前へ移した。★
mon_atama = sum(1 for l in path_gyou if l.startswith("path=mon_"))
mon_base = sum(1 for l in path_gyou
               if os.path.basename(l[len("path="):l.find(" sha256=")]).startswith("mon_"))
mon_dokoka = sum(1 for l in path_gyou if "mon_" in l)

# ★assert は書込の前★(裁333131②・家老の疵の形を踏まぬ)
assert rc == 0, "★追記器 rc=%d ―― %s★" % (rc, err)
assert mon_atama == 0 and mon_base == 0, \
    "★臺帳に門控が混じつた(行頭 %d 行／basename %d 行)★" % (mon_atama, mon_base)

K.kaku(os.path.join(BUNDLE, "raw", "50_daichou_shime.txt"), u"""★臺帳を建てた★
追記器 = scripts/checks/karo_mac_manifest_append.py ／ cwd = ★束の根★(臺帳の根は束内相対・裁 seq322699)
rc = {rc}(管を通さず returncode から取つた)
★建てる前に在つた臺帳★ = {furui} ―― ★退けてから建てた(追記器は追記ゆゑ二度走ると倍に成る)★
★臺帳外(名を挙げて除いた紙)★ = raw/50_daichou_shime.txt(本紙自身 ―― 追記器の後に書かれる)
  ―― 條②③④⑤ は 55 が argv で当てる。條① は臺帳の行のみを歩く故 鳴らぬ。

★書いた紙 = {n} 本★(臺帳の `path=` 行 = {g} 行 ／ 差 = {sa})
★臺帳の mon_ 行(三つの數)★:
  ⑴行頭が `path=mon_`            = ★{ma} 行★ ―― ★0 を宣する(禁)★
  ⑵basename が `mon_` で始まる    = ★{mb} 行★ ―― ★0 を宣する(禁)★。下層に紛れた門控も拾ふ
  ⑶行の何處かに `mon_` が在る      = {md} 行 ―― ★禁ではない★(参考)
  ★⑶を禁にしてはならぬ★: 本束は五束の門控を `raw/35_mon_<束>_<回>.out` 等の名で持つ ――
  之は ★己の門控ではなく測つた対象の出目★ であり、臺帳に載るべき紙である。

★臺帳外(意図)★: manifest.txt 自身(紙は己を含む數を書けぬ)と、此の後に出る ★門控★・
  及び本紙より後に生まれる紙。其の實數は 60 で歩いて宣する。

器の言(out) = {o}
器の言(err) = {e}

★此の数が意味せぬ事★:
  ・{n} 本は ★此の刻の disk の状態★ である。★後で紙が増えれば此の数は古びる。★
  ・mon_ = 0 は「臺帳に門控が載つて居らぬ」の意であり、★門が通る事を意味せぬ★(門は別に走らせる)。
""".format(furui=FURUI, rc=rc, n=len(kami), g=len(path_gyou), sa=len(path_gyou) - len(kami),
           ma=mon_atama, mb=mon_base, md=mon_dokoka, o=out.strip() or u"―", e=err.strip() or u"―"))
print("rc=%d 本=%d path行=%d mon_頭=%d mon_base=%d mon_中=%d(参考)"
      % (rc, len(kami), len(path_gyou), mon_atama, mon_base, mon_dokoka))
