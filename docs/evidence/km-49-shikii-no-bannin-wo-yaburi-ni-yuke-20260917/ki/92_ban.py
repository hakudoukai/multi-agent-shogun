#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 92_ban.py ―― ★閾の番人 二人(env_state / num_same_op)を、生器から逐語で抜いて当てる。★
#
# 為す事:
#   ⑴ 生器(karo_mac_gate4.sh 等)から env_state と num_same_op の定義を ★逐語で抜く★。
#      ―― 書き写さぬ。抜いた範囲の行番号と sha16 を刷る(「己が走らす版を讀め」の法)。
#   ⑵ 閾の形を一つづつ env へ載せ、91_ichi.sh 越しに二人の番人へ当てる。
#   ⑶ ㋐逐語と byte 列 ㋑env_state の出目 ㋒num_same_op の rc を TSV で出す。
#
# ★書かぬ★ ―― 生器へは一字も触れぬ。抜いた物は己の束の .nama/ へ置く。
#
# usage: 92_ban.py <生器.sh> <変数名> <抜き先.sh> [--tsv <出し先>]
import io, os, re, sys, subprocess, hashlib, ctypes

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

def nukidasu(src, dest):
    u"""生器から env_state / num_same_op を ★逐語★ で抜く。行番号は字面で当てる(焼き込まぬ)。"""
    lines = io.open(src, encoding='utf-8').read().split(u'\n')
    out, ranges = [], []
    for i, l in enumerate(lines):
        if l.startswith(u'num_same_op()'):
            out.append(l); ranges.append((u'num_same_op', i + 1, i + 1))
        elif l.startswith(u'env_state()'):
            j = i
            while j < len(lines) and lines[j] != u'}':
                j += 1
            out.extend(lines[i:j + 1]); ranges.append((u'env_state', i + 1, j + 1))
    if len(ranges) != 2:
        sys.stderr.write(u'★測れぬ: 函數が二つ揃はぬ(得た %d)★\n' % len(ranges)); sys.exit(2)
    body = u'\n'.join(out) + u'\n'
    with io.open(dest, 'w', encoding='utf-8', newline='') as fh:
        fh.write(body)
    return ranges, sha16(body.encode('utf-8'))

# ―― 閾の形(★名 / 値 / 註★)。値 None = ★未設定★
KATACHI = [
    (u'㋐01 未設定',            None,                        u'env に置かぬ'),
    (u'㋐02 空文字',            u'',                         u'置くが零字'),
    (u'㋐03 空白のみ(SP)',      u' ',                        u'ASCII 空白 一つ'),
    (u'㋐04 空白のみ(TAB)',     u'\t',                       u'ASCII TAB'),
    (u'㋐05 全角空白のみ',      u'\u3000',                   u'U+3000 ―― 出目は locale 次第(C.UTF-8 では tr が消し blank・LC_ALL=C では残り value)'),
    (u'㋐06 負値 -1',           u'-1',                       u'★狙ひ★'),
    (u'㋐07 負零 -0',           u'-0',                       u'★狙ひ★'),
    (u'㋐08 零 0',              u'0',                        u'★狙ひ★'),
    (u'㋐09 +50',               u'+50',                      u'符号付き'),
    (u'㋐10 前後に空白',        u' 50 ',                     u'★狙ひ★'),
    (u'㋐11 改行(末尾)',        u'50\n',                     u''),
    (u'㋐12 改行(中)',          u'50\n9999',                 u''),
    (u'㋐13 全角数字',          u'\uff15\uff10',             u'５０'),
    (u'㋐14 0x32',              u'0x32',                     u'十六進の字面'),
    (u'㋐15 0o62',              u'0o62',                     u'八進の字面(py 形)'),
    (u'㋐16 先頭零 007',        u'007',                      u''),
    (u'㋐17 先頭零 010',        u'010',                      u'八進なら 8・十進なら 10'),
    (u'㋐18 2^63-1',            u'9223372036854775807',      u''),
    (u'㋐19 2^63',              u'9223372036854775808',      u''),
    (u'㋐20 極長桁(9 x 400)',   u'9' * 400,                  u''),
    (u'㋐21 単位付 10m',        u'10m',                      u'timeout(1) の正しい語法'),
    (u'㋐22 NUL 入り',          u'50\x009999',               u'★env へ載るか否かを含めて測る★'),
]

