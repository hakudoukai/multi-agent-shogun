# -*- coding: utf-8 -*-
# order237 E33: sweep 悉く / 皆 / 一つも over my own papers and ask,
# for each occurrence, whether 母 (denominator) and 網 (net shape) sit on the SAME line.
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
KO = u"悉く"      # kotogotoku
MI = u"皆"            # mina
SK = u"悉皆"      # shikkai (contains MI)
HT = u"一つも"  # hitotsumo
JYO = re.compile(u"(條|条\\(|隊の条|家老 條|新條)")
# BO = denominator on the same line: N/M, n=N, "N 件/行/枚/本/族/窓", "母 N"
BO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|[0-9][0-9,]*\\s*(件|行|枚|本|族|窓|個)|母\\s*[0-9])")
# AMI = net named on the same line
AMI = re.compile(u"(網|窓|錨|ast|grep|glob|正規表現|pattern|悉皆|門|pin|blob|器)")
# self-act negation: 己の行の否定 (floor compliance), not a population claim
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|動し|書き換|数へ|用ゐ|打つ|打ち|送つ)")
files = sorted(glob.glob(os.path.join(D, u"*.md")))
cnt = collections.Counter()
mi_net = 0
rows = []
for f in files:
    t = io.open(f, encoding="utf-8").read()
    mi_net += t.count(MI) - t.count(SK)
    for i, ln in enumerate(t.split(chr(10)), 1):
        if ln.lstrip().startswith(u">"):
            cnt[u"skip_quote"] += ln.count(KO) + ln.count(HT); continue
        if JYO.search(ln):
            cnt[u"skip_jyo"] += ln.count(KO) + ln.count(HT); continue
        for w in (KO, HT):
            k = 0
            while True:
                k = ln.find(w, k)
                if k < 0: break
                k += len(w)
                tail = ln[k:k+6].strip()
                selfact = bool(ACT.match(tail))
                bo = bool(BO.search(ln)); am = bool(AMI.search(ln))
                kind = u"selfact" if selfact else u"claim"
                cnt[(w, kind, u"bo=%d" % bo, u"ami=%d" % am)] += 1
                if kind == u"claim" and not bo:
                    rows.append((os.path.basename(f), i, w, ln.strip()[:90]))
print(u"md=%d  mina_standalone=%d (all %s are inside %s)" % (len(files), mi_net, MI, SK))
for k in sorted([x for x in cnt if isinstance(x, tuple)]):
    print(u"%s %-7s %-5s %-6s %5d" % (k[0], k[1], k[2], k[3], cnt[k]))
for k in (u"skip_quote", u"skip_jyo"):
    print(u"%-10s %5d" % (k, cnt[k]))
print(u"claim_without_bo=%d files=%d" % (len(rows), len(set(r[0] for r in rows))))
