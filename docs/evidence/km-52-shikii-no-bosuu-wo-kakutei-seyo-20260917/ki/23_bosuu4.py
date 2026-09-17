#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 23_bosuu4.py(22_bosuu3.py の写しに ★疵F★ の直しのみ足した)
# 22_bosuu3.py ―― 21_bosuu2.py の ★二つの疵★ を直した第三走。
#   疵D) ★節の区切りに `{` `}` を入れた為、`${NAME:-d}` を三つに割つてゐた★。
#        `local max_typing_skip="${MAX_TYPING_SKIP:-5}"` の右辺が `"$` に成り、代理が立たず
#        MAX_TYPING_SKIP を ★落として居た★(第二走の inbox_watcher が 10本の内 5本しか出なんだ因)。
#        直し=区切りは `;` `&&` `||` と 語(then/do/else) のみ。★波括弧では割らぬ★。
#   疵E) ★代理を別の箇所として二重に数へた★ ―― `fix_threshold CONTEXT_WARN_BYTES 1600000 WARN_BYTES`
#        の WARN_BYTES は CONTEXT_WARN_BYTES の受け皿であつて、別の閾ではない。
#        直し=名の入り口を三つに分けて記し(default/fixth/bare)、★bare のみで入り且つ他の名の代理★
#        である物は落とす。落とした数を刷る。
#
# ★判定条件(第52弾 ㋐① の答・逐語)★
#   「閾を読む箇所」= 次を悉く満たす ★(shell file, 環境変数名) の組★。
#   甲 file が git ls-files に在り、docs/evidence/ の下に無く、拡張子 .sh 又は shebang が sh/bash。
#   乙 其の名が同 file 内で ①`${NAME:-d}`/`${NAME-d}`/`${NAME:=d}` ②`fix_threshold NAME d 受皿`
#      ③file 内に代入の無い裸の `$NAME` ―― の何れかで現れる(＝process 環境から値を取り得る)。
#   丙 其の名か其の受け皿が、同 file 内で ★数値比較器の項★ に立つ。
#      数値比較器=`項 -eq|-ne|-lt|-le|-gt|-ge 項`(test/[/[[) 及び `(( … ))`/`$(( … ))` の中。
#   単位=★組(file,名)★。同じ名が十行に出ても一箇所。行数は別欄で刷る。
import sys, os, re, io, subprocess, json

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
EXC = 'docs/evidence/'

