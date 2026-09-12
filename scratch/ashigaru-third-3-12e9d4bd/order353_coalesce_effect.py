# -*- coding: utf-8 -*-
"""令353 の器 ―― COALESCE patch が現に何を防ぐかを 字の鎖で一つに畳む。

§0 母（家老が先に引き 席が再測する・悉く讀取のみ）
  ROOT = /home/hakudoukai/karo3/wt-abbrev-guard-20260912 （家老の樹・書込 0）
  A = supabase/migrations/proposals/20260912_get_abbreviation_rules_coalesce_apply.sql
  B = supabase/migrations/20260909170000_snapshot_live_public_functions.sql
  C = backend/utils/abbreviation_checker.py

§1 網（撃つ前に逐語で鋳る・新条46）
  網1 = A の COALESCE の當たり ―― 境界付きで取る。
        engine = python re / pattern = (^|[^A-Za-z0-9_])COALESCE([^A-Za-z0-9_]|$) / 大小は区別する。
        「第二引数」は 括弧を数へて閉ぢ位置を求め 其の行の逐語を控へる（行番だけを証にせぬ・床(10)）。
  網2 = B の中から get_abbreviation_rules の塊のみを切り出す。
        切り方 = 頭註の行（-- ===== get_abbreviation_rules(date) で始まる行）から
                 直後の $function$; の行まで。塊の中で網1 を撃ち直す（0 か否か）。
        塊の 3 鍵 = 'official' / 'corrections' / 'detail_required' の行と 其の閉ぢ行。
  網3 = C の呼手 ―― rest/v1/rpc/get_abbreviation_rules を含む行と
        其の直後 8 行以内の json= の行（呼手が現に渡す物）。
        併せて null を吸ふ形（or []）の當たりを 函の名と共に取る。
  母の別 = A は 提案の file（DB 未適用と頭註に在る）・B は 既に樹に在る定義の写し・C は 製品の呼手。
  数へる単位 = 當たりは「行」で数へる（呼出回数ではない・床(22)）。

§2 床
  DB 0・psql 0・MCP 0・当て 0・check 0・patch 鋳造 0・書込 0（家老の樹は讀取のみ）。
  焚 1・走 1。値は名のみ・鍵の個々の値は写さぬ。
"""

import io
import os
import re

ROOT = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912"
A = "supabase/migrations/proposals/20260912_get_abbreviation_rules_coalesce_apply.sql"
B = "supabase/migrations/20260909170000_snapshot_live_public_functions.sql"
C = "backend/utils/abbreviation_checker.py"

NET_COALESCE = re.compile("(^|[^A-Za-z0-9_])COALESCE([^A-Za-z0-9_]|$)")
KEYS = ("'official'", "'corrections'", "'detail_required'")


def readlines(rel):
    p = os.path.join(ROOT, rel)
    with io.open(p, encoding="utf-8") as fh:
        return fh.read().split(chr(10))


def close_line_of(lines, start_idx):
    """start_idx の行から括弧を数へ、深さが 0 へ戻る行の index を返す。"""
    depth = 0
    started = False
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == "(":
                depth += 1
                started = True
            elif ch == ")":
                depth -= 1
        if started and depth <= 0:
            return i
    return -1


def hits(lines, net):
    return [i for i, t in enumerate(lines) if net.search(t)]


print("ROOT " + ROOT)
print("UNIT hit=line / 1-origin line numbers")
print("")

al = readlines(A)
print("---- A file=" + A)
print("A lines(split)=%d wc=%d" % (len(al), len(al) - 1))
ah = hits(al, NET_COALESCE)
print("A COALESCE hits=%d lines=%s" % (len(ah), ",".join(str(i + 1) for i in ah)))
for i in ah:
    j = close_line_of(al, i)
    print("  A open  L%d : %s" % (i + 1, al[i].strip()))
    print("  A close L%d : %s" % (j + 1, al[j].strip()))
second = []
for i in ah:
    j = close_line_of(al, i)
    m = re.search(r"\),\s*(.+?)\)\s*,?\s*$", al[j].strip())
    second.append(m.group(1) if m else "UNPARSED")
print("A second-arg literals = %s" % (" | ".join(second),))
print("A second-arg all-identical = %s" % (len(set(second)) == 1,))
print("")

bl = readlines(B)
print("---- B file=" + B)
print("B lines(split)=%d wc=%d" % (len(bl), len(bl) - 1))
head = [i for i, t in enumerate(bl) if t.startswith("-- ===== get_abbreviation_rules(date)")]
print("B block-head hits=%d lines=%s" % (len(head), ",".join(str(i + 1) for i in head)))
h = head[0]
end = -1
for i in range(h + 1, len(bl)):
    if bl[i].strip() == "$function$;":
        end = i
        break
blk = bl[h:end + 1]
print("B block L%d-L%d  block_lines=%d" % (h + 1, end + 1, len(blk)))
print("B block head verbatim : " + bl[h].strip())
bh = hits(blk, NET_COALESCE)
print("B block COALESCE hits=%d" % (len(bh),))
for k in KEYS:
    idx = [i for i, t in enumerate(blk) if t.strip().startswith(k + ",")]
    for i in idx:
        j = close_line_of(blk, i)
        print("  B key %s open  L%d : %s" % (k, h + i + 1, blk[i].strip()))
        print("  B key %s close L%d : %s" % (k, h + j + 1, blk[j].strip()))
agg = [i for i, t in enumerate(blk) if "jsonb_agg" in t]
print("B block jsonb_agg hits=%d lines=%s" % (len(agg), ",".join(str(h + i + 1) for i in agg)))
print("B block: 空の集合の時の返りを述べた字 = %d 行" % (len([t for t in blk if "NULL" in t or "null" in t]),))
print("")

cl = readlines(C)
print("---- C file=" + C)
print("C lines(split)=%d wc=%d" % (len(cl), len(cl) - 1))
rpc = [i for i, t in enumerate(cl) if "rest/v1/rpc/get_abbreviation_rules" in t]
print("C rpc-url hits=%d lines=%s" % (len(rpc), ",".join(str(i + 1) for i in rpc)))
for i in rpc:
    print("  C L%d : %s" % (i + 1, cl[i].strip()))
    for j in range(i, min(i + 9, len(cl))):
        if cl[j].strip().startswith("json="):
            print("  C payload L%d : %s" % (j + 1, cl[j].strip()))
            break
dateish = [i for i, t in enumerate(cl) if "p_diagnosis_date" in t or "diagnosis_date" in t]
print("C diagnosis-date hits=%d lines=%s" % (len(dateish), ",".join(str(i + 1) for i in dateish)))
orempty = [i for i, t in enumerate(cl) if re.search(r"or\s+\[\]", t)]
print("C or-empty hits=%d lines=%s" % (len(orempty), ",".join(str(i + 1) for i in orempty)))
for i in orempty:
    print("  C L%d : %s" % (i + 1, cl[i].strip()))
emp = [i for i, t in enumerate(cl) if t.startswith("def _empty_rules")]
print("C _empty_rules def L%d : %s" % (emp[0] + 1, cl[emp[0] + 2].strip()))
print("")
print("END")
