#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 71_kougodan.py ―― ★18閾の「後段の讀手」を、生器から己の手で引く★
# 使ひ方: 71_kougodan.py <watcher> <health> <context> <enter>
#
# ★何故 專任2 の欄を使はぬか★
#   彼の「後段の逐語」欄は 18 の内 ★6★ が散文(「冷却比較」「段の番号」「打鍵中の見送り上限」)で、
#   行番も演算子も無い。∴ 其の 6 は彼の紙からは讀手が割れぬ。生器から引き直す。
#
# ★己の疵(先の版で踏んだ)★
#   ⑴ 受け皿違ひ: health/context/enter は fix_threshold NAME 既定 ★別名★ と呼ぶ。
#      閾名で grep すると呼出行しか出ず「後段無し」と誤る。∴ 受け皿名でも引く。
#   ⑵ 緩い当て: 「行の何處かに $(( が在る」で算術と断ずると、`$((now - OTHER))` と
#      `${NAME:-300}` が同じ行に居るだけで算術に化ける。∴ ★括弧の中に居るか★を見る。
#   ⑶ 局所写し: `local m="${NAME:-5}"` の後、比較は m で行はれる。∴ 一段だけ別名を追ふ。
import sys, io, re
if len(sys.argv) < 5:
    sys.stderr.write(u'★測れぬ: watcher health context enter の四つを argv で渡せ★\n'); sys.exit(2)
KI = [(u'watcher', sys.argv[1]), (u'health', sys.argv[2]),
      (u'context', sys.argv[3]), (u'enter', sys.argv[4])]

def lines(p):
    return [l.rstrip(u'\n') for l in io.open(p, encoding='utf-8', errors='replace')]

CALL = re.compile(r'fix_threshold\s+([A-Z_][A-Z0-9_]*)\s+(\S+)\s+([A-Za-z_][A-Za-z0-9_]*)')
LIST = re.compile(r'\b([A-Z_][A-Z0-9_]*):([0-9]+)\b')
ALIAS = re.compile(r'\blocal\s+([a-z_][a-z0-9_]*)=\"\$\{([A-Z_][A-Z0-9_]*)')

def arith_spans(s):
    out = []; i = 0
    while True:
        j = s.find(u'$((', i)
        if j < 0: break
        k = s.find(u'))', j)
        if k < 0: k = len(s)
        out.append(s[j:k]); i = k + 2
    return out

print(u'閾名\t器\t受け皿\t行\t讀手\t使用箇所の逐語')
soroi = []
for ki, path in KI:
    src = lines(path)
    ukezara = {}
    naka = False                              # ★番人列(for _t in ... done)の中に居るか★
    for n, l in enumerate(src, 1):
        m = CALL.search(l)
        if m and u'fix_threshold()' not in l and not l.strip().startswith(u'#'):
            ukezara[m.group(1)] = m.group(3)
        if l.strip().startswith(u'for _t in'): naka = True
        if naka:
            for a, b in LIST.findall(l):
                ukezara.setdefault(a, a)     # ★番人列は 名←名(己へ書き戻す)★
            if l.strip() == u'done': naka = False
    for na in sorted(ukezara):
        uz = ukezara[na]
        toks = {na, uz}
        # 一段だけ局所写しを追ふ
        for l in src:
            m = ALIAS.search(l)
            if m and m.group(2) in toks: toks.add(m.group(1))
        atari = []
        for n, l in enumerate(src, 1):
            if u'fix_threshold' in l: continue
            if l.strip().startswith(u'#'): continue
            hit = [t for t in toks if re.search(r'(\$\{?|\b)' + re.escape(t) + r'\b', l)]
            if not hit: continue
            yo = []
            if any(re.search(r'\b' + re.escape(t) + r'\b', sp) for t in toks for sp in arith_spans(l)):
                yo.append(u'算術$(( ))')
            if re.search(r'\[\s.*-(lt|le|gt|ge|eq|ne)\s', l) and any(re.search(r'\$\{?"?' + re.escape(t) + r'\b', l) for t in toks):
                yo.append(u'test[ ]')
            if re.search(r'(gtimeout|inotifywait|timeout)\b', l) and any(re.search(r'\$\{?"?' + re.escape(t) + r'\b', l) for t in toks):
                yo.append(u'外器')
            if re.search(r'\$\{(' + u'|'.join(re.escape(t) for t in toks) + r'):-', l):
                yo.append(u'残存既定${:-}')
            if not yo: continue
            atari.append((n, u'+'.join(yo), l.strip()))
        if not atari:
            print(u'%s\t%s\t%s\t―\t★後段見當らず★\t―' % (na, ki, uz))
            soroi.append((na, ki, u'★後段見當らず★'))
        for n, yo, l in atari:
            print(u'%s\t%s\t%s\t%d\t%s\t%s' % (na, ki, uz, n, yo, l))
            soroi.append((na, ki, yo))
print(u'')
print(u'閾_件\t%d' % len(set((a, b) for a, b, c in soroi)))
