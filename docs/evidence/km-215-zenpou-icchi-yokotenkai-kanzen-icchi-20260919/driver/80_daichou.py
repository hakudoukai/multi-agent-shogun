# -*- coding: utf-8 -*-
"""80 ―― 臺帳を建てる。★根は束内相対★(裁 seq322699)ゆゑ cwd=束 で追記器を呼ぶ。

★己(80)も束の紙である★ ―― 数へる側に己を入れる。
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
kami = []
for dp, dn, fn in os.walk(BUNDLE):
    dn[:] = sorted(d for d in dn if d != "__pycache__")
    for f in sorted(fn):
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, BUNDLE)
        if rel == OZOTO or rel.startswith("mon_"):
            continue
        if not os.path.isfile(p) or os.path.islink(p):
            continue
        kami.append(rel)
kami.sort()

TOOL = os.path.join(ROOT, "scripts", "checks", "karo_mac_manifest_append.py")
p = subprocess.run([sys.executable, "-B", TOOL, OZOTO] + kami, cwd=BUNDLE,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
rc = p.returncode
out = p.stdout.decode("utf-8", "replace")
err = p.stderr.decode("utf-8", "replace")

man = io.open(os.path.join(BUNDLE, OZOTO), encoding="utf-8").read()
path_gyou = [l for l in man.split("\n") if l.startswith("path=")]
# ★mon_ を二つの数で見る★: ⑴行頭が path=mon_ ⑵行の何處かに mon_ が在る(下層に紛れた物も拾ふ)
mon_atama = sum(1 for l in path_gyou if l.startswith("path=mon_"))
mon_dokoka = sum(1 for l in path_gyou if "mon_" in l)

K.kaku(os.path.join(BUNDLE, "raw", "80_daichou_shime.txt"), u"""★臺帳を建てた★
追記器 = scripts/checks/karo_mac_manifest_append.py ／ cwd = ★束の根★(臺帳の根は束内相対・裁 seq322699)
rc = {rc}(管を通さず returncode から取つた)

★書いた紙 = {n} 本★(臺帳の `path=` 行 = {g} 行 ／ 差 = {sa})
★臺帳の mon_ 行★: 行頭が `path=mon_` = ★{ma} 行★ ／ 行中の何處かに `mon_` = ★{md} 行★
  ―― ★二つとも 0 である事を宣する★(門控は臺帳に載せてはならぬ)。
  ★二つ数へる譯★: 行頭だけを見ると ★下層 dir に紛れた mon_ を見落とす★(例 `path=raw/mon_x`)。

★臺帳外(意図)★: manifest.txt 自身(紙は己を含む數を書けぬ)と、此の後に出る ★門控★・
  及び本紙より後に生まれる紙。其の實數は 90 で歩いて宣する。

器の言(out) = {o}
器の言(err) = {e}

★此の数が意味せぬ事★:
  ・{n} 本は ★此の刻の disk の状態★ である。★後で紙が増えれば此の数は古びる。★
  ・mon_ = 0 は「臺帳に門控が載つて居らぬ」の意であり、★門が通る事を意味せぬ★(門は別に走らせる)。
""".format(rc=rc, n=len(kami), g=len(path_gyou), sa=len(path_gyou) - len(kami),
           ma=mon_atama, md=mon_dokoka, o=out.strip() or u"―", e=err.strip() or u"―"))
print("rc=%d 本=%d path行=%d mon_頭=%d mon_中=%d"
      % (rc, len(kami), len(path_gyou), mon_atama, mon_dokoka))
assert rc == 0, "★追記器 rc=%d ―― %s★" % (rc, err)
assert mon_dokoka == 0, "★臺帳に mon_ が %d 行 混じつた★" % mon_dokoka
