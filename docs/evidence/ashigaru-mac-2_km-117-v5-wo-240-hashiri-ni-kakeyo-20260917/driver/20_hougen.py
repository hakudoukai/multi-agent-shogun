#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑ 「則②を先へ」が★現に壊す行★を repo 全体で数へる器。

★歩き根は一本★: argv[1](既定 = <repo>/docs/evidence)。母數・根・深さ・rc・刻を刷る。

★母數が二つ在る★(どちらも書く ―― 片方だけ書けば嘘になる):
  母數甲(名で引く) = basename に 'manifest' を含み ★.txt で終はる★ file
      ―― 「臺帳らしき物」。名で引く故 ★名の違ふ臺帳を取り落す★(memory「Name-match ≠ table-match」)。
  母數乙(中身で引く) = `path=` 行を持つ file ★悉く★(甲の名を持たぬ物)
      ―― 紙の引用・raw の写しをも含む(memory「現物 counts exclude fixtures & quotes」)。
      ∴ 乙は ★上限★ であり「臺帳の数」ではない。

行の仕分(★排他・網羅★ ―― path= を含む行を五つに分ける):
  ①隣接    則②の捕り B が在り、B == 則①の捕り A(path= と sha256= の間が★一語★)
  ②a食ひ過ぎ B != A かつ B の中に ★'=' を持つ語★ が在る(＝他の欄が挟まる)★←家老の虞★
  ②b空白名  B != A かつ B の中に '=' を持つ語が ★無い★(＝空白を含む名・則②が正しく切る)
  ③sha無し  行に sha256=<64hex> が ★無い★(＝讀み手は此の行を ★数へずに飛ばす★)
  ④sha先    sha256 は在るが path= の後に無い(則②が當らぬ)
  (註) '#' で始まる行は讀み手が飛ばす ―― 別に数へて母數から分ける。

