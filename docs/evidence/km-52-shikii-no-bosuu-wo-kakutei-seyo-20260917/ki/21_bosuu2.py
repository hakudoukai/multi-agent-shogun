#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 21_bosuu2.py ―― 20_bosuu.py(第一走)の ★三つの疵を名指して直した★ 版。
#
# ★第一走(20_bosuu.py)の出目★ = file=1979 内 shell=198・箇所=576・行=862・鳴つた file=113
#   ―― 之は ★過大★ であつた。因を三つ名指す(nama/20_bosuu.first.raw に残す)。
#   疵A) ★代理の伝播が緩い★ ―― `INBOX="$SCRIPT_DIR/queue/..."` を「SCRIPT_DIR の代理」と看做し、
#        以後 `$INBOX` を含む比較行を悉く SCRIPT_DIR の丙と数へた(path 組立は値の流れに非ず)。
#        直し=代理は ★右辺が展開其の物★ の時のみ作る(`OUT="${NAME:-d}"` / `OUT="$NAME"`)。
#   疵B) ★一行に二つ以上の代入を見逃す★ ―― `_ft_n="$1"; _ft_o="$3"` の二つ目以降を
#        「代入無き裸の $NAME」＝env 由来 と誤つた(_ft_o/_ft_d/_ld/_i 等)。
#        直し=`;`/`&&`/`||`/`(`/`then`/`do` で区切つた ★各節の頭★ で代入を探す。
#   疵C) ★比較器の『行に在る』と『演算子の項である』を混同★ ――
#        `[ "$INBOX" = x ] && [ $n -lt 3 ]` の INBOX を丙と数へた。
#        直し=`項 -op 項` を取り出し、★其の二項の中に在る時のみ★ 丙とする。
#
# ★歩く根(declare)★ ―― 「repo source」とは ★git ls-files の内、docs/evidence/ の下に無い物★ を謂ふ。
#   docs/evidence/ の下は ★過去の弾の写し★(走らぬ紙)であり、走る器ではない。
#   ★除いたのであつて、歩いて居らぬのではない★ ―― 除いた file 数・其の内 shell 数・
#   其処で鳴つた箇所数を ★別欄で刷る★(memory「A declared exclusion still counts in the 母數」)。
import sys, os, re, io, subprocess, json

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
EXCLUDE_PREFIX = 'docs/evidence/'

