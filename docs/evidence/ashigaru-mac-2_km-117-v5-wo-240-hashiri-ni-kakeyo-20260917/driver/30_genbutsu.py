#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑-2/㋒-2 ★現物の臺帳★で v5 と 案甲鎖 の出目が違ふ行を数へる器。

★理屈で仕分けぬ ―― 二つの paths_of を★現に呼んで★候補列を突き合はせる。★
(regex で「此の行は②に當る筈」と読むのは推測である。器に問へば推測が要らぬ。)

歩き根は argv[1](既定 = <repo>/docs/evidence) ―― ★一本★。深さ無制限。
仕分(排他・網羅 ―― ★讀み手 main が実際に辿る道★で分ける):
  ㋐飛ばし  sha256=<64hex> が行に無い ―― ★main が paths_of を呼ぶ前に continue する★
            (∴ 此処に何行在つても v5 と案甲鎖 の差には★成り得ぬ★)
  ㋑m2當り  paths_of へ入り、v5 の則② (path=(.+?)[ \t]+sha256=) が當る
            ―― v5 は ★唯一の候補★ を返す(案甲鎖 と同じ構へ)
  ㋒m2外れ  paths_of へ入るが 則② が當らぬ ―― ★v5 は列べる形＋第二の for へ落ちる★
各行に付き cands_v5 / cands_鎖 / cands_列 / cands_v4 を取り、
  ・候補列が ★一字でも違ふ行★
  ・候補列は違ふが ★昇る物(最初に disk に在る候補)が同じ行★
  ・★昇る物まで違ふ行★(= 出目が現に変る行)
の三段で数へる。基点は ⑴臺帳の隣(dirname) ⑵repo 根 の二つ(讀み手の既定に倣ふ)。

出 = raw/30_genbutsu.txt / raw/30_chigau_gyou.tsv / raw/30_daini_for.tsv
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

KI = [
    ("v5", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),
    ("鎖", os.path.join(BUNDLE, "_an", "an_kou_kusari.py")),
    ("列", os.path.join(BUNDLE, "_an", "an_kou_retsu.py")),
    ("v4", os.path.join(SEED, "v4_naoshita.py")),
]


