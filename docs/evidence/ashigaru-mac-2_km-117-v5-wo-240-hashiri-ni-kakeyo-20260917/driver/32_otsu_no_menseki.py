#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★区辛・方言乙 の疵★(v5 が ★清い行★ で鳴る)を現物で測る器 ―― ㋓ の裏。

型見で出た事: 区辛(空白無し・正しい行・★負対照★)を 方言乙
  `path=kiyoi.txt bytes=6 lines=1 sha256=<64>`
の形で書くと、v5・案甲鎖・案乙 は ★rc1(偽の赤)★ に成る。v4・案甲列 は rc0(正)。
因: 則②の非貪欲は `path=` から ★次の sha256= まで★ を呑む ∴ 候補が
  'kiyoi.txt bytes=6 lines=1' の一本に成り、鎖/早期 return は其処で止まる。
列べる形は ① が 'kiyoi.txt' も出す故に助かる。

∴ 問ふべきは「★現物の臺帳に 方言乙 が何行在るか★」である。
本器は 臺帳甲(名 manifest*.txt)の各行に付き
  ・則② の捕り物に ★空白が混じるか★(= 他の欄を呑んだ印)
  ・v5 が昇らせる物 / v4 が昇らせる物 が違ふか
  ・★v5 では昇らぬが v4 では昇る行★(= v5 が新たに作る 偽の赤 の上限)
を数へる。基点は ⑴臺帳の隣 ⑵repo 根。

