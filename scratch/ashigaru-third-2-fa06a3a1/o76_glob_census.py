#!/usr/bin/env python3
r"""order76 の規: v3 の入口(regex)と出口(fnmatch)の目の差を数へる (讀取のみ・DB 0・network 0)。

1 = path 1 本。母集合は 2 つ:
  M1 = git の追跡簿 ∧ 作業樹に実在        (入口 collect_files の実母集合)
  M2 = 局所 ref 226 本の合併 (json・当席の前の數へ) ―― ★出口の実母集合は DB 行であり讀めぬ★ ゆゑ代用
網 (何を 1 と数へたか):
  Ar = matches_include_patterns (regex・EXCLUDE 掛けぬ)
  A  = Ar ∧ ¬should_exclude ∧ ¬EXCLUDE_DIRS   = collect_files 実装の儘
  B  = any(fnmatch(p,pat) for pat in INCLUDE_PATTERNS) = compute_stale_paths 実装の儘 (EXCLUDE 掛けぬ)
  Bx = B ∧ ¬should_exclude ∧ ¬EXCLUDE_DIRS
差は 2 元素に分ける (四条③ ゆゑ足さぬ):
  ① glob の意味の差   = Ar△B  (EXCLUDE の条件を揃へた上での regex vs fnmatch)
  ② EXCLUDE を掛けぬ差 = B \ Bx
"""
import fnmatch
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/mnt/c/DentalBI")
V3 = REPO / "scripts" / "sync_source_cache.py"

spec = importlib.util.spec_from_file_location("v3", V3)
v3 = importlib.util.module_from_spec(spec)
sys.modules["v3"] = v3
spec.loader.exec_module(v3)

INC = list(v3.INCLUDE_PATTERNS)
EXD = set(v3.EXCLUDE_DIRS)


def in_excl_dirs(rel: str) -> bool:
    return any(part in EXD for part in Path(rel).parts)


def eye_Ar(p):
    return v3.matches_include_patterns(p)


def eye_B(p):
    return any(fnmatch.fnmatch(p, pat) for pat in INC)


def keep(p):
    return (not in_excl_dirs(p)) and (not v3.should_exclude(p))


def m1():
    proc = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                          capture_output=True, text=True, check=True)
    rels = [r for r in proc.stdout.split("\0") if r]
    return sorted(r for r in rels if (REPO / r).is_file())


def m0(commit):
    """order52 と同じ母集合 (其の折の commit の樹・実在 filter 掛けぬ) を再現する。"""
    proc = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", "-z", commit],
                          capture_output=True, text=True, check=True)
    return sorted(r for r in proc.stdout.split("\0") if r)


def m2(path):
    return sorted(set(json.load(open(path, encoding="utf-8"))))


def census(name, paths):
    Ar = {p for p in paths if eye_Ar(p)}
    B = {p for p in paths if eye_B(p)}
    A = {p for p in Ar if keep(p)}
    Bx = {p for p in B if keep(p)}
    only_Ar = Ar - B
    only_B = B - Ar
    print(f"== {name}: 母集合 {len(paths)} 本")
    print(f"   Ar(regex)={len(Ar)}  B(fnmatch)={len(B)}  A(実装 入口)={len(A)}  Bx={len(Bx)}")
    print(f"   ★元素① glob の意味の差★ regex のみ={len(only_Ar)} / fnmatch のみ={len(only_B)}"
          f" / 和(対称差)={len(only_Ar) + len(only_B)}")
    print(f"   ★元素② EXCLUDE を掛けぬ差★ B \\ Bx={len(B - Bx)}")
    print(f"   参考: 実装同士 A \\ B={len(A - B)} / B \\ A={len(B - A)} (①②の混合ゆゑ①②と足すな)")
    for label, s in (("regex のみ", only_Ar), ("fnmatch のみ", only_B)):
        if not s:
            continue
        top = Counter(p.split("/")[0] for p in s).most_common(6)
        print(f"   {label} 頭 dir: " + " ".join(f"{k}={v}" for k, v in top))
        pat = Counter()
        for p in s:
            for q in INC:
                if (eye_Ar(p) and fnmatch.fnmatch(p, q)) or (not eye_Ar(p) and fnmatch.fnmatch(p, q)):
                    pat[q] += 1
                    break
            else:
                for q in INC:
                    if v3._glob_pattern_to_regex(q).match(p):
                        pat[q] += 1
                        break
        print(f"   {label} pattern: " + " ".join(f"{k}={v}" for k, v in pat.most_common(6)))
        for p in sorted(s)[:3]:
            print(f"     例: {p}")
    return {"Ar": len(Ar), "B": len(B), "A": len(A), "onlyAr": len(only_Ar), "onlyB": len(only_B)}


if __name__ == "__main__":
    p1 = m1()
    census("M1 追跡簿∧実在 (現 HEAD)", p1)
    try:
        census("M0 dbf05a029 の樹 (order52 と同じ母集合・実在 filter 無し)", m0("dbf05a029"))
    except subprocess.CalledProcessError as exc:
        print(f"-- M0 讀めぬ: rc={exc.returncode}")
    j = Path(__file__).resolve().parent / "o70_union_local.json"
    if j.exists():
        census("M2 局所 ref 合併(代用・当席の前の數へ)", m2(j))
    else:
        print(f"-- M2 の json が無い: {j}")
