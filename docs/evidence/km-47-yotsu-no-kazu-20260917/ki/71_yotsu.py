#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 71_yotsu.py -- ★四つの數を四つで出す器★(第47弾 ㋐)。束の中の器であり、生器へは据ゑぬ。
#
# 【何故建てたか】
#   第46弾の納め便で當席は ★本束臺帳230行も旧器222/実体無6→新器229/0★ と書いた。
#   臺帳照合の出目は ★四つ(一致・相違・実体無・讀めぬ行)+母數★ である。
#   當席は旧器を ★二つ(222 と 実体無6)★ で、新器を ★二つ(229 と 0)★ で述べた。
#   消したのではない ―― ★四つの結果を二つで要約した★。
#   讀手には「新器は相違も0であつた」と読める。實は ★相違1(破れの fixture・在つて正しい)★ が在る。
#
# 【形と、其の形を選んだ理由】
#   ⑴ 出す側(fuda): 五つの數を ★一つの札★ にして出し、其の末に
#      ★封=sha16(五つを繋いだ正準文字列)★ を刷る。
#      ―― ★二数要約を構造的に不能にする★ 肝は此處である:
#         封は五つ悉くから導かれる。二つだけを抜き書きすれば封は再現できぬ。
#         ∴ 「札を引く」には五つ全てを運ぶ他ない。抜き書きは ★検め器で必ず落ちる★。
#   ⑵ 検める側(arai): 便の文面から「臺帳照合の出目を述べる span」を取り、★覆ひの條★ で判ずる ――
#      ・完全な札(甲=封の合ふ四数札 / 五欄悉く述べた文)が ★覆ひ★ を成す。
#      ・五欄の内 1〜4 を述べる文は、其の (欄,値) が ★覆ひに在る時に限り★ 許す。無ければ ★赤★。
#      ・欄名を一つも負はぬ裸の數(丙)は、其の紙に ★覆ひが一つも無ければ赤★。在れば ★註★ に留める。
#      ★何故 註に留めるか ―― 器は「四数を★報ずる★文」と「四数を★論ずる★文」を判じ得ぬ。★
#      決し得ぬ條を赤にすれば、器は ★数へ子★ に堕ち、鳴り続けて誰も聞かなくなる。
#      ∴ 「報ずるなら札で」の強制は ★書き手の側★ に置き、器は ★覆ひの有無★ だけを断ずる。
#      ★之は宣言した限りである。★ 覆ひの在る紙の中で、札と食ひ違ふ物語を書く事は此の器では防げぬ。
#      ―― 「一つも述べて居らぬ」は赤にせぬ(便は出目に触れぬ事も在る)。
#         ★一つ以上述べて、五つに満たぬ★ 時のみ赤。之が「要約して消す」の形である。
#   ⑶ 測れなんだ時は ★rc=2(器の誤り)★ ―― 青へは倒さぬ(default-deny)。
#      和(一致+相違+実体無+讀めぬ行)が母數に合はねば ★rc=2★。數が壊れて居る故。
#
# 使ひ方:
#   71_yotsu.py fuda <臺帳> [基点...]          ―― 照合を走らせ 四数札 を出す
#   71_yotsu.py fuda --kikai <verify.py> <臺帳> [基点...]
#   71_yotsu.py arai <便の file>               ―― 便の文面を検める
#   71_yotsu.py --jikenme                      ―― 己を検める(陽性対照・負対照)
import sys, io, os, re, hashlib, subprocess

FIELDS = [u'母數', u'一致', u'相違', u'実体無', u'讀めぬ行']
# 器(verify.py)は「読めぬ行」と刷る。札の正準は「讀めぬ行」。封の前に必ず正規化する。
NORM = {u'読めぬ行': u'讀めぬ行', u'讀めぬ行': u'讀めぬ行',
        u'母数': u'母數', u'母數': u'母數',
        u'實体無': u'実体無', u'実体無': u'実体無',
        u'一致': u'一致', u'相違': u'相違'}
FIELD_RE = u'(?:' + u'|'.join([u'母數', u'母数', u'一致', u'相違', u'実体無', u'實体無',
                               u'讀めぬ行', u'読めぬ行']) + u')'

VERIFY_LINE = re.compile(
    u'一致\\s*★?\\s*(\\d+)\\s*★?\\s*/\\s*相違\\s*(\\d+)\\s*/\\s*'
    u'(?:実体無|實体無)\\s*(\\d+)\\s*/\\s*(?:読めぬ行|讀めぬ行)\\s*(\\d+)'
    u'\\s*\\(\\s*(?:母數|母数)\\s*(\\d+)\\s*\\)')

