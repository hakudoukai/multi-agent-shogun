# -*- coding: utf-8 -*-
"""走り器(第79弾 km-86・二走・km-84 の lib_run の写し+拡張・30 と 40 が共に使ふ)―― 束内の写し器を、名 N に値 value を env で渡して一度走らせ、
rc / 枝(stdout の BRANCH=…)/ ★向先★(stdout の TARGET=<hex> / TMUX_ARG=<hex> を byte 通りに復元)/ 器の報せ行 / 外の声行を返す。
★tmux は一度も打たぬ★: PATH の先頭に束内 stub dir(tmux/timeout/gtimeout= 引数を hex で刷るだけ)を置き、写し器の中でも同名の関数を定義する(二重の柵)。
二欄は別: 外の声= `: line N:`・syntax error・Traceback・Error・expected・unbound・invalid・No such・not found に当たる stderr 行、器の報せ= 其の他の非空 stderr 行。"""
import os, re, subprocess
SOTO = re.compile(r': line \d+:|syntax error|Traceback|Error|expected|unbound|invalid|No such|not found|command not found')
def mark(v):
    if v is None: return '(未設定)'
    if v == '': return '(空文字)'
    if v == ' ': return '␠'
    if v == '\u3000': return '(全角空白)'
    if len(v) > 40: return f'({len(v)}字:{v[:6]}…)'
    return v.replace('\n', '␊').replace('\t', '␉').replace('\u3000', '(全角空白)')
TMUX_FN = 'tmux(){ for __a in "$@"; do printf \'TMUX_ARG=\'; printf \'%s\' "$__a" | od -An -v -tx1 | tr -d \' \\n\'; printf \'\\n\'; done; printf \'TMUX_NARGS=%s\\n\' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }'
def stub_dir(D):
    S = D + '/raw/stub'; os.makedirs(S, exist_ok=True)
    for n in ('tmux', 'timeout', 'gtimeout'):
        p = S + '/' + n
        if not os.path.exists(p):
            body = ('#!/bin/bash\n# stub(第79弾 km-86)―― 実 tmux を打たぬ。引数を hex で刷るのみ。\n' + TMUX_FN + '\ntmux "$@"\n') if n == 'tmux' else '#!/bin/sh\n# stub timeout ―― 先頭の秒を捨てて残りを走らせる\nshift; exec "$@"\n'
            open(p, 'w', encoding='utf-8').write(body); os.chmod(p, 0o755)
    return S
def unhex(h):
    try: return bytes.fromhex(h).decode('utf-8', 'replace')
    except ValueError: return '?hex?'
def run(harness, kind, N, value, cwd, preset=()):
    env = dict(os.environ); env.pop(N, None)
    for k, v in preset: env[k] = v
    if value is not None: env[N] = value
    env['PATH'] = stub_dir(cwd) + ':' + env.get('PATH', '')
    argv = ['/bin/bash', harness] if kind == 'sh' else ['python3', '-B', harness]
    try: p = subprocess.run(argv, capture_output=True, env=env, cwd=cwd, timeout=20); rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e: rc, so, se = 124, e.stdout or b'', (e.stderr or b'') + b'\n[lib_run] timeout 20s'
    so = so.decode('utf-8', 'replace'); se = se.decode('utf-8', 'replace')
    m = re.search(r'^BRANCH=(\S+)', so, re.M); br = m.group(1) if m else '無'
    tg = [unhex(h) for h in re.findall(r'^TARGET=([0-9a-f]*)$', so, re.M)]; ta = [unhex(h) for h in re.findall(r'^TMUX_ARG=([0-9a-f]*)$', so, re.M)]; na = re.findall(r'^TMUX_NARGS=(\d+)', so, re.M)
    err = [l for l in se.split('\n') if l.strip()]
    soto = [l for l in err if SOTO.search(l)]; utsuwa = [l for l in err if not SOTO.search(l)]
    head = (err[0] if err else '').replace(cwd + '/', '').replace('\n', '␊')[:110]
    return {'rc': rc, 'branch': br, 'targets': tg, 'tmux': ta, 'nargs': na, 'utsuwa': len(utsuwa), 'soto': len(soto), 'head': head}
