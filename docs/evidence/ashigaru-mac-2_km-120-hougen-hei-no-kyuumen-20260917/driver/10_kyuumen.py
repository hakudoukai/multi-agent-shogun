#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐㋓ 型見 10区 × 3方言 × 5器 = 150 走。★九面を名で挙げ★、六欄の動きを出す。

★見本は束の外へ建てる★(/private/tmp/…) ―― 札 kinshi「束に空白を含む名の実体を置くな」。
★建てる手順を刷る★(走る毎に建て直す・残り物を引かぬ)。

基準器 = ⑶(c1486ca1) = 今 PR に載つて居る物 = 「何も直さぬ」の案。
出目:
  raw/10_ban.tsv          150 行 + 頭 ―― 全走の rc と六欄
  raw/10_ban_tateta.txt   建てる手順(逐語)
  raw/10_kyuumen.tsv      ★九面の明細★(臺帳行の逐語・候補・期待・現・因)
  raw/10_yoyaku.txt       器 × 判定 の要約 と ★六欄の合計★
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

KI = [
    ("⑶_c1486ca1", os.path.join(BUNDLE, "_ki", "san_c1486ca1.py")),   # ★基準=現状維持★
    ("v5_571f3387", os.path.join(BUNDLE, "_ki", "v5_571f3387.py")),   # 参考(PR#23 merge 前の head)
    ("案戊", os.path.join(BUNDLE, "_an", "an_bo_km120.py")),
    ("案庚", os.path.join(BUNDLE, "_an", "an_kou_km120.py")),
    ("案己", os.path.join(BUNDLE, "_an", "an_ki_km120.py")),
]

PREFIX = "prefix no naka\n"
REAL = "real no naka(kuuhaku mei)\n"
KIYOI = "kiyoi\n"
NA_REAL = "a b.txt"
NA_PRE = "a"


def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()


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
        return "path=%s sha256=%s bytes=%d lines=%d" % (path, want, nbytes, nlines)
    if hougen == "乙":
        return "path=%s bytes=%d lines=%d sha256=%s" % (path, nbytes, nlines, want)
    return "sha256=%s path=%s bytes=%d lines=%d" % (want, path, nbytes, nlines)


def tateru(root, ku, hougen, tejun):
    name, pre, real, shakind, path, _ = ku
    d = os.path.join(root, "%s_%s" % (name, hougen))
    os.makedirs(d)
    tejun.append("mkdir -p %s" % d)
    if pre == "file":
        with open(os.path.join(d, NA_PRE), "w", newline="\n") as fh:
            fh.write(PREFIX)
        tejun.append("printf '%%s' %r > %s/%s   # prefix=file" % (PREFIX, d, NA_PRE))
    elif pre == "dir":
        os.makedirs(os.path.join(d, NA_PRE))
        tejun.append("mkdir %s/%s   # prefix=dir" % (d, NA_PRE))
    else:
        tejun.append("# prefix 無し(建てぬ)")
    if real:
        with open(os.path.join(d, NA_REAL), "w", newline="\n") as fh:
            fh.write(REAL)
        tejun.append("printf '%%s' %r > '%s/%s'   # ★空白を含む実名★" % (REAL, d, NA_REAL))
    if path == "kiyoi.txt":
        with open(os.path.join(d, "kiyoi.txt"), "w", newline="\n") as fh:
            fh.write(KIYOI)
        tejun.append("printf '%%s' %r > %s/kiyoi.txt" % (KIYOI, d))
    want = {"prefix": sha(PREFIX), "real": sha(REAL), "kiyoi": sha(KIYOI)}[shakind]
    body = {"prefix": PREFIX, "real": REAL, "kiyoi": KIYOI}[shakind]
    man = os.path.join(d, "manifest.txt")
    ln = gyou(hougen, path, want, len(body.encode()), 1)
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# km-120 見本(器の外・束の外)\n")
        fh.write(ln + "\n")
    tejun.append("# 臺帳 %s の一行 = %s" % (man, ln))
    return d, man, ln


def hakaru(ki_path, man, base):
    p = subprocess.run([sys.executable, "-B", ki_path, man, base + os.sep],
                       capture_output=True, text=True)
    n = {"一致": 0, "相違": 0, "実体無": 0, "読めぬ行": 0, "曖昧": 0}
    nazashi = "-"
    for lnn in p.stdout.split("\n"):
        if "一致 ★" in lnn:
            t = lnn.replace("★", " ").replace("/", " ").replace("(", " ").split()
            for i, w in enumerate(t):
                if w in n and i + 1 < len(t) and t[i + 1].isdigit():
                    n[w] = int(t[i + 1])
        if "曖昧 " in lnn and "★" not in lnn.split("曖昧")[0][-3:]:
            t = lnn.replace("(", " ").split()
            for i, w in enumerate(t):
                if w == "曖昧" and i + 1 < len(t) and t[i + 1].isdigit():
                    n["曖昧"] = int(t[i + 1])
        s = lnn.strip()
        if nazashi == "-" and s.startswith("★") and "★" in s[1:]:
            k = s[1:].split("★")[0]
            if k in ("相違", "実体無", "読めぬ行", "曖昧"):
                nazashi = k + ":" + s.split("★", 2)[-1].strip()
    return p.returncode, n, nazashi


