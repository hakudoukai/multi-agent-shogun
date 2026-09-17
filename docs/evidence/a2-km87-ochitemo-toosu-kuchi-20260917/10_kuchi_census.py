# -*- coding: utf-8 -*-
"""★落ちても値が出る口★ の母數を、字面の方言ごとに排他で数へる。
使ひ方: python3 -B 10_kuchi_census.py <target.sh>
★己の判定は stdout・數は末尾に刷る。0 でも一行出す。★"""
import sys, re, hashlib

if len(sys.argv) < 2:
    sys.stderr.write('usage: 10_kuchi_census.py <target.sh>\n'); sys.exit(2)
p = sys.argv[1]
b = open(p, 'rb').read()
print('的 path = %s' % p)
print('的 sha16 = %s' % hashlib.sha256(b).hexdigest()[:16])
lines = b.decode('utf-8').split('\n')
# ★wc -l は改行の数。末尾に改行が在れば split は空の尾を生む★
print('行(改行数 = wc -l 相当) = %d' % b.count(b'\n'))
print('split 片 = %d (末尾空片 = %s)' % (len(lines), lines[-1] == ''))

# ─── python -c "..." の中(=非 shell)の帯を、逐語で当てる ───
PY_OPEN = 'python3 -c "'
py_band = set()
for i, L in enumerate(lines, 1):
    if L.strip() == PY_OPEN.strip() or L.rstrip().endswith(PY_OPEN):
        # 開き。閉ぢは行頭が `"` の行
        for j in range(i + 1, len(lines) + 1):
            if lines[j - 1].startswith('"'):
                break
            py_band.add(j)
print('非shell帯(python -c の胴) = %s' % (sorted(py_band) if py_band else '無'))

def is_comment(L):
    return L.lstrip().startswith('#')

# ─── 方言(排他に当てる: 優先順で一片一札) ───
DIALECTS = [
    ('甲a_or_true',   re.compile(r'\|\|\s*true\b')),
    ('甲b_or_echo',   re.compile(r'\|\|\s*echo\b')),
    ('甲c_or_colon',  re.compile(r'\|\|\s*:\s*$')),
    ('乙a_2devnull',  re.compile(r'2>\s*/dev/null')),
    ('乙b_amp_devnull', re.compile(r'&>\s*/dev/null')),
    ('丙a_colon_dash', re.compile(r'\$\{[A-Za-z_][A-Za-z0-9_]*:-')),
]
hits = {}   # (line, dialect) -> text
for i, L in enumerate(lines, 1):
    if i in py_band:      continue
    if is_comment(L):     continue
    for name, rx in DIALECTS:
        for m in rx.finditer(L):
            hits[(i, name, m.start())] = L.strip()

print('')
print('=== 方言別 出目(註と非shell帯を除く) ===')
per = {}
for (i, name, col), txt in sorted(hits.items()):
    per.setdefault(name, []).append((i, col, txt))
for name, _rx in DIALECTS:
    v = per.get(name, [])
    print('--- %s : %d 片 ---' % (name, len(v)))
    for i, col, txt in v:
        print('  L%-4d col%-3d | %s' % (i, col, txt[:150]))
    if not v:
        print('  (0 片)')

# ─── 排他性: 同じ行に二方言が乗るか ───
byline = {}
for (i, name, col) in hits:
    byline.setdefault(i, set()).add(name)
multi = {i: sorted(s) for i, s in byline.items() if len(s) > 1}
print('')
print('=== 排他性 ===')
print('片の総和 = %d' % len(hits))
print('片を持つ行 = %d' % len(byline))
print('二方言以上が乗る行 = %d %s' % (len(multi), multi if multi else ''))

# ─── exit の口(註と非shell帯を除く実の exit) ───
print('')
print('=== 実の exit(註・非shell帯を除く) ===')
ex = []
for i, L in enumerate(lines, 1):
    if i in py_band or is_comment(L): continue
    if re.search(r'(^|[;&|]|\s)exit\b', L):
        ex.append((i, L.strip()))
for i, t in ex:
    print('  L%-4d | %s' % (i, t))
print('実の exit = %d 口' % len(ex))
# 註の中の exit も別に数へる(見分けの為)
exc = sum(1 for L in lines if is_comment(L) and re.search(r'\bexit\b', L))
print('註の中の exit = %d (母數の外)' % exc)
