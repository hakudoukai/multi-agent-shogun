# -*- coding: utf-8 -*-
"""50 ―― ★本番の彫り★(裁333611 ㋓)。己の枝・己の worktree の中だけ。
順 = ⑴`git rm --cached <大文字>` ⑵`git checkout -- <小文字>` ⑶検め ⑷彫り。
★⑴と⑵を入れ替へず・⑵を飛ばさず★。⑷ の形だけは 41 の数で選んだ(素の `git commit -m`)。
★reset を打たぬ・push せぬ・main に触れぬ・gh を叩かぬ★。
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
EDA = "ashigaru-mac-2/km-186-futago-no-kesu-jun-20260918"
WT = "/Users/momizimac/wt/a2-km186"
OO = "docs/runbooks/ERR-EKARTE-001.md"
KO = "docs/runbooks/err-ekarte-001.md"
SEIHON_SHA1 = "de00cbd99d9909f4a923041ae17f0d2cbb587668"
SEIHON_BYTE = 3471
GYO = []


def g(args, cwd=WT):
    p = subprocess.run(["git", "-C", cwd] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def hei(s):
    return s.replace(u"\t", u" ⇥ ").replace(u"\n", u" ⏎ ").strip() or u"―"


def utsu(fuda, args, cwd=WT):
    rc, out, err = g(args, cwd)
    GYO.append((time.strftime("%H:%M:%S"), fuda, u"git " + u" ".join(args), str(rc), hei(out), hei(err)))
    return rc, out, err


def porcelain(fuda):
    rc, out, err = g(["status", "--porcelain", "--", "docs/runbooks/"])
    gy = [l for l in out.split("\n") if l]
    GYO.append((time.strftime("%H:%M:%S"), fuda, u"git status --porcelain -- docs/runbooks/",
                str(rc), u"｜".join(hei(l) for l in gy) or u"★空★", u"行数=%d" % len(gy)))
    return gy


def blobsha1(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def disk(nm):
    ap = os.path.join(WT, nm)
    b = io.open(ap, "rb").read()
    return len(b), blobsha1(b), os.stat(ap).st_ino


# ―― 枝を切る ――
if not os.path.isdir(WT):
    utsu(u"枝を切る(己の worktree)", ["worktree", "add", "-b", EDA, WT, KOTEI], cwd=ROOT)

# ―― 〇 共用樹と同じ姿を作る(disk = 大文字の blob) ――
utsu(u"〇 共用樹の姿を再現(★是をせねば ⑵ が仕事を持たぬ★)", ["checkout", "--", OO])
mae_byte, mae_sha1, mae_ino = disk(KO)
mae_porc = porcelain(u"〇 ★⑴の前★ の porcelain")

# ―― ⑴ ―― 索引からのみ外す(disk へ手を出さぬ) ――
utsu(u"⑴ ★git rm --cached <大文字>★", ["rm", "--cached", OO])
ichi_byte, ichi_sha1, ichi_ino = disk(KO)
ichi_porc = porcelain(u"⑴ の後の porcelain")

# ―― ⑵ ―― 正本の中身を disk へ戻す ――
utsu(u"⑵ ★git checkout -- <小文字>★", ["checkout", "--", KO])
ni_byte, ni_sha1, ni_ino = disk(KO)
ni_porc = porcelain(u"⑵ の後の porcelain")

# ―― ⑶ ―― 検め(★呑まず・数で★) ――
assert ni_byte == SEIHON_BYTE, u"★⑶ bytes = %d(期待 %d)★" % (ni_byte, SEIHON_BYTE)
assert ni_sha1 == SEIHON_SHA1, u"★⑶ blob sha1 = %s(期待 %s)★" % (ni_sha1, SEIHON_SHA1)
oo_d = [l for l in ni_porc if l[3:].strip() == OO]
ko_m = [l for l in ni_porc if l[3:].strip() == KO]
assert len(ni_porc) == 1 and oo_d and oo_d[0].startswith("D "), u"★⑶ porcelain = %r★" % ni_porc
assert not ko_m, u"★⑶ 小文字の M が残つて居る = %r★" % ko_m

rc_dc, out_dc, _ = g(["diff", "--cached", "--name-status"])
GYO.append((time.strftime("%H:%M:%S"), u"⑶ ★index に載つて居る変化(是だけが彫られる)★",
            u"git diff --cached --name-status", str(rc_dc), hei(out_dc), u"―"))
assert out_dc.strip() == "D\t" + OO, u"★⑶ index = %r★" % out_dc

# ―― ⑷ ―― 彫る(41 の数で選んだ形) ――
DOU = u"""fix(runbooks): ★双子の片方を消す ―― 大文字 ERR-EKARTE-001.md を樹から外す★(委員長裁 seq333611)

