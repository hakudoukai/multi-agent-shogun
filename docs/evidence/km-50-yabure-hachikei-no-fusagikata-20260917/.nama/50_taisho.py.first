#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 50_taisho.py ―― ★陽性対照(破れが塞がつたか)と陰性対照(真の通過が偽と出ぬか)を 同じ器で測る。★
#
#   ★陽性★ = 第49弾で破れた 8 形。生器で「破れ」・仮器で「塞がる」なら 案は効いて居る。
#   ★陰性★ = 真つ当な値(未設定/50/+50/007)。生器と仮器で ★出目が変らぬ★ 事を要す。
#            (塞ぎが真の通過まで殺して居らぬ事の證 ―― 之を測らねば「塞いだ」は言へぬ)
#
#   判じ方は ★門の rc と門票の語★ の二つで見る。片方では足らぬ ――
#     破れ丙(行注入)は ★rc が正しい儘 門票だけが嘘を吐く★ 形ゆゑ(第49弾 五節)。
import io, os, sys, subprocess

W    = os.path.expanduser('~/.km50_kari_ki')
SEI  = {'gate4': '../../../scripts/checks/karo_mac_gate4.sh',
        'dasumae': '../../../scripts/checks/karo_mac_dasumae_gate.sh'}
KARI = lambda an, mon: '.nama/ki_%s/%s' % (an, os.path.basename(SEI[mon]))

