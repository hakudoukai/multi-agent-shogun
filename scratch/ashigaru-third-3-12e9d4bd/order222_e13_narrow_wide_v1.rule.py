# -*- coding: utf-8 -*-
"""order222 / E13 ―― 狭網と広網の差 1 を潰す（走 0・讀取のみ）

三つの網を ★同じ走で並べて★ 数へる:
  N1 狭網  = 行頭(左空白を除く)が "@pytest.mark.skip("  / "@pytest.mark.skipif(" で始まる行の数
  N2 広網  = 字 "pytest.mark.skip(" / "pytest.mark.skipif(" の出現数（字の数へ・註釈も文字列も拾ふ）
  N3 ast網 = ast で見た pytest.mark.skip / skipif の ★呼び出しの個数★（棲家を別々に名指す）

床(31)「形は ast で」。床(30)「何を一つと数へたか」を出力の各行に持たせる。
"""
import os, io, ast, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = "/home/hakudoukai/a3/wt-bundle-fix4"
PIN = "47c8bc3b86613d7bd55cdfc062a46dccf8d81d1b"
OUT = os.path.join(HERE, "order222_e13_narrow_wide_v1.raw.txt")

FILES = [
    "backend/tests/test_cmd004_cross_cutting_integration.py",
    "tests/test_step_a4_handover_sheet.py",
    "tests/test_step_q.py",
    "tests/test_step_r_ui.py",
    "tests/test_step_s3.py",
    "tests/test_step_s4.py",
]

L = []
def say(x):
    L.append(x)

