# -*- coding: utf-8 -*-
"""30 ㋒ 毒十形(第79弾 km-86)―― 20 が挙げた害の讀手(同 file 20_shimo.tsv + 他file 20_cross.tsv・類 ⑴〜⑸)ごとに ★束内の写し器★ を建て、
毒十形(空文字・空白のみ・全角空白・`;`入り・`$(…)`入り・改行入り・`..`入り・絶対path・在らぬ名・256字超)+ 陰性(宣どほりの名= 口の既定の字面・無ければ kaname86)を env で当てる。
写し器= [口の行(10_na.tsv の純粋な口 `N=${N:-d}` / `: "${N:=d}"` を逐語・無ければ合成と宣す)] + [派生の別名の行(20 の「派X」・逐語)] + [讀手の写し]:
  ⑴⑵ tmux の段(`tmux … -t "$X" …` を逐語・★tmux/timeout は stub★= 引数を刷るのみ・実 tmux 0 打)/ ⑶⑷ 名を含む語を `printf 'TARGET=%q'` で刷る(open せぬ・存在は python が読取のみで見る)/ ⑸ test 式を逐語に `if … then BRANCH`。
  `$(…)` を含む讀手の断片は写さぬ(写せぬ・理由を刷る)。python の讀手は口の直後の値のみ刷る(下流の合成は写さぬ・宣)。
★二走★: 讀手の断片は引用符を数へて切る(初走は引用の中の | ; & で切り 110 走が写し器の壊れで鳴つた= 疵)・写し器は走らせる前に `bash -n` で検め壊れは「写せぬ」へ・向先は hex で byte 通りに取る(printf %q の別形を誤読せぬ)。
四欄= rc / 枝(BRANCH か 向先の類)/ 器の報せ行 / 向先(実測)+ 外の声行は別欄。向先の「変」= 陰性の向先に対し 素通し(値が其の儘)/ 既定へ(向先 不変)/ ★別形★、+ 上へ(..)/ 根が変はる(絶対)/ 割れた(語分割)/ ★実行された★(INJ86 が展開)。
scope_out(專任2 km-83 の三 file)は口の file か讀手の file が其れなら ★毒を当てず★ 数へて理由を刷る。稼働器 不觸・repo 0 字。"""
import os, sys, re, time, collections, shlex, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_run import run, mark, TMUX_FN; M = '/Users/momizimac/multi-agent-shogun'; H = D + '/raw/30_h'; os.makedirs(H, exist_ok=True)
HARM = ('⑴', '⑵', '⑶', '⑷', '⑸'); SO = {'scripts/pane_enter_watcher_supervisor.sh', 'scripts/lib/detect_stale.sh', 'scripts/watchdogs/enter_restart_commander_watchdog.sh'}
POIS = [('陰性', None), ('未設定', 'UNSET'), ('空文字', ''), ('空白のみ', ' '), ('全角空白', '\u3000'), (';入り', 'a;b'), ('$(…)入り', '$(printf INJ86)'), ('改行入り', 'a\nb'), ('..入り', '../km86'), ('絶対path', '/tmp/km86_abs'), ('在らぬ名', 'zz_no_such_km86'), ('256字超', 'A' * 300)]
na = [l.split('\t') for l in open(D + '/raw/10_na.tsv', encoding='utf-8').read().split('\n')[1:] if l]
r20 = [l.split('\t') for l in open(D + '/raw/20_shimo.tsv', encoding='utf-8').read().split('\n')[1:] if l]
rx = [l.split('\t') for l in open(D + '/raw/20_cross.tsv', encoding='utf-8').read().split('\n')[1:] if l]
SRC = {}
def src(f):
    if f not in SRC: SRC[f] = open(M + '/' + f, encoding='utf-8', errors='replace').read().split('\n')
    return SRC[f]
def strip_q(s): s = s.strip(); return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in '\'"' else s
cases = []; excluded = collections.Counter()
for r in r20:
    if r[3] in HARM: cases.append((r[0], r[2], r[0], int(r[1]), r[3], r[4]))
for r in rx:
    if r[4] in HARM: cases.append((r[0], r[1], r[2], int(r[3]), r[4], r[5]))
