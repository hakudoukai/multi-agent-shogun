#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁 seq326349 ―― ★PR ref の到達★ を固定頭で測る(読取のみ)。
軍師mac 326273 の残指摘は三つ: ⑴提出 raw が親363d5fb0 の --mae 走 ⑵生成物の臺帳 ⑶PR ref の到達。
本器は⑶を担ふ。「到達」を★二義に割つて★測る(混ぜれば數が嘘になる):
  甲 = 紙が頭から到達可能か ―― 束の file 悉くが <頭>:<path> として引けるか
       (最初の REVISE の因は「commit 内 0(untracked)」＝甲の不到達であつた)
  乙 = 頭を含む ref は何本か ―― for-each-ref --contains / branch -r --contains
★零には四つの札★: ⑴陽性対照 ⑵根と深さ ⑶rc ⑷刻。
註: --contains は在らぬ commit に rc=129 で空を返す ∴ 數と rc を必ず並べて刷る。
使ひ方: 50_ref_toutatsu.py <頭の ref か sha>
"""
import os, subprocess, sys, time

ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()


def g(*a):
    # ★-C ROOT を必ず噛ます★: ls-tree の pathspec は ★cwd 相対★ ゆゑ、
    # 束の中から呼ぶと同じ引数が 0 本を返す(2026-09-17 實測 ―― 甲=0/13 の偽)。
    # cat-file の <rev>:<path> は根相対で、此の二つは ★別の約束★ である。
    p = subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'surrogateescape')

def kaki(path, lines):
    open(path, 'w', encoding='utf-8').write(
        '\n'.join(l.replace('\r', '').rstrip() for l in lines) + '\n')

def main():
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__); return 2
    root = ROOT
    taba_rel = 'docs/evidence/karo-mac-miki-push-negai-20260917'
    taba = os.path.join(root, taba_rel)
    L = ['刻 = ' + time.strftime('%Y-%m-%dT%H:%M:%S%z'),
         '根 = ' + root,
         '束 = ' + taba_rel, '']

    rc, sha = g('rev-parse', '--verify', sys.argv[1] + '^{commit}')
    if rc:
        L.append('★頭が引けぬ★ rc=%d 引数=%s' % (rc, sys.argv[1]))
        kaki(os.path.join(taba, 'raw/51_toutatsu.txt'), L); return 3
    head = sha.strip()
    L += ['頭 = %s (引数=%s)' % (head, sys.argv[1]), '']

    # ―― 甲: 紙が頭から到達可能か ――――――――――――――――――――――――
    L.append('甲 紙の到達 ―― 束の file 悉くが <頭>:<path> で引けるか')
    # ⑴陽性対照(同じ路に乗せる): 在る筈の物と、在らぬ筈の物を一つづつ通す
    rc_a, _ = g('cat-file', '-e', '%s:%s/MANIFEST.txt' % (head, taba_rel))
    rc_b, _ = g('cat-file', '-e', '%s:%s/__zettai_ni_nai__.txt' % (head, taba_rel))
    L.append('  ⑴対照 在る筈=%s(rc=%d) / 在らぬ筈=%s(rc=%d)  %s'
             % ('到達' if rc_a == 0 else '不到達', rc_a,
                '到達' if rc_b == 0 else '不到達', rc_b,
                '★器は生きて居る★' if (rc_a == 0 and rc_b != 0) else '★対照が倒れた=數を名乗る資格無★'))
    if not (rc_a == 0 and rc_b != 0):
        kaki(os.path.join(taba, 'raw/51_toutatsu.txt'), L); return 4

    disk = []
    for dp, dn, fn in os.walk(taba):
        dn[:] = [d for d in dn if d != '__pycache__']
        for n in sorted(fn):
            p = os.path.join(dp, n)
            if os.path.isfile(p) and not os.path.islink(p):
                disk.append(os.path.relpath(p, taba))
    disk.sort()
    rc_t, tree = g('ls-tree', '-r', '-z', '--full-tree', '--name-only', head, '--', taba_rel + '/')
    intree = sorted(x[len(taba_rel) + 1:] for x in tree.split('\0') if x)
    # ⑴-乙 ★ls-tree 自身への対照★ ―― 上の cat-file 対照は ★別の path 約束★ を検めて居り、
    #   ls-tree が 0 本を返す疵(pathspec が cwd 相対)を捕へられぬ。同じ出目で検める。
    L.append('  ⑴-乙 ls-tree 対照 MANIFEST.txt が出目に在るか = %s (出目 %d 本・rc=%d)'
             % ('在(★器は生きて居る★)' if 'MANIFEST.txt' in intree
                else '★無=出目が空か根を外して居る★', len(intree), rc_t))
    if 'MANIFEST.txt' not in intree:
        kaki(os.path.join(taba, 'raw/51_toutatsu.txt'), L)
        return 5
    todatsu = [p for p in disk if p in set(intree)]
    futodatsu = [p for p in disk if p not in set(intree)]
    L += ['  ⑵根と深さ disk を歩いた本(file・__pycache__除)= %d / 頭の tree に在る本 = %d (ls-tree rc=%d)'
          % (len(disk), len(intree), rc_t),
          '  ★到達 %d 本 / 不到達 %d 本★' % (len(todatsu), len(futodatsu))]
    for p in futodatsu:
        L.append('     不到達: ' + p)
    # 中身まで合ふか(名だけの到達では足らぬ)
    chigai = []
    for p in todatsu:
        rcc, _ = g('cat-file', '-e', '%s:%s/%s' % (head, taba_rel, p))
        blob = subprocess.run(['git', 'cat-file', '-p', '%s:%s/%s' % (head, taba_rel, p)],
                              capture_output=True).stdout
        if rcc != 0 or blob != open(os.path.join(taba, p), 'rb').read():
            chigai.append(p)
    L += ['  ⑶rc 中身まで照した本 = %d / ★disk と頭で異なる本 = %d★' % (len(todatsu), len(chigai))]
    for p in chigai:
        L.append('     異: ' + p)

    # ―― 乙: 頭を含む ref ――――――――――――――――――――――――――――
    L += ['', '乙 ref の到達 ―― 頭を含む ref は何本か']
    for nm, args in (('手許(refs/heads)', ['for-each-ref', '--format=%(refname)', '--contains', head, 'refs/heads']),
                     ('遠隔(refs/remotes)', ['for-each-ref', '--format=%(refname)', '--contains', head, 'refs/remotes'])):
        rc_r, out = g(*args)
        names = [x for x in out.split('\n') if x]
        L.append('  %-18s = %d 本 (rc=%d) %s' % (nm, len(names), rc_r, ' '.join(names) or '―'))
    for nm, other in (('前の PR 頭 363d5fb0', '363d5fb060845171338c067ef42bfcbef8ad9188'),
                      ('基 origin/main', 'origin/main')):
        rc_o, s = g('rev-parse', '--verify', other + '^{commit}')
        if rc_o:
            L.append('  %-18s = ★引けぬ★ rc=%d' % (nm, rc_o)); continue
        rc_anc, _ = g('merge-base', '--is-ancestor', s.strip(), head)
        L.append('  %-18s = %s は頭の祖先か: %s (rc=%d)  sha=%s'
                 % (nm, nm, '然り' if rc_anc == 0 else '否', rc_anc, s.strip()[:12]))

    L += ['', '⑷刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'),
          '★數が意味せぬ事★: 乙の「遠隔 0 本」は★未 push★を意味するのみで、疵では無い',
          '  (push は総監督の代行が正路ゆゑ、當席は commit で止める)。',
          '  甲の「不到達 N 本」は★本走の後に生れる紙★(此の紙自身・臺帳・門の控)を含む ―― 名を悉く上へ列べた。']
    kaki(os.path.join(taba, 'raw/51_toutatsu.txt'), L)
    print('\n'.join(L))
    return 0 if not chigai else 1

sys.exit(main())
