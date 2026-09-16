# -*- coding: utf-8 -*-
"""追ひ便 8 の器 66(第66弾・根の外)―― 家老の commit 02f733a を見た後に生れた _after/63b_sent.txt 1 本を add -f した(staged・未 commit)事を一便で告げる。字数を先に印字・300 超は送らぬ。"""
import sys, os, subprocess, time, yaml
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, D + '/_after'); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; W = M + '/.claude/worktrees/karo-mac-a1'
head = subprocess.run(['git', '-C', W, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
st = [l for l in subprocess.run(['git', '-C', W, 'status', '--porcelain', '--', 'docs/evidence/km-66-noranu-336-20260917'], capture_output=True, text=True).stdout.split('\n') if l]
tracked = sum(1 for _ in subprocess.run(['git', '-C', W, 'ls-files', '--', 'docs/evidence/km-66-noranu-336-20260917'], capture_output=True, text=True).stdout.split('\n') if _)
body = f"[第66弾 追ひ便 8] 家老の commit {head} を見た(束 tracked {tracked} 本)。其の後に生れた {' '.join(l.split()[-1].split('/')[-1] for l in st)} {len(st)} 本を add -f した(staged・未commit・64 追ひ便7 の送達記録)。commit は家老の手で。己の箱 未読 0・席は idle へ"
print('字数', len(body)); assert len(body) <= 300
p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', 'karo-mac', body, 'report', 'ashigaru-mac-1'], capture_output=True, text=True, cwd=M)
ms = yaml.safe_load(open(M + '/queue/inbox/karo-mac.yaml', encoding='utf-8')).get('messages') or []
ids = [m['id'] for m in ms if m.get('from') == 'ashigaru-mac-1' and str(m.get('content', '')).startswith('[第66弾 追ひ便 8]')]
c = next((str(m.get('content', '')).rstrip('\n') for m in ms if m['id'] == ids[-1]), '') if ids else ''
K.kaku(D + '/_after/63c_sent.txt', f'{time.strftime("%Y-%m-%dT%H:%M:%S%z")}\n便 8({len(body)} 字) inbox_write rc={p.returncode} / entry {len(ids)} 本 {ids} / 逐語一致 {c == body}\n本文: {body}')
print(open(D + '/_after/63c_sent.txt', encoding='utf-8').read())
