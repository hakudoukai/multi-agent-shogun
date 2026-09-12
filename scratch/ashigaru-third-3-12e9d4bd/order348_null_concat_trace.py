# -*- coding: utf-8 -*-
# ============================================================================
# 令348 の網（撃つ前に此処へ逐語で鋳る ―― 新条(46)）
#  §0 母 = 家老の樹 /home/hakudoukai/karo3/wt-abbrev-guard-20260912 の
#     supabase/migrations/20260909170000_snapshot_live_public_functions.sql（讀取のみ）
#  §1 覆ひ = 行註(--) 帯註(/* */) 単引用の中（$tag$ の帯は code ゆゑ母の内）。令347 と同じ器
#  §2 的の当たり = L61 と L62 の string_agg（令347 で裸かつ受け得ると分けた 2 当たり）
#  §3 当たりの文 = 当たりから 前へ直近の生きた SELECT／後ろへ 深さ 0 の `;`・深さが負へ落ちる `)`・
#     深さ 0 の LOOP/THEN/END の何れか早い方まで（令347 §6 と同じ定め）
#  §4 受けの変数 = 当たりの文の INTO の後に続く識別子の列（読点区切り）。
#     当たりが選び出しの何番目かを 深さ 0 の読点の数で数へ 同じ順の名を採る
#  §5 型 = DECLARE の帯（CREATE FUNCTION の頭から最初の BEGIN まで）の中で
#     其の名が行頭に現れる行の 名の後の語
#  §6 現れ = 名が識別子の境界で現れる生の当たりを悉く。種は
#     (a)宣言＝DECLARE の帯の中 (b)受け＝INTO の後 (c)用ゐる所＝其の他
#  §7 連結の種の分け（用ゐる所の当たりごと・三つを別々に数へる）
#     (7a)二本の縦棒 = 当たりの左右を同じ深さで白を飛ばして見 二本の縦棒が隣る
#     (7b)concat 系 = 包む呼びの名が concat または concat_ws
#     (7c)format 系 = 包む呼びの名が format
#     何れでもなければ 連結に非ず
#  §8 行き先 = 用ゐる所の当たりを含む代入の文（前へ直近の深さ 0 の `;` か BEGIN/THEN/ELSE から
#     後ろへ深さ 0 の `;` まで）の頭が「名 := 」なら 其の名を行き先とする。
#     其の名が RETURN の後に識別子の境界で現れるなら 返りへ伝はる筋が字の上に在る と印す
#  §9 言へぬ事 = 母の字に書かれて居らぬ事（jsonb_build_object が null をどう扱ふか等）は
#     外の知識で断ぜず 言へぬ と出す
# ============================================================================
import io, re, hashlib

SRC = ("/home/hakudoukai/karo3/wt-abbrev-guard-20260912/supabase/migrations/"
       "20260909170000_snapshot_live_public_functions.sql")
raw = io.open(SRC, "rb").read()
s = raw.decode("utf-8")
print("FILE lines=%d bytes=%d sha256first16=%s" %
      (s.count("\n"), len(raw), hashlib.sha256(raw).hexdigest()[:16]))

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
live = lambda i: not mask[i]
lineno = lambda i: s.count("\n", 0, i) + 1
print("MASK masked chars=%d of %d" % (sum(1 for x in mask if x), len(s)))

fre = re.compile(r"(?im)^[ \t]*CREATE[ \t]+(?:OR[ \t]+REPLACE[ \t]+)?FUNCTION[ \t]+([A-Za-z0-9_.]+)")
funcs = [(m.start(), m.group(1)) for m in fre.finditer(s) if live(m.start())]
def owner(i):
    nm = None; st = 0; en = len(s)
    for k, (p, n) in enumerate(funcs):
        if p <= i: nm = n; st = p; en = funcs[k+1][0] if k+1 < len(funcs) else len(s)
    return nm, st, en

sel = [m.start() for m in re.finditer(r"(?i)(?<![A-Za-z0-9_])SELECT(?![A-Za-z0-9_])", s) if live(m.start())]
stopkw = re.compile(r"(?i)(?<![A-Za-z0-9_])(LOOP|THEN|END)(?![A-Za-z0-9_])")

def stmt_span(p, floor):
    st = floor
    for q in sel:
        if floor <= q <= p: st = q
        if q > p: break
    i = st; d = 0; n = len(s)
    while i < n:
        if live(i):
            c = s[i]
            if c == "(": d += 1
            elif c == ")":
                d -= 1
                if d < 0: return st, i
            elif c == ";" and d == 0: return st, i
            elif d == 0 and stopkw.match(s, i) and (i == 0 or not re.match(r"[A-Za-z0-9_]", s[i-1])):
                return st, i
        i += 1
    return st, n

def enclosing(p, floor):
    names = []; i = p - 1; d = 0
    while i >= floor:
        if live(i):
            c = s[i]
            if c == ")": d += 1
            elif c == "(":
                if d == 0:
                    j = i - 1
                    while j >= floor and s[j] in " \t\r\n": j -= 1
                    e = j + 1
                    while j >= floor and re.match(r"[A-Za-z0-9_.]", s[j]): j -= 1
                    nm = s[j+1:e]
                    names.append(nm if nm else "-")
                    i = j; continue
                d -= 1
        i -= 1
    return names

# ---- §2 的の当たり -------------------------------------------------------
pat = re.compile("(?i)(?<![A-Za-z0-9_])string_agg(?![A-Za-z0-9_])[ \t\r\n]*\\(")
targets = [m.start() for m in pat.finditer(s) if live(m.start()) and lineno(m.start()) in (61, 62)]
print("TARGET hits=%d lines=%s" % (len(targets), ",".join(str(lineno(x)) for x in targets)))

