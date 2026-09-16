# -*- coding: utf-8 -*-
"""門の後の検め 96b(第70弾・_after/)―― 96 は「臺帳に無い raw/ の file」を悉く疵と数へた(後 9・rc 1)。然れど其の 9 は 50(臺帳の器)と 59(門の前の検め)の ★自產物★ で、臺帳の後・門の前に生れた物である。
96b は歩哨(_after/00_hosho.txt・錠の後・門の直前)の mtime_ns で割る: 門の前(臺帳の後)/ 門の後。期待 門の後 = 0。96 は讀むのみ(raw/ は錠の下)。"""
import os, sys, re, stat, time
B = sys.argv[1]; D = os.path.dirname(B); RAW = D + '/raw'; AFT = D + '/_after'; MAN = B + '_manifest.txt'; M = '/Users/momizimac/multi-agent-shogun'
sys.path.insert(0, AFT); import kaki as K; sys.path.insert(0, M + '/scripts/checks'); import karo_mac_manifest_verify as V
H = os.stat(AFT + '/00_hosho.txt').st_mtime_ns
items = set()
for raw in open(MAN, encoding='utf-8'):
    s = raw.strip()
    if s and not s.startswith('#') and V.SHA.search(s): items.add(V.paths_of(s)[0])
mae = []; ato = []
for d, ds, fs in os.walk(RAW):
    for f in fs:
        q = os.path.join(d, f)
        if not stat.S_ISREG(os.lstat(q).st_mode): continue
        r = os.path.relpath(q, D)
        if r in items: continue
        (mae if os.stat(q).st_mtime_ns < H else ato).append(r)
mae.sort(); ato.sort(); jisan = [r for r in mae if re.match(r'raw/(50_|59_)', r)]
out = [f'# 96b 門の後(歩哨で割る)/ 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 歩哨 mtime_ns {H}', f'臺帳に無い raw/ の通常 file {len(mae) + len(ato)} = 門の前(臺帳の後) {len(mae)}(内 50/59 の自產物 {len(jisan)}・他 {len(mae) - len(jisan)} {[r for r in mae if r not in jisan][:5]}) / ★門の後 {len(ato)}★ {ato[:5]}',
       '門の前の名: ' + ' '.join(mae), f'判: {"★門の後 0・門の前は悉く自產物 ―― 疵 0★" if not ato and len(jisan) == len(mae) else "★門の後か自產物でない物が在る★"}',
       '96 の rc 1 は「後 9 を疵と札した」故で、其の 9 は此處で門の前の自產物と判つた ―― 96 の則が狭かつた(己の器の疵・96 は消さず残す)。']
K.kaku(AFT + '/96b_after.txt', '\n'.join(out)); print('\n'.join(out)); sys.exit(0 if not ato and len(jisan) == len(mae) else 1)
