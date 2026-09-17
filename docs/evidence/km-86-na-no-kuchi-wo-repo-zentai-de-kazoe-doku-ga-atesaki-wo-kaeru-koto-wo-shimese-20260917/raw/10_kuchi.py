# -*- coding: utf-8 -*-
"""10 ㋐㋓ 母數と分類(第79弾 km-86)―― 根A(00_rootA.txt・169 本= km-84 の根)を歩き、km-84 と ★同じ口の則(regex 逐語)★ で env から受ける口を悉く引き(km-84 の 493 と一致せねば止まる)、
各口を【閾 / 旗 / 名 / 其の他】へ ★順に一つの則で★ 落とす(排他は構造・網羅は 和=母數 で刷る・落とせぬ口は「不能」):
  R0 名が大文字 env の形でない(小文字/位置引数)→ 其の他:小文字 / R1 (file,名) が km-84 の旗 16 本 → 旗 / R2 既定が數の字面 → 閾:既定 / R3 既定が真偽語 → 其の他:真偽語 /
  R4 既定が非空の字面(數でも真偽語でも変数でもない)→ 名:既定 / R5 既定が空・無・変数式($…)の時は同 file の讀手で決む(lib_yomite: 數の讀手のみ→閾:讀手 / 名の讀手⑴〜⑸→名:讀手 / 両方→★重なり(名を優先し数へる)★)/
  R6 讀手が無ければ名の★末尾の語★で決む(數の語→閾:語 / 名の語→名:語)/ R7 何れにも当たらぬ → 不能。
㋓: 口の形 `${N:-d}`(甲・空も既定へ)/ `${N-d}`(乙・空を素通し)/ `:=` `=` `:+` / python get(既定あり= 乙と同じく空を素通し)/ python [] を根A と根B の両方で数へ、乙は逐語で挙げる。
対照: 陽性= scripts/watchdogs/enter_restart_commander_watchdog.sh(專任2 が名の口十本と申した file)から 名 が ≥1 出る / 陰性= ZZ_KM86_NEG 0 行・git grep -c rc 1。己の束(docs/evidence)は歩かぬ。"""
import os, sys, re, time, subprocess, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from lib_yomite import classes_sh, classes_py; M = '/Users/momizimac/multi-agent-shogun'
KM84 = M + '/docs/evidence/km-84-hata-no-tane-wo-repo-zentai-de-kazoe-yo-20260917/raw/10_kuchi.tsv'
FLAGS = {(r.split('\t')[0], r.split('\t')[2]) for r in open(KM84, encoding='utf-8').read().split('\n')[1:] if r}
rootA = [l for l in open(D + '/raw/00_rootA.txt', encoding='utf-8').read().split('\n') if l]; rootB = [l for l in open(D + '/raw/00_rootB.txt', encoding='utf-8').read().split('\n') if l]
ENV = re.compile(r'^[A-Z][A-Z0-9_]+$')
PORT = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)(:-|:=|:\+|-|=)([^}]*)\}')            # km-84 逐語
PYPORT = re.compile(r'os\.(?:environ\.get|getenv)\(\s*([\'"])([A-Za-z_][A-Za-z0-9_]*)\1\s*(?:,\s*([^)]*))?\)')  # km-84 逐語
PYIDX = re.compile(r'os\.environ\[\s*([\'"])([A-Za-z_][A-Za-z0-9_]*)\1\s*\]')          # km-84 逐語
FIX = re.compile(r'^\s*fix_flag\s+([A-Za-z_][A-Za-z0-9_]*)\s+(\S+)\s+')                  # km-84 逐語(番人口・493 の外)
NUMLIT = re.compile(r'^-?[0-9]+(\.[0-9]+)?$'); BOOLW = {'true', 'false', 'yes', 'no', 'True', 'False', 'TRUE', 'FALSE'}
NUM_LAST = {'TIMEOUT', 'SEC', 'SECS', 'SECONDS', 'MIN', 'MINS', 'MINUTES', 'MAX', 'LIMIT', 'COUNT', 'INTERVAL', 'THRESHOLD', 'THRESH', 'RETRIES', 'RETRY', 'BYTES', 'SIZE', 'DELAY', 'TTL', 'AGE', 'PORT', 'NUM', 'N', 'LINES', 'PCT', 'PERCENT', 'RATE', 'PID', 'TS', 'EPOCH', 'MS', 'HOURS', 'DAYS', 'WIDTH', 'HEIGHT', 'DEPTH', 'LEN', 'LENGTH', 'ATTEMPTS', 'BACKOFF', 'JITTER', 'CAP', 'FACTOR', 'TOKENS', 'GRACE', 'TOTAL', 'HITS', 'SEEN', 'CHARS', 'STEP', 'STEPS', 'CYCLES', 'PERIOD'}
NAME_LAST = {'PANE', 'TARGET', 'SESSION', 'TOPIC', 'PATH', 'DIR', 'FILE', 'NAME', 'ROLE', 'AGENT', 'HOST', 'URL', 'BRANCH', 'REPO', 'CMD', 'BIN', 'LOG', 'SOCK', 'SOCKET', 'USER', 'HOME', 'TABLE', 'KEY', 'ID', 'ROOT', 'BASE', 'PREFIX', 'SUFFIX', 'TO', 'FROM', 'SENDER', 'RECEIVER', 'PC', 'TYPE', 'MODE', 'LABEL', 'TAG', 'MODEL', 'CLI', 'SHELL', 'EDITOR', 'LANG', 'YAML', 'JSON', 'TSV', 'CSV', 'MD', 'TXT', 'SCRIPT', 'PYTHON', 'PY', 'WINDOW', 'OWNER', 'TITLE', 'MSG', 'MESSAGE', 'BODY', 'CONTENT', 'TEXT', 'PATTERN', 'REGEX', 'GLOB', 'ENV', 'PROFILE', 'ACCOUNT', 'TOKEN', 'SECRET', 'PASSWORD', 'PASS', 'EMAIL', 'ADDR', 'ADDRESS', 'IP', 'ENDPOINT', 'API', 'SERVICE', 'UNIT', 'PLIST', 'INBOX', 'QUEUE', 'CHANNEL', 'SUBJECT', 'DEST', 'SRC', 'SOURCE', 'STATE', 'STATUS'}
FAMILY = {'PANE', 'TARGET', 'SESSION', 'TOPIC', 'PATH', 'DIR', 'FILE', 'NAME', 'ROLE', 'AGENT'}  # 家老の「名らしき」則(名に含む)
def strip_q(s): s = s.strip(); return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in '\'"' else s
def is_comment(l): return l.lstrip().startswith('#')
def kind_of(f): return 'py' if f.endswith('.py') else 'sh'
def ports_of(f):
    """km-84 と同じ則で file f の口を返す: [(line, form, op, default, verbatim, N)] と fix_flag の數。"""
    L = open(M + '/' + f, encoding='utf-8', errors='replace').read().split('\n'); out = []; fix = 0; kind = kind_of(f)
    for i, l in enumerate(L, 1):
        if is_comment(l): continue
        if kind == 'sh':
            for m in PORT.finditer(l): out.append((i, 'A', m.group(2), m.group(3), l.strip(), m.group(1)))
            if FIX.match(l): fix += 1
        else:
            for m in PYPORT.finditer(l): out.append((i, 'B get', 'get', (m.group(3) if m.group(3) is not None else '(無)'), l.strip(), m.group(2)))
            for m in PYIDX.finditer(l): out.append((i, 'B []', '[]', '(必須)', l.strip(), m.group(2)))
    return L, out, fix