出 = raw/32_otsu.txt / raw/32_otsu_gyou.tsv
"""
import importlib.util
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
SEED = os.path.join(BUNDLE, "..",
                    "karo-mac_km-113-kuuhaku-wo-fukumu-na-ga-arawasenu-kizu-20260917",
                    "_ver")
SHA = re.compile(r"sha256=([0-9a-f]{64})")
M2 = re.compile(r"(?:^|\s)path=(.+?)[ \t]+sha256=")
HAS_PATH = re.compile(r"(?:^|\s)path=\S")

KI = [("v5", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),
      ("鎖", os.path.join(BUNDLE, "_an", "an_kou_kusari.py")),
      ("v4", os.path.join(SEED, "v4_naoshita.py")),
      ("列", os.path.join(BUNDLE, "_an", "an_kou_retsu.py"))]


def load(name, path):
    spec = importlib.util.spec_from_file_location("ki32_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.paths_of


def mieru(s, cap=80):
    s = str(s).replace("\t", "␉").replace("\r", "␍").replace("\n", "␊")
    return s if len(s) <= cap else s[:cap] + "…"


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.join(BUNDLE, "raw")
    t0 = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    fn = {k: load(k, p) for k, p in KI}

    # ★陽性対照★ 区辛・方言乙 の一行を其の儘入れる(器が現に違ふ答を出す事を先に示す)
    ctl = "path=kiyoi.txt bytes=6 lines=1 sha256=" + "0" * 64
    ctl_rows = [["区辛方言乙(型見と同じ行)", mieru(ctl, 60)] +
                [mieru("|".join(fn[g](ctl))) for g, _ in KI]]

    files = []
    pycache = irreg = 0
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if os.path.basename(dirpath) == "__pycache__":
            pycache += len(filenames)
            dirnames[:] = []
            continue
        for f in filenames:
            b = f.lower()
            if not ("manifest" in b and b.endswith(".txt")):
                continue
            p = os.path.join(dirpath, f)
            try:
                st = os.lstat(p)
            except OSError:
                irreg += 1
                continue
            if not stat.S_ISREG(st.st_mode):
                irreg += 1
                continue
            files.append(p)

    cache = {}

    def aru(b, p):
        k = (b, p)
        if k not in cache:
            try:
                cache[k] = os.path.isfile(os.path.join(b, p)) if p else False
            except (OSError, ValueError):
                cache[k] = False
        return cache[k]

    def noboru(bases, cands):
        for p in cands:
            for b in bases:
                if aru(b, p):
                    return p
        return None

    n_line = n_m2 = n_m2_kuuhaku = 0
    n_v5_naki = n_v4_ari = n_gyakuten = 0
    rows = []
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            irreg += 1
            continue
        bases = [os.path.dirname(p), REPO]
        for no, raw in enumerate(txt.split("\n"), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if not HAS_PATH.search(line) and not SHA.search(line):
                continue
            if not SHA.search(line):
                continue
            n_line += 1
            m = M2.search(line.replace("\r", ""))
            if not m:
                continue
            n_m2 += 1
            tore = m.group(1)
            kuuhaku = bool(re.search(r"\s", tore.strip()))
            if kuuhaku:
                n_m2_kuuhaku += 1
            a = noboru(bases, fn["v5"](line))
            b = noboru(bases, fn["v4"](line))
            if a is None:
                n_v5_naki += 1
            if b is not None:
                n_v4_ari += 1
            if a is None and b is not None:
                n_gyakuten += 1
                rows.append([mieru(os.path.relpath(p, REPO), 120), no,
                             "★捕り物に空白★" if kuuhaku else "空白無し",
                             mieru(tore), mieru(str(b)), mieru(line)])

    dt = time.time() - t0
    o = [f"# ㋓裏 ★方言乙 の面積★ ―― v5 が ★清い行★ で鳴るか / 刻 {stamp} / 所要 {dt:.1f}s",
         f"# 歩き根(★一本★) = {walk_root} ―― ★名が manifest を含み .txt で終る file のみ★",
         f"#   其の file = {len(files)} 本 / 讀めなんだ・S_ISREG でない = {irreg} 本 / "
         f"__pycache__ で除いた = {pycache} 本",
         "",
         "# ★陽性対照★ 型見 区辛方言乙 の一行を其の儘器へ入れる",
         "\t".join(["対照", "行(頭60字)"] + [g for g, _ in KI])]
    for r in ctl_rows:
        o.append("\t".join(str(x) for x in r))
    o += ["",
          "\t".join(["量", "行数", "意味"]),
          "\t".join(["sha256 有りの行", str(n_line), "★paths_of へ入る行★(母數)"]),
          "\t".join(["則②が當る行", str(n_m2), "v5 は此処で ★唯一の候補★ を返す"]),
          "\t".join(["其の捕り物に空白が混じる行", str(n_m2_kuuhaku),
                     "★方言乙 の印★(他の欄を呑んだ) ―― 型見 区辛乙 と同じ形"]),
          "\t".join(["v5 で昇る物が無い行", str(n_v5_naki), "実体無 ―― 鳴る側"]),
          "\t".join(["v4 で昇る物が有る行", str(n_v4_ari), "―"]),
          "\t".join(["★v5 で昇らず v4 で昇る行★", str(n_gyakuten),
                     "★v5 が新たに作る 偽の赤 の上限★(昇つた後の sha 照合は別)"]),
          "",
          "# ★此の数が言はぬ事★",
          "#  ・『昇らぬ』は ★鳴る★ を意味するが、★sha が合はぬ★ とは別の理由である。",
          "#  ・『v4 で昇る』は ★v4 が正しい★ を意味せぬ ―― v4 は型見で 偽の通 6 本を出す。",
          "#  ・区域は ★名★ で分けた(manifest*.txt)。名が違ふ臺帳は此の母數に入つて居らぬ。",
          "#  ・数は此の歩き根・此の刻の物である。",
          "#  ・★0 行でも『方言乙 が無害』とは言へぬ★ ―― 今の束に其の形が無いだけである"
          "(型見 区辛乙 では現に鳴る)。"]
    kaku(os.path.join(outdir, "32_otsu.txt"), "\n".join(o))
    kaku_tsv(os.path.join(outdir, "32_otsu_gyou.tsv"), rows,
             header=["file", "行", "則②の捕り物", "捕り物(逐語)", "v4 で昇る物", "行(頭80字)"])
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
