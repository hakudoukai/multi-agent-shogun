# -*- coding: utf-8 -*-
"""07 中間便(家老便 msg_20260917_085831 の課= 09:50 迄・㋐ の母數と器の名・零の四札・宣の式)―― 各便 300 字の條・門(字数・?・先送り語)を通してから inbox_write。id は箱+archive から引く。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
letters = [
 f"[第74弾 中間 1/3・㋐母數] 凍結点6dbe09e6。四器の_th_say行を讀む器=★0本★。器=git grep -n -E(凍結版 scripts+.claude)/~/bin .sh .py 30本/Mac起動器boot-mac-fleet.sh 160行。其の内byte切り=0本(母數0=讀む器が無い)。四器の中の切り4本(watcher:439,744 watchdog:223 health:361)は_th_say行に非ず・閾の値に非ず。",
 f"[第74弾 中間 2/3・零の四札] 陽性対照=同じgit grepがinbox_watcher.shを7 file拾ふ・同じ讀み方が~/binで queue/inboxを3/30拾ふ・切りの形はscripts全体で2 file(pane_identity 3・shogun_report_watcher 1)/根と深さ=凍結版樹・~/bin深さ1・起動器1本/rc=零のgrepは1/刻={koku[:19]}。走るwatcherは旧inode(fd255 20564860)ゆゑlogに「閾」0(43378行・陽性unread 17196)。",
 f"[第74弾 中間 3/3・宣の式] 11:00=着手08:56+124分。式=器8本×10分/器=80分(00起/05控/10讀み手/20切り/30番人/40捕り/50臺帳/60門)+紙25分+便19分(3便×字数門)。根=第73弾は16本を29.5分(1.85分/器)だが本弾は器毎に凍結点のgit show讀みが要る故10分/器に置いた。今09:1x 生6本済・残=紙・臺帳・門・便。",
]
naru = []
for i, b in enumerate(letters, 1):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    q = subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True)
    if q.returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if naru: K.kaku(D + '/raw/07_chukan.txt', f'★門が鳴つた {naru}★\n' + '\n---\n'.join(letters)); sys.exit(1)
out = [f'# 07 中間便 / 刻 {koku} / 便 {len(letters)} / 字数 {[len(b) for b in letters]}']
for i, b in enumerate(letters, 1):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    raw = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read() + open(M + f'/queue/inbox/_archive/{TO}_pruned.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in raw.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} inbox_write rc {p.returncode} / 第八の番人(箱+archive で胴の頭 40 字を引く)= {len(ids)} 本 {ids} / 胴:\n{b}')
K.kaku(D + '/raw/07_chukan.txt', '\n'.join(out)); print('\n'.join(out)[:900])
