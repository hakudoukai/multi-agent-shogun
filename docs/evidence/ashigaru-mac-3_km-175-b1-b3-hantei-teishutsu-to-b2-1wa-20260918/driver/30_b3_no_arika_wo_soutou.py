# -*- coding: utf-8 -*-
"""★B3 の束の在処を掃討する★(家老令 km-175 ㋒ ―― 三 sha256 で両樹と隔離樹を当てる)
板 38dcde86 の current_step が名指す三本(頭8字のみ判る): 紙 a1e6d2ff(10944B/105行)/ 門控 0e1228fd(253B)/ 臺帳 a012d6b4(1401B)。
歩く所 = ⑴隔離樹 /tmp/b3poc(★symlink を解いて /private/tmp を歩く★) ⑵DentalBI 全 obj ⑶multi-agent-shogun 全 obj。
★零には四札が要る★ ―― 陽性対照(現に在る紙と blob を同じ検出子で当てる)・根と深さ・rc・刻。
★pipe を通さぬ★。生の出目は悉く kaki を通す。"""
import os
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
DENTAL = "/Users/momizimac/DentalBI"
POC = os.path.realpath("/tmp/b3poc")        # ★symlink を解く ―― /tmp は /private/tmp への link★
MATO = [("紙", "a1e6d2ff", 10944), ("門控", "0e1228fd", 253), ("臺帳", "a012d6b4", 1401)]
NAI = ("陰性対照", "98765432", -1)          # ★在らぬ頭 ―― 0 件が正★
ATAMA = [m[1] for m in MATO] + [NAI[1]]

# ―― 陽性対照 ⑴ 現に在る紙(本束の便)を、同じ検出子で当てる ――
SEI_KAMI = os.path.join(BUNDLE, "_letters", "10_chakushu_eta.txt")
sei_raw = open(SEI_KAMI, "rb").read()
SEI_SHA = hashlib.sha256(sei_raw).hexdigest()
p = subprocess.run(["shasum", "-a", "256", SEI_KAMI], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
SEI_SHA_HOKA = p.stdout.decode().split()[0] if p.returncode == 0 else "-"
ATAMA.append(SEI_SHA[:8])

# ―― 陽性対照 ⑵ 現に在る blob(B1 の現物)を、同じ git 掃討で当てる ――
SEI_BLOB_SHA = "d9a8e3178d64aad065ed438e813a74731a0191468fa5bc72e9f3ea407f6a7a9c"
ATAMA.append(SEI_BLOB_SHA[:8])

atari = []      # [類, 頭, 在処, 寸法, sha256]
gyou = []


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ―― ⑴ 隔離樹を歩く(★『紙 0 本』は『歩いて居らぬ』と区別せねば嘘に成る★) ――
def aruku(na, root):
    """戻り= (dir 数, 常の紙 数, symlink 数, 深さ, mtime の最小/最大)。★常の紙・link・dir を別々に数へる★"""
    d = n = l = 0
    fukasa = 0
    mt = []
    if not os.path.isdir(root):
        return (0, 0, 0, 0, [])
    for r, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in ("__pycache__", ".git")]
        d += 1
        mt.append(os.path.getmtime(r))
        if r != root:
            fukasa = max(fukasa, len(os.path.relpath(r, root).split(os.sep)))
        for f in fs:
            fp = os.path.join(r, f)
            if os.path.islink(fp):
                l += 1
                saki = os.path.realpath(fp)
                LINK.append([na, os.path.relpath(fp, root), os.readlink(fp)[:58],
                             ("解ける" if os.path.exists(saki) else "★解けぬ★"),
                             ("紙" if os.path.isfile(saki) else ("dir" if os.path.isdir(saki) else "-"))])
                continue
            if not os.path.isfile(fp):
                continue
            n += 1
            sh = sha256_of(fp)
            if sh[:8] in ATAMA:
                atari.append([na, sh[:8], os.path.relpath(fp, root), os.path.getsize(fp), sh])
    return (d, n, l, fukasa, mt)


