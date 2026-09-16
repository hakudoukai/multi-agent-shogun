# -*- coding: utf-8 -*-
"""追ひ便 10 の器 64(第68弾・根の外 _after/)。紙の後に生れた事を告げる: ⑴ 96 の實測 ⑵ git add -f ⑶ 宣⇔實(両基準・過大)⑷ 前置 59 の一走目が己の生 > 捕へ(62_dry.err 0byte)を咎めた事。数は 96/63/67/59.first の .txt/.out から regex で引く。字数を先に測り 300 超なら送らぬ。送る前に 40 を束全体へ今一度掛け(97_bundle_final)疵を数へる。"""
import os, sys, re, time, subprocess, yaml
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; RAW = D + '/raw'; M = '/Users/momizimac/multi-agent-shogun'; sys.path.insert(0, AFT); import kaki as K
def rd(p): return open(p, encoding='utf-8').read()
def num(pat, t, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
q = subprocess.run(['python3', '-B', RAW + '/40_mon_no_ato.py', D, AFT + '/00_hosho.txt', RAW + '/50_sengen.txt', AFT, '97_bundle_final'], capture_output=True, text=True)
ato = num(r'## 後 (\d+) 本', q.stdout); kz = num(r'疵\) (\d+) 本', q.stdout); mu = num(r'母數 通常 file (\d+)', q.stdout)
S63 = rd(AFT + '/63_sent.txt'); seki = re.search(r'席基準[^\n]*實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+)', S63); karo = re.search(r'家老基準[^\n]*實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+)', S63)
G67 = rd(AFT + '/67_git_add.txt'); stg = num(r'staged (\d+) 本', G67); head = num(r'HEAD (\w+)', G67); rc67 = num(r'/ rc (\d+)', G67)
A96 = rd(AFT + '/96_after.txt'); r1 = re.search(r'⑴ 根 raw/[^\n]*rc (\d+) / 母數 (\d+) / 後 (\d+) / ★疵 (\d+)★', A96); r2 = re.search(r'⑵ 根 束全体[^\n]*後 (\d+)\(宣に在る (\d+)\)/ ★疵 (\d+)★', A96); j = num(r'一致 (\d+) / 相違 0 / 実体無 0 / 読めぬ行 0', A96)
first59 = rd(RAW + '/59_prescan.first.out'); n59 = num(r'鳴つた file (\d+)', first59); f59 = num(r"★\['條④空'\] (\S+)", first59)
bai = float(seki.group(2)) / float(seki.group(1))
body = (f"[第68弾 追ひ便 10] 紙の後: ①96 實測 raw/ 後{r1.group(3)} 疵{r1.group(4)} EACCES(母數{r1.group(2)})/束全体 後{r2.group(1)}(宣{r2.group(2)})疵{r2.group(3)}/照合{j}一致/錠 悉く。今の束(97)母數{mu} 後{ato} 疵{kz}。"
        f"②git add -f rc{rc67} staged{stg}(HEAD {head}・64の出目は未staged)。③宣⇔實 席{seki.group(1)}分(宣{seki.group(2)}・{seki.group(3)})家老{karo.group(1)}分({karo.group(3)})符號同=★{bai:.1f}倍の過大★(長く置いた宣が逆へ外れた)。"
        f"④前置59 一走目が己の生 > 捕へ({f59} 0byte){n59}本を咎め→10_run 越しに直した(.first)")
n = len(body); print('字数', n); assert n <= 300, n
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', body, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
hit = [m for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith('[第68弾 追ひ便 10]')]
out = [time.strftime('%Y-%m-%dT%H:%M:%S%z'), f'宛 karo-mac / type report / 追ひ便 10({n} 字)/ inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''),
       f'第八の番人: entry {len(hit)} 本 {[m["id"] for m in hit]} / ' + ' | '.join(f'箱 {len(str(m.get("content", "")).rstrip(chr(10)))} / 64 {n} / 逐語一致 {str(m.get("content", "")).rstrip(chr(10)) == body}' for m in hit), f'40 束全体(97_bundle_final): rc {q.returncode} / 母數 {mu} / 後 {ato} / 疵 {kz}', '本文: ' + body]
K.kaku(AFT + '/63b_sent.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 6)
