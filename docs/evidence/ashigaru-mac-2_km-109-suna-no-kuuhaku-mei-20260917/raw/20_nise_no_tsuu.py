# -*- coding: utf-8 -*-
"""㋒ 「素の空白名」が ★偽の通★ を産むかを、生器を走らせて確かめる(專任2 km-109)。

作る五つの條(三つは札の指定・二つは當席が足した基準線と決め手):
  c1_chigau        `a` と `a b.txt` 両方在り・中身 ★違ふ★      (札⑴)
  c2_saki_dake     `a` だけ在り(`a b.txt` は disk に無い)       (札⑵)
  c3_nashi         どちらも無し                                 (札⑶)
  c4_onaji         `a` と `a b.txt` 両方在り・中身 ★同じ★      (★決め手★ 當席が足した)
  c5_kuuhaku_dake  `a b.txt` だけ在り(先頭語 `a` は無い)        (★基準線★ 當席が足した)

★sha256 は悉く実物から取る★ ―― 手で書かぬ。
  c1/c4/c5 は其の條の `a b.txt` 其の物から。
  c2/c3 は `a b.txt` が disk に無い故、★同じ中身を持つ c5 の実物★ から取り、其の旨を紙に書く。
試験臺帳(shiken_daichou.txt)は ★手で綴る★ ―― 正規の書き手 karo_mac_manifest_append.py は
空白名を必ず括る(tsuzuri の逐語)故、★素の空白名は正規の書き手からは出ぬ★。
之は束の臺帳(manifest.txt)ではなく ★試験の入力★ である。
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki  # noqa: E402

BUNDLE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
UTSUWA = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")
FIX = os.path.join(BUNDLE, "fixtures")

NAKAMI_X = "kore ga honmono no nakami de gozaru\n"     # `a b.txt` の中身
NAKAMI_Y = "kore wa betsu no nakami de gozaru\n"       # `a` の中身(違ふ側)

SPACE = "a b.txt"
SAKI = "a"


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def kazoe(p):
    n = os.path.getsize(p)
    with open(p, "rb") as fh:
        data = fh.read()
    gyou = data.count(b"\n") + (0 if (not data or data.endswith(b"\n")) else 1)
    return n, gyou


# ―― 條ごとに紙を置く ――
JOU = {
    "c1_chigau":       {SPACE: NAKAMI_X, SAKI: NAKAMI_Y},
    "c2_saki_dake":    {SAKI: NAKAMI_X},
    "c3_nashi":        {"README.md": "# 此の條は `a` も `a b.txt` も置かぬ(實体無の陽性対照)\n"},
    "c4_onaji":        {SPACE: NAKAMI_X, SAKI: NAKAMI_X},
    "c5_kuuhaku_dake": {SPACE: NAKAMI_X},
}
for d, mono in JOU.items():
    os.makedirs(os.path.join(FIX, d), exist_ok=True)
    for na, nakami in mono.items():
        kaki.kaku(os.path.join(FIX, d, na), nakami)

# ―― sha は実物から ――
MOTO = os.path.join(FIX, "c5_kuuhaku_dake", SPACE)     # c2/c3 の sha の出所
SHA_MOTO = {
    "c1_chigau":       os.path.join(FIX, "c1_chigau", SPACE),
    "c2_saki_dake":    MOTO,
    "c3_nashi":        MOTO,
    "c4_onaji":        os.path.join(FIX, "c4_onaji", SPACE),
    "c5_kuuhaku_dake": MOTO,
}

rows = []
for d in ["c1_chigau", "c2_saki_dake", "c3_nashi", "c4_onaji", "c5_kuuhaku_dake"]:
    moto = SHA_MOTO[d]
    sha = sha256_of(moto)
    n, g = kazoe(moto)
    gyou = "path=%s sha256=%s bytes=%d lines=%d" % (SPACE, sha, n, g)
    man = os.path.join(FIX, d, "shiken_daichou.txt")
    kaki.kaku(man, "\n".join([
        "# 試験臺帳(★手で綴つた★ ―― 正規の書き手は空白名を必ず括る故、素の空白名は其處からは出ぬ)",
        "# sha256 の出所(実物) = %s" % os.path.relpath(moto, BUNDLE),
        gyou,
    ]))
    r = subprocess.run([sys.executable, UTSUWA, man, os.path.join(FIX, d) + os.sep],
                       capture_output=True, text=True)
    rows.append((d, moto, sha, gyou, man, r))

out = []
out.append("# ㋒ 偽の通は出るか ―― 五條の實測(專任2 km-109)")
out.append("")
out.append("## 走らせた口(逐語)")
out.append("  %s <試験臺帳> <其の條の dir>/" % os.path.relpath(UTSUWA, REPO))
out.append("  ★基点を第二引数で明示★ ―― 既定基点(repo 根)を混ぜぬ為")
out.append("")
out.append("## 出目一覧")
out.append("")
out.append("| 條 | disk に在る物 | 臺帳の行(sha は実物から) | 出目 | rc |")
out.append("|---|---|---|---|---|")
for d, moto, sha, gyou, man, r in rows:
    aru = sorted(x for x in os.listdir(os.path.join(FIX, d)) if x != "shiken_daichou.txt")
    demé = []
    for ln in r.stdout.splitlines():
        if "一致 ★" in ln:
            demé.append(ln.strip())
        if ln.strip().startswith("★実体無★") or ln.strip().startswith("★相違★") \
           or ln.strip().startswith("★読めぬ行★"):
            demé.append(ln.strip())
    out.append("| %s | %s | `path=a b.txt sha256=%s… bytes=..` | %s | %d |"
               % (d, " ".join("`%s`" % a for a in aru), sha[:12],
                  " / ".join(demé) if demé else "(出目行が取れず)", r.returncode))
out.append("")
out.append("## 條ごとの全文")
for d, moto, sha, gyou, man, r in rows:
    out.append("")
    out.append("### %s" % d)
    out.append("  sha の出所(実物) = %s" % os.path.relpath(moto, BUNDLE))
    out.append("  臺帳の行 = %s" % gyou)
    out.append("  rc = %d" % r.returncode)
    out.append("  --- stdout ---")
    for ln in r.stdout.splitlines():
        out.append("  | %s" % ln)
    out.append("  --- stderr(★stdout と混ぜぬ★) ---")
    if r.stderr.strip():
        for ln in r.stderr.splitlines():
            out.append("  | %s" % ln)
    else:
        out.append("  | (空)")
kaki.kaku(os.path.join(HERE, "20_nise_no_tsuu.txt"), "\n".join(out))
for d, moto, sha, gyou, man, r in rows:
    print("%-16s rc=%d" % (d, r.returncode))
    for ln in r.stdout.splitlines():
        if "一致 ★" in ln or ln.strip().startswith("★"):
            print("    " + ln.strip())