正 = docs/runbooks/err-ekarte-001.md ―― 3471 bytes ／ blob de00cbd9… ／ 2026-05-29 の新版
消 = docs/runbooks/ERR-EKARTE-001.md ―― 2596 bytes ／ blob e6de627b… ／ 2026-05-05 の旧版

★case を畳む disk では二つの名が同じ inode を指す★(実測 10724954)。
∴ 素の `git rm <大文字>` は ★正本の実体を消す★(実射 raw/35_gyaku.tsv)。
彫りの順 = ⑴ git rm --cached <大文字> ⑵ git checkout -- <小文字> ⑶ 検め ⑷ 彫り(裁333611 ㋓)。
canon の側 = 索引は ★小文字のみ★ を指す(2 行 4 当り)・大文字を指す行 0(raw/20,25)。
測り = docs/evidence/ashigaru-mac-2_km-186-oomoji-komoji-no-futago-20260918/

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
"""
rc_c, out_c, err_c = utsu(u"⑷ ★彫る(素の commit ―― index の D 一行のみ)★", ["commit", "-m", DOU])
assert rc_c == 0, u"★⑷ commit rc=%d ―― %s★" % (rc_c, err_c)

rc_h, head, _ = g(["rev-parse", "HEAD"])
rc_t, tree, _ = g(["rev-parse", "HEAD^{tree}"])
rc_l, lst, _ = g(["ls-tree", "-r", "HEAD", "--", "docs/runbooks/"])
futago = [l for l in lst.split("\n") if "ekarte" in l.lower()]
assert len(futago) == 1 and SEIHON_SHA1 in futago[0], u"★彫つた tree の双子 = %r★" % futago
rc_s, stat, _ = g(["show", "--stat", "--oneline", "HEAD"])
ato_porc = porcelain(u"⑷ の後の porcelain")

# ―― 未 push の證(★0 行では証せぬ ∴ 陽性対照を併せる★) ――
rc_r1, rem_main, _ = g(["ls-remote", "origin", "refs/heads/main"], cwd=ROOT)
rc_r2, rem_eda, _ = g(["ls-remote", "origin", "refs/heads/" + EDA], cwd=ROOT)
rc_r3, rem_nai, _ = g(["ls-remote", "origin", "refs/heads/kesshite-sonzaishinu-eda-20260918"], cwd=ROOT)
GYO.append((time.strftime("%H:%M:%S"), u"未push ★陽性対照★", u"git ls-remote origin refs/heads/main",
            str(rc_r1), u"%d 行" % len([l for l in rem_main.split("\n") if l]), hei(rem_main)))
GYO.append((time.strftime("%H:%M:%S"), u"未push ★当の枝★", u"git ls-remote origin refs/heads/%s" % EDA,
            str(rc_r2), u"%d 行" % len([l for l in rem_eda.split("\n") if l]), hei(rem_eda)))
GYO.append((time.strftime("%H:%M:%S"), u"未push ★負対照★", u"git ls-remote origin refs/heads/<存在せぬ枝>",
            str(rc_r3), u"%d 行" % len([l for l in rem_nai.split("\n") if l]), hei(rem_nai)))

K.kaku_tsv(os.path.join(BUNDLE, "raw", "50_hori.tsv"), GYO,
           header=("刻", "札", "打つた命", "rc", "out", "err/註"))

K.kaku(os.path.join(BUNDLE, "raw", "50_shime.txt"), u"""★50 の〆 ―― ★命の順で彫つた★(裁333611 ㋓)★
刻 = {koku} ／ 枝 = ★{eda}★ ／ 場 = {wt}(己の worktree) ／ 固定 = {kotei}

