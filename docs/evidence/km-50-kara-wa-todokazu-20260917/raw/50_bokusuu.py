#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋔ ★is_num の母數を實測する★ ―― 家老の言(「八本」)を根拠に使はず、己の器で歩く。

★歩き根・深さ・rc・刻・陽性陰性対照★ を悉く刷る(裁「零には四つの札が要る」に倣ふ)。
★己の束も除かぬ ―― 別欄に分けて刷る(「除いた」は「歩いて居らぬ」ではない)。★
"""
import hashlib
import os
import stat as S
import sys
import time

KOKU = time.strftime('%Y-%m-%dT%H:%M:%S')
NE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
TABA = 'docs/evidence/km-50-kara-wa-todokazu-20260917'
OOKII = 1048576            # ★此れより大きい file は開かぬ(測れぬ欄へ)★
IN = b'is_num'             # 粗い印
TEI = b'is_num(){'         # ★定義の印(本形)★
TEI2 = b'is_num ()'        # 方言(空白を挟む形) ―― 在るか否かも測る


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    t0 = time.time()
    aruita = 0
    hiraita = 0
    ookii = []
    hijou = []
    yomenu = []
    tei_hits = []          # (path, lineno, line_bytes)
    tei2_hits = []
    genkyuu = []           # 定義でなく ★言及★ のみ
    for r, ds, fs in os.walk(NE, followlinks=False):
        for f in fs:
            p = os.path.join(r, f)
            rel = os.path.relpath(p, NE)
            aruita += 1
            try:
                st = os.lstat(p)
            except OSError as e:
                yomenu.append((rel, 'lstat: %s' % e)); continue
            if not S.S_ISREG(st.st_mode):
                hijou.append(rel); continue
            if st.st_size > OOKII:
                ookii.append((rel, st.st_size)); continue
            try:
                b = open(p, 'rb').read()
            except OSError as e:
                yomenu.append((rel, 'open: %s' % e)); continue
            hiraita += 1
            if IN not in b:
                continue
            atta_tei = False
            for i, line in enumerate(b.split(b'\n'), 1):
                if TEI in line:
                    tei_hits.append((rel, i, line)); atta_tei = True
                if TEI2 in line:
                    tei2_hits.append((rel, i, line)); atta_tei = True
            if not atta_tei:
                genkyuu.append(rel)

    w = sys.stdout.write
    w('刻 = %s\n' % KOKU)
    w('歩き根 = %s\n' % NE)
    w('深さ = ★無制限★(followlinks=False) / 名で除いた dir = ★無し(.git も queue/ も歩いた)★\n')
    w('開かぬ物 = ⑴常なる file でない物 ⑵%d byte 超の file ―― 下の「測れぬ」欄に數と名を出す\n' % OOKII)
    w('印 = 定義本形 %r / 定義方言 %r / 粗い印 %r\n\n' % (TEI.decode(), TEI2.decode(), IN.decode()))

    w('― 歩いた數 ―\n')
    w('  歩いた file = %d / 開いた file = %d\n' % (aruita, hiraita))
    w('  測れぬ(常なる file でない) = %d 本\n' % len(hijou))
    w('  測れぬ(%d byte 超ゆゑ開かぬ) = %d 本\n' % (OOKII, len(ookii)))
    w('  測れぬ(開けなんだ) = %d 本\n' % len(yomenu))
    for rel, e in yomenu[:10]:
        w('      %s :: %s\n' % (rel, e))
    w('  ★上の「測れぬ」は母數から外して居らぬ ―― 歩いたが開かなんだ物として數へて在る。★\n')

    w('\n― ★定義本形 is_num(){ ―― 一本一行として數へる★ ―\n')
    uchi, soto = [], []
    for rel, i, line in tei_hits:
        (uchi if rel.startswith(TABA) else soto).append((rel, i, line))
    w('  ★總計 = %d 行 / %d 本(file)★\n' % (len(tei_hits), len(set(x[0] for x in tei_hits))))
    w('  内訳 = 束の外 %d 行 ／ ★己の束(%s)の中 %d 行★\n' % (len(soto), TABA, len(uchi)))
    w('  ★己の束を除かぬ ―― 下に分けて出す。器は己を數へた事を隠さぬ。★\n\n')

    def dasu(nm, xs):
        w('  【%s】%d 行\n' % (nm, len(xs)))
        for rel, i, line in sorted(xs):
            w('    %s:%d\n' % (rel, i))
            w('      逐語 = %s\n' % line.decode('utf-8', 'replace'))
            w('      sha16(改行無) = %s / sha16(改行有) = %s / %d byte\n'
              % (sha16(line), sha16(line + b'\n'), len(line)))
    dasu('束の外', soto)
    dasu('己の束の中', uchi)

    w('\n― 字句の同一 ―\n')
    ss = {}
    for rel, i, line in tei_hits:
        ss.setdefault(sha16(line), []).append('%s:%d' % (rel, i))
    for h, ps in sorted(ss.items(), key=lambda kv: -len(kv[1])):
        w('  sha16=%s ―― %d 行\n' % (h, len(ps)))
        for x in sorted(ps):
            w('      %s\n' % x)
    w('  ★家老が下さつた sha16 = 9ebb7840f743508b ―― 上に在るか: %s★\n'
      % ('★在る★' if '9ebb7840f743508b' in ss else '★無い★'))

    w('\n― 定義方言 is_num () ―\n')
    w('  %d 行%s\n' % (len(tei2_hits), '' if tei2_hits else ' ―― ★一行も無い(空である旨の一行)★'))
    for rel, i, line in sorted(tei2_hits):
        w('    %s:%d %s\n' % (rel, i, line.decode('utf-8', 'replace')))

    w('\n― ★言及のみ(is_num を含むが定義行を持たぬ file)★ ―\n')
    w('  %d 本%s\n' % (len(genkyuu), '' if genkyuu else ' ―― ★一本も無い(空である旨の一行)★'))
    for rel in sorted(genkyuu):
        w('    %s\n' % rel)

    w('\n― 対照(★同じ檢出子を通した★) ―\n')
    you = os.path.join(TABA, 'raw', '05_ki.sh')
    inn = os.path.join(TABA, 'raw', '00_koku.txt')
    you_atta = any(rel == you for rel, _, _ in tei_hits)
    in_atta = any(rel == inn for rel, _, _ in tei_hits)
    w('  陽性対照 %s ―― 定義行 %s(★在るべし★)\n' % (you, '在り' if you_atta else '★無し=器が壊れて居る★'))
    w('  陰性対照 %s ―― 定義行 %s(★無かるべし★)\n' % (inn, '★在り=誤検出★' if in_atta else '無し'))
    ok = you_atta and not in_atta
    w('  ★対照 = %s★\n' % ('通(器として使へる)' if ok else '落ち(數を出すな)'))

    w('\n― 測れぬの名(%d byte 超・上位10) ―\n' % OOKII)
    for rel, sz in sorted(ookii, key=lambda x: -x[1])[:10]:
        w('    %s (%d byte)\n' % (rel, sz))
    w('  ★是等は「is_num を含まぬ」と申して居らぬ。★開かなんだ★ のである。★\n')

    w('\n走り = %.2f 秒 / rc = %d\n' % (time.time() - t0, 0 if ok else 1))
    return 0 if ok else 1


sys.exit(main())
