# -*- coding: utf-8 -*-
"""㋒ 對照の器 42(第67弾・★二走目★ = 40 に ctime を足し L1 を錠→歩哨の順に直し L3 を足した。一走目(ctime 無・P6 黙・L1 錠→歩哨の逆順)は 42_taishou.first.* に残す)―― 陽性 7 形・陰性 4 形・零 1 形・錠 2 形を raw/taishou/<id>/ に實時間で建て、★悉く 40 を subprocess で通す★(手前で折り返す抜け道無し)。各形で 40 の出目から 母數・後・疵・rc を regex で引き、母數 0 の陽性/陰性は「零長の比較 = 偽の通過」として ★不★ にする。期待: P* rc 1 / N* rc 0 / Z1 rc 2 / L1 PermissionError / L2 書けた。rc = 0 if 悉く合 else 1。fixture は條②③④を通る形(LF 一つ・末尾空白 0・CR 0・0byte 無)で書く ―― 臺帳に載る故。"""
import os, sys, subprocess, re, time, shutil, stat as S
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
BASE = E + '/taishou'; F40 = E + '/40_mon_no_ato.py'
if os.path.isdir(BASE):
    for d, ds, fs in os.walk(BASE):
        os.chmod(d, 0o755)
        for f in fs: os.chmod(os.path.join(d, f), 0o644)
    shutil.rmtree(BASE)
def w(p, s='x\n', mode='w'):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode, encoding='utf-8', newline='\n') as fh: fh.write(s)
def hosho(d): w(d + '/hosho.txt', '歩哨 ―― 門の直前の一行\n'); return os.stat(d + '/hosho.txt').st_mtime_ns
def sengen(d, pats): w(d + '/sengen.txt', '# 員外 ㊂ 門の後に生れる物: ' + ' / '.join(pats) + '\n')
def same_sec_pair(d, first, second, want_second_later):
    """同秒に二つ書く ―― want_second_later=True なら first を先に(N2 は file→歩哨・P4 は歩哨→file)。同秒に収まるまで書き直す(上限 60)。"""
    for i in range(60):
        w(first, 'x\n'); w(second, 'x\n')
        a, b = os.stat(first).st_mtime_ns, os.stat(second).st_mtime_ns
        if a // 10**9 == b // 10**9 and b > a: return i + 1, a, b
    return 0, a, b
forms = []
def form(idx, kind, expect, build, note):
    d = f'{BASE}/{idx}'; root = d + '/root'; os.makedirs(root, exist_ok=True); extra = build(d, root) or ''
    args = ['python3', '-B', F40, root, d + '/hosho.txt', d + '/sengen.txt' if os.path.isfile(d + '/sengen.txt') else '-', d + '/out', '40_' + idx] + (['--probe'] if kind == 'L' else [])
    p = subprocess.run(args, capture_output=True, text=True); t = p.stdout
    mu = re.search(r'母數 通常 file (\d+)', t); at = re.search(r'## 後 (\d+) 本', t); kz = re.search(r'疵\) (\d+) 本', t); pr = re.search(r'## P0 錠の證: (.*)', t)
    mu = int(mu.group(1)) if mu else -1; at = int(at.group(1)) if at else -1; kz = int(kz.group(1)) if kz else -1
    if kind == 'L': ok = (pr is not None) and (expect in pr.group(1))
    elif kind == 'Z': ok = p.returncode == expect
    else: ok = p.returncode == expect and mu > 0
    forms.append((idx, kind, note, expect if kind != 'L' else expect, p.returncode, mu, at, kz, '合' if ok else '★不★', (pr.group(1)[:60] if pr else '') + (' ' + extra if extra else '')))
# 陽性
form('P1', 'P', 1, lambda d, r: (w(r + '/a.txt'), w(r + '/b.txt'), hosho(d), w(r + '/c.txt')) and '', '新 file を歩哨の後に書く')
form('P2', 'P', 1, lambda d, r: (w(r + '/a.txt'), w(r + '/b.txt'), hosho(d), w(r + '/a.txt', 'y\n', 'a')) and '', '既存 a.txt へ追記(birth 前・mtime 後)')
form('P3', 'P', 1, lambda d, r: (w(r + '/a.txt'), w(r + '/b.txt'), hosho(d), os.utime(r + '/a.txt', None)) and '', 'touch(中身同・mtime のみ後)')
def p4(d, r):
    w(r + '/a.txt'); n, a, b = same_sec_pair(d, d + '/hosho.txt', r + '/c.txt', True); return f'同秒 {"成" if n else "★不成★"}(試行{n}) 歩哨 {a} file {b} 差 {(b - a) / 1e6:.3f}ms'
