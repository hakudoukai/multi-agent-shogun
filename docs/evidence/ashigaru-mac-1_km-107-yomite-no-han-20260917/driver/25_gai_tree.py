#!/usr/bin/env python3 -B
# -*- coding: utf-8 -*-
"""25_gai_tree.py ―― ★git の樹の母數★(km-107 ㋐) と其の害行(㋑)。disk とは別欄。
樹の宣(逐語): (i) HEAD の樹 = `git ls-tree -r -z HEAD` の blob ∧ basename が大小文字を區別せず 'manifest' を含む。
             (ii) 全 ref の和 = `git for-each-ref` の各 ref に (i) と同じ濾しを當て、★重複無き blob★ で數へる(同じ blob は一度)。
             (iii) 讀み手 scripts/checks/karo_mac_manifest_verify.py の版を ref 每に取る(家老の 68/69 の再測)。
blob の中身は `git cat-file --batch` で取り、disk の紙は一切讀まぬ。分類器は gai.file_wake(disk と同一)。"""
import os, sys, subprocess, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gai, K
REPO = "/Users/momizimac/multi-agent-shogun"
BUN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(BUN)
def git(*a, inp=None):
    return subprocess.run(["git", "-C", REPO, *a], input=inp, capture_output=True)
t0 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

def lstree(ref):
    r = git("ls-tree", "-r", "-z", ref)
    out = []
    for ent in r.stdout.split(b"\0"):
        if not ent:
            continue
        meta, path = ent.split(b"\t", 1)
        mode, typ, blob = meta.decode().split()
        if typ != "blob":
            continue
        p = path.decode("utf-8", "surrogateescape")
        if "manifest" in os.path.basename(p).lower():
            out.append((blob, p))
    return r.returncode, out

def blobs_read(blobs):
    r = git("cat-file", "--batch", inp=("\n".join(blobs) + "\n").encode())
    data, i, res = r.stdout, 0, {}
    while i < len(data):
        j = data.index(b"\n", i)
        head = data[i:j].decode().split()
        if len(head) == 3:
            sha, typ, n = head[0], head[1], int(head[2])
            res[sha] = data[j + 1:j + 1 + n]
            i = j + 1 + n + 1
        else:
            i = j + 1
    return r.returncode, res

def shuukei(name, ents, blobmap, refs_of=None):
    """ents=[(blob,path)] 重複無き blob で數へる"""
    seen, rows, kizu = set(), [], []
    tot = {k: 0 for k in ("行總", "註", "讀めぬ", "path行", "甲", "乙", "丙", "平", "丁")}
    nB = nC = fk = fo = 0
    for blob, p in ents:
        if blob in seen:
            continue
        seen.add(blob)
        b = blobmap[blob]
        c, kz = gai.file_wake(b)
        isB = p.lower().endswith(".txt"); isC = c["path行"] >= 1
        nB += isB; nC += isC; fk += c["甲"] > 0; fo += c["乙"] > 0
        for k in tot:
            tot[k] += c[k]
        nref = len(refs_of[blob]) if refs_of else 1
        rows.append("\t".join(str(x) for x in (blob, repr(p), nref, int(isB), int(isC), len(b), c["行總"], c["註"], c["讀めぬ"], c["path行"], c["甲"], c["乙"], c["丙"], c["平"], c["丁"])))
        for no, sh, seg, line in kz:
            kizu.append("\t".join((blob, repr(p), str(no), sh, repr(seg), repr(line))))
    K.kaku("raw/%s_files.tsv" % name, "blob\tpath(repr)\tref數\tB\tC\tbytes\t行總\t註\t讀めぬ\tpath行\t甲\t乙\t丙\t平\t丁\n" + "\n".join(rows) + "\n")
    K.kaku("raw/%s_kizu_rows.tsv" % name, "blob\tpath(repr)\t行番\t種\tseg(repr)\t行(repr)\n" + "\n".join(kizu) + "\n")
    return len(seen), nB, nC, tot, fk, fo

