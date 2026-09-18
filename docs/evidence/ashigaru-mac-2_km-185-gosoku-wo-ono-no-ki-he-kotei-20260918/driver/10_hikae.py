# -*- coding: utf-8 -*-
"""10 ―― ★写す前の控★(km-185 ㋒)。五束の全紙の 相対path・bytes・sha256 を採る。
★置き所は樹の外★ ―― 本束(共用樹の下)に置く。/tmp は禁(證の紙は束へ)。
★歩きは「全紙」である★ ―― __pycache__ も除かぬ。除けば「写せて居らぬ物」を見落とす。
  (臺帳は __pycache__ を除く方言ゆゑ、臺帳の數と此の數は ★一致せぬ束が在る★ ―― 其の差も刷る。)
★此の數が意味せぬ事★: 本表は ★此の刻の disk★ である。後で紙が増えれば古びる。
"""
import hashlib, io, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

TABA = [
    "docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918",
    "docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918",
    "docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918",
    "docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918",
    "docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918",
]


def aruki(base):
    out = []
    for dp, dn, fn in os.walk(base):
        dn[:] = sorted(dn)
        for f in sorted(fn):
            p = os.path.join(dp, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            out.append(p)
    return sorted(out)


rows, shime = [], []
for t in TABA:
    base = os.path.join(ROOT, t)
    assert os.path.isdir(base), u"★束が無い: %s★" % t
    fs = aruki(base)
    pyc = sum(1 for p in fs if "__pycache__" in p)
    wa = 0
    for p in fs:
        b = io.open(p, "rb").read()
        wa += len(b)
        rows.append((t, K.esc(os.path.relpath(p, base)), len(b),
                     hashlib.sha256(b).hexdigest()))
    shime.append((t, len(fs), pyc, len(fs) - pyc, wa))

K.kaku_tsv(os.path.join(KI, "raw", "10_hikae.tsv"), rows,
           header=("taba", "rel_path", "bytes", "sha256"))
K.kaku_tsv(os.path.join(KI, "raw", "10_shime.tsv"), shime,
           header=("taba", "kami_zen", "pycache", "kami_jo_pycache", "byte_wa"))
print(u"刻 = %s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
for r in shime:
    print(u"%-72s 全=%3d pycache=%d 除=%3d byte和=%d" % (r[0][14:], r[1], r[2], r[3], r[4]))
print(u"★合計 紙(全)=%d★ / 行(表)=%d" % (sum(r[1] for r in shime), len(rows)))
assert sum(r[1] for r in shime) == len(rows), u"★締と表の行が合はぬ★"
