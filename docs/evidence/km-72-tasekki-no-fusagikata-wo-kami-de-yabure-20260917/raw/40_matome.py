# -*- coding: utf-8 -*-
"""40 纏め(第72弾)―― 20 の行列(TSV)から、㋑(単 vs 合)・㋒(71 の六形)・㋓(rc/裁/注入行/欺き)・新たな穴 を表に引く。手写し 0(数は悉く TSV から)。"""
import sys, csv, time, collections
D = sys.argv[1]; RAW = D + '/raw'; sys.path.insert(0, RAW); import kaki as K
rows = list(csv.DictReader(open(RAW + '/20_matrix.tsv', encoding='utf-8'), delimiter='\t'))
for r in rows:
    for k in ('rc', 'n_lines', 'ku_n', 'gi_rc_ne0_and_ku', 'after_ku_lines', 'odd_lines_n'): r[k] = int(r[k])
import re
def unesc(t):
    o = []; i = 0
    while i < len(t):
        c = t[i]
        if c == '\\' and i + 1 < len(t): d = t[i + 1]; o.append({'n': '\n', 't': '\t', 'r': '\r', '\\': '\\'}.get(d, '\\' + d)); i += 2
        else: o.append(c); i += 1
    return ''.join(o)
esc = lambda s: s.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
# ★20 の eff/odd 欄は切り出しが甘かつた(eff が札の行から拾はれ・★閾 の行頭が odd に数へられた・.first)。此處で門票から引き直す(20 の欄は疵として残す)★
base2 = {}
for r in rows:
    t = unesc(r['stderr_esc']); ls = t.split('\n'); ls = ls[:-1] if ls and ls[-1] == '' else ls
    if r['vid'] == 'u00': base2[(r['gate'], r['var'])] = {l[:2] for l in ls} | {'閾 ', '★閾', '★條', '條⑤', '  '}
for r in rows:
    t = unesc(r['stderr_esc']); ls = t.split('\n'); ls = ls[:-1] if ls and ls[-1] == '' else ls
    if r['gate'] == 'dasumae': m = re.search(r'byte和 \d+\(閾 (.*?)(?:未満\)|・裁)', t, re.S)
    elif r['thr'] == 'GATE4_MAX_FILE_MB': m = re.search(r'(?:単 file 上限 (.*?) MB 以下|MB\(上限 (.*?)\)――)', t, re.S)
    else: m = re.search(r'総和 (?:が )?\d+ MB\(上限 (.*?)\)', t, re.S)
    r['eff_esc'] = esc(next((g for g in (m.groups() if m else ()) if g is not None), '')) if m else '(條⑤の行 無)'
    odd = [l for l in ls if l[:2] not in base2[(r['gate'], r['var'])]]; r['odd_lines_n'] = len(odd); r['odd_esc'] = esc('|'.join(odd))
    # ★20 の sai 欄は「最初の閾の行」を見て居た(受けた時に隣の閾の既定札を拾ふ・.second)。的の閾名を含む札だけで引き直す★
    # ★裁は行でなく門票全文で引く(.third まで: 行で引いた故、値の改行や丙の cut で割れた札を 受 と誤読した)★
    st = [i for i, l in enumerate(ls) if f"閾 {r['thr']}" in l]; fuda = ls[st[0]] if st else ''; r['fuda_esc'] = esc(fuda)
    if not st: r['sai'] = '受' if r['vid'] != 'u00' else '-'
    elif '未設定' in fuda: r['sai'] = '既定(未設定)'
    elif '既定' in fuda: r['sai'] = '倒'
    else:
        k = next((j for j in range(st[0] + 1, len(ls)) if '既定' in ls[j]), None)
        r['sai'] = f'倒(札割れ★+{k - st[0]}行)' if k is not None else '倒(札割れ★既定無)'