def yomu(path, nm):
    """器から paths_of を ★取り出して★ 候補を直に見る(rc だけでは因が言へぬ)。"""
    spec = importlib.util.spec_from_file_location("ki_" + nm, path)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod.paths_of


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S")
    koku = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    root = "/private/tmp/km120_ban_%s_%d" % (stamp, os.getpid())
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    tejun = ["# ★建てる手順★(走る毎に建て直す・%s の走りの逐語)" % koku,
             "# 根 = %s  ―― ★束の外★(札 kinshi 順守)" % root,
             "rm -rf %s; mkdir -p %s" % (root, root)]
    kouho = {nm: yomu(p, nm.replace("⑶", "san").replace("案", "an")) for nm, p in KI}
    rows, mei = [], []
    for ku in KU:
        for hougen in HOUGEN:
            d, man, ln = tateru(root, ku, hougen, tejun)
            for kiname, kipath in KI:
                rc, n, nazashi = hakaru(kipath, man, d)
                kekka = ("正" if (ku[5] == "通る") == (rc == 0)
                         else ("★偽の通★" if ku[5] == "鳴る" else "★偽の赤★"))
                rows.append([hougen, ku[0], ku[1], "有" if ku[2] else "無", ku[3], ku[5],
                             kiname, rc, n["一致"], n["相違"], n["実体無"],
                             n["読めぬ行"], n["曖昧"], kekka, nazashi])
                if kiname == "⑶_c1486ca1" and kekka != "正":
                    ka = kouho[kiname](ln)
                    mei.append([hougen + ku[0], hougen, ku[0], ku[1], "有" if ku[2] else "無",
                                ku[3], ku[5], "rc%d" % rc, kekka, nazashi,
                                repr(ka), ln])
    kaku_tsv(os.path.join(BUNDLE, "raw", "10_ban.tsv"), rows,
             header=["方言", "区", "prefix", "実名", "宣sha", "期待", "器", "rc",
                     "一致", "相違", "実体無", "読めぬ行", "曖昧", "判定", "名指し"])
    kaku(os.path.join(BUNDLE, "raw", "10_ban_tateta.txt"), "\n".join(tejun))

    # ―― ㋐ 九面の明細 ＋ 各案が其の面で何を出すか
    mrows = []
    for m in mei:
        men = m[0]
        ato = []
        for kiname, _ in KI:
            r = [x for x in rows if x[0] == m[1] and x[1] == m[2] and x[6] == kiname][0]
            ka = kouho[kiname](m[11])
            ato.append("%s=rc%d/%s/%s" % (kiname, r[7], r[13].replace("★", ""), repr(ka)))
        mrows.append(m + [" | ".join(ato)])
    kaku_tsv(os.path.join(BUNDLE, "raw", "10_kyuumen.tsv"), mrows,
             header=["面", "方言", "区", "prefix", "実名", "宣sha", "期待", "現rc", "判定",
                     "名指し", "⑶の候補", "臺帳行の逐語", "各器の出目"])

    # ―― ㋓ 器 × 判定 と ★六欄の合計★
    yo = ["# ㋐ 型見 %d 走(10区 × 3方言 × %d器)  刻=%s  見本の根=%s" % (len(rows), len(KI), koku, root),
          "# 「★偽の通★」= 鳴るべき行で rc=0 / 「★偽の赤★」= 通るべき行で rc≠0",
          "",
          "## 器 × 判定(母數 30 = 10区 × 3方言)",
          "\t".join(["器", "偽の通", "偽の赤", "正", "母數"])]
    for kiname, _ in KI:
        sub = [x for x in rows if x[6] == kiname]
        t = sum(1 for x in sub if x[13] == "★偽の通★")
        a = sum(1 for x in sub if x[13] == "★偽の赤★")
        yo.append("\t".join([kiname, str(t), str(a), str(len(sub) - t - a), str(len(sub))]))
    yo += ["", "## ★六欄の合計★(30 面を通した rc≠0 の数 と 一致/相違/実体無/読めぬ行/曖昧 の和)",
           "\t".join(["器", "rc≠0の面", "一致", "相違", "実体無", "読めぬ行", "曖昧"])]
    for kiname, _ in KI:
        sub = [x for x in rows if x[6] == kiname]
        yo.append("\t".join([kiname, str(sum(1 for x in sub if x[7] != 0))]
                            + [str(sum(x[i] for x in sub)) for i in (8, 9, 10, 11, 12)]))
    yo += ["", "## 方言別の(偽の通/偽の赤)  ―― 因の所在を分ける",
           "\t".join(["器"] + ["方言" + h for h in HOUGEN])]
    for kiname, _ in KI:
        line = [kiname]
        for h in HOUGEN:
            sub = [x for x in rows if x[6] == kiname and x[0] == h]
            line.append("%d/%d" % (sum(1 for x in sub if x[13] == "★偽の通★"),
                                   sum(1 for x in sub if x[13] == "★偽の赤★")))
        yo.append("\t".join(line))
    yo += ["", "## ★基準 ⑶ が正でない面 = %d 面★(名で挙げる)" % len(mei),
           "\t".join([m[0] + "(" + m[8].replace("★", "") + ")" for m in mei])]
    kaku(os.path.join(BUNDLE, "raw", "10_yoyaku.txt"), "\n".join(yo))
    print("\n".join(yo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
