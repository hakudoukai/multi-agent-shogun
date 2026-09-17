#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 30_kessai.py ―― 第52弾 ㋐ の決算器。
#
# ★測る物★ 「閾を読む箇所」の内、★guard(fix_threshold)を通る側★ の母數を
#   ★凍結点 6dbe09e6 の樹★ で確定し、同じ物差で ★disk(HEAD 作業樹)★ も測つて並べる。
#   ―― 家老mac 第52弾 ㋐②「6file/20箇所 が再現するか」への答を作る器である。
#
# ★判定条件(逐語・㋐①)★
#   甲 file は 凍結点の樹(又は git ls-files)に在り、docs/evidence/ の下に無い。
#   乙 其の file 内に ★`fix_threshold <名> <既定> <受皿>` の呼★ が在る。
#      呼の引数が `"$_n" "$_d" "$_n"` の形(loop 呼)である時は、
#      直前の `for _t in NAME:DEF …` の一覧を展開して ★名の一本一本★ を数へる。
#      ―― 之が「閾を読む箇所」の ★guard 側★ の定義である。單位=(file, 環境変数名)。
#   丙 其の名か其の受皿が、同 file 内で ★数値比較器の項★ に立つか否かを別欄で刷る。
#      数値比較器 = `項 -eq|-ne|-lt|-le|-gt|-ge 項`(test/[/[[) 及び `(( … ))` / `$(( … ))` の中。
#      ★丙は母數を削らぬ★ ―― 「読む箇所」と「比較へ渡る箇所」は別の數であり、両方刷る。
#
# ★之が数へぬ物★ 素で比べる箇所(guard を通らぬ側)。其れは 23_bosuu4.py が数へて居る。
import sys, io, os, re, subprocess, json

FREEZE = '6dbe09e6'
ROOT   = '/Users/momizimac/multi-agent-shogun'

RE_CALL  = re.compile(r'^[ \t]*fix_threshold[ \t]+(\S+)[ \t]+(\S+)[ \t]+(\S+)')
RE_FORT  = re.compile(r'^[ \t]*for[ \t]+_t[ \t]+in[ \t]+(.*)$')
RE_OPS   = re.compile(r'(?:\[\[?|\btest\b)(.*?)(?:\]\]?|$)')
RE_CMP   = re.compile(r'(\S+)[ \t]+-(?:eq|ne|lt|le|gt|ge)[ \t]+(\S+)')
RE_ARITH = re.compile(r'\(\(([^()]*)\)\)')

