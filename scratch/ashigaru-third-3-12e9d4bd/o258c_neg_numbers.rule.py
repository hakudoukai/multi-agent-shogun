# -*- coding: utf-8 -*-
# o258c -- numbers for the re-derived negative side and the corrected cost. reads no file.
import math
A = 0.05
def pm(n): return None if n <= 0 else 1.0 - A ** (1.0 / n)
def needN(t): return int(math.ceil(math.log(A) / math.log(1.0 - t)))
def pc(x): return "測定不能" if x is None else "%.1f%%" % (100.0 * x)
N14 = needN(0.20)
print("needN 20%% = %d ; 30%% = %d ; 10%% = %d" % (N14, needN(0.30), needN(0.10)))
NEW = {"m1": 6, "m2": 5, "m3": 0}          # 己の條 191 行 の網
OLD = {"m1": 2, "m2": 2, "m3": 1}          # E48 の網 (A1 紙3 + 台帳1行)
print("== negative side, three nets ==")
for k in ("m1", "m2", "m3"):
    n_new, n_old = NEW[k], OLD[k]
    n_sum = n_new + n_old
    print("%s new=%d(%s) old=%d(%s) sum=%d(%s) short_to_%d: new=%d sum=%d"
          % (k, n_new, pc(pm(n_new)), n_old, pc(pm(n_old)), n_sum, pc(pm(n_sum)),
             N14, max(0, N14 - n_new), max(0, N14 - n_sum)))
LINES_SCANNED = 191
PAPERS_SCANNED = 102
PAPERS_TOTAL = 336
print("== yield actually measured on the new net ==")
for k in ("m1", "m2", "m3"):
    per_line = float(NEW[k]) / LINES_SCANNED
    per_paper = float(NEW[k]) / PAPERS_SCANNED
    need = max(0, N14 - NEW[k])
    docs = "測定不能" if per_paper <= 0 else str(int(math.ceil(need / per_paper)))
    print("%s per_line=%.4f per_paper=%.4f need=%d papers_required=%s (unscanned left=%d)"
          % (k, per_line, per_paper, need, docs, PAPERS_TOTAL - PAPERS_SCANNED))
print("== E51 assumed yield vs measured ==")
for k, assumed in (("m1", 0.50), ("m2", 0.50), ("m3", 0.25)):
    meas = float(NEW[k]) / PAPERS_SCANNED
    r = "測定不能" if meas <= 0 else "%.1f" % (assumed / meas)
    print("%s assumed=%.2f/源 measured=%.4f/紙 ratio=%s" % (k, assumed, meas, r))
print("== denominator recount ==")
print("A3=191 A2=25 KARO=20 TOTAL=236 (E48 206 -> +30)")
print("A3 191 = E46 158 + (388-395)8 + (396-420)25 ; uncaught in 169..420 = 61 (same 61 as E46)")
