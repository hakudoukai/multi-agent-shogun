# -*- coding: utf-8 -*-
"""門の後の検め 96(第70弾・_after/)。⑴ raw/ に門の後に生れた物(臺帳に無い通常 file)= 後 N・錠の下で 1 byte 書けるか(P0・期待 EACCES)⑵ 己の臺帳を verify.py に基点=束の根で(期待 一致 N / rc 0)と基点無し(期待 実体無 N / rc 1)⑶ 既成束の印 前(00_start)⇔今。"""
import os, sys, subprocess, re, hashlib, stat, time
B = sys.argv[1]; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; MAN = B + '_manifest.txt'; M = '/Users/momizimac/multi-agent-shogun'; VP = M + '/scripts/checks/karo_mac_manifest_verify.py'
sys.path.insert(0, AFT); import kaki as K; sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
items = set()
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if s and not s.startswith('#') and V.SHA.search(s): items.add(V.paths_of(s)[0])
disk = set(); hi = 0
for d, ds, fs in os.walk(RAW):
    for f in fs:
        q = os.path.join(d, f)
        if not stat.S_ISREG(os.lstat(q).st_mode): hi += 1; continue
        disk.add(os.path.relpath(q, D))
ato = sorted(disk - items); kizu = sorted(x for x in ato if not x.endswith('.first'))
try: open(RAW + '/96_probe.txt', 'w').write('x'); p0 = '★書けた★'
except OSError as e: p0 = f'{type(e).__name__}({e.errno})'
def vf(argv):
    p = subprocess.run(['python3', '-B', VP, MAN] + argv, capture_output=True, text=True, cwd=M); j = re.search(r'一致 ★(\d+)★ / 相違 (\d+) / 実体無 (\d+) / 読めぬ行 (\d+)\s+\(母數 (\d+)\)', p.stdout)
    return f'rc {p.returncode} / 一致 {j.group(1)} / 相違 {j.group(2)} / 実体無 {j.group(3)} / 読めぬ行 {j.group(4)} (母數 {j.group(5)})' if j else f'rc {p.returncode} / ?'
def taba_in(d):
    rows = []
    for r, ds, fs in os.walk(M + '/' + d):
        for f in fs:
            q = os.path.join(r, f)
            if stat.S_ISREG(os.lstat(q).st_mode): rows.append(os.path.relpath(q, M + '/' + d) + ' ' + hashlib.sha256(open(q, 'rb').read()).hexdigest())
    rows.sort(); return hashlib.sha256('\n'.join(rows).encode()).hexdigest()[:16]
st = open(RAW + '/00_start.txt', encoding='utf-8').read(); mae = dict(re.findall(r'(km-4\d|km-5\d) 印 ([0-9a-f]{16})', st))
KISEI = ['docs/evidence/km-47-yotsu-no-kazu-20260917', 'docs/evidence/km-50-kara-wa-todokazu-20260917']; ima = {d.split('/')[-1][:5]: taba_in(d) for d in KISEI}
onaji = all(mae.get(k) == v for k, v in ima.items())
out = [f'# 96 門の後 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}', f'⑴ 根 raw/: 臺帳の項 {len(items)} / disk 通常 {len(disk)}(非通常 {hi}) / 後 {len(ato)} / ★疵 {len(kizu)}★ {kizu[:5]} / P0 根へ 1 byte 書けぬ = {p0}',
       f'⑵ 臺帳を照合器で(基点=束の根・cwd main 樹): {vf([D])}', f'⑵ 臺帳を照合器で(基点無し・既定 repo 根): {vf([])} ―― 束内相対ゆゑ落ちて正',
       f'⑶ 既成束の印 前⇔今: ' + ' / '.join(f'{k} {mae.get(k, "?")}→{v}' for k, v in ima.items()) + f' / 印 前後 {"同" if onaji else "★違★"}']
K.kaku(AFT + '/96_after.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if not kizu and p0 != '★書けた★' and onaji else 1)
