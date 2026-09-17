# -*- coding: utf-8 -*-
"""72 門の初控から ★初走の疵★ を引き直す器

  ★何故 此の器が要るか(當席の疵)★:
  71 を二度走らせた。二走目は ★己の初走が既に直した後★ を見るゆゑ 甲=2/乙=0 と出、
  `raw/71_seikei.txt` を上書きして ★初走の覚(甲=19/乙=3)を消した★。
  ∴ 覚を書く器は ★冪等でない★ ―― 走る度に己の前の値を消す。
  然るに ★門の初控 `_gate/92_gate.err` は動かぬ★。之が初走の真である。
  ★器の覚より、門の控を信ぜよ。★
"""
import io, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw'))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = B + '/_gate/92_gate.err'
t = io.open(src, encoding='utf-8').read()
kara = re.findall(r'★EOF改行 ―― (\S+) は空file\(0byte\)★', t)
sue  = re.findall(r'★末尾空白 ―― (\S+) に (\d+) 行★', t)
# 今の disk で、空の一行を担ふ file を数へ直す(=直しが残つて居るか)
ATAMA = '★空である★'
ima = []
for root, ds, fs in os.walk(B):
    ds[:] = [d for d in ds if d not in ('_gate', '__pycache__')]
    for f in sorted(fs):
        p = os.path.join(root, f)
        if f.endswith('.pyc') or os.path.relpath(p, B) == 'manifest.txt':
            continue
        try:
            h = io.open(p, encoding='utf-8').readline()
        except (UnicodeDecodeError, OSError):
            continue
        if h.startswith(ATAMA):
            ima.append(os.path.relpath(p, B))
o = []
o.append('# 72 門の初控(_gate/92_gate.err)から引いた ★初走の疵★ ―― 器の覚ではなく門の控が典拠')
o.append('')
o.append('甲 0byte(條④が鳴つた) = %d本' % len(kara))
for x in sorted(kara):
    o.append('    %s' % x)
o.append('')
o.append('乙 末尾空白(條②が鳴つた) = %d本 / 延べ %d行' % (len(sue), sum(int(n) for _, n in sue)))
for x, n in sorted(sue):
    o.append('    %s  %s行' % (x, n))
o.append('')
o.append('★今の disk で「空である旨の一行」を担ふ file = %d本★' % len(ima))
o.append('  (門が鳴らした %d本 との差 %+d は、71 の二走目が己の .err を足した分である)'
         % (len(kara), len(ima) - len(kara)))
for x in ima:
    o.append('    %s' % x)
o.append('')
o.append('★零の四札★: 陽性対照=條② は初走で現に 3本 鳴つた(∴ 檢出子は生きて居る) /')
o.append('            根=束の直下・深さ無限(_gate と __pycache__ のみ除く) / rc=門 初走 1・再走 0 / 刻=本弾')
K.kaku(B + '/raw/72_kado_shoso.txt', '\n'.join(o))
print('甲=%d 乙=%d 今=%d' % (len(kara), len(sue), len(ima)))
