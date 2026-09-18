# -*- coding: utf-8 -*-
"""55 ―― ★門を二度通す★。控の名は run ごとに変へる(同名へ二度書けば一度目が消える)。

★門控(mon_*)は束の根に置く★ ―― 50 の除外則は `rel.startswith("mon_")` である。
★門の出目は二流★: 門自身の行と結語 = stderr ／ 代行器 verify.py の要約 = stdout。★両方読む★。
★臺帳の根は束内相対★ ∴ `KM_GATE_MANIFEST_BASE=.` を要する(無ければ條①が悉く落ちる)。
rc は subprocess.run().returncode から素で採る(管を通さぬ)。
"""
import io
import os
import subprocess
import sys

KI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K  # noqa: E402

MON = os.path.join(ROOT, "scripts", "checks", "karo_mac_dasumae_gate.sh")
assert os.path.exists(MON), u"★門が無い★: %s" % MON

man = io.open(os.path.join(KI, "manifest.txt"), encoding="utf-8").read()
paths = []
for ln in man.split("\n"):
    if ln.startswith("path="):
        i = ln.find(" sha256=")
        assert i > 0, u"★sha256 欄の無い行★: %r" % ln[:60]
        paths.append(ln[len("path="):i])
assert paths, u"★臺帳に path 行が一つも無い★"
# ★臺帳外の二紙も條②③④⑤ には掛ける★ ―― 臺帳に載せられぬ(後に書かれる)故 argv で足す。
#   條① は臺帳の行だけを歩く故、argv に足しても「相違」には成らぬ(実測で確かめる)。
SOTO = [x for x in ("raw/50_daichou_shime.txt", "raw/70_daichougai.txt")
        if os.path.exists(os.path.join(KI, x))]
K.kaku(os.path.join(KI, "mon_paths.txt"), u"\n".join(paths))

kan = dict(os.environ, KM_GATE_MANIFEST_BASE=".", PYTHONDONTWRITEBYTECODE="1")
deme = []
for na in ("ichi", "ni"):
    p = subprocess.run(["bash", MON, "manifest.txt"] + paths + SOTO, cwd=KI, env=kan,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rc = p.returncode
    K.kaku(os.path.join(KI, "mon_bikae_%s.out" % na), p.stdout.decode("utf-8", "replace"))
    K.kaku(os.path.join(KI, "mon_bikae_%s.err" % na), p.stderr.decode("utf-8", "replace"))
    K.kaku(os.path.join(KI, "mon_bikae_%s.rc" % na), u"%d" % rc)
    deme.append((na, rc))
    print("門 控=%s rc=%d" % (na, rc))

print("★渡した path = %d 本(臺帳 %d + 臺帳外 %d)★" % (len(paths) + len(SOTO), len(paths), len(SOTO)))
for na, rc in deme:
    assert rc == 0, u"★門 控=%s が rc=%d で落ちた ―― 出すな★" % (na, rc)
