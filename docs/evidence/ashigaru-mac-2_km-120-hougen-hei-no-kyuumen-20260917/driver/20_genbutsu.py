#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ 九面の ★現物での面積★ ―― 歩き根一本で `path=` 行を悉く仕分け、
   ⑶ と 案己 の候補が ★現に食ひ違ふ行★ を数へる。

★歩き根は一本★: argv[1](既定 = <repo>/docs/evidence)。母數・根・深さ・rc・刻を刷る。
★己の束は別勘定★(memory「Instrument must exclude itself」/「己の系譜は字面で除けぬ」)
  ―― 此の束の下の file は「己束」として分けて数へる。字面ではなく ★path の前綴★ で分ける。

仕分(★排他・網羅★ ―― `path=` を含む行を五つに):
  ①隣接     則②の捕り B == 則①の捕り A(path= と sha256= の間が一語)
  ②a欄呑み  B != A かつ B に '=' を持つ語が在る   ← ★方言乙の形★(因A の当たる所)
  ②b空白名  B != A かつ '=' を持つ語が無い        ← 方言甲 で名に空白
  ③sha無    行に sha256=<64hex> が無い(讀み手は此の行を ★飛ばす★)
  ④sha先    sha256 は在るが path= の後に無い      ← ★方言丙の形★(因B の当たる所)
  (註) '#' で始まる行は讀み手が飛ばす ―― 別に数へ、母數から分ける。

★面積の本体★: 各行に ⑶.paths_of と 案己.paths_of を掛け、
  ⑴候補が食ひ違ふか ⑵食ひ違ふ時、どちらが disk に実在するか を数へる。
  ―― 之が「案己を据ゑたら現物で何行の判定が動くか」の直答である。
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
    m1, m2 = P1.search(line), P2.search(line)
    a = dequote(m1.group(1)) if m1 else None
    b = dequote(m2.group(1)) if m2 else None
    if not SHA.search(line):
        return "③sha無"
    if b is None:
        return "④sha先"
    if a is not None and b == a:
        return "①隣接"
    if any("=" in t for t in b.split()):
        return "②a欄呑み"
    return "②b空白名"


def yomu(path, nm):
    spec = importlib.util.spec_from_file_location("ki_" + nm, path)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod.paths_of


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    t0 = time.time()
    koku = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    san = yomu(os.path.join(BUNDLE, "_ki", "san_c1486ca1.py"), "san")
    ki = yomu(os.path.join(BUNDLE, "_an", "an_ki_km120.py"), "ki")
    bo = yomu(os.path.join(BUNDLE, "_an", "an_bo_km120.py"), "bo")
    kou = yomu(os.path.join(BUNDLE, "_an", "an_kou_km120.py"), "kou")

    files, pycache, irreg, maxdepth = [], 0, 0, 0
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if "__pycache__" in os.path.basename(dirpath):
            pycache += len(filenames)
            dirnames[:] = []
            continue
        maxdepth = max(maxdepth, dirpath[len(walk_root):].count(os.sep) + 1)
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                st = os.lstat(p)
            except OSError:
                irreg += 1
                continue
            if not stat.S_ISREG(st.st_mode):   # ★FIFO は「止」★(memory)
                irreg += 1
                continue
            files.append(p)

    kubun = {k: 0 for k in ("①隣接", "②a欄呑み", "②b空白名", "③sha無", "④sha先")}
    kubun_ono = dict(kubun)
    nfile = nfile_ono = ngyou = ngyou_ono = ncomment = 0
    chigau = []          # 候補が食ひ違ふ行
    yomenu = 0
    for p in files:
        ono = os.path.abspath(p).startswith(os.path.abspath(BUNDLE) + os.sep)
        try:
            s = open(p, encoding="utf-8", errors="strict").read()
        except (UnicodeDecodeError, OSError):
            yomenu += 1
            continue
        hit = False
        for no, line in enumerate(s.split("\n"), 1):
            if not HAS_PATH.search(line):
                continue
            if line.lstrip().startswith("#"):
                ncomment += 1
                continue
            hit = True
            k = classify(line)
            (kubun_ono if ono else kubun)[k] += 1
            if ono:
                ngyou_ono += 1
            else:
                ngyou += 1
            a, b_, c_, d_ = san(line), ki(line), bo(line), kou(line)
            if a != b_:
                base = os.path.dirname(p)
                def aru(ts):
                    return [t for t in ts if os.path.isfile(os.path.join(base, t))]
                chigau.append([os.path.relpath(p, walk_root), no, k,
                               "己束" if ono else "外",
                               repr(a), repr(b_), repr(c_), repr(d_),
                               len(aru(a)), len(aru(b_)), line[:240]])
        if hit:
            if ono:
                nfile_ono += 1
            else:
                nfile += 1

    rc_note = "rc=0(歩き切つた)"
    out = []
    A = out.append
    A("# ㋒ 九面の現物面積  刻=%s" % koku)
    A("歩き根 = %s   ★一本★" % walk_root)
    A("深さ(最大) = %d / 歩いた file = %d / __pycache__ で刈つた file = %d / 非通常file・讀めぬ = %d+%d"
      % (maxdepth, len(files), pycache, irreg, yomenu))
    A("経過 = %.1f 秒 / %s" % (time.time() - t0, rc_note))
    A("")
    A("## 母數(`path=` を含む行。★'#' 起しは讀み手が飛ばす故 別勘定★ = %d 行)" % ncomment)
    A("外(己束を除く)   file=%d  行=%d" % (nfile, ngyou))
    A("己束(此の束の下) file=%d  行=%d  ―― ★己の産物ゆゑ別に数へる★" % (nfile_ono, ngyou_ono))
    A("")
    A("## 仕分(★排他・網羅★)")
    A("\t".join(["区分", "外", "己束", "計", "当たる因"]))
    inn = {"①隣接": "―(正しく讀める)", "②a欄呑み": "★因A(乙の四面)★", "②b空白名": "―(⑶ が正しく讀む)",
           "③sha無": "―(讀み手が飛ばす)", "④sha先": "★因B(丙の五面)★"}
    for k in ("①隣接", "②a欄呑み", "②b空白名", "③sha無", "④sha先"):
        A("\t".join([k, str(kubun[k]), str(kubun_ono[k]), str(kubun[k] + kubun_ono[k]), inn[k]]))
    A("検算 外 %d = %d / 己束 %d = %d"
      % (sum(kubun.values()), ngyou, sum(kubun_ono.values()), ngyou_ono))
    A("")
    A("## ★⑶ と 案己 で候補が食ひ違ふ行★ = %d 行(内 外=%d / 己束=%d)"
      % (len(chigau), sum(1 for r in chigau if r[3] == "外"),
         sum(1 for r in chigau if r[3] == "己束")))
    if chigau:
        A("  ―― 明細は raw/20_chigau.tsv")
    kaku_tsv(os.path.join(BUNDLE, "raw", "20_chigau.tsv"), chigau,
             header=["file(根から)", "行", "区分", "所", "⑶の候補", "案己の候補",
                     "案戊の候補", "案庚の候補", "⑶の実在数", "案己の実在数", "行の逐語(240字まで)"])
    kaku(os.path.join(BUNDLE, "raw", "20_genbutsu.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
