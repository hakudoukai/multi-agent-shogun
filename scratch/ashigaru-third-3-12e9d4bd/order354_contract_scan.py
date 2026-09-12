# -*- coding: utf-8 -*-
"""令354 の器 -- atomic 契約の悉皆を字だけで数へる (DB 0 / 走 0 / 当て 0)。

§0 母 (讀取のみ・家老配下の樹)
  ROOT = /home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912
  F = backend/api/treatment_validation.py
  S = supabase/migrations/20260724235805_v6_save_draft_treatment_set_rpc_20260724.sql
  M = backend/db/migrations/049_karte_visit_items_documentation_identity.sql

§1 網 (新条㊻: 撃つ前に逐語で鋳る。engine = python re。境界は明示クラス)
  網1 = (^|[^A-Za-z0-9_])_ATOMIC_SAVE_ITEM_FIELDS([^A-Za-z0-9_]|$)   母 = F 全行
  網2 = (^|[^A-Za-z0-9_])_build_atomic_visit_item_snapshot([^A-Za-z0-9_]|$)  母 = F 全行
  網3 = (^|[^A-Za-z0-9_])documentation_field_id([^A-Za-z0-9_]|$)     母 = F, S, M 各全行
  網4 = ^\s*"([a-z_]+)":            母 = F の row.update( の塊のみ
  網5 = ^\s*([a-z_]+)[ ,]           母 = S の INSERT 列表 と jsonb_to_recordset の型表の塊のみ
  ※ 何れも註釈の行も拾ふ (粗さ)。数へる単位 = 行 (hit=line, 1-origin)。
     鍵の名は書くが 鍵の個々の値は一つも写さぬ。

§2 床
  DB 0 / psql 0 / MCP 0 / 当て 0 / 走 0 / 製品 code 書込 0 / rm 0 / find 0 / ssh 0。
  本器は讀取と数へのみを行ふ。
"""
import hashlib
import io
import os
import re

ROOT = "/home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912"
F = "backend/api/treatment_validation.py"
S = "supabase/migrations/20260724235805_v6_save_draft_treatment_set_rpc_20260724.sql"
M = "backend/db/migrations/049_karte_visit_items_documentation_identity.sql"


def bound(name):
    return re.compile("(^|[^A-Za-z0-9_])" + name + "([^A-Za-z0-9_]|$)")


NET1 = bound("_ATOMIC_SAVE_ITEM_FIELDS")
NET2 = bound("_build_atomic_visit_item_snapshot")
NET3 = bound("documentation_field_id")
NET4 = re.compile('^\\s*"([a-z_]+)":')
NET5 = re.compile('^\\s*([a-z_]+)[ ,]')


def load(rel):
    p = os.path.join(ROOT, rel)
    raw = io.open(p, "rb").read()
    s = raw.decode("utf-8")
    lines = s.split(chr(10))
    return {
        "rel": rel,
        "lines": lines,
        "split": len(lines),
        "wc": s.count(chr(10)),
        "sha": hashlib.sha256(raw).hexdigest()[:16],
    }


def hits(doc, net):
    return [i + 1 for i, x in enumerate(doc["lines"]) if net.search(x)]


def close_line_of(lines, start_idx):
    """start_idx (0-origin) から括弧を数へ 深さ 0 へ戻る行番 (1-origin) を返す。"""
    depth = 0
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
        if depth == 0 and i > start_idx:
            return i + 1
        if depth == 0 and i == start_idx and ("(" in lines[i] or "[" in lines[i]):
            return i + 1
    return -1


def block_names(lines, open_line, close_line, net):
    out = []
    for i in range(open_line, close_line - 1):
        m = net.match(lines[i])
        if m:
            out.append(m.group(1))
    return out


