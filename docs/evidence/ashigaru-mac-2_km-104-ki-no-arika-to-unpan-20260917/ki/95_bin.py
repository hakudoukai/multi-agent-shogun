# -*- coding: utf-8 -*-
"""納め便を★器で測つてから★送る。★300字が條★・`python3` の `len`(codepoint)で測る。
 ★awk の length() は byte を返す ∴ 使はぬ。★
 門の数は★書かぬ★ ―― 便に焼けば臺帳が育つ度に古びる。紙の一行目を指すに留める。
"""
import os, sys
ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
assert os.path.basename(ROOT).startswith('ashigaru-mac-2_km-104-'), ROOT
GEN = 300
body = (
 '專任2 第45弾 km-104 納め。㋑46枝(家老45との差1本=km-gate-kou-otsu が幹へ進んだ刻の差)の門控から器を逐語で拾ひ'
 '相異67→甲14。㋐甲14の内 origin/main に在るは6・★欠8★。㋒幹68b6e07bが運ぶは2(gate/gate4)'
 '∴★残る欠6★=append.py＋~/bin5本(PRでは治らぬ)。★append.py は path ref 0/90・object すら無し'
 '＝disk が失せれば臺帳が建たぬ★。在る6の内2は異版。案甲乙丙を紙に(据ゑず)。門rc/母數は紙の一行目。'
 '束=ashigaru-mac-2_km-104-…/')
n = len(body)
print('納め便 字数=%d' % n)
assert n <= GEN, ('★條を超えた★', n)
open(os.path.join(ROOT, 'raw', '95_bin.txt'), 'w', encoding='utf-8').write(body + '\n')
