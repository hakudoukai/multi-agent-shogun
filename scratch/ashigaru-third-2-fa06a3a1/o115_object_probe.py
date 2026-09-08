#!/usr/bin/env python3
# o115: 第四の目「其の ref が指す object の在否」で 112/88 が分かれるかを検める。
#   ★在否 ≠ 到達可能性★（expire は entry を消すのみ・後の gc で混ざる）＝『半ば』の意。
#   副の的: prefix の分布（★偏りが出ても「名で決めた」の証には成らぬ＝生れの偏りと交絡★）／
#           対 59 名で唯一食ひ違つた 1 名（空×別刻）の名。
#   ★file を讀むだけ。git は一度も実行せぬ。書込は scratch のみ。★
import collections, datetime, os, struct

GIT  = "/mnt/c/DentalBI/.git"
D    = "scratch/ashigaru-third-2-fa06a3a1"
L112 = D + "/o112_split_20260908_115933.txt"

rows = []
with open(L112, encoding="utf-8") as f:
    for ln in f:
        if not ln.startswith("#"):
            c = ln.rstrip("\n").split("\t")
            if len(c) >= 4:
                rows.append(c)          # 組/名/階層/在り処/最古/最新/行数/mtime
print("母数(引継) %d 本" % len(rows))

# ── ① tip sha を取る（packed-refs ＋ loose ref file）──
packed = {}
pr = os.path.join(GIT, "packed-refs")
with open(pr, encoding="utf-8", errors="replace") as f:
    for ln in f:
        if ln.startswith(("#", "^")):
            continue
        p = ln.split()
        if len(p) >= 2:
            packed[p[1]] = p[0]
print("packed-refs から %d 本" % len(packed))

tips = {}; miss = []
for c in rows:
    nm = c[1]
    p = os.path.join(GIT, nm)
    sha = None
    if os.path.isfile(p):
        try:
            t = open(p, encoding="utf-8", errors="replace").read().strip()
            if len(t) == 40:
                sha = t
        except OSError:
            pass
    if sha is None:
        sha = packed.get(nm)
    if sha is None:
        miss.append(nm)
    else:
        tips[nm] = sha
print("tip sha 取れた %d 本 / 取れぬ %d 本（名: %s）" % (len(tips), len(miss), miss[:5]))

# ── ② object の在否（loose ＋ pack idx v2 を binary parse）──
have = set()
objdir = os.path.join(GIT, "objects")
n_loose = 0
for d2 in os.listdir(objdir):
    if len(d2) == 2:
        try:
            for fn in os.listdir(os.path.join(objdir, d2)):
                if len(fn) == 38:
                    have.add(d2 + fn); n_loose += 1
        except OSError:
            pass
packdir = os.path.join(objdir, "pack")
n_pack = 0; idxn = 0
for fn in sorted(os.listdir(packdir)):
    if not fn.endswith(".idx"):
        continue
    idxn += 1
    with open(os.path.join(packdir, fn), "rb") as f:
        b = f.read()
    assert b[:4] == b"\xfftOc", "idx magic 違ひ: %s" % fn      # v1 は形が違ふ ―― 落とさず止める
    ver = struct.unpack(">I", b[4:8])[0]
    assert ver == 2, "idx version=%d (v2 を前提として居る): %s" % (ver, fn)
    fan = struct.unpack(">256I", b[8:8 + 1024])
    n = fan[255]
    off = 8 + 1024
    for i in range(n):
        have.add(b[off + i * 20: off + i * 20 + 20].hex())
    n_pack += n
print("object 在り: loose %d ＋ pack %d 本(idx %d 枚) = 索 %d" % (n_loose, n_pack, idxn, len(have)))

# ── ③ 組ごとの在る割合 ──
tab = collections.Counter(); det = collections.defaultdict(list)
for c in rows:
    grp, nm = c[0], c[1]
    sha = tips.get(nm)
    st = "tip 取れず" if sha is None else ("在り" if sha in have else "★無し★")
    tab[(grp, st)] += 1
    det[grp].append((nm, sha, st))
for grp in ("空", "保つ", "別刻"):
    tot = sum(v for k, v in tab.items() if k[0] == grp)
    d = {k[1]: v for k, v in tab.items() if k[0] == grp}
    print("③ %s 計 %d ―― %s" % (grp, tot, d))
    ng = [x for x in det[grp] if x[2] == "★無し★"]
    if ng:
        print("     無しの名(頭 3): %s" % [x[0][:56] for x in ng[:3]])

# ── ④ 副: prefix の分布（★交絡込みの記述であり 分け目の証に非ず★）──
def pref(nm):
    p = nm.split("/")
    b = "/".join(p[2:]) if (len(p) > 2 and p[1] == "heads") else ("/".join(p[3:]) if len(p) > 3 else p[-1])
    return b.split("/")[0] if "/" in b else (b.split("-")[0] if "-" in b else b)
pt = collections.defaultdict(collections.Counter)
for c in rows:
    pt[pref(c[1])][c[0]] += 1
top = sorted(pt.items(), key=lambda x: -sum(x[1].values()))[:8]
print("④ prefix 上位 8（★生れの偏りと交絡・分け目の証に非ず★）:")
for k, v in top:
    print("     %-28s %s" % (k[:28], dict(v)))

# ── ⑤ 対 59 名で唯一食ひ違つた 1 名 ──
by = collections.defaultdict(dict)
for c in rows:
    p = c[1].split("/")
    if len(p) > 2 and p[1] == "heads":
        by["/".join(p[2:])]["heads"] = c[0]
    elif len(p) > 3 and p[1] == "remotes" and p[2] == "origin":
        by["/".join(p[3:])]["origin"] = c[0]
odd = [(b, d) for b, d in by.items() if "heads" in d and "origin" in d and d["heads"] != d["origin"]]
print("⑤ ★食ひ違つた対 = %d 名★: %s" % (len(odd), odd))

stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out = "%s/o115_objects_%s.txt" % (D, stamp)
with open(out, "w", encoding="utf-8") as f:
    f.write("# o115 tip object の在否。列: 組 / 名 / tip sha / 在否 / prefix\n")
    for c in rows:
        nm = c[1]; sha = tips.get(nm)
        st = "tip 取れず" if sha is None else ("在り" if sha in have else "無し")
        f.write("%s\t%s\t%s\t%s\t%s\n" % (c[0], nm, sha or "-", st, pref(nm)))
print("名の一覧: %s (%d 行)" % (out, len(rows) + 1))
