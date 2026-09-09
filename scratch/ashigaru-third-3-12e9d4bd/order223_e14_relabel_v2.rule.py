# -*- coding: utf-8 -*-
"""order223 / E14 ―― 「狭 11」に語を足して直す（走 0・讀取のみ）

令: ①数でなく語を足す ②前紙は封じ後継で併記 ③別母 1484 枚の代入形も同じ語で
    ④直した後 同じ語で数へ直して ★差 0★ を示せ

差 0 の当て方（見込みを写さぬ為・見込み ㋖）:
  ★order222 の生 file から 数を讀み取り★、本弾で数へ直した数と突き合はせる。
  己の記憶・見込みの数は一つも使はぬ。
"""
import os, io, ast, re, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = "/home/hakudoukai/a3/wt-bundle-fix4"
PIN = "47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b"
PREV_RAW = os.path.join(HERE, "order222_e13_narrow_wide_v1.raw.txt")
OUT = os.path.join(HERE, "order223_e14_relabel_v2.raw.txt")

FILES = [
    "backend/tests/test_cmd004_cross_cutting_integration.py",
    "tests/test_step_a4_handover_sheet.py",
    "tests/test_step_q.py",
    "tests/test_step_r_ui.py",
    "tests/test_step_s3.py",
    "tests/test_step_s4.py",
]

L = []
def say(x): L.append(x)

