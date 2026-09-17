# -*- coding: utf-8 -*-
u"""30_bosuu.py ―― ㋐ ★母數を一本の歩き根で数へ直す★(km-85 第54弾)。

歩き根 = /Users/momizimac/multi-agent-shogun ★ただ一つ★。深さ=無限(os.walk 全下降・除外宣言 0)。
S_ISREG のみ読む。FIFO/socket/device/symlink は『非常体』として ★名指して別に数へる★
  (開けば止まる ―― 2026-09-16 FIFO で 10 分 戻らなんだ実測)。「除いた」ではない。歩いて、数へた。
拾ふ語 = num_same_op(byte 一致)。行は utf-8 errors=replace で割る。
区分 = 定義 / 呼び手 / 註(行頭 #) / 文(便・紙・log・diff 等)。
層   = 生器(scripts/) / 紙寫(docs/evidence/) / 別樹(.claude/) / 便(queue/) / 記(logs/) / 控(backups/) / 他。
己の束(docs/evidence/km-85-…) は ★員外★ として別に数へ名指す。
陽性対照 = scripts/agent_health_check.sh(在ると判つて居る・★同じ路★に乗せる)。
陰性対照 = 走時に組み立てる語(disk に literal 無し)。同じ路で 0 を示す。
出し = nama/30_bosuu.txt(総) / nama/31_teigi.tsv(定義行) / nama/32_yobite.tsv(呼び手行) / nama/33_chuu_bun.tsv(註と文)
"""
import os, sys, stat, time, hashlib, collections
B = sys.argv[1]; sys.path.insert(0, os.path.join(B, 'ki')); import kaki as K
M = u'/Users/momizimac/multi-agent-shogun'
NEEDLE = b'num_same_op'
POS = u'scripts/agent_health_check.sh'
NEG = u'ZZ_KM85_' + u'NEG_' + str(98765432)          # ★走時組立 ―― 此の file に literal は無い★
NEGB = NEG.encode('utf-8')
SAGASU = u'15ac9f97' + u'f473245d'                   # 家老 第52弾 便が申した sha16(同じく走時組立)
JIBUN = u'docs/evidence/km-85-onore-no-bannin-no-ana-wo-hachihon-de-hakare-20260917'

def sou(rel):
    if rel.startswith(u'scripts/'): return u'生器'
    if rel.startswith(u'docs/evidence/'): return u'紙寫'
    if rel.startswith(u'.claude/'): return u'別樹'
    if rel.startswith(u'queue/'): return u'便'
    if rel.startswith(u'logs/'): return u'記'
    if rel.startswith(u'backups/'): return u'控'
    return u'他'

def kubun(rel, l):
    s = l.strip()
    if s.startswith(u'#'): return u'註'
    if u'num_same_op()' in l.replace(u' ', u'') and u'{' in l: return u'定義'
    if (u'num_same_op "' in l) or (u'num_same_op $' in l) or (u'! num_same_op' in l): return u'呼び手'
    return u'文'

t0 = time.time()
walked = reg = nbytes = 0; maxdepth = 0
nonreg = []; unread = []; hits = []; neghits = []; shahits = []
for dp, dn, fn in os.walk(M):
    rel_dir = os.path.relpath(dp, M)
    d = 0 if rel_dir == u'.' else rel_dir.count(os.sep) + 1
    maxdepth = max(maxdepth, d)
    for f in sorted(fn):
        p = os.path.join(dp, f); rel = os.path.relpath(p, M); walked += 1
        try: st = os.lstat(p)
        except OSError as e: unread.append((rel, u'lstat errno=%s' % e.errno)); continue
        if not stat.S_ISREG(st.st_mode):
            nonreg.append((rel, oct(stat.S_IFMT(st.st_mode)))); continue
        reg += 1
        try: data = open(p, 'rb').read()
        except OSError as e: unread.append((rel, u'open errno=%s' % e.errno)); continue
        nbytes += len(data)
        if NEEDLE not in data and NEGB not in data and SAGASU.encode() not in data: continue
        txt = data.decode('utf-8', 'replace')
        for i, l in enumerate(txt.split(u'\n'), 1):
            if u'num_same_op' in l: hits.append((rel, i, l.strip()))
            if NEG in l: neghits.append((rel, i))
            if SAGASU in l: shahits.append((rel, i))
el = time.time() - t0

innai = [h for h in hits if not h[0].startswith(JIBUN)]
ingai = [h for h in hits if h[0].startswith(JIBUN)]
cnt = collections.Counter(); soucnt = collections.Counter()
teigi = []; yobite = []; chuubun = []
for rel, i, l in innai:
    k = kubun(rel, l); s = sou(rel); cnt[k] += 1; soucnt[(s, k)] += 1
    row = (s, rel, i, l)
    if k == u'定義': teigi.append(row)
    elif k == u'呼び手': yobite.append(row)
    else: chuubun.append((k, s, rel, i, l))
