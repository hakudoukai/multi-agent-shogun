# -*- coding: utf-8 -*-
"""order224 / E16 追ひ ―― ★疵の芽★ が 現に立つ母を持つか を実測する器。

★何故 此の file が在るか★:
  本器は初め heredoc 直流で走らせた。生は残つたが ★規が残らなかつた★ ――
  作法 五条目「数を出した規は script で残せ」に反する。
  ∴ ★同じ規を file として鋳直し★ v2 とした。
  ★然るに v2 の生は v1 と大きく食ひ違つた★ ―― 因は三つ（紙 §八 に自訴）。
  ★v3 は v2 の網を 一字も変へず★（條 百七十四）、★母を二欄に分けるのみ★:
    ㋐ 己の一族（basename が order224_ で始まる物）を ★含む★ 母
    ㋑ 同じく ★除く★ 母
  之により「己が母を増やす」「己の紙が己の網に当たる」を ★数の側で分離★ する。
  （床⑾「一時 file を作るな」は ★一時 file★ の禁であり、
    器と生は ★残す物★ ゆゑ 両者は噛み合ふ。）

★何処で走らせるか★（五条目の補ひ）:
  cwd = /home/hakudoukai/multi-agent-shogun / host = momizi-dx / user = hakudoukai
  argv = python3 scratch/ashigaru-third-3-12e9d4bd/order224_e16_seed_probe_v1.rule.py
"""
import io, os, re, glob

D = "scratch/ashigaru-third-3-12e9d4bd/"
OUT = D + "order224_e16_seed_probe_v3.raw.txt"
L = []
def say(x):
    L.append(x)

def is_mine(f):
    """★己の一族★ = 本弾(order224)で己が書いた器・生・紙。"""
    return os.path.basename(f).startswith("order224_")

def split_mother(fs):
    return fs, [f for f in fs if not is_mine(f)]

say("=== order224 / E16 追い ―― ★疵の芽★ が 現に立つ母を持つか を実測する ===")
say("問ひ: 『当たりが 2 件以上 立ち得る』は 見込みである。★現に立つ母が在るか★ を数へる。")
say("")

# --- §1 as_of の網 = 母は .md 悉く ---
mds_all = sorted(glob.glob(D + "*.md"))
pat_asof = re.compile(r"as_of[:：]")

def count_md(fs):
    z0 = z1 = z2 = 0
    bad = 0
    multi = []
    for f in fs:
        try:
            t = io.open(f, encoding="utf-8").read()
        except Exception:
            bad += 1
            continue
        n = len(pat_asof.findall(t))
        if n == 0:
            z0 += 1
        elif n == 1:
            z1 += 1
        else:
            z2 += 1
            multi.append((os.path.basename(f), n))
    return z0, z1, z2, bad, multi

say("--- §1 母 = 本席 dir の .md（網 = as_of[:：]・★v2 と 一字も変へて居らぬ★） ---")
for lab, fs in ((u"ㅠ己の一族を ★含む★ 母", mds_all),
                (u"ㅡ己の一族を ★除く★ 母", split_mother(mds_all)[1])):
    z0, z1, z2, bad, multi = count_md(fs)
    say("%s = %d 枚：0 件 = %d / 1 件 = %d / ★2 件以上 = %d★ / 讀めなんだ = %d"
        % (lab, len(fs), z0, z1, z2, bad))
    for b, n in multi:
        say("    ★2 件以上★ %s = %d 件" % (b, n))
say("")

# --- §2 ROOT = の網 = 母は .py 悉く ---
pys_all = sorted(glob.glob(D + "*.py"))
pat_root = re.compile(r"ROOT\s*=\s*")

def count_py(fs):
    y0 = y1 = y2 = 0
    multi = []
    for f in fs:
        try:
            t = io.open(f, encoding="utf-8").read()
        except Exception:
            continue
        n = len(pat_root.findall(t))
        if n == 0:
            y0 += 1
        elif n == 1:
            y1 += 1
        else:
            y2 += 1
            multi.append((os.path.basename(f), n))
    return y0, y1, y2, multi

say("--- §2 母 = 本席 dir の .py（網 = ROOT\\s*=\\s* ・★v2 と 一字も変へて居らぬ★） ---")
for lab, fs in ((u"ㅠ己の一族を ★含む★ 母", pys_all),
                (u"ㅡ己の一族を ★除く★ 母", split_mother(pys_all)[1])):
    y0, y1, y2, multi = count_py(fs)
    say("%s = %d 枚：0 件 = %d / 1 件 = %d / ★2 件以上 = %d★" % (lab, len(fs), y0, y1, y2))
    for b, n in multi:
        say("    ★2 件以上★ %s = %d 件" % (b, n))
say("")

# --- §3 'from: ' の網 = 母は己の箱の便 block ---
box = "queue/inbox/ashigaru-third-3.yaml"
t = io.open(box, encoding="utf-8").read()
blocks = []
cur = None
for ln in t.split(chr(10)):
    if ln.startswith("- id: "):
        if cur is not None:
            blocks.append(chr(10).join(cur))
        cur = [ln]
    elif cur is not None:
        cur.append(ln)
if cur is not None:
    blocks.append(chr(10).join(cur))
pat_from = re.compile(r"from: ")
x0 = x1 = x2 = 0
for b in blocks:
    n = len(pat_from.findall(b))
    if n == 0:
        x0 += 1
    elif n == 1:
        x1 += 1
    else:
        x2 += 1
say("--- §3 母 = 己の箱の便 block（網 = 'from: ' の形） ---")
say("便 block = %d 件 / 当たり 0 = %d / 1 = %d / ★2 件以上 = %d★" % (len(blocks), x0, x1, x2))
say("※★便の本文に 'from: ' の字が入れば 2 件に成る★ ―― 本箱では上の数の通り。")
say("")

# --- §4 負の対照 ---
zz = "zzz_no_such_o224_probe"

def count_zz(fs):
    tot = 0
    hit = []
    for f in fs:
        try:
            k = io.open(f, encoding="utf-8").read().count(zz)
        except Exception:
            k = 0
        tot += k
        if k:
            hit.append((os.path.basename(f), k))
    return tot, hit

say("--- §4 負の対照（網 = 現に無い字 '%s'） ---" % zz)
for lab, fs in ((u"ㅠ己の一族を ★含む★ 母", mds_all),
                (u"ㅡ己の一族を ★除く★ 母", split_mother(mds_all)[1])):
    tot, hit = count_zz(fs)
    say("%s = %d 枚：当たりの和 = %d" % (lab, len(fs), tot))
    for b, k in hit:
        say("    ★当たった★ %s = %d 件" % (b, k))
say("※★v2 では此の和が 1 であつた★ ―― 因は器ではなく ★己が書いて居る紙★が 同じ字を持つ故。")
say("※★條 二百六十四は 器だけでなく ★紙にも掛かる★―― 書き手と讀み手が同じ席なら 紙も己の一族である。")

io.open(OUT, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))
print("wrote %s lines=%d" % (OUT, len(L)))
