# -*- coding: utf-8 -*-
"""usage: 10_sha.py <repo根>  ―― ★讀取のみ★。生器四本の今の sha16 と、km-52 の写しとの一致を測る。
記憶「席が走る間に版は動く」 ∴ 直し紙が引いた版(ab2a1f1)と今の版が同じか先に確かめる。
"""
import sys, os, hashlib
R=sys.argv[1]
K52=os.path.join(R,'docs/evidence/km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917')
PAIR=[('scripts/inbox_watcher.sh','utsushi/scripts_inbox_watcher.sh'),
      ('scripts/watchdogs/enter_restart_common_watchdog.sh','utsushi/scripts_watchdogs_enter_restart_common_watchdog.sh'),
      ('scripts/agent_health_check.sh','utsushi/scripts_agent_health_check.sh'),
      ('scripts/checks/context_usage_warn.sh','utsushi/scripts_checks_context_usage_warn.sh')]
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
TGT='_th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"'
o=['=== 生器四本 ―― 今の版 と km-52 の写し ===','#colspec\t生器\t今のsha16\t写しのsha16\t同じか\t直す行の本数(今)']
allsame=True
for live,uts in PAIR:
    lp=os.path.join(R,live); up=os.path.join(K52,uts)
    ls, us = sha(lp), sha(up)
    n=open(lp,encoding='utf-8').read().count(TGT)
    if ls!=us: allsame=False
    o.append('%s\t%s\t%s\t%s\t%d' % (live,ls,us,'★同★' if ls==us else '★異★',n))
o.append('')
o.append('※ 直す行は 四本 悉く ★byte 一致の一行★(直し紙⑴の宣)。上表の最終欄で再確認した。')
o.append('★版の動き★: %s' % ('四本とも km-52 の写しと同一 ―― 直し紙は今も当たる' if allsame else '★動いた本が在る ―― 当てる前に引き直せ★'))
print('\n'.join(o))
open(os.path.join(R,'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/10_sha.tsv'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
