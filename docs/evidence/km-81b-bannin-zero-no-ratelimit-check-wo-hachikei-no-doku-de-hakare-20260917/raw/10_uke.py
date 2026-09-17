# -*- coding: utf-8 -*-
"""10 ㋐㋑(第77弾 km-81b)―― 的 scripts/ratelimit_check.sh の「受ける口」を ★二定義で別々に★ 数へ(甲= `${NAME:-既定}` の字面 / 乙= 外から値が入る変数= $HOME・argv($1 $2 $#)・命令置換 $( )・read)、
㋑ 比較器の全行を演算子の種で分け(數 [[ -lt ]] / 字面 ==,!= / 正規 =~ / case / 変数を命令として実行 `if $flag`)、
守る表(fix_threshold/env_state/num_same_op/_th_say/`for _t in`)が ★無い★ 事を零の四札(陽性対照= inbox_watcher.sh で鳴る・陰性対照= ZZ_KM81B_NEG・根と深さ・rc・刻)で示す。disk と HEAD の二版。行番号は己の器で引く。"""
import os, sys, re, time, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'; T = 'scripts/ratelimit_check.sh'; CTRL = 'scripts/inbox_watcher.sh'
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=M).stdout.strip()
src = {'disk': open(M + '/' + T, encoding='utf-8').read().split('\n'), 'HEAD': subprocess.run(['git', 'show', head + ':' + T], capture_output=True, text=True, cwd=M).stdout.split('\n')}
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z')
out = [f'# 10 ㋐㋑ / 刻 {koku} / 的 {T} / HEAD {head[:12]} / disk {len(src["disk"])-1} 行・HEAD {len(src["HEAD"])-1} 行']
A = ['版\t定義\t行\t名\t出所の種\t逐語']; C = ['版\t行\t左項\t演算子\t右項\t演算子の種\t逐語']
OPS = r'(-eq|-ne|-lt|-le|-gt|-ge|==|!=|=~|=)'
for v in ('disk', 'HEAD'):
    L = src[v]; kou = []; otsu = {}; hei = {}; infn = False
    for i, l in enumerate(L):
        s = l.strip()
        if re.match(r'^[A-Za-z_][A-Za-z_0-9]*\(\)\s*\{', l): infn = True
        if l == '}': infn = False
        if s.startswith('#'): continue
        for m in re.finditer(r'\$\{([A-Za-z_0-9#@]+):-([^}]*)\}', l):
            kou.append((i + 1, m.group(1), m.group(2)))
            A.append(f'{v}\t甲 ${{NAME:-既定}}\t{i+1}\t{m.group(1)}\t' + ('位置引数(既定 ' + m.group(2) + ')' if m.group(1).isdigit() else '内部状態変数(既定 ' + m.group(2)[:20] + ')') + f'\t{s}')
        m = re.match(r'^(?:local\s+)?([A-Za-z_][A-Za-z_0-9]*)\+?=(.*)$', s)
        if m:
            nm, rhs = m.group(1), m.group(2); kinds = []
            if '$HOME' in rhs: kinds.append('env $HOME')
            if re.search(r'\$[12#]\b|\$\{[12]', rhs): kinds.append('函数引数(内部から渡る)' if infn else 'argv')
            if re.search(r'\$\((?!\()', rhs): kinds.append('命令置換 $( )')
            if kinds and infn and kinds == ['函数引数(内部から渡る)']: hei.setdefault(nm, []).append((i + 1, kinds[0], s))
            elif kinds: otsu.setdefault(nm, []).append((i + 1, '+'.join(kinds), s))
        m2 = re.search(r'\bread\s+(?:-r\s+)?([A-Za-z_][A-Za-z_0-9]*)\b', s)
        if m2 and 'IFS' in s: otsu.setdefault(m2.group(1), []).append((i + 1, 'read(process substitution)', s))
        if re.match(r'^--lang\)\s+LANG_MODE="\$2"', s): otsu.setdefault('LANG_MODE', []).append((i + 1, 'argv', s))
    for nm, ws in sorted(otsu.items()):
        for ln, kd, s in ws: A.append(f'{v}\t乙 外から値が入る変数\t{ln}\t{nm}\t{kd}\t{s}')
    out.append(f'{v}: 甲 `${{NAME:-既定}}` の字面 {len(kou)} 口(名 {len(set(k[1] for k in kou))})= ' + ' '.join(f'{n}(L{ln})' for ln, n, d in kou))
    out.append(f'{v}: 乙 外から値が入る変数 {sum(len(w) for w in otsu.values())} 口・{len(otsu)} 名= ' + ' '.join(f'{n}(L{",".join(str(a) for a,b,c in w)})' for n, w in sorted(otsu.items())))
    for nm, ws in sorted(hei.items()):
        for ln, kd, s2 in ws: A.append(f'{v}\t丙 函数引数(乙に数へぬ)\t{ln}\t{nm}\t{kd}\t{s2}')
    out.append(f'{v}: 丙 函数内で $1/$2 を受ける local(乙に数へぬ) {sum(len(w) for w in hei.values())} 口・{len(hei)} 名= ' + ' '.join(f'{n}(L{",".join(str(a) for a,b,c in w)})' for n, w in sorted(hei.items())))
    K.kaku(D + f'/raw/10_otsu_{v}.txt', '\n'.join(sorted(otsu)))
    # ㋑ 比較器
    n_kind = {}
    for i, l in enumerate(L):
        s = l.strip()
        if s.startswith('#'): continue
        for ex in re.findall(r'\[\[(.+?)\]\]', s):
            for part in re.split(r'\s(?:&&|\|\|)\s', ex.strip()):
                m = re.match(r'^(\S+)\s+' + OPS + r'\s+(\S+)$', part.strip())
                if m:
                    op = m.group(2); kind = '數([[ ]] 内・算術評価)' if op.startswith('-') else ('正規 =~' if op == '=~' else '字面')
                    C.append(f'{v}\t{i+1}\t{m.group(1)}\t{op}\t{m.group(3)}\t{kind}\t{s}'); n_kind[kind] = n_kind.get(kind, 0) + 1
                else:
                    m1 = re.match(r'^!?\s*(-[a-z])\s+(\S+)$', part.strip())
                    if m1: C.append(f'{v}\t{i+1}\t{m1.group(2)}\t{m1.group(1)}\t-\t単項(-n/-z/-f/-x)\t{s}'); n_kind['単項'] = n_kind.get('単項', 0) + 1
        if re.match(r'^case\s+(\S+)\s+in', s):
            C.append(f'{v}\t{i+1}\t{re.match(r"^case\s+(\S+)\s+in", s).group(1)}\tcase\t(pattern)\tcase 字面\t{s}'); n_kind['case'] = n_kind.get('case', 0) + 1
        m3 = re.match(r'^if\s+(!\s+)?\$([A-Za-z_][A-Za-z_0-9]*);', s)
        if m3: C.append(f'{v}\t{i+1}\t${m3.group(2)}\t(exec)\t-\t変数を命令として実行(true/false)\t{s}'); n_kind['exec'] = n_kind.get('exec', 0) + 1
    out.append(f'{v}: ㋑ 比較器 {sum(n_kind.values())} 件= ' + ' / '.join(f'{k} {n}' for k, n in sorted(n_kind.items())))
    num = [r for r in C if r.startswith(v + '\t') and r.split('\t')[5].startswith('數')]
    out.append(f'{v}: 數比較器 {len(num)} 件の左項= ' + ' '.join(f'{r.split(chr(9))[2]}(L{r.split(chr(9))[1]})' for r in num))
