# -*- coding: utf-8 -*-
"""00 起(第78弾 km-84)―― 刻・枝・HEAD・札の sha16/行、★母數の根と深さの宣★(git 追跡 file・repo 根・深さ無制限・shell/python)、
其の census(拡張子別・上位 dir 別・shebang で拾ふ拡張子無し)、員外の宣(docs/evidence/ = 写しの束・.bak・queue/ の fixture・.venv・.claude)、此の PC の bash/python の版。読取のみ・repo へ 0 字。"""
import os, sys, time, hashlib, subprocess, shutil, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
FUDA = 'queue/tasks/ashigaru-mac-1.yaml'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout, p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')
fb = open(M + '/' + FUDA, 'rb').read()
out = [f'# 00 起 / 刻 {koku} / 枝 {br.strip()} / HEAD {head.strip()[:12]} / 札 {FUDA} sha16 {hashlib.sha256(fb).hexdigest()[:16]} {fb.count(b"\n")}行']
ls, rc = git('ls-files', '-z'); files = [f for f in ls.split('\0') if f]
out.append(f'git ls-files -z rc {rc} → 追跡 file {len(files)} 本(★母數の根= repo 根 {M} / 深さ= 無制限 / 集合= git 追跡 file のみ★)')
def shebang(p):
    try:
        with open(p, 'rb') as fh: h = fh.readline(128)
    except OSError: return ''
    return h.decode('utf-8', 'replace').strip() if h.startswith(b'#!') else ''
sh = []; py = []; ext_no = []; missing = 0
for f in files:
    p = M + '/' + f
    if not os.path.isfile(p): missing += 1; continue
    if f.endswith('.sh') or f.endswith('.bash'): sh.append(f)
    elif f.endswith('.py'): py.append(f)
    else:
        b = shebang(p)
        if b:
            if 'python' in b: py.append(f); ext_no.append((f, b))
            elif 'bash' in b or b.endswith('/sh') or ' sh' in b or 'zsh' in b: sh.append(f); ext_no.append((f, b))
out.append(f'追跡 file の内 disk に無い(追跡だが消えた) {missing} 本')
out.append(f'★母數の器の入口★: shell {len(sh)} 本(拡張子 .sh/.bash + shebang で拾つた拡張子無し)/ python {len(py)} 本(.py + shebang)/ 合 {len(sh) + len(py)} 本')
out.append('shebang で拾つた拡張子無しの file(逐語): ' + (' / '.join(f'{f}({b})' for f, b in ext_no) or '0 本'))
c = collections.Counter((f.split('/')[0] if '/' in f else '(根)') for f in sh + py)
out.append('上位 dir 別: ' + ' / '.join(f'{k} {v}' for k, v in c.most_common()))
out.append('員外(母數に載せぬ・宣): docs/evidence/**(先例の束= 写しの器・己の束を含む= 器が己を測る疵の予防)は ★追跡でも除く★ / 追跡外= .bak* / queue/**(fixture) / .venv / .claude / backups / __pycache__')
ev = [f for f in sh + py if f.startswith('docs/evidence/')]; out.append(f'  内 docs/evidence/ 配下の追跡 shell/python = {len(ev)} 本 → 除いた後の母數 file = {len(sh) + len(py) - len(ev)} 本')
# 員外の大きさ(disk・宣のみ)
def cnt(cmd): p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
b1, r1 = cnt("git ls-files | grep -c '\\.bak' ; :"); out.append(f'  追跡の .bak = {b1 or "0"}(grep -c・0 なら rc1 が正)')
for tool in ('bash', 'python3'):
    w = shutil.which(tool); v, _ = cnt(f'{w} --version 2>&1 | head -1'); out.append(f'{tool}= {w} / {v}')
out.append('scope_out(札): scripts/inbox_watcher.sh の ASW_PROCESS_TIMEOUT は ★母數に数へ・直さぬ(當席 km-82 で閉ぢ済)★ / km-83(專任2)の 3file の閾は彼の任・旗は本弾で測る / repo 外(~/bin 等)は測らぬ。')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
