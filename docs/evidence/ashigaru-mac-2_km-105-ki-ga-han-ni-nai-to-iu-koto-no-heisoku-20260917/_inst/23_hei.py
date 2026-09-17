# -*- coding: utf-8 -*-
"""23_hei.py ―― ★22 の治し★。丙(系が供給する器)を、偽陽性を除いて数へ直す。
★22 の疵(逐語で残す)★:
  ⑴ 緩い規が ★和文の散文★ を拾つた ―― verify.py:34「裸の file 名」/ :179 同/ append 同。
     「file」は英語の器名であると同時に ★本文の語★ である(memory: 語は path にも本文にも現れる)。
  ⑵ print の中の字 ―― verify.py:191 `例: git show <版>:<path> | shasum -a 256` は
     ★助言の文★ であつて ★走る器★ ではない。
  ⑶ 規の網から ★xxd / tail / timeout / head / cut★ を落して居た(TOOLS に無かつた)。
  ∴ 疵の形 = 「網が粗く、かつ狭い」。★偽陽性と偽陰性は同時に起きる★。
治し: ⑴註行を除く ⑵引用符の中を除く ⑶網を広げる ⑷★拾つた行を悉く逐語で刷り、目で検められる形にする★。
"""
import os, re, subprocess, time
NE='/Users/momizimac/multi-agent-shogun'
B=os.path.join(NE,'docs/evidence/ashigaru-mac-2_km-105-ki-ga-han-ni-nai-to-iu-koto-no-heisoku-20260917')
KIT=['scripts/checks/karo_mac_dasumae_gate.sh','scripts/checks/karo_mac_manifest_verify.py',
     'scripts/checks/karo_mac_manifest_append.py']
TOOLS=['tr','stat','sed','awk','date','grep','sort','wc','od','xxd','tail','head','cut',
       'timeout','gtimeout','find','xargs','shasum','md5','file','printf','cat','mktemp','ls']
L=[]
def w(s): L.append(s); print(s)
w('刻 = %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z')); w(__doc__.strip()); w('')

def sosogu(line):
    """註を落し、引用符の中を伏せる(字は残し、語として拾はれぬやう空白へ)。"""
    if line.lstrip().startswith('#'): return ''
    out=[]; q=None
    for ch in line:
        if q is None and ch in '"\'': q=ch; out.append(' '); continue
        if q is not None:
            if ch==q: q=None
            out.append(' '); continue
        out.append(ch)
    s=''.join(out)
    return s.split('#')[0] if '#' in s else s

hit={}
for rel in KIT:
    for i,line in enumerate(open(os.path.join(NE,rel),encoding='utf-8').read().split('\n'),1):
        s=sosogu(line)
        if not s.strip(): continue
        for t in TOOLS:
            if re.search(r'(?:^|[;&|(`$]\s*|\s)%s(?:\s|$)' % re.escape(t), s):
                hit.setdefault(t,[]).append((os.path.basename(rel),i,line.strip()))
w('★治した網で拾つた 系の器★ = %d種' % len(hit))
for t in sorted(hit):
    w('  ■ %-9s %d箇所' % (t,len(hit[t])))
    for b,i,raw in hit[t]: w('       %s:%d  %s' % (b,i,raw[:120]))
w('')
w('【丙 の判じ】―― repo に版が無く、★方言で判じが変り得る★ 物のみを丙とする')
HEI=[('stat','BSD は `stat -f %z` / GNU は `stat -c %s` ―― ★書式が非互換★。'
              'gate.sh:107,109 は `-f %z` を用ゐる ∴ GNU 系では ★寸法が取れず 條⑤ が倒れる★'),
     ('tr',  'BSD tr は U+3000 を [:space:] と讀む(本機で實測・残0byte)。'
              'GNU tr は C locale で讀まぬ ∴ ★同じ値が blank と非blank に分かれる★'),
     ('xxd', 'xxd は vim 同梱 ―― ★coreutils では無い★。無い系では 條④(EOF改行)が ★無言で空を返す★'),
     ('timeout','stock macOS に `timeout` は無い(coreutils の gtimeout)。'
              'gate.sh は TIMEOUT_BIN で倒すが、★倒した先の振舞ひは系で変る★')]
for t,riyuu in HEI:
    n=len(hit.get(t,[]))
    w('  丙 %-8s 箇所=%d ―― %s' % (t,n,riyuu))
w('  ★丙 = %d種★(閉包の器そのものは repo 内 ∴ 丙は「器」では無く「器が踏む地面」である)' % len(HEI))
for nm,cmd,mi in [('stat -f %z(BSD書式)','stat -f %z -- /etc/hosts','GNU では illegal option'),
                  ('xxd の在否','command -v xxd','無ければ 條④ が空を返す'),
                  ('timeout の在否','command -v timeout || echo ★無★','stock macOS は gtimeout')]:
    r=subprocess.run(['bash','-c',cmd],capture_output=True,text=True)
    w('    本機實測 %-22s → rc=%d 出目=%s' % (nm,r.returncode,(r.stdout+r.stderr).strip()[:60]))
open(os.path.join(B,'_raw/23_hei.txt'),'w',encoding='utf-8').write(''.join(x+'\n' for x in L))
