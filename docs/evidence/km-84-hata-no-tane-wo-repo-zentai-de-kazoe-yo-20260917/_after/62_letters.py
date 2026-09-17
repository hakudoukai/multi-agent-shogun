# -*- coding: utf-8 -*-
"""納め便の器 62(第78弾 km-84・_after= 臺帳の後の器・員外)―― 五便・各 300 字の條・門(宛先/未讀/字数 二器/?/先送り語)を通してから inbox_write。id は箱の胴の頭 40 字で引く(第八の番人)。宣⇔實は着手便の timestamp(箱の値)を起点に測る。數は悉く器の出目(raw/*.txt・_after/60_gate_rcs.txt)から regex で抽く。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}; LOG = re.search(r'門控 main (\S+)', rcs).group(1)
P_, MN, G = sha16(D + '/README.md'), sha16(D + '/MANIFEST.txt'), sha16(D + '/' + LOG); PB = os.path.getsize(D + '/README.md'); PL = open(D + '/README.md', encoding='utf-8').read().count('\n'); NI = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path='))
me = open(OUT + '/60_gate_main.err', encoding='utf-8').read(); bs = re.search(r'byte和[ =]*(\d+)', me); bs = bs.group(1) if bs else '?'
st = open(E + '/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
FR = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path=') and re.search(r'\.first ', l))
T10 = open(E + '/10_kuchi.txt', encoding='utf-8').read(); g10 = lambda pat: re.search(pat, T10).group(1)
T20 = open(E + '/20_bunrui.txt', encoding='utf-8').read(); g20 = lambda pat: re.search(pat, T20).group(1)
T30 = open(E + '/30_tally.txt', encoding='utf-8').read(); g30 = lambda pat: re.search(pat, T30).group(1)
T40 = open(E + '/40_taishou.txt', encoding='utf-8').read(); g40 = lambda pat: re.search(pat, T40).group(1)
T70 = open(E + '/70_kami_awase.txt', encoding='utf-8').read(); g70 = lambda pat: re.search(pat, T70).group(1)
KZ = sum(1 for l in open(D + '/README.md', encoding='utf-8') if re.match(r'^- ★?疵', l))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); t0 = time.mktime(time.strptime(st_ts, '%Y-%m-%dT%H:%M:%S')); jitsu = (time.time() - t0) / 60
letters = [
 f"[第78弾 納め 1/5・束] docs/evidence/{KM}/ 紙 README.md {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{NI})/ 門控(走毎に一本) {LOG.split('/')[-1][:-4]} {G}。repo 0字・据ゑず・稼働器不觸。着手便 {st_id[-8:]}({st_ts[11:19]})。照合器 母數{g70(r'母數 (\d+)')} ○{g70(r'○ (\d+)')} ×{g70(r'× (\d+)')} rc{g70(r'rc (\d+)')}。",
 f"[第78弾 納め 2/5・門] selftest rc{g['selftest']}・main rc{g['main']}({NI}本・byte和{bs}・條①一致)・nobase rc{g['nobase']}(基点無し・落ちて正)。員外=MANIFEST.txt・_gate/*・_after/*・raw/50_build_manifest.*・raw/50_sengen.txt。.first({FR}本)は員内(倒れた走を残す)。",
 f"[第78弾 納め 3/5・㋐] 根=repo根の git追跡 file(深さ無制限・docs/evidence/除く)={g10(r'歩いた file (\d+) 本')}本({g10(r'shell (\d+) /')}sh/{g10(r'python (\d+)\)')}py)・口{g10(r'口の總數 (\d+)')}(env名{g10(r'env 名 (\d+)')})。★旗の口{g10(r'旗の口 (\d+) 行')}行/旗{g10(r'旗 (\d+) 本')}本(file×名)/file{g10(r'file (\d+) 本\(shell')}本★。既定0|1だけの候補{g10(r'候補のみ\(i 既定 0\|1 だが註も等値比較も無し= 計数/刻/pid の類・員外\) (\d+) 名')}名(計數/刻/pid)は員外。陽性ASW_DISABLE_ESCALATION {g10(r'ASW_DISABLE_ESCALATION = (\d+) 行')}行/陰性ZZ_KM84_NEG 0行rc1。",
 f"[第78弾 納め 4/5・㋑㋒] 讀手{g20(r'讀手\(甲乙丙外\)の行 (\d+)')}行=甲{g20(r'甲 (\d+) /')}乙{g20(r'乙 (\d+) /')}丙{g20(r'丙 (\d+) /')}外{g20(r'外 (\d+)★')}(排他 重なり{g20(r'当たつた行 = (\d+)')})。毒6値×写し器{g30(r'写せた (\d+)')}={g30(r'走 (\d+)')}走中: ★甲{g30(r'甲 讀手 (\d+) 本')}本×6=78走 悉く黙り(0側{g30(r'甲 讀手.*?黙つて 0側 (\d+)')}・1側{g30(r'甲 讀手.*?黙つて 1側 (\d+)')})★。乙は01/+1/␊1を1と讀み・2は黙つて0側・空白のみ声1。",
 f"[第78弾 納め 5/5・㋓㋔] 対照{g40(r'○=(\d+)/')}/{g40(r'○=\d+/(\d+)')}(陽性A=番人付き値2で報せ1・陽性B=乙へabcで声1・陰性は番人付き/裸で同挙動)。既定1の旗3本(NO_IDLE_FULL_READ/PROCESS_TIMEOUT/D3_FAIL_CLOSED)は毒で守りが黙つて外れる側。疵{KZ}(紙㊇)。宣60〜120分⇔實{jitsu:.0f}分。監査はsbでgunshi-macへ。",
]
raw = open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8').read(); un = raw.count('\n  read: false')
ROSTER = sorted(os.path.basename(p)[:-5] for p in os.listdir(M + '/queue/inbox') if p.endswith('.yaml') and not p.startswith('_')); naru = []
if TO not in ROSTER or TO == ME: naru.append('宛先')
if un: naru.append(f'己の箱に未読 {un}')
for i, b in enumerate(letters, 1):
    n2 = subprocess.run(['wc', '-m'], input=b.encode('utf-8'), capture_output=True).stdout.decode().strip()
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if str(len(b)) != n2: naru.append(f'便{i} 二器不一致 {len(b)}/{n2}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if naru: K.kaku(OUT + '/62_letters.txt', f'★門が鳴つた {naru}★\n' + '\n---\n'.join(letters)); sys.exit(1)
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO} / 着手便 {st_id} {st_ts} / 實 {jitsu:.2f} 分(起点= 着手便 timestamp・端点= 此の刻)/ 宣 60〜120 分(幅)']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:2600])
