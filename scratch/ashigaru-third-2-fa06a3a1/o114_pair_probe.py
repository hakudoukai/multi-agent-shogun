#!/usr/bin/env python3
# o114: 112 と 88 の分け目を ★対★ と ★第三の目(時の閾)★ で挟み撃つ。
#   ①345 本を枝名で対にする(層を跨いで同名を束ねる)
#   ②(heads の組 × origin の組) の表
#   ③空 heads と 空 origin の ★重なりを名で★ 落とす
#   ④第三の目=『時の閾で切つた(reflog expire の形)』を検める ―― T2 直前の切れ目
#   ★file を讀むだけ。git は一度も実行せぬ。★
import collections, datetime, os

D     = "scratch/ashigaru-third-2-fa06a3a1"
L112  = D + "/o112_split_20260908_115933.txt"      # 組/名/階層/在り処/最古/最新/行数/mtime
L113  = D + "/o113_birthmark_20260908_121130.txt"  # 組/名/刻/印/action/理由

def load(path, keycol=1):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("#"):
                continue
            c = ln.rstrip("\n").split("\t")
            if len(c) > keycol:
                rows.append(c)
    return rows

r112 = load(L112)
r113 = {c[1]: c for c in load(L113)}
print("母数(引継) %d 本 / o113 の印 %d 本" % (len(r112), len(r113)))

def base(nm):
    # refs/heads/X → X ／ refs/remotes/<remote>/X → X ／ refs/stash → stash
    p = nm.split("/")
    if len(p) >= 3 and p[1] == "heads":
        return "/".join(p[2:])
    if len(p) >= 4 and p[1] == "remotes":
        return "/".join(p[3:])
    return "/".join(p[1:])

def layer(nm):
    p = nm.split("/")
    if len(p) >= 2 and p[1] == "heads":
        return "heads"
    if len(p) >= 4 and p[1] == "remotes":
        return "remotes/" + p[2]
    return p[1] if len(p) > 1 else "?"

pair = collections.defaultdict(dict)
for c in r112:
    grp, nm = c[0], c[1]
    pair[base(nm)][layer(nm)] = (grp, nm, c[6], c[4])   # 組/名/行数/最古
print("★枝名で束ねると %d 個の名★（345 本 → %d 名）" % (len(pair), len(pair)))

# ── ② (heads の組 × origin の組) ──
tab = collections.Counter()
only = collections.Counter()
for b, d in pair.items():
    h = d.get("heads"); o = d.get("remotes/origin")
    if h and o:
        tab[(h[0], o[0])] += 1
    elif h:
        only[("heads のみ", h[0])] += 1
    elif o:
        only[("origin のみ", o[0])] += 1
    else:
        only[("其の他の層のみ", list(d.values())[0][0])] += 1
print("② 対に成つた名 %d 個の (heads の組 × origin の組):" % sum(tab.values()))
for k, v in sorted(tab.items(), key=lambda x: -x[1]):
    print("     %s × %s = %d" % (k[0], k[1], v))
print("② 片側だけの名 %d 個: %s" % (sum(only.values()), dict(only)))

# ── ③ 重なりを名で ──
both_zero = sorted(b for b, d in pair.items()
                   if d.get("heads", ("",))[0] == "空" and d.get("remotes/origin", ("",))[0] == "空")
split_hz = sorted(b for b, d in pair.items()
                  if d.get("heads", ("",))[0] == "空" and d.get("remotes/origin", ("",))[0] == "保つ")
split_oz = sorted(b for b, d in pair.items()
                  if d.get("heads", ("",))[0] == "保つ" and d.get("remotes/origin", ("",))[0] == "空")
print("③ ★双方 空 = %d 名★ / ★heads 空・origin 保つ = %d 名★ / ★heads 保つ・origin 空 = %d 名★"
      % (len(both_zero), len(split_hz), len(split_oz)))
for lab, lst in (("双方空", both_zero), ("h空o保", split_hz), ("h保o空", split_oz)):
    print("     %s の名(頭 4): %s" % (lab, lst[:4]))

# ── ④ 第三の目: 時の閾 ──
ts = []
for c in r112:
    if c[0] in ("保つ", "別刻") and c[4] != "-":
        ts.append((c[4], c[0], c[1]))
ts.sort()
T2 = min(t for t, g, n in ts if g == "保つ")
print("④ T2(保つ の最古) = %s" % T2)
before = [x for x in ts if x[0] < T2]
print("④ T2 より古い最古 entry = %d 本: %s" % (len(before), [(x[0], x[2][:40]) for x in before]))
after = [x for x in ts if x[0] >= T2]
print("④ T2 以降 = %d 本・最初の 6 本:" % len(after))
for x in after[:6]:
    print("     %s %s %s" % (x[0], x[1], x[2][:52]))
# 切れ目(隣り合ふ最古 entry の間隔)の上位
gaps = []
for i in range(1, len(after)):
    a = datetime.datetime.fromisoformat(after[i - 1][0])
    b2 = datetime.datetime.fromisoformat(after[i][0])
    gaps.append(((b2 - a).total_seconds() / 3600.0, after[i - 1][0], after[i][0]))
gaps.sort(reverse=True)
print("④ T2 以降の最古 entry 群で ★最も広い間隔 上位 3★(時間): %s"
      % [(round(g[0], 1), g[1], g[2]) for g in gaps[:3]])
if before:
    gb = (datetime.datetime.fromisoformat(T2)
          - datetime.datetime.fromisoformat(max(x[0] for x in before))).total_seconds() / 3600.0
    print("④ ★T2 直前の切れ目 = %.1f 時間★(T2 より古い最も新しい本から T2 迄)" % gb)

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out = "%s/o114_pairs_%s.txt" % (D, stamp)
with open(out, "w", encoding="utf-8") as f:
    f.write("# o114 枝名で束ねた対。列: 枝名 / heads の組 / origin の組 / 其の他の層 / heads 行数 / origin 行数\n")
    for b in sorted(pair):
        d = pair[b]
        h = d.get("heads"); o = d.get("remotes/origin")
        oth = ",".join("%s=%s" % (k, v[0]) for k, v in d.items() if k not in ("heads", "remotes/origin"))
        f.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (b, h[0] if h else "-", o[0] if o else "-",
                                              oth or "-", h[2] if h else "-", o[2] if o else "-"))
print("名の一覧: %s (%d 行)" % (out, len(pair) + 1))
