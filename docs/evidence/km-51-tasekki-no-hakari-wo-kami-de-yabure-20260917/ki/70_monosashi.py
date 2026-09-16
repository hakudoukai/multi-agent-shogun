#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 70_monosashi.py ―― ★己の物差しで割り直し、專任2 と食ひ違ふ組を名指す★
# 使ひ方: 70_monosashi.py <km52_raw_60_gai.tsv> <71_kougodan.tsv>
#
# ★當席の物差し(宣)★ 單位=組(閾×形)。★「決定に効くか」で門を立てる★
#   其の閾の★決定の讀手★を、71_kougodan.py が生器から引いた表で定める(彼の散文欄に依らぬ)。
#     算術  … 決定そのものが $(( )) の中で起きる閾
#     外器  … 決定が外の器(gtimeout / inotifywait -t)へ渡る閾
#     test  … 其の他(比較は [ ] で起きる)
#   有害 ⇔ 次の孰れか一つでも立つ:
#     ⑴定値化 … ★決定の讀手が讀んだ値★が 0 / 極大 で、比較が現実の域で定値に倒れる
#     ⑵外器害 … 外器が起動を拒む、又は限りが張られぬ(★外器の閾のみ★)
#     ⑶割れ   … ★決定の讀手が讀んだ値★ ≠ 人が字面から讀む値。
#                ★表示だけの $(( )) は此に数へぬ(決定に効かぬゆゑ)★
#   無害 ⇔ 右の孰れも立たぬ。
# ★專任2 の物差しとの差(先に宣す)★
#   彼は「其の閾に $(( ) が一つでも触れて居れば 讀手の割れ」と割る。
#   當席は「其の $(( )) が★決定★か★表示★か」を分ける。∴ 表示のみの組で割れ得る。
import sys, io
if len(sys.argv) < 3:
    sys.stderr.write(u'★測れぬ: 60_gai.tsv と 71_kougodan.tsv を argv で渡せ★\n'); sys.exit(2)

def yomu(p):
    ls = [l.rstrip(u'\n') for l in io.open(p, encoding='utf-8') if l.strip()]
    h = ls[0].split(u'\t'); b = [l.split(u'\t') for l in ls[1:] if u'\t' in l]
    zure = len(h) - len(b[0])
    assert zure in (0, 1), u'★測れぬ: 頭%d 胴%d★' % (len(h), len(b[0]))
    def idx(na):
        for i, x in enumerate(h):
            if na in x: return i - zure
        raise KeyError(na)
    return b, idx

# ―― 決定の讀手を 71 の表から起こす ――
kb, kidx = yomu(sys.argv[2])
k_na, k_yo, k_gy, k_ji = kidx(u'閾名'), kidx(u'讀手'), kidx(u'行'), kidx(u'使用箇所の逐語')
yomite = {}
for r in kb:
    if len(r) <= k_ji: continue
    na, yo, ji = r[k_na], r[k_yo], r[k_ji]
    if u'外器' in yo: yomite[na] = u'外器'
    elif u'算術' in yo and u'文言' not in ji and u'echo' not in ji and u'KB' not in ji:
        yomite.setdefault(na, u'算術')
    else: yomite.setdefault(na, u'test')
# 表示のみの算術は上の条件で落ちる。落ちた閾は test 扱ひ(既定)。

gb, gidx = yomu(sys.argv[1])
c_ki, c_na, c_fu, c_ge = gidx(u'器'), gidx(u'閾名'), gidx(u'形札'), gidx(u'逐語')
c_t, c_a, c_g, c_ku = gidx(u'①test'), gidx(u'②算術'), gidx(u'④gtimeout'), gidx(u'区分')

MEN = {u'07': 0, u'08': 0, u'09': 50, u'10': 50, u'16': 7, u'17': 10, u'18': 2**63 - 1}
def kazu(s):
    s = s.strip()
    if s.startswith(u'2^63'): return 2**63 - 1
    try: return int(s, 10)
    except ValueError: return None

print(u'器\t閾名\t形\t逐語\t決定の讀手\t實(決定が讀む)\t面(人が讀む)\t當席\t立つた述語\t專任2\t判')
kui = []; ari = {}
for r in gb:
    if len(r) <= c_ku: continue
    ki, na, fu, ge = r[c_ki], r[c_na], r[c_fu], r[c_ge]
    yo = yomite.get(na, u'★表に無し★')
    men = MEN.get(fu)
    jitsu = kazu(r[c_a]) if yo == u'算術' else kazu(r[c_t])
    j = []
    if jitsu == 0: j.append(u'⑴定値化(零)')
    if jitsu == 2**63 - 1: j.append(u'⑴定値化(極大)')
    if yo == u'外器':
        if u'拒' in r[c_g]: j.append(u'⑵外器拒')
        if u'限り' in r[c_g]: j.append(u'⑵限り張られず')
    if jitsu is not None and men is not None and jitsu != men: j.append(u'⑶割れ')
    han = u'有害' if j else u'無害'
    ari[(na, fu)] = han
    kare = u'無害' if u'無害' in r[c_ku] else u'有害'
    ok = (han == kare)
    if not ok: kui.append((ki, na, fu, ge, r[c_ku], han, u','.join(j) or u'―', yo))
    print(u'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (
        ki, na, fu, ge, yo, r[c_a] if yo == u'算術' else r[c_t], men, han,
        u','.join(j) or u'―', r[c_ku], u'合' if ok else u'★食ひ違ひ★'))

print(u'')
print(u'母數_組\t%d' % len(ari))
print(u'當席_有害_組\t%d' % len([v for v in ari.values() if v == u'有害']))
print(u'當席_無害_組\t%d' % len([v for v in ari.values() if v == u'無害']))
print(u'專任2_有害_組\t59\t專任2_無害_組\t67')
print(u'★食ひ違ひ_組\t%d★' % len(kui))
if not kui:
    print(u'★食ひ違ひ 0 ―― 名指すべき組は無い★')
for k in kui:
    print(u'食ひ違ひ\t%s/%s/形%s\t逐語=%s\t決定の讀手=%s\t專任2=%s\t當席=%s\t述語=%s' % (
        k[0], k[1], k[2], k[3], k[7], k[4], k[5], k[6]))
print(u'')
print(u'#決定の讀手 内訳')
import collections
for y, n in sorted(collections.Counter(yomite.values()).items()):
    print(u'讀手\t%s\t%d閾\t%s' % (y, n, u' '.join(sorted(a for a in yomite if yomite[a] == y))))
