# -*- coding: utf-8 -*-
"""usage: 60_yobite.py <bundle>
㋑ 案イを「拒んだ後」で破る ―― 呼手四態 × 三門。
㋒ 案ロの「必ず刷る」を、呼手の側から破る。
併せて ★LC_ALL=C の穴★(全角空白が value に残り 案イが拒まぬ)を實測。
"""
import sys, os, subprocess
bundle=os.path.abspath(sys.argv[1]); UT=os.path.join(bundle,'utsushi'); FX=os.path.join(bundle,'raw','fx')
P=[os.path.join(FX,'kami1.txt'),os.path.join(FX,'kami2.txt')]
MT=os.path.join(FX,'manifest_taba.txt'); MK=os.path.join(FX,'manifest_kyu.txt')
G={'現行':'gate_base.sh','案イ':'gate_an_i.sh','案ロ':'gate_an_ro.sh'}
out=[]
def run(sh, man, base=None, loc=None, shell=None):
    e=dict(os.environ); e.pop('KM_GATE_MANIFEST_BASE',None)
    if base is not None: e['KM_GATE_MANIFEST_BASE']=base
    if loc: e['LC_ALL']=loc
    cmd = shell if shell else 'bash %s %s %s %s' % (os.path.join(UT,sh),man,P[0],P[1])
    r=subprocess.run(['bash','-c',cmd],capture_output=True,env=e)
    return r.returncode, r.stdout.decode('utf-8','replace'), r.stderr.decode('utf-8','replace')

out.append('=== ㋑-4 ★呼手四態★ ―― 案イの「拒む」は呼手に届くか ===')
out.append('題: 空文字(形02)× 舊形臺帳 ―― 現行門が ★rc=0 で通して了ふ★ 穴。案イが拒む筈の所。')
out.append('')
GT=os.path.join(UT,'gate_an_i.sh')
yobite=[
 ('甲 rc を讀まぬ', 'bash %s %s %s %s; echo "呼手の見た値=通つた事にする"' % (GT,MK,P[0],P[1])),
 ('乙 pipe 越しの rc', 'bash %s %s %s %s 2>&1 | tail -1; echo "呼手の rc=$?"' % (GT,MK,P[0],P[1])),
 ('丙 stdout のみ取る', 'bash %s %s %s %s 2>/dev/null; echo "呼手の rc=$?"' % (GT,MK,P[0],P[1])),
 ('丁 rc を正しく取る', 'rc=0; bash %s %s %s %s >/dev/null 2>&1 || rc=$?; echo "呼手の rc=$rc"' % (GT,MK,P[0],P[1])),
]
for nm,cmd in yobite:
    rc,so,se=run(None,None,base='',shell=cmd)
    out.append('%-16s 呼手の出目: %s' % (nm, so.strip().replace('\n',' / ') or '(空)'))
out.append('∴ 甲・乙 は ★案イの拒絶を取り零す★。乙は pipe 故 rc が常に 0(tail の rc)。')
out.append('  丙 は rc を得るが ★案イは stdout に一字も出さぬ★ ∴ 「何が落ちたか」は判らぬ。')
out.append('')
out.append('=== ㋑-5 ★rc=1 は五條のどれでも同じ顔★ ―― 呼手は條①を條②〜⑤と分てるか ===')
out.append('#colspec\t仕掛\t案イのrc\tstdout字\t「條①」を名乗る stderr 行')
kizu=os.path.join(FX,'kizu_trail.txt'); open(kizu,'w',encoding='utf-8').write('末に空白有り \n')
cases=[('條① 基点が空(案イの拒絶)', MK, '', [P[0],P[1]]),
       ('條① 臺帳とdiskの差',        MK, FX, [P[0],P[1]]),
       ('條②③ 行末空白',            MT, FX, [P[0],P[1],kizu])]
for nm,man,base,pp in cases:
    e=dict(os.environ); e['KM_GATE_MANIFEST_BASE']=base
    r=subprocess.run(['bash',GT,man]+pp,capture_output=True,env=e)
    se=r.stderr.decode('utf-8','replace')
    j1=[l for l in se.split('\n') if l.strip().startswith('★條') or '條①' in l]
    out.append('%s\t%d\t%d\t%s' % (nm,r.returncode,len(r.stdout),(j1[-1][:60] if j1 else '(無)')))
out.append('∴ ★三者悉く rc=1★。呼手が rc だけを見る限り ★條①の拒絶と 條②③の疵は同じ値★。')
out.append('  分てる欄は stderr の文言のみ ―― ★機械可読な欄は無い★(番号も無い)。')
out.append('')
out.append('=== ㋑-6 ★fail-closed が新たに塞ぐ正路★ ―― LC_ALL=C の全角空白 ===')
out.append('#colspec\tLC_ALL\t門\trc\t案の札')
for loc in ('C','ja_JP.UTF-8'):
    for nm,sh in (('現行',G['現行']),('案イ',G['案イ']),('案ロ',G['案ロ'])):
        rc,so,se=run(sh,MT,base='　',loc=loc)
        f=[l for l in se.split('\n') if '基点' in l]
        out.append('%s\t%s\t%d\t%s' % (loc,nm,rc,(f[0][:64] if f else '(無)')))
out.append('∴ ★LC_ALL=C では U+3000 が value に残る★ ―― 案イは拒まず、存在せぬ基点として verify へ渡す。')
out.append('  ∴ 案イの fail-closed は ★locale に依る★。cron/systemd 等 LC_ALL 未設定の路では塞がらぬ。')
out.append('')
out.append('=== ㋒-3 ★舊形臺帳が rc=0 で通る形★ ―― 二案とも塞がぬ ===')
out.append('#colspec\t基点の形\t現行\t案イ\t案ロ')
for tag,base in (('02 空文字',''),('04 点 "."','.'),('未設定',None)):
    row=[tag]
    for nm in ('現行','案イ','案ロ'):
        rc,so,se=run(G[nm],MK,base=base)
        row.append(str(rc))
    out.append('\t'.join(row))
out.append('※ 走らせた cwd = repo 根。舊形臺帳(main樹根相対)を置いた。')
out.append('∴ ★形04「点」は 三門とも rc=0★ ―― 「明示した」形を取る故、案イの拒絶に掛からぬ。')
out.append('  ★二案が塞ぐのは「空/空白」の一形だけであり、cwd 相対其の物は塞がぬ。★')
out.append('  「.」を書く一手間で、舊法の臺帳は今日も通る。★之が二案の最大の残穴である。★')
open(os.path.join(bundle,'raw','60_yobite.txt'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('\n'.join(out))
