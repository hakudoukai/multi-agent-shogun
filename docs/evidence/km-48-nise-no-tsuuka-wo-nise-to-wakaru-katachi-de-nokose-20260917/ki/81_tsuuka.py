# -*- coding: utf-8 -*-
"""81_tsuuka.py ―― ★通過の母數を数へる器★ (第48弾 ㋐)

宣:
  母數 = 「或る弾の中で下された ★通/不通 の判★」の総数。
  判とは「器が或る一件に対して 通つた/通らぬ を一度言つた箇所」を云ふ。
  ★何を判と数へるかは下の 族(family) 表が全てである。表に無い形は数へて居らぬ。★

族(逐語の形で割る。重なりは 0 である事を毎走 検める):
  ★字下げは剥いでから当てる★ ―― 行頭固定の形は字下げした判を黙つて落す
  (本器の初走は ^★rc= で当てて居り、A6 の字下げ二判を落して居た。母數が 44→46 に増えた)

  甲 自検判  ^---- 出た rc=N / 望む rc=N ―― (合ふ|合はぬ)   … 器が己を検めた一件
  乙 器判    ^★rc=N ――                                     … 器が本走で下した判
  丙 門判    ^條[①-⑤]                                      … 出す前 門 の一條
  丁 臺帳行判 門の「一致 ★N★ / 相違 … (母數 M)」の M 行     … 臺帳一行に一判
  戊 結語判  ^★出す前 門 (通|落)                            … 門の総judgment 一行

通の判定:
  甲 … 「合ふ」で通、「合はぬ」で不通
  乙 … rc=0 で通、其れ以外 不通
  丙 … 逐語に「通」が在れば通・「落」「鳴」が在れば不通・★何れも無ければ 測れぬ★
       (門の各條は ★機械に読める出目の欄を持たぬ★。持たぬ物を通にも不通にも倒さぬ)
  丁 … 一致の数だけ通、母數-一致 だけ不通
  戊 … 「通」で通、「落」で不通

出目は ★三★ である ―― 通 / 不通 / ★測れぬ★。母數は三つの和である。

★本器が数へぬ物(宣)★:
  ・走そのものの rc(shell の $?)。第47弾の .out には ★走の rc を書いた行が無い★。
    故に「走が通つた」は本器の母數に入らぬ ―― ★紙に無い物は数へられぬ★。
  ・人の目で「良し」とした箇所。観測できる欄が無い。
"""
import sys
sys.dont_write_bytecode = True
import os, re, io, glob, hashlib

KOU = re.compile(u'^\\s*---- 出た rc=(\\d+) / 望む rc=(\\d+) ―― (合ふ|合はぬ)')
OTSU = re.compile(u'^\\s*★rc=(\\d+)\\s*(?:\\(赤\\))?\\s*――')
HEI  = re.compile(u'^\\s*條[①-⑤]')
BO   = re.compile(u'^\\s*★出す前 門 (通|落)')
TEI  = re.compile(u'一致 ★?(\\d+)★? / 相違 (\\d+) / 実体無 (\\d+) / 読めぬ行 (\\d+)\\s+\\(母數 (\\d+)\\)')

def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()[:16]

