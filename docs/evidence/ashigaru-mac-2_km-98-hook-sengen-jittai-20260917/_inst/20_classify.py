#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_classify.py <rev> <hooks.tsv> ―― hook の command から path を取り出し四つへ判ずる。
  甲=其の rev の tree に在る(git cat-file -e で實測)
  乙=disk に在るが tree に無い(遮断の則を check-ignore -v で名指す)
  丙=disk にも無い
  丁=path を取り出せぬ(理由を書く)
TSV を stdout・數を stderr。argv から的を取る。"""
import sys, os, shlex, subprocess

INTERP = {'bash', 'sh', 'zsh', 'python3', 'python', 'env', 'node', 'ruby', 'perl'}
ROOT = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True).stdout.strip()

def expand(tok):
    """${VAR:-default} を一段だけ展開。env に無ければ default。"""
    out, i, note = [], 0, []
    while i < len(tok):
        if tok.startswith('${', i):
            j = tok.find('}', i)
            if j < 0:
                return None, '★${ が閉ぢぬ★'
            inner = tok[i+2:j]
            if ':-' in inner:
                name, dflt = inner.split(':-', 1)
            elif '-' in inner:
                name, dflt = inner.split('-', 1)
            else:
                name, dflt = inner, None
            if name in os.environ:
                out.append(os.environ[name]); note.append('%s=env' % name)
            elif dflt is not None:
                out.append(dflt); note.append('%s=既定' % name)
            else:
                return None, '★%s 未設定かつ既定無し★' % name
            i = j + 1
        else:
            out.append(tok[i]); i += 1
    return ''.join(out), '/'.join(note)

def pick_path(cmd):
    """command から path token を一つ取る。取れねば (None, 理由)。"""
    try:
        toks = shlex.split(cmd)
    except ValueError as e:
        return None, None, '★shlex 分割不能: %s★' % e
    cands = []
    for t in toks:
        if t in INTERP or t.startswith('-'):
            continue
        if '/' in t:
            cands.append(t)
    if not cands:
        return None, None, '★path らしき token 無し(tok=%d)★' % len(toks)
    tok = cands[0]
    p, note = expand(tok)
    if p is None:
        return None, tok, note
    return p, tok, note

def main():
    if len(sys.argv) != 3:
        sys.stderr.write('usage: 20_classify.py <rev> <hooks.tsv>\n'); return 2
    rev, tsv = sys.argv[1], sys.argv[2]
    print('#no\tevent\t判\tpath(展開後)\ttree(%s)\tdisk\t遮断(check-ignore -v)\t註' % rev[:8])
    cnt = {'甲': 0, '乙': 0, '丙': 0, '丁': 0}
    n = 0
    for line in open(tsv, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        f = line.split('\t')
        if len(f) < 7:
            sys.stderr.write('★欄不足の行を飛ばす: %r★\n' % line); continue
        no, ev, cmd = f[0], f[1], f[6]
        cmd = cmd.replace('␊', '\n').replace('␍', '\r').replace('␉', '\t')
        n += 1
        p, tok, note = pick_path(cmd)
        if p is None:
            cnt['丁'] += 1
            print('%s\t%s\t丁\t-\t-\t-\t-\t%s' % (no, ev, note or '-'))
            continue
        # repo 相対
        ap = p if os.path.isabs(p) else os.path.join(ROOT, p)
        ap = os.path.normpath(ap)
        if ap.startswith(ROOT + os.sep):
            rel = ap[len(ROOT)+1:]
        else:
            rel = None
        # tree
        if rel is None:
            tree = '外(repo外ゆゑ tree 問へず)'
            in_tree = False
        else:
            r = subprocess.run(['git', 'cat-file', '-e', '%s:%s' % (rev, rel)],
                               capture_output=True)
            in_tree = (r.returncode == 0)
            tree = '有' if in_tree else '無(rc=%d)' % r.returncode
        on_disk = os.path.exists(ap)
        disk = '有' if on_disk else '無'
        # 遮断
        ig = '-'
        if rel is not None and not in_tree:
            r2 = subprocess.run(['git', 'check-ignore', '-v', '--', rel],
                                capture_output=True, text=True)
            if r2.returncode == 0:
                ig = r2.stdout.strip().replace('\t', ' : ')
            else:
                ig = '遮断無(check-ignore rc=%d)' % r2.returncode
        if in_tree:
            j = '甲'
        elif on_disk:
            j = '乙'
        else:
            j = '丙'
        cnt[j] += 1
        # ★空欄は '-' で埋める(末尾の空欄は tab を末尾空白として残し、門 條② が鳴る)★
        print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (no, ev, j, rel if rel else ap, tree, disk, ig, note or '-'))
    sys.stderr.write('★判定 母數=%d 甲=%d 乙=%d 丙=%d 丁=%d★\n'
                     % (n, cnt['甲'], cnt['乙'], cnt['丙'], cnt['丁']))
    sys.stderr.write('和=%d (母數と%s)\n' % (sum(cnt.values()),
                     '一致' if sum(cnt.values()) == n else '★不一致★'))
    return 0

sys.exit(main())
