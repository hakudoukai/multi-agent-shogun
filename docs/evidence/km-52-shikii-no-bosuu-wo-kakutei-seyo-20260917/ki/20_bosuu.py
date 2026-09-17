#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 20_bosuu.py ―― 第52弾 ㋐① の ★判定条件を code で述べる器★。
#
# ★宣(逐語)★ ―― 「閾を読む箇所」とは、次の三つを悉く満たす ★(file, 環境変数名) の組★ を謂ふ。
#   甲) file が ★shell script★ である事(git ls-files に在り、且つ 拡張子 .sh か 冠 shebang に sh/bash を持つ)。
#   乙) 其の file の中で、當該の名が ★process 環境から値を取り得る★ 事。
#       即ち次の何れかの形で現れる ―― ①`${NAME:-既定}`/`${NAME-既定}`/`${NAME:=既定}` の展開
#       ②`fix_threshold NAME 既定 受皿`(受皿は NAME の代理と看做す) ③file 内で一度も代入されぬ裸の `$NAME`。
#   丙) 其の値(又は其の代理変数)が、同じ file の中で ★数値比較器★ へ達する事。
#       数値比較器とは `-eq -ne -lt -le -gt -ge`(test/[/[[ の中)・`(( ))`・`$(( ))` の四形を謂ふ。
#
# ★数へ方の単位★ = ★組(file, 環境変数名)★ であつて「行」ではない。
#   同じ名が一 file 内で三行に現れても ★一箇所★ と数へる(家老の18本の数へ方に合はせた)。
#   ∴ 「箇所」と「行」は別の數である ―― 両方を刷る。
#
# ★此の器が見えぬ物(自ら申す限界)★
#   ⑴ file を跨ぐ流れ(A.sh が export し B.sh が読む)は見えぬ。
#   ⑵ `eval`/間接展開 `${!v}` の先は見えぬ。
#   ⑶ 数値の引数を取る外器(sleep/timeout/inotifywait -t/head -n)は ★丙に含めて居らぬ★。
#      ∴ 之等は「閾を読む箇所」から外れる ―― ★外したのであつて、無いのではない★(別欄で数へる)。
#   ⑷ 行中の `#` 以降を comment として削らぬ(`${x#pat}` と紛れる故)。∴ comment 中の比較器を拾ひ得る。
#      ―― 但し ★冠が # で始まる行★ は削る。削つた行數を刷る。
import sys, os, re, io, subprocess, json

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
MODE = sys.argv[2] if len(sys.argv) > 2 else 'tracked'   # tracked | disk

