# -*- coding: utf-8 -*-
"""10 読み手の戸籍(㋐㋑)―― 四器の _th_say の行が落ちる先と、其の先を ★讀む器★ を数へる(凍結版 repo・~/bin・Mac 起動器・走る process)。零には四札。"""
import os, sys, glob, re, subprocess, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; C = '6dbe09e6'; H = os.path.expanduser('~')
def sh(cmd): p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=M); return p.stdout, p.returncode
rows = []; out = [f'# 10 読み手の戸籍 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 凍結点 {C} / 根と深さ= ⒜ git grep {C} -- scripts .claude(凍結版の樹) ⒝ ~/bin/*.sh *.py(深さ 1) ⒞ ~/hermes-departments-mac/bin/*.sh(Mac 起動器・深さ 1) ⒟ 走る process(lsof)']
# 落ち先(源の行)
saki = {'watcher': ('scripts/inbox_watcher.sh', r'^_th_say\(\)'), 'watchdog': ('scripts/watchdogs/enter_restart_common_watchdog.sh', r'^_th_say\(\)|^log\(\)'), 'health': ('scripts/agent_health_check.sh', r'^_th_say\(\)'), 'ctxwarn': ('scripts/checks/context_usage_warn.sh', r'^_th_say\(\)')}
out.append('=== ⑴ 落ち先(源の逐語・凍結版) ===')
for k, (p, pat) in saki.items():
    src = subprocess.run(['git', 'show', f'{C}:{p}'], capture_output=True, text=True, cwd=M).stdout.split('\n')
    for i, l in enumerate(src, 1):
        if re.search(pat, l): out.append(f'  {k:9s} {p}:{i}: {l.strip()[:120]}')
out.append('  → watcher/health/ctxwarn= stderr(>&2)・watchdog= tee -a $LOG(ER_LOG_DIR/日付.log)+stdout')
# ⑵ 読み手(repo 凍結版)
out.append('=== ⑵ 落ち先を讀む器 ―― 凍結版 repo(git grep -n・supervisor の >> は書き手ゆゑ除く) ===')
pats = [('inbox_watcher の log を讀む', r"(tail|grep|awk|cat|sed|head|less|python)[^|]*(logs/inbox_watcher_|inbox_watcher_[a-z0-9-]*\.log|/tmp/inbox_watcher_[a-z0-9-]*\.log)"),
        ('watchdog の log を讀む', r"(tail|grep|awk|cat|sed|head|python)[^|]*(ER_LOG_DIR|enter_restart_[a-z_]*/|service\.log)"),
        ('health_check の出目を讀む', r"agent_health_check\.sh[^#]*(2>|\||\$\()"),
        ('ctxwarn の出目を讀む', r"context_usage_warn\.sh[^#]*(2>|\||\$\()")]
for name, pat in pats:
    o, rc = sh(f"git grep -n -E '{pat}' {C} -- scripts .claude | grep -v -E 'scripts/inbox_watcher.sh:|scripts/agent_health_check.sh:|scripts/checks/context_usage_warn.sh:|enter_restart_common_watchdog.sh:'")
    n = len([l for l in o.split('\n') if l.strip()]); rows.append(('repo@' + C, name, n, rc)); out.append(f'  {name}: {n} 行 (rc {rc})'); [out.append('    ' + l[:150]) for l in o.split('\n') if l.strip()][:8]
o, rc = sh(f"git grep -l -E 'inbox_watcher\\.sh' {C} -- scripts | wc -l"); out.append(f'  ★陽性対照(同じ git grep が在る語 inbox_watcher.sh を拾ふ file 数)= {o.strip()} (rc {rc})')
# ⑶ ~/bin
out.append('=== ⑶ ~/bin(深さ 1・.sh .py・repo 外・讀むのみ) ===')
files = sorted(glob.glob(H + '/bin/*.sh') + glob.glob(H + '/bin/*.py')); hit = []
for f in files:
    t = open(f, encoding='utf-8', errors='replace').read()
    if re.search(r'inbox_watcher_[a-z0-9-]*\.log|logs/inbox_watcher|enter_restart|agent_health_check|context_usage_warn|\[watcher\]|\[health_check\]|\[context_warn\]', t): hit.append(os.path.basename(f))
pos = sum(1 for f in files if 'queue/inbox' in open(f, encoding='utf-8', errors='replace').read())
out.append(f'  母數 {len(files)} 本 / 四器の出目を指す語を持つ file= {len(hit)} 本 {hit} / ★陽性対照 同じ讀み方で「queue/inbox」を持つ file= {pos} 本★'); rows.append(('~/bin', '四器の出目を指す', len(hit), 0))
# ⑷ Mac 起動器
bt = H + '/hermes-departments-mac/bin/boot-mac-fleet.sh'; t = open(bt, encoding='utf-8', errors='replace').read().split('\n')
out.append('=== ⑷ Mac 起動器(repo 外・讀むのみ)―― 四器の出目を何処へ結ぶか ===')
for i, l in enumerate(t, 1):
    if re.search(r'inbox_watcher|health_check|watchdog|context_usage', l): out.append(f'  {os.path.relpath(bt, H)}:{i}: {l.strip()[:140]}')
out.append('  → 起動器は stderr を /tmp/inbox_watcher_$ag.log へ結ぶと書くが、★走る process は logs/ へ結んで居る(⑸)★ ―― 起動元は起動器ではない(09-10 20:07:54 の起動・第73弾までに家老が別経路で起こした由・本紙は「起動元 未特定」と書く)')
# ⑸ 走る process
o, rc = sh("L=$(command -v lsof); $L -p 9826 -a -d 1,2,255 2>&1"); out.append('=== ⑸ 走る watcher(pid 9826・己の箱)の fd 1/2/255(lsof・刻は本 file 頭) ==='); [out.append('  ' + l[:150]) for l in o.split('\n') if l.strip()]
o2, _ = sh("grep -c '' logs/inbox_watcher_ashigaru-mac-1.log; grep -c 'unread' logs/inbox_watcher_ashigaru-mac-1.log; grep -c '閾' logs/inbox_watcher_ashigaru-mac-1.log; echo rc=$?")
a = o2.split(); out.append(f'  logs/inbox_watcher_ashigaru-mac-1.log: 総行 {a[0]} / 在る語 unread {a[1]} 行(陽性対照) / 「閾」の行 {a[2]} ({a[3]})―― ★走る器は旧 inode(00_start)ゆゑ 6dbe09e6 の _th_say は一度も走つて居らぬ。0 は「無い」でなく「未だ刷られて居らぬ」★')
out.append('=== ∴ ㋐㋑ の答(此の母數の内) === 四器の _th_say の行を ★値として讀み返す器= 0★(repo 凍結版 0・~/bin 0・起動器 0)。讀む者は人と Claude(端末・紙)であり、器の外。')
K.kaku(D + '/raw/10_yomite.txt', '\n'.join(out)); K.kaku_tsv(D + '/raw/10_yomite.tsv', rows, ['根', '何を', '本', 'rc']); print('\n'.join(out))