idx = {(r['gate'], r['var'], r['thr'], r['vid']): r for r in rows}
VIDS = [r['vid'] for r in rows if r['gate'] == 'dasumae' and r['var'] == 'nama' and r['thr'] == 'DASUMAE_READ_TIMEOUT']; LAB = {r['vid']: r['label'] for r in rows}
out = [f'# 40 纏め / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 行 {len(rows)}']
cell = lambda r: f"{r['rc']}/{r['sai'][:1]}" if r else '-'
for gate, thr, vs in (('dasumae', 'DASUMAE_READ_TIMEOUT', ['nama', 'kou', 'otsu', 'hei', 'gou', 'gou_x', 'gou_y']), ('dasumae', 'DASUMAE_MAX_BYTES', ['nama', 'kou', 'otsu', 'hei', 'gou']), ('gate4', 'GATE4_MAX_FILE_MB', ['nama', 'kou', 'hei', 'gou']), ('gate4', 'GATE4_MAX_TOTAL_MB', ['nama', 'kou', 'hei', 'gou'])):
    out.append(f'\n## {gate} / {thr} ―― rc/裁(既=既定(未設定)・倒・受) / test_ge0 / 行数 / eff(條⑤の閾字面) / gi / after_ku / odd'); out.append('vid\tlabel\tge0\t' + '\t'.join(vs) + '\tn_lines(nama..)\teff(nama|gou)\tgi(nama|gou)\tafter_ku(nama|gou)\todd(nama|gou)')
    for v in VIDS:
        rs = [idx.get((gate, x, thr, v)) for x in vs]; n = idx[(gate, 'nama', thr, v)]; g = idx[(gate, 'gou', thr, v)]
        out.append(f"{v}\t{LAB[v]}\t{n['test_ge0_rc']}\t" + '\t'.join(cell(r) for r in rs) + f"\t{'/'.join(str(r['n_lines']) for r in rs)}\t{n['eff_esc']}|{g['eff_esc']}\t{n['gi_rc_ne0_and_ku']}|{g['gi_rc_ne0_and_ku']}\t{n['after_ku_lines']}|{g['after_ku_lines']}\t{n['odd_lines_n']}|{g['odd_lines_n']}")
# ㋑ 単 vs 合
out.append('\n## ㋑ 単 vs 合 ―― (rc,裁) が 合 と 単(甲/乙/丙) で違ふ組(dasumae は甲乙丙・gate4 は甲丙)')
for gate, thr in (('dasumae', 'DASUMAE_READ_TIMEOUT'), ('dasumae', 'DASUMAE_MAX_BYTES'), ('gate4', 'GATE4_MAX_FILE_MB'), ('gate4', 'GATE4_MAX_TOTAL_MB')):
    singles = ['kou', 'otsu', 'hei'] if gate == 'dasumae' else ['kou', 'hei']; cnt = collections.Counter()
    for v in VIDS:
        g = idx[(gate, 'gou', thr, v)]; gk = (g['rc'], g['sai']); ss = {s: (idx[(gate, s, thr, v)]['rc'], idx[(gate, s, thr, v)]['sai']) for s in singles}
        agree = [s for s in ss if ss[s] == gk]; cnt[len(agree)] += 1
        if len(agree) < len(singles): out.append(f"  {thr} {v} {LAB[v]}: 合 {gk} ⇔ " + ' '.join(f"{s}{ss[s]}" for s in singles) + f" → 合に一致する単 {agree or '無'}" + (f" / 合の札「{g['fuda_esc'][:70]}」" if g['fuda_esc'] else ''))
    out.append(f"  {thr}: 値 {len(VIDS)} の内 全単と一致 {cnt[len(singles)]} / 一部一致 {sum(c for k, c in cnt.items() if 0 < k < len(singles))} / 無一致 {cnt[0]}")
# 合x / 合y
out.append('\n## 合x(呼び口の床天 5..60)/ 合y(chk を無い名 tmo_okk) ⇔ 合 ―― TIMEOUT で (rc,裁,札) が違ふ組')
for x in ('gou_x', 'gou_y'):
    for v in VIDS:
        a = idx[('dasumae', 'gou', 'DASUMAE_READ_TIMEOUT', v)]; b = idx[('dasumae', x, 'DASUMAE_READ_TIMEOUT', v)]
        if (a['rc'], a['sai'], a['fuda_esc']) != (b['rc'], b['sai'], b['fuda_esc']): out.append(f"  {x} {v} {LAB[v]}: 合 {a['rc']}/{a['sai']}「{a['fuda_esc'][:60]}」 ⇔ {x} {b['rc']}/{b['sai']}「{b['fuda_esc'][:80]}」 odd {b['odd_lines_n']}「{b['odd_esc'][:80]}」")
out.append('\n## 合x ―― 呼び口の床天を 5..60 に替へた合: 受かつた値と、拒んだ札の「許」')
for v in VIDS:
    b = idx[('dasumae', 'gou_x', 'DASUMAE_READ_TIMEOUT', v)]
    if b['sai'] == '受' and b['test_ge0_rc'] in ('0', '1'): out.append(f"  gou_x {v} {LAB[v]}: 受(札 無)rc {b['rc']}")
