# -*- coding: utf-8 -*-
"""58 ★丙 ―― 「測れて居らぬ」の四名を、測れるか否かまで運ぶ器★

家老の見立 丙 は「當席の grep は下流の比較器を見付けられなんだ ∴ ★測れて居らぬ★」。
★「見付けられなんだ」は「無い」ではない。★ ∴ 四名を名指しで歩き、逐語を引く。

歩き根 = scripts/ (生器のみ。控/worktree/退役 は 11 と同じ絞りで落す)
引く物 = 其の名が現れる ★全行★(sh も py も)。註釈は別に数へる。
判ずる = ㋐番人(fix_threshold)が在るか ㋑数の比較器へ入るか
         ㋒別言語(python の int() 等)で受けるか ㋓一度も讀まれぬか
"""
import io, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = '/Users/momizimac/multi-agent-shogun'
NA = ['STALE_SEC', 'POLL_SEC', 'DETECT_STALE_STALE_SEC', 'ER_THRESHOLD_MIN']
OCHI = ('/worktrees/', '/docs/evidence/', '/.git/', '/node_modules/', '/retired/', '/_hikae/')
CMP = re.compile(r'-(?:gt|lt|ge|le|eq|ne)\b')

files = []
for dp, dn, fn in os.walk(ROOT + '/scripts'):
    if any(o in dp + '/' for o in OCHI):
        continue
    for f in fn:
        if f.endswith(('.sh', '.py', '.bash')):
            files.append(os.path.join(dp, f))
files.sort()
assert files, '★歩き根に一本も無い ―― 根が誤つて居る★'

rows = []
for name in NA:
    W = re.compile(r'(?<![A-Za-z0-9_])' + name + r'(?![A-Za-z0-9_])')
    for p in files:
        try:
            L = io.open(p, encoding='utf-8', errors='replace').read().split('\n')
        except Exception as e:
            rows.append([name, p.replace(ROOT + '/', ''), 0, '★讀めず★', str(e)[:80]])
            continue
        for k, t in enumerate(L, 1):
            if not W.search(t):
                continue
            st = t.strip()
            if st.startswith('#'):
                sei = '註釈'
            elif re.search(r'fix_threshold\s+' + name + r'\b', t) or re.search(
                    r'\b' + name + r':\d', t):
                sei = '★番人★'
            elif CMP.search(t) or '((' in t:
                sei = '★数の比較器★'
            elif re.search(r'int\s*\(\s*os\.environ', t) or 'os.environ' in t or 'getenv' in t:
                sei = '★別言語が受ける★'
            elif re.match(r'\s*(export\s+)?' + name + r'=', t) or re.search(
                    r'\$\{' + name + r'[:}-]', t):
                sei = '置く/展く'
            else:
                sei = '他'
            rows.append([name, p.replace(ROOT + '/', ''), k, sei, st[:160]])

K.kaku_tsv(B + '/raw/58_hei.tsv', rows, ['name', 'file', 'line', '性', '逐語'])

s = ['# 58 丙の四名 / 歩き根= scripts/ (%d 本) / 引いた行= %d' % (len(files), len(rows))]
s.append('# 絞り(逐語)= %s' % ' '.join(OCHI))
s.append('')
for name in NA:
    mine = [r for r in rows if r[0] == name]
    c = {}
    for r in mine:
        c[r[3]] = c.get(r[3], 0) + 1
    s.append('■ %s ―― 行= %d  %s' % (name, len(mine), ' / '.join('%s=%d' % kv for kv in sorted(c.items())) or '(一行も無し)'))
    for r in mine:
        s.append('    %-6s %s:%s  %s' % (r[3], r[1], r[2], r[4]))
    s.append('')
K.kaku(B + '/raw/58_hei_summary.txt', '\n'.join(s))
print('\n'.join(x for x in s if x.startswith('■') or x.startswith('#')))
