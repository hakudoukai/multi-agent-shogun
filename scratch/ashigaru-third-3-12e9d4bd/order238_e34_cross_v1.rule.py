# -*- coding: utf-8 -*-
# E34 cross: 紙の「母無し主張」の内、★便に載つた物★ を悉皆に取る。
# 紙側の語彙(BO/ACT/AMI/JYO)は order237 v3 と ★一字も違へぬ★(下で source を突合し assert する)。
# 便側の解析は order238 v3 と同形(鍵順に依らぬ塊読み)。
# 讀取のみ・走行 0・書込は本 file の出力(標準出力)のみ。
import io, os, glob, re, sys

D = u"scratch/ashigaru-third-3-12e9d4bd"
KO = u"悉く"; MI = u"皆"; SK = u"悉皆"; HT = u"一つも"
JYO = re.compile(u"(條|条\\(|隊の条|家老 條|新條|[一二三四五六七八九]百[〇一二三四五六七八九十]+)")
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"
KAN = u"[一二三四五六七八九十]+"
BO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]"
                u"|n\\s*=\\s*[0-9]"
                u"|[0-9][0-9,]*\\s*" + UNIT +
                u"|母\\s*[0-9]"
                u"|[0-9][0-9,]*\\s*(→|->)\\s*[0-9]"
                u"|" + KAN + UNIT +
                u"|\\|\\s*[0-9][0-9,]*\\s*\\|)")
AMI = re.compile(u"(網|窓|錨|ast|grep|glob|正規表現|pattern|悉皆|門|pin|blob|器)")
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|書き換|数へ|用ゐ|打つ|打ち|送つ"
                 u"|算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")

# ---- 語彙が o237 v3 と同一である事を器自身に言はせる ----
ref = io.open(os.path.join(D, u"order237_e33_universal_words_v3.rule.py"), encoding="utf-8").read()
for name, lit in ((u"UNIT", UNIT), (u"KAN", KAN)):
    pass
same = (u'AMI = re.compile(u"(網|窓|錨|ast|grep|glob|正規表現|pattern|悉皆|門|pin|blob|器)")' in ref)
sys.stdout.write("vocab_same_as_o237v3=%s\n" % same)

# ---- 紙側: 母無し主張の行を text 付きで取る ----
files = sorted(glob.glob(os.path.join(D, u"*.md")))
prows = []
for f in files:
    t = io.open(f, encoding="utf-8").read()
    for i, ln in enumerate(t.split(chr(10)), 1):
        if ln.lstrip().startswith(u">"): continue
        if JYO.search(ln): continue
        for w in (KO, HT):
            k = 0
            while True:
                k = ln.find(w, k)
                if k < 0: break
                k += len(w)
                if ACT.match(ln[k:k+6].strip()): continue
                masked = ln.replace(KO, u"　　").replace(HT, u"　　　")
                if BO.search(masked): continue
                prows.append((os.path.basename(f), i, w, k - len(w), ln))
sys.stdout.write("paper_claim_without_bo=%d papers=%d\n"
                 % (len(prows), len(set(r[0] for r in prows))))

# ---- 便側 ----
ME = u"ashigaru-third-3"
SRC = []
for p in (u"queue/inbox/karo*.yaml", u"queue/inbox/_archive/karo*.yaml",
          u"queue/inbox/archive/karo*.yaml", u"queue/archive/*.yaml"):
    SRC.extend(sorted(glob.glob(p)))
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
letters = {}
for f in SRC:
    t = io.open(f, encoding="utf-8", errors="replace").read()
    for raw in re.split(u"(?m)^- ", t)[1:]:
        d = parse_block(u"  " + raw)
        if d.get(u"from", u"").strip() != ME: continue
        i = d.get(u"id", u"").strip()
        c = d.get(u"content", u"")
        if i and (i not in letters or len(c) > len(letters[i])):
            letters[i] = c
sys.stdout.write("letters=%d\n" % len(letters))

# ---- 突合: 空白と飾りを除いた 24 字窓 ----
DROP = re.compile(u"[\\s★☆・、。「」『』()（）\\\\]")
def norm(s): return DROP.sub(u"", s)
NL = dict((i, norm(c)) for i, c in letters.items())
W = 12
hit = []; miss = 0
for (fn, ln_no, w, pos, ln) in prows:
    key = norm(ln[max(0, pos - W): pos + len(w) + W])
    if len(key) < 10:
        miss += 1; continue
    got = [i for i in NL if key in NL[i]]
    if got: hit.append((fn, ln_no, w, sorted(got)[0], len(got), ln.strip()))
    else: miss += 1
sys.stdout.write("carried_in_letter=%d not_carried=%d window=%d\n" % (len(hit), miss, W))
for h in hit:
    sys.stdout.write("CARRIED\t%s:%d\t%s\t%s\tn=%d\t%s\n"
                     % (h[0], h[1], h[2].encode("utf-8"), h[3], h[4], h[5][:200].encode("utf-8")))
