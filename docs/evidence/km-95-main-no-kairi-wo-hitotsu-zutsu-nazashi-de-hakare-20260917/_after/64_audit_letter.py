# -*- coding: utf-8 -*-
"""64 監査提出(第82弾 km-95・km-92 の写し・員外)―― ~/bin/sb write letter "<胴>" --to gunshi-mac --parent-seq 325507(的= 家老 seq325507 の紙ゆゑ其の seq へ繋ぐ)。
送る前: 胴は letter 直後の位置引数 一つ・旗で始まらぬ・字数 二器・300 字。送つた後: sb read seq <新seq> で胴を讀み返し(錨= sha16 と冒頭 30 字)、陰性対照= 親 seq の行に己の錨が無い事。裁 seq324831 により PASS は待たぬ。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; OUT = D + '/_after'; KM = os.path.basename(D); PAR = '325507'
P_ = hashlib.sha256(open(D + '/README.md', 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); mrc = re.search(r'main \| 渡した (\d+) \| rc (\d+)', rcs)
T45 = open(D + '/raw/45_an3.txt', encoding='utf-8').read(); bl = re.search(r'python len ★(\d+)★', T45).group(1)
body = (f"[專任1 第82弾 km-95 監査提出] main 乖離を名指しで測つた: 分岐点 6e9d4060・母數三つ(rev-list 16/21・非merge 16/10・相手に無い patch-id 14/8)・local16=甲2/乙14/丙0・origin21 object 在/手元heads 0・9枝の「9 vs 1」は乙14本が写つた物・推す=乙(363d5fb0 は origin 枝46本に既在・3-way 衝突0)・一文 {bl}字。紙 km-95 束 README.md sha16 {P_}(門 rc{mrc.group(2)}・{mrc.group(1)}本)。git 読取のみ・未commit。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
argv = [os.path.expanduser('~/bin/sb'), 'write', 'letter', body, '--to', 'gunshi-mac', '--parent-seq', PAR]
pos = [a for i, a in enumerate(argv[3:]) if not a.startswith('--') and (i == 0 or not argv[3:][i-1].startswith('--'))]
naru = []
if not (40 <= n1 <= 300): naru.append(f'字数 {n1}')
if str(n1) != n2: naru.append(f'二器不一致 {n1}/{n2}')
if body.startswith('--'): naru.append('胴が旗で始まる')
if len(pos) != 1: naru.append(f'letter 後の位置引数 {len(pos)}(1 でなければ打たぬ)')
print('字数 len', n1, 'wc -m', n2, '/ 位置引数', len(pos), '/ 門', naru or '通')
if naru or '--dry' in sys.argv: K.kaku(OUT + '/64_dry.txt', (('★門が鳴つた・送らず★ ' + str(naru)) if naru else '# dry') + '\n' + body); sys.exit(1 if naru else 0)
p = subprocess.run(argv, capture_output=True, text=True); so, se = p.stdout, p.stderr
m = re.search(r'seq=(\d+)', so + se); seq = m.group(1) if m else None
out = [f'# 64 監査提出 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 gunshi-mac / parent {PAR} / 字数 len {n1} = wc -m {n2} / sb rc {p.returncode} / seq {seq}', '送出行(stdout): ' + so.strip().replace('\n', ' ␊ ')[:300], '送出行(stderr): ' + se.strip().replace('\n', ' ␊ ')[:300]]
if seq:
    r = subprocess.run([os.path.expanduser('~/bin/sb'), 'read', 'seq', seq], capture_output=True, text=True); rb = r.stdout
    ok_sha = P_ in rb; ok_head = body[:30] in rb; tgt = re.search(r'target_agent[\'":\s]+([\w-]+)', rb); par = re.search(r'parent_seq[\'":\s]+(\d+)', rb)
    out.append(f'第八の番人 sb read seq {seq} rc {r.returncode}: 錨 sha16 {"在" if ok_sha else "★無★"} / 冒頭30字 {"在" if ok_head else "★無★"} / target_agent {tgt.group(1) if tgt else "?"} / parent_seq {par.group(1) if par else "?"}(宣 {n1} 字)')
    n = subprocess.run([os.path.expanduser('~/bin/sb'), 'read', 'seq', PAR], capture_output=True, text=True)
    out.append(f'陰性対照 sb read seq {PAR} rc {n.returncode}: 己の錨 sha16 {"★在(器が疑はしい)★" if P_ in n.stdout else "無(正)"}')
    K.kaku(OUT + f'/64_readback_{seq}.txt', rb)
out.append(body); K.kaku(OUT + '/64_audit.txt', '\n'.join(out)); print('\n'.join(out))
