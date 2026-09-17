# -*- coding: utf-8 -*-
"""40 ―― 定義丁(${NAME:-數} の口)を ★全★ と ★閾(名の條)★ の二表で数へ、口ごとに 45 番人の三態(+別形)と 47 下流の比較器を測る。disk と HEAD 6ba8fcb2。読取のみ。
出目: 40_tei_all.tsv(全口) / 40_tei_shikii.tsv(閾の口) / 45_bannin.tsv / 47_hikaku.tsv / 40_tei.txt(要約)"""
import sys, re, subprocess, os
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gg import gg, fuda, koku, HEAD, is_comment, M
RE_T = r'\$\{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\}'; RE_PY = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*):-([0-9]+)\}')
RE_H = re.compile(r'既定[^ \t]{0,8}へ倒す|fail-closed'); OPS = r'-(lt|le|gt|ge|eq|ne)\b'
def src(path, rev):
    if rev is None: return open(M + '/' + path, encoding='utf-8', errors='replace').read().split('\n')
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True, cwd=M).stdout.decode('utf-8', 'replace').split('\n')
def guarded_names(lines):
    """此の file が fix_threshold で守る名(明示 arg1 ∪ for _t in の list)。"""
    g = set(); s = '\n'.join(lines)
    for ln in lines:
        m = re.match(r'^\s*fix_threshold\s+([A-Z][A-Z0-9_]*)\s', ln)
        if m: g.add(m.group(1))
    m = re.search(r'^for _t in (.*?); do$', s, re.S | re.M)
    if m: g |= set(w.split(':')[0] for w in m.group(1).replace('\\\n', ' ').split() if ':' in w)
    return g
def case_guard(lines, var, start):
    """別形の番人: 口の後に case "$var" in … が在り、其の 6 行内に 丙 の文言が在る → 其の行番号。"""
    for i in range(start, len(lines)):
        if re.match(r'^\s*case\s+"?\$\{?' + re.escape(var) + r'\}?"?\s+in', lines[i]):
            for j in range(i, min(i + 7, len(lines))):
                if RE_H.search(lines[j]): return i + 1
    return 0
def comparators(lines, var, start):
    hits = []
    for i in range(start, len(lines)):
        ln = lines[i]
        if is_comment(ln): continue
        if not re.search(r'\$\{?' + re.escape(var) + r'\b\}?', ln): continue
        if (re.search(OPS, ln) and re.search(r'\[', ln)) or re.search(r'\(\(', ln): hits.append(i + 1)
    return hits
def receiver(text, name, n, lines=(), idx=0):
    exp = r'\$\{' + name + ':-' + n + r'\}'
    # ★.first の疵★: env 行が \ で續く時(supervisor:52)、子の path は次行に在る → 續き 2 行を継いで見る
    if text.rstrip().endswith('\\') and lines: text = text.rstrip()[:-1] + ' ' + ' '.join(l.strip().rstrip('\\') for l in lines[idx + 1: idx + 3])
    m = re.match(r'^\s*(?:export\s+|local\s+)?([A-Za-z_][A-Za-z0-9_]*)=["\']?' + exp, text)
    if m: return ('var', m.group(1))
    if re.search(r'^\s*(?:[A-Z_]+="' + RE_T + r'"\s+)+', text) and re.search(r'\.py|\.sh|\$[A-Z_]*(PY|SH|WATCHER)', text): return ('env→子', text)
    if re.search(r'(=|!=)\s+"?' + exp, text) or re.search(exp + r'"?\s+(=|!=)\s', text): return ('同行文字列比較(= / != ・數比較に非ず)', name)
    if re.search(OPS + r'\s+"?' + exp, text) or re.search(exp + r'"?\s+' + OPS, text): return ('同行比較', name)
    if re.search(r'\$\(\(.*' + exp + r'.*\)\)', text): return ('同行算術', name)
    if re.match(r'^\s*case\s+"?' + exp, text): return ('同行case', name)
    return ('用途', re.sub(r'\s+', ' ', text.strip())[:40])
