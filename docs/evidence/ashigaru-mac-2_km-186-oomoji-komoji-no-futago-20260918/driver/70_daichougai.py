# -*- coding: utf-8 -*-
"""70 ―― ★臺帳外の紙を歩いて宣する★(裁の「員外を 0 と言ふな」)。
★己(此の紙)と、此の後に出る門控は 此の数に入らぬ★ ―― 数へた後に生まれる故である。
∴ ★入らぬ物の名を先に挙げる★。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

OZOTO = "manifest.txt"
KONO_KAMI = os.path.join("raw", "70_daichougai.txt")

man = io.open(os.path.join(BUNDLE, OZOTO), encoding="utf-8").read()
sengen = set()
for l in man.split("\n"):
    if l.startswith("path="):
        # ★方言は四欄★: path=<p> sha256=<64hex> bytes=<n> lines=<n>
        v = l[len("path="):].split(" sha256=")[0]
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        sengen.add(v)

disk = []
for dp, dn, fn in os.walk(BUNDLE):
    dn[:] = sorted(dn)
    for f in sorted(fn):
        p = os.path.join(dp, f)
        if not os.path.isfile(p) or os.path.islink(p):
            continue
        disk.append(os.path.relpath(p, BUNDLE))
disk.sort()
ingai = [d for d in disk if d not in sengen]

K.kaku(os.path.join(BUNDLE, KONO_KAMI), u"""★70 ―― 臺帳外の紙を歩いた★
歩き根 = 束の根(bundle 相対) ／ 刻 = 歩いた時の disk の状態

★disk の紙 = {d} 本★ ／ ★臺帳が宣する path = {s} 行★ ／ ★臺帳外 = {i} 本★

臺帳外の逐語:
{namae}

★此の數に入らぬ物(★名を挙げる★)★:
  ・{kono}(★此の紙自身★ ―― 数へた後に書かれる)
  ・`mon_*`(門控 ―― 此の後に出る)
∴ ★門を通した後の臺帳外は {i} + 1(此の紙) + 門控の本数 に成る。★

★此の數が意味せぬ事★:
  ・臺帳外 = {i} 本は ★誤りの數ではない★ ―― 臺帳は己(manifest.txt)と `__pycache__` を意図して除く。
  ・「臺帳外」は ★門の條①に鳴らぬ★(條①は臺帳の行と disk の差を見る故)。★通る事を意味せぬ★ ――
    門は別に走らせ、rc を刷る。
""".format(d=len(disk), s=len(sengen), i=len(ingai), kono=KONO_KAMI,
           namae=u"\n".join(u"  ・" + n for n in ingai) or u"  ―(無し)"))
print(u"disk=%d 宣=%d 臺帳外=%d ―― %s" % (len(disk), len(sengen), len(ingai), u"／".join(ingai)))
