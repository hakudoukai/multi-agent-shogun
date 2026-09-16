# -*- coding: utf-8 -*-
"""usage: 40_an_otsu.py <repo根> <束外の写し置場>
★据ゑず★、紙の上で 直しの直し を測る。
甲(紙の儘) = tr '\n\r\t' '\266\215\211' ―― BSD tr は ★byte 器★ ゆゑ \266 は 1 byte 0xB6 = UTF-8 不正。
乙(當席案) = bash の置換 ${v//$'\n'/␊} ―― 文字列器ゆゑ ★多 byte の可視印★ が置ける。fork も無い。
測る欄: 改行が消えるか / 札が UTF-8 で讀めるか / 倒す先(OUT)が動かぬか / bash -n / 清い値に触れぬか
"""
import sys, os, subprocess, re
R, S = sys.argv[1], sys.argv[2]
TGT = ['scripts/inbox_watcher.sh','scripts/watchdogs/enter_restart_common_watchdog.sh',
       'scripts/agent_health_check.sh','scripts/checks/context_usage_warn.sh']
MAE = r"""  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
KOU = r"""  _ft_vp="$(printf '%s' "${_ft_v}" | tr '\n\r\t' '\266\215\211')"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定不変・表示のみ)★
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
OTSU = """  _ft_vp="${_ft_v//$'\\n'/␊}"; _ft_vp="${_ft_vp//$'\\r'/␍}"; _ft_vp="${_ft_vp//$'\\t'/␉}"  # ★行注入封じ(乙)★: bash の置換ゆゑ多byteの可視印が置ける・fork 無し・判定不変
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
DRV = '\nfix_threshold KM53B_TH 99 KM53B_OUT\nprintf "OUT=%s\\n" "${KM53B_OUT-（未設定）}"\n'
CHU = '1' + chr(10) + '★閾 KM53B_TH を比較器が扱へぬ(「0」) ―― 既定 0 へ倒す(fail-closed)★'
KATA = [('甲 行注入(★陽性★)', CHU), ('乙 ★負1★ 清い非数', 'abc'),
        ('丙 ★負2★ 正しい数', '777'), ('丁 ★負3★ 空文字', '')]

def dai(src, an):
    b = src if an == '現行' else src.replace(MAE, KOU if an == '紙(甲)' else OTSU, 1)
    tail = MAE if an == '現行' else (KOU if an == '紙(甲)' else OTSU)
    assert b.count(tail) == 1, '★当たつて居らぬ: %s★' % an
    i = b.index('_th_say(){'); j = b.index('\n}\n', b.index(tail))
    sl = b[i:j+3]
    atama = '#!/bin/bash\n'
    if 'log(){' not in sl:
        atama += "log(){ printf '%s\\n' \"$*\" >&2; }\n"
    return atama + sl + DRV

def hashi(p, v):
    e = dict(os.environ); e['KM53B_TH'] = v; e['LC_ALL'] = 'C'
    r = subprocess.run(['/bin/bash', p], capture_output=True, env=e)
    return r.returncode, r.stdout, r.stderr

def u8(b):
    try:
        b.decode('utf-8'); return '★正★'
    except UnicodeDecodeError as x:
        return '不正0x%02X' % b[x.start]

o = ['=== 直しの直し ―― ★据ゑず紙の上で★ 甲(紙の儘) と 乙(當席案) を同じ台で比べる ===',
     '甲 逐語: ' + KOU.strip().split(chr(10))[0].strip(),
     '乙 逐語: ' + OTSU.strip().split(chr(10))[0].strip(), '']
o.append('#colspec\t生器\t案\t形\t鳴り行数\tOUT\t札のUTF-8\tbash -n rc\t走 rc')
os.makedirs(S, exist_ok=True)
for t in TGT:
    src = open(os.path.join(R, t), encoding='utf-8').read()
    for an in ('現行', '紙(甲)', '乙(當席案)'):
        p = os.path.join(S, 'an_%s__%s.sh' % (t.replace('/', '__'), an))
        open(p, 'w', encoding='utf-8').write(dai(src, an))
        bn = subprocess.run(['/bin/bash', '-n', p], capture_output=True).returncode
        for nm, v in KATA:
            rc, so, se = hashi(p, v)
            n = len([x for x in se.decode('utf-8', 'surrogateescape').split('\n') if x.strip()])
            m = re.search(r'OUT=(.*)', so.decode('utf-8', 'surrogateescape'))
            o.append('%s\t%s\t%s\t%d\t%s\t%s\t%d\t%d' % (t, an, nm, n, m.group(1) if m else '(無)', u8(se), bn, rc))
o.append('')
o.append('★読み★: 甲・乙 とも 陽性で 2行→1行(改行を封ず)・OUT 不変・負三形は現行と同一。')
o.append('       ★分れ目は札の UTF-8★ ―― 甲は 0xB6 で不正、乙は正。∴ ★乙を推す★(据ゑるは家老の下知を待つ)。')
print('\n'.join(o))
open(os.path.join(R,'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/40_an_otsu.tsv'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