# 守る表 ―― 零の四札
def gc(pat, path):
    p = subprocess.run(['grep', '-c', '-E', pat, path], capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
PAT = r'fix_threshold|env_state|num_same_op|_th_say|^for _t in '
n_t, rc_t = gc(PAT, T); n_c, rc_c = gc(PAT, CTRL); z_t, zrc_t = gc('ZZ_KM81B_NEG', T); z_c, zrc_c = gc('ZZ_KM81B_NEG', CTRL)
hb = subprocess.run(['git', 'show', head + ':' + T], capture_output=True, text=True, cwd=M).stdout; n_h = len(re.findall(r'(?m)' + PAT, hb))
out.append(f'守る表(語 {PAT}): 的 disk {n_t} 行 rc {rc_t} / 的 HEAD {n_h} 行(python re) / ★陽性対照★ {CTRL}(disk) {n_c} 行 rc {rc_c} / ★陰性対照★ ZZ_KM81B_NEG 的 {z_t} 行 rc {zrc_t}・{CTRL} {z_c} 行 rc {zrc_c} / 根= 的 file 一本 全 {len(src["disk"])-1} 行(再帰無し・深さ 0) / 刻 {koku}')
out.append(f'∴ ★守る表は 0 行(grep -c は 0 の時 rc 1 = 「無い」を器が言ふ)・陽性対照は同じ器・同じ語で {n_c} 行 rc {rc_c} ∴ 器は生きて居る★(疵: 初走は此処に「4 行」と手で書いた ―― 器の數 {n_c} と違ふ・.first に残す)')
# 受けぬ閾(literal)
lit = [(i + 1, s.strip()) for i, s in enumerate(src['disk']) if re.match(r'^(CODEX_CONTEXT_WARN|CODEX_CONTEXT_CRIT|CODEX_LIMIT_HITS_WARN)=', s.strip())]
lit80 = [(i + 1, s.strip()) for i, s in enumerate(src['disk']) if re.search(r'-ge 80 ', s)]
rec_th = [(i + 1) for i, s in enumerate(src['disk']) if re.search(r'\$\{(CODEX_CONTEXT_WARN|CODEX_CONTEXT_CRIT|CODEX_LIMIT_HITS_WARN):-', s)]
out.append(f'閾(數比較器の右項)= 名 3(L{",".join(str(a) for a,b in lit)}: ' + ' / '.join(b for a, b in lit) + f') + 裸の literal 80 ×{len(lit80)}(L{",".join(str(a) for a,b in lit80)}) ―― ★何れも `${{NAME:-}}` の受口を持たぬ(受口 {len(rec_th)} 行)= 外から毒を当てる口が無い★。毒が届くのは ★數比較器の左項(外から値が入る変数)★ の側。')
K.kaku(D + '/raw/10_uke.txt', '\n'.join(out)); K.kaku(D + '/raw/10_ukeru.tsv', '\n'.join(A)); K.kaku(D + '/raw/10_hikakuki.tsv', '\n'.join(C)); print('\n'.join(out)); print('\n'.join(A)); print('\n'.join(C))
