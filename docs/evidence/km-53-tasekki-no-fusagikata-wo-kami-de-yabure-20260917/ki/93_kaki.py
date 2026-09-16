# -*- coding: utf-8 -*-
"""usage: 93_kaki.py  ―― 門が名指した疵を ★元を残して★ 正す(⑺ .first)。
直すのは器の産物のみ: ⑴EOF 改行の欠 ⑵行末空白(逐字刷りの `%3d| ` が空行で残す)。
★意図した疵の紙(raw/fx/kizu_trail.txt)は直さぬ★ ―― 陽性対照の道具である。門の argv から宣して除く。
"""
import io, os
naosu=['raw/40_hashiru.json','raw/50_chunyu.txt','raw/55_nukeana.txt','raw/60_yobite.txt']
for p in naosu:
    s=io.open(p,encoding='utf-8').read()
    io.open(p+'.first','w',encoding='utf-8').write(s)
    t='\n'.join(l.rstrip() for l in s.split('\n')).rstrip('\n')+'\n'
    io.open(p,'w',encoding='utf-8').write(t)
    print('%-24s 元 %d字 → %d字  (.first に残す)' % (p,len(s),len(t)))
print('★直さぬ紙★ raw/fx/kizu_trail.txt ―― 意図した行末空白。門の argv から除く(宣)。')
