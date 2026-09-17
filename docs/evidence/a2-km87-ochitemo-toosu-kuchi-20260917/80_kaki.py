# -*- coding: utf-8 -*-
"""★書き★ ―― 捕へた流れを束の作法へ揃へる。
  (a) 行末の空白/TAB/CR を剥ぐ  (b) 末尾の改行を丁度一つ  (c) LF のみ
  (d) ★空(0byte)は「空であつた」の一行を書く★(ㄦ′ writer・裁の作法)
★正規化の前の寸法を必ず記す★(裁: 事後に導出するな・実測せよ)
使ひ方: python3 -B 80_kaki.py <控への path> <紙...>"""
import sys, os, hashlib, datetime

if len(sys.argv) < 3:
    sys.stderr.write('usage: 80_kaki.py <hikae> <file...>\n'); sys.exit(2)
hikae = sys.argv[1]; targets = sys.argv[2:]
now = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
rows = []; changed = 0; emptied = 0
for p in targets:
    if not os.path.isfile(p):
        rows.append((p, 'NOTFILE', '-', '-', '-', '-')); continue
    b0 = open(p, 'rb').read()
    before = (len(b0), b0.count(b'\n'), hashlib.sha256(b0).hexdigest()[:16])
    if len(b0) == 0:
        body = ('# ★空であつた★ ―― 器が何も書かなんだ(0 byte)。'
                '刻=%s 紙=%s\n' % (now, os.path.basename(p))).encode('utf-8')
        emptied += 1
    else:
        t = b0.decode('utf-8', errors='surrogateescape')
        t = t.replace('\r\n', '\n').replace('\r', '\n')
        t = '\n'.join(L.rstrip(' \t') for L in t.split('\n'))
        t = t.rstrip('\n') + '\n'
        body = t.encode('utf-8', errors='surrogateescape')
    if body != b0:
        open(p, 'wb').write(body); changed += 1
    after = (len(body), body.count(b'\n'), hashlib.sha256(body).hexdigest()[:16])
    rows.append((p, 'EMPTY' if before[0] == 0 else ('FIXED' if body != b0 else 'ASIS'),
                 before[0], before[2], after[0], after[2]))
with open(hikae, 'w', encoding='utf-8') as fh:
    fh.write('# ★書きの控★ ―― 正規化の★前★の寸法を記す(導出でなく実測)\n')
    fh.write('# 刻 %s\n' % now)
    fh.write(('# %-46s %-6s %10s %-18s %10s %-18s' % ('紙', '札', '前byte', '前sha16', '後byte', '後sha16')).rstrip() + '\n')
    for r in rows:
        fh.write(('%-48s %-6s %10s %-18s %10s %-18s' % r).rstrip() + '\n')
    fh.write('# 母數=%d / 直した=%d / 内 空であつた=%d\n' % (len(rows), changed, emptied))
print('母數=%d 直した=%d 空であつた=%d 控=%s' % (len(rows), changed, emptied, hikae))
