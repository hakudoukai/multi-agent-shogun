# -*- coding: utf-8 -*-
"""95_bin.py ―― 納め便を組み、★送る前に字を測る★(300字が條)。
  ★字は python3 の len(=符号点)で測る。★ macOS の awk length() は byte を返すゆゑ用ゐぬ。
  出目 = raw/95_bin.txt(送る胴そのもの) + 測つた字数。
"""
import io, os

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('a2_km-101-'), ROOT
os.chdir(ROOT)
GEN = 300

body = (
 '專任2 第44弾 km-101 納め。割当13本・手許に物13/13。取込1/60を再現。'
 '⑴対main和6190/⑵自前和1434 ―― ⑴は枝の仕事量に非ずmainの遅れ。'
 '仕分=甲13/乙0/丙0。鎖0・呑むtip0 ∴13本悉く末端、一本も落とせぬ。'
 '衝突78対中blob相異0＝真の衝突0。基準枝4本は悉く割当の外、B前はPR484〜637file。'
 '臺帳7本中 束内相対6・旧形1(hantei)。門rc=0/母數34/條①34。'
 '★枝上の門rc=0は未測★(checkout禁)。束=a2_km-101-…-20260917/'
)

n = len(body)
print('納め便 字数(python3 len・符号点)=%d / 條=%d / %s' % (n, GEN, '通' if n <= GEN else '★超★'))
assert n <= GEN, n
io.open('raw/95_bin.txt', 'w', encoding='utf-8').write(body + '\n')
print('胴を raw/95_bin.txt へ落とした(送る物と同一)。')