def load(name, path):
    spec = importlib.util.spec_from_file_location("ki_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.paths_of


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    t0 = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    fn = {k: load(k, p) for k, p in KI}
    # ★陽性対照★ ―― 器が現に別物を返す事を、己で建てた一行で先に示す
    taishou = [
        ("②が當る行(空白名)", "path=a b.txt sha256=" + "0" * 64 + " bytes=1 lines=1"),
        ("②が當らぬ行(sha先)", "sha256=" + "0" * 64 + " path=a b.txt bytes=1 lines=1"),
        ("path= 無し・'/'語有り", "sha256=" + "0" * 64 + " docs/x/y.txt"),
    ]
    trows = [[k, ln[:60]] + ["|".join(fn[g](ln)) or "(空)" for g, _ in KI] for k, ln in taishou]

    files = []
    pycache = irreg = 0
    maxdepth = 0
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if os.path.basename(dirpath) == "__pycache__":
            pycache += len(filenames)
            dirnames[:] = []
            continue
        maxdepth = max(maxdepth, dirpath[len(walk_root):].count(os.sep) + 1)
        for f in filenames:
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

    MINE = BUNDLE + os.sep
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

    n = {"㋐飛ばし": 0, "㋑m2當り": 0, "㋒m2外れ": 0}
    nz = {}
    comment = 0
    chigau, daini = [], []
    n_kouho_chigau = n_noboru_chigau = 0
    n_daini_kasegu = 0          # 第二の for が★候補を現に足した★行
    n_daini_noboru = 0          # 其の足した候補が★現に昇つた★行
    nfile_hit = 0
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            irreg += 1
            continue
        if "sha256=" not in txt and "path=" not in txt:
            continue
        zone = "丙己束" if p.startswith(MINE) else "甲乙(己束の外)"
        base = os.path.dirname(p)
        bases = [base, REPO]
        hit = False
        for no, raw in enumerate(txt.split("\n"), 1):
            line = raw.strip()
            if not line:
                continue
            if not HAS_PATH.search(line) and not SHA.search(line):
                continue
            hit = True
            if line.startswith("#"):
                comment += 1
                continue
            if not SHA.search(line):
                n["㋐飛ばし"] += 1
                nz[(zone, "㋐飛ばし")] = nz.get((zone, "㋐飛ばし"), 0) + 1
                continue
            kind = "㋑m2當り" if M2.search(line.replace("\r", "")) else "㋒m2外れ"
            n[kind] += 1
            nz[(zone, kind)] = nz.get((zone, kind), 0) + 1
            c = {g: fn[g](line) for g, _ in KI}
            if c["v5"] != c["鎖"]:
                n_kouho_chigau += 1
                a, b = noboru(bases, c["v5"]), noboru(bases, c["鎖"])
                if a != b:
                    n_noboru_chigau += 1
                chigau.append([os.path.relpath(p, REPO), no, zone, kind,
                               "|".join(c["v5"])[:70], "|".join(c["鎖"])[:70],
                               str(a), str(b), "★昇る物も違ふ★" if a != b else "昇る物は同",
                               line[:70].replace("\t", " ")])
            if kind == "㋒m2外れ":
                # ★第二の for★ が足した分を測る ―― 列(第二の for を持たぬ)との差
                add = [x for x in c["v5"] if x not in c["列"]]
                if add:
                    n_daini_kasegu += 1
                    nb = noboru(bases, c["v5"])
                    got = nb in add
                    if got:
                        n_daini_noboru += 1
                    daini.append([os.path.relpath(p, REPO), no, zone,
                                  "|".join(add)[:70], str(nb),
                                  "★足した候補が昇つた★" if got else "昇らず",
                                  line[:70].replace("\t", " ")])
        if hit:
            nfile_hit += 1

    dt = time.time() - t0
    o = [f"# ㋑-2/㋒-2 現物の臺帳で ★v5 と案甲鎖 の出目が違ふ行★ ―― 刻 {stamp} / 所要 {dt:.1f}s",
         f"# 歩き根(★一本★) = {walk_root}",
         f"#   深さ(最大) = {maxdepth} 段 / 歩いた file = {len(files)} 本 / "
         f"path= か sha256= を持つ file = {nfile_hit} 本",
         f"#   __pycache__ 配下で除いた = {pycache} 本 / S_ISREG でない・讀めなんだ = {irreg} 本",
         f"# '#' で始まる行(讀み手が飛ばす) = {comment} 行 ―― 下の母數の★外★",
         "",
         "# ★陽性対照★ ―― 器が現に別の候補列を返す事を、己で建てた三行で示す",
         "#   (之が無ければ『差 0 行』は『器が差を見られぬ』の意かも知れぬ)",
         "\t".join(["対照", "行(頭60字)"] + [g for g, _ in KI])]
    for r in trows:
        o.append("\t".join(str(x) for x in r))
    o += ["",
          "# 讀み手 main が辿る道での仕分(★排他・網羅★)",
          "\t".join(["区分", "行数", "意味"]),
          "\t".join(["㋐飛ばし", str(n["㋐飛ばし"]),
                     "sha256=<64hex> が無い ―― ★paths_of を呼ぶ前に continue★・差に成り得ぬ"]),
          "\t".join(["㋑m2當り", str(n["㋑m2當り"]),
                     "v5 は ★唯一の候補★ を返す(案甲鎖 と同じ構へ)"]),
          "\t".join(["㋒m2外れ", str(n["㋒m2外れ"]),
                     "★v5 が列べる形＋第二の for へ落ちる行★"]),
          "\t".join(["計", str(sum(n.values())), "―"]),
          "",
          "# 区分 × 区域(己の束を別に数へる ―― 除くのではない)",
          "\t".join(["区域", "㋐飛ばし", "㋑m2當り", "㋒m2外れ", "計"])]
    for z in ("甲乙(己束の外)", "丙己束"):
        r = [nz.get((z, k), 0) for k in ("㋐飛ばし", "㋑m2當り", "㋒m2外れ")]
        o.append("\t".join([z] + [str(x) for x in r] + [str(sum(r))]))
    o += ["",
          f"★断㋑★ v5 と案甲鎖 で ★候補列が違ふ行★ = {n_kouho_chigau} 行"
          f"(母數 {n['㋑m2當り'] + n['㋒m2外れ']} = paths_of へ入つた行)",
          f"★断㋑★ 其の内 ★昇る物(最初に disk に在る候補)まで違ふ行★ = {n_noboru_chigau} 行"
          " ―― 之が『出目が現に変る』上限",
          f"★断㋒★ ★第二の for が候補を現に足した行★ = {n_daini_kasegu} 行"
          f"(母數 {n['㋒m2外れ']} = m2 が外れた行)",
          f"★断㋒★ 其の内 ★足した候補が現に昇つた行★ = {n_daini_noboru} 行",
          "",
          "# ★此の数が言はぬ事★",
          "#  ・『0 行』は ★此の歩き根・此の刻★ の話である。別の根・別の刻では動く。",
          "#  ・㋐飛ばし の行数は ★v5 と鎖 の差とは無縁★ ―― main が paths_of を呼ばぬ故。",
          "#  ・候補列が同じでも ★基点が違へば昇る物は違ふ★ ―― 上は二基点(臺帳の隣・repo根)のみ。",
          "#  ・現物に無い形は測れて居らぬ ―― 型見の 10 区(raw/11_hougen_betsu.txt)が其の受け皿。"]
    HD = ["file", "行", "区域", "区分", "v5 の候補", "鎖 の候補",
          "v5 で昇る物", "鎖 で昇る物", "判", "行(頭70字)"]
    kaku(os.path.join(outdir, "30_genbutsu.txt"), "\n".join(o))
    kaku_tsv(os.path.join(outdir, "30_chigau_gyou.tsv"), chigau, header=HD)
    kaku_tsv(os.path.join(outdir, "30_daini_for.tsv"), daini,
             header=["file", "行", "区域", "第二の for が足した候補", "昇る物", "判", "行(頭70字)"])
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
