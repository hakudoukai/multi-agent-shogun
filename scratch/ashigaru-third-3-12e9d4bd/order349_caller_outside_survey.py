# -*- coding: utf-8 -*-
# order349_caller_outside_survey.py
# 令349（A3）― 呼手を母の外で数へる（残弾 ㊌ を撃つ）
#
# ★網（撃つ前に逐語で鋳る・新条㊻）★
#
# §0 母
#   母 ＝ 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の
#        ★git の管理下の file 全体★（git ls-files で数へる）。
#   當たりは git grep の讀取のみで取る。find は一度も打たぬ。作業樹を舐めぬ。
#   家老の樹へは一字も書かぬ。
#
# §1 名（何を数へるか・固有名と一般名を分ける＝床(23)）
#   固有名 四つ:
#     N1 check_document_integrity
#     N2 fn_repeat_message_trap
#     N3 get_abbreviation_rules
#     N4 validate_treatment_entry__pre_dlane_20260614
#   併せて 一般名 N5 validate_treatment_entry を ★別に★ 数へる。
#   N5 は N4 の頭を共有する ★別の名★ である。境界を二重下線で切る故
#   N4 の當たりは N5 の網には掛からぬ。混ぜて数へてはならぬ。
#
# §2 網（識別子境界形・床⒅⒇）
#   pat(name) = (^|[^A-Za-z0-9_]) + name + ([^A-Za-z0-9_]|$)
#   ★行末で終はる當たりも取る★（末尾の $ を入れる）。
#   git grep -I -n -E <五名の交り> を ★一度だけ★ 打ち、
#   返つた行を python の中で名ごとに当て直す。
#   grep は engine を名指す（git grep の -E ＝ POSIX 拡張）。
#
# §3 一つの数へ方（床(30)）
#   一つ ＝ ★當たり行★（同じ行に名が二度現れても一つ）。
#   file ごとの数も當たり行で数へる。
#
# §4 分け（㊀㊁㊂ ＋ 判じられぬ・上から順に当てる）
#   ㊀呼ぶ  = 次の何れか（★註の行を除く★）
#             (a) 行に  rest/v1/rpc/<名>  を含む
#             (b) 行に  rpc( に続く引用符 + <名>  を含む
#             (c) 行に  SELECT <名>( か PERFORM <名>( を含み CREATE 行でない
#   ㊁定める = 行に CREATE [OR REPLACE] FUNCTION に続く（public. を挟み得る）<名> を含む
#             （★註の行を除く★）
#   ㊂名のみ = ㊀㊁ に当たらず、かつ 次の何れか
#             (p) 行の頭（空白を除く）が  --  #  |  -  の何れかで始まる（註・表・箇条・見出し）
#             (q) 行に <名>( の形が一度も現れぬ（括弧を伴はぬ言及）
#   判じられぬ = 上の何れにも当たらぬ物（括弧を伴ふが呼びとも定めとも決められぬ）
#   ★判じられぬ を 0 と混ぜぬ★
#   ㊂ の棲家を別に数へる ―― ㋐-- 行 ㋑# 行 ㋒| 表行 ㋓- 箇条行 ㋔括弧無しの其の他
#
# §5 ㋒（空の集合を渡し得るか）
#   ㊀ が在る名についてのみ、其の呼びの行と其の前後 12 行を出す。
#   ★渡す側の引数の字のみを見る★。外の知識で断ぜぬ。
#
# §6 床
#   DB 0・psql 0・MCP 0・当て 0・patch 0・製品 code 書込 0・install 0・find 0・rm 0
#   ssh 0・/mnt/c 不触・家老の樹へ書込 0（讀取のみ）。焚 1・走 上限 1。
#   値・患者の字・鍵の個々の値は一つも出さぬ（名と行番のみ）。

import re, subprocess, sys

ROOT = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912"

N1 = "check_document_integrity"
N2 = "fn_repeat_message_trap"
N3 = "get_abbreviation_rules"
N4 = "validate_treatment_entry__pre_dlane_20260614"
N5 = "validate_treatment_entry"
NAMES = [N1, N2, N3, N4, N5]
KOYU = [N1, N2, N3, N4]

def sh(args):
    return subprocess.check_output(args, cwd=ROOT).decode("utf-8", "replace")

# --- §0 母 ---
head = sh(["git", "rev-parse", "HEAD"]).strip()
files_all = sh(["git", "ls-files"]).split("\n")
files_all = [x for x in files_all if x]
print("ROOT_HEAD %s" % head[:16])
print("ROOT_FILES tracked=%d (unit=path)" % len(files_all))

# --- §2 網 ---
alt = "|".join(NAMES)
netto = "(^|[^A-Za-z0-9_])(" + alt + ")([^A-Za-z0-9_]|$)"
print("NET %s" % netto)
try:
    raw = subprocess.check_output(
        ["git", "grep", "-I", "-n", "-E", netto], cwd=ROOT
    ).decode("utf-8", "replace")
