#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_mon_no_todoki.py ―― 門の器が「何処の樹に・何の版で」在るかを歩き根を argv へ出して測る。
使い方: python3 driver/10_mon_no_todoki.py <repo根> <出先dir> <門のpath>
★歩き根は refs/heads と refs/remotes の両方★。片方だけの数は「無い」の證に成らぬ。"""
import subprocess, sys, os, datetime

def run(args, cwd):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def kaki(path, lines):
    """空の流れも一行として書く。末尾は必ず改行一つ。"""
    body = "\n".join(lines) if lines else "(空 ―― 該当0行)"
    if not body.endswith("\n"):
        body += "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return len(body.encode("utf-8")), body.count("\n")

def main():
    repo, out, gate = sys.argv[1], sys.argv[2], sys.argv[3]
    koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    rc, so, se = run(["git", "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes"], repo)
    refs = [r for r in so.splitlines() if r.strip()]
    kaki(os.path.join(out, "10_refs.txt"), refs)

    motsu, motanu = [], []
    for r in refs:
        rc2, so2, _ = run(["git", "rev-parse", "-q", "--verify", "%s:%s" % (r, gate)], repo)
        blob = so2.strip()
        if rc2 == 0 and blob:
            rc3, so3, _ = run(["git", "cat-file", "blob", blob], repo)
            n = so3.count("\n") + (0 if so3.endswith("\n") or not so3 else 1)
            motsu.append("%d\t%s\t%s" % (n, blob[:8], r))
        else:
            motanu.append(r)
    kaki(os.path.join(out, "11_motsu.tsv"), ["行数\tblob8\tref"] + motsu)
    kaki(os.path.join(out, "12_motanu.txt"), motanu)

    ban = {}
    for row in motsu:
        n, b8, _ = row.split("\t", 2)
        ban.setdefault((n, b8), 0)
        ban[(n, b8)] += 1
    kaki(os.path.join(out, "13_ban.tsv"),
         ["枝数\t行数\tblob8"] + ["%d\t%s\t%s" % (v, k[0], k[1])
                                  for k, v in sorted(ban.items(), key=lambda kv: -kv[1])])

    # 2320dbb を載せる ref(祖先判定) ―― rc=1 は「載せぬ」であつて器の疵ではない
    noseru, nosenu = [], []
    for r in refs:
        rc4, _, _ = run(["git", "merge-base", "--is-ancestor", "2320dbb", r], repo)
        (noseru if rc4 == 0 else nosenu).append("%s\trc=%d" % (r, rc4))
    kaki(os.path.join(out, "14_2320dbb_noseru.tsv"), ["ref\trc"] + noseru)
    kaki(os.path.join(out, "15_2320dbb_nosenu.tsv"), ["ref\trc"] + nosenu)

    rcd, sod, _ = run(["git", "hash-object", gate], repo)
    with open(os.path.join(repo, gate), "rb") as fh:
        disk = fh.read()
    kaki(os.path.join(out, "16_disk.tsv"),
         ["欄\t値", "刻\t%s" % koku, "歩き根\trefs/heads + refs/remotes",
          "ref母數\t%d" % len(refs), "持つ\t%d" % len(motsu), "持たぬ\t%d" % len(motanu),
          "版の数\t%d" % len(ban), "disk行数\t%d" % disk.count(b"\n"),
          "disk_blob\t%s" % sod.strip(), "disk_blob_rc\t%d" % rcd,
          "2320dbb載せる\t%d" % len(noseru), "2320dbb載せぬ\t%d" % len(nosenu)])
    print("★了★ ref=%d 持つ=%d 持たぬ=%d 版=%d 載せる=%d" %
          (len(refs), len(motsu), len(motanu), len(ban), len(noseru)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
