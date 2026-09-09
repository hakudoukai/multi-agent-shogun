# -*- coding: utf-8 -*-
# E50: apply the chosen non-retreating gate (rule of three) form by form.
# run at /home/hakudoukai/multi-agent-shogun. reads nothing; pure arithmetic.
import math
A = 0.05
def pimax(n):
    return 1.0 - A ** (1.0 / n)
def needN(t):
    return int(math.ceil(math.log(A) / math.log(1.0 - t)))

print("== 1. pi_max table (a form seen 0 times among n items) ==")
for n in (1, 2, 3, 4, 5, 6, 10, 11, 12, 15, 20, 29, 40, 59):
    print("n=%3d pi_max=%.4f (%.1f%%)" % (n, pimax(n), 100 * pimax(n)))

print("== 2. n needed to push pi_max down to a target ==")
for t in (0.50, 0.30, 0.20, 0.10, 0.05):
    print("target %.0f%% -> n>=%d" % (100 * t, needN(t)))

FORMS = ["c1", "c2", "c3", "c4", "c5"]
UA = dict(zip(FORMS, [4, 4, 2, 1, 1]))
UB = dict(zip(FORMS, [6, 6, 2, 1, 1]))
NEG = {"c1": 2, "c2": 2, "c3": 1}

print("== 3. whole corpus: an unseen FORM ==")
for name, N in (("unitA", 12), ("unitB", 15)):
    print("%s N=%d -> a form rarer than %.1f%% could be missing" % (name, N, 100 * pimax(N)))

print("== 4. inside each form: an unseen SUB-form ==")
for f in FORMS:
    print("%s nA=%d -> %.1f%%   nB=%d -> %.1f%%"
          % (f, UA[f], 100 * pimax(UA[f]), UB[f], 100 * pimax(UB[f])))

print("== 5. negative side (E48 section 7) ==")
for f in sorted(NEG):
    print("%s neg n=%d -> a counter-form rarer than %.1f%% could be missing"
          % (f, NEG[f], 100 * pimax(NEG[f])))
print("c4 neg n=0 -> pi_max undefined (no negative side observed at all)")
print("c5 neg n=0 -> pi_max undefined (no negative side observed at all)")

print("== 6. shortfall to a 20%% resolution, per form (unitB) ==")
t = 0.20
for f in FORMS:
    print("%s nB=%d need=%d short=%d" % (f, UB[f], needN(t), needN(t) - UB[f]))
print("whole corpus unitB N=15 need=%d short=%d" % (needN(t), needN(t) - 15))

print("== 7. cross-reference only (gate NOT chosen): coverage 1-f1/N ==")
print("unitA 1-2/12=%.4f  unitB 1-2/15=%.4f" % (1 - 2.0 / 12, 1 - 2.0 / 15))
