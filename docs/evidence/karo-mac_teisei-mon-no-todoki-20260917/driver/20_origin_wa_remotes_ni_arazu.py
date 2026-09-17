#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_origin_wa_remotes_ni_arazu.py ―― 「refs/remotes に無い」が「origin に無い」の證に成るかを測る。
使ひ方: python3 driver/20_origin_wa_remotes_ni_arazu.py <repo根> <出先dir> <門のpath> <門のblob>
★歩き根は二つ★: 甲=手元(refs/heads+refs/remotes) 乙=origin の生(git ls-remote --heads origin)。
乙は網を渡るゆゑ、手元に object の無い枝が出る ―― 其れは「測れぬ」であつて「無い」に非ず。"""
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
    repo, out, gate, blob = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    koku = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

    # 甲 ―― 手元の歩き根
    _, so, _ = run(["git", "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes"], repo)
    temoto = [r for r in so.splitlines() if r.strip()]
    kaki(os.path.join(out, "20_temoto_refs.txt"), temoto)

    # 乙 ―― origin の生。網を渡る。rc も書く。
    rc_ls, so_ls, se_ls = run(["git", "ls-remote", "--heads", "origin"], repo)
    nama = [l for l in so_ls.splitlines() if l.strip()]
    kaki(os.path.join(out, "21_origin_nama.txt"), nama)

    # 門の blob を載せる枝 ―― 乙の側で。object が手元に無い枝は「測れぬ」へ。
    noseru, hakarenu = [], []
    for line in nama:
        parts = line.split("\t")
        if len(parts) != 2:
            hakarenu.append("形が二欄ならず\t%s" % line)
            continue
        sha, ref = parts[0], parts[1]
        rc_e, _, _ = run(["git", "cat-file", "-e", "%s^{commit}" % sha], repo)
        if rc_e != 0:
            hakarenu.append("object 手元に無し\t%s\t%s" % (sha, ref))
            continue
        rc_b, so_b, _ = run(["git", "rev-parse", "-q", "--verify", "%s:%s" % (sha, gate)], repo)
        b = so_b.strip()
        if b == blob:
            noseru.append("%s\t%s\t%s" % (ref, sha, b))
    kaki(os.path.join(out, "22_origin_ni_aru_kono_ban.tsv"), noseru)
    kaki(os.path.join(out, "23_hakarenu.tsv"), hakarenu)

    # 三面の対照 ―― 同じ一本の枝を、三つの器で問ふ
    br = "karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917"
    san = []
    rc_a, so_a, _ = run(["git", "show-ref", "--verify", "refs/heads/%s" % br], repo)
    san.append("甲 refs/heads\trc=%d\t%s" % (rc_a, so_a.strip() or "(空)"))
    rc_b2, so_b2, se_b2 = run(["git", "show-ref", "--verify", "refs/remotes/origin/%s" % br], repo)
    san.append("乙 refs/remotes\trc=%d\t%s" % (rc_b2, (so_b2.strip() or se_b2.strip() or "(空)")))
    rc_c, so_c, _ = run(["git", "ls-remote", "origin", "refs/heads/%s" % br], repo)
    san.append("丙 ls-remote\trc=%d\t%s" % (rc_c, so_c.strip() or "(空)"))
    kaki(os.path.join(out, "24_sanmen.tsv"), san)

    shime = [
        "刻\t%s" % koku,
        "歩き根甲 手元 refs/heads+refs/remotes\t%d" % len(temoto),
        "歩き根乙 origin の生 ls-remote --heads\t%d\trc=%d" % (len(nama), rc_ls),
        "乙の内 門blob %s を載せる枝\t%d" % (blob[:16], len(noseru)),
        "乙の内 測れぬ枝(object 手元に無し 等)\t%d" % len(hakarenu),
        "門のpath\t%s" % gate,
    ]
    kaki(os.path.join(out, "25_shime.tsv"), shime)
    for l in shime:
        print(l)

if __name__ == "__main__":
    main()
