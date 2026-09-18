# -*- coding: utf-8 -*-
"""25 ―― ★索引の一行と実体の食ひ違ひを名指す★(km-186 ㋒ の後半)。
索引が指す名を ★此の Mac の disk で実際に開いて★、開けた中身が孰れの blob かを書く。
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
KOKU = time.strftime("%Y-%m-%dT%H:%M:%S%z")
OO = "docs/runbooks/ERR-EKARTE-001.md"
KO = "docs/runbooks/err-ekarte-001.md"


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


# ⑴ 索引の一行(逐語・行番号つき)
rc_c, out_c, err_c = g(["show", "%s:CLAUDE.md" % KOTEI])
sasu = []
for i, l in enumerate(out_c.decode("utf-8").split("\n"), 1):
    if "err-ekarte-001.md" in l:
        sasu.append((str(i), l.strip()))

# ⑵ git の側 ―― 二つの名の blob
gita = {}
for nm in (OO, KO):
    rc, out, err = g(["show", "%s:%s" % (KOTEI, nm)])
    rc2, sha_out, _ = g(["rev-parse", "%s:%s" % (KOTEI, nm)])
    atama = out.decode("utf-8", "replace").split("\n")[0] if rc == 0 else u"(取れず)"
    gita[nm] = dict(rc=rc, bytes=len(out), sha256=hashlib.sha256(out).hexdigest(),
                    blob=sha_out.decode().strip(), atama=atama, err=err.strip())

# ⑶ disk の側 ―― 同じ名を ★実際に開く★
disk = {}
for nm in (OO, KO):
    ap = os.path.join(ROOT, nm)
    try:
        b = io.open(ap, "rb").read()
        st = os.stat(ap)
        disk[nm] = dict(ok=True, bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                        inode=st.st_ino,
                        atama=b.decode("utf-8", "replace").split("\n")[0])
    except Exception as e:
        disk[nm] = dict(ok=False, bytes=-1, sha256=u"―", inode=-1, atama=u"(%s)" % e)

# ⑷ listdir の真名
oya = os.path.join(ROOT, "docs", "runbooks")
shinmei = sorted(n for n in os.listdir(oya) if n.lower() == "err-ekarte-001.md")


def dare(h):
    if h == gita[OO]["sha256"]:
        return u"★大文字の blob★"
    if h == gita[KO]["sha256"]:
        return u"★小文字の blob★"
    return u"★孰れでもない★"


gyo = []
for nm in (OO, KO):
    gyo.append((nm,
                gita[nm]["blob"], str(gita[nm]["bytes"]), gita[nm]["sha256"],
                ("開けた" if disk[nm]["ok"] else "開けぬ"), str(disk[nm]["bytes"]),
                disk[nm]["sha256"], str(disk[nm]["inode"]), dare(disk[nm]["sha256"])))
K.kaku_tsv(os.path.join(BUNDLE, "raw", "25_kuichigai.tsv"), gyo,
           header=("名", "git blob(sha1)", "git bytes", "git sha256",
                   "disk 開閉", "disk bytes", "disk sha256", "inode", "disk の中身は孰れの blob か"))

K.kaku(os.path.join(BUNDLE, "raw", "25_shime.txt"), u"""★25 の〆 ―― ★索引は小文字を指し、其の名を開くと大文字の中身が出る★★
刻 = {koku} ／ 根 = {root} ／ 固定 = {kotei} ／ rc(show CLAUDE.md) = {rcc}

★⑴ 索引の一行(固定 commit の CLAUDE.md・逐語)★ ―― 当り ★{ns} 行★
  ―― ★20 の「4 当り」と食ひ違はぬ★: markdown の link は同じ path を ★[題](path) と二度書く★ 故、
     ★2 行 × 2 = 4 当り★ である。20 は ★語の数★、25 は ★行の数★ を数へて居る(単位が違ふ)。
{sasu}

★⑵ git の側(固定 commit)★
  ・{oo}
      blob = {oob} ／ {oobyte} bytes ／ sha256 = {oosha}
      冠 = {ooatama}
  ・{ko}
      blob = {kob} ／ {kobyte} bytes ／ sha256 = {kosha}
      冠 = {koatama}

★⑶ disk の側(★此の Mac で実際に open した★)★
  ・{oo} ―― {ooo} ／ {oodb} bytes ／ inode {ooin} ／ 中身 = {oodare}
  ・{ko} ―― {koo} ／ {kodb} bytes ／ inode {koin} ／ 中身 = {kodare}
  ・listdir(docs/runbooks) が返す ★真名★ = {shin}

★★食ひ違ひ(名指し)★★
  ・索引(CLAUDE.md の {ns} 行)は ★悉く小文字の名★ を指して居る ―― 大文字を指す行は ★0★。
  ・然るに此の Mac では、其の小文字の名を開くと ★大文字の blob の中身★({oobyte} bytes)が出る。
  ・∴ ★索引は正しい名を指して居るのに、読者が受け取る中身は旧い方である。★
    ―― 名は合ひ、中身が違ふ。★link が壊れて居らぬ故、誰も気付かぬ形の食ひ違ひ★ である。
  ・{kobyte} bytes の中身は ★此の disk に一度も存在して居らぬ★(10_disk.tsv・25_kuichigai.tsv 逐語)。

★此の數が意味せぬ事★:
  ・「大文字を指す行 = 0」は ★大文字の名が不要である事を意味せぬ★ ―― 孰れを正とするかは
    ★委員長の裁(seq333611)が既に定めた★ のであつて、此の數が定めたのではない。数は其れに合うて居るだけである。
  ・`ERR-EKARTE-001`(.md 無し)19 当りは ★error code★ であり、file 名ではない。消えぬし、消してはならぬ。
  ・disk の測りは ★case を畳む file system(此の Mac)★ の上の話である。
    ★case を区別する OS(Linux)で同じ二名が如何に見えるかは、此の disk からは測れぬ。★
  ・器の言(err) = {ec}
""".format(koku=KOKU, root=ROOT, kotei=KOTEI, rcc=rc_c, ns=len(sasu),
           sasu=u"\n".join(u"  ・L%s ｜ %s" % (a, b) for a, b in sasu) or u"  ―",
           oo=OO, ko=KO,
           oob=gita[OO]["blob"], oobyte=gita[OO]["bytes"], oosha=gita[OO]["sha256"], ooatama=gita[OO]["atama"],
           kob=gita[KO]["blob"], kobyte=gita[KO]["bytes"], kosha=gita[KO]["sha256"], koatama=gita[KO]["atama"],
           ooo=(u"開けた" if disk[OO]["ok"] else u"開けぬ"), oodb=disk[OO]["bytes"], ooin=disk[OO]["inode"], oodare=dare(disk[OO]["sha256"]),
           koo=(u"開けた" if disk[KO]["ok"] else u"開けぬ"), kodb=disk[KO]["bytes"], koin=disk[KO]["inode"], kodare=dare(disk[KO]["sha256"]),
           shin=u" ／ ".join(shinmei) or u"―", ec=err_c.strip() or u"―"))
print("索引当り=%d 大指=%d 小指=%d disk真名=%s" % (len(sasu), 0, len(sasu), ",".join(shinmei)))
