# -*- coding: utf-8 -*-
"""納め便の器 62(第77弾 km-81b・_after= 臺帳の後の器・員外)―― 五便・各 300 字の條・門(宛先/未讀/字数 二器/?/先送り語)を通してから inbox_write。id は箱の胴の頭 40 字で引く(第八の番人)。宣⇔實は着手便の timestamp(箱の値)を起点に測る。"""
import os, sys, re, time, subprocess, hashlib
D = sys.argv[1]; E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}; LOG = re.search(r'門控 (\S+)', rcs).group(1)
P_, MN, G = sha16(D + '/README.md'), sha16(D + '/MANIFEST.txt'), sha16(D + '/' + LOG); PB = os.path.getsize(D + '/README.md'); PL = open(D + '/README.md', encoding='utf-8').read().count('\n'); NI = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path='))
me = open(OUT + '/60_gate_main.err', encoding='utf-8').read(); bs = re.search(r'byte和[ =]*(\d+)', me); bs = bs.group(1) if bs else '?'
st = open(E + '/01_letter.txt', encoding='utf-8').read(); st_id, st_ts = re.search(r"\('(msg_\S+)', '([^']+)'\)", st).groups()
KZ = sum(1 for l in open(D + '/README.md', encoding='utf-8') if re.match(r'^- ★?疵', l))
FR = sum(1 for l in open(D + '/MANIFEST.txt', encoding='utf-8') if l.startswith('path=') and re.search(r'\.(first|second) ', l))
U = open(E + '/10_uke.txt', encoding='utf-8').read(); g10 = lambda pat: re.search(pat, U).group(1)
KO, OT, OTN = g10(r'disk: 甲 `\$\{NAME:-既定\}` の字面 (\d+) 口'), g10(r'disk: 乙 外から値が入る変数 (\d+) 口'), g10(r'disk: 乙 外から値が入る変数 \d+ 口・(\d+) 名'); HN = g10(r'disk: 丙 .*?口・(\d+) 名'); MC = g10(r'★陽性対照★ scripts/inbox_watcher.sh\(disk\) (\d+) 行')
HK = re.search(r'disk: ㋑ 比較器 (\d+) 件= (.*)', U); HKN, HKD = HK.group(1), re.sub(r'\(\[\[ \]\] 内・算術評価\)', '', HK.group(2)).replace(' / ', '/').replace('正規 =~', '=~')
TL = open(E + '/35_tally.txt', encoding='utf-8').read(); tot = dict(re.findall(r'(刷つて別枝|刷つて通る|鳴つて止まる|黙つて別枝|黙つて通る)\([^)]*\) (\d+)', TL.split('全口の八形 合計: ')[1].split('\n')[0])); WQ = re.search(r'枠の口\(P3 5h \+ P4 7d\)の八形 (\d+) 走★: (.*)', TL); wq = dict(re.findall(r'(刷つて別枝|刷つて通る|鳴つて止まる|黙つて別枝|黙つて通る)\([^)]*\) (\d+)', WQ.group(2))); NS = re.search(r'八形\(10 値\)× P1-P6 の 6 口= (\d+) 走', TL).group(1)
SB = open(E + '/40_sanbun.txt', encoding='utf-8').read(); BO = re.search(r'母數= 甲 (\d+) ∪ 乙 (\d+) = (\d+) 名\(重なり (\d+)', SB); SK = {k: re.search(k + r'[^:]*: (\d+) 名', SB).group(1) for k in ('閾', '旗', '状態変数')}
WA = re.search(r'三類の和 (\d+) (= 母數 \d+ ★一致★|★≠[^★]*★)', SB)
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); t0 = time.mktime(time.strptime(st_ts, '%Y-%m-%dT%H:%M:%S')); jitsu = (time.time() - t0) / 60
letters = [
 f"[第77弾 納め 1/5・束] docs/evidence/{KM}/ 紙 README.md {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項{NI})/ 門控 {LOG.split('/')[-1][:-4]} {G}。的 disk=HEAD=main(7f1e0311・582行)。repo 0字・信号0・据ゑず。着手便 {st_id[-8:]}({st_ts[11:19]})。",
 f"[第77弾 納め 2/5・門] selftest rc{g['selftest']}・main rc{g['main']}({NI}本・byte和{bs}・條①一致)・nobase rc{g['nobase']}(基点無し・落ちて正)。員外=MANIFEST.txt・_gate/*・_after/*・raw/50_build_manifest.*・raw/50_sengen.txt。.first/.second({FR}本)は員内(倒れた走を残す)。",
 f"[第77弾 納め 3/5・㋐㋑] 受口=甲`${{X:-}}`{KO}口/乙外来{OT}口{OTN}名/丙函数引数{HN}名。守る表0行rc1(陽性=inbox_watcher {MC}行rc0・陰性ZZ_KM81B_NEG 0行rc1・根=的1本582行深さ0)。閾3名+裸80×2は口を持たぬ。比較器{HKN}={HKD}(數は悉く[[ ]])。[[ ]]は20桁でrc2に非ず黙つて巻く・非ASCIIと疑問符と1e3でrc2・識別子はset -uで鳴つて止まる。",
 f"[第77弾 納め 4/5・㋒㋓] 八形10値×6口={NS}走: 黙つて通る{tot.get('黙つて通る', 0)}・黙つて別枝{tot.get('黙つて別枝', 0)}・鳴つて止まる{tot.get('鳴つて止まる', 0)}・刷つて通る{tot.get('刷つて通る', 0)}・刷つて別枝{tot.get('刷つて別枝', 0)}。★枠の口(5h/7d){WQ.group(1)}走の内{wq.get('黙つて通る', 0)}が黙つてOK(⚠️無)=枠を見ずに走る側が主★。None(python null)はset -uで鳴つて止まる。両対照 7口とも○。三分類: 母數{BO.group(3)}(甲{BO.group(1)}∪乙{BO.group(2)}・重なり{BO.group(4)})=閾{SK['閾']}+旗{SK['旗']}+状態{SK['状態変数']} ★和{WA.group(1)} {'一致' if '一致' in WA.group(2) else '≠母數'}★。閾0は「閾が口を持たぬ」ゆゑ。",
 f"[第77弾 納め 5/5・㋔疵宣] 稼働0(lsof名引き0/ps0・陽性対照はpidで引き3本inode20564860)・呼び手0・disk inode1238425=HEAD=main。★此のMacはbash3.2のみ∴本走はlib/_section18_roles.sh L108 declare -Aでset -uが鳴りrc1(46)・lib三本は在る=着手便の『三本無し』は己のpath誤り★。疵{KZ}(紙㊇)。宣30分⇔實{koku[11:19]}({jitsu:.1f}分)={30/jitsu:.1f}倍。監査はsbでgunshi-macへ。",
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
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO} / 着手便 {st_id} {st_ts} / 實 {jitsu:.2f} 分(起点= 着手便 timestamp・端点= 此の刻)/ 宣 30 分']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:2600])
