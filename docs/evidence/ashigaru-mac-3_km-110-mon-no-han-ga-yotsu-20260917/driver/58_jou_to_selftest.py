# -*- coding: utf-8 -*-
"""㋑㋒ の補ひ ―― ⑴條①〜條⑤ を ★一條づつ★ 数へる(和で数へると零が隠れる)
⑵各版の ★自己検め(--selftest)★ を走らせる(器が己の陽性對照で鳴るか)。

usage: python3 driver/58_jou_to_selftest.py <bundle_root> <repo_root>
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

ORDER = ["9cd550fc2cf963ca0475b3448bb33483b9aede6b",
         "54e133c85832d48aa731d0ab0d105d399b9b8fbd",
         "b0bf5b05ededce4b06286dbab05cf0b616414ef2",
         "054c442eaee3886b2283f98f7c3a1ab8cb813b68"]
DISK_VER8 = "ebfc4c0e"
JOU = ["條①", "條②", "條③", "條④", "條⑤"]


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    raw = os.path.join(bundle, "raw")
    rows = []
    for b in ORDER:
        t = open(os.path.join(raw, "31_han_%s.sh" % b[:16]), encoding="utf-8", errors="surrogateescape").read()
        rows.append([b[:16]] + [str(t.count(j)) for j in JOU]
                    + ["有" if all(t.count(j) for j in JOU) else "★欠★"])
    K.kaku_tsv(os.path.join(raw, "59_jou_kobetsu.tsv"), rows,
               header=["門版(16)"] + ["%s の字數" % j for j in JOU] + ["五條 悉く在るか"])

    st = []
    for b in ORDER:
        d = os.path.join(repo, ".km110_scratch", "甲_%s_%s" % (b[:16], DISK_VER8))
        p = subprocess.run(["bash", os.path.join(d, "karo_mac_dasumae_gate.sh"), "--selftest"],
                           cwd=os.path.join(bundle, "shiken"),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        body = p.stdout.decode("utf-8", "surrogateescape")
        nm = "mon_%s_自_%s.log" % (b[:16], time.strftime("%H%M%S"))
        with open(os.path.join(bundle, "_gate", nm), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# 自己検め(--selftest) 版=%s / 刻=%s / rc=%d\n" % (b, time.strftime("%F %T %z"), p.returncode))
            fh.write(body if body else "(出目 無)\n")
        owari = [ln for ln in body.split("\n") if ln.strip()][-1] if body.strip() else "(出目 無)"
        st.append([b[:16], str(p.returncode), owari.strip(), nm])
        time.sleep(1)
    K.kaku_tsv(os.path.join(raw, "60_selftest.tsv"), st,
               header=["門版(16)", "rc", "終の一行", "控"])

    out = ["★條を一條づつ数へた(和で数へれば零が隠れる)★"]
    out.append("版\t" + "\t".join(JOU) + "\t五條 悉く")
    for r in rows:
        out.append("\t".join(r))
    out.append("")
    out.append("★各版の自己検め(--selftest)★")
    for r in st:
        out.append("  版%s rc=%s ―― %s" % (r[0], r[1], r[2]))
    K.kaku(os.path.join(raw, "61_jou_selftest_matome.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
