# -*- coding: utf-8 -*-
# order239 E35 v1: cast the six 母(denominator) forms as an explicit TYPE table,
#   and measure the GATE before widening (立条: measure gate+power first).
# finding to verify here: o237 v3's own header comment claims it widened for
#   "kanji numerals / 箇所 / bare N / N->M arrows / table columns" but the BO regex
#   contains NO bare-N alternative. comment vs instrument disagree.
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
KO = u"悉く"; MI = u"皆"; SK = u"悉皆"; HT = u"一つも"
JYO = re.compile(u"(條|条\\(|隊の条|家老 條|新條|[一二三四五六七八九]百[〇一二三四五六七八九十]+)")
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"
KAN = u"[一二三四五六七八九十]+"
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|書き換|数へ|用ゐ|打つ|打ち|送つ"
                 u"|算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")
# ---- the TYPE table (each form is its own regex, named) ----
AU = (u"(file|files|blob|blobs|spec|specs|commit|commits|ref|refs|entry|entries"
      u"|row|rows|col|cols|line|lines|byte|bytes|KB|MB|px|node|nodes|token|tokens"
      u"|case|cases|item|items|hit|hits|dir|dirs|py|sh|md|yaml|json|B)")
FORMS = [
    (u"F1_kanji",  re.compile(KAN + UNIT)),
    (u"F2_wa_unit",re.compile(u"[0-9][0-9,]*\\s*" + UNIT)),
    (u"F3_ratio",  re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|母\\s*[0-9])")),
    (u"F4_arrow",  re.compile(u"[0-9][0-9,]*\\s*(→|->)\\s*[0-9]")),
    (u"F5_column", re.compile(u"\\|\\s*[0-9][0-9,]*\\s*\\|")),
    (u"F6_ascii",  re.compile(u"[0-9][0-9,]*\\s*" + AU + u"([^A-Za-z]|$)")),
    (u"F7_bare",   re.compile(u"(^|[^0-9A-Za-z_])[0-9][0-9,]*([^0-9A-Za-z_]|$)")),
]
OLD = set([u"F1_kanji", u"F2_wa_unit", u"F3_ratio", u"F4_arrow", u"F5_column"])
def mask(ln):
    return ln.replace(KO, u"　　").replace(HT, u"　　　")
def hits(ln):
    m = mask(ln)
    return set(n for n, r in FORMS if r.search(m))
# ---- corpus A: papers ----
prow = []
for f in sorted(glob.glob(os.path.join(D, u"*.md"))):
    t = io.open(f, encoding="utf-8").read()
    for i, ln in enumerate(t.split(chr(10)), 1):
        if ln.lstrip().startswith(u">") or JYO.search(ln): continue
        for w in (KO, HT):
            k = 0
            while True:
                k = ln.find(w, k)
                if k < 0: break
                k += len(w)
                if ACT.match(ln[k:k+6].strip()): continue
                prow.append((os.path.basename(f), i, w, ln))
# ---- corpus B: letters ----
ME = u"ashigaru-third-3"
SRC = (u"queue/inbox/karo*.yaml", u"queue/inbox/_archive/karo*.yaml",
       u"queue/inbox/archive/karo*.yaml", u"queue/archive/*.yaml")
def parse_block(b):
    d = {}; key = None; buf = []
    for ln in b.split(u"\n"):
        m = re.match(u"^  ([A-Za-z_][A-Za-z0-9_]*): ?(.*)$", ln)
        if m:
            if key is not None: d[key] = u"\n".join(buf)
            key = m.group(1); buf = [m.group(2)]
        elif re.match(u"^ {4,}\\S", ln) and key is not None:
            buf.append(ln.strip())
    if key is not None: d[key] = u"\n".join(buf)
    return d
seen = set(); lrow = []
for pat in SRC:
    for f in sorted(glob.glob(pat)):
        t = io.open(f, encoding="utf-8", errors="replace").read()
        for raw in re.split(u"(?m)^- ", t)[1:]:
            d = parse_block(u"  " + raw)
            if d.get(u"from", u"").strip() != ME: continue
            i = d.get(u"id", u"").strip()
            if not i or i in seen: continue
            seen.add(i)
            for ln in d.get(u"content", u"").split(u"\n"):
                if JYO.search(ln): continue
                for w in (KO, HT):
                    k = 0
                    while True:
                        k = ln.find(w, k)
                        if k < 0: break
                        k += len(w)
                        if ACT.match(ln[k:k+6].strip()): continue
                        lrow.append((i, w, ln))
def report(name, rows, txti):
    old_no = []; tab = collections.Counter()
    for r in rows:
        h = hits(r[txti])
        if h & OLD: continue
        old_no.append((r, h))
        tab[u"|".join(sorted(h)) or u"NONE"] += 1
    print(u"[%s] claims=%d  without_bo_under_OLD=%d" % (name, len(rows), len(old_no)))
    for k in sorted(tab, key=lambda x: -tab[x]):
        print(u"   newly_caught_by %-20s %5d" % (k, tab[k]))
    return old_no
pno = report(u"papers", prow, 3)
lno = report(u"letters", lrow, 2)
print(u"letters_distinct=%d" % len(seen))

# ---- v2 adds ONLY reporting. the measuring part above is unchanged (條 o174). ----
LOT7 = [u"msg_20260908_042426_3696d114", u"msg_20260908_042649_8abd966e",
        u"msg_20260908_042815_64a33631", u"msg_20260908_043316_f532a142",
        u"msg_20260908_085717_abac3049", u"msg_20260908_202104_acb3734e",
        u"msg_20260909_065735_c32689d0"]
print(u"---- ground truth: the 7 hand-labelled lot rows ----")
for r, h in lno:
    if r[0] in LOT7:
        print(u"LOT %s %s [%s] %s" % (r[0][-8:], r[1], u"|".join(sorted(h)) or u"NONE", r[2][:90]))
print(u"---- sample: letters caught by F6 only (第六形の独自の取り) ----")
n = 0
for r, h in lno:
    if h == set([u"F6_ascii"]):
        n += 1
        if n <= 12: print(u"F6 %s %s | %s" % (r[0][-8:], r[1], r[2][:110]))
print(u"F6_only_total=%d" % n)
print(u"---- sample: letters caught by F7 only (裸の数) ----")
n = 0
for r, h in lno:
    if h == set([u"F7_bare"]):
        n += 1
        if n % 42 == 1 and n <= 500: print(u"F7 %s %s | %s" % (r[0][-8:], r[1], r[2][:110]))
print(u"F7_only_letters=%d" % n)
print(u"---- sample: papers with NONE (数が一つも無い) ----")
n = 0
for r, h in pno:
    if not h:
        n += 1
        if n % 9 == 1 and n <= 90: print(u"NONE %s:%d %s | %s" % (r[0][:34], r[1], r[2], r[3][:100]))
print(u"NONE_papers=%d" % n)
print(u"---- my own E34 paper's contribution to its own denominator ----")
mine = [r for r, h in pno if r[0] == u"order238_e34_letters_v1.md"]
print(u"order238_e34_letters_v1.md rows_without_bo_under_OLD=%d" % len(mine))
