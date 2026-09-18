# -*- coding: utf-8 -*-
"""★当て紙の基底を引き直す★(家老mac 09:00:05 msg_20260918_090005_9fd8e802)
PR#27 が merge され main=6bde7170… と成つた。共用樹 disk の門は ★未commit の三つ目の版★ ゆゑ、
其れを基底にした当て紙は main へ当たらぬ。∴ 基底を origin/main から束へ引き、sha256 を紙に刷る。
★base_gate.sh は byte 忠実の抜き取りであり kaki を通さぬ★ ―― 通せば行末が動き sha が変り、当て紙が当たらなく成る。
  (本束の他の出目は悉く kaki を通る。通さぬのは此の一本のみ ―― 之を宣する為に此の器が在る。)
四札: 刻=冠 / 根=cwd / rc=git の returncode(管を通さず) / 陽性対照=在らぬ ref を引いて rc≠0 を先に見せる。"""
import os
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

GATE = sys.argv[1] if len(sys.argv) > 1 else "scripts/checks/karo_mac_dasumae_gate.sh"
REF = sys.argv[2] if len(sys.argv) > 2 else "origin/main"
DEST = os.path.join(BUNDLE, "base_gate.sh")


def g(args):
    p = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout, p.stderr.decode("utf-8", "replace").strip(), p.returncode


def sha(b):
    return hashlib.sha256(b).hexdigest()


rows = []
# ―― ★陽性対照★ 在らぬ ref を先に引く(器が黙つて 0byte を書かぬ事を示す) ――
_o, e_bad, rc_bad = g(["show", "km-159-in-nai-ref-seitaishou:%s" % GATE])
rows.append(["★陽性対照★ 在らぬ ref", "km-159-in-nai-ref-seitaishou", rc_bad,
             ("★引けぬ(=正)★" if rc_bad != 0 else "引けた(=異)"), (e_bad or "(何も言はず)")[:60]])

head_sha, _e, rc1 = g(["rev-parse", REF])
blob_sha, _e2, rc2 = g(["rev-parse", "%s:%s" % (REF, GATE)])
disk_sha, _e3, rc3 = g(["rev-parse", "HEAD:%s" % GATE])
body, e_show, rc4 = g(["show", "%s:%s" % (REF, GATE)])
assert rc1 == 0 and rc2 == 0 and rc4 == 0, "基底が引けぬ ―― rc=%d/%d/%d %s" % (rc1, rc2, rc4, e_show)
assert len(body) > 0, "基底が 0byte ―― 引けて居らぬ"
with open(DEST, "wb") as fh:          # ★byte 忠実。kaki を通さぬ(宣は冠に在り)。★
    fh.write(body)

disk_bytes = open(GATE, "rb").read()
rows.append([REF + " の commit", head_sha.decode().strip(), rc1, "-", "-"])
rows.append([REF + " の blob(git object)", blob_sha.decode().strip(), rc2, "-", "-"])
rows.append(["HEAD の blob(git object)", disk_sha.decode().strip(), rc3,
             ("★main と別物★" if disk_sha != blob_sha else "同じ"), "-"])
rows.append(["★新基底★ base_gate.sh の中身 sha256", sha(body), 0, "%d行 %dbyte" % (body.count(b"\n"), len(body)), "束へ引いた"])
rows.append(["★旧基底★ 共用樹 disk の中身 sha256", sha(disk_bytes), 0,
             "%d行 %dbyte" % (disk_bytes.count(b"\n"), len(disk_bytes)),
             "★未commit の三つ目の版(触らず・読むのみ)★"])
rows.append(["二つの基底は", ("同じ" if body == disk_bytes else "★別物★"), 0,
             "差 %dbyte" % (len(body) - len(disk_bytes)), "-"])
kaku_tsv(os.path.join(BUNDLE, "raw", "65_kitei.tsv"), rows,
         header=["物", "値", "rc", "判", "註"])
kaku(os.path.join(BUNDLE, "raw", "66_kitei_sengen.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "★基底の宣★ ―― 当て紙が当たるべき相手は ★%s の %s★ である。\n"
     "  ・新基底 = 束内 base_gate.sh(byte 忠実の抜き取り・★kaki を通さぬ唯一の出目★)\n"
     "  ・旧基底 = 共用樹 disk の門(★未commit の三つ目の版★) ―― 触れず、読むのみ。\n"
     "  ・旧基底で書いた当て紙 raw/60・raw/61 は ★捨てず★ 残す(家老 09:00:05 の命)。\n"
     "★一つ前の弾(raw/50・60・61)の測りは悉く『旧基底』に対する物である。★\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT, REF, GATE))
print("新基底 sha256=%s (%dbyte)" % (sha(body), len(body)))
print("旧基底 sha256=%s (%dbyte)" % (sha(disk_bytes), len(disk_bytes)))
