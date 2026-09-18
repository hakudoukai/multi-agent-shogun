# -*- coding: utf-8 -*-
"""10 ―― ★母數を己で作る★(km-186 ㋐㋑)。
origin/main 6bde7170… の全 path を歩き、★casefold で括つて 2 本以上に成る組★を悉く出す。
・path は ★-z(NUL 区切り)★ で取る ―― git は非 ASCII を引用符で括る故、行単位では壊れる。
・rc は ★returncode 素★ で取る(管を通さぬ)。
・組の各 blob の sha256/bytes と、★disk に在る一本★の実名・sha256・bytes・inode を併せ出す。
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


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


rc_n, out_n, err_n = g(["ls-tree", "-r", "--name-only", "-z", KOTEI])
paths = [x.decode("utf-8", "surrogateescape") for x in out_n.split(b"\0") if x]
rc_f, out_f, err_f = g(["ls-tree", "-r", "-z", KOTEI])
blob = {}
for rec in out_f.split(b"\0"):
    if not rec:
        continue
    atama, _, p = rec.partition(b"\t")
    mode, typ, sha = atama.split()
    blob[p.decode("utf-8", "surrogateescape")] = (mode.decode(), typ.decode(), sha.decode())

kumi = {}
for p in paths:
    kumi.setdefault(p.casefold(), []).append(p)
futago = {k: sorted(v) for k, v in kumi.items() if len(v) >= 2}

gyo = []
for k in sorted(futago):
    for p in futago[k]:
        mode, typ, sha = blob[p]
        rc_s, out_s, _ = g(["cat-file", "-s", sha])
        rc_b, out_b, _ = g(["cat-file", "blob", sha])
        gyo.append((k, p, typ, sha, out_s.decode().strip(), str(len(out_b)),
                    hashlib.sha256(out_b).hexdigest(), "rc_s=%d rc_b=%d" % (rc_s, rc_b)))
K.kaku_tsv(os.path.join(BUNDLE, "raw", "10_kumi_git.tsv"), gyo,
           header=("casefold鍵", "git の path", "型", "blob sha1", "cat-file -s の bytes",
                   "実際に読めた bytes", "中身の sha256", "rc"))

# ★disk の側★ ―― mac の file 系は大小を畳む故、★親 dir を listdir して実名を引く★
disk = []
for k in sorted(futago):
    oya = set(os.path.dirname(p) for p in futago[k])
    for d in sorted(oya):
        zen = os.path.join(ROOT, d)
        na = sorted(os.listdir(zen)) if os.path.isdir(zen) else []
        for p in futago[k]:
            b = os.path.basename(p)
            ari = b in na
            zenpath = os.path.join(ROOT, p)
            if os.path.isfile(zenpath):
                dat = io.open(zenpath, "rb").read()
                st = os.stat(zenpath)
                disk.append((k, p, "dir に実名有り=%s" % ari, "open 出来る=True",
                             str(len(dat)), hashlib.sha256(dat).hexdigest(), str(st.st_ino)))
            else:
                disk.append((k, p, "dir に実名有り=%s" % ari, "open 出来る=False", "―", "―", "―"))
K.kaku_tsv(os.path.join(BUNDLE, "raw", "10_disk.tsv"), disk,
           header=("casefold鍵", "git の path", "親 dir の listdir に其の名が在るか",
                   "其の path で開けるか", "disk の bytes", "disk の sha256", "inode"))

K.kaku(os.path.join(BUNDLE, "raw", "10_shime.txt"), u"""★10 の〆 ―― 母數と組★
刻 = {koku} ／ 根 = {root} ／ 固定 = origin/main {kotei}
器 = git ls-tree -r --name-only -z(★NUL 区切り★ ―― git は非 ASCII を引用符で括る故 行では壊れる)
rc(name-only) = {rcn} ／ rc(full) = {rcf}(★returncode 素・管を通さぬ★)

★母數 = {bo} path★(固定 commit の全 blob path)
★casefold で括つて 2 本以上に成る組 = {kn} 組★
{ichiran}

★此の數が意味せぬ事★:
  ・母數は ★固定 commit {kotei} の樹★ の數である。★disk の數ではない★し、他の枝の數でもない。
  ・「{kn} 組」は ★path の字面を casefold で括つた數★ であり、
    ★中身が同じか否かは一切言つて居らぬ★(中身は 10_kumi_git.tsv の sha256 を見よ)。
  ・disk 側の「開けるか」は ★mac の file 系が大小を畳む★故に True に成り得る ――
    ★其の path の名で実体が在る事を意味せぬ★(実名は親 dir の listdir で引いた)。
  ・器の言(err): name-only={en} ／ full={ef}
""".format(koku=KOKU, root=ROOT, kotei=KOTEI, rcn=rc_n, rcf=rc_f, bo=len(paths), kn=len(futago),
           ichiran=u"\n".join(u"  ⑴鍵=%s ―― %s" % (k, u" ／ ".join(futago[k])) for k in sorted(futago)) or u"  ―(0 組)",
           en=err_n.strip() or u"―", ef=err_f.strip() or u"―"))
print("母數=%d 組=%d rc_name=%d rc_full=%d" % (len(paths), len(futago), rc_n, rc_f))
