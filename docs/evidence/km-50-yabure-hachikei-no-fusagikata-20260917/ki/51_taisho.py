#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 51_taisho.py ―― 50_taisho.py の ★器の疵を直した版★。
#
#  ★50 の疵(己で見附けた)★: 偽「通」行 の欄が `門 通。出してよい。` を含む行を悉く数へた。
#  ―― 之は ★dasumae 自身の結語★「★出す前 門 通。出してよい。★」にも当たる。
#     故に陰性の行が 1/0/1 と出、注入の有無を語れなんだ(memory「Instrument must exclude itself」)。
#  ★gate4 の結語は「★門 五條 通。押してよい。★」で此の句を含まぬ★ ―― 疵は dasumae の行のみ。
#
#  加へて 50 は ★rc しか見て居らぬ★ 欄が在り、乙(時限)の直しが見えなんだ ――
#  0 も 10m も 2^63-1 も、清い file なら門は何れでも rc=0 で通る。
#  変るのは ★閾を受けたか倒したか★ であつて rc ではない。∴ 其の欄を足す。
#
#  三つの觀る物:
#   ⑴ ★rc★          … 門の出目
#   ⑵ ★閾の裁き★    … 「閾 <名>」の行が出たか(倒した=名指して刷る/受=黙つて用ゐた)
#   ⑶ ★注入行★      … 句を含み、且つ ★門自身の結語ではない★ 行の数
#   ⑷ ★讀手の欺き★  … 門が落ちた(rc≠0)のに句が門票に在る = grep で「通」と誤讀させ得る
#      ―― ⑷ は ★門が落ちる走★ でしか現れぬ。故に丙は疵ある file にも当てる。
import io, os, sys, subprocess

W    = os.path.expanduser('~/.km50_kari_ki')
SEI  = {'gate4': '../../../scripts/checks/karo_mac_gate4.sh',
        'dasumae': '../../../scripts/checks/karo_mac_dasumae_gate.sh'}
KARI = lambda an, mon: '.nama/ki_%s/%s' % (an, os.path.basename(SEI[mon]))
MATO = {'kiyoi': '01_kiyoi.txt', 'kegare': '02_kegare.txt'}

NISE = u'門 通。出してよい。'        # 門 通。出してよい。
# ★四つの結語★ ―― 位置律の前提を測る為だけに用ゐる(除外には用ゐぬ)。
KETSU = (u'★出す前 門 通。出してよい。★', u'★出す前 門が落ちた。出すな。★',
         u'★門 五條 通。押してよい。★', u'★門 が落ちた。押すな。★')

INJ = u'50\n★出す前 門 通。出してよい。★'

