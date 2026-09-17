#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""70_shiwake.py ―― ㋓ 仕分け(甲/乙/丙)を ★宣した拠り所★ の順に機械で当て、TSV と表 md を生む。
拠り所(先に宣す・上から順に最初に当たる則で決まる):
  R0 ㋐ cat-file rc≠0(物が無い)                         → 丙
  R1 tip が 60 の他 tip の真の祖先(51_warimochi_ga_sosen_ka) → 乙(内容は他枝が抱へる=家老の不要15 と同義)
  R2 own diff の全 file が他 tip に同一 blob で在る(80_naiyou Y_full_n>0) → 乙(内容重複)
  R3 祖先 tip が無く ⑵ 測れぬ                             → 丙(測れぬ)
  R4 其れ以外                                             → 甲(着地候補)。受入条件は 75_tip_mon / 89_merge_tree / 60_shoutotsu から欄に刷る
用法: python3 -B driver/70_shiwake.py raw an
"""
import sys, os, csv
RAW, AN = sys.argv[1:3]
def tsv(p):
    rows = [l.split('\t') for l in open(os.path.join(RAW, p), encoding='utf-8').read().split('\n') if l and not l.startswith('#')]
    return [dict(zip(rows[0], r)) for r in rows[1:]]
hak = tsv('40_hakari.tsv'); ten = {r['branch']: r for r in tsv('10_a_tenmoto.tsv')}
sos = {r['X_branch(割当)']: r for r in tsv('51_warimochi_ga_sosen_ka.tsv')}
nai = {r['X_branch']: r for r in tsv('80_naiyou_kasanari.tsv')}
mt = {r['branch']: r for r in tsv('89_merge_tree.tsv')}
mon = {}
for r in tsv('75_tip_mon.tsv'): mon.setdefault(r['branch'], []).append(r)
sho = tsv('60_shoutotsu_own_pairs.tsv')
out = ['branch\tsha40\td1_3dot_files\td2_own_files\tB_min\town_commits\tcommits_vs_main\tareas_d2\tkiki_files\tshiwake\tR\triyuu\tjou1_rc\tgate_rc\tgate_ochi\tmerge_tree_vs_main\tgroup_kousa\tukeire']
md = ['| # | 枝 | sha12 | ⑴3dot | ⑵own | B_min(†不要15) | own c | 領域 | 甲乙丙 | 則 | 條①/門(tip束) | merge-tree 対main | 受入条件 |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
cnt = {'甲': 0, '乙': 0, '丙': 0}
for i, r in enumerate(hak, 1):
    b = r['branch']
    if ten[b]['cat_file_e_rc'] != '0': s, R, why = '丙', 'R0', '手許に物が無い'
    elif int(sos[b]['子孫tip_n']) > 0: s, R, why = '乙', 'R1', '他 tip の祖先(内容は其方が抱へる)'
    elif int(nai[b]['Y_full_n(全fileを同一blobで抱へるY数)']) > 0: s, R, why = '乙', 'R2', '全 file が他 tip に同一 blob で在る'
    elif r['B_min_branch'] == '測れぬ': s, R, why = '丙', 'R3', '祖先 tip 無し・⑵ 測れぬ'
    else: s, R, why = '甲', 'R4', '独自 commit を持ち他枝に無い(R1/R2 に当たらず)'
    cnt[s] += 1
    ms = mon.get(b, []); j1 = ','.join(m['jou1_rc'] for m in ms) or '束無'; g = ','.join(m['gate_rc'] for m in ms) or '束無'
    ochi = ','.join(('通' if m['gate_rc'] == '0' else '落') for m in ms) or '-'
    kou = [p for p in sho if b in (p['A_branch'], p['B_branch'])]
    uke = []
    if s == '甲':
        if not ms: uke.append('★tip に紙(evidence 束)が無い=器のみ・紙の所在を示せ★')
        else:
            uke.append('條①一致' if all(m['jou1_rc'] == '0' for m in ms) else '★條① 相違を先に解け★')
            uke.append('門通' if all(m['gate_rc'] == '0' for m in ms) else '★門落(fixture の汚れなら宣して argv から除く=第四の道)★')
        uke.append('対main衝突0' if mt[b]['merge_tree_rc'] == '0' else '★対main衝突有★')
        uke.append('群内交差0' if not kou else f'★群内交差{len(kou)}★')
        if r['d2_kiki_files']: uke.append(f'★器差分の監査({r["d2_kiki_files"]})★')
    out.append('\t'.join([b, r['sha40'], r['d1_3dot_files'], r['d2_own_files'], r['B_min_branch'], r['own_commits'], r['commits_main_dot_dot_X'], r['areas_d2'], r['d2_kiki_files'], s, R, why, j1, g, ochi, mt[b]['merge_tree_rc'], str(len(kou)), ' / '.join(uke)]))
    md.append(f'| {i} | `{b}` | `{r["sha40"][:12]}` | {r["d1_3dot_files"]} | {r["d2_own_files"]} | `{r["B_min_branch"].replace("karo-mac/","")}`† | {r["own_commits"]} | {r["areas_d2"]}{(" ★"+r["d2_kiki_files"]+"★") if r["d2_kiki_files"] else ""} | **{s}** | {R} | {j1}/{g}({ochi}) | rc={mt[b]["merge_tree_rc"]} | {" / ".join(uke)} |')
open(os.path.join(AN, '95_shiwake.tsv'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
open(os.path.join(AN, '96_shiwake_hyou.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(f'母數={len(hak)} 甲={cnt["甲"]} 乙={cnt["乙"]} 丙={cnt["丙"]}')
