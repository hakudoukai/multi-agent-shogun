#!/usr/bin/env python3
# order101 (K) / 席 ashigaru-third-2 / as_of 2026-09-08 09:5x JST
# 問: 紙 §3 の ㋑(他枝のみ 1,442) ∩ ㋺(履歴 D で消えた 357) を、★§3 を書いた時点(09-07 16:4x)の ref 集合★
#     で数へ直すと幾らか。o98(E) は ★現在(09-08 09:2x・334 ref)★ で数へた ―― 日が違ふ。
# ★出る数は「近似」である(実測ではない)。理 三つは印字の頭に置く。★
# 借り: order48_n_by_commit.py の L1-40（git / consts / g2re）を exec で再利用。★元器は不書換★。
# 写し: keep() / tree() / 判定は o98_overlap_probe.py の逐語＝二重実装ゆゑ開示（近似 ref を食はせる形にのみ変へた）。
# 走: python process ★1本★。git は cat-file/rev-parse/ls-tree/log/show の讀取のみ（書込動詞 0）。reflog は file を直に讀む。
import pathlib, fnmatch, subprocess, datetime, collections

REPO  = pathlib.Path("/mnt/c/DentalBI")
LOGS  = REPO / ".git" / "logs"
T_STR = "2026-09-07 16:45:00 +09:00"
T     = int(datetime.datetime(2026, 9, 7, 16, 45, 0,
            tzinfo=datetime.timezone(datetime.timedelta(hours=9))).timestamp())
ZERO  = "0" * 40

print("=" * 78)
print("★本器が出す数は【近似】である。実測と呼ぶな。★  基準時刻 T = %s (epoch %d)" % (T_STR, T))
print("―― 質が落つ理 三つ（打つ前に申した通り）――")
print(" 限り①: T の後に★削られた ref★ は reflog ごと失せ、復せぬ。∴ 本器の ref 集合は ★下振れ★ する。")
print(" 限り②: reflog を持たぬ ref が在り得る（clone 直後・手で作つた ref 等）。数へた上で除外する。")
print(" 限り③: T 時点の値も ★reflog 依り★（刈り取り gc.reflogExpire・時刻は書いた側の local 記録）。")
print("=" * 78)

