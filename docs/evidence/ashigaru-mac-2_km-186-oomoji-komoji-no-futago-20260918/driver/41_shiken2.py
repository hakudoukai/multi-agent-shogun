# -*- coding: utf-8 -*-
"""41 ―― ★40 で甲も乙も彫れなかつた★(commit rc=1「no changes added」)。
∴ ★彫れる形を探す★ ―― 候補を三つ、己の使ひ捨ての中で撃つ。
★40 の断は誤りであつた(「甲で足りる」と書いたが、甲も彫れて居らぬ)。41 で書き直す。★
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

KOTEI = "6bde7170ce574090a6139ba2dfe3aa4cb6db8634"
OO = "docs/runbooks/ERR-EKARTE-001.md"
KO = "docs/runbooks/err-ekarte-001.md"
GYO = []


def g(args, cwd):
    p = subprocess.run(["git", "-C", cwd] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def hei(s):
    return s.replace(u"\t", u" ⇥ ").replace(u"\n", u" ⏎ ").strip() or u"―"


def utsu(fuda, wt, args):
    rc, out, err = g(args, wt)
    GYO.append((fuda, u"git " + u" ".join(args), str(rc), hei(out), hei(err)))
    return rc, out, err


def shitaku(nm):
    wt = "/Users/momizimac/wt/a2-km186-%s" % nm
    if not os.path.isdir(wt):
        p = subprocess.run(["git", "-C", ROOT, "worktree", "add", "--detach", wt, KOTEI],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GYO.append((u"支度 %s" % nm, u"git worktree add --detach", str(p.returncode),
                    hei(p.stdout.decode("utf-8", "replace")), hei(p.stderr.decode("utf-8", "replace"))))
    utsu(u"支度 %s ―― 共用樹の姿を再現" % nm, wt, ["checkout", "--", OO])
    utsu(u"支度 %s ⑴" % nm, wt, ["rm", "--cached", OO])
    utsu(u"支度 %s ⑵" % nm, wt, ["checkout", "--", KO])
    rc, out, _ = g(["diff", "--cached", "--name-status"], wt)
    GYO.append((u"支度 %s ―― ★index に載つて居る変化★" % nm, u"git diff --cached --name-status",
                str(rc), hei(out), u"★是が commit されるべき全て★"))
    return wt


def hakaru(wt, fuda):
    rc, head, _ = g(["rev-parse", "HEAD"], wt)
    rc2, out, _ = g(["ls-tree", "-r", "HEAD", "--", "docs/runbooks/"], wt)
    futago = [l for l in out.split("\n") if "ekarte" in l.lower()]
    ugoita = head.strip() != KOTEI
    GYO.append((fuda, u"git rev-parse HEAD + ls-tree", str(rc),
                u"HEAD=%s ／ ★動いた=%s★ ／ 双子の行=%d 本" % (head.strip()[:12], u"是" if ugoita else u"否", len(futago)),
                u"｜".join(hei(l) for l in futago) or u"★無★"))
    return ugoita, futago


# 丙 ―― 素の `git commit -m`(index に載つた物だけを彫る)
wt3 = shitaku("t3")
utsu(u"丙⑷", wt3, ["commit", "-m", "test(t3): 素の commit(index の儘)"])
hei_ugoita, hei_futago = hakaru(wt3, u"★丙の結果★(素の `git commit -m`)")

# 丁 ―― `git commit --only <dir>`(dir で括る)
wt4 = shitaku("t4")
utsu(u"丁⑷", wt4, ["commit", "--only", "docs/runbooks/", "-m", "test(t4): commit --only <dir>"])
tei_ugoita, tei_futago = hakaru(wt4, u"★丁の結果★(`git commit --only docs/runbooks/`)")

# 戊 ―― `git commit --only <小文字>`(生き残る方の名で括る)
wt5 = shitaku("t5")
utsu(u"戊⑷", wt5, ["commit", "--only", KO, "-m", "test(t5): commit --only <小文字>"])
bo_ugoita, bo_futago = hakaru(wt5, u"★戊の結果★(`git commit --only <小文字>`)")

K.kaku_tsv(os.path.join(BUNDLE, "raw", "41_shiken2.tsv"), GYO, header=("札", "打つた命", "rc", "out", "err"))


def mi(u, f):
    if not u:
        return u"★彫れず(HEAD 動かず)★"
    if len(f) == 1 and "de00cbd9" in f[0]:
        return u"★彫れた ―― 双子は 1 本・中身は正本(de00cbd9…)★"
    return u"★彫れたが姿が違ふ(双子 %d 本)★" % len(f)


K.kaku(os.path.join(BUNDLE, "raw", "41_shime.txt"), u"""★41 の〆 ―― ★彫れる形は一つだけであつた★★
刻 = {koku} ／ 撃つた場 = ★己の使ひ捨て t3/t4/t5★(detached {kotei}) ／ ★共有樹では撃つて居らぬ★

