#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 20_kotei.py ―― ★測る前に版を固める★
#   出所 = memory「席が走る間に版は動く」。本弾の的 file(scripts/stop_hook_inbox.sh)は
#   ★下知(09:55)の後の 09:58 に disk で動いて居た★ ―― ∴ 刻無しの數は嘘に成る。
#   本器は ⑴刻 ⑵枝と HEAD ⑶三つの版(disk/index/HEAD)の ★歩き根の総括 sha★
#   ⑷汚れた file の一覧 を刷る。★一字も書き換へぬ(讀取のみ)。★
#
# 使ひ方: 20_kotei.py <根1> [<根2> ...]      (既定の根 = scripts .claude)
import sys, os, subprocess, hashlib, time

ROOTS = sys.argv[1:] or ['scripts', '.claude']

def sh(args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

out = []
out.append(u'# 20_kotei ―― 版の固め / 刻= %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
out.append(u'# 根= %s (★本弾の一本の歩き根★)' % u' '.join(ROOTS))

rc, o, e = sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']); eda = o.decode().strip()
rc2, o2, e2 = sh(['git', 'rev-parse', 'HEAD']); head = o2.decode().strip()
out.append(u'枝= %s rc=%d / HEAD= %s rc=%d' % (eda, rc, head, rc2))

# ⑶ 三つの版の総括 sha ―― 「path\0blobsha\n」を連ねた物の sha256(16)
rc, o, e = sh(['git', 'ls-tree', '-r', head, '--'] + ROOTS)
out.append(u'[HEAD] ls-tree rc=%d 行=%d 総括sha16= %s' % (rc, o.count(b'\n'), sha16(o)))
rc, o, e = sh(['git', 'ls-files', '-s', '--'] + ROOTS)
out.append(u'[index] ls-files -s rc=%d 行=%d 総括sha16= %s' % (rc, o.count(b'\n'), sha16(o)))

# disk は git を通さず己で歩く(追跡の有無に依らぬ)
h = hashlib.sha256(); n = 0; hijou = 0
for r in ROOTS:
    for dp, dn, fn in os.walk(r):
        dn.sort(); fn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            st = os.lstat(p)
            if not os.path.isfile(p) or os.path.islink(p):
                hijou += 1; continue
            try:
                b = open(p, 'rb').read()
            except Exception:
                hijou += 1; continue
            h.update(p.encode('utf-8') + b'\0' + hashlib.sha256(b).hexdigest().encode() + b'\n')
            n += 1
out.append(u'[disk] 歩いた file=%d 非常体(symlink/讀めぬ)=%d 総括sha16= %s' % (n, hijou, h.hexdigest()[:16]))

# ⑷ 汚れた file(根の下のみ)
rc, o, e = sh(['git', 'status', '--porcelain', '--'] + ROOTS)
lines = [l for l in o.decode('utf-8', 'replace').split('\n') if l]
out.append(u'汚れ rc=%d 件=%d ―― ★index と disk と HEAD は別物である★' % (rc, len(lines)))
for l in lines:
    out.append(u'  %s' % l)
sys.stdout.write(u'\n'.join(out) + u'\n')