def ident(tok):
    """`"$FOO"` `${FOO:-1}` `$FOO` `FOO` から識別子を悉く取る。"""
    out = set()
    for m in re.finditer(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', tok): out.add(m.group(1))
    for m in re.finditer(r'(?<![A-Za-z0-9_$])([A-Za-z_][A-Za-z0-9_]*)(?![A-Za-z0-9_])', tok): out.add(m.group(1))
    return out

def cmp_operands(line):
    """其の行で ★比較器の項★ に立つ識別子の集合。"""
    s = set()
    for m in RE_CMP.finditer(line):
        s |= ident(m.group(1)); s |= ident(m.group(2))
    for m in RE_ARITH.finditer(line):
        s |= ident(m.group(1))
    return s

def files_at(rev):
    if rev == 'DISK':
        o = subprocess.run(['git','ls-files'], cwd=ROOT, capture_output=True, text=True)
    else:
        o = subprocess.run(['git','ls-tree','-r','--name-only',rev], cwd=ROOT, capture_output=True, text=True)
    if o.returncode != 0:
        sys.stderr.write(u'★測れぬ: ls rc=%d★\n' % o.returncode); sys.exit(3)
    return [p for p in o.stdout.split('\n') if p and not p.startswith('docs/evidence/')]

def text_of(rev, path):
    if rev == 'DISK':
        fp = os.path.join(ROOT, path)
        if not os.path.isfile(fp): return None
        try: return io.open(fp, encoding='utf-8', errors='replace').read()
        except Exception: return None
    o = subprocess.run(['git','show','%s:%s' % (rev,path)], cwd=ROOT, capture_output=True, text=True)
    return o.stdout if o.returncode == 0 else None

def census(rev):
    rows = []
    for path in files_at(rev):
        t = text_of(rev, path)
        if t is None or 'fix_threshold' not in t: continue
        L = t.split('\n')
        pend = []                      # 直前の for _t in … の一覧
        for i, l in enumerate(L, 1):
            m = RE_FORT.match(l)
            if m:
                buf, j = m.group(1), i
                while buf.rstrip().endswith('\\') and j < len(L):
                    buf = buf.rstrip()[:-1] + ' ' + L[j]; j += 1
                pend = [w for w in buf.replace(';',' ').split() if ':' in w and not w.startswith('$')]
                continue
            c = RE_CALL.match(l)
            if not c: continue
            n, d, o = c.group(1), c.group(2), c.group(3)
            if n.startswith('"$') or n.startswith('$'):        # loop 呼
                for w in pend:
                    nm, df = w.split(':', 1)
                    rows.append({'file':path,'decl':i,'name':nm,'def':df,'recv':nm,'kata':'loop'})
            else:
                rows.append({'file':path,'decl':i,'name':n,'def':d,'recv':o,'kata':'literal'})
        # 丙: 比較器の項
        for r in rows:
            if r['file'] != path or 'cmp' in r: continue
            hit = []
            for i, l in enumerate(L, 1):
                if i == r['decl']: continue
                ops = cmp_operands(l)
                if r['name'] in ops or r['recv'] in ops: hit.append(i)
            r['cmp'] = hit
    return rows

def show(rev, tag, rows):
    fs = sorted(set(r['file'] for r in rows))
    withcmp = [r for r in rows if r['cmp']]
    print(u'')
    print(u'━━ %s (%s) ━━' % (tag, rev))
    print(u'  ★宣言(乙)= %d 箇所 / %d file★   ★内 比較器に立つ(丙)= %d 箇所★   立たぬ= %d'
          % (len(rows), len(fs), len(withcmp), len(rows)-len(withcmp)))
    for f in fs:
        rr = [r for r in rows if r['file'] == f]
        print(u'  ── %s  (%d)' % (f, len(rr)))
        for r in sorted(rr, key=lambda x: x['decl']):
            c = ','.join(str(x) for x in r['cmp']) if r['cmp'] else u'★比較器に立たぬ★'
            print(u'     %s:%d  %-28s 既定=%-10s 受皿=%-22s 比較行=%s'
                  % (f, r['decl'], r['name'], r['def'], r['recv'], c))
    return rows, fs, withcmp

fz, dk = census(FREEZE), census('DISK')
print(u'★第52弾 ㋐ 決算 ―― guard(fix_threshold)を通る閾の母數★')
print(u'凍結点=%s ／ 器=ki/30_kessai.py ／ 單位=(file, 環境変数名)' % FREEZE)
show(FREEZE, u'凍結点の樹', fz)
show('DISK',  u'disk(HEAD 作業樹)', dk)

kf = set((r['file'],r['name']) for r in fz)
kd = set((r['file'],r['name']) for r in dk)
print(u'')
print(u'━━ 凍結点 ⇔ disk の差 ━━')
for k in sorted(kd - kf): print(u'  ＋disk のみ: %s  %s' % k)
for k in sorted(kf - kd): print(u'  −凍結点のみ: %s  %s' % k)
if kd == kf: print(u'  差 無し(同一集合)')
json.dump({'freeze':fz,'disk':dk}, io.open('nama/30_kessai.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=1)
sys.stderr.write(u'★決算 了 凍結点=%d/%dfile disk=%d/%dfile★\n'
                 % (len(fz), len(set(r['file'] for r in fz)),
                    len(dk), len(set(r['file'] for r in dk))))