★順(一字も入れ替へて居らぬ)★
  〇 共用樹の姿を再現   ―― 小文字の名を開くと {mb} bytes ／ blob {ms}… ／ inode {mi}
  ⑴ git rm --cached <大文字> ―― 後の disk = {ib} bytes ／ inode {ii}(★disk は動いて居らぬ★)
  ⑵ git checkout -- <小文字> ―― 後の disk = ★{nb} bytes★ ／ blob ★{ns}★
  ⑶ 検め(assert は ★彫りの前★)
      ・bytes = {nb} = ★3471★                     ―― 合
      ・blob sha1(己で計算) = {ns} ―― ★de00cbd9…★ 合
      ・porcelain = ★{np}★ ―― ★大文字の D 一行のみ・小文字の M は消えた★
        ★陽性対照★: 同じ器が ⑵の前には ★{mp}★ と刷つた(∴ 器は M を刷る能を持つ)
      ・index に載つた変化 = ★D {oo} の一行のみ★
  ⑷ git commit(★素の commit ―― index の儘★) ―― rc = {rcc}

★彫つた物★
  HEAD = ★{head}★ ／ tree = {tree}
  樹の中の双子 = ★1 本★ ―― {futago}
  {stat}
  彫つた後の porcelain(docs/runbooks) = ★{ap}★

★未 push の證(★0 行では証せぬ★ ∴ 三役で書く)★
  ・陽性対照 `git ls-remote origin refs/heads/main`      = ★{r1} 行★(rc={rc1}) ―― ★器は届いて居る★
  ・当の枝   `git ls-remote origin refs/heads/<当枝>`    = ★{r2} 行★(rc={rc2}) ―― ★未 push★
  ・負対照   `git ls-remote origin refs/heads/<無き枝>`  = ★{r3} 行★(rc={rc3}) ―― 無い物は 0 行

★⑷ の形について(★命の字義から外した唯一の点★)★
  ・命は「`git add -f` の後 `git commit --only <同じ path>`」と在る。
  ・然し此の双子では ★字義通りでは彫れぬ★ ―― `--only <大文字>` も `add -f`+`--only` も
    ★rc=1「no changes added to commit」で HEAD が動かなかつた★(40/41 の実測)。
    因 = `--only` は worktree の其の path を読み直すが、case を畳む disk では ★大文字の名がまだ開ける★ 故。
  ・∴ ⑷ のみ ★素の `git commit`★ を用ゐた。★index には D 一行しか載つて居らぬ事を先に assert して居る★。
  ・★共用樹では素の commit を打たぬ★(他席の staged を呑む)。此処は ★己が切つた己の枝★ である。
  ・★家老の御下知を仰ぐ★ ―― 便で名指しする。

★此の數が意味せぬ事★:
  ・彫つた事は ★PR が在る事を意味せぬ★。push も gh も打つて居らぬ(裁332449・km-172㋕⑶)。
  ・「双子 1 本」は ★此の枝の tree の話★ であり、★main の話ではない★。main には一指も触れて居らぬ。
  ・case を区別する Linux で此の commit が如何に見えるかは ★測れぬ★(㋕) ―― 彼方では二本とも
    ★別々の file として存在して居る筈★ だが、★此の disk からは確かめられぬ★。
""".format(koku=time.strftime("%Y-%m-%dT%H:%M:%S%z"), eda=EDA, wt=WT, kotei=KOTEI,
           mb=mae_byte, ms=mae_sha1[:12], mi=mae_ino, ib=ichi_byte, ii=ichi_ino,
           nb=ni_byte, ns=ni_sha1, oo=OO,
           np=u"｜".join(ni_porc), mp=u"｜".join(mae_porc), rcc=rc_c,
           head=head.strip(), tree=tree.strip(), futago=hei(futago[0]),
           stat=hei(stat), ap=u"｜".join(ato_porc) or u"★空★",
           r1=len([l for l in rem_main.split("\n") if l]), rc1=rc_r1,
           r2=len([l for l in rem_eda.split("\n") if l]), rc2=rc_r2,
           r3=len([l for l in rem_nai.split("\n") if l]), rc3=rc_r3))
print("HEAD=%s 双子=%d 未push=%d行(陽性=%d行)" % (head.strip()[:12], len(futago),
      len([l for l in rem_eda.split("\n") if l]), len([l for l in rem_main.split("\n") if l])))
