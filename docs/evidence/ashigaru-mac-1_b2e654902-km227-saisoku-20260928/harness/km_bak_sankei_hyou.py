# -*- coding: utf-8 -*-
# km-227 ㋐: .bak 三形(form1='.bak' / form2='.bak-' / form3='-bak-')の per-file 表を作る器。
# 旧器 km_tmux_census2.py(956c4669...)の除外条件は「'.bak' in p or p.endswith('~')」。
# 新器 km_tmux_census2_bakfix.py(c447a028...)の除外条件は三形+trailing~。
# 本器はxargsを一切使わず(os.walkの結果を直接Pythonのリストで保持する)、
# 引数長死(km-181系で踏んだ xargs -I{} の死因)を構造上回避する。
# 歩行対象の絞り込み(器候補)は旧器/新器と同一: EXTか実行bitを持つ通常file(symlink除く)。
import os, sys, stat, hashlib

SKIPDIR = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache",
           "worktrees", "backups", "test-results", "evidence"}
EXT = ('.sh', '.py', '.bats', '.zsh', '.bash')
FORM1 = '.bak'
FORM2 = '.bak-'
FORM3 = '-bak-'

root = sys.argv[1] if len(sys.argv) > 1 else '.'

n_walk_all = 0          # os.walk が返した全 candidate(器判定前)
n_isfile_noSlink = 0    # S_ISREG かつ symlink でない
n_ki_pre_bak = 0        # EXT or 実行bit を満たす(bak判定より前・trailing~ も未判定)
rows = []               # (path, form1, form2, form3, trailing_tilde)

for dp, dns, fns in os.walk(root):
    dns[:] = [d for d in dns if d not in SKIPDIR]
    for fn in fns:
        p = os.path.join(dp, fn)
        n_walk_all += 1
        if os.path.islink(p):
            continue
        try:
            st = os.lstat(p)
        except OSError:
            continue
        if not stat.S_ISREG(st.st_mode):
            continue
        n_isfile_noSlink += 1
        is_exec = bool(st.st_mode & stat.S_IXUSR)
        if not (p.endswith(EXT) or is_exec):
            continue
        n_ki_pre_bak += 1
        hit1 = FORM1 in p
        hit2 = FORM2 in p
        hit3 = FORM3 in p
        tilde = p.endswith('~')
        if hit1 or hit2 or hit3 or tilde:
            rows.append((p, hit1, hit2, hit3, tilde))

rows.sort(key=lambda r: r[0])

print("=== 母數(walk_root=%r) ===" % root)
print("歩き根 = %s" % root)
print("os.walk 全candidate(器判定前) = %d" % n_walk_all)
print("S_ISREG かつ symlink でない   = %d" % n_isfile_noSlink)
print("器候補(EXT or 実行bit, bak判定前) = %d" % n_ki_pre_bak)
print("いずれかの形(form1/2/3/~)に当たる file = %d 本" % len(rows))
print()

print("=== per-file 表(旧器/新器の除外の当否・changed=除外の当たりが変わつた) ===")
print("path\tform1(.bak)\tform2(.bak-)\tform3(-bak-)\ttilde(~)\told_excluded\tnew_excluded\tchanged")
n_old = n_new = n_changed = 0
for p, h1, h2, h3, t in rows:
    old_excluded = h1 or t
    new_excluded = h1 or h2 or h3 or t
    changed = (old_excluded != new_excluded)
    if old_excluded: n_old += 1
    if new_excluded: n_new += 1
    if changed: n_changed += 1
    print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (p, h1, h2, h3, t, old_excluded, new_excluded, changed))

print()
print("=== 排他性(和集合の中での重なり) ===")
s1 = set(p for p, h1, h2, h3, t in rows if h1)
s2 = set(p for p, h1, h2, h3, t in rows if h2)
s3 = set(p for p, h1, h2, h3, t in rows if h3)
uni = s1 | s2 | s3
print("form1 実本数=%d / form2 実本数=%d / form3 実本数=%d / 和集合=%d" % (len(s1), len(s2), len(s3), len(uni)))
print("form1∩form2=%d / form1∩form3=%d / form2∩form3=%d / 三形全交差=%d" % (
    len(s1 & s2), len(s1 & s3), len(s2 & s3), len(s1 & s2 & s3)))

print()
print("=== 集計(old/new excluded 件数・changed 件数) ===")
print("old_excluded=%d本 / new_excluded=%d本 / changed(除外の当たりが変わつた)=%d本" % (n_old, n_new, n_changed))
print("和集合との整合: len(rows)=%d (old/newいずれかで excluded の全候補と一致すべき)" % len(rows))

print()
print("=== changed 本の名指し(old→new で除外の当否が変わつた file のみ) ===")
for p, h1, h2, h3, t in rows:
    old_excluded = h1 or t
    new_excluded = h1 or h2 or h3 or t
    if old_excluded != new_excluded:
        print("  %s  form1=%s form2=%s form3=%s tilde=%s  old=%s new=%s" % (p, h1, h2, h3, t, old_excluded, new_excluded))
