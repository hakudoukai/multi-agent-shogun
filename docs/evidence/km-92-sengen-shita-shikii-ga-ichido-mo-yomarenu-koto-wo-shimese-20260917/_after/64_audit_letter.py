# -*- coding: utf-8 -*-
"""64 監査提出(第81弾 km-92・km-86 の写し・員外)―― ~/bin/sb write letter "<胴>" --to gunshi-mac --parent-seq 324588(km-84 と同じ系= 裁 seq324588「閾の番人」の横展開ゆゑ親に繋ぐ)。
送る前: 胴は letter 直後の位置引数 一つ・旗で始まらぬ・字数 二器・300 字。送つた後: sb read seq <新seq> で胴を讀み返し(錨= sha16 と冒頭 30 字)、陰性対照= 親 seq の行に己の錨が無い事。裁 seq324831 により PASS は待たぬ。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; OUT = D + '/_after'; KM = os.path.basename(D)
P_ = hashlib.sha256(open(D + '/README.md', 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); mrc = re.search(r'main \| 渡した (\d+) \| rc (\d+)', rcs)
T10 = open(D + '/raw/10_meisho.txt', encoding='utf-8').read(); T41 = open(D + '/raw/41_kansu_after.txt', encoding='utf-8').read(); T45 = open(D + '/raw/45_commit.txt', encoding='utf-8').read()
g = lambda T, p: re.search(p, T, re.S).group(1)
body = (f"[專任1 第81弾 km-92 監査提出] 閾 DETECT_STALE_STALE_SEC は口1讀手0(閾999999でも不変)・/bin/date -d rc1・非數6/8が auto-poke。直し=閾を讀ませ+fromisoformat+數字のみ&[-gt 0]&[-le 253402300799]。両対照{g(T41, r'判 ○ (\d+) /')}/{g(T41, r'母數 (\d+)')}○・test BF/G PASS。紙 km-92 束 README.md sha16 {P_}(門rc{mrc.group(2)})。枝 ashigaru-mac-1/km-92-… {g(T45, r'full sha (\S+) /')[:12]}(的1本)。push請はず(裁324588 順⑶)。")
n1 = len(body); n2 = subprocess.run(['wc', '-m'], input=body.encode('utf-8'), capture_output=True).stdout.decode().strip()
argv = [os.path.expanduser('~/bin/sb'), 'write', 'letter', body, '--to', 'gunshi-mac', '--parent-seq', '324588']
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
out = [f'# 64 監査提出 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 宛 gunshi-mac / parent 324588 / 字数 len {n1} = wc -m {n2} / sb rc {p.returncode} / seq {seq}', '送出行(stdout): ' + so.strip().replace('\n', ' ␊ ')[:300], '送出行(stderr): ' + se.strip().replace('\n', ' ␊ ')[:300]]
if seq:
    r = subprocess.run([os.path.expanduser('~/bin/sb'), 'read', 'seq', seq], capture_output=True, text=True); rb = r.stdout
    ok_sha = P_ in rb; ok_head = body[:30] in rb; tgt = re.search(r'target_agent[\'":\s]+([\w-]+)', rb); par = re.search(r'parent_seq[\'":\s]+(\d+)', rb)
    out.append(f'第八の番人 sb read seq {seq} rc {r.returncode}: 錨 sha16 {"在" if ok_sha else "★無★"} / 冒頭30字 {"在" if ok_head else "★無★"} / target_agent {tgt.group(1) if tgt else "?"} / parent_seq {par.group(1) if par else "?"}(宣 {n1} 字)')
    n = subprocess.run([os.path.expanduser('~/bin/sb'), 'read', 'seq', '324588'], capture_output=True, text=True)
    out.append(f'陰性対照 sb read seq 324588 rc {n.returncode}: 己の錨 sha16 {"★在(器が疑はしい)★" if P_ in n.stdout else "無(正)"}')
    K.kaku(OUT + f'/64_readback_{seq}.txt', rb)
out.append(body); K.kaku(OUT + '/64_audit.txt', '\n'.join(out)); print('\n'.join(out))
