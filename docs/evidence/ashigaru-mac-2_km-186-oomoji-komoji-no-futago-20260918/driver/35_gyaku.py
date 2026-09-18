# -*- coding: utf-8 -*-
"""35 ―― ★逆順を己の worktree の中で撃つ★(km-186 補㋔)。
「一本の実体を二つの名が指す disk では、★消す順が正本の生死を決める★」を ★数で★ 示す。
★共有樹では撃たぬ★ ―― 撃つのは /Users/momizimac/wt/a2-km186-gyaku(己が切つた使ひ捨て)のみ。
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

WT = "/Users/momizimac/wt/a2-km186-gyaku"
OO = "docs/runbooks/ERR-EKARTE-001.md"
KO = "docs/runbooks/err-ekarte-001.md"
OYA = os.path.join(WT, "docs", "runbooks")
BLOB = {"abf519d04dc5cfbb3adb7dbcf6a5dd2c132e52c3c492530e4f8b90a0ff363fba": u"★大文字の blob(2596B・5/5 の旧版)★",
        "24cf87840d94dd6b18a5f292bef598f370eede58127296f01a04b5667ee3d50f": u"★小文字の blob(3471B・5/29 の新版 = 委員長が正と定めた方)★"}
KIROKU = []


def g(args, cwd=WT):
    p = subprocess.run(["git", "-C", cwd] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def miru(fuda):
    """★其の刻の disk と index を悉く測る★"""
    d = {"札": fuda, "刻": time.strftime("%H:%M:%S")}
    try:
        d["真名"] = " ／ ".join(sorted(n for n in os.listdir(OYA) if n.lower() == "err-ekarte-001.md")) or u"★無★"
    except Exception as e:
        d["真名"] = u"(%s)" % e
    for nm, fud in ((OO, "大"), (KO, "小")):
        ap = os.path.join(WT, nm)
        try:
            b = io.open(ap, "rb").read()
            h = hashlib.sha256(b).hexdigest()
            d[fud] = u"開けた ／ %d bytes ／ inode %d ／ 中身 = %s" % (
                len(b), os.stat(ap).st_ino, BLOB.get(h, u"★孰れでもない(%s…)★" % h[:12]))
        except Exception as e:
            d[fud] = u"★開けぬ ―― %s★" % type(e).__name__
    rc, out, err = g(["status", "--porcelain", "--", "docs/runbooks/"])
    d["porcelain"] = (u"｜".join(l for l in out.split("\n") if l) or u"★空★") + u" (rc=%d)" % rc
    rc2, out2, _ = g(["ls-files", "-s", "--", "docs/runbooks/"])
    # ★`ls-files -s` は mode sha stage ★TAB★ path の形★ ―― TAB を其の儘 tsv へ入れると欄が割れる。
    d["index"] = u"｜".join(l.replace(u"\t", u" ⇥ ") for l in out2.split("\n")
                           if "ekarte" in l.lower()) or u"★無★"
    KIROKU.append(d)
    return d


def utsu(fuda, args, cwd=WT):
    rc, out, err = g(args, cwd)
    KIROKU.append({"札": u"★撃つた★ %s ―― `git %s`" % (fuda, " ".join(args)),
                   "刻": time.strftime("%H:%M:%S"), "真名": u"rc = %d" % rc,
                   "大": u"out = %s" % (out.strip().replace("\n", " ⏎ ") or u"―"),
                   "小": u"err = %s" % (err.strip().replace("\n", " ⏎ ") or u"―"),
                   "porcelain": u"―", "index": u"―"})
    return rc, out, err


# ―― 〇 共用樹と同じ姿を作る(disk が ★大文字の blob★ を抱く形) ――
miru(u"〇 鮮な checkout の直後")
utsu(u"共用樹の姿を再現(大文字の blob を dirent へ書く)", ["checkout", "--", OO])
zero = miru(u"〇' 共用樹と同じ姿(disk = 大文字の blob)")

# ―― 一 ★素の git rm を踏む(★禁じられた手★・己の使ひ捨ての中だけ)★ ――
utsu(u"★逆順 ―― 素の git rm★", ["rm", OO])
ichi = miru(u"一 素の `git rm <大文字>` の直後")

# ―― 二 其の儘 `git commit -a` 相当へ進んだら如何に成るか ――
utsu(u"逆順の続き ―― 消えた実体を index へ載せる(git add -A 相当)", ["add", "-A", "--", "docs/runbooks/"])
ni = miru(u"二 `git add -A` の後 ―― ★index からも正本が消えた★")

# ―― 三 戻せるか(此処が分かれ目) ――
utsu(u"戻しを試みる(index が既に空なら戻らぬ)", ["checkout", "--", KO])
san = miru(u"三 `git checkout -- <小文字>` を打つた後")
utsu(u"最後の頼み ―― HEAD から戻す", ["checkout", "HEAD", "--", OO, KO])
yon = miru(u"四 `git checkout HEAD -- <両名>` の後")

hyou = [(d["札"], d["刻"], d["真名"], d["大"], d["小"], d["porcelain"], d["index"]) for d in KIROKU]
K.kaku_tsv(os.path.join(BUNDLE, "raw", "35_gyaku.tsv"), hyou,
           header=("札", "刻", "listdir の真名", "大文字の名を開くと", "小文字の名を開くと", "porcelain(docs/runbooks)", "index"))

K.kaku(os.path.join(BUNDLE, "raw", "35_shime.txt"), u"""★35 の〆 ―― ★消す順が正本の生死を決める★(逆順を撃つた記録)★
刻 = {koku} ／ 撃つた場 = ★{wt}★(己が切つた使ひ捨ての worktree・detached 6bde7170)
★共有樹では一発も撃つて居らぬ★(共有樹の HEAD/index は 30/99 の紙で不動を證する)

