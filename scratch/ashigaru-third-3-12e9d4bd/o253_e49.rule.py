# -*- coding: utf-8 -*-
# E49: gate re-design. run at /home/hakudoukai/multi-agent-shogun. reads nothing; pure arithmetic.
import math
from math import comb

UNITS = {"A": (12, [4, 4, 2, 1, 1]), "B": (15, [6, 6, 2, 1, 1])}
# A: circled1=4 circled2=4 circled3=2 circled4=1 circled5=1  (sum 12)
# B: circled1=6 circled2=6 circled3=2 circled4=1 circled5=1  (sum 16, one event carries two labels -> 15 events)
ALPHA = 0.05

print("== 0. f1 check ==")
for u, (N, sizes) in UNITS.items():
    f1 = sum(1 for x in sizes if x == 1)
    print("unit%s N=%d sizes=%s sum=%d f1=%d" % (u, N, sizes, sum(sizes), f1))

print("== 1. why the E47 gate retreats ==")
for N in (11, 12, 15, 20, 40, 100, 1000, 100000):
    p0 = 2.0 / N
    print("N=%7d p0=f1/N=%.6f (1-p0)^N=%.4f" % (N, p0, (1 - p0) ** N))
print("limit exp(-2)=%.4f" % math.exp(-2))

print("== 2. candidate ONE: coverage C=1-f1/N (monotone in N when f1 fixed) ==")
for u, (N, sizes) in UNITS.items():
    f1 = sum(1 for x in sizes if x == 1)
    print("unit%s C=%.4f  needN for C>=0.95 : %d  short=%d"
          % (u, 1 - f1 / float(N), int(math.ceil(f1 / ALPHA)), int(math.ceil(f1 / ALPHA)) - N))
print("f1 fixed=2 :", ["N=%d C=%.4f" % (N, 1 - 2.0 / N) for N in (12, 15, 20, 40, 100)])
print("f1 grows as sqrt(N) :", ["N=%d f1=%.1f C=%.4f" % (N, math.sqrt(N), 1 - math.sqrt(N) / N) for N in (12, 15, 40, 100, 1000)])

print("== 3. candidate TWO: rule of three, exact pi_max = 1 - alpha^(1/N) ==")
for N in (11, 12, 15, 20, 40, 100, 200):
    print("N=%4d pi_max=%.4f (%.1f%%)  approx3/N=%.4f" % (N, 1 - ALPHA ** (1.0 / N), 100 * (1 - ALPHA ** (1.0 / N)), 3.0 / N))
for tgt in (0.10, 0.05):
    N = 1
    while 1 - ALPHA ** (1.0 / N) > tgt:
        N += 1
    print("to see forms rarer than %.0f%% : N>=%d" % (100 * tgt, N))

print("== 4. candidate THREE: rarefaction E[S(m)] (no Good-Turing) ==")
for u, (N, sizes) in UNITS.items():
    ev = N
    curve = []
    for m in range(1, ev + 1):
        e = 0.0
        for nf in sizes:
            e += 1.0 - (comb(ev - nf, m) / float(comb(ev, m)) if ev - nf >= m else 0.0)
        curve.append(e)
    print("unit%s S(m) m=1..%d : %s" % (u, ev, " ".join("%.3f" % x for x in curve)))
    print("   last slope S(N)-S(N-1)=%.6f   f1/N=%.6f  (identity check)"
          % (curve[-1] - curve[-2], sum(1 for x in sizes if x == 1) / float(ev)))
    print("   S(N)=%.3f of %d forms ; half-sample S(N/2)=%.3f" % (curve[-1], len(sizes), curve[ev // 2 - 1]))
