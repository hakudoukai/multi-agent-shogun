#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★當席の足跡★ ―― 幹束に何を残したかを、主張ではなく ★頭の blob★ に言はせる。

★此の器は一度 誤つて居た(初版・16:44)★ ―― 記録として残す:
  初版は `git status --porcelain` と `git diff HEAD` で足跡を数へ、
  「變つた本 = 0」と刷つた。然れど 16:40 の blob 照合は「異なる」と出て居た ―― 矛盾。
  因は二つ、いづれも ★HEAD と .gitignore★ である:
    ⑴ 當席の枝の HEAD(75aa92f)は ★0bb92e2 を含まぬ★(merge-base --is-ancestor rc=1)
       ∴ `diff HEAD` は幹束の紙を ★一本も追跡して居らぬ★ ―― 靜かなのは當然。
    ⑵ 束は .gitignore:7 の ★裸の `*`★(allowlist 形)で遮断され、
       `status --untracked-files=all` にも出ぬ(18 行目 `!README.md` ゆゑ README だけ ?? に見えた)。
  ∴ ★「status が靜か」は「變へて居らぬ」の證に成らぬ★。
  正しい物差は ★頭 0bb92e2 の blob と disk の一本づつの照合★ である(本版)。
使ひ方: 60_ashiato.py <頭>
"""
import hashlib
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
kaki = import_module('00_kaki').kaki

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()
TABA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIKI = 'docs/evidence/karo-mac-miki-push-negai-20260917'


def g(*a):
    p = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return p.returncode, p.stdout


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    rc_h, s = g('rev-parse', '--verify', sys.argv[1] + '^{commit}')
    if rc_h:
        kaki(os.path.join(TABA, 'raw/60_ashiato.txt'), ['★頭が引けぬ★ rc=%d' % rc_h])
        return 3
    head = s.decode().strip()
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'), '根 = ' + ROOT,
         '物差 = 頭 %s の blob(★HEAD でも status でもない★)' % head, '']

    # ―― 先づ「status が使へぬ」事を證す ――
    rc_hd, hd = g('rev-parse', 'HEAD')
    rc_anc, _ = g('merge-base', '--is-ancestor', head, hd.decode().strip())
    p = subprocess.run(['git', '-C', ROOT, 'check-ignore', '-v',
                        MIKI + '/raw/51_toutatsu.txt'], capture_output=True)
    L += ['―― 甲 ★何故 status を物差に出来ぬか★ ――',
          '  當席の枝の HEAD = %s (rc=%d)' % (hd.decode().strip(), rc_hd),
          '  HEAD は頭 %s を含むか = %s (merge-base --is-ancestor rc=%d)'
          % (head[:12], '然り' if rc_anc == 0 else '★否★', rc_anc),
          '  幹束の紙は .gitignore に掛かるか: rc=%d %s'
          % (p.returncode, p.stdout.decode('utf-8', 'surrogateescape').replace('\t', ' → ').strip()),
          '  ∴ ★status も diff HEAD も、此の束に就いては何も見て居らぬ★。',
          '    「靜か」を「變へて居らぬ」と読めば ―― ★之が初版の誤りであつた★。', '']

    # ―― 一本づつ blob と照らす ――
    rc_t, tree = g('ls-tree', '-r', '-z', '--full-tree', '--name-only', head, '--', MIKI + '/')
    intree = sorted(x[len(MIKI) + 1:] for x in tree.decode('utf-8', 'surrogateescape').split('\0') if x)
    disk = []
    for dp, dn, fn in os.walk(os.path.join(ROOT, MIKI)):
        dn[:] = [d for d in dn if d != '__pycache__']
        for f in sorted(fn):
            fp = os.path.join(dp, f)
            if os.path.isfile(fp) and not os.path.islink(fp):
                disk.append(os.path.relpath(fp, os.path.join(ROOT, MIKI)))
    disk.sort()

    onaji, chigau, nashi = [], [], []
    for rel in disk:
        if rel not in set(intree):
            nashi.append(rel)
            continue
        pb = subprocess.run(['git', '-C', ROOT, 'cat-file', '-p',
                             '%s:%s/%s' % (head, MIKI, rel)], capture_output=True)
        body = open(os.path.join(ROOT, MIKI, rel), 'rb').read()
        (onaji if (pb.returncode == 0 and pb.stdout == body) else chigau).append(rel)

    L += ['―― 乙 頭の blob と disk の一本づつの照合(ls-tree rc=%d) ――' % rc_t,
          '  disk = %d 本 / 頭の tree = %d 本' % (len(disk), len(intree)),
          '  ★同じ = %d 本 / 異なる = %d 本 / 頭に無い = %d 本★'
          % (len(onaji), len(chigau), len(nashi))]
    for rel in chigau:
        b = open(os.path.join(ROOT, MIKI, rel), 'rb').read()
        pb = subprocess.run(['git', '-C', ROOT, 'cat-file', '-p',
                             '%s:%s/%s' % (head, MIKI, rel)], capture_output=True)
        L += ['    異: %s' % rel,
              '        頭  sha256=%s (%d byte)' % (hashlib.sha256(pb.stdout).hexdigest(), len(pb.stdout)),
              '        disk sha256=%s (%d byte)' % (hashlib.sha256(b).hexdigest(), len(b))]
    for rel in nashi:
        L.append('    頭に無い: ' + rel)

    L += ['',
          '★此の數が意味せぬ事★',
          '  ・「異なる 1 本」は ★當席が中身を書いた★ の意ではない ―― 器が己の出目を其處へ置いた(仕様)。',
          '  ・「同じ %d 本」は ★正しい★ の意ではない ―― 唯 頭の blob と一致するといふだけ。' % len(onaji),
          '  ・此の照合は ★commit して居らぬ★ ―― disk の姿を述べたのみ。',
          '',
          '⑷刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z')]
    kaki(os.path.join(TABA, 'raw/60_ashiato.txt'), L)
    print('\n'.join(L))
    return 0


sys.exit(main())