def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'用: 81_tsuuka.py <束dir>\n'); return 2
    B = os.path.abspath(argv[1])
    out = io.StringIO()
    W = out.write

    ans = sorted(glob.glob(os.path.join(B, 'an', '*.out')))
    gates = sorted(glob.glob(os.path.join(B, '*_gate.txt')))
    if not ans:
        sys.stderr.write(u'★測れぬ★ an/*.out が無い\n'); return 2

    W(u'★歩いた紙★\n')
    for p in ans + gates:
        W(u'  %s bytes=%d sha16=%s\n' % (os.path.relpath(p, B), os.path.getsize(p), sha16(p)))
    W(u'\n')

    rows = []          # (族, 出所, 行番, 通/不通, 逐語)
    kasanari = 0
    for p in ans + gates:
        rel = os.path.relpath(p, B)
        with open(p, encoding='utf-8', errors='replace') as f:
            for i, raw in enumerate(f, 1):
                line = raw.rstrip(u'\n')
                hit = []
                m = KOU.match(line)
                if m:
                    hit.append((u'甲 自検判', u'通' if m.group(3) == u'合ふ' else u'不通'))
                m = OTSU.match(line)
                if m:
                    hit.append((u'乙 器判', u'通' if m.group(1) == '0' else u'不通'))
                if HEI.match(line):
                    if (u'落' in line) or (u'鳴' in line):
                        v = u'不通'
                    elif u'通' in line:
                        v = u'通'
                    else:
                        v = u'測れぬ'
                    hit.append((u'丙 門判', v))
                m = BO.match(line)
                if m:
                    hit.append((u'戊 結語判', u'通' if m.group(1) == u'通' else u'不通'))
                if len(hit) > 1:
                    kasanari += 1
                for fam, verd in hit:
                    rows.append((fam, rel, i, verd, line[:160]))

    # 丁 ―― 門の臺帳行。一致N/母數M を拾ひ、M 判に割る
    tei = None
    for p in gates:
        rel = os.path.relpath(p, B)
        with open(p, encoding='utf-8', errors='replace') as f:
            for i, raw in enumerate(f, 1):
                m = TEI.search(raw)
                if m:
                    icchi, soui, jittai, yome, bogen = (int(x) for x in m.groups())
                    tei = (rel, i, icchi, bogen, raw.strip()[:160])
                    for _ in range(icchi):
                        rows.append((u'丁 臺帳行判', rel, i, u'通', u'(臺帳一行の一致)'))
                    for _ in range(bogen - icchi):
                        rows.append((u'丁 臺帳行判', rel, i, u'不通', u'(臺帳一行の非一致)'))

    fams = [u'甲 自検判', u'乙 器判', u'丙 門判', u'丁 臺帳行判', u'戊 結語判']
    W(u'★族ごとの判★ (通/不通/測れぬ)\n')
    for fam in fams:
        t = [r for r in rows if r[0] == fam]
        c = lambda v: len([r for r in t if r[3] == v])
        W(u'  %s  判=%3d  通=%3d  不通=%3d  測れぬ=%3d\n' % (fam, len(t), c(u'通'), c(u'不通'), c(u'測れぬ')))
    bogen = len(rows)
    tsuuka = len([r for r in rows if r[3] == u'通'])
    hakare = len([r for r in rows if r[3] == u'測れぬ'])
    futsu = bogen - tsuuka - hakare
    unmatched = [r for r in rows if r[0] == u'丙 門判' and r[3] == u'測れぬ']
    W(u'\n★排他性★ 二族に当たつた行 = %d %s\n' % (kasanari, u'―― 族は重なつて居らぬ' if kasanari == 0 else u'★重なり有り。母數は水増しされて居る★'))
    W(u'★母數★ 判 = %d   ―― 内 ★通 = %d★ / 不通 = %d / ★測れぬ = %d★\n' % (bogen, tsuuka, futsu, hakare))
    W(u'★恒等★ 通+不通+測れぬ = %d %s 母數 %d\n' % (tsuuka + futsu + hakare, u'=' if tsuuka + futsu + hakare == bogen else u'≠', bogen))
    for fam, rel, i, verd, line in unmatched:
        W(u'  ★測れぬ★ %s:%d  %s\n' % (rel, i, line))
    if tei:
        W(u'★丁の出所(逐語)★ %s:%d  %s\n' % (tei[0], tei[1], tei[4]))
    W(u'\n★通つた判 悉く(逐語)★ ―― 丁は行単位ゆゑ 1 行に畳む\n')
    n = 0
    for fam, rel, i, verd, line in rows:
        if verd != u'通':
            continue
        if fam == u'丁 臺帳行判':
            continue
        n += 1
        W(u'  %2d. [%s] %s:%d  %s\n' % (n, fam, rel, i, line))
    tei_tsu = len([r for r in rows if r[0] == u'丁 臺帳行判' and r[3] == u'通'])
    W(u'  %2d. [丁 臺帳行判] %s ―― ★臺帳 %d 行が一致した(一行に一判)★\n' % (n + 1, tei[0] if tei else u'(無)', tei_tsu))

    seal = hashlib.sha256((u'通過母數v1|母數=%d|通=%d|不通=%d|測れぬ=%d|重なり=%d' % (bogen, tsuuka, futsu, hakare, kasanari)).encode('utf-8')).hexdigest()[:16]
    W(u'\n通過母數v1 母數=%d 通=%d 不通=%d 測れぬ=%d 重なり=%d 封=%s\n' % (bogen, tsuuka, futsu, hakare, kasanari, seal))
    sys.stdout.write(out.getvalue())
    return 0 if kasanari == 0 else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
