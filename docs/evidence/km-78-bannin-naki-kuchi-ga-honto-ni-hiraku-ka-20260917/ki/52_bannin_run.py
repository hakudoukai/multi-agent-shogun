# -*- coding: utf-8 -*-
"""52 ★番人の写しを走らせる★ ―― 「番人在り」を字面でなく出目で確かめる(㋒)
當席の点呼器(10)は `fix_threshold NAME` を ★口の行で★ 探した。然るに inbox_watcher.sh は
  `for _t in NAME:既定 … ; do fix_threshold "$_n" "$_d" "$_n"; done`
の ★輪の形★ で十名を一度に守る。∴ 點呼は之を見落し、當席は三口へ ①fail-open を誤って貼つた。
本器は写し(125-178 逐語)を走らせ、★倒れた後の値が數であるか★ を八形で見る。
★陽性対照★=形5(正常値7)は 7 の儘 通らねばならぬ(倒せば番人が効き過ぎ)。
★陰性対照★=番人の輪に ★入つて居らぬ★ 名(LAST_NUDGE_TS)を同じ八形で流し、素通りする事を示す。"""
import os, re, sys, subprocess, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
H = D + '/utsushi/bannin_harness.sh'
txt = open(D + '/utsushi/bannin_loop_verbatim.txt', encoding='utf-8').read()
m = re.search(r'for _t in (.+?); do', txt, re.S)
names = [t.split(':')[0] for t in m.group(1).replace('\\\n', ' ').split()]
FORMS = [('1未設定', None), ('2空文字', ''), ('3空白のみ', ' '),
         ('4二十桁', '99999999999999999999'), ('5正常値7', '7'), ('6負数', '-5'),
         ('7改行入り', '1\n2'), ('8既存␊', '1␊2')]
out, ctl, bad = [], [], 0
for name in names + ['LAST_NUDGE_TS']:
    neg = name == 'LAST_NUDGE_TS'
    for lab, val in FORMS:
        env = dict(os.environ); env.pop(name, None); env['KM_NAME'] = name
        if val is not None: env[name] = val
        p = subprocess.run(['/bin/bash', H], capture_output=True, text=True, env=env)
        # ★改行を含む値は OUT 行を跨ぐ★ ―― 初走は一行目だけを取り、`1␊2` を `1` と誤り
        # rc=0(倒れず)と刷つた。出目は末尾の OUT\t 以降を悉く取る。
        i = p.stdout.rfind('OUT\t')
        v = p.stdout[i+4:].rstrip('\n') if i >= 0 else '(出目無)'
        q = subprocess.run(['/bin/bash', '-c', '[ "$1" -ge 0 ]; echo $?', '_', v],
                           capture_output=True, text=True)
        rc = q.stdout.strip()
        say = '有' if '[watcher]' in p.stderr else '無'
        out.append([name, '陰性対照' if neg else '番人内', lab, repr(val), v.replace('\n', '␊'), rc, say])
        if lab == '5正常値7' and not neg and v != '7': bad += 1
        if not neg and rc == '2': ctl.append((name, lab, v))
K.kaku_tsv(D + '/raw/52_bannin.tsv', out,
           header=['name', '別', '形', '與へた値', '倒れた後の値', '比較器rc', '鳴り'])
sm = ['# 52 番人の写しを走らせた / 輪が守る名= %d / 陰性対照= 1 / 走= %d' % (len(names), len(out))]
sm.append('# 輪の十名: ' + ' '.join(names))
sm.append('★陽性対照(形5=7 が 7 の儘 通る)に外れた名= %d ―― 0 が健全★' % bad)
sm.append('★番人を通つた後に比較器が倒れた(rc=2)組= %d ―― 0 なら番人は効いて居る★' % len(ctl))
for n, l, v in ctl: sm.append('    ★破れ★ %s %s → 「%s」' % (n, l, v))
if not ctl: sm.append('    (空である旨の一行 ―― 破れは無い)')
neg_rows = [r for r in out if r[1] == '陰性対照']
sm.append('')
sm.append('# ★陰性対照★ LAST_NUDGE_TS(輪に入らぬ名) ―― 素通りする筈:')
for r in neg_rows: sm.append('    %-10s 與「%s」→ 後「%s」 比較器rc=%s 鳴り=%s' % (r[2], r[3], r[4], r[5], r[6]))
n2 = sum(1 for r in neg_rows if r[5] == '2')
sm.append('    ∴ 陰性対照は %d/8 形で比較器を倒す ―― ★番人の有無が出目を分ける事の証★' % n2)
sm.append('')
sm.append('★∴ 點呼(10)の「番人在= 2」は ★輪の形を見落した數★ である。')
sm.append('  輪が守る十名を加へれば、生器の口 81 の内 ★番人在★ は下の 53 で引き直す。')
K.kaku(D + '/raw/52_bannin_summary.txt', '\n'.join(sm))
print('\n'.join(sm))
