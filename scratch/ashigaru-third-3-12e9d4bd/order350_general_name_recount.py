# -*- coding: utf-8 -*-
# order350_general_name_recount.py
# 令350 ― ㊏ を撃つ：一般名 validate treatment entry の當たりを 網を直して分け直す
#
# ★網（撃つ前に逐語で鋳る・新条㊻）★
#
# §0 母（令349 と同じ事を符で示す）
#   母 ＝ 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の git 管理下 全体。
#   讀取のみ・書込 0・find 0。樹の頭（git の id ＝ sha1）を刷り 令349 の 6b5ac1f730ba4f0c と
#   同じである事を器自身に言はせる。
#
# §1 名
#   一般名 G ＝ validate_treatment_entry
#   固有名 K ＝ validate_treatment_entry + 二重下線 + pre_dlane_20260614
#   境界が下線で切れる故 K の當たりは G の網に掛からぬ。令349 の通り別の名として保つ。
#
# §2 網（識別子境界形・令349 と同じ）
#   pat = (^|[^A-Za-z0-9_]) + G + ([^A-Za-z0-9_]|$)
#   git grep -I -n -E を ★一度だけ★ 打つ。一つ ＝ 當たり行。
#
# §3 file の種で割る（★先づ之を為す★）
#   ㋐ code          = 拡張子が py / ts / tsx / sql（実行される字）
#   ㋑ log と産出    = 拡張子が log / json（走りの記録・raw の出力）
#   ㋒ 紙            = 拡張子が md / txt
#   ㋓ 其他          = 上の何れでもない
#   拡張子は path の末の点より後を小文字に均した物。点が無ければ 其他。
#
# §4 四分け（★㋐ code に限つて当てる★・㋑㋒㋓ は数だけ）
#   ㊀呼ぶ  ―― 註の行を除き 次の何れか
#     (a) 行に rest/v1/rpc/<名> を含む
#     (b) 行に rpc( に続く引用符 + <名> を含む
#     (b2) ★令350 で足した★ 行が 引用符に包まれた名のみ（前後は空白と読点と括弧のみ）であり
#          其の上 3 行以内に rpc の括弧開きが在る（引数を行に分けて書く形を取る）
#     (c) 行に SELECT <名>( か PERFORM <名>( を含み 定めの行でない
#   ㊁定める ―― 註の行を除き 次の何れか
#     (d) CREATE [OR REPLACE] FUNCTION に続く（public. を挟み得る）<名>  ＝ 令349 の網
#     (e) ★令350 で足した★ DROP FUNCTION [IF EXISTS] / ALTER FUNCTION / COMMENT ON FUNCTION
#         に続く（public. を挟み得る）<名>
#   ㊂名のみ ―― ㊀㊁ に当たらず、行頭（空白を除く）が 二重の横棒 か 井桁 か 縦棒 か 横棒 か
#     星印 で始まるか、行に <名>( の形が一度も現れぬ
#   判じられぬ ―― 残り
#   ★物差しを動かした分を分けて書く（作法 八条目）★ ゆゑ
#   令349 の網（(a)(b) と (d) のみ）の数も 同じ走りで併せて刷る。
#
# §5 ㊀ の呼びが集合を渡し得るか
#   呼びの行から下 24 行を讀み 引数の鍵名のみを挙げる（★値は一つも刷らぬ★）。
#
# §6 床
#   DB 0・psql 0・MCP 0・当て 0・check 0・patch 0・製品 code 書込 0・install 0・find 0
#   rm 0・ssh 0・/mnt/c 書込 0・家老の樹へ書込 0。焚 1・走 1。
#   ★産出は head にも pipe にも繋がず 器の中で讀み切り 丈を抑へて刷る★
#   値・患者の字・鍵の個々の値は一つも刷らぬ（名と行番と数のみ）。

import re, subprocess

ROOT = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912"
G = "validate_treatment_entry"

CODE_EXT = ("py", "ts", "tsx", "sql")
LOGOUT_EXT = ("log", "json")
PAPER_EXT = ("md", "txt")

def sh(a):
    return subprocess.check_output(a, cwd=ROOT).decode("utf-8", "replace")

head = sh(["git", "rev-parse", "HEAD"]).strip()
print("ROOT_HEAD %s same_as_order349=%s" % (head[:16], "yes" if head[:16] == "6b5ac1f730ba4f0c" else "no"))
tracked = len([x for x in sh(["git", "ls-files"]).split("\n") if x])
print("ROOT_FILES tracked=%d (unit=path)" % tracked)

net = "(^|[^A-Za-z0-9_])" + G + "([^A-Za-z0-9_]|$)"
print("NET %s" % net)
try:
    raw = subprocess.check_output(["git", "grep", "-I", "-n", "-E", net], cwd=ROOT).decode("utf-8", "replace")
except subprocess.CalledProcessError as e:
    raw = e.output.decode("utf-8", "replace") if e.output else ""
recs = [x for x in raw.split("\n") if x]
print("GREP rawlines=%d (unit=hit-line)" % len(recs))

def ext(p):
    b = p.split("/")[-1]
    if "." not in b:
        return ""
    return b.split(".")[-1].lower().strip('"')

