#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""84_tobi.py -- ★跳を故意に増やす臺帳を三枚建てる器★(第48弾 ㋒⑴)。

  T0 = 元の臺帳の ★逐語の写し★(一字も変へぬ)
  T1 = T0 + ★跳甲★(空行と `#` 註行)を 10 行
  T2 = T1 + ★跳乙★(path は在るが ★sha256= 欄が無い★ 行)を 5 行

  ★跳乙の行は「本来照合されるべき行」である。★ path も bytes も lines も書いて在る。
  欠けて居るのは sha 欄だけ ―― 然るに器は之を ★数へずに跳ぶ。★
  T1→T2 で母數が一指も動かぬ事が、其の儘 ★宣言されて居らぬ跳★ の證である。

  ★元の臺帳へは一字も書かぬ。★ 写しは悉く本束の fixture/tobi/ の下へ建てる。

使ひ方: 84_tobi.py <元の臺帳> <出し先 dir>
"""
import sys
sys.dont_write_bytecode = True
import io, os, subprocess

if len(sys.argv) < 3:
    sys.stderr.write(u'★測れぬ: <元の臺帳> <出し先 dir> を argv で渡せ★\n'); sys.exit(2)
MOTO, DEST = sys.argv[1], sys.argv[2]
KI = os.path.dirname(os.path.abspath(__file__))
KAKI = os.path.join(KI, '80_kaki.py')
if not os.path.isfile(MOTO):
    sys.stderr.write(u'★測れぬ: 元の臺帳が無い %s★\n' % MOTO); sys.exit(2)
if not os.path.isdir(DEST):
    os.makedirs(DEST)

src = io.open(MOTO, encoding='utf-8').read()
moto_rows = src.split(u'\n')
while moto_rows and moto_rows[-1] == u'':
    moto_rows.pop()

KOU = []
for i in range(1, 11):
    KOU.append(u'' if i % 2 else u'# ★跳甲★ 故意に足した註行 %d ―― 器の頭註 L22 が「数へぬ」と宣して居る形' % i)

# ★跳乙★ ―― path も bytes も lines も在るが sha 欄だけが無い。
#   実在する紙を指す ―― 「disk に無いから跳んだ」と読まれぬ様に。
OTSU = [u'path=docs/evidence/km-48-nise-no-tsuuka-wo-nise-to-wakaru-katachi-de-nokose-20260917/ki/83_yotsu5.py bytes=0 lines=0',
        u'path=docs/evidence/km-48-nise-no-tsuuka-wo-nise-to-wakaru-katachi-de-nokose-20260917/ki/84_tobi.py bytes=0 lines=0',
        u'path=docs/evidence/km-48-nise-no-tsuuka-wo-nise-to-wakaru-katachi-de-nokose-20260917/ki/80_kaki.py bytes=0 lines=0',
        u'path=docs/evidence/km-48-nise-no-tsuuka-wo-nise-to-wakaru-katachi-de-nokose-20260917/ki/hashiru.sh bytes=0 lines=0',
        u'path=scripts/checks/karo_mac_manifest_verify.py bytes=0 lines=0']


def kaku(name, rows):
    p = os.path.join(DEST, name)
    r = subprocess.run([sys.executable, '-B', KAKI, p, '--nushi', '84_tobi.py'],
                       input=u'\n'.join(rows), capture_output=True, text=True)
    sys.stdout.write(u'= %s ―― 行=%d bytes=%d\n' % (p, len(rows), os.path.getsize(p)))
    if r.stderr.strip():
        sys.stdout.write(u'  %s\n' % r.stderr.strip())
    return p


sys.stdout.write(u'元 %s ―― 非空の行=%d\n' % (MOTO, len(moto_rows)))
kaku('T0_utsushi.txt', moto_rows)
kaku('T1_kou10.txt', moto_rows + KOU)
kaku('T2_kou10_otsu5.txt', moto_rows + KOU + OTSU)
sys.stdout.write(u'\n★足した物★ 跳甲=10 行(空5/註5) ・ 跳乙=5 行(path 有・sha 欄無・現物は悉く實在)\n')
sys.stdout.write(u'★T0 と元の中身が同じか★ %s\n'
                 % (u'同じ' if io.open(os.path.join(DEST, 'T0_utsushi.txt'), encoding='utf-8').read().strip()
                    == src.strip() else u'★違ふ ―― 写しが元と食ひ違つた★'))
sys.exit(0)
