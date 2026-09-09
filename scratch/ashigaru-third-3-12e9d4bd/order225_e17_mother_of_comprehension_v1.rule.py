# -*- coding: utf-8 -*-
"""order225 / E17 追ひ ―― ★㋒『一行が母』の 母を 現に測る★（走 0・讀取のみ）

E17 一発目(order225_e17_shape_recheck_v1)で二つ判つた:
  ㊀ ★㋑ に『値の徴』を探す問ひは 検出力が現に無い★
     ―― classify は Attribute 経由の Call を ★先に★ ㋐ へ落とす ゆゑ、
        ㋑ に落ちた物へ徴を探しても ★0 しか出ぬ★（負の対照の一行目が現に ㋐ へ落ちた）。
  ㊁ ★㋒ 9 件の逐語を讀むと 母が『一行』でない物が現に在る★
     ―― `[f for f in OUT if re.search(T1, txt[f])]` の母は ★txt[f] = file 全文★ である。

∴ 本器は ★㋒ の母を ast で引いて 一行か否かを判ずる材料を出す★。
   ★判は器に言はせず 己が紙で書く★（條 二百六十一 の精神・器は数へるまで）。

★網・分けは E16 器 L21-L72 の逐語の写し（一字も変へぬ・條 二百七十一）★
"""
import os, io, ast, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order225_e17_mother_of_comprehension_v1.raw.txt")

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

# ===== 以上 ★E16 器からの逐語の写し★ / 以下 ★E17 追ひで足した網の外★ =====

def src_of(nd, text):
    """節点の逐語（ast.get_source_segment・無ければ行を返す）"""
    try:
        g = ast.get_source_segment(text, nd)
        if g: return " ".join(g.split())
    except Exception:
        pass
    ln = getattr(nd, "lineno", 0)
    lines = text.split(chr(10))
    return lines[ln-1].strip() if 0 < ln <= len(lines) else ""

def target_names(t):
    """comprehension の target に現れる名を悉く"""
    return sorted(set(x.id for x in ast.walk(t) if isinstance(x, ast.Name)))

def arg_shape(nd):
    """網を当てる相手（第 2 引数）の ast の形と 現れる名"""
    if len(nd.args) < 2: return "(引数が 2 に満たぬ)", []
    a = nd.args[1]
    return type(a).__name__, sorted(set(x.id for x in ast.walk(a) if isinstance(x, ast.Name)))

def enclosing_comp(nd, par):
    """当たり節点を包む comprehension 節点（無ければ None）"""
    cur = nd
    for _ in range(12):
        up = par.get(id(cur))
        if up is None: return None
        if isinstance(up, ast.comprehension): return up
        cur = up
    return None

names = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
say("=== order225 / E17 追ひ ―― ㋒『一行が母』の 母を 現に測る ===")
say("母(本席 dir の .py 悉く) = " + str(len(names)) + " 枚")
say("網・分け = ★E16 器 L21-L72 の逐語の写し（一字も変へず）★")
say("")

rows = []
for nm in names:
    ap = os.path.join(HERE, nm)
    try:
        text = io.open(ap, encoding="utf-8").read()
    except Exception:
        continue
    try:
        tree = ast.parse(text)
    except SyntaxError:
        continue
    par = build_parent(tree)
    for nd in ast.walk(tree):
        if not isinstance(nd, ast.Call): continue
        cn = call_name(nd)
        if cn is None: continue
        kind, why = classify(nd, par, tree)
        if kind != "㋒一行が母": continue
        comp = enclosing_comp(nd, par)
        sh, anames = arg_shape(nd)
        rows.append((nm, getattr(nd, "lineno", 0), cn, why,
                     src_of(nd, text),
                     (src_of(comp.target, text) if comp is not None else "(comprehension が無い)"),
                     (src_of(comp.iter, text) if comp is not None else "(comprehension が無い)"),
                     (target_names(comp.target) if comp is not None else []),
                     sh, anames))

say("--- §A ㋒ と判じた箇所の ★母★（一つづつ・逐語は切らぬ） ---")
say("㋒ = " + str(len(rows)) + " 箇所")
say("")
for nm, ln, cn, why, s_call, s_tgt, s_iter, tnames, sh, anames in rows:
    say("  ● " + nm + ":" + str(ln) + " [" + cn + "] 決め手=" + why)
    say("      当たりの逐語 : " + s_call)
    say("      ★網を当てる相手★ : 形=" + sh + " / 名=" + repr(anames))
    say("      comprehension の target : " + s_tgt + "  名=" + repr(tnames))
    say("      comprehension の iter   : " + s_iter)
    ov = [x for x in anames if x in tnames]
    say("      ★相手と target が名を共有するか★ = " + (repr(ov) if ov else "★せぬ★"))
    say("")

say("--- §B 形ごとの和（★判ではなく 数★） ---")
agg = {}
for r in rows:
    agg[r[8]] = agg.get(r[8], 0) + 1
for k in sorted(agg.keys()):
    say("  網を当てる相手の形 " + k + " = " + str(agg[k]) + " 箇所")
say("")
say("  ※★『相手が Name』は 母が iter の一要素である事を ★示唆する★ に留まる★")
say("  ※★『相手が Subscript』は 母が ★別の入れ物の中身★ である事を示唆する★")
say("  ※★何れも『一行か否か』を ★断ずるには iter の中身を讀まねばならぬ★★ ―― 判は紙で己が書く")
say("")

say("--- §C 負の対照（★器が 二つの形を現に分ける口を持つか★・家老 165） ---")
NL = chr(10)
probe = ("import re" + NL
         + "a = [l for l in s.split('x') if re.search('p', l)]" + NL
         + "b = [f for f in FS if re.search('p', txt[f])]" + NL)
t2 = ast.parse(probe); p2 = build_parent(t2)
got = []
for nd in ast.walk(t2):
    if isinstance(nd, ast.Call) and call_name(nd):
        k2, w2 = classify(nd, p2, t2)
        comp = enclosing_comp(nd, p2)
        sh2, an2 = arg_shape(nd)
        tn2 = target_names(comp.target) if comp is not None else []
        got.append((k2, sh2, an2, tn2, [x for x in an2 if x in tn2]))
for g in got:
    say("  作り物 ⇒ " + repr(g))
say("★Name(共有 有り) と Subscript(共有 有り) の双方が現に出る★")
say("現に無い path: exists=" + str(os.path.exists(os.path.join(HERE, "no_such_o225b.py"))))
say("")

say("--- §D ★網・分けの逐語が E16 と差 0★（條 二百七十一） ---")
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
