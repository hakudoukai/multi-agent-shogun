# -*- coding: utf-8 -*-
"""order227 / E22 ★門の外は 真に回らぬのか ―― 輪が呼手に居る形を数へる★（走 0・讀取のみ）

★的一行★ = E21(order226 v2) が「包む輪が無い」と断じた件は、★真に回らぬ★ のか、
           それとも ★輪が 己の外(呼手)に居る★ のか。

★本器で一字も変へぬ物★:
  ・分け(call_name / build_parent / classify) = E16 器 L21-L72 の逐語（條 二百七十一）
  ・輪の辿り(COMP_NODES / enclosing_loops / names_in / arg_names / spin) = order226 v2 の逐語
★本器で足す物★ = ★呼手の辿り★（同 file 内で 当たりを含む def が 輪の中から呼ばれて居るか）
★本器で別に測る物★ = 己の一族を母から外した時の数（E23・條 二百七十五 の始末）
"""
import os, io, ast, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTP = os.path.join(HERE, "order227_e22_loop_in_caller_v1.raw.txt")
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
# ===== 以上 ★逐語の写し★ / 以下 ★E22 で足した 呼手の辿り★ =====

def enclosing_def(nd, par):
    """当たりを包む一番近い def / lambda を返す。無ければ None。"""
    cur = nd
    for _ in range(60):
        up = par.get(id(cur))
        if up is None: return None
        if isinstance(up, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)): return up
        cur = up
    return None

def call_sites(tree, name):
    """同 file 内で 名 name を ★呼ぶ★ 節点を悉く返す（Name 呼出のみ）。"""
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name]

def caller_verdict(nd, tree, par):
    """★輪は呼手に居るか★ ―― 五つに分ける。
    ㋐ 包む def が無い       -> 「def の外に居る」（呼手の問ひが立たぬ）
    ㋑ 包む def が lambda     -> 「lambda ゆゑ名で呼手を引けぬ」（測定不能）
    ㋒ 同 file に呼手 0 本    -> 「同 file に呼手が無い」（★母が空＝測定不能★・條 二百七十）
    ㋓ 呼手の内 輪の中が 1 本以上 -> 「★呼手が回る★」
    ㋔ 呼手は在るが 悉く輪の外 -> 「呼手も回らぬ」
    """
    d = enclosing_def(nd, par)
    if d is None: return ("def の外に居る", "(無し)", 0, 0)
    if isinstance(d, ast.Lambda): return ("lambda ゆゑ名で呼手を引けぬ", "(lambda)", 0, 0)
    sites = call_sites(tree, d.name)
    if not sites: return ("同 file に呼手が無い", d.name, 0, 0)
    spun = len([c for c in sites if enclosing_loops(c, par)])
    if spun: return ("★呼手が回る★", d.name, len(sites), spun)
    return ("呼手も回らぬ", d.name, len(sites), 0)

def src_of(nd, text):
    try:
        g = ast.get_source_segment(text, nd)
        if g: return " ".join(g.split())
    except Exception:
        pass
    ln = getattr(nd, "lineno", 0)
    lines = text.split(chr(10))
    return lines[ln-1].strip() if 0 < ln <= len(lines) else ""

def is_mine(f):
    """★己の一族の定め（條 二百七十五）★ ―― 本席が本 lot で書いた器の接頭辞を悉く挙げる。"""
    b = os.path.basename(f)
    return b[:9] in ("order224_", "order225_", "order226_", "order227_")

def scan(names):
    rows = []
    for f in names:
        try:
            src = io.open(os.path.join(HERE, f), encoding="utf-8").read()
            tree = ast.parse(src)
        except Exception:
            continue
        par = build_parent(tree)
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call): continue
            if call_name(n) is None: continue
            kind, where = classify(n, par, tree)
            rows.append((f, n.lineno, call_name(n), kind, where, spin(n, par), n, par, tree, src_of(n, src)))
    return rows

COMP_NODES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)

def enclosing_loops(nd, par):
    """★分けの外の辿り★ ―― 上へ 40 段辿り 包む輪を悉く返す。
    ※ classify の break 条件は ★一切見ぬ★（分けの外ゆゑ）。

    ★v1 の疵（本器で直した所）★:
      v1 は ast.comprehension 節点のみを輪とした。而して ★内包の elt に居る当たりは
      comprehension を親に持たぬ★（親は ListComp / GeneratorExp 本体）。
      ∴ `any(re.search(p,l) for p in DECL)` の ★網 p を 悉く取り落した★。
      本器は ★内包本体(ListComp/SetComp/DictComp/GeneratorExp)の generators も輪として拾ふ★。"""
    out = []
    cur = nd
    for _ in range(40):
        up = par.get(id(cur))
        if up is None: break
        if isinstance(up, ast.comprehension):
            out.append(("comprehension", up.target, up.iter))
        elif isinstance(up, COMP_NODES):
            for g in up.generators:
                out.append((type(up).__name__, g.target, g.iter))
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


KA = "\u32d0値を取る".encode("ascii").decode("unicode_escape") if False else None
A = chr(0x32d0) + "値を取る"

