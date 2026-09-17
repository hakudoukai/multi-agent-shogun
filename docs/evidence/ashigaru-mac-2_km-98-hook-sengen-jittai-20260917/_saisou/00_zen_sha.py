#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""00_zen_sha.py <歩き根> <出目path> ―― 歩き根の下の ★総ての現物 file★ の sha256 を録る。

何の為か: 家老の手順① は「元の raw は `git cat-file -p <枝>:<path>` で戻して sha 不動を證せ」と言ふ。
★併し km-98 の束は一つの ref にも commit にも入つて居らぬ★(其れが今治す疵の本体である) ∴ 其の路は
★通れぬ★。依つて「再走の前に録つた sha256」を不動の證の代りに据ゑる。之は git より弱い ―― 録つたのが
己自身だからである。★其の弱さを紙に書く★(隠して強く見せるより良い)。

数の規律3: 此の数は「file が git に在る」事を ★意味せぬ★。「或る刻の disk の中身」のみを意味する。
歩き根は argv から取る(器は的を argv から取れ)。symlink は辿らず、非 regular は別に数へる。
"""
import hashlib, os, sys, time

def main():
    if len(sys.argv) != 3:
        sys.stderr.write('usage: 00_zen_sha.py <歩き根> <出目path>\n'); return 2
    root, out = sys.argv[1], sys.argv[2]
    if not os.path.isdir(root):
        sys.stderr.write('★歩き根が dir に非ず★ %s\n' % root); return 3
    rows, hijou, kara = [], [], 0
    for d, ds, fs in os.walk(root):
        ds.sort(); fs.sort()
        for f in fs:
            p = os.path.join(d, f)
            st = os.lstat(p)
            import stat as _s
            if not _s.S_ISREG(st.st_mode):
                hijou.append('%s\tmode=%o' % (os.path.relpath(p, root), st.st_mode)); continue
            b = open(p, 'rb').read()
            if not b: kara += 1
            rows.append((os.path.relpath(p, root), hashlib.sha256(b).hexdigest(), len(b)))
    rows.sort()
    刻 = time.strftime('%Y-%m-%dT%H:%M:%S')
    L = ['# 00_zen_sha.py ―― 再走前の現物 sha256',
         '# 歩き根=%s' % os.path.abspath(root),
         '# 刻=%s' % 刻,
         '# 意味=此の刻の disk の中身のみ。★git に在る事は意味せぬ★',
         '# path(根相対)\tsha256\tbytes']
    for r in rows: L.append('%s\t%s\t%d' % r)
    L.append('# 現物 file=%d / 0byte=%d / 非regular=%d' % (len(rows), kara, len(hijou)))
    for h in hijou: L.append('# ★非regular★\t%s' % h)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    sys.stderr.write('★録つた file=%d / 0byte=%d / 非regular=%d / 刻=%s★\n'
                     % (len(rows), kara, len(hijou), 刻))
    sys.stderr.write('出目=%s\n' % out)
    return 0

sys.exit(main())
