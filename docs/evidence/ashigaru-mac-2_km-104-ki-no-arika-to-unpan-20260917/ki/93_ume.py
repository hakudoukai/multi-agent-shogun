# -*- coding: utf-8 -*-
"""93_ume.py ―― 紙の一行目へ ★門の出目★ を焼く(何度走らせても同じ形に成る)。
  ★値は手で書かぬ★ ―― `_gate/` の最も新しい `92_gate_*` の .rc と .out から取る。
  ★置換は必ず数へて検める★(裁: 当たらぬ置換は黙つて何もせず「直つた様に見える」)。
  ★己の走りが臺帳の母數を +2 する(ki/93_ume.py と raw/93_ume.txt)★ ゆゑ、
   本器→kaki→臺帳→門 の順で二度回す要が在る。一度目の門の数は古い(母數が己を含まぬ)。
  使ひ方: 93_ume.py [<控の幹 例 _gate/92_gate_20260917T160000>]   ※省けば最も新しい物
"""
import glob, os, re, sys

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('ashigaru-mac-2_km-104-'), ROOT
os.chdir(ROOT)

if len(sys.argv) > 1:
    stem = sys.argv[1]
else:
    rcs = sorted(glob.glob('_gate/92_gate_*.rc'))   # 名に刻が入る ∴ 字順=時順
    assert rcs, '★控が無い★'
    stem = rcs[-1][:-3]
print('控の幹=%s' % stem)

rc = open(stem + '.rc', encoding='utf-8').read().strip()
assert re.fullmatch(r'\d+', rc), rc

# 門の出目は悉く stderr。★但し照合器(verify)の stdout 塊だけは .out に出る★。
out = open(stem + '.out', encoding='utf-8').read()
# 例: 「一致 ★31★ / 相違 0 / 実体無 0 / 読めぬ行 0  (母數 31)」 ―― ★は在る事も無い事も在る。
m = re.search(r'一致\s*★?(\d+)★?\s*/\s*相違\s*★?(\d+)★?\s*/\s*実体無\s*★?(\d+)★?'
              r'\s*/\s*読めぬ行\s*★?(\d+)★?\s*\(母數\s*(\d+)\)', out)
assert m, '★.out から條①の塊を拾へぬ★'
itchi, soui, jittainashi, yomenu, bosuu = m.groups()
print('拾つた: rc=%s 母數=%s 一致=%s 相違=%s 実体無=%s 読めぬ行=%s'
      % (rc, bosuu, itchi, soui, jittainashi, yomenu))

atarashii = ('★門 rc=%s / 母數 %s / 條① 一致 %s・相違 %s・実体無 %s・読めぬ行 %s★'
             '(控 `_gate/` の★最も新しい `92_gate_*`★・`KM_GATE_MANIFEST_BASE=.`・臺帳=束内相対)'
             % (rc, bosuu, itchi, soui, jittainashi, yomenu))

PAPER = 'report.md'
s = open(PAPER, encoding='utf-8').read()
lines = s.split('\n')
atari = [i for i, ln in enumerate(lines) if ln.startswith('★門 rc=')]
print('一行目の形に当たる行=%d 本 %s' % (len(atari), atari))
assert len(atari) == 1 and atari[0] == 0, atari   # ★丁度一本・且つ頭★
mae = lines[0]
lines[0] = atarashii
open(PAPER, 'w', encoding='utf-8').write('\n'.join(lines))

os.makedirs('raw', exist_ok=True)
with open('raw/93_ume.txt', 'w', encoding='utf-8') as f:
    f.write('控の幹=%s\n' % stem)
    f.write('rc=%s 母數=%s 一致=%s 相違=%s 実体無=%s 読めぬ行=%s\n'
            % (rc, bosuu, itchi, soui, jittainashi, yomenu))
    f.write('前の一行目=%s\n' % mae)
    f.write('後の一行目=%s\n' % atarashii)
    f.write('★当たつた行=1(頭)★ ―― 0 なら assert で倒れる(黙つて素通りせぬ)。\n')
    f.write('★此の数は「己を含む臺帳」の数である ∴ 本器を足した後に建て直した臺帳の物でなければならぬ。\n')

# ★読み直して検める★(書けた事と、書いた通りに成つた事は別)
s2 = open(PAPER, encoding='utf-8').read()
assert s2.split('\n')[0] == atarashii, '★書き戻しが合はぬ★'
print('★一行目を焼いた。読み直しで一致★')
