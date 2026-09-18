# -*- coding: utf-8 -*-
"""15 ―― ★「全 repo」を ref の先で歩く★(㋐ の外延・km-186)。
命の母數は固定 commit 一本だが、下命の言は「★全 repo で数へよ★」である。
∴ ★全 ref の先★ を歩いて casefold の組を数へる。★歴史(過去の commit)は歩いて居らぬ★ ―― 是は㋕で名指す。
同じ樹 sha は一度だけ歩く(数へ直しの重複を避ける)。
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

KOKU = time.strftime("%Y-%m-%dT%H:%M:%S%z")


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


rc_r, out_r, err_r = g(["for-each-ref", "--format=%(objectname) %(refname)"])
refs = [l.split(" ", 1) for l in out_r.decode("utf-8", "replace").split("\n") if l.strip()]

mita = {}
gyo = []
kumi_zen = {}
for sha, name in refs:
    if sha in mita:
        gyo.append((name, sha, "既に歩いた樹", mita[sha][0], mita[sha][1]))
        continue
    rc, out, err = g(["ls-tree", "-r", "--name-only", "-z", sha])
    if rc != 0:
        gyo.append((name, sha, "rc=%d(歩けぬ)" % rc, "―", err.strip()[:60] or "―"))
        mita[sha] = ("―", "rc=%d" % rc)
        continue
    ps = [x.decode("utf-8", "surrogateescape") for x in out.split(b"\0") if x]
    k = {}
    for p in ps:
        k.setdefault(p.casefold(), []).append(p)
    f = {a: sorted(b) for a, b in k.items() if len(b) >= 2}
    for a, b in f.items():
        kumi_zen.setdefault(a, set()).update(b)
    mita[sha] = (str(len(ps)), "組=%d" % len(f))
    gyo.append((name, sha, "歩いた", str(len(ps)), "組=%d" % len(f)))

K.kaku_tsv(os.path.join(BUNDLE, "raw", "15_ref.tsv"), gyo,
           header=("ref", "先の sha", "歩いたか", "其の樹の path 數", "casefold の組"))
K.kaku(os.path.join(BUNDLE, "raw", "15_shime.txt"), u"""★15 の〆 ―― ref の先を悉く歩いた★
刻 = {koku} ／ 根 = {root}
rc(for-each-ref) = {rcr}(★returncode 素★) ／ ref = ★{nr} 本★ ／ 別々の樹 = ★{nt} 本★

★ref の先で見えた casefold の組 = {nk} 組★
{ichiran}

★此の數が意味せぬ事★:
  ・歩いたのは ★ref の先(tip)★ のみである。★過去の commit は一つも歩いて居らぬ★ ――
    歴史の途中に在つて今は消えた双子は ★此の數に入らぬ★。
  ・ref には他席の枝も含まれる。★他席の枝を歩いた事は、其の枝に触れた事を意味せぬ★(読取のみ・checkout せず)。
  ・組の數は ★path の字面★ の話であり、中身の異同を言つて居らぬ。
  ・器の言(err) = {er}
""".format(koku=KOKU, root=ROOT, rcr=rc_r, nr=len(refs), nt=len(mita), nk=len(kumi_zen),
           ichiran=u"\n".join(u"  ・%s ―― %s" % (a, u" ／ ".join(sorted(b))) for a, b in sorted(kumi_zen.items())) or u"  ―(0 組)",
           er=err_r.strip() or u"―"))
print("ref=%d 樹=%d 組=%d rc=%d" % (len(refs), len(mita), len(kumi_zen), rc_r))
