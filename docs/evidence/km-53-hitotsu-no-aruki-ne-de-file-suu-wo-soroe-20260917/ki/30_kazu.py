#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 30_kazu.py ―― ★定義丁を「一本の歩き根」で数へ直す器★(第53弾 ㋐)
#
# 定義丁の逐語(專任1 第77弾 raw/40_tei.txt より引く):
#   根= scripts .claude(git 追跡 file 全深)
#   條(全)= ERE \$\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\}  1 出現 1 口(一行に複数可)
#   條(閾)= 名が ^[A-Z][A-Z0-9_]*$ ∧ 既定 ≥1 ∧ 註行でない
#           ―― ★「閾らしき」は此の條で置き換へた(語感で数へぬ)★
#
# 使ひ方:
#   30_kazu.py --gen disk|index|<rev> [--ne "scripts .claude"] [--tan occ|line]
#              [--kitei 1|0] [--chu nuku|komu]
# 出目: 頭に 根/深さ/源/除外(宣)/條/刻/rc、次に [丁閾] 總數、次に file毎内訳表、次に員外。
import sys, os, re, subprocess, time

def sh(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = p.communicate()
    return p.returncode, o, e

gen = None; ne = u'scripts .claude'; tan = u'occ'; kitei = 1; chu = u'nuku'
av = sys.argv[1:]
i = 0
while i < len(av):
    a = av[i]
    if a == '--gen' and i + 1 < len(av): gen = av[i+1]; i += 2; continue
    if a == '--ne' and i + 1 < len(av): ne = av[i+1]; i += 2; continue
    if a == '--tan' and i + 1 < len(av): tan = av[i+1]; i += 2; continue
    if a == '--kitei' and i + 1 < len(av): kitei = int(av[i+1]); i += 2; continue
    if a == '--chu' and i + 1 < len(av): chu = av[i+1]; i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % a); sys.exit(2)
if gen is None:
    sys.stderr.write(u'★測れぬ: --gen を argv で渡せ(disk|index|<rev>)★\n'); sys.exit(2)
roots = ne.split()

ZEN = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):-([0-9]+)\}')
SHIKII_NA = re.compile(r'^[A-Z][A-Z0-9_]*$')

rcs = []
# ★疵(本弾で踏んだ)★ `git ls-files -- scripts .claude` の path 指定は ★cwd 相対★ ゆゑ、
#   束の中(docs/evidence/...)から呼ぶと一つも当たらず、rc=0 の儘 ★口 0 / file 0★ を返した。
#   ∴ ⑴歩き根を repo 頂へ固定し ⑵歩いた file が 0 なら「測れぬ」で倒す(黙つて零を返さぬ)。
rc_top, o_top, e_top = sh(['git', 'rev-parse', '--show-toplevel'])
if rc_top != 0 or not o_top.strip():
    sys.stderr.write(u'★測れぬ: repo の頂が引けぬ(rev-parse rc=%d)★\n' % rc_top); sys.exit(3)
itadaki = o_top.strip().decode('utf-8')
os.chdir(itadaki)
rcs.append(('rev-parse --show-toplevel', rc_top))
# ―― 源から「path → bytes」を引く。歩き根は一本、深さは全深(git が追跡する全 path)。
bunsho = []   # (path, bytes or None)
if gen == 'disk':
    rc, o, e = sh(['git', 'ls-files', '-z', '--'] + roots); rcs.append(('ls-files', rc))
    for p in o.split(b'\x00'):
        if not p: continue
        path = p.decode('utf-8', 'surrogateescape')
        try:
            with open(path, 'rb') as fh: bunsho.append((path, fh.read()))
        except Exception:
            bunsho.append((path, None))
elif gen == 'index':
    rc, o, e = sh(['git', 'ls-files', '-s', '-z', '--'] + roots); rcs.append(('ls-files -s', rc))
    for row in o.split(b'\x00'):
        if not row: continue
        try:
            meta, path = row.split(b'\t', 1)
            blob = meta.split()[1]
        except Exception:
            continue
        rc2, o2, e2 = sh(['git', 'cat-file', 'blob', blob.decode('ascii')])
        bunsho.append((path.decode('utf-8', 'surrogateescape'), o2 if rc2 == 0 else None))
else:
    rc, o, e = sh(['git', 'ls-tree', '-r', '-z', '--full-tree', gen, '--'] + roots)
    rcs.append(('ls-tree', rc))
    for row in o.split(b'\x00'):
        if not row: continue
        try:
            meta, path = row.split(b'\t', 1)
            f = meta.split()
            if f[1] != b'blob': continue
            blob = f[2]
        except Exception:
            continue
        rc2, o2, e2 = sh(['git', 'cat-file', 'blob', blob.decode('ascii')])
        bunsho.append((path.decode('utf-8', 'surrogateescape'), o2 if rc2 == 0 else None))

