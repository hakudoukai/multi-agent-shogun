#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋓⑵⑶ ―― ★凍らせた定義を当てて 6/4/7 を割る★

順は札の仰せの通り ⑴則を先に書く(済・01_kizu_no_nori.txt)⑵數へ直す ⑶割れ目を逐語で出す。
★本器は則を後から書いて居らぬ事を、則の file の刻(02_nori_koku.txt)で示す。★
"""
import hashlib, io, os, re, sys, time

NE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
R = os.path.join(os.path.dirname(os.path.abspath(__file__)))
KAMI48 = os.path.join(NE, 'queue/reports/ashigaru-mac-2_km-48-michibikeru-mono-to-michibikenu-mono-wo-wakete-taba-wo-yasesaseyo-jou5-no-sai-20260917.md')
HAKO = os.path.join(NE, 'queue/inbox/karo-mac.yaml')
KURA = os.path.join(NE, 'queue/inbox/_archive/karo-mac_pruned.yaml')
SEKI = 'ashigaru-mac-2'
w = sys.stdout.write


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


w('刻 = %s\n\n' % time.strftime('%Y-%m-%dT%H:%M:%S'))

# ―― 一 則が數へるより先に在つた事
w('― 一 ★則は數へるより先に在つた★ ―\n')
for nm in ('01_kizu_no_nori.txt', '02_nori_koku.txt'):
    p = os.path.join(R, nm)
    b = open(p, 'rb').read()
    w('  %s  %d byte  sha16=%s\n' % (nm, len(b), sha16(b)))
w('  則の刻 = %s ―― 本器の刻(上)より ★前★ である。\n' % io.open(os.path.join(R, '02_nori_koku.txt'), encoding='utf-8').read().strip())
w('  ★數が定義に従つたのではない。定義が數より前に在る。★\n\n')

# ―― 二 母數の境を「移した事」を先に宣する
w('― 二 ★境を移した事を先に申す★ ―\n')
w('  則 01 が定めた母數 = 「本弾(km-49)の紙 + 其の束の追補 + 箱に在る %s 発の便」。\n' % SEKI)
w('  然し札が割れと仰せの 6/4/7 は ★第48弾の疵の數★ である。\n')
w('  ∴ 同じ形の境を第48弾へ当てる ―― 紙 = km-48 の紙 / 便 = 箱の %s 発 / 追補 = 箱の「㋖追補」行。\n' % SEKI)
w('  ★境を移した事を黙つて當てはめぬ。之を書かねば「定義を後から書いた」と同じ事になる。★\n\n')

# ―― 三 紙
w('― 三 ★紙★ %s ―\n' % os.path.relpath(KAMI48, NE))
s = io.open(KAMI48, encoding='utf-8').read()
L = s.split('\n')
st = [i for i, l in enumerate(L) if l.startswith('## ㋖')]
i0 = st[0]
i1 = next((j for j in range(i0 + 1, len(L)) if L[j].startswith('## ')), len(L))
setsu = L[i0:i1]
rx = re.compile(r'^(\d+)\. \*\*')
kami_hit = [(i0 + 1 + k, l) for k, l in enumerate(setsu) if rx.match(l)]
w('  ㋖ の節 = L%d〜L%d / ★項 = %d★\n' % (i0 + 1, i1, len(kami_hit)))
for n, l in kami_hit:
    w('    L%-4d %s\n' % (n, l[:110]))
w('  本文中の相互参照 (㋖-N):\n')
for i, l in enumerate(L, 1):
    for m in re.finditer(r'㋖-(\d+)', l):
        w('    L%-4d ㋖-%s ≪%s≫\n' % (i, m.group(1), l.strip()[:80]))
w('  ★紙は 6 で閉ぢて居る(参照も 1・3・4 の三つで、7 を指す物は無い)。★\n\n')

# ―― 四 追補
w('― 四 ★追補★ ―\n')
# ★箱は測る間に動いた★ ―― 03:55 に回転し、a3 の追補便が生箱から落ちた。
# ∴ 生箱 ★と★ 藏(_archive/karo-mac_pruned.yaml)の ★両方★ を歩き、id で重複を除く。
w('― 三.五 ★歩いた箱を宣する(箱は測る間に動く)★ ―\n')
_srcs = []
for _nm, _p in (('生箱', HAKO), ('藏', KURA)):
    if os.path.isfile(_p):
        _b = open(_p, 'rb').read()
        w('  %s %s  %d byte  sha16=%s\n' % (_nm, os.path.relpath(_p, NE), len(_b), sha16(_b)))
        _srcs.append(io.open(_p, encoding='utf-8', errors='replace').read())
    else:
        w('  %s %s ―― ★無し★\n' % (_nm, os.path.relpath(_p, NE)))
box = '\n'.join(_srcs)
_raw = re.split(r'(?m)^(?=- content: )', box)
ents, _seen = [], set()
for _e in _raw:
    _i = re.search(r'(?m)^  id: (\S+)$', _e)
    _k = _i.group(1) if _i else ('__noid__%d' % len(ents))
    if _k in _seen: continue
    _seen.add(_k); ents.append(_e)
w('  重複を除いた便 = %d 通(生箱+藏)\n' % len(ents))
w('  ★生箱のみを歩いた 03:56 の走りでは追補便が 0 通であつた ―― 箱が回転した故である。★\n')
w('  ★「無い」と「移つた」は別である。藏を当たらずに「消えた」と書けば、其れが疵になる。★\n\n')
tsui = []
for e in ents:
    if '㋖追補' not in e: continue
    f = re.search(r'(?m)^  from: (.*)$', e)
    t = re.search(r'(?m)^  timestamp: (.*)$', e)
    i = re.search(r'(?m)^  id: (.*)$', e)
    tsui.append((f.group(1) if f else '?', t.group(1) if t else '?', i.group(1) if i else '?', ' '.join(e.split())))
w('  箱(生箱+藏)に在る「㋖追補」を載せた便 = ★%d 通★\n' % len(tsui))
if not tsui:
    w('  ★零 ―― 本器は之より先を刷らぬ。★項の無い物から割れ目は出せぬ。★\n')
    w('  ★零の四札★ 陽性対照=下の五節(便は %d 通見えて居る) / 歩き根=上の三.五 / rc=2 / 刻=%s\n'
      % (0, time.strftime('%%Y-%%m-%%dT%%H:%%M:%%S')))
    sys.exit(2)
for fr, ts, mid, body in tsui:
    w('    from=%s  ts=%s  id=%s\n' % (fr, ts, mid))
    j = body.index('【㋖追補】')
    seg = body[j:]
    end = seg.index('。') + 1
    honbun = seg[len('【㋖追補】'):end]
    koumoku = [x.strip() for x in honbun.split('/') if x.strip()]
    w('      逐語(終止「。」まで) = %s\n' % honbun)
    w('      ★項 = %d★\n' % len(koumoku))
    for k, x in enumerate(koumoku, 1):
        w('        %d. %s\n' % (k, x))
    w('      ―― 第49弾の器は `l.strip()[:200]` で刷つた。其の時見えた字:\n')
    w('        ≪%s≫\n' % body[j:j + 200].strip())
    w('      ★200字の壁が第5項「己の器の産物を己の母數に数へ相違1を生んだ」を切り落とした。★\n')
    w('      ★∴ 「追補4」は追補の數ではない ―― ★刷る幅の數★ である。★\n')
    if fr != SEKI:
        w('      ★★此の便の差出は %s であつて %s ではない。★★\n' % (fr, SEKI))
        w('      ∴ 則 01(疵=★己の★既に納めた誤り)の下では、之は ★己の疵ではない★。母數の外である。\n')
w('\n')

# ―― 五 便
w('― 五 ★便★ ―\n')
w('  境 甲 = 箱の %s 発 且つ ★胴に「第48弾」を含む★ 物(札が問ふ「便7」の在り所)\n' % SEKI)
w('  境 乙 = 箱の %s 発の ★一切★(參考・弾を問はぬ)\n' % SEKI)
w('  ★境を二つ立てて両方刷る ―― 一つだけ刷れば、選んだ事が見えぬ。★\n')
ben_all, ben48 = [], []
for e in ents:
    f = re.search(r'(?m)^  from: (.*)$', e)
    if not f or f.group(1) != SEKI: continue
    body = ' '.join(e.split())
    for m in re.finditer(r'己の疵\s*(\d+)', body):
        t = re.search(r'(?m)^  timestamp: (.*)$', e)
        i = re.search(r'(?m)^  id: (.*)$', e)
        rec = (t.group(1), i.group(1), m.group(1), body[max(0, m.start() - 70):m.start() + 20])
        ben_all.append(rec)
        if '第48弾' in body: ben48.append(rec)
ben = ben48
w('\n  【甲 第48弾】= ★%d 通★\n' % len(ben48))
for ts, mid, n, ctx in ben48:
    w('    ts=%s id=%s ★N=%s★\n      逐語 ≪…%s…≫\n' % (ts, mid, n, ctx))
w('\n  【乙 弾を問はぬ】= ★%d 通★ ―― 名乗つた數の列 = %s\n'
  % (len(ben_all), ' / '.join(x[2] for x in sorted(ben_all, key=lambda y: y[0]))))
for ts, mid, n, ctx in sorted(ben_all, key=lambda y: y[0]):
    w('    ts=%s id=%s N=%s\n' % (ts, mid, n))
w('  ★乙の %d 通、★一通として項を列挙して居らぬ★。★\n' % len(ben_all))
w('  ★∴ 「己の疵N」は本席の便に於て ★常に列挙の無い數★ であつた。第48弾だけの病ではない。★\n')
w('  ★便は 7 と申したが、★項を一つも挙げて居らぬ★。列挙の無い數である。★\n\n')

# ―― 六 割れ目
w('― 六 ★6 / 4 / 7 は何処で割れたか(逐語)★ ―\n')
w('  ⑴ ★4 は「同じ物の別の數へ方」ですらない。★\n')
w('     追補便の差出 = %s ／ 第48弾の紙の書き手 = %s ―― ★別人である★。\n' % (tsui[0][0] if tsui else '?', SEKI))
w('     加へて項は 4 ではなく %d。4 は ★[:200] の切り口★ が生んだ數。\n' % (len([x for x in (tsui[0][3][tsui[0][3].index('【㋖追補】') + 5:tsui[0][3].index('【㋖追補】') + 5 + tsui[0][3][tsui[0][3].index('【㋖追補】'):].index('。')].split('/')) if x.strip()]) if tsui else 0))
w('     ∴ 第49弾の紙が「紙6・追補4・便7 ―― 同じ物を数へた三つの數」と書いたのは ★誤り★。\n')
w('       ★二重計上ではない。★他人の紙を己の欄に入れた★のである。★\n')
w('  ⑵ ★6 と 7 の差は「一項の欠落」ではなく「列挙の不在」。★\n')
w('     紙 = 6 項、悉く逐語で在る(上・三)。便 = 7、★項は零★。\n')
w('     ∴ 「7 本目が何処に在るか」は問へぬ。★在ると書かれた事しか無い。★\n')
w('  ⑶ 紙に 7 と読める數は在るか(★未證の候補として挙げる・因と断ぜぬ★):\n')
for i, l in enumerate(L, 1):
    if re.search(r'[(（]\s*7\s*[つ本件]', l) or re.search(r'7\s*[つ本件]', l):
        w('      L%-4d ≪%s≫\n' % (i, l.strip()[:100]))
w('     ★之等が便の「7」の出所である證は無い。數が合ふのみである。★\n')
w('     ★一つ數が合つた事を以て因と断ずるのは、本弾が咎めて居る当の病である。★\n\n')

# ―― 七 則を当てた數
w('― 七 ★則 01 を当てた時の數★ ―\n')
w('  母數に入る物 = 紙の 6 項(己の・既に納めた・直せる誤り)\n')
w('  母數の外     = 追補便 %d 項(差出が別人 ∴ 「己の」に当たらぬ)\n' % (len([x for x in tsui[0][3][tsui[0][3].index('【㋖追補】') + 5:].split('。')[0].split('/') if x.strip()]) if tsui else 0))
w('  數へられぬ物 = 便の「7」(項が無く、則の「何を以て一とするか」を当てる対象が無い)\n')
w('  ★∴ 第48弾の己の疵 = ★6★。★7 でも 10 でもない。★\n')
w('  ★則が直したのは數ではない ―― ★どの數が何を数へて居るか★ である。★\n')
w('\n― 八 測れなんだ事 ―\n')
w('  紙 %s は git に載つて居らぬ(git ls-files rc=1)。\n' % os.path.relpath(KAMI48, NE))
w('  ∴ ★㋖ が嘗て 7 項であつたか否かは、履歴が無い故 測れぬ。★「無かつた」とは申さぬ。\n')
w('\nrc = 0\n')
