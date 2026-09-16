# -*- coding: utf-8 -*-
"""追ひ便 9 の器 64(第67弾・根の外 _after/)。紙の後に生れた事を告げる: ⑴ 59 が 40/50 の行末空白を咎め門の前に直した(挙動不変・.first)⑵ 96 の實測 ⑶ git add -f ⑷ 宣⇔實 ⑸ 便1 の DRY 282 → 實 293(埋めで伸びた)。送る前に 40 を束全体へ今一度掛け(97_bundle_final)疵を数へる。字数を先に測り 300 超なら送らぬ。"""
import os, sys, re, time, subprocess, yaml
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; RAW = D + '/raw'; M = '/Users/momizimac/multi-agent-shogun'; sys.path.insert(0, AFT); import kaki as K
def rd(p): return open(p, encoding='utf-8').read()
def num(pat, t, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
q = subprocess.run(['python3', '-B', RAW + '/40_mon_no_ato.py', D, AFT + '/00_hosho.txt', RAW + '/50_sengen.txt', AFT, '97_bundle_final'], capture_output=True, text=True)
ato = num(r'## 後 (\d+) 本', q.stdout); kz = num(r'疵\) (\d+) 本', q.stdout); mu = num(r'母數 通常 file (\d+)', q.stdout)
S63 = rd(AFT + '/63_sent.txt'); seki = re.search(r'席基準[^\n]*實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+)', S63); karo = re.search(r'家老基準[^\n]*實 ([\d.]+) 分 ⇔ 宣 ([\d.]+) 分 → 宣−實 ([+\-][\d.]+)', S63)
G67 = rd(AFT + '/67_git_add.txt'); stg = num(r'staged (\d+) 本', G67); head = num(r'HEAD (\w+)', G67); rc67 = num(r'/ rc (\d+)', G67)
A96 = rd(AFT + '/96_after.txt'); r1 = re.search(r'⑴ 根 raw/[^\n]*rc (\d+) / 母數 (\d+) / 後 (\d+) / ★疵 (\d+)★', A96); r2 = re.search(r'⑵ 根 束全体[^\n]*後 (\d+)\(宣に在る (\d+)\)/ ★疵 (\d+)★', A96); j = num(r'一致 (\d+) / 相違 0 / 実体無 0 / 読めぬ行 0', A96)
first59 = rd(RAW + '/59_prescan.first.out'); n59 = num(r'鳴つた file (\d+)', first59)
body = (f"[第67弾 追ひ便 9] 紙の後に生れた事: ①前置59 一走目が 40/50 の行末空白を{n59}本咎め→門の前に直した(空白のみ・挙動不変・.first に残す)。②96 實測: raw/ 後{r1.group(3)} 疵{r1.group(4)} 書けば EACCES(母數{r1.group(2)})/束全体 後{r2.group(1)}(宣{r2.group(2)})疵{r2.group(3)}/照合{j}一致/錠 悉く。今の束(97)母數{mu} 後{ato} 疵{kz}。"
        f"③git add -f rc{rc67} staged{stg}(HEAD {head}・64/67の出目は未staged)。④宣⇔實 席{seki.group(1)}分({seki.group(3)})家老{karo.group(1)}分({karo.group(3)})符號同・過大。⑤疵: 便1 DRY282→實293(sha埋めで伸びる・DRYは仮値)")
n = len(body); print('字数', n); assert n <= 300, n
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', body, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
hit = [m for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith('[第67弾 追ひ便 9]')]
out = [time.strftime('%Y-%m-%dT%H:%M:%S%z'), f'宛 karo-mac / type report / 追ひ便 9({n} 字)/ inbox_write rc={p.returncode}' + (f' stderr={p.stderr.strip()[:140]}' if p.stderr.strip() else ''),
       f'第八の番人: entry {len(hit)} 本 {[m["id"] for m in hit]} / ' + ' | '.join(f'箱 {len(str(m.get("content", "")).rstrip(chr(10)))} / 64 {n} / 逐語一致 {str(m.get("content", "")).rstrip(chr(10)) == body}' for m in hit), f'40 束全体(97_bundle_final): rc {q.returncode} / 母數 {mu} / 後 {ato} / 疵 {kz}', '本文: ' + body]
K.kaku(AFT + '/63b_sent.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if p.returncode == 0 and len(hit) == 1 else 6)
