# -*- coding: utf-8 -*-
u"""order194 規 — 「直す前」を ★git show の blob★ で数へ直し、「直した後」と並べる

何故 走らせぬか:
  直す前の姿 = 樹の HEAD (47c8bc3b) の blob。直した姿 = ★未 commit の working tree★。
  ∴ detach しても姿は変はらず、`git checkout --` は ★不可逆★ ゆゑ採らぬ。
  blob を讀むのは ★讀取のみ・書込 0・走行 0★ である。

定め:
 1) 的の樹 = /home/hakudoukai/a3/wt-bundle-fix4 ・ pin = HEAD の完全 SHA を器自身に言はせる
 2) 「前」= `git show <tip>:<rel>` ／「後」= working tree の file
 3) 三箱 A:飾り B:pytestmark C:collect_ignore を、skip と skipif を ★別値★ で数へる
 4) 覆ふ試験本数を併記 (床(30) 何を一つと数へたか)
 5) wc(改行数) と split 片数の双方 (床(32))
 6) 讀取のみ・書込 0・走行 0・DB 0
"""
import ast, io, os, subprocess, hashlib

TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
FILES = [
    u"tests/test_step_r_ui.py",
    u"tests/test_step_a4_handover_sheet.py",
    u"tests/test_step_q.py",
    u"tests/test_step_s3.py",
    u"tests/test_step_s4.py",
    u"backend/tests/test_cmd004_cross_cutting_integration.py",
]

def sh(a):
    return subprocess.check_output(a, cwd=TREE).decode("utf-8")

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

def scan(src):
    """一枚の字面を三箱で数へる。返り = (skip_units, skipif_units, skip_tests, skipif_tests, rows)"""
    rows = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    su = si = st_ = si_t = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for d in getattr(node, u"decorator_list", []):
                a = _attr(d)
                if a not in (u"skip", u"skipif"):
                    continue
                t = _tests_in([node]) or (1 if node.name.startswith(u"test") else 0)
                rows.append((d.lineno, a, node.name, t))
                if a == u"skip":
                    su += 1; st_ += t
                else:
                    si += 1; si_t += t
    for stm in tree.body:
        if isinstance(stm, ast.Assign) and any(isinstance(t, ast.Name) and t.id == u"pytestmark" for t in stm.targets):
            vals = stm.value.elts if isinstance(stm.value, (ast.List, ast.Tuple)) else [stm.value]
            for v in vals:
                a = _attr(v)
                if a not in (u"skip", u"skipif"):
                    continue
                t = _tests_in(tree.body)
                rows.append((stm.lineno, a + u"(pytestmark)", u"<module>", t))
                if a == u"skip":
                    su += 1; st_ += t
                else:
                    si += 1; si_t += t
    return (su, si, st_, si_t, sorted(rows))

def main():
    tip = sh(["git", "rev-parse", "HEAD"]).strip()
    br  = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    print(u"tree=%s" % TREE)
    print(u"git_tip=%s" % tip)
    print(u"git_branch=%s" % br)
    print(u"note=前=git show <tip>:<rel> の blob / 後=working tree の file（未 commit）")
    print(u"")
    tot = {u"b_su": 0, u"b_si": 0, u"b_st": 0, u"b_sit": 0,
           u"a_su": 0, u"a_si": 0, u"a_st": 0, u"a_sit": 0}
    for rel in FILES:
        before = sh(["git", "show", u"%s:%s" % (tip, rel)])
        after  = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
        bh = hashlib.sha256(before.encode("utf-8")).hexdigest()
        ah = hashlib.sha256(after.encode("utf-8")).hexdigest()
        b = scan(before); a = scan(after)
        print(u"## %s" % rel)
        print(u"  before: sha256(blob text)=%s wc=%d split=%d" % (bh, before.count(u"\n"), len(before.split(u"\n"))))
        print(u"  after : sha256(file)     =%s wc=%d split=%d" % (ah, after.count(u"\n"), len(after.split(u"\n"))))
        if b is None or a is None:
            print(u"  SYNTAX_ERROR"); continue
        print(u"  before: skip_units=%d skipif_units=%d skip_tests=%d skipif_tests=%d" % (b[0], b[1], b[2], b[3]))
        print(u"  after : skip_units=%d skipif_units=%d skip_tests=%d skipif_tests=%d" % (a[0], a[1], a[2], a[3]))
        print(u"  --- before rows (line|kind|name|tests) ---")
        for r in b[4]:
            print(u"    %d|%s|%s|%d" % r)
        print(u"  --- after rows (line|kind|name|tests) ---")
        for r in a[4]:
            print(u"    %d|%s|%s|%d" % r)
        print(u"")
        tot[u"b_su"] += b[0]; tot[u"b_si"] += b[1]; tot[u"b_st"] += b[2]; tot[u"b_sit"] += b[3]
        tot[u"a_su"] += a[0]; tot[u"a_si"] += a[1]; tot[u"a_st"] += a[2]; tot[u"a_sit"] += a[3]
    print(u"## TOTAL (6 枚のみ・collect_ignore は別勘定ゆゑ含まぬ)")
    print(u"before: skip_units=%d skip_tests=%d skipif_units=%d skipif_tests=%d" % (tot[u"b_su"], tot[u"b_st"], tot[u"b_si"], tot[u"b_sit"]))
    print(u"after : skip_units=%d skip_tests=%d skipif_units=%d skipif_tests=%d" % (tot[u"a_su"], tot[u"a_st"], tot[u"a_si"], tot[u"a_sit"]))
    print(u"delta : skip_units=%+d skip_tests=%+d skipif_units=%+d skipif_tests=%+d"
          % (tot[u"a_su"] - tot[u"b_su"], tot[u"a_st"] - tot[u"b_st"],
             tot[u"a_si"] - tot[u"b_si"], tot[u"a_sit"] - tot[u"b_sit"]))

if __name__ == "__main__":
    main()
