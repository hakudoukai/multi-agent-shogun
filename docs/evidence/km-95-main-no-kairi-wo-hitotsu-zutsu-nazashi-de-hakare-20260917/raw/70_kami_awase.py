# -*- coding: utf-8 -*-
"""70 紙の数の照合(第82弾 km-95)―― README.md に写した主な数・sha を raw の出目に当てる(組を列べた分だけ・全数ではない)。○/× と母數を刷る。"""
import sys, re, time
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K
R = open(D + '/README.md', encoding='utf-8').read(); T = lambda n: open(D + f'/raw/{n}', encoding='utf-8').read()
kumi = [
 ('分岐点 6e9d4060', '10_bunki.txt', r"merge-base --all = \['6e9d40600a801aa713ac238e2e62bbae06c9e683'\]\(本数 1\)"),
 ('rev-list 16/21', '10_bunki.txt', r'local 側.*rev-list commit 数 16\(内 merge 0\).*\n.*origin 側.*rev-list commit 数 21\(内 merge 11\)'),
 ('非merge 16/10', '10_bunki.txt', r'cherry の母數 16 .*\n.*cherry の母數 10 '),
 ('相手に無い 14/8', '10_bunki.txt', r'相手側に無い patch-id 14 .*\n.*相手側に無い patch-id 8 '),
 ('stable≠unstable 11/7', '10_bunki.txt', r'食ひ違ふ commit 11\n.*食ひ違ふ commit 7'),
 ('ls-remote 239/41/18・手元 7', '10_bunki.txt', r'全 239 本 / karo-mac/ 41 / ashigaru-mac-\*/ 18.*★7 本★'),
 ('甲 2 乙 14 丙 0', '20_local_side.txt', r'甲 2 / 乙 14 / 丙 0 → 甲\+乙\+丙 = 16'),
 ('甲 f2bfa26a≡af0dacfc', '20_local_side.txt', r'f2bfa26a163dbee334861bd80bb0bd8affa0636d \| 甲 \| origin af0dacfcbc88'),
 ('甲 f0d59a3b≡26e23590', '20_local_side.txt', r'f0d59a3b6315058b2af40bd57689b397243e32c9 \| 甲 \| origin 26e23590f4e4'),
 ('origin 集計 0/21/2/8/11', '30_origin_side.txt', r'refs/heads/\* から届く 0 / refs/remotes/\* からのみ届く 21 / patch-id が local と一致\(非merge\) 2 / 不一致\(非merge\) 8 / merge 11'),
 ('fetch 痕 2026-09-17 04:19:56', '30_reflog_origin_main.txt', r'4be3ee1 origin/main@\{2026-09-17 04:19:56 \+0900\} fetch origin --quiet: fast-forward'),
 ('reflog origin/main 8 行', '30_reflog_origin_main.txt', r'/ 8 行'),
 ('reflog main 40 行', '30_reflog_heads_main.txt', r'/ 40 行'),
 ('main の ff 2026-08-07', '30_reflog_heads_main.txt', r'9b8c89b main@\{2026-08-07 02:00:57 \+0900\} merge origin/main: Fast-forward'),
 ('9 枝 基点local 9 / origin 1', '40_eda9.txt', r'基点=local で \+0 の枝 9\(家老の宣 9\)/ 基点=origin で \+0 の枝 1\(家老の宣 1\) \[\'karo-mac/skills-tools-20260908b\'\]'),
 ('km-gate-kou-otsu +14 −2', '40_eda9.txt', r'karo-mac/km-gate-kou-otsu-20260917 \| 363d5fb06084 \| 一致 \| heads/\S+ \| 在 \| \+0 −0 \| \+14 −2 \| ○/×'),
 ('重なり 2', '45_an3.txt', r'重なり ★2★ \[\'\.gitignore\', \'scripts/checks/karo_mac_manifest_verify\.py\'\]'),
 ('46 枝が含む・157 測れぬ', '45_an3.txt', r'object が手元に無い 157\(測れぬ・fetch せぬ\)/ local main の tip 363d5fb0 を含む枝 ★46★'),
 ('一文 299 字', '45_an3.txt', r'python len ★299★ 字 / wc -m 299 / 條 300 → 通'),
 ('3-way rc 0', '46_gitignore_3way.txt', r'git merge-file -p local base origin → rc ★0★'),
 ('ls-remote = 写し', '00_start.txt', r'★ls-remote origin refs/heads/main\(今の値・読取 rc 0\)= 4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1★ → 手元の写しと 一致'),
 ('家老紙 2620B 585eea9f', '00_start.txt', r'= 2620B sha256 585eea9f775e549d\S+ → 札の宣.*と 一致'),
]
out = [f'# 70 紙の照合 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 組の母數 {len(kumi)}']; ok = 0
for label, fn, pat in kumi:
    hit = re.search(pat, T(fn)); inR = label.split(' ')[-1] in R or label in R
    ok += bool(hit); out.append(f'{"○" if hit else "★×★"} {label} ← raw/{fn} {"在" if hit else "★無★"} / 紙に語 {"在" if inR else "(紙は別表記)"}')
out.append(f'判 ○ {ok} / × {len(kumi) - ok} / 母數 {len(kumi)}')
K.kaku(D + '/raw/70_kami_awase.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if ok == len(kumi) else 1)
