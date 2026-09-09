# -*- coding: utf-8 -*-
# o258d -- unit B after the one positive found inside the 條 corpus. reads no file.
import math
A = 0.05
def pm(n): return 1.0 - A ** (1.0 / n)
def pc(x): return "%.1f%%" % (100.0 * x)
old = {"N": 15, "m": [6, 6, 2, 1, 1]}
new = {"N": 16, "m": [7, 6, 2, 1, 1]}
for tag, d in (("E48/E50 old", old), ("o258 new", new)):
    print("%-12s N=%d sum=%d pi_max=%s" % (tag, d["N"], sum(d["m"]), pc(pm(d["N"]))))
    print("             within: %s" % " ".join("%d->%s" % (k, pc(pm(k))) for k in d["m"]))
print("20%% line needN=14 ; unitB overall short: old=%d new=%d"
      % (max(0, 14 - old["N"]), max(0, 14 - new["N"])))
print("within m1 short to 14: old=%d new=%d" % (max(0, 14 - 6), max(0, 14 - 7)))
print("unitA: N=12 -> 236 母 の下では 未判 30 本 ; 狭 12 は 母206 の範のみ")
