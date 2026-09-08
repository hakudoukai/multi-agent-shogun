#!/usr/bin/env python3
"""order78 甲: stale 経路を呼ぶ口の悉皆 + full-scan が消し得る母集合の proxy 測定 (v2)。
★底本は origin/main★ (CI が現に走る枝)。作業樹 (枝 wp-a1-a3-3-20260723) とは別物ゆゑ両方を測る。
讀取のみ。DB へ行かぬ (get_cached_paths 呼ばぬ)・v3 の main() 走らせぬ。1 = path 1 本。"""
import subprocess, fnmatch, importlib.util, time, sys
from pathlib import Path

REPO = Path("/mnt/c/DentalBI")
SCR = Path("scratch/ashigaru-third-2-fa06a3a1")
BOOKS = {
    "origin/main": SCR / "o78_v3_originmain.py",   # git show origin/main:scripts/sync_source_cache.py
    "作業樹HEAD":   REPO / "scripts" / "sync_source_cache.py",
}

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # main() は __main__ 保護で走らぬ
    return m

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=REPO)

# ---- 局所 ref を悉皆で合併 (proxy: 他の枝にのみ在る path) ----
refs = sorted({l.strip() for l in git("for-each-ref", "--format=%(objectname)",
                                      "refs/heads", "refs/remotes").stdout.splitlines() if l.strip()})
t0 = time.time()
union = set()
for sha in refs:
    for p in git("ls-tree", "-r", "--name-only", "-z", sha).stdout.split("\0"):
        if p:
            union.add(p)
print("§NET 局所 ref(heads+remotes)=%d  合併 path=%d  経過=%.1fs" % (len(refs), len(union), time.time() - t0))
print("§NET proxy の意味 = 局所 ref の合併 から 現樹の INCLUDE 集合 を引いた path。")
print("§NET ★DB の行では無い★ (DB 讀 0)。総監督殿の 1,483/1,442 とは元素が別ゆゑ足すな・比べるな。")

for label, path in BOOKS.items():
    v3 = load(path, "v3_" + label.replace("/", "_"))
    INC, EXCL_DIRS = v3.INCLUDE_PATTERNS, v3.EXCLUDE_DIRS
    ex = lambda p: any(part in EXCL_DIRS for part in p.split("/"))
    fn = lambda p: any(fnmatch.fnmatch(p, pat) for pat in INC)   # compute_stale_paths の目
    rx = v3.matches_include_patterns                              # collect_files / git 差分の目
    local = set(v3.collect_files(REPO))
    orphan = {p for p in union if p not in local}
    o_fn = {p for p in orphan if (not ex(p)) and fn(p)}
    o_rx = {p for p in orphan if (not ex(p)) and rx(p)}
    print("\n== 底本 %s (INCLUDE %d 本・行数 %d) ==" % (label, len(INC), path.read_bytes().count(b"\n")))
    print("  現樹 INCLUDE (collect_files) =", len(local))
    print("  proxy 孤児 全体 =", len(orphan))
    print("  ★full_scan が消す側 (fnmatch) =", len(o_fn), "★")
    print("  order76 の案文を当てた後 (regex) =", len(o_rx))
    print("  fnmatch のみ =", len(o_fn - o_rx), " regex のみ =", len(o_rx - o_fn))
