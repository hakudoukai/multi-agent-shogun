# -*- coding: utf-8 -*-
"""order224 / E16 追ひ ―― ★疵の芽★ が 現に立つ母を持つか を実測する器。

★何故 此の file が在るか★:
  本器は初め heredoc 直流で走らせた。生は残つたが ★規が残らなかつた★ ――
  作法 五条目「数を出した規は script で残せ」に反する。
  ∴ ★同じ規を file として鋳直し★ v2 とする。
  ★但し 生は v1 と一致せぬ★ ―― ★己が此の file を書いた分 .py の母が 1 枚増える★。
  之は疵ではなく ★己が母を増やす★ の現行であり、v1 の生は消さずに残す。
  （床⑾「一時 file を作るな」は ★一時 file★ の禁であり、
    器と生は ★残す物★ ゆゑ 両者は噛み合ふ。）

★何処で走らせるか★（五条目の補ひ）:
  cwd = /home/hakudoukai/multi-agent-shogun / host = momizi-dx / user = hakudoukai
  argv = python3 scratch/ashigaru-third-3-12e9d4bd/order224_e16_seed_probe_v1.rule.py
"""
import io, os, re, glob

D = "scratch/ashigaru-third-3-12e9d4bd/"
OUT = D + "order224_e16_seed_probe_v2.raw.txt"
L = []
def say(x):
    L.append(x)

say("=== order224 / E16 追い ―― ★疵の芽★ が 現に立つ母を持つか を実測する ===")
say("問ひ: 『当たりが 2 件以上 立ち得る』は 見込みである。★現に立つ母が在るか★ を数へる。")
say("")

# --- §1 as_of の網 = 母は .md 悉く ---
mds = sorted(glob.glob(D + "*.md"))
pat_asof = re.compile(r"as_of[:：]")
z0 = z1 = z2 = 0
bad = 0
multi = []
for f in mds:
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
say("--- §1 母 = 本席 dir の .md 悉く = %d 枚 ---" % len(mds))
say("当たり 0 件 = %d 枚 / 1 件 = %d 枚 / ★2 件以上 = %d 枚★ / 讀めなんだ = %d" % (z0, z1, z2, bad))
for b, n in multi:
    say("  ★2 件以上★ %s = %d 件" % (b, n))
say("")

# --- §2 ROOT = の網 = 母は .py 悉く ---
pys = sorted(glob.glob(D + "*.py"))
pat_root = re.compile(r"ROOT\s*=\s*")
y0 = y1 = y2 = 0
for f in pys:
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
say("--- §2 母 = 本席 dir の .py 悉く = %d 枚（網 = ROOT = の形） ---" % len(pys))
say("当たり 0 件 = %d 枚 / 1 件 = %d 枚 / ★2 件以上 = %d 枚★" % (y0, y1, y2))
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
tot = 0
for f in mds:
    try:
        tot += io.open(f, encoding="utf-8").read().count(zz)
    except Exception:
        pass
say("--- §4 負の対照 ---")
say("現に無い網 '%s' の当たり（.md 悉く） = %d" % (zz, tot))
say("※★己(此の器)は .py ゆゑ .md の母に入らぬ★ ―― 條 二百六十四 の『己の一族を母から外す』を 母の側で果たした。")

io.open(OUT, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))
print("wrote %s lines=%d" % (OUT, len(L)))