LINK = []
poc_aru = os.path.isdir(POC)
poc_ev = os.path.join(POC, "docs", "evidence")
POC_D, poc_n, POC_L, poc_fukasa, POC_MT = aruku("隔離樹", POC)
gyou.append(["隔離樹 /tmp/b3poc", POC, "在り" if poc_aru else "★無し★", poc_n, poc_fukasa,
             "dir %d・link %d・常の紙 %d / docs/evidence=%s"
             % (POC_D, POC_L, poc_n, "在り" if os.path.isdir(poc_ev) else "★無し★")])

# ―― 陽性対照⑶ ―― ★同じ歩きの器★ を、紙が現に在る所(本束)へ向ける ――
HON_D, hon_n, HON_L, hon_fukasa, _ = aruku("陽性対照(本束)", BUNDLE)
gyou.append(["陽性対照(本束)", BUNDLE, "在り", hon_n, hon_fukasa,
             "dir %d・link %d・常の紙 %d ―― ★器は常の紙を見る事が出来る★" % (HON_D, HON_L, hon_n)])
kaku_tsv(os.path.join(BUNDLE, "raw", "32_kakuri_no_link.tsv"),
         LINK or [["-", "★link 0 本★", "-", "-", "-"]],
         header=["歩いた所", "link の在処", "指す先(58字で截つ)", "解けるか", "先の類"])
