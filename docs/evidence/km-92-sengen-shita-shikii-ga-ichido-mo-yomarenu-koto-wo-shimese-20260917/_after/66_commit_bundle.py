# -*- coding: utf-8 -*-
"""66 束の commit(第81弾 km-92・員外)―― 直しの commit(45)の上に、束 docs/evidence/km-92-…/ を ★同じ温 recipe★(temp index・hash-object・update-index --cacheinfo・worktree を讀まぬ・触らぬ)で二つ目の commit として自枝へ据ゑる。symlink(raw/stub_gnu/date)は 120000 で載せる。0 byte の file は載せぬ(在れば名指して落ちる)。porcelain 前後 一字も変はらぬ事を刷る。push は請はぬ。"""
import os, sys, subprocess, hashlib, time, stat
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; OUT = D + '/_after'
BR = 'ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917'; REL = os.path.relpath(D, M)
def git(*a, env=None, inp=None): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M, env=env, input=inp); return p.stdout.strip(), p.stderr.strip(), p.returncode
before, _, _ = git('status', '--porcelain'); parent, _, rcp = git('rev-parse', '--verify', '-q', 'refs/heads/' + BR); assert rcp == 0, '枝が無い(45 が先)'
out = [f'# 66 束の commit / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 {BR} / 親(直しの commit) {parent}']
idx = subprocess.run(['mktemp', '-u'], capture_output=True, text=True).stdout.strip(); env = dict(os.environ); env['GIT_INDEX_FILE'] = idx
o, e, rc = git('read-tree', parent, env=env); out.append(f'read-tree {parent[:12]} rc {rc} {e}')
n = nl = 0; zero = []; skipped = []
for d, ds, fs in os.walk(D):
    ds[:] = sorted(x for x in ds if x != '__pycache__')
    for f in sorted(fs):
        q = os.path.join(d, f); rel = os.path.relpath(q, M); st = os.lstat(q)
        if stat.S_ISLNK(st.st_mode):
            tgt = os.readlink(q); blob = subprocess.run(['git', 'hash-object', '-w', '--stdin'], input=tgt, capture_output=True, text=True, cwd=M).stdout.strip(); mode = '120000'; nl += 1
        elif stat.S_ISREG(st.st_mode):
            if st.st_size == 0: zero.append(rel); continue
            blob, _, _ = git('hash-object', '-w', q); mode = '100755' if os.access(q, os.X_OK) else '100644'; n += 1
        else: skipped.append(rel); continue
        o, e, rc = git('update-index', '--add', '--cacheinfo', f'{mode},{blob},{rel}', env=env); assert rc == 0, (rel, e)
assert not zero, f'0 byte の file が在る(載せぬ・名指す): {zero}'
tree, e, rc = git('write-tree', env=env); out.append(f'write-tree → {tree} rc {rc} / 載せた通常 file {n} + symlink {nl} / 非通常(飛ばした) {skipped}')
msg = f'''evidence(km-92): ★宣した閾が一度も讀まれぬ事を示し、方言と非數の番人を塞いだ★ ―― 專任1 第81弾(直し= 親 commit {parent[:12]})

束 {REL}/ = 紙 README.md + 追紙 TSUIGAMI_km86.md(km-86 疵二つ)+ raw/(器と出目・写し utsushi/ と直した写し 40_utsushi/・stub 四組・.first/.second)+ MANIFEST.txt + _gate/ + _after/。
生器へ 0 字・稼働 watcher 不觸・push 請はず。

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
'''
K.kaku(OUT + '/66_commit_msg.txt', msg)
c, e, rc = git('commit-tree', tree, '-p', parent, '-F', OUT + '/66_commit_msg.txt', env=env); out.append(f'commit-tree -p {parent[:12]} → {c} rc {rc} {e}')
o, e, rc = git('update-ref', f'refs/heads/{BR}', c, parent, env=env); out.append(f'update-ref(旧値 {parent[:12]} を検めて) rc {rc} {e}')
if os.path.exists(idx): os.remove(idx)
after, _, _ = git('status', '--porcelain'); out.append(f'★porcelain 前後: {"一字も変はらず(一致)" if before == after else "★変はつた★"} / {len(before.split(chr(10)))} 行 / sha16 {hashlib.sha256(before.encode()).hexdigest()[:16]} → {hashlib.sha256(after.encode()).hexdigest()[:16]}★')
st_, _, _ = git('diff', '--stat', parent, c); out.append('git diff --stat 親..束: ' + st_.split('\n')[-1].strip())
names, _, _ = git('diff', '--name-only', parent, c); outside = [x for x in names.split('\n') if x and not x.startswith(REL + '/')]; out.append(f'★束の外で変はつた file {len(outside)} 本 {outside}(0 なら ○)★')
lg, _, _ = git('log', '--format=%H %P %ci %s', '-2', BR); out.append('git log -2 枝:\n' + '\n'.join('  ' + l[:160] for l in lg.split('\n')))
out.append(f'★枝 {BR} / 束の full sha {c} / 直しの full sha {parent} / push は請はぬ★')
K.kaku(OUT + '/66_commit_bundle.txt', '\n'.join(out)); print('\n'.join(out))
