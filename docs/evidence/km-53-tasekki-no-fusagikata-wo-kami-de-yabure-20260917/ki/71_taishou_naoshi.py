# -*- coding: utf-8 -*-
"""usage: 71_taishou_naoshi.py <bundle>
★70 の疵を直す★。70 は「一致」を名乗る行を数へたが、★本物の一致行★ と ★偽行★ を分てなんだ。
∴ 陰性(改行無)でも 1 と出て ★否★ に成つた ―― ★器が誤つたのであつて、案が正しかつたのではない。★
直した判: 「一致」行と「落ちた」行が ★同時に在る★ = 矛盾 = ★注入の印★。
"""
import sys, os, subprocess
b=os.path.abspath(sys.argv[1]); UT=os.path.join(b,'utsushi'); FX=os.path.join(b,'raw','fx')
P=[os.path.join(FX,'kami1.txt'),os.path.join(FX,'kami2.txt')]
MT=os.path.join(FX,'manifest_taba.txt')
ITCHI='條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0)'
OCHI ='★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★'
v12=FX+'\n'+'條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0'
o=['=== ㋓/㋔ 直した測り ―― 「一致」と「落ちた」の ★同時出現★ を印とする ===','']
o.append('#colspec\t門\t値\t一致行\t落ちた行\t矛盾\t判(期待)')
def probe(sh, base, expect):
    e=dict(os.environ); e['KM_GATE_MANIFEST_BASE']=base
    r=subprocess.run(['bash',os.path.join(UT,sh),MT]+P,capture_output=True,env=e)
    L=r.stderr.decode('utf-8','replace').split('\n')
    a=sum(1 for l in L if l.strip()==ITCHI); c=sum(1 for l in L if l.strip()==OCHI)
    mu = (a>=1 and c>=1)
    return a,c,mu,('★合★' if mu==expect else '★否★')
for sh,nm in (('gate_an_i.sh','案イ'),('gate_an_ro.sh','案ロ'),('gate_base.sh','現行')):
    a,c,mu,j=probe(sh,v12, expect=(sh!='gate_base.sh'))
    o.append('%s\t形12 改行有(陽性)\t%d\t%d\t%s\t%s' % (nm,a,c,'★有★' if mu else '無',j))
for sh,nm in (('gate_an_i.sh','案イ'),('gate_an_ro.sh','案ロ'),('gate_base.sh','現行')):
    a,c,mu,j=probe(sh,FX, expect=False)
    o.append('%s\t改行無(陰性)\t%d\t%d\t%s\t%s' % (nm,a,c,'★有★' if mu else '無',j))
o.append('')
o.append('★否★の数 = %d' % sum(1 for l in o if l.endswith('★否★')))
o.append('')
o.append('∴ ★案イ・案ロ のみ、「一致」と「落ちた」が同じ門票に並ぶ。★')
o.append('  實は verify は落ちて居る。★偽行だけが「一致」と名乗る。★')
o.append('  現行門は同じ値でも 一致行 0 / 落ちた行 1 ―― ★矛盾せぬ。★')
o.append('')
o.append('=== 器の疵 二件、名指して記す ===')
o.append('疵甲(40_hashiru.py): 偽行を ★完全一致★ で数へた ∴ say の末尾 ")" が付く形10 を 0 と数へた。')
o.append('     ―― stderr 行が 8→9 に増えて居た事で気付いた。★数へ方が形に依存して居た。★')
o.append('疵乙(70_taishou.py): 「一致」行を数へ、★本物と偽を分てなんだ★ ∴ 陰性対照が ★否★ と出た。')
o.append('     ―― ★否★ を「案が正しい」と読むのは誤り。★器が誤つたのである。★ 本器で直した。')
o.append('★二度とも、器の刷つた數が誤つて居た。★ 之は本弾自身が ㋔ の教へを踏んだ證である。')
open(os.path.join(b,'raw','71_taishou_naoshi.tsv'),'w',encoding='utf-8').write('\n'.join(o)+'\n')
print('\n'.join(o))
