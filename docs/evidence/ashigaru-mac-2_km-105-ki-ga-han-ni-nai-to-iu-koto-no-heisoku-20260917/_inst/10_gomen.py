# -*- coding: utf-8 -*-
"""10_gomen.py ―― 閉包の器を ★五面★ で測る(札 ⑵)。
 面1 disk      : 在否 / byte / sha256 / ★中身から組んだ blob sha1★
 面2 index     : 共有 index に在るか(ls-files -s)・其の blob sha
 面3 object    : 面1 の blob sha1 を ★cat-file -e★ で問ふ(★hash-object は書く故 使はぬ★)
 面4 origin/main: path 在否 ★と中身の sha★(ls-tree -r --full-tree) + disk との異同
 面5 幹 PR#20  : 0bb92e2b800c が運ぶか(同上)
★ls-tree の作法(札 ki_no_chuui)★: 悉く `git -C <根>` + `--full-tree`。
  且つ ★出目への対照★ ―― cat-file で在ると判つた1本が ★ls-tree 自身の出目★ に在るかを検め、
  無ければ ★止まる★(rc=3)。家老は cat-file で対照を立てた故、対照が通つて數が偽であつた。
★零の四札★: 零を刷る所には 陽性対照・根と深さ・rc・刻 を併記する。
"""
import os, sys, subprocess, hashlib, time
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
HEI=['scripts/checks/karo_mac_dasumae_gate.sh',
     'scripts/checks/karo_mac_manifest_verify.py',
     'scripts/checks/karo_mac_manifest_append.py']          # 閉包(甲乙丙 を判ずる)
TEI=['scripts/checks/context_usage_warn.sh']                # 丁(家老が中身異と名指した・宣の外)
MIKI='0bb92e2b800c'
L=[]
def w(s): L.append(s); print(s)
def g(*a):
    p=subprocess.run(['git','-C',NE]+list(a),capture_output=True,text=True)
    return p.returncode, p.stdout, p.stderr
KOKU=time.strftime('%Y-%m-%dT%H:%M:%S%z')
w('刻 = %s / 根 = %s' % (KOKU,NE))

# ---- 面1/面3 ----------------------------------------------------------
disk={}
for rel in HEI+TEI:
    p=os.path.join(NE,rel)
    if not os.path.isfile(p): disk[rel]=None; continue
    b=open(p,'rb').read()
    disk[rel]={'byte':len(b),
               'sha256':hashlib.sha256(b).hexdigest(),
               'blob':hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()}

# ---- 面2 ----
rc_i,out_i,_=g('ls-files','-s','--','scripts/checks/')
idx={}
for line in out_i.split('\n'):
    if not line.strip(): continue
    meta,path=line.split('\t',1); mode,sha,stage=meta.split()
    idx[path]=sha
w('面2 index: ls-files -s -- scripts/checks/ rc=%d 行=%d' % (rc_i,len(idx)))

# ---- 面4/面5 ―― ★対照付きの ls-tree★ ----
def ki(rev,label):
    """<rev> の scripts/checks/ を根相対で歩き、★出目への対照★を掛ける。"""
    rc_t,out_t,err_t=g('cat-file','-t',rev)
    if rc_t!=0:
        w('  ★%s は此の repo に無い(cat-file -t rc=%d)∴ 零に非ず「測れぬ」★' % (label,rc_t))
        return None
    rc,out,err=g('ls-tree','-r','--full-tree',rev,'--','scripts/checks/')
    rows={}
    for line in out.split('\n'):
        if not line.strip(): continue
        meta,path=line.split('\t',1); mode,typ,sha=meta.split()
        rows[path]=(mode,typ,sha)
    # ★対照★: cat-file(根相対・別器)で在ると判つた1本が、★此の出目★に在るか
    ctl=None
    for cand in ['scripts/checks/pane_identity.sh','scripts/checks/context_usage_warn.sh',
                 'scripts/checks/karo_mac_gate7.sh']:
        if g('cat-file','-e','%s:%s'%(rev,cand))[0]==0: ctl=cand; break
    if ctl is None:
        w('  ★対照を立てられぬ(候補3本とも %s に無し)∴ 止まる★' % label); sys.exit(3)
    if ctl not in rows:
        w('  ★対照 %s は cat-file では在るのに ls-tree の出目に無い ∴ ★止まる★(數が偽)' % ctl)
        sys.exit(3)
    w('面%s %s: rc=%d 行=%d / ★対照★ %s = 出目に在り(cat-file rc=0 と一致)'
      % (label[0],label,rc,len(rows),ctl))
    return rows

w('')
ORI=ki('origin/main','4:origin/main')
PR =ki(MIKI,'5:幹PR#20 '+MIKI)

# ---- 卓 ----
w('')
w('='*96)
for rel in HEI+TEI:
    kind='閉包' if rel in HEI else '★丁(宣外)★'
    w('■ %s  [%s]' % (rel,kind))
    d=disk[rel]
    if d is None: w('   面1 disk = ★無★'); continue
    w('   面1 disk   = 在 / %d byte / sha256=%s' % (d['byte'],d['sha256']))
    w('              blob sha1(中身から組んだ) = %s' % d['blob'])
    w('   面2 index  = %s' % (('在 sha=%s / 手許 blob と %s'
        % (idx[rel], '一致' if idx[rel]==d['blob'] else '★相違★')) if rel in idx else '★外★'))
    rc_e,_,_=g('cat-file','-e',d['blob'])
    w('   面3 object = %s (cat-file -e %s rc=%d)'
      % ('★在★' if rc_e==0 else '★無★',d['blob'],rc_e))
    for rows,nm in ((ORI,'面4 origin/main'),(PR,'面5 幹PR#20  ')):
        if rows is None: w('   %s = ★測れぬ★' % nm); continue
        if rel not in rows: w('   %s = ★path 無★' % nm); continue
        mode,typ,sha=rows[rel]
        w('   %s = path 在 sha=%s ∴ 手許と %s'
          % (nm,sha,'★一致★' if sha==d['blob'] else '★中身 異★'))
w('='*96)
open(os.path.join(B,'_raw/10_gomen.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))