fn, floor, ceil = owner(targets[0])
print("OWNER fn=%s span=L%d..L%d" % (fn, lineno(floor), lineno(ceil-1)))
mb = re.search(r"(?im)^[ \t]*BEGIN[ \t]*$", s[floor:ceil])
decl_end = floor + mb.start() if mb else floor
print("DECLARE band = L%d..L%d" % (lineno(floor), lineno(decl_end)))

# ---- §4/§5 受けの変数と型 ------------------------------------------------
VARS = []
for p in targets:
    a, b = stmt_span(p, floor)
    st = s[a:b]
    mi = re.search(r"(?i)(?<![A-Za-z0-9_])INTO(?![A-Za-z0-9_])", st)
    names = []
    if mi:
        tail = st[mi.end():]
        mm = re.match(r"[ \t\r\n]*((?:[A-Za-z_][A-Za-z0-9_]*[ \t\r\n]*,[ \t\r\n]*)*[A-Za-z_][A-Za-z0-9_]*)", tail)
        if mm: names = [x.strip() for x in mm.group(1).split(",")]
    # 選び出しの何番目か = SELECT から当たりまでの 深さ 0 の読点の数
    idx = 0; d = 0
    for i in range(a, p):
        if live(i):
            if s[i] == "(": d += 1
            elif s[i] == ")": d -= 1
            elif s[i] == "," and d == 0: idx += 1
    nm = names[idx] if idx < len(names) else "-"
    dm = re.search(r"(?m)^[ \t]*" + re.escape(nm) + r"[ \t]+([A-Za-z0-9_ ]+?)[ \t]*;", s[floor:decl_end]) if nm != "-" else None
    ty = dm.group(1).strip() if dm else "-"
    print("ASSIGN L%d string_agg -> into=%s idx=%d name=%s type=%s intolist=%s"
          % (lineno(p), "yes" if mi else "no", idx, nm, ty, "/".join(names) or "-"))
    VARS.append(nm)

# ---- §6 現れ / §7 連結 / §8 行き先 ---------------------------------------
CON = {"pipes": 0, "concat": 0, "format": 0, "none": 0}
USES = []
for nm in VARS:
    br = re.compile("(?<![A-Za-z0-9_])" + re.escape(nm) + "(?![A-Za-z0-9_])")
    occ = [m.start() for m in br.finditer(s) if live(m.start())]
    print("---- var %s : live occurrences=%d lines=%s"
          % (nm, len(occ), ",".join(str(lineno(x)) for x in occ)))
    for i in occ:
        if i < decl_end: kind = "decl"
        else:
            a, b = stmt_span(i, floor)
            mi = re.search(r"(?i)(?<![A-Za-z0-9_])INTO(?![A-Za-z0-9_])", s[a:b])
            kind = "into" if (mi and a + mi.end() <= i) else "use"
        info = ""
        if kind == "use":
            ch = enclosing(i, floor)
            # 7a 左右の隣り
            j = i - 1
            while j >= floor and s[j] in " \t\r\n": j -= 1
            lft = s[max(floor, j-1):j+1]
            k = i + len(nm)
            while k < ceil and s[k] in " \t\r\n": k += 1
            rgt = s[k:k+2]
            pipes = (lft == "||") or (rgt == "||")
            cc = any(x.lower() in ("concat", "concat_ws") for x in ch)
            ff = any(x.lower() == "format" for x in ch)
            if pipes: CON["pipes"] += 1
            elif cc: CON["concat"] += 1
            elif ff: CON["format"] += 1
            else: CON["none"] += 1
            # §8 行き先
            e = i; d = 0
            while e < ceil:
                if live(e):
                    if s[e] == "(": d += 1
                    elif s[e] == ")": d -= 1
                    elif s[e] == ";" and d == 0: break
                e += 1
            st2 = i; d = 0
            while st2 > floor:
                if live(st2):
                    if s[st2] == ")": d += 1
                    elif s[st2] == "(": d -= 1
                    elif s[st2] == ";" and d == 0: break
                st2 -= 1
            head = re.match(r"[ \t\r\n]*([A-Za-z_][A-Za-z0-9_]*)[ \t\r\n]*:=", s[st2+1:e])
            sink = head.group(1) if head else "-"
            info = ("chain=%s pipes=%s concat=%s format=%s sink=%s"
                    % ("/".join(ch) or "-", pipes, cc, ff, sink))
        print("   L%-5d kind=%-5s %s" % (lineno(i), kind, info))
        if kind == "use": USES.append((nm, lineno(i), info))

print("CONCAT pipes=%d concat=%d format=%d none=%d (unit=use-occurrence)"
      % (CON["pipes"], CON["concat"], CON["format"], CON["none"]))

# ---- §8 返りへ ------------------------------------------------------------
for r in re.finditer(r"(?i)(?<![A-Za-z0-9_])RETURN(?![A-Za-z0-9_])[ \t]*([A-Za-z_][A-Za-z0-9_]*)?", s):
    if live(r.start()) and floor <= r.start() < ceil:
        print("RETURN at L%d value=%s" % (lineno(r.start()), r.group(1) or "-"))
# 母の中の二本の縦棒（此の函の内）
pp = [m.start() for m in re.finditer(re.escape("||"), s) if live(m.start()) and floor <= m.start() < ceil]
print("PIPES in owner fn=%d lines=%s" % (len(pp), ",".join(str(lineno(x)) for x in pp)))
print("DONE")
