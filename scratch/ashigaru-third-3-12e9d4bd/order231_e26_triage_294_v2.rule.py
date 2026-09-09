# -*- coding: utf-8 -*-
"""order231 / E26 v2 ★窓を広げて検出力が立つか★（走 0・讀取のみ・製品走 0）

v1 の答 = ★一行窓では 陽性対照 12 行の当たり 0（徴 0 が 12）★。
v2 = ★同じ徴の定めの儘、窓だけを広げる★（器を一字も変へずに二度測れ ―― 條 o174 の逆向き適用: ★窓のみ動かす★）。
"""
import io, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = HERE
OUTP = os.path.join(HERE, "order231_e26_triage_294_v2.raw.txt")
LOT = set(["order226_e21_zero_by_instrument_v1.md", "order227_e22_loop_in_caller_v1.md"])
KEY = "\u6e2c\u5b9a\u4e0d\u80fd"
A = "\u32d0"; B = "\u32d1"; C = "\u32d2"; DD = "\u32d3"

SIGN_WORD = ["\u689d", "\u5e8a\u2470", "\u578b 8 \u9805", "\u4e09\u629e\u8a9e", "\u968a\u306e\u6761", "\u4f5c\u6cd5", "\u51e1\u4f8b"]
SIGN_A = ["\u539f\u7406", "\u5c4a\u304b\u306c", "\u4f5c\u3064\u3066\u3082", "\u53ca\u3070\u306c", "\u5b57\u3060\u3051\u3067\u306f", "\u624b\u306e\u5c4a\u304b\u306c", "\u5224\u3058\u5f97\u306c"]
SIGN_B = ["\u8d70\u884c 0", "\u8d70\u884c\u3092\u8981", "\u8d70\u3089\u305b\u3066\u5c45\u3089\u306c", "\u7981", "\u8ae4\u308b", "\u5e8a\u306b\u4f9d\u308a", "\u8b80\u53d6\u306e\u307f", "\u8d70 1 \u8981"]
SIGN_C = ["\u672a\u3060", "\u4f5c\u308c\u3070", "\u5668\u3092\u4f5c", "\u5e83\u3052\u308c\u3070", "\u76f4\u305b\u3070", "\u8a66\u3057\u3066\u5c45\u3089\u306c", "\u6e2c\u3064\u3066\u5c45\u3089\u306c", "\u5206\u3051\u3089\u308c\u3066\u5c45\u3089\u306c", "\u6570\u3078\u3066\u5c45\u3089\u306c", "\u5668\u306e\u75b5", "\u7f6e\u304b\u308c\u3066\u5c45\u3089\u306c"]
SIGN_D = ["\u66f8\u304d\u65b9", "\u8a18\u6cd5", "\u66f8\u6dfb\u3078", "\u6a39\u3092\u66f8", "\u6307\u793a\u8a9e", "\u7565\u53f7"]

def signs_of(s):
    r = []
    if any(w in s for w in SIGN_WORD): r.append("\u6587\u8a00")
    if any(w in s for w in SIGN_A): r.append(A)
    if any(w in s for w in SIGN_B): r.append(B)
    if any(w in s for w in SIGN_C): r.append(C)
    if any(w in s for w in SIGN_D): r.append(DD)
    return r

OUT = []
def say(s): OUT.append(s)

names = sorted([f for f in os.listdir(D) if f.endswith(".md")])
docs = {}
for f in names:
    docs[f] = io.open(os.path.join(D, f), encoding="utf-8").read().split(chr(10))

rows = []
for f in names:
    for i, ln in enumerate(docs[f], 1):
        if KEY in ln:
            rows.append((f, i))

say("=== order231 / E26 v2 \u7a93\u3092\u5e83\u3052\u308b ===")
say("\u6bcd = *.md " + str(len(names)) + " \u679a / \u5f53\u305f\u308a\u884c = " + str(len(rows)))
lot = [r for r in rows if r[0] in LOT]
oth = [r for r in rows if r[0] not in LOT]
say("\u672c lot = " + str(len(lot)) + " / \u305d\u306e\u5916 = " + str(len(oth)))
say("")

