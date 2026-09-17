# -*- coding: utf-8 -*-
"""00 起(第75弾 km-77)―― 刻・枝・HEAD・的の樹(scripts .claude)の HEAD と disk の差を先に取る。読取のみ。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')
diff, rc = git('diff', '--name-only', 'HEAD', '--', 'scripts', '.claude'); unt, rc2 = git('ls-files', '--others', '--exclude-standard', '--', 'scripts', '.claude')
out = [f'# 00 起 / 刻 {koku} / 枝 {br} / HEAD {head[:12]} / 的の樹= scripts .claude(★凍結点= HEAD {head[:8]}・器は git grep {head[:8]} で引く★)']
out.append(f'HEAD と disk の差(git diff --name-only HEAD -- scripts .claude・rc {rc}): {len(diff.splitlines())} 本' + (('\n  ' + '\n  '.join(diff.splitlines())) if diff else '(差 0)'))
out.append(f'未追跡(git ls-files --others --exclude-standard・rc {rc2}): {len(unt.splitlines())} 本 ―― ★.gitignore 7 行目が裸の * ゆゑ未追跡は「無い」でなく「見えぬ」★')
out.append('生器へ 0 字(scripts/ .claude/ ~/bin/ は讀むのみ)/ 專任3 の束 km-52-shikii-no-bosuu-wo-kakutei-seyo-20260917 は ★納めまで讀まぬ(㋗)★ ―― 讀んだら紙に書く')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