RE_DEFAULT  = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(:?[-=])')
RE_ANYVAR   = re.compile(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?')
RE_FIXTH    = re.compile(r'(?:^|[;&|(\s])fix_threshold\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s+"?([^\s"]+)"?\s+"?([A-Za-z_][A-Za-z0-9_]*)"?')
RE_ASSIGN_H = re.compile(r'^\s*(?:export\s+|local\s+|readonly\s+|declare\s+(?:-\w+\s+)?|typeset\s+)?([A-Za-z_][A-Za-z0-9_]*)=')
RE_NUMCMP   = re.compile(r'(\S+)\s+-(eq|ne|lt|le|gt|ge)\s+(\S+)')
RE_ARITHBLK = re.compile(r'\(\(([^()]*)\)\)')
SEP         = re.compile(r';|&&|\|\||\bthen\b|\bdo\b|\belse\b|\{|\}')
# 右辺が「展開其の物」か ―― 前後の引用符のみ許す
RE_PURE     = re.compile(r'^\s*"?\$\{?([A-Za-z_][A-Za-z0-9_]*)(?::?[-=][^}]*)?\}?"?\s*$')

def sh_files(root):
    out = subprocess.check_output(['git','-C',root,'ls-files','-z'])
    rels = [p.decode('utf-8') for p in out.split(b'\x00') if p]
    sh = []
    for r in rels:
        ap = os.path.join(root, r)
        if not os.path.isfile(ap) or os.path.islink(ap): continue
        if r.endswith('.sh'): sh.append(r); continue
        try:
            with open(ap,'rb') as fh: head = fh.readline(200)
        except Exception: continue
        if head.startswith(b'#!') and (b'bash' in head or b'/sh' in head): sh.append(r)
    return rels, sh

def assigns_in_line(l):
    """一行の中の全ての代入名。`;`/`&&` 等で割つた各節の頭を見る(疵B の直し)。"""
    acc = []
    for seg in SEP.split(l):
        m = RE_ASSIGN_H.match(seg)
        if m: acc.append(m.group(1))
    return acc

def numeric_operands(l):
    """其の行の ★数値比較器の項★ の集合。`項 -op 項` と `(( ... ))` の中。"""
    ops = set()
    for m in RE_NUMCMP.finditer(l):
        ops.add(m.group(1)); ops.add(m.group(3))
    for m in RE_ARITHBLK.finditer(l):
        ops.add(m.group(1))
    return ops

def analyse(root, rel):
    ap = os.path.join(root, rel)
    src = io.open(ap, encoding='utf-8', errors='replace').read().split('\n')
    kept = [(i, '' if l.lstrip().startswith('#') else l) for i,l in enumerate(src,1)]
    assigned = set()
    for i,l in kept: assigned.update(assigns_in_line(l))
    env = {}
    def touch(n):
        env.setdefault(n, {'read':[], 'prox':set([n])})
        return env[n]
    for i,l in kept:
        for m in RE_DEFAULT.finditer(l):
            e = touch(m.group(1)); e['read'].append(i)
        for m in RE_FIXTH.finditer(l):
            e = touch(m.group(1)); e['read'].append(i); e['prox'].add(m.group(3))
    for i,l in kept:
        for m in RE_ANYVAR.finditer(l):
            n = m.group(1)
            if n in assigned or n in env or n.isdigit(): continue
            e = touch(n); e['read'].append(i)
    # 代理 ―― 右辺が展開其の物の時のみ(疵A の直し)。収束まで回す。
    for _ in range(4):
        grew = False
        for i,l in kept:
            for seg in SEP.split(l):
                m = RE_ASSIGN_H.match(seg)
                if not m: continue
                lhs = m.group(1); rhs = seg.split('=',1)[1]
                p = RE_PURE.match(rhs)
                if not p: continue
                src_name = p.group(1)
                for n,e in env.items():
                    if src_name in e['prox'] and lhs not in e['prox']:
                        e['prox'].add(lhs); grew = True
        if not grew: break
    hits = []
    for n,e in env.items():
        cmp_lines = []
        for i,l in kept:
            ops = numeric_operands(l)
            if not ops: continue
            blob = ' '.join(ops)
            for p in e['prox']:
                if re.search(r'\$\{?%s[\}\s"\']|\$%s$' % (re.escape(p), re.escape(p)), blob) \
                   or re.search(r'(?<![A-Za-z0-9_$])%s(?![A-Za-z0-9_])' % re.escape(p), blob):
                    cmp_lines.append(i); break
        if cmp_lines:
            hits.append({'env':n, 'proxies':sorted(e['prox']),
                         'read_lines':sorted(set(e['read'])), 'cmp_lines':sorted(set(cmp_lines))})
    hits.sort(key=lambda h: h['env'])
    return hits, len(src)

def main():
    rels, sh = sh_files(ROOT)
    inc = [r for r in sh if not r.startswith(EXCLUDE_PREFIX)]
    exc = [r for r in sh if r.startswith(EXCLUDE_PREFIX)]
    out = {'root':ROOT, 'files_tracked':len(rels), 'files_shell':len(sh),
           'walk_root':'git ls-files ∧ ¬docs/evidence/', 'files_walked':len(inc),
           'files_excluded_shell':len(exc), 'files_excluded_all':sum(1 for r in rels if r.startswith(EXCLUDE_PREFIX)),
           'kasho':0, 'gyou':0, 'files_with_hits':0, 'rows':[],
           'excluded_kasho':0, 'excluded_files_with_hits':0}
    for r in sorted(inc):
        hits, n = analyse(ROOT, r)
        if hits:
            out['files_with_hits'] += 1; out['kasho'] += len(hits)
            for h in hits:
                out['gyou'] += len(h['cmp_lines']); out['rows'].append({'file':r, **h})
    for r in sorted(exc):
        hits, n = analyse(ROOT, r)
        if hits:
            out['excluded_files_with_hits'] += 1; out['excluded_kasho'] += len(hits)
    json.dump(out, io.open(1,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('★母數(第二走)★ tracked=%d shell=%d 歩いた=%d 除いた(shell)=%d ／ 箇所=%d 行=%d 鳴file=%d ／ 除いた側 箇所=%d file=%d\n'
        % (out['files_tracked'], out['files_shell'], out['files_walked'], out['files_excluded_shell'],
           out['kasho'], out['gyou'], out['files_with_hits'], out['excluded_kasho'], out['excluded_files_with_hits']))
    return 0

sys.exit(main())
