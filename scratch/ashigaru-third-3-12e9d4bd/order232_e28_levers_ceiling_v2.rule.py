# -*- coding: utf-8 -*-
"""order232 / E28 v2 ★\u2460\u8a9e\u5f59\u306e\u5929\u4e95\u3092 \u6587\u3067\u306a\u304f ★\u53e5★ \u3067\u6e2c\u308a\u76f4\u3059★

v1 \u306e\u75b5 = \u8a9e\u5f59\u306e\u5929\u4e95\u3092 ★\u6587\u5168\u4f53\u306e\u91cd\u8907★ \u3067\u6e2c\u3064\u305f\u3002
\u2192 \u6587\u306f 738/756 \u304c\u4e00\u56de\u9650\u308a \u2234 \u300c\u8a9e\u5f59\u306f\u52b9\u304b\u306c\u300d\u3068\u898b\u3078\u305f\u304c\u3001
   ★\u53e5\u306f\u6587\u3092\u8de8\u3044\u3067\u7e70\u308a\u8fd4\u3055\u308c\u308b★ \u2234 \u5929\u4e95\u306f\u53e5\u3067\u6e2c\u308b\u3079\u304d\u3067\u3042\u3064\u305f\u3002
"""
import io, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = HERE
OUTP = os.path.join(HERE, "order232_e28_levers_ceiling_v2.raw.txt")
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

# ★\u5019\u88dc\u306e\u53e5★ = (\u53e5, \u898b\u8fbc\u307f\u306e\u5225)  \u2015\u2015 \u5df1\u304c\u9078\u3093\u3060\u7269
CAND = [
 ("\u306e\u307f\u3067\u306f", B),                       # のみでは
 ("\u672a\u6e2c", C),                                     # 未測
 ("\u4e0a\u9650\u304c\u6e2c\u308c\u306c", A),         # 上限が測れぬ
 ("\u5024\u304c\u6e2c\u308c\u306c", A),                # 値が測れぬ
 ("\u5668\u306e\u5916", A),                              # 器の外
 ("\u672c\u675f\u306e\u5916", A),                       # 本束の外
 ("\u6301\u305f\u306c", A),                              # 持たぬ
 ("\u73fe\u306b\u7121\u3044", C),                       # 現に無い
 ("\u5f53\u3064\u3066\u5c45\u3089\u306c", C),         # 当つて居らぬ
 ("\u898b\u3066\u5c45\u3089\u306c", C),                # 見て居らぬ
 ("\u53d6\u3064\u3066\u5c45\u3089\u306c", C),         # 取つて居らぬ
 ("\u66f8\u3044\u3066\u5c45\u3089\u306c", DD),        # 書いて居らぬ
 ("\u304b\u5426\u304b", None),                           # か否か（別を指さぬ）
 ("git 0", B),
 ("\u5e8a\u306e\u6025\u5831", B),                       # 床の急報
 ("\u540c\u540d\u306e", C),                              # 同名の
]

OUT = []
def say(s): OUT.append(s)

names = sorted([f for f in os.listdir(D) if f.endswith(".md")])
docs = dict((f, io.open(os.path.join(D, f), encoding="utf-8").read().split(chr(10))) for f in names)
rows = [(f, i) for f in names for i, ln in enumerate(docs[f], 1) if KEY in ln]
oth = [r for r in rows if r[0] not in LOT]
def win(f, i, n):
    ls = docs[f]; return chr(10).join(ls[max(0, i - 1 - n):min(len(ls), i + n)])

say("=== order232 / E28 v2 \u2460\u8a9e\u5f59\u306e\u5929\u4e95\uff08\u53e5\u3067\u6e2c\u308b\uff09 ===")
say("\u6bcd = *.md " + str(len(names)) + " \u679a / \u5f53\u305f\u308a = " + str(len(rows))
    + " / \u672c lot \u306e\u5916 = " + str(len(oth)))

for N, tag in [(3, "\u7a93 3"), (5, "\u7a93 5(\u5cf0)")]:
    z = [(f, i) for f, i in oth if not signs(win(f, i, N))]
    say("")
    say("--- " + tag + " \u3067 \u5fb4 0 = " + str(len(z)) + " \u884c \u3078 \u5019\u88dc\u53e5\u3092\u5f53\u3066\u308b ---")
    wins = dict(((f, i), win(f, i, N)) for f, i in z)
    say("  \u53e5\u5358\u4f53\u306e\u899b\u3072\uff08\u53e5 | \u898b\u8fbc\u307f\u306e\u5225 | \u899b\u3075\u884c\uff09:")
    for ph, kind in CAND:
        c = sum(1 for k in z if ph in wins[k])
        say("    " + ph.ljust(14) + " | " + (kind if kind else "(\u5225\u306a\u3057)")
            + " | " + str(c).rjust(4))
    # \u8caa\u6b32\u306b\u7a4d\u3080
    say("  \u8caa\u6b32\u306b\u7a4d\u3093\u3060\u7d2f\u7a4d\uff08\u53e5\u3092\u4e00\u3064\u305a\u3064\u8db3\u3059\uff09:")
    left = set(z); used = []
    for step in range(1, 9):
        best = None
        for ph, kind in CAND:
            if ph in used: continue
            c = sum(1 for k in left if ph in wins[k])
            if best is None or c > best[1]: best = (ph, c)
        if best is None or best[1] == 0: break
        used.append(best[0])
        left = set(k for k in left if best[0] not in wins[k])
        say("    +" + str(step).rjust(2) + " " + best[0].ljust(14) + " \u65b0\u305f\u306b "
            + str(best[1]).rjust(4) + " \u884c / \u6b8b\u308a " + str(len(left)).rjust(4)
            + " (\u7d2f\u7a4d " + ("%.1f%%" % (100.0 * (len(z) - len(left)) / len(z))) + ")")
    say("  \u2192 \u53e5 " + str(len(used)) + " \u3064\u3067 " + str(len(z) - len(left))
        + " / " + str(len(z)) + " \u884c (" + ("%.1f%%" % (100.0 * (len(z) - len(left)) / len(z))) + ")")
    say("  \u2192 \u6b8b\u308b " + str(len(left)) + " \u884c \u306f \u5019\u88dc 16 \u53e5\u306e\u5916")

say("")
say("--- \u00a7 \u5668\u306e\u9650 ---")
say("  \u5019\u88dc 16 \u53e5\u306f ★\u5df1\u304c\u9078\u3093\u3060\u7269★ \u2015\u2015 \u6a5f\u68b0\u304c\u62fe\u3064\u305f\u7269\u3067\u306f\u7121\u3044\u3002")
say("  \u899b\u3072\u306f ★\u53e5\u304c\u7a93\u306b\u5728\u308b\u304b★ \u306e\u307f\u3092\u6e2c\u308b\u3002★\u6b63\u3057\u3044\u5225\u3092\u6307\u3059\u304b\u306f\u5225\u306e\u554f★\u3067\u3042\u308b\u3002")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(OUT) + chr(10))
print(chr(10).join(OUT))
