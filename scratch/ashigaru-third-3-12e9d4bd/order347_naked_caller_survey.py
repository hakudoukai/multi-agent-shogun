# -*- coding: utf-8 -*-
# ============================================================================
# 令347 の網（撃つ前に此処へ逐語で鋳る ―― 新条(46)）
#  §0 母 = 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の
#     supabase/migrations/20260909170000_snapshot_live_public_functions.sql（讀取のみ）
#  §1 集約 = 空の時 null を返す 13 語（jsonb_agg json_agg jsonb_object_agg json_object_agg
#     array_agg string_agg sum max min avg bool_and bool_or every）／count は母の外
#  §2 当たり = 名の直後に開き括弧。境界は英数と下線以外の明示クラス。大小文字は無視
#  §3 母の外 = 行註(--) 帯註(/* */) 単引用の中（$tag$ の帯は code ゆゑ母の内）
#  §4 守り = 括弧の対応で外へ辿り 包む呼びの何れかが coalesce（上限＝其の CREATE FUNCTION の頭）
#  §5 呼手 = 函の素の名（schema 冠を外した名）が識別子境界で現れ 直後に開き括弧。
#     其の行が CREATE [OR REPLACE] FUNCTION で始まるなら 定義 ゆゑ呼手から除く。母の外は数へぬ。
#     別に「名の当たり（括弧を問はぬ）」も数へる（床(22) 参照と呼出行を分けるため）
#  §6 当たりの文 = 当たりの位置から 前へ 直近の生きた SELECT まで／後ろへ
#     (a)深さ 0 の `;` (b)深さが負へ落ちる `)` (c)深さ 0 の LOOP/THEN/END の何れか早い方まで
#  §7 空の集合を受け得るか の分け（上から順に当てる・最初に当たつた一つのみ採る）
#     (7a)群化 = 当たりの文に GROUP BY が在る → 受けぬ（群は必ず一行以上）
#     (7b)上のIF = 当たりの文より前の直近の IF/ELSIF 行に 当たりの文の FROM の括弧の中の
#         識別子が在り 且つ 其の行に 0 より大きいを判ずる字（> 0）が在る → 受けぬ
#     (7c)絞り = 当たりの文に FROM が在り 群化が無い → 受け得る（WHERE の有無は別に印す）
#     (7d)上の何れにも当たらぬ → 判じられぬ
#  §8 三鍵と同じ形 の定め（二つ立て 数を別々に書く）
#     狭 = 裸 かつ 受け得る かつ 集約が jsonb_agg かつ 包む呼びに jsonb_build_object が在る
#     広 = 裸 かつ 受け得る
# ============================================================================
import io, re, hashlib

SRC = ("/home/hakudoukai/karo3/wt-abbrev-guard-20260912/supabase/migrations/"
       "20260909170000_snapshot_live_public_functions.sql")

raw = io.open(SRC, "rb").read()
s = raw.decode("utf-8")
print("FILE lines=%d bytes=%d sha256first16=%s" %
      (s.count("\n"), len(raw), hashlib.sha256(raw).hexdigest()[:16]))

# ---- §3 mask -------------------------------------------------------------
def build_mask(t):
    n = len(t); m = [False]*n; i = 0
    while i < n:
        c = t[i]
        if c == "-" and i+1 < n and t[i+1] == "-":
            j = t.find("\n", i)
            if j < 0: j = n
            for k in range(i, j): m[k] = True
            i = j; continue
        if c == "/" and i+1 < n and t[i+1] == "*":
            d = 1; j = i+2
            while j < n and d > 0:
                if t[j] == "/" and j+1 < n and t[j+1] == "*": d += 1; j += 2; continue
                if t[j] == "*" and j+1 < n and t[j+1] == "/": d -= 1; j += 2; continue
                j += 1
            for k in range(i, min(j, n)): m[k] = True
            i = j; continue
        if c == "'":
            j = i+1
            while j < n:
                if t[j] == "'":
                    if j+1 < n and t[j+1] == "'": j += 2; continue
                    j += 1; break
                j += 1
            for k in range(i, min(j, n)): m[k] = True
            i = j; continue
        if c == "$":
            mm = re.match(r"\$[A-Za-z0-9_]*\$", t[i:])
            if mm:
                i = i + len(mm.group(0)); continue
            i += 1; continue
        i += 1
    return m

