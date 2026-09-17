#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""karyuu_trace.py ―― 各口が ★下流で何の演算子で讀まれるか★ を追ふ器。

口は「開く」だけでは害を成さぬ。★讀まれて初めて枝が分かれる★。
故に此の器は、口毎に (一)自file (二)子器 (三)repo 全体 の三つの根で讀みを数へ、
讀み方を【數 / 字面 / case / path / export / 算術】へ分類する。
★讀まれぬ口(宣のみ)★ も名指しで挙げる ―― 之が「番人を立てても何も守れぬ」口である。

用法: karyuu_trace.py <決まり.tsv>
  決まり.tsv の欄: 名<TAB>宣file<TAB>宣行<TAB>子器(無ければ -)
返り値: 0=追つた / 2=引数の誤り / 4=対象が無い
"""
import os
import re
import subprocess
import sys

REPO = os.environ.get('KM83_REPO', '/Users/momizimac/multi-agent-shogun')


def classify(line, name):
    """讀みの演算子を分類する。一行が複数に当たれば複数返す。"""
    out = []
    if re.search(r'\[\s*["\']?\$\{?%s\}?["\']?\s*-(ge|gt|le|lt|eq|ne)\b' % name, line) or \
       re.search(r'-(ge|gt|le|lt|eq|ne)\s+["\']?\$\{?%s\b' % name, line):
        out.append('數(-ge/-lt 等)')
    if re.search(r'\[\s*["\']?\$\{?%s\}?["\']?\s*(=|==|!=)' % name, line) or \
       re.search(r'(=|==|!=)\s*["\']?\$\{?%s\b' % name, line):
        out.append('字面(=)')
    if re.search(r'case\s+["\']?\$\{?%s\b' % name, line):
        out.append('case')
    if re.search(r'\$\(\(.*%s' % name, line):
        out.append('算術(( ))')
    if re.search(r'(>>?|<|-f|-d|-e|mkdir|rm|touch|cat|tee)\s*["\']?\$?\{?%s\b' % name, line) or \
       re.search(r'\$\{?%s\}?/' % name, line):
        out.append('path として open')
    if re.search(r'^\s*export\s+%s=' % name, line):
        out.append('export(子へ渡す)')
    if re.search(r'^\s*%s=' % name, line):
        out.append('宣(代入)')
    if re.search(r'-t\s+["\']?\$\{?%s\b' % name, line):
        out.append('tmux -t 的')
    return out or ['(其の他/展開のみ)']


def hits(root, name, exclude=None):
    """root 配下で name を含む行を(path,行番,逐語)で返す。"""
    try:
        r = subprocess.run(['grep', '-rn', '--include=*.sh', '--include=*.py',
                            '-e', name, root],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None, 'TIMEOUT'
    out = []
    for ln in r.stdout.split('\n'):
        if not ln.strip():
            continue
        parts = ln.split(':', 2)
        if len(parts) < 3:
            continue
        p, no, body = parts
        if exclude and os.path.abspath(p) == os.path.abspath(exclude[0]) and no == str(exclude[1]):
            continue
        out.append((p, no, body))
    return out, r.returncode


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    try:
        rows = [l.split('\t') for l in open(sys.argv[1], encoding='utf-8').read().split('\n') if l.strip()]
    except OSError as e:
        sys.stderr.write('★対象が無い★ %s\n' % e)
        return 4
    yomarenu = []
    for r in rows:
        name, decl_f, decl_l, child = r[0], r[1], r[2], r[3]
        print('=' * 78)
        print('★口★ %s   (宣= %s L%s / 子器= %s)' % (name, decl_f, decl_l, child))
        own, rc_own = hits(os.path.join(REPO, decl_f), name, exclude=(os.path.join(REPO, decl_f), decl_l))
        print('--- (一) 自file 内の 宣以外の讀み: %d 行 (grep_rc=%s) ---'
              % (len(own) if own is not None else -1, rc_own))
        for (p, no, body) in (own or []):
            print('    L%-4s %-28s %s' % (no, '/'.join(classify(body, name)), body.strip()[:96]))
        if child and child != '-':
            ch, rc_ch = hits(os.path.join(REPO, child), name)
            print('--- (二) 子器 %s の讀み: %d 行 (grep_rc=%s) ---'
                  % (child, len(ch) if ch is not None else -1, rc_ch))
            for (p, no, body) in (ch or []):
                print('    L%-4s %-28s %s' % (no, '/'.join(classify(body, name)), body.strip()[:96]))
        else:
            ch = []
        allh, rc_all = hits(os.path.join(REPO, 'scripts'), name)
        print('--- (三) scripts/ 全体の出現: %d 行 (grep_rc=%s) ---'
              % (len(allh) if allh is not None else -1, rc_all))
        for (p, no, body) in (allh or []):
            print('    %s:%s  %s' % (p.replace(REPO + '/', ''), no, body.strip()[:80]))
        if not own and not ch and len(allh or []) <= 1:
            yomarenu.append(name)
            print('★★ 讀まれぬ口(宣のみ) ★★ ―― 番人を立てても ★一つの枝も守らぬ★')
        print()
    print('#' * 78)
    print('★讀まれぬ口(宣のみで使はれぬ)= %d 本: %s' % (len(yomarenu), ' '.join(yomarenu) or '無'))
    return 0


sys.exit(main())