def main():
    df = load(F)
    ds = load(S)
    dm = load(M)
    print("ROOT " + ROOT)
    print("UNIT hit=line / 1-origin / digest=sha256 head16")
    for d in (df, ds, dm):
        print("MOTHER %s split=%d wc=%d sha16=%s" % (d["rel"], d["split"], d["wc"], d["sha"]))

    print("---- 段一: 契約の悉皆 ----")
    h1 = hits(df, NET1)
    print("F NET1 hits=%d lines=%s" % (len(h1), ",".join(str(x) for x in h1)))
    open_line = h1[0]
    close_line = close_line_of(df["lines"], open_line - 1)
    keys = []
    for i in range(open_line, close_line - 1):
        t = df["lines"][i].strip()
        if t.startswith('"') and t.endswith('",'):
            keys.append(t[1:-2])
    print("F tuple open L%d close L%d keycount=%d" % (open_line, close_line, len(keys)))
    print("F tuple keys = " + " ".join(keys))
    readers = [x for x in h1 if x != open_line]
    print("F readers of the tuple = %d lines=%s" % (len(readers), ",".join(str(x) for x in readers)))
    h2 = hits(df, NET2)
    print("F NET2 hits=%d lines=%s" % (len(h2), ",".join(str(x) for x in h2)))
    for r in readers:
        encl = [x for x in h2 if x <= r]
        print("  reader L%d : nearest NET2 line at or above = L%s" % (r, encl[-1] if encl else "none"))

    print("---- 段一b: 組み直した行の鍵 ----")
    upd = [i + 1 for i, x in enumerate(df["lines"]) if x.strip() == "row.update("]
    print("F row.update( lines=%s" % ",".join(str(x) for x in upd))
    uo = upd[0]
    uc = close_line_of(df["lines"], uo - 1)
    unames = block_names(df["lines"], uo, uc, NET4)
    print("F row.update block L%d-L%d names=%d : %s" % (uo, uc, len(unames), " ".join(unames)))
    union = list(keys)
    for n in unames:
        if n not in union:
            union.append(n)
    print("F emitted row keycount = %d (tuple %d + update-only %d)"
          % (len(union), len(keys), len(union) - len(keys)))

    print("---- 段三: RPC 側の受け口 ----")
    ins = [i + 1 for i, x in enumerate(ds["lines"])
           if "INSERT INTO public.karte_visit_items" in x]
    print("S insert lines=%s" % ",".join(str(x) for x in ins))
    io_ = ins[0]
    ic = close_line_of(ds["lines"], io_ - 1)
    cols = []
    for i in range(io_, ic - 1):
        for tok in re.findall("[a-z_]+", ds["lines"][i]):
            cols.append(tok)
    print("S insert column block L%d-L%d colcount=%d" % (io_, ic, len(cols)))
    print("S insert columns = " + " ".join(cols))
    rec = [i + 1 for i, x in enumerate(ds["lines"]) if "jsonb_to_recordset(p_items)" in x]
    print("S jsonb_to_recordset lines=%s" % ",".join(str(x) for x in rec))
    target = [x for x in rec if x > io_]
    ro = target[0]
    rc = close_line_of(ds["lines"], ro - 1)
    fields = block_names(ds["lines"], ro, rc, NET5)
    print("S recordset block L%d-L%d fieldcount=%d" % (ro, rc, len(fields)))
    print("S recordset fields = " + " ".join(fields))

    print("---- 網3: 当該鍵の悉皆 ----")
    for d in (df, ds, dm):
        h = hits(d, NET3)
        print("NET3 %s hits=%d lines=%s" % (d["rel"], len(h), ",".join(str(x) for x in h)))
    print("NET3 in S insert columns = %s" % ("yes" if "documentation_field_id" in cols else "no"))
    print("NET3 in S recordset fields = %s" % ("yes" if "documentation_field_id" in fields else "no"))
    print("NET3 in F tuple keys = %s" % ("yes" if "documentation_field_id" in keys else "no"))

    print("---- 錨 (patch の当て所を実物で確かめる) ----")
    for n in (4105, 4106, 4107, 4108):
        print("F L%d : %s" % (n, df["lines"][n - 1]))
    print("END")


main()
