# -*- coding: utf-8 -*-
"""order225 / E17 ―― ㋑在否を問ふ・㋒一行が母 を ★一つづつ★ 讀み直す（走 0・讀取のみ）

E16 で己は ㊅『器の分けが粗い』を ★己の疵として★ 数へた（any(re.search(..)) 5 件を ㋐ に入れた）。
條 二百六十九: ★分けの粗さは 分けた側の疵である★ ―― 『何処に居るか』でなく『何に使はれて居るか』で分けよ。
∴ 本弾は ★同じ粗さが ㋑ と ㋒ にも在るか★ を検める。

★網も分けも E16 の器から 逐語で写した（一字も変へぬ・條 二百七十一）★
  ―― call_name / build_parent / classify は order224 器の L21-L72 を ★機械が写した★。
  ★差 0 は §F で器自身に言はせる★。

E17 で足したは ★網の外★ のみ:
  ㊀ 親鎖(辿つた節点の型)を悉く出す
  ㊁ 値を現に使ふ徴(Attribute/Subscript/BinOp/JoinedStr/別の Call へ渡す)を数へる
  ㊂ 己の一族(order225_)を 含む／除く の二欄に分ける（條 二百六十四・二百六十八）
"""
import os, io, ast, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order225_e17_shape_recheck_v1.raw.txt")

WANT_ATTR = {("re", "search"): "re.search", ("re", "match"): "re.match"}
L = []
def say(x): L.append(x)


def call_name(nd):
    """返す: 網の名 or None"""
    f = nd.func
    if isinstance(f, ast.Name) and f.id == "next":
        return "next"
    if isinstance(f, ast.Attribute):
        v = f.value
        if isinstance(v, ast.Name) and (v.id, f.attr) in WANT_ATTR:
            return WANT_ATTR[(v.id, f.attr)]
        if f.attr == "find":
            return ".find"
    return None

def build_parent(tree):
    par = {}
    for nd in ast.walk(tree):
        for ch in ast.iter_child_nodes(nd):
            par[id(ch)] = nd
    return par

def classify(nd, par, tree):
    """㋐値を取る / ㋑在否を問ふ / ㋒一行が母 / ㋓判じ得ず"""
    # 上へ辿り 最初に出会ふ「使ひ方を決める」節点
    cur = nd
    seen_for = False
    for _ in range(12):
        up = par.get(id(cur))
        if up is None:
            return "㋓判じ得ず", "親が無い"
        if isinstance(up, (ast.If, ast.While, ast.Assert, ast.IfExp)):
            # test の中に居るか
            t = getattr(up, "test", None)
            if t is not None:
                for sub in ast.walk(t):
                    if sub is cur:
                        return "㋑在否を問ふ", type(up).__name__ + ".test"
            return "㋓判じ得ず", type(up).__name__ + "(test の外)"
        if isinstance(up, ast.UnaryOp) and isinstance(up.op, ast.Not):
            return "㋑在否を問ふ", "not"
        if isinstance(up, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return, ast.NamedExpr)):
            return "㋐値を取る", type(up).__name__
        if isinstance(up, ast.comprehension):
            return "㋒一行が母", "comprehension"
        if isinstance(up, (ast.For, ast.AsyncFor)):
            seen_for = True
        if isinstance(up, ast.Call):
            fn = getattr(up.func, "id", None) or getattr(up.func, "attr", None)
            if fn in ("bool", "assert_", "print", "say"):
                return "㋑在否を問ふ", "Call:" + str(fn)
            return "㋐値を取る", "Call:" + str(fn)
        cur = up
    return ("㋒一行が母" if seen_for else "㋓判じ得ず"), "上限まで辿つた"

# ===== 以上 ★E16 器からの逐語の写し★ / 以下 ★E17 で足した網の外★ =====

VALUE_MARK = (ast.Attribute, ast.Subscript, ast.BinOp, ast.JoinedStr, ast.FormattedValue)

def chain(nd, par):
    """当たり節点から 分けが決まる所まで 辿つた親の型名を悉く返す。"""
    out = []
    cur = nd
    for _ in range(12):
        up = par.get(id(cur))
        if up is None:
            out.append("(親が無い)"); break
        out.append(type(up).__name__)
        if isinstance(up, (ast.If, ast.While, ast.Assert, ast.IfExp)):
            break
        if isinstance(up, ast.UnaryOp) and isinstance(up.op, ast.Not):
            break
        if isinstance(up, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return, ast.NamedExpr)):
            break
        if isinstance(up, ast.comprehension):
            break
        if isinstance(up, ast.Call):
            break
        cur = up
    return out