K.kaku_tsv(os.path.join(B, 'nama', '31_teigi.tsv'), teigi, [u'層', u'file', u'行', u'逐語'])
K.kaku_tsv(os.path.join(B, 'nama', '32_yobite.tsv'), yobite, [u'層', u'file', u'行', u'逐語'])
K.kaku_tsv(os.path.join(B, 'nama', '33_chuu_bun.tsv'), chuubun, [u'区分', u'層', u'file', u'行', u'逐語'])

namaki_t = sorted(set(r[1] for r in teigi if r[0] == u'生器'))
namaki_y = sorted(set(r[1] for r in yobite if r[0] == u'生器'))
g = []
g.append(u'★㋐ 母數 ―― 一本の歩き根★')
g.append(u'刻(始)=%s  刻(終)=%s  経過=%.1f 秒  rc=0(本器は最後まで走つた)'
         % (time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(t0)),
            time.strftime('%Y-%m-%dT%H:%M:%S%z'), el))
g.append(u'歩き根=%s  深さ=無限(最大 %d 段)  ★除外宣言=0★' % (M, maxdepth))
g.append(u'歩いた項=%d / 常体(S_ISREG)=%d / 非常体=%d(読まぬ・名指す) / 讀めぬ=%d / 読んだ byte=%d'
         % (walked, reg, len(nonreg), len(unread), nbytes))
g.append(u'')
g.append(u'★零の四札★ 陽性対照・根と深さ・rc・刻 ―― 四つ悉く上に在る。')
g.append(u'陽性対照 = %s ―― 同じ路で当たり ★%d 行★(0 なら器が盲)' % (POS, sum(1 for h in innai if h[0] == POS)))
g.append(u'陰性対照 = 走時組立の語(disk に literal 無し) ―― 当たり ★%d 行★(0 が正)' % len(neghits))
g.append(u'')
g.append(u'★員内(己の束を除く)の当たり行 = %d★' % len(innai))
for k in (u'定義', u'呼び手', u'註', u'文'):
    g.append(u'    %s = %d' % (k, cnt[k]))
g.append(u'★員外(己の束 %s の中)= %d 行★ ―― 除いたのではない。歩き、名指し、別に数へた。' % (JIBUN, len(ingai)))
for rel, i, l in ingai:
    g.append(u'    員外 %s:%d' % (rel, i))
g.append(u'')
g.append(u'★層別(員内)★  層\\区分  定義 / 呼び手 / 註 / 文')
for s in (u'生器', u'紙寫', u'別樹', u'便', u'記', u'控', u'他'):
    g.append(u'    %s\t%d\t%d\t%d\t%d' % (s, soucnt[(s, u'定義')], soucnt[(s, u'呼び手')],
                                          soucnt[(s, u'註')], soucnt[(s, u'文')]))
g.append(u'')
g.append(u'★生器(scripts/)の定義 file = %d 本★(札 scope_in の宣 = 8)' % len(namaki_t))
for r in sorted([x for x in teigi if x[0] == u'生器'], key=lambda z: z[1]):
    g.append(u'    定義 %s:%d  %s' % (r[1], r[2], r[3]))
g.append(u'★生器(scripts/)の呼び手 file = %d 本★' % len(namaki_y))
for r in sorted([x for x in yobite if x[0] == u'生器'], key=lambda z: z[1]):
    g.append(u'    呼手 %s:%d  %s' % (r[1], r[2], r[3]))
g.append(u'')
g.append(u'★家老 第52弾 便の sha16 %s の捜索(全 repo・同じ路)= %d 行★' % (SAGASU, len(shahits)))
for rel, i in shahits[:10]:
    g.append(u'    %s:%d' % (rel, i))
g.append(u'')
g.append(u'★非常体 = %d 項(S_ISREG に非ず ∴ 開かぬ)★' % len(nonreg))
for rel, m in nonreg:
    g.append(u'    非常体 %s (S_IFMT=%s)' % (rel, m))
g.append(u'★讀めぬ = %d 項★' % len(unread))
for rel, m in unread:
    g.append(u'    讀めぬ %s (%s)' % (rel, m))
K.kaku(os.path.join(B, 'nama', '30_bosuu.txt'), u'\n'.join(g))
sys.stderr.write(u'書いた: 30_bosuu.txt / 31_teigi.tsv(%d) / 32_yobite.tsv(%d) / 33_chuu_bun.tsv(%d)\n'
                 % (len(teigi), len(yobite), len(chuubun)))
