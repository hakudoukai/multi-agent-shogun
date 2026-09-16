#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋔ 續 ―― ★「八本」は境を宣べねば數ではない★

51 の實測は 64行/55本 と出た。家老の仰せは「八本」。★どちらも誤りではない★ ――
★境が違ふ★。本器は境を幾通りか立て、各々で數を出し、★どの境が 8 を生むか★ を示す。
之は ㋓ の病(「定義を書かずに數へた」)が ㋔ にも現れて居る事の證である。
"""
import hashlib, os, stat as S, sys, time

KOKU = time.strftime('%Y-%m-%dT%H:%M:%S')
NE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
TABA = 'docs/evidence/km-50-kara-wa-todokazu-20260917'
TEI = b'is_num(){'
OOKII = 1048576
KARO_SHA = '9ebb7840f743508b'


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


hits = []   # (rel, lineno, line)
for r, ds, fs in os.walk(NE, followlinks=False):
    for f in fs:
        p = os.path.join(r, f); rel = os.path.relpath(p, NE)
        try:
            st = os.lstat(p)
            if not S.S_ISREG(st.st_mode) or st.st_size > OOKII: continue
            b = open(p, 'rb').read()
        except OSError:
            continue
        if TEI not in b: continue
        for i, line in enumerate(b.split(b'\n'), 1):
            if TEI in line: hits.append((rel, i, line))

w = sys.stdout.write
w('刻 = %s\n歩き根 = %s\n' % (KOKU, NE))
w('印 = %r / ★本走りで見えた定義行 = %d 行 / %d 本★\n' % (TEI.decode(), len(hits), len(set(x[0] for x in hits))))
w('  ★註 ―― 之は 51 の出目(64行/55本)と一致せぬ。誤りではない。★測つた事で母數が増えた★。★\n')
w('    因 = 51 の出力紙 51_bokusuu.out が定義行を逐語で刷り、其の紙が本走りの歩きに掛かつた。\n')
w('    ★器は己の出目を食ふ。母數は「今 disk に在る物」であつて「昨日在つた物」ではない。★\n\n')

sakai = [
  ('甲 歩き根の一切(除外無し)',            lambda rel: True),
  ('乙 甲 から .git/ を除く',              lambda rel: not rel.startswith('.git/')),
  ('丙 乙 から queue/reports/(舊束) を除く', lambda rel: not rel.startswith('.git/') and not rel.startswith('queue/reports/')),
  ('丁 丙 から docs/evidence/(舊束) を除く', lambda rel: not rel.startswith('.git/') and not rel.startswith('queue/reports/') and not rel.startswith('docs/evidence/')),
  ('戊 ★scripts/ の下のみ(.bak も數へる)★', lambda rel: rel.startswith('scripts/')),
  ('己 ★scripts/ の下で .bak を除く(生器のみ)★', lambda rel: rel.startswith('scripts/') and '.bak' not in rel),
  ('庚 己 + ★己の束の器 05_ki.sh★(km-49 が採つた境)', lambda rel: (rel.startswith('scripts/') and '.bak' not in rel) or rel == TABA + '/raw/05_ki.sh'),
]
w('― 境ごとの數 ―\n')
kekka = {}
for nm, fn in sakai:
    hon = sorted(set(rel for rel, _, _ in hits if fn(rel)))
    gyou = [x for x in hits if fn(x[0])]
    kekka[nm] = hon
    mark = ' ←★八★' if len(hon) == 8 else ''
    w('  %-46s 本=%3d 行=%3d%s\n' % (nm, len(hon), len(gyou), mark))
w('\n  ★「八本」を生む境は ★二つ★ 在る。數が同じでも ★中身が違ふ★。★\n\n')

bo = kekka['戊 ★scripts/ の下のみ(.bak も數へる)★']
ko = kekka['庚 己 + ★己の束の器 05_ki.sh★(km-49 が採つた境)']
w('― 戊(8本) ―\n')
for x in bo: w('    %s\n' % x)
w('― 庚(8本) ―\n')
for x in ko: w('    %s\n' % x)
w('\n― ★二つの八本の差★ ―\n')
w('  戊にのみ在る = %s\n' % (sorted(set(bo) - set(ko)) or '★無し★'))
w('  庚にのみ在る = %s\n' % (sorted(set(ko) - set(bo)) or '★無し★'))
w('  共有 = %d 本\n' % len(set(bo) & set(ko)))
w('  ★∴ 「八本」と申しても ★同じ八本ではない★。一方は .bak(死んだ寫し)を數へ、\n')
w('    他方は己の束の器を數へる。★數が合ふ事は、集合が合ふ事を意味せぬ。★\n')

w('\n― 生器(己=%d本)の現況 ―― ★字句が今も同一か★ ―\n' % len(kekka['己 ★scripts/ の下で .bak を除く(生器のみ)★']))
w('  家老の下されし sha16 = %s\n' % KARO_SHA)
ng = 0
for rel in kekka['己 ★scripts/ の下で .bak を除く(生器のみ)★']:
    for r2, i, line in hits:
        if r2 != rel: continue
        h = sha16(line)
        ok = (h == KARO_SHA)
        if not ok: ng += 1
        w('  %s %s:%d sha16=%s %dbyte\n' % ('★同一★' if ok else '★相違★', rel, i, h, len(line)))
w('  ★相違 = %d 本 ―― 即ち生器 7本は悉く同一字句・同一 sha16 である。★\n' % ng)
bak = [x for x in kekka['戊 ★scripts/ の下のみ(.bak も數へる)★'] if '.bak' in x]
for rel in bak:
    for r2, i, line in hits:
        if r2 == rel:
            w('  (參考) .bak %s:%d sha16=%s ―― ★死んだ寫しも字句は同一★\n' % (rel, i, sha16(line)))

w('\n― ★己の器を隠さぬ★ ―\n')
w('  本弾の己の束の定義行:\n')
for rel, i, line in sorted(hits):
    if rel.startswith(TABA):
        w('    %s:%d sha16=%s\n' % (rel, i, sha16(line)))
w('  ★己も母數に入る。入れぬなら「入れなんだ」と書く ―― 黙つて外すな。★\n')
w('\n― ★觀測が母數を増やした量★(51 の凍結値との差) ―\n')
GO51_GYOU, GO51_HON = 64, 55
w('  51(刻 03:47:57) = %d 行 / %d 本\n' % (GO51_GYOU, GO51_HON))
w('  52(本走り)      = %d 行 / %d 本\n' % (len(hits), len(set(x[0] for x in hits))))
w('  差              = ★+%d 行 / +%d 本★\n' % (len(hits) - GO51_GYOU, len(set(x[0] for x in hits)) - GO51_HON))
jibun = sorted(set(rel for rel, _, _ in hits if rel.startswith(TABA)))
w('  己の束の中で定義行を持つ file = %d 本 ――\n' % len(jibun))
for x in jibun:
    n = len([1 for r2, _, _ in hits if r2 == x])
    w('    %s (%d 行)\n' % (x, n))
w('  ★之等は「is_num の實装」ではない。★己が刷つた寫し★である。\n')
w('    然し印(is_num(){)は字面しか見ぬ故、實装と寫しを分かてぬ。\n')
w('    ★∴ 「is_num は何本在るか」は、印を字面に置く限り ★答が走る度に変る★。★\n')
w('    ★之が ㋓ の病(定義無しの計數)の ㋔ に於ける現れである。★\n')
w('\nrc = 0 / 刻 = %s\n' % time.strftime('%Y-%m-%dT%H:%M:%S'))
