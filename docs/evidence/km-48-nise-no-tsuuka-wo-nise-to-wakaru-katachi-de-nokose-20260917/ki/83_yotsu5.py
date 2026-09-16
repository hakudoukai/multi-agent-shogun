#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""83_yotsu5.py -- ★五つ目の數「跳」を足す器★(第48弾 ㋒)。束の中の器であり、生器へは据ゑぬ。

【何故建てたか ―― 專任1 が名指した欄の欠】
  逐語(第68弾㋓):「四数札に ★何行を跳んだか★ の欄が無い」。
  四つの數(母數/一致/相違/実体無/讀めぬ行)は ★歩いた行★ を割る。
  ★跳んだ行は一つも数へられて居らぬ。★ ∴ 跳が増えても四つの數は一指も動かぬ。

【跳は二種である ―― 之を割らねば「跳N」は診立てに成らぬ】
  跳甲 = 空行・`#` で始まる註行。
        ―― ★宣言済★(karo_mac_manifest_verify.py 頭註 L22 逐語「# で始まる行は註(基点の宣言など)ゆゑ数へぬ」)。
  跳乙 = 跳甲に非ず、且つ ★行に `sha256=<64hex>` が無い★ 行(器 L131-133 `if not m: continue`)。
        ―― ★宣言されて居らぬ。★ 頭註にも rc の條にも現れぬ。
        之が起きると ★臺帳に書いた一行が、照合されず・数へられず・鳴らずに消える★。
        母數は黙つて縮む。讀手には「其の行は初めから無かつた」と見える。

【和の條(此の器が己に課す檢め)】
  跳甲 + 跳乙 + 母數 == ★器が讀んだ全行★(file を器と同じ形で回した行數)
  合はねば ★rc=2★ ―― 青へは倒さぬ(default-deny)。數の割り方が壊れて居る故。

【封】
  五数札v1 と同じ趣旨 ―― 封は ★六つ悉く★(母數/一致/相違/実体無/讀めぬ行/跳)から導く。
  抜き書きすれば封が再現できぬ。∴ 「跳だけ落として引く」が檢出可能に成る。

使ひ方:
  83_yotsu5.py fuda [--kikai <verify.py>] <臺帳> [基点...]
  83_yotsu5.py tobi <臺帳>                       ―― 跳の内訳だけを出す(逐語つき)
"""
import sys
sys.dont_write_bytecode = True      # ★生器の隣へ __pycache__ を書かぬ為(作法⑴ 生器への変更0)★
import io, os, re, hashlib, subprocess

FIELDS = [u'母數', u'一致', u'相違', u'実体無', u'讀めぬ行', u'跳']

VERIFY_LINE = re.compile(
    u'一致\\s*★?\\s*(\\d+)\\s*★?\\s*/\\s*相違\\s*(\\d+)\\s*/\\s*'
    u'(?:実体無|實体無)\\s*(\\d+)\\s*/\\s*(?:読めぬ行|讀めぬ行)\\s*(\\d+)'
    u'\\s*\\(\\s*(?:母數|母数)\\s*(\\d+)\\s*\\)')

FUDA5_RE = re.compile(
    u'五数札v1\\s+母數=(\\d+)\\s+一致=(\\d+)\\s+相違=(\\d+)\\s+'
    u'実体無=(\\d+)\\s+讀めぬ行=(\\d+)\\s+跳=(\\d+)\\s*\\(甲(\\d+)/乙(\\d+)\\)'
    u'\\s+和検=(\\S+)\\s+封=([0-9a-f]{16})')


def nobori():
    u"""己の在處から上へ辿つて樹の根を探す(第47弾 71_yotsu.py の nobori() を踏襲)。"""
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for _ in range(12):
        if os.path.isfile(os.path.join(d, 'scripts', 'checks',
                                       'karo_mac_manifest_verify.py')):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return None


def sha_re_of(kikai):
    u"""★器自身の SHA 正規表現を器の源から取る★ ―― 書き写さぬ。

    書き写せば ★器が変つた時に此の器だけ古いまま黙る★。
    取れなんだ時は ★測れぬ(None)★ を返す ―― 己で似た物を拵へて代用せぬ。
    """
    try:
        src = io.open(kikai, encoding='utf-8', errors='replace').read()
    except Exception:
        return None, u'器の源が讀めぬ'
    m = re.search(u'^SHA\\s*=\\s*re\\.compile\\(r?["\'](.+?)["\']\\)\\s*$',
                  src, re.M)
    if not m:
        return None, u'器の源から SHA = re.compile(...) の一行が取れぬ'
    try:
        return re.compile(m.group(1)), m.group(1)
    except Exception:
        return None, u'取れた綴りが正規表現に成らぬ: %s' % m.group(1)


def tobi_of(man, kikai):
    u"""★器と同じ回し方★ で臺帳を回し、跳甲/跳乙/歩いた行 を割る。

    器 L114-133 の逐語:
        for raw in open(man, encoding="utf-8", errors="replace"):
            line = raw.strip()
            if not line or line.startswith("#"):   continue   ← ★跳甲★
            ...
            m = SHA.search(line)
            if not m:                              continue   ← ★跳乙★
    ∴ 此處で再び綴るのは ★跳の二つの述語だけ★ である。
       照合(path 取り・disk 当て・sha 比べ)は一字も写さぬ ―― 其れは器の仕事。
    """
    sha, note = sha_re_of(kikai)
    if sha is None:
        return None, note
    kou, otsu, aruita = 0, 0, 0
    kou_rows, otsu_rows = [], []
    zen = 0
    for raw in io.open(man, encoding='utf-8', errors='replace'):
        zen += 1
        line = raw.strip()
        if not line or line.startswith(u'#'):
            kou += 1
            if len(kou_rows) < 8:
                kou_rows.append(line[:90] if line else u'(空行)')
            continue
        if not sha.search(line):
            otsu += 1
            if len(otsu_rows) < 8:
                otsu_rows.append(line[:90])
            continue
        aruita += 1
    return (zen, kou, otsu, aruita, kou_rows, otsu_rows), note


def seal(vals):
    s = u'五数札v1|' + u'|'.join([u'%s=%d' % (f, v) for f, v in zip(FIELDS, vals)])
    return s, hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def fuda_line(bo, ok, ng, miss, unread, kou, otsu):
    tobi = kou + otsu
    wa = ok + ng + miss + unread
    canon, fu = seal([bo, ok, ng, miss, unread, tobi])
    wak = (u'和=%d=母數・跳和=%d=甲%d+乙%d' % (wa, tobi, kou, otsu)
           if wa == bo else u'★和=%d≠母數%d★' % (wa, bo))
    return (u'五数札v1 母數=%d 一致=%d 相違=%d 実体無=%d 讀めぬ行=%d 跳=%d(甲%d/乙%d) 和検=%s 封=%s'
            % (bo, ok, ng, miss, unread, tobi, kou, otsu, wak, fu)), canon, fu


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
    man = argv[0]
    if not os.path.isfile(man):
        sys.stderr.write(u'★測れぬ: 臺帳が無い %s★\n' % man); return 2
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

    t, note = tobi_of(man, kikai)
    if t is None:
        sys.stdout.write(u'★測れぬ ―― 跳が割れぬ: %s★\n' % note)
        return 2
    zen, kou, otsu, aruita, kou_rows, otsu_rows = t
    sys.stdout.write(u'★器の四数行(逐語)★ %s\n' % m.group(0))
    sys.stdout.write(u'★器の SHA 綴り(器の源から取つた)★ %s\n' % note)
    sys.stdout.write(u'★臺帳を器と同じ形で回した★ 全行=%d 跳甲(空/註)=%d 跳乙(sha欄無)=%d 歩いた=%d\n'
                     % (zen, kou, otsu, aruita))
    line, canon, fu = fuda_line(bo, ok, ng, miss, unread, kou, otsu)
    sys.stdout.write(u'★正準文字列★ %s\n' % canon)
    sys.stdout.write(line + u'\n')

    # ---- 己の檢め(default-deny) ----
    if aruita != bo:
        sys.stdout.write(u'★rc=2 ―― 己が数へた歩いた行 %d と 器の母數 %d が合はぬ。'
                         u'跳の割り方が器と食ひ違つて居る★\n' % (aruita, bo))
        return 2
    if kou + otsu + bo != zen:
        sys.stdout.write(u'★rc=2 ―― 跳甲%d+跳乙%d+母數%d=%d が全行%d に合はぬ★\n'
                         % (kou, otsu, bo, kou + otsu + bo, zen))
        return 2
    if ok + ng + miss + unread != bo:
        sys.stdout.write(u'★rc=2 ―― 四数の和が母數に合はぬ。數が壊れて居る故 青へ倒さぬ★\n')
        return 2

    if otsu:
        sys.stdout.write(u'\n★跳乙 %d 行 ―― 之が起きて居る時、何が起きて居るのか★\n' % otsu)
        sys.stdout.write(u'  ★臺帳に書いた行が、照合されず・四つの數の何れにも数へられず・鳴りもせずに消えて居る'
                         u'(母數が黙つて縮んだ)。★\n')
        for r in otsu_rows:
            sys.stdout.write(u'    ★跳乙★ %s\n' % r)
        if otsu > len(otsu_rows):
            sys.stdout.write(u'    … 他 %d 行\n' % (otsu - len(otsu_rows)))
    if kou:
        for r in kou_rows[:3]:
            sys.stdout.write(u'    跳甲 %s\n' % r)
        if kou > 3:
            sys.stdout.write(u'    … 他 %d 行(跳甲は ★宣言済★ ゆゑ赤にせぬ)\n' % (kou - 3))

    if otsu:
        sys.stdout.write(u'★rc=1 ―― 跳乙が立つ(宣言されて居らぬ跳)★\n')
        return 1
    if ng or miss or unread or ok == 0:
        sys.stdout.write(u'★rc=1 ―― 相違/実体無/讀めぬ行 の何れかが立つ(または一致0)★\n')
        return 1
    sys.stdout.write(u'★rc=0 ―― 五数悉く清し★\n')
    return 0


def mode_tobi(argv):
    if not argv:
        sys.stderr.write(u'★測れぬ: 臺帳を argv で渡せ★\n'); return 2
    root = nobori()
    if root is None:
        sys.stderr.write(u'★測れぬ: 樹の根が取れぬ★\n'); return 2
    kikai = os.path.join(root, 'scripts', 'checks', 'karo_mac_manifest_verify.py')
    t, note = tobi_of(argv[0], kikai)
    if t is None:
        sys.stdout.write(u'★測れぬ: %s★\n' % note); return 2
    zen, kou, otsu, aruita, kr, orow = t
    sys.stdout.write(u'臺帳 %s\n  全行=%d 跳甲=%d 跳乙=%d 歩いた=%d\n' % (argv[0], zen, kou, otsu, aruita))
    for r in orow:
        sys.stdout.write(u'  ★跳乙★ %s\n' % r)
    return 1 if otsu else 0


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'★測れぬ: fuda / tobi の何れかを渡せ★\n'); return 2
    if argv[1] == 'fuda':
        return mode_fuda(argv[2:])
    if argv[1] == 'tobi':
        return mode_tobi(argv[2:])
    sys.stderr.write(u'★測れぬ: 知らぬ口 %s★\n' % argv[1]); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
