#!/usr/bin/env python3
# order94: update-index --refresh が " M" を消さぬ因を對で剥がす（隔離のみ・network 0・本物不触）
import subprocess, pathlib, shutil, os, json

BASE = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/o94_lab").resolve()
if BASE.exists(): shutil.rmtree(BASE)
BASE.mkdir(parents=True)

ENV = dict(os.environ)
ENV.update({"GIT_AUTHOR_NAME":"a2","GIT_AUTHOR_EMAIL":"a2@lab",
            "GIT_COMMITTER_NAME":"a2","GIT_COMMITTER_EMAIL":"a2@lab",
            "GIT_CONFIG_NOSYSTEM":"1","GIT_TERMINAL_PROMPT":"0"})

def run(a, cwd, check=True):
    r = subprocess.run(a, cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit("FAILED %s rc=%d\n%s\n%s" % (a, r.returncode, r.stdout, r.stderr))
    return r

def w(p, data, mode=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f: f.write(data)
    if mode is not None: p.chmod(mode)

CRLF_BODY = b"#!/bin/bash\r\necho one\r\necho two\r\nexit 0\r\n"          # 41 byte
LF_BODY   = b"#!/bin/bash\necho one\necho two\nexit 0\n"                   # 37 byte

def dbg(cwd, name):
    """ls-files --debug の該当 file の stat 行を拾ふ"""
    out = run(["git","ls-files","--debug",name], cwd=cwd).stdout.splitlines()
    d = {}
    for ln in out:
        ln = ln.strip()
        for k in ("ctime:","mtime:","dev:","ino:","size:"):
            if ln.startswith(k):
                d[k.rstrip(":")] = ln[len(k):].strip()
    return d

def build(tag, autocrlf, attrs):
    wk = BASE/tag
    wk.mkdir()
    run(["git","init","--quiet","-b","main",str(wk)], cwd=BASE)
    run(["git","config","core.autocrlf",autocrlf], cwd=wk)
    if attrs is not None:
        w(wk/".gitattributes", attrs)
    w(wk/"crlf.sh", CRLF_BODY, 0o755)   # ケース①用
    w(wk/"touch.sh", LF_BODY, 0o755)    # ケース②用
    w(wk/"real.sh",  LF_BODY, 0o755)    # ケース③用
    run(["git","add","-A"], cwd=wk)
    run(["git","commit","--quiet","-m","seed"], cwd=wk)
    return wk

def probe(wk, name, mutate):
    """mutate を当てて refresh の前後を測る"""
    f = wk/name
    before_bytes = f.read_bytes()
    idx_before = dbg(wk, name)
    mutate(f)
    after_bytes = f.read_bytes()
    st_before = run(["git","status","--porcelain",name], cwd=wk).stdout.rstrip("\n")
    ref = run(["git","update-index","--refresh"], cwd=wk, check=False)
    st_after = run(["git","status","--porcelain",name], cwd=wk).stdout.rstrip("\n")
    idx_after = dbg(wk, name)
    hf  = run(["git","hash-object",name], cwd=wk).stdout.strip()
    hnf = run(["git","hash-object","--no-filters",name], cwd=wk).stdout.strip()
    lsf = run(["git","ls-files","-s",name], cwd=wk).stdout.split()
    return {
      "worktree_byte": [len(before_bytes), len(after_bytes)],
      "index_size":    [idx_before.get("size"), idx_after.get("size")],
      "index_ino":     [idx_before.get("ino"),  idx_after.get("ino")],
      "index_mtime":   [idx_before.get("mtime"),idx_after.get("mtime")],
      "status_before": st_before,
      "refresh_rc":    ref.returncode,
      "refresh_out":   (ref.stdout + ref.stderr).strip().splitlines(),
      "status_after":  st_after,
      "index_blob":    lsf[1] if len(lsf) > 1 else None,
      "hash_filtered": hf,
      "hash_nofilter": hnf,
    }

def m_sed(f):   subprocess.run(["sed","-i","s/\\r$//",str(f)], check=True)
def m_touch(f): os.utime(f, (0, 0))
def m_real(f):  w(f, f.read_bytes().replace(b"echo two", b"echo TWO"), 0o755)

REPOS = [("P","input","* text eol=lf\n"),
         ("Q","input",None),
         ("R","false",None)]
CASES = [("crlf.sh","(1)sed CRLF->LF", m_sed),
         ("touch.sh","(2)touch のみ",  m_touch),
         ("real.sh","(3)中身を現に変ふ", m_real)]

res = {}
for tag, ac, at in REPOS:
    wk = build(tag, ac, at.encode() if at else None)
    res[tag] = {"autocrlf": ac, "gitattributes": at}
    for name, label, fn in CASES:
        res[tag][label] = probe(wk, name, fn)

with open(BASE/"o94_result.json","w",encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

for tag,_,_ in REPOS:
    r = res[tag]
    print("="*72)
    print("repo %s  autocrlf=%s  gitattributes=%r" % (tag, r["autocrlf"], r["gitattributes"]))
    for _, label, _ in CASES:
        d = r[label]
        print("  %-18s status %-4r -> refresh(rc=%d) -> %-4r  | worktree byte %s  index size %s  ino %s"
              % (label, d["status_before"], d["refresh_rc"], d["status_after"],
                 d["worktree_byte"], d["index_size"], d["index_ino"]))
        if d["refresh_out"]:
            for ln in d["refresh_out"]: print("      refresh 出力: %s" % ln)
        print("      blob=%s  hash(filter)=%s  hash(no-filter)=%s"
              % (d["index_blob"][:12], d["hash_filtered"][:12], d["hash_nofilter"][:12]))
