#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★門控を員外へ出す三案を ★測つて★ 比べる器★(命二・据ゑるな・提案の為の實測)

問: 門控(_gate/*.err,.out,.rc)を臺帳へ入れると、★最後の走りが己の行を古びさせる★。
    ∴ 不動点が立たぬ(第53弾 破れ㋐・家老の指摘)。三案の何れが不動点を立てるか。

案: 甲① 臺帳を締めてから走る(控は束内・臺帳へ入れぬ)
    乙② 控を ★束外★ へ出す(束内に控が残らぬ)
    丙③ 臺帳に控を入れぬ + ★宣して argv から除く★(控は束内・紙に員外として宣す)
    現  (対照) 控を臺帳へ入れる ―― 第53弾の形

測: 各案で門を ★二度★ 走らせ ⑴一走目 rc ⑵二走目 rc ⑶條① 相違数 ⑷byte和 の前後
    不動点 = ★二走目の條① 相違=0 かつ byte和 が一走目と同じ★。

使ひ方: 20_kadobikae.py <實験の根(束外)>
"""
import os, sys, shutil, subprocess, hashlib, re

R = '/Users/momizimac/multi-agent-shogun'
MON = R + '/scripts/checks/karo_mac_dasumae_gate.sh'
APP = R + '/scripts/checks/karo_mac_manifest_append.py'
PY = '/opt/homebrew/bin/python3'

def sh(cmd, cwd=None, env=None):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

def tateru(d):
    """小さな束を建てる ―― ki 1本・raw 2本。控はまだ無い。"""
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d + '/ki'); os.makedirs(d + '/raw'); os.makedirs(d + '/_gate')
    open(d + '/ki/00.sh', 'w', encoding='utf-8').write('#!/bin/bash\necho hi\n')
    open(d + '/raw/00.txt', 'w', encoding='utf-8').write('一\n')
    open(d + '/raw/01.txt', 'w', encoding='utf-8').write('二\n')

def shimeru(d, paths):
    """臺帳を締める(束内相対・裁 seq322699 ―― 束へ降りてから呼ぶ)。"""
    open(d + '/_manifest.txt', 'w', encoding='utf-8').close()
    return sh([PY, '-B', APP, '_manifest.txt'] + paths, cwd=d)

def bytewa(d):
    """臺帳の bytes= 欄の和(門 條⑤ が見る數)。"""
    s = 0
    for ln in open(d + '/_manifest.txt', encoding='utf-8'):
        m = re.search(r' bytes=(\d+) ', ln)
        if m: s += int(m.group(1))
    return s

def jou1(err):
    """條① の出目を門の stderr から引く。★門は數を刷らぬ ―― 落ちた事だけを刷る★。
    ∴ 欄は「數」ではなく ★通/落★ である(初走で -1 を刷り、測れて居らなんだ。raw/*.first に残す)。"""
    if '條① 台帳とdiskの差が落ちた' in err: return '落'
    if '條①' in err: return '通'
    return '★測れぬ(條① の行が無い)★'

def jou5_bytewa(err):
    """條⑤ の byte和 を門の stderr から引く。★臺帳の bytes= 欄の和とは別物★
    ―― 門は argv の現物を測り、臺帳自身は其の和の外に在る(km-51 實測)。"""
    m = re.search(r'條⑤ 寸法 = byte和 (\d+)', err)
    return int(m.group(1)) if m else -1

def hashiru(d, hikae_saki, jogai):
    """門を走らせる。hikae_saki=控の置き場(絶対path)。jogai=argv から除く束内相対 path。"""
    paths = []
    for root, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x != '__pycache__']
        for f in fs:
            rp = os.path.relpath(os.path.join(root, f), d)
            if rp == '_manifest.txt' or rp in jogai: continue
            paths.append(rp)
    env = dict(os.environ); env['KM_GATE_MANIFEST_BASE'] = os.path.abspath(d)
    rc, out, err = sh(['bash', MON, '_manifest.txt'] + sorted(paths), cwd=d, env=env)
    os.makedirs(hikae_saki, exist_ok=True)
    open(hikae_saki + '/gate.err', 'w', encoding='utf-8').write(err if err else '★空である旨★\n')
    open(hikae_saki + '/gate.out', 'w', encoding='utf-8').write(out if out else '★空である旨★\n')
    open(hikae_saki + '/gate.rc', 'w', encoding='utf-8').write('%d\n' % rc)
    return rc, err

def an(base, name, hikae_in_bundle, hikae_in_manifest, sengen_jogai, teichou=False):
    """teichou=True: 控を臺帳へ入れた上で ★門の後に定型(固定の一行)で上書き★ する。
    家老の宣「臺帳の中に己の出目を入れた限り、何度建て直しても閉ぢぬ」を ★測つて★ 検める案丁。"""
    d = os.path.join(base, name)
    tateru(d)
    hikae = (d + '/_gate') if hikae_in_bundle else os.path.join(base, name + '_hikae_sotogawa')
    honpaths = ['ki/00.sh', 'raw/00.txt', 'raw/01.txt']
    def teisei():
        if not teichou: return
        os.makedirs(hikae, exist_ok=True)
        for n in ('gate.err', 'gate.out', 'gate.rc'):
            open(os.path.join(hikae, n), 'w', encoding='utf-8').write('★定型★\n')
    teisei()          # ★締める前に定型を置く★ ―― 臺帳が記すのは定型の sha である
    if hikae_in_manifest:
        # 控を臺帳へ入れる ―― 其の為に先づ一度走らせて控を生む(第53弾の形)
        if not teichou: hashiru(d, hikae, set())
        honpaths += ['_gate/gate.err', '_gate/gate.out', '_gate/gate.rc']
    shimeru(d, honpaths)
    b0 = bytewa(d)
    jogai = set(sengen_jogai)
    rc1, e1 = hashiru(d, hikae, jogai); teisei()
    b1 = bytewa(d); g1 = jou5_bytewa(e1)
    rc2, e2 = hashiru(d, hikae, jogai); teisei()
    b2 = bytewa(d); g2 = jou5_bytewa(e2)
    # 員外 = 束内 disk − 臺帳
    dai = set(re.match(r'^path=(.*) sha256=', l).group(1)
              for l in open(d + '/_manifest.txt', encoding='utf-8')
              if l.startswith('path='))
    disk = set(os.path.relpath(os.path.join(r, f), d)
               for r, ds, fs in os.walk(d) for f in fs if '__pycache__' not in r)
    ingai = sorted(disk - dai)
    return dict(an=name, rc1=rc1, rc2=rc2, jou1_1=jou1(e1), jou1_2=jou1(e2),
                daichou_bytewa=b0, jou5_1=g1, jou5_2=g2,
                ingai_hon=len(ingai), ingai_na=','.join(ingai) or '―')

def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__); return 2
    base = os.path.abspath(sys.argv[1]); os.makedirs(base, exist_ok=True)
    rows = [
        an(base, 'gen_hikae_wo_daichou_he', True,  True,  []),                 # 現行(対照)
        an(base, 'kou1_shimete_kara',       True,  False, []),                 # 甲①
        an(base, 'otsu2_sotogawa_he',       False, False, []),                 # 乙②
        an(base, 'hei3_sengen_shite_nozoku', True, False,
           ['_gate/gate.err', '_gate/gate.out', '_gate/gate.rc']),             # 丙③
        an(base, 'tei4_daichou_ni_irete_teichou', True, True, [], teichou=True),  # 丁④
    ]
    cols = ['an', 'rc1', 'rc2', 'jou1_1', 'jou1_2', 'daichou_bytewa',
            'jou5_1', 'jou5_2', 'ingai_hon', 'ingai_na']
    print('\t'.join(cols))
    for r in rows:
        r['fudouten'] = ('★立つ★' if (r['jou1_2'] == '通' and r['jou5_1'] == r['jou5_2'])
                         else '★立たぬ★')
        print('\t'.join(str(r[c]) for c in cols))
    print('')
    print('案\t不動点\t二走目 rc\t二走目 條①\t條⑤byte和 一走⇔二走\t束内員外')
    for r in rows:
        print('%s\t%s\t%d\t%s\t%d⇔%d %s\t%d本' %
              (r['an'], r['fudouten'], r['rc2'], r['jou1_2'], r['jou5_1'], r['jou5_2'],
               '同' if r['jou5_1'] == r['jou5_2'] else '★異★', r['ingai_hon']))
    return 0

sys.exit(main())
