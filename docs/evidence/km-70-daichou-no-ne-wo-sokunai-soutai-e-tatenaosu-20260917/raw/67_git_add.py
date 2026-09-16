# -*- coding: utf-8 -*-
"""git add -f の記録 67(第70弾・main 樹・根の外 _after/)。.gitignore 7 行目が裸の * ゆゑ -f が要る。己の束のみを staged にし(commit/push は家老)、前後の HEAD・枝・staged 本数を書く。git reset / commit は打たぬ(共有樹)。"""
import os, sys, subprocess, time
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; M = '/Users/momizimac/multi-agent-shogun'; sys.path.insert(0, AFT); import kaki as K
rel = os.path.relpath(D, M); g = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd=M)
head = g('rev-parse', '--short', 'HEAD').stdout.strip(); br = g('branch', '--show-current').stdout.strip()
p = g('add', '-f', '--', rel); st = g('status', '--porcelain', '--', rel).stdout.split('\n')
staged = [l for l in st if l[:1] in 'AM']; un = [l for l in st if l[:2] in ('??', ' M', 'AM')]
out = [f'# 67 git add -f / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 {br} / HEAD {head} / 対象 {rel} / rc {p.returncode}' + (f' stderr {p.stderr.strip()[:200]}' if p.stderr.strip() else ''),
       f'## staged {len(staged)} 本 / 未 staged(此の器の後に生れる物) {len(un)} 本: {[l[3:] for l in un][:8]}', '## commit と push は家老の手(席は置くのみ・reset は打たぬ)'] + ['  ' + l for l in st if l]
K.kaku(AFT + '/67_git_add.txt', '\n'.join(out)); print('\n'.join(out[:3])); sys.exit(p.returncode)