SRCF = pathlib.Path("/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
ns = {}
exec(compile("\n".join(SRCF.read_text(encoding="utf-8").split("\n")[0:40]), str(SRCF), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

# ―― reflog を讀む（file を直に讀む＝git 書込動詞 0）
def reflog_entries(path):
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        if not line.strip():
            continue
        head = line.split("\t", 1)[0].split(" ")
        if len(head) < 4:
            continue
        try:
            ts = int(head[-2])
        except ValueError:
            continue
        out.append((ts, head[0], head[1]))          # (時刻, old, new)
    return out

reflog_files = sorted(q for q in LOGS.rglob("*") if q.is_file())
print("\n[1] reflog file 本数 = %d" % len(reflog_files))

# ―― 現在の ref 一覧（reflog を持たぬ ref を数へる為）
now_refs = {}
for l in git("for-each-ref", "--format=%(objectname) %(refname)").split("\n"):
    if l:
        sha, name = l.split(" ", 1)
        now_refs[name] = sha
print("[2] 現在の ref 本数 = %d   （§3 の記載 226 / o98 実測 334）" % len(now_refs))

approx, born_after, no_log, dead_at_T = {}, [], [], []
for q in reflog_files:
    rel = q.relative_to(LOGS).as_posix()
    if rel == "HEAD":
        continue
    ent = reflog_entries(q)
    before = [e for e in ent if e[0] <= T]
    if not before:
        born_after.append(rel)                      # T 時点で未だ無い（or reflog が刈られた＝限り③）
        continue
    new = before[-1][2]
    if new == ZERO:
        dead_at_T.append(rel)                       # T 時点で消えて居た
        continue
    approx[rel] = new
for name in now_refs:
    if not (LOGS / name).is_file():
        no_log.append(name)

print("[3] T 時点に在つたと近似できた ref = ★%d★" % len(approx))
print("    内訳外: T 以後に生まれた(=T 前の記録が無い) %d / T 時点で消えて居た %d / reflog を持たぬ現 ref %d"
      % (len(born_after), len(dead_at_T), len(no_log)))
print("    ★限り①の分（T に在り今は無い ref）は ここに 1 本も入つて居らぬ★")

def sha_at_T(name):
    return approx.get(name)

# ―― HEAD と origin/main を T 時点へ
head_ent = reflog_entries(LOGS / "HEAD")
head_before = [e for e in head_ent if e[0] <= T]
head_then = head_before[-1][2] if head_before else None
main_then = sha_at_T("refs/remotes/origin/main") or sha_at_T("refs/heads/main")
print("\n[4] T 時点の HEAD = %s / origin/main = %s" % (str(head_then)[:9], str(main_then)[:9]))
print("    現在の  HEAD = %s / origin/main = %s"
      % (git("rev-parse", "HEAD").strip()[:9], git("rev-parse", "origin/main").strip()[:9]))

# ―― 網（INCLUDE/EXCLUDE）も T 時点の物を使ふ。現在の網との違ひも見る。
C_then = consts(main_then) if main_then else None
C_now  = consts("origin/main")
same_net = (C_then == C_now)
print("[5] 網(INCLUDE/EXCLUDE/EXCLUDE_DIRS) T 時点と現在で同一か = %s" % same_net)
C = C_then or C_now
INC = [g2re(p) for p in C.get("INCLUDE_PATTERNS", [])]
EXC = list(C.get("EXCLUDE_PATTERNS", []))
EXD = set(C.get("EXCLUDE_DIRS", set()) or set())
print("    使つた網: INCLUDE=%d EXCLUDE=%d EXCLUDE_DIRS=%d （T 時点の main の sync_source_cache.py 由来）"
      % (len(INC), len(EXC), len(EXD)))

def keep(paths):
    out = set()
    for rel in paths:
        if not rel: continue
        if EXD and any(part in EXD for part in rel.split("/")): continue
        if not any(r.match(rel) for r in INC): continue
        if any(fnmatch.fnmatch(rel, p) for p in EXC): continue
        out.add(rel)
    return out

def tree(c):
    return [l for l in git("ls-tree", "-r", "--name-only", c).split("\n") if l]

M = keep(tree(main_then))
H = keep(tree(head_then)) if head_then else set()
print("\n[6] T 時点 main tip の INCLUDE 通過 M=%d / HEAD の H=%d" % (len(M), len(H)))

U, miss = set(), 0
shas = []
for name, sha in sorted(approx.items()):
    try:
        U |= keep(tree(sha))
        shas.append(sha)
    except Exception:
        miss += 1
print("[7] 近似 ref 合併の INCLUDE 集合 U=★%d★   （§3 の記載 5,627 / 讀めなんだ ref %d）" % (len(U), miss))

I1 = U - M
print("[8] ★㋑ 他枝のみ（近似）★ = %d   （§3 の記載 1,442 / o98 の現在値と比べよ）" % len(I1))

dele = set()
uniq = sorted(set(shas))
CH = 200
for i in range(0, len(uniq), CH):
    dele |= set(l for l in git("log", "--diff-filter=D", "--pretty=format:", "--name-only", *uniq[i:i + CH]).split("\n") if l)
I2 = keep(dele) - H
print("[9] ★㋺ 履歴 D で消え 現(T)tree に無い（近似）★ = %d   （§3 の記載 357）" % len(I2))

both = I1 & I2
print("\n" + "=" * 78)
print("[10] ★★㋑ ∩ ㋺ ＝ %d 本（近似・T=09-07 16:45）★★" % len(both))
print("     ㋑ のみ = %d / ㋺ のみ = %d / 和(重複を除く) = %d" % (len(I1 - I2), len(I2 - I1), len(I1 | I2)))
tops = collections.Counter(p.split("/")[0] for p in both)
print("     重なりの先頭階層別: " + ", ".join("%s=%d" % kv for kv in tops.most_common()))
print("=" * 78)
print("★再掲：上の数は【近似】である。限り①②③により ★下振れし得る★。実測と呼ぶな。★")
