# -*- coding: utf-8 -*-
"""km-91 _after/20 ―― 生器へ治を当てる。★逐語で探し・置換数を assert する★
   (行番で追はぬ: 裁の :70 が既に外れて居た故。置換数 0 は黙つて素通りする故 assert する)"""
import sys, hashlib, io

src, dst = sys.argv[1], sys.argv[2]
s = io.open(src, encoding='utf-8').read()
orig = s

OLD_FN = 'num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }\n'
NEW_FN = (
'# ★裁 seq324588⊀① の治(當席 ashigaru-mac-3 2026-09-17 實測)★\n'
)
# 註を組む(非ASCII を素直に書く為 直書き)
NEW_FN = u"""# ★裁 seq324588⑴ の治 ―― 當席(ashigaru-mac-3) 2026-09-17 實測★
#   舊 `num_same_op` は「`-ge` が扱へるか」しか問はず、rc=1(＝0 と負)を ★通して居た★。
#   實測(docs/evidence/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917/_after/11,12,13):
#     -5 / -1 → `read -t` が `invalid timeout specification` で摳ね ★即 rc=1・讀めた字数 0★
#     0      → ★stderr 一行も出さず★ 一字も讀まぬ(regular file 供給でも同じ ∴ 競合に非ず)
#   孰れも INPUT="" → L120 の json.load が倒れ stop_hook_active が常に False
#   → ★無限ループ防ぎが消える★。「赤が青に成る」ではなく ★番人が居らぬ事に誰も気付かぬ★ 形。
#   ∴ 「演算子が扱へるか」ではなく ★下流の二口が共に食へる範囲か★ を問ふ。
#   上限 86400(1日): `read -t` の實受容上限は此の bash 3.2 で 4294967295 (2^32-1)
#   だが(實測 _after/13)、其れは版に依る故、運用上有り得ぬ大きさで手前に切る。
#   甲(裁 seq322952): 下流 `[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` と ★同じ -ge★ で検む。
num_in_range() { [ "${1:-}" -ge 1 ] 2>/dev/null && [ "${1:-}" -le 86400 ] 2>/dev/null; }
"""

OLD_CALL = 'if ! num_same_op "$STOP_HOOK_STDIN_TIMEOUT"; then\n'
NEW_CALL = 'if ! num_in_range "$STOP_HOOK_STDIN_TIMEOUT"; then\n'

OLD_MSG = u'を比較器が扱へぬ(「${__th_vp}」)'
NEW_MSG = u'が 1〜86400 の整数に非ず(「${__th_vp}」)'

edits = [('比較器本体', OLD_FN, NEW_FN),
         ('呼ぶ口',       OLD_CALL, NEW_CALL),
         ('診断の文言', OLD_MSG, NEW_MSG)]
report = []
for name, old, new in edits:
    n = s.count(old)
    if n != 1:
        sys.stderr.write(u'★置換数が 1 に非ず★ %s: %d\n' % (name, n))
        sys.exit(3)
    s = s.replace(old, new, 1)
    report.append(u'%s: 置換数=1 ✓' % name)

# 舊名が一つも残らぬ事を検む
# 舊名が ★註以外★ に残らぬ事を検む(註の中の「舊 num_same_op は…」は残つてよい ―― 由来を消さぬ為)
live = [ln for ln in s.split('\n')
        if 'num_same_op' in ln and not ln.lstrip().startswith('#')]
if live:
    sys.stderr.write(u'★舊名 num_same_op が註以外に %d 行残る★: %s\n' % (len(live), live))
    sys.exit(4)

io.open(dst, 'w', encoding='utf-8').write(s)
h = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:16]
print(u'\n'.join(report))
print(u'舊 num_same_op の残り=0 ✓   新 num_in_range の出=%d' % s.count('num_in_range'))
print(u'src sha16=%s lines=%d' % (h(orig), orig.count('\n')))
print(u'dst sha16=%s lines=%d' % (h(s), s.count('\n')))
