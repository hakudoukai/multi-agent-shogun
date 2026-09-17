# -*- coding: utf-8 -*-
"""読取専用の git 口(第82弾 km-95)―― 許す subcommand を白表で縛る。fetch/pull/merge/rebase/reset/cherry-pick/push/update-ref/branch(-f)/remote/commit は此処からは打てぬ(assert)。"""
import subprocess
M = '/Users/momizimac/multi-agent-shogun'
SHIRO = {'rev-parse', 'ls-remote', 'for-each-ref', 'merge-base', 'rev-list', 'log', 'cherry', 'diff-tree', 'patch-id', 'cat-file', 'show-ref', 'ls-tree', 'diff', 'reflog', 'name-rev', 'branch'}
def git(*a, inp=None):
    assert a[0] in SHIRO, f'白表外の git 口: {a[0]}'
    if a[0] == 'branch': assert all(x in ('--contains', '-a', '--format=%(refname)', '--list') or x.startswith('--') is False for x in a[1:]) and '-f' not in a and '-D' not in a and '-d' not in a and '-m' not in a, '書く branch 口は禁'
    if a[0] == 'reflog': assert a[1] in ('show',), 'reflog は show のみ'
    p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=M, input=inp)
    return p.stdout, p.stderr, p.returncode
def patch_id(sha, stable=True):
    d, _, rc = git('diff-tree', '-p', '--no-color', '--root', sha)
    if rc != 0: return None
    o, _, rc2 = git('patch-id', *(['--stable'] if stable else ['--unstable']), inp=d)
    if rc2 != 0 or not o.strip(): return ''   # 空 diff
    return o.split()[0]
def meta(sha):
    o, _, _ = git('log', '-1', '--format=%H%x1f%P%x1f%an%x1f%ae%x1f%aI%x1f%cn%x1f%ce%x1f%cI%x1f%s', sha)
    f = o.strip('\n').split('\x1f'); return dict(sha=f[0], parents=f[1].split(), an=f[2], ae=f[3], ad=f[4], cn=f[5], ce=f[6], cd=f[7], subj=f[8])