def git(args):
    pr = subprocess.Popen(["git", "-C", TREE] + args,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = pr.communicate()
    return pr.returncode, o, e

# ---------- N1 狭網 ----------
def n1_narrow(text):
    sk = 0; sf = 0
    for ln in text.split(chr(10)):
        t = ln.lstrip()
        if t.startswith("@pytest.mark.skipif("): sf += 1
        elif t.startswith("@pytest.mark.skip("): sk += 1
    return sk, sf

# ---------- N2 広網 ----------
def n2_wide(text):
    return text.count("pytest.mark.skip("), text.count("pytest.mark.skipif(")

# ---------- N3 ast網 ----------
def is_pytest_mark_call(node, want):
    if not isinstance(node, ast.Call): return False
    f = node.func
    if not isinstance(f, ast.Attribute): return False
    if f.attr != want: return False
    v = f.value
    if not isinstance(v, ast.Attribute): return False
    if v.attr != "mark": return False
    w = v.value
    return isinstance(w, ast.Name) and w.id == "pytest"

def n3_ast(text, label):
    """返す: 一覧 [(line, name, 棲家, 添書)] ／ 棲家 = decorator_func / decorator_class /
    assign_module_pytestmark / assign_module_pytestmark_list / assign_other / bare"""
    try:
        tree = ast.parse(text)
    except SyntaxError as ex:
        return None, "PARSE_FAIL " + label + " " + str(ex)
    deco = {}
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "decorator_class" if isinstance(nd, ast.ClassDef) else "decorator_func"
            for d in nd.decorator_list:
                for sub in ast.walk(d):
                    deco[id(sub)] = (kind, nd.name)
    assigns = {}
    for nd in tree.body:
        if isinstance(nd, ast.Assign):
            names = [t.id for t in nd.targets if isinstance(t, ast.Name)]
            tag = "assign_module_pytestmark" if "pytestmark" in names else "assign_other"
            val = nd.value
            if isinstance(val, (ast.List, ast.Tuple)):
                tag = tag + "_list"
                for el in val.elts:
                    for sub in ast.walk(el):
                        assigns[id(sub)] = (tag, ",".join(names))
            else:
                for sub in ast.walk(val):
                    assigns[id(sub)] = (tag, ",".join(names))
    rows = []
    for nd in ast.walk(tree):
        for want in ("skip", "skipif"):
            if is_pytest_mark_call(nd, want):
                if id(nd) in deco:
                    home, owner = deco[id(nd)]
                elif id(nd) in assigns:
                    home, owner = assigns[id(nd)]
                else:
                    home, owner = "bare", "-"
                rows.append((nd.lineno, want, home, owner))
    rows.sort()
    return rows, None

# ---------- 走 ----------
say("=== order222 / E13 三網の並べ ===")
say("TREE=" + TREE)
say("PIN=" + PIN)
say("母 = porcelain の 6 枚（前=blob / 今=作業樹）")
say("")

tot = {}
for side in ("前", "今"):
    tot[side] = dict(n1s=0, n1f=0, n2s=0, n2f=0, n3=0, homes={})

say("--- §A 12 本（と其の前身）を 一本づつ 悉くに ---")
say("side | # | file | line | name | 棲家 | 持ち主")
for rel in FILES:
    rc, out, err = git(["show", PIN + ":" + rel])
    assert rc == 0, "BLOB_MISS " + rel
    before = out.decode("utf-8")
    now = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
    for side, text in (("前", before), ("今", now)):
        s1, f1 = n1_narrow(text)
        s2, f2 = n2_wide(text)
        rows, perr = n3_ast(text, side + " " + rel)
        assert perr is None, perr
        tot[side]["n1s"] += s1; tot[side]["n1f"] += f1
        tot[side]["n2s"] += s2; tot[side]["n2f"] += f2
        tot[side]["n3"] += len(rows)
        n = 0
        for (ln, nm, home, owner) in rows:
            n += 1
            tot[side]["homes"][home] = tot[side]["homes"].get(home, 0) + 1
            say(side + " | " + str(n) + " | " + rel + " | " + str(ln) + " | " + nm
                + " | " + home + " | " + owner)
        say(side + " | 小計 | " + rel + " | N1狭 skip=" + str(s1) + " skipif=" + str(f1)
            + " | N2広 skip=" + str(s2) + " skipif=" + str(f2) + " | N3ast=" + str(len(rows)))
say("")

say("--- §B 三網の和（母 = 6 枚） ---")
for side in ("前", "今"):
    t = tot[side]
    say(side + ": N1狭 skip=" + str(t["n1s"]) + " skipif=" + str(t["n1f"])
        + " 和=" + str(t["n1s"] + t["n1f"]))
    say(side + ": N2広 skip=" + str(t["n2s"]) + " skipif=" + str(t["n2f"])
        + " 和=" + str(t["n2s"] + t["n2f"]))
    say(side + ": N3ast 和=" + str(t["n3"]) + " 棲家別=" + repr(sorted(t["homes"].items())))
say("")
say("★N1 と N3 の差★: 前=" + str(tot["前"]["n3"] - (tot["前"]["n1s"] + tot["前"]["n1f"]))
    + " 今=" + str(tot["今"]["n3"] - (tot["今"]["n1s"] + tot["今"]["n1f"])))
say("★N2 と N3 の差★: 前=" + str((tot["前"]["n2s"] + tot["前"]["n2f"]) - tot["前"]["n3"])
    + " 今=" + str((tot["今"]["n2s"] + tot["今"]["n2f"]) - tot["今"]["n3"]))
say("")

# ---------- §C 12 本の外（的の樹の追跡下 py 悉く） ----------
say("--- §C 12 本の外（★別母★ = 的の樹の追跡下 .py 悉く・今の姿のみ） ---")
rc, out, err = git(["ls-files", "*.py"])
assert rc == 0, "LSFILES_FAIL"
allpy = [x for x in out.decode("utf-8").split(chr(10)) if x]
say("別母 N(追跡下 .py) = " + str(len(allpy)))
hit_files = 0; hit_rows = 0; homes2 = {}; unread = 0; parsefail = 0
assign_hits = []
for rel in allpy:
    ap = os.path.join(TREE, rel)
    if not os.path.exists(ap):
        unread += 1
        continue
    try:
        text = io.open(ap, encoding="utf-8").read()
    except Exception:
        unread += 1
        continue
    if "pytest.mark.skip" not in text:
        continue
    rows, perr = n3_ast(text, "tree " + rel)
    if perr is not None:
        parsefail += 1
        continue
    if not rows:
        continue
    hit_files += 1
    hit_rows += len(rows)
    for (ln, nm, home, owner) in rows:
        homes2[home] = homes2.get(home, 0) + 1
        if home.startswith("assign"):
            assign_hits.append(rel + ":" + str(ln) + " " + nm + " " + home)
say("当たつた file 数 = " + str(hit_files) + " / 呼び出し数 = " + str(hit_rows))
say("棲家別 = " + repr(sorted(homes2.items())))
say("讀めなんだ = " + str(unread) + " / ast が解せなんだ = " + str(parsefail))
say("★代入形（狭網が落とす形）の在処★ = " + str(len(assign_hits)) + " 件")
for h in assign_hits:
    say("  代入形: " + h)
say("")

# ---------- §D 負の対照 ----------
say("--- §D 負の対照 ---")
probe = "import pytest" + chr(10) + "pytestmark = pytest.mark.skip(reason='x')" + chr(10)       + "@pytest.mark.skipif(True, reason='y')" + chr(10) + "def f():" + chr(10) + "    pass" + chr(10)
r, e = n3_ast(probe, "probe")
say("作り物に当てた ast網 = " + repr(r) + " / err=" + repr(e))
s1, f1 = n1_narrow(probe); s2, f2 = n2_wide(probe)
say("作り物の N1狭 = skip " + str(s1) + " skipif " + str(f1)
    + " / N2広 = skip " + str(s2) + " skipif " + str(f2))
say("★作り物で 狭網が 代入形を落とす事が 現に出る★（N1狭 skip=0 だが N3ast に assign が在る）")
rc9, o9, e9 = git(["show", PIN + ":no_such_file_for_negative_control_o222"])
say("現に無い path の rc = " + str(rc9))
say("")

# ---------- 生を書く ----------
txt = chr(10).join(L) + chr(10)
io.open(OUT, "w", encoding="utf-8").write(txt)
print("wrote " + OUT)
print("raw_sha256=" + hashlib.sha256(txt.encode("utf-8")).hexdigest())
print("raw_lines_wc=" + str(txt.count(chr(10))) + " split=" + str(len(txt.split(chr(10)))))
