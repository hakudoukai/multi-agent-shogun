# -*- coding: utf-8 -*-
"""40 ㋓ 不要候補 9 枝の測り直し(第82弾 km-95)―― 名と sha は家老の紙(karo-mac-origin-eda-kenbun-20260917/README.md)から regex で抽く(手写し 0)。各枝に就き: ls-remote の今の sha(10 の snapshot)と紙の sha の一致 / 手元の ref(heads・remotes)の有無 / object の有無 / git cherry <local main> <sha> の +− / git cherry <origin/main> <sha> の +− / tip が local main・origin/main の祖先か(merge-base --is-ancestor)/ tip から分岐点への距離。★基点を変へた時の食ひ違ひが何処から来るか★ を、+ に立つ commit の sha を名指して示す。"""
import sys, time, re
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git
M = '/Users/momizimac/multi-agent-shogun'; L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'; MB = '6e9d40600a801aa713ac238e2e62bbae06c9e683'
kami = open(M + '/docs/evidence/karo-mac-origin-eda-kenbun-20260917/README.md', encoding='utf-8').read()
eda = re.findall(r'^  - (karo-mac/\S+)  ([0-9a-f]{40})$', kami, re.M)
snap = dict(l.split()[::-1] for l in open(D + '/raw/10_ls_remote_heads.txt', encoding='utf-8') if not l.startswith('#') and l.strip())
lpids = set(l.split('\t')[3] for l in open(D + '/raw/10_local.tsv', encoding='utf-8').read().split('\n')[1:] if l)
out = [f'# 40 ㋓ 不要候補 9 枝 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 紙から抽いた枝 {len(eda)} 本(宣 9) / 基点 甲= local main {L[:12]} / 基点 乙= origin main {O[:12]} / 分岐点 {MB[:12]}']
out.append('| 枝 | 紙の sha | ls-remote 今 | 手元 ref | object | cherry 基点=local +/− | cherry 基点=origin +/− | 祖先(local/origin) | + に立つ commit(基点=origin) |'); out.append('|---|---|---|---|---|---|---|---|---|')
rows = []; agree_local0 = 0; origin0 = []
for name, sha in eda:
    now = snap.get('refs/heads/' + name, '(無)'); same = '一致' if now == sha else f'★違ふ {now[:12]}★'
    hr, _, _ = git('for-each-ref', '--format=%(refname)', f'refs/heads/{name}', f'refs/remotes/origin/{name}'); hr = [x.replace('refs/', '') for x in hr.split('\n') if x]
    _, _, rce = git('cat-file', '-e', sha + '^{commit}'); obj = '在' if rce == 0 else '★無★'
    def cherry(base):
        o, e, rc = git('cherry', base, sha); ls = [x for x in o.split('\n') if x]
        return sum(1 for x in ls if x[0] == '+'), sum(1 for x in ls if x[0] == '-'), [x.split()[1] for x in ls if x[0] == '+'], rc
    pl, ml, plus_l, rcl = cherry(L); po, mo, plus_o, rco = cherry(O)
    _, _, al = git('merge-base', '--is-ancestor', sha, L); _, _, ao = git('merge-base', '--is-ancestor', sha, O)
    anc = f'{"○" if al == 0 else "×"}/{"○" if ao == 0 else "×"}'
    inL = sum(1 for p in plus_o if p in {l.split('\t')[0] for l in open(D + '/raw/10_local.tsv', encoding='utf-8').read().split('\n')[1:] if l})
    if pl == 0: agree_local0 += 1
    if po == 0: origin0.append(name)
    rows.append((name, sha, now, ';'.join(hr), obj, f'+{pl} -{ml} rc{rcl}', f'+{po} -{mo} rc{rco}', anc, ' '.join(p[:12] for p in plus_o), inL))
    out.append(f'| {name} | {sha[:12]} | {same} | {";".join(hr) or "無"} | {obj} | +{pl} −{ml} | +{po} −{mo} | {anc} | {" ".join(p[:12] for p in plus_o)}(内 local 側 16 本の中 {inL}) |')
out.append(f'\n集計(母數 {len(eda)}): 基点=local で +0 の枝 {agree_local0}(家老の宣 9)/ 基点=origin で +0 の枝 {len(origin0)}(家老の宣 1) {origin0}')
out.append('★食ひ違ひの出所(一行)★: 9 枝の tip は悉く local main の祖先(祖先列 ○/×)ゆゑ基点=local では寄与 0 だが、其の tip が含む commit の内 ★local 側 16 本に属する物(乙 14 本)は origin/main に無い★ ∴ 基点=origin では其れらが + に立つ ―― 差は「枝の中身」でなく「main の乖離 14 本」其の物が写つて居る。')
out.append('註: karo-mac/km-gate-kou-otsu-20260917 の tip は local main 其の物(363d5fb0)ゆゑ、基点=origin では 14 本 悉くが + に立つ。skills-tools-20260908b の tip は分岐点 6e9d4060 其の物ゆゑ両基点で 0(origin/main の PR #8 merge がこれを含む)。')
K.kaku_tsv(D + '/raw/40_eda9.tsv', rows, ['branch', 'paper_sha', 'ls_remote_now', 'local_refs', 'object', 'cherry_vs_local', 'cherry_vs_origin', 'ancestor_L_O', 'plus_commits_vs_origin', 'plus_in_local16'])
K.kaku(D + '/raw/40_eda9.txt', '\n'.join(out)); print('\n'.join(out))
