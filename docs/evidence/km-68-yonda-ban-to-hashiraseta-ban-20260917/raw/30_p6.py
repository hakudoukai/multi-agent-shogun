# -*- coding: utf-8 -*-
"""㋑ P6 の始末 30(第68弾)―― 同じ fixture に 則一(41・mtime|birth)と 則二(40・mtime|birth|ctime)を掛け、合否が反転するかを見る。
形: P6(歩哨の後に新 file を書き utime で mtime を歩哨−1s へ戻す)/ L1a(歩哨→錠 = 第67弾 一走目の順)/ L1b(錠→歩哨 = 二走目の順)/ N1(悉く前・陰性)/ P1(新 file 後・陽性)。
各 fixture は一度だけ建て、41 → 40 の順に ★讀むのみ★ で掛ける(--probe 無・根へ書かぬ)。期待: P6 41→rc0(黙) 40→rc1(鳴)= 反転 / L1a 41→0 40→1(錠自身が鳴る)/ L1b 41→0 40→0 / N1 0,0 / P1 1,1。
∴ 「ctime を足した」が P6 を救ひ、「錠を歩哨の前へ」が ctime の副作用(L1a)を消した ―― 二つの変更は別の物を救つた。出目 raw/30_p6.txt(+ raw/p6/<形>/out/)。"""
import os, sys, subprocess, re, time, shutil
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
BASE = E + '/p6'; F40 = E + '/40_mon_no_ato.py'; F41 = E + '/41_mon_no_ato_rule1.py'
if os.path.isdir(BASE):
    for d, ds, fs in os.walk(BASE):
        os.chmod(d, 0o755)
        for f in fs: os.chmod(os.path.join(d, f), 0o644)
    shutil.rmtree(BASE)
def w(p, s='x\n'):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as fh: fh.write(s)
def hosho(d): w(d + '/hosho.txt', '歩哨 ―― 門の直前の一行\n'); return os.stat(d + '/hosho.txt').st_mtime_ns
def lock(r):
    for q in os.listdir(r): os.chmod(os.path.join(r, q), 0o444)
    os.chmod(r, 0o555)
def stat_fb(p): return subprocess.run(['stat', '-f', '%Fm %FB %Fc', p], capture_output=True, text=True).stdout.strip()
def p6(d, r):
    w(r + '/a.txt'); A = hosho(d); w(r + '/e.txt'); os.utime(r + '/e.txt', ns=(A - 10**9, A - 10**9))
    return f'e.txt: 歩哨 {A} / 戻した後の stat(mtime birth ctime)= {stat_fb(r + "/e.txt")} ―― birth が mtime へ締められて居るか(macOS APFS)'
