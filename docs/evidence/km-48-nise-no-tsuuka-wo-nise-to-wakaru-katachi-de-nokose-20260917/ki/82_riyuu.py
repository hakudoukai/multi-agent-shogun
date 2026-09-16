#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""82_riyuu.py -- ★札に「何故通つたか」の欄を足す器★(第48弾 ㋑)。束の中の器であり、生器へは据ゑぬ。

【何故建てたか】
  第47弾の四数札(及び本弾の五数札)は ★通つた事★ を書く。★何故通つたかを書かぬ。★
  ㋒ の一件が其の實例である ―― 對照は 230/230/0/0 rc=0 を出したが、
  其れは ★器が直つたから★ ではなく ★器を破る検体を臺帳から除けたから★ であつた。
  ★札の上では、本物の通過と見分けが付かぬ。★

【足した二欄(下命の最低限)】
  ⑴ 固定 ―― 其の走が何を固定して居るか。
       ・宣(kotei)   = 書き手が一語で述べた固定
       ・出所(demae) = 臺帳が ★元の物★ か ★元から作り変へた対照★ か(★行の差で機械が割る★)
       ・器/臺帳/基点 = 四数を生んだ三つの素性(sha16 付き)
  ⑵ 崩 ―― 固定が崩れた時に ★鳴るか黙るか★。★宣言ではなく實測である。★
       同じ器・同じ基点で ★崩した臺帳★ を走らせ、五数札の正準文字列を比べる:
         変つた → ★鳴★ / 変らぬ → ★黙★
       ★黙は「其の通過が固定を一度も見て居らぬ」事の直接の證である。★

【判じ方(rc)】
  rc=0 ―― 五数清し・崩=鳴・出所=原     ★本物の通過★
  rc=1 ―― 崩=黙、または出所=対照、または五数に赤 ★偽と判る通過、若しくは赤★
  rc=2 ―― 測れなんだ(五数札が取れぬ等)。青へは倒さぬ。

【封】
  封は ★十一欄悉く★(六數+器+臺帳+基点+固定+崩+出所)から導く。
  ∴ 「通つた」だけを抜き書きすれば封が再現できぬ ―― 理由を落した引用が檢出可能に成る。

【此の器が塞げぬ物(宣言した限り)】
  ・崩しは ★書き手が渡した一つ★ である。渡さなんだ崩し方は測つて居らぬ。
  ・固定の「宣」は文字列であり、器は其の当否を判じ得ぬ(出所と崩だけが實測である)。

使ひ方:
  82_riyuu.py [--kikai <verify.py>] --kotei "<一語>" --kuzushi <崩した臺帳>
              [--moto <元の臺帳>] <臺帳> [基点...]
  82_riyuu.py --jikenme <repo根>          ―― 己を検める(陽性/陰性 対照)
