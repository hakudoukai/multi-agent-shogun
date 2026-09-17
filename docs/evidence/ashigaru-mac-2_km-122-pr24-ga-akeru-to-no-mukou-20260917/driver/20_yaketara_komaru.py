#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋒ ★秘の外で「焼いたら困る物」を名指す★ ―― 的の例示(患者らしき文字列・氏名・
絶対 path の利用者名・巨大 file・他席の worktree の写し・__pycache__)を一つ宛測る。

★無いなら「無い」を数で書く★。値は刷らぬ(<伏:N字>)。陽性対照は★測る当の函数★に通す。
「語が在る」と「人を特定し得る形が在る」は★別の数★である ―― 分けて書く。
歩き根=argv[1] 出先=argv[2]
"""
import os
import re
import datetime
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv, esc, fuse  # noqa: E402

F = "KM122ZQ"   # 符丁(対照を現物から見分ける)

# ―― 本文に当てる則(値を捕る物は群1を伏せる) ――
HON = [
    ("㋒5a_電話らしき",     re.compile(r"\b0\d{1,4}-\d{1,4}-\d{4}\b"), "個人を特定し得る形"),
    ("㋒5b_郵便番号らしき",  re.compile(r"\b\d{3}-\d{4}\b"), "個人を特定し得る形"),
    ("㋒5c_メールらしき",   re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "個人を特定し得る形"),
    ("㋒5d_生年月日らしき",  re.compile(r"\b(?:19|20)\d{2}[-/年](?:0?[1-9]|1[0-2])[-/月](?:0?[1-9]|[12]\d|3[01])日?\b"), "個人を特定し得る形"),
    ("㋒5e_和暦生年らしき",  re.compile(r"[明大昭平令][治正和成如][0-9]{1,2}年[0-9]{1,2}月[0-9]{1,2}日"), "個人を特定し得る形"),
    ("㋒5f_12桁連番",       re.compile(r"(?<![0-9])\d{12}(?![0-9])"), "個人を特定し得る形"),
    ("㋒6_敬称付きの名らしき", re.compile(r"([一-龥ぁ-んァ-ヶ]{2,5})(?:様|さん|氏)(?![がのはでをに])"), "★辞書無し ∴ 名か否か断ぜぬ★"),
    ("㋒5g_診療語",          re.compile(r"患者|カルテ|受診|主訴|処方|診療録"), "語 ―― 人を特定せぬ"),
]
# ―― path に当てる則 ――
MICHI = [
    ("㋒3_利用者名入り絶対path", re.compile(r"/Users/([A-Za-z0-9._\-]+)")),
]

TAI = [
    ("対_電話",   "㋒5a_電話らしき",     F + " 090-1234-5678 " + F),
    ("対_郵便",   "㋒5b_郵便番号らしき",  F + " 857-0851 " + F),
    ("対_メール", "㋒5c_メールらしき",   F + " taro@example.com " + F),
    ("対_生年",   "㋒5d_生年月日らしき",  F + " 1980-01-02 " + F),
    ("対_和暦",   "㋒5e_和暦生年らしき",  F + " 昭和55年1月2日 " + F),
    ("対_12桁",   "㋒5f_12桁連番",       F + " 123456789012 " + F),
    ("対_敬称",   "㋒6_敬称付きの名らしき", F + " 山田太郎様 " + F),
    ("対_診療語", "㋒5g_診療語",          F + " 患者 " + F),
]

OOKII = 1048576   # 1MiB

# ★「当つた」だけでは何も言へぬ★ ―― 当つた物の★字形★と★宛先の種★を器に数へさせる。
KOUKAI = ("@github.com", "@users.noreply.github.com", "@anthropic.com",
          "@example.com", "@example.org", "@example.invalid", "@MomiziMac-mini.local")


def keishiki(v):
    """数字を 9 へ潰す ―― 値を出さずに★形★を見せる。"""
    return re.sub(r"[0-9]", "9", v)


def toki_ka(v):
    """12桁が YYYYMMDDHHMM として読めるか。読めぬなら byte/seq/乱数の類。"""
    try:
        datetime.datetime.strptime(v, "%Y%m%d%H%M")
        return True
    except ValueError:
        return False


def main():
    ne = os.path.abspath(sys.argv[1])
    outdir = os.path.abspath(sys.argv[2])
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # 陽性対照 ―― ★本走査と同じ則 object★ に通す
    hon_d = dict((n, r) for n, r, _ in HON)
    trows, naranu = [], 0
    for na, zoku, s in TAI:
        ok = hon_d[zoku].search(s) is not None
        trows.append([na, zoku, "鳴つた" if ok else "★鳴らぬ★", fuse(s)])
        if not ok:
            naranu += 1
    tane = set(s for _, _, s in TAI)

    kata = {}       # 族 -> 字形 -> 件数
    ate = {}        # メール宛 -> 件数(値は持つが刷らぬ)
    d12 = {"刻(YYYYMMDDHHMM)として読める": 0, "刻として読めぬ(byte/seq の類)": 0}
    ken = {}        # 族 -> 件数
    fken = {}       # 族 -> file集合
    nushi = {}      # 利用者名 -> 件数
    ookii, pyc, pyc_b, worktree, kyouyuu = [], 0, 0, [], []
    nfile = nbyte = yomenu = tanemore = 0
    fukutsuu = 0    # 己の束の本数

    for dp, dn, fns in os.walk(ne):
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, ne)
            try:
                st = os.lstat(p)
            except OSError:
                yomenu += 1
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            nfile += 1
            nbyte += st.st_size
            if st.st_size >= OOKII:
                ookii.append([esc(rel), st.st_size])
            if "__pycache__" in rel or rel.endswith(".pyc"):
                pyc += 1
                pyc_b += st.st_size
            if "/worktrees/" in "/" + rel or "/.git/" in "/" + rel or rel.endswith("/.git"):
                worktree.append([esc(rel), st.st_size])
            if rel.endswith(".b64") or rel.endswith(".sh"):
                kyouyuu.append([esc(rel), st.st_size])
            for na, r in MICHI:
                for m in r.finditer(os.path.abspath(p)):
                    ken[na] = ken.get(na, 0) + 1
                    fken.setdefault(na, set()).add(rel)
                    nushi[m.group(1)] = nushi.get(m.group(1), 0) + 1
            try:
                t = open(p, "rb").read().decode("utf-8", "replace")
            except OSError:
                yomenu += 1
                continue
            for s in tane:
                if s in t:
                    tanemore += 1
            for na, r, _ in HON:
                n = 0
                for m in r.finditer(t):
                    n += 1
                    v = m.group(0)
                    if na.startswith("㋒5c"):
                        ate[v] = ate.get(v, 0) + 1
                    elif na.startswith("㋒6"):
                        kata.setdefault(na, {})
                        kata[na][m.group(1)] = kata[na].get(m.group(1), 0) + 1
                    else:
                        kata.setdefault(na, {})
                        k2 = keishiki(v)
                        kata[na][k2] = kata[na].get(k2, 0) + 1
                    if na.startswith("㋒5f"):
                        d12["刻(YYYYMMDDHHMM)として読める" if toki_ka(v)
                            else "刻として読めぬ(byte/seq の類)"] += 1
                if n:
                    ken[na] = ken.get(na, 0) + n
                    fken.setdefault(na, set()).add(rel)
            # 本文中の /Users/ も数へる(path 欄として紙に写された物)
            for m in re.finditer(r"/Users/([A-Za-z0-9._\-]+)", t):
                ken["㋒3b_本文に写された利用者名"] = ken.get("㋒3b_本文に写された利用者名", 0) + 1
                fken.setdefault("㋒3b_本文に写された利用者名", set()).add(rel)
                nushi[m.group(1)] = nushi.get(m.group(1), 0) + 1

    L = []
    L.append("== ㋒ 秘の外で「焼いたら困る物」を名指す ==")
    L.append("歩き根(絶対)= %s" % ne)
    L.append("刻(始)= %s  刻(終)= %s" % (t0, time.strftime("%Y-%m-%dT%H:%M:%S%z")))
    L.append("file数(S_ISREG のみ)= %d  byte和= %d  読めぬ= %d  種漏れ= %d" % (nfile, nbyte, yomenu, tanemore))
    L.append("")
    L.append("-- 陽性対照(★本走査と同じ則 object★) 鳴らぬ= %d --" % naranu)
    for r in trows:
        L.append("  %-8s %-22s %s  %s" % (r[0], r[1], r[2], r[3]))
    L.append("")
    L.append("-- 出目(件数と file数・★値は刷らぬ★) --")
    for na, _, imi in HON:
        L.append("  %-24s %7d 件  %5d file  ― %s"
                 % (na, ken.get(na, 0), len(fken.get(na, set())), imi))
    for na in ("㋒3_利用者名入り絶対path", "㋒3b_本文に写された利用者名"):
        L.append("  %-24s %7d 件  %5d file" % (na, ken.get(na, 0), len(fken.get(na, set()))))
    L.append("  相異なる利用者名= %d 通り(値は刷らぬ ―― %s)"
             % (len(nushi), " ".join(fuse(k) for k in sorted(nushi, key=lambda x: -nushi[x])[:5])))
    L.append("")
    L.append("  ㋒1_巨大file(1MiB 以上)= %d 本  byte和= %d" % (len(ookii), sum(r[1] for r in ookii)))
    for r in sorted(ookii, key=lambda x: -x[1])[:5]:
        L.append("      %10d byte  %s" % (r[1], r[0]))
    L.append("  ㋒2___pycache__/.pyc= %d 本  byte和= %d" % (pyc, pyc_b))
    L.append("  ㋒4_他席 worktree/.git の写し= %d 本  byte和= %d"
             % (len(worktree), sum(r[1] for r in worktree)))
    L.append("  ㋒7_器の写し(.sh/.b64)= %d 本  byte和= %d"
             % (len(kyouyuu), sum(r[1] for r in kyouyuu)))
    for r in sorted(kyouyuu, key=lambda x: -x[1])[:5]:
        L.append("      %10d byte  %s" % (r[1], r[0]))
    L.append("")
    L.append("-- ★当つた物の字形★(値ではなく形・数字は 9 へ潰した) --")
    for na in ("㋒5a_電話らしき", "㋒5b_郵便番号らしき", "㋒5d_生年月日らしき", "㋒5f_12桁連番"):
        d = kata.get(na, {})
        L.append("  %s 相異なる形= %d" % (na, len(d)))
        for k in sorted(d, key=lambda x: -d[x])[:3]:
            L.append("      %6d 件  %s" % (d[k], k))
    L.append("  ㋒5f の内訳: %s" % "  ".join("%s=%d" % (k, v) for k, v in sorted(d12.items())))
    d = kata.get("㋒6_敬称付きの名らしき", {})
    L.append("  ㋒6 敬称の前の語 相異なる= %d ―― 上位(★値を出す: 氏名ではない事を示す為★)" % len(d))
    for k in sorted(d, key=lambda x: -d[x])[:5]:
        L.append("      %6d 件  「%s」" % (d[k], k))
    L.append("")
    L.append("-- ★メールの宛先★(局のみ・名は伏せる) 相異なる= %d 通り 計= %d 件"
             % (len(ate), sum(ate.values())))
    nama = dict((k, v) for k, v in ate.items() if not any(k.endswith(x) for x in KOUKAI))
    L.append("  公開bot・例示・此の機の局を除いた★実在らしき宛★= %d 通り / %d 件"
             % (len(nama), sum(nama.values())))
    for k in sorted(nama, key=lambda x: -nama[x])[:6]:
        u, _, dm = k.partition("@")
        L.append("      %4d 件  %s@%s" % (nama[k], fuse(u), dm))
    L.append("")
    L.append("★数が何を意味せぬか★")
    L.append("・㋒5g(診療語)は ★語★ の数である ―― 人を一人も特定せぬ。艦の条・紙の議論に現れる。")
    L.append("・㋒6 は ★辞書を持たぬ★ ∴ 「名か否か」を断じて居らぬ。敬称の前の2〜5字を数へただけ。")
    L.append("  役職名(委員長様 等)も此処に入る。★∴ 之は上限であつて、氏名の数ではない。★")
    L.append("・0 は「其の形が無い」意であつて「其の物が無い」意ではない(別形は測れて居らぬ)。")
    L.append("・㋒3 の 件数 は ★出現の数★ であつて file の数ではない(file数を併記した)。")
    kaku(os.path.join(outdir, "20_komaru.txt"), "\n".join(L))
    kaku_tsv(os.path.join(outdir, "20_taishou.tsv"), trows, ["対照", "族", "出目", "値"])
    kaku_tsv(os.path.join(outdir, "20_ookii.tsv"), sorted(ookii, key=lambda x: -x[1]), ["path", "byte"])
    kaku_tsv(os.path.join(outdir, "20_utsushi.tsv"), sorted(kyouyuu, key=lambda x: -x[1]), ["path", "byte"])
    sys.stderr.write("20_komaru rc=0 file=%d 巨大=%d pyc=%d worktree=%d 器写=%d 鳴らぬ対照=%d 読めぬ=%d 種漏れ=%d\n"
                     % (nfile, len(ookii), pyc, len(worktree), len(kyouyuu), naranu, yomenu, tanemore))
    return 0


sys.exit(main())
