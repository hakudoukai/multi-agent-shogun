# -*- coding: utf-8 -*-
"""㋑⑵ の母集団 ―― ★60 本の mac 枝 tip★ を据ゑ、手許に物が在るかを検める。

  usage: python3 driver/20_roster.py <家老TSV(20_mac_eda.tsv)> <出目dir>
  ★字面で固定せぬ★(argv から受ける)。
  據: 家老mac の實測(docs/evidence/karo-mac-eda-fuyou-20260917/raw/20_mac_eda.tsv・ls-remote 由来)。
      ★他席の數を其の儘使はぬ★ ―― 己で ⑴ ls-remote を引き直して突合し、⑵ 物の存否を一本づつ検める。
  出目: 21_roster.tsv(sha40/branch/cat_file_rc/lsremote一致) / 22_lsremote.txt / 22_lsremote.rc
"""
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")
MAC = ("karo-mac/", "ashigaru-mac-")


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    karo_tsv, outdir = sys.argv[1], sys.argv[2]

    # ⑴ 己で origin を引き直す(★refs を書換へぬ読取のみ★ ―― fetch ではない)
    p = subprocess.run(["git", "ls-remote", "--heads", "origin"], capture_output=True, text=True)
    K.kaku(outdir + "/22_lsremote.txt", p.stdout if p.stdout.strip() else "")
    K.kaku(outdir + "/22_lsremote.rc", "rc=%d\nstderr_bytes=%d" % (p.returncode, len(p.stderr.encode())))
    live = {}
    if p.returncode == 0:
        for ln in p.stdout.split("\n"):
            if "\t" not in ln:
                continue
            sha, ref = ln.split("\t", 1)
            name = ref.strip()[len("refs/heads/"):] if ref.strip().startswith("refs/heads/") else ref.strip()
            if name.startswith(MAC):
                live[name] = sha.strip()

    # ⑵ 家老の臺帳を讀む
    karo = {}
    with open(karo_tsv, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            ln = ln.rstrip("\n")
            if i == 0 or not ln.strip():
                continue
            c = ln.split("\t")
            if len(c) >= 2:
                karo[c[1]] = c[0]

    names = sorted(set(karo) | set(live))
    rows, hand = [], 0
    for nm in names:
        ks, ls = karo.get(nm, "-"), live.get(nm, "-")
        sha = ks if ks != "-" else ls
        rc = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"],
                            capture_output=True, text=True).returncode if sha != "-" else "-"
        if rc == 0:
            hand += 1
        if ks == "-":
            agree = "★家老臺帳に無し(己の ls-remote のみ)★"
        elif ls == "-":
            agree = "★己の ls-remote に無し(家老臺帳のみ)★" if p.returncode == 0 else "ls-remote 引けず(突合せず)"
        else:
            agree = "一致" if ks == ls else "★食違★ls=" + ls
        rows.append([sha, nm, rc, agree])
    K.kaku_tsv(outdir + "/21_roster.tsv", rows, header=["sha40", "branch", "cat_file_e_rc", "lsremote_totsugou"])
    sys.stderr.write("家老臺帳=%d / 己の ls-remote(mac)=%d(rc=%d) / 和=%d / 手許に物=%d\n"
                     % (len(karo), len(live), p.returncode, len(names), hand))
    return 0


sys.exit(main())
