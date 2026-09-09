# -*- coding: utf-8 -*-
# o261a -- judge the +30 (A3 396-420, A2 21-25) into the five buckets. reads no file.
# hand judgement, recorded here so the numbers are reproducible (作法 五条目).
J = {
 396:"axis_cut", 397:"axis_cut", 398:"off_axis", 399:"axis_cut", 400:"off_axis",
 401:"wide",     402:"off_axis", 403:"off_axis", 404:"wide",     405:"off_axis",
 406:"off_axis", 407:"off_axis", 408:"off_axis", 409:"off_axis", 410:"off_axis",
 411:"off_axis", 412:"axis_cut", 413:"axis_cut", 414:"off_axis", 415:"off_axis",
 416:"axis_cut", 417:"off_axis", 418:"wide",     419:"off_axis", 420:"narrow",
}
JA2 = {21:"axis_cut", 22:"off_axis", 23:"wide", 24:"wide", 25:"off_axis"}
BASE = dict(wide=73, narrow=12, bundled_axis=120, both=1)   # E48, denominator 206
LAB = dict(wide=u"wide(広)", narrow=u"narrow(狭)", axis_cut=u"axis_cut(軸外)",
           off_axis=u"off_axis(軸に載らぬ)", both=u"both(両側)")
add = {}
for d in (J, JA2):
    for k, v in d.items():
        add[v] = add.get(v, 0) + 1
n_new = len(J) + len(JA2)
print("new items = %d (A3 396-420 = %d , A2 21-25 = %d)" % (n_new, len(J), len(JA2)))
for k in ("wide", "narrow", "axis_cut", "off_axis", "both"):
    print("  +%-22s %d" % (LAB[k], add.get(k, 0)))
assert sum(add.values()) == 30, "SUM30"
w = BASE["wide"] + add.get("wide", 0)
nr = BASE["narrow"] + add.get("narrow", 0)
ax = BASE["bundled_axis"] + add.get("axis_cut", 0) + add.get("off_axis", 0)
bo = BASE["both"] + add.get("both", 0)
tot = w + nr + ax + bo
print("== five buckets at denominator 236 ==")
print("  wide=%d narrow=%d bundled(axis_cut+off_axis)=%d both=%d TOTAL=%d" % (w, nr, ax, bo, tot))
assert tot == 236, "TOT=%d" % tot
print("  narrow / 236        = %.2f%%" % (100.0 * nr / 236))
print("  narrow / (wide+narrow=%d) = %.2f%%  (E48: 12/85 = %.2f%%)" % (w + nr, 100.0 * nr / (w + nr), 100.0 * 12 / 85))
print("== split of the +30 only (base 120 stays bundled) ==")
print("  axis_cut=%d off_axis=%d" % (add.get("axis_cut", 0), add.get("off_axis", 0)))
