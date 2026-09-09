# -*- coding: utf-8 -*-
"""order231 / E26 v3 ★語彙の効き と 窓の効き を分ける交叉表★（走 0）

v1\u2192v2 \u3067 \u2460\u8a9e\u5f59\u3092\u5e83\u3052 \u2461\u7a93\u3092\u5e83\u3052 \u306e\u4e8c\u3064\u3092 ★\u540c\u6642\u306b\u52d5\u304b\u3057\u305f★\u3002
\u21d2 2x2 \u306e\u4ea4\u53c9\u8868\u3067 \u5225\u3005\u306e\u52b9\u304d\u3092\u51fa\u3059\uff08\u689d o174 \u306e\u9075\u5b88\uff09\u3002
"""
import io, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = HERE
OUTP = os.path.join(HERE, "order231_e26_triage_294_v3.raw.txt")
LOT = ["order226_e21_zero_by_instrument_v1.md", "order227_e22_loop_in_caller_v1.md"]
KEY = "\u6e2c\u5b9a\u4e0d\u80fd"
A = "\u32d0"; B = "\u32d1"; C = "\u32d2"; DD = "\u32d3"; W = "\u6587\u8a00"

# --- \u8a9e\u5f59 \u72ed = v1 ---
V1 = {
 W:  ["\u689d", "\u5e8a", "\u578b 8 \u9805", "\u4e09\u629e\u8a9e", "\u968a\u306e\u6761", "\u4f5c\u6cd5"],
 A:  ["uid", "\u539f\u7406", "\u5c4a\u304b\u306c", "\u4f5c\u3064\u3066\u3082", "\u53ca\u3070\u306c"],
 B:  ["\u8d70 1", "\u8d70\u884c", "\u7981", "\u8ae4\u308b", "\u88c1\u3092\u8981", "\u5e8a\u306b\u4f9d\u308a"],
 C:  ["\u672a\u3060", "\u4f5c\u308c\u3070", "\u5668\u3092\u4f5c", "\u5e83\u3052\u308c\u3070", "\u76f4\u305b\u3070"],
 DD: ["\u66f8\u304d\u65b9", "\u8a18\u6cd5", "\u66f8\u6dfb\u3078", "\u6a39\u3092\u66f8"],
}
# --- \u8a9e\u5f59 \u5e83 = v2 ---
V2 = {
 W:  ["\u689d", "\u5e8a\u2470", "\u578b 8 \u9805", "\u4e09\u629e\u8a9e", "\u968a\u306e\u6761", "\u4f5c\u6cd5", "\u51e1\u4f8b"],
 A:  ["\u539f\u7406", "\u5c4a\u304b\u306c", "\u4f5c\u3064\u3066\u3082", "\u53ca\u3070\u306c", "\u5b57\u3060\u3051\u3067\u306f", "\u624b\u306e\u5c4a\u304b\u306c", "\u5224\u3058\u5f97\u306c"],
 B:  ["\u8d70\u884c 0", "\u8d70\u884c\u3092\u8981", "\u8d70\u3089\u305b\u3066\u5c45\u3089\u306c", "\u7981", "\u8ae4\u308b", "\u5e8a\u306b\u4f9d\u308a", "\u8b80\u53d6\u306e\u307f", "\u8d70 1 \u8981"],
 C:  ["\u672a\u3060", "\u4f5c\u308c\u3070", "\u5668\u3092\u4f5c", "\u5e83\u3052\u308c\u3070", "\u76f4\u305b\u3070", "\u8a66\u3057\u3066\u5c45\u3089\u306c", "\u6e2c\u3064\u3066\u5c45\u3089\u306c", "\u5206\u3051\u3089\u308c\u3066\u5c45\u3089\u306c", "\u6570\u3078\u3066\u5c45\u3089\u306c", "\u5668\u306e\u75b5", "\u7f6e\u304b\u308c\u3066\u5c45\u3089\u306c"],
 DD: ["\u66f8\u304d\u65b9", "\u8a18\u6cd5", "\u66f8\u6dfb\u3078", "\u6a39\u3092\u66f8", "\u6307\u793a\u8a9e", "\u7565\u53f7"],
}
ORDER = [W, A, B, C, DD]

