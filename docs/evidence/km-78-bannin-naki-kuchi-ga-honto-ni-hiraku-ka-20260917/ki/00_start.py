# -*- coding: utf-8 -*-
"""00 起(第56弾 km-78)―― 刻・枝・HEAD を取り、★的の生器の disk sha16 を凍結★する。
生器は他席が同じ夜に書き換へて居る(第55弾の教訓「席が走る間に版は動く」)。
∴ 本弾の全ての測りは ★此処で凍結した sha16 の版★ に対する物である。讀取のみ・0字も書かぬ。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'

def git(*a):
    p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M)
    return p.stdout.strip(), p.returncode

def sha16(p):
    try:
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except FileNotFoundError:
        return '★実体無★'

koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')

# 的 ―― 家老の見立が名指した器 + fix_threshold を持つ器(番人在り)
MATO = [
 'scripts/stop_hook_inbox.sh',
 'scripts/inbox_watcher.sh',
 'scripts/pane_enter_watcher_supervisor.sh',
 'scripts/lib/detect_stale.sh',
 'scripts/watchdogs/enter_restart_commander_watchdog.sh',
 'scripts/watchdogs/enter_restart_common_watchdog.sh',
 'scripts/agent_health_check.sh',
 'scripts/checks/context_usage_warn.sh',
 'scripts/checks/karo_mac_gate4.sh',
 'scripts/checks/karo_mac_dasumae_gate.sh',
 'scripts/redundancy/shogun_report_watcher.sh',
]
out = [f'# 00 起 / 刻 {koku} / 席 ashigaru-mac-2 / 枝 {br} / HEAD {head[:12]}']
out.append('# ★凍結★ 以下の sha16 は本弾の全測りの前提である。走り終りに再測して不変を示す(90 で検む)。')
for p in MATO:
    ap = os.path.join(M, p)
    ex = os.path.exists(ap)
    n = sum(1 for _ in open(ap, encoding='utf-8', errors='replace')) if ex else 0
    out.append(f'{sha16(ap)}\t{n}行\t{p}' + ('' if ex else '\t★disk に無い★'))
diff, rc = git('diff', '--name-only', 'HEAD', '--', 'scripts', '.claude')
out.append(f'# HEAD と disk の差(rc {rc}): {len(diff.splitlines())} 本 ―― ★走るのは disk・git grep は HEAD★ ゆゑ本弾は disk を測る')
for l in diff.splitlines():
    out.append('#   ' + l)
K.kaku(D + '/raw/00_start.txt', '\n'.join(out))
print('\n'.join(out))
