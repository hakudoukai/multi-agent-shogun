# -*- coding: utf-8 -*-
"""20 ―― 五束を己の三樹へ写し、★母數と一致数の両方を書く★(km-185 ㋒)。
★元の束は一指も触れぬ★ ―― 読むだけ。copy2 で刻も持つて行く。
★一致は「sha256 が等しい」だけでは足らぬ★ ―― ⑴宛に實體が在る ⑵bytes が等しい ⑶sha256 が等しい
  の三つを別々に数へる(一つに畳むと「実体無」が「不一致」に紛れる)。
★此の數が意味せぬ事★: 一致 314/314 は ★写しが正しい★の意であり、★commit された★の意ではない
  (commit は 30 の仕事・git add -f を要する ―― docs/evidence は .gitignore:7 の裸の `*` に落ちる)。
"""
import hashlib, io, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

KI_SAKI = {
    "docs/evidence/ashigaru-mac-2_km-171-ukeire-to-genbutsu-no-sa-wo-hakaru-403-ka-404-ka-20260918": "a2-km171",
    "docs/evidence/ashigaru-mac-2_km-171-uke-ire-no-jimen-wo-404-he-20260918": "a2-km171",
    "docs/evidence/ashigaru-mac-2_km-171-toi-heno-kotae-20260918": "a2-km171",
    "docs/evidence/ashigaru-mac-2_km-172-hako-no-utsushi-de-fail-open-wo-jissho-suru-20260918": "a2-km172",
    "docs/evidence/ashigaru-mac-2_km-174-otona-ban-yoyaku-iriguchi-ichi-oufuku-20260918": "a2-km174",
}
WT = os.path.expanduser("~/wt")

hikae = io.open(os.path.join(KI, "raw", "10_hikae.tsv"), encoding="utf-8").read().split("\n")
hdr, rows = hikae[0], [l for l in hikae[1:] if l.strip()]
assert hdr == u"taba\trel_path\tbytes\tsha256", u"★控の頭が違ふ: %s★" % hdr

bo, jitsutai, byte_icchi, sha_icchi = 0, 0, 0, 0
warui = []
for ln in rows:
    taba, rel, by, sha = ln.split("\t")
    by = int(by)
    assert "\\" not in rel, u"★行器を壊す名が在る(esc された): %s★" % rel
    src = os.path.join(ROOT, taba, rel)
    dst = os.path.join(WT, KI_SAKI[taba], taba, rel)
    bo += 1
    d = os.path.dirname(dst)
    if not os.path.isdir(d):
        os.makedirs(d)
    shutil.copy2(src, dst)
    if not os.path.isfile(dst):
        warui.append((taba, rel, u"実体無"))
        continue
    jitsutai += 1
    b = io.open(dst, "rb").read()
    if len(b) == by:
        byte_icchi += 1
    else:
        warui.append((taba, rel, u"bytes %d→%d" % (by, len(b))))
    if hashlib.sha256(b).hexdigest() == sha:
        sha_icchi += 1
    else:
        warui.append((taba, rel, u"sha256 相違"))

K.kaku_tsv(os.path.join(KI, "raw", "20_warui.tsv"), warui or [(u"―", u"―", u"★一本も無い★")],
           header=("taba", "rel_path", "shou"))
K.kaku(os.path.join(KI, "raw", "20_shime.txt"), u"""★写しの〆★ 刻 = {t}
★母數(控の行) = {bo}★
  ⑴宛に實體が在る  = {j} / {bo}
  ⑵bytes が等しい  = {b} / {bo}
  ⑶sha256 が等しい = {s} / {bo}
  ★悪い行 = {w} 本★(raw/20_warui.tsv 逐語)
写し先: {m}
★此の數が意味せぬ事★: 一致 {s}/{bo} は ★写しが正しい★ の意のみ。
  ・★commit された事を意味せぬ★(30 の仕事・docs/evidence は .gitignore:7 の裸の `*` に落ちる故 add -f を要する)。
  ・★元の束が不動である事を意味せぬ★(之は 25 が共用樹の porcelain と控で別に測る)。
""".format(t=time.strftime("%Y-%m-%dT%H:%M:%S%z"), bo=bo, j=jitsutai, b=byte_icchi,
           s=sha_icchi, w=len(warui),
           m=u" / ".join(u"%s→~/wt/%s" % (k[14:40], v) for k, v in sorted(KI_SAKI.items()))))
print(u"母數=%d 実体=%d bytes一致=%d sha一致=%d 悪い=%d" % (bo, jitsutai, byte_icchi, sha_icchi, len(warui)))
assert len(warui) == 0 and sha_icchi == bo, u"★写しが揃はぬ★"
