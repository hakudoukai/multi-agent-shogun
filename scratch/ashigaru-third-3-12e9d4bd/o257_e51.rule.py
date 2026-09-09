# -*- coding: utf-8 -*-
# o257_e51 -- E51: how many more, per tier, and what each count would let us say.
# Reads no file. 母の形は E46-E48 の紙から手で置いた定数 (引き継いだ値・當て直しは未了)。
import math
ALPHA = 0.05
M = [chr(0x3280 + i) for i in range(5)]
UA = (12, [4, 4, 2, 1, 1])          # unit A: 条
UB = (15, [6, 6, 2, 1, 1])          # unit B: 事例
NEG = [2, 2, 1]                      # negative side (E48 s7, 下限), net = 4 物
NEG_SOURCES = 4                      # A1 の紙 3 本 + 家老台帳 1 行
LINES = (0.50, 0.30, 0.20, 0.10, 0.05)
LADDER = (1, 2, 4, 6, 9, 12, 14, 15, 20, 29, 59)

def pimax(n):
    return None if n <= 0 else 1.0 - ALPHA ** (1.0 / n)

def needN(t):
    return int(math.ceil(math.log(ALPHA) / math.log(1.0 - t)))

def pct(x):
    return "測定不能" if x is None else ("%.1f%%" % (100.0 * x))

need = dict((t, needN(t)) for t in LINES)
print("== 0. lines ==")
for t in LINES:
    print("line=%.0f%% needN=%d" % (100.0 * t, need[t]))

print("== 1. shortfall per tier, one line each ==")
rows = []
rows.append(("tier1 unitA overall", UA[0]))
rows.append(("tier1 unitB overall", UB[0]))
for i in range(5):
    rows.append(("tier2 unitB %s within" % M[i], UB[1][i]))
for i in range(3):
    rows.append(("tier3 %s negative" % M[i], NEG[i]))
for name, n in rows:
    short = " ".join("%.0f%%:%d" % (100.0 * t, max(0, need[t] - n)) for t in LINES)
    print("%-26s n=%-3d pi_max=%-7s short[%s]" % (name, n, pct(pimax(n)), short))

print("== 2. what N would let us say (ladder) ==")
for n in LADDER:
    print("n=%-3d pi_max=%s" % (n, pct(pimax(n))))

print("== 3. cost: tier2 needs events of that shape; convert via observed shape rate ==")
NB = UB[0]
for i in range(5):
    k = UB[1][i]
    rate = float(k) / NB
    tgt = need[0.20]
    need_total_cases = int(math.ceil(tgt / rate))
    print("%s k=%d rate=%.4f  to reach n=%d need_total_cases=%d add_cases=%d"
          % (M[i], k, rate, tgt, need_total_cases, need_total_cases - NB))

print("== 4. cost: tier3 negatives come from reading an existing corpus ==")
for i in range(3):
    per = float(NEG[i]) / NEG_SOURCES
    add = max(0, need[0.20] - NEG[i])
    docs = "測定不能" if per <= 0 else str(int(math.ceil(add / per)))
    print("%s neg=%d per_source=%.2f add=%d docs_to_read=%s" % (M[i], NEG[i], per, add, docs))

print("== 5. growth of the denominator (unit A only; unit B has no series) ==")
print("unitA E46 N=11 -> E48 N=12 : +1 over 2 弾 -> 0.50 条/弾 (一度の観測)")
for name, n in (("unitA overall", UA[0]),):
    add = max(0, need[0.20] - n)
    print("%s add=%d at 0.50/弾 -> 弾=%d" % (name, add, int(math.ceil(add / 0.5))))
print("unitB 事例 growth rate = 測定不能 (系列が無い) -> 弾数は書けぬ")
