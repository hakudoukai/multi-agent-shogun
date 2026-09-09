# -*- coding: utf-8 -*-
"""order231 / E26 ★己の紙の「測定不能」を 徴で当てる★（走 0・讀取のみ・製品走 0）

★的一行★ = 己の紙 307 枚の「測定不能」1,366 行の内、本 lot 12 行の外の ★1,354 行★ が
           {A}(器が及ばぬ) / {B}(床に依り測らぬ) / {C}(未だ器を作らぬ) / {DD}(己の記法の疵) の何れか。

★本器が為す事★ = ★断定ではなく 徴(しるし)を数へる★。人が読む欄を残す。
★検出力を先に測る★ = 本 lot 12 行を ★既知の答★ として当て、徴が現に分かれるかを見る（立条）。
"""
import io, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = HERE
OUTP = os.path.join(HERE, "order231_e26_triage_294_v1.raw.txt")
LOT = set(["order226_e21_zero_by_instrument_v1.md", "order227_e22_loop_in_caller_v1.md"])
KEY = "\u6e2c\u5b9a\u4e0d\u80fd"          # 測定不能
A = "\u32d0"; B = "\u32d1"; C = "\u32d2"; DD = "\u32d3"   # (a)(b)(c)(d)

OUT = []
def say(s):
    OUT.append(s)

# ---- 徴の定め（★語で当てる・断定ではない★）----
SIGN_WORD = [
    "\u689d",                      # 條
    "\u5e8a",                      # 床
    "\u578b 8 \u9805",            # 型 8 項
    "\u4e09\u629e\u8a9e",        # 三択語
    "\u968a\u306e\u6761",        # 隊の条
    "\u4f5c\u6cd5",               # 作法
]
SIGN_A = [
    "uid", "\u539f\u7406",        # 原理
    "\u5c4a\u304b\u306c",        # 届かぬ
    "\u4f5c\u3064\u3066\u3082", # 作つても
    "\u53ca\u3070\u306c",        # 及ばぬ
]
SIGN_B = [
    "\u8d70 1", "\u8d70\u884c",  # 走 1 / 走行
    "\u7981",                      # 禁
    "\u8ae4\u308b",               # 諮る
    "\u88c1\u3092\u8981",        # 裁を要
    "\u5e8a\u306b\u4f9d\u308a", # 床に依り
]
SIGN_C = [
    "\u672a\u3060",               # 未だ
    "\u4f5c\u308c\u3070",        # 作れば
    "\u5668\u3092\u4f5c",        # 器を作
    "\u5e83\u3052\u308c\u3070", # 広げれば
    "\u76f4\u305b\u3070",        # 直せば
]
SIGN_D = [
    "\u66f8\u304d\u65b9",        # 書き方
    "\u8a18\u6cd5",               # 記法
    "\u66f8\u6dfb\u3078",        # 書添へ
    "\u6a39\u3092\u66f8",        # 樹を書
]

def home_of(line):
    t = line.strip()
    if t.startswith("#"):
        return "\u898b\u51fa\u3057"          # 見出し
    if t.startswith(">"):
        return "\u5f15\u7528"                  # 引用
    if t.startswith("|"):
        return "\u8868"                         # 表
    if t.startswith("-") or t.startswith("*") or re.match(r"^[0-9]+[.)]", t):
        return "\u7b87\u6761"                  # 箇条
    if t.startswith("`") or t.startswith("    "):
        return "\u5668\u306e\u5e2f"           # 器の帯
    return "\u5730\u306e\u6587"               # 地の文

def signs_of(line):
    s = []
    if any(w in line for w in SIGN_WORD): s.append("\u6587\u8a00")  # 文言
    if any(w in line for w in SIGN_A): s.append(A)
    if any(w in line for w in SIGN_B): s.append(B)
    if any(w in line for w in SIGN_C): s.append(C)
    if any(w in line for w in SIGN_D): s.append(DD)
    return s

