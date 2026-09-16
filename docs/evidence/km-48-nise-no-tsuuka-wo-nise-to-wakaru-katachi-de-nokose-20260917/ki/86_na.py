# -*- coding: utf-8 -*-
"""86_na.py ―― ★「直せぬ」と呼んだ物を、測つて確かめる器★ (第48弾 ㋓)
名の中に LF/CR を持つ現物が在るか否かを、歩いて数へる。
★是は「臺帳に書けるか」ではなく「在るか」を測る。二つは別の問である。★
"""
import sys
sys.dont_write_bytecode = True
import os, hashlib

def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'用: 86_na.py <歩き根...>\n'); return 2
    zen = lf = cr = kuu = hi = 0
    mei = []
    roots = [os.path.abspath(a) for a in argv[1:]]
    for R in roots:
        for dp, dns, fns in os.walk(R):
            for n in fns:
                p = os.path.join(dp, n)
                zen += 1
                if not os.path.isfile(p) or os.path.islink(p):
                    hi += 1
                    continue
                if u'\n' in n:
                    lf += 1; mei.append((u'LF', os.path.relpath(p, R)))
                if u'\r' in n:
                    cr += 1; mei.append((u'CR', os.path.relpath(p, R)))
                if u' ' in n:
                    kuu += 1
    print(u'★歩き根★')
    for R in roots:
        print(u'  %s' % R)
    print(u'★全名★ %d (内 非常体/link %d)' % (zen, hi))
    print(u'★名中LF★ %d   ★名中CR★ %d   ★名中空白★ %d' % (lf, cr, kuu))
    for k, n in mei[:20]:
        print(u'  %s %s' % (k, n))
    print(u'★陽性対照★ ―― 検出子が生きて居る事を己の作つた名で示す')
    import tempfile
    d = os.path.join(os.path.dirname(os.path.abspath(argv[1])), '.na_taishou')
    try:
        os.makedirs(d)
    except OSError:
        pass
    ok = True
    try:
        t = os.path.join(d, u'a\nb.txt')
        open(t, 'w').write('x')
        got = [n for n in os.listdir(d) if u'\n' in n]
        print(u'  作つた名=%r  検出=%d 本 ―― %s' % (u'a\nb.txt', len(got), u'★鳴る★' if got else u'★黙る(検出子が死んで居る)★'))
        ok = bool(got)
        os.remove(t)
    except Exception as e:
        print(u'  ★測れぬ★ %s' % e); ok = False
    try:
        os.rmdir(d)
    except OSError:
        pass
    seal = hashlib.sha256((u'名札v1|全名=%d|LF=%d|CR=%d|空白=%d' % (zen, lf, cr, kuu)).encode('utf-8')).hexdigest()[:16]
    print(u'名札v1 全名=%d 名中LF=%d 名中CR=%d 名中空白=%d 陽性対照=%s 封=%s'
          % (zen, lf, cr, kuu, u'鳴' if ok else u'黙', seal))
    return 0 if ok else 2

if __name__ == '__main__':
    sys.exit(main(sys.argv))
