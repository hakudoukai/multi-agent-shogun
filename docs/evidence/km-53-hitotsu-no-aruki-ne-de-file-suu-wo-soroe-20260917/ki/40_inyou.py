#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 40_inyou.py ―― ★stdin 時限の陰陽対照器(據ゑず・寫しで測る)★(第53弾 ㋒)
#
# ★hook 本体は触らぬ★: 對象 file は ★讀むだけ★。判定に使ふ行を ★逐語で抜き★、
# 束の中の寫し(harness)へ写して走らせる。行番号は ★字面で探す(決め打ちせぬ)★。
#
# 使ひ方:
#   40_inyou.py --mato <對象sh> --atai <閾の値> [--keika <経過秒>] --dest <寫しの出し先>
#     --mato : argv で取る(當席が当てた後の版も同じ器で測れる)
#     --atai : STOP_HOOK_STDIN_TIMEOUT へ入れる値(陽性=20桁の十進 / 陰性=正しい十進)
#     --keika: __stdin_el(経過秒)。既定 10。
#
# 抜く規則(宣):
#   ⑴番人域 = 「num_same_op()」を含む行 ∨ 「STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-」を
#     含む行 の ★早い方★ から、「if IFS= read」を含む行の ★直前★ まで(逐語)。
#   ⑵判定行 = 「-ge "$STOP_HOOK_STDIN_TIMEOUT"」を含む行(逐語)。枝(then/else)のみ本器が付す(宣)。
#   ⑶閾の比較の素の rc は、判定行から `[ ... -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` を逐語で抜いて別に測る。
import sys, os, io, re, subprocess, time, hashlib

mato = None; atai = None; keika = u'10'; dest = None
av = sys.argv[1:]; i = 0
while i < len(av):
    a = av[i]
    if a == '--mato' and i+1 < len(av): mato = av[i+1]; i += 2; continue
    if a == '--atai' and i+1 < len(av): atai = av[i+1]; i += 2; continue
    if a == '--keika' and i+1 < len(av): keika = av[i+1]; i += 2; continue
    if a == '--dest' and i+1 < len(av): dest = av[i+1]; i += 2; continue
    sys.stderr.write(u'★測れぬ: 知らぬ引数 %s★\n' % a); sys.exit(2)
for k, v in [('--mato', mato), ('--atai', atai), ('--dest', dest)]:
    if v is None:
        sys.stderr.write(u'★測れぬ: %s を argv で渡せ★\n' % k); sys.exit(2)
if not os.path.exists(mato):
    sys.stderr.write(u'★測れぬ: 對象が無い %s ―― 「無い」は「絶無」ではない(路を疑へ)★\n' % mato); sys.exit(2)

raw = open(mato, 'rb').read()
sha16 = hashlib.sha256(raw).hexdigest()[:16]
lines = raw.decode('utf-8').split(u'\n')

def find(sub, frm=0):
    for n in range(frm, len(lines)):
        if sub in lines[n]:
            return n
    return -1

i_num = find(u'num_same_op()')
i_def = find(u'STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-')
cands = [x for x in (i_num, i_def) if x >= 0]
i_read = find(u'if IFS= read')
# ★疵(本弾で踏んだ)★ 字面 `-ge "$STOP_HOOK_STDIN_TIMEOUT"` だけで探すと、
#   對象の ★註行★(其の比較を説明して居る行)を先に拾ふ。寫しへ註行を `if` の座に置いた結果、
#   `else` が宙に浮いて ★line 35: syntax error★ を出しながら判定を刷つた ―― 出た出目は偽である。
#   ∴ 判定行の條を三つにする: ⑴字面を含む ⑵註行に非ず ⑶`if`/`elif` で起き `; then` で閉づ。
#   合致が複数なら悉く刷り、先頭を採る旨を宣する。條に合ふ物が無ければ ★測れぬ★ で倒す。
def hantei_sagashi(lines):
    ate = []
    for k, ln in enumerate(lines):
        if u'-ge "$STOP_HOOK_STDIN_TIMEOUT"' not in ln: continue
        t = ln.strip()
        chu = t.startswith(u'#')
        kata = (t.startswith(u'if ') or t.startswith(u'elif ')) and t.rstrip().endswith(u'then')
        ate.append((k, chu, kata, t))
    return ate
hantei_ate = hantei_sagashi(lines)
i_cmp = -1
for k, chu, kata, t in hantei_ate:
    if (not chu) and kata:
        i_cmp = k; break
w = sys.stdout.write
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
w(u'# 40_inyou ―― stdin 時限の陰陽対照 / 刻= %s\n' % koku)
w(u'# 對象= %s / sha16= %s / bytes= %d / 行= %d\n' % (mato, sha16, len(raw), raw.count(b'\n')))
w(u'# ★對象は讀むのみ(hook 本体を触らぬ)・判定は束の中の寫しで行ふ★\n')
if not cands or i_read < 0 or i_cmp < 0:
    w(u'★測れぬ: 字面が見付からぬ(num_same_op=%d :-定義=%d read=%d 判定=%d ―― 1起点で -1 は不在)★\n'
      % (i_num+1, i_def+1, i_read+1, i_cmp+1))
    sys.exit(3)
