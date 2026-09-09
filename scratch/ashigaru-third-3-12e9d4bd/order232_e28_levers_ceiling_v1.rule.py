# -*- coding: utf-8 -*-
"""order232 / E28 ★三梃子の天井を測る★（走 0・讀取のみ・製品走 0）

\u4ee4 = \u300c\u4e09\u5206\u304c\u6210\u3089\u306c\u306a\u3089 \u4f55\u3092\u8db3\u305b\u3070\u6210\u308b\u304b\u300d
  \u2460\u8a9e\u5f59\u3092\u8db3\u3059 \u2461\u7a93\u3092\u5e83\u3052\u308b \u2462\u5225\u306e\u5fb4
\u2015\u2015 ★\u898b\u8fbc\u307f\u3067\u66f8\u304b\u305a \u5929\u4e95\u3092\u6e2c\u308b★\u3002
"""
import io, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = HERE
OUTP = os.path.join(HERE, "order232_e28_levers_ceiling_v1.raw.txt")
LOT = set(["order226_e21_zero_by_instrument_v1.md", "order227_e22_loop_in_caller_v1.md"])
KEY = "\u6e2c\u5b9a\u4e0d\u80fd"
A = "\u32d0"; B = "\u32d1"; C = "\u32d2"; DD = "\u32d3"; W = "\u6587\u8a00"

V2 = {
 W:  ["\u689d", "\u5e8a\u2470", "\u578b 8 \u9805", "\u4e09\u629e\u8a9e", "\u968a\u306e\u6761", "\u4f5c\u6cd5", "\u51e1\u4f8b"],
 A:  ["\u539f\u7406", "\u5c4a\u304b\u306c", "\u4f5c\u3064\u3066\u3082", "\u53ca\u3070\u306c", "\u5b57\u3060\u3051\u3067\u306f", "\u624b\u306e\u5c4a\u304b\u306c", "\u5224\u3058\u5f97\u306c"],
 B:  ["\u8d70\u884c 0", "\u8d70\u884c\u3092\u8981", "\u8d70\u3089\u305b\u3066\u5c45\u3089\u306c", "\u7981", "\u8ae4\u308b", "\u5e8a\u306b\u4f9d\u308a", "\u8b80\u53d6\u306e\u307f", "\u8d70 1 \u8981"],
 C:  ["\u672a\u3060", "\u4f5c\u308c\u3070", "\u5668\u3092\u4f5c", "\u5e83\u3052\u308c\u3070", "\u76f4\u305b\u3070", "\u8a66\u3057\u3066\u5c45\u3089\u306c", "\u6e2c\u3064\u3066\u5c45\u3089\u306c", "\u5206\u3051\u3089\u308c\u3066\u5c45\u3089\u306c", "\u6570\u3078\u3066\u5c45\u3089\u306c", "\u5668\u306e\u75b5", "\u7f6e\u304b\u308c\u3066\u5c45\u3089\u306c"],
 DD: ["\u66f8\u304d\u65b9", "\u8a18\u6cd5", "\u66f8\u6dfb\u3078", "\u6a39\u3092\u66f8", "\u6307\u793a\u8a9e", "\u7565\u53f7"],
}
ORDER = [W, A, B, C, DD]
def signs(s):
    return [k for k in ORDER if any(w in s for w in V2[k])]

OUT = []
def say(s): OUT.append(s)

names = sorted([f for f in os.listdir(D) if f.endswith(".md")])
docs = dict((f, io.open(os.path.join(D, f), encoding="utf-8").read().split(chr(10))) for f in names)
rows = [(f, i) for f in names for i, ln in enumerate(docs[f], 1) if KEY in ln]
oth = [r for r in rows if r[0] not in LOT]
def win(f, i, n):
    ls = docs[f]; return chr(10).join(ls[max(0, i - 1 - n):min(len(ls), i + n)])