FUDA_RE = re.compile(
    u'四数札v1\\s+母數=(\\d+)\\s+一致=(\\d+)\\s+相違=(\\d+)\\s+'
    u'実体無=(\\d+)\\s+讀めぬ行=(\\d+)\\s+和検=(\\S+)\\s+封=([0-9a-f]{16})')


def unicode_str(x):
    return u'%d' % x if isinstance(x, int) else u'%s' % x


def seal(bo, ok, ng, miss, unread):
    s = u'四数札v1|母數=%d|一致=%d|相違=%d|実体無=%d|讀めぬ行=%d' % (bo, ok, ng, miss, unread)
    return s, hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def fuda_line(bo, ok, ng, miss, unread):
    wa = ok + ng + miss + unread
    canon, fu = seal(bo, ok, ng, miss, unread)
    wak = u'和=%d=母數' % wa if wa == bo else u'★和=%d≠母數%d★' % (wa, bo)
    return (u'四数札v1 母數=%d 一致=%d 相違=%d 実体無=%d 讀めぬ行=%d 和検=%s 封=%s'
            % (bo, ok, ng, miss, unread, wak, fu)), canon, fu, wa


def nobori():
    u"""己の在處から ★上へ辿つて★ 樹の根を探す(相對の dirname を数へ違へぬ為)。

    由来: 初版は dirname を ★四度★ 重ねて根と看做し、docs/ を根と誤つた
          (實測 2026-09-17: 「器が無い .../docs/scripts/checks/…」)。
          ★数へ違へる形は、束の深さが変る度に黙つて壊れる。★
    """
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(12):
        if os.path.isfile(os.path.join(d, 'scripts', 'checks',
                                       'karo_mac_manifest_verify.py')):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return None


def mode_fuda(argv):
    kikai = None
    if argv and argv[0] == '--kikai':
        if len(argv) < 2:
            sys.stderr.write(u'★測れぬ: --kikai の後に器の path が無い★\n'); return 2
        kikai = argv[1]; argv = argv[2:]
    if not argv:
        sys.stderr.write(u'★測れぬ: 臺帳を argv で渡せ★\n'); return 2
    root = nobori()
    if root is None:
        sys.stderr.write(u'★測れぬ: 樹の根が取れぬ★\n'); return 2
    if kikai is None:
        kikai = os.path.join(root, 'scripts', 'checks', 'karo_mac_manifest_verify.py')
    if not os.path.isfile(kikai):
        sys.stderr.write(u'★測れぬ: 器が無い %s★\n' % kikai); return 2
    # ★基点は必ず明示して渡す★ ―― 器は既定基点を ★己の在處★ から導く故、
    #   束の中へ写した器(verify_AFTER.py)は ★別の根★ を見て「実体無 230」を出す。
    #   實測 2026-09-17: 明示せぬ AFTER 走は 一致0/実体無230 であつた。
    #   ∴ 二つの器へ ★同じ根★ を渡し、出目の差が ★器の差だけ★ に成る様にする。
    tsuka = list(argv)
    if len(tsuka) == 1:
        tsuka = tsuka + [root + os.sep]
    cmd = [sys.executable, '-B', kikai] + tsuka
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = pr.communicate()
    out = out.decode('utf-8', 'replace'); err = err.decode('utf-8', 'replace')
    sys.stdout.write(u'★走らせた★ %s\n' % u' '.join(cmd))
    sys.stdout.write(u'★器の rc★ %d\n' % pr.returncode)
    m = VERIFY_LINE.search(out)
    if not m:
        sys.stdout.write(u'★測れぬ ―― 器の出目から四数の行が取れなんだ★\n')
        sys.stdout.write(u'--- 器の stdout(頭 40 行) ---\n')
        for l in out.splitlines()[:40]:
            sys.stdout.write(l + u'\n')
        sys.stdout.write(u'--- 器の stderr ---\n' + (err or u'(空)\n'))
        return 2
    ok, ng, miss, unread, bo = [int(x) for x in m.groups()]
    line, canon, fu, wa = fuda_line(bo, ok, ng, miss, unread)
    sys.stdout.write(u'★器の四数行(逐語)★ %s\n' % m.group(0))
    sys.stdout.write(u'★正準文字列★ %s\n' % canon)
    sys.stdout.write(line + u'\n')
    if wa != bo:
        sys.stdout.write(u'★rc=2 ―― 和が母數に合はぬ。數が壊れて居る故 青へ倒さぬ★\n')
        return 2
    if ng or miss or unread or ok == 0:
        sys.stdout.write(u'★rc=1 ―― 相違/実体無/讀めぬ行 の何れかが立つ(または一致0)★\n')
        return 1
    sys.stdout.write(u'★rc=0 ―― 四数悉く清し★\n')
    return 0


