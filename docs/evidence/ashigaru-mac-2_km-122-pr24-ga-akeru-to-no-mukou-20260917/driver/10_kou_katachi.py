#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐-甲 ★形を知る器★ ―― 既知の秘匿形(11族)を歩き根の下で数へる。

★値は決して刷らぬ★ ―― 出目は「族・件数・path・当つた字数(伏せ)」のみ。
★陽性対照は此の file の字面に完全形を置かぬ★ ―― 部品から組み立てる。
  (置けば ①本器自身が歩き根に在る時 己を鳴らす ②紙が秘匿形を運ぶ)
★対照を通さぬ族は 0 と書かず「測れぬ」と書く★。

歩き根 = argv[1] 一本。出 = raw/10_kou.txt / raw/10_kou_atari.tsv / raw/10_kou_taishou.tsv
"""
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv, esc, fuse  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))

# ―― 族 = (名, 正規表現, 捕へる群番号) ―――――――――――――――――――――――
ZOKU = [
    ("甲1_aws_鍵id",  re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA)[0-9A-Z]{16}\b"), 0),
    ("甲2_pem秘鍵",   re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----"), 0),
    ("甲3_anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"), 0),
    ("甲4_sk系",      re.compile(r"\bsk-(?!ant-)[A-Za-z0-9]{20,}"), 0),
    ("甲5_github",    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{22,}"), 0),
    ("甲6_slack",     re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"), 0),
    ("甲7_google",    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"), 0),
    ("甲8_jwt",       re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), 0),
    ("甲9_url内資格", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^/\s:@]+:[^/\s@]{3,}@"), 0),
    ("甲10_代入",     re.compile(r"(?i)\b(?:pass(?:word|wd)?|secret|token|api[_\-]?key|access[_\-]?key|client[_\-]?secret|service[_\-]?role)\b[ \t]*[:=][ \t]*[\"']?([^\s\"',;#]{8,})"), 1),
    ("甲11_基本認証", re.compile(r"(?i)\bauthorization[ \t]*[:=][ \t]*[\"']?(?:bearer|basic)[ \t]+([A-Za-z0-9+/=_\-\.]{12,})"), 1),
]

# ―― 置き字(値でない物)の印 ―― 当つても「現物の秘匿」とは数へぬ族分け ――
OKIJI = re.compile(r"(?i)^(?:\*+|x{3,}|<[^>]*>|\{\{.*|\$\{?[A-Z_]+\}?|your[_\-]?|dummy|example|sample|changeme|redacted|placeholder|test[_\-]?|fake|\.\.\.|伏)")

# ―― ★第三の札「式」★ ――
# 実測(本弾 21:51): 甲10 が拾つた 43 件を人の目で開いたら、悉く★値でなく式★であつた。
#   例 = os.environ.get("…") / self.get_token() / process.env.X / config["…"]
#   ∴ 「置字か値か」の二分は★偽の値★を産む。二分を宣する前に測れ、の条に己が背いた。
SHIKI = re.compile(r"""(?x)^(?:
      os\.environ | os\.getenv | getenv | process\.env | System\.getenv
    | self\.[A-Za-z_] | this\.[A-Za-z_] | cls\.[A-Za-z_]
    | [A-Za-z_][A-Za-z0-9_]*\s*\(
    | [A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\s*[(\[]
    | [A-Za-z_][A-Za-z0-9_]*\[
    )""")


def yomu(path):
    """★S_ISREG のみ開く★(FIFO は「止」に成る)。二進は replace で読む ―― 読まぬのではない。"""
    with open(path, "rb") as fh:
        b = fh.read()
    nishin = b"\x00" in b[:8192]
    return b.decode("utf-8", "replace"), nishin, len(b)


def sagasu(text):
    """★対照も現物も、此の一つの関数を通す★(測る路に対照を乗せる)。"""
    hits = []
    for name, rx, gi in ZOKU:
        for m in rx.finditer(text):
            v = m.group(gi) if gi else m.group(0)
            hits.append((name, v))
    return hits


# ★符丁★ ―― 己の対照を現物から見分ける為の字。
# 実測(本弾 21:47): 部品連結は compiler が★定数畳み★して .pyc に完全形を残し、
#   其の .pyc が己の束に落ちて 9/11 の種が「現物」として鳴つた(種漏れ=11)。
#   ∴ 駆動は python3 -B で走らせ、.pyc を産まぬ事。
# 実測(同刻): 残る 2 件は★他席 mac-1 の km-112 束★に同じ字が在つた
#   (両者が同じ教科書的な例値を選んだ) ∴ 符丁で己の種を一意にする。
FUCHOU = "KM122ZQ"


def taishou_wo_tateru():
    """★陽性対照 ―― 部品から組み立て、符丁で一意にする★"""
    A = "A" * 0  # 見た目合せ
    U = "ABCDEFGHIJKLMNOP"          # 16字・大文字のみ
    L = "abcdefghijklmnopqrstuvwxyz0123456789"
    parts = [
        ("甲1_aws_鍵id",  "AK" + "IA" + "KM122ZQABCDEFGHI"),
        ("甲2_pem秘鍵",   "-----" + "BEGIN " + "RSA " + "PRIVATE " + "KEY" + "-----" + " " + FUCHOU),
        ("甲3_anthropic", "sk" + "-" + "ant" + "-" + FUCHOU + L[:20]),
        ("甲4_sk系",      "sk" + "-" + FUCHOU + "Zz09" * 5),
        ("甲5_github",    "gh" + "p_" + FUCHOU + "Aa0" * 9 + "Aa"),
        ("甲6_slack",     "xo" + "xb" + "-" + FUCHOU + "-" + "1234567890"),
        ("甲7_google",    "AI" + "za" + FUCHOU + ("Bb1" * 9) + "c"),
        ("甲8_jwt",       "ey" + "J" + FUCHOU + "abcde" + "." + "ey" + "J" + FUCHOU + "klmno" + "." + FUCHOU + "uvw"),
        ("甲9_url内資格", "postgres" + "://" + "riyousha" + ":" + FUCHOU + "@" + "host/db"),
        ("甲10_代入",     "pass" + "word" + ": " + FUCHOU + "naga12"),
        ("甲11_基本認証", "Author" + "ization" + ": " + "Bearer " + FUCHOU + "Aa0Bb1Cc"),
    ]
    return parts + [("", A)]


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    os.makedirs(outdir, exist_ok=True)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # ―― ① 陽性対照(★現物を測る前に★通す) ――
    trows, naranu = [], []
    for name, s in taishou_wo_tateru():
        if not name:
            continue
        got = [z for z, v in sagasu(s)]
        ok = name in got
        trows.append((name, "鳴つた" if ok else "★鳴らぬ★", fuse(s), ";".join(sorted(set(got))) or "(無)"))
        if not ok:
            naranu.append(name)

    # ―― ② 陰性対照: 対照の字が歩き根の下に居らぬ事 ――
    tane = set(s for n, s in taishou_wo_tateru() if n)

    # ―― ③ 現物 ――
    atari, yomenu = [], []
    nfile = nbin = 0
    tot = 0
    hit_tane = []
    for dp, dns, fns in os.walk(walk_root):
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, walk_root)
            try:
                st = os.lstat(p)
            except OSError as e:
                yomenu.append((esc(rel), "lstat:" + type(e).__name__))
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            nfile += 1
            tot += st.st_size
            try:
                text, nishin, nb = yomu(p)
            except OSError as e:
                yomenu.append((esc(rel), "open:" + type(e).__name__))
                continue
            if nishin:
                nbin += 1
            for t in tane:
                if t in text:
                    hit_tane.append((esc(rel), fuse(t)))
            for zoku, v in sagasu(text):
                fuda = ("置字" if OKIJI.match(v) else
                        "式" if SHIKI.match(v) else "★値らしき★")
                atari.append((zoku, esc(rel), fuse(v), fuda))

    t1 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    kaku_tsv(os.path.join(outdir, "10_kou_taishou.tsv"), trows,
             header=["族", "対照の出目", "対照の長さ(伏)", "鳴つた族"])
    kaku_tsv(os.path.join(outdir, "10_kou_atari.tsv"), sorted(atari),
             header=["族", "rel_path_esc", "当つた長さ(伏)", "置字か値か"])

    kazu = {}
    for zoku, rel, f, kind in atari:
        k = kazu.setdefault(zoku, [0, 0, set()])
        k[0] += 1
        if kind == "★値らしき★":
            k[1] += 1
        k[2].add(rel)

    L = ["★甲 ―― 形を知る器の出目★", "歩き根= %s ―― ★一本★" % walk_root,
         "刻(始)= %s  刻(終)= %s" % (t0, t1),
         "器= driver/10_kou_katachi.py  版= 本弾書き下ろし  python= %s" % sys.version.split()[0],
         "族の数= %d  歩いた file(S_ISREG)= %d  byte和= %d  二進らしき file= %d" %
         (len(ZOKU), nfile, tot, nbin),
         "読めなんだ file= %d ―― ★0 でなければ其の分は「測れぬ」★" % len(yomenu), ""]
    L.append("―― ① 陽性対照(★現物より先に通した★・対照は sagasu() の★同じ路★を通る) ――")
    for r in trows:
        L.append("  %-14s %s  長さ=%s  鳴つた族=%s" % r)
    L.append("  ★鳴らなんだ族= %d★ %s" % (len(naranu), " ".join(naranu) or "(無)"))
    L.append("")
    L.append("―― ② 陰性対照(対照の種が歩き根の下に居らぬ事) ――")
    L.append("  種が現物に当つた= %d 件 %s" % (len(hit_tane), "★己の対照が漏れて居る★" if hit_tane else "(無 ―― 出目は己の対照の写しではない)"))
    for r in hit_tane[:20]:
        L.append("    %s  %s" % r)
    L.append("")
    L.append("―― ③ 現物の当り(★値は刷らぬ・長さのみ★) ――")
    if not kazu:
        L.append("  当り= 0 件")
    for zoku, _rx, _gi in ZOKU:
        k = kazu.get(zoku)
        if not k:
            L.append("  %-14s 件数=0  値らしき=0  file=0" % zoku)
        else:
            L.append("  %-14s 件数=%d  値らしき=%d  file=%d" % (zoku, k[0], k[1], len(k[2])))
    L.append("")
    L.append("★此の数が意味せぬ事★")
    L.append("・「0」は★此の11族の形★が無い意であつて、秘匿が無い意ではない(形を知らぬ秘匿は甲では出ぬ)")
    L.append("・札は三つ ―― 置字 / 式(os.environ.get 等の★code★) / ★値らしき★。")
    L.append("  ★二分(置字か値か)で出した初手は 43 件を「値らしき」と刷つたが、人の目で開けば悉く式であつた★")
    L.append("・「置字」も「式」も器の見立てであつて ―― ★人の目の代りにはならぬ★")
    L.append("・歩き根は docs/evidence ★一本★ ―― queue/・他席 worktree・他 repo は測つて居らぬ")
    L.append("・己の束(km-122)も母数に入つて居る ―― 除いた数ではない")
    kaku(os.path.join(outdir, "10_kou.txt"), "\n".join(L))
    print("10_kou rc=0 file=%d 当り=%d 鳴らぬ族=%d 読めぬ=%d 種漏れ=%d" %
          (nfile, len(atari), len(naranu), len(yomenu), len(hit_tane)))
    return 0


sys.exit(main(sys.argv))