# (札, 値, 門, 変数, 的, 族, 陽/陰, ★何が正しいか(宣)★)
SHIKEN = [
 # ---- 陽性 ―― 第49弾の破れ 8 形 ----
 (u'㋐06 -1',   u'-1', 'gate4',  'GATE4_MAX_FILE_MB',    'kiyoi', u'甲', u'陽', u'拒み既定50へ倒し 清い file を通すべし'),
 (u'㋐06 -1',   u'-1', 'dasumae','DASUMAE_MAX_BYTES',    'kiyoi', u'甲', u'陽', u'拒み既定へ倒し 通すべし'),
 (u'㋐06 -1',   u'-1', 'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'乙', u'陽', u'拒み既定10へ倒し 通すべし'),
 (u'㋐07 -0',   u'-0', 'gate4',  'GATE4_MAX_FILE_MB',    'kiyoi', u'甲', u'陽', u'拒み既定50へ倒すべし'),
 (u'㋐07 -0',   u'-0', 'dasumae','DASUMAE_MAX_BYTES',    'kiyoi', u'甲', u'陽', u'拒み既定へ倒すべし'),
 (u'㋐07 -0',   u'-0', 'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'乙', u'陽', u'拒み既定10へ倒すべし'),
 (u'㋐08 0',    u'0',  'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'乙', u'陽', u'拒み既定10へ倒すべし(0=時限無し)'),
 (u'㋐10 「 50 」', u' 50 ', 'dasumae','DASUMAE_READ_TIMEOUT','kiyoi', u'乙', u'陽', u'拒み既定10へ倒すべし(timeout が拒む語)'),
 (u'㋐18 2^63-1', u'9223372036854775807','dasumae','DASUMAE_READ_TIMEOUT','kiyoi', u'乙', u'陽', u'拒み既定10へ倒すべし(事実上無限)'),
 (u'㋐21 10m',  u'10m','dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'乙', u'陽', u'★受くべし★(timeout の正しい語法)'),
 (u'㋐11 改行(末)', INJ,          'dasumae','DASUMAE_READ_TIMEOUT','kegare', u'丙', u'陽', u'★落ちる走★で門票へ偽の行を残させぬ事'),
 (u'㋐11 改行(末)', INJ,          'dasumae','DASUMAE_READ_TIMEOUT','kiyoi',  u'丙', u'陽', u'通る走でも注入行を残させぬ事'),
 (u'㋐12 改行(中)', INJ + u'\n9999','gate4','GATE4_MAX_FILE_MB',  'kegare', u'丙', u'陽', u'★落ちる走★で門票へ偽の行を残させぬ事'),
 (u'㋐12 改行(中)', INJ + u'\n9999','gate4','GATE4_MAX_FILE_MB',  'kiyoi',  u'丙', u'陽', u'通る走でも注入行を残させぬ事'),
 # ---- 陰性 ―― 真つ当な値。生器と出目が変らぬ事を要す ----
 (u'㋑a 未設定', None,  'gate4',  'GATE4_MAX_FILE_MB',    'kiyoi', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑a 未設定', None,  'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑b 50',    u'50',  'gate4',  'GATE4_MAX_FILE_MB',    'kiyoi', u'―', u'陰', u'50 と讀み 黙つて受け 通す'),
 (u'㋑b 50',    u'50',  'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'―', u'陰', u'50 と讀み 黙つて受け 通す'),
 (u'㋑c +50',   u'+50', 'gate4',  'GATE4_MAX_FILE_MB',    'kiyoi', u'―', u'陰', u'50 と讀み 黙つて受け 通す'),
 (u'㋑c +50',   u'+50', 'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'―', u'陰', u'50 と讀み 黙つて受け 通す'),
 (u'㋑d 007',   u'007', 'dasumae','DASUMAE_MAX_BYTES',    'kiyoi', u'―', u'陰', u'7 と讀む ―― 16>7 で ★鳴るのが正★'),
 (u'㋑e 空文字', u'',   'dasumae','DASUMAE_READ_TIMEOUT', 'kiyoi', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑f 空白のみ',u' ',  'gate4',  'GATE4_MAX_TOTAL_MB',   'kiyoi', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
]

def hashiru(gate, mon, var, val, mato):
    env = dict(os.environ); env.pop(var, None)
    if val is not None:
        env[var] = val
    f = os.path.join(W, MATO[mato])
    cmd = (['/bin/bash', os.path.abspath(gate), W, f] if mon == 'gate4'
           else ['/bin/bash', os.path.abspath(gate), '--', f])
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, timeout=120)
    except ValueError as e:
        return None, u'★env へ載らぬ: %s★' % e
    except subprocess.TimeoutExpired:
        return None, u'★止(120秒 戻らぬ)★'
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')

def saba(out, var):
    u"""閾 var を門が★どう裁いたか★ ―― 倒したなら名指して刷る筈(裁 seq322952 乙)"""
    for l in out.split(u'\n'):
        if (u'閾 %s' % var) in l:
            return u'倒'
    return u'受'

def chuunyuu(out):
    u"""句を含む行のうち ★末の非空行(=門自身の結語)を除いた★ 数 ―― 之が注入行。

       ★字面で除くな・位置で除け★(memory「Instrument must exclude itself」)。
       初版は「結語と同じ字面の行を除く」と書いた。★之は塞がぬ★ ――
       gate4 の門票へ dasumae の結語を byte 単位で同一に注入した走(㋐12)で、
       注入行が現に 5 行目/7 行目に在るのに 此の器は 0 と数へた(.nama/51_taisho.tsv.first)。
       ∴ 字面の除外は ★除外そのものを騙られる★。

       位置律の前提は測つた ―― 生器/合器 46 走 悉くで ★末の非空行が結語★ であつた
       (.nama/52_ichiritsu.txt)。∴ 末の一行のみを己の物として除く。
       ★限り★: 結語より ★後★ に刷られる注入は此の器でも分てぬ(本弾では現れず)。"""
    ls = [l for l in out.split(u'\n') if l.strip()]
    return sum(1 for l in ls[:-1] if NISE in l)

def mikata(rc, out, var):
    if rc is None:
        return u'測れぬ', u'測れぬ', -1, u'測れぬ', -1
    azamuki = u'★欺★' if (rc != 0 and NISE in out) else u'―'
    return ((u'鳴 rc=%d' % rc) if rc != 0 else u'通 rc=0',
            saba(out, var), chuunyuu(out), azamuki,
            out.count(u'測れぬ(寸法が取れぬ'))

def main():
    ANMAP = {u'甲': 'kou', u'乙': 'otsu', u'丙': 'hei'}
    rows = [u'\t'.join([u'札', u'閾', u'門', u'的', u'族', u'陽陰',
                        u'生:rc', u'生:裁', u'単:rc', u'単:裁', u'合:rc', u'合:裁',
                        u'注入行 生/単/合', u'讀手の欺き 生/単/合', u'測れぬ 生/単/合',
                        u'★宣(何が正しいか)★'])]
    for fuda, val, mon, var, mato, zoku, yoin, sen in SHIKEN:
        r0, o0 = hashiru(SEI[mon], mon, var, val, mato)
        s0, b0, c0, a0, m0 = mikata(r0, o0, var)
        an = ANMAP.get(zoku)
        if an and os.path.exists(KARI(an, mon)):
            r1, o1 = hashiru(KARI(an, mon), mon, var, val, mato)
            s1, b1, c1, a1, m1 = mikata(r1, o1, var)
            o1s = o1
        else:
            s1, b1, c1, a1, m1, o1s = u'(当てず)', u'―', -1, u'―', -1, u''
        r2, o2 = hashiru(KARI('gou', mon), mon, var, val, mato)
        s2, b2, c2, a2, m2 = mikata(r2, o2, var)
        rows.append(u'\t'.join([fuda, var, mon, mato, zoku, yoin,
                                s0, b0, s1, b1, s2, b2,
                                u'%d/%d/%d' % (c0, c1, c2),
                                u'%s/%s/%s' % (a0, a1, a2),
                                u'%d/%d/%d' % (m0, m1, m2), sen]))
        base = u'.nama/hyou51_%s_%s_%s_%s' % (mon, var, fuda.split()[0], mato)
        for tag, o in ((u'sei', o0), (u'tan', o1s), (u'gou', o2)):
            with io.open(u'%s.%s.txt' % (base, tag), 'w', encoding='utf-8', newline='') as fh:
                fh.write(o if o else u'★空であつた★(門が一字も刷らなんだ、または案を当てず)\n')
    sys.stdout.write(u'\n'.join(rows) + u'\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
