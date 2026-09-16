# -*- coding: utf-8 -*-
"""捕へ器 40(第67弾・㋐)―― 門の後に根へ生れた/触られた物を ★ns の刻★ で捕へる。
argv = <歩き根> <歩哨file> <宣file or -> <出力dir> <名> [--probe]
刻 = 歩哨 file の st_mtime_ns(os.stat・kernel の値・stat -f %Fm と同じ ―― 両方を印字して一致を示す)。
後 = mtime_ns > 刻 ★又は★ birth_ns(stat -f %FB・生れた刻)> 刻 ★又は★ ctime_ns > 刻 / 同 = mtime_ns == 刻 / 前 = 其の他。
★則を一つ変へた(一走目の後・42 P6 が黙つた故)★: 一走目は ctime を使はなかつた(chmod/rename が動かす故)。然し macOS は utime で mtime を birth より前へ戻すと birth も其処へ締める ∴ 前へ戻された新 file は mtime/birth では見えず、ctime(utime も今へ動かす)でしか見えぬ。∴ ctime を足し、錠(chmod)は歩哨の ★前★ に掛ける順へ変へた(錠が後なら錠自身が鳴る = L1 一走目の形)。一走目の出目は *.first.* に残す。
宣 = 宣 file の行から取つた fnmatch 型(brace {a,b} 展開・(…) は落とす・<束> は *・末尾 / は配下悉く)。★疵 = 後 ∧ 宣に無い★。
rc: 2 = 母數 0(歩いて居らぬ・通でも鳴でもない)/ 1 = 疵 ≥ 1(鳴)/ 0 = 疵 0(通)。--probe = 根へ 1 byte 書けるかを試す(錠の證・己の束のみ)。
讀むのみ ―― 己の出目は <出力dir>/<名>.txt 一本(根の外に置け)。"""
import os, sys, re, time, stat, fnmatch, subprocess, itertools
root, hosho, sengen, outd, name = sys.argv[1:6]; PROBE = '--probe' in sys.argv[6:]
E = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, E); import kaki as K
root = os.path.abspath(root); now = time.strftime('%Y-%m-%dT%H:%M:%S%z')
def brace(t):
    m = re.search(r'\{([^{}]*)\}', t)
    if not m: return [t]
    return [x for alt in m.group(1).split(',') for x in brace(t[:m.start()] + alt + t[m.end():])]
pats = []
if sengen != '-':
    for ln in open(sengen, encoding='utf-8', errors='replace'):
        if not re.search(r'㊂|門の後|post', ln): continue
        ln = re.sub(r'\([^()]*\)', '', ln); ln = re.sub(r'（[^（）]*）', '', ln); ln = ln.split(':', 1)[-1] if '門の後' in ln.split(':', 1)[0] else ln
        for tok in re.split(r'\s+/\s+|\s+', ln.strip()):
            tok = tok.strip().rstrip(':').replace('<束>', '*')
            if not tok or tok.startswith('#') or not re.search(r'[A-Za-z0-9_]', tok) or re.search(r'[぀-ヿ一-鿿]', tok): continue
            pats += brace(tok)
pats = sorted(set(pats))
anc = [root] + [os.path.dirname(root)] + [os.path.dirname(os.path.dirname(root))]
def declared(p):
    cands = [os.path.relpath(p, a) for a in anc]
    for pat in pats:
        for c in cands:
            if pat.endswith('/') and (c.startswith(pat) or ('/' + c).startswith('/' + pat)): return pat
            if fnmatch.fnmatchcase(c, pat) or fnmatch.fnmatchcase(os.path.basename(c), pat) and '/' not in pat: return pat
    return None
hs = os.stat(hosho); A = hs.st_mtime_ns
fm = subprocess.run(['stat', '-f', '%Fm', hosho], capture_output=True, text=True).stdout.strip()
A_stat = int(fm.replace('.', '')) if re.fullmatch(r'\d+\.\d{9}', fm) else None
reg = []; nonreg = 0; walked = 0
for d, ds, fs in os.walk(root):
    for f in fs:
        p = os.path.join(d, f); st = os.lstat(p); walked += 1
        if not stat.S_ISREG(st.st_mode): nonreg += 1; continue
        reg.append((p, st))
births = {}
clean = [p for p, _ in reg if '\n' not in p and '\t' not in p]
for i in range(0, len(clean), 200):
    ch = clean[i:i + 200]; r = subprocess.run(['stat', '-f', '%FB%t%N'] + ch, capture_output=True, text=True)
    for ln in r.stdout.split('\n'):
        if '\t' in ln:
            b, q = ln.split('\t', 1)
            if re.fullmatch(r'\d+\.\d{9}', b): births[q] = int(b.replace('.', ''))