def spans_of(text):
    u"""便の文面から ★臺帳照合の出目を述べる span★ を取る。

    條(此の器が採る割り方・讀手が判ぜられる様に刷る):
      甲 四数札v1 の行 ―― 一つの span(封まで込み)
      乙 四つの欄名(一致/相違/実体無/讀めぬ行/母數)の何れかを含み、且つ
         ★半角の數字を一字以上含む★ 一文(。 と 改行 で区切る)
         ―― 數字を求めるのは「㋓三本も一致」の如き ★數を述べて居らぬ文★ を
            span に数へぬ為である。★漢数字は讀まぬ ―― 之は宣言した盲である★
      丙 乙に当たらぬが ★數/數★ の群(例 229/0)を含み、且つ同じ文に
         器・臺帳・照合を指す語(器/臺帳/台帳/照合/行)が在る文
    ―― 丙を置いたのは、當席の「新器229/0」が ★欄名を一つも持たぬ★ 故である。
       欄名で拾ふ形だけでは ★最も惡い書き方(欄名を全て落した書き方)が擦り抜ける。★
    """
    out = []
    for m in FUDA_RE.finditer(text):
        out.append((u'甲(四数札)', m.group(0)))
    parts = re.split(u'[。\n]', text)
    for p in parts:
        p = p.strip()
        if not p or u'四数札v1' in p:
            continue
        if re.search(FIELD_RE, p) and re.search(u'[0-9]', p):
            out.append((u'乙(欄名を含む文)', p))
        elif re.search(u'\\d+\\s*/\\s*\\d+', p) and re.search(u'器|臺帳|台帳|照合|行', p):
            out.append((u'丙(數/數の群+器臺帳語)', p))
    return out


def fields_in(span):
    got = {}
    for m in re.finditer(u'(' + FIELD_RE + u')\\s*[=:★]?\\s*(\\d+)', span):
        got[NORM[m.group(1)]] = int(m.group(2))
    return got


