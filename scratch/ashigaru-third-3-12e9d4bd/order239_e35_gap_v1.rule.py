# -*- coding: utf-8 -*-
# order239 E35 gap: after hand-labelling 12 F7_bare rows, two further forms appeared.
#   F8_unitgap  = number + a 助数詞 that the o237 UNIT vocabulary never held (様/欄/点/…)
#   F9_prevline = the 母 sits on the PREVIOUS line (the window is one line wide)
# this instrument measures the GATE of each, separately, on both corpora.
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
KO = u"悉く"; MI = u"皆"; SK = u"悉皆"; HT = u"一つも"
JYO = re.compile(u"(條|条\\(|隊の条|家老 條|新條|[一二三四五六七八九]百[〇一二三四五六七八九十]+)")
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"
UNIT2 = (u"(様|欄|点|階|段|層|組|対|面|側|群|類|名|台|基|列|表|図|節|項|種|口|席|枝|型|形|例"
         u"|色|系|軸|度|通|周|巡|品|物|人|機|環|端|辺|双|冊|葉|株|片|節|款|符|札|箱|便|紙|器)")
KAN = u"[一二三四五六七八九十]+"
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|書き換|数へ|用ゐ|打つ|打ち|送つ"
                 u"|算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")
OLDBO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|[0-9][0-9,]*\\s*" + UNIT +
                   u"|母\\s*[0-9]|[0-9][0-9,]*\\s*(→|->)\\s*[0-9]|" + KAN + UNIT +
                   u"|\\|\\s*[0-9][0-9,]*\\s*\\|)")
AU = (u"(file|files|blob|blobs|spec|specs|commit|commits|ref|refs|entry|entries"
      u"|row|rows|col|cols|line|lines|byte|bytes|KB|MB|px|node|nodes|token|tokens"
      u"|case|cases|item|items|hit|hits|dir|dirs|py|sh|md|yaml|json|B)")
F6 = re.compile(u"[0-9][0-9,]*\\s*" + AU + u"([^A-Za-z]|$)")
F8 = re.compile(u"([0-9][0-9,]*\\s*" + UNIT2 + u"|" + KAN + UNIT2 + u")")
def mask(ln): return ln.replace(KO, u"　　").replace(HT, u"　　　")
def scan(lines):
    """lines = list of text lines; returns rows (idx, word, line) that are claims w/o OLD 母."""
    out = []
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith(u">") or JYO.search(ln): continue
        for w in (KO, HT):
            k = 0
            while True:
                k = ln.find(w, k)
                if k < 0: break
                k += len(w)
                if ACT.match(ln[k:k+6].strip()): continue
                if OLDBO.search(mask(ln)): continue
                out.append((i, w, ln))
    return out
def tally(name, docs):
    c = collections.Counter()
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln)
            f6 = bool(F6.search(m)); f8 = bool(F8.search(m))
            prev = mask(lines[i-1]) if i > 0 else u""
            f9 = bool(OLDBO.search(prev) or F6.search(prev) or F8.search(prev))
            c[u"total"] += 1
            if f6: c[u"F6_ascii"] += 1
            if f8: c[u"F8_unitgap"] += 1
            if f9: c[u"F9_prevline"] += 1
            if f8 and not f6: c[u"F8_only"] += 1
            if f9 and not (f6 or f8): c[u"F9_only"] += 1
            if not (f6 or f8 or f9): c[u"residue"] += 1
    print(u"[%s]" % name)
    for k in (u"total", u"F6_ascii", u"F8_unitgap", u"F8_only", u"F9_prevline", u"F9_only", u"residue"):
        print(u"   %-12s %5d" % (k, c[k]))
    return c
papers = [io.open(f, encoding="utf-8").read().split(chr(10))
          for f in sorted(glob.glob(os.path.join(D, u"*.md")))]
tally(u"papers", papers)
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
seen = set(); letters = []
for pat in SRC:
    for f in sorted(glob.glob(pat)):
        t = io.open(f, encoding="utf-8", errors="replace").read()
        for raw in re.split(u"(?m)^- ", t)[1:]:
            d = parse_block(u"  " + raw)
            if d.get(u"from", u"").strip() != ME: continue
            i = d.get(u"id", u"").strip()
            if not i or i in seen: continue
            seen.add(i); letters.append(d.get(u"content", u"").split(u"\n"))
tally(u"letters", letters)
print(u"letters_distinct=%d  papers=%d" % (len(seen), len(papers)))
