# -*- coding: utf-8 -*-
"""25 ―― ★元の束と共用樹の不動★を測る(km-185 ㋓)。控名を argv から取る(前/後で二度走らす為)。
用法: python3 driver/25_fudou.py <控名>
測る物:
  ⑴五束の全紙を歩き直し 10_hikae.tsv と ★path集合・bytes・sha256★ を突き合はせる
  ⑵共用樹の HEAD 40桁 ／ index(git ls-files -s の sha256) ／ porcelain の行数
     ―― ★porcelain の行数は stdout のみ数へる★(stderr の warning を混ぜれば數が偽に成る)
  ⑶docs/runbooks の porcelain(家老曰く case 双子で常に 1 行 ―― 之は前から在る)
★此の數が意味せぬ事★: porcelain の行数が同じでも ★中身が同じとは限らぬ★ ∴ 行の逐語も採る。
"""
import hashlib, io, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(KI, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

NA = sys.argv[1]
TABA = sorted(set(l.split("\t")[0] for l in
                  io.open(os.path.join(KI, "raw", "10_hikae.tsv"), encoding="utf-8").read().split("\n")[1:]
                  if l.strip()))


def aruki(base):
    out = {}
    for dp, dn, fn in os.walk(base):
        dn[:] = sorted(dn)
        for f in sorted(fn):
            p = os.path.join(dp, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            b = io.open(p, "rb").read()
            out[os.path.relpath(p, base)] = (len(b), hashlib.sha256(b).hexdigest())
    return out


hikae = {}
for l in io.open(os.path.join(KI, "raw", "10_hikae.tsv"), encoding="utf-8").read().split("\n")[1:]:
    if not l.strip():
        continue
    t, rel, by, sha = l.split("\t")
    hikae.setdefault(t, {})[rel] = (int(by), sha)

rows = []
zen_fue, zen_ke, zen_ugoki, zen_bo = 0, 0, 0, 0
for t in TABA:
    ima = aruki(os.path.join(ROOT, t))
    mae = hikae[t]
    fue = sorted(set(ima) - set(mae))
    ke = sorted(set(mae) - set(ima))
    ugoki = sorted(k for k in set(ima) & set(mae) if ima[k] != mae[k])
    zen_bo += len(mae); zen_fue += len(fue); zen_ke += len(ke); zen_ugoki += len(ugoki)
    rows.append((t, len(mae), len(ima), len(fue), len(ke), len(ugoki),
                 K.esc(u"|".join(fue + ke + ugoki)) or u"―"))
K.kaku_tsv(os.path.join(KI, "raw", "25_taba_%s.tsv" % NA), rows,
           header=("taba", "hikae_kami", "ima_kami", "fueta", "kieta", "ugoita", "namae"))


def g(*a):
    p = subprocess.run(["git", "-C", ROOT] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

rc_h, head, _ = g("rev-parse", "HEAD")
rc_i, idx, _ = g("ls-files", "-s")
rc_p, por, per = g("status", "--porcelain")
rc_r, run, _ = g("status", "--porcelain", "--", "docs/runbooks")
por_gyou = [l for l in por.split("\n") if l != ""]

K.kaku(os.path.join(KI, "raw", "25_ki_%s.txt" % NA), u"""★共用樹と元束の不動 ―― 控={na}★ 刻 = {t}
[元の束]
  母數(控の紙) = {bo} ／ ★増えた = {f} ／ 消えた = {k} ／ 中身が動いた = {u}★
  (束ごとの内訳 = raw/25_taba_{na}.tsv 逐語)
[共用樹 /Users/momizimac/multi-agent-shogun]
  HEAD(40桁) = {h}  (rc={rch})
  index = git ls-files -s の sha256 = {ix}  (rc={rci}・{n}行)
  porcelain = ★{pg} 行★(rc={rcp}・★stdout のみ★ ―― stderr の warning は数へて居らぬ)
    stderr(逐語) = {pe}
  docs/runbooks の porcelain (rc={rcr}) =
{ru}
★此の數が意味せぬ事★:
  ・増えた/消えた/動いた が悉く 0 は ★元の束を當席が触れて居らぬ★ の意。
    ★他席が触れて居らぬ事は之では言へぬ★(當席は他席の手を測れぬ)。
  ・porcelain の行数が前後で同じでも ★中身が同じとは限らぬ★ ∴ docs/runbooks の逐語を併せ採つた。
""".format(na=NA, t=time.strftime("%Y-%m-%dT%H:%M:%S%z"), bo=zen_bo, f=zen_fue, k=zen_ke, u=zen_ugoki,
           h=head.strip(), rch=rc_h, ix=hashlib.sha256(idx.encode("utf-8")).hexdigest(),
           rci=rc_i, n=len(idx.strip().split("\n")), pg=len(por_gyou), rcp=rc_p,
           pe=K.esc(per.strip()) or u"―", rcr=rc_r,
           ru=u"\n".join(u"    " + K.esc(l) for l in run.split("\n") if l) or u"    ―"))
print(u"控=%s 増=%d 消=%d 動=%d ／ HEAD=%s porcelain=%d行" % (NA, zen_fue, zen_ke, zen_ugoki, head.strip()[:8], len(por_gyou)))
assert (zen_fue, zen_ke, zen_ugoki) == (0, 0, 0), u"★元の束が動いた★"