# (i) HEAD
head_sha = git("rev-parse", "HEAD").stdout.decode().strip()
head_ref = git("rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
rc_h, ents_h = lstree("HEAD")
rc_hb, bm_h = blobs_read(sorted({b for b, _ in ents_h}))
nH, nHB, nHC, totH, fkH, foH = shuukei("25_tree_head", ents_h, bm_h)

# (ii) all refs
r = git("for-each-ref", "--format=%(refname) %(objectname)")
refs = [l.split() for l in r.stdout.decode().splitlines() if l.strip()]
ents_all, refs_of, rc_bad = [], collections.defaultdict(set), []
per_ref = []
for name, obj in refs:
    rc, ents = lstree(name)
    if rc != 0:
        rc_bad.append((name, rc))
    per_ref.append("%s\t%s\t%d\t%d" % (name, obj, rc, len(ents)))
    for b, p in ents:
        refs_of[b].add(name); ents_all.append((b, p))
K.kaku("raw/27_refs_walk.tsv", "ref\tcommit\tls-tree_rc\t定義A_ent數\n" + "\n".join(per_ref) + "\n")
rc_ab, bm_all = blobs_read(sorted(refs_of))
nA, nAB, nAC, totA, fkA, foA = shuukei("28_refs_union", ents_all, bm_all, refs_of)

# (iii) verify.py version per ref
VP = "scripts/checks/karo_mac_manifest_verify.py"
ver, vrows = collections.Counter(), []
for name, obj in refs:
    q = git("rev-parse", "-q", "--verify", "%s:%s" % (name, VP))
    b = q.stdout.decode().strip() if q.returncode == 0 else "ABSENT"
    ver[b] += 1; vrows.append("%s\t%s\t%s" % (name, obj, b))
K.kaku("raw/29_refs_verify_ver.tsv", "ref\tcommit\tverify.py_blob\n" + "\n".join(vrows) + "\n")
disk_ver = git("hash-object", VP).stdout.decode().strip()

t1 = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
def tl(tag, n, nB, nC, tot, fk, fo):
    return ["## %s" % tag, "重複無き blob=%d  B(.txt)=%d  C(path行>=1)=%d" % (n, nB, nC),
            "行總=%d 註=%d 讀めぬ=%d path行=%d" % (tot["行總"], tot["註"], tot["讀めぬ"], tot["path行"]),
            "★甲 行=%d★ blob=%d / ★乙 行=%d★ blob=%d / 丙=%d 平=%d 丁=%d" % (tot["甲"], fk, tot["乙"], fo, tot["丙"], tot["平"], tot["丁"])]
out = ["# 26_tree_totals ―― git の樹の母數(km-107 ㋐㋑)・disk とは別欄", "刻(始)=%s 刻(終)=%s" % (t0, t1),
       "HEAD=%s (%s) ls-tree_rc=%d cat-file_rc=%d 定義A ent=%d" % (head_sha, head_ref, rc_h, rc_hb, len(ents_h))] + \
      tl("(i) HEAD の樹", nH, nHB, nHC, totH, fkH, foH) + \
      ["", "ref 總=%d ls-tree rc≠0 の ref=%d %s cat-file_rc=%d 定義A ent(延べ)=%d" % (len(refs), len(rc_bad), rc_bad, rc_ab, len(ents_all))] + \
      tl("(ii) 全 ref の和(重複無き blob)", nA, nAB, nAC, totA, fkA, foA) + \
      ["", "## (iii) 讀み手 %s の版 (ref 數)" % VP, "disk(作業樹)の blob=%s" % disk_ver] + \
      ["%s\t%d" % (k, v) for k, v in ver.most_common()]
K.kaku("raw/26_tree_totals.txt", "\n".join(out) + "\n")
print(open("raw/26_tree_totals.txt", encoding="utf-8").read())
