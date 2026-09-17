# -*- coding: utf-8 -*-
"""gg ―― git grep の薄い皮(第75弾)。disk(作業樹・rev 無し)と HEAD(rev 付き)を同じ regex で引く。rc は subprocess の returncode(pipe 無し)。
零の四札の為に、呼んだ器の逐語(argv)・根と深さ(scripts .claude・git 追跡 file 全深)・rc・刻 を出目に添へる。"""
import subprocess, time, re
M = '/Users/momizimac/multi-agent-shogun'; HEAD = '6ba8fcb2'; ROOTS = ['scripts', '.claude']
def koku(): return time.strftime('%Y-%m-%dT%H:%M:%S%z')
def gg(regex, rev=None, roots=ROOTS, extra=()):
    argv = ['git', 'grep', '-n', '-E', *extra, regex] + ([rev] if rev else []) + ['--'] + list(roots)
    p = subprocess.run(argv, capture_output=True, cwd=M)
    rows = []
    for ln in p.stdout.decode('utf-8', 'replace').split('\n'):
        if not ln: continue
        if rev: ln = ln.split(':', 1)[1]  # rev: を落とす
        path, no, text = ln.split(':', 2); rows.append((path, int(no), text))
    return rows, p.returncode, ' '.join(argv)
NEG = 'ZZ_KM77_NEGATIVE_9x7q'  # 陰性対照(樹に無い語・此の file 自身は git 追跡外ゆゑ拾はれぬ)
def fuda(regex_pos, regex_neg=NEG):
    """陽性対照= 渡した regex が 1 行以上拾ふ事・陰性対照= 無い語が 0 行 rc1。両 rev。"""
    out = []
    for rev in (None, HEAD):
        rp, rcp, ap = gg(regex_pos, rev); rn, rcn, an = gg(regex_neg, rev)
        out.append(f'  [{"disk" if rev is None else "HEAD " + rev}] 陽性 {len(rp)} 行 rc {rcp} ({regex_pos}) / 陰性 {len(rn)} 行 rc {rcn} ({regex_neg})')
    return out
def is_comment(text):
    return text.lstrip().startswith('#')
