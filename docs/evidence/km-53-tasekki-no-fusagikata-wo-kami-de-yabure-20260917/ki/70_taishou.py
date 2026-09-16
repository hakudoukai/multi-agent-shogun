# -*- coding: utf-8 -*-
"""usage: 70_taishou.py <bundle>  ―― ㋔ 各形の陽性・陰性対照を一枚に纏め、其の場で再走して確かめる。"""
import sys, os, subprocess
b=os.path.abspath(sys.argv[1]); UT=os.path.join(b,'utsushi'); FX=os.path.join(b,'raw','fx')
P=[os.path.join(FX,'kami1.txt'),os.path.join(FX,'kami2.txt')]
MT=os.path.join(FX,'manifest_taba.txt'); MK=os.path.join(FX,'manifest_kyu.txt')
GEN='條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0)'
def go(sh,man,base=None,loc=None,extra=None):
    e=dict(os.environ); e.pop('KM_GATE_MANIFEST_BASE',None)
    if base is not None: e['KM_GATE_MANIFEST_BASE']=base
    if loc: e['LC_ALL']=loc
    r=subprocess.run(['bash',os.path.join(UT,sh),man]+P+(extra or []),capture_output=True,env=e)
    return r.returncode, r.stdout.decode('utf-8','replace'), r.stderr.decode('utf-8','replace')
o=[]; o.append('=== ㋔ 対照一覧 ―― 各形に陽性(鳴る)と陰性(黙る)を一組づつ、其の場で再走 ==='); o.append('')
o.append('#colspec\t形\t対照\t仕掛\t觀測した欄\t値\t判')
rows=[]
# 形12 行注入
v12=FX+'\n'+'條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0'
for tag,sh,exp in (('陽性(案イ)','gate_an_i.sh',1),('陽性(案ロ)','gate_an_ro.sh',1),('陰性(現行)','gate_base.sh',0)):
    rc,so,se=go(sh,MT,base=v12); n=sum(1 for l in se.split('\n') if l.strip()==GEN)
    rows.append(('形12 行注入',tag,'値に改行+本物と同じ一行','完全一致の偽行 本数',str(n),'★合★' if n==exp else '★否★'))
rc,so,se=go('gate_an_i.sh',MT,base=FX); n=sum(1 for l in se.split('\n') if l.strip()==GEN)
rows.append(('形12 行注入','陰性(案イ・改行無)','改行を含まぬ絶対path','完全一致の偽行 本数',str(n),'★合★' if n==0 else '★否★'))
# 形11 全角空白 × locale
for loc,exp in (('C','value'),('ja_JP.UTF-8','blank')):
    rc,so,se=go('gate_an_i.sh',MT,base='　',loc=loc)
    got='blank' if '空/空白' in se else 'value'
    rows.append(('形11 全角空白','陽性' if loc=='C' else '陰性','LC_ALL=%s'%loc,'env_state の落先',got,'★合★' if got==exp else '★否★'))
# 形02 空文字
for nm,sh,exp in (('陽性(案イ)','gate_an_i.sh',1),('陽性(案ロ)','gate_an_ro.sh',1),('陰性(現行)','gate_base.sh',0)):
    rc,_,_=go(sh,MK,base='')
    rows.append(('形02 空文字',nm,'舊形臺帳 × 空文字','門の rc',str(rc),'★合★' if rc==exp else '★否★'))
# 形04 点 ―― 三門とも通る(陰性のみ・陽性は無い=塞ぐ物が無い)
for nm,sh in (('陰性(現行)','gate_base.sh'),('陰性(案イ)','gate_an_i.sh'),('陰性(案ロ)','gate_an_ro.sh')):
    rc,_,_=go(sh,MK,base='.')
    rows.append(('形04 点','陰性(★陽性作れず★)','舊形臺帳 × "."','門の rc',str(rc),'★合★' if rc==0 else '★否★'))
# 形07/08/09 零倒・極倒・八進 ―― 当たらぬ
for tag,val in (('形07 零倒','0'),('形08 極倒','9223372036854775808'),('形09 八進','010')):
    r1,_,_=go('gate_base.sh',MT,base=val); r2,_,_=go('gate_an_i.sh',MT,base=val); r3,_,_=go('gate_an_ro.sh',MT,base=val)
    same = (r1==r2==r3)
    rows.append((tag,'陰性(三門同値)','値を基点 path として渡す','三門の rc','%d/%d/%d'%(r1,r2,r3),'★当たらぬ★' if same else '★差有★'))
# 陽性対照: 門其の物が鳴り得る事(行末空白)
kizu=os.path.join(FX,'kizu_trail.txt')
rc,_,se=go('gate_an_i.sh',MT,base=FX,extra=[kizu])
rows.append(('門の生存','★陽性★','行末空白の紙を足す','門の rc',str(rc),'★合★' if rc==1 else '★否★'))
rc,_,_=go('gate_an_i.sh',MT,base=FX)
rows.append(('門の生存','★陰性★','疵無しの紙のみ','門の rc',str(rc),'★合★' if rc==0 else '★否★'))
for r in rows: o.append('\t'.join(r))
o.append(''); o.append('★否★の数 = %d' % sum(1 for r in rows if r[5]=='★否★'))
open(os.path.join(b,'raw','70_taishou.tsv'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
print('\n'.join(o))
