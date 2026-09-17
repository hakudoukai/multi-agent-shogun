# -*- coding: utf-8 -*-
"""00 起(第79弾 km-86)―― 刻・枝・HEAD・札の sha16/行、★二つの母數の根を並べて宣し、差を file 名で名指す★:
  根A(km-84 の根・本弾の主)= git 追跡 file の内 .sh/.bash/.py + shebang(bash/sh/zsh/python)で拾ふ拡張子無し、docs/evidence/ を除く、disk に在る物。
  根B(家老の根 11:18)= `git ls-files -- '*.sh' '*.py'`(docs/evidence/ を含む・shebang 無し・.bash 無し)。
census(拡張子別・上位 dir 別)、員外の宣、此の PC の bash/python の版。読取のみ・repo へ 0 字。git の path は -z で受ける(非ASCII path の引用符に騙されぬ)。"""
import os, sys, time, hashlib, subprocess, shutil, collections
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
FUDA = 'queue/tasks/ashigaru-mac-1.yaml'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout, p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')
fb = open(M + '/' + FUDA, 'rb').read()
out = [f'# 00 起 / 刻 {koku} / 枝 {br.strip()} / HEAD {head.strip()[:12]} / 札 {FUDA} sha16 {hashlib.sha256(fb).hexdigest()[:16]} {fb.count(b"\n")}行']
ls, rc = git('ls-files', '-z'); files = [f for f in ls.split('\0') if f]
out.append(f'git ls-files -z rc {rc} → 追跡 file {len(files)} 本(repo 根 {M})')
def shebang(p):
    try:
        with open(p, 'rb') as fh: h = fh.readline(128)
    except OSError: return ''
    return h.decode('utf-8', 'replace').strip() if h.startswith(b'#!') else ''
# 根A(km-84 と同じ則・逐語)
A_sh = []; A_py = []; ext_no = []; missing = []
for f in files:
    p = M + '/' + f
    if not os.path.isfile(p): missing.append(f); continue
    if f.endswith('.sh') or f.endswith('.bash'): A_sh.append(f)
    elif f.endswith('.py'): A_py.append(f)
    else:
        b = shebang(p)
        if b:
            if 'python' in b: A_py.append(f); ext_no.append((f, b))
            elif 'bash' in b or b.endswith('/sh') or ' sh' in b or 'zsh' in b: A_sh.append(f); ext_no.append((f, b))
A_all = A_sh + A_py; A_ev = [f for f in A_all if f.startswith('docs/evidence/')]; A = sorted(set(A_all) - set(A_ev))
out.append(f'追跡 file の内 disk に無い(追跡だが消えた) {len(missing)} 本' + (': ' + ' / '.join(missing) if missing else ''))
out.append(f'★根A(km-84 の根・本弾の主・逐語)= 追跡 .sh/.bash/.py + shebang 拡張子無し {len(A_all)} 本(shell {len(A_sh)} / python {len(A_py)})、docs/evidence/ 配下 {len(A_ev)} 本を除き ★{len(A)} 本★(shell {sum(1 for f in A if f in set(A_sh))} / python {sum(1 for f in A if f in set(A_py))})')
out.append('  shebang で拾つた拡張子無し(逐語): ' + (' / '.join(f'{f}({b})' for f, b in ext_no if not f.startswith('docs/evidence/')) or '0 本') + f' ／ docs/evidence/ 配下の同類 {sum(1 for f, b in ext_no if f.startswith("docs/evidence/"))} 本')
# 根B(家老の根・逐語 `git ls-files -- '*.sh' '*.py'`)
lsB, rcB = git('ls-files', '-z', '--', '*.sh', '*.py'); Bf = sorted(f for f in lsB.split('\0') if f)
B_ev = [f for f in Bf if f.startswith('docs/evidence/')]
out.append(f"★根B(家老の根・逐語 `git ls-files -- '*.sh' '*.py'`・rc {rcB})= ★{len(Bf)} 本★(内 docs/evidence/ 配下 {len(B_ev)} 本・disk に無い {sum(1 for f in Bf if not os.path.isfile(M + '/' + f))} 本)")
onlyA = sorted(set(A) - set(Bf)); onlyB = sorted(set(Bf) - set(A)); onlyB_nonev = [f for f in onlyB if not f.startswith('docs/evidence/')]
out.append(f'★差(file 名で名指す)★: 根A にのみ在る {len(onlyA)} 本 / 根B にのみ在る {len(onlyB)} 本(内 docs/evidence/ {len(onlyB) - len(onlyB_nonev)} 本・其の外 {len(onlyB_nonev)} 本)/ 両方に在る {len(set(A) & set(Bf))} 本')
out.append('  根A にのみ(= .bash か shebang 拡張子無し): ' + (' / '.join(onlyA) or '0 本'))
out.append('  根B にのみ・docs/evidence/ の外(= 根A が落とした .sh/.py・理由を右に): ' + (' / '.join(f + ('(disk に無し)' if not os.path.isfile(M + '/' + f) else '(★理由不明★)') for f in onlyB_nonev) or '0 本'))
out.append(f'  根B にのみ・docs/evidence/ 配下 {len(onlyB) - len(onlyB_nonev)} 本= 先例の束の写し器(根A は宣で除く)。束名別: ' + ' / '.join(f'{k} {v}' for k, v in collections.Counter(f.split('/')[2] for f in onlyB if f.startswith('docs/evidence/')).most_common()))
c = collections.Counter((f.split('/')[0] if '/' in f else '(根)') for f in A)
out.append('根A 上位 dir 別: ' + ' / '.join(f'{k} {v}' for k, v in c.most_common()))
out.append('員外(根A に載せぬ・宣): docs/evidence/**(先例の束= 写しの器・己の束を含む= 器が己を測る疵の予防)は ★追跡でも除く★ / 追跡外= .bak* / queue/**(fixture・追跡分は載る) / .venv / .claude / backups / __pycache__ / repo 外(~/bin)')
SO = ['scripts/pane_enter_watcher_supervisor.sh', 'scripts/lib/detect_stale.sh', 'scripts/watchdogs/enter_restart_commander_watchdog.sh']
out.append('scope_out(札・專任2 km-83 の三 file)= 母數には入れて歩き ★毒当てのみ除く★: ' + ' / '.join(f'{f}({"根A 内" if f in set(A) else "★根A 外★"})' for f in SO))
for tool in ('bash', 'python3'):
    w = shutil.which(tool); v = subprocess.run(f'{w} --version 2>&1 | head -1', shell=True, capture_output=True, text=True).stdout.strip(); out.append(f'{tool}= {w} / {v}')
out.append('則: 生器(scripts/ lib/ shim/ ~/bin)へ 0 字 / 稼働 watcher 不觸 / tmux 実打ち 0(写し器は tmux を echo stub へ差し替へる)/ 直しは紙にのみ。')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); K.kaku(D + '/raw/00_rootA.txt', '\n'.join(A)); K.kaku(D + '/raw/00_rootB.txt', '\n'.join(Bf)); print('\n'.join(out))