say("=== order227 / E22 ★門の外は 真に回らぬのか★ ===")
say("★的一行★ = E21 が「包む輪が無い」と断じた件は 真に回らぬか ★輪が呼手に居る★ か")
say("分け = E16 器 L21-L72 の逐語 / 輪の辿り = order226 v2 の逐語（★双方 一字も変へず★）")
say("")

names_all = sorted([f for f in os.listdir(HERE) if f.endswith(".py")])
mine = [f for f in names_all if is_mine(f)]
names_out = [f for f in names_all if not is_mine(f)]
say("--- §零 ★母★ ---")
say("母(本席 dir の .py 悉く) = " + str(len(names_all)) + " 枚 / ★己の一族 = " + str(len(mine)) + " 枚★ / ★一族を外した母 = " + str(len(names_out)) + " 枚★")
say("一族の名: " + ", ".join(mine))
say("")

say("--- §一 ★E23 一族を外した時の数★（分けも輪の辿りも一字も変へず・動かすは母のみ） ---")
for tag, nm in (("一族を含む", names_all), ("★一族を外した★", names_out)):
    rows = scan(nm)
    aa = [r for r in rows if r[3] == A]
    have = [r for r in aa if r[5][0] != "包む輪が無い"]
    agg = {}
    for r in have:
        agg[r[5][0]] = agg.get(r[5][0], 0) + 1
    say("  " + tag + ": 母=" + str(len(nm)) + "枚 / " + A + "=" + str(len(aa)) + "件 / 門=" + str(len(have)) + "件 / 門外=" + str(len(aa) - len(have)) + "件")
    say("      門の内訳: " + ", ".join([k + " " + str(agg[k]) for k in sorted(agg)]))
say("")

say("--- §二 ★検出力★（呼手の辿りが 現に出分けるか） ---")
N2 = chr(10)
probe = ("import re" + N2
 + "def f1(x):" + N2 + "    return re.search(PAT, x)" + N2
 + "for a in AS:" + N2 + "    f1(a)" + N2
 + "def f2(x):" + N2 + "    return re.search(PAT, x)" + N2
 + "f2(1)" + N2
 + "def f3(x):" + N2 + "    return re.search(PAT, x)" + N2
 + "def f4(x):" + N2 + "    return re.search(PAT, x)" + N2
 + "zz = [f4(b) for b in BS]" + N2
 + "g = lambda y: re.search(PAT, y)" + N2
 + "TOPV = re.search(PAT, TOP)" + N2)
t2 = ast.parse(probe)
p2 = build_parent(t2)
kinds2 = []
for n in ast.walk(t2):
    if isinstance(n, ast.Call) and call_name(n) == "re.search":
        v = caller_verdict(n, t2, p2)
        kinds2.append(v[0])
        say("  作り物 => " + repr(v))
say("★出分けた種 = " + repr(sorted(set(kinds2))) + "（" + str(len(set(kinds2))) + " 種）★")
say("現に無い path: exists=" + str(os.path.exists(os.path.join(HERE, "no_such_o227.py"))))
say("")

rows = scan(names_all)
aa = [r for r in rows if r[3] == A]
outside = [r for r in aa if r[5][0] == "包む輪が無い"]
say("--- §三 ★門★（母が足るか） ---")
say(A + " = " + str(len(aa)) + " 件 / ★内 包む輪が無い = " + str(len(outside)) + " 件★ ―― ★之が本問ひの母★")
ok_gate = len(outside) > 0
ok_power = len(set(kinds2)) >= 3
say("門(母 >= 1) = " + str(ok_gate) + " / 検出力(種 >= 3) = " + str(ok_power) + "（現に出分けた種 = " + str(len(set(kinds2))) + "）")
if not ok_gate:
    say("★∴ 撃たぬ。母が足らぬ事を 答として申す（測定不能）★")
elif not ok_power:
    say("★∴ 撃たぬ。器に口が無い事を 答として申す（測定不能）★")
else:
    say("★∴ 門を通つた ―― 下 §四 で 本測に進む★")
    say("")
    say("--- §四 本測 ―― 門外 " + str(len(outside)) + " 件を 一つづつ ---")
    agg2 = {}
    got = []
    for r in outside:
        f, ln, cn, kind, where, sp, nd, par, tree, verb = r
        v = caller_verdict(nd, tree, par)
        agg2[v[0]] = agg2.get(v[0], 0) + 1
        got.append((f, ln, cn, where, v, verb))
    for k in sorted(agg2):
        say("  ★" + k + " = " + str(agg2[k]) + " 件★")
    say("")
    for f, ln, cn, where, v, verb in got:
        say("  ● " + f + ":" + str(ln) + " [" + cn + "] 分け=" + A + "(" + where + ")")
        say("      ★輪は呼手に居るか★ = " + v[0])
        say("      包む def = " + v[1] + " / 同 file の呼手 = " + str(v[2]) + " 本 / 内 輪の中 = " + str(v[3]) + " 本")
        say("      逐語: " + verb)
        say("")

io.open(OUTP, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))
raw = io.open(OUTP, "rb").read()
print("wrote " + OUTP)
print("raw_sha256=" + hashlib.sha256(raw).hexdigest())
txt = raw.decode("utf-8")
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
