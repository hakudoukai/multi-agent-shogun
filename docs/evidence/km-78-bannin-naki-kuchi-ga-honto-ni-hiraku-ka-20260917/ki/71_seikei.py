# -*- coding: utf-8 -*-
"""71 形を整へる器 ―― ★中身は一字も変へぬ。変へるのは「空」と「末尾の空白」だけ★

  甲 0byte …… 作法⑸「空は 0byte でなく ★空である旨の一行★」
  乙 末尾空白 …… 末尾が TAB なら ★空欄が在る★ ゆゑ `-` を置いて欄数を保つ。
                  末尾が空白なら ★何も担つて居らぬ★ ゆゑ剥ぐ。
  ★何を触れたかを悉く raw/71_seikei.txt に刷る。★
"""
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = '\t'
rec = ['# 71 形を整へた覚 ―― ★測つた値は一つも変へて居らぬ★', '']
kara, sue = [], []
for root, ds, fs in os.walk(B):
    ds[:] = [d for d in ds if d not in ('_gate', '__pycache__')]
    for f in sorted(fs):
        p = os.path.join(root, f)
        r = os.path.relpath(p, B)
        if r == 'manifest.txt' or f.endswith('.pyc'):
            continue
        if os.path.getsize(p) == 0:
            kara.append(r)
            continue
        try:
            t = io.open(p, encoding='utf-8').read()
        except UnicodeDecodeError:
            continue
        L = t.split('\n')
        n = 0
        for i, l in enumerate(L):
            if l and l[-1] in ' \t':
                n += 1
                L[i] = (l + '-') if l[-1] == TAB else l.rstrip(' \t')
        if n:
            sue.append((r, n))
            K.kaku(p, '\n'.join(L))

rec.append('■ 甲 0byte ―― 「空である旨の一行」を据ゑた: %d本' % len(kara))
for r in kara:
    rec.append('    %s' % r)
    K.kaku(B + '/' + r, '★空である★ ―― 此の器は何も吐かなんだ(0byte ではなく此の一行を以て空を示す・作法⑸)')
rec.append('')
rec.append('■ 乙 末尾空白 ―― 剥いだ / 欄を `-` で保つた: %d本' % len(sue))
for r, n in sue:
    rec.append('    %s  %d行' % (r, n))
rec.append('')
rec.append('★断り★ `.first` を含むのは 作法⑺(倒れた走を消すな)に反せぬ ―― 消して居らぬ。')
rec.append('        形だけを整へた。倒れた走の ★値★ は其の儘である。')
K.kaku(B + '/raw/71_seikei.txt', '\n'.join(rec))
print('甲 0byte=%d / 乙 末尾空白=%d本' % (len(kara), len(sue)))
