# -*- coding: utf-8 -*-
"""㋐ 母數を埋める ―― origin の heads 全本について 門 scripts/checks/karo_mac_dasumae_gate.sh の在否と blob。

家老の穴: 当 repo の fetch refspec は +refs/heads/main:refs/remotes/origin/main 一本 ∴ 手元に
object が在るのは 244 中 86 のみであつた。本器は refs/km110/* へ全本を取り(refs/remotes/origin/* は不触)、
★取れた本數と取れなんだ本數を別欄で★ 立てる(「0」と丸めぬ)。

usage: python3 driver/10_bogen.py <bundle_root> <repo_root>
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

GATE = "scripts/checks/karo_mac_dasumae_gate.sh"
VERIFY = "scripts/checks/karo_mac_manifest_verify.py"
APPEND = "scripts/checks/karo_mac_manifest_append.py"


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "surrogateescape"), p.stderr.decode("utf-8", "surrogateescape")


def main(argv):
    bundle, repo = argv[1], argv[2]
    raw = os.path.join(bundle, "raw")

    # ⑴ ls-remote(遠隔の名簿・刻付き) と refs/km110/*(手元に取れた物) を別欄で読む
    rem = {}
    with open(os.path.join(raw, "10_ls_remote_heads.txt"), encoding="utf-8", errors="surrogateescape") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            sha, ref = ln.split("\t", 1)
            assert ref.startswith("refs/heads/"), ref
            rem[ref[len("refs/heads/"):]] = sha

    loc = {}
    with open(os.path.join(raw, "12_km110_refs.txt"), encoding="utf-8", errors="surrogateescape") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if not ln:
                continue
            sha, ref = ln.split(" ", 1)
            assert ref.startswith("refs/km110/"), ref
            loc[ref[len("refs/km110/"):]] = sha

    torenu = sorted(set(rem) - set(loc))          # 名簿に在るが手元に取れなんだ
    yokei = sorted(set(loc) - set(rem))           # 手元に在るが名簿に無い(取つた後に消えた等)
    ugoita = sorted(n for n in set(rem) & set(loc) if rem[n] != loc[n])  # 二つの刻の間に頭が動いた

    rows = []
    stat = {"有": 0, "無": 0, "測れぬ": 0}
    blobs = {}
    for name in sorted(rem):
        r_sha = rem[name]
        l_sha = loc.get(name, "")
        if not l_sha:
            rows.append([name, r_sha, "-", "測れぬ", "-", "-", "-", "手元に object 無(fetch で取れなんだ)"])
            stat["測れぬ"] += 1
            continue
        note = "同" if r_sha == l_sha else "★頭が動いた(名簿 %s / 手元 %s)★" % (r_sha[:12], l_sha[:12])
        cells = []
        for path in (GATE, VERIFY, APPEND):
            rc, out, _ = git(repo, "rev-parse", "--verify", "--quiet", "%s:%s" % (l_sha, path))
            cells.append(out.strip() if rc == 0 else "")
        gate_blob, ver_blob, app_blob = cells
        if gate_blob:
            stat["有"] += 1
            blobs.setdefault(gate_blob, []).append(name)
        else:
            stat["無"] += 1
        rows.append([name, r_sha, l_sha, "有" if gate_blob else "無",
                     gate_blob or "-", ver_blob or "-", app_blob or "-", note])

    K.kaku_tsv(os.path.join(raw, "21_zenpon.tsv"), rows,
               header=["枝名", "遠隔sha(ls-remote 17:11:06)", "手元sha(refs/km110 17:11:19)",
                       "門の在否", "門blob(full)", "verify.py blob(full)", "append.py blob(full)", "註"])

    lines = []
    lines.append("㋐ 母數 ―― 遠隔 heads 全本の門の在否(★數へ直した★)")
    lines.append("遠隔 heads(git ls-remote --heads origin 17:11:06) = %d 本" % len(rem))
    lines.append("refs/km110/* へ取れた本數(git fetch '+refs/heads/*:refs/km110/*' 17:11:19) = %d 本" % len(loc))
    lines.append("★取れなんだ本數 = %d 本★(別欄・0 と丸めては居らぬ)" % len(torenu))
    for n in torenu:
        lines.append("  取れぬ: %s" % n)
    lines.append("名簿に無いが手元に在る本數 = %d 本" % len(yokei))
    for n in yokei:
        lines.append("  余計: %s" % n)
    lines.append("二刻の間に頭が動いた本數 = %d 本" % len(ugoita))
    for n in ugoita:
        lines.append("  動: %s 名簿=%s 手元=%s" % (n, rem[n][:12], loc[n][:12]))
    lines.append("")
    lines.append("門 %s を ―― 載せる=%d 本 / 載せぬ=%d 本 / 測れぬ=%d 本 (和=%d)"
                 % (GATE, stat["有"], stat["無"], stat["測れぬ"], stat["有"] + stat["無"] + stat["測れぬ"]))
    lines.append("門の blob の種數 = %d" % len(blobs))
    for b in sorted(blobs, key=lambda x: -len(blobs[x])):
        lines.append("  %s  %d 本" % (b, len(blobs[b])))
    K.kaku(os.path.join(raw, "22_bogen_matome.txt"), "\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
