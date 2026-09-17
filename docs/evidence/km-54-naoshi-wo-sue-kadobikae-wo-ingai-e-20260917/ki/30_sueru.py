#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★行注入の直しを ★自席の器★ へ据ゑる(命一)★ ―― 前後 sha16・負テスト一形・可逆を測る。

何処へ据ゑるか(讀み): 直し紙の対象は生器 共有器四本であるが、家老の条 ㋑ は
「生器 scripts/・~/bin へ一字も書くな」である。★二読みは家老へ問ひ、答は未着★。
∴ 本弾は ★當席の器 ki/10_ingai.py★ へ据ゑる ―― 同じ疵(形12)を ★己が持つて居る★ 故。

形12 とは: 注入した値が ★閉ぢの一字まで本物と違はぬ偽行★ を立てる事。
  番人の札では 「」と ) を閉ぢて偽の札を一本増やす。
  ★當席の器では、path に改行/TAB が在れば TSV の偽の行・偽の欄が立つ。★ 同じ形である。

測る事:
  ⑴ 前後 sha16(据ゑる前・据ゑた後)      ⑵ py_compile rc
  ⑶ 陽性(形12 の名が在る時 偽行が立つ/拒まれる) ⑷ 負テスト一形(清い名は前後で一字も違はぬ)
  ⑸ 判定不変(員外の數が前後で同じ)        ⑹ 可逆(逆当てで ★同じ sha16 へ戻る★)
