# -*- coding: utf-8 -*-
"""00 起(第74弾)―― 凍結点 commit 6dbe09e6 の四器 sha16(git show)と disk の sha16・走る watcher の inode を先に取る。読取のみ。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; C = '6dbe09e6'
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]
def git(*a): return subprocess.run(['git', *a], capture_output=True, text=True, cwd=M).stdout.strip()
def gitb(*a): return subprocess.run(['git', *a], capture_output=True, cwd=M).stdout
MATO = {'watcher': 'scripts/inbox_watcher.sh', 'watchdog': 'scripts/watchdogs/enter_restart_common_watchdog.sh', 'health': 'scripts/agent_health_check.sh', 'ctxwarn': 'scripts/checks/context_usage_warn.sh'}
HOKA = {'dasumae': 'scripts/checks/karo_mac_dasumae_gate.sh', 'gate4': 'scripts/checks/karo_mac_gate4.sh', 'append': 'scripts/checks/karo_mac_manifest_append.py', '照合器': 'scripts/checks/karo_mac_manifest_verify.py'}
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
out = [f'# 00 起 / 刻 {koku} / 枝 {git("branch","--show-current")} HEAD {git("rev-parse","--short","HEAD")} / 凍結点 {git("rev-parse", C)} ({git("log","-1","--format=%ad %s","--date=iso", C)[:60]})']
out.append('★四器(的・讀むのみ・scripts/ へ 0 字)★ 凍結版 sha16(git show) ／ disk sha16 ／ 一致')
for k, p in MATO.items():
    g = sha16(gitb('show', f'{C}:{p}')); d = sha16(open(f'{M}/{p}', 'rb').read()); out.append(f'  {k:9s} {p} 凍結 {g} disk {d} {"一致" if g == d else "★不一致(disk は凍結点でない)★"}')
out.append('門・臺帳の器(凍結版 sha16 / disk sha16): ' + ' / '.join(f'{k} {sha16(gitb("show", f"{C}:{p}"))}/{sha16(open(M+"/"+p,"rb").read())}' for k, p in HOKA.items()))
st = os.stat(f'{M}/scripts/inbox_watcher.sh'); out.append(f'disk の inbox_watcher.sh inode={st.st_ino} bytes={st.st_size}(lsof で見た走る pid 9826 の fd255 = inode 20564860 bytes 74274 ―― 09:01:53 實測・同じか= {"是" if st.st_ino == 20564860 else "★否(走る器は旧 inode)★"})')
out.append('前版(第72/73弾で引いた・★古い★・捨てる): watcher cac867f8 / watchdog b224557e / health 6493c1d7 / ctxwarn 897412b0')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
