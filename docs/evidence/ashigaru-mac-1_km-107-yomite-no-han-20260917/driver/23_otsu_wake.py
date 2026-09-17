#!/usr/bin/env python3 -B
# -*- coding: utf-8 -*-
"""23_otsu_wake.py ―― 甲/乙 の行を ★層★ に分ける(km-107 ㋑ の内訳)。數は 21/28 の行を再集計するのみ(檢出子は gai)。
層の宣(逐語・上から順に一つだけ當てる):
  拡張子 = 紙の名の最後の '.' 以降(小文字)。'.txt' 以外の紙(.out/.tsv/.md/.manifest 等)は「臺帳でない疑ひ」として別欄。
  乙-表  = inner が '|' で始まるか終はる(markdown 表の桁 ―― 空白は表の記法であつて名の空白ではない)
  乙-写  = inner に '★' か '読めぬ' か '讀めぬ' か 'ep=' が在る(讀み手の出力 ★読めぬ行★ の写し)
  乙-殘  = 上の何れでもない(★名に空白が在る疑ひが最も濃い★・全行を刷る)
  甲-對照 = 紙の path に taishou / fixture / fx / shikake / saiken / seigyo / _gate/ の何れかを含む(対照・作り物・門控の疑ひ)
  甲-現物 = 其れ以外
"""
import os, sys, ast, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import K
BUN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(BUN)
FIX = ("taishou", "fixture", "fx", "shikake", "saiken", "seigyo", "_gate/")

def otsu_sou(inner):
    s = inner.strip()
    if s.startswith("|") or s.endswith("|"):
        return "乙-表"
    if any(k in s for k in ("★", "読めぬ", "讀めぬ", "ep=")):
        return "乙-写"
    return "乙-殘"

def kou_sou(path):
    return "甲-對照" if any(k in path for k in FIX) else "甲-現物"

def inner_of(seg):
    return seg[1:-1] if len(seg) >= 2 and seg[0] == seg[-1] and seg[0] in "\"'" else seg

def run(src, name, path_col, seg_col, kind_col):
    lines = open(src, encoding="utf-8").read().split("\n")
    hdr, body = lines[0], [l for l in lines[1:] if l]
    ext_c = collections.Counter(); sou_c = collections.Counter(); files = collections.defaultdict(set)
    zan, kou_gen = [], []
    for l in body:
        f = l.split("\t")
        path = ast.literal_eval(f[path_col]); seg = ast.literal_eval(f[seg_col]); kind = f[kind_col]
        ext = path.rsplit(".", 1)[-1].lower() if "." in os.path.basename(path) else "(無)"
        inner = inner_of(seg)
        if kind == "乙":
            sou = otsu_sou(inner)
        else:
            sou = kou_sou(path)
        ext_c[(kind, ext)] += 1; sou_c[sou] += 1; files[sou].add(path)
        if sou == "乙-殘":
            zan.append("%s\t%s\t%r" % (path, f[path_col + 1], inner))
        if sou == "甲-現物":
            kou_gen.append("%s\t%s\t%r" % (path, f[path_col + 1], inner))
    out = ["# %s ―― 甲/乙 の層(入=%s)" % (name, src),
           "## 種×拡張子: 行"] + ["%s\t%s\t%d" % (k[0], k[1], v) for k, v in sorted(ext_c.items())] + \
          ["", "## 層: 行\t紙"] + ["%s\t%d\t%d" % (s, sou_c[s], len(files[s])) for s in ("甲-現物", "甲-對照", "乙-表", "乙-写", "乙-殘")] + \
          ["", "## 乙-殘 全行: path\t行番\tinner"] + zan + \
          ["", "## 甲-現物 全行: path\t行番\tinner"] + kou_gen + \
          ["", "## 甲-對照 の紙:"] + sorted(files["甲-對照"]) + \
          ["", "## 乙-表 の紙:"] + sorted(files["乙-表"]) + ["", "## 乙-写 の紙:"] + sorted(files["乙-写"])
    K.kaku("raw/%s.txt" % name, "\n".join(out) + "\n")
    print(open("raw/%s.txt" % name, encoding="utf-8").read())

run("raw/21_disk_kizu_rows.tsv", "23_disk_sou", 0, 3, 2)
run("raw/28_refs_union_kizu_rows.tsv", "24_refs_sou", 1, 4, 3)