RE_DEFAULT  = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(:?[-=])')
RE_ANYVAR   = re.compile(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?')
RE_FIXTH    = re.compile(r'(?:^|[;&|(\s])fix_threshold\s+"?([A-Za-z_][A-Za-z0-9_]*)"?\s+"?([^\s"]+)"?\s+"?([A-Za-z_][A-Za-z0-9_]*)"?')
RE_ASSIGN_H = re.compile(r'^\s*(?:export\s+|local\s+|readonly\s+|declare\s+(?:-\w+\s+)?|typeset\s+)?([A-Za-z_][A-Za-z0-9_]*)\+?=')
RE_READ     = re.compile(r'(?:^|[;&|\s])read\s+(?:-\w+\s+|-\w+\s+\S+\s+)*([A-Za-z_][A-Za-z0-9_ ]*)')
RE_FOR      = re.compile(r'(?:^|[;&|\s])for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b')
RE_LOCALS   = re.compile(r'^\s*(?:local|declare|typeset)\s+((?:[A-Za-z_][A-Za-z0-9_]*\s*)+)$')
RE_NUMCMP   = re.compile(r'(\S+)\s+-(eq|ne|lt|le|gt|ge)\s+(\S+)')
RE_ARITHBLK = re.compile(r'\(\(([^()]*)\)\)')
SEP         = re.compile(r';|&&|\|\||\bthen\b|\bdo\b|\belse\b')
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
    acc = []
    for seg in SEP.split(l):
        m = RE_ASSIGN_H.match(seg)
        if m: acc.append(m.group(1))
        m = RE_LOCALS.match(seg)
        if m: acc.extend(m.group(1).split())
    for m in RE_READ.finditer(l): acc.extend(m.group(1).split())
    for m in RE_FOR.finditer(l): acc.append(m.group(1))
    return acc

def numeric_operands(l):
    ops = set()
    for m in RE_NUMCMP.finditer(l): ops.add(m.group(1)); ops.add(m.group(3))
    for m in RE_ARITHBLK.finditer(l): ops.add(m.group(1))
    return ops

def analyse(root, rel):
    src = io.open(os.path.join(root, rel), encoding='utf-8', errors='replace').read().split('\n')
    kept = [(i, '' if l.lstrip().startswith('#') else l) for i,l in enumerate(src,1)]
    assigned = set()
    for i,l in kept: assigned.update(assigns_in_line(l))
    env = {}
    def touch(n, via):
        e = env.setdefault(n, {'read':[], 'prox':set([n]), 'via':set()})
        e['via'].add(via); return e
    for i,l in kept:
        for m in RE_DEFAULT.finditer(l): touch(m.group(1),'default')['read'].append(i)
        for m in RE_FIXTH.finditer(l):
            e = touch(m.group(1),'fixth'); e['read'].append(i); e['prox'].add(m.group(3))
    for i,l in kept:
        names = [m.group(1) for m in RE_ANYVAR.finditer(l)]
        # ★疵F の直し★ 算術 `(( … ))`/`$(( … ))` の中では変数は `$` 無しで書ける。
        #   第三走は `$` を要求した為 `[ "$X" -lt "$((now - ESCALATE_COOLDOWN))" ]` の
        #   ESCALATE_COOLDOWN を ★一度も env に入れて居らなんだ★(inbox_watcher の10本目)。
        for m in RE_ARITHBLK.finditer(l):
            names += re.findall(r'(?<![A-Za-z0-9_$])([A-Za-z_][A-Za-z0-9_]*)(?![A-Za-z0-9_])', m.group(1))
        for n in names:
            if n in assigned or n in env or n.isdigit(): continue
            touch(n,'bare')['read'].append(i)
    for _ in range(5):
        grew = False
        for i,l in kept:
            for seg in SEP.split(l):
                m = RE_ASSIGN_H.match(seg)
                if not m: continue
                lhs = m.group(1); rhs = seg.split('=',1)[1]
                p = RE_PURE.match(rhs)
                if not p: continue
                for n,e in env.items():
                    if p.group(1) in e['prox'] and lhs not in e['prox']:
                        e['prox'].add(lhs); grew = True
        if not grew: break
    # 疵E ―― bare のみで入り且つ他の名の代理 を落とす
    others = set()
    for n,e in env.items():
        for p in e['prox']:
            if p != n: others.add(p)
    dropped = sorted(n for n,e in env.items() if e['via'] == {'bare'} and n in others)
    for n in dropped: del env[n]
    hits = []
    for n,e in env.items():
        cmp_lines = []
        for i,l in kept:
            ops = numeric_operands(l)
            if not ops: continue
            blob = ' '.join(ops)
            for p in e['prox']:
                if re.search(r'\$\{?%s(?![A-Za-z0-9_])' % re.escape(p), blob) \
                   or re.search(r'(?<![A-Za-z0-9_$])%s(?![A-Za-z0-9_])' % re.escape(p), blob):
                    cmp_lines.append(i); break
        if cmp_lines:
            hits.append({'env':n, 'via':sorted(e['via']), 'proxies':sorted(e['prox']),
                         'read_lines':sorted(set(e['read'])), 'cmp_lines':sorted(set(cmp_lines))})
    hits.sort(key=lambda h: h['env'])
    return hits, len(src), dropped

def main():
    rels, sh = sh_files(ROOT)
    inc = [r for r in sh if not r.startswith(EXC)]
    exc = [r for r in sh if r.startswith(EXC)]
    out = {'root':ROOT, 'walk_root':'git ls-files ∧ ¬'+EXC,
           'files_tracked':len(rels), 'files_shell':len(sh), 'files_walked':len(inc),
           'files_excluded_shell':len(exc),
           'files_excluded_all':sum(1 for r in rels if r.startswith(EXC)),
           'kasho':0,'gyou':0,'files_with_hits':0,'dropped_proxy_names':0,
           'excluded_kasho':0,'excluded_files_with_hits':0,'rows':[]}
    for r in sorted(inc):
        hits, n, dropped = analyse(ROOT, r)
        out['dropped_proxy_names'] += len(dropped)
        if hits:
            out['files_with_hits'] += 1; out['kasho'] += len(hits)
            for h in hits:
                out['gyou'] += len(h['cmp_lines']); out['rows'].append({'file':r, **h})
    for r in sorted(exc):
        hits, n, dropped = analyse(ROOT, r)
        if hits: out['excluded_files_with_hits'] += 1; out['excluded_kasho'] += len(hits)
    json.dump(out, io.open(1,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('★母數(第三走)★ tracked=%d shell=%d 歩いた=%d 除いた(shell)=%d ／ 箇所=%d 行=%d 鳴file=%d 代理落し=%d ／ 除いた側 箇所=%d file=%d\n'
        % (out['files_tracked'],out['files_shell'],out['files_walked'],out['files_excluded_shell'],
           out['kasho'],out['gyou'],out['files_with_hits'],out['dropped_proxy_names'],
           out['excluded_kasho'],out['excluded_files_with_hits']))
    return 0

sys.exit(main())
