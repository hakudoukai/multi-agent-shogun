# -*- coding: utf-8 -*-
"""40 ―― ★三つの數の差を名指す★: 臺帳の行 / 彫つた commit の紙 / disk の紙。
★同じ「紙」と呼んで違ふ物を数へるな★(裁の語・數の規律)。三者は次の理由で食ひ違ふ:
  ⑴臺帳は ★己(manifest.txt)を含めぬ★(紙は己を含む數を書けぬ)
  ⑵臺帳は ★門控(mon_*)を除く★・束に依つては ★__pycache__ も除く★
  ⑶臺帳を建てた後に生まれた紙(90_okuri.txt・95_yomikaeshi.tsv・門控)は ★臺帳外★
  ⑷彫りは disk を其の儘持つ ∴ 臺帳外も悉く commit に入る
★門の條① が鳴つた札は 逐語で名指し、臺帳の宣(sha256/bytes)と disk の實を並べる。★
"""
import hashlib, io, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402
WT = os.path.expanduser("~/wt")
SOKU = [
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918", "k171a"),
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918", "k171b"),
    ("a2-km171", "docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918", "k171c"),
    ("a2-km172", "docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918", "k172"),
    ("a2-km174", "docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918", "k174"),
]

kazu, sai = [], []
for w, rel, na in SOKU:
    base = os.path.join(WT, w, rel)
    sen = {}
    for ln in io.open(os.path.join(base, "manifest.txt"), encoding="utf-8").read().split("\n"):
        if not ln.startswith("path="):
            continue
        d = {}
        for tok in ln.split(" "):
            if "=" in tok:
                k, _, v = tok.partition("=")
                d.setdefault(k, v)
        sen[d["path"]] = (int(d.get("bytes", -1)), d.get("sha256", u"―"))
    disk = {}
    for dp, dn, fn in os.walk(base):
        dn[:] = sorted(dn)
        for f in sorted(fn):
            p = os.path.join(dp, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            b = io.open(p, "rb").read()
            disk[os.path.relpath(p, base)] = (len(b), hashlib.sha256(b).hexdigest())
    p = subprocess.run(["git", "-C", os.path.join(WT, w), "ls-tree", "-r", "--name-only", "HEAD", "--", rel],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hori = sorted(l[len(rel) + 1:] for l in p.stdout.decode("utf-8", "replace").split("\n") if l.strip())
    gai = sorted(set(disk) - set(sen))
    nashi = sorted(set(sen) - set(disk))
    soui = sorted(k for k in set(sen) & set(disk) if sen[k] != disk[k])
    pyc = sum(1 for k in disk if "__pycache__" in k)
    kazu.append((na, len(sen), len(hori), len(disk), pyc, len(gai), len(nashi), len(soui), p.returncode))
    for k in soui:
        sai.append((na, K.esc(k), sen[k][0], disk[k][0], sen[k][1][:16], disk[k][1][:16],
                    u"bytes も sha も動いた" if sen[k][0] != disk[k][0] else u"bytes 同じ・sha 相違"))
K.kaku_tsv(os.path.join(KI, "raw", "40_kazu.tsv"), kazu,
           header=("soku", "daichou_gyou", "hotta_kami", "disk_kami", "pycache",
                   "daichougai", "daichou_ari_disk_nashi", "soui", "rc_lstree"))
K.kaku_tsv(os.path.join(KI, "raw", "40_soui.tsv"), sai or [(u"―",) * 7],
           header=("soku", "rel_path", "sen_bytes", "disk_bytes", "sen_sha16", "disk_sha16", "kata"))
print(u"刻 = %s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
print(u"%-6s 臺帳 彫 disk pyc 臺帳外 帳有disk無 相違" % u"束")
for r in kazu:
    print(u"%-6s %4d %4d %4d %3d %5d %8d %5d" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
print(u"★相違の札 計 = %d★" % len(sai))
assert sum(r[6] for r in kazu) == 0, u"★臺帳に在り disk に無い札が在る★"
assert all(r[2] == r[3] for r in kazu), u"★彫つた紙と disk の紙が合はぬ★"
