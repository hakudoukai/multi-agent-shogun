# -*- coding: utf-8 -*-
"""★零には四つの札★(陽性対照・根と深さ・rc・刻)。本紙の零を、檢出子★其の物★で鳴らして見せる。

鳴らす零は三つ:
  零① karo_mac_manifest_append.py を抱へる ref = 0 / 90
  零② ~/bin の甲 5本の同名 path = 0 (全 ref・全 path)
  零③ 其の disk の版の object = 無(cat-file rc≠0)
陽性対照(同じ路・同じ器で鳴らす):
  対① 同じ歩きで karo_mac_manifest_verify.py は ★65/90★ を返すか
  対② 同じ basename 表で 'karo_mac_manifest_append.py' は 0、'CLAUDE.md' は ★>0★ を返すか
  対③ 同じ cat-file で、現に在る blob(HEAD の CLAUDE.md)は rc=0 を返すか
★対照が鳴らねば、零は「無い」の證に成らぬ。器を疑へ。★
"""
import os, subprocess, hashlib, time
os.chdir('/Users/momizimac/multi-agent-shogun')
print('刻=%s' % time.strftime('%Y-%m-%dT%H:%M:%S'))
print('根=/Users/momizimac/multi-agent-shogun (git dir) / 深さ=全 ref・全 path(ls-tree -r)')
refs = [ln for ln in subprocess.run(['git', 'for-each-ref', '--format=%(refname)'],
                                    capture_output=True, text=True).stdout.split('\n') if ln]
print('ref 母數=%d' % len(refs))

def path_refs(path):
    c = 0
    for r in refs:
        p = subprocess.run(['git', 'ls-tree', '--name-only', r + '^{commit}', '--', path],
                           capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            c += 1
    return c

a = path_refs('scripts/checks/karo_mac_manifest_append.py')
b = path_refs('scripts/checks/karo_mac_manifest_verify.py')
print('零① append を抱へる ref=%d  ／ 対① verify を抱へる ref=%d' % (a, b))
assert a == 0 and b > 0, (a, b)

base = set()
for r in refs:
    p = subprocess.run(['git', 'ls-tree', '-r', '--name-only', r + '^{commit}'], capture_output=True, text=True)
    if p.returncode == 0:
        for x in p.stdout.split('\n'):
            if x:
                base.add(x.rsplit('/', 1)[-1])
z2 = sum(1 for n in ('agent_letter.py', 'deferral_gate.py', 'fleet_liveness_check.sh',
                     'inbox_mark_read.py', 'sb') if n in base)
print('零② ~/bin 甲 5本の内 全 ref に同名が在る物=%d  ／ 対② CLAUDE.md が表に在るか=%s' % (z2, 'CLAUDE.md' in base))
assert z2 == 0 and 'CLAUDE.md' in base, (z2,)

d = open('/Users/momizimac/bin/inbox_mark_read.py', 'rb').read()
sha = hashlib.sha1(b'blob %d\0' % len(d) + d).hexdigest()
rc1 = subprocess.run(['git', 'cat-file', '-e', sha]).returncode
h = subprocess.run(['git', 'rev-parse', 'HEAD:CLAUDE.md'], capture_output=True, text=True).stdout.strip()
rc2 = subprocess.run(['git', 'cat-file', '-e', h]).returncode
print('零③ inbox_mark_read.py の版の object rc=%d ／ 対③ HEAD:CLAUDE.md の object rc=%d' % (rc1, rc2))
assert rc1 != 0 and rc2 == 0, (rc1, rc2)
print('★対照 三つ悉く鳴つた。∴ 零は器の黙りでは無く、實の零である。★')
