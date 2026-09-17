# -*- coding: utf-8 -*-
"""30 ㋒ 毒表(第78弾 km-84)―― 20 が挙げた讀手(甲・乙・丙)の行ごとに ★束内の写し器★ を建て、8 値 `0` `1` `2` `01` `+1` 空文字 空白のみ ␊1(+補: 未設定)を env で当てる。
写し器= [受ける口の行(同 file の純粋な口 `N=${N:-d}` が在れば逐語・fix_flag の口は ★裸の比較器★ で測り 40 で番人付きを測る)] + `if <比較器 逐語>; then BRANCH=then else BRANCH=else`。
既定の中で他の変数を引く口(L247 の $ASW_PHASE・L249 の $ASW_FINAL_ESCALATION_ONLY)は其の変数を 0 に据ゑて走らせる(補・宣)。
側= 値 1 の枝を 1側・値 0 の枝を 0側 とし、毒がどちらへ倒れたかを書く。★器の報せ行と外の声行は二欄★。repo へ 0 字・稼働 process 不觸。"""
import os, sys, re, time, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_run import run, mark; M = '/Users/momizimac/multi-agent-shogun'; H = D + '/raw/30_h'
VALUES = ['0', '1', '2', '01', '+1', '', ' ', '\n1', None]
r20 = [l.split('\t') for l in open(D + '/raw/20_bunrui.tsv', encoding='utf-8').read().split('\n')[1:] if l]
r10 = [l.split('\t') for l in open(D + '/raw/10_kuchi.tsv', encoding='utf-8').read().split('\n')[1:] if l]
readers = [r for r in r20 if r[3] in ('甲', '乙', '丙')]
def pure_port(f, N):
    for r in r10:
        if r[0] == f and r[2] == N and r[3].startswith('A') and re.match(r'^' + re.escape(N) + r'="?\$\{' + re.escape(N) + r'[^}]*\}"?$', r[6]): return r[6]
    return None
def test_expr(N, s):
    for m in re.finditer(r'\[\[\s.*?\s\]\]|\[\s.*?\s\]', s):
        if re.search(r'\$\{?' + re.escape(N) + r'(?![A-Za-z0-9_])', m.group(0)): return m.group(0)
    return None
rows = []; harn = []; utsusenu = []
for idx, r in enumerate(readers, 1):
    f, ln, N, cls, _, verb = r[0], int(r[1]), r[2], r[3], r[4], r[5]; kind = 'py' if f.endswith('.py') else 'sh'
    port = pure_port(f, N); preset = []
    hp = H + f'/{idx:02d}_{N}_L{ln}.' + kind
    if kind == 'sh':
        te = test_expr(N, verb)
        if not te: utsusenu.append((f, ln, N, verb)); continue
        head = ['#!/bin/bash', f'# 写し器 {idx} ―― {f}:{ln} 旗 {N} 類 {cls} / 口= ' + (port or '(口は比較器の中・純粋な口無し)'), '']
        if port:
            for v in sorted(set(re.findall(r'\$\{?([A-Z][A-Z0-9_]+)', port)) - {N}): head.append(f'{v}=0  # 補: 既定の中で引く他の変数を 0 に据ゑる(宣)'); preset.append((v, '0'))
            head.append(port)
        head.append(f'if {te}; then printf \'BRANCH=then\\n\'; else printf \'BRANCH=else\\n\'; fi')
        K.kaku(hp, '\n'.join(head))
    else:
        m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$', verb)
        if not m: utsusenu.append((f, ln, N, verb)); continue
        K.kaku(hp, f'# 写し器 {idx} ―― {f}:{ln} 旗 {N} 類 {cls}\nimport os\n{verb}\nprint("BRANCH=" + ("then" if {m.group(1)} else "else"))')
    harn.append((idx, f, ln, N, cls, verb, hp, preset))
    res = {v: run(hp, kind, N, v, D, preset) for v in VALUES}
    B1, B0 = res['1']['branch'], res['0']['branch']
    for v in VALUES:
        x = res[v]; side = '1側' if x['branch'] == B1 and B1 != '無' else ('0側' if x['branch'] == B0 and B0 != '無' else '無/他')
        rows.append((idx, f, ln, N, cls, mark(v), x['rc'], x['branch'], side, x['utsuwa'], x['soto'], x['head'], verb))
K.kaku_tsv(D + '/raw/30_doku.tsv', rows, header=('idx', 'file', 'line', 'flag', 'class', 'value', 'rc', 'branch', 'side', 'utsuwa_lines', 'soto_lines', 'stderr_head', 'verbatim'))
POI = ['2', '01', '+1', '(空文字)', '␠', '␊1']
def tally(sub):
    c = collections.Counter()
    for r in sub:
        if r[5] not in POI: continue
        quiet = (r[9] == 0 and r[10] == 0)
        c[('黙つて' if quiet else '鳴つて') + ' ' + r[8]] += 1
    return c
out = [f'# 30 ㋒ 毒表 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 讀手 {len(readers)}(甲 {sum(1 for r in readers if r[3] == "甲")} 乙 {sum(1 for r in readers if r[3] == "乙")} 丙 {sum(1 for r in readers if r[3] == "丙")})/ 写せた {len(harn)} / 写せぬ {len(utsusenu)} / 値 {len(VALUES)}(8 + 補 未設定)/ 走 {len(rows)} / 写し器= raw/30_h/ / bash= /bin/bash',
       '則: 毒 6 値(2・01・+1・空文字・空白・␊1)。「黙つて」= 器の報せ 0 行 ∧ 外の声 0 行。側= 値1 の枝= 1側・値0 の枝= 0側。宣の値(0・1)と補(未設定)は集計の外(表には載す)。']
for cls in ('甲', '乙', '丙'):
    sub = [r for r in rows if r[4] == cls]; c = tally(sub); n = len({r[0] for r in sub})
    out.append(f'★{cls} 讀手 {n} 本 × 毒 6 値 = {n * 6} 走: ' + (' / '.join(f'{k} {v}' for k, v in sorted(c.items())) or '(0 本)') + '★')
out.append('## 讀手ごと(idx file:行 旗 類 | 値1→枝 値0→枝 | 毒 6 値の倒れ先(値=枝/報せ/声) | 未設定→枝)')
for (idx, f, ln, N, cls, verb, hp, preset) in harn:
    sub = {r[5]: r for r in rows if r[0] == idx}
    out.append(f'  {idx:02d} {f}:{ln}\t{N}\t{cls}\t1→{sub["1"][7]} 0→{sub["0"][7]}\t' + ' '.join(f'{v}={sub[v][8]}/{sub[v][9]}/{sub[v][10]}' for v in POI) + f'\t未設定→{sub["(未設定)"][7]} rc{sub["(未設定)"][6]}\t| {verb[:90]}')
out.append('## 写せぬ讀手(写し器を建てられなんだ・宣)'); out += [f'  {f}:{ln} {N} | {v[:120]}' for f, ln, N, v in utsusenu] or ['  0']
out.append('## 外の声の頭(鳴つた走のみ)'); out += [f'  {r[0]:02d} {r[3]} 値 {r[5]} rc{r[6]} 枝 {r[7]} 声 {r[10]} 報せ {r[9]} | {r[11]}' for r in rows if r[10] or r[9]] or ['  (鳴つた走 0)']
K.kaku(D + '/raw/30_tally.txt', '\n'.join(out)); print('\n'.join(out))