mask = build_mask(s)
print("MASK masked chars=%d of %d" % (sum(1 for x in mask if x), len(s)))

def live(i):
    return not mask[i]

def lineno(i):
    return s.count("\n", 0, i) + 1

# ---- CREATE FUNCTION の頭 -------------------------------------------------
fre = re.compile(r"(?im)^[ \t]*CREATE[ \t]+(?:OR[ \t]+REPLACE[ \t]+)?FUNCTION[ \t]+([A-Za-z0-9_.]+)")
funcs = [(m.start(), m.group(1)) for m in fre.finditer(s) if live(m.start())]
print("FUNCS total=%d" % len(funcs))

def owner(i):
    nm = None; st = 0
    for p, n in funcs:
        if p <= i: nm = n; st = p
        else: break
    return nm, st

# ---- §1/§2 当たり ---------------------------------------------------------
AGGS = ["jsonb_agg","json_agg","jsonb_object_agg","json_object_agg","array_agg",
        "string_agg","sum","max","min","avg","bool_and","bool_or","every"]
hits = []
for a in AGGS:
    pat = re.compile("(?i)(?<![A-Za-z0-9_])" + a + "(?![A-Za-z0-9_])[ \t\r\n]*\\(")
    for m in pat.finditer(s):
        hits.append((m.start(), a, m.end()-1))
hits.sort()
raw_n = len(hits)
dead = [h for h in hits if not live(h[0])]
hits = [h for h in hits if live(h[0])]
print("HITS raw=%d / in comment or literal=%d / live=%d" % (raw_n, len(dead), len(hits)))

# ---- §4 守り（外へ辿る） --------------------------------------------------
def enclosing(p, floor):
    names = []; i = p - 1; depth = 0
    while i >= floor:
        if live(i):
            c = s[i]
            if c == ")": depth += 1
            elif c == "(":
                if depth == 0:
                    j = i - 1
                    while j >= floor and (s[j] in " \t\r\n"): j -= 1
                    e = j + 1
                    while j >= floor and re.match(r"[A-Za-z0-9_.]", s[j]): j -= 1
                    nm = s[j+1:e]
                    if nm: names.append(nm)
                    i = j; continue
                depth -= 1
        i -= 1
    return names

guarded = []; naked = []
for (p, a, op) in hits:
    fn, st = owner(p)
    ch = enclosing(p, st)
    g = any(x.lower().endswith("coalesce") for x in ch)
    rec = {"pos": p, "agg": a, "line": lineno(p), "fn": fn, "chain": ch}
    (guarded if g else naked).append(rec)
print("SPLIT guarded=%d naked=%d (unit=hit)" % (len(guarded), len(naked)))

# ---- §5 呼手 --------------------------------------------------------------
TARGET = ["check_document_integrity", "fn_repeat_message_trap",
          "get_abbreviation_rules", "validate_treatment_entry__pre_dlane_20260614"]
print("---- caller counts (unit=hit)")
for t in TARGET:
    bare = re.compile("(?<![A-Za-z0-9_])" + t + "(?![A-Za-z0-9_])")
    allhit = [m.start() for m in bare.finditer(s)]
    liv = [i for i in allhit if live(i)]
    withp = []
    for i in liv:
        j = i + len(t)
        while j < len(s) and s[j] in " \t\r\n": j += 1
        if j < len(s) and s[j] == "(": withp.append(i)
    defs = []
    calls = []
    for i in withp:
        ls = s.rfind("\n", 0, i) + 1
        le = s.find("\n", i)
        ln = s[ls:le if le > 0 else len(s)]
        if re.match(r"^[ \t]*CREATE[ \t]+(?:OR[ \t]+REPLACE[ \t]+)?FUNCTION", ln, re.I):
            defs.append(i)
        else:
            calls.append(i)
    print("  %s : name_all=%d name_live=%d with_paren=%d def=%d caller=%d %s"
          % (t, len(allhit), len(liv), len(withp), len(defs), len(calls),
             "lines=" + ",".join(str(lineno(i)) for i in calls) if calls else "lines=none"))

# ---- §6 当たりの文 --------------------------------------------------------
sel = [m.start() for m in re.finditer(r"(?i)(?<![A-Za-z0-9_])SELECT(?![A-Za-z0-9_])", s) if live(m.start())]
stopkw = re.compile(r"(?i)(?<![A-Za-z0-9_])(LOOP|THEN|END)(?![A-Za-z0-9_])")