RE_DEFAULT  = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(:?[-=])')      # ${NAME:-d} ${NAME-d} ${NAME:=d}
RE_ANYVAR   = re.compile(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?')
RE_ASSIGN   = re.compile(r'^\s*(?:export\s+|local\s+|declare\s+(?:-\w+\s+)?)?([A-Za-z_][A-Za-z0-9_]*)=')
RE_FIXTH    = re.compile(r'(?:^|[;&|(\s])fix_threshold\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s+"?([^\s"]+)"?\s+"?([A-Za-z_][A-Za-z0-9_]*)"?')
RE_NUMOP    = re.compile(r'(?<![A-Za-z0-9_-])-(?:eq|ne|lt|le|gt|ge)(?![A-Za-z0-9_])')
RE_ARITH    = re.compile(r'\(\(|\$\(\(')

def files_tracked(root):
    out = subprocess.check_output(['git','-C',root,'ls-files','-z'])
    return [p.decode('utf-8') for p in out.split(b'\x00') if p]

def files_disk(root):
    acc=[]
    for dp,dn,fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git','node_modules','__pycache__')]
        for f in fn:
            acc.append(os.path.relpath(os.path.join(dp,f), root))
    return acc

def is_shell(root, rel):
    ap = os.path.join(root, rel)
    if not os.path.isfile(ap) or os.path.islink(ap): return False
    if rel.endswith('.sh'): return True
    try:
        with open(ap,'rb') as fh: head = fh.readline(200)
    except Exception: return False
    return head.startswith(b'#!') and (b'bash' in head or b'/sh' in head or b' sh' in head)

def analyse(root, rel):
    """返す=(箇所の list, 行數, 削つた comment 行數)。箇所= dict(env=名, proxies=[..], cmp_lines=[..], read_lines=[..])"""
    ap = os.path.join(root, rel)
    try:
        src = io.open(ap, encoding='utf-8', errors='replace').read().split('\n')
    except Exception as e:
        return None, 0, 0, str(e)
    kept, dropped = [], 0
    for i,l in enumerate(src,1):
        if l.lstrip().startswith('#'): dropped += 1; kept.append((i,''))
        else: kept.append((i,l))
    assigned = set()
    for i,l in kept:
        m = RE_ASSIGN.match(l)
        if m: assigned.add(m.group(1))
    # 乙 ―― env 由来の名を集める
    env_names = {}   # env名 -> dict(read_lines=[], proxies=set())
    def touch(n):
        if n not in env_names: env_names[n] = {'read_lines':[], 'proxies':set([n])}
        return env_names[n]
    for i,l in kept:
        for m in RE_DEFAULT.finditer(l):
            n = m.group(1); e = touch(n); e['read_lines'].append(i)
            a = RE_ASSIGN.match(l)
            if a: e['proxies'].add(a.group(1))
        for m in RE_FIXTH.finditer(l):
            n, d, out = m.group(1), m.group(2), m.group(3)
            e = touch(n); e['read_lines'].append(i); e['proxies'].add(out)
    # ③裸の $NAME で file 内に代入無き物
    for i,l in kept:
        for m in RE_ANYVAR.finditer(l):
            n = m.group(1)
            if n in assigned or n in env_names: continue
            if n in ('1','2','0'): continue
            if n.isdigit(): continue
            e = touch(n); e['read_lines'].append(i)
    # 代理の伝播(一段) ―― `OUT=${NAME:-d}` は上で取つた。`OUT="$PROXY"` も一段だけ追ふ。
    for i,l in kept:
        a = RE_ASSIGN.match(l)
        if not a: continue
        lhs = a.group(1); rhs = l.split('=',1)[1]
        for n,e in env_names.items():
            for p in list(e['proxies']):
                if re.search(r'\$\{?%s\}?(?![A-Za-z0-9_])' % re.escape(p), rhs):
                    e['proxies'].add(lhs)
    # 丙 ―― 数値比較器へ達するか
    hits = []
    for n,e in env_names.items():
        cmp_lines = []
        for i,l in kept:
            if not (RE_NUMOP.search(l) or RE_ARITH.search(l)): continue
            for p in e['proxies']:
                if re.search(r'\$\{?%s\b' % re.escape(p), l) or re.search(r'\(\(\s*[^)]*\b%s\b' % re.escape(p), l):
                    cmp_lines.append(i); break
        if cmp_lines:
            hits.append({'env':n,'proxies':sorted(e['proxies']),
                         'read_lines':sorted(set(e['read_lines'])),
                         'cmp_lines':sorted(set(cmp_lines))})
    hits.sort(key=lambda h: h['env'])
    return hits, len(src), dropped, None

def main():
    rels = files_tracked(ROOT) if MODE=='tracked' else files_disk(ROOT)
    sh = [r for r in rels if is_shell(ROOT, r)]
    out = {'root':ROOT,'mode':MODE,'files_all':len(rels),'files_shell':len(sh),
           'files_with_hits':0,'kasho':0,'gyou':0,'dropped_comment_lines':0,'err':[],'rows':[]}
    for r in sorted(sh):
        hits, nlines, dropped, err = analyse(ROOT, r)
        out['dropped_comment_lines'] += dropped
        if err: out['err'].append({'file':r,'err':err}); continue
        if hits:
            out['files_with_hits'] += 1
            out['kasho'] += len(hits)
            for h in hits:
                out['gyou'] += len(h['cmp_lines'])
                out['rows'].append({'file':r, **h})
    json.dump(out, io.open(1,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('★母數★ 歩いた file=%d(内 shell=%d) 箇所=%d 行=%d 鳴つた file=%d 削つた冠#行=%d 疵=%d\n'
                     % (out['files_all'], out['files_shell'], out['kasho'], out['gyou'],
                        out['files_with_hits'], out['dropped_comment_lines'], len(out['err'])))
    return 0

sys.exit(main())