POC_KOKU = "-"
if POC_MT:
    import datetime as _dt
    POC_KOKU = "最古 %s / 最新 %s" % (
        _dt.datetime.fromtimestamp(min(POC_MT)).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        _dt.datetime.fromtimestamp(max(POC_MT)).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"))


# ―― ⑵⑶ git の樹を掃討(全 obj を批で読む ―― 寸法で絞つてから中身を量る) ――
def ki_soutou(na, repo):
    p1 = subprocess.run(["git", "-C", repo, "cat-file", "--batch-all-objects", "--batch-check"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    rows = [l.split() for l in p1.stdout.decode("utf-8", "replace").split("\n") if l.strip()]
    obj = len(rows)
    blob = [r for r in rows if len(r) == 3 and r[1] == "blob"]
    sun = set([m[2] for m in MATO] + [len(sei_raw), 6058])
    kouho = [r for r in blob if int(r[2]) in sun]
    n_atari = 0
    for oid, _, sz in kouho:
        p2 = subprocess.run(["git", "-C", repo, "cat-file", "blob", oid],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        if p2.returncode != 0:
            continue
        s = hashlib.sha256(p2.stdout).hexdigest()
        if s[:8] in ATAMA:
            atari.append([na, s[:8], "blob=" + oid, len(p2.stdout), s])
            n_atari += 1
    p3 = subprocess.run(["git", "-C", repo, "for-each-ref", "--format=%(refname)"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    ref = len([l for l in p3.stdout.decode("utf-8", "replace").split("\n") if l.strip()])
    gyou.append([na, repo, "rc=%d" % p1.returncode, obj, ref,
                 "blob %d 本・寸法で絞つて %d 本を量り %d 本当たつた" % (len(blob), len(kouho), n_atari)])
    return obj, ref


ki_soutou("DentalBI 全obj", DENTAL)
ki_soutou("multi-agent-shogun 全obj", ROOT)

kaku_tsv(os.path.join(BUNDLE, "raw", "30_soutou_no_ne_to_fukasa.tsv"), gyou,
         header=["歩いた所", "根", "rc/在否", "紙 or obj 数", "深さ or ref 数", "言"])
kaku_tsv(os.path.join(BUNDLE, "raw", "31_soutou_no_atari.tsv"),
         atari or [["-", "-", "★一本も当たらぬ★", "-", "-"]],
         header=["類", "sha256 頭8", "在処", "寸法(byte)", "sha256(全)"])

mato_atari = {m[1]: [a for a in atari if a[1] == m[1]] for m in MATO}
sei1 = [a for a in atari if a[1] == SEI_SHA[:8]]
sei2 = [a for a in atari if a[1] == SEI_BLOB_SHA[:8]]
nai_atari = [a for a in atari if a[1] == NAI[1]]

kaku(os.path.join(BUNDLE, "raw", "39_b3_dan.txt"),
     "刻=%s\n\n【歩いた根と深さ】\n"
     "・隔離樹=%s(★/tmp は symlink ゆゑ解いた★・在否=%s・★常の紙 %d 本★・深さ %d)\n"
     "  ―― dir %d 箇・symlink %d 本・常の紙 %d 本。★『紙 0 本』は『歩いて居らぬ』に非ず★:\n"
     "     dir を %d 箇 現に列べ、深さ %d まで下りて居る(歩いた證)。之は ★紙だけが消えた樹★ である。\n"
     "     dir の mtime= %s ―― ★一斉に同じ刻へ寄つて居る★(掃きの跡と読めるが、掃いた者は本紙では測れぬ)。\n"
     "  docs/evidence=%s(下に dir は在るが常の紙は 0 本)\n"
     "  ★陽性対照⑶★= 同じ歩きの器を本束へ向けると 常の紙 %d 本を見る ∴ 器は紙を見落さぬ\n"
     "・DentalBI=%s / multi-agent-shogun=%s(両樹とも ★全 obj★ を批で読み、寸法で絞つてから中身を量つた)\n\n"
     "【三本の的(板 38dcde86 の current_step が名指す物)】\n%s\n\n"
     "【四札 ―― 零を宣ずる為に要る物】\n"
     "・陽性対照⑴(紙の検出子)= 本束の便 _letters/10_chakushu_eta.txt を ★同じ歩きの検出子★ で当てた\n"
     "  sha256=%s / 己の器=%s / shasum(別器)=%s ―― %s\n"
     "  ★但し此の紙は隔離樹の外に在る★ ∴ 検出子が働く事の證であり、隔離樹を歩けた事の證ではない\n"
     "  隔離樹を歩けた事の證= 紙 %d 本を現に量つた(0 本ならば歩けて居らぬ)\n"
     "・陽性対照⑵(git 掃討の検出子)= B1 の現物 blob(sha256 %s…)を同じ掃討で当てた ―― 当たり %d 件\n"
     "・陰性対照= 在らぬ頭 %s に当たる物 %d 件(0 が正)\n"
     "・rc= 各行に記す(★pipe を通さず採つた★)\n\n"
     "【断】\n%s\n"
     % (KOKU, POC, ("在り" if poc_aru else "無し"), poc_n, poc_fukasa,
        POC_D, POC_L, poc_n, POC_D, poc_fukasa, POC_KOKU,
        ("在り" if os.path.isdir(poc_ev) else "★無し★"), hon_n, DENTAL, ROOT,
        "\n".join("・%s %s…(%d byte 相当)= 当たり %d 件%s"
                  % (m[0], m[1], m[2], len(mato_atari[m[1]]),
                     ("" if not mato_atari[m[1]] else " ―― " + mato_atari[m[1]][0][2]))
                  for m in MATO),
        SEI_SHA[:16], SEI_SHA[:16], SEI_SHA_HOKA[:16],
        ("★二器一致★" if SEI_SHA == SEI_SHA_HOKA else "★食ひ違ふ ―― 検出子を疑へ★"),
        poc_n, SEI_BLOB_SHA[:8], len(sei2), NAI[1], len(nai_atari),
        ("★三本悉く不在である★ ―― 隔離樹・DentalBI 全obj・multi-agent-shogun 全obj の何れにも当たらぬ。\n"
         "∴ 家老令 ㋒③ に従ひ ★原本は不在★ と宣し、板の current_step の逐語から ★再生★ の札を打つた紙を焼く。\n"
         "★再生は原本ではない★ ―― 寸法も sha256 も原本と一致せぬ(一致したら偶然を疑へ)。"
         if all(not mato_atari[m[1]] for m in MATO)
         else "★当たつた物が在る ―― 上の表の在処を固定 ref と path で書き、再生に走らぬ★")))
print("掃討 ―― 隔離樹 dir %d・link %d・常の紙 %d(深さ %d)/ 当たり %d 件"
      % (POC_D, POC_L, poc_n, poc_fukasa, len(atari)))
print("  隔離樹 dir の mtime= %s" % POC_KOKU)
print("  陽性対照⑶ 本束= 常の紙 %d 本(器は紙を見る)" % hon_n)
for m in MATO:
    print("  %s %s… 当たり %d" % (m[0], m[1], len(mato_atari[m[1]])))
print("  陽性⑴紙=%d 件(二器一致=%s) / 陽性⑵blob=%d 件 / 陰性=%d 件"
      % (len(sei1), SEI_SHA == SEI_SHA_HOKA, len(sei2), len(nai_atari)))