i_start = min(cands)
bannin = lines[i_start:i_read]
hantei = lines[i_cmp]
w(u'# 番人域(逐語)= %d〜%d 行(%d 行)  ★行番号は字面で探した(決め打ちせぬ)★\n'
  % (i_start+1, i_read, len(bannin)))
w(u'# 判定行の候補(字面が当たつた行 悉く)= %d 本 ★註行・if 以外は採らぬ★\n' % len(hantei_ate))
for k, chu, kata, t in hantei_ate:
    w(u'#   %d 行: 註行=%s / if…then=%s / 採=%s : %s\n'
      % (k+1, u'真' if chu else u'偽', u'真' if kata else u'偽',
         u'★之★' if k == i_cmp else u'―', t))
w(u'# 判定行= %d 行(逐語): %s\n' % (i_cmp+1, hantei.strip()))
kata = u'新形(num_same_op ―― 比べる時と同じ演算子で検む)' if i_num >= 0 else u'旧形(case の glob *[!0-9]* ―― 字面で検む)'
w(u'# 番人の形= %s\n' % kata)

m = re.search(r'\[\s*"\$__stdin_el"\s+-ge\s+"\$STOP_HOOK_STDIN_TIMEOUT"\s*\]', hantei)
suhikaku = m.group(0) if m else u'(抜けず)'
w(u'# 閾比較の素(逐語抜き)= %s\n' % suhikaku)

harness = []
harness.append(u'#!/bin/bash')
harness.append(u'# ★寫し★ 對象= %s sha16= %s / 刻= %s' % (mato, sha16, koku))
harness.append(u'# 以下 「番人域」「判定行」は對象から ★逐語で写した★。枝(見る/見ぬ)のみ本器が付す(宣)。')
harness.append(u'STOP_HOOK_STDIN_TIMEOUT=%s' % ("'" + atai.replace("'", "'\\''") + "'"))
harness.append(u'# ---- 番人域(逐語 %d〜%d) ----' % (i_start+1, i_read))
harness.extend(bannin)
harness.append(u'# ---- 番人域 了 ----')
harness.append(u'echo "番人の後の閾= [${STOP_HOOK_STDIN_TIMEOUT}]"')
harness.append(u'__read_rc=1')
harness.append(u'__stdin_el=%s' % keika)
if m:
    harness.append(u'%s' % suhikaku)
    harness.append(u'echo "閾比較の素 rc=$?"')
harness.append(u'# ---- 判定行(逐語 %d) ----' % (i_cmp+1))
harness.append(hantei.rstrip())
harness.append(u'    echo "★時限切れを見る(then へ入つた)★"')
harness.append(u'else')
harness.append(u'    echo "★時限切れを見ぬ(else へ落ちた ―― 危険側)★"')
harness.append(u'fi')
harness.append(u'exit 0')
txt = u'\n'.join(harness) + u'\n'
with io.open(dest, 'w', encoding='utf-8', newline='') as fh:
    fh.write(txt)
os.chmod(dest, 0o755)
w(u'# 寫し= %s (%d bytes / %d 行) sha16= %s\n'
  % (dest, len(txt.encode('utf-8')), txt.count(u'\n'),
     hashlib.sha256(txt.encode('utf-8')).hexdigest()[:16]))

# ★疵(本弾で踏んだ)★ 寫しが `syntax error` を出しながら ★判定を刷つた★ ―― 出目が在る事は
#   器が正しい事の証に成らぬ。∴ ⑴走らす前に `bash -n` で形を検め ⑵走らせた後 rc≠0 を「測れぬ」に倒す。
pn = subprocess.Popen(['/bin/bash', '-n', dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
on, en = pn.communicate()
w(u'# 寫しの形検め(bash -n) rc= %d\n' % pn.returncode)
if pn.returncode != 0:
    for ln in en.decode('utf-8', 'replace').split(u'\n'):
        if ln: w(u'#   [bash -n err] %s\n' % ln)
    w(u'★測れぬ: 寫しの形が壊れて居る(bash -n rc=%d) ―― 判定を刷らぬ★\n' % pn.returncode)
    sys.exit(4)
p = subprocess.Popen(['/bin/bash', dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = p.communicate()
w(u'\n--- 寫しの出目(値= %s / 経過秒= %s) rc= %d ---\n' % (atai, keika, p.returncode))
for ln in o.decode('utf-8', 'replace').split(u'\n'):
    if ln: w(u'[out] %s\n' % ln)
if p.returncode != 0:
    w(u'★測れぬ: 寫しが rc=%d で倒れた ―― 上の出目を判定に用ゐてはならぬ★\n' % p.returncode)
for ln in e.decode('utf-8', 'replace').split(u'\n'):
    if ln: w(u'[err] %s\n' % ln)
sys.exit(0)