㋑の断: ★②a が 0 本か否か★。0 なら陽性対照を置いて器が数へられる事を示す。
併せて ②a の行に付き ★B が disk に実在するか★ を問ふ ―― 之が「案甲鎖が★現に★壊す本数」。
"""
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))  # 束→evidence→docs→repo根

P1 = re.compile(r'(?:^|\s)path=([^\s"\']+)')
P2 = re.compile(r"(?:^|\s)path=(.+?)[ \t]+sha256=")
SHA = re.compile(r"sha256=([0-9a-f]{64})")
HAS_PATH = re.compile(r"(?:^|\s)path=\S")


def dequote(t):
    t = t.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        t = t[1:-1]
    return t


def classify(line):
    line = line.replace("\r", "")
    m1 = P1.search(line)
    m2 = P2.search(line)
    a = dequote(m1.group(1)) if m1 else None
    b = dequote(m2.group(1)) if m2 else None
    if not SHA.search(line):
        return "③sha無し", a, b
    if b is None:
        return "④sha先", a, b
    if a is not None and b == a:
        return "①隣接", a, b
    if any("=" in t for t in b.split()):
        return "②a食ひ過ぎ", a, b
    return "②b空白名", a, b


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    tag = argv[3] if argv[3:] else "20_hougen"
    t0 = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    files = []
    pycache = irreg = 0
    maxdepth = 0
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if "__pycache__" in os.path.basename(dirpath):
            pycache += len(filenames)
            dirnames[:] = []
            continue
        d = dirpath[len(walk_root):].count(os.sep)
        maxdepth = max(maxdepth, d + 1)
        for fn in filenames:
            p = os.path.join(dirpath, fn)
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

    def zone_of(path, is_kou):
        if path.startswith(MINE):
            return "丙己束"      # ★己の束★(己の raw・己の作つた型見) ―― 数へるが混ぜぬ
        return "甲" if is_kou else "乙のみ"

    zfiles = {"甲": [], "乙のみ": [], "丙己束": []}
    rows = []
    rows2b = []
    tally = {}
    comment = 0
    exists_cache = {}

    def aru(base, p):
        k = (base, p)
        if k not in exists_cache:
            exists_cache[k] = os.path.isfile(os.path.join(base, p)) if p else False
        return exists_cache[k]

    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            irreg += 1
            continue
        if "path=" not in txt:
            continue
        bn = os.path.basename(p)
        is_kou = ("manifest" in bn.lower()) and bn.lower().endswith(".txt")
        hit = False
        per = {}
        for no, raw in enumerate(txt.split("\n"), 1):
            line = raw.strip()
            if not line or not HAS_PATH.search(line):
                continue
            hit = True
            if line.startswith("#"):
                comment += 1
                per["#"] = per.get("#", 0) + 1
                continue
            kind, a, b = classify(line)
            per[kind] = per.get(kind, 0) + 1
            key = (zone_of(p, is_kou), kind)
            tally[key] = tally.get(key, 0) + 1
            if kind == "②b空白名":
                base = os.path.dirname(p)
                rows2b.append([os.path.relpath(p, REPO), no, zone_of(p, is_kou),
                               a or "-", b or "-",
                               "有" if aru(base, b) else "無",
                               "有" if aru(REPO, b) else "無",
                               "有" if aru(base, a) else "無",
                               line[:80].replace("\t", " ")])
            if kind == "②a食ひ過ぎ":
                base = os.path.dirname(p)
                rows.append([os.path.relpath(p, REPO), no,
                             zone_of(p, is_kou),
                             a or "-", b or "-",
                             "有" if aru(base, b) else "無",
                             "有" if aru(REPO, b) else "無",
                             "有" if aru(base, a) else "無",
                             line[:80].replace("\t", " ")])
        if hit:
            zfiles[zone_of(p, is_kou)].append((p, per))

    dt = time.time() - t0
    kinds = ["①隣接", "②a食ひ過ぎ", "②b空白名", "③sha無し", "④sha先"]
    out = [f"# ㋑ 方言の仕分 ―― 刻 {stamp} / 所要 {dt:.1f}s",
           f"# 歩き根(★一本★) = {walk_root}",
           f"#   深さ(最大) = {maxdepth} 段 / 歩いた file = {len(files)} 本",
           f"#   __pycache__ 配下で除いた file = {pycache} 本(★除いたが歩いて居る★)",
           f"#   S_ISREG でない・讀めなんだ = {irreg} 本",
           f"# 母數甲(名 'manifest'*.txt) = {len(zfiles['甲'])} 本"
           f" / 母數乙(path= 行を持つ・甲以外) = {len(zfiles['乙のみ'])} 本"
           f" / 丙己束 = {len(zfiles['丙己束'])} 本",
           "#   ★己の束(km-114)★ は別区『丙己束』に分ける ―― 除くのではなく★別に数へる★",
           "#   ★註★ 丙己束 の本数は★此の器自身の出目★を含む ―― 走らせる度に動く(自己言及)。"
           "甲・乙は之に影響されぬ",
           f"# '#' で始まる path= 行(讀み手が飛ばす) = {comment} 行 ―― 下の母數の★外★",
           "",
           "\t".join(["区分"] + kinds + ["計"])]
    for zone in ("甲", "乙のみ", "丙己束"):
        r = [tally.get((zone, k), 0) for k in kinds]
        out.append("\t".join([zone] + [str(x) for x in r] + [str(sum(r))]))
    allr = [sum(tally.get((z, k), 0) for z in ("甲", "乙のみ")) for k in kinds]
    out.append("\t".join(["甲+乙(己束の外)"] + [str(x) for x in allr] + [str(sum(allr))]))
    out.append("")
    n2a_kou = tally.get(("甲", "②a食ひ過ぎ"), 0)
    n2a_all = allr[1]
    out.append(f"★断★ ②a(則②が食ひ過ぎる行) = 母數甲 {n2a_kou} 行 / 甲+乙 {n2a_all} 行")
    yabureru = sum(1 for r in rows if r[5] == "有" or r[6] == "有")
    out.append(f"★断★ 其の内 ★B(食ひ過ぎた語)が disk に実在★ = {yabureru} 行"
               f" ―― 之が『案甲鎖が★偽の通/偽の赤★を新たに生む』上限")
    naoru = sum(1 for r in rows2b if r[2] != "丙己束" and (r[5] == "有" or r[6] == "有"))
    out.append(f"★断★ ②b(空白を含む名・則②が正しく切る) = {allr[2]} 行"
               f" / 其の内 ★B が disk に実在★ = {naoru} 行"
               f" ―― 之が『則②を先へ』が★現に治す★本数(現形は此処で★偽の赤/偽の通★)")
    out.append("")
    out.append("# 陽性対照 ―― 器が ②a を数へられる事を、己で建てた一行で示す(下の 20_taishou.txt)")
    HD = ["file", "行", "区分", "A(則①の捕り)", "B(則②の捕り)",
          "B実在(臺帳の隣)", "B実在(repo根)", "A実在(臺帳の隣)", "行(頭80字)"]
    kaku(os.path.join(outdir, tag + ".txt"), "\n".join(out))
    kaku_tsv(os.path.join(outdir, tag + "_2a_gyou.tsv"), rows, header=HD)
    kaku_tsv(os.path.join(outdir, tag + "_2b_gyou.tsv"), rows2b, header=HD)
    fl = ["# 母數甲の内訳(名で引いた臺帳 ―― 一本づつ)",
          "\t".join(["file"] + kinds + ["#"])]
    for p, per in sorted(zfiles["甲"]):
        fl.append("\t".join([os.path.relpath(p, REPO)]
                            + [str(per.get(k, 0)) for k in kinds]
                            + [str(per.get("#", 0))]))
    kaku(os.path.join(outdir, tag + "_bosuu_kou_uchiwake.txt"), "\n".join(fl))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
