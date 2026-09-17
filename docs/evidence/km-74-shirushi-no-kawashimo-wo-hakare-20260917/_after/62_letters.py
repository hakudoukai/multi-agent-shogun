# -*- coding: utf-8 -*-
"""納め便の器 62(第74弾・_after に置く= 臺帳の後の器・員外)―― 四便・各 300 字の條・門(宛先/未讀/字数/?/先送り語)を通してから inbox_write。id は箱+archive の胴の頭 40 字で引く。"""
import os, sys, re, time, subprocess, hashlib
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; KM = os.path.basename(D)
sha16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
P_, MN, G = sha16(B + '.md'), sha16(B + '_manifest.txt'), sha16(B + '_gate.txt'); PB = os.path.getsize(B + '.md'); PL = open(B + '.md', encoding='utf-8').read().count('\n')
rcs = open(OUT + '/60_gate_rcs.txt', encoding='utf-8').read(); g = {k: re.search(k + r'.*rc (\d+)', rcs).group(1) for k in ('selftest', 'main', 'nobase')}
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
letters = [
 f"[第74弾 納め 1/5・束] 束 docs/evidence/{KM}/ 紙 {P_}({PB}B・{PL}行)/ 臺帳 {MN}(項18・append.py・基点=束内相対)/ 門控 {G}(員外)。凍結点6dbe09e6・四器 disk一致4/4・scripts/へ0字・箱へ書かず(既讀印は家老便3通のみ)。",
 f"[第74弾 納め 2/5・門] selftest rc{g['selftest']}・main rc{g['main']}(18本・byte和54332・條①一致18)・nobase rc{g['nobase']}(基点無し・落ちて正)。員外(臺帳の頭でなく此処と紙㊆⑹で宣す)=門控・_after/*・raw/50_build_manifest.*・raw/50_sengen.txt・raw/60_gate_run.py(臺帳の後に書いた器)。",
 f"[第74弾 納め 3/5・㋐] _th_say行の下流のbyte切り=★現に0本★。讀む器=0(凍結版repo git grep 0行・~/bin 0/30・起動器は書き手のみ)。四札=中間便2/3の通り。四器内の切り4本(watcher:439,744/watchdog:223/health:361)は閾の値に非ず。∴己の㋓(18/66)は「切れば割れる」の實證で「現に切る器」の證に非ず=潜在。人の端末とClaudeは器の外(母數外)。",
 f"[第74弾 納め 4/5・㋑㋒] ㋑印が値に戻る路=0(四器で_th_sayを$( )で捕る行0・logを讀む器0)。走るwatcherは旧inode故logに閾0(未だ刷られず)。㋒番人=四器の倒す行20/6fileで32(裁の20と6は同時に立たず・二数併記)。㋔は四器の値刷り4行(164/115/125/71)で乙門が閉ぢた。★乙が未だ当たらぬ2箇所=dasumae_gate:59・gate4:92(「${{raw}}」・乙置換0・乙門0)を先に★。",
 f"[第74弾 納め 5/5・疵・宣] 疵=着手便744字(條越え)→以後300字以内に割つた/20の結び「2本」を器の4に直した/05・30の器が倒れ直した。宣11:00⇔實{koku[11:19]}(式=器8本×10分+紙25+便19)。09:08の便(差出 from: karo・karo-macに非ず)は中間便3通(09:07:38)が既に答へ、本弾は止まつて居らぬ。監査代送は家老に乞ふ。",
]
raw = open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8').read(); un = raw.count('  read: false')
ROSTER = sorted(os.path.basename(p)[:-5] for p in os.listdir(M + '/queue/inbox') if p.endswith('.yaml') and not p.startswith('_')); naru = []
if TO not in ROSTER or TO == ME: naru.append('宛先')
if un: naru.append(f'己の箱に未読 {un}')
for i, b in enumerate(letters, 1):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if naru: K.kaku(OUT + '/62_letters.txt', f'★門が鳴つた {naru}★\n' + '\n---\n'.join(letters)); sys.exit(1)
out = [f'# 62 納め便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]} / 宛 {TO}']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read() + open(M + f'/queue/inbox/_archive/{TO}_pruned.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/62_letters.txt', '\n'.join(out)); print('\n'.join(out)[:1400])