say("=== order232 / E28 \u4e09\u68c3\u5b50\u306e\u5929\u4e95 ===")
say("\u6bcd = *.md " + str(len(names)) + " \u679a / \u5f53\u305f\u308a = " + str(len(rows))
    + " / \u672c lot \u306e\u5916 = " + str(len(oth)))
say("")

# ---- \u2461 \u7a93\u306e\u5929\u4e95 ----
say("--- \u00a7\u4e00 \u2461\u7a93\u3092\u5e83\u3052\u308b \u306e\u5929\u4e95\uff08\u6bcd " + str(len(oth)) + " \u884c\uff09 ---")
say("  \u5e45 | \u5fb4 0 | 1 \u3064(\u7d5e\u308c\u305f) | \u591a\u5fb4 | \u7d5e\u308c\u305f\u5272")
prev = None
for n in [0, 1, 2, 3, 5, 8, 12, 20]:
    z = one = mul = 0
    for f, i in oth:
        g = signs(win(f, i, n))
        if not g: z += 1
        elif len(g) == 1: one += 1
        else: mul += 1
    say("  " + str(n).rjust(2) + " | " + str(z).rjust(5) + " | " + str(one).rjust(11)
        + " | " + str(mul).rjust(5) + " | " + ("%.1f%%" % (100.0 * one / len(oth))))
say("  \u2192 \u7d5e\u308c\u305f\u6570\u306e ★\u5cf0★ \u304c\u7a93\u306e\u5929\u4e95\u3067\u3042\u308b\u3002")
say("")

# ---- \u2460 \u8a9e\u5f59\u306e\u5929\u4e95 ----
say("--- \u00a7\u4e8c \u2460\u8a9e\u5f59\u3092\u8db3\u3059 \u306e\u5929\u4e95 ---")
z3 = [(f, i) for f, i in oth if not signs(win(f, i, 3))]
say("  \u7a93 3 \u3067 \u5fb4 0 = " + str(len(z3)) + " \u884c")
say("  \u5185 \u7d19\u306e\u6570 = " + str(len(set(f for f, i in z3))) + " \u679a")
# \u540c\u3058\u6587\u304c\u4f55\u5ea6\u51fa\u308b\u304b\uff08\u91cd\u8907\u5ea6\uff09
txt = collections.Counter(docs[f][i - 1].strip() for f, i in z3)
say("  \u7570\u306a\u308b\u6587 = " + str(len(txt)) + " / \u5ef6\u3079 " + str(len(z3)))
top = txt.most_common(12)
say("  \u203b \u6700\u3082\u591a\u304f\u51fa\u308b\u6587 12\uff08\u56de\u6570 | \u9010\u8a9e\uff09:")
cum = 0
for s, c in top:
    cum += c
    say("    " + str(c).rjust(3) + " | " + s[:96])
say("  \u2192 \u4e0a\u4f4d 12 \u6587\u3067 " + str(cum) + " \u884c ("
    + ("%.1f%%" % (100.0 * cum / len(z3))) + ") \u3092\u899b\u3075")
# 2 \u56de\u4ee5\u4e0a\u51fa\u308b\u6587\u306e\u5408\u8a08
rep = sum(c for s, c in txt.items() if c >= 2)
say("  \u2192 2 \u56de\u4ee5\u4e0a\u51fa\u308b\u6587 = " + str(rep) + " \u884c ("
    + ("%.1f%%" % (100.0 * rep / len(z3))) + ")  / 1 \u56de\u9650\u308a = " + str(len(z3) - rep) + " \u884c")
say("")

# ---- \u2462 \u5225\u306e\u5fb4\u306e\u5929\u4e95 ----
say("--- \u00a7\u4e09 \u2462\u5225\u306e\u5fb4 \u306e\u5929\u4e95 ---")
def home(line):
    t = line.strip()
    if t.startswith("#"): return "\u898b\u51fa\u3057"
    if t.startswith(">"): return "\u5f15\u7528"
    if t.startswith("|"): return "\u8868"
    if t.startswith("-") or t.startswith("*") or re.match(r"^[0-9]+[.)]", t): return "\u7b87\u6761"
    if t.startswith("`") or t.startswith("    "): return "\u5668\u306e\u5e2f"
    return "\u5730\u306e\u6587"