kyo = sorted({re.search(r'許 ([^)]*)\)', unesc(r['fuda_esc'])).group(1) for r in rows if r['var'] == 'gou_x' and '許' in r['fuda_esc']}); out.append(f'  gou_x の拒んだ札が刷る「許」= {kyo} / tmo_ok が課す床天 = 1..86400(hard-code・呼び口の $2 $3 を讀まぬ)')
out.append('\n## 札二行(丙の cut が改行を足す)―― 形ごとの数')
c = collections.Counter((r['var'], r['gate'], r['sai']) for r in rows if r['sai'].startswith('倒(札割れ')); out.append('  ' + (' / '.join(f'{k} {n}' for k, n in sorted(c.items())) or '0') + ' / 値: ' + ', '.join(sorted({r['label'] + '(' + r['var'] + ')' for r in rows if r['sai'].startswith('倒(札割れ')})))
# 受けた非整数(test_ge0=2 なのに 受)
out.append('\n## 受けた讀めぬ値 ―― [ -ge 0 ] rc=2 なのに 裁=受(番人が數でない物を通した)')
for r in rows:
    if r['test_ge0_rc'] == '2' and r['sai'] == '受': out.append(f"  {r['gate']} {r['var']} {r['thr']} {r['vid']} {r['label']}: rc {r['rc']} / eff「{r['eff_esc']}」/ 行数 {r['n_lines']} / odd {r['odd_lines_n']}「{r['odd_esc'][:100]}」")
# 受けた値が條⑤に生の儘刷られ 行を増やした(受ける路の注入)
out.append('\n## 受ける路の注入 ―― 裁=受 で 條⑤の閾字面(eff)に 改行/空白 が残る(丙が守らぬ路)')
for r in rows:
    if r['sai'] == '受' and (('\\n' in r['eff_esc']) or ('\\t' in r['eff_esc']) or r['eff_esc'] != r['eff_esc'].strip() or ' ' in r['eff_esc']): out.append(f"  {r['gate']} {r['var']} {r['thr']} {r['vid']} {r['label']}: rc {r['rc']} eff「{r['eff_esc']}」 行数 {r['n_lines']} odd {r['odd_lines_n']}「{r['odd_esc'][:60]}」")
# 札の語 ―― 甲/合 の「扱へぬ か 範囲外」が 讀めぬ(rc2)と 範囲外(rc0/1)を分けぬ
out.append('\n## 札の語 ―― 「扱へぬ か 範囲外」を刷つた走を test_ge0 で割る(讀めぬ=2 / 負=1 / 非負=0)')
c = collections.Counter((r['var'], r['test_ge0_rc']) for r in rows if '範囲外' in r['fuda_esc']); out.append('  ' + ' / '.join(f'{k[0]} ge0={k[1]}: {n}' for k, n in sorted(c.items())))
# 欺き(專任3 定義)と 結語の後の行
out.append('\n## 欺き(rc≠0 なのに通句)/ 通句の行数≠1 / 結語の後に行 ―― 形ごとに数へる')
c1 = collections.Counter((r['var'], r['gate']) for r in rows if r['gi_rc_ne0_and_ku']); c2 = collections.Counter((r['var'], r['gate']) for r in rows if r['ku_n'] != 1); c3 = collections.Counter((r['var'], r['gate']) for r in rows if r['after_ku_lines'] > 0)
out.append('  gi: ' + (' / '.join(f'{k} {n}' for k, n in sorted(c1.items())) or '0')); out.append('  ku_n≠1: ' + (' / '.join(f'{k} {n}' for k, n in sorted(c2.items())) or '0')); out.append('  after_ku>0: ' + (' / '.join(f'{k} {n}' for k, n in sorted(c3.items())) or '0'))
for r in rows:
    if r['gi_rc_ne0_and_ku'] or r['ku_n'] != 1 or r['after_ku_lines'] > 0: out.append(f"  {r['gate']} {r['var']} {r['thr']} {r['vid']} {r['label']}: rc {r['rc']} ku_n {r['ku_n']} after {r['after_ku_lines']} gi {r['gi_rc_ne0_and_ku']}")
K.kaku(RAW + '/40_matome.txt', '\n'.join(out)); print('\n'.join(out))
