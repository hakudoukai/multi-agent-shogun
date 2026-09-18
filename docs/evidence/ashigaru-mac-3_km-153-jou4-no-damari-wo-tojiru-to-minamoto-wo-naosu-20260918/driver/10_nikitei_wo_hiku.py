# -*- coding: utf-8 -*-
"""二基底を束へ引く ―― 新(origin/main の blob)と旧(共用樹 disk の未commit 版)。
家老令 msg_20260918_090005_9fd8e802: 「当て紙は★其の基底に対して★ git apply --check せよ」。
★共用樹の file は触らぬ(読取のみ)★。"""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module

K = import_module("00_kaki")

HERE = os.path.dirname(os.path.abspath(__file__))
TABA = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(TABA, "..", "..", ".."))
GATE_REL = "scripts/checks/karo_mac_dasumae_gate.sh"


def sh(args, cwd=ROOT, binary=False):
    p = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout if binary else p.stdout.decode("utf-8", "replace")
    return out, p.stderr.decode("utf-8", "replace"), p.returncode


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    rows = []
    # 新基底 ―― origin/main の blob を bytes で引く(改行を殺さぬ)
    shin, err, rc = sh(["git", "show", "origin/main:" + GATE_REL], binary=True)
    if rc != 0:
        print("新基底が引けぬ rc=%d err=%s" % (rc, err))
        return 2
    p_shin = os.path.join(TABA, "_fx", "base_shin_origin_main.sh")
    with open(p_shin, "wb") as fh:
        fh.write(shin)

    # 旧基底 ―― 共用樹 disk の版(未commit)。★読取のみ★
    with open(os.path.join(ROOT, GATE_REL), "rb") as fh:
        kyuu = fh.read()
    p_kyuu = os.path.join(TABA, "_fx", "base_kyuu_disk.sh")
    with open(p_kyuu, "wb") as fh:
        fh.write(kyuu)

    # HEAD の blob も参考に(三版在る事の證)
    head_b, _e, rc_h = sh(["git", "show", "HEAD:" + GATE_REL], binary=True)

    blob_shin, _e, _r = sh(["git", "rev-parse", "origin/main:" + GATE_REL])
    blob_head, _e, _r = sh(["git", "rev-parse", "HEAD:" + GATE_REL])
    main_sha, _e, _r = sh(["git", "rev-parse", "origin/main"])
    head_sha, _e, _r = sh(["git", "rev-parse", "HEAD"])
    koku, _e, _r = sh(["date", "+%Y-%m-%dT%H:%M:%S%z"])

    def gyou(b):
        return b.decode("utf-8", "replace").count("\n")

    rows.append(("新基底", "origin/main " + main_sha.strip(), blob_shin.strip(),
                 str(len(shin)), str(gyou(shin)), sha_bytes(shin),
                 os.path.relpath(p_shin, TABA)))
    rows.append(("旧基底", "共用樹 disk(未commit)", "(blob 無し ―― index にも無い版)",
                 str(len(kyuu)), str(gyou(kyuu)), sha_bytes(kyuu),
                 os.path.relpath(p_kyuu, TABA)))
    rows.append(("参考", "HEAD " + head_sha.strip(), blob_head.strip(),
                 str(len(head_b)) if rc_h == 0 else "測れぬ",
                 str(gyou(head_b)) if rc_h == 0 else "測れぬ", sha_bytes(head_b) if rc_h == 0 else "測れぬ",
                 "(束へ引かず ―― 当て紙の基底に用ゐぬ)"))
    K.kaku_tsv(os.path.join(TABA, "raw", "10_nikitei.tsv"), rows,
               header=("名", "出所", "git blob", "bytes", "LF行", "sha256", "束内 path"))
    K.kaku(os.path.join(TABA, "raw", "10_nikitei.koku.txt"),
           "引いた刻=%s\n★此の數が意味せぬ事★: 三版在る事は「何れかが誤り」の意ではない ―― 版が割れて居るのみ。"
           % koku.strip())
    print("新=%s(%dbyte) 旧=%s(%dbyte)" % (blob_shin.strip()[:8], len(shin), sha_bytes(kyuu)[:8], len(kyuu)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
