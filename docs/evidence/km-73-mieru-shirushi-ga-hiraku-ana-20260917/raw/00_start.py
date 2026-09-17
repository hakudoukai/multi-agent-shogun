# -*- coding: utf-8 -*-
"""00 起(第73弾・km-72 の写し)―― 生器四本(的)と門の器四本の sha16 と、讀むだけの束(專任2 km-53b・km-52 直し紙)の印を先に取る(60 が前⇔後を比べ、0 字 を示す)。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
def snap(d):
    rows = []
    for r, ds, fs in os.walk(d):
        for f in fs:
            q = os.path.join(r, f)
            if os.path.isfile(q) and not os.path.islink(q): rows.append(os.path.relpath(q, d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16] + f'({len(rows)})'
KI = {'門': 'scripts/checks/karo_mac_dasumae_gate.sh', 'gate4': 'scripts/checks/karo_mac_gate4.sh', '照合器': 'scripts/checks/karo_mac_manifest_verify.py', 'append': 'scripts/checks/karo_mac_manifest_append.py'}
MATO = {'watcher': 'scripts/inbox_watcher.sh', 'watchdog': 'scripts/watchdogs/enter_restart_common_watchdog.sh', 'health': 'scripts/agent_health_check.sh', 'ctxwarn': 'scripts/checks/context_usage_warn.sh'}
TABA = {'km-53b': 'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917', 'km-52': 'docs/evidence/km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917'}
head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=M).stdout.strip(); br = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, cwd=M).stdout.strip()
out = [f'# 00 起 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 {br} HEAD {head} / ' + ' / '.join(f'{k} sha16 {sha16(M + "/" + p)}' for k, p in KI.items()),
       '的(生器四本・讀むのみ・0 字): ' + ' / '.join(f'{k} {p} sha16 {sha16(M + "/" + p)}' for k, p in MATO.items())] + [f'{k} {snap(M + "/" + d)}→(00_start の前)' for k, d in TABA.items()]
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
