# -*- coding: utf-8 -*-
"""order226 / E21 ★門と検出力を先に測る★ ―― ㋐ 21 件に「網が回る」形が潜むか（走 0・讀取のみ）

★本器は 答を出す器ではない。★撃つてよいか★ を判ずる器である。★（立条）

E17 で己は ★門と検出力を測らずに撃ち★、後から「其の問ひは 0 しか出ぬ問ひであつた」と知つた（條 二百七十三）。
∴ 本弾は ★先に門を数へ、母が足らねば 撃たずに其れを答として申す★。

問ひ: ㋐値を取る 21 件に、E17 §七 で見つけた ★第四の形『網が回る』★ が潜むか。

門(gate)   = ㋐ 21 件の内 ★包む for / comprehension が現に在る★ 数（之が母）
検出力(power) = 作り物で ★網が回る★『母が回る』『何れも回らぬ』の ★三つが現に出分けるか★

★包む節点を探す辿りは 分けの外に置く★（條 二百七十三 ―― 疵は分けの外からしか見えぬ）。
"""
import os, io, ast, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "order226_e21_gate_and_power_v1.raw.txt")

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

# ===== 以上 ★E16 器からの逐語の写し（分け）★ / 以下 ★E21 で足した 分けの外★ =====

def enclosing_loops(nd, par):
    """★分けの外の辿り★ ―― 上へ 40 段辿り 包む for / comprehension を悉く返す。
    ※ classify の break 条件は ★一切見ぬ★（分けの外ゆゑ）。"""
    out = []
    cur = nd
    for _ in range(40):
        up = par.get(id(cur))
        if up is None: break
        if isinstance(up, ast.comprehension):
            out.append(("comprehension", up.target, up.iter))
        elif isinstance(up, (ast.For, ast.AsyncFor)):
            out.append(("For", up.target, up.iter))
        cur = up
    return out

def names_in(nd):
    return sorted(set(x.id for x in ast.walk(nd) if isinstance(x, ast.Name)))

def arg_names(nd, i):
    if len(nd.args) <= i: return None
    return names_in(nd.args[i])

def spin(nd, par):
    """★何が回つて居るか★ ―― ('網', ...) / ('母', ...) / ('何れも回らぬ', ...) / ('包む輪が無い', ...)"""
    loops = enclosing_loops(nd, par)
    if not loops:
        return "包む輪が無い", [], []
    tnames = []
    for kind, tgt, it in loops:
        tnames += names_in(tgt)
    tnames = sorted(set(tnames))
    a0 = arg_names(nd, 0) or []
    a1 = arg_names(nd, 1) or []
    net = [x for x in a0 if x in tnames]
    haha = [x for x in a1 if x in tnames]
    if net and not haha: return "網が回る", net, haha
    if haha and not net: return "母が回る", net, haha
    if net and haha:     return "★双方が回る★", net, haha
    return "何れも回らぬ", net, haha

def src_of(nd, text):
    try:
        g = ast.get_source_segment(text, nd)
        if g: return " ".join(g.split())
    except Exception:
        pass
    ln = getattr(nd, "lineno", 0)
    lines = text.split(chr(10))
    return lines[ln-1].strip() if 0 < ln <= len(lines) else ""

names = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
say("=== order226 / E21 ★門と検出力を先に測る★（答を出す器ではない） ===")
say("母(本席 dir の .py 悉く) = " + str(len(names)) + " 枚")
say("網・分け = ★E16 器 L21-L72 の逐語の写し（一字も変へず・條 二百七十一）★")
say("★包む輪を探す辿りは 分けの外に置いた★（條 二百七十三）")
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
        loops = enclosing_loops(nd, par)
        sp, net, haha = spin(nd, par)
        rows.append((nm, getattr(nd, "lineno", 0), cn, kind, why, sp, net, haha,
                     [k for k, t, i in loops], src_of(nd, text), tree, par, nd, text))

ka = [r for r in rows if r[3] == "㋐値を取る"]

say("--- §一 ★門★（母が足るか） ---")
say("㋐値を取る = " + str(len(ka)) + " 件")
have = [r for r in ka if r[8]]
say("★内 包む輪(for / comprehension)が現に在る = " + str(len(have)) + " 件★ ―― ★之が本問ひの母★")
say("★包む輪が無い = " + str(len(ka) - len(have)) + " 件★ ―― 網も母も回らぬ ゆゑ 本問ひの外")
say("")
say("包む輪の種ごと:")
agg = {}
for r in have:
    k = "+".join(r[8])
    agg[k] = agg.get(k, 0) + 1
for k in sorted(agg.keys()):
    say("  " + k + " = " + str(agg[k]) + " 件")
say("")

say("--- §二 ★検出力★（三つが現に出分けるか） ---")
NL = chr(10)
probe = ("import re" + NL
         + "for p in PATS:" + NL + "    m = re.search(p, s)" + NL
         + "for l in LS:" + NL + "    m2 = re.search(PAT, l)" + NL
         + "for k in KS:" + NL + "    m3 = re.search(PAT, s)" + NL
         + "for q in QS:" + NL + "    m4 = re.search(q, q)" + NL)
t2 = ast.parse(probe); p2 = build_parent(t2)
got = []
for nd in ast.walk(t2):
    if isinstance(nd, ast.Call) and call_name(nd):
        k2, w2 = classify(nd, p2, t2)
        sp2, n2, h2 = spin(nd, p2)
        got.append((k2, sp2, n2, h2))
for g in got:
    say("  作り物 ⇒ " + repr(g))
kinds = sorted(set(g[1] for g in got))
say("★出分けた種 = " + repr(kinds) + "（" + str(len(kinds)) + " 種）★")
say("★之が 1 種しか出ぬなら 器に口が無い ―― 撃つても 0 しか出ぬ★（條 二百七十三）")
say("現に無い path: exists=" + str(os.path.exists(os.path.join(HERE, "no_such_o226.py"))))
say("")

say("--- §三 ★門を通つたか★ ---")
ok_gate = len(have) > 0
ok_power = len(kinds) >= 3
say("門(母 >= 1) = " + str(ok_gate) + "（母 = " + str(len(have)) + " 件）")
say("検出力(種 >= 3) = " + str(ok_power) + "（現に出分けた種 = " + str(len(kinds)) + "）")
if not ok_gate:
    say("★∴ 撃たぬ。母が足らぬ事を 答として申す（測定不能）★")
elif not ok_power:
    say("★∴ 撃たぬ。器に口が無い事を 答として申す（測定不能）★")
else:
    say("★∴ 門を通つた ―― 下 §四 で 本測に進む★")
say("")

if ok_gate and ok_power:
    say("--- §四 本測 ―― ㋐ の内 包む輪が在る " + str(len(have)) + " 件を 一つづつ ---")
    agg2 = {}
    for r in have:
        agg2[r[5]] = agg2.get(r[5], 0) + 1
    for k in sorted(agg2.keys()):
        say("  ★" + k + " = " + str(agg2[k]) + " 件★")
    say("")
    for nm, ln, cn, kind, why, sp, net, haha, lk, s_call, tr, pr, nd0, tx in have:
        say("  ● " + nm + ":" + str(ln) + " [" + cn + "] 分け=" + kind + "(" + why + ")")
        say("      ★何が回るか★ = " + sp + " / 網に回る名=" + repr(net) + " / 母に回る名=" + repr(haha))
        say("      包む輪 = " + "+".join(lk))
        say("      逐語: " + s_call)
        say("")

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
