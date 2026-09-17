#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""40_toguchi.py ―― ㋔で「測れて居らぬ」と書いた一点を測る。

問: 案⑵(己の三束のみ焼く)は ★.gitignore を一指も触れずに★ 成るか。

★測り方の肝★: 本番の index へ一指も触れぬ。
  .git/index を写して ★捨て臺帳★ を作り、GIT_INDEX_FILE で其方へ向ける。
  測る前後で本番 index の sha256 を取り、★動いて居らぬ事を證してから★ 出目を刷る。
  (動いて居れば rc=3 で落ちる ―― 出目を刷らぬ)

使ひ方: 40_toguchi.py <repo根> <束> [<束>...]
"""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K

SUTE = "/private/tmp/km122_toguchi_ki"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def git(repo, args, idx=None):
    env = dict(os.environ)
    if idx:
        env["GIT_INDEX_FILE"] = idx
    p = subprocess.run(["git", "-C", repo] + args, capture_output=True, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def nuri(repo, taba, tsukau_f, idx):
    """捨て臺帳へ add し、三束に載つた path を返す。"""
    a = ["add"] + (["-f"] if tsukau_f else []) + list(taba)
    rc, _, err = git(repo, a, idx)
    rc2, out, _ = git(repo, ["ls-files", "--cached", "--"] + list(taba), idx)
    nose = [l for l in out.split("\n") if l]
    return rc, err, rc2, nose


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    repo, taba = sys.argv[1], sys.argv[2:]
    real = os.path.join(repo, ".git", "index")
    mae = sha(real)

    os.makedirs(SUTE, exist_ok=True)
    kekka = {}
    for na, f in (("甲_素のadd(-f無)", False), ("乙_add -f", True)):
        idx = os.path.join(SUTE, "sute_%s.idx" % ("f" if f else "nashi"))
        with open(real, "rb") as a, open(idx, "wb") as b:
            b.write(a.read())
        kekka[na] = nuri(repo, taba, f, idx)

    ato = sha(real)
    if mae != ato:
        sys.stderr.write("★本番 index が動いた ―― 出目を刷らず落ちる★ 前=%s 後=%s\n" % (mae, ato))
        return 3

    # disk 側の本数(母数)と、遮られて居る本数
    disk = []
    for t in taba:
        for r, _d, fs in os.walk(os.path.join(repo, t)):
            for n in fs:
                p = os.path.join(r, n)
                if os.path.isfile(p) and not os.path.islink(p):
                    disk.append(os.path.relpath(p, repo))
    disk.sort()
    rc_ci, out_ci, _ = git(repo, ["check-ignore"] + disk)
    shadan = [l for l in out_ci.split("\n") if l]

    # 本番 index に三束が何本在るか(= 戸が閉ぢて居る事の git 側の證)
    _rc, out_h, _ = git(repo, ["ls-files", "--cached", "--"] + list(taba))
    honban = [l for l in out_h.split("\n") if l]

    gy = []
    gy.append("★㋔の穴を塞ぐ ―― 案⑵は .gitignore を触れずに成るか★")
    gy.append("repo根= %s" % repo)
    gy.append("束(母数)= %d" % len(taba))
    for t in taba:
        gy.append("  %s" % t)
    gy.append("")
    gy.append("本番 index sha256 前= %s" % mae)
    gy.append("本番 index sha256 後= %s" % ato)
    gy.append("★不動を證した上で以下を刷る★")
    gy.append("")
    gy.append("disk 側 三束の本数(S_ISREG・symlink 除)= %d" % len(disk))
    gy.append("本番 index に在る三束の本数= %d  ―― 戸は閉ぢて居る" % len(honban))
    gy.append("check-ignore で遮られる本数= %d / %d (rc=%d)" % (len(shadan), len(disk), rc_ci))
    gy.append("")
    for na in ("甲_素のadd(-f無)", "乙_add -f"):
        rc, err, rc2, nose = kekka[na]
        gy.append("[%s] add rc=%d  err行=%d  ls-files rc=%d  ★捨て臺帳に載つた本数=%d★"
                  % (na, rc, len([x for x in err.split("\n") if x]), rc2, len(nose)))
        if err.strip():
            for l in err.split("\n")[:4]:
                if l:
                    gy.append("    err: %s" % K.esc(l))
    gy.append("")
    b_nashi = len(kekka["甲_素のadd(-f無)"][3])
    b_f = len(kekka["乙_add -f"][3])
    gy.append("★断★")
    if b_nashi == 0 and b_f == len(disk):
        gy.append("  ⑴ 素の add は ★rc=0 で黙つて 0 本★ ―― 誤つて空の commit を作り得る")
        gy.append("  ⑵ add -f は %d/%d 本を載せる ―― ★.gitignore を書換へる要は無い★" % (b_f, len(disk)))
    else:
        gy.append("  ★上の二つの何れでもない ―― 素=%d 本 / -f=%d 本 / disk=%d 本★" % (b_nashi, b_f, len(disk)))
    gy.append("")
    gy.append("★之が意味せぬ事★")
    gy.append("  ・「-f で載る」は「載せてよい」の意ではない ―― 可否は委員長の裁である")
    gy.append("  ・捨て臺帳で成る事は、本番の index・枝・remote で成る事を意味せぬ(測つて居らぬ)")
    gy.append("  ・本数は ★此の刻の disk★ の函数である ―― 束は測る間も育つ")

    K.kaku(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "40_toguchi.txt"),
           "\n".join(gy))

    # 載つた物の内訳(TSV)
    rows = [("束", "path", "bytes")]
    for p in kekka["乙_add -f"][3]:
        ap = os.path.join(repo, p)
        rows.append((p.split("/")[2] if p.count("/") > 2 else "?", p,
                     str(os.path.getsize(ap)) if os.path.exists(ap) else "-1"))
    K.kaku(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "40_nosetta.tsv"),
           "\n".join("\t".join(K.esc(c) for c in r) for r in rows))

    sys.stderr.write("40_toguchi rc=0 disk=%d 素=%d -f=%d 遮=%d index不動=True\n"
                     % (len(disk), b_nashi, b_f, len(shadan)))
    return 0


sys.exit(main())
