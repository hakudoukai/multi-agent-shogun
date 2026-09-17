# -*- coding: utf-8 -*-
"""㋐ 母數の宣 ―― 割当の枝を逐語で列べ、full sha を書き、★手許に物が在るか★を一本づつ検める。

  usage: python3 driver/10_bogen.py <札のpath> <出目dir>
  ★字面で札を固定せぬ★(argv から受ける ―― 器を他席の札へも向けられる様に)。
  出目: <出目dir>/11_bogen.tsv  欄= n / sha40 / branch / cat_file_rc / kind / short_ok
"""
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")


def sh(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    fuda, outdir = sys.argv[1], sys.argv[2]
    import yaml
    d = yaml.safe_load(open(fuda, encoding="utf-8"))
    body = d.get("eda_warimochi") or ""
    rows, seen = [], {}
    n = 0
    for ln in body.split("\n"):
        if not ln.strip():
            continue
        parts = ln.split()
        if len(parts) != 2:
            rows.append([n, "★讀めぬ行★", ln.strip(), "-", "-", "-"])
            continue
        n += 1
        sha, name = parts
        rc, out, _ = sh(["git", "cat-file", "-e", sha + "^{commit}"])
        rc2, kind, _ = sh(["git", "cat-file", "-t", sha])
        rc3, full, _ = sh(["git", "rev-parse", sha + "^{commit}"])
        ok = "同一" if (rc3 == 0 and full == sha) else ("★食違★:" + full if rc3 == 0 else "★引けぬ★")
        seen.setdefault(sha, []).append(name)
        rows.append([n, sha, name, rc, kind if rc2 == 0 else "★引けぬ★", ok])
    K.kaku_tsv(outdir + "/11_bogen.tsv", rows,
               header=["n", "sha40", "branch", "cat_file_e_rc", "object_type", "sha40_vs_rev_parse"])
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    sys.stderr.write("母數=%d / 物が手許に在る=%d / 同一 sha の枝=%d\n"
                     % (n, sum(1 for r in rows if r[3] == 0), len(dup)))
    for k, v in dup.items():
        sys.stderr.write("★同一 sha★ %s : %s\n" % (k, " ".join(v)))
    return 0


sys.exit(main())
