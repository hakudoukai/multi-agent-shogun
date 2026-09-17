#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kuchi_extract2.py ―― 口を挙げ、★註(comment)と実(code)を分けて★刷る器。

v1 の疵: `${VAR:-default}` が ★註の中★ に在つても口として数へた。
         其の一つが家老の 21 と當席の 20 の差である ―― 數が合ふ事は正しさではない。

★註の見分け方(heuristic・限界を併記する)★:
  行を頭から嘗め、'…' と "…" の中か否かを追ひ、★括りの外に在る # ★ を註の起しとする。
  限界: heredoc 本文・`$(( ))` 内の # ・行継続で跨いだ括りは見分けられぬ。
        三file には heredoc が無い事を別途 grep で示す(陰性対照)。

用法: kuchi_extract2.py <file> [<file>...]
      kuchi_extract2.py --selftest    ★両対照★(註の口/実の口)を己で走らせる
返り値: 0=挙げた / 2=引数の誤り / 4=対象が無い / 5=selftest が落ちた
"""
import re
import sys

RE_DEF = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*|[0-9]+)(:?[-=])([^}]*)\}')


def comment_start(ln):
    """括りの外の # の位置を返す。無ければ None。"""
    q = None
    for i, ch in enumerate(ln):
        if q:
            if ch == q:
                q = None
            elif ch == '\\' and q == '"':
                pass
        elif ch in ('"', "'"):
            q = ch
        elif ch == '#':
            if i == 0 or ln[i - 1] in ' \t':
                return i
    return None


def scan(path):
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    jitsu, chuu = [], []
    for i, ln in enumerate(lines, 1):
        c = comment_start(ln)
        for m in RE_DEF.finditer(ln):
            rec = (i, m.group(1), m.group(2), m.group(3), ln.strip())
            (chuu if (c is not None and m.start() > c) else jitsu).append(rec)
    return lines, jitsu, chuu


def selftest():
    import tempfile
    import os
    src = (
        '#!/bin/bash\n'
        '# 註の口: ${CHUU_NO_KUCHI:-yes} ―― 之を数へたら疵\n'
        'X="${JITSU_NO_KUCHI:-1}"   # 実の口(行末に註が有つても実)\n'
        'echo "a # b ${KAKURI_NAI_NO_KUCHI:-2}"   # 括りの中の # は註に非ず\n'
    )
    fd, p = tempfile.mkstemp(suffix='.sh')
    os.write(fd, src.encode('utf-8'))
    os.close(fd)
    _, jitsu, chuu = scan(p)
    os.unlink(p)
    jn = sorted(r[1] for r in jitsu)
    cn = sorted(r[1] for r in chuu)
    want_j = ['JITSU_NO_KUCHI', 'KAKURI_NAI_NO_KUCHI']
    want_c = ['CHUU_NO_KUCHI']
    print('★陽性対照★(註の口は註へ落ちるか): 得=%s 期=%s → %s'
          % (cn, want_c, 'PASS' if cn == want_c else '★FAIL★'))
    print('★陰性対照★(実の口は実に留まるか): 得=%s 期=%s → %s'
          % (jn, want_j, 'PASS' if jn == want_j else '★FAIL★'))
    ok = (cn == want_c and jn == want_j)
    print('selftest=%s' % ('PASS' if ok else '★FAIL★'))
    return 0 if ok else 5


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    if sys.argv[1] == '--selftest':
        return selftest()
    tj = tc = 0
    per = []
    for p in sys.argv[1:]:
        try:
            lines, jitsu, chuu = scan(p)
        except OSError as e:
            sys.stderr.write('★対象が無い★ %s: %s\n' % (p, e))
            return 4
        print('########## %s (行=%d) ##########' % (p, len(lines)))
        print('--- 実(code)の口 ―― 之のみが ★現に開く口★ ---')
        for (i, nm, op, dv, raw) in jitsu:
            print('  L%-4d %-32s 既定=%r' % (i, nm, dv))
        print('--- 註(comment)の口 ―― ★口に非ず★(散文) ---')
        for (i, nm, op, dv, raw) in chuu:
            print('  L%-4d %-32s 既定=%r' % (i, nm, dv))
            print('         逐語: %s' % raw)
        names = sorted(set(r[1] for r in jitsu))
        print('==> 実_名=%d 実_出現=%d / 註_名=%d 註_出現=%d'
              % (len(names), len(jitsu), len(set(r[1] for r in chuu)), len(chuu)))
        print()
        per.append((p, len(names), len(jitsu), len(chuu)))
        tj += len(names)
        tc += len(chuu)
    print('########## 合計 ##########')
    for (p, n, o, c) in per:
        print('  %-40s 実_名=%-3d 実_出現=%-3d 註_出現=%d' % (p.split('/')[-1], n, o, c))
    print('★口(実・名で数ふ)= %d ★   註中の幻 = %d' % (tj, tc))
    print('註: 家老の見立 21 = 実 %d + 註中の幻 %d' % (tj, tc))
    return 0


sys.exit(main())
