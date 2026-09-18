# -*- coding: utf-8 -*-
"""35 ―― ★彫つた五束に門を二度通す★(km-185 ㋕)。cwd=束・KM_GATE_MANIFEST_BASE=. (裁322699)。
★門控を束の中へ置かぬ★ ―― 置けば ★彫つた後に束が動く★。控は本束(km-185)の raw/ へ採る。
★出目は二流★: 門自身の行と結語=stderr ／ 代行器 verify.py の要約=stdout。★別の file へ採る★。
★rc=0 でない時も止めず、悉く走らせてから最後に纏めて名指す★ ―― 一本目で止まれば残りの出目が採れぬ。
"""
import io, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

MON = os.path.join(ROOT, "scripts", "checks", "karo_mac_dasumae_gate.sh")
assert os.path.exists(MON), u"★門が無い★: %s" % MON
WT = os.path.expanduser("~/wt")
SOKU = [
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918", "k171a"),
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918", "k171b"),
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918", "k171c"),
    ("a2-km172", "docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918", "k172"),
    ("a2-km174", "docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918", "k174"),
]
KAN = dict(os.environ, KM_GATE_MANIFEST_BASE=".", PYTHONDONTWRITEBYTECODE="1")
BYTE_WA = re.compile(u"byte和 (\\d+)")

rows, ochita = [], []
for w, rel, na in SOKU:
    base = os.path.join(WT, w, rel)
    man = io.open(os.path.join(base, "manifest.txt"), encoding="utf-8").read()
    paths = []
    for ln in man.split("\n"):
        if ln.startswith("path="):
            i = ln.find(" sha256=")
            assert i > 0, u"★sha256 欄の無い行★: %r" % ln[:60]
            paths.append(ln[len("path="):i])
    assert paths, u"★臺帳に path 行が一つも無い: %s★" % rel
    K.kaku(os.path.join(KI, "raw", "35_paths_%s.txt" % na), u"\n".join(paths))
    for kai in ("ichi", "ni"):
        p = subprocess.run(["bash", MON, "manifest.txt"] + paths, cwd=base, env=KAN,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rc = p.returncode
        o = p.stdout.decode("utf-8", "replace")
        e = p.stderr.decode("utf-8", "replace")
        K.kaku(os.path.join(KI, "raw", "35_mon_%s_%s.out" % (na, kai)), o)
        K.kaku(os.path.join(KI, "raw", "35_mon_%s_%s.err" % (na, kai)), e)
        K.kaku(os.path.join(KI, "raw", "35_mon_%s_%s.rc" % (na, kai)), u"%d" % rc)
        m = BYTE_WA.search(e) or BYTE_WA.search(o)
        wa = m.group(1) if m else u"★拾へず★"
        nari = [l for l in e.split("\n") if l.startswith(u"★條") or (u"條" in l and u"落ちた" in l)]
        rows.append((na, w, kai, rc, len(paths), wa, K.esc(u"|".join(nari)) or u"―"))
        print(u"%-6s %-4s rc=%d path=%d byte和=%s" % (na, kai, rc, len(paths), wa))
        if rc != 0:
            ochita.append((na, kai, rc))

K.kaku_tsv(os.path.join(KI, "raw", "35_mon.tsv"), rows,
           header=("soku", "ki", "kai", "rc", "watashita_path", "byte_wa", "narishi_jou"))
# ★二度の byte和 が同じ事を束ごとに書く★
wa_onaji = []
for w, rel, na in SOKU:
    f = [r for r in rows if r[0] == na]
    wa_onaji.append((na, f[0][5], f[1][5], u"同" if f[0][5] == f[1][5] else u"★違★"))
K.kaku_tsv(os.path.join(KI, "raw", "35_bytewa.tsv"), wa_onaji,
           header=("soku", "ichi_byte_wa", "ni_byte_wa", "onaji_ka"))
K.kaku(os.path.join(KI, "raw", "35_shime.txt"), u"""★門の〆★ 刻 = {t}
走らせた束 = {n} ／ 走り = 束ごと二度 = ★{r} 回★
★落ちた回 = {oc} 回★ {ocs}
★二度の byte和★ = raw/35_bytewa.tsv 逐語(同/違)
★此の數が意味せぬ事★:
  ・rc=0 は ★臺帳と disk が合ふ★ の意であり、★中身が正しい事を意味せぬ★。
  ・rc≠0 の條は ★分けて数へよ★ ―― 條①(臺帳とdiskの差)と條⑤(byte和)は別物である。
  ・門は ★臺帳外の紙に鳴らぬ★ ∴ rc=0 でも束に臺帳外の紙が在り得る。
""".format(t=time.strftime("%Y-%m-%dT%H:%M:%S%z"), n=len(SOKU), r=len(rows),
           oc=len(ochita), ocs=K.esc(u"|".join(u"%s/%s rc=%d" % x for x in ochita)) or u"―"))
print(u"★落ちた回 = %d★" % len(ochita))
