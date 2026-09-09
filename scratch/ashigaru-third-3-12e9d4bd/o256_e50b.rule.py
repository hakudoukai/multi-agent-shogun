# -*- coding: utf-8 -*-
# o256_e50b -- E50: chosen gate = rule-of-three (pi_max). Re-judge the three shapes.
# Reads no file.母の形は E46-E48 の紙から手で置いた定数 (引き継いだ値・當て直しは未了)。
import math
ALPHA = 0.05
M = [chr(0x3280 + i) for i in range(5)]          # marks 1..5
UNITS = {"A": (12, [4, 4, 2, 1, 1]), "B": (15, [6, 6, 2, 1, 1])}
NEG = [2, 2, 1]                                   # negative-side counts for shapes 1..3 (E48 s7, 下限)

def pimax(n):
    if n <= 0:
        return None
    return 1.0 - ALPHA ** (1.0 / n)

def needN(t):
    return int(math.ceil(math.log(ALPHA) / math.log(1.0 - t)))

def pct(x):
    return "測定不能" if x is None else ("%.1f%%" % (100.0 * x))

print("== 1. overall: a wholly unseen shape ==")
for u in ("A", "B"):
    N = UNITS[u][0]
    print("unit%s N=%d pi_max=%s" % (u, N, pct(pimax(N))))

print("== 2. within-shape: an unseen sub-form inside each shape ==")
for u in ("A", "B"):
    N, sizes = UNITS[u]
    for i, n in enumerate(sizes):
        print("unit%s %s n=%d pi_max=%s" % (u, M[i], n, pct(pimax(n))))

print("== 3. negative side (E48 s7 lower bound) ==")
for i, n in enumerate(NEG):
    print("%s neg_n=%d pi_max=%s" % (M[i], n, pct(pimax(n))))

print("== 4. n needed to reach a target rarity ==")
for t in (0.50, 0.30, 0.20, 0.10, 0.05):
    print("target=%.0f%% needN=%d" % (100.0 * t, needN(t)))

print("== 5. shortfall to the 20%% line, per shape ==")
n20 = needN(0.20)
for u in ("A", "B"):
    N, sizes = UNITS[u]
    print("unit%s overall N=%d short=%d" % (u, N, max(0, n20 - N)))
    for i, n in enumerate(sizes):
        print("unit%s %s n=%d short=%d" % (u, M[i], n, max(0, n20 - n)))
for i, n in enumerate(NEG):
    print("neg %s n=%d short=%d" % (M[i], n, max(0, n20 - n)))

print("== 6. sanity: pi_max is monotone decreasing in n ==")
prev = None
mono = True
for n in range(1, 201):
    v = pimax(n)
    if prev is not None and not (v < prev):
        mono = False
    prev = v
print("monotone_decreasing=%s pimax(1)=%s pimax(200)=%s" % (mono, pct(pimax(1)), pct(pimax(200))))
