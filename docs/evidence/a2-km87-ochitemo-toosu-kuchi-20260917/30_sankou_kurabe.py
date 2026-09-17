# -*- coding: utf-8 -*-
"""㋒ 三度書かれた同じ行(L144/L191/L240)の★文脈差★を、逐語で示す。
出目の差は 20_kowashi.sh の実測から引く(此処は「何が違はせたか」の道筋)。"""
import re, sys, hashlib
p='utsushi/stop_hook_inbox.sh'
b=open(p,'rb').read()
lines=b.decode('utf-8').split('\n')
print('的 sha16=%s'%hashlib.sha256(b).hexdigest()[:16])
TARGET="UNREAD_COUNT=$(grep -cE '^  read: false$' \"$INBOX\" 2>/dev/null || true)"
locs=[i for i,L in enumerate(lines,1) if L.strip()==TARGET]
print('逐語一致の行 = %s (計 %d 口)'%(locs,len(locs)))
print('★行番で当てず逐語で当てた★ ―― 家老見立の L144/L191/L240 と一致: %s'%(locs==[144,191,240]))
print('')
for n in locs:
    print('=== L%d の文脈 ==='%n)
    # 直前の「守り」を遡つて探す
    guard=None
    for j in range(n-1,0,-1):
        s=lines[j-1].strip()
        if s.startswith('if [ ! -f'):
            guard=('-f 守り L%d'%j, s); break
        if s.startswith('if [ "$STOP_HOOK_ACTIVE"'):
            guard=('active 枝 L%d'%j, s); break
        if s.startswith('if command -v inotifywait'):
            guard=('inotifywait 枝 L%d'%j, s); continue
    print('  直上の守り : %s'%(('%s | %s'%guard) if guard else '★無し★'))
    # 直後の始末
    after=[]
    for j in range(n+1,min(n+6,len(lines)+1)):
        s=lines[j-1].strip()
        if s and not s.startswith('#'): after.append('L%d %s'%(j,s))
        if len(after)>=3: break
    print('  直後の始末 : %s'%' / '.join(after))
