# -*- coding: utf-8 -*-
# ★負テスト両対照(裁 seq324588)★ ―― 「鳴らなかつた」は器が生きて居る証を添へねば空虚である。
#   陰性A(値1・宣)=黙つて timeout 枝／陰性B(値0・宣)=黙つて枝無(event-only)／陽性(値2・毒)=枝が変はる
#   ★対照の証★: 陰性A で BRANCH=timeout が出る ⇒ 「BRANCH=無」は器の死に非ず、枝の違ひである。
import subprocess, os
SH = '/bin/bash'
CASES = [('陰性A(値1・宣どほり)', '1'), ('陰性B(値0・宣どほり)', '0'), ('★陽性(値2・毒)★', '2')]
rows = []
for label, val in CASES:
    for form in ('genkei', 'naoshi'):
        env = dict(os.environ); env['ASW_PROCESS_TIMEOUT'] = val
        p = subprocess.run([SH, 'raw/13_harness_%s.sh' % form], capture_output=True, text=True, env=env)
        sh = [l for l in p.stderr.splitlines() if l.startswith('[watcher]')]
        hk = [l for l in p.stderr.splitlines() if l and not l.startswith('[watcher]')]
        br = [l.split('=', 1)[1] for l in p.stdout.splitlines() if l.startswith('BRANCH=')]
        rows.append((label, form, val, p.returncode, br[0] if br else '無', len(sh), len(hk)))
out = ['対照\t器形\t値\trc\tBRANCH\t器の報せ行\t外の声行']
for r in rows: out.append('\t'.join(str(x) for x in r))
def get(label, form): return [r for r in rows if r[0] == label and r[1] == form][0]
ok = []
ok.append(('陰性A 両形とも BRANCH=timeout・報せ0',
           get(CASES[0][0], 'genkei')[4] == 'timeout' and get(CASES[0][0], 'naoshi')[4] == 'timeout'
           and get(CASES[0][0], 'genkei')[5] == 0 and get(CASES[0][0], 'naoshi')[5] == 0))
ok.append(('陰性B 両形とも BRANCH=無・報せ0(宣=event-only)',
           get(CASES[1][0], 'genkei')[4] == '無' and get(CASES[1][0], 'naoshi')[4] == '無'
           and get(CASES[1][0], 'genkei')[5] == 0 and get(CASES[1][0], 'naoshi')[5] == 0))
ok.append(('★陽性 現形= BRANCH無・報せ0(黙つて縮退=害)★',
           get(CASES[2][0], 'genkei')[4] == '無' and get(CASES[2][0], 'genkei')[5] == 0))
ok.append(('★陽性 直し形= BRANCH=timeout・報せ1(刷つて倒す)★',
           get(CASES[2][0], 'naoshi')[4] == 'timeout' and get(CASES[2][0], 'naoshi')[5] == 1))
ok.append(('対照の証: 同じ器が BRANCH=timeout を出せる(陰性A) ⇒ 「無」は器の死に非ず',
           get(CASES[0][0], 'genkei')[4] == 'timeout'))
out.append('')
for t, v in ok: out.append('%s %s' % ('○' if v else '×★落★', t))
out.append('')
out.append('判=%s(○=%d/%d)' % ('通' if all(v for _, v in ok) else '★落★', sum(1 for _, v in ok if v), len(ok)))
open('raw/21_taishou.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
