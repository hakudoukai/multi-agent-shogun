# -*- coding: utf-8 -*-
"""門の後の實走 96(第68弾・根の外 _after/)―― 捕へ器 40 を ⑴ 根 = raw/(歩哨 _after/00_hosho.txt・宣 無・--probe)⑵ 根 = 束全体(宣 = raw/50_sengen.txt)に掛け、⑶ 臺帳を照合器で当て、⑷ 錠が掛かつて居るかを mode で数へる。期待: ⑴ 後 0・疵 0・P0 PermissionError・rc 0 / ⑵ 後 = _after/ と門控 悉く宣・疵 0・rc 0 / ⑶ rc 0。"""
import os, sys, subprocess, re, time, stat
B = sys.argv[1]; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; MAN = B + '_manifest.txt'; M = '/Users/momizimac/multi-agent-shogun'
sys.path.insert(0, AFT); import kaki as K
F40 = RAW + '/40_mon_no_ato.py'; HOSHO = AFT + '/00_hosho.txt'; SEN = RAW + '/50_sengen.txt'
r1 = subprocess.run(['python3', '-B', F40, RAW, HOSHO, '-', AFT, '96_raw', '--probe'], capture_output=True, text=True)
r2 = subprocess.run(['python3', '-B', F40, D, HOSHO, SEN, AFT, '96_bundle'], capture_output=True, text=True)
v = subprocess.run(['python3', '-B', M + '/scripts/checks/karo_mac_manifest_verify.py', MAN, ''], capture_output=True, text=True, cwd=M)
def g(t, pat, alt='?'): m = re.search(pat, t); return m.group(1) if m else alt
nf = nbad = 0
for d, ds, fs in os.walk(RAW):
    if (os.stat(d).st_mode & 0o777) != 0o555: nbad += 1
    for f in fs:
        q = os.path.join(d, f)
        if stat.S_ISREG(os.lstat(q).st_mode): nf += 1; nbad += (os.stat(q).st_mode & 0o777) != 0o444
j1 = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', v.stdout)
out = [f'# 96 門の後の實走 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 歩哨 {HOSHO} mtime_ns {os.stat(HOSHO).st_mtime_ns}',
       f'## ⑴ 根 raw/(宣 無・--probe): rc {r1.returncode} / 母數 {g(r1.stdout, r"母數 通常 file (\d+)")} / 後 {g(r1.stdout, r"## 後 (\d+) 本")} / ★疵 {g(r1.stdout, r"疵\) (\d+) 本")}★ / P0 {g(r1.stdout, r"## P0 錠の證: (.*)")} / 出目 _after/96_raw.txt',
       f'## ⑵ 根 束全体(宣 = raw/50_sengen.txt): rc {r2.returncode} / 母數 {g(r2.stdout, r"母數 通常 file (\d+)")} / 後 {g(r2.stdout, r"## 後 (\d+) 本")}(宣に在る {g(r2.stdout, r"後∧宣に在る (\d+) 本")})/ ★疵 {g(r2.stdout, r"疵\) (\d+) 本")}★ / 出目 _after/96_bundle.txt']
out += ['   ' + l.strip() for l in r2.stdout.split('\n') if l.startswith('  後')]
out.append(f'## ⑶ 臺帳を照合器で(基点 ""・cwd main 樹): rc {v.returncode} / 一致 {j1.group(1) if j1 else "?"} / 相違 {j1.group(2) if j1 else "?"} / 実体無 {j1.group(3) if j1 else "?"} / 読めぬ行 {j1.group(4) if j1 else "?"} (母數 {j1.group(5) if j1 else "?"})')
out.append(f'## ⑷ 錠: raw/ 配下 通常 file {nf} / 0444・0555 でない物 {nbad}')
ok = r1.returncode == 0 and r2.returncode == 0 and 'PermissionError' in r1.stdout and v.returncode == 0 and nbad == 0 and g(r1.stdout, r'## 後 (\d+) 本') == '0'
out.append(f'# 結 96: {"★通 ―― 門の後に raw/ へ書いた物 0・書けもせぬ(EACCES)・束全体の後は悉く宣に在る・臺帳 照合 rc 0・錠 悉く★" if ok else "★不 ―― 上の何れかが期待と違ふ★"}')
for nm, r in (('96_raw', r1), ('96_bundle', r2)):
    if r.stderr.strip(): out.append(f'   {nm} stderr: {r.stderr.strip()[:300]}')
K.kaku(AFT + '/96_after.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if ok else 1)
