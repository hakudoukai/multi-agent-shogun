# -*- coding: utf-8 -*-
"""45 直しの commit(第81弾 km-92 ㋓)―― 札の温 recipe(temp index・共有 worktree を汚さぬ)で ★的 一本のみ★ を自枝へ commit する。生の scripts/lib/detect_stale.sh には触れぬ: 直した写し raw/40_utsushi/scripts/lib/detect_stale.sh を `git hash-object -w` で blob にし `update-index --add --cacheinfo` で index へ据ゑる(worktree を読まぬ)。
前後の `git status --porcelain` を刷つて一字も変はらぬ事を示す。push は請はぬ(枝名と full sha を報せる)。"""
import os, sys, subprocess, hashlib, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
BR = 'ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917'; TGT = 'scripts/lib/detect_stale.sh'; FIX = D + '/raw/40_utsushi/scripts/lib/detect_stale.sh'
def git(*a, env=None, inp=None): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M, env=env, input=inp); return p.stdout.strip(), p.stderr.strip(), p.returncode
fb = open(FIX, 'rb').read(); fsha = hashlib.sha256(fb).hexdigest()
before, _, _ = git('status', '--porcelain'); K.kaku(D + '/raw/45_porcelain_before.txt', before)
main, _, _ = git('rev-parse', 'main'); exists, _, rc_ex = git('rev-parse', '--verify', '-q', 'refs/heads/' + BR)
out = [f'# 45 直しの commit / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 {BR} / 親 main {main} / 枝は{"★既に在る(打たぬ)★" if rc_ex == 0 else "無し(新設)"} / 直し sha256 {fsha} {len(fb)}B {fb.count(b"\n")}行']
if rc_ex == 0: K.kaku(D + '/raw/45_commit.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(3)
msg = f'''fix(lib): detect_stale.sh ―― 宣した閾 DETECT_STALE_STALE_SEC を★讀ませ★、date -d の方言と非數の番人を塞ぐ(km-92)

的= scripts/lib/detect_stale.sh 一本(前 sha16 de4fefbdadb2be63 292行 → 後 sha16 {fsha[:16]} {fb.count(b"\n")}行)。

㋐ 閾: DETECT_STALE_STALE_SEC(設計 §1.2 verbatim 120s)は宣のみで讀手 0 であつた(repo 全体 git grep 1 行= 宣其の物・
   閾を 999999/abc にしても出目不変)。stale= now ≥ deadline + 閾 とし、閾は比較器そのもの [ -ge 0 ] で検め、
   空/空白/非數/負/桁溢れは名指しの WARN と共に既定 120 へ倒す(裁 seq323062⑷ 甲乙)。
㋑ 方言: `date -d` は GNU 語法・BSD(macOS)では rc1 → `|| echo "0"` → 正しい時刻も悉く ANOMALY。python3 の
   fromisoformat(本 lib が既に json で依る・enter_restart_common_watchdog.sh と同 idiom)へ。
㋒ 番人: `[ "$deadline_epoch" -le 0 ]` は非數(abc/空/1e3/2^63/改行)で rc2 → if 偽 → 次の [ -lt ] も偽 →
   STALE 候補へ落ち auto-poke(実測: 悉く enqueued=1)。出目を 數字のみ + [ -gt 0 ] && [ -le 253402300799 ] で検み ANOMALY へ。

実測= docs/evidence/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917/(別 commit)。
既存 test 二本(scripts/tests/test_detect_stale.sh / test_fukuincho_detect_stale_cli.sh)は写しの樹で GNU 姿・BSD+flock 姿とも PASS。

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
'''
K.kaku(D + '/raw/45_commit_msg.txt', msg)
idx = subprocess.run(['mktemp', '-u'], capture_output=True, text=True).stdout.strip(); env = dict(os.environ); env['GIT_INDEX_FILE'] = idx
o, e, rc1 = git('read-tree', main, env=env); out.append(f'read-tree {main[:12]} rc {rc1} {e}')
blob, e, rc2 = git('hash-object', '-w', FIX); out.append(f'hash-object -w 直し → blob {blob} rc {rc2} {e}')
o, e, rc3 = git('update-index', '--add', '--cacheinfo', f'100644,{blob},{TGT}', env=env); out.append(f'update-index --cacheinfo 100644,{blob[:12]},{TGT} rc {rc3} {e}')
tree, e, rc4 = git('write-tree', env=env); out.append(f'write-tree → {tree} rc {rc4} {e}')
c, e, rc5 = git('commit-tree', tree, '-p', main, '-F', D + '/raw/45_commit_msg.txt', env=env); out.append(f'commit-tree -p main → {c} rc {rc5} {e}')
o, e, rc6 = git('update-ref', f'refs/heads/{BR}', c, env=env); out.append(f'update-ref refs/heads/{BR} rc {rc6} {e}')
if os.path.exists(idx): os.remove(idx)
after, _, _ = git('status', '--porcelain'); K.kaku(D + '/raw/45_porcelain_after.txt', after)
out.append(f'★porcelain 前後: {"一字も変はらず(一致)" if before == after else "★変はつた★"} / 前 {len(before.split(chr(10)))} 行 / 後 {len(after.split(chr(10)))} 行 / sha16 前 {hashlib.sha256(before.encode()).hexdigest()[:16]} 後 {hashlib.sha256(after.encode()).hexdigest()[:16]}★')
st, _, _ = git('diff', '--stat', main, c); out.append(f'git diff --stat main..{c[:12]}:\n' + '\n'.join('  ' + l for l in st.split('\n')))
names, _, _ = git('diff', '--name-only', main, c); out.append(f'★変はつた file= {names.split()} ({len(names.split())} 本・的一本なら ○)★')
shown = subprocess.run(['git', 'show', f'{c}:{TGT}'], capture_output=True, cwd=M).stdout; out.append(f'git show {c[:12]}:{TGT} sha256 {hashlib.sha256(shown).hexdigest()} → 直しと {"一致" if shown == fb else "★不一致★"} / 生 {TGT} は {"不変(sha16 de4fefbdadb2be63)" if hashlib.sha256(open(M + "/" + TGT, "rb").read()).hexdigest()[:16] == "de4fefbdadb2be63" else "★変はつた★"}')
lg, _, _ = git('log', '--format=%H %P %ci %s', '-1', c); out.append('git log -1: ' + lg[:200])
out.append(f'★枝 {BR} / full sha {c} / push は請はぬ(代行は家老が総監督へ)★')
K.kaku(D + '/raw/45_commit.txt', '\n'.join(out)); print('\n'.join(out))
