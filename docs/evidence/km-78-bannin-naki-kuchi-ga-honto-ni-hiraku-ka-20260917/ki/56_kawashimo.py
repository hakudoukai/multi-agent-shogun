# -*- coding: utf-8 -*-
"""56 ★川下の比較器を口ごとに引く器★ + ★版ずれの検出★

㋔ の欄「何が抜けるか」は ★読みではなく 川下の逐語★ から起す。
∴ ①fail-open の口 一つ一つに就いて、其の名を ★数の比較器★ に食はせて居る行を
   生器から引き、逐語で刷る。引けなんだ口は「★川下 無し★」と書く(黙るな)。

★併せて版を検む★ ―― stop_hook_inbox.sh は本弾の最中に他席が書き換へた。
   53 の行番号が今の disk と合ふか否かを口ごとに刷る。合はぬ物は数に入れぬ。
"""
import hashlib, io, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = '/Users/momizimac/multi-agent-shogun'

def sha16(p):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    n = sum(1 for _ in io.open(p, 'rb'))
    return h, n

# ―― 00 の凍結を読む
freeze = {}
for ln in io.open(B + '/raw/00_start.txt', encoding='utf-8'):
    m = re.match(r'^([0-9a-f]{16})\t(\d+)行\t(\S+)$', ln.rstrip('\n'))
    if m:
        freeze[m.group(3)] = (m.group(1), int(m.group(2)))

rows53 = [l.rstrip('\n').split('\t') for l in io.open(B + '/raw/53_saihyou.tsv', encoding='utf-8')]
hdr = rows53[0]
i_file, i_line, i_name, i_yurai, i_fuda = hdr.index('file'), hdr.index('line'), hdr.index('name'), hdr.index('由来'), hdr.index('札')
targets = [r for r in rows53[1:] if r[i_fuda] == '①fail-open']
assert targets, '★53 に ①fail-open が一つも無い ―― 器か入力が壊れて居る★'

# 数の比較器: [ ... -gt ... ] 等 / (( )) / test
CMP = re.compile(r'-(?:gt|lt|ge|le|eq|ne)\b')

cache = {}
def lines_of(rel):
    if rel not in cache:
        cache[rel] = io.open(ROOT + '/' + rel, encoding='utf-8', errors='replace').read().split('\n')
    return cache[rel]

out = []
zure = 0
nashi = 0
for r in targets:
    rel, lno, name, yurai = r[i_file], int(r[i_line]), r[i_name], r[i_yurai]
    L = lines_of(rel)
    cur = L[lno - 1] if 0 < lno <= len(L) else ''
    ok = '一致' if name in cur else '★ずれ★'
    if ok != '一致':
        zure += 1
    # ★初走の疵★: k == lno を飛ばして居た。然れど `if [ "${N:-0}" -eq 0 ]` の如く
    #   ★口の行 其れ自身が比較器★ である事が多い。之を除けば「川下 無し」が 9 口 立ち、
    #   ★測れて居る物を測れて居らぬと書く★ 事に成る。∴ 自身も引き、其の旨を欄に刷る。
    # ★二走目の疵 二つ★(共に本器の物):
    #  甲 `name in t` は ★字面の部分一致★ ―― 名 `n` は殆ど全行に当たり、
    #     `COUNT` は `INSERT_COUNT` / `_AMP_PATTERN_COUNT` に食はれた。∴ 語の境で括る。
    #  乙 ★註釈の行★ を比較器として拾つた(序22 が `#   20桁の…` を引いた)。
    #     註釈は走らぬ ∴ 頭が # の行は除く。
    W = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(name) + r'(?![A-Za-z0-9_])')
    hits = []
    for k, t in enumerate(L, 1):
        if t.lstrip().startswith('#'):
            continue
        if not W.search(t):
            continue
        if CMP.search(t) or '((' in t:
            hits.append((k, t.strip(), '★口の行 自身★' if k == lno else '川下'))
    if not hits:
        nashi += 1
        out.append([rel, lno, name, yurai, ok, '-', '無', '★数の比較器に一度も入らぬ★'])
    for k, t, where in hits:
        out.append([rel, lno, name, yurai, ok, k, where, t])

K.kaku_tsv(B + '/raw/56_kawashimo.tsv', out,
           ['file', 'line', 'name', '由来', '版', '比較器行', '所', '比較器逐語'])

# ―― 版の再測(凍結との差)
ver = []
for rel, (h0, n0) in sorted(freeze.items()):
    h1, n1 = sha16(ROOT + '/' + rel)
    ver.append('%s %s %d行 → %s %d行  %s' % (
        rel, h0, n0, h1, n1, '不変' if (h0, n0) == (h1, n1) else '★動いた★'))

kumi = sorted(set((r[0], r[2]) for r in out))
s = []
s.append('# 56 川下の比較器 / ①fail-open の口 %d / 相異なる(file,name) %d 組' % (len(targets), len(kumi)))
s.append('# ★版★ 53 の行番号が今の disk と合ふ口= %d / 合はぬ口= %d' % (len(targets) - zure, zure))
s.append('# ★数の比較器に一度も入らぬ口(口の行 自身も含めて 無し)= %d★' % nashi)
s.append('')
s.append('# ―― 組ごとの川下(逐語・重複は畳む)')
for f, n in kumi:
    hs = sorted(set((str(r[5]), r[6], r[7]) for r in out if r[0] == f and r[2] == n), key=lambda x: (len(x[0]), x[0]))
    s.append('  %s  %s' % (f, n))
    for k, where, t in hs:
        s.append('      %s%s: %s' % (k, '' if where == '川下' else '(自身)', t[:150]))
s.append('')
s.append('# ―― 版の再測(00 の凍結 → 今)')
s.extend('  ' + v for v in ver)
K.kaku(B + '/raw/56_kawashimo_summary.txt', '\n'.join(s))
print('\n'.join(s[:4]))
print('...書いた: raw/56_kawashimo.tsv (%d 行) / raw/56_kawashimo_summary.txt' % len(out))