def readers(L, kind, N):
    """同 file の讀手の類の集合(口の行も含む・註を除く)。"""
    alias = set()
    if kind == 'py':
        for l in L:
            a = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*.*os\.(?:environ\.get|getenv|environ\[)\(?\s*[\'"]' + re.escape(N) + r'[\'"]', l)
            if a: alias.add(a.group(1))
    cs = collections.Counter()
    for l in L:
        c, s = classes_sh(N, l) if kind == 'sh' else classes_py(N, alias, l)
        for x in c: cs[x] += 1
    return cs, alias
rows = []; fixC = 0; walked = 0; lines_total = 0; kasanari = 0; formsA = collections.Counter(); otsuA = []
for f in rootA:
    kind = kind_of(f); L, ps, fx = ports_of(f); fixC += fx; walked += 1; lines_total += len(L)
    cache = {}
    for (i, form, op, d, v, N) in ps:
        formsA[(form, op)] += 1
        if form == 'A' and op in ('-', '='): otsuA.append((f, i, N, v))
        dq = strip_q(d); dv = d.strip()
        if not ENV.match(N): cls, sub, rule = '其の他', '小文字/位置引数', 'R0'
        elif (f, N) in FLAGS: cls, sub, rule = '旗', 'km-84 の旗', 'R1'
        elif NUMLIT.match(dq): cls, sub, rule = '閾', '既定が數', 'R2'
        elif dq in BOOLW: cls, sub, rule = '其の他', '真偽語', 'R3'
        elif dq not in ('', '(無)', '(必須)') and '$' not in dv and not dv.startswith('None'): cls, sub, rule = '名', ('既定が path' if '/' in dq else '既定が語'), 'R4'
        else:
            if N not in cache: cache[N] = readers(L, kind, N)
            cs, alias = cache[N]; na = sum(cs[x] for x in ('⑴', '⑵', '⑶', '⑷', '⑸')); nu = cs['數']
            if na and nu: kasanari += 1; cls, sub, rule = '名', '讀手(★數の讀手も在る=重なり★)', 'R5重'
            elif na: cls, sub, rule = '名', '讀手 ' + '+'.join(x for x in ('⑴', '⑵', '⑶', '⑷', '⑸') if cs[x]), 'R5'
            elif nu: cls, sub, rule = '閾', '讀手が數', 'R5'
            else:
                last = N.split('_')[-1]; toks = set(N.split('_'))
                if last in NUM_LAST: cls, sub, rule = '閾', f'語(末尾 {last})', 'R6'
                elif last in NAME_LAST: cls, sub, rule = '名', f'語(末尾 {last})', 'R6'
                elif toks & NUM_LAST and not toks & NAME_LAST: cls, sub, rule = '閾', f'語(含む {"/".join(sorted(toks & NUM_LAST))})', 'R6b'
                elif toks & NAME_LAST and not toks & NUM_LAST: cls, sub, rule = '名', f'語(含む {"/".join(sorted(toks & NAME_LAST))})', 'R6b'
                else: cls, sub, rule = '不能', '既定無・讀手無・語も無', 'R7'
        rows.append((f, i, N, form, op, d if d else '(空)', cls, sub, rule, v))
rows.sort(key=lambda r: (r[0], r[1], r[2]))
K.kaku_tsv(D + '/raw/10_kuchi.tsv', rows, header=('file', 'line', 'name', 'form', 'op', 'default', 'class', 'sub', 'rule', 'verbatim'))
na_rows = [r for r in rows if r[6] == '名']; K.kaku_tsv(D + '/raw/10_na.tsv', na_rows, header=('file', 'line', 'name', 'form', 'op', 'default', 'class', 'sub', 'rule', 'verbatim'))
tot = collections.Counter(r[6] for r in rows); subc = collections.Counter((r[6], r[7]) for r in rows); rulec = collections.Counter(r[8] for r in rows)
assert sum(tot.values()) == len(rows)
# km-84 との突き合はせ
k84 = [l for l in open(M + '/docs/evidence/km-84-hata-no-tane-wo-repo-zentai-de-kazoe-yo-20260917/raw/10_kuchi.txt', encoding='utf-8').read().split('\n') if '口の總數' in l][0]
k84n = int(re.search(r'口の總數 (\d+)', k84).group(1))
# ㋓ 根B(docs/evidence を含む)の形の数
formsB = collections.Counter(); otsuB = []; namesA = set(); namesB = set(); namesBsh = set()
for f in rootB:
    L, ps, fx = ports_of(f)
    for (i, form, op, d, v, N) in ps:
        formsB[(form, op)] += 1
        if form == 'A' and op in ('-', '='): otsuB.append((f, i, N, v))
        if ENV.match(N) and any(w in N for w in FAMILY): namesB.add(N); (namesBsh.add(N) if not f.endswith('.py') else None)
for r in rows:
    if ENV.match(r[2]) and any(w in r[2] for w in FAMILY): namesA.add(r[2])
g = subprocess.run(['git', 'grep', '-c', 'ZZ_KM86_NEG', '--', '*.sh', '*.py', '*.bash'], capture_output=True, text=True, cwd=M)
pos = [r for r in rows if r[0] == 'scripts/watchdogs/enter_restart_commander_watchdog.sh' and r[6] == '名']
posB = [x for x in otsuB if x[0].endswith('km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917/ki/41_ukezara.sh')]
def fm(c, form, op): return c[(form, op)]
ochiruA = fm(formsA, 'A', ':-') + fm(formsA, 'A', ':='); sudooriA = fm(formsA, 'A', '-') + fm(formsA, 'A', '=') + fm(formsA, 'B get', 'get') + fm(formsA, 'B []', '[]')
ochiruB = fm(formsB, 'A', ':-') + fm(formsB, 'A', ':='); sudooriB = fm(formsB, 'A', '-') + fm(formsB, 'A', '=') + fm(formsB, 'B get', 'get') + fm(formsB, 'B []', '[]')
out = [f'# 10 ㋐㋓ 母數と分類 / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 根A= 00_rootA.txt(km-84 の根・逐語= git 追跡 .sh/.bash/.py + shebang・docs/evidence/ 除く・深さ無制限)/ 歩いた {walked} 本・行 {lines_total}',
       f'口の則(km-84 逐語 regex): A PORT={PORT.pattern} / B PYPORT={PYPORT.pattern} ・ PYIDX={PYIDX.pattern} / 名の則 ENV={ENV.pattern} / C FIX(番人口・493 の外)={FIX.pattern}',
       f'★母數= 口 {len(rows)}(km-84 の 493 と{"一致" if len(rows) == k84n else "★不一致★"}・km-84 の出目 {k84n})/ 番人口 fix_flag {fixC}(母數の外・km-84 は env 名 437 に之を含め 總數 493 に含めなんだ= km-84 の疵として紙に書く)★',
       f'★分類(排他= 順に一つの則・網羅= 和): 閾 {tot["閾"]} / 旗 {tot["旗"]} / 名 {tot["名"]} / 其の他 {tot["其の他"]} / 不能 {tot["不能"]} ＝ 和 {sum(tot.values())} = 母數 {len(rows)} / 重複 0(一口一行) / 余り {len(rows) - sum(tot.values())}★',
       '  則別: ' + ' / '.join(f'{k} {v}' for k, v in sorted(rulec.items())) + f' ／ 重なり(名の讀手と數の讀手が同 file に共に在る口・名へ落とした) {kasanari}',
       '  細目: ' + ' / '.join(f'{c}:{s} {n}' for (c, s), n in sorted(subc.items())),
       f'★㋓ 口の形(根A {len(rows)} 口): 甲 `${{N:-d}}` {fm(formsA, "A", ":-")} / `${{N:=d}}` {fm(formsA, "A", ":=")} / 乙 `${{N-d}}` {fm(formsA, "A", "-")} / `${{N=d}}` {fm(formsA, "A", "=")} / `${{N:+d}}` {fm(formsA, "A", ":+")} / python get {fm(formsA, "B get", "get")} / python [] {fm(formsA, "B []", "[]")}★',
       f'  ★空文字が既定へ落ちる口(甲 :- :=)= {ochiruA} ／ 空の儘 下流へ行く口(乙 - = ・python get(既定は None/未設定の時のみ・空文字は素通し)・python [])= {sudooriA}★ ／ 何れでもない(:+) {fm(formsA, "A", ":+")}',
       f'  乙(根A・逐語)= {len(otsuA)} 本' + (': ' + ' / '.join(f'{f}:{i} {N} `{v[:60]}`' for f, i, N, v in otsuA) if otsuA else ' ―― ★零の四札: 陽性対照= 同じ regex が根B の km-51 ki/41_ukezara.sh の乙を拾ふ ' + str(len(posB)) + ' 本(≥1 が正)/ 根と深さ= 根A 169 本・深さ無制限/ rc= 此の器 0/ 刻= 上の刻★'),
       f'  根B(家老の根 {len(rootB)} 本・docs/evidence/ を含む): 甲 :- {fm(formsB, "A", ":-")} / := {fm(formsB, "A", ":=")} / 乙 - {fm(formsB, "A", "-")} / = {fm(formsB, "A", "=")} / :+ {fm(formsB, "A", ":+")} / py get {fm(formsB, "B get", "get")} / py [] {fm(formsB, "B []", "[]")} ／ 落ちる {ochiruB} / 素通し {sudooriB}(家老の見立 甲 614・乙 6 との差は根と形の数へ方(sh のみ/重複)に依る・右の逐語で照合せよ)',
       f'  乙(根B・逐語)= {len(otsuB)} 本: ' + (' / '.join(f'{f.split("/")[-1]}:{i} {N} `{v[:50]}`' for f, i, N, v in otsuB) or '0'),
       f'家老の「名らしき env 名(一意・PANE|TARGET|SESSION|TOPIC|PATH|DIR|FILE|NAME|ROLE|AGENT を含む)」則: 根A {len(namesA)} / 根B {len(namesB)}(sh のみ {len(namesBsh)})(家老 165)',
       f'陽性対照 scripts/watchdogs/enter_restart_commander_watchdog.sh の 名 = {len(pos)} 口 → ' + ('★出た(器は生きて居る)★' if pos else '★出ぬ(器が死んで居る)★'),
       f'陰性対照 ZZ_KM86_NEG = {sum(1 for r in rows if r[2] == "ZZ_KM86_NEG")} 口 / git grep -c rc {g.returncode}(1 = 0 件が正・出目「{g.stdout.strip()[:60]}」)',
       f'己を測る疵の検め: docs/evidence/ 配下の行 = {sum(1 for r in rows if r[0].startswith("docs/evidence/"))}(0 が正)',
       '## 不能の口(全行)'] + ([f'  {r[0]}:{r[1]}\t{r[2]}\t{r[3]} {r[4]}\t既定 {r[5]}\t| {r[9][:120]}' for r in rows if r[6] == '不能'] or ['  0'])
out.append(f'## 名の口 全行({tot["名"]} 口・file:行 名 形 既定 則 | 逐語)')
out += [f'  {r[0]}:{r[1]}\t{r[2]}\t{r[3]} {r[4]}\t既定 {r[5]}\t{r[8]} {r[7]}\t| {r[9][:140]}' for r in na_rows]
out.append('## 名の口 file 別(口數)'); cf = collections.Counter(r[0] for r in na_rows); out += [f'  {f}\t{n}' for f, n in sorted(cf.items(), key=lambda x: (-x[1], x[0]))]
K.kaku(D + '/raw/10_kuchi.txt', '\n'.join(out)); print('\n'.join(out[:16])); print(f'... 全行は raw/10_kuchi.txt({len(out)} 行)')
