# -*- coding: utf-8 -*-
u"""order193 規 v1 ―― 現に隠して居る 24 行/試験 31 本 を顕在化する為の器。

定め(数を出す前に置く・後から動かさぬ):
 (1) 的の樹 = /home/hakudoukai/a3/wt-bundle-fix4 (己の席の樹)。git は一度も打たぬ(床の急報)。
 (2) 母集団 = 当該樹の .py 悉皆。除外は名指し = node_modules / .git / .venv / venv /
     __pycache__ / .pytest* (order192 と同じ定め)。
 (3) 「現に隠して居る」= 走らずに定まる逃げ道 = B(mark.skip 無条件) + H(collect_ignore)。
     order192 の実測 = 24 行 / file 16 / 試験関数 31 本 / file 15。
 (4) 振り先は三つのみ。㋑理由付きの条件化(importorskip 同族 = 条件を器に測らせる形)
     ㋺本物の移植(今の設計へ当て直す) ㋩出来ぬ(理由を必ず書く)。
     一行も余さず三つの何れかに入れる。
 (5) 「隠し得る 107 行」には手を触れぬ。紙には「測定不能」の語で残す。
     「隠して居らぬ」とは書かぬ。
 (6) 製品 code に一字も書かぬ。触るは試験 file のみ。
 (7) 直す前の数と直した後の数を、同じ器で二度測り併記する(條 百九十七)。
 (8) 行数は wc と split の双方を書く(床(32))。sha16 は sha256 頭16(釘83)。
 (9) 判定語(PASS/合格/緑 等)を書かぬ。三択語(現に在る/現に無い/測定不能)で結ぶ。
"""
import os, io, re, ast, hashlib

ROOT = u"/home/hakudoukai/a3/wt-bundle-fix4"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__"])
RE_B = re.compile(r"mark\.skip\s*[\(\)]|mark\.skip$")
RE_H = re.compile(r"collect_ignore")


def walk_py():
    for d, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in SKIPD and not x.startswith(u".pytest")]
        for f in fs:
            if f.endswith(u".py"):
                yield os.path.join(d, f)


def rd(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def rel(p):
    return p[len(ROOT) + 1:]


def stage1():
    print(u"stage1: 定めのみ。数は出さぬ。")



def _is_skip_deco(node):
    f = node.func if isinstance(node, ast.Call) else node
    return isinstance(f, ast.Attribute) and f.attr == u"skip"


def _tests_in(body):
    n = 0
    for st in body:
        if isinstance(st, (ast.FunctionDef,)) and st.name.startswith(u"test"):
            n += 1
        elif isinstance(st, ast.ClassDef):
            n += _tests_in(st.body)
    return n


def hidden_units():
    """現に隠して居る単位を (file, 行, 覆ふ試験本数, 形) で返す。1 と数へるのは
    ★飾り 1 個 / pytestmark 1 個 / collect_ignore 1 行★ (床(30))。"""
    out = []
    for p in walk_py():
        t = rd(p)
        lines = t.split(u"\n")
        for i, l in enumerate(lines, 1):
            if RE_H.search(l):
                out.append((rel(p), i, None, u"H collect_ignore"))
        try:
            tree = ast.parse(t)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for d in node.decorator_list:
                    if _is_skip_deco(d):
                        cnt = 1 if isinstance(node, ast.FunctionDef) else _tests_in(node.body)
                        out.append((rel(p), d.lineno, cnt, u"B 飾り/" + node.__class__.__name__))
        for st in tree.body:
            if isinstance(st, ast.Assign):
                for tg in st.targets:
                    if isinstance(tg, ast.Name) and tg.id == u"pytestmark":
                        if _is_skip_deco(st.value):
                            out.append((rel(p), st.lineno, _tests_in(tree.body), u"B pytestmark/module"))
    return out


def stage2():
    rows = hidden_units()
    tot = sum([r[2] for r in rows if r[2] is not None])
    print(u"stage2 単位=%d 覆ふ試験本数の和=%d" % (len(rows), tot))
    for f, ln, c, k in sorted(rows):
        print(u"  %s:%d 本=%s %s" % (f, ln, c, k))



# 直す前に、飾りの「理由」が言ふ的が現に在るか否かを己の目で測る。
# (紙へ写すは 在/無 の別と件数のみ。中身は写さぬ)
TARGETS = [
 (u"tests/test_step_r_ui.py", 282, u"frontend/src/components/shared/EmptyState.tsx"),
 (u"tests/test_step_a4_handover_sheet.py", 377, u"frontend/src/hooks/useSheetPagination.ts"),
 (u"tests/test_step_q.py", 461, u"frontend/src/hooks/useBillingRules.ts"),
 (u"tests/test_step_s3.py", 664, u"frontend/src/features/kanban/CheckoutModal.tsx"),
 (u"tests/test_step_s3.py", 678, u"frontend/src/features/kanban/ComplaintForm.tsx"),
 (u"tests/test_step_s3.py", 692, u"frontend/src/features/kanban/ComplaintForm.tsx"),
 (u"tests/test_step_s3.py", 703, u"frontend/src/features/dashboard/ProductivitySection.tsx"),
 (u"tests/test_step_s3.py", 715, u"frontend/src/features/dashboard/ProductivitySection.tsx"),
 (u"tests/test_step_s3.py", 726, u"frontend/src/features/dashboard/ProductivitySection.tsx"),
 (u"tests/test_step_s4.py", 742, u"frontend/src/features/handover-sheet/SheetHeader.tsx"),
 (u"tests/test_step_s4.py", 758, u"frontend/src/features/handover-sheet/SheetPrintView.tsx"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/services/consent_gate.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/services/notifications/facade.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/routers/ceremony_events.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/routers/celebration_api.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/services/teriha_passport_engine.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/dependencies/clinic_id_resolver.py"),
 (u"backend/tests/test_cmd004_cross_cutting_integration.py", 24, u"backend/services/observability/metrics.py"),
]


def stage3():
    ari = nashi = 0
    miss = []
    for f, ln, tgt in TARGETS:
        e = os.path.exists(os.path.join(ROOT, tgt))
        if e:
            ari += 1
            miss.append(u"  在 %s:%d -> %s" % (f, ln, tgt))
        else:
            nashi += 1
    print(u"stage3 的=%d 現に在る=%d 現に無い=%d" % (len(TARGETS), ari, nashi))
    for m in miss:
        print(m)


if __name__ == "__main__":
    stage1()
    stage2()
    stage3()
