# -*- coding: utf-8 -*-
"""20_kotei.py ―― ★一手目の版凍結★(第52弾で家老が据ゑた lane の作法㋐)。
的の生器 8本(札 scope_in の名)＋ HEAD ＋ 刻 を刷り、以後の紙は悉く此の sha16 を指す。
出し先= nama/00_kotei.txt(kaki 経由)。★生器へ 0 字(open は 'rb' 読取のみ)★。"""
import os, sys, io, time, subprocess, hashlib
B = sys.argv[1]; sys.path.insert(0, B + '/ki'); import importlib.util
M = '/Users/momizimac/multi-agent-shogun'
NAMA = [
    'scripts/agent_health_check.sh',
    'scripts/inbox_watcher.sh',
    'scripts/stop_hook_inbox.sh',
    'scripts/checks/karo_mac_gate4.sh',
    'scripts/checks/context_usage_warn.sh',
    'scripts/checks/karo_mac_dasumae_gate.sh',
    'scripts/watchdogs/enter_restart_common_watchdog.sh',
    'scripts/redundancy/shogun_report_watcher.sh',
]
KARO = {  # 札 scope_in が宣した行番(定義/呼び手)
    'scripts/agent_health_check.sh': (91, 117),
    'scripts/inbox_watcher.sh': (130, 156),
    'scripts/stop_hook_inbox.sh': (58, 65),
    'scripts/checks/karo_mac_gate4.sh': (68, 93),
    'scripts/checks/context_usage_warn.sh': (37, 63),
    'scripts/checks/karo_mac_dasumae_gate.sh': (36, 60),
    'scripts/watchdogs/enter_restart_common_watchdog.sh': (81, 107),
    'scripts/redundancy/shogun_report_watcher.sh': (35, 61),
}
out = []
out.append(u'★km-85 版凍結★ 刻=%s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=M).stdout.strip()
out.append(u'HEAD=%s' % head)
out.append(u'母數の根=%s (生器は札 scope_in の 8本)' % M)
out.append(u'')
out.append(u'file\tsha16\tbytes\t行(\\n 数へ)\t定義行(家老宣)\t呼び手行(家老宣)')
miss = 0
for f in NAMA:
    p = os.path.join(M, f)
    if not os.path.isfile(p):
        out.append(u'%s\t★実体無★\t-\t-\t-\t-' % f); miss += 1; continue
    d = open(p, 'rb').read()
    out.append(u'%s\t%s\t%d\t%d\t%d\t%d' % (
        f, hashlib.sha256(d).hexdigest()[:16], len(d), d.count(b'\n'),
        KARO[f][0], KARO[f][1]))
out.append(u'')
out.append(u'★実体無=%d★' % miss)
out.append(u'註: 家老 第52弾 便の「今の sha16 15ac9f97f473245d」は本 8本の何れにも当たらぬ(後述 30 で全 repo を歩いて確かめる)。')
body = u'\n'.join(out) + u'\n'
sys.stderr.write(body)
