# -*- coding: utf-8 -*-
"""order224 / E16 ―― 「最初の当たりで決める」53 箇所を ★一つづつ★ 判ずる（走 0・讀取のみ）

條 二百六十三: ★『最初の当たり』で決める網は 当たりの数を先に数へよ★

判ずる形（★ast で 棲家を分ける★・字の網ではない）:
  ㋐ 値を取る   = 当たりから ★数・逐語★ を引く（Assign/Return/f-string 等）★條の掛かり★
  ㋑ 在否を問ふ = if/while/assert/not の中でのみ使ふ ★條の外★（在れば足る・二つ目は要らぬ）
  ㋒ 一行が母   = for の中で ★一行づつ★ に当てる ★條の外★（母が一行ゆゑ 二つ目が別の母に成らぬ）
  ㋓ 判じ得ず   = 上の何れにも定まらぬ
"""
import os, io, ast, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order224_e16_first_hit_triage_v1.raw.txt")

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

names = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
say("=== order224 / E16 ―― 『最初の当たりで決める』箇所を 一つづつ判ずる ===")
say("母 = 本席 dir の .py 悉く = " + str(len(names)) + " 枚")
say("網 = ★ast★（re.search / re.match / .find / next の Call 節点）※字の網ではない")
say("")

rows = []
unread = 0; pf = 0
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
        if not isinstance(nd, ast.Call):
            continue
        cn = call_name(nd)
        if cn is None:
            continue
        kind, why = classify(nd, par, tree)
        ln = getattr(nd, "lineno", 0)
        src = lines[ln-1].strip() if 0 < ln <= len(lines) else ""
        rows.append((nm, ln, cn, kind, why, src))

say("--- §A 一つづつ（★逐語を併記★・床⑽） ---")
for nm, ln, cn, kind, why, src in rows:
    say("  " + nm + ":" + str(ln) + " [" + cn + "] " + kind + "(" + why + ")")
    say("      逐語: " + (src[:120] + ("…" if len(src) > 120 else "")))
say("")

say("--- §B 種ごとの和 ---")
agg = {}
for r in rows:
    agg[r[3]] = agg.get(r[3], 0) + 1
for k in sorted(agg.keys()):
    say("  " + k + " = " + str(agg[k]))
say("★ast で拾つた和 = " + str(len(rows)) + " 箇所（母 " + str(len(names)) + " 枚・讀めなんだ "
    + str(unread) + " / ast が解せなんだ " + str(pf) + "）★")
say("")

say("--- §C ★條 二百六十三 が現に掛かるは ㋐ のみ★ ---")
ka = [r for r in rows if r[3] == "㋐値を取る"]
say("㋐ = " + str(len(ka)) + " 箇所 ―― ★此処が『当たりの数を先に数へよ』の掛かり先★")
for nm, ln, cn, kind, why, src in ka:
    say("  ★要検★ " + nm + ":" + str(ln) + " [" + cn + "]")
say("")
say("※★但し ㋐ の悉くが 疵ではない★ ―― 当たりが 2 件以上 ★立ち得る母★ に当てて居る物のみが疵である。")
say("※其の別は ★母（食はせる text）を一つづつ読まねば決まらぬ★ ゆゑ 本弾では ★測定不能★。")
say("")

say("--- §D 字の網（v2・53 箇所）との差 ---")
say("字の網の和 = 53 / ast の和 = " + str(len(rows)))
say("★差 = " + str(53 - len(rows)) + "★ ―― 因は ①字の網が ★己の網の定義行(PATS)★ を拾ふ")
say("  ②`head -1` `grep -m1` は ★python の Call に非ず★（shell の字）ゆゑ ast に映らぬ")
say("  ③字の網は 註釈・文字列の中の名も拾ふ")
say("★∴ 53 と " + str(len(rows)) + " は ★別の物を数へた数★ である ―― 足すな・引いて疵と呼ぶな★")
say("")

say("--- §E 負の対照 ---")
probe = "import re" + chr(10)       + "m = re.search('x', s)" + chr(10)       + "if re.search('y', s):" + chr(10) + "    pass" + chr(10)
t2 = ast.parse(probe); p2 = build_parent(t2)
got = []
for nd in ast.walk(t2):
    if isinstance(nd, ast.Call) and call_name(nd):
        got.append(classify(nd, p2, t2)[0])
say("作り物（値を取る 1 ＋ 在否を問ふ 1）を食はせた結果 = " + repr(sorted(got)))
say("★器は ㋐ と ㋑ の双方を出す口を現に持つ★（家老 165）")
say("現に無い path: exists=" + str(os.path.exists(os.path.join(HERE, "no_such_o224.py"))))

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
