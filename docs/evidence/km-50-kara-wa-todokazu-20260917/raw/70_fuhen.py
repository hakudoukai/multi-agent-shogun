#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sahou⑴ ―― ★生器へ一字も据ゑて居らぬ★ を ★己の言でなく器で★ 示す。

法 = 着手(2026-09-17T03:37:38)以後に mtime を持つ file を生器の下から探す。
★陽性対照★ = 己の束の紙。同じ檢出子で ★必ず引つ掛かる★ 事を先に示す。
   (引つ掛からねば「生器に無い」も信ずるに足らぬ ―― ★恒真の器では零は證にならぬ★)
"""
import os, stat as S, sys, time, calendar

NE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
CHAKUSHU = '2026-09-17T03:37:38'
# ★走一は ここで倒れた★ ―― calendar.timegm - time.timezone は符號を違へ、9時間先の刻を作つた。
# 陽性対照が「動いた物 0 本」と出て器が止まつた(71_fuhen.taoreta.out に現物)。
# ★對照が落ちた故に零を刷らずに済んだ ―― 恒真の器であれば「生器は不動」と偽つて刷つて居た。★
# 直し = time.mktime は ★地方刻として讀む★。
T0 = time.mktime(time.strptime(CHAKUSHU, '%Y-%m-%dT%H:%M:%S'))
TABA = os.path.join(NE, 'docs/evidence/km-50-kara-wa-todokazu-20260917')
w = sys.stdout.write

# ★札が名指した生器は四箇である ―― scripts/ ・ ~/bin ・ hook ・ settings。★
# 走二では根に .claude/ を丸ごと取り 97 本を鳴らしたが、其の悉くが ★他席(足軽mac1号)の worktree★ と
# ★走時の log(~/.claude/projects・history・backups)★ であつた(71_fuhen.hashiri2.out に現物)。
# ★取り過ぎた根は「動いた」を増やすが、問ひに答へて居らぬ。★ 故に四箇へ絞り、周りは別欄に出す。
SEIKI = [
    ('scripts/', os.path.join(NE, 'scripts')),
    ('~/bin',    os.path.expanduser('~/bin')),
]
SEIKI_FILE = [
    ('hook/settings(束)', os.path.join(NE, '.claude/settings.json')),
    ('settings(家)',      os.path.expanduser('~/.claude/settings.json')),
]
MAWARI = [
    ('束 .claude/(他席の worktree を含む)', os.path.join(NE, '.claude')),
    ('~/.claude/(走時の log)',              os.path.expanduser('~/.claude')),
]

w('刻 = %s\n着手 = %s (epoch %d)\n\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), CHAKUSHU, T0))


def aruku(root, fukasa_max=None):
    n, atara, yomenu = 0, [], 0
    if not os.path.isdir(root):
        return None, [], 0
    for r, ds, fs in os.walk(root, followlinks=False):
        if '.git' in ds: ds.remove('.git')
        for f in fs:
            p = os.path.join(r, f)
            n += 1
            try:
                st = os.lstat(p)
            except OSError:
                yomenu += 1; continue
            if st.st_mtime >= T0:
                atara.append((os.path.relpath(p, NE), time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(st.st_mtime)), st.st_size))
    return n, atara, yomenu


w('― 零 ★陽性対照 ―― 同じ檢出子が「動いた物」を見付けられるか★ ―\n')
n, a, y = aruku(TABA)
w('  己の束 %s : 歩き %d 本 / ★着手以後に動いた = %d 本★\n' % (os.path.relpath(TABA, NE), n, len(a)))
if len(a) == 0:
    w('  ★対照が落ちた ―― 檢出子が動きを見付けられぬ。以下の零は證にならぬ。rc=1★\n')
    sys.exit(1)
w('  例(三本): %s\n' % ' / '.join('%s %s' % (x[0].split("/")[-1], x[1]) for x in sorted(a, key=lambda z: z[1])[:3]))
w('  ★対照 通 ―― 檢出子は動きを見る。∴ 下の零は「見えなんだ」ではなく「無い」である。★\n\n')

w('― 一 ★札が名指した生器 四箇★ ―\n')
sou = 0
for na, root in SEIKI:
    n, a, y = aruku(root)
    if n is None:
        w('  %-18s %s ―― ★dir 無し(歩いて居らぬ ∴ 零ではない)★\n' % (na, root)); continue
    sou += len(a)
    w('  %-18s 根=%s\n' % (na, root))
    w('  %-18s 歩き %5d 本 / 讀めぬ %d / ★着手以後に動いた = %d 本★\n' % ('', n, y, len(a)))
    for rel, mt, sz in sorted(a, key=lambda z: z[1]):
        w('      ★%s  %s  %d byte★\n' % (rel, mt, sz))
for na, f in SEIKI_FILE:
    if not os.path.isfile(f):
        w('  %-18s %s ―― ★file 無し★\n' % (na, f)); continue
    st = os.lstat(f)
    ugoita = st.st_mtime >= T0
    if ugoita: sou += 1
    w('  %-18s %s\n' % (na, f))
    w('  %-18s mtime=%s  %d byte  ★%s★\n'
      % ('', time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(st.st_mtime)), st.st_size,
         '動いた' if ugoita else '着手より前 ∴ 動いて居らぬ'))
w('\n  ★生器四箇で動いた總計 = %d 本★\n' % sou)
w('  %s\n' % ('  ★∴ 據ゑ零。生器へは一字も入れて居らぬ。★' if sou == 0
             else '  ★★動いた物が在る ―― 上に名を出した。之を隠さぬ。★★'))

w('\n― 一.五 ★周り ―― 動いたが、己の手ではない物★ ―\n')
w('  ★之を「生器が動いた」と書けば偽り、黙れば隠蔽である。∴ 別欄に數と持主を出す。★\n')
for na, root in MAWARI:
    n, a, y = aruku(root)
    if n is None:
        w('  %-34s ―― dir 無し\n' % na); continue
    kumi = {}
    for rel, mt, sz in a:
        if '/worktrees/' in rel:
            key = '他席の worktree(' + rel.split('/worktrees/')[1].split('/')[0] + ')'
        elif '/projects/' in rel or 'history.jsonl' in rel or '/sessions/' in rel or '/backups/' in rel:
            key = '走時の log(Claude Code 自身が書く物)'
        elif '/memory/' in rel:
            key = 'memory(別の走りが書いた物)'
        else:
            key = '其の他'
        kumi.setdefault(key, []).append(rel)
    w('  %-34s 歩き %5d 本 / ★動いた %d 本★\n' % (na, n, len(a)))
    for k, v in sorted(kumi.items(), key=lambda kv: -len(kv[1])):
        w('      %-40s %3d 本  例= %s\n' % (k, len(v), v[0]))
w('  ★己の手で据ゑた物は此の中に一本も無い ―― 但し ★mtime は持主を言はぬ★。\n')
w('    持主は ★path の名★(他席の束名 km-67/km-68)と ★己が走らせた器の一覧★ から読んだ。之は推である。★\n')

w('\n― 二 ★此の零が意味せぬ事★ ―\n')
w('  ⑴ mtime は ★内容が変つた事★ ではなく ★書かれた事★ を言ふ。同じ字を書き直しても動く。\n')
w('     逆に ★mtime を戻せば見えぬ★ ―― 本器は「戻す手」を見て居らぬ。\n')
w('  ⑵ 歩きから .git/ を除いた ―― ★除いた事を宣する★。git の内部を据ゑても本器は黙る。\n')
w('  ⑶ hook は settings の中の ★字★ である。file が動かずとも、外の settings が指す先が変れば効きは変る。\n')
w('  ⑷ ~/bin が無い機ならば「零」は ★歩いて居らぬ零★ である(上に dir 無しと出す)。\n')
w('\nrc = 0\n')