def git(args):
    pr = subprocess.Popen(["git", "-C", TREE] + args,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = pr.communicate()
    return pr.returncode, o, e

def n1_narrow(text):
    sk = 0; sf = 0
    for ln in text.split(chr(10)):
        t = ln.lstrip()
        if t.startswith("@pytest.mark.skipif("): sf += 1
        elif t.startswith("@pytest.mark.skip("): sk += 1
    return sk, sf

def n2_wide(text):
    return text.count("pytest.mark.skip("), text.count("pytest.mark.skipif(")

def is_pm(node, want):
    if not isinstance(node, ast.Call): return False
    f = node.func
    if not isinstance(f, ast.Attribute) or f.attr != want: return False
    v = f.value
    if not isinstance(v, ast.Attribute) or v.attr != "mark": return False
    w = v.value
    return isinstance(w, ast.Name) and w.id == "pytest"

def n3_ast(text):
    tree = ast.parse(text)
    deco = {}
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "decorator_class" if isinstance(nd, ast.ClassDef) else "decorator_func"
            for d in nd.decorator_list:
                for sub in ast.walk(d): deco[id(sub)] = kind
    assigns = {}
    for nd in tree.body:
        if isinstance(nd, ast.Assign):
            names = [t.id for t in nd.targets if isinstance(t, ast.Name)]
            tag = "assign_module_pytestmark" if "pytestmark" in names else "assign_other"
            val = nd.value
            if isinstance(val, (ast.List, ast.Tuple)):
                tag = tag + "_list"
                for el in val.elts:
                    for sub in ast.walk(el): assigns[id(sub)] = tag
            else:
                for sub in ast.walk(val): assigns[id(sub)] = tag
    homes = {}
    n = 0
    for nd in ast.walk(tree):
        for want in ("skip", "skipif"):
            if is_pm(nd, want):
                n += 1
                h = deco.get(id(nd)) or assigns.get(id(nd)) or "bare"
                homes[h] = homes.get(h, 0) + 1
    return n, homes

def GO(narrow, homes, ast_n, label):
    """★語形★ = <網>=<数>(class 飾 a ＋ func 飾 b・代入形 c は 含まず)"""
    a = homes.get("decorator_class", 0)
    b = homes.get("decorator_func", 0)
    c = sum(v for k, v in homes.items() if k.startswith("assign"))
    other = ast_n - a - b - c
    s = label + " 狭網=" + str(narrow) + "(class 飾 " + str(a) + " ＋ func 飾 " + str(b)         + "・代入形 " + str(c) + " は 含まず)"
    s += " / ast網=" + str(ast_n) + "(class 飾 " + str(a) + " ＋ func 飾 " + str(b)         + " ＋ 代入形 " + str(c) + ")"
    if other: s += " ★其の外 " + str(other) + "★"
    s += " ※★覆ふ試験の数は 別★（class 飾は中の試験 N 本・func 飾は 1 本・代入形は file 悉くを覆ふ）"
    return s, a, b, c, other

say("=== order223 / E14 v2 ―― 語を足して直す（数は動かさぬ） ===")
say("★v2 の由★: v1 は 生から数を讀む網が ★最初の当たり★ を拾ひ、別母の棲家に 6 枚母の数(8/3)を当てた。")
say("★数が動いたのではない ―― 動いたは 己の讀取網である（條 二百五十三）★")
say("TREE=" + TREE + " / PIN=" + PIN)
rc, o, e = git(["rev-parse", "HEAD"]); say("的の樹 HEAD(走の前)=" + o.decode("utf-8").strip())
rc, o, e = git(["status", "--porcelain"])
say("的の樹 porcelain(走の前)=" + str(len([x for x in o.decode('utf-8').split(chr(10)) if x])) + " 行")
say("")

# ---------- §A 母 = 6 枚 ----------
say("--- §A 母 = porcelain の 6 枚（前=blob 47c8bc3b / 今=作業樹） ---")
res = {}
for side in ("前", "今"):
    tn1 = 0; tn2 = 0; tn3 = 0; homes = {}
    for rel in FILES:
        if side == "前":
            rc, out, err = git(["show", PIN + ":" + rel]); assert rc == 0, "BLOB_MISS " + rel
            text = out.decode("utf-8")
        else:
            text = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
        s1, f1 = n1_narrow(text); s2, f2 = n2_wide(text)
        n3, h = n3_ast(text)
        tn1 += s1 + f1; tn2 += s2 + f2; tn3 += n3
        for k, v in h.items(): homes[k] = homes.get(k, 0) + v
    line, a, b, c, other = GO(tn1, homes, tn3, side + "(母 6 枚)")
    say(line)
    res[side] = dict(n1=tn1, n2=tn2, n3=tn3, a=a, b=b, c=c, other=other)
    say(side + "(母 6 枚) 広網=" + str(tn2) + "（字の出現・棲家を問はぬ）")
    say(side + "(母 6 枚) ★狭網 ＋ 代入形 = " + str(tn1 + c) + " / ast網 = " + str(tn3)
        + " ⇒ 一致=" + str(tn1 + c == tn3) + "★")
say("")

# ---------- §B 別母 = 追跡下 .py 悉く ----------
say("--- §B ★別母★ = 的の樹の追跡下 .py 悉く（今の姿のみ） ---")
rc, out, err = git(["ls-files", "*.py"]); assert rc == 0, "LSFILES_FAIL"
allpy = [x for x in out.decode("utf-8").split(chr(10)) if x]
bn1 = 0; bn2 = 0; bn3 = 0; bhomes = {}; hit = 0; unread = 0; pf = 0; assign_where = []
for rel in allpy:
    ap = os.path.join(TREE, rel)
    if not os.path.exists(ap): unread += 1; continue
    try: text = io.open(ap, encoding="utf-8").read()
    except Exception: unread += 1; continue
    if "pytest.mark.skip" not in text: continue
    try: n3, h = n3_ast(text)
    except SyntaxError: pf += 1; continue
    if not n3: continue
    hit += 1
    s1, f1 = n1_narrow(text); s2, f2 = n2_wide(text)
    bn1 += s1 + f1; bn2 += s2 + f2; bn3 += n3
    for k, v in h.items(): bhomes[k] = bhomes.get(k, 0) + v
    if any(k.startswith("assign") for k in h):
        for k, v in h.items():
            if k.startswith("assign"):
                assign_where.append(rel + " [" + k + " ×" + str(v) + "]")
say("別母 N(追跡下 .py) = " + str(len(allpy)) + " / 当たつた file = " + str(hit)
    + " / 讀めなんだ = " + str(unread) + " / ast が解せなんだ = " + str(pf))
bline, ba, bb, bc, bother = GO(bn1, bhomes, bn3, "今(別母 " + str(len(allpy)) + " 枚)")
say(bline)
say("今(別母) 広網=" + str(bn2) + "（字の出現・棲家を問はぬ）")
say("今(別母) ★狭網 ＋ 代入形 = " + str(bn1 + bc) + " / ast網 = " + str(bn3)
    + " ⇒ 一致=" + str(bn1 + bc == bn3) + "★")
say("★代入形の在処（悉皆・名指し）★ = " + str(len(assign_where)) + " 件")
for w in assign_where:
    inner = "★12 本の内★" if w.split(" ")[0] in FILES else "★12 本の外★"
    say("  " + inner + " " + w)
say("")

# ---------- §C 差 0（★o222 の生から讀む★） ----------
say("--- §C ★差 0★ の当て（o222 の生 file から 数を讀んで突合・己の見込みは使はぬ） ---")
prev = io.open(PREV_RAW, encoding="utf-8").read()
say("讀んだ生 = " + os.path.basename(PREV_RAW)
    + " sha256=" + hashlib.sha256(prev.encode("utf-8")).hexdigest())
def pick(pat, label, want=1, nth=0):
    """★v1 の疵の直し★: re.search は ★最初の当たり★ を返す。
    ∴ 当たりの数を数へ、期する数と違へば止める。何番目を取つたかも刷る。"""
    ms = re.findall(pat, prev, re.M)
    say("  [網] " + label + ": 当たり " + str(len(ms)) + " 件（期する " + str(want)
        + "・取るは " + str(nth) + " 番目）")
    assert len(ms) == want, "PREV_PATTERN_COUNT " + label + " got=" + str(len(ms))
    it = list(re.finditer(pat, prev, re.M))
    return it[nth]
exp = {}
m = pick(r"前: N1狭 skip=(\d+) skipif=(\d+) 和=(\d+)", "前N1"); exp["前n1"] = int(m.group(3))
m = pick(r"前: N2広 skip=(\d+) skipif=(\d+) 和=(\d+)", "前N2"); exp["前n2"] = int(m.group(3))
m = pick(r"前: N3ast 和=(\d+)", "前N3"); exp["前n3"] = int(m.group(1))
m = pick(r"今: N1狭 skip=(\d+) skipif=(\d+) 和=(\d+)", "今N1"); exp["今n1"] = int(m.group(3))
m = pick(r"今: N2広 skip=(\d+) skipif=(\d+) 和=(\d+)", "今N2"); exp["今n2"] = int(m.group(3))
m = pick(r"今: N3ast 和=(\d+)", "今N3"); exp["今n3"] = int(m.group(1))
m = pick(r"呼び出し数 = (\d+)", "別母ast"); exp["別母n3"] = int(m.group(1))
m = pick(r"^棲家別 = \[\('assign_module_pytestmark', \d+\), \('decorator_class', (\d+)\), \('decorator_func', (\d+)\)\]",
         "別母棲家(★行頭 '棲家別 = [' に限る★)")
exp["別母a"] = int(m.group(1)); exp["別母b"] = int(m.group(2))
m = pick(r"代入形（狭網が落とす形）の在処★ = (\d+) 件", "別母代入"); exp["別母c"] = int(m.group(1))

now = {
    "前n1": res["前"]["n1"], "前n2": res["前"]["n2"], "前n3": res["前"]["n3"],
    "今n1": res["今"]["n1"], "今n2": res["今"]["n2"], "今n3": res["今"]["n3"],
    "別母n3": bn3, "別母a": ba, "別母b": bb, "別母c": bc,
}
bad = 0
for k in sorted(exp.keys()):
    d = now[k] - exp[k]
    if d: bad += 1
    say("  " + k + ": o222 の生=" + str(exp[k]) + " / 本弾=" + str(now[k]) + " / 差=" + str(d))
say("★差が 0 でなかつた項 = " + str(bad) + " 件（母 " + str(len(exp)) + " 項）★")
say("")

# ---------- §D 負の対照 ----------
say("--- §D 負の対照 ---")
probe = "import pytest" + chr(10) + "pytestmark = pytest.mark.skip(reason='x')" + chr(10)       + "@pytest.mark.skipif(True, reason='y')" + chr(10) + "class C:" + chr(10) + "    pass" + chr(10)
pn1s, pn1f = n1_narrow(probe); pn3, ph = n3_ast(probe)
pl, _, _, _, _ = GO(pn1s + pn1f, ph, pn3, "作り物")
say(pl)
say("★作り物では 狭網 1 / ast 2 ―― 器は『一致=False』を刷る口を現に持つ★: "
    + "狭網 ＋ 代入形 = " + str(pn1s + pn1f + 1) + " / ast = " + str(pn3))
say("差の器の負の対照: o222 の生に無い字を探せば止まる（PREV_PATTERN_MISS を assert で持つ）")
rc9, o9, e9 = git(["show", PIN + ":no_such_file_for_negative_control_o223"])
say("現に無い path の rc = " + str(rc9))
say("")

rc, o, e = git(["rev-parse", "HEAD"]); say("的の樹 HEAD(走の後)=" + o.decode("utf-8").strip())
rc, o, e = git(["status", "--porcelain"])
say("的の樹 porcelain(走の後)=" + str(len([x for x in o.decode('utf-8').split(chr(10)) if x])) + " 行")

txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
