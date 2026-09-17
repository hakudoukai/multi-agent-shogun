#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐ fail-open の面積を測る器 ―― 見本を建て、八つの器へ通し、rc の表を出す。

★見本は束の外へ建てる★(/private/tmp/…) ―― 札 kinshi「束に空白を含む名の実体を置くな」。
★建てる手順で固定再現を担保する★(走る毎に建て直す・残り物を引かぬ)。

区(見本)の十:
  甲   prefix=file / 実名=無 / 宣sha=sha(prefix)   期待=鳴る  ←★家老が自訴した面★
  乙   prefix=file / 実名=無 / 宣sha=sha(実名)     期待=鳴る
  丙   prefix=無   / 実名=無 / 宣sha=sha(実名)     期待=鳴る
  丁   prefix=dir  / 実名=無 / 宣sha=sha(実名)     期待=鳴る
  丁二 prefix=dir  / 実名=有 / 宣sha=sha(実名)     期待=通る
  戊   prefix=file / 実名=有 / 宣sha=sha(実名)     期待=通る  ←★空白名の正しい行★
  戊二 prefix=無   / 実名=有 / 宣sha=sha(実名)     期待=通る
  己   prefix=file / 実名=有 / 宣sha=sha(prefix)   期待=鳴る
  庚   空白無し・真に不在                          期待=鳴る  ←★陽性対照(㋓)★
  辛   空白無し・正しい行                          期待=通る  ←★負対照★

方言の三:
  甲 path=<p> sha256=<64> bytes= lines=   (★隣接★・本形)
  乙 path=<p> bytes= lines= sha256=<64>   (★間に他の欄が挟まる★)
  丙 sha256=<64> path=<p> bytes= lines=   (★sha が path より前★)

出目: raw/10_menseki.tsv(全 360 行 = 10区 × 3方言 × 12器) / raw/10_ban_tateta.txt(建てる手順) /
      raw/10_menseki_yoyaku.txt(器 × 区 の rc 表)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

SEED = os.path.join(BUNDLE, "..",
                    "karo-mac_km-113-kuuhaku-wo-fukumu-na-ga-arawasenu-kizu-20260917",
                    "_ver")
AN = os.path.join(BUNDLE, "_an")

KI = [
    ("v1_127行", os.path.join(SEED, "v1_127gyou.py")),
    ("v2_originmain", os.path.join(SEED, "v2_originmain.py")),
    ("v4_家老の直し", os.path.join(SEED, "v4_naoshita.py")),
    ("案甲鎖", os.path.join(AN, "an_kou_kusari.py")),
    ("案甲列", os.path.join(AN, "an_kou_retsu.py")),
    ("案乙", os.path.join(AN, "an_otsu.py")),
    ("案丙", os.path.join(AN, "an_hei.py")),
    ("案丁", os.path.join(AN, "an_tei.py")),
    ("v5_PR23", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),   # ★九本目★ PR#23 head
    ("v5_第二無", os.path.join(AN, "v5_daini_nashi.py")),        # ★十本目★ v5 − 第二の for
    ("案甲鎖_第二無", os.path.join(AN, "an_kusari_daini_nashi.py")),  # ★十一本目★ 鎖 − 第二の for
    ("案戊", os.path.join(AN, "an_bo.py")),                       # ★十二本目★ v5 −第二の for ＋②の欄剥ぎ
]

PREFIX = "prefix no naka\n"          # file `a` の中身
REAL = "real no naka(kuuhaku mei)\n"  # file `a b.txt` の中身
KIYOI = "kiyoi\n"                     # 空白無しの正しい file

NA_REAL = "a b.txt"
NA_PRE = "a"


def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()


# 区 = (名, prefix状態, 実名有無, 宣sha, path, 期待)
KU = [
    ("甲", "file", False, "prefix", NA_REAL, "鳴る"),
    ("乙", "file", False, "real", NA_REAL, "鳴る"),
    ("丙", "無", False, "real", NA_REAL, "鳴る"),
    ("丁", "dir", False, "real", NA_REAL, "鳴る"),
    ("丁二", "dir", True, "real", NA_REAL, "通る"),
    ("戊", "file", True, "real", NA_REAL, "通る"),
    ("戊二", "無", True, "real", NA_REAL, "通る"),
    ("己", "file", True, "prefix", NA_REAL, "鳴る"),
    ("庚", "無", False, "real", "nai.txt", "鳴る"),
    ("辛", "無", False, "kiyoi", "kiyoi.txt", "通る"),
]

HOUGEN = ["甲", "乙", "丙"]


def gyou(hougen, path, want, nbytes, nlines):
    if hougen == "甲":
        return f"path={path} sha256={want} bytes={nbytes} lines={nlines}"
    if hougen == "乙":
        return f"path={path} bytes={nbytes} lines={nlines} sha256={want}"
    return f"sha256={want} path={path} bytes={nbytes} lines={nlines}"


