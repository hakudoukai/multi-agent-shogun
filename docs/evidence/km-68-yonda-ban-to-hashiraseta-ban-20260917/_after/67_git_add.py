# -*- coding: utf-8 -*-
"""git add -f の記録 67(第68弾・根の外 _after/)。.gitignore 7 行目が裸の * ゆゑ -f が要る。己の束のみを staged にし(commit/push は家老)、前後の HEAD・staged 本数・未 staged(此の後に生れる 64/67 の出目)を書く。"""
import os, sys, subprocess, time
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; W = '/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1'; sys.path.insert(0, AFT); import kaki as K
rel = os.path.relpath(D, W); head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, cwd=W).stdout.strip()
p = subprocess.run(['git', 'add', '-f', '--', rel], capture_output=True, text=True, cwd=W)
st = subprocess.run(['git', 'status', '--porcelain', '--', rel], capture_output=True, text=True, cwd=W).stdout.split('\n')
staged = [l for l in st if l[:1] in 'AM']; un = [l for l in st if l[:2] in ('??', ' M', 'AM')]
out = [f'# 67 git add -f / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 karo-mac/a1-r56 / HEAD {head} / 対象 {rel} / rc {p.returncode}' + (f' stderr {p.stderr.strip()[:200]}' if p.stderr.strip() else ''),
       f'## staged {len(staged)} 本 / 未 staged(此の器の後に生れる物・64/67 の出目) {len(un)} 本: {[l[3:] for l in un][:8]}', '## commit と push は家老の手(席は置くのみ)'] + ['  ' + l for l in st if l]
K.kaku(AFT + '/67_git_add.txt', '\n'.join(out)); print('\n'.join(out[:3])); sys.exit(p.returncode)
