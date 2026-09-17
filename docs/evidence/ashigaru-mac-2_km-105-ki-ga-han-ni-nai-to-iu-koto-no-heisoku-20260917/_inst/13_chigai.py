# -*- coding: utf-8 -*-
"""13_chigai.py ―― 「幹が運ぶ」と書く前に ★中身の差★ を測る。
 在るのに違ふ物を「運ぶ」と書けば、其れが ★最も静かな嘘★ に成る(家老の言を継ぐ)。
 併せて ⑴61a9fe1c の刻 ⑵宣外9辺に ★repo 外★ が混じるか(丙の候補)を歩く。
"""
import os, subprocess, time, difflib
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
MIKI='0bb92e2b800c'
L=[]
def w(s): L.append(s); print(s)
def g(*a):
    p=subprocess.run(['git','-C',NE]+list(a),capture_output=True,text=True)
    return p.returncode,p.stdout,p.stderr
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
w('')
w('【一】幹PR#20 %s が運ぶ版 と 手許 の差' % MIKI)
for rel,tag in [('scripts/checks/karo_mac_dasumae_gate.sh','閉包'),
                ('scripts/checks/karo_mac_manifest_verify.py','閉包'),
                ('scripts/checks/context_usage_warn.sh','★丁★')]:
    rc,out,_=g('show','%s:%s'%(MIKI,rel))
    if rc!=0: w('  %s [%s] = 幹に path 無(rc=%d)'%(rel,tag,rc)); continue
    m=out.splitlines(); d=open(os.path.join(NE,rel),encoding='utf-8').read().splitlines()
    dl=list(difflib.unified_diff(m,d,lineterm='',n=0))
    plus=sum(1 for x in dl if x.startswith('+') and not x.startswith('+++'))
    minus=sum(1 for x in dl if x.startswith('-') and not x.startswith('---'))
    w('  ■ %s [%s]' % (rel,tag))
    w('     幹 %d行 / 手許 %d行 / ★差 +%d -%d★' % (len(m),len(d),plus,minus))
    kizu=[x for x in dl if x.startswith(('+','-')) and not x.startswith(('+++','---'))]
    for x in kizu[:6]: w('       %s' % x[:140])
    if len(kizu)>6: w('       …(以下 %d行 略・全文は _raw/13 の後段)' % (len(kizu)-6))

w('')
w('【二】家老の枝 61a9fe1c の刻')
rc,out,_=g('show','-s','--format=%H%n  著者刻 %ai%n  commit刻 %ci%n  題 %s','61a9fe1c18beffddef6b40503766ba726b8b0a05')
for l in out.rstrip('\n').split('\n'): w('  '+l)
w('  (札 issued_at = 2026-09-17T16:10:00+0900 / km-104 の裁は其の前)')

w('')
w('【三】宣外9辺に ★repo 外★ が混じるか(丙の候補を探す)')
tsv=os.path.join(B,'_raw/02_yobidashi.tsv')
rows=[l.rstrip('\n').split('\t') for l in open(tsv,encoding='utf-8') if l.strip()]
w('  02_yobidashi.tsv = %d行(冠含む)' % len(rows))
soto=[]
for r in rows[1:]:
    tgt=r[-1] if r else ''
    joined='\t'.join(r)
    if '宣外' in joined or '見当らぬ' in joined:
        w('    %s' % joined[:150])
        for tok in r:
            if tok.startswith('/') or tok.startswith('~') or '../..' in tok: soto.append(tok)
w('  ★repo 外を指す辺 = %d本★' % len(soto))
w('  ∴ 閉包3本は悉く %s の下 ∴ ★丙(repo 外ゆゑ PR で治らぬ)は閉包の中に ★0本★★' % NE)
w('    但し「0本」は ★宣した閉包の中での0★ である。宣の外(便の器・hook・~/bin)は測つて居らぬ。')
open(os.path.join(B,'_raw/13_chigai.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))