say("  \u5fb4-a \u68f2\u5bb6 : \u5fb4 0 \u884c " + str(len(z3)) + " \u306e\u5185\u8a33")
hc = collections.Counter(home(docs[f][i - 1]) for f, i in z3)
for k, v in hc.most_common():
    say("    " + k + " = " + str(v))
# \u5fb4-b : \u76f4\u524d 8 \u5b57
say("  \u5fb4-b \u76f4\u524d\u306e\u5f62\uff08\u300c\u6e2c\u5b9a\u4e0d\u80fd\u300d\u306e\u524d 8 \u5b57\u30fb\u4e0a\u4f4d 10\uff09:")
pre = collections.Counter()
for f, i in z3:
    ln = docs[f][i - 1]
    k = ln.find(KEY)
    pre[ln[max(0, k - 8):k].strip()] += 1
c2 = 0
for s, c in pre.most_common(10):
    c2 += c
    say("    " + str(c).rjust(3) + " | " + repr(s)[1:])
say("    \u2192 \u4e0a\u4f4d 10 \u5f62\u3067 " + str(c2) + " \u884c ("
    + ("%.1f%%" % (100.0 * c2 / len(z3))) + ")")
say("  \u5fb4-c \u7d19\u306e\u5e2f\uff08order \u756a\u53f7\u5e2f\u30fb\u5fb4 0 \u884c\uff09:")
band = collections.Counter()
for f, i in z3:
    m = re.match(r"^order([0-9]+)", f)
    band[("order" + m.group(1)[:-1] + "x") if m else "\u975e order"] += 1
for k, v in band.most_common(8):
    say("    " + k + " = " + str(v))
say("")

# ---- \u5834\u5408\u306e\u5206\u3051 ----
say("--- \u00a7\u56db \u5929\u4e95\u306e\u307e\u3068\u3081\uff08\u6570\u306e\u307f\uff09 ---")
best = None
for n in [0, 1, 2, 3, 5, 8, 12, 20]:
    one = sum(1 for f, i in oth if len(signs(win(f, i, n))) == 1)
    if best is None or one > best[1]: best = (n, one)
say("  \u2461\u7a93 : \u5cf0 = \u5e45 " + str(best[0]) + " \u3067 \u7d5e\u308c\u305f " + str(best[1])
    + " / " + str(len(oth)) + " (" + ("%.1f%%" % (100.0 * best[1] / len(oth))) + ")")
say("  \u2460\u8a9e\u5f59 : \u5fb4 0 " + str(len(z3)) + " \u884c \u306e\u5185 2 \u56de\u4ee5\u4e0a\u51fa\u308b\u6587 = "
    + str(rep) + " \u884c \u2190 ★\u5c11\u306a\u3044\u8a9e\u3067\u591a\u304f\u899b\u3078\u308b\u9650★")
say("  \u2462\u5225\u306e\u5fb4 : \u76f4\u524d 8 \u5b57\u306e\u4e0a\u4f4d 10 \u5f62 = " + str(c2) + " \u884c")
say("")
say("--- \u00a7\u4e94 \u5668\u306e\u9650 ---")
say("  \u672c\u5668\u306f ★\u5929\u4e95\u3092\u6e2c\u308b\u306e\u307f★\u3002\u5929\u4e95\u306b\u5c4a\u3044\u305f\u6642 ★\u6b63\u3057\u304f\u5206\u3051\u3089\u308c\u308b\u304b★ \u306f\u5225\u306e\u554f\u3067\u3042\u308b\u3002")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(OUT) + chr(10))
print(chr(10).join(OUT))
