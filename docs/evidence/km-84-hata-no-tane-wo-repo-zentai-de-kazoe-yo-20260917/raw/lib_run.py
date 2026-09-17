# -*- coding: utf-8 -*-
"""走り器(第78弾 km-84・30 と 40 が共に使ふ)―― 束内の写し器(harness)を、旗 N に値 value(None= 未設定)を env で渡して一度走らせ、
rc / BRANCH(stdout の BRANCH=… ・無ければ 無)/ 器の報せ行 / 外の声行(interpreter の悲鳴)/ stderr の頭 を返す。★二欄は別★: 外の声= `: line N:`・syntax error・Traceback・Error・expected・unbound に当たる行、器の報せ= 其の他の非空行。"""
import os, re, subprocess
SOTO = re.compile(r': line \d+:|syntax error|Traceback|Error|expected|unbound|invalid')
MARK = {'': '(空文字)', ' ': '␠', '\n1': '␊1', None: '(未設定)'}
def mark(v): return MARK.get(v, v if v is None or '\n' not in v else v.replace('\n', '␊'))
def run(harness, kind, N, value, cwd, preset=()):
    env = dict(os.environ); env.pop(N, None)
    for k, v in preset: env[k] = v
    if value is not None: env[N] = value
    argv = ['/bin/bash', harness] if kind == 'sh' else ['python3', '-B', harness]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=cwd)
    so = p.stdout.decode('utf-8', 'replace'); m = re.search(r'BRANCH=(\S+)', so); br = m.group(1) if m else '無'
    err = [l for l in p.stderr.decode('utf-8', 'replace').split('\n') if l.strip()]
    soto = [l for l in err if SOTO.search(l)]; utsuwa = [l for l in err if not SOTO.search(l)]
    head = (err[0] if err else '').replace(cwd + '/', '').replace('\n', '␊')[:110]
    return {'rc': p.returncode, 'branch': br, 'utsuwa': len(utsuwa), 'soto': len(soto), 'head': head}