sums = []; all_rows = []; shi_rows = []; ban_rows = []; hik_rows = []
for rev in (None, HEAD):
    tag = 'disk' if rev is None else 'HEAD'; r, rc, argv = gg(RE_T, rev); cache = {}
    n_all = n_note = 0; files_all = set(); files_shi = set(); n_shi = 0; alt_upper = 0
    for path, no, text in r:
        for m in RE_PY.finditer(text):
            name, dflt = m.group(1), m.group(2); note = is_comment(text); n_all += 1; files_all.add(path)
            if note: n_note += 1
            upper = bool(re.match(r'^[A-Z][A-Z0-9_]*$', name)); shi = (not note) and upper and int(dflt) >= 1
            if (not note) and upper: alt_upper += 1
            all_rows.append((tag, path, no, name, dflt, '註' if note else '-', '閾' if shi else '-', '/archive/' in path and 'archive' or '-', text.strip()[:70]))
            if not shi: continue
            n_shi += 1; files_shi.add(path); shi_rows.append((tag, path, no, name, dflt, text.strip()[:80]))
            lines = cache.setdefault(path, src(path, rev)); g = guarded_names(lines); has_def = any(re.match(r'^fix_threshold\(\)\{', l) for l in lines)
            has_call = any(re.match(r'^\s*fix_threshold\s', l) for l in lines)
            kind, recv = receiver(text, name, dflt, lines, no - 1); jtext = recv if kind == 'env→子' else text
            cg = case_guard(lines, recv if kind == 'var' else name, no - 1)
            if name in g: state = 'C 守られて居る(fix_threshold)'
            elif cg: state = f'C′ 別形の番人(case … 既定へ倒す L{cg})'
            elif has_call or has_def: state = 'B 呼んで居るが其の名を守らぬ'
            else: state = 'A fix_threshold 無し'
            # 他 file の番人(env で渡る名): 樹全体で fix_threshold NAME を呼ぶ file
            others = sorted(set(p for p, _, t in gg(r'^[ \t]*fix_threshold[ \t]+' + name + r'[ \t]', rev)[0] if p != path)) if kind in ('env→子', 'var') else []  # ★.first の疵: \s は macOS ERE に無く 0 件に落ちて居た★
            if state.startswith('A') and others: state = 'A′ 己は無し・他 file が守る'
            ban_rows.append((tag, path, no, name, state, kind, recv if kind != 'env→子' else name, ' '.join(others) or '-'))
            # 比較器
            if kind in ('同行比較', '同行算術'): hk = ['同行']
            elif kind == '同行case': hk = ['case(値の分岐・比較器に非ず)']
            elif kind == 'var':
                hk = [str(x) for x in comparators(lines, recv, no)]
                for i in range(no, len(lines)):
                    mm = re.match(r'^\s*(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)=["\']?\$\{?' + re.escape(recv) + r'\b', lines[i])
                    if mm and mm.group(1) != recv:
                        via = comparators(lines, mm.group(1), i + 1)
                        if via: hk.append(f'経由 L{i + 1}({mm.group(1)})→{via}')
            elif kind == 'env→子':
                child = [t for t in re.findall(r'[A-Za-z_./$]*\.(?:py|sh)|\$[A-Z_]+', jtext) if t.endswith(('.py', '.sh')) or t.startswith('$')]
                cf = ''
                for t in child:
                    if t.startswith('$'):
                        mm = re.search(r'^' + t[1:] + r'="?([^"\n]+)"?', '\n'.join(lines), re.M); t = mm.group(1) if mm else t
                    t = re.sub(r'^\$\{?SCRIPT_DIR\}?/|^\$\(dirname "\$0"\)/|^\$\{?HERE\}?/', 'scripts/', t)
                    if t.endswith(('.py', '.sh')): cf = t
                cpath = cf if os.path.exists(M + '/' + cf) else ('scripts/' + os.path.basename(cf) if os.path.exists(M + '/scripts/' + os.path.basename(cf)) else '')
                if cpath:
                    cl = src(cpath, rev); use = [i + 1 for i, l in enumerate(cl) if re.search(r'\b' + name + r'\b', l) and not is_comment(l)]
                    hk = [f'子 {cpath}: 名の行 {use}']
                else: hk = [f'子 未解決({text.strip()[:40]})']
            else: hk = []
            hik_rows.append((tag, path, no, name, kind, recv, '有' if hk and hk != ['case(値の分岐・比較器に非ず)'] else '無', ' '.join(hk) or '-'))
    sums.append(f'[{tag}] rc {rc} / 行 {len(r)} / ★丁全= 口 {n_all}(内 註 {n_note}) file {len(files_all)}(archive/ {len([p for p in files_all if "/archive/" in p])})★ / 別條(大文字名・註除く・既定 0 も含む)= {alt_upper} 口 / ★丁閾(大文字名 ∧ 既定≥1 ∧ 註除く)= 口 {n_shi} file {len(files_shi)}★')
    sums.append(f'  逐語: {argv}')
    st = {}
    for x in ban_rows:
        if x[0] == tag: st[x[4][:2]] = st.get(x[4][:2], 0) + 1
    sums.append(f'  45 番人(閾の口ごと): ' + ' / '.join(f'{k} {v}' for k, v in sorted(st.items())))
    hh = [x for x in hik_rows if x[0] == tag]; sums.append(f'  47 比較器(閾の口ごと): 有 {sum(1 for x in hh if x[6]=="有")} / 無 {sum(1 for x in hh if x[6]=="無")}')
K.kaku_tsv(D + '/raw/40_tei_all.tsv', all_rows, ['rev', 'path', 'line', 'name', 'default', 'note', 'shikii', 'archive', 'text'])
K.kaku_tsv(D + '/raw/40_tei_shikii.tsv', shi_rows, ['rev', 'path', 'line', 'name', 'default', 'text'])
K.kaku_tsv(D + '/raw/45_bannin.tsv', ban_rows, ['rev', 'path', 'line', 'name', 'state', 'kind', 'receiver', 'other_file_guard'])
K.kaku_tsv(D + '/raw/47_hikaku.tsv', hik_rows, ['rev', 'path', 'line', 'name', 'kind', 'receiver', 'comparator', 'where'])
K.kaku(D + '/raw/40_tei.txt', f'# 40 定義丁 ${{NAME:-數}} の口 / 刻 {koku()} / 根= scripts .claude(git 追跡 file 全深) / 條(全)= ERE \\$\\{{[A-Za-z_][A-Za-z0-9_]*:-[0-9]+\\}} 1 出現 1 口(一行に複数可) / 條(閾)= 名が ^[A-Z][A-Z0-9_]*$ ∧ 既定 ≥1 ∧ 註行でない ―― ★「閾らしき」は此の條で置き換へた(語感で数へぬ)★\n' + '\n'.join(sums) + '\n45 三態の條: A= file に fix_threshold の定義も呼出も無し / B= 呼んで居るが其の名が arg1 にも for list にも無し / C= 守られて居る / C′= fix_threshold でなく case…既定へ倒す の別形番人(口の後 6 行内に丙の文言)\n47 の條: 受け皿 var が口の後の行で [ … -lt/-le/-gt/-ge/-eq/-ne … ] か (( )) に入る行番号 / 同行比較・同行算術は其の行 / env→子 は子 file で名が出る行を示す(子の中の番人は別途)\n零の札:\n' + '\n'.join(fuda(RE_T)))
print(open(D + '/raw/40_tei.txt', encoding='utf-8').read())