# ---- 母 ----
names = sorted([f for f in os.listdir(D) if f.endswith(".md")])
rows = []   # (file, lineno, line, home, signs)
for f in names:
    t = io.open(os.path.join(D, f), encoding="utf-8").read()
    for i, ln in enumerate(t.split(chr(10)), 1):
        if KEY in ln:
            rows.append((f, i, ln, home_of(ln), signs_of(ln)))

say("=== order231 / E26 ===")
say("\u6bcd = " + D + "/*.md " + str(len(names)) + " \u679a")
say("\u5f53\u305f\u308a\u884c = " + str(len(rows)))
lot_rows = [r for r in rows if r[0] in LOT]
oth_rows = [r for r in rows if r[0] not in LOT]
say("\u5185 \u672c lot(order226/227) = " + str(len(lot_rows)) + " / \u305d\u306e\u5916 = " + str(len(oth_rows)))
say("\u542b\u3080\u7d19 = " + str(len(set(r[0] for r in rows))) + " \u679a")
say("")

# ---- §一 検出力（陽性対照 = 本 lot 12 行・既知の答）----
say("--- \u00a7\u4e00 \u691c\u51fa\u529b\uff08\u967d\u6027\u5bfe\u7167 = \u672c lot 12 \u884c\uff09 ---")
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
hit = 0; miss = 0; wrong = 0
for r in lot_rows:
    k = (r[0], r[1])
    want = KNOWN.get(k)
    got = r[4]
    if want is None:
        say("  ?? " + r[0] + ":" + str(r[1]) + " \u5916(\u65e2\u77e5\u8868\u306b\u7121\u3057) signs=" + "+".join(got))
        continue
    if not got:
        miss += 1
        say("  \u5f81 0 : " + r[0] + ":" + str(r[1]) + " want=" + want)
    elif want in got:
        hit += 1
    else:
        wrong += 1
        say("  \u9055 : " + r[0] + ":" + str(r[1]) + " want=" + want + " got=" + "+".join(got))
say("  \u967d\u6027\u5bfe\u7167 " + str(len(lot_rows)) + " \u884c : \u5f53\u305f\u308a=" + str(hit)
    + " / \u5f81 0=" + str(miss) + " / \u9055=" + str(wrong))
say("")

# ---- §二 その外 1,354 行の徴の度数 ----
say("--- \u00a7\u4e8c \u672c lot \u306e\u5916 " + str(len(oth_rows)) + " \u884c\u306e\u5f81 ---")
cnt = collections.Counter()
for r in oth_rows:
    key = "+".join(r[4]) if r[4] else "(\u5f81 0)"
    cnt[key] += 1
for k, v in cnt.most_common():
    say("  " + k + " = " + str(v))
say("")

say("--- \u00a7\u4e09 \u68f2\u5bb6\u3054\u3068 ---")
hc = collections.Counter(r[3] for r in oth_rows)
for k, v in hc.most_common():
    say("  " + k + " = " + str(v))
say("")

# ---- §四 人が読む欄（各徴の逐語 3 例）----
say("--- \u00a7\u56db \u4eba\u304c\u8aad\u3080\u6b04\uff08\u5404\u5f81 3 \u4f8b\uff09 ---")
seen = collections.Counter()
for r in oth_rows:
    key = "+".join(r[4]) if r[4] else "(\u5f81 0)"
    if seen[key] < 3:
        seen[key] += 1
        say("  [" + key + "] " + r[0] + ":" + str(r[1]) + " | " + r[2].strip()[:110])
say("")

say("--- \u00a7\u4e94 \u5668\u306e\u9650 ---")
say("  \u672c\u5668\u306f ★\u65ad\u5b9a\u305b\u306c★ \u2015\u2015 \u8a9e\u306e\u5728\u5426\u3092\u6570\u3078\u308b\u306e\u307f\u3002")
say("  \u5f81 0 \u306e\u884c\u306f \u300c\u5225\u304c\u7121\u3044\u300d\u306e\u610f\u306b\u975e\u305a\u3001\u300c\u8a9e\u3067\u306f\u5206\u304b\u3089\u306c\u300d\u306e\u610f\u3067\u3042\u308b\u3002")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(OUT) + chr(10))
print(chr(10).join(OUT))
