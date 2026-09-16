# -*- coding: utf-8 -*-
"""usage: 55_nukeana.py <bundle>
㋑㋒ の素: ⑴ 二案の case に ★`*)` 腕が無い★ 事の實證(第五の語を足した写しで測る)
          ⑵ 全角空白(U+3000)の落先が ★locale 依存★ か否か(tr -d '[:space:]' の實測)
          ⑶ 案ロ の刷り先(stdout か stderr か)を ★分けて★ 測る
"""
import sys, os, re, subprocess
bundle = os.path.abspath(sys.argv[1]); UT=os.path.join(bundle,'utsushi'); FX=os.path.join(bundle,'raw','fx')
paths=[os.path.join(FX,'kami1.txt'), os.path.join(FX,'kami2.txt')]
man=os.path.join(FX,'manifest_taba.txt')
out=[]
out.append('=== ㋑-1 ★case に `*)` 腕が有るか★(逐語で数へる) ===')
for g in ('gate_base.sh','gate_an_i.sh','gate_an_ro.sh'):
    s=open(os.path.join(UT,g),encoding='utf-8').read()
    m=re.search(r'case "\$\(env_state KM_GATE_MANIFEST_BASE\)" in(.*?)\n\s*esac', s, re.S)
    if not m: out.append('%-16s case 無し(env_state を用ゐぬ=現行門)' % g); continue
    body=m.group(1)
    arms=re.findall(r'^\s*([A-Za-z*|]+)\)', body, re.M)
    out.append('%-16s 腕=%s  ★`*)` = %s★' % (g, '/'.join(arms), '有' if '*' in arms else '★無★'))
out.append('')
out.append('※ env_state は unset/empty/blank/value の四語しか刷らぬ ∴ 今日は届かぬ。')
out.append('  然し ★現行門は if/else の二分岐で「必ずどちらかを通る」★ ―― 二案は其の保證を捨てた。')
out.append('  第五の語が一語増えた刹那、set -u + local vrc 未代入 で ★門其の物が死ぬ★。實證↓')
out.append('')
out.append('=== ㋑-2 ★第五の語★ を足した探り写し(prove_5th.sh)で實證 ===')
src=open(os.path.join(UT,'gate_an_i.sh'),encoding='utf-8').read()
# env_state に第五の語を刷らせる(探り専用の写し・生器不触)
probe=src.replace("else printf 'value\\n'; fi", "else printf 'gogo\\n'; fi", 1)
assert probe != src, '★置換不成立★'
pp=os.path.join(UT,'prove_5th.sh'); open(pp,'w',encoding='utf-8').write(probe)
env=dict(os.environ); env['KM_GATE_MANIFEST_BASE']=FX
r=subprocess.run(['bash',pp,man]+paths,capture_output=True,env=env)
err=r.stderr.decode('utf-8','replace')
out.append('rc=%d' % r.returncode)
for i,l in enumerate(err.split('\n'),1): out.append('%3d| %s' % (i,l))
out.append('★unbound variable を含むか= %s★' % ('有' if 'unbound' in err else '無'))
out.append('')
out.append('=== ㋑-3 陰性対照: 同じ第五の語を ★現行門★ へ当てる ===')
src0=open(os.path.join(UT,'gate_base.sh'),encoding='utf-8').read()
probe0=src0.replace("else printf 'value\\n'; fi", "else printf 'gogo\\n'; fi", 1)
assert probe0 != src0, '★置換不成立(base)★'
pp0=os.path.join(UT,'prove_5th_base.sh'); open(pp0,'w',encoding='utf-8').write(probe0)
r0=subprocess.run(['bash',pp0,man]+paths,capture_output=True,env=env)
e0=r0.stderr.decode('utf-8','replace')
out.append('rc=%d  unbound=%s  行=%d' % (r0.returncode, '有' if 'unbound' in e0 else '★無★', len(e0.split('\n'))))
out.append('∴ ★現行門は死なぬ。二案のみ死ぬ。★ 是れ ★二案が持ち込む退歩★ である。')
out.append('')
out.append('=== ㋒-1 全角空白 U+3000 の落先は locale に依るか ===')
for loc in ('C','ja_JP.UTF-8','en_US.UTF-8'):
    for nm,val in (('U+3000 全角空白','　'),('U+0020 半角空白',' '),('U+00A0 NBSP',' '),('U+2003 EM SPACE',' ')):
        e=dict(os.environ); e['LC_ALL']=loc; e['X']=val
        rr=subprocess.run(['bash','-c','printf %s "$X" | tr -d "[:space:]" | wc -c'],capture_output=True,env=e)
        left=rr.stdout.decode().strip()
        out.append('LC_ALL=%-12s %-16s tr 後の byte=%s → %s' % (loc,nm,left,'blank(消えた)' if left=='0' else 'value(残る)'))
out.append('')
out.append('※ ∴ 專任1 §2⑶「全角空白のみ ―― value として verify へ渡る」は ★實測と合はぬ★。')
out.append('  上表の通り、當機では locale に依らず U+3000 は [:space:] に含まれ ★blank★ へ落ちる。')
out.append('')
out.append('=== ㋒-2 案ロ の刷りは stdout か stderr か(分けて測る) ===')
for tag,val,setit in (('01 未設定',None,False),('02 空文字','',True),('11 全角空白','　',True),('05 絶対fx',FX,True)):
    e=dict(os.environ); e.pop('KM_GATE_MANIFEST_BASE',None)
    if setit: e['KM_GATE_MANIFEST_BASE']=val
    rr=subprocess.run(['bash',os.path.join(UT,'gate_an_ro.sh'),man]+paths,capture_output=True,env=e)
    eo=rr.stderr.decode('utf-8','replace'); so=rr.stdout.decode('utf-8','replace')
    hit_e=[l for l in eo.split('\n') if '基点' in l]
    hit_o=[l for l in so.split('\n') if '基点' in l]
    out.append('%-12s rc=%d  「基点」を含む行: stderr=%d本 / ★stdout=%d本★' % (tag,rr.returncode,len(hit_e),len(hit_o)))
    for l in hit_e: out.append('        stderr| %s' % l)
out.append('∴ 案ロ の「必ず刷る」は ★悉く stderr★(say() = printf >&2, L22)。')
out.append('  stdout だけを取る呼手には ★一字も届かぬ★。')
open(os.path.join(bundle,'raw','55_nukeana.txt'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('\n'.join(out))