todo = []; seen = set()
for pf, N, rf, ln, cls, am in cases:
    if pf in SO or rf in SO: excluded[('scope_out(專任2 km-83 の的・毒当てを除く)', pf.split('/')[-1] if pf in SO else rf.split('/')[-1])] += 1; continue
    al = re.search(r'派([A-Za-z_][A-Za-z0-9_]*)', am); al = al.group(1) if al else None
    key = (N, rf, ln, pf, al)
    if key in seen: continue
    seen.add(key); todo.append((pf, N, rf, ln, cls, al))
def port_line(pf, N):
    rows = [r for r in na if r[0] == pf and r[2] == N]; kind = 'py' if pf.endswith('.py') else 'sh'
    if kind == 'sh':
        for r in rows:
            v = r[9]
            if re.match(r'^(export\s+)?' + re.escape(N) + r'="?\$\{' + re.escape(N) + r'(:-|:=|-|=)[^}]*\}"?\s*$', v) or re.match(r'^:\s+"?\$\{' + re.escape(N) + r':=[^}]*\}"?\s*$', v): return v, '逐語', r[4], strip_q(r[5]) if r[5] != '(空)' else ''
        r = rows[0]; d = '' if r[5] == '(空)' else r[5]
        return f'{N}="${{{N}{r[4]}{d}}}"', '合成', r[4], strip_q(d)
    else:
        for r in rows:
            m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:str\(|int\()?os\.(?:environ\.get|getenv|environ\[)', r[9])
            if m: return r[9].strip(), '逐語', r[4], ('' if r[5] in ('(無)', '(必須)', '(空)') else strip_q(r[5]))
        return None, '写せぬ(python の口が代入形でない)', rows[0][4], ''
SPECIAL = {'HOME', 'PWD', 'RANDOM', 'BASH_SOURCE', 'BASHPID', 'PPID', 'LINENO', 'SECONDS', 'FUNCNAME', 'OLDPWD', 'IFS', 'PATH', 'USER', 'SHELL', 'TERM', 'LANG', 'LC_ALL', 'TMUX', 'TMUX_PANE', 'EUID', 'UID', 'HOSTNAME', 'REPLY', 'PIPESTATUS', 'OSTYPE'}
WORD = r'(?:"(?:[^"\\]|\\.)*"|\'[^\']*\'|[^\s"\'|&;()<>])+'
HEX = "| od -An -v -tx1 | tr -d ' \\n'; printf '\\n'"
def cut_cmd(raw, start):
    """raw[start:] を引用符を数へて ★引用の外の★ | ; & ) で切る。返り= (断片, 引用が閉ぢたか)"""
    i = start; q = None; out = []
    while i < len(raw):
        ch = raw[i]
        if q:
            out.append(ch)
            if ch == '\\' and q == '"' and i + 1 < len(raw): out.append(raw[i + 1]); i += 2; continue
            if ch == q: q = None
        elif ch in ('"', "'"): q = ch; out.append(ch)
        elif ch == '\\' and i + 1 < len(raw): out.append(ch); out.append(raw[i + 1]); i += 2; continue
        elif ch in '|;&)': break
        else: out.append(ch)
        i += 1
    return ''.join(out).rstrip(), (q is None)
def extract(cls, raw, X):
    R = r'\$\{?' + re.escape(X) + r'(?![A-Za-z0-9_])'
    if cls in ('⑴', '⑵'):
        for m in re.finditer(r'\btmux\b', raw):
            seg, closed = cut_cmd(raw, m.start())
            if not re.search(R, seg): continue
            if not closed: return None, '写せぬ(引用が閉ぢぬ段)'
            seg = re.sub(r'\s+[12]?>\s*\S+', '', seg); seg = re.sub(r'\s+2>&1', '', seg)
            if '$(' in seg or '`' in seg: return None, '写せぬ($(…) を含む段)'
            return seg, 'tmux 段'
        return None, '写せぬ(tmux の段が無い)'
    if cls in ('⑶', '⑷'):
        for m in re.finditer(WORD, raw):
            w = m.group(0)
            if re.search(R, w):
                if '$(' in w or '`' in w: return None, '写せぬ($(…) を含む語)'
                return f"printf 'TARGET='; printf '%s' {w} {HEX}", '語'
        return None, '写せぬ(名を含む語が無い)'
    if cls == '⑸':
        if re.search(r'\bcase\s', raw) and not re.search(r'\[\[?\s', raw): return None, '写せぬ(case)'
        for m in re.finditer(r'\[\[\s.*?\s\]\]|\[\s.*?\s\]', raw):
            if re.search(R, m.group(0)):
                te = m.group(0)
                if '$(' in te or '`' in te: return None, '写せぬ($(…) を含む test)'
                return f"printf 'TARGET='; printf '%s' \"${X}\" {HEX}; if {te}; then printf 'BRANCH=then\\n'; else printf 'BRANCH=else\\n'; fi", 'test 式'
        return None, '写せぬ(test 式が無い)'
def alias_line(rf, X, N):
    for l in src(rf):
        if l.lstrip().startswith('#'): continue
        m = re.match(r'^\s*(?:local\s+|export\s+|declare\s+[-a-zA-Z]+\s+|readonly\s+)?' + re.escape(X) + r'=(.*)$', l)
        if m and re.search(r'\$\{?' + re.escape(N) + r'(?![A-Za-z0-9_])', l): return X + '=' + m.group(1).strip()
    return None
rows = []; harn = []; utsusenu = collections.Counter(); utsu_list = []
for idx, (pf, N, rf, ln, cls, al) in enumerate(todo, 1):
    kind = 'py' if rf.endswith('.py') else 'sh'; pl, pk, op, dflt = port_line(pf, N)
    raw = src(rf)[ln - 1]; X = al or N
    if kind != ('py' if pf.endswith('.py') else 'sh'): utsusenu['写せぬ(口と讀手の言語が違ふ)'] += 1; utu_list = utsu_list.append((pf, N, rf, ln, cls, '言語違ひ')); continue
    if pl is None: utsusenu[pk] += 1; utsu_list.append((pf, N, rf, ln, cls, pk)); continue
    if kind == 'sh':
        piece, how = extract(cls, raw, X)
        if piece is None: utsusenu[how] += 1; utsu_list.append((pf, N, rf, ln, cls, how)); continue
        alin = alias_line(rf, X, N) if al else None
        if al and alin is None: utsusenu['写せぬ(別名の行が引けぬ)'] += 1; utsu_list.append((pf, N, rf, ln, cls, '別名の行が引けぬ')); continue
        if alin and ('$(' in alin or '`' in alin) and not re.search(r'\$\(\s*(tmux|timeout|printf|echo|basename|dirname|cd |pwd|date)', alin): utsusenu['写せぬ(別名の行に $(…))'] += 1; utsu_list.append((pf, N, rf, ln, cls, '別名の行に $(…)')); continue
        body = ['#!/bin/bash', f'# 写し器 {idx} ―― 口 {pf}:{N}({pk}) / 讀手 {rf}:{ln} 類 {cls}' + (f' / 派 {al}' if al else ''), TMUX_FN, pl] + ([alin] if alin else []) + [piece]
        text = '\n'.join(body)
        others = sorted({v for v in re.findall(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', '\n'.join(body[3:])) if v not in (N, X) and v not in SPECIAL})
        preset = [(v, f'@{v}@') for v in others]
    else:
        body = [f'# 写し器 {idx} ―― 口 {pf}:{N}({pk}) / 讀手 {rf}:{ln} 類 {cls}(python= 口の直後の値のみ・下流の合成は写さぬ)', 'import os, binascii', pl, f"print('TARGET=' + binascii.hexlify(str({pl.split('=')[0].strip()}).encode('utf-8')).decode())"]
        text = '\n'.join(body); preset = []
    hp = H + f'/{idx:03d}_{N}_{cls}.{kind}'; K.kaku(hp, text)
    if kind == 'sh':
        chk = subprocess.run(['/bin/bash', '-n', hp], capture_output=True)
        if chk.returncode != 0: utsusenu['写せぬ(写しが壊れた・bash -n)'] += 1; utsu_list.append((pf, N, rf, ln, cls, 'bash -n ' + chk.stderr.decode('utf-8', 'replace').strip()[:80])); os.remove(hp); continue
    neg = dflt if (dflt and '$' not in dflt and '(' not in dflt) else 'kaname86'
    res = {}
    for label, v in POIS:
        val = neg if v is None else v; x = run(hp, kind, N, (None if v == 'UNSET' else val), D, preset)
        if x['tmux']:
            a = x['tmux']; j = next((k for k in range(len(a) - 1) if a[k] in ('-t', '-s')), None); tval = a[j + 1] if j is not None else ' '.join(a); tg = ' '.join(a)
        else: tval = x['targets'][0] if x['targets'] else '無'; tg = tval
        res[label] = (x, val, tg, tval)
    xn, vneg, tneg, tvneg = res['陰性']; xu, _, _, tvun = res['未設定']   # ★三走: 既定の向先= 未設定で走らせた向先(既定が $… の式でも正しく引ける・初〜二走は既定の字面で比べ 27 走を別形と誤つた)
    for label, v in POIS:
        x, val, tg, tval = res[label]; hen = []
        if label == '陰性': hen.append('宣どほり' if tval != '無' else '無')
        elif label == '未設定': hen.append('既定の向先(比較の基準)')
        else:
            if tval == '無': hen.append('無(向先が刷られぬ)')
            elif (tval == tvun or (tval == tvneg and val != vneg)) and tval != '無': hen.append('既定へ落ちた(向先 不変)')
            elif tvneg != '無' and vneg in tvneg and tval == tvneg.replace(vneg, val): hen.append('素通し(値が其の儘 向先へ)')
            else: hen.append('★別形★')
            ochita = hen[-1].startswith('既定へ')
            first = lambda t: (t.split('/', 2)[1] if t.startswith('/') else t.split('/', 1)[0])   # 根の第一成分('' なら / そのもの)
            if '..' in tval and not ochita: hen.append('上へ(..)')
            if tval.startswith('/') and not ochita and tval != '無' and (not tvun.startswith('/') or first(tval) != first(tvun)): hen.append('根が変はる(絶対)')   # ★四走: 既定へ落ちた走には付けぬ・既定が絶対でも第一成分が違へば根が変はる
            if x['nargs'] and xn['nargs'] and int(x['nargs'][0]) != int(xn['nargs'][0]): hen.append(f'割れた(引数 {xn["nargs"][0]}→{x["nargs"][0]})')
            if 'INJ86' in tg and '$(' not in tg: hen.append('★実行された★')
            if '\n' in tval and not ochita: hen.append('改行を含む')
            if '\u3000' in tval and not ochita: hen.append('全角空白を含む')
            if label == '空白のみ' and ' ' not in tval and tval != '無': hen.append('空白が消えた')
        exists = ''
        if cls in ('⑶',) and kind == 'sh' and tval not in ('無', '') and '@' not in tval:
            exists = '在' if tval.strip() and os.path.exists(tval) else '無'   # 読取のみ(os.path.exists・open せぬ)
        rows.append((idx, pf, N, rf, ln, cls, al or '', pk, label, mark(val), x['rc'], x['branch'], x['utsuwa'], x['soto'], mark(tval) if len(tval) <= 40 else tval[:60].replace('\n', '␊') + f'…({len(tval)}字)', '+'.join(hen), exists, x['head']))
    harn.append((idx, pf, N, rf, ln, cls, al, pk, hp))
K.kaku_tsv(D + '/raw/30_doku.tsv', rows, header=('idx', 'port_file', 'name', 'reader_file', 'line', 'class', 'alias', 'port_kind', 'poison', 'value', 'rc', 'branch', 'utsuwa_lines', 'soto_lines', 'target', 'hen', 'exists', 'stderr_head'))
K.kaku_tsv(D + '/raw/30_utsusenu.tsv', utsu_list, header=('port_file', 'name', 'reader_file', 'line', 'class', 'reason'))
tally = collections.defaultdict(collections.Counter)
for r in rows:
    if r[8] in ('陰性', '未設定'): continue
    tally[(r[5], r[8])]['走'] += 1
    for h in r[15].split('+'): tally[(r[5], r[8])][h.split('(')[0]] += 1
    if r[13]: tally[(r[5], r[8])]['声>0'] += 1
    if r[12]: tally[(r[5], r[8])]['報せ>0'] += 1
    if r[10]: tally[(r[5], r[8])]['rc≠0'] += 1
ncls = collections.Counter(h[5] for h in harn)
out = [f'# 30 ㋒ 毒十形 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 害の讀手(同file+他file・類⑴〜⑸) {len(cases)} 行 → scope_out 除外 {sum(excluded.values())} / 重複を畳んで {len(todo)} 件 / 写せた {len(harn)}(⑴ {ncls["⑴"]} ⑵ {ncls["⑵"]} ⑶ {ncls["⑶"]} ⑷ {ncls["⑷"]} ⑸ {ncls["⑸"]})/ 写せぬ {sum(utsusenu.values())} / 値 {len(POIS)}(毒 10 + 陰性 + 未設定)/ 走 {len(rows)} / 写し器= raw/30_h/ / stub= raw/stub/(tmux 実打ち 0)',
       '則: 向先= tmux 段なら stub が刷つた argv(hex)の -t/-s の右・語/test なら printf %s を hex で受けた byte 通りの文字列。「変」= 陰性(宣どほりの名= 口の既定の字面・無ければ kaname86)の向先との比べ。四欄= rc/枝/報せ/向先、声は別欄。',
       'scope_out 除外(件・理由・file): ' + (' / '.join(f'{k[0]} {k[1]} {v}' for k, v in sorted(excluded.items())) or '0'),
       '写せぬ(理由別): ' + (' / '.join(f'{k} {v}' for k, v in sorted(utsusenu.items())) or '0')]
out.append('## 類 × 毒 の集計(走 / 素通し / 既定へ / ★別形★ / 上へ / 根が変はる / 割れた / ★実行された★ / 空白が消えた / 声>0 / 報せ>0 / rc≠0)')
for cls in HARM:
    for label, _ in POIS[1:]:
        c = tally[(cls, label)]
        if not c['走']: continue
        out.append(f'  {cls} {label}\t走 {c["走"]}\t素通し {c["素通し"]}\t既定へ {c["既定へ落ちた"]}\t★別形★ {c["★別形★"]}\t上へ {c["上へ"]}\t根が変はる {c["根が変はる"]}\t割れた {c["割れた"]}\t★実行された★ {c["★実行された★"]}\t空白が消えた {c["空白が消えた"]}\t声>0 {c["声>0"]}\t報せ>0 {c["報せ>0"]}\trc≠0 {c["rc≠0"]}')
tot = collections.Counter()
for r in rows:
    if r[8] not in ('陰性', '未設定'):
        tot['走'] += 1; tot['声>0'] += bool(r[13]); tot['報せ>0'] += bool(r[12]); tot['黙つて向先が変はつた'] += (not r[12] and not r[13] and (r[15].startswith('素通し') or r[15].startswith('★別形★')))
        tot['黙つて既定へ落ちた'] += (not r[12] and not r[13] and r[15].startswith('既定へ'))
out.append(f'★毒 10 形 × 写し器 {len(harn)} = {tot["走"]} 走(+ 陰性・未設定 各 {len(harn)}): 器の報せ>0 {tot["報せ>0"]} / 外の声>0 {tot["声>0"]} / ★黙つて向先が変はつた(報せ 0・声 0・素通し or 別形){tot["黙つて向先が変はつた"]}★ / 黙つて既定へ落ちた {tot["黙つて既定へ落ちた"]} / 向先が刷られぬ等 {tot["走"] - tot["黙つて向先が変はつた"] - tot["黙つて既定へ落ちた"]}')
out.append('## 写し器ごとの陰性と毒の向先(idx 口 讀手 類 | 陰性→向先 | 空文字→ | ..入り→ | 絶対→ | ;入り→ | $(…)→(実行?) )')
for (idx, pf, N, rf, ln, cls, al, pk, hp) in harn:
    sub = {r[8]: r for r in rows if r[0] == idx}
    out.append(f'  {idx:03d} {pf.split("/")[-1]}:{N}({pk}) → {rf.split("/")[-1]}:{ln} {cls}' + (f' 派{al}' if al else '') + f'\t陰性 {sub["陰性"][14][:40]}\t未設定 {sub["未設定"][14][:30]}\t空文字 {sub["空文字"][14][:30]} [{sub["空文字"][15]}]\t.. {sub["..入り"][14][:30]} [{sub["..入り"][15]}]\t絶対 {sub["絶対path"][14][:30]} [{sub["絶対path"][15]}]\t; [{sub[";入り"][15]}]\t$( [{sub["$(…)入り"][15]}]')
out.append('## 声が鳴つた走(idx 名 毒 rc 声 | 頭)'); out += [f'  {r[0]:03d} {r[2]} {r[8]} rc{r[10]} 声{r[13]} | {r[17]}' for r in rows if r[13]] or ['  (鳴つた走 0)']
K.kaku(D + '/raw/30_tally.txt', '\n'.join(out)); print('\n'.join(out[:5 + 55])); print('...'); print(out[5 + 55 + 0] if len(out) > 60 else '')