★〇 鮮な checkout が置く物(★是が第一の測り★)★
  ・dirent は ★一本★(真名 = err-ekarte-001.md)、中身は ★{zeroko}★
  ・∴ ★鮮な clone/checkout では正本(3471B)が残る★ ―― index の並び順(大文字が先・小文字が後)で
    ★後に書いた方が勝つ★ 故である。★然るに共用樹の disk は 2596B を抱いて居る★(25_kuichigai.tsv)。
    ―― 共用樹が旧版を抱く因は ★未測★(此処では測つて居らぬ・推さぬ)。

★一 ★素の `git rm docs/runbooks/ERR-EKARTE-001.md` を踏むと何が起きたか★★
  ・打つ前 : {maename} ／ 小文字の名を開くと {maeko}
  ・打つた後: {atoname} ／ 小文字の名を開くと {atoko}
  ・∴ ★大文字の名へ打つた rm が、小文字の名の実体を消した★ ―― 二つの名が ★同じ inode★ を指す故。
    ★委員長が正と定めた名が、正でない名への命令で死ぬ。★

★二 其の儘進んだら(`git add -A`)★
  ・index = {niindex}
  ・∴ ★index からも正本の行が消えた★。此処で commit すれば ★樹から正本が落ちる★。

★三・四 戻せるか★
  ・`git checkout -- <小文字>`  → {sanko}
  ・`git checkout HEAD -- <両名>` → {yonko}
  ・∴ ★HEAD が生きて居る限り戻る★。然し ⑴commit を打つ ⑵push する ⑶HEAD を動かす の
    孰れかを踏めば ★戻す先が無く成る★。★逆順の害は「消えた事」ではなく「気付かぬ儘 commit する事」である。★

★此の數が意味せぬ事★:
  ・此処の測りは ★case を畳む file system(macOS)★ の上の話である。
    ★case を区別する Linux で同じ手順が同じ結果に成るかは、此の disk からは測れぬ★(㋕)。
  ・「鮮な checkout では 3471 が勝つ」は ★git の index 並び順から出た振舞ひ★ であり、
    ★git が正本を選んだ★ のではない。★偶々 後に書かれた方が残つただけ★ である。
  ・逆順を撃つたのは ★使ひ捨ての worktree★ のみ。此の枝は ★出さぬ★(PR に載せぬ)。
""".format(koku=time.strftime("%Y-%m-%dT%H:%M:%S%z"), wt=WT,
           zeroko=KIROKU[0]["小"], maeko=zero["小"], maename=zero["真名"],
           atoname=ichi["真名"], atoko=ichi["小"], niindex=ni["index"],
           sanko=san["小"], yonko=yon["小"]))
print("逆順 記録 %d 件" % len(KIROKU))
