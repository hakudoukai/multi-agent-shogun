#!/usr/bin/env python3
# o112: ★何が 112(空にされた) と 88(同秒に触られたが中身を保つた) を分けたか★ を数へる。
#   物差し三つ ―― ①名の階層 ②中身の刻 ③今の ref の在り処(loose / packed / 無し)
#   偏りが在れば「其の物差しに規則が現れて居る」・無ければ「其の物差しでは説明できぬ」。
# 走 1。讀取のみ。git 実行 0。DB 0。
import collections, datetime, pathlib, re

JST  = datetime.timezone(datetime.timedelta(hours=9))
G    = pathlib.Path("/mnt/c/DentalBI/.git")
T_S  = 1  # 帯の幅(秒)。T の「同じ秒」に触られた物を一組と見る。
LINE = re.compile(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$")

def ts(v):
    return datetime.datetime.fromtimestamp(v, JST).strftime("%Y-%m-%dT%H:%M:%S")

def entries(p):
    """(最古, 最新, 行数) / 讀めねば None"""
    first = last = None; n = 0
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for l in f:
            l = l.rstrip("\n")
            if not l:
                continue
            m = LINE.match(l)
            if not m:
                continue
            n += 1
            v = int(m.group(3))
            if first is None:
                first = v
            last = v
    return (first, last, n) if first is not None else None

def layer(nm):
    """refs/heads/x/y -> 'heads' ／ refs/remotes/origin/... -> 'remotes/origin'"""
    parts = nm.split("/")
    if len(parts) >= 3 and parts[1] == "remotes":
        return "remotes/" + parts[2]
    return parts[1] if len(parts) >= 2 else nm

def main():
    print("=== o112 112 と 88 を分けた物は何か ===")
    print("as_of = %s" % ts(datetime.datetime.now(JST).timestamp()))

    root = G / "logs" / "refs"
    rows = []                       # (name, size, mtime, entries or None)
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        nm = "refs/" + str(p.relative_to(root))
        st = p.stat()
        e = None if st.st_size == 0 else entries(p)
        rows.append((nm, st.st_size, st.st_mtime, e))

    zero = [r for r in rows if r[1] == 0]
    T = max(r[2] for r in zero)
    band = int(T)
    keep = [r for r in rows if r[1] > 0 and int(r[2]) == band]     # 同秒・中身在り
    late = [r for r in rows if r[1] > 0 and int(r[2]) != band]     # 別の刻
    print("母数 %d = 空 %d ＋ 同秒で中身在り %d ＋ 別の刻 %d" % (len(rows), len(zero), len(keep), len(late)))
    assert len(zero) + len(keep) + len(late) == len(rows), "母数の検算に合はぬ"

    # 今の ref の在り処
    loose = set()
    rr = G / "refs"
    for p in rr.rglob("*"):
        if p.is_file():
            loose.add("refs/" + str(p.relative_to(rr)))
    packed = set()
    pf = G / "packed-refs"
    if pf.is_file():
        with open(pf, "r", encoding="utf-8", errors="replace") as f:
            for l in f:
                l = l.rstrip("\n")
                if not l or l[0] in "#^":
                    continue
                sp = l.split(" ", 1)
                if len(sp) == 2:
                    packed.add(sp[1].strip())
    def where(nm):
        a, b = nm in loose, nm in packed
        return "両方" if (a and b) else ("loose" if a else ("packed" if b else "無し"))

    for label, grp in (("空 112", zero), ("同秒・中身在り 88", keep), ("別の刻", late)):
        print("---- [%s] %d 本 ----" % (label, len(grp)))
        c1 = collections.Counter(layer(r[0]) for r in grp)
        print("  ①名の階層 : " + " / ".join("%s=%d" % (k, c1[k]) for k in sorted(c1)))
        c3 = collections.Counter(where(r[0]) for r in grp)
        print("  ③在り処   : " + " / ".join("%s=%d" % (k, c3[k]) for k in sorted(c3)))
        es = [r[3] for r in grp if r[3]]
        if es:
            print("  ②中身の刻 : 最古 %s / 最新 %s / 行数 計 %d (中央 %d)"
                  % (ts(min(e[0] for e in es)), ts(max(e[1] for e in es)),
                     sum(e[2] for e in es), sorted(e[2] for e in es)[len(es) // 2]))
        else:
            print("  ②中身の刻 : ★中身が無いゆゑ 出せぬ★")

    # 交差表: 空/保つ × 在り処
    print("---- 交差表 (空 対 保つ) × 在り処 ----")
    for w in ("loose", "packed", "両方", "無し"):
        z = sum(1 for r in zero if where(r[0]) == w)
        k = sum(1 for r in keep if where(r[0]) == w)
        print("  %-6s : 空 %3d / 保つ %3d" % (w, z, k))
    print("---- 交差表 (空 対 保つ) × 名の階層 ----")
    ks = sorted(set(layer(r[0]) for r in zero) | set(layer(r[0]) for r in keep))
    for k_ in ks:
        z = sum(1 for r in zero if layer(r[0]) == k_)
        k = sum(1 for r in keep if layer(r[0]) == k_)
        print("  %-18s : 空 %3d / 保つ %3d" % (k_, z, k))

    stamp = datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S")
    out = pathlib.Path(__file__).with_name("o112_split_%s.txt" % stamp)
    lines = ["# o112 112/88/別の刻 の名の一覧。0 本でも落とす(五条の親類)。",
             "# 列: 組 / 名 / 階層 / 在り処 / 中身の最古 / 中身の最新 / 行数 / mtime"]
    for label, grp in (("空", zero), ("保つ", keep), ("別刻", late)):
        for nm, sz, mt, e in sorted(grp):
            lines.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                label, nm, layer(nm), where(nm),
                ts(e[0]) if e else "-", ts(e[1]) if e else "-", e[2] if e else 0, ts(mt)))
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("名の一覧 = %s (%d 行)" % (out.name, len(lines)))
    print("=== 了 ===")

main()
