# -*- coding: utf-8 -*-
# order238 E34: collect every letter I sent to 家老 (from: ashigaru-third-3) across the live box
# and the archives, then ask which of them carry 悉く / 一つも as a CLAIM WITHOUT a denominator.
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections
KO = u"悉く"; MI = u"皆"; SK = u"悉皆"; HT = u"一つも"
UNIT = u"(件|行|枚|本|族|窓|個|箇所|回|語|字|所|つ)"; KAN = u"[一二三四五六七八九十]+"
BO = re.compile(u"([0-9][0-9,]*\\s*/\\s*[0-9]|n\\s*=\\s*[0-9]|[0-9][0-9,]*\\s*" + UNIT +
                u"|母\\s*[0-9]|[0-9][0-9,]*\\s*(→|->)\\s*[0-9]|" + KAN + UNIT + u"|\\|\\s*[0-9][0-9,]*\\s*\\|)")
AMI = re.compile(u"(網|窓|錨|ast|grep|glob|正規表現|pattern|悉皆|門|pin|blob|器)")
ACT = re.compile(u"^(写し|書い|書か|作つ|作ら|作っ|触れ|消し|動か|書き換|数へ|用ゐ|打つ|打ち|送つ"
                 u"|算じ|取つ|見て|試し|測ら|測つ|當て直|当て直|使つ|出して|置い|讀ま|読ま|讀んで)")
SRC = []
for pat in (u"queue/inbox/karo-third.yaml", u"queue/inbox/_archive/*.yaml",
            u"queue/inbox/archive/*.yaml", u"queue/archive/*.yaml"):
    SRC.extend(sorted(glob.glob(pat)))
seen = {}          # msg id -> (src, content)
for f in SRC:
    try:
        t = io.open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for blk in re.split(r"(?m)^- (?=id: )", t):
        if u"from: ashigaru-third-3" not in blk:
            continue
        m = re.match(r"id: (\S+)", blk)
        if not m:
            continue
        i = m.group(1)
        c = re.search(r"(?s)content: (.*?)(?:\n  [a-z_]+: |\Z)", blk)
        body = c.group(1) if c else u""
        if i not in seen or len(body) > len(seen[i][1]):
            seen[i] = (os.path.basename(f), body)
print(u"src_files=%d  distinct_letters=%d" % (len(SRC), len(seen)))
mi_raw = sum(v[1].count(MI) for v in seen.values())
sk_raw = sum(v[1].count(SK) for v in seen.values())
print(u"%s_raw=%d  %s_raw=%d  %s_standalone=%d" % (MI, mi_raw, SK, sk_raw, MI, mi_raw - sk_raw))
cnt = collections.Counter(); rows = []
for i, (src, body) in sorted(seen.items()):
    one = body.replace(chr(10), u" ")
    for w in (KO, HT):
        k = 0
        while True:
            k = one.find(w, k)
            if k < 0: break
            k += len(w)
            selfact = bool(ACT.match(one[k:k+6].strip()))
            masked = one.replace(KO, u"　　").replace(HT, u"　　　")
            bo = bool(BO.search(masked)); am = bool(AMI.search(one))
            kind = u"selfact" if selfact else u"claim"
            cnt[(w, kind, u"bo=%d" % bo)] += 1
            if kind == u"claim" and not bo:
                rows.append((i, src, w, one.strip()[:150]))
for k in sorted([x for x in cnt]):
    print(u"%s %-7s %-5s %4d" % (k[0], k[1], k[2], cnt[k]))
print(u"claim_without_bo=%d  letters=%d" % (len(rows), len(set(r[0] for r in rows))))
print(u"---- the letters ----")
for n, (i, src, w, s) in enumerate(rows, 1):
    print(u"#%02d %s [%s] %s" % (n, i, w, s))