def stmt_span(p, floor):
    st = floor
    for q in sel:
        if q <= p and q >= floor: st = q
        if q > p: break
    i = st; depth = 0; n = len(s)
    while i < n:
        if live(i):
            c = s[i]
            if c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth < 0: return st, i
            elif c == ";" and depth == 0: return st, i
            elif depth == 0:
                mm = stopkw.match(s, i)
                if mm and (i == 0 or not re.match(r"[A-Za-z0-9_]", s[i-1])):
                    return st, i
        i += 1
    return st, n

ifre = re.compile(r"(?im)^[ \t]*(?:ELSIF|IF)[ \t].*$")

print("---- naked analysis (unit=hit)")
cls = {"受けぬ": 0, "受け得る": 0, "判じられぬ": 0}
rule = {}
narrow = []; wide = []
for r in naked:
    try:
        fn, floor = r["fn"], owner(r["pos"])[1]
        a, b = stmt_span(r["pos"], floor)
        st = s[a:b]
        stl = re.sub(r"--[^\n]*", " ", st)
        has_group = re.search(r"(?i)(?<![A-Za-z0-9_])GROUP[ \t\r\n]+BY(?![A-Za-z0-9_])", stl) is not None
        mfrom = re.search(r"(?i)(?<![A-Za-z0-9_])FROM(?![A-Za-z0-9_])[ \t\r\n]*([A-Za-z0-9_.]+)([ \t\r\n]*\()?", stl)
        has_from = mfrom is not None
        src = mfrom.group(1) if mfrom else ""
        args = ""
        if mfrom and mfrom.group(2):
            k = stl.find("(", mfrom.end(1)); d = 0; e = k
            while e < len(stl):
                if stl[e] == "(": d += 1
                elif stl[e] == ")":
                    d -= 1
                    if d == 0: break
                e += 1
            args = stl[k+1:e]
        has_where = re.search(r"(?i)(?<![A-Za-z0-9_])WHERE(?![A-Za-z0-9_])", stl) is not None
        ifline = ""
        for m in ifre.finditer(s, floor, a):
            if live(m.start()): ifline = m.group(0).strip()
        ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", args))
        ifguard = bool(ids) and any(i2 in ifline for i2 in ids) and \
                  re.search(r">[ \t]*0", ifline) is not None
        if has_group: c, why = "受けぬ", "7a group"
        elif ifguard: c, why = "受けぬ", "7b if"
        elif has_from and not has_group: c, why = "受け得る", "7c filter"
        else: c, why = "判じられぬ", "7d"
        cls[c] += 1; rule[why] = rule.get(why, 0) + 1
        if c == "受け得る":
            wide.append(r["line"])
            if r["agg"].lower() == "jsonb_agg" and any(x.lower().endswith("jsonb_build_object") for x in r["chain"]):
                narrow.append(r["line"])
        print("  L%-5d %-16s fn=%-46s cls=%-8s rule=%-9s group=%s where=%s from=%s chain=%s"
              % (r["line"], r["agg"], str(fn), c, why, has_group, has_where, src, "/".join(r["chain"]) or "-"))
    except Exception as e:
        print("  L%-5d %s EXC %s" % (r["line"], r["agg"], type(e).__name__))

print("CLASS 受けぬ=%d 受け得る=%d 判じられぬ=%d (unit=hit)" % (cls["受けぬ"], cls["受け得る"], cls["判じられぬ"]))
print("RULEHIT " + " ".join("%s=%d" % (k, v) for k, v in sorted(rule.items())))

# ---- §8 三鍵と同じ形 ------------------------------------------------------
KEYS = [732, 743, 754]
rest_wide = [x for x in wide if x not in KEYS]
rest_narrow = [x for x in narrow if x not in KEYS]
print("SHAPE keys=%s" % (",".join(str(x) for x in KEYS)))
print("SHAPE rest total=%d" % (len(naked) - len([r for r in naked if r['line'] in KEYS])))
print("SHAPE narrow in rest=%d lines=%s" % (len(rest_narrow), ",".join(str(x) for x in rest_narrow) or "none"))
print("SHAPE wide   in rest=%d lines=%s" % (len(rest_wide), ",".join(str(x) for x in rest_wide) or "none"))
print("DONE")
