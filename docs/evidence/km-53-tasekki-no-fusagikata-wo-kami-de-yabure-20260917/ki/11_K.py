# -*- coding: utf-8 -*-
"""usage: 11_K.py <outdir>
K を絞る ―― 「門の名を持つ file」から ★呼ぶ器★ だけを残す。
分類: 器(呼ぶ) / 記録(docs/evidence・queue の出目) / 控(.bak) / 他樹(.claude/worktrees)
K の各行に ★通したか(実行)★ / ★讀んだだけ(宣)★ を記す ―― 本弾で実際に走らせたのは 0 本(生器不触)。
"""
import sys, os, re, subprocess
outdir = sys.argv[1]
root = os.getcwd()
GATE = 'karo_mac_dasumae_gate.sh'
ENV = 'KM_GATE_MANIFEST_BASE'
CALL = re.compile(r'(bash|sh|/)\s*[^\s\'"]*karo_mac_dasumae_gate\.sh|karo_mac_dasumae_gate\.sh["\']?\s*,|subprocess.*karo_mac_dasumae_gate')

tracked = [n.decode('utf-8','surrogateescape') for n in subprocess.run(['git','ls-files','-z'],capture_output=True).stdout.split(b'\0') if n]
extra = []
for base in (os.path.expanduser('~/bin'), os.path.join(root,'scripts')):
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ('.git','__pycache__')]
        for f in fn:
            extra.append(os.path.relpath(os.path.join(dp,f), root))
cands = sorted(set(tracked) | set(extra))

def cls(p):
    if p.startswith('docs/evidence/') or p.startswith('queue/'): return '記録'
    if '.claude/worktrees' in p: return '他樹'
    if '.bak-' in p or p.endswith('.first'): return '控'
    return '器'

rows=[]
for p in cands:
    ap = os.path.join(root,p)
    if not os.path.isfile(ap) or os.path.islink(ap): continue
    try:
        if os.path.getsize(ap) > 4_000_000: continue
        t = open(ap,'rb').read().decode('utf-8','replace')
    except Exception: continue
    if GATE not in t: continue
    rows.append((cls(p), 'yes' if CALL.search(t) else 'no', 'yes' if ENV in t else 'no', p))

ki = [r for r in rows if r[0]=='器']
out=[]
out.append('=== ㋐-3 K ―― 門の名を持つ file を分類 ===')
out.append('#colspec\t分類\t呼形有\tENV有\tpath')
for r in sorted(rows): out.append('\t'.join(r))
out.append('')
n_call = len([r for r in ki if r[1]=='yes'])
out.append('★K の宣★: 分類=器 %d 本、内 ★呼形を持つ(=門を呼ぶ路)★ %d 本、内 ENV を書く物 %d 本。'
           % (len(ki), n_call, len([r for r in ki if r[1]=='yes' and r[2]=='yes'])))
out.append('★K の数へ方★: 字面(呼形の正規表現)で数へた ―― ★本弾で実際に通した路は 0 本★(生器不触の條)。')
out.append('  ∴ K は「宣」であつて「通した」ではない。通したのは ★束内 utsushi/ の写し★ のみ(ki/40 参照)。')
out.append('  記録 %d / 他樹 %d / 控 %d は路に非ず(過去の出目・別 checkout・控)。'
           % (len([r for r in rows if r[0]=='記録']), len([r for r in rows if r[0]=='他樹']), len([r for r in rows if r[0]=='控'])))
open(os.path.join(outdir,'11_K.txt'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('\n'.join(out[:6] + out[-8:]))

# ―― 追補: 「呼び手」の実体は束ごとの使ひ捨て器である ――
import collections
call_rec = [r for r in rows if r[0]=='記録' and r[1]=='yes']
bund = collections.Counter(p.split('/')[2] for _,_,_,p in call_rec if p.startswith('docs/evidence/'))
add=[]
add.append('')
add.append('=== ㋐-4 ★K の真の姿★ ―― 門の呼び手は「据ゑた器」ではなく「束ごとの使ひ捨て器」 ===')
add.append('scripts/ ・~/bin に ★門を呼ぶ据ゑ器は 0 本★(上の 器 2 本は門自身と其の臺帳)。')
add.append('呼形を持つ記録 %d 本 / それを含む束 %d 個。' % (len(call_rec), len(bund)))
for b,c in sorted(bund.items()):
    add.append('  %s\t%d' % (b,c))
add.append('∴ 二案が当たる路 K = ★束ごとに書き直される呼び手★ ―― 今後書かれる物を含み、★上限を宣せぬ★。')
add.append('  既に在る物だけ数へれば 束 %d 個。之が本弾の K である。' % len(bund))
open(os.path.join(outdir,'11_K.txt'),'a',encoding='utf-8').write('\n'.join(add)+'\n')
print('\n'.join(add))
