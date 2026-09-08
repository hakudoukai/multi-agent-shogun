#!/usr/bin/env python3
# o111: 「logs 樹は一度に作られた(09-07 10:39:53)」の★見当★を、
#       器の刻(mtime)でなく ★中身の刻(reflog 最古 entry)★ で当てる。
#   在り(閾より前の中身が現に在る) = ★中身は持ち越された(copy)★
#   無し                          = ★其の刻に始まつた★
# 走 1。両樹の .git は讀取のみ。git 実行 0。DB 0。
import collections, datetime, pathlib, re, sys

JST  = datetime.timezone(datetime.timedelta(hours=9))
MNTC = pathlib.Path("/mnt/c/DentalBI/.git")
HOME = pathlib.Path("/home/hakudoukai/multi-agent-shogun/.git")
LINE = re.compile(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .*?> (\d+) ([+-]\d{4})\t?(.*)$")

def ts(v):
    return datetime.datetime.fromtimestamp(v, JST).strftime("%Y-%m-%dT%H:%M:%S")

def first_entry(p):
    """(epoch, None) / (None, 除いた理由). 理由は★名で★残す(五条の親類)。"""
    try:
        st = p.stat()
    except OSError as e:
        return None, "stat:" + type(e).__name__
    if st.st_size == 0:
        return None, "zero-byte"
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for l in f:
                l = l.rstrip("\n")
                if not l:
                    continue
                m = LINE.match(l)
                if not m:
                    return None, "no-match"
                return int(m.group(3)), None
    except OSError as e:
        return None, "open:" + type(e).__name__
    return None, "no-nonblank-line"

def survey(G, label):
    root = G / "logs" / "refs"
    files = sorted(p for p in root.rglob("*") if p.is_file()) if root.is_dir() else []
    ok, excl = [], []            # ok=(name, birth, mtime) / excl=(name, 理由)
    for p in files:
        nm = "refs/" + str(p.relative_to(root))
        b, why = first_entry(p)
        if b is None:
            excl.append((nm, why))
        else:
            ok.append((nm, b, p.stat().st_mtime))
    print("[%s] logs/refs file = %d ―― 讀めた %d ＋ 除いた %d" % (label, len(files), len(ok), len(excl)))
    c = collections.Counter(w for _, w in excl)
    for w, n in sorted(c.items()):
        print("[%s]   除いた理由 %-16s = %d 本" % (label, w, n))
    assert len(ok) + len(excl) == len(files), "母数の検算に合はぬ"
    zm = sorted(set(round(p.stat().st_mtime, 3) for p in files
                    if p.stat().st_size == 0))
    if zm:
        print("[%s] 0byte の mtime 相異なる分 = %d 個 (最古 %s / 最新 %s)"
              % (label, len(zm), ts(zm[0]), ts(zm[-1])))
    # logs/HEAD の最古 entry
    h = G / "logs" / "HEAD"
    if h.is_file():
        b, why = first_entry(h)
        print("[%s] logs/HEAD 最古 entry = %s" % (label, ts(b) if b else "×(" + str(why) + ")"))
    return ok, excl, (zm[-1] if zm else None)

def verdict(ok, T, label):
    if T is None:
        print("[%s] 閾を此の樹から取れず ⇒ 判じ無し" % label)
        return [], []
    before = [t for t in ok if t[1] <  T]
    after  = [t for t in ok if t[1] >= T]
    print("[%s] 閾 T = %s (0byte 112 本の mtime)" % (label, ts(T)))
    print("[%s] 中身の刻が T より★前★ = %d 本 / T 以降 = %d 本 (計 %d)"
          % (label, len(before), len(after), len(ok)))
    if ok:
        bs = sorted(t[1] for t in ok)
        print("[%s] 中身の刻 最古 = %s / 最新 = %s" % (label, ts(bs[0]), ts(bs[-1])))
        d = collections.Counter(datetime.datetime.fromtimestamp(t[1], JST).strftime("%Y-%m") for t in ok)
        for k in sorted(d):
            print("[%s]   月別 %s = %d 本" % (label, k, d[k]))
    # 中身の刻 vs 器の刻(mtime) の前後
    older = [t for t in ok if t[1] < t[2] - 1]
    print("[%s] 中身の刻が 己の mtime より★古い★ = %d / %d 本" % (label, len(older), len(ok)))
    return before, after

def main():
    print("=== o111 中身の刻で『一度に作られた』を当てる ===")
    print("as_of = %s" % ts(datetime.datetime.now(JST).timestamp()))
    ok_c, ex_c, T = survey(MNTC, "/mnt/c")
    before, after = verdict(ok_c, T, "/mnt/c")
    print("---- 対照(home・同一条件に非ず) ----")
    ok_h, ex_h, Th = survey(HOME, "home")
    verdict(ok_h, T, "home")   # 閾は /mnt/c の物を借りる(比較の為)
    stamp = datetime.datetime.now(JST).strftime("%Y%m%d_%H%M%S")
    out = pathlib.Path(__file__).with_name("o111_content_clock_%s.txt" % stamp)
    lines = ["# o111 中身の刻(最古 entry) 一覧。0 本でも落とす(五条の親類)。",
             "# 閾 T = %s" % (ts(T) if T else "取れず"),
             "# 列: 樹 / 名 / 中身の最古 entry / file の mtime / T より前か"]
    for lab, rows in (("/mnt/c", ok_c), ("home", ok_h)):
        for nm, b, mt in sorted(rows):
            lines.append("%s\t%s\t%s\t%s\t%s" % (lab, nm, ts(b), ts(mt),
                                                 "前" if (T and b < T) else "以降"))
    for lab, rows in (("/mnt/c", ex_c), ("home", ex_h)):
        for nm, why in sorted(rows):
            lines.append("%s\t%s\t除いた:%s" % (lab, nm, why))
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("名の一覧 = %s (%d 行)" % (out.name, len(lines)))
    print("=== 了 ===")

main()
