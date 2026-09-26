#!/usr/bin/env python3
# km-197 第二測の器: 帳(yaml)を argv で受け、done の塊を母数に 18 欄を 有/空/無 で数へ、
# tip/tree/oya を 40桁 regex と git cat-file -e(peel 無し)で判ずる。帳は読むだけ。
# 使ふ: 30_census_v2.py <帳.yaml> <git_dir> <out_prefix> [hira]
import sys, re, subprocess, collections, yaml
chou, gitdir, out = sys.argv[1:4]
RAN = ["task_id","status","completed_at","branch","tip","tree","oya","worktree","pushed","kotae",
       "bundle","nou_bin","kansa_seq","kansa_parent_seq","kansa_readback","board_task","sen_eta","jitsu"]
H40 = re.compile(r"^[0-9a-f]{40}$")
d = yaml.safe_load(open(chou, encoding="utf-8"))
if not isinstance(d, dict):
    print(f"top が dict でない: {type(d).__name__}"); sys.exit(3)
blk = {k: v for k, v in d.items() if isinstance(v, dict)}
st = collections.Counter(str(v.get("status")) for v in blk.values())
done = {k: v for k, v in blk.items() if v.get("status") == "done"}
if len(sys.argv) > 4 and sys.argv[4] == "hira":  # 平場の帳(一弾一件)は top 自身を一件として数へる
    done = {"(top)": d} if d.get("status") == "done" else {}
print(f"帳={chou}\n全鍵={len(d)} 塊={len(blk)} 塊でない鍵={len(d)-len(blk)} status内訳={dict(st)} 母数(done塊)={len(done)}")
with open(out + "_ran_sanchi.tsv", "w", encoding="utf-8") as f:
    f.write("ran\tyuu\tkara\tmu\twa\n")
    for r in RAN:
        c = collections.Counter()
        for v in done.values():
            if r not in v: c["無"] += 1
            elif v[r] is None or (isinstance(v[r], str) and v[r].strip() == ""): c["空"] += 1
            else: c["有"] += 1
        wa = c["有"] + c["空"] + c["無"]
        f.write(f"{r}\t{c['有']}\t{c['空']}\t{c['無']}\t{wa}\n")
        print(f"  {r:18s} 有={c['有']:3d} 空={c['空']:3d} 無={c['無']:3d} 和={wa}{'' if wa==len(done) else ' ★和≠母数★'}")
allf = sum(1 for v in done.values() if all(r in v and v[r] not in (None, "") for r in RAN))
kotei = sum(1 for v in done.values() if all(r in v and v[r] not in (None, "") for r in ("branch","tip","tree","oya")))
print(f"18欄悉く有={allf}/{len(done)} 固定ref四点(branch,tip,tree,oya)悉く有={kotei}/{len(done)}")
def jz(sha):
    p = subprocess.run(["git", "--git-dir", gitdir, "cat-file", "-e", sha], capture_output=True)
    if p.returncode == 0:
        t = subprocess.run(["git", "--git-dir", gitdir, "cat-file", "-t", sha], capture_output=True, text=True)
        return "在", t.stdout.strip(), 0
    return ("不在" if p.returncode == 1 else "測れぬ"), "-", p.returncode
cnt = collections.Counter()
with open(out + "_sha_jitsuzai.tsv", "w", encoding="utf-8") as f:
    f.write("key\tran\tvalue\tkatachi\thantei\tkata\trc\n")
    for k, v in sorted(done.items()):
        for r in ("tip", "tree", "oya"):
            if r not in v or v[r] in (None, ""): continue
            s = str(v[r])
            if not H40.match(s):
                f.write(f"{k}\t{r}\t{s}\t非40桁\t判ぜず(形の疵)\t-\t-\n"); cnt[(r, "非40桁")] += 1; continue
            h, t, rc = jz(s)
            f.write(f"{k}\t{r}\t{s}\t40桁\t{h}\t{t}\t{rc}\n"); cnt[(r, h)] += 1; cnt[(r, "kata:" + t)] += 1
for r in ("tip", "tree", "oya"):
    print(f"  {r}: " + " ".join(f"{x}={n}" for (rr, x), n in sorted(cnt.items()) if rr == r))
for name, s in (("陽性対照(HEAD)", subprocess.run(["git","--git-dir",gitdir,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()), ("陰性対照(0x40)", "0"*40)):
    h, t, rc = jz(s); print(f"  {name} {s} → {h} 型={t} rc={rc}")
