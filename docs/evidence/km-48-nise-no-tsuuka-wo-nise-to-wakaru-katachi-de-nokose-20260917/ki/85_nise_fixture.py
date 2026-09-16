#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""85_nise_fixture.py -- ★「鳴る通過」と「黙る通過」を一対で建てる器★(第48弾 ㋑の陽性/陰性対照)。

【何を作るか】
  甲 honmono/ ―― ★素の名★ の紙一本。臺帳の sha 欄が現物に合ふ。
  乙 nise/    ―― ★名の中に己の sha を持つ★ 紙一本(`…sha256=<己の64hex>…`・★空白を含めぬ★)。
                 臺帳の sha 欄は同じく現物に合ふ。

  ★二本とも初手は 一致=1 である。四数札は二本を判じ得ぬ。★

【何故乙が偽か】
  karo_mac_manifest_verify.py L131 は `SHA.search(line)` ―― ★行の最初の sha256=★ を録 sha と取る。
  乙の行では其の最初が ★名の中★ に在る。∴ 器は ★臺帳の sha 欄を一度も讀まぬ。★
  ―― 甲の通過は「臺帳の sha 欄が現物に合つた」故。
     乙の通過は「★名の中の hex が現物に合つた★」故。★同じ 一致=1 が、別の理由で立つて居る。★

【崩し ―― 鳴るか黙るかを實測する形】
  固定 = 「臺帳の sha 欄が現物と一致して居る事」
  崩し = 其の ★sha 欄(行の末の方の sha256=)★ を一字変へる。
  甲 → 相違1 に成る(★鳴る★)。 乙 → 一致1 の儘(★黙る★)。
  ★黙る側の通過が、偽の通過である。★

  ※ 名に ★空白★ を混ぜてはならぬ ―― `path=(.+?)[ \t]+sha256=` が名を切り落し「実体無」で
     ★鳴つて了ふ★。鳴れば偽の通過に成らぬ。第46弾の A10 が空白を含んで居た故 相違1 で鳴つた。
     ★空白を除くだけで、同じ疵が鳴る側から黙る側へ移る。★ 之が本器の要点である。

使ひ方: 85_nise_fixture.py <出し先 dir> <repo 根>
  出す物: <出し先>/honmono/<紙> ・ <出し先>/nise/<紙>
          <出し先>/M_kou.txt M_kou_kuzushi.txt M_otsu.txt M_otsu_kuzushi.txt
"""
import sys
sys.dont_write_bytecode = True
import io, os, hashlib, subprocess

if len(sys.argv) < 3:
    sys.stderr.write(u'★測れぬ: <出し先 dir> <repo 根> を argv で渡せ★\n'); sys.exit(2)
DEST, ROOT = sys.argv[1], sys.argv[2]
KI = os.path.dirname(os.path.abspath(__file__))
KAKI = os.path.join(KI, '80_kaki.py')

NAKAMI = (u'★之は第48弾 ㋑ の検体である。★\n'
          u'中身に意味は無い ―― 名と臺帳の書き方だけが検めの的である。\n')
B = NAKAMI.encode('utf-8')
S = hashlib.sha256(B).hexdigest()

for d in ('honmono', 'nise'):
    p = os.path.join(DEST, d)
    if not os.path.isdir(p):
        os.makedirs(p)

KOU_NA = os.path.join(DEST, 'honmono', 'sunao.txt')
OTSU_NA = os.path.join(DEST, 'nise', 'na_ni_sha256=%s_owari.txt' % S)
for p in (KOU_NA, OTSU_NA):
    io.open(p, 'wb').write(B)

GYOU = u'path=%s sha256=%s bytes=%d lines=%d'


def rel(p):
    return os.path.relpath(os.path.abspath(p), os.path.abspath(ROOT))


def kaku(name, rows):
    p = os.path.join(DEST, name)
    r = subprocess.run([sys.executable, '-B', KAKI, p, '--nushi', '85_nise_fixture.py'],
                       input=u'\n'.join(rows), capture_output=True, text=True)
    return p, r.stderr.strip()


KUZUSHI_SHA = u'0' * 64          # ★崩し★ = 臺帳の sha 欄を現物に合はぬ値へ
SEN = (u'# dialect: path= sha256= bytes= lines=  ―― 本形(4欄)。'
       u'此の臺帳は 85_nise_fixture.py が建てた検体である。')

made = []
for na, tag in ((KOU_NA, 'kou'), (OTSU_NA, 'otsu')):
    ok_row = GYOU % (rel(na), S, len(B), B.count(b'\n'))
    ng_row = GYOU % (rel(na), KUZUSHI_SHA, len(B), B.count(b'\n'))
    made.append(kaku('M_%s.txt' % tag, [SEN, ok_row]))
    made.append(kaku('M_%s_kuzushi.txt' % tag, [SEN, ng_row]))

print(u'★現物★')
print(u'  甲(素の名) %s' % rel(KOU_NA))
print(u'  乙(名の中に己の sha) %s' % rel(OTSU_NA))
print(u'  二本とも中身は同一 ―― sha256=%s bytes=%d' % (S, len(B)))
print(u'  ★名に空白は無い★ 甲=%d字 乙=%d字'
      % (len(os.path.basename(KOU_NA)), len(os.path.basename(OTSU_NA))))
print(u'★臺帳 四枚★')
for p, e in made:
    print(u'  %s (bytes=%d)' % (rel(p), os.path.getsize(p)))
    if e:
        print(u'    %s' % e)
print(u'★崩し★ 臺帳の sha 欄を %s… へ替へた丈 ―― 現物にも名にも一字も触れて居らぬ' % KUZUSHI_SHA[:16])
sys.exit(0)
