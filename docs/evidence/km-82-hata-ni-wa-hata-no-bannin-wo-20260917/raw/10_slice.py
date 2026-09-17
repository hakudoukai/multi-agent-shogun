# -*- coding: utf-8 -*-
# 逐語の切り出し器 ―― ★手で書き写すな★(裁 seq322952 の紙の則)。錨は逐語・数は必ず1。
# 使ひ方: python3 -B raw/10_slice.py   (束の中で走らせる)
import sys, hashlib
GEN = '_before/inbox_watcher.sh.snapshot'   # 現形(控)
NAO = '../../../scripts/inbox_watcher.sh'   # 直し形(disk・repo source が正)
def cut(text, a, b, tag):
    if text.count(a) != 1: sys.exit('★錨(頭) %s の数=%d(1でない)★' % (tag, text.count(a)))
    i = text.index(a)
    j = text.index(b, i)
    if j < 0: sys.exit('★錨(尾) %s 無し★' % tag)
    return text[i:j+len(b)]
A_BAN = '# ─── 閾の番人(甲/乙) ───\n'
B_BAN = '  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"\n  eval "$_ft_o=\\$_ft_d"\n}\n'
A_HIK = '    if [ "$rc" -eq 2 ]; then\n'
B_HIK = '        process_unread "event" || true\n    fi\n'
UKE_G = 'ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}\n'
A_UKE_N = '# ★受ける口を番人へ替へる(裁 seq324588⑵)★'
B_UKE_N = 'fix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT\n'
out = []
for form, path in (('genkei', GEN), ('naoshi', NAO)):
    t = open(path, encoding='utf-8').read()
    ban = cut(t, A_BAN, B_BAN, form + '/番人')
    if form == 'naoshi':                      # 直し形の番人は fix_flag も含む(閉じ括弧まで延ばす)
        k = t.index('fix_flag(){')
        e = t.index('\n}\n', k) + len('\n}\n')
        ban = t[t.index(A_BAN):e]
    hik = cut(t, A_HIK, B_HIK, form + '/比較器')
    if form == 'genkei':
        if t.count(UKE_G) != 1: sys.exit('★現形の受口の数=%d★' % t.count(UKE_G))
        uke = UKE_G
    else:
        uke = cut(t, A_UKE_N, B_UKE_N, 'naoshi/受口')
    for name, body in (('bannin', ban), ('uke', uke), ('hikaku', hik)):
        p = 'raw/slice_%s_%s.sh' % (form, name)
        open(p, 'w', encoding='utf-8').write(body)
        out.append((p, body.count('\n'), hashlib.sha256(body.encode()).hexdigest()[:16]))
for p, n, h in out:
    print('%s\t%d行\t%s' % (p, n, h))
