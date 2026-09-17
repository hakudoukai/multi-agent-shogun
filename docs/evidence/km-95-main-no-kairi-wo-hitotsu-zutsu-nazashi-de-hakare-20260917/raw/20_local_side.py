# -*- coding: utf-8 -*-
"""20 ㋑ local 側 16 本の判(第82弾 km-95)―― 各本を 甲(origin に同じ内容が別 sha で在る= patch-id 一致)/ 乙(origin に無い)/ 丙(判ぜられぬ)へ落とす。判の器= patch-id(--stable)を origin 側(L..O)の非merge と突き合はせ、加へて ★cherry の出目(+/−)と一致するか★ を刷る(二器)。乙に就いては ★変へた path の blob が origin/main の tip で同じか★ も測る(tip に同じ中身が在るなら「別の経路で届いた」の徴・判は変へぬ)。"""
import sys, time, csv
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git
L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'
rd = lambda n: list(csv.DictReader(open(D + f'/raw/10_{n}.tsv', encoding='utf-8'), delimiter='\t'))
loc, ori = rd('local'), rd('origin'); opid = {r['patch_id_stable']: r['sha'] for r in ori if r['kind'] == 'single'}
out = [f'# 20 ㋑ local 側の判 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 母數= local 側 rev-list {len(loc)} 本(非merge {sum(1 for r in loc if r["kind"] == "single")})/ 突合せ先= origin 側 非merge {len(opid)} 本の patch-id(--stable)']
out.append('| # | full sha | 判 | 根拠(patch-id 一致先 / cherry) | 変へた path 数 | 内 O の tip で blob 同じ | subject |'); out.append('|---|---|---|---|---|---|---|')
tally = {'甲': 0, '乙': 0, '丙': 0}; rows = []
for i, r in enumerate(loc, 1):
    s = r['sha']; nm, _, _ = git('diff-tree', '--no-commit-id', '--name-only', '-r', '--root', s); paths = [p for p in nm.split('\n') if p]
    same = 0
    for p in paths:
        a, _, ra = git('rev-parse', '-q', '--verify', f'{s}:{p}'); b, _, rb = git('rev-parse', '-q', '--verify', f'{O}:{p}')
        if ra == 0 and rb == 0 and a.strip() == b.strip(): same += 1
    if r['kind'] != 'single' or r['patch_id_stable'] in ('-', ''): han, kon = '丙', 'merge か空 diff ゆゑ patch-id が取れぬ'
    elif r['patch_id_stable'] in opid: han, kon = '甲', f'origin {opid[r["patch_id_stable"]][:12]} と patch-id 一致 / cherry {r["cherry"]}'
    else: han, kon = '乙', f'origin 側 {len(opid)} 本の何れとも不一致 / cherry {r["cherry"]}'
    if (han == '甲') != (r['cherry'] == '-'): han, kon = '丙', kon + ' ★二器(patch-id/cherry)が食ひ違ふ★'
    tally[han] += 1; rows.append((s, han, kon, len(paths), same, r['subject']))
    out.append(f'| {i} | {s} | {han} | {kon} | {len(paths)} | {same} | {r["subject"][:70].replace("|", "¦")} |')
out.append(f'\n判の集計(母數 {len(loc)}): 甲 {tally["甲"]} / 乙 {tally["乙"]} / 丙 {tally["丙"]} → 甲+乙+丙 = {sum(tally.values())}')
out.append('甲の二本は、origin 側 PR #15(mac/karo-manifest-verify-20260910)の中身 af0dacfc / 26e23590 と同 patch-id ―― 即ち ★同じ直しが別の枝で作り直され PR で入つた★(局所 main の sha は origin に無いが中身は在る)。')
out.append('乙 14 本の「O の tip で blob 同じ」列が 0 でない物は、path の中身が別の commit で届いた徴に過ぎず、判(乙)は変へぬ。')
K.kaku_tsv(D + '/raw/20_local_side.tsv', rows, ['sha', 'han', 'konkyo', 'paths', 'same_blob_at_O_tip', 'subject'])
K.kaku(D + '/raw/20_local_side.txt', '\n'.join(out)); print('\n'.join(out))