def signs(voc, s):
    return [k for k in ORDER if any(w in s for w in voc[k])]

OUT = []
def say(s): OUT.append(s)

names = sorted([f for f in os.listdir(D) if f.endswith(".md")])
docs = dict((f, io.open(os.path.join(D, f), encoding="utf-8").read().split(chr(10))) for f in names)
rows = [(f, i) for f in names for i, ln in enumerate(docs[f], 1) if KEY in ln]
lot = [r for r in rows if r[0] in LOT]
oth = [r for r in rows if r[0] not in LOT]

KNOWN = {
 (LOT[0], 23): A, (LOT[0], 132): C, (LOT[0], 144): C, (LOT[0], 146): C,
 (LOT[0], 151): W, (LOT[0], 193): C, (LOT[0], 194): C, (LOT[0], 195): C,
 (LOT[1], 119): C, (LOT[1], 129): W, (LOT[1], 176): C, (LOT[1], 179): C,
}

def win(f, i, n):
    ls = docs[f]; return chr(10).join(ls[max(0, i - 1 - n):min(len(ls), i + n)])

say("=== order231 / E26 v3 \u4ea4\u53c9\u8868 ===")
say("\u6bcd = *.md " + str(len(names)) + " \u679a / \u5f53\u305f\u308a\u884c = " + str(len(rows))
    + " / \u672c lot = " + str(len(lot)) + " / \u305d\u306e\u5916 = " + str(len(oth)))
say("")
say("--- \u00a7\u4e00 2x2 \u4ea4\u53c9\uff08\u967d\u6027\u5bfe\u7167 12 \u884c\u30fb\u5f53\u305f\u308a\u6570\uff09 ---")
say("  \u8a9e\u5f59\\\u7a93 |  0 |  3 | \u5dee(\u7a93)")
for nm, voc in [("\u72ed(v1)", V1), ("\u5e83(v2)", V2)]:
    r = []
    for n in [0, 3]:
        r.append(sum(1 for f, i in lot if KNOWN[(f, i)] in signs(voc, win(f, i, n))))
    say("  " + nm + "  | " + str(r[0]).rjust(2) + " | " + str(r[1]).rjust(2) + " | +" + str(r[1] - r[0]))
c00 = sum(1 for f, i in lot if KNOWN[(f, i)] in signs(V1, win(f, i, 0)))
c10 = sum(1 for f, i in lot if KNOWN[(f, i)] in signs(V2, win(f, i, 0)))
say("  \u5dee(\u8a9e\u5f59\u30fb\u7a93 0) = +" + str(c10 - c00))
say("")
say("--- \u00a7\u4e8c \u591a\u5f81\uff08\u4e00\u3064\u306b\u7d5e\u308c\u306c\u884c\uff09 ---")
for nm, voc in [("\u72ed(v1)", V1), ("\u5e83(v2)", V2)]:
    for n in [0, 3]:
        m = sum(1 for f, i in lot if len(signs(voc, win(f, i, n))) > 1)
        say("  " + nm + " \u7a93" + str(n) + " : \u5f81\u304c 2 \u4ee5\u4e0a = " + str(m) + " / 12")
say("")
say("--- \u00a7\u4e09 \u6bcd " + str(len(oth)) + " \u884c \u306e \u5f81\u306e\u6570\uff08\u5e83(v2)\u30fb\u7a93 3\uff09 ---")
d = collections.Counter()
for f, i in oth:
    d[len(signs(V2, win(f, i, 3)))] += 1
for k in sorted(d):
    say("  \u5f81 " + str(k) + " \u3064 = " + str(d[k]))
say("")
say("--- \u00a7\u56db \u5668\u306e\u9650 ---")
say("  \u4ea4\u53c9\u8868\u306f ★\u5f53\u305f\u308a\u6570★ \u306e\u307f\u3092\u5206\u3051\u308b\u3002\u591a\u5f81\u884c\u306f ★\u4e00\u3064\u306b\u7d5e\u308c\u3066\u5c45\u3089\u306c★\u3002")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(OUT) + chr(10))
print(chr(10).join(OUT))
