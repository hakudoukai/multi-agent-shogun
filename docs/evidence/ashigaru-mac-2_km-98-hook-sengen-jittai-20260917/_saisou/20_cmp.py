#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_cmp.py <束の根> <前sha表> <出目> ―― 再走の「前→後」を byte で突き合はせる。

三つを測る:
  甲 ★前→後★ ―― `_raw/<幹>.<面>` と `_saisou/<幹>.<面>` の sha256 を並べ、同/異 を名指す。
  乙 ★_raw/ の不動★ ―― 再走前に録つた <前sha表> の `_raw/` 行を今の disk と突き合はせる。
       ★之が家老の手順①「sha 不動を證せ」の代りである★。git の路(`git cat-file -p <枝>:<path>`)は
       ★km-98 の束が一つの commit にも入つて居らぬ★ ゆゑ通れぬ ―― 其れが今治す疵の本体である。
       ∴ 此の證は git より弱い(録つたのが己自身)。★其の弱さを紙に書く。★
  丙 ★陽性対照★ ―― 必ず異なる二本(11_hooks_base.tsv と 31_hooks_main.tsv)を同じ路へ通す。
       ★此処が「同」と出たら比較器を疑へ。鳴らぬ対照は対照に非ず。★

数の規律3: 「同」は「器が正しい」を意味せぬ。「同じ入から同じ出が出た」のみを意味する。
"""
import hashlib, os, sys

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def main():
    if len(sys.argv) != 4:
        sys.stderr.write('usage: 20_cmp.py <束の根> <前sha表> <出目>\n'); return 2
    B, ZEN, OUT = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
    S, R = os.path.join(B, '_saisou'), os.path.join(B, '_raw')
    L = ['# 20_cmp.py ―― 再走の前→後', '']

    # 甲
    kan = sorted(f for f in os.listdir(S)
                 if os.path.exists(os.path.join(R, f)))
    L.append('## 甲 前→後(`_raw/` → `_saisou/`)')
    L.append('# name\t前sha256\t後sha256\t前bytes\t後bytes\t判')
    onaji = kotonaru = 0
    for f in kan:
        a, b = os.path.join(R, f), os.path.join(S, f)
        sa, sb = sha(a), sha(b)
        j = '同' if sa == sb else '★異★'
        if sa == sb: onaji += 1
        else: kotonaru += 1
        L.append('%s\t%s\t%s\t%d\t%d\t%s'
                 % (f, sa, sb, os.path.getsize(a), os.path.getsize(b), j))
    L.append('# 突合せた本数=%d / 同=%d / 異=%d' % (len(kan), onaji, kotonaru))
    L.append('')

    # 乙
    L.append('## 乙 `_raw/` の不動(再走前の表と今の disk)')
    zen = {}
    for ln in open(ZEN, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        p, s, n = ln.rstrip('\n').split('\t')
        if p.startswith('_raw/'):
            zen[p] = (s, int(n))
    fudou = ugoita = kieta = []
    fudou, ugoita, kieta = 0, [], []
    for p, (s, n) in sorted(zen.items()):
        ap = os.path.join(B, p)
        if not os.path.exists(ap):
            kieta.append(p); continue
        if sha(ap) == s:
            fudou += 1
        else:
            ugoita.append(p)
    ima = sorted(os.path.relpath(os.path.join(d, f), B)
                 for d, _, fs in os.walk(R) for f in fs)
    L.append('# 前の表に在る `_raw/` の本数=%d' % len(zen))
    L.append('# 今の disk の `_raw/` の本数=%d' % len(ima))
    L.append('# 不動=%d / ★動いた=%d★ / ★消えた=%d★ / ★増えた=%d★'
             % (fudou, len(ugoita), len(kieta), len(set(ima) - set(zen))))
    for p in ugoita: L.append('★動いた★\t%s' % p)
    for p in kieta:  L.append('★消えた★\t%s' % p)
    for p in sorted(set(ima) - set(zen)): L.append('★増えた★\t%s' % p)
    L.append('# 之は git の證に非ず ―― 己が録つた表との突合せである(其の弱さを宣す)')
    L.append('')

    # 丙
    L.append('## 丙 陽性対照(必ず異なる二本を同じ路へ通す)')
    x = os.path.join(S, '11_hooks_base.tsv'); y = os.path.join(S, '31_hooks_main.tsv')
    sx, sy = sha(x), sha(y)
    taisho = '★異★' if sx != sy else '★同(=比較器を疑へ)★'
    L.append('11_hooks_base.tsv\t%s' % sx)
    L.append('31_hooks_main.tsv\t%s' % sy)
    L.append('判=%s' % taisho)
    L.append('# 対照が「異」と出た ∴ 甲・乙 の「同/不動」は ★鳴る路の上で測つた★ 零である')

    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    sys.stderr.write('★甲 %d 本: 同=%d 異=%d / 乙 不動=%d 動=%d 消=%d / 丙 対照=%s★\n'
                     % (len(kan), onaji, kotonaru, fudou, len(ugoita), len(kieta), taisho))
    ng = kotonaru + len(ugoita) + len(kieta) + (0 if sx != sy else 1)
    sys.stderr.write('出目=%s\n' % OUT)
    return 0 if ng == 0 else 6

sys.exit(main())
