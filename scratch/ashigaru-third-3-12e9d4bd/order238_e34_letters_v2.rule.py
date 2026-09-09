# -*- coding: utf-8 -*-
# E34 v2: 便(己が家老へ運んだ物)を悉皆に取る。v1 の疵=塊分けが `^- (?=id: )` 形で
# archive(`- content:` 先頭)を悉く落した。v2 は `^- ` で割り 鍵順に依らず読む。
import io, os, re, glob, sys

ME = u"ashigaru-third-3"
SRCPAT = (u"queue/inbox/karo*.yaml",
          u"queue/inbox/_archive/karo*.yaml",
          u"queue/inbox/archive/karo*.yaml",
          u"queue/archive/*.yaml")
SRC = []
for p in SRCPAT:
    SRC.extend(sorted(glob.glob(p)))

KO = u"悉く"; MI = u"皆"; SK = u"悉皆"; HT = u"一つも"
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"
KAN  = u"[一二三四五六七八九十]+"
BO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|[0-9][0-9,]*\\s*" + UNIT +
                u"|母\\s*[0-9]|[0-9][0-9,]*\\s*(→|->)\\s*[0-9]|" + KAN + UNIT +
                u"|\\|\\s*[0-9][0-9,]*\\s*\\|)")
AMI = re.compile(u"(網|窓|錨|ast|grep|glob|正規表現|pattern|悉皆|門|pin|blob|器)")
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|動し|書き換|数へ|用ゐ|打つ|打ち|送つ|"
                 u"算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")

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

seen = {}
nblk = 0; nmine = 0; noid = 0; hit_files = {}
for f in SRC:
    try:
        t = io.open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for raw in re.split(u"(?m)^- ", t)[1:]:
        nblk += 1
        d = parse_block(u"  " + raw)
        if d.get(u"from", u"").strip() != ME: continue
        nmine += 1
        hit_files[f] = hit_files.get(f, 0) + 1
        i = d.get(u"id", u"").strip()
        if not i:
            noid += 1; i = u"NOID:" + os.path.basename(f) + u":" + str(nblk)
        c = d.get(u"content", u"")
        if i not in seen or len(c) > len(seen[i][2]):
            seen[i] = (os.path.basename(f), d.get(u"from", u""), c)

sys.stdout.write("src_files=%d blocks=%d mine_blocks=%d noid=%d distinct=%d\n"
                 % (len(SRC), nblk, nmine, noid, len(seen)))
for f in sorted(hit_files):
    sys.stdout.write("SRC\t%s\t%d\n" % (f, hit_files[f]))

def count(sub):
    n = 0; L = 0
    for i in seen:
        k = seen[i][2].count(sub)
        if k: n += 1; L += k
    return L, n
for nm, sub in ((u"KO",KO),(u"MI",MI),(u"SK",SK),(u"HT",HT)):
    L, n = count(sub)
    sys.stdout.write("%s raw=%d letters=%d\n" % (nm, L, n))
mo = 0; moL = 0
for i in seen:
    k = seen[i][2].count(MI) - seen[i][2].count(SK)
    if k > 0: mo += 1; moL += k
sys.stdout.write("mina_standalone raw=%d letters=%d\n" % (moL, mo))

rows = []
for i in sorted(seen):
    s, fr, c = seen[i]
    for ln in c.split(u"\n"):
        for w in (KO, HT):
            if w not in ln: continue
            hit = False
            for m in re.finditer(re.escape(w), ln):
                if ACT.match(ln[m.end():m.end()+6]): continue
                hit = True; break
            if not hit: continue
            masked = ln.replace(KO, u"　　").replace(HT, u"　　　")
            rows.append((i, s, w, bool(BO.search(masked)), bool(AMI.search(ln)), ln.strip()))
            break
nobo = [r for r in rows if not r[3]]
sys.stdout.write("claim=%d claim_without_bo=%d letters_with_nobo=%d\n"
                 % (len(rows), len(nobo), len(set(r[0] for r in nobo))))
for r in nobo:
    sys.stdout.write("NOBO\t%s\t%s\t%s\tami=%s\t%s\n"
                     % (r[0], r[1], r[2].encode("utf-8"), r[4], r[5][:170].encode("utf-8")))