def l1a(d, r): w(r + '/a.txt'); hosho(d); lock(r); return '歩哨 → 錠(第67弾 一走目の順)/ chmod は ctime を動かす'
def l1b(d, r): w(r + '/a.txt'); lock(r); hosho(d); return '錠 → 歩哨(第67弾 二走目の順)'
def n1(d, r): w(r + '/a.txt'); w(r + '/b.txt'); hosho(d); return '陰性'
def p1(d, r): w(r + '/a.txt'); hosho(d); w(r + '/c.txt'); return '陽性(新 file 後)'
forms = [('P6', 1, 0, 1, p6, 'utime で mtime を前へ戻した新 file(birth が後)'), ('L1a', 0, 0, 1, l1a, '歩哨→錠(一走目の順)'), ('L1b', 0, 0, 0, l1b, '錠→歩哨(二走目の順)'), ('N1', 0, 0, 0, n1, '悉く前'), ('P1', 1, 1, 1, p1, '新 file を後に')]
rows = []; notes = []
for idx, want_true, want41, want40, build, note in forms:
    d = f'{BASE}/{idx}'; r = d + '/root'; os.makedirs(r, exist_ok=True); extra = build(d, r)
    res = {}
    for tag, F in (('41', F41), ('40', F40)):
        p = subprocess.run(['python3', '-B', F, r, d + '/hosho.txt', '-', d + '/out', f'{tag}_{idx}'], capture_output=True, text=True)
        mu = re.search(r'母數 通常 file (\d+)', p.stdout); at = re.search(r'## 後 (\d+) 本', p.stdout); kz = re.search(r'疵\) (\d+) 本', p.stdout); nan = re.findall(r'何で後=(\w*)', p.stdout)
        res[tag] = (p.returncode, int(mu.group(1)) if mu else -1, int(at.group(1)) if at else -1, int(kz.group(1)) if kz else -1, ','.join(nan) or '-', p.stderr.strip()[:120])
    ok = res['41'][0] == want41 and res['40'][0] == want40 and res['41'][1] > 0 and res['40'][1] > 0
    rows.append((idx, note, want_true, want41, res['41'][0], res['41'][3], res['41'][4], want40, res['40'][0], res['40'][3], res['40'][4], '反転' if res['41'][0] != res['40'][0] else '同じ', '合' if ok else '★不★', res['41'][1]))
    notes.append(f'  {idx}: {extra}' + (f' / 41 stderr {res["41"][5]}' if res['41'][5] else '') + (f' / 40 stderr {res["40"][5]}' if res['40'][5] else ''))
hdr = ('id', '形', '真の期待', '41 期待', '41 rc', '41 疵', '41 何で後', '40 期待', '40 rc', '40 疵', '40 何で後', '41→40', '判', '母數')
K.kaku_tsv(E + '/30_p6.tsv', rows, hdr)
bad = [r for r in rows if r[12] != '合']; p6r = [r for r in rows if r[0] == 'P6'][0]; l1a = [r for r in rows if r[0] == 'L1a'][0]; l1b = [r for r in rows if r[0] == 'L1b'][0]
out = [f'# 30 ㋑ P6 の始末 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 形 {len(rows)} / 各 fixture を一度建て 41(則一・mtime|birth)→40(則二・mtime|birth|ctime)の順に讀むのみで掛けた(--probe 無)/ 合 {len(rows) - len(bad)} 不 {len(bad)}',
       '| ' + ' | '.join(hdr) + ' |'] + ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows] + ['## fixture の註'] + notes + [
       f'## ⑴ P6 を二走目の則で走らせ直す: 41 rc {p6r[4]} → 40 rc {p6r[8]} = ★{p6r[11]}★(41 何で後 {p6r[6]} / 40 何で後 {p6r[10]})',
       f'## ⑵ 何が救つたか: P6 は 40 で「何で後={p6r[10]}」―― ' + ('★c(ctime)だけ★で後に入つた。m も b も刻より前(macOS は utime で mtime を birth より前へ戻すと birth も締める)。∴ P6 を救つたのは ctime の追加であり、錠の順ではない。' if p6r[10] == 'c' else f'★c だけではない({p6r[10]})★ ―― 見立てと違ふ。何が救つたかは此の列を讀め。'),
       f'   錠の順が救つた物: L1a(歩哨→錠)41 rc {l1a[4]} / 40 rc {l1a[8]}(錠自身が ctime で鳴る)‖ L1b(錠→歩哨)41 rc {l1b[4]} / 40 rc {l1b[8]}。∴ 「錠を歩哨の前へ」は ★ctime を足した事の副作用(錠が鳴る)を消す★ 為の変更であり、P6 とは別の物を救つた。',
       '## ⑶ 変更前後の則の逐語 = raw/30_rule_verbatim.txt / 器の diff -u = raw/30_rule_diff.txt(31 が作る)',
       f'# 結 30: {"★P6 は反転した(則一 黙 → 則二 鳴)・ctime が救ひ・錠の順は L1a を救つた★" if not bad and p6r[11] == "反転" else "★期待と違ふ形が在る ―― 上の表の ★不★ を讀め★"}']
K.kaku(E + '/30_p6.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if not bad else 1)
