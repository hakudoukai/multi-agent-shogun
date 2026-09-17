#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""73_seigyo.py -- ★㋒ 陽性対照★ ―― 「破れの fixture を直せば 230/相違0 に成る」を實測する器。

★fixture 其物には一字も触れぬ。★ 触れれば第46弾の主題(=讀手の疵)が disk から消える。
代りに ⑴同じ中身の ★直した写し★ を別 path へ建て ⑵臺帳の其の一行だけを写しへ向けた
★対照用の臺帳★ を機械で作り ⑶同じ器で両方を測る。

直し方(★何を直したのかを一語で言へる様に★):
  名の中の `sha256=` を `sha256_` へ改める ―― ★中身も byte 数も行数も変へぬ。名だけ。★
  ∵ 相違の機は「sha 欄の抽出が ★名の中の 64hex★ を先に掴む」事に在る。名から其の形を除けば鳴らぬ。

★之は偽の通過である。★ 直したのは ★器ではなく検体★ である。
  器の sha 欄抽出は依然 ★最初の sha256=★ を取る。次に同じ形の名が来れば ★同じ様に黙つて誤る。★

使ひ方: 73_seigyo.py <km-46 の臺帳> <km-47 の束> [<repo 根>]
"""
import io, os, re, sys, hashlib, subprocess

if len(sys.argv) < 3:
    sys.stderr.write(u'★測れぬ: <臺帳> <km-47 の束> を argv で渡せ★\n'); sys.exit(2)
MAN, B47 = sys.argv[1], sys.argv[2]
ROOT = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
KI = os.path.dirname(os.path.abspath(__file__))
KAKI = os.path.join(KI, '70_kaki.py')
HEX = re.compile(u'sha256=([0-9a-f]{64})')
GYOU = re.compile(u'^path=(?:"(.+)"|(\\S+))\\s+sha256=([0-9a-f]{64})\\s+bytes=(\\d+)\\s+lines=(\\d+)\\s*$')

src = io.open(MAN, encoding='utf-8').read().split(u'\n')
NAOSHI = os.path.join(B47, 'fixture', 'naoshita')

out, utsushi = [], []
bo = 0
for l in src:
    if not l.strip():
        continue
    bo += 1
    m = GYOU.match(l)
    if not m:
        out.append(l); continue
    na = m.group(1) if m.group(1) is not None else m.group(2)
    sen, by, gy = m.group(3), int(m.group(4)), int(m.group(5))
    # ★直す条件★ = 名の中に 64hex の sha256= を持つ行(= sha 欄抽出を破る形)のみ
    if not HEX.search(na):
        out.append(l); continue
    ap = os.path.join(ROOT, na)
    if not os.path.isfile(ap):
        out.append(l)
        utsushi.append((na, None, u'★写せぬ ―― disk に現物が無い★'))
        continue
    atara_na = os.path.basename(na).replace(u'sha256=', u'sha256_')
    oya = os.path.join(NAOSHI, os.path.basename(os.path.dirname(na)))
    if not os.path.isdir(oya):
        os.makedirs(oya)
    dest = os.path.join(oya, atara_na)
    nakami = io.open(ap, 'rb').read()
    io.open(dest, 'wb').write(nakami)
    ima = hashlib.sha256(nakami).hexdigest()
    rel = os.path.relpath(os.path.abspath(dest), os.path.abspath(ROOT))
    out.append(u'path="%s" sha256=%s bytes=%d lines=%d' % (rel, ima, len(nakami), nakami.count(b'\n')))
    utsushi.append((na, rel, u'中身同一 sha=%s… bytes=%d' % (ima[:16], len(nakami))))

AN = os.path.join(B47, 'an', 'seigyo')
if not os.path.isdir(AN):
    os.makedirs(AN)
TAI = os.path.join(AN, 'taishou_manifest.txt')
subprocess.run([sys.executable, '-B', KAKI, TAI, '--nushi', '73_seigyo.py'],
               input=u'\n'.join(out), capture_output=True, text=True)

print(u'= 元の臺帳 %s (行 %d)' % (MAN, bo))
print(u'= 対照の臺帳 %s (行 %d bytes=%d)'
      % (TAI, len(out), os.path.getsize(TAI)))
print(u'= ★直した写し★ %d 本 ―― ★元の fixture には一字も触れて居らぬ★' % len([u for u in utsushi if u[1]]))
for a, b, c in utsushi:
    print(u'  元 %s' % a)
    print(u'  写 %s   %s' % (b if b else u'(無し)', c))
print()

VER = os.path.join(ROOT, 'docs', 'evidence', 'km-46-yomite-no-kizu-20260917', 'patch', 'verify_AFTER.py')
FUDA = os.path.join(KI, '71_yotsu.py')


def hakaru(na, man):
    r = subprocess.run([sys.executable, '-B', FUDA, 'fuda', '--kikai', VER, man, ROOT],
                       capture_output=True, text=True)
    print(u'-- %s --' % na)
    for l in r.stdout.split(u'\n'):
        if l.strip():
            print(u'   %s' % l)
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.returncode


rc_moto = hakaru(u'★元の臺帳(破れの fixture 在り)★', MAN)
rc_tai = hakaru(u'★対照の臺帳(直した写しへ向けた)★', TAI)
print()
print(u'★元の rc=%d / 対照の rc=%d★' % (rc_moto, rc_tai))
print()
print(u'== ★之が偽の通過である理由★ ==')
print(u'  ⑴ 直したのは ★検体(fixture の名)★ であつて ★器(sha 欄の抽出)★ ではない。')
print(u'  ⑵ 器は今も ★行の最初の sha256=★ を欄として取る。名の中に 64hex が在れば ★其れを録 sha と読む。★')
print(u'  ⑶ ∴ 対照が 相違0 を出したのは ★器が直つたから★ ではなく ★器を破る検体を除けたから★ である。')
print(u'  ⑷ ★次に同じ形の名が来れば、器は同じ様に黙つて誤る ―― 然も今度は鳴らす検体が無い。★')
print(u'  ⑸ 相違1 は疵ではなく ★器の破れが未だ在る事の唯一の證★ である。消せば證が消えるだけである。')
sys.exit(0)