form('P4', 'P', 1, p4, '★同秒の後 ns★(66 の穴 = 秒>秒 が隠す形)')
form('P5', 'P', 1, lambda d, r: (w(r + '/a.txt'), hosho(d), w(r + '/sub/d.txt')) and '', '新 dir + file を後に')
def p6(d, r):
    w(r + '/a.txt'); A = hosho(d); w(r + '/e.txt'); os.utime(r + '/e.txt', ns=(A - 10**9, A - 10**9)); return f'e.txt mtime を歩哨-1s へ戻した(birth は後)'
form('P6', 'P', 1, p6, 'utime で mtime を前へ戻した新 file(birth が後)')
form('P7', 'P', 1, lambda d, r: (w(r + '/a.txt'), sengen(d, ['root/g_*.txt']), hosho(d), w(r + '/g_mon.txt'), w(r + '/h.txt')) and '', '宣に在る名(g_mon)と無い名(h)が共に後 → h で鳴る')
# 陰性
form('N1', 'N', 0, lambda d, r: (w(r + '/a.txt'), w(r + '/b.txt'), w(r + '/c.txt'), hosho(d)) and '', '悉く歩哨の前')
def n2(d, r):
    n, a, b = same_sec_pair(d, r + '/a.txt', d + '/hosho.txt', True); return f'同秒 {"成" if n else "★不成★"}(試行{n}) file {a} 歩哨 {b} 差 {(b - a) / 1e6:.3f}ms'
form('N2', 'N', 0, n2, '★同秒の前 ns★(file → 歩哨 が同じ秒)')
form('N3', 'N', 0, lambda d, r: (w(r + '/a.txt'), sengen(d, ['root/g_*.txt', 'mon/']), hosho(d), w(r + '/g_mon.txt'), w(r + '/mon/m.out')) and '', '宣に在る名だけが後(g_mon・mon/)')
form('N4', 'N', 0, lambda d, r: (w(r + '/x/y/z/f.txt'), w(r + '/x/g.txt'), w(r + '/h.txt', 'h\n'), w(r + '/x/y/i.txt'), hosho(d)) and '', '深い dir・悉く前')
# 零
form('Z1', 'Z', 2, lambda d, r: hosho(d) and '', '空の根(歩哨のみ) → rc 2 = 歩いて居らぬ')
# 錠
def lock(r):
    for q in os.listdir(r): os.chmod(os.path.join(r, q), 0o444)
    os.chmod(r, 0o555)
def l1(d, r):
    w(r + '/a.txt'); lock(r); hosho(d); return '錠 → 歩哨 の順(二走目)/ 根 0555 file 0444'
form('L1', 'L', 'PermissionError', l1, '錠を歩哨の★前★に掛け --probe で 1 byte 書く → PermissionError・鳴らぬ')
def l3(d, r):
    w(r + '/a.txt'); lock(r); hosho(d); os.chmod(r, 0o755); os.chmod(r + '/a.txt', 0o644); return '錠 → 歩哨 → ★錠を外す★(chmod は ctime を動かす)'
form('L3', 'P', 1, l3, '歩哨の後に錠を外す → ctime で鳴る(外した事自体が捕へられる)')
form('L2', 'L', '書けた', lambda d, r: (w(r + '/a.txt'), hosho(d)) and '錠 無', '錠なしで --probe → 書けた(probe が本物である證)')
hdr = ('id', '種', '形', '期待', '實rc', '母數', '後', '疵', '判', '註')
K.kaku_tsv(E + '/42_taishou.tsv', forms, hdr)
bad = [f for f in forms if f[8] != '合']
out = [f'# 42 對照 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 形 {len(forms)}(陽 7・陰 4・零 1・錠 3 = L1 錠→歩哨 / L2 錠無 / L3 錠を外す)/ 悉く 40 を subprocess で通した / 合 {len(forms) - len(bad)} 不 {len(bad)} / 陰性で鳴つた(騒音) {sum(1 for f in forms if f[1] == "N" and f[4] == 1)} / 陽性で黙つた {sum(1 for f in forms if f[1] == "P" and f[4] != 1)} / 母數 0 の陽陰 {sum(1 for f in forms if f[1] in "PN" and f[5] <= 0)}',
       '| ' + ' | '.join(hdr) + ' |'] + ['| ' + ' | '.join(str(x) for x in f) + ' |' for f in forms]
K.kaku(E + '/42_taishou.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if not bad else 1)
