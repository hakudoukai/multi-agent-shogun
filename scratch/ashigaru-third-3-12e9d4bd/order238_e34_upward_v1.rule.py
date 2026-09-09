# -*- coding: utf-8 -*-
# E34 ③: 己の「母無し主張」が ★上へ運ばれたか★ を、己が讀める上位の箱で悉皆に当てる。
# 讀取のみ。上位箱 = shogun-third / commander / commander-third / iincho / gunshi-third / shogun。
import io, os, re, glob, sys
D = u"scratch/ashigaru-third-3-12e9d4bd"
KO = u"悉く"; HT = u"一つも"
JYO = re.compile(u"(條|条\\(|隊の条|家老 條|新條|[一二三四五六七八九]百[〇一二三四五六七八九十]+)")
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"
KAN = u"[一二三四五六七八九十]+"
BO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|[0-9][0-9,]*\\s*" + UNIT +
                u"|母\\s*[0-9]|[0-9][0-9,]*\\s*(→|->)\\s*[0-9]|" + KAN + UNIT +
                u"|\\|\\s*[0-9][0-9,]*\\s*\\|)")
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|書き換|数へ|用ゐ|打つ|打ち|送つ"
                 u"|算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")
DROP = re.compile(u"[\\s★☆・、。「」『』()（）\\\\]")
def norm(s): return DROP.sub(u"", s)

prows = []
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
                if BO.search(ln.replace(KO, u"　　").replace(HT, u"　　　")): continue
                prows.append((os.path.basename(f), i, w, k - len(w), ln))
sys.stdout.write("paper_nobo_rows=%d\n" % len(prows))

UP = [u"queue/inbox/shogun-third.yaml", u"queue/inbox/shogun.yaml",
      u"queue/inbox/commander.yaml", u"queue/inbox/commander-third.yaml",
      u"queue/inbox/iincho.yaml", u"queue/inbox/gunshi-third.yaml"]
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
ups = []   # (box, id, from, normtext)
for f in UP:
    if not os.path.exists(f): continue
    t = io.open(f, encoding="utf-8", errors="replace").read()
    n = 0
    for raw in re.split(u"(?m)^- ", t)[1:]:
        d = parse_block(u"  " + raw)
        c = d.get(u"content", u"")
        if not c: continue
        ups.append((os.path.basename(f), d.get(u"id", u"?"), d.get(u"from", u"?").strip(), norm(c)))
        n += 1
    sys.stdout.write("UPBOX\t%s\tblocks=%d\n" % (os.path.basename(f), n))
sys.stdout.write("up_letters=%d\n" % len(ups))

W = 12
hit = 0; short = 0
for (fn, i, w, pos, ln) in prows:
    key = norm(ln[max(0, pos - W): pos + len(w) + W])
    if len(key) < 10: short += 1; continue
    for (box, mid, fr, txt) in ups:
        if key in txt:
            hit += 1
            sys.stdout.write("UPHIT\t%s:%d\t%s\t%s\t%s\t%s\t%s\n"
                             % (fn, i, w.encode("utf-8"), box, mid, fr.encode("utf-8"),
                                ln.strip()[:150].encode("utf-8")))
            break
sys.stdout.write("carried_upward=%d skipped_short=%d window=%d\n" % (hit, short, W))
