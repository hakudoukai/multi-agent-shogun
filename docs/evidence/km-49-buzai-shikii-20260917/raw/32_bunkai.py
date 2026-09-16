#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑ ―― 7,896,856 が ★何で出来てゐるか★ を集合の差で分解する。
   甲(肥えた束) と 乙(痩せた束) を ★名の集合★ で引き算し、増減を一本づつ數へる。"""
import os, sys, collections
kou, otsu = sys.argv[1], sys.argv[2]
def walk(root):
    d = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                d[os.path.relpath(p, root)] = os.path.getsize(p)
    return d
for _r in (kou, otsu):
    if not os.path.isdir(_r):
        sys.stderr.write("★歩き根が無い(「%s」) ―― 0 本を返さず倒れる(fail-closed)★\n" % _r); sys.exit(3)
A = walk(kou); B = walk(otsu)
for _n, _d, _r in (("甲", A, kou), ("乙", B, otsu)):
    if not _d:
        sys.stderr.write("★%s の歩きが 0 本(「%s」) ―― 差は取れぬ(fail-closed)★\n" % (_n, _r)); sys.exit(3)
# 乙 は 甲 を moto_evidence/raw の下へ抱へてゐる。名を揃へる為に接頭を剥ぐ。
PRE = "moto_evidence/raw" + os.sep
B2 = {}
soto = {}
for k, v in B.items():
    if k.startswith(PRE): B2[k[len(PRE):]] = v
    else: soto[k] = v
print("甲 = %d 本 / %d byte" % (len(A), sum(A.values())))
print("乙 = %d 本 / %d byte(内 moto_evidence/raw 下 = %d 本 %d byte・其の外 = %d 本 %d byte)"
      % (len(B), sum(B.values()), len(B2), sum(B2.values()), len(soto), sum(soto.values())))
print("★甲−乙 = %d byte★" % (sum(A.values()) - sum(B.values())))
print("")
ochita = sorted(set(A) - set(B2)); waita = sorted(set(B2) - set(A))
kawatta = sorted(k for k in (set(A) & set(B2)) if A[k] != B2[k])
print("―― 落ちた本(甲に在り乙に無し) = %d 本 / 和 %d byte" % (len(ochita), sum(A[k] for k in ochita)))
for k in ochita: print("     %10d  %s" % (A[k], k))
print("―― 湧いた本(乙の中の同じ階に在り甲に無し) = %d 本 / 和 %d byte" % (len(waita), sum(B2[k] for k in waita)))
for k in waita: print("     %10d  %s" % (B2[k], k))
print("―― 寸が変つた本 = %d 本" % len(kawatta))
for k in kawatta: print("     %10d → %10d  %s" % (A[k], B2[k], k))
print("―― moto_evidence/raw の外に置かれた本 = %d 本 / 和 %d byte" % (len(soto), sum(soto.values())))
for k in sorted(soto): print("     %10d  %s" % (soto[k], k))
print("")
o = sum(A[k] for k in ochita); w = sum(B2[k] for k in waita); s = sum(soto.values())
print("★式 ―― 落ちた %d − 湧いた %d − 外に置いた %d = %d★" % (o, w, s, o - w - s))
print("   甲−乙 = %d ―― 一致 %s" % (sum(A.values()) - sum(B.values()), "○" if o - w - s == sum(A.values()) - sum(B.values()) else "×"))
