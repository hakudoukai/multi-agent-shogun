# -*- coding: utf-8 -*-
"""10 ―― origin/main 全pathの case-fold census。
⒜ 母數(本数・argv・rc)を先に宣し、全pathを case-fold(小文字化)して衝突の組を★全部★列挙する。
⒝ 各組について blob sha256(64桁)/bytes/同異/disk 現存者。
"""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

TAG = sys.argv[1] if len(sys.argv) > 1 else "10_casefold_census"

def run(argv, cwd=ROOT):
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

# ⒜ 母數
argv_a = ["git", "ls-tree", "-r", "--name-only", "origin/main"]
rc_a, out_a, err_a = run(argv_a)
assert rc_a == 0, u"ls-tree rc=%d err=%r" % (rc_a, err_a)
paths = out_a.decode("utf-8", "surrogateescape").split("\n")
paths = [p for p in paths if p != ""]
bogen = len(paths)

groups = {}
for p in paths:
    key = p.lower()
    groups.setdefault(key, []).append(p)

collisions = {k: v for k, v in groups.items() if len(v) > 1}

# ⒝ 各組について blob sha256/bytes/同異/disk 現存者
def blob_content(path):
    argv = ["git", "cat-file", "-p", "origin/main:%s" % path]
    rc, out, err = run(argv)
    return rc, out, err

def on_disk_sha256(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None, None
    try:
        data = io.open(full, "rb").read()
        return hashlib.sha256(data).hexdigest(), len(data)
    except OSError:
        return None, None

rows = []
for key in sorted(collisions.keys()):
    members = collisions[key]
    member_info = []
    for m in members:
        rc_c, out_c, err_c = blob_content(m)
        assert rc_c == 0, u"cat-file rc=%d path=%s err=%r" % (rc_c, m, err_c)
        sha = hashlib.sha256(out_c).hexdigest()
        nbytes = len(out_c)
        member_info.append((m, sha, nbytes))
    same = len(set(sha for _, sha, _ in member_info)) == 1
    # disk 現存者(このworktree = ROOT の実体)
    disk_hits = []
    for m in members:
        dsha, dbytes = on_disk_sha256(m)
        disk_hits.append((m, dsha, dbytes))
    rows.append((key, member_info, same, disk_hits))

lines = []
lines.append(u"★10 ―― origin/main case-fold census★")
lines.append(u"")
lines.append(u"■⒜ 母數")
lines.append(u"  cwd=%s" % ROOT)
lines.append(u"  argv=%s" % " ".join(argv_a))
lines.append(u"  rc=%d" % rc_a)
lines.append(u"  母數(本数)=%d" % bogen)
lines.append(u"")
lines.append(u"■衝突の組(case-fold key が同じ path が2本以上)")
lines.append(u"  組数=%d" % len(rows))
if not rows:
    lines.append(u"  (無し)")
for key, member_info, same, disk_hits in rows:
    lines.append(u"  ―― key=%s" % key)
    for m, sha, nbytes in member_info:
        lines.append(u"     path=%s sha256=%s bytes=%d" % (m, sha, nbytes))
    lines.append(u"     同異=%s" % (u"同じ" if same else u"★違ふ★"))
    for m, dsha, dbytes in disk_hits:
        if dsha is None:
            lines.append(u"     disk[%s]=★不在(ENOENT)★" % m)
        else:
            hit = u"★現存(blobと一致)★" if any(dsha == s for _, s, _ in member_info) else u"現存(blobと不一致?)"
            match_member = [mm for mm, s, _ in member_info if s == dsha]
            lines.append(u"     disk[%s] sha256=%s bytes=%d ―― %s%s" %
                          (m, dsha, dbytes, hit,
                           (u" (=%s)" % match_member[0]) if match_member else u""))

lines.append(u"")
lines.append(u"★此の数が意味せぬ事★:")
lines.append(u"  ・「disk 現存」は★本worktree(a2-km218)の checkout 直後の状態★であり、")
lines.append(u"    他worktree/他席では case-insensitive FS の勝者が異なり得る(チェックアウト順序に依存)。")
lines.append(u"  ・母數は origin/main の此の刻(fetch後)の tree であり、次の push で動き得る。")

K.kaku(os.path.join(BUNDLE, "raw", "%s.txt" % TAG), u"\n".join(lines) + u"\n")

print(u"bogen=%d argv_rc=%d collisions=%d" % (bogen, rc_a, len(rows)))
for key, member_info, same, disk_hits in rows:
    print(u"  %s same=%s members=%s" % (key, same, [m for m, _, _ in member_info]))
