# -*- coding: utf-8 -*-
"""90_sueru.py ―― 束を ★枝へ据ゑる★ 器(家老mac 手順③の實體)。

★共有 index にも HEAD にも触れぬ★。私有の GIT_INDEX_FILE の上でのみ組む。
  read-tree <親> → hash-object -w → update-index --cacheinfo → write-tree → commit-tree → update-ref

★踏まぬ為の註(家老mac が踏んだ疵)★:
  git ls-tree の pathspec は ★cwd 相対★。束の中から呼ぶと ★0本を rc=0★ で返す。
  ∴ `git -C <根>` を噛ませ `--full-tree` を付け、★出目に既知の1本が在るか★を対照に置く。
  `<rev>:<path>` の方は ★根相対★ ―― 此の二つは別の約束である。
  本器は ★両方を実際に呼び★、疵の側が本当に 0本/rc=0 を返す事も紙に録る。

★本器が己を含む事★: 本器は束の中に在る ∴ 己自身を木へ入れる(走る時には既に完本)。
  併し ★本器の出目(92_/93_/94_)は木に入らぬ★ ―― 器の後に生まれるゆゑ。之を丙で名指す。

出目:
  _after/92_sueru.txt   手順と數
  _after/93_lstree.txt  commit の木の path(根相対・full-tree)
  _after/94_taisho.txt  対照三件(既知の1本・cwd相対の疵・disk再歩きとの差)
"""
import os, subprocess, sys

NE = '/Users/momizimac/multi-agent-shogun'
TABA = 'docs/evidence/ashigaru-mac-2_km-98-hook-sengen-jittai-20260917'
OYA = '1da2b6b9fb7fcf9a4a51be2c495b3a0fef386424'
EDA = 'refs/heads/ashigaru-mac-2/km-98-hook-sengen-jittai-20260917'
IDX = '/tmp/ashigaru-mac-2_idx.sueru'
SHIRU = TABA + '/README.md'          # ★既知の1本(陽性対照)★

env = dict(os.environ); env['GIT_INDEX_FILE'] = IDX

def g(*a, **kw):
    e = kw.pop('env', None)
    p = subprocess.run(('git', '-C', NE) + a, capture_output=True, text=True, env=e)
    return p.returncode, p.stdout, p.stderr

L = []
def w(s): L.append(s); print(s)

# ―― 前提の検め(一つでも崩れたら据ゑぬ) ――――――――――――――――
rc, o, e = g('cat-file', '-t', OYA)
assert rc == 0 and o.strip() == 'commit', '★親が commit で無い★ rc=%d %r' % (rc, o)
rc, o, e = g('show-ref', '--verify', EDA)
assert rc != 0, '★枝が既に在る★ ―― 新設の形(旧値=空)は落ちる。止まる。 %r' % o
w('前提: 親 %s = commit / 枝 %s = ★未在(rc=%d)★' % (OYA[:8], EDA, rc))

# ―― 甲 束を歩く(此の一歩きが「木に入れる物」の全部) ――――――――
aru = []
for root, dirs, files in os.walk(os.path.join(NE, TABA)):
    dirs.sort()
    for f in sorted(files):
        p = os.path.join(root, f)
        st = os.lstat(p)
        import stat as _s
        assert _s.S_ISREG(st.st_mode), '★非regular★ %s' % p
        assert not os.access(p, os.X_OK), '★実行権有り(mode 100755 が要る)★ %s' % p
        aru.append(os.path.relpath(p, NE))
aru.sort()
w('甲 歩いた現物 = ★%d本★(全て regular / 全て mode 100644)' % len(aru))

# ―― 乙 私有 index の上で木を組む ―――――――――――――――――
if os.path.exists(IDX): os.remove(IDX)
rc, o, e = g('read-tree', OYA, env=env); assert rc == 0, 'read-tree rc=%d %s' % (rc, e)
rc, o, e = g('ls-files', '--cached', env=env); moto = len(o.splitlines())
w('乙 read-tree %s → index の元入 = %d 件(★共有 index に非ず。%s★)' % (OYA[:8], moto, IDX))

