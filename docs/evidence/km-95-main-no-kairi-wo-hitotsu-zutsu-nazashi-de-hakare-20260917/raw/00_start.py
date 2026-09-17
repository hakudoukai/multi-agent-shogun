# -*- coding: utf-8 -*-
"""00 起(第82弾 km-95)―― 刻・作業樹の枝・HEAD・local main・refs/remotes/origin/main・★ls-remote(純粋な読取)の origin main★・札の sha16/行/bytes・家老の紙(karo-mac-origin-eda-kenbun-20260917/README.md)の sha256 と札の宣 585eea9f775e549d の照合・git/python3 の版。
★git は読取の口のみ★(rev-parse / ls-remote / for-each-ref)。fetch/pull/merge/rebase/reset/cherry-pick/update-ref/branch -f は一つも走らせぬ(札の禁)。"""
import os, sys, time, hashlib, subprocess
D = sys.argv[1]; sys.path.insert(0, D + '/raw'); import kaki as K; M = '/Users/momizimac/multi-agent-shogun'
FUDA = 'queue/tasks/ashigaru-mac-1.yaml'; KAMI = 'docs/evidence/karo-mac-origin-eda-kenbun-20260917/README.md'
def git(*a): p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M); return p.stdout.strip(), p.returncode
koku = time.strftime('%Y-%m-%dT%H:%M:%S%z'); head, _ = git('rev-parse', 'HEAD'); br, _ = git('branch', '--show-current')
L, _ = git('rev-parse', 'refs/heads/main'); OR, _ = git('rev-parse', 'refs/remotes/origin/main')
lsr, rc_ls = git('ls-remote', 'origin', 'refs/heads/main'); LS = lsr.split('\t')[0] if lsr else '(空)'
fb = open(M + '/' + FUDA, 'rb').read(); kb = open(M + '/' + KAMI, 'rb').read(); ksha = hashlib.sha256(kb).hexdigest()
out = [f'# 00 起 / 刻 {koku} / 作業樹の枝 {br}(共有・不觸) / HEAD {head[:12]} / 札 {FUDA} sha16 {hashlib.sha256(fb).hexdigest()[:16]} {fb.count(b"\n")}行 {len(fb)}B']
out.append(f'local main(refs/heads/main)= {L}')
out.append(f'refs/remotes/origin/main(手元の写し・古び得る)= {OR}')
out.append(f'★ls-remote origin refs/heads/main(今の値・読取 rc {rc_ls})= {LS}★ → 手元の写しと {"一致" if LS == OR else "★食ひ違ふ★(食ひ違ひ其の物を紙に書く)"}')
out.append(f'札の宣 local {"一致" if L == "363d5fb060845171338c067ef42bfcbef8ad9188" else "★不一致★"} / origin {"一致" if LS == "4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1" else "★不一致★"}')
out.append(f'家老の紙 {KAMI} = {len(kb)}B sha256 {ksha} → 札の宣(2620B / 585eea9f775e549d…)と {"一致" if len(kb) == 2620 and ksha.startswith("585eea9f775e549d") else "★不一致★"}')
for name, cmd in [('git', 'git --version'), ('python3', 'python3 --version; command -v python3'), ('uname', 'uname -sr')]:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True); out.append(f'{name}= ' + ' | '.join(x for x in (p.stdout + p.stderr).strip().split('\n') if x) + f' (rc {p.returncode})')
out.append('則: git は読取の口のみ(rev-parse/ls-remote/for-each-ref/merge-base/rev-list/log/cherry/diff-tree/patch-id/cat-file/reflog show)。fetch・pull・merge・rebase・reset・cherry-pick・push・update-ref・branch -f・remote set-url・commit は ★一つも走らせぬ★(札の禁「refs を書き換へる命令を一つも」を字義で読む ∴ 束の commit も己では打たぬ)。生器へ 0 字・watcher 不觸・/tmp 不使用・行番を焼かぬ。')
K.kaku(D + '/raw/00_start.txt', '\n'.join(out)); print('\n'.join(out))