def value_signs(nd, par):
    """★値を現に使ふ徴★ ―― 中間に Attribute/Subscript/BinOp/f-string が在るか。
    ※ Compare 単独は ★在否の言ひ換へ★(find(x) != -1)ゆゑ 徴に数へぬ。"""
    sig = []
    cur = nd
    for _ in range(12):
        up = par.get(id(cur))
        if up is None: break
        if isinstance(up, VALUE_MARK):
            sig.append(type(up).__name__ + (":" + up.attr if isinstance(up, ast.Attribute) else ""))
        if isinstance(up, (ast.If, ast.While, ast.Assert, ast.IfExp, ast.comprehension)):
            break
        if isinstance(up, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return, ast.NamedExpr)):
            break
        if isinstance(up, ast.UnaryOp) and isinstance(up.op, ast.Not):
            break
        if isinstance(up, ast.Call):
            break
        cur = up
    return sig

def is_mine(f):
    """★己の一族★ = 本弾(order225)で己が書いた器・生・紙。"""
    return os.path.basename(f).startswith("order225_")

def scan(names):
    rows = []; unread = 0; pf = 0
    for nm in names:
        ap = os.path.join(HERE, nm)
        try:
            text = io.open(ap, encoding="utf-8").read()
        except Exception:
            unread += 1; continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            pf += 1; continue
        par = build_parent(tree)
        lines = text.split(chr(10))
        for nd in ast.walk(tree):
            if not isinstance(nd, ast.Call): continue
            cn = call_name(nd)
            if cn is None: continue
            kind, why = classify(nd, par, tree)
            ln = getattr(nd, "lineno", 0)
            srcline = lines[ln-1].strip() if 0 < ln <= len(lines) else ""
            rows.append((nm, ln, cn, kind, why, srcline, chain(nd, par), value_signs(nd, par)))
    return rows, unread, pf

allpy = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
mine = [f for f in allpy if is_mine(f)]
notmine = [f for f in allpy if not is_mine(f)]

say("=== order225 / E17 ―― ㋑ と ㋒ を 一つづつ讀み直す ===")
say("母(含む 己の一族) = " + str(len(allpy)) + " 枚 ／ 母(除く) = " + str(len(notmine)) + " 枚")
say("★己の一族 = " + str(len(mine)) + " 枚★ ―― " + repr(sorted(mine)))
say("網・分け = ★E16 器 L21-L72 の逐語の写し（一字も変へず）★")
say("")

rows, unread, pf = scan(allpy)
rowsN, unreadN, pfN = scan(notmine)

def cnt(rs):
    a = {}
    for r in rs: a[r[3]] = a.get(r[3], 0) + 1
    return a

say("--- §零 和（★含む／除く の二欄★） ---")
ca, cn2 = cnt(rows), cnt(rowsN)
for k in sorted(set(list(ca.keys()) + list(cn2.keys()))):
    say("  " + k + " ―― 含む " + str(ca.get(k, 0)) + " / 除く " + str(cn2.get(k, 0)))
say("  和 ―― 含む " + str(len(rows)) + " / 除く " + str(len(rowsN)))
say("  讀めなんだ " + str(unread) + " / ast が解せなんだ " + str(pf))
say("")

say("--- §A ㋑在否を問ふ を 一つづつ ---")
kb = [r for r in rows if r[3] == "㋑在否を問ふ"]
say("㋑ = " + str(len(kb)) + " 箇所（母 含む " + str(len(allpy)) + " 枚）")
say("")
susp_b = []
for nm, ln, cn3, kind, why, srcline, ch, sig in kb:
    say("  " + nm + ":" + str(ln) + " [" + cn3 + "] 決め手=" + why)
    say("      親鎖: " + " -> ".join(ch))
    say("      値の徴: " + (repr(sig) if sig else "★無し★"))
    say("      逐語: " + (srcline[:120] + ("…" if len(srcline) > 120 else "")))
    if sig: susp_b.append((nm, ln, sig))
say("")
say("★㋑ の内 ★値の徴が現に在る★ = " + str(len(susp_b)) + " 箇所★")
for nm, ln, sig in susp_b:
    say("  ★要検★ " + nm + ":" + str(ln) + " 徴=" + repr(sig))
