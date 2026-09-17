# -*- coding: utf-8 -*-
"""㋐ ―― 宣・直し・比較器の三点を ★逐語で引き直す★(家老の与へた行番は使はぬ)。
usage: (cd <束> && python3 ki/30_sanden.py)
出目は raw/30_sanden.txt へ。★行番は己で引く★ ―― 家老の値との差も刷る。
"""
import os, sys, io
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KARO = {'宣': (251, 253), '直し': (258, 258), '比較器': (1633, 1633)}
VERS = ['kyuu', 'index', 'shin', 'hashiru_kouho']
NAME = 'ASW_PROCESS_TIMEOUT'

print('★㋐ 宣・直し・比較器 ―― 逐語で引き直す★')
print('引き方=「%s」を含む行を悉く出し、役を字面で判じる。' % NAME)
print('  宣    = 行頭が "#" で、値の意味を述べる註')
print('  受け口= 変数へ値を入れる行(旧 `NAME=${NAME:-既定}` / 新 `fix_flag NAME 既定 NAME`)')
print('  比較器= `[ ... = "1" ]` の形で枝を分ける行')
print('  註    = 上の三つの何れでもない註(直しの説明など)')
print('')
for v in VERS:
    p = 'ki/%s.sh' % v
    src = open(p, encoding='utf-8').read()
    L = src.split('\n')
    # ★末尾改行で split は空の尾を一つ生む ―― 行数はそれを除いて数へる★
    nrow = len(L) - 1 if src.endswith('\n') else len(L)
    hits = [(i + 1, l) for i, l in enumerate(L) if NAME in l]
    print('══ %s (%d 行) ―― 当たり %d 本 ══' % (v, nrow, len(hits)))
    for n, l in hits:
        t = l.strip()
        if t.startswith('#') and ('=0' in t or '=1' in t) and 'do not process' in t:
            役 = '宣'
        elif t.startswith('#'):
            役 = '註'
        elif t.startswith('fix_flag ') or t.startswith(NAME + '='):
            役 = '受け口'
        elif '= "1" ]' in t:
            役 = '比較器'
        else:
            役 = '★判じ得ぬ★'
        print('  %-6s L%-5d| %s' % (役, n, l))
    print('')

print('★家老の与へた行番との差(的=shin)★')
L = open('ki/shin.sh', encoding='utf-8').read().split('\n')
hits = [(i + 1, l) for i, l in enumerate(L) if NAME in l]
mine = {}
for n, l in hits:
    t = l.strip()
    if t.startswith('#') and 'do not process' in t: mine['宣'] = n
    elif t.startswith('fix_flag '): mine['直し'] = n
    elif '= "1" ]' in t: mine['比較器'] = n
for k in ('宣', '直し', '比較器'):
    a, b = KARO[k]
    m = mine.get(k)
    if a == b:
        s = '家老=L%d' % a
        ok = (m == a)
    else:
        s = '家老=L%d-%d' % (a, b)
        ok = (m is not None and a <= m <= b)
    print('  %-6s %s / 己=L%s → %s' % (k, s, m, '合ふ' if ok else '★違ふ★'))
print('')
print('★家老が「L251-253」と書いた幅の中身★ ―― 251/252 は何の行か')
for n in (251, 252, 253):
    print('  L%d| %s' % (n, L[n - 1]))
