# -*- coding: utf-8 -*-
"""30 ㋒ origin 側 21 本(第82弾 km-95)―― local に無い理由を ★測れる物だけ★ 測る: ①object が手元に在るか(cat-file -e) ②手元の何の ref から届くか(for-each-ref --contains) ③local main の非merge と patch-id 一致か(= 中身は届いて居るか) ④committer(GitHub の web merge は committer が noreply@github.com) ⑤merge の第二親が手元の何の ref か。加へて ★reflog show(読取)★ で refs/remotes/origin/main と refs/heads/main の動いた刻を列べる(fetch は走らせぬ・過去の fetch の痕を読む)。測れぬ物は測れぬと書く。"""
import sys, time, csv
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git
L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'
rd = lambda n: list(csv.DictReader(open(D + f'/raw/10_{n}.tsv', encoding='utf-8'), delimiter='\t'))
loc, ori = rd('local'), rd('origin'); lpid = {r['patch_id_stable']: r['sha'] for r in loc if r['kind'] == 'single'}
out = [f'# 30 ㋒ origin 側 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 母數= origin 側 rev-list {len(ori)} 本(merge {sum(1 for r in ori if r["kind"] == "merge")}・非merge {sum(1 for r in ori if r["kind"] == "single")})/ 突合せ先= local 側 非merge {len(lpid)} 本']
out.append('| # | full sha | 種 | object 手元 | 届く手元の ref | patch-id 一致(local) | committer | 第二親→手元 ref | 測れた事 / 測れぬ事 |'); out.append('|---|---|---|---|---|---|---|---|---|')
rows = []; n_only_remote = 0; n_in_heads = 0
for i, r in enumerate(ori, 1):
    s = r['sha']; _, _, rce = git('cat-file', '-e', s + '^{commit}'); has = '在' if rce == 0 else '★無★'
    fr, _, _ = git('for-each-ref', '--contains', s, '--format=%(refname)'); refs = [x for x in fr.split('\n') if x]
    heads = [x for x in refs if x.startswith('refs/heads/')]; rem = [x for x in refs if x.startswith('refs/remotes/')]
    if heads: n_in_heads += 1
    elif rem: n_only_remote += 1
    pm = lpid.get(r['patch_id_stable']) if r['kind'] == 'single' else None
    pmtxt = f'一致 local {pm[:12]}' if pm else ('不一致(中身も届いて居らぬ)' if r['kind'] == 'single' else 'merge(対象外)')
    p2 = ''
    if r['kind'] == 'merge':
        ps, _, _ = git('log', '-1', '--format=%P', s); p2sha = ps.split()[1] if len(ps.split()) > 1 else ''
        f2, _, _ = git('for-each-ref', '--contains', p2sha, '--format=%(refname)') if p2sha else ('', '', 0)
        f2h = [x for x in f2.split('\n') if x.startswith('refs/heads/')]
        p2 = f'{p2sha[:12]} → ' + (f'heads {len(f2h)} 本 {f2h[:2]}' if f2h else '手元の heads に無し')
    comm = f'{r["committer"]} <{r["committer_email"]}>'
    hakari = []
    hakari.append('local main から届かぬ(rev-list L..O の定義)')
    if has == '在': hakari.append('object は手元に在る= 過去に fetch 済(refs/remotes/origin/main 経由・reflog 参照)')
    else: hakari.append('object 無し= 測れぬ(fetch せぬ)')
    if heads: hakari.append(f'手元の枝 {len(heads)} 本が含む {heads[:2]}')
    if pm: hakari.append('中身は local main に別 sha で在る(sha だけが違ふ)')
    if 'noreply@github.com' in r['committer_email']: hakari.append('committer= GitHub(web/PR merge)')
    hakari.append('★測れぬ★: 誰が・何処の PC から押したか／local main へ取り込まぬ判断の有無(clone からは読めぬ)')
    rows.append((s, r['kind'], has, ';'.join(refs), pmtxt, comm, p2, ' / '.join(hakari), r['subject']))
    out.append(f'| {i} | {s} | {r["kind"]} | {has} | {";".join(x.replace("refs/", "") for x in refs)[:60]} | {pmtxt} | {comm[:40]} | {p2[:60]} | {" / ".join(hakari)[:150].replace("|", "¦")} |')
out.append(f'\n集計(母數 {len(ori)}): 手元の refs/heads/* から届く {n_in_heads} / refs/remotes/* からのみ届く {n_only_remote} / patch-id が local と一致(非merge) {sum(1 for r in rows if r[4].startswith("一致"))} / 不一致(非merge) {sum(1 for r in rows if r[4].startswith("不一致"))} / merge {sum(1 for r in rows if r[1] == "merge")}')
out.append('\n## reflog show(読取・fetch の痕)')
for ref in ('refs/remotes/origin/main', 'refs/heads/main'):
    rl, _, rc = git('reflog', 'show', '--date=iso', '--format=%h %gd %gs', ref); ls = [x for x in rl.split('\n') if x]
    out.append(f'{ref} (rc {rc}・{len(ls)} 行・新しい方が上・頭 12 行):'); out += ['  ' + x[:150] for x in ls[:12]]
    K.kaku(D + f'/raw/30_reflog_{ref.split("/")[-2]}_{ref.split("/")[-1]}.txt', f'# reflog show --date=iso {ref} / rc {rc} / {len(ls)} 行\n' + '\n'.join(ls))
K.kaku_tsv(D + '/raw/30_origin_side.tsv', rows, ['sha', 'kind', 'object', 'refs_containing', 'patchid_match_local', 'committer', 'second_parent', 'hakari', 'subject'])
K.kaku(D + '/raw/30_origin_side.txt', '\n'.join(out)); print('\n'.join(out))
