#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 93_mon.py ―― 閾の形を ★門そのもの★ へ当て、㋓鳴つたか を実測する。
#
#   92_ban.py は番人二人(env_state / num_same_op)だけを当てた。
#   本器は ★生の門を端から端まで走らせ★、其の rc と stderr を見る。
#   ―― 番人を擦り抜けた値が、後段で何を仕出かすかは ★門を走らせねば判らぬ★。
#
# ★書かぬ★ 生器は読み取りで呼ぶのみ。仮の樹(94_kari_ki.sh)は repo の外に建てる。
#
# usage: 93_mon.py gate4   <gate4.sh> <仮の樹> <staged file> <変数名> [--tsv <出し先>]
#        93_mon.py dasumae <dasumae.sh> <当てる file> <変数名> [--tsv <出し先>]
import io, os, sys, subprocess

KATACHI = [
    (u'㋐01 未設定',          None),
    (u'㋐02 空文字',          u''),
    (u'㋐03 空白のみ(SP)',    u' '),
    (u'㋐04 空白のみ(TAB)',   u'\t'),
    (u'㋐05 全角空白のみ',    u'　'),
    (u'㋐06 負値 -1',         u'-1'),
    (u'㋐07 負零 -0',         u'-0'),
    (u'㋐08 零 0',            u'0'),
    (u'㋐09 +50',             u'+50'),
    (u'㋐10 前後に空白',      u' 50 '),
    (u'㋐11 改行(末尾)',      u'50\n'),
    (u'㋐12 改行(中)',        u'50\n9999'),
    (u'㋐13 全角数字',        u'５０'),
    (u'㋐14 0x32',            u'0x32'),
    (u'㋐15 0o62',            u'0o62'),
    (u'㋐16 先頭零 007',      u'007'),
    (u'㋐17 先頭零 010',      u'010'),
    (u'㋐18 2^63-1',          u'9223372036854775807'),
    (u'㋐19 2^63',            u'9223372036854775808'),
    (u'㋐20 極長桁(9 x 400)', u'9' * 400),
    (u'㋐21 単位付 10m',      u'10m'),
    (u'㋐22 NUL 入り',        u'50\x009999'),
]

def hashiru(cmd, var, val):
    env = dict(os.environ)
    env.pop(var, None)
    if val is not None:
        env[var] = val
    try:
        p = subprocess.run(cmd, env=env, capture_output=True)
    except ValueError as e:
        return None, u'★env へ載らぬ ―― %s★' % e
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')

def hiroi(out, keys):
    u"""出目から目印の行だけ拾ふ(一行に畳む)。"""
    got = []
    for l in out.split(u'\n'):
        for k in keys:
            if k in l:
                got.append(l.strip()); break
    return u' ／ '.join(got) if got else u'(其の行 無し)'

def main(argv):
    if len(argv) < 2:
        sys.stderr.write(u'usage: 93_mon.py gate4|dasumae …\n'); return 2
    mode = argv[1]
    if mode == 'gate4':
        gate, W, f, var = argv[2], argv[3], argv[4], argv[5]
        cmd = ['/bin/bash', gate, W, f]
        keys = [u'閾 %s' % var, u'條⑤', u'門 が落ちた', u'門 五條 通']
    elif mode == 'dasumae':
        gate, f, var = argv[2], argv[3], argv[4]
        cmd = ['/bin/bash', gate, '--', f]
        keys = [u'閾 %s' % var, u'條④ 測れぬ', u'條⑤', u'門 通', u'門が落ちた']
    else:
        sys.stderr.write(u'★測れぬ: mode は gate4 か dasumae★\n'); return 2

    rows = [u'# 門 %s' % gate, u'# 変数 %s' % var, u'# 打つ形 %s' % ' '.join(cmd),
            u'\t'.join([u'形', u'㋓門の rc', u'㋓鳴つたか', u'門の出目(拾ひ)'])]
    for nm, val in KATACHI:
        rc, out = hashiru(cmd, var, val)
        if rc is None:
            rows.append(u'\t'.join([nm, u'―', u'★測れぬ★', out])); continue
        natta = u'★鳴つた★' if rc != 0 else u'鳴らぬ(通)'
        rows.append(u'\t'.join([nm, u'%d' % rc, natta, hiroi(out, keys)]))
    body = u'\n'.join(rows) + u'\n'
    if '--tsv' in argv:
        with io.open(argv[argv.index('--tsv') + 1], 'w', encoding='utf-8', newline='') as fh:
            fh.write(body)
    sys.stdout.write(body)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
