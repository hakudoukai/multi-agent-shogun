# -*- coding: utf-8 -*-
u"""order194 規その二 — 匿名 fixture / row の ★欠落を数で★（幾つ中 幾つ）

何を「一つ」と数へたか (床(30)):
  ・母数A = `source_evidence_ids` に触れる ★試験 file★ の枚数
  ・母数B = 其の試験 file の中で `source_evidence_ids` を含む ★行★ の数
  ・母数C = 其の試験 file の中の ★試験 def★ の本数（class 内を辿る）
  ・「匿名 fixture を持つ」= 其の file 内に `@pytest.fixture` の飾りが付く def が現に在る
  ・「合成 row を持つ」= 其の file 内に literal の dict / list を返す fixture、
     または `source_evidence_ids` を含む行が literal の中に在る（= DB から取らぬ）
  ・「DB に依る」= 其の file 内に DB 語（pg_cursor / psycopg / cursor / conn /
     DATABASE_URL / execute(）が現に在る
  ・★「持つ」と「DB に依る」は排他に非ず★ ― 双方を別値で数へ、重なりも出す

定め: 讀取のみ・走行 0・書込 0・DB 0・値/患者本文/secret を採らぬ（語の在処と度数のみ）
"""
import ast, io, os, re, subprocess, hashlib

TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
WORD = u"source_evidence_ids"
DB_WORDS = [u"pg_cursor", u"psycopg", u"DATABASE_URL", u"cursor", u"conn", u".execute("]

def sh(a):
    return subprocess.check_output(a, cwd=TREE).decode("utf-8")

def sha(rel):
    h = hashlib.sha256(); h.update(io.open(os.path.join(TREE, rel), "rb").read())
    return h.hexdigest()

def find_files():
    """WORD を含む .py のうち 試験 file と 本番 file を分けて返す"""
    tests, prod = [], []
    for dp, dn, fn in os.walk(TREE):
        dn[:] = [x for x in dn if x not in (u"node_modules", u".git", u".venv", u"venv", u"__pycache__")]
        for f in fn:
            if not f.endswith(u".py"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), TREE)
            if rel.startswith(u"reports/"):
                continue                      # reports は写しの山ゆゑ母数から外す（名指し除外）
            try:
                src = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            if WORD not in src:
                continue
            (tests if (u"/tests/" in u"/" + rel or os.path.basename(rel).startswith(u"test_")) else prod).append(rel)
    return sorted(tests), sorted(prod)

def tests_in(body):
    n = 0
    for st in body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name.startswith(u"test"):
            n += 1
        elif isinstance(st, ast.ClassDef):
            n += tests_in(st.body)
    return n

def fixture_defs(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in getattr(node, u"decorator_list", []):
                f = d.func if isinstance(d, ast.Call) else d
                nm = getattr(f, u"attr", None) or getattr(f, u"id", None)
                if nm == u"fixture":
                    out.append((node.lineno, node.name)); break
    return out

def literal_ret(tree, names):
    """fixture のうち literal(dict/list/tuple/str/num のみ) を返す物 = 合成"""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            for st in ast.walk(node):
                if isinstance(st, ast.Return) and st.value is not None:
                    try:
                        ast.literal_eval(st.value); out.append((node.lineno, node.name)); break
                    except (ValueError, SyntaxError, TypeError):
                        pass
    return out

def main():
    tip = sh(["git", "rev-parse", "HEAD"]).strip()
    br  = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    tests, prod = find_files()
    print(u"tree=%s" % TREE); print(u"git_tip=%s" % tip); print(u"git_branch=%s" % br)
    print(u"note=reports/ 配下は写しの山ゆゑ母数から名指しで外した")
    print(u"")
    print(u"## 母数A 試験 file = %d 枚 ／ 本番 file = %d 枚" % (len(tests), len(prod)))
    print(u"")
    print(u"## 本番側（書く側）")
    for rel in prod:
        src = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
        n = len([1 for l in src.split(u"\n") if WORD in l])
        print(u"  %s | %s | wc=%d | split=%d | %s_lines=%d"
              % (rel, sha(rel), src.count(u"\n"), len(src.split(u"\n")), WORD, n))
    print(u"")
    print(u"## 試験側（検める側）— 一枚づつ")
    hdr = (u"  rel | sha256-64 | wc | split | word_lines | test_defs | fixture_defs | "
           u"literal_fixtures | db_words | word_in_assert")
    print(hdr)
    tot = dict(files=0, words=0, tdefs=0, fx=0, lit=0, db=0, assertln=0,
               no_fx=0, no_lit=0, db_dep=0, lit_and_no_db=0)
    rows = []
    for rel in tests:
        src = io.open(os.path.join(TREE, rel), encoding="utf-8").read()
        lines = src.split(u"\n")
        wl = [i + 1 for i, l in enumerate(lines) if WORD in l]
        try:
            tree = ast.parse(src)
        except SyntaxError:
            print(u"  %s | SYNTAX_ERROR" % rel); continue
        td = tests_in(tree.body)
        fx = fixture_defs(tree)
        lit = literal_ret(tree, set(n for (_, n) in fx))
        db = sorted(set(w for w in DB_WORDS if w in src))
        # WORD を含む行が assert の中に在るか
        aln = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                seg = u"\n".join(lines[node.lineno - 1: getattr(node, u"end_lineno", node.lineno)])
                if WORD in seg:
                    aln += 1
        rows.append((rel, sha(rel), src.count(u"\n"), len(lines), len(wl), td, len(fx), len(lit), len(db), aln))
        print(u"  %s | %s | %d | %d | %d | %d | %d | %d | %s | %d"
              % (rel, sha(rel), src.count(u"\n"), len(lines), len(wl), td, len(fx), len(lit),
                 (u",".join(db) if db else u"-"), aln))
        tot["files"] += 1; tot["words"] += len(wl); tot["tdefs"] += td
        tot["fx"] += len(fx); tot["lit"] += len(lit); tot["assertln"] += aln
        if not fx: tot["no_fx"] += 1
        if not lit: tot["no_lit"] += 1
        if db: tot["db_dep"] += 1
        if lit and not db: tot["lit_and_no_db"] += 1
    print(u"")
    print(u"## ★欠落を数で（幾つ中 幾つ）★")
    n = tot["files"]
    print(u"  母数A 試験 file                         = %d" % n)
    print(u"  母数B %s を含む行             = %d" % (WORD, tot["words"]))
    print(u"  母数C 試験 def                          = %d" % tot["tdefs"])
    print(u"  ㋑ fixture を ★一つも持たぬ★ 枚         = %d / %d" % (tot["no_fx"], n))
    print(u"  ㋺ literal を返す fixture を持たぬ 枚   = %d / %d" % (tot["no_lit"], n))
    print(u"  ㋩ DB 語が現に在る 枚                   = %d / %d" % (tot["db_dep"], n))
    print(u"  ㋥ literal 有り かつ DB 語 無し の 枚   = %d / %d" % (tot["lit_and_no_db"], n))
    print(u"  ㋭ %s が assert の中に在る 節 = %d" % (WORD, tot["assertln"]))
    print(u"  fixture def 総数=%d  literal fixture 総数=%d" % (tot["fx"], tot["lit"]))

if __name__ == "__main__":
    main()
