#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐-乙 ★形を知らぬ器★ ―― 秘匿の「形」ではなく★乱れ(entropy)★で測る。

甲(形を知る器)と★路が違ふ★事が肝である ―― 甲の 0 は「甲の知る11形が無い」意に過ぎぬ。
乙は形を一つも知らぬ。長く・字種が混じり・乱れた塊を数へる。
∴ 甲乙とも 0 なら「二つの別の路で 0」と書ける(★それでも「秘匿無し」の証ではない★)。

★値は刷らぬ★(<伏:N字>)。★宣して除いた類は母数に残す★(「除いた」は「歩いて居らぬ」ではない)。
歩き根 = argv[1] 一本。出 = raw/11_otsu.txt / raw/11_otsu_nokori.tsv / raw/11_otsu_taishou.tsv
"""
import math
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

TOKEN = re.compile(r"[A-Za-z0-9+/=_\-]{24,}")
HEX = re.compile(r"(?i)^[0-9a-f]+$")
DIGIT = re.compile(r"^[0-9]+$")
SHITA = re.compile(r"^[a-z0-9_\-]+$")
UE = re.compile(r"^[A-Z0-9_\-]+$")

# ★則に / と = を入れた所為で `path=raw/30_h/165_SUPABASE_URL_` の一行分が
#   「一つの乱れた塊」に見えた(実測 21:57: 残り 95812 の内 107343/115629 が此の類)。
#   ∴ 二類を足す。★但し path形の則を緩めると本物の base64 を呑む★ゆゑ
#   + と = を一字でも含む塊は path形に入れぬ(盲点は紙に書く)。
KEYVAL = re.compile(r"^.*=.*[^=]{2}$")
PATHKE = re.compile(r"^/?[A-Za-z0-9_\-]+(?:/[A-Za-z0-9_\-]+)+/?$")

SHIKII_MIDARE = 3.6   # bit/字
SHIKII_NAGASA = 24    # 字


def midare(s):
    n = len(s)
    if n == 0:
        return 0.0
    cnt = {}
    for c in s:
        cnt[c] = cnt.get(c, 0) + 1
    return -sum((v / n) * math.log2(v / n) for v in cnt.values())


def shibun(tok):
    """★排他・網羅★に仕分ける ―― 一つの塊は必ず一つの類に入る。"""
    n = len(tok)
    if HEX.match(tok):
        if n == 64:
            return "宣除1_64hex(sha256形)"
        if n == 40:
            return "宣除2_40hex(sha1形)"
        if n == 32:
            return "宣除3_32hex(md5形)"
        return "宣除4_其他hex"
    if DIGIT.match(tok):
        return "宣除5_数字のみ"
    if SHITA.match(tok):
        return "宣除6_小文字系のみ(path/識別子らしき)"
    if UE.match(tok):
        return "宣除7_大文字系のみ"
    if "=" in tok[:-2]:
        return "宣除10_=が末尾詰め以外(key=value・臺帳の欄)"
    if "+" not in tok and "=" not in tok and PATHKE.match(tok):
        return "宣除11_path形(/区切・各節が[A-Za-z0-9_-])"
    has_u = any(c.isupper() for c in tok)
    has_l = any(c.islower() for c in tok)
    has_d = any(c.isdigit() for c in tok)
    if not (has_u and has_l and has_d):
        return "宣除8_字種が三つ揃はぬ"
    if midare(tok) < SHIKII_MIDARE:
        return "宣除9_乱れが閾未満"
    return "★残り_乱れた混字★"


def taishou():
    F = "KM122ZQ"
    return [
        ("乙対照1_長い混字", F + "aB3xQ7pL9zR2mV5tY8wK4nH6"),
        ("乙対照2_base64風", F + "dGhpc0lzTm90QVJlYWxTZWNyZXQ5OTk="),
        ("乙対照3_jwt胴", F + "eyJhbGciOiJIUzI1NiJ9aBcD3fGh7Jk"),
    ]


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    os.makedirs(outdir, exist_ok=True)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    trows, naranu = [], []
    for name, s in taishou():
        k = shibun(s)
        ok = k.startswith("★残り")
        trows.append((name, k, "%.2f" % midare(s), fuse(s), "鳴つた" if ok else "★鳴らぬ★"))
        if not ok:
            naranu.append(name)
    tane = set(s for _, s in taishou())

    kazu = {}
    nokori, yomenu, tanemore = [], [], []
    nfile = 0
    ntok = 0
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
            try:
                with open(p, "rb") as fh:
                    text = fh.read().decode("utf-8", "replace")
            except OSError as e:
                yomenu.append((esc(rel), "open:" + type(e).__name__))
                continue
            for t in tane:
                if t in text:
                    tanemore.append((esc(rel), fuse(t)))
            for m in TOKEN.finditer(text):
                tok = m.group(0)
                ntok += 1
                k = shibun(tok)
                kazu[k] = kazu.get(k, 0) + 1
                if k.startswith("★残り"):
                    nokori.append((esc(rel), fuse(tok), "%.2f" % midare(tok)))

    t1 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    kaku_tsv(os.path.join(outdir, "11_otsu_taishou.tsv"), trows,
             header=["対照", "仕分", "乱れ", "長さ(伏)", "出目"])
    kaku_tsv(os.path.join(outdir, "11_otsu_nokori.tsv"), sorted(nokori),
             header=["rel_path_esc", "長さ(伏)", "乱れ"])

    L = ["★乙 ―― 乱れで測る器の出目(形を一つも知らぬ)★",
         "歩き根= %s ―― ★一本★(甲と同じ根)" % walk_root,
         "刻(始)= %s  刻(終)= %s" % (t0, t1),
         "器= driver/11_otsu_midare.py  版= 本弾書き下ろし  python= %s" % sys.version.split()[0],
         "塊の則= %s  長さ條= %d字  乱れ條= %.1f bit/字" % (TOKEN.pattern, SHIKII_NAGASA, SHIKII_MIDARE),
         "歩いた file(S_ISREG)= %d  読めなんだ= %d  塊の母数= %d" % (nfile, len(yomenu), ntok), ""]
    L.append("―― ① 陽性対照(★現物より先に・同じ shibun() を通す★) ――")
    for r in trows:
        L.append("  %-14s 仕分=%s 乱れ=%s 長さ=%s %s" % r)
    L.append("  ★鳴らなんだ対照= %d★ %s" % (len(naranu), " ".join(naranu) or "(無)"))
    L.append("")
    L.append("―― ② 陰性対照 ―― 種が現物に当つた= %d 件 %s" %
             (len(tanemore), "★己の対照が漏れて居る★" if tanemore else "(無)"))
    for r in tanemore[:10]:
        L.append("    %s %s" % r)
    L.append("")
    L.append("―― ③ 仕分(★排他・網羅★ ―― 一塊は必ず一類・検算あり) ――")
    tot = 0
    for k in sorted(kazu):
        L.append("  %-28s %d" % (k, kazu[k]))
        tot += kazu[k]
    L.append("  検算: 類の和= %d / 塊の母数= %d / 一致= %s" % (tot, ntok, tot == ntok))
    L.append("  ★宣して除いた類も母数に在る★ ―― 「除いた」は「歩いて居らぬ」ではない")
    L.append("")
    L.append("―― ④ 残り(★乱れた混字★)= %d 件 / file= %d 本 ――" %
             (len(nokori), len(set(r[0] for r in nokori))))
    L.append("")
    L.append("★此の数が意味せぬ事★")
    L.append("・残り 0 は「秘匿無し」の意ではない ―― 短い秘・低乱れの秘・二進の中の秘は乙では出ぬ")
    L.append("・閾(%.1f bit/字・%d字)は★己が選んだ★ ―― 閾を下げれば残りは増える" % (SHIKII_MIDARE, SHIKII_NAGASA))
    L.append("・★宣除11(path形)の盲点★: / を含み + も = も持たぬ base64url の秘は此処へ落ちる")
    L.append("  ―― 之は★推測ではなく則の字面から読める穴★である(塞いで居らぬ・数は測れぬ)")
    L.append("・★宣除10 の盲点★: `KEY=<秘>` の形は欄と見て除く ―― 甲10(代入)が拾ふ側に回る")
    L.append("・甲と乙は★別の路★だが★同じ根・同じ刻の近傍★を歩いた ―― 根違ひの比較ではない")
    kaku(os.path.join(outdir, "11_otsu.txt"), "\n".join(L))
    print("11_otsu rc=0 file=%d 塊=%d 残り=%d 鳴らぬ対照=%d 読めぬ=%d 種漏れ=%d" %
          (nfile, ntok, len(nokori), len(naranu), len(yomenu), len(tanemore)))
    return 0


sys.exit(main(sys.argv))
