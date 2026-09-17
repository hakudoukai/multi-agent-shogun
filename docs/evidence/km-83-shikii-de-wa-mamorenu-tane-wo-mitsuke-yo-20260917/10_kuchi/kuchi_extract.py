#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kuchi_extract.py ―― 三file の ★口★ を全数で挙げる器。

★口★ の定義は ★一つではない★。同じ語で違ふ物を数へれば數は食ひ違ふ。
故に此の器は ★四つの定義を別欄で刷る★(単位を欄名へ焼く)。

  定義甲 kuchi_name_with_default : ${NAME:-既定} を持つ ★相異なる名★ の數
  定義乙 kuchi_occ_with_default  : ${NAME:-既定} の ★出現箇所★ の數(同名再出も数へる)
  定義丙 kuchi_name_all_expand   : 展開される ★相異なる名★ の數(既定の有無を問はず)
  定義丁 kuchi_occ_all_expand    : 展開の ★出現箇所★ の數

用法: kuchi_extract.py <file> [<file>...]
返り値: 0=挙げた / 2=引数の誤り / 4=対象が無い
"""
import re
import sys

# ${NAME:-既定} / ${NAME:=既定} / ${NAME-既定}  (NAME は英数_ か 数字=位置引数)
RE_DEF = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*|[0-9]+)(:?[-=])([^}]*)\}')
# ${NAME} / ${NAME[..]} / $NAME  (既定無しも含む全展開)
RE_BRACE = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*|[0-9]+|[*@?#])([^}]*)\}')
RE_BARE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*|[0-9]|[*@?#])')


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    paths = sys.argv[1:]
    grand = {'kou': 0, 'otsu': 0, 'hei': 0, 'tei': 0}
    for p in paths:
        try:
            with open(p, encoding='utf-8') as fh:
                lines = fh.read().split('\n')
        except OSError as e:
            sys.stderr.write('★対象が無い★ %s: %s\n' % (p, e))
            return 4
        name_def, occ_def = {}, []
        name_all, occ_all = {}, []
        for i, ln in enumerate(lines, 1):
            for m in RE_DEF.finditer(ln):
                nm, op, dv = m.group(1), m.group(2), m.group(3)
                name_def.setdefault(nm, []).append(i)
                occ_def.append((i, nm, op, dv, ln.strip()))
            for m in RE_BRACE.finditer(ln):
                nm = m.group(1)
                name_all.setdefault(nm, []).append(i)
                occ_all.append((i, nm))
            for m in RE_BARE.finditer(ln):
                nm = m.group(1)
                name_all.setdefault(nm, []).append(i)
                occ_all.append((i, nm))
        print('########## %s (行=%d) ##########' % (p, len(lines)))
        print('--- 定義乙: ${NAME:-既定} の出現箇所 一覧(行番/名/演算子/既定/逐語) ---')
        for (i, nm, op, dv, raw) in occ_def:
            print('L%-4d %-34s op=%-2s 既定=%r' % (i, nm, op, dv))
            print('        逐語: %s' % raw)
        print('--- 定義丙: 展開される相異なる名(既定の有無を問はず) ---')
        for nm in sorted(name_all):
            print('  %-36s 出現行=%s' % (nm, ','.join(str(x) for x in name_all[nm])))
        print('==> kuchi_name_with_default=%d  kuchi_occ_with_default=%d'
              '  kuchi_name_all_expand=%d  kuchi_occ_all_expand=%d'
              % (len(name_def), len(occ_def), len(name_all), len(occ_all)))
        print()
        grand['kou'] += len(name_def)
        grand['otsu'] += len(occ_def)
        grand['hei'] += len(name_all)
        grand['tei'] += len(occ_all)
    print('########## 三file 合計 ##########')
    print('定義甲 kuchi_name_with_default = %d   ← ★家老の「口」に最も近い★' % grand['kou'])
    print('定義乙 kuchi_occ_with_default  = %d' % grand['otsu'])
    print('定義丙 kuchi_name_all_expand   = %d   (註: file 毎の和ゆゑ file 跨ぎの同名は重複計上)' % grand['hei'])
    print('定義丁 kuchi_occ_all_expand    = %d' % grand['tei'])
    return 0


sys.exit(main())
