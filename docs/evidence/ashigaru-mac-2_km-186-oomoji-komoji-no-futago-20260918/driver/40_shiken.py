# -*- coding: utf-8 -*-
"""40 ―― ★㋓⑷ の彫り方を、己の使ひ捨てで先に試す★(裁333611「命の通りに踏め・但し呑むな、検めよ」)。
⑷ は「`git add -f` の後 `git commit --only <同じ path>`」と在る。
然し ★此の双子では add -f の宛先が問題に成る★ ―― 大文字の名は case を畳む disk では ★まだ開ける★ 故。
∴ ★本番の枝で撃つ前に、使ひ捨て二本で候補を撃ち、commit の tree を測る★。
"""
import hashlib
import io
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
    """使ひ捨てを一本切り、★共用樹と同じ姿(disk=2596)★ を作る"""
    wt = "/Users/momizimac/wt/a2-km186-%s" % nm
    if not os.path.isdir(wt):
        p = subprocess.run(["git", "-C", ROOT, "worktree", "add", "--detach", wt, KOTEI],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GYO.append((u"支度 %s" % nm, u"git worktree add --detach %s %s" % (wt, KOTEI[:8]),
                    str(p.returncode), hei(p.stdout.decode("utf-8", "replace")),
                    hei(p.stderr.decode("utf-8", "replace"))))
    utsu(u"支度 %s ―― 共用樹の姿を再現" % nm, wt, ["checkout", "--", OO])
    return wt


def sugata(wt, fuda):
    """commit の tree を測る ―― ★双子は何本残つたか★"""
    rc, out, _ = g(["ls-tree", "-r", "HEAD", "--", "docs/runbooks/"], wt)
    futago = [l for l in out.split("\n") if "ekarte" in l.lower()]
    rc2, head, _ = g(["rev-parse", "HEAD"], wt)
    GYO.append((fuda, u"git ls-tree -r HEAD -- docs/runbooks/", str(rc),
                u"HEAD=%s ／ 双子の行=%d 本" % (head.strip()[:12], len(futago)),
                u"｜".join(hei(l) for l in futago) or u"★無★"))
    return futago


# ―― 候補甲: ⑷ を「add -f は打たず、commit --only <大文字> だけ」 ――
wt1 = shitaku("t1")
utsu(u"甲⑴", wt1, ["rm", "--cached", OO])
utsu(u"甲⑵", wt1, ["checkout", "--", KO])
utsu(u"甲⑷", wt1, ["commit", "--only", OO, "-m", "test(t1): commit --only <大文字> だけ"])
kou = sugata(wt1, u"★甲の結果★(commit --only <大文字> のみ)")

# ―― 候補乙: ⑷ を「命の字義通り ―― add -f <大文字> の後 commit --only <大文字>」 ――
wt2 = shitaku("t2")
utsu(u"乙⑴", wt2, ["rm", "--cached", OO])
utsu(u"乙⑵", wt2, ["checkout", "--", KO])
utsu(u"乙⑷a", wt2, ["add", "-f", OO])
utsu(u"乙⑷b", wt2, ["commit", "--only", OO, "-m", "test(t2): add -f の後 commit --only"])
otsu = sugata(wt2, u"★乙の結果★(add -f <大文字> → commit --only)")

K.kaku_tsv(os.path.join(BUNDLE, "raw", "40_shiken.tsv"), GYO,
           header=("札", "打つた命", "rc", "out", "err"))

K.kaku(os.path.join(BUNDLE, "raw", "40_shime.txt"), u"""★40 の〆 ―― ★㋓⑷ を字義通りに踏むと双子が蘇る★★
刻 = {koku} ／ 撃つた場 = ★己の使ひ捨て二本★(a2-km186-t1 / a2-km186-t2・detached {kotei})
★共有樹では撃つて居らぬ★。本番の枝(50)へ進む前に ★彫り方だけを先に試した★。

★甲 ―― `git rm --cached` → `git checkout --` → ★`git commit --only <大文字>` のみ★★
  ・commit の tree に残つた双子 = ★{nk} 本★
    {kou}
★乙 ―― 命の字義通り ★`git add -f <大文字>` を挟む★★
  ・commit の tree に残つた双子 = ★{no} 本★
    {otsu}

★★断(数から出る事のみ)★★
  ・★甲も乙も彫れて居らぬ★ ―― commit は二つとも ★rc=1「no changes added to commit」★ で、
    HEAD は 6bde7170 の儘 ★動いて居らぬ★(40_shiken.tsv 逐語)。
  ・∴ 「双子の行 = 2 本」は ★消しが失敗した事★ を意味する ―― 「add -f が蘇らせた」ではない。
    ★甲と乙の差は此の測りでは出て居らぬ(二つとも同じ壁で止まつた)。★
  ・因と ★彫れる形★ は 41 で測り直した ―― `raw/41_shime.txt` を見よ。
  ・★此の紙の初版には「甲で足りる」と書いた。測る前に断を書いたのが疵である(41 で訂す)。★

★此の數が意味せぬ事★:
  ・「双子の行 = 1 本」は ★中身が正本である事を意味せぬ★ ―― blob sha を併せ読め(50 で測る)。
  ・此処の commit は ★使ひ捨ての detached HEAD★ に在り、★枝でも PR でもない★。出さぬ。
  ・case を区別する Linux で `add -f` が同じ振舞ひを見せるかは ★此の disk からは測れぬ★(㋕)。
""".format(koku=time.strftime("%Y-%m-%dT%H:%M:%S%z"), kotei=KOTEI[:8],
           nk=len(kou), no=len(otsu),
           kou=u"\n    ".join(hei(l) for l in kou) or u"★無★",
           otsu=u"\n    ".join(hei(l) for l in otsu) or u"★無★"))
print("甲=%d本 乙=%d本" % (len(kou), len(otsu)))
