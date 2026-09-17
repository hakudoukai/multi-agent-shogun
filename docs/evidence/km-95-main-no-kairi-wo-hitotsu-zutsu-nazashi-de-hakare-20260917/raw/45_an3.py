# -*- coding: utf-8 -*-
"""45 ㋔ 乖離を解く道 三案(第82弾 km-95)―― 案を書く前に ★三つの測り★ を足す(読取のみ): ①分岐点から両側が変へた path の重なり(merge した時に衝突し得る母數)②origin の枝の内、object が手元に在り local main の tip 363d5fb0 を祖先に持つ物(= 乙 14 本が既に origin の何処かに在るか)③二重(甲 2 本)が merge/rebase で何に成るか。然る後、三案(甲/乙/丙)に就き 直る物・直らぬ物 を一行づつ、推す案と捨てた理由、裁へ出す一文(300 字以内・len を焼く)。"""
import sys, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git
L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'; MB = '6e9d40600a801aa713ac238e2e62bbae06c9e683'
out = [f'# 45 ㋔ 三案 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
a, _, _ = git('diff', '--name-only', MB, L); b, _, _ = git('diff', '--name-only', MB, O); pa = set(x for x in a.split('\n') if x); pb = set(x for x in b.split('\n') if x); kasanari = sorted(pa & pb)
out.append(f'① path の重なり: local 側が分岐点から変へた path {len(pa)} / origin 側 {len(pb)} / 重なり ★{len(kasanari)}★ {kasanari}')
for p in kasanari:
    x, _, _ = git('rev-parse', '-q', '--verify', f'{L}:{p}'); y, _, _ = git('rev-parse', '-q', '--verify', f'{O}:{p}')
    out.append(f'   {p}: blob L {x.strip()[:12] or "(無)"} / O {y.strip()[:12] or "(無)"} → {"同じ(衝突せぬ)" if x.strip() == y.strip() else "★違ふ(merge で衝突し得る・3-way の結果は merge を走らせねば測れぬ)★"}')
heads = [l.split() for l in open(D + '/raw/10_ls_remote_heads.txt', encoding='utf-8') if not l.startswith('#') and l.strip()]
hold = []; noobj = 0
for sha, ref in heads:
    _, _, rce = git('cat-file', '-e', sha + '^{commit}')
    if rce != 0: noobj += 1; continue
    _, _, ra = git('merge-base', '--is-ancestor', L, sha)
    if ra == 0: hold.append((ref.replace('refs/heads/', ''), sha[:12]))
out.append(f'② origin の枝 {len(heads)} 本の内 object が手元に無い {noobj}(測れぬ・fetch せぬ)/ local main の tip 363d5fb0 を含む枝 ★{len(hold)}★ {hold} ∴ 乙 14 本は origin に ★枝としては既に在る★(main としては無い)')
out.append('③ 甲 2 本(f2bfa26a / f0d59a3b ≡ af0dacfc / 26e23590): merge なら両 sha が歴史に残り diff は空(同 patch)・rebase なら local 側の 2 本が落ちて origin 側の sha が残る。')
out.append('')
out.append('## 三案 ―― 各案に 直る物 / 直らぬ物')
out.append('甲= local main を origin/main へ寄せる(reset --hard origin/main 相当・D レーン)。直る: local main = origin main と成り、9 枝の「不要」判定が基点に依らず一つに成る。直らぬ: 乙 14 本が local main から落ち、origin 側は main に無い儘 ―― 中身は karo-mac/km-gate-kou-otsu-20260917(origin・363d5fb0)にしか残らず、9 枝を消せば ★両側から失せる★。')
out.append('乙= origin へ local の未到達分を出す(PR: karo-mac/km-gate-kou-otsu-20260917 → main、或は local main へ origin/main を merge して push)。直る: 乙 14 本が origin/main へ届き、9 枝は両基点で寄与 0 と成つて初めて「不要」が基点に依らず言へる。直らぬ: 甲 2 本の二重 sha は歴史に残る(害は無い・diff 空)／重なり path 2 本の内 .gitignore は file 単位 3-way で衝突 0(46)だが、真の merge の出目は走らせねば測れぬ／local main は其の後 origin/main へ合はせる一手(merge か ff)が要る。')
out.append('丙= 両者を別物として扱ひ、枝の「不要」の基点だけ origin/main へ改める。直る: 家老の紙の「9 本 vs 1 本」の食ひ違ひ(定義の差)は消え、消してよい枝は skills-tools-20260908b の 1 本と読める。直らぬ: 乖離 14/8 其の物は残り、以後の測りは毎回「基点は何か」を宣さねば数が二つ出る／乙 14 本は origin/main へ永久に届かぬ。')
out.append('')
out.append('★推す案= 乙★。捨てた理由: 甲は「消す」側へ倒す道で乙 14 本(門・死箱の門・evidence 10 本)を main から落とす ―― 測りの目的(枝を消せるか)に対し中身を失ふ危険が大きい。丙は数の食ひ違ひを説明で済ませる道で、乖離を解かぬ(札の的は「乖離を解く道」)。乙は既に origin に枝として在る 363d5fb0 を main へ入れるだけで、此の席からの push は要らず、可逆(PR は閉ぢられる)。')
bun = ("裁へ: local main 363d5fb0 と origin main 4be3ee19 は分岐点 6e9d4060 から両向きに乖離(patch-id で local 14・origin 8、内 2 本は同 patch 別 sha)。"
       "local の 14 本は origin に枝 karo-mac/km-gate-kou-otsu-20260917(=363d5fb0)に在り main に無い。"
       "推す道=乙: 其の枝を PR で origin main へ入れ、後に local main を合はせる。"
       "9 枝は其の後 両基点で寄与 0 と成つてから消す。今消せば 14 本が両側から失せる。")
n1 = len(bun); n2 = subprocess.run(['wc', '-m'], input=bun.encode('utf-8'), capture_output=True).stdout.decode().strip()
out.append(f'\n## 裁へ出す一文(python len ★{n1}★ 字 / wc -m {n2} / 條 300 → {"通" if n1 <= 300 else "★超★"})'); out.append(bun)
K.kaku(D + '/raw/45_an3.txt', '\n'.join(out)); print('\n'.join(out))
