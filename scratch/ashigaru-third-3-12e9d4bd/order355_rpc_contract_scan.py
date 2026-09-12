# -*- coding: utf-8 -*-
"""令355 の器 -- RPC の受け口と入れる列を字だけで数へ 錨を逐語で刷る (DB 0 / 走 0 / 当て 0)。

§0 母 (讀取のみ・家老配下の樹)
  ROOT = /home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912
  S  = supabase/migrations/20260724235805_v6_save_draft_treatment_set_rpc_20260724.sql
  S2 = supabase/migrations/20260726014452_v6_amendment_exact_clone_carry_forward_20260726.sql
  S3 = supabase/migrations/20260724225117_v6_create_amendment_draft_rpc_20260724.sql

§1 網 (新条㊻: 撃つ前に逐語で鋳る。engine = python re。境界は明示クラス)
  網3 = (^|[^A-Za-z0-9_])documentation_field_id([^A-Za-z0-9_]|$)  母 = S, S2, S3 各全行
  網5 = ^\s*([a-z_]+)[ ,]           母 = S の入れる列の塊 と 受け口の型の塊 のみ
  網6 = INSERT INTO public.karte(下線)visit(下線)items の素の当たり  母 = S, S2, S3
  網7 = jsonb(下線)to(下線)recordset の素の当たり                   母 = S, S2, S3
  ※ 註釈の行も拾ふ (粗さ)。数へる単位 = 行 (hit=line, 1-origin)。
     鍵と列の名は書くが 鍵の個々の値は一つも写さぬ。

§2 床
  DB 0 / psql 0 / MCP 0 / 当て 0 / 走 0 / 製品 code 書込 0 / rm 0 / find 0 / ssh 0。
  本器は讀取と数へと錨の刷りのみを行ふ。
"""
import hashlib
import io
import os
import re

ROOT = "/home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912"
S = "supabase/migrations/20260724235805_v6_save_draft_treatment_set_rpc_20260724.sql"
S2 = "supabase/migrations/20260726014452_v6_amendment_exact_clone_carry_forward_20260726.sql"
S3 = "supabase/migrations/20260724225117_v6_create_amendment_draft_rpc_20260724.sql"

NET3 = re.compile("(^|[^A-Za-z0-9_])documentation_field_id([^A-Za-z0-9_]|$)")
NET5 = re.compile('^\\s*([a-z_]+)[ ,]')
INS = "INSERT INTO public.karte_visit_items"
REC = "jsonb_to_recordset"


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


def plain(doc, needle):
    return [i + 1 for i, x in enumerate(doc["lines"]) if needle in x]


def close_line_of(lines, start_idx):
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


def show(doc, n):
    t = doc["lines"][n - 1]
    lead = len(t) - len(t.lstrip(" "))
    print("  L%d lead=%d |%s|" % (n, lead, t))


def main():
    ds = load(S)
    d2 = load(S2)
    d3 = load(S3)
    print("ROOT " + ROOT)
    print("UNIT hit=line / 1-origin / digest=sha256 head16")
    for d in (ds, d2, d3):
        print("MOTHER %s split=%d wc=%d sha16=%s" % (d["rel"], d["split"], d["wc"], d["sha"]))

    print("---- 段一: 受け口と入れる列 ----")
    ins = plain(ds, INS)
    print("S insert lines=%s" % ",".join(str(x) for x in ins))
    io_ = ins[0]
    ic = close_line_of(ds["lines"], io_ - 1)
    cols = []
    for i in range(io_, ic - 1):
        for tok in re.findall("[a-z_]+", ds["lines"][i]):
            cols.append(tok)
    print("S 入れる列の塊 L%d-L%d count=%d" % (io_, ic, len(cols)))
    print("S 入れる列 = " + " ".join(cols))
    sel = [i + 1 for i, x in enumerate(ds["lines"]) if x.strip() == "SELECT" and i + 1 > ic]
    so = sel[0]
    rec = [x for x in plain(ds, REC) if x > io_]
    ro = rec[0]
    rc = close_line_of(ds["lines"], ro - 1)
    print("S SELECT の塊 L%d-L%d" % (so, ro - 1))
    fields = []
    for i in range(ro, rc - 1):
        m = NET5.match(ds["lines"][i])
        if m:
            fields.append(m.group(1))
    print("S 受け口の型の塊 L%d-L%d count=%d" % (ro, rc, len(fields)))
    print("S 受け口の型 = " + " ".join(fields))
    print("S 当該鍵 入れる列に在るか = %s / 受け口に在るか = %s"
          % ("yes" if "documentation_field_id" in cols else "no",
             "yes" if "documentation_field_id" in fields else "no"))
    for d in (ds, d2, d3):
        h = hits(d, NET3)
        print("NET3 %s hits=%d lines=%s" % (d["rel"], len(h), ",".join(str(x) for x in h)))

    print("---- 錨 (二本の patch の当て所を実物で確かめる) ----")
    print("錨A 受け口へ足す所 = L384 の次")
    for n in (383, 384, 385, 386):
        show(ds, n)
    print("錨B-1 入れる列へ足す所 = L356 の中")
    for n in (355, 356, 357):
        show(ds, n)
    print("錨B-2 SELECT へ足す所 = L365 の中")
    for n in (364, 365, 366):
        show(ds, n)

    print("---- 段三: 尚 残る所 ----")
    for d in (ds, d2, d3):
        print("%s : insert=%s recordset=%s"
              % (d["rel"].split("/")[-1],
                 ",".join(str(x) for x in plain(d, INS)),
                 ",".join(str(x) for x in plain(d, REC))))
    print("END")


main()
