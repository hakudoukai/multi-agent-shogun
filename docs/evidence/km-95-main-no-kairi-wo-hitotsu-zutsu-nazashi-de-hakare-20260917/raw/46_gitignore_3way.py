# -*- coding: utf-8 -*-
"""46 重なり path の 3-way(第82弾 km-95)―― 45① で「衝突し得る」と書いた .gitignore を、★git merge を走らせずに★ file 単位の 3-way(git merge-file・repo の ref にも index にも worktree にも触れぬ・入力は束内の写し三本)で測る。rc = 衝突 hunk の数(0 なら衝突無し・負なら器の誤り)。"""
import os, sys, time, subprocess, hashlib
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; from gitro import git
L = '363d5fb060845171338c067ef42bfcbef8ad9188'; O = '4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1'; MB = '6e9d40600a801aa713ac238e2e62bbae06c9e683'
W = D + '/raw/46_gitignore'; os.makedirs(W, exist_ok=True); out = [f'# 46 .gitignore の 3-way(merge-file・ref 不觸) / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")}']
for name, rev in (('base', MB), ('local', L), ('origin', O)):
    o, e, rc = git('cat-file', '-p', f'{rev}:.gitignore'); open(W + f'/{name}.gitignore', 'w', encoding='utf-8', newline='\n').write(o)
    out.append(f'{name} {rev[:12]}:.gitignore → {len(o.encode())}B {o.count(chr(10))}行 sha16 {hashlib.sha256(o.encode()).hexdigest()[:16]} (cat-file rc {rc})')
p = subprocess.run(['git', 'merge-file', '-p', '-L', 'local', '-L', 'base', '-L', 'origin', W + '/local.gitignore', W + '/base.gitignore', W + '/origin.gitignore'], capture_output=True, text=True)
open(W + '/merged.gitignore', 'w', encoding='utf-8', newline='\n').write(p.stdout)
out.append(f'git merge-file -p local base origin → rc ★{p.returncode}★(= 衝突 hunk の数・0 は衝突無し) / 出目 {len(p.stdout.encode())}B {p.stdout.count(chr(10))}行 / 衝突印 <<<<<<< の行 {sum(1 for l in p.stdout.split(chr(10)) if l.startswith("<<<<<<<"))}')
dl = subprocess.run(['diff', W + '/base.gitignore', W + '/local.gitignore'], capture_output=True, text=True).stdout; do = subprocess.run(['diff', W + '/base.gitignore', W + '/origin.gitignore'], capture_output=True, text=True).stdout
out.append('base→local の差(diff 逐語):'); out += ['  ' + x for x in dl.split('\n') if x]; out.append('base→origin の差(diff 逐語):'); out += ['  ' + x for x in do.split('\n') if x]
out.append('此の測りが意味せぬ事: file 単位の 3-way であり、rename/mode/他 path との連関は見ぬ。scripts/checks/karo_mac_manifest_verify.py は両 tip で同 blob(45①)ゆゑ 3-way 不要。')
K.kaku(D + '/raw/46_gitignore_3way.txt', '\n'.join(out)); print('\n'.join(out))