for rel in aru:
    rc, o, e = g('hash-object', '-w', '--', rel)
    assert rc == 0, 'hash-object rc=%d %s' % (rc, e)
    b = o.strip()
    rc, o, e = g('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (b, rel), env=env)
    assert rc == 0, 'update-index rc=%d %s' % (rc, e)
rc, o, e = g('ls-files', '--cached', env=env); ato = len(o.splitlines())
w('乙 %d本を据ゑた → index = %d 件(増 %d)' % (len(aru), ato, ato - moto))

rc, t, e = g('write-tree', env=env); assert rc == 0, 'write-tree rc=%d %s' % (rc, e); t = t.strip()
rc, c, e = g('commit-tree', t, '-p', OYA, '-F', os.path.join(NE, TABA, '_after/91_msg.txt'))
assert rc == 0, 'commit-tree rc=%d %s' % (rc, e); c = c.strip()
w('乙 tree = %s / commit = ★%s★(親 %s)' % (t, c, OYA[:8]))

# ―― 丙 据ゑる前に木を検める(対照が無ければ止まる) ―――――――――
rc, o, e = g('ls-tree', '-r', '--full-tree', '--name-only', c, '--', TABA + '/')
assert rc == 0, 'ls-tree rc=%d %s' % (rc, e)
ki = sorted(x for x in o.splitlines() if x)
open(os.path.join(NE, TABA, '_after/93_lstree.txt'), 'w', encoding='utf-8').write(
    ''.join(x + '\n' for x in ki))
w('丙 commit の木(根相対・--full-tree) = ★%d本★' % len(ki))

T = ['★対照 其の一 ―― 既知の1本が出目に在るか(無ければ止まれ)★']
T.append('  求めた path = %s' % SHIRU)
T.append('  出目に在り  = %s' % ('★在り★' if SHIRU in ki else '★無し★'))
assert SHIRU in ki, '★陽性対照が落ちた。据ゑぬ。★'

rc2, o2, e2 = subprocess.run(
    ['git', 'ls-tree', '-r', '--name-only', c, '--', TABA + '/'],
    cwd=os.path.join(NE, TABA), capture_output=True, text=True).returncode, None, None
p2 = subprocess.run(['git', 'ls-tree', '-r', '--name-only', c, '--', TABA + '/'],
                    cwd=os.path.join(NE, TABA), capture_output=True, text=True)
T.append('')
T.append('★対照 其の二 ―― 家老mac の踏んだ疵を、此方でも実際に踏んで録る★')
T.append('  束の中(cwd=<束>)から `-C` 無し・`--full-tree` 無しで同じ pathspec を呼ぶと:')
T.append('    rc = %d / 出た本数 = ★%d本★' % (p2.returncode, len([x for x in p2.stdout.splitlines() if x])))
T.append('    ★rc=0 の儘 0本を返す ―― 之が「鳴らぬ零」である。★')
T.append('  ∴ 本器の甲の測りは `git -C <根>` + `--full-tree` の側のみを採る。')

# 丁 disk と commit の異
d1 = sorted(set(aru) - set(ki)); d2 = sorted(set(ki) - set(aru))
w('丁 disk(歩いた%d) と commit(%d) の異 = ★%d★ (disk のみ %d / commit のみ %d)'
  % (len(aru), len(ki), len(d1) + len(d2), len(d1), len(d2)))
assert not d1 and not d2, '★異が在る★ disk only=%r commit only=%r' % (d1, d2)

# ―― 戊 枝へ落とす(新設ゆゑ旧値=空形) ――――――――――――――――
rc, o, e = g('update-ref', EDA, c, '')
assert rc == 0, 'update-ref rc=%d %s' % (rc, e)
rc, o, e = g('rev-parse', EDA); assert rc == 0
yomi = o.strip()
w('戊 update-ref %s ← %s (旧値=★空(新設)★) / 読戻し = %s / 一致 = %s'
  % (EDA, c[:8], yomi, '★是★' if yomi == c else '★非★'))
assert yomi == c

# ―― 己 据ゑた後、disk を再度歩いて差を名指す(本器の出目が出る筈) ――
ato_aru = []
for root, dirs, files in os.walk(os.path.join(NE, TABA)):
    dirs.sort()
    for f in sorted(files):
        ato_aru.append(os.path.relpath(os.path.join(root, f), NE))
ato_aru.sort()
nochi = sorted(set(ato_aru) - set(ki))
T.append('')
T.append('★対照 其の三 ―― 据ゑた後に disk を再度歩く(本器の出目が差に成る筈)★')
T.append('  据ゑた後の disk = %d本 / commit = %d本 / disk のみ = ★%d本★' % (len(ato_aru), len(ki), len(nochi)))
for x in nochi:
    T.append('    %s' % x)
T.append('  ★之は疵に非ず。本器が commit の後に書いた己の出目である。★')
T.append('  ★判じ★: disk のみの %d本が悉く `_after/9` で始まるか = %s'
         % (len(nochi), '★是★' if all(os.path.basename(x).startswith(('92_', '93_', '94_')) for x in nochi) else '★非★'))
open(os.path.join(NE, TABA, '_after/94_taisho.txt'), 'w', encoding='utf-8').write(
    ''.join(x + '\n' for x in T))

w('')
w('★枝 %s = %s★' % (EDA, c))
open(os.path.join(NE, TABA, '_after/92_sueru.txt'), 'w', encoding='utf-8').write(
    ''.join(x + '\n' for x in L))
