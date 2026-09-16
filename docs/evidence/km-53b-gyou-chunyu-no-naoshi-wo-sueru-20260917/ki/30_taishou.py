# -*- coding: utf-8 -*-
"""usage: 30_taishou.py <repo根> <束外の写し置場>
㋒ ★負テスト★ を必ず添へる(家老條㋒「『塞いだ』を陽性だけで言ふな」)。
四本の★今の版★から fix_threshold の胴だけを抜いて台に載せ、前/後 の二版を同じ形で走らせる。
形: 甲=行注入(陽性・鳴りが2行→1行) 乙=★負1: 清い非数★(鳴り1行の儘・倒す先不変)
    丙=★負2: 正しい数★(鳴り0行の儘・値が通る=判定不変の證) 丁=★負3: 空文字★(別の枝・不変)
"""
import sys, os, re, hashlib, subprocess

R, S = sys.argv[1], sys.argv[2]
TGT = ['scripts/inbox_watcher.sh',
       'scripts/watchdogs/enter_restart_common_watchdog.sh',
       'scripts/agent_health_check.sh',
       'scripts/checks/context_usage_warn.sh']
MAE = r"""  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
ATO = r"""  _ft_vp="$(printf '%s' "${_ft_v}" | tr '\n\r\t' '\266\215\211')"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定不変・表示のみ)★
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
"""
DRV = '\nfix_threshold KM53B_TH 99 KM53B_OUT\nprintf "OUT=%s\\n" "${KM53B_OUT-（未設定）}"\n'

CHU = '1' + chr(10) + '★閾 KM53B_TH を比較器が扱へぬ(「0」) ―― 既定 0 へ倒す(fail-closed)★'
KATA = [('甲 行注入(★陽性★)', CHU),
        ('乙 ★負1★ 清い非数', 'abc'),
        ('丙 ★負2★ 正しい数', '777'),
        ('丁 ★負3★ 空文字', '')]

def dai(src_text, patched):
    # ★疵(初走)★: 頭から切ると 生器の preflight(argv 必須・env 必須・SUPABASE 必須)が先に死に、
    # fix_threshold へ一度も届かなんだ ―― 四本中 三本が「鳴り1行」を出したが、其れは ★札ではなく
    # preflight の悲鳴★ であつた。∴ ★助器四本の定義だけ★ を切り出す(preflight を一行も含めぬ)。
    b = src_text.replace(MAE, ATO, 1) if patched else src_text
    if patched:
        assert b.count(ATO) == 1, '★当たつて居らぬ★'
    i = b.index('_th_say(){')
    j = b.index('\n}\n', b.index(MAE if not patched else ATO))
    sl = b[i:j+3]
    for nm in ('_th_say', 'num_same_op', 'env_state', 'fix_threshold'):
        assert (nm + '(){') in sl, '★助器 %s が切り身に無い★' % nm
    atama = '#!/bin/bash\n'
    if 'log(){' not in sl and 'log()' not in sl:
        atama += 'log(){ printf \'%s\\n\' "$*" >&2; }  # ★台の代器★: 生器の log は preflight の向う側ゆゑ、同じ「stderr へ一行」で代へる\n'
    return atama + sl + DRV

def hashi(path, val):
    # ★text=True で受けるな★: 直しの tr は \266 = ★生 byte 0xB6★ を吐き、UTF-8 として不正ゆゑ
    # decode が例外で死ぬ(實測 2026-09-17)。bytes で受け、不正 byte を surrogateescape で温存する。
    e = dict(os.environ); e['KM53B_TH'] = val; e['LC_ALL'] = 'C'
    r = subprocess.run(['/bin/bash', path], capture_output=True, env=e)
    d = lambda b: b.decode('utf-8', 'surrogateescape')
    return r.returncode, d(r.stdout), d(r.stderr), r.stderr

o = ['=== ㋒ 陽性一形 ＋ ★負テスト三形★ ―― 前(現行)と 後(直し当て)を同じ台で ===',
     '台 = 各生器の今の版から ★助器四本(_th_say/num_same_op/env_state/fix_threshold)の定義だけ★ を抜き、駆動一行を足した物(束外 %s)' % S,
     '  ―― preflight は一行も含めぬ。初走は頭から切つて preflight で死に、四本中三本が札を一度も出さなんだ(raw/30_taishou.tsv.first に残す)', '']
o.append('#colspec\t生器\t形\t前:鳴り行数\t後:鳴り行数\t前:OUT\t後:OUT\t倒す先不変\t前:改行が札に入つたか\t後:改行が札に入つたか\t前rc\t後rc\t前:札のUTF-8\t後:札のUTF-8')
os.makedirs(S, exist_ok=True)
warui = []
for t in TGT:
    src = open(os.path.join(R, t), encoding='utf-8').read()
    ps = {}
    for tag, pat in (('mae', False), ('ato', True)):
        p = os.path.join(S, 'dai_%s__%s.sh' % (t.replace('/', '__'), tag))
        open(p, 'w', encoding='utf-8').write(dai(src, pat))
        ps[tag] = p
    for nm, val in KATA:
        rcm, som, sem, bm = hashi(ps['mae'], val)
        rca, soa, sea, ba = hashi(ps['ato'], val)
        def u8(b):
            try:
                b.decode('utf-8'); return '★正★'
            except UnicodeDecodeError as x:
                return '★不正 byte 0x%02X★' % b[x.start]
        nm_ = len([x for x in sem.split('\n') if x.strip()])
        na_ = len([x for x in sea.split('\n') if x.strip()])
        om = (re.search(r'OUT=(.*)', som) or [None, '(無)'])[1]
        oa = (re.search(r'OUT=(.*)', soa) or [None, '(無)'])[1]
        fuhen = '★同★' if om == oa else '★異★'
        # 札(=鳴り)の中に生の改行が持ち込まれたか ―― 一鳴りが二行に割れたかで見る
        wm = '★入つた★' if (chr(10) in val and nm_ >= 2) else '無'
        wa = '★入つた★' if (chr(10) in val and na_ >= 2) else '無'
        if om != oa:
            warui.append('%s %s 倒す先が動いた' % (t, nm))
        o.append('%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s'
                 % (t, nm, nm_, na_, om, oa, fuhen, wm, wa, rcm, rca, u8(bm), u8(ba)))
o.append('')
o.append('★負テストの読み★: 乙丙丁 は 前後で 鳴り行数・OUT・rc が悉く同じ ―― ★直しは清い値に一切触れぬ★。')
o.append('★陽性の読み★: 甲 のみ 前=2行 / 後=1行 ―― ★割れて居た札が一行に戻る★。OUT は前後同じ(★判定不変★)。')
o.append('★疵★: 直しの置換先 \\266 \\215 \\211 は ★生 byte 0xB6/0x8D/0x89★ ―― 紙は「可視印」と称するが')
o.append('      UTF-8 としては ★不正 byte★ である。改行は確かに消えるが、札を UTF-8 で讀む下流は decode で死ぬ')
o.append('      (實測: 本器が text=True で受けた初走が UnicodeDecodeError で倒れた)。')
o.append('★判★: ' + ('落ち無し' if not warui else '★落ち★ ' + ' ／ '.join(warui)))
print('\n'.join(o))
open(os.path.join(R, 'docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/raw/30_taishou.tsv'),
     'w', encoding='utf-8').write('\n'.join(o) + '\n')