def hexbytes(s):
    if s is None:
        return u'(無)'
    b = s.encode('utf-8')
    if len(b) > 24:
        return u' '.join(u'%02x' % c for c in b[:12]) + u' … (計 %d byte)' % len(b)
    return u' '.join(u'%02x' % c for c in b)

def hashiru(fn, var, val):
    env = dict(os.environ)
    env.pop(var, None)
    if val is not None:
        env[var] = val
    try:
        p = subprocess.run(['/bin/bash', os.path.join(os.path.dirname(os.path.abspath(__file__)), '91_ichi.sh'), fn, var],
                           env=env, capture_output=True)
    except ValueError as e:
        return (u'★env へ載らぬ★', u'―', u'★測れぬ ―― %s★' % e)
    o = p.stdout.decode('utf-8', 'replace').strip().split(u'\t')
    while len(o) < 3:
        o.append(u'(無)')
    return tuple(o[:3])

def futatabi(fn, var):
    u"""★env に同名を二度★ ―― execve の environ を生で二本にして、bash が何方を取るかを測る。"""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r); os.dup2(w, 1); os.dup2(w, 2)
        libc = ctypes.CDLL(None)
        argv_l = [b'/bin/bash', b'-c', ('printf %%s "${%s-}"' % var).encode()]
        env_l = [('%s=1' % var).encode(), ('%s=99999' % var).encode(), b'PATH=/usr/bin:/bin']
        A = (ctypes.c_char_p * (len(argv_l) + 1))(*(argv_l + [None]))
        E = (ctypes.c_char_p * (len(env_l) + 1))(*(env_l + [None]))
        libc.execve(b'/bin/bash', A, E)
        os._exit(127)
    os.close(w)
    got = os.read(r, 4096).decode('utf-8', 'replace')
    os.close(r); os.waitpid(pid, 0)
    return got

def main(argv):
    if len(argv) < 4:
        sys.stderr.write(u'usage: 92_ban.py <生器.sh> <変数名> <抜き先.sh> [--tsv <出し先>]\n'); return 2
    src, var, dest = argv[1], argv[2], argv[3]
    ranges, s16 = nukidasu(src, dest)
    rows = []
    rows.append(u'# 源 %s sha16=%s' % (src, sha16(io.open(src, 'rb').read())))
    for nm, a, b in ranges:
        rows.append(u'# 抜いた %s = L%d..L%d' % (nm, a, b))
    rows.append(u'# 抜き先 %s sha16=%s ―― ★書き写さず逐語で抜いた★' % (dest, s16))
    rows.append(u'# 変数 %s' % var)
    rows.append(u'\t'.join([u'形', u'㋐逐語', u'㋐byte列', u'㋑env_state', u'㋒num_same_op rc', u'㋒判', u'註']))
    for nm, val, chu in KATACHI:
        st, rc, han = hashiru(dest, var, val)
        gyaku = u'(未設定)' if val is None else (u'「%s」' % val.replace(u'\n', u'\\n').replace(u'\t', u'\\t').replace(u'\x00', u'\\0'))
        # ★末尾の空欄は欄を落す(讀む器が列を取り違へる)★ ―― 空には「-」を立てる
        rows.append(u'\t'.join([nm, gyaku, hexbytes(val), st, rc, han, chu or u'-']))
    got = futatabi(dest, var)
    rows.append(u'\t'.join([u'㋐23 env に同名を二度', u'「1」と「99999」を生の environ へ二本',
                            u'—', u'(bash が取つた値)= 「%s」' % got, u'—',
                            u'★後で当てる★', u'execve の environ を ctypes で二本にした']))
    body = u'\n'.join(rows) + u'\n'
    if '--tsv' in argv:
        with io.open(argv[argv.index('--tsv') + 1], 'w', encoding='utf-8', newline='') as fh:
            fh.write(body)
    sys.stdout.write(body)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