def mode_arai(argv):
    if not argv:
        sys.stderr.write(u'\u2605\u6e2c\u308c\u306c: \u4fbf\u306e file \u3092 argv \u3067\u6e21\u305b\u2605\n'); return 2
    path = argv[0]
    if not os.path.isfile(path):
        sys.stderr.write(u'\u2605\u6e2c\u308c\u306c: \u4fbf\u304c\u7121\u3044 %s\u2605\n' % path); return 2
    text = io.open(path, encoding='utf-8', errors='replace').read()
    sys.stdout.write(u'\u2605\u691c\u3081\u305f\u4fbf\u2605 %s (bytes=%d \u884c=%d)\n'
                     % (path, len(text.encode('utf-8')), text.count(u'\n')))
    sys.stdout.write(u'\u2605\u689d\u2605 \u7532=\u56db\u6570\u672d\u306e\u884c / \u4e59=\u6b04\u540d\u3092\u542b\u3080\u6587 / \u4e19=\u6570/\u6570\u306e\u7fa4+\u5668\u81fa\u5e33\u8a9e\n')
    sp = spans_of(text)
    sys.stdout.write(u'\u2605\u51fa\u76ee\u3092\u8ff0\u3079\u308b span\u2605 %d \u672c\n' % len(sp))

    # ---- 一度目: ★覆ひ★ を集める(完全な札だけが覆ひを成す) ----
    ooi = {}            # 欄 -> 覆ひ得る値の集合
    kanzen = 0
    for kind, ss in sp:
        if kind.startswith(u'甲'):
            m = FUDA_RE.search(ss)
            bo, ok, ng, miss, unread = [int(x) for x in m.groups()[:5]]
            if seal(bo, ok, ng, miss, unread)[1] != m.group(7):
                continue            # 封の合はぬ札は覆ひにならぬ
            got = dict(zip(FIELDS, [bo, ok, ng, miss, unread]))
        else:
            got = fields_in(ss)
            if len(got) < 5:
                continue
        kanzen += 1
        for f, v in got.items():
            ooi.setdefault(f, set()).add(v)
    sys.stdout.write(u'\u2605\u8986\u3072\u2605 \u5b8c\u5168\u306a\u672d %d \u672c \u2015\u2015 %s\n'
                     % (kanzen, (u' / '.join([u'%s\u2208{%s}' % (f, u','.join([unicode_str(x) for x in sorted(ooi[f])]))
                                              for f in FIELDS if f in ooi]))
                        or u'\u2605\u4e00\u3064\u3082\u7121\u3057\u2605'))

    aka, chuu = 0, 0
    for i, (kind, s_) in enumerate(sp, 1):
        sys.stdout.write(u'\n[%d] %s\n    %s\n' % (i, kind, s_[:200]))
        if kind.startswith(u'\u7532'):
            m = FUDA_RE.search(s_)
            bo, ok, ng, miss, unread = [int(x) for x in m.groups()[:5]]
            fu = m.group(7)
            canon, want = seal(bo, ok, ng, miss, unread)
            if want == fu:
                sys.stdout.write(u'    \u2605\u5c01 \u5408\u3075\u2605 %s \u2015\u2015 \u4e94\u3064\u6089\u304f\u904b\u3070\u308c\u3066\u5c45\u308b\n' % fu)
            else:
                sys.stdout.write(u'    \u2605\u5c01 \u5408\u306f\u306c\u2605 \u672d=%s \u6b63=%s \u2015\u2015 \u629c\u304d\u66f8\u304d\u304b\u66f8\u304d\u63db\u3078\n' % (fu, want))
                aka += 1
            continue
        got = fields_in(s_)
        have = [f for f in FIELDS if f in got]
        miss_f = [f for f in FIELDS if f not in got]
        nums = re.findall(u'\\d+', s_)
        sys.stdout.write(u'    \u2605\u8ff0\u3079\u305f\u6b04\u2605 %d/5 %s\n'
                         % (len(have), (u'\u30fb'.join([u'%s=%d' % (f, got[f]) for f in have])
                                        or u'(\u4e00\u3064\u3082\u7121\u3057)')))
        if len(have) == 5:
            sys.stdout.write(u'    \u2605\u5b8c\u5168\u2605 \u4e94\u6b04\u6089\u304f\u8ff0\u3079\u3066\u5c45\u308b(\u8986\u3072\u3092\u6210\u3059)\n')
            continue
        sys.stdout.write(u'    \u2605\u843d\u3061\u305f\u6b04\u2605 %s\n' % (u'\u30fb'.join(miss_f) or u'(\u7121\u3057)'))
        sys.stdout.write(u'    \u2605\u6587\u4e2d\u306e\u88f8\u306e\u6570\u2605 %s\n' % (u','.join(nums) or u'(\u7121\u3057)'))
        if have:
            nai = [u'%s=%d' % (f, got[f]) for f in have if got[f] not in ooi.get(f, set())]
            if nai:
                sys.stdout.write(u'    \u2605\u8d64\u2605 \u8986\u3072\u306b\u7121\u3044\u90e8\u5206\u8a00\u53ca = %s \u2015\u2015 \u5b8c\u5168\u306a\u672d\u304c\u540c\u3058\u7d19\u306b\u7121\u3044\n'
                                 % u'\u30fb'.join(nai))
                aka += 1
            else:
                sys.stdout.write(u'    \u8a3b \u90e8\u5206\u8a00\u53ca\u3060\u304c \u2605\u8986\u3072\u306b\u5728\u308b\u2605 \u2015\u2015 \u8a31\u3059\n')
                chuu += 1
        else:
            if kanzen == 0:
                sys.stdout.write(u'    \u2605\u8d64\u2605 \u6b04\u540d\u3092\u8ca0\u306f\u306c\u6570\u3067\u3042\u308a\u3001\u4e14\u3064 \u2605\u3053\u306e\u7d19\u306b\u5b8c\u5168\u306a\u672d\u304c\u4e00\u3064\u3082\u7121\u3044\u2605\n')
                aka += 1
            else:
                sys.stdout.write(u'    \u8a3b \u6b04\u540d\u3092\u8ca0\u306f\u306c\u6570 \u2015\u2015 \u5668\u306f\u300c\u5831\u305a\u308b\u6587\u300d\u3068\u300c\u8ad6\u305a\u308b\u6587\u300d\u3092\u5224\u3058\u5f97\u306c\u3002\u8986\u3072\u6709\u308a\u3086\u3091\u8a31\u3059\n')
                chuu += 1
    sys.stdout.write(u'\n')
    if not sp:
        sys.stdout.write(u'\u2605rc=0 \u2015\u2015 \u51fa\u76ee\u3092\u8ff0\u3079\u308b span \u304c\u4e00\u3064\u3082\u7121\u3044(\u4fbf\u304c\u7167\u5408\u306b\u89e6\u308c\u3066\u5c45\u3089\u306c)\u2605\n')
        return 0
    if aka:
        sys.stdout.write(u'\u2605rc=1(\u8d64) \u2015\u2015 \u8986\u3072\u306e\u7121\u3044 span \u304c %d \u672c\u3002\u2605\u56db\u3064\u306e\u7d50\u679c\u3092\u4e8c\u3064\u3067\u8981\u7d04\u3057\u3066\u5c45\u308b\u2605\n' % aka)
        sys.stdout.write(u'  \u76f4\u3057\u65b9: \u56db\u6570\u672dv1 \u306e\u4e00\u884c\u3092\u5176\u306e\u5118 \u8cbc\u308c\u3002\u5c01\u304c\u4e94\u3064\u3092\u7e1b\u308b\u6545 \u629c\u304d\u66f8\u304d\u3067\u304d\u306c\u3002\n')
        return 1
    sys.stdout.write(u'\u2605rc=0 \u2015\u2015 \u51fa\u76ee\u3092\u8ff0\u3079\u308b span \u306f\u6089\u304f \u2605\u8986\u3072\u306e\u4e0b\u2605(\u5b8c\u5168\u306a\u672d %d \u672c / \u8a3b %d \u672c)\u2605\n'
                     % (kanzen, chuu))
    return 0


