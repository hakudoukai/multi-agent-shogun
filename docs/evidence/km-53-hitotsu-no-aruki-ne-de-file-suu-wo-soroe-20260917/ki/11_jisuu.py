#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 11_jisuu.py ―― ★便を送る前に、送信とは別の器で字数を測る★
#   出所 = 第52弾 疵0(着手便 361字・一便300字の條を61字超え)。
#   其の疵の因は「字数を送信と同じ一行で測つた」事であり、
#   ∴ 本器は ★送信の器を一切呼ばぬ★。測るだけである。
#
# 使ひ方: 11_jisuu.py <便の胴の file> [上限=300]
#   字   = Python の len(str)(= wc -m 相当・全角も1字)
#   byte = utf-8 の長さ(= wc -c 相当)
#   行   = 改行の数
#   出目 = 超えて居れば rc=1(名指して刷る)・収まれば rc=0
# ★memory「Measure letter length before writing the sender」「字は wc -m / python len」★
import sys, io

if len(sys.argv) < 2:
    sys.stderr.write(u'★測れぬ: 便の胴の file を argv で渡せ★\n'); sys.exit(2)
path = sys.argv[1]
try:
    jou = int(sys.argv[2]) if len(sys.argv) > 2 else 300
except ValueError:
    sys.stderr.write(u'★測れぬ: 上限が數でない(「%s」)★\n' % sys.argv[2]); sys.exit(2)

s = io.open(path, encoding='utf-8', errors='strict').read()
# 便の胴は EOF 改行を含めて渡される事が在る ―― ★末尾の改行は字に数へぬ★(送る胴に入らぬ故)
hontai = s.rstrip(u'\n')
ji = len(hontai)
by = len(hontai.encode('utf-8'))
gyou = hontai.count(u'\n') + (1 if hontai else 0)
koe = 1 if ji > jou else 0
sys.stdout.write(u'file=%s 字=%d byte=%d 行=%d 上限=%d 超=%d\n' % (path, ji, by, gyou, jou, koe))
if koe:
    sys.stderr.write(u'★超えた: %d字 ―― 上限 %d字 を %d字 超えて居る。送るな。★\n' % (ji, jou, ji - jou))
    sys.exit(1)
sys.stderr.write(u'★収まつた: %d字 / 上限 %d字(残 %d字)★\n' % (ji, jou, jou - ji))
sys.exit(0)
