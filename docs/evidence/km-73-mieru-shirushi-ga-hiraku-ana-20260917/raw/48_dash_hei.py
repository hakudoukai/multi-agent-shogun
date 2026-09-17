# -*- coding: utf-8 -*-
"""48 丙四案を dash で走らせた stderr 逐語(esc)―― 47 の dash 欄が 60 字で切れて居た故。初走は python3 - で inline に打ち __pycache__ を raw/ に産んだ(消して本 file に据ゑ -B で走らせ直した・出目同)。"""
import sys, subprocess
A = sys.argv[1]; sys.path.insert(0, A + '/raw'); import kaki as K, dai73 as T
out = ['# 48 丙四案を dash で走らせた stderr 逐語(esc)―― 47 の dash 欄が 60 字で切れて居た故']
for an in T.HEI:
    p = T.dai_path(A + '/raw/dai', 'watcher', an); r = subprocess.run(['/bin/dash', p], capture_output=True, env={'LC_ALL': 'C', 'KM73_TH': '1\n' + T.FAKE})
    out.append(f'{an}: rc {r.returncode} / stdout {T.esc(r.stdout)} / stderr {T.esc(r.stderr)}')
K.kaku(A + '/raw/48_dash_hei.txt', '\n'.join(out)); print('\n'.join(out)[:300])
