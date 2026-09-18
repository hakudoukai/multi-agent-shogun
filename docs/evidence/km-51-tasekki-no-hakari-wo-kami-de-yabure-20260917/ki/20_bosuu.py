#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 20_bosuu.py ―― ★母數を己の手で出す★(專任2 の宣を寫さず、凍らせた生 tsv から数へる)
# 使ひ方: 20_bosuu.py <30_ate.tsv> <60_gai.tsv>
#
# ★欄の方言(本器が最初に転んだ所・逐語で宣する)★
#   30_ate.tsv : 頭13欄(頭[0]='#colspec' は★札★)・胴12欄 ∴ 胴[i] ↔ 頭[i+1] (ずれ=1)
#   60_gai.tsv : 頭12欄(頭[0]='#colspec')・胴12欄(胴[0]='' の空欄) ∴ 胴[i] ↔ 頭[i] (ずれ=0)
#   ∴ ★同じ束の中に方言が二つ在る★。頭の名で引かねば一欄ずれる(初走で ④gtimeout を 区分 と誤読した)。
# 單位: 閾_件 / 形_件 / 組(=閾×形) / 行(=tsv の行)
import sys, io
if len(sys.argv) < 3:
    sys.stderr.write(u'★測れぬ: 30_ate.tsv と 60_gai.tsv を argv で渡せ★\n'); sys.exit(2)

def yomu(p):
    ls = [l.rstrip(u'\n') for l in io.open(p, encoding='utf-8') if l.strip()]
    h = ls[0].split(u'\t'); b = [l.split(u'\t') for l in ls[1:]]
    zure = len(h) - len(b[0])          # 0 か 1。★測つて決める。決め打たぬ★
    assert zure in (0, 1), u'★測れぬ: 頭%d 胴%d★' % (len(h), len(b[0]))
    def idx(na):
        for i, x in enumerate(h):
            if na in x: return i - zure
        raise KeyError(na)
    return h, b, zure, idx

ah, ab, az, aidx = yomu(sys.argv[1])
gh, gb, gz, gidx = yomu(sys.argv[2])
print(u'方言\t30_ate\t頭%d\t胴%d\tずれ%d' % (len(ah), len(ab[0]), az))
print(u'方言\t60_gai\t頭%d\t胴%d\tずれ%d' % (len(gh), len(gb[0]), gz))
print(u'')
c_ki, c_na, c_ki2, c_fu = aidx(u'器'), aidx(u'env名'), aidx(u'既定'), aidx(u'形札')
shikii, kata = [], []
for r in ab:
    k = (r[c_ki], r[c_na], r[c_ki2])
    if k not in shikii: shikii.append(k)
    if r[c_fu] not in kata: kata.append(r[c_fu])
print(u'#閾一覧\t番\t器\t閾名\t既定')
for i, (ki, na, kt) in enumerate(shikii, 1):
    print(u'閾%02d\t%s\t%s\t%s' % (i, ki, na, kt))
print(u'')
print(u'閾_件\t%d' % len(shikii))
print(u'形_件\t%d' % len(kata))
print(u'積_組\t%d' % (len(shikii) * len(kata)))
print(u'30_ate_行\t%d' % len(ab))
print(u'一致(積==行)\t%s' % (u'合' if len(shikii) * len(kata) == len(ab) else u'★不一致★'))
print(u'60_gai_行\t%d' % len(gb))

g_ku, g_fu, g_na = gidx(u'区分'), gidx(u'形札'), gidx(u'閾名')
ku = {}
for r in gb:
    ku[r[g_ku]] = ku.get(r[g_ku], 0) + 1
print(u'')
print(u'#區分(★專任2 の物差し★)\t組')
for k in sorted(ku, key=lambda x: (-ku[x], x)):
    print(u'%s\t%d' % (k, ku[k]))
print(u'區分_和_組\t%d' % sum(ku.values()))
gai = sum(v for k, v in ku.items() if u'無害' not in k)
print(u'★專任2 宣: 有害相当\t%d\t無害\t%d★' % (gai, sum(ku.values()) - gai))
print(u'')
tsu = sorted(set(r[g_fu] for r in gb))
print(u'通形_件\t%d\t札=%s' % (len(tsu), u','.join(tsu)))
for t in tsu:
    print(u'通形_組\t%s\t%d' % (t, len([r for r in gb if r[g_fu] == t])))
print(u'60_gai_閾_件\t%d' % len(set(r[g_na] for r in gb)))
