# -*- coding: utf-8 -*-
"""束の全紙(raw/ だけでなく suna/ も)を門の條②③④へ合はせる。
 ・0 byte の紙 → ★真の大きさを台帳(raw/94_kuu.txt)へ録つてから★「空である旨」の一行を書く(裁 seq310228⑶)
 ・行末の空白を落とし・EOF 改行を丁度1本
 ・`.first`/`.second`/`.third`(倒れた走の控)は ★触れぬ★
 ・陽性対照: 己で汚した紙を作り、檢出子が★鳴る★事を先に示してから本番を歩く
"""
import os, shutil, datetime
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_D = {'_gate', '.git'}
SKIP_F = {'_manifest.txt'}
TOMERU = ('.first', '.second', '.third')
LOG = []
def W(x): LOG.append(x); print(x)

W('# 94_kuu ―― 束の全紙を條②③④へ合はせる(刻 %s)'
  % datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
W('# 歩き根 = %s  深さ=無制限(_gate/ と _manifest.txt と *.first は除く)' % os.getcwd())

# ── 陽性対照(檢出子が鳴る事を先に示す) ─────────────
W('')
W('== 陽性対照 ―― 檢出子が★鳴る★事を先に示す ==')
probe = os.path.join('raw', '.94_youseitaishou.tmp')
open(probe, 'w', encoding='utf-8').write('kiyoi\nmatsu ni kuuhaku  \n\n\n')
s = open(probe, encoding='utf-8').read()
t = chr(10).join(l.rstrip() for l in s.split(chr(10))).rstrip(chr(10)) + chr(10)
W('  汚した紙 %r → 整へた %r  : 変つた=%s(★鳴る★)' % (s, t, t != s))
z = os.path.join('raw', '.94_zero.tmp'); open(z, 'w').close()
W('  0 byte の紙 : size=%d → 條④に触れる形である事を確かめた' % os.path.getsize(z))
os.remove(probe); os.remove(z)

# ── 本歩き ──────────────────────────────────────
W('')
W('== 0 byte の紙(真の大きさを録つてから一行を書き入れる) ==')
zeros, fixed, clean, skipped, nonutf = [], [], 0, [], []
for r, ds, ns in os.walk('.'):
    ds[:] = [d for d in ds if d not in SKIP_D]
    for x in sorted(ns):
        p = os.path.normpath(os.path.join(r, x))
        if x in SKIP_F or p.endswith(TOMERU):
            skipped.append(p); continue
        try:
            n = os.path.getsize(p)
        except OSError:
            continue
        if n == 0:
            zeros.append(p)
            open(p, 'w', encoding='utf-8').write(
                '★空である旨★ 本紙は生まれた儘 0 byte であつた(裁 seq310228⑶)\n')
            continue
        # ★疵10★ 初版は UTF-8 で讀めぬ紙を ★黙つて飛ばして居た★(9枚)。控=raw/94_kuu.txt.first
        #   之では「整へた」と「見て居らぬ」が同じ顔になる ―― 正に本弾が咎めて居る形ゆゑ、
        #   讀めぬ紙は ★byte の儘★ 同じ條(末空白落し・CR落し・EOF改行1本)へ掛け、名を挙げる。
        b = open(p, 'rb').read()
        try:
            b.decode('utf-8'); utf = True
        except UnicodeDecodeError:
            utf = False; nonutf.append(p)
        c = b'\n'.join(l.rstrip(b' \t\r') for l in b.split(b'\n')).rstrip(b'\n') + b'\n'
        if c != b:
            if not os.path.exists(p + '.first'):
                shutil.copyfile(p, p + '.first')
            open(p, 'wb').write(c); fixed.append(p + ('' if utf else '  ★UTF-8で讀めぬ紙★'))
        else:
            clean += 1
for p in zeros:
    W('  0 byte → 一行: %s' % p)
W('')
W('== 結 ==')
W('  0 byte であつた紙 = %d 枚(真の大きさは悉く ★0★ ―― 上に名を悉く挙げた)' % len(zeros))
W('  整へた紙(原本→.first) = %d 枚' % len(fixed))
for p in fixed: W('    ' + p)
W('  元より整ふ紙 = %d 枚' % clean)
W('  UTF-8 で讀めぬ紙 = %d 枚(byte の儘 同じ條へ掛けた ―― 飛ばして居らぬ)' % len(nonutf))
for p in nonutf: W('    ' + p)
W('  触れぬ紙(控・臺帳) = %d 枚' % len(skipped))
for p in skipped: W('    ' + p)
open('raw/94_kuu.txt', 'w', encoding='utf-8').write(chr(10).join(LOG) + chr(10))
