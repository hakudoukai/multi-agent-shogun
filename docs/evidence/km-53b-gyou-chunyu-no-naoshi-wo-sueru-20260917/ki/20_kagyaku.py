# -*- coding: utf-8 -*-
"""usage: 20_kagyaku.py <repo根> <束外の写し置場>
★可逆を「書く」のでなく「測る」★(家老條㋐)。束外の写しへ当て・逆当てし、sha を三点で測る。
  ①元 sha16 → ②当てた後 sha16(動く事) → ③逆当ての後 sha16(★①と同じへ戻る事★)
生器へは一字も書かぬ ―― 読むのみ。書くのは <束外の写し置場> の中だけである。
"""
import sys, os, hashlib, shutil, subprocess

R, S = sys.argv[1], sys.argv[2]
TGT = [ 'scripts/inbox_watcher.sh',
        'scripts/watchdogs/enter_restart_common_watchdog.sh',
        'scripts/agent_health_check.sh',
        'scripts/checks/context_usage_warn.sh' ]

MAE = r"""  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
ATO = r"""  _ft_vp="$(printf '%s' "${_ft_v}" | tr '\n\r\t' '\266\215\211')"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定不変・表示のみ)★
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def bash_n(p):
    r = subprocess.run(['/bin/bash', '-n', p], capture_output=True, text=True)
    return r.returncode, (r.stderr.strip() or '(出目無し)')

os.makedirs(S, exist_ok=True)
o = ['=== ㋐ 可逆の實測 ―― 束外の写しへ当て、逆当てで同じ sha へ戻る事 ===',
     '写し置場(★束外★・生器でも束でもない): ' + S, '']
o.append('#colspec\t生器\t①元sha16\t②当後sha16\t①≠②\t③逆当後sha16\t★①=③★\tbash -n rc(当後)\t当てた箇所数\t逆当ての箇所数')
ok = True
for t in TGT:
    src = os.path.join(R, t)
    dst = os.path.join(S, t.replace('/', '__'))
    shutil.copyfile(src, dst)            # ★写す★(生器は読むのみ)
    s1 = sha(dst)
    b = open(dst, encoding='utf-8').read()
    n1 = b.count(MAE)
    assert n1 == 1, '★当てる行が %d 本 ―― 1 本で無ければ当てぬ(fail-closed)★ %s' % (n1, t)
    b2 = b.replace(MAE, ATO, 1)
    open(dst, 'w', encoding='utf-8').write(b2)
    s2 = sha(dst)
    rc, err = bash_n(dst)
    n2 = b2.count(ATO)
    assert n2 == 1, '★逆当ての的が %d 本★ %s' % (n2, t)
    b3 = b2.replace(ATO, MAE, 1)
    open(dst, 'w', encoding='utf-8').write(b3)
    s3 = sha(dst)
    ugoku = '★動いた★' if s1 != s2 else '★動かぬ(當たつて居らぬ)★'
    modoru = '★戻つた★' if s1 == s3 else '★戻らぬ★'
    if s1 == s2 or s1 != s3 or rc != 0:
        ok = False
    o.append('%s\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%d' % (t, s1, s2, ugoku, s3, modoru, rc, n1, n2))
    if rc != 0:
        o.append('\t★bash -n の出目★\t' + err.replace('\n', ' / '))
o.append('')
o.append('★生器への書込★: 0 字(上の路は src を open(rb) で讀み shutil.copyfile で写すのみ)')
o.append('★判★: ' + ('四本悉く 可逆(sha が動き・逆当てで元の sha へ戻り・bash -n rc=0)' if ok else '★一本以上 落ちた ―― 據ゑるな★'))
print('\n'.join(o))
open(os.path.join(R, 'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/20_kagyaku.tsv'),
     'w', encoding='utf-8').write('\n'.join(o) + '\n')
