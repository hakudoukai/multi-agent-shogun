# -*- coding: utf-8 -*-
u"""order195 型で出し直す規 (軍師third REVISE 291807 への是正)

定め:
 1) 的の樹 = /home/hakudoukai/a3/wt-bundle-fix4 (別樹・repo 相対 path を持たぬ)
 2) 母集団 = tests/ と backend/tests/ 配下の test_*.py と conftest.py のみ
    (全樹 walk は 120s で timeout した実績が在る ∴ 絞る)
 3) 「隠す形」を三箱で数へる = A:飾り(decorator) B:pytestmark C:collect_ignore/glob
    skip と skipif を ★別値★ で出す (skipif は器が毎度測る形 = 現に隠して居らぬ)
 4) ★正対照★ = 直した 6 枚に現に在る skipif を file:行 で逐語列挙
    ★負対照★ = 直して居らぬ file に現に残る skip を file:行 で逐語列挙
    (双方が現に出得る事を先に示す = 家老 條 165)
 5) 数は wc(改行数) と split 片数の双方を出す (床(32))
 6) 判定語を書かず 三択語で結ぶ
 7) 走行 0 (pytest を起こさぬ)・書込 0 (讀取のみ)
"""
import ast, io, os, re, hashlib

ROOT = u"/home/hakudoukai/a3/wt-bundle-fix4"
DIRS = [u"tests", u"backend/tests"]
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__", u"fixtures"])
FIXED6 = set([
    u"tests/test_step_r_ui.py",
    u"tests/test_step_a4_handover_sheet.py",
    u"tests/test_step_q.py",
    u"tests/test_step_s3.py",
    u"tests/test_step_s4.py",
    u"backend/tests/test_cmd004_cross_cutting_integration.py",
])

def files():
    out = []
    for d in DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [x for x in dn if x not in SKIPD]
            for f in fn:
                if not f.endswith(u".py"):
                    continue
                if not (f.startswith(u"test_") or f == u"conftest.py"):
                    continue
                out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(out)

def sha(rel):
    h = hashlib.sha256()
    h.update(io.open(os.path.join(ROOT, rel), "rb").read())
    return h.hexdigest()

def _attr(node):
    f = node.func if isinstance(node, ast.Call) else node
    return f.attr if isinstance(f, ast.Attribute) else None

def _tests_in(body):
    n = 0
    for st in body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name.startswith(u"test"):
            n += 1
        elif isinstance(st, ast.ClassDef):
            n += _tests_in(st.body)
    return n

def scan(rel):
    """一枚を三箱で数へ、skip と skipif を別値で返す"""
    src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    lines = src.split(u"\n")
    res = {u"A_skip": [], u"A_skipif": [], u"B_skip": [], u"B_skipif": [], u"C": []}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None, src, lines
    # A: 飾り
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for d in getattr(node, u"decorator_list", []):
                a = _attr(d)
                if a == u"skip":
                    res[u"A_skip"].append((d.lineno, node.name, _tests_in([node]) or (1 if node.name.startswith(u"test") else 0)))
                elif a == u"skipif":
                    res[u"A_skipif"].append((d.lineno, node.name, _tests_in([node]) or (1 if node.name.startswith(u"test") else 0)))
    # B: pytestmark (module 直下の代入)
    for st in tree.body:
        if isinstance(st, ast.Assign):
            names = [t.id for t in st.targets if isinstance(t, ast.Name)]
            if u"pytestmark" not in names:
                continue
            vals = st.value.elts if isinstance(st.value, (ast.List, ast.Tuple)) else [st.value]
            for v in vals:
                a = _attr(v)
                if a == u"skip":
                    res[u"B_skip"].append((st.lineno, u"<module>", _tests_in(tree.body)))
                elif a == u"skipif":
                    res[u"B_skipif"].append((st.lineno, u"<module>", _tests_in(tree.body)))
    # C: collect_ignore
    for i, l in enumerate(lines):
        if re.search(r"collect_ignore", l):
            res[u"C"].append((i + 1, u"<collect_ignore>", 0))
    return res, src, lines

def main():
    fl = files()
    print(u"# order195 typed reproof")
    print(u"tree=%s" % ROOT)
    print(u"population_files=%d" % len(fl))
    tot_tests = 0
    rows = []
    for rel in fl:
        res, src, lines = scan(rel)
        if res is None:
            rows.append((rel, u"SYNTAX_ERROR", 0, 0, 0, 0, 0, 0, 0))
            continue
        try:
            t = _tests_in(ast.parse(src).body)
        except SyntaxError:
            t = 0
        tot_tests += t
        rows.append((rel, sha(rel), len(lines) - 1, len(lines), t,
                     len(res[u"A_skip"]) + len(res[u"B_skip"]),
                     len(res[u"A_skipif"]) + len(res[u"B_skipif"]),
                     len(res[u"C"]),
                     sum(x[2] for x in res[u"A_skip"] + res[u"B_skip"])))
    print(u"population_test_defs=%d" % tot_tests)
    print(u"")
    print(u"## per-file  rel | sha256 | wc | split | tests | skip_units | skipif_units | collect_ignore | tests_under_skip")
    for r in rows:
        print(u"%s | %s | %s | %s | %s | %s | %s | %s | %s" % r)
    # 対照
    print(u"")
    print(u"## POSITIVE (直した6枚に現に在る skipif) file:line:name:tests")
    pos = 0
    for rel in sorted(FIXED6):
        res, src, lines = scan(rel)
        for (ln, nm, t) in res[u"A_skipif"] + res[u"B_skipif"]:
            print(u"%s:%d:%s:%d" % (rel, ln, nm, t)); pos += 1
    print(u"positive_count=%d" % pos)
    print(u"")
    print(u"## NEGATIVE (直して居らぬ file に現に残る skip) file:line:name:tests")
    neg = 0; neg_tests = 0
    for rel in fl:
        if rel in FIXED6:
            continue
        res, src, lines = scan(rel)
        if res is None:
            continue
        for (ln, nm, t) in res[u"A_skip"] + res[u"B_skip"]:
            print(u"%s:%d:%s:%d" % (rel, ln, nm, t)); neg += 1; neg_tests += t
    print(u"negative_count=%d negative_tests=%d" % (neg, neg_tests))
    print(u"")
    print(u"## RESIDUAL (直した6枚に現に残る skip) file:line:name:tests")
    res_u = 0; res_t = 0
    for rel in sorted(FIXED6):
        res, src, lines = scan(rel)
        for (ln, nm, t) in res[u"A_skip"] + res[u"B_skip"]:
            print(u"%s:%d:%s:%d" % (rel, ln, nm, t)); res_u += 1; res_t += t
    print(u"residual_units=%d residual_tests=%d" % (res_u, res_t))

if __name__ == "__main__":
    main()
