# -*- coding: utf-8 -*-
"""usage: 25_kagyaku_otsu.py <repo根> <束外の写し置場>
20_kagyaku.py と同じ形で ★案乙★(當席案)の可逆を測る。生器へは一字も書かぬ。
"""
import sys, os, hashlib, shutil, subprocess
R, S = sys.argv[1], sys.argv[2]
TGT = ['scripts/inbox_watcher.sh','scripts/watchdogs/enter_restart_common_watchdog.sh',
       'scripts/agent_health_check.sh','scripts/checks/context_usage_warn.sh']
MAE = r"""  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
OTSU = """  _ft_vp="${_ft_v//$'\\n'/␊}"; _ft_vp="${_ft_vp//$'\\r'/␍}"; _ft_vp="${_ft_vp//$'\\t'/␉}"  # ★行注入封じ(乙)★: bash の置換ゆゑ多byteの可視印が置ける・fork 無し・判定不変
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
sha = lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
os.makedirs(S, exist_ok=True)
o = ['=== ㋐ 可逆の實測(★案乙★・當席案) ―― 束外の写しへ当て、逆当てで同じ sha へ戻る事 ===',
     '写し置場: ' + S, '',
     '#colspec\t生器\t①元sha16\t②当後sha16\t①≠②\t③逆当後sha16\t★①=③★\tbash -n rc(当後)\t当\t逆']
ok = True
for t in TGT:
    src = os.path.join(R, t); dst = os.path.join(S, 'otsu__' + t.replace('/','__'))
    shutil.copyfile(src, dst)
    s1 = sha(dst); b = open(dst,encoding='utf-8').read()
    n1 = b.count(MAE); assert n1 == 1, '★的が %d 本★ %s' % (n1, t)
    b2 = b.replace(MAE, OTSU, 1); open(dst,'w',encoding='utf-8').write(b2); s2 = sha(dst)
    rc = subprocess.run(['/bin/bash','-n',dst],capture_output=True).returncode
    n2 = b2.count(OTSU); assert n2 == 1
    open(dst,'w',encoding='utf-8').write(b2.replace(OTSU, MAE, 1)); s3 = sha(dst)
    if s1 == s2 or s1 != s3 or rc != 0: ok = False
    o.append('%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d' % (t, s1, s2,
        '★動いた★' if s1!=s2 else '★動かぬ★', s3, '★戻つた★' if s1==s3 else '★戻らぬ★', rc, n1, n2))
o += ['', '★生器への書込★: 0 字', '★判★: ' + ('四本悉く可逆' if ok else '★落ちた★')]
print('\n'.join(o))
open(os.path.join(R,'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/25_kagyaku_otsu.tsv'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