yomenu = []
uchi = {}      # path -> [(name, default, lineno, line)] 丁閾に当たる物
ingai = {}     # path -> [(name, default, lineno, riyuu)]
zen_kuchi = 0

for path, data in sorted(bunsho):
    if data is None:
        yomenu.append((path, u'開けぬ/引けぬ')); continue
    try:
        text = data.decode('utf-8')
    except Exception:
        yomenu.append((path, u'非UTF-8(復号不能)')); continue
    lines = text.split(u'\n')
    seen_line = set()
    for ln, line in enumerate(lines, 1):
        is_chu = line.lstrip().startswith(u'#')
        for m in ZEN.finditer(line):
            zen_kuchi += 1
            name, dflt = m.group(1), m.group(2)
            riyuu = []
            if not SHIKII_NA.match(name): riyuu.append(u'名が大文字條に非ず')
            if int(dflt) < kitei: riyuu.append(u'既定 %s < %d' % (dflt, kitei))
            if chu == 'nuku' and is_chu: riyuu.append(u'註行')
            if riyuu:
                ingai.setdefault(path, []).append((name, dflt, ln, u'+'.join(riyuu)))
                continue
            if tan == 'line':
                if ln in seen_line: continue
                seen_line.add(ln)
            uchi.setdefault(path, []).append((name, dflt, ln, line.strip()))

kuchi = sum(len(v) for v in uchi.values())
fsuu = len(uchi)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
w = sys.stdout.write
w(u'# 30_kazu ―― 定義丁の数へ直し / 刻= %s\n' % koku)
w(u'# ★根(歩き根 一本)= %s★ / 深さ= 全深(git 追跡の全 path・上限無し)\n' % ne)
if len(bunsho) == 0:
    sys.stderr.write(u'\u2605\u6e2c\u308c\u306c: \u6b69\u3044\u305f file \u304c 0 \u3067\u3042\u308b(\u6839=%s / \u9802=%s / gen=%s) \u2015\u2015 \u9ed9\u3064\u3066\u96f6\u3092\u8fd4\u3055\u306c\u2605\n'
                     % (ne, itadaki, gen)); sys.exit(3)
w(u'# \u9802(\u6b69\u304d\u6839\u306e\u57fa\u70b9)= %s\n' % itadaki)
w(u'# 源= %s / 歩いた file= %d / 讀めぬ file= %d\n' % (gen, len(bunsho), len(yomenu)))
w(u'# 除外(宣)= ①git 非追跡の物(.claude/worktrees/ 配下の別 checkout・*.bak 控 等)は根に入らぬ\n')
w(u'#           ②非UTF-8 は「讀めぬ」として別行に数へる(黙つて落とさぬ)\n')
w(u'#           ③本器は docs/evidence/ に在り根の外ゆゑ己を数へぬ(★宣して除く★)\n')
w(u'# 條(全)= \\$\\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\\} / 單位= %s / 註= %s / 既定閾= >=%d\n'
  % (tan, chu, kitei))
w(u'# 條(閾)= 名 ^[A-Z][A-Z0-9_]*$ ∧ 既定 >=%d ∧ 註行に非ず\n' % kitei)
w(u'# rc= %s\n' % u' '.join(u'%s:%d' % (k, v) for k, v in rcs))
w(u'# 條(全)に当たつた口(閾を問はず)= %d\n' % zen_kuchi)
w(u'\n★[丁閾] 口= %d  file= %d★\n' % (kuchi, fsuu))
w(u'\n--- file毎内訳(file / 口數 / 名) ---\n')
for path in sorted(uchi):
    na = u' '.join(u'%s:-%s@%d' % (n, d, l) for n, d, l, _ in uchi[path])
    w(u'%s\t%d\t%s\n' % (path, len(uchi[path]), na))
w(u'\n--- 員外(條(全)に当たるが條(閾)で落ちた口) ---\n')
if not ingai:
    w(u'(員外 無し)\n')
for path in sorted(ingai):
    na = u' '.join(u'%s:-%s@%d(%s)' % (n, d, l, r) for n, d, l, r in ingai[path])
    w(u'%s\t%d\t%s\n' % (path, len(ingai[path]), na))
w(u'\n--- 讀めぬ file ---\n')
if not yomenu:
    w(u'(讀めぬ file 無し)\n')
for path, why in yomenu:
    w(u'%s\t%s\n' % (path, why))
sys.exit(0)