KNOWN = {
    ("order226_e21_zero_by_instrument_v1.md", 23): A,
    ("order226_e21_zero_by_instrument_v1.md", 132): C,
    ("order226_e21_zero_by_instrument_v1.md", 144): C,
    ("order226_e21_zero_by_instrument_v1.md", 146): C,
    ("order226_e21_zero_by_instrument_v1.md", 151): "\u6587\u8a00",
    ("order226_e21_zero_by_instrument_v1.md", 193): C,
    ("order226_e21_zero_by_instrument_v1.md", 194): C,
    ("order226_e21_zero_by_instrument_v1.md", 195): C,
    ("order227_e22_loop_in_caller_v1.md", 119): C,
    ("order227_e22_loop_in_caller_v1.md", 129): "\u6587\u8a00",
    ("order227_e22_loop_in_caller_v1.md", 176): C,
    ("order227_e22_loop_in_caller_v1.md", 179): C,
}

def window(f, i, n):
    ls = docs[f]
    a = max(0, i - 1 - n); b = min(len(ls), i + n)
    return chr(10).join(ls[a:b])

# ---- §一 窓の幅ごとの検出力（陽性対照 12 行）----
say("--- \u00a7\u4e00 \u7a93\u306e\u5e45\u3054\u3068\u306e\u691c\u51fa\u529b\uff08\u967d\u6027\u5bfe\u7167 12 \u884c\uff09 ---")
say("  \u5e45 | \u5f53\u305f\u308a | \u5f81 0 | \u9055 | \u5f81\u304c 2 \u4ee5\u4e0a")
for n in [0, 1, 2, 3, 5, 8]:
    hit = 0; zero = 0; wrong = 0; multi = 0
    for f, i in lot:
        g = signs_of(window(f, i, n))
        w = KNOWN[(f, i)]
        if not g: zero += 1
        elif w in g:
            hit += 1
            if len(g) > 1: multi += 1
        else: wrong += 1
    say("  " + str(n).rjust(2) + " | " + str(hit).rjust(6) + " | " + str(zero).rjust(4)
        + " | " + str(wrong).rjust(2) + " | " + str(multi).rjust(6))
say("")

# ---- §二 陰性対照 = 徴が「無い方へ」倒れるか ----
say("--- \u00a7\u4e8c \u967d\u6027\u5bfe\u7167 12 \u884c\u306e\u5185\u8a33\uff08\u5e45 3\uff09 ---")
for f, i in lot:
    g = signs_of(window(f, i, 3))
    say("  " + f[:34] + ":" + str(i).rjust(3) + " want=" + KNOWN[(f, i)]
        + " got=" + ("+".join(g) if g else "(0)"))
say("")

# ---- §三 母へ当てる（幅 3）----
say("--- \u00a7\u4e09 \u6bcd " + str(len(oth)) + " \u884c\u3078\u5f53\u3066\u308b\uff08\u5e45 3\uff09 ---")
cnt = collections.Counter()
for f, i in oth:
    g = signs_of(window(f, i, 3))
    cnt["+".join(g) if g else "(\u5f81 0)"] += 1
for k, v in cnt.most_common():
    say("  " + k + " = " + str(v))
say("")

say("--- \u00a7\u56db \u5668\u306e\u9650 ---")
say("  \u7a93\u3092\u5e83\u3052\u308b\u3068 \u5f81\u304c\u91cd\u306a\u308b \u2015\u2015 \u5f53\u305f\u308a\u304c\u5897\u3078\u3066\u3082 ★\u4e00\u3064\u306b\u7d5e\u308c\u306c★\u3002")
say("  \u672c\u5668\u306f ★\u65ad\u5b9a\u305b\u306c★\u3002\u4eba\u304c\u8aad\u3080\u6b04\u3092\u6b8b\u3059\u3002")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(OUT) + chr(10))
print(chr(10).join(OUT))
