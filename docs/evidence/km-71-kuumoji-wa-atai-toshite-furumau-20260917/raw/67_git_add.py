# -*- coding: utf-8 -*-
"""git add -f の記録 67(第71弾・main 樹・出目は _after/)。.gitignore 7 行目が裸の * ゆゑ -f が要る。己の束のみを staged にし(commit/push は家老)、枝・HEAD・staged 本数を書く。git reset / commit は打たぬ。
km-70 の 67 の疵(`l[:1] in 'AM'` が空文字で True → 一本多く数へた・km-70 _after/66)を直した形: `l and l[0] in 'AM'`。"""
import os, sys, subprocess, time
B = sys.argv[1]; D = os.path.dirname(B); AFT = D + '/_after'; M = '/Users/momizimac/multi-agent-shogun'; sys.path.insert(0, D + '/raw'); import kaki as K
rel = os.path.relpath(D, M); g = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True, cwd=M)
head = g('rev-parse', '--short', 'HEAD').stdout.strip(); br = g('branch', '--show-current').stdout.strip()
p = g('add', '-f', '--', rel); st = [l for l in g('status', '--porcelain', '--', rel).stdout.split('\n') if l]
staged = [l for l in st if l and l[0] in 'AM']; un = [l for l in st if l[:2] in ('??', ' M', 'AM')]; cached = [l for l in g('diff', '--cached', '--name-only', '--', rel).stdout.split('\n') if l]
out = [f'# 67 git add -f / 刻 {time.strftime("%Y-%m-%dT%H:%M:%S%z")} / 枝 {br} / HEAD {head} / 対象 {rel} / rc {p.returncode}' + (f' stderr {p.stderr.strip()[:200]}' if p.stderr.strip() else ''),
       f'## staged {len(staged)} 本(porcelain 一字目 A/M・空行は数へぬ)/ git diff --cached --name-only {len(cached)} 本 / 未 staged(此の器の後に生れる物) {len(un)} 本: {[l[3:] for l in un][:8]}', '## 本 67 の出目 file 自身は add の後に書かれる故 AM に残る(順の性質・km-70 _after/66 ④)。commit と push は家老の手'] + ['  ' + l for l in st]
K.kaku(AFT + '/67_git_add.txt', '\n'.join(out)); print('\n'.join(out[:3])); sys.exit(p.returncode)