except subprocess.CalledProcessError as e:
    raw = e.output.decode("utf-8", "replace") if e.output else ""
lines = [x for x in raw.split("\n") if x]
print("GREP rawlines=%d (unit=hit-line)" % len(lines))

pats = {}
for n in NAMES:
    pats[n] = re.compile("(^|[^A-Za-z0-9_])" + n + "([^A-Za-z0-9_]|$)")

def split3(rec):
    # git grep -n の形 = path:lineno:text （path に : は出ぬ前提を検める）
    i = rec.find(":")
    j = rec.find(":", i + 1)
    if i < 0 or j < 0:
        return None
    return rec[:i], rec[i+1:j], rec[j+1:]

MARK = ("--", "#", "|", "-")

def is_comment(t):
    u = t.lstrip()
    for m in MARK:
        if u.startswith(m):
            return True
    return False

def klass(name, t):
    low = t.lower()
    c = is_comment(t)
    cre = re.search("create[ \t]+(or[ \t]+replace[ \t]+)?function[ \t]+(public\\.)?" + name + "([^A-Za-z0-9_]|$)", low)
    if not c:
        if ("rest/v1/rpc/" + name) in t:
            return "call"
        if re.search("rpc[ \t]*\\([ \t]*['\"]" + name + "['\"]", t):
            return "call"
        if re.search("(select|perform)[ \t]+(public\\.)?" + name + "[ \t]*\\(", low) and not cre:
            return "call"
    if cre and not c:
        return "def"
    if c:
        return "name"
    if not re.search(name + "[ \t]*\\(", t):
        return "name"
    return "unk"

def home(t):
    u = t.lstrip()
    if u.startswith("--"):
        return "dash"
    if u.startswith("#"):
        return "sharp"
    if u.startswith("|"):
        return "table"
    if u.startswith("-"):
        return "bullet"
    return "other"

res = {}
for n in NAMES:
    res[n] = {"files": {}, "call": 0, "def": 0, "name": 0, "unk": 0,
              "homes": {"dash": 0, "sharp": 0, "table": 0, "bullet": 0, "other": 0},
              "calls": []}

bad = 0
for rec in lines:
    p = split3(rec)
    if p is None:
        bad += 1
        continue
    path, ln, txt = p
    for n in NAMES:
        if pats[n].search(txt):
            r = res[n]
            r["files"][path] = r["files"].get(path, 0) + 1
            k = klass(n, txt)
            r[k] += 1
            if k == "name":
                r["homes"][home(txt)] += 1
            if k == "call":
                r["calls"].append((path, ln))
print("MALFORMED %d" % bad)

for n in NAMES:
    r = res[n]
    tot = r["call"] + r["def"] + r["name"] + r["unk"]
    tag = "koyu" if n in KOYU else "ippan"
    print("")
    print("==== %s (%s)" % (n, tag))
    print("  HITS total=%d files=%d (unit=hit-line)" % (tot, len(r["files"])))
    print("  SPLIT call=%d def=%d nameonly=%d undecidable=%d (unit=hit-line)"
          % (r["call"], r["def"], r["name"], r["unk"]))
    print("  HOME(nameonly) dash=%d sharp=%d table=%d bullet=%d other=%d"
          % (r["homes"]["dash"], r["homes"]["sharp"], r["homes"]["table"],
             r["homes"]["bullet"], r["homes"]["other"]))
    if len(r["files"]) <= 12:
        for f in sorted(r["files"]):
            print("    FILE %s : %d" % (f, r["files"][f]))
    else:
        ss = sorted(r["files"].items(), key=lambda kv: -kv[1])
        print("    FILES(top12 of %d)" % len(r["files"]))
        for f, c in ss[:12]:
            print("    FILE %s : %d" % (f, c))
    for f, ln in r["calls"]:
        print("    CALL %s:%s" % (f, ln))

# --- §5 呼手の引数の字 ---
print("")
print("==== ARG (呼手の渡す字・前後12行)")
for n in NAMES:
    for f, ln in res[n]["calls"]:
        k = int(ln)
        body = open(ROOT + "/" + f, "rb").read().decode("utf-8", "replace").split("\n")
        lo = max(0, k - 1)
        hi = min(len(body), k + 12)
        seg = body[lo:hi]
        joined = "\n".join(seg)
        has_json = "json=" in joined
        m = re.search("json=[ \t]*(\\{[^\\n]*\\}|[A-Za-z_][A-Za-z0-9_]*)", joined)
        print("  %s %s:%s json_kw=%s arg=%s"
              % (n, f, ln, "yes" if has_json else "no", m.group(1) if m else "none"))

print("DONE")
