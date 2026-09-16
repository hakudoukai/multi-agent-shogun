# -*- coding: utf-8 -*-
"""usage: 50_chunyu.py <bundle>
㋓ 行注入 を精密に当てる。40 の形10 は ★偽行 0★ と出たが stderr 行は 8→9 に増えて居た ――
器(40)の数へ方が「完全一致」であつた為で、注入は成立して居た。★器の疵を先に申告する。★
形12 = say の閉ぢ括弧 ')' を ★値の側で食はせる★ ―― 完全に本物と同じ一行を作る。
陽性対照 = 形12 が偽行 1 を作る / 陰性対照 = 現行門(gate_base) は同じ値で偽行 0。
"""
import sys, os, subprocess, hashlib
bundle = os.path.abspath(sys.argv[1]); root = os.getcwd()
UT = os.path.join(bundle,'utsushi'); FX = os.path.join(bundle,'raw','fx')
paths = [os.path.join(FX,'kami1.txt'), os.path.join(FX,'kami2.txt')]
man_taba = os.path.join(FX,'manifest_taba.txt')
GENUINE = '條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0)'
# 形10 = 完結した偽行を置く(末に ')' が余る) / 形12 = 閉ぢ括弧を say に食はせる
V10 = FX + '\n' + GENUINE
V12 = FX + '\n' + '條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0'
out=[]
out.append('=== ㋓-1 ★器の疵 申告★ ===')
out.append('40_hashiru.py の「偽行」欄は l.strip()==GENUINE の完全一致で数へた。')
out.append('形10 は say の末尾 ")" が偽行に付く為 完全一致に成らず ★0★ と出た ―― 注入は成立して居た(stderr 行 8→9)。')
out.append('∴ 本器(50)で ⑴行数の増 ⑵完全一致 の二欄に分けて数へ直す。')
out.append('')
out.append('=== ㋓-2 形10 / 形12 × 写し三本 ===')
out.append('#colspec\t器\t形\trc\tstderr行\t完全一致の偽行\t「一致」を名乗る行の総数')
rows=[]
for g in ('gate_base.sh','gate_an_i.sh','gate_an_ro.sh'):
    for tag, val in (('形10 余り括弧', V10), ('形12 括弧食ひ', V12)):
        env = dict(os.environ); env['KM_GATE_MANIFEST_BASE'] = val
        r = subprocess.run(['bash', os.path.join(UT,g), man_taba]+paths, capture_output=True, env=env, cwd=root)
        err = r.stderr.decode('utf-8','replace')
        lines = err.split('\n')
        exact = sum(1 for l in lines if l.strip()==GENUINE)
        claim = sum(1 for l in lines if '台帳とdiskの差 = 一致' in l)
        rows.append((g,tag,r.returncode,len(lines),exact,claim))
        out.append('%s\t%s\t%d\t%d\t%d\t%d' % (g,tag,r.returncode,len(lines),exact,claim))
        open(os.path.join(bundle,'raw','40_logs','chunyu_%s_%s.err'%(g.replace('.sh',''),tag.split()[0])),'w',encoding='utf-8').write(err)
out.append('')
out.append('=== ㋓-3 逐字(gate_an_i × 形12 の stderr 全文) ===')
env = dict(os.environ); env['KM_GATE_MANIFEST_BASE'] = V12
r = subprocess.run(['bash', os.path.join(UT,'gate_an_i.sh'), man_taba]+paths, capture_output=True, env=env, cwd=root)
for i,l in enumerate(r.stderr.decode('utf-8','replace').split('\n'),1):
    out.append('%3d| %s' % (i,l))
out.append('rc=%d  stdout字=%d' % (r.returncode, len(r.stdout)))
out.append('')
out.append('=== ㋓-4 陰性対照(現行門 gate_base × 形12)の逐字 ===')
r0 = subprocess.run(['bash', os.path.join(UT,'gate_base.sh'), man_taba]+paths, capture_output=True, env=env, cwd=root)
for i,l in enumerate(r0.stderr.decode('utf-8','replace').split('\n'),1):
    out.append('%3d| %s' % (i,l))
out.append('rc=%d  stdout字=%d' % (r0.returncode, len(r0.stdout)))
open(os.path.join(bundle,'raw','50_chunyu.txt'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('\n'.join(out))