rows = []
for p, st in reg:
    rel = os.path.relpath(p, root); mns = st.st_mtime_ns; bns = births.get(p); bsrc = 'FB'
    if bns is None: bns = int(round(getattr(st, 'st_birthtime', st.st_mtime) * 1e9)); bsrc = 'py~'
    cns = st.st_ctime_ns; later = mns > A or bns > A or cns > A; same = (not later) and mns == A
    k = '後' if later else ('同' if same else '前'); dec = declared(p) if later else None
    rows.append((rel, st.st_size, mns, bns, bsrc, k, dec, cns))
ato = [r for r in rows if r[5] == '後']; ato_in = [r for r in ato if r[6]]; ato_out = [r for r in ato if not r[6]]; same = [r for r in rows if r[5] == '同']; mae = [r for r in rows if r[5] == '前']
sec_after = [r for r in rows if r[2] // 10**9 > A // 10**9]
hidden = [r for r in ato if r[2] // 10**9 <= A // 10**9]
def T(ns): return time.strftime('%H:%M:%S', time.localtime(ns / 1e9)) + '.%09d' % (ns % 10**9)
out = [f'# 40 捕へ器(二走目・mtime|birth|ctime) / {name} / 刻 {now} / 歩き根 {root} / 歩哨 {hosho} / 刻(歩哨 mtime_ns) {A} = {T(A)} / stat -f %Fm {fm} → 一致 {A_stat == A} / 宣 {sengen}(型 {len(pats)}) / probe {PROBE}',
       f'## 母數 通常 file {len(reg)}(歩いた {walked}・非通常 {nonreg})/ byte 和 {sum(r[1] for r in rows)} / birth の出處 FB {sum(1 for r in rows if r[4] == "FB")} py~ {sum(1 for r in rows if r[4] == "py~")}',
       f'## 後 {len(ato)} 本 {sum(r[1] for r in ato)} B = 後∧宣に在る {len(ato_in)} 本 {sum(r[1] for r in ato_in)} B + ★後∧宣に無い(疵) {len(ato_out)} 本 {sum(r[1] for r in ato_out)} B★ / 同 {len(same)} / 前 {len(mae)} / 和 {len(ato) + len(same) + len(mae)} = 母數 {len(reg)} 差 {len(reg) - len(ato) - len(same) - len(mae)}',
       f'## 比較・秒>秒(66 の定義)なら 後 {len(sec_after)} 本 {sum(r[1] for r in sec_after)} B ―― ns が捕へて 秒>秒 が隠す物 {len(hidden)} 本 {sum(r[1] for r in hidden)} B: {[r[0] for r in hidden]}']
if pats: out.append('## 宣の型: ' + ' | '.join(pats))
for r in sorted(ato, key=lambda r: r[2]): out.append(f'  後{"・宣" if r[6] else "・★無★"} {r[0]} {r[1]}B mtime {T(r[2])}(+{(r[2] - A) / 1e6:.3f}ms) birth {T(r[3])}({r[4]}) ctime {T(r[7])} 何で後={"m" if r[2] > A else ""}{"b" if r[3] > A else ""}{"c" if r[7] > A else ""} {"宣=" + r[6] if r[6] else ""}')
for r in same: out.append(f'  同 {r[0]} {r[1]}B mtime == 刻')
if not ato: out.append('  (後 空 ―― 歩哨より後に此の根へ生れた/触られた物は一本も無い)')
if PROBE:
    q = os.path.join(root, '.40_probe');
    try:
        with open(q, 'wb') as fh: fh.write(b'x')
        os.remove(q); out.append('## P0 錠の證: 根へ 1 byte ★書けた★(錠が掛かつて居らぬ・書いた後に消した ―― 之は書込みである)'); probe_ok = False
    except PermissionError as e: out.append(f'## P0 錠の證: 根へ 1 byte 書けぬ = PermissionError({e.errno}) ★出来なく なつて居る★'); probe_ok = True
    except OSError as e: out.append(f'## P0 錠の證: 別の OSError {e.__class__.__name__}({e.errno})'); probe_ok = False
rc = 2 if not reg else (1 if ato_out else 0)
out.append(f'# 結 {name}: rc {rc} = ' + {2: '★母數 0・歩いて居らぬ(通でも鳴でもない)★', 1: f'★鳴 ―― 門の後に根へ書いた物 {len(ato_out)} 本(宣に無い)★', 0: f'通 ―― 後 {len(ato)} は悉く宣に在る・疵 0'}[rc])
os.makedirs(outd, exist_ok=True); K.kaku(os.path.join(outd, name + '.txt'), '\n'.join(out)); print('\n'.join(out)); sys.exit(rc)
