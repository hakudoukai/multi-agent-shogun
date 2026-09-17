# -*- coding: utf-8 -*-
"""㋑ 版の表 ―― 門の blob 毎に六欄。

欄: ⑴full sha ⑵行 ⑶byte ⑷KM_GATE_MANIFEST_BASE の参照數 ⑸karo_mac_manifest_verify の参照數
    ⑹載せる枝の本數と代表枝名(三つ迄)
★單位を欄名へ焼く★: 行(LF數) と 行(grep -c '' 相當=末の不完全行も一と數へる) を別欄に立てる。
    同じ「行」の語で二つの數を混ぜぬ為(第57弾で踏んだ)。

usage: python3 driver/30_han.py <bundle_root> <repo_root>
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")


def main(argv):
    bundle, repo = argv[1], argv[2]
    raw = os.path.join(bundle, "raw")

    blobs = {}
    with open(os.path.join(raw, "21_zenpon.tsv"), encoding="utf-8", errors="surrogateescape") as fh:
        head = fh.readline()
        for ln in fh:
            c = ln.rstrip("\n").split("\t")
            if c[3] != "有":
                continue
            blobs.setdefault(c[4], []).append(c[0])

    rows = []
    for b in sorted(blobs, key=lambda x: -len(blobs[x])):
        p = subprocess.run(["git", "-C", repo, "cat-file", "blob", b], stdout=subprocess.PIPE)
        data = p.stdout
        assert p.returncode == 0, b
        # ★己で書いた物でなく git が吐いた byte を其の儘數へる★
        open(os.path.join(raw, "31_han_%s.sh" % b[:16]), "wb").write(data)
        text = data.decode("utf-8", "surrogateescape")
        lf = data.count(b"\n")
        grep_gyou = lf + (0 if (not data or data.endswith(b"\n")) else 1)
        base_ref = text.count("KM_GATE_MANIFEST_BASE")
        ver_ref = text.count("karo_mac_manifest_verify")
        eda = sorted(blobs[b])
        rows.append([b, str(lf), str(grep_gyou), str(len(data)), str(base_ref), str(ver_ref),
                     str(len(eda)), " / ".join(eda[:3])])

    K.kaku_tsv(os.path.join(raw, "32_han_hyou.tsv"), rows,
               header=["⑴門blob(full sha)", "⑵行(LF數)", "⑵'行(grep -c ''相當)", "⑶byte",
                       "⑷KM_GATE_MANIFEST_BASE 参照數", "⑸karo_mac_manifest_verify 参照數",
                       "⑹載せる枝の本數", "⑹代表枝名(三つ迄)"])

    out = ["㋑ 版の表(門 blob 毎・六欄)", ""]
    for r in rows:
        out.append("blob %s" % r[0])
        out.append("  行(LF數)=%s / 行(grep相當)=%s / byte=%s" % (r[1], r[2], r[3]))
        out.append("  KM_GATE_MANIFEST_BASE 参照=%s / karo_mac_manifest_verify 参照=%s" % (r[4], r[5]))
        out.append("  載せる枝=%s 本 ―― %s" % (r[6], r[7]))
    out.append("")
    out.append("和(載せる枝の本數) = %d 本" % sum(int(r[6]) for r in rows))
    K.kaku(os.path.join(raw, "33_han_matome.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
