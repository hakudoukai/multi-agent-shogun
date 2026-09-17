# -*- coding: utf-8 -*-
"""10 ㋐ 分岐点(第82弾 km-95)―― merge-base を出し、両側の commit を full sha・subject・author 日で悉く列べる。★母數を三つ宣してから数を書く★: (a) rev-list の commit 数 (b) 非merge の commit 数(=cherry の母數) (c) patch-id を一意化した数、と cherry の +/−。patch-id は --stable と --unstable の両方で取り、食ひ違ふかを刷る。ls-remote --heads の全枝も snapshot して refs/remotes/origin/* との差を書く。"""
import sys, time, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git, patch_id, meta
L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); out = [f'# 10 ㋐ 分岐点 / 刻 {koku} / local main {L} / origin main {O}(ls-remote と一致= 00)']
mb, _, _ = git('merge-base', '--all', L, O); mbs = mb.split(); out.append(f'merge-base --all = {mbs}(本数 {len(mbs)})')
for b in mbs: m = meta(b); out.append(f'  分岐点 {m["sha"]} / {m["ad"]} / {m["an"]} / {m["subj"][:90]}')
side = {}
for name, rng in (('local', f'{O}..{L}'), ('origin', f'{L}..{O}')):
    shas, _, _ = git('rev-list', '--topo-order', rng); shas = shas.split(); rows = []
    for s in shas:
        m = meta(s); ismerge = len(m['parents']) > 1
        pid_s = None if ismerge else patch_id(s, True); pid_u = None if ismerge else patch_id(s, False)
        rows.append(dict(m, merge=ismerge, pid_s=pid_s, pid_u=pid_u))
    side[name] = rows
# cherry
ch = {}
for name, up, hd in (('local', O, L), ('origin', L, O)):
    o, _, _ = git('cherry', up, hd); ch[name] = {l.split()[1]: l[0] for l in o.strip().split('\n') if l}
out.append('')
out.append('## 母數の宣(三つ)と数')
for name in ('local', 'origin'):
    rows = side[name]; nm = [r for r in rows if not r['merge']]; pids = [r['pid_s'] for r in nm]; other = {r['pid_s'] for r in side['origin' if name == 'local' else 'local'] if not r['merge']}
    uniq = set(pids); notin = {p for p in uniq if p not in other}
    diffsu = sum(1 for r in nm if r['pid_s'] != r['pid_u'])
    plus = sum(1 for v in ch[name].values() if v == '+'); minus = sum(1 for v in ch[name].values() if v == '-')
    out.append(f'{name} 側(= {"O..L" if name == "local" else "L..O"}): (a) rev-list commit 数 {len(rows)}(内 merge {len(rows) - len(nm)}) / (b) 非merge= cherry の母數 {len(nm)} / (c) patch-id(--stable) 一意化 {len(uniq)}(重複 {len(pids) - len(uniq)}・空 diff {sum(1 for p in pids if p == "")}) / 相手側に無い patch-id {len(notin)} / cherry + {plus} − {minus}(母數 {len(ch[name])}) / --stable と --unstable が食ひ違ふ commit {diffsu}')
out.append(f'∴ 家老の「14」= local 側 cherry + / 「8」= origin 側 cherry +。commit の数(rev-list)は {len(side["local"])}/{len(side["origin"])}、非merge は {sum(1 for r in side["local"] if not r["merge"])}/{sum(1 for r in side["origin"] if not r["merge"])}。')
out.append('')
for name in ('local', 'origin'):
    out.append(f'## {name} 側 全列({len(side[name])} 本・topo 順・新しい方が上)'); out.append('| # | full sha | merge | cherry | author 日 | author | subject |'); out.append('|---|---|---|---|---|---|---|')
    for i, r in enumerate(side[name], 1):
        out.append(f'| {i} | {r["sha"]} | {"merge(" + str(len(r["parents"])) + "親)" if r["merge"] else "-"} | {ch[name].get(r["sha"], "対象外")} | {r["ad"]} | {r["an"]} | {r["subj"][:80].replace("|", "¦")} |')
    K.kaku_tsv(D + f'/raw/10_{name}.tsv', [(r['sha'], 'merge' if r['merge'] else 'single', ch[name].get(r['sha'], 'na'), r['pid_s'] or '-', r['pid_u'] or '-', r['ad'], r['an'], r['ae'], r['cn'], r['ce'], r['cd'], r['subj']) for r in side[name]], ['sha', 'kind', 'cherry', 'patch_id_stable', 'patch_id_unstable', 'author_date', 'author', 'author_email', 'committer', 'committer_email', 'commit_date', 'subject'])
# ls-remote heads snapshot
lr, _, rc = git('ls-remote', '--heads', 'origin'); heads = [l.split('\t') for l in lr.strip().split('\n') if l]
K.kaku(D + '/raw/10_ls_remote_heads.txt', f'# ls-remote --heads origin / 刻 {koku} / rc {rc} / 本数 {len(heads)}\n' + '\n'.join(f'{a} {b}' for a, b in heads))
lo, _, _ = git('for-each-ref', '--format=%(objectname) %(refname)', 'refs/remotes/origin'); lo = [l for l in lo.strip().split('\n') if l]
km = sum(1 for a, b in heads if b.startswith('refs/heads/karo-mac/')); am = sum(1 for a, b in heads if b.startswith('refs/heads/ashigaru-mac-'))
out.append(''); out.append(f'## origin の枝 snapshot(raw/10_ls_remote_heads.txt): 全 {len(heads)} 本 / karo-mac/ {km} / ashigaru-mac-*/ {am}(家老の宣 239 / 41 / 18) / 手元の refs/remotes/origin/* は ★{len(lo)} 本★のみ {[l.split()[1] for l in lo]} ∴ origin の枝の殆どは手元に ref が無い(object は在り得る)')
K.kaku(D + '/raw/10_bunki.txt', '\n'.join(out)); print('\n'.join(out))