def kind(p):
    e = ext(p)
    if e in CODE_EXT:
        return "code"
    if e in LOGOUT_EXT:
        return "logout"
    if e in PAPER_EXT:
        return "paper"
    return "other"

def split3(r):
    i = r.find(":")
    j = r.find(":", i + 1)
    if i < 0 or j < 0:
        return None
    return r[:i], int(r[i+1:j]), r[j+1:]

buckets = {"code": {}, "logout": {}, "paper": {}, "other": {}}
coderecs = []
bad = 0
for r in recs:
    t = split3(r)
    if t is None:
        bad += 1
        continue
    p, ln, txt = t
    k = kind(p)
    buckets[k][p] = buckets[k].get(p, 0) + 1
    if k == "code":
        coderecs.append((p, ln, txt))
print("MALFORMED %d" % bad)

print("")
print("---- KIND (unit=file / hit-line)")
for k in ("code", "logout", "paper", "other"):
    b = buckets[k]
    print("  %-7s files=%d hits=%d" % (k, len(b), sum(b.values())))
print("---- CODE files (unit=hit-line)")
for p in sorted(buckets["code"]):
    print("  %s : %d  ext=%s" % (p, buckets["code"][p], ext(p)))

MARK = ("--", "#", "|", "-", "*")
def is_comment(t):
    u = t.lstrip()
    for m in MARK:
        if u.startswith(m):
            return True
    return False

# 呼びの (b2) 用に file の中身を持つ
cache = {}
def body(p):
    if p not in cache:
        fp = ROOT + "/" + p.strip('"')
        cache[p] = open(fp, "rb").read().decode("utf-8", "replace").split("\n")
    return cache[p]

only_q = re.compile("^[ \t]*['\"]" + G + "['\"][ \t]*,?[ \t]*$")
rpc_open = re.compile("rpc[ \t]*\\(")

def is_call(p, ln, t, wide):
    if is_comment(t):
        return False
    if ("rest/v1/rpc/" + G) in t:
        return True
    if re.search("rpc[ \t]*\\([ \t]*['\"]" + G + "['\"]", t):
        return True
    low = t.lower()
    if re.search("(select|perform)[ \t]+(public\\.)?" + G + "[ \t]*\\(", low):
        return True
    if wide and only_q.match(t):
        b = body(p)
        for k in range(max(0, ln - 4), ln - 1):
            if k < len(b) and rpc_open.search(b[k]):
                return True
    return False

def is_def(t, wide):
    if is_comment(t):
        return False
    low = t.lower()
    if re.search("create[ \t]+(or[ \t]+replace[ \t]+)?function[ \t]+(public\\.)?" + G + "([^a-z0-9_]|$)", low):
        return True
    if wide:
        if re.search("drop[ \t]+function[ \t]+(if[ \t]+exists[ \t]+)?(public\\.)?" + G + "([^a-z0-9_]|$)", low):
            return True
        if re.search("alter[ \t]+function[ \t]+(public\\.)?" + G + "([^a-z0-9_]|$)", low):
            return True
        if re.search("comment[ \t]+on[ \t]+function[ \t]+(public\\.)?" + G + "([^a-z0-9_]|$)", low):
            return True
    return False

def klass(p, ln, t, wide):
    if is_call(p, ln, t, wide):
        return "call"
    if is_def(t, wide):
        return "def"
    if is_comment(t):
        return "name"
    if not re.search(G + "[ \t]*\\(", t):
        return "name"
    return "unk"

for wide, tag in ((False, "order349-net"), (True, "order350-net")):
    c = {"call": 0, "def": 0, "name": 0, "unk": 0}
    calls = []
    for p, ln, t in coderecs:
        k = klass(p, ln, t, wide)
        c[k] += 1
        if k == "call":
            calls.append((p, ln))
    print("")
    print("---- SPLIT(code only, %s) call=%d def=%d nameonly=%d undecidable=%d (unit=hit-line)"
          % (tag, c["call"], c["def"], c["name"], c["unk"]))
    for p, ln in calls:
        print("    CALL %s:%d" % (p, ln))
    if wide:
        print("---- ARG (呼びの下 24 行の引数の鍵名のみ・値は刷らぬ)")
        for p, ln in calls:
            b = body(p)
            seg = b[ln - 1: min(len(b), ln + 24)]
            keys = []
            for line in seg:
                m = re.match("^[ \t]*['\"](p_[A-Za-z0-9_]+)['\"][ \t]*:", line)
                if m and m.group(1) not in keys:
                    keys.append(m.group(1))
            print("    ARG %s:%d keys=%d %s" % (p, ln, len(keys), ",".join(keys)))

print("")
print("---- NONCODE (数のみ・分けには入れぬ)")
for k in ("logout", "paper", "other"):
    b = buckets[k]
    top = sorted(b.items(), key=lambda kv: -kv[1])[:4]
    print("  %-7s files=%d hits=%d top=%s" % (k, len(b), sum(b.values()),
          " ".join(["%s:%d" % (x[0].split("/")[-1].strip('"'), x[1]) for x in top])))
print("DONE")
