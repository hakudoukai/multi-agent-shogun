#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐-締 ★乙の残りを、値を刷らずに名指す★ ―― 「残り2529」は数であつて答ではない。

乙(11)が宣除に落とせなんだ塊を、★排他かつ網羅★の類へ分ける。
肝は最後の類 ―― path片でも日附でも語連結でもない★純混字★だけが
「秘かも知れぬ」類である。之は件数が少なければ★人が全数を開ける★。
値は刷らぬ(<伏:N字>)。刻・rc・歩き根・陽性対照を併書。
歩き根=argv[1] 出先=argv[2]
"""
import math
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv, esc, fuse  # noqa: E402

TOKEN = re.compile(r"[A-Za-z0-9+/=_\-]{24,}")
HEX = re.compile(r"(?i)^[0-9a-f]+$")
DIGIT = re.compile(r"^[0-9]+$")
SHITA = re.compile(r"^[a-z0-9_\-]+$")
UE = re.compile(r"^[A-Z0-9_\-]+$")
PATHKE = re.compile(r"^/?[A-Za-z0-9_\-]+(?:/[A-Za-z0-9_\-]+)+/?$")
SHIKII_MIDARE = 3.6
HIDUKE = re.compile(r"20[0-9]{6}")

# ★対照★ ―― 11 と同じ路を通して「此の器が鳴る事」を先に證す
FUCHOU = "KM122ZQ"
TAISHOU = [
    ("対1_純混字(秘の形)", "Zq7" + FUCHOU + "xR4mN8vB2kT6yH1wS5dG9jL3pC0f"),
    ("対2_path片",         "docs/evidence/" + FUCHOU + "/raw/aB3cD4eF5gH6/path=x"),
    ("対3_=末尾詰め",       "aB3cD4eF5gH6iJ7kL8mN9oP0qR1s" + FUCHOU + "=="),
]


def midare(s):
    n = len(s)
    if n == 0:
        return 0.0
    c = {}
    for ch in s:
        c[ch] = c.get(ch, 0) + 1
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def nokori_ka(tok):
    """11 と同じ宣除。残る物だけ True。"""
    if len(tok) < 24:
        return False
    if HEX.match(tok) or DIGIT.match(tok) or SHITA.match(tok) or UE.match(tok):
        return False
    if "=" in tok[:-2]:
        return False
    if "+" not in tok and "=" not in tok and PATHKE.match(tok):
        return False
    if not (any(c.isupper() for c in tok) and any(c.islower() for c in tok)
            and any(c.isdigit() for c in tok)):
        return False
    if midare(tok) < SHIKII_MIDARE:
        return False
    return True


def wake(tok):
    """★排他かつ網羅★ ―― 上から当たつた一つだけを返す。"""
    if "/" in tok:
        return "残1_path片(/ を含む ―― 他席の束名・歩き路の写し)"
    if HIDUKE.search(tok):
        return "残2_日附入りの札(20YYMMDD を含む ―― 控・枝・弾の名)"
    if tok.endswith("="):
        return "残3_=末尾詰め(base64 らしき ―― 値の器)"
    if "_" in tok or "-" in tok:
        return "残4_語連結(_ か - で切れる ―― 識別子・file名)"
    return "★残5_純混字(切れ目無し)★"


def main():
    ne = os.path.abspath(sys.argv[1])
    outdir = os.path.abspath(sys.argv[2])
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # 陽性対照 ―― ★測る当の函数★に通す(別の路で通した対照は対照でない)
    tai_rows, nara = [], 0
    for na, v in TAISHOU:
        ok = nokori_ka(v)
        w = wake(v) if ok else "―(宣除に落ちた)"
        tai_rows.append([na, "残る" if ok else "★鳴らぬ★", w, fuse(v), "%.3f" % midare(v)])
        if not ok:
            nara += 1

    kazu, zaisho, yomenu, tanemore = {}, {}, 0, 0
    zan5_file = {}
    rows = []
    file_n = 0
    for dp, dn, fns in os.walk(ne):
        for f in fns:
            p = os.path.join(dp, f)
            try:
                if not stat.S_ISREG(os.lstat(p).st_mode):
                    continue
                b = open(p, "rb").read()
            except Exception:
                yomenu += 1
                continue
            file_n += 1
            t = b.decode("utf-8", "replace")
            for _, _tv in TAISHOU:
                if _tv in t:
                    tanemore += 1
            rel = os.path.relpath(p, ne)
            for m in TOKEN.finditer(t):
                tok = m.group(0)
                if not nokori_ka(tok):
                    continue
                k = wake(tok)
                kazu[k] = kazu.get(k, 0) + 1
                zaisho.setdefault(k, set()).add(rel.split("/")[0])
                if k.startswith("★残5"):
                    rows.append([esc(rel), len(tok), fuse(tok), "%.3f" % midare(tok)])
                    zan5_file[rel] = zan5_file.get(rel, 0) + 1

    kei = sum(kazu.values())
    L = []
    L.append("== ㋐-締 乙の残りを名指す(値は刷らぬ) ==")
    L.append("歩き根(絶対)= %s" % ne)
    L.append("刻(始)= %s  刻(終)= %s" % (t0, time.strftime("%Y-%m-%dT%H:%M:%S%z")))
    L.append("file数(S_ISREG のみ)= %d  読めぬ= %d  種漏れ= %d" % (file_n, yomenu, tanemore))
    L.append("")
    L.append("-- 陽性対照(★測る当の函数に通した★) 鳴らぬ= %d --" % nara)
    for r in tai_rows:
        L.append("  %s  %s  %s  %s  乱れ=%s" % (r[0], r[1], r[2], r[3], r[4]))
    L.append("")
    L.append("-- 残りの分け(排他・網羅 計=%d) --" % kei)
    for k in sorted(kazu, key=lambda x: -kazu[x]):
        L.append("  %-46s %6d 件  在処=%d束" % (k, kazu[k], len(zaisho[k])))
    L.append("  ―― 和= %d (乙の残りと合ふべき数)" % kei)
    L.append("")
    L.append("★肝★: 残1〜残4 は ★切れ目を持つ★ ―― 秘は切れ目を持たぬ。")
    L.append("       ∴ 人が全数を開けるべきは ★残5(純混字)= %d 件★ のみである。" % kazu.get("★残5_純混字(切れ目無し)★", 0))
    L.append("")
    L.append("-- ★残5 の在処★(file 別・全%d本) --" % len(zan5_file))
    for k in sorted(zan5_file, key=lambda x: -zan5_file[x])[:12]:
        L.append("  %6d 件  %s" % (zan5_file[k], esc(k)))
    L.append("  ―― 上位3本(.b64 = ★共有器 script を base64 で凍らせた写し★)で %d/%d 件"
             % (sum(sorted(zan5_file.values(), reverse=True)[:3]), sum(zan5_file.values())))
    L.append("★宣★: 之は「残1〜4 に秘が無い」の證ではない ―― ★形で分けただけ★である。")
    L.append("       残1〜4 に秘を隠す事は出来る(例: 秘に `-` を一字入れれば残4へ落ちる)。")
    L.append("       其の穴は★塞いで居らぬ・数も測れぬ★。甲(11形)が拾ふ側に回る。")
    kaku(os.path.join(outdir, "12_nokori_wake.txt"), "\n".join(L))
    kaku_tsv(os.path.join(outdir, "12_zan5.tsv"), rows, ["path(束内相対)", "字数", "値", "乱れ"])
    kaku_tsv(os.path.join(outdir, "12_taishou.tsv"), tai_rows,
             ["対照", "出目", "類", "値", "乱れ"])
    sys.stderr.write("12_nokori rc=0 file=%d 残り計=%d 残5=%d 鳴らぬ対照=%d 読めぬ=%d 種漏れ=%d\n"
                     % (file_n, kei, kazu.get("★残5_純混字(切れ目無し)★", 0), nara, yomenu, tanemore))
    return 0


sys.exit(main())
