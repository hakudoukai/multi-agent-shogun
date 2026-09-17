# -*- coding: utf-8 -*-
"""40 口ごと 8形 の負テスト(第56弾 km-78 ㋐)
★何を走らせるか★: 口の川下で当つた ★比較器そのもの★ を、名の居る側を保つた儘
  `[ "$V" -op "0" ]` 又は `[ "0" -op "$V" ]` の形へ落として /bin/bash 3.2 で走らせる。
★何を走らせぬか★: 器の全体は走らせぬ(側効=箱書き・tmux 送鍵が在るゆゑ)。
  ∴ 本器が示すのは ★比較器の出目★ であつて ★器の振舞ひ★ ではない(甲のみ 30 で全体を走らせた)。
★陽性対照★: 形5(正常値 7)は悉くの口で rc 0 又は 1 に成らねばならぬ。2 が出れば器の壊れ。
★陰性対照★: 「比較器に入らぬ」と分類した口を 3 つ混ぜ、-op が無いゆゑ ★測れぬ★ と刷る。"""
import os, re, sys, subprocess, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
rows = [l.split('\t') for l in open(D + '/raw/20_kawashimo.tsv', encoding='utf-8').read().splitlines()[1:]]
NUM = re.compile(r'-(?:ge|gt|le|lt|eq|ne)\b')
FORMS = [('1未設定', None), ('2空文字', ''), ('3空白のみ', ' '),
         ('4二十桁', '99999999999999999999'), ('5正常値7', '7'), ('6負数', '-5'),
         ('7改行入り', '1\n2'), ('8既存␊', '1␊2')]
best = {}
for f, name, pl, ul, kind, gen in rows:
    if kind != '数比': continue
    k = (f, name)
    if k in best: continue
    m = NUM.search(gen)
    if not m: continue
    op = m.group(0)
    left = bool(re.search(r'\$\{?' + re.escape(name) + r'[^\s]*"?\s*' + op, gen))
    best[k] = (op, 'L' if left else 'R', pl, ul, gen)
out, ctl_bad = [], 0
for (f, name), (op, side, pl, ul, gen) in sorted(best.items()):
    expr = '[ "$V" %s "0" ]' % op if side == 'L' else '[ "0" %s "$V" ]' % op
    res = []
    for lab, val in FORMS:
        env = dict(os.environ)
        env.pop('V', None)
        if val is not None: env['V'] = val
        p = subprocess.run(['/bin/bash', '-c', expr + '; echo $?'],
                           capture_output=True, text=True, env=env)
        rc = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else '?'
        res.append(rc)
        if lab == '5正常値7' and rc == '2': ctl_bad += 1
    out.append([f, name, pl, ul, op, side, expr] + res)
K.kaku_tsv(D + '/raw/40_hakari.tsv', out,
           header=['file', 'name', 'port_line', 'use_line', 'op', 'side', 'expr'] + [l for l, _ in FORMS])
c = collections.Counter()
for r in out:
    for i, (lab, _) in enumerate(FORMS):
        if r[7 + i] == '2': c[lab] += 1
sm = ['# 40 8形 負テスト / 数比口= %d / 一口 8走 = %d 走' % (len(out), len(out) * 8)]
sm.append('★陽性対照(形5 正常値7)で rc=2 を出した口= %d ―― 0 が健全★' % ctl_bad)
sm.append('# 形ごとの「rc=2(比較器が倒れる)」口数:')
for lab, _ in FORMS:
    sm.append('    %-10s %2d / %d 口' % (lab, c[lab], len(out)))
sm.append('# ★rc=2 は「條件が偽」ではない。`[` が判定を放棄した出目である。')
sm.append('#   if の側から見れば偽と同じ道を通る ―― ∴ ★倒れた事に気付かぬ★ 之が fail-open の正体。')
K.kaku(D + '/raw/40_hakari_summary.txt', '\n'.join(sm))
print('\n'.join(sm))
