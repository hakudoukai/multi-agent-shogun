# -*- coding: utf-8 -*-
# order237 E33 v2: same as v1 but with 母(BO) and 己の行(ACT) vocabularies WIDENED.
# widened after hand-labelling 29 live cases showed the v1 net missed
#   kanji numerals / 箇所 / bare N / N->M arrows / table columns  (母 present but unseen)
#   and self-act verbs 算じ / 取つ / 見て / 試し / 測ら / 當て直 / 使つ / 出して (self-report, not a claim)
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections
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
files = sorted(glob.glob(os.path.join(D, u"*.md")))
cnt = collections.Counter(); mi_net = 0; rows = []
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
                selfact = bool(ACT.match(ln[k:k+6].strip()))
                bo = bool(BO.search(ln)); am = bool(AMI.search(ln))
                kind = u"selfact" if selfact else u"claim"
                cnt[(w, kind, u"bo=%d" % bo, u"ami=%d" % am)] += 1
                if kind == u"claim" and not bo:
                    rows.append((os.path.basename(f), i, w))
print(u"md=%d  mina_standalone=%d" % (len(files), mi_net))
for k in sorted([x for x in cnt if isinstance(x, tuple)]):
    print(u"%s %-7s %-5s %-6s %5d" % (k[0], k[1], k[2], k[3], cnt[k]))
for k in (u"skip_quote", u"skip_jyo"):
    print(u"%-10s %5d" % (k, cnt[k]))
print(u"claim_without_bo=%d files=%d" % (len(rows), len(set(r[0] for r in rows))))
