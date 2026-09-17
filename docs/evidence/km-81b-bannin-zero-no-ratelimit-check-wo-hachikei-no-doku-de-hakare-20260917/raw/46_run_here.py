# -*- coding: utf-8 -*-
"""46(第77弾 km-81b)―― 此の checkout で的を其の儘一度起こし(bash scripts/ratelimit_check.sh・引数無し・repo へ 0 字・tmux へは L28 で止まるゆゑ届かぬ)、何処で・どう止まるかを rc と stderr で測る。
陽性対照= 同じ呼び方で `--help`(L19-22・source の前に exit 0 する筈)。"""
import sys, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/ratelimit_check.sh'
out = [f'# 46 此の checkout で起こす / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 的 {T} / cwd {M}']
RES = {}
for label, args in (('本走(引数無し)', []), ('陽性対照 --help(L19-22・source L28 より前に exit 0)', ['--help'])):
    p = subprocess.run(['bash', T] + args, capture_output=True, cwd=M, timeout=30); so = p.stdout.decode('utf-8', 'replace').strip(); se = p.stderr.decode('utf-8', 'replace').strip(); RES[label[:2]] = (p.returncode, se)
    out.append(f'{label}: rc {p.returncode} / stdout {so.count(chr(10)) + 1 if so else 0} 行「{so.replace(chr(10), "␊")[:120]}」/ stderr {se.count(chr(10)) + 1 if se else 0} 行「{se.replace(M + "/", "").replace(chr(10), "␊")[:200]}」')
import re
rc0, se = RES['本走']; p = type('R', (), {'returncode': rc0})()  # ★本走の結果を名指す(二走は loop の最後= --help を拾つた・loop 外の index は n-1)★
m = re.search(r'(\S+): line (\d+): (\S+): unbound variable', se); m2 = re.search(r'No such file', se)
if p.returncode != 0 and se: out.append(f'讀み(測りから): 本走は rc {p.returncode}・stderr 有= ★鳴つて止まる★(黙らぬ)。止まつた所= ' + (f'source 先 {m.group(1)} の {m.group(2)} 行目で `{m.group(3)}` が set -u に触れた(L30 の source の中)' if m else ('source 先が無い' if m2 else '逐語を讀め')) + '。∴ 此の checkout では毒は L397 以降の比較器へ届く前に止まる(L64 declare -A にも届かぬ)。')
else: out.append(f'讀み(測りから): rc {p.returncode}・stderr {se.count(chr(10)) + 1 if se else 0} 行 ―― 止まらなんだ/黙つた。')
if m and m.group(3) == 'shogun' and 'section18' in m.group(1): out.append('補(讀み): lib/_section18_roles.sh L108 は `declare -A SECTION18_ROLE_ALIASES=( [shogun]=… )`。bash 3.2 に連想配列は無く、`[shogun]` が算術の添字と讀まれ `shogun` が set -u に触れる ―― ∴ 止めたのは ★此の Mac の bash 3.2★ であり file の有無ではない(00 の declare -A rc2 と同根)。')
out.append('疵: .first は測る前に「L28 で file 無し」と讀みを書いた(誤り・SCRIPT_DIR は repo 根ゆゑ lib/ は在る)。.second は讀みを loop の最後の走(--help)から取り「止まらなんだ」と書いた(loop 外の index は n-1)。此の版は本走の結果を名指して導く。')
K.kaku(D + '/raw/46_run_here.txt', '\n'.join(out)); print('\n'.join(out))
