# -*- coding: utf-8 -*-
"""70 突合(㋘・臺帳の後・員外)―― 專任3 第52弾 km52_report.md を ★納めの後 09:43:13 に初めて讀んだ★ 上で、己の數と定義ごとに突き合はせ、追ひ便 6/7 を出す。
加へて己の丁全(40_tei_all.tsv)から「既定 0 か小文字名(丁閾の外)で數比較器の同行に立つ口」を数へる(專任3 の乙側と己の母數の境を示す為)。"""
import os, sys, re, time, subprocess
B = sys.argv[1]; D = os.path.dirname(B); E = D + '/raw'; OUT = D + '/_after'; sys.path.insert(0, E); import kaki as K
M = '/Users/momizimac/multi-agent-shogun'; ME = 'ashigaru-mac-1'; TO = 'karo-mac'; S = M + '/docs/evidence/km-52-shikii-no-bosuu-wo-kakutei-seyo-20260917/km52_report.md'
import hashlib; ssha = hashlib.sha256(open(S, 'rb').read()).hexdigest()[:16]
rows = [l.rstrip('\n').split('\t') for l in open(E + '/40_tei_all.tsv', encoding='utf-8')][1:]
OPS = re.compile(r'-(lt|le|gt|ge|eq|ne)\b'); outer = [r for r in rows if r[0] == 'disk' and r[6] == '-' and r[5] == '-' and OPS.search(r[8]) and '[' in r[8]]
files = sorted(set(r[1] for r in outer))
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
txt = [f'# 70 突合 / 刻 {koku} / 專任3 紙 {S.split("/docs/")[1]} sha16 {ssha}(★讀んだ刻 09:43:13= 納め 5/5 09:43:06 の後★) / 己の紙 sha16 {hashlib.sha256(open(B + ".md", "rb").read()).hexdigest()[:16]}',
 '## 一致(独立二器で一致 ―― 讀む前に己の數は臺帳に固定済)',
 '  ⑴ 守る名(單位= (file, 環境変数名)・fix_threshold 明示+loop 展開): 專任3 凍結 6dbe09e6 で 22/6 file・disk 23/7 ⇔ 己 HEAD 6ba8fcb2 で 22/6・disk 23/7 ―― ★数も file も一致★(己の器は行を数へた上で名を展開・專任3 は (file,名) を直に数へた= 別の器)。',
 '  ⑵ dasumae:77 DASUMAE_READ_TIMEOUT→SAFE_SIZE_TMO は數比較器の項に立たぬ(timeout の引数のみ): 專任3 差② ⇔ 己 47 の「無 1(C)」―― 一致。',
 '  ⑶ ASW_PHASE は 216/217 で -ge に立つ: 一致。NUDGE_COOLDOWN_SEC/_CODEX/_CLAUDE・MAX_TYPING_SKIP は一跳びの別名で比較器へ: 專任3 疵H の直し ⇔ 己の「経由」―― 一致。',
 '  ⑷ disk の 7 本目= shogun_report_watcher.sh:78(未 commit): 一致。',
 '## 食ひ違ひ ―― どちらが正ではなく「何の定義が違ふか」',
 '  ① ★「20箇所6file が立つ定義」が二つ在る★: 專任3= (file,名) 22 から SAFE_SIZE_TMO(比較へ渡らぬ)と ASW_PHASE(段の番号)を ★判断で除いて★ 20 / 己= 甲′「fix_threshold の語を含む行の総数(定義+呼出+註)」を HEAD で足して 20(4+3+3+3+2+5)・file 6。★單位(行 vs (file,名))と除外の有無が違ふ。二つとも 20/6 に届くゆゑ、裁の定義は未だ一つに閉ぢぬ ―― 委員長が定義を名指すまで「閉」とは書けぬ。★',
 f'  ② ★同じ數「69」が二度出る ―― 別の定義★: 專任3 の 69= 全形(${{NAME:-d}}/${{NAME-d}}/${{NAME:=d}}/裸 $NAME)の素の口 91−22 / 己の 69= ${{NAME:-數}} の内 大文字名∧註除く(既定 0 を含む)。★一致に数へぬ★(同じ語で違ふ物を数へるな)。',
 f'  ③ ★己の「番人無し∧數比較器= 0」は 丁閾(大文字∧既定≥1)の 23 口の内でのみ★。專任3 の乙側 52 口(fail-open 49)は 既定 0 の ${{X:-0}} と裸の $NAME を含み、己の 丁閾 の外。己の 丁全(disk 86 口)で ★丁閾の外(既定 0 か小文字名)かつ同行で數比較器に立つ口= {len(outer)} 口 / {len(files)} file★: ' + ' / '.join(f'{r[1].split("/")[-1]}:{r[2]} {r[3]}' for r in outer) + ' ―― 之は專任3 の測つた側であり、己は数へた丈で毒は当てて居らぬ。',
 '  ④ 凍結点が違ふ: 專任3= 6dbe09e6(08:58 固定)/ 己= HEAD 6ba8fcb2(09:32)+disk。六本の file は両凍結点で sha 同一(專任3 の宣)ゆゑ 22/6 は動かぬ。',
 '  ⑤ 專任3 は python/yaml/plist を歩かず・己も同じ(丁は shell の形のみ)。supervisor→子 python の int() は己が一つ見た丈。',
 '## 委員長へ持つて行ける形(家老が編む) ―― 三行',
 '  1 「20箇所6file」は fix_threshold の語の行数(HEAD)でも (file,名)−2 でも立つ。定義を一つ名指すまで閉ぢぬ。 2 閾(既定≥1)の口 23/6 は番人無し∧數比較器= 0 で閉。 3 状態変数(既定 0・裸 $NAME)の口は專任3 の 49 が開いて居る ―― 之が次の弾の的。']