★先づ 40 の断を改める★:
  40 で「甲(commit --only <大文字> のみ)で足りる」と書いたが、★甲も彫れて居らぬ★
  ―― rc=1「no changes added to commit」で ★HEAD は 6bde7170 の儘★ であつた。
  ★測る前に断を書いたのが疵である。41 の数で書き直す。★

★四つの候補と其の出目★
  ・甲 `git commit --only <大文字>`            → ★彫れず★(rc=1・40_shiken.tsv)
  ・乙 `git add -f <大文字>` → `commit --only` → ★彫れず★(rc=1・40_shiken.tsv)
  ・丙 `git commit -m`(index の儘)            → {mhei}
  ・丁 `git commit --only docs/runbooks/`     → {mtei}
  ・戊 `git commit --only <小文字>`            → {mbo}

★因(数から言へる所まで)★:
  ・`--only <path>` は ★worktree の其の path を読み直して彫る★。
    case を畳む disk では ★大文字の名は まだ開ける★ 故、git は「消えた」ではなく「modified」と見て、
    ★消しを彫らぬ★(「no changes added to commit」)。
  ・⑴の `git rm --cached` は ★index には正しく載る★(`git diff --cached --name-status` = D 一行)。
    ∴ ★載つて居る物を其の儘彫る形★ でなければ、此の消しは commit に入らぬ。

★∴ 本番の彫り(50)で用ゐる形★: {erabu}
  ―― ★㋓⑴⑵の順は一字も変へて居らぬ★。変へたのは ⑷ の彫り方だけであり、
     其れも ★字義通りでは彫れぬと数で出た★ 故である(㋔「呑むな・検めよ」)。★家老の御下知を仰ぐ★。

★此の數が意味せぬ事★:
  ・「彫れた」は ★中身が正しい事を別に確かめねば意味を成さぬ★ ―― 50 で blob sha を測る。
  ・素の `git commit -m` が安全なのは ★己の使ひ捨て/己の枝で index が空の時だけ★ である。
    ★共用樹では他席の staged が混じり得る ∴ 共用樹では決して打たぬ。★
  ・Linux(case を区別する側)で `--only` が同じ振舞ひを見せるかは ★此の disk からは測れぬ★(㋕)。
""".format(koku=time.strftime("%Y-%m-%dT%H:%M:%S%z"), kotei=KOTEI[:8],
           mhei=mi(hei_ugoita, hei_futago), mtei=mi(tei_ugoita, tei_futago), mbo=mi(bo_ugoita, bo_futago),
           erabu=(u"★丙 ―― 素の `git commit -m`(己の枝・index は D 一行のみ)★"
                  if hei_ugoita and len(hei_futago) == 1 else u"★未定(丙も彫れず ―― 家老へ上げる)★")))
print("丙=%s 丁=%s 戊=%s" % (mi(hei_ugoita, hei_futago), mi(tei_ugoita, tei_futago), mi(bo_ugoita, bo_futago)))
