#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_hakari.py ―― km-100 ㋐〜㋕ を ★読取のみ★ で測る器。
枝を一本も触らぬ: 呼ぶ git は cat-file / merge-base / rev-list / diff --name-only / ls-tree / show / rev-parse のみ。
用法: python3 -B driver/10_hakari.py <REPO> <割当tsv(sha40 TAB branch)> <60tips tsv> <MAIN sha> <raw出力dir>
"""
import sys, subprocess, datetime, os, collections, itertools
REPO, WARI, TIPS, MAIN, OUT = sys.argv[1:6]
def git(*a):
    # ★名一覧は -z(NUL 区切り)で受け split('\0') ―― str.splitlines() は U+2028 等も行末と見做し名を割る(家老mac 檢分 2026-09-17 15:37)★
    p = subprocess.run(['git', '-c', 'core.quotePath=false', '-C', REPO, *a], capture_output=True, text=True)  # 非ASCII path を引用符で括らせぬ
    return p.returncode, p.stdout, p.stderr
def w(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f: f.write(text)
NOW = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
log = [f'刻={NOW}', f'MAIN={MAIN}']
# 入力
wari = [l.split('\t') for l in open(WARI, encoding='utf-8').read().split('\n') if l and not l.startswith('#')]
tips = [l.split('\t') for l in open(TIPS, encoding='utf-8').read().split('\n')[1:] if l]
assert all(len(x)==2 for x in wari) and all(len(x)==2 for x in tips)
log.append(f'割当 母數={len(wari)} / 60tips 母數={len(tips)}')
name_of = {s: n for s, n in tips}
# 割当が 60 の中に在るか(逐語一致)
miss = [(s,n) for s,n in wari if (s,n) not in set(map(tuple,tips))]
log.append(f'割当の内 60tips に無い物={len(miss)} {miss}')
# ㋐ 手許に在るか
rows_a = ['branch\tsha40\tcat_file_e_rc']
ok = {}
for s, n in wari:
    rc, _, _ = git('cat-file', '-e', s + '^{commit}')
    ok[s] = rc; rows_a.append(f'{n}\t{s}\t{rc}')
w('10_a_tenmoto.tsv', '\n'.join(rows_a) + '\n')
log.append(f'㋐ rc=0 の枝={sum(1 for v in ok.values() if v==0)}/{len(wari)}')
# 60 tip 同士の祖先関係(A が B の真の祖先: sha 異なり is-ancestor rc=0)
anc = collections.defaultdict(list)   # X -> [B ...] B は X の真の祖先
rows_anc = ['B_branch\tB_sha12\tX_branch\tX_sha12\tis_ancestor_rc\tsame_sha']
for (sb, nb), (sx, nx) in itertools.permutations(tips, 2):
    if nb == nx: continue
    same = (sb == sx)
    rc, _, _ = git('merge-base', '--is-ancestor', sb, sx)
    if rc == 0:
        rows_anc.append(f'{nb}\t{sb[:12]}\t{nx}\t{sx[:12]}\t{rc}\t{int(same)}')
        if not same: anc[sx].append((sb, nb))
w('20_anc_pairs_60x59.tsv', '\n'.join(rows_anc) + '\n')
log.append(f'60×59 is-ancestor 呼出={len(tips)*(len(tips)-1)} / rc=0 の対={len(rows_anc)-1}')
# ㋑㋒ 一本づつ
hdr = ['branch','sha40','main_is_ancestor_rc','merge_base_main12','d1_3dot_files','d1_2dot_files','commits_main_dot_dot_X',
       'anc_tips_n','B_min_branch','B_min_sha12','B_min_revlist_count','B_min_ties','d2_own_files','own_commits',
       'areas_d1','areas_d2','d2_outside_docs_evidence','d2_evidence_dirs','d2_kiki_files']
rows = ['\t'.join(hdr)]
detail = {}
for s, n in wari:
    rc_m, _, _ = git('merge-base', '--is-ancestor', MAIN, s)
    _, mb, _ = git('merge-base', MAIN, s); mb = mb.strip()
    _, d3, _ = git('diff', '--name-only', '-z', f'{MAIN}...{s}'); d3 = [x for x in d3.split('\0') if x]
    _, d2, _ = git('diff', '--name-only', '-z', f'{MAIN}..{s}');  d2 = [x for x in d2.split('\0') if x]
    _, cnt, _ = git('rev-list', '--count', f'{MAIN}..{s}'); cnt = cnt.strip()
    w(f'30_d1_3dot_{n.replace("/","__")}.txt', '\n'.join(d3) + ('\n' if d3 else ''))
    cands = anc.get(s, [])
    bmin = None; ties = []; own = None; own_files = []; own_cnt = ''
    if cands:
        scored = []
        for sb, nb in cands:
            _, c, _ = git('rev-list', '--count', f'{sb}..{s}'); scored.append((int(c.strip()), sb, nb))
        scored.sort()
        bmin = scored[0]; ties = [x for x in scored if x[0] == bmin[0]]
        _, df, _ = git('diff', '--name-only', '-z', f'{bmin[1]}..{s}'); own_files = [x for x in df.split('\0') if x]
        own_cnt = str(bmin[0])
        w(f'31_d2_own_{n.replace("/","__")}.txt', '\n'.join(own_files) + ('\n' if own_files else ''))
        w(f'32_anc_cands_{n.replace("/","__")}.tsv', 'revlist_count\tB_sha12\tB_branch\n' + ''.join(f'{c}\t{sb[:12]}\t{nb}\n' for c, sb, nb in scored))
    areas1 = sorted({(p.split('/')[0] if '/' in p else p) for p in d3})
    areas2 = sorted({(p.split('/')[0] if '/' in p else p) for p in own_files})
    outside = [p for p in own_files if not p.startswith('docs/evidence/')]
    evdirs = sorted({p.split('/')[2] for p in own_files if p.startswith('docs/evidence/') and p.count('/') >= 2})
    detail[s] = dict(name=n, d3=d3, own=own_files, outside=outside, evdirs=evdirs, bmin=bmin, ties=ties, cands=cands)
    rows.append('\t'.join([n, s, str(rc_m), mb[:12], str(len(d3)), str(len(d2)), cnt,
        str(len(cands)), bmin[2] if bmin else '測れぬ', bmin[1][:12] if bmin else '-', own_cnt or '-',
        str(len(ties)) if bmin else '-', str(len(own_files)) if bmin else '測れぬ', own_cnt or '-',
        ','.join(areas1), ','.join(areas2) if bmin else '-', str(len(outside)) if bmin else '-', ','.join(evdirs), ';'.join(outside)]))
w('40_hakari.tsv', '\n'.join(rows) + '\n')
# ㋕ 割当群の中の祖先対
rows_k = ['B_branch(祖先)\tX_branch(子孫)\tB_sha12\tX_sha12']
wset = {s for s, _ in wari}
for sx, lst in anc.items():
    if sx not in wset: continue
    for sb, nb in lst:
        if sb in wset: rows_k.append(f'{nb}\t{name_of[sx]}\t{sb[:12]}\t{sx[:12]}')
w('50_warimochi_nai_anc.tsv', '\n'.join(rows_k) + '\n')
log.append(f'㋕ 割当18 の中で tip が他 tip の真の祖先に成る対={len(rows_k)-1}')
# 割当 tip が 60 の他 tip の祖先に成つて居るか(=不要側に落ちるか)
rows_r = ['X_branch(割当)\t子孫tip_n\t子孫tips']
desc = collections.defaultdict(list)
for sx, lst in anc.items():
    for sb, nb in lst: desc[sb].append(name_of[sx])
for s, n in wari: rows_r.append(f'{n}\t{len(desc.get(s,[]))}\t{",".join(sorted(desc.get(s,[])))}')
w('51_warimochi_ga_sosen_ka.tsv', '\n'.join(rows_r) + '\n')
log.append(f'割当18 の内 他 tip の祖先に成つて居る枝={sum(1 for s,_ in wari if desc.get(s))}')
# ㋔ 衝突: 割当群 同士で own diff の file 交差(docs/evidence 以外 と 以内 を分ける)
rows_c = ['A_branch\tB_branch\t共有file_n\t共有file(docs/evidence外)\t共有file(docs/evidence内)']
for (sa, na), (sb2, nb2) in itertools.combinations(wari, 2):
    fa = set(detail[sa]['own']); fb = set(detail[sb2]['own'])
    inter = sorted(fa & fb)
    if inter:
        o = [p for p in inter if not p.startswith('docs/evidence/')]; i = [p for p in inter if p.startswith('docs/evidence/')]
        rows_c.append(f'{na}\t{nb2}\t{len(inter)}\t{";".join(o)}\t{";".join(i)}')
w('60_shoutotsu_own_pairs.tsv', '\n'.join(rows_c) + '\n')
log.append(f'㋔ own diff の file が交差する割当対={len(rows_c)-1}')
# 受入条件の材料: tip の樹に README/MANIFEST/門控 が在るか(ls-tree・checkout せず)
rows_j = ['branch\tevidence_dir\tREADME\tMANIFEST\tMANIFEST_1行目\tpath=相対か\t門控file_n\t門控rc']
for s, n in wari:
    for d in detail[s]['evdirs']:
        base = f'docs/evidence/{d}'
        _, lt, _ = git('ls-tree', '-r', '-z', '--name-only', s, '--', base); files = [x for x in lt.split('\0') if x]
        has_r = int(f'{base}/README.md' in files); has_m = int(f'{base}/MANIFEST.txt' in files)
        first = ''; rel = '-'
        if has_m:
            _, mtxt, _ = git('show', f'{s}:{base}/MANIFEST.txt')
            lines = [l for l in mtxt.split('\n') if l.startswith('path=')]
            first = lines[0][:90] if lines else '(path= 行無)'
            rel = 'no_path_rows' if not lines else ('絶対/束外' if any(l.split()[0][5:].startswith(('docs/','/')) for l in lines) else '束内相対')
        gates = [f for f in files if ('_gate/' in f or 'gate_dasumae' in f or 'hashiri' in f)]
        rcs = []
        for f in gates:
            if f.endswith('.rc'):
                _, v, _ = git('show', f'{s}:{f}'); rcs.append(f'{os.path.basename(f)}={v.strip()}')
        rows_j.append(f'{n}\t{d}\t{has_r}\t{has_m}\t{first}\t{rel}\t{len(gates)}\t{";".join(rcs)}')
w('70_ukeire_zairyou.tsv', '\n'.join(rows_j) + '\n')
w('90_log.txt', '\n'.join(log) + '\n')
print('\n'.join(log))