say("")

say("--- §B ㋒一行が母 を 一つづつ ---")
kc = [r for r in rows if r[3] == "㋒一行が母"]
say("㋒ = " + str(len(kc)) + " 箇所（母 含む " + str(len(allpy)) + " 枚）")
say("")
susp_c = []
for nm, ln, cn3, kind, why, srcline, ch, sig in kc:
    say("  " + nm + ":" + str(ln) + " [" + cn3 + "] 決め手=" + why)
    say("      親鎖: " + " -> ".join(ch))
    say("      値の徴: " + (repr(sig) if sig else "★無し★"))
    say("      逐語: " + (srcline[:120] + ("…" if len(srcline) > 120 else "")))
    if why == "上限まで辿つた":
        susp_c.append((nm, ln, why))
say("")
say("★㋒ の内 ★決め手が『上限まで辿つた』★（＝12 段辿つても決まらず for が在つたゆゑ ㋒ に落ちた）= "
    + str(len(susp_c)) + " 箇所★")
for nm, ln, why in susp_c:
    say("  ★要検★ " + nm + ":" + str(ln))
say("")

say("--- §C ㋓判じ得ず（分けの粗さが最も出る所） ---")
kd = [r for r in rows if r[3] == "㋓判じ得ず"]
say("㋓ = " + str(len(kd)) + " 箇所")
for nm, ln, cn3, kind, why, srcline, ch, sig in kd:
    say("  " + nm + ":" + str(ln) + " [" + cn3 + "] 決め手=" + why + " / 親鎖: " + " -> ".join(ch))
    say("      逐語: " + (srcline[:120] + ("…" if len(srcline) > 120 else "")))
say("")

say("--- §D 負の対照（★器が『値の徴』を現に出す口を持つか★・家老 165） ---")
NL = chr(10)
probe = ("import re" + NL
         + "if re.search('a', s).group(1) == 'x':" + NL + "    pass" + NL
         + "if re.search('b', s):" + NL + "    pass" + NL
         + "for l in [x for x in ys if re.search('c', x)]:" + NL + "    pass" + NL)
t2 = ast.parse(probe); p2 = build_parent(t2)
got = []
for nd in ast.walk(t2):
    if isinstance(nd, ast.Call) and call_name(nd):
        k2, w2 = classify(nd, p2, t2)
        got.append((k2, w2, value_signs(nd, p2)))
for g in got:
    say("  作り物 ⇒ " + repr(g))
say("★立つ／立たぬ の双方が現に出得る事を 上の三行が示す★")
say("  ―― ㋑ で値の徴が ★在る★ 物と ★無い★ 物、㋒ の物が 各 1 件づつ出て居るか を讀め")
say("現に無い path: exists=" + str(os.path.exists(os.path.join(HERE, "no_such_o225.py"))))
say("")

say("--- §E E16 の数との突合（★母が動いた分を名指す★） ---")
say("E16 の生に刷つた数 = ㋐ 21 / ㋑ 11 / ㋒ 9 / 和 41（母 83 枚・as_of 2026-09-09T11:17:30+09:00）")
say("本弾(含む) = ㋐ " + str(ca.get("㋐値を取る", 0)) + " / ㋑ " + str(ca.get("㋑在否を問ふ", 0))
    + " / ㋒ " + str(ca.get("㋒一行が母", 0)) + " / 和 " + str(len(rows)) + "（母 " + str(len(allpy)) + " 枚）")
say("★母は " + str(len(allpy) - 83) + " 枚 増えた ―― 増やしたは ★己★（order225 の器）★")
say("")

say("--- §F ★網・分けの逐語が E16 と差 0 である事を 器自身に言はせる★（條 二百七十一） ---")
me = io.open(os.path.abspath(__file__), encoding="utf-8").read()
o224 = io.open(os.path.join(HERE, "order224_e16_first_hit_triage_v1.rule.py"), encoding="utf-8").read()
core224 = chr(10).join(o224.split(chr(10))[20:72])
say("E16 器 L21-L72 が 本器に ★逐語で含まれるか★ = " + str(core224 in me))
say("其の長さ = " + str(len(core224)) + " 字 / sha256 頭16 = "
    + hashlib.sha256(core224.encode("utf-8")).hexdigest()[:16])

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
