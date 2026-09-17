# -*- coding: utf-8 -*-
"""㋑ 則の到達可能性を實測で閉ぢる(專任2 km-109)。

★器本体は一字も書換へぬ★ ―― 生器から ⑴函數其の物を import し ⑵正規表現を ast で
逐語に抜き出し、當席の写しで「どの則が当たつたか」を追ふ。
写しが正しい事は ★生器の出目と一字一句合ふか★ で證す(合はねば此の紙は無効)。
"""
import ast
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kaki  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
UTSUWA = os.path.join(REPO, "scripts", "checks", "karo_mac_manifest_verify.py")

# ―― ⑴ 生器を import(読取のみ・書換へぬ) ――
spec = importlib.util.spec_from_file_location("km_verify_ro", UTSUWA)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ―― ⑵ 三つの則を ast で逐語に抜く(★行番を焼き込まぬ★) ――
src = open(UTSUWA, encoding="utf-8").read()
tree = ast.parse(src)
fn = None
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "paths_of":
        fn = n
if fn is None:
    raise SystemExit("★paths_of が見付からぬ★")
SOKU = []
for n in ast.walk(fn):
    if isinstance(n, ast.Call):
        f = n.func
        if isinstance(f, ast.Attribute) and f.attr == "search" \
           and isinstance(f.value, ast.Name) and f.value.id == "re":
            if n.args and isinstance(n.args[0], ast.Constant):
                SOKU.append((n.lineno, n.args[0].value))
SOKU.sort()
assert len(SOKU) == 3, "★則が3本でない(%d本) ―― 器が変つた。此の紙を使ふな★" % len(SOKU)
P1, P2, P3 = [s for _, s in SOKU]


def utsushi(line):
    """★生器 paths_of の写し★ ―― 出目に加へて「当たつた則」を返す。"""
    def _dequote(t):
        t = t.strip()
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1]
        return t
    out = []
    line = line.replace("\r", "")
    atatta = None
    m = re.search(P1, line)
    if m:
        atatta = "①"
    if not m:
        m = re.search(P2, line)
        if m:
            atatta = "②"
    if not m:
        m = re.search(P3, line)
        if m:
            atatta = "③"
    kara_soku = None
    if m:
        kara_soku = _dequote(m.group(1))
        out.append(kara_soku)
    tok_add = []
    for tok in line.split():
        if tok.startswith("sha256=") or tok.startswith("bytes=") or tok.startswith("lines="):
            continue
        t = tok.split("=", 1)[-1] if tok.startswith("path=") else tok
        t = _dequote(t)
        if "/" in t and t not in out:
            out.append(t)
            tok_add.append(t)
    return out, (atatta or "―(一本も当たらず)"), kara_soku, tok_add


S64 = "0" * 64
TSUZURI = [
    ("1  括つた空白名(二重)",        'path="a b.txt" sha256=%s' % S64),
    ("2  ★素の空白名★",              'path=a b.txt sha256=%s' % S64),
    ("3  清い名",                    'path=kiyoi.txt sha256=%s' % S64),
    ("4  path= の直後が空白",        'path= a b.txt sha256=%s' % S64),
    ("5  sha256 が前に在る",         'sha256=%s path=a b.txt' % S64),
    ("6  空白が二つ",                'path=a b c.txt sha256=%s' % S64),
    ("7  括つた空白名(一重)",        "path='a b.txt' sha256=%s" % S64),
    ("8  素の空白名+'/'を含む",      'path=docs/x y.txt sha256=%s' % S64),
    ("9  本形四欄・素の空白名",      'path=a b.txt sha256=%s bytes=6 lines=1' % S64),
    ("10 sha256 が無い(素の空白名)", 'path=a b.txt'),
    ("11 TAB 区切り(素の空白名)",    'path=a\tb.txt\tsha256=%s' % S64),
    ("12 空白名・末に空白",          'path=a b.txt  sha256=%s' % S64),
    ("13 括り有・sha256 無し",       'path="a b.txt" bytes=6'),
    ("14 直後空白・sha256 無し",     'path= kiyoi.txt bytes=6'),
]

rows = []
fugou = 0
for na, line in TSUZURI:
    mine, soku, kara, tok = utsushi(line)
    real = mod.paths_of(line)
    ok = (mine == real)
    if not ok:
        fugou += 1
    rows.append((na, line, soku, kara, tok, mine, real, ok))

out = []
out.append("# ㋑ 則の到達可能性 ―― 實測表(專任2 km-109)")
out.append("")
out.append("## 器と則の出所")
out.append("  生器  %s" % os.path.relpath(UTSUWA, REPO))
out.append("  則は ast で抜いた(行番を焼き込まず、re.search の第一引数を出現順に取る)")
for i, (ln, s) in enumerate(SOKU, 1):
    out.append("    則%d (src 行%d)  %r" % (i, ln, s))
out.append("")
out.append("## 写しの證(★之が全て True でなければ以下の表は無効★)")
out.append("  写し utsushi() の出目 == 生器 paths_of() の出目 : 不合 %d / %d 綴り" % (fugou, len(rows)))
out.append("")
out.append("## 表 ―― 綴りごとに ⑴当たつた則 ⑵出た path の一覧")
out.append("")
out.append("| # 綴り | 行(逐語・sha は 0*64 に略) | 当たつた則 | 則が出した語 | 語の輪が足した語 | 出た path の一覧 | 生器と一致 |")
out.append("|---|---|---|---|---|---|---|")
for na, line, soku, kara, tok, mine, real, ok in rows:
    disp = line.replace(S64, "<64>").replace("\t", "\\t")
    out.append("| %s | `%s` | %s | %s | %s | %s | %s |"
               % (na, disp, soku,
                  ("―" if kara is None else "`%s`" % kara),
                  ("―" if not tok else " ".join("`%s`" % t for t in tok)),
                  ("★空★" if not mine else " ".join("`%s`" % t for t in mine)),
                  "○" if ok else "★×★"))
out.append("")
out.append("## 讀み")
out.append("  ・則②(非貪欲・素の空白名の為に書かれた)が当たつた綴りは ★%d 件★。"
           % sum(1 for r in rows if r[2] == "②"))
out.append("  ・則①が当たつた綴りは %d 件。則③は %d 件。一本も当たらぬは %d 件。"
           % (sum(1 for r in rows if r[2] == "①"),
              sum(1 for r in rows if r[2] == "③"),
              sum(1 for r in rows if r[2].startswith("―"))))
kaki.kaku(os.path.join(HERE, "10_soku_no_toutatsu.txt"), "\n".join(out))
print("不合=%d / %d" % (fugou, len(rows)))
for na, line, soku, kara, tok, mine, real, ok in rows:
    print("%-28s 則%s  %s" % (na, soku, mine))