"""
import sys
sys.dont_write_bytecode = True
import io, os, re, hashlib, subprocess

KI = os.path.dirname(os.path.abspath(__file__))
YOTSU5 = os.path.join(KI, '83_yotsu5.py')
FUDA5 = re.compile(u'(五数札v1 母數=\\d+ 一致=\\d+ 相違=\\d+ 実体無=\\d+ 讀めぬ行=\\d+ '
                   u'跳=\\d+\\(甲\\d+/乙\\d+\\)) 和検=\\S+ 封=([0-9a-f]{16})')
RIYUU_RE = re.compile(u'理由札v1\\s+(.+?)\\s+封=([0-9a-f]{16})')


def sha16(p):
    try:
        return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]
    except Exception:
        return u'★讀めぬ★'


def gyou_set(p):
    u"""臺帳の ★非空・非註★ の行を集合で返す(出所の差を行で割る為)。"""
    out = []
    try:
        for raw in io.open(p, encoding='utf-8', errors='replace'):
            l = raw.strip()
            if l and not l.startswith(u'#'):
                out.append(l)
    except Exception:
        return None
    return out


def hakaru(kikai, man, bases):
    u"""83_yotsu5.py を走らせ (五数の正準, 封, rc, 生の出目) を返す。"""
    cmd = [sys.executable, '-B', YOTSU5, 'fuda']
    if kikai:
        cmd += ['--kikai', kikai]
    cmd += [man] + list(bases)
    r = subprocess.run(cmd, capture_output=True, text=True)
    m = FUDA5.search(r.stdout)
    if not m:
        return None, None, r.returncode, r.stdout + u'\n--- stderr ---\n' + r.stderr
    return m.group(1), m.group(2), r.returncode, r.stdout


def seal(parts):
    s = u'理由札v1|' + u'|'.join(parts)
    return s, hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def hitohashiri(kikai, man, bases, kotei, kuzushi, moto, kataru=True):
    u"""一走ぶんの理由札を建てる。返す物: (rc, 札の行, 正準, 語り)"""
    go = []
    go5, fu5, rc5, nama = hakaru(kikai, man, bases)
    if go5 is None:
        go.append(u'★測れぬ ―― 五数札が取れなんだ★\n' + nama[:2000])
        return 2, None, None, u'\n'.join(go)
    go.append(u'★本走の五数★ %s 封=%s (rc=%d)' % (go5, fu5, rc5))

    # ---- 崩 ―― 固定を崩して ★實測★ する ----
    if kuzushi:
        k5, kfu, krc, knama = hakaru(kikai, kuzushi, bases)
        if k5 is None:
            go.append(u'★測れぬ ―― 崩した臺帳の五数札が取れなんだ★\n' + knama[:1200])
            return 2, None, None, u'\n'.join(go)
        go.append(u'★崩した走の五数★ %s 封=%s (rc=%d)' % (k5, kfu, krc))
        naru = (k5 != go5)
        kuzu = u'鳴' if naru else u'黙'
        go.append(u'★崩★ %s ―― %s'
                  % (kuzu, u'崩せば五数が変つた(固定を見て居る)' if naru
                     else u'★崩しても五数が一指も動かぬ。此の通過は固定を一度も見て居らぬ★'))
    else:
        kuzu = u'測らず'
        go.append(u'★崩★ 測らず ―― 崩した臺帳を渡されて居らぬ(★宣言した空白である★)')

    # ---- 出所 ―― 臺帳が元の物か、作り変へた対照か ----
    if moto:
        a, b = gyou_set(man), gyou_set(moto)
        if a is None or b is None:
            demae = u'測れぬ'
        else:
            sa = len(set(a) ^ set(b))
            demae = u'原' if sa == 0 else u'対照(元との差%d行)' % sa
        go.append(u'★出所★ %s ―― 元=%s' % (demae, os.path.basename(moto)))
    else:
        demae = u'不明'
        go.append(u'★出所★ 不明 ―― 元の臺帳を渡されて居らぬ')

    parts = [go5,
             u'器=%s:%s' % (os.path.basename(kikai) if kikai else u'(既定)',
                            sha16(kikai) if kikai else u'-'),
             u'臺帳=%s:%s' % (os.path.basename(man), sha16(man)),
             u'基点=%s' % (u','.join(bases) if bases else u'(既定)'),
             u'固定=%s' % kotei,
             u'崩=%s' % kuzu,
             u'出所=%s' % demae]
    canon, fu = seal(parts)
    line = u'理由札v1 ' + u' '.join(parts) + u' 封=%s' % fu

    if kuzu == u'黙':
        rc = 1
        mi = u'★rc=1 ―― ★偽の通過★。通つては居るが、固定を崩しても鳴らぬ'
    elif demae.startswith(u'対照'):
        rc = 1
        mi = u'★rc=1 ―― ★偽の通過★。通つたのは ★元とは別の臺帳★ の上である'
    elif rc5 != 0:
        rc = 1
        mi = u'★rc=1 ―― 五数に赤が立つて居る(通過では無い)'
    elif kuzu == u'測らず' or demae == u'不明':
        rc = 1
        mi = u'★rc=1 ―― 理由の欄が埋まつて居らぬ。★理由の書けぬ通過を青にせぬ★'
    else:
        rc = 0
        mi = u'★rc=0 ―― ★本物の通過★。五数清し・崩せば鳴る・元の臺帳の上'
    go.append(u'★正準文字列★ ' + canon)
    go.append(line)
    go.append(mi)
    return rc, line, canon, u'\n'.join(go)


def mode_jikenme(root):
    u"""★陽性対照が鳴かねば器では無い★ ―― 己を検める。

    陽性 = ★偽の通過が偽と出る★ 事 / 陰性 = ★真の通過が偽と出ぬ★ 事。
    """
    F = os.path.join(KI, '..', 'fixture', 'nise')
    F = os.path.normpath(F)
    V = os.path.join(root, 'scripts', 'checks', 'karo_mac_manifest_verify.py')
    kata = [
        (u'陰性甲: ★真の通過★(素の名・臺帳の sha 欄を崩せば鳴る)',
         os.path.join(F, 'M_kou.txt'), os.path.join(F, 'M_kou_kuzushi.txt'),
         os.path.join(F, 'M_kou.txt'), u'臺帳のsha欄が現物に一致', 0),
        (u'陽性甲: ★偽の通過★(名の中に己の sha ―― 崩しても黙る)',
         os.path.join(F, 'M_otsu.txt'), os.path.join(F, 'M_otsu_kuzushi.txt'),
         os.path.join(F, 'M_otsu.txt'), u'臺帳のsha欄が現物に一致', 1),
        (u'陽性乙: ★崩しを渡さぬ走★(理由の書けぬ通過は青にせぬ)',
         os.path.join(F, 'M_kou.txt'), None,
         os.path.join(F, 'M_kou.txt'), u'臺帳のsha欄が現物に一致', 1),
        (u'陽性丙: ★元を渡さぬ走★(出所不明は青にせぬ)',
         os.path.join(F, 'M_kou.txt'), os.path.join(F, 'M_kou_kuzushi.txt'),
         None, u'臺帳のsha欄が現物に一致', 1),
    ]
    rcs = []
    for na, man, kuz, moto, kotei, want in kata:
        sys.stdout.write(u'\n==== %s ==== (望む rc=%d)\n' % (na, want))
        rc, line, canon, go = hitohashiri(V, man, [root + os.sep], kotei, kuz, moto)
        sys.stdout.write(go + u'\n')
        sys.stdout.write(u'---- 出た rc=%d / 望む rc=%d ―― %s\n'
                         % (rc, want, u'合ふ' if rc == want else u'★合はぬ★'))
        rcs.append(rc == want)
    sys.stdout.write(u'\n★自検め★ %d/%d 合ふ\n' % (sum(1 for x in rcs if x), len(rcs)))
    return 0 if all(rcs) else 1


def main(argv):
    a = argv[1:]
    if a and a[0] == '--jikenme':
        if len(a) < 2:
            sys.stderr.write(u'★測れぬ: --jikenme の後に repo 根を渡せ★\n'); return 2
        return mode_jikenme(a[1])
    kikai = kotei = kuzushi = moto = None
    rest = []
    i = 0
    while i < len(a):
        if a[i] == '--kikai' and i + 1 < len(a):
            kikai = a[i + 1]; i += 2
        elif a[i] == '--kotei' and i + 1 < len(a):
            kotei = a[i + 1]; i += 2
        elif a[i] == '--kuzushi' and i + 1 < len(a):
            kuzushi = a[i + 1]; i += 2
        elif a[i] == '--moto' and i + 1 < len(a):
            moto = a[i + 1]; i += 2
        else:
            rest.append(a[i]); i += 1
    if not rest:
        sys.stderr.write(u'★測れぬ: 臺帳を argv で渡せ★\n'); return 2
    if kotei is None:
        sys.stderr.write(u'★測れぬ: --kotei で ★何を固定して居るか★ を一語で述べよ★\n'); return 2
    man, bases = rest[0], rest[1:]
    rc, line, canon, go = hitohashiri(kikai, man, bases, kotei, kuzushi, moto)
    sys.stdout.write(go + u'\n')
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