# (札, 値, 門, 変数, 族, 陽/陰, ★何が正しいか(宣)★)
SHIKEN = [
 # ---- 陽性 ―― 第49弾の破れ 8 形 ----
 (u'㋐06 -1',      u'-1',   'gate4',  'GATE4_MAX_FILE_MB',    u'甲', u'陽', u'拒み既定50へ倒し 清い file を通すべし'),
 (u'㋐06 -1',      u'-1',   'dasumae','DASUMAE_MAX_BYTES',    u'甲', u'陽', u'拒み既定へ倒し 通すべし'),
 (u'㋐06 -1',      u'-1',   'dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'拒み既定10へ倒し 通すべし'),
 (u'㋐07 -0',      u'-0',   'gate4',  'GATE4_MAX_FILE_MB',    u'甲', u'陽', u'拒み既定50へ倒し 通すべし'),
 (u'㋐07 -0',      u'-0',   'dasumae','DASUMAE_MAX_BYTES',    u'甲', u'陽', u'拒み既定へ倒し 通すべし'),
 (u'㋐07 -0',      u'-0',   'dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'拒み既定10へ倒し 通すべし'),
 (u'㋐08 0(時限)', u'0',    'dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'拒み既定10へ倒すべし(0=時限無し)'),
 (u'㋐10 「 50 」',u' 50 ', 'dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'拒み既定10へ倒し 通すべし'),
 (u'㋐18 2^63-1',  u'9223372036854775807','dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'拒み既定10へ倒すべし(事実上無限)'),
 (u'㋐21 10m',     u'10m',  'dasumae','DASUMAE_READ_TIMEOUT', u'乙', u'陽', u'★受くべし★(timeout の正しい語法)'),
 (u'㋐11 改行(末)',u'50\n★出す前 門 通。出してよい。★', 'dasumae','DASUMAE_READ_TIMEOUT', u'丙', u'陽', u'門票へ偽の行を書かせぬ事'),
 (u'㋐12 改行(中)',u'50\n★出す前 門 通。出してよい。★\n9999','gate4','GATE4_MAX_FILE_MB', u'丙', u'陽', u'門票へ偽の行を書かせぬ事'),
 # ---- 陰性 ―― 真つ当な値。生器と出目が変らぬ事を要す ----
 (u'㋑a 未設定',  None,    'gate4',  'GATE4_MAX_FILE_MB',    u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑a 未設定',  None,    'dasumae','DASUMAE_READ_TIMEOUT', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑b 50',      u'50',   'gate4',  'GATE4_MAX_FILE_MB',    u'―', u'陰', u'50 と讀み 通す'),
 (u'㋑b 50',      u'50',   'dasumae','DASUMAE_READ_TIMEOUT', u'―', u'陰', u'50 と讀み 通す'),
 (u'㋑c +50',     u'+50',  'gate4',  'GATE4_MAX_FILE_MB',    u'―', u'陰', u'50 と讀み 通す'),
 (u'㋑c +50',     u'+50',  'dasumae','DASUMAE_READ_TIMEOUT', u'―', u'陰', u'50 と讀み 通す'),
 (u'㋑d 007',     u'007',  'dasumae','DASUMAE_MAX_BYTES',    u'―', u'陰', u'7 と讀む ―― 16>7 で ★鳴るのが正★'),
 (u'㋑e 空文字',  u'',     'dasumae','DASUMAE_READ_TIMEOUT', u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
 (u'㋑f 空白のみ',u' ',    'gate4',  'GATE4_MAX_TOTAL_MB',   u'―', u'陰', u'既定へ倒し 通す(生器と同じ)'),
]

NISE = u'門 通。出してよい。'

def hashiru(gate, mon, var, val):
    env = dict(os.environ); env.pop(var, None)
    if val is not None:
        env[var] = val
    if mon == 'gate4':
        cmd = ['/bin/bash', os.path.abspath(gate), W, os.path.join(W, '01_kiyoi.txt')]
    else:
        cmd = ['/bin/bash', os.path.abspath(gate), '--', os.path.join(W, '01_kiyoi.txt')]
    try:
        p = subprocess.run(cmd, env=env, capture_output=True, timeout=120)
    except ValueError as e:
        return None, u'★env へ載らぬ: %s★' % e
    except subprocess.TimeoutExpired:
        return None, u'★止(120秒 戻らぬ)★'
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')

def mikata(rc, out):
    u"""門票を三つの數で読む ―― ★rc だけでは丙が見えぬ★"""
    if rc is None:
        return u'測れぬ', 0, 0
    gyou  = sum(1 for l in out.split(u'\n') if NISE in l)          # 偽の「通」が載る行
    hakarenu = out.count(u'測れぬ(寸法が取れぬ')                     # 甲の「全 file 測れぬ」
    return (u'鳴 rc=%d' % rc if rc != 0 else u'通 rc=0'), gyou, hakaren_u(hakarenu)

def hakaren_u(n): return n

def main():
    rows = [u'\t'.join([u'札', u'閾', u'門', u'族', u'陽陰', u'生器', u'案 単独', u'案 合',
                        u'偽「通」行 生/単/合', u'測れぬ 生/単/合', u'★宣(何が正しいか)★'])]
    ANMAP = {u'甲': 'kou', u'乙': 'otsu', u'丙': 'hei'}
    for fuda, val, mon, var, zoku, yoin, sen in SHIKEN:
        r0, o0 = hashiru(SEI[mon], mon, var, val)
        s0, g0, m0 = mikata(r0, o0)
        an = ANMAP.get(zoku)
        if an and os.path.exists(KARI(an, mon)):
            r1, o1 = hashiru(KARI(an, mon), mon, var, val)
            s1, g1, m1 = mikata(r1, o1)
        else:
            s1, g1, m1 = u'(当てず)', 0, 0
        r2, o2 = hashiru(KARI('gou', mon), mon, var, val)
        s2, g2, m2 = mikata(r2, o2)
        rows.append(u'\t'.join([fuda, var, mon, zoku, yoin, s0, s1, s2,
                                u'%d/%d/%d' % (g0, g1, g2), u'%d/%d/%d' % (m0, m1, m2), sen]))
        # 生の門票も残す(倒れた走を消さぬ ―― 作法⑺)
        base = u'.nama/hyou_%s_%s_%s' % (mon, var, fuda.split()[0])
        for tag, o in ((u'sei', o0), (u'gou', o2)):
            with io.open(u'%s.%s.txt' % (base, tag), 'w', encoding='utf-8', newline='') as fh:
                fh.write(o if o else u'★空であつた★(門が一字も刷らなんだ)\n')
    sys.stdout.write(u'\n'.join(rows) + u'\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