"""
import os, sys, shutil, subprocess, hashlib, py_compile, tempfile

R = '/Users/momizimac/multi-agent-shogun'
B = R + '/docs/evidence/km-54-naoshi-wo-sue-kadobikae-wo-ingai-e-20260917'
KI = B + '/ki/10_ingai.py'
PY = '/opt/homebrew/bin/python3'

MAE = '''    w = sys.stdout.write
    w('刻\\t%s\\n' % koku)
    w('根\\t%s\\n' % root)
    w('臺帳\\t%s\\n' % os.path.relpath(man, root))
    w('#\\t欄: 別\\tpath\\t註\\n')
    for p in ingai_ta: w('員外(他)\\t%s\\t―\\n' % p)
    for p in ingai_ji: w('員外(己)\\t%s\\t★本器が生む紙・名指しで宣す★\\n' % p)
    for p in jittai:   w('実体無\\t%s\\t★臺帳に在り disk に無し★\\n' % p)
    for p, m in hijou: w('非常体\\t%s\\t%s\\n' % (p, m))
'''

ATO = '''    def hyouji(s):
        """★行注入封じ(形12)★: 改行/復帰/TAB を可視印へ均す ―― ★表示のみ・判定不変★。
        TSV は改行で行を、TAB で欄を割る。∴ 名に其の三字が在れば
        ★閉ぢの一字まで本物と違はぬ偽の行★ を立てられる。可視印は多byteゆゑ
        tr では置けぬ(BSD tr は byte 器・\\266 は生 byte 0xB6 を吐く。實測 2026-09-17)。
        str.translate は codepoint 器ゆゑ ★UTF-8 として正しい★ 印が置ける。"""
        return s.translate({0x0a: '␊', 0x0d: '␍', 0x09: '␉'})

    w = sys.stdout.write
    w('刻\\t%s\\n' % koku)
    w('根\\t%s\\n' % hyouji(root))
    w('臺帳\\t%s\\n' % hyouji(os.path.relpath(man, root)))
    w('#\\t欄: 別\\tpath\\t註\\n')
    for p in ingai_ta: w('員外(他)\\t%s\\t―\\n' % hyouji(p))
    for p in ingai_ji: w('員外(己)\\t%s\\t★本器が生む紙・名指しで宣す★\\n' % hyouji(p))
    for p in jittai:   w('実体無\\t%s\\t★臺帳に在り disk に無し★\\n' % hyouji(p))
    for p, m in hijou: w('非常体\\t%s\\t%s\\n' % (hyouji(p), m))
'''

def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def ate(path, mae, ato):
    """★当てる。当たつた本数を必ず検める(0 でも黙つて「直つた顔」をせぬ)★"""
    s = open(path, encoding='utf-8').read()
    n = s.count(mae)
    if n != 1:
        raise SystemExit('★当たらぬ ―― 前の字面が %d 本(1 を要す)★ %s' % (n, path))
    open(path, 'w', encoding='utf-8').write(s.replace(mae, ato, 1))
    return n

def compile_rc(path):
    try:
        py_compile.compile(path, cfile=os.path.join(tempfile.mkdtemp(), 'x.pyc'),
                           doraise=True)
        return 0
    except py_compile.PyCompileError:
        return 1

def tateru(d, akumei):
    """實験の束。akumei=True なら ★形12 の名★(改行+TAB で偽の行を立てる名)を一本置く。"""
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d + '/raw')
    open(d + '/raw/kiyoi.txt', 'w', encoding='utf-8').write('清\n')
    open(d + '/_manifest.txt', 'w', encoding='utf-8').write(
        '# dialect: path= sha256= bytes= lines=\n'
        '# ★此の臺帳へ行を足すのは karo_mac_manifest_append.py のみ★\n')
    if akumei:
        # ★形12★: 名の中で行を閉ぢ、次の行を「員外(他)\t…\t―」の形に仕立てる。
        nise = 'a.txt\n員外(他)\t★偽の一行 ―― 本物と一字も違はぬ★\t―'
        open(os.path.join(d + '/raw', nise), 'w', encoding='utf-8').write('毒\n')
    return d

def hakaru(d):
    r = subprocess.run([PY, '-B', KI, '.', '_manifest.txt'], cwd=d, capture_output=True)
    out = r.stdout.decode('utf-8', 'surrogateescape')
    err = r.stderr.decode('utf-8', 'surrogateescape')
    gyou = [x for x in out.split('\n') if x.startswith('員外(他)')]
    nise = [x for x in gyou if '偽の一行' in x]
    n_ingai = -1
    for ln in err.split('\n'):
        if ln.startswith('★員外='):
            n_ingai = int(ln.split('=')[1].split('(')[0])
    # ★偽行 = 員外として刷られた行数 − 員外の實數★。字面で数へるな(直した後も字面は残る)。
    return dict(rc=r.returncode, gyou=len(gyou), nise=len(gyou) - n_ingai,
                jimen=len(nise), ingai=n_ingai, out=out,
                utf8=('正' if _utf8ok(out) else '★不正★'))

def _utf8ok(s):
    try:
        s.encode('utf-8'); return True
    except UnicodeEncodeError:
        return False

def main():
    base = os.path.expanduser('~/km54-sueru-20260917')
    os.makedirs(base, exist_ok=True)
    doku = tateru(base + '/doku', True)      # 陽性: 形12 の名を含む
    kiyo = tateru(base + '/kiyo', False)     # 負テスト一形: 清い名のみ

    # ★前走の据ゑを解いてから測る★(器は再走に耐へねばならぬ)
    src = open(KI, encoding='utf-8').read()
    if src.count(ATO) == 1 and src.count(MAE) == 0:
        open(KI, 'w', encoding='utf-8').write(src.replace(ATO, MAE, 1))
        sys.stderr.write('★前走の据ゑを解いた(再走の為)★\n')

    rows = []
    s_mae = sha16(KI)
    rows.append(('前', s_mae, compile_rc(KI), hakaru(doku), hakaru(kiyo)))

    ate(KI, MAE, ATO)
    s_ato = sha16(KI)
    rows.append(('後', s_ato, compile_rc(KI), hakaru(doku), hakaru(kiyo)))

    ate(KI, ATO, MAE)                         # 逆当て
    s_modo = sha16(KI)
    rows.append(('戻', s_modo, compile_rc(KI), hakaru(doku), hakaru(kiyo)))

    ate(KI, MAE, ATO)                         # ★据ゑる★(戻したまま終らぬ)
    s_sue = sha16(KI)

    w = sys.stdout.write
    w('段\tsha16\tpy_compile\t陽性:員外行数\t陽性:偽行(行数-實數)\t陽性:員外實數\t陽性:UTF8\t'
      '負1:員外行数\t負1:偽行(行数-實數)\t負1:員外實數\t負1:UTF8\n')
    for nm, s, c, D, K in rows:
        w('%s\t%s\t%d\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%s\n'
          % (nm, s, c, D['gyou'], D['nise'], D['ingai'], D['utf8'],
             K['gyou'], K['nise'], K['ingai'], K['utf8']))
    w('据\t%s\t%d\t―\t―\t―\t―\t―\t―\t―\t―\n' % (s_sue, compile_rc(KI)))
    w('\n')
    w('可逆\t前=%s 戻=%s → %s\n' % (s_mae, s_modo, '★同じ sha16 へ戻る★'
                                     if s_mae == s_modo else '★戻らぬ★'))
    w('据ゑた\t後=%s 据=%s → %s\n' % (s_ato, s_sue, '★同じ★' if s_ato == s_sue else '★異★'))
    w('負テスト一形(清い名)\t前後の出目が一字も違はぬ: %s\n'
      % ('★違はぬ★' if rows[0][4]['out'] == rows[1][4]['out'] else '★違ふ★'))
    w('負テスト一形(偽行が拒まれる)\t陽性の偽行 前%d本 → 後%d本 → %s\n'
      % (rows[0][3]['nise'], rows[1][3]['nise'],
         '★拒まれた★' if (rows[0][3]['nise'] > 0 and rows[1][3]['nise'] == 0)
         else '★塞げて居らぬ★'))
    w('判定不変\t員外の數 陽性 前%d/後%d・負1 前%d/後%d → %s\n'
      % (rows[0][3]['ingai'], rows[1][3]['ingai'], rows[0][4]['ingai'], rows[1][4]['ingai'],
         '★不変★' if (rows[0][3]['ingai'] == rows[1][3]['ingai']
                      and rows[0][4]['ingai'] == rows[1][4]['ingai']) else '★変つた★'))
    return 0

sys.exit(main())
