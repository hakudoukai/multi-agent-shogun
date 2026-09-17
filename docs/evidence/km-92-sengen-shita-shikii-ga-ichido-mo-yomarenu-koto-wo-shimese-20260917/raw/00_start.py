# -*- coding: utf-8 -*-
"""00 起(第81弾 km-92)―― 刻・枝・HEAD・main・札の sha16/行/bytes、★的 scripts/lib/detect_stale.sh を其の場で己の手で固定★(sha256 全字・sha16・bytes・行・git の最終 commit)し、写し raw/00_target_detect_stale.sh を置いて写しの sha が生と一致する事を刷る(版は席が走る間に動く)。此の PC の bash/python3/date/gdate/flock/git の版。読取のみ・生器へ 0 字。"""
import os, sys, time, hashlib, subprocess, shutil
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
FUDA = 'queue/tasks/ashigaru-mac-1.yaml'; TGT = 'scripts/lib/detect_stale.sh'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
def sh(cmd): p = subprocess.run(cmd, shell=True, capture_output=True, text=True); return (p.stdout + p.stderr).strip().split('\n')[0], p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current'); mainsha, _ = git('rev-parse', 'main')
fb = open(M + '/' + FUDA, 'rb').read(); tb = open(M + '/' + TGT, 'rb').read()
full = hashlib.sha256(tb).hexdigest()
out = [f'# 00 起 / 刻 {koku} / 枝 {br} / HEAD {head[:12]} / main {mainsha[:12]} / 札 {FUDA} sha16 {hashlib.sha256(fb).hexdigest()[:16]} {fb.count(b"\n")}行 {len(fb)}B']
out.append(f'★的 {TGT} ―― 固定(己の手・此の刻)★: sha256 {full} / sha16 {full[:16]} / {len(tb)} bytes / {tb.count(b"\n")} 行(LF の數) / 札の宣 sha16 de4fefbdadb2be63 292行 → {"一致" if full[:16] == "de4fefbdadb2be63" and tb.count(b"\n") == 292 else "★不一致★"}')
lg, rc = git('log', '-1', '--format=%h %ci %s', '--', TGT); out.append(f'git log -1 -- {TGT} (rc {rc}): {lg[:120]}')
st, rc = git('status', '--porcelain', '--', TGT); out.append(f'git status --porcelain -- {TGT} (rc {rc}): [{st}] ← 空= 生は追跡版と同じ')
shutil.copyfile(M + '/' + TGT, D + '/raw/00_target_detect_stale.sh'); cb = open(D + '/raw/00_target_detect_stale.sh', 'rb').read()
out.append(f'写し raw/00_target_detect_stale.sh sha16 {hashlib.sha256(cb).hexdigest()[:16]} {len(cb)}B → 生と {"一致" if cb == tb else "★不一致★"}')
for name, cmd in [('bash', '/bin/bash --version'), ('python3', 'python3 --version; command -v python3'), ('date', 'command -v date; /bin/date -Iseconds'), ('gdate', 'command -v gdate; gdate --version'), ('flock', 'command -v flock || echo "flock: 無し(command -v rc 1)"'), ('git', 'git --version'), ('uname', 'uname -sr')]:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True); out.append(f'{name}= ' + ' | '.join(x for x in (p.stdout + p.stderr).strip().split('\n') if x) + f' (rc {p.returncode})')
out.append('則: 生器(scripts/ lib/ ~/bin)へ 0 字 / 稼働 watcher・supervisor 不觸 / settings.json 不觸 / 測りは写し(raw/00_target_detect_stale.sh と其の直し raw/40_*)で / 直しは自枝へ commit(temp index・porcelain 不変・push 請はず)。的は detect_stale.sh 一本(他三本へ手を伸ばさぬ)。')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