def tateru(root, ku, hougen, tejun):
    name, pre, real, shakind, path, _ = ku
    d = os.path.join(root, f"{name}_{hougen}")
    os.makedirs(d)
    tejun.append(f"mkdir -p {d}")
    if pre == "file":
        with open(os.path.join(d, NA_PRE), "w", newline="\n") as fh:
            fh.write(PREFIX)
        tejun.append(f"printf '%s' {PREFIX!r} > {d}/{NA_PRE}   # prefix=file")
    elif pre == "dir":
        os.makedirs(os.path.join(d, NA_PRE))
        tejun.append(f"mkdir {d}/{NA_PRE}   # prefix=dir")
    else:
        tejun.append(f"# prefix 無し(建てぬ)")
    if real:
        with open(os.path.join(d, NA_REAL), "w", newline="\n") as fh:
            fh.write(REAL)
        tejun.append(f"printf '%s' {REAL!r} > '{d}/{NA_REAL}'   # ★空白を含む実名★")
    if path == "kiyoi.txt":
        with open(os.path.join(d, "kiyoi.txt"), "w", newline="\n") as fh:
            fh.write(KIYOI)
        tejun.append(f"printf '%s' {KIYOI!r} > {d}/kiyoi.txt")
    want = {"prefix": sha(PREFIX), "real": sha(REAL), "kiyoi": sha(KIYOI)}[shakind]
    body = {"prefix": PREFIX, "real": REAL, "kiyoi": KIYOI}[shakind]
    man = os.path.join(d, "manifest.txt")
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# km-114 見本(器の外・束の外)\n")
        fh.write(gyou(hougen, path, want, len(body.encode()), 1) + "\n")
    tejun.append(f"# 臺帳 {man} の一行 = {gyou(hougen, path, want[:8] + '…', len(body.encode()), 1)}")
    return d, man


def hakaru(ki_path, man, base):
    p = subprocess.run([sys.executable, "-B", ki_path, man, base + os.sep],
                       capture_output=True, text=True)
    n = {"一致": 0, "相違": 0, "実体無": 0, "読めぬ行": 0, "曖昧": 0}
    nazashi = "-"
    for ln in p.stdout.split("\n"):
        if "一致 ★" in ln:
            t = ln.replace("★", " ").replace("/", " ").replace("(", " ").split()
            for i, w in enumerate(t):
                if w in n and i + 1 < len(t) and t[i + 1].isdigit():
                    n[w] = int(t[i + 1])
        if "曖昧 " in ln and "★" not in ln.split("曖昧")[0][-3:]:
            t = ln.replace("(", " ").split()
            for i, w in enumerate(t):
                if w == "曖昧" and i + 1 < len(t) and t[i + 1].isdigit():
                    n["曖昧"] = int(t[i + 1])
        s = ln.strip()
        if nazashi == "-" and s.startswith("★") and "★" in s[1:]:
            k = s[1:].split("★")[0]
            if k in ("相違", "実体無", "読めぬ行", "曖昧"):
                nazashi = k + ":" + s.split("★", 2)[-1].strip()
    return p.returncode, n, nazashi, p.stdout, p.stderr


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    root = f"/private/tmp/km114_ban_{stamp}_{os.getpid()}"
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    tejun = [f"# ★建てる手順★(走る毎に建て直す・{stamp} の走りの逐語)",
             f"# 根 = {root}  ―― ★束の外★(札 kinshi 順守)",
             f"rm -rf {root}; mkdir -p {root}"]
    rows = []
    for ku in KU:
        for hougen in HOUGEN:
            d, man = tateru(root, ku, hougen, tejun)
            for kiname, kipath in KI:
                rc, n, nazashi, out, err = hakaru(kipath, man, d)
                kekka = ("正" if (ku[5] == "通る") == (rc == 0)
                         else ("★偽の通★" if ku[5] == "鳴る" else "★偽の赤★"))
                rows.append([hougen, ku[0], ku[1], "有" if ku[2] else "無",
                             ku[3], ku[5], kiname, rc,
                             n["一致"], n["相違"], n["実体無"], n["読めぬ行"],
                             n["曖昧"], kekka, nazashi])
    kaku_tsv(os.path.join(BUNDLE, "raw", "10_menseki.tsv"), rows,
             header=["方言", "区", "prefix", "実名", "宣sha", "期待", "器", "rc",
                     "一致", "相違", "実体無", "読めぬ行", "曖昧", "判定", "名指し"])
    kaku(os.path.join(BUNDLE, "raw", "10_ban_tateta.txt"), "\n".join(tejun))

    # 要約 ―― 器 × 区 の判定表(方言甲のみ / 三方言の合算は別表)
    ki_names = [k for k, _ in KI]
    yo = ["# ㋐ 器 × 区 の判定(方言甲=隣接・本形)",
          "# 「★偽の通★」= 鳴るべき行で rc=0 / 「★偽の赤★」= 通るべき行で rc≠0",
          "\t".join(["区", "期待"] + ki_names)]
    for ku in KU:
        line = [ku[0], ku[5]]
        for kiname in ki_names:
            r = [x for x in rows if x[0] == "甲" and x[1] == ku[0] and x[6] == kiname][0]
            line.append(f"rc{r[7]}/{r[13]}")
        yo.append("\t".join(line))
    yo.append("")
    yo.append("# ㋐' 三方言 合算 ―― 器毎の ★偽の通★ / ★偽の赤★ の本数(母數 30=10区×3方言)")
    yo.append("\t".join(["器", "偽の通", "偽の赤", "正", "母數"]))
    for kiname in ki_names:
        sub = [x for x in rows if x[6] == kiname]
        t = sum(1 for x in sub if x[13] == "★偽の通★")
        a = sum(1 for x in sub if x[13] == "★偽の赤★")
        yo.append("\t".join([kiname, str(t), str(a), str(len(sub) - t - a), str(len(sub))]))
    kaku(os.path.join(BUNDLE, "raw", "10_menseki_yoyaku.txt"), "\n".join(yo))
    print("\n".join(yo))
    print(f"\n見本の根 = {root}(★束の外★・残す ―― 次走で別名が建つ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