K.kaku(OUT + '/70_tsukiawase.txt', '\n'.join(txt)); print('\n'.join(txt))
letters = [
 f"[第75弾 追ひ 6/7・㋘突合] 專任3 紙 km52_report.md({ssha})を納め後09:43:13に初讀。★独立二器で一致★=守る名(file,名) 凍結22/6・disk23/7⇔己HEAD22/6・disk23/7、SAFE_SIZE_TMO比較無、ASW_PHASE 216/217、NUDGE一跳び、7本目shogun_report:78。食ひ違ひ①20/6が立つ定義が二つ=專任3(file,名)22−2(判断除外)/己 甲′語の総行HEAD20。★單位と除外が違ふ・裁は未だ閉ぢぬ★。",
 f"[第75弾 追ひ 7/7・㋘續] ②「69」が二度出るが別定義(專任3=全形の素の口91−22/己=大文字∧註除く∧既定0含む)★一致に数へぬ★。③己の「番人無し∧數比較器=0」は丁閾(既定≥1)23口の内のみ。專任3乙側52(fail-open49)は既定0・裸$NAMEで己の外。己の丁全で丁閾外∧同行數比較={len(outer)}口/{len(files)}file(_after/70)。∴委員長へ三行=定義未閉/閾23口は閉/状態変数49は開。",
]
raw = open(M + f'/queue/inbox/{ME}.yaml', encoding='utf-8').read(); un = raw.count('\n  read: false'); naru = []
if un: naru.append(f'己の箱に未読 {un}')
for i, b in enumerate(letters, 6):
    if not (40 <= len(b) <= 300): naru.append(f'便{i} 字数 {len(b)}')
    if '?' in b: naru.append(f'便{i} 引けぬ數')
    if subprocess.run(['python3', '-B', os.path.expanduser('~/bin/deferral_gate.py')], input=b.encode('utf-8'), capture_output=True).returncode == 10: naru.append(f'便{i} 先送り語')
print('字数', [len(b) for b in letters], '門', naru or '通(0 鳴)')
if naru: K.kaku(OUT + '/72_letters.txt', f'★門が鳴つた {naru}★\n' + '\n---\n'.join(letters)); sys.exit(1)
out = [f'# 72 追ひ便 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 便 2 / 字数 {[len(b) for b in letters]} / 宛 {TO}']
for i, b in enumerate(letters, 6):
    p = subprocess.run(['bash', M + '/scripts/inbox_write.sh', TO, b, 'report_received', ME], capture_output=True, text=True, cwd=M)
    box = open(M + f'/queue/inbox/{TO}.yaml', encoding='utf-8').read() + open(M + f'/queue/inbox/_archive/{TO}_pruned.yaml', encoding='utf-8').read()
    ids = [re.search(r'\n  id: (\S+)', q).group(1) for q in box.split('\n- content: ')[1:] if b[:40] in q and re.search(r'\n  id: (\S+)', q)]
    out.append(f'便{i} rc {p.returncode} / 第八の番人= {len(ids)} 本 {ids}\n{b}')
K.kaku(OUT + '/72_letters.txt', '\n'.join(out)); print('\n'.join(out))