def mode_jikenme():
    u"""己を検める ―― ★陽性対照が鳴かねば器では無い★。"""
    import tempfile
    rcs = []
    kata = [
        (u'陽性甲: 二数要約(當席の第46弾の形)',
         u'本束臺帳230行も旧器222/実体無6→新器229/0。', 1),
        (u'陽性乙: 欄名を一つも持たぬ數の群',
         u'新器の出目は 229/0 であつた(臺帳の行)。', 1),
        (u'陽性丙: 四つ書いて母數を落した',
         u'一致229 相違1 実体無0 讀めぬ行0 であつた。', 1),
        (u'陽性丁: 封を書き換へた札',
         u'四数札v1 母數=230 一致=229 相違=1 実体無=0 讀めぬ行=0 和検=和=230=母數 封=0000000000000000', 1),
        (u'負対照甲: 正しい四数札',
         fuda_line(230, 229, 1, 0, 0)[0], 0),
        (u'負対照乙: 照合に触れぬ便',
         u'着手した。宣ETA は六時十五分である。', 0),
        (u'負対照丙: ★覆ひの下の部分言及★(赤にしてはならぬ形)',
         fuda_line(230, 229, 1, 0, 0)[0]
         + u'\n上の札の通り、相違=1 が在る事は fixture の破れゆゑ正しい ―― 疵ではない。'
         + u'\n新器の出目は 229/0 であつた、と第46弾は書いた(裸の數の引用)。', 0),
    ]
    for name, body, want in kata:
        fd, p = tempfile.mkstemp(suffix='.txt'); os.close(fd)
        io.open(p, 'w', encoding='utf-8').write(body + u'\n')
        sys.stdout.write(u'\n==== %s ==== (望む rc=%d)\n' % (name, want))
        rc = mode_arai([p])
        os.unlink(p)
        sys.stdout.write(u'---- 出た rc=%d / 望む rc=%d ―― %s\n'
                         % (rc, want, u'合ふ' if rc == want else u'★合はぬ★'))
        rcs.append(rc == want)
    sys.stdout.write(u'\n★自検め★ %d/%d 合ふ\n' % (sum(1 for x in rcs if x), len(rcs)))
    return 0 if all(rcs) else 1


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'★測れぬ: fuda / arai / --jikenme の何れかを渡せ★\n'); return 2
    if argv[1] == 'fuda':
        return mode_fuda(argv[2:])
    if argv[1] == 'arai':
        return mode_arai(argv[2:])
    if argv[1] == '--jikenme':
        return mode_jikenme()
    sys.stderr.write(u'★測れぬ: 知らぬ口 %s★\n' % argv[1]); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
