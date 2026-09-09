# -*- coding: utf-8 -*-
# o261d -- N series (令258 の追) and what the 乙 road (waiting) would cost. reads no file.
import math
A = 0.05
def pm(n): return None if n <= 0 else 1.0 - A ** (1.0 / n)
def pc(x): return u"測定不能" if x is None else "%.1f%%" % (100.0 * x)
SER = [("E46", 158, 195), ("E48", 166, 206), ("o258", 191, 236), ("o261", 197, 242)]
print("== N series (per 令258 の追) ==")
prev = None
for tag, a3, tot in SER:
    d = "" if prev is None else " (+%d A3 / +%d 母)" % (a3 - prev[0], tot - prev[1])
    print("  %-5s A3=%-4d 母=%-4d%s" % (tag, a3, tot, d))
    prev = (a3, tot)
print("== 甲 road (read what already exists) ==")
print("  non-order papers in own dir = 234 ; 條-carrying among them = 0 (悉皆, not a sample)")
print("  -> papers left to read that could carry 條 = 0")
print("== 乙 road (wait for future 條) : negative side, own-條 net ==")
NEG = dict(m1=6, m2=5, m3=0)
BASE_JOU = 191
for k in ("m1", "m2", "m3"):
    n = NEG[k]
    rate = n / float(BASE_JOU)
    short = max(0, 14 - n)
    if rate > 0:
        need = int(math.ceil(short / rate))
        print("  %s n=%d pi_max=%s rate=%.4f/條 short_to_14=%d -> 要る新條 = %d"
              % (k, n, pc(pm(n)), rate, short, need))
    else:
        print("  %s n=%d pi_max=%s rate=0 short_to_14=%d -> 要る新條 = 測定不能"
              % (k, n, pc(pm(n)), short))
mint = [(SER[i + 1][1] - SER[i][1]) for i in range(len(SER) - 1)]
print("  observed minting per 弾 = %s ; mean = %.1f" % (mint, sum(mint) / float(len(mint))))
print("  (率も 弾あたりの鋳数も 一度の観測に近い ∴ 商は 見込みの見込み -- 條 四百十八)")
