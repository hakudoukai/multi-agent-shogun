# -*- coding: utf-8 -*-
"""
order356_rewrite_path_scan.py -- 令356 段一の器（一度きり起動・焚1）

§0 母
  ROOT = /home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912 （作業樹・讀取のみ）
  S26  = supabase/migrations/20260726014452_v6_amendment_exact_clone_carry_forward_20260726.sql
  対象の 5 箇所 = L156 L184 L278 L343 L442 （令355 の器が刷つた行番）

§1 網（撃つ前に逐語で鋳る）
  網3 = 当該鍵 documentation-field-id を 名の前後を英数字と下線以外の字で挟む形で当てる。
        engine = python の re。母 = S26 全行。単位 = 行（1 起点）。
  網6 = 受け口の頭 = 素の字 jsonb-to-recordset を含む行。
  網7 = 受け口の型の行 = 頭の空白の後に 小文字と下線の連なり が来る行。
        塊の終りは 閉じ丸括弧のみ（前後の空白を除く）の行。
  網8 = 三分け ―― 受け口の型か 入れる列か 値の塊か を
        ㋐ AS 別名 開き丸括弧 の形を持つ塊 = 受け口の型
        ㋑ INSERT INTO を上に持つ塊 = 入れる列
        ㋒ SELECT を頭に持ち 式を並べる塊 = 値の塊
        の三つで分ける。本器は各箇所の上 12 行を刷り 人が字で確かめられる様にする。

§2 床
  当て 0（git apply --check のみ・本器は check すら打たぬ）・走 0・DB 0・psql 0・MCP 0
  製品 code 書込 0・rm 0・find 0・install 0・一時 file 0。焚 1。
  鍵の個々の値は一つも刷らぬ。刷るのは 名・行番・数・型の字のみ。
"""
import hashlib
import io
import os
import re

ROOT = "/home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912"
S26 = "supabase/migrations/20260726014452_v6_amendment_exact_clone_carry_forward_20260726.sql"
SITES = [156, 184, 278, 343, 442]

NET3 = re.compile("(^|[^A-Za-z0-9_])documentation_field_id([^A-Za-z0-9_]|$)")
NET6 = "jsonb_to_recordset"
NET7 = re.compile("^([ ]*)([a-z_]+)[ ]")
CLOSE = re.compile("^[ ]*\\)[ ]*,?[ ]*$")


def read(rel):
    p = os.path.join(ROOT, rel)
    b = io.open(p, "rb").read()
    s = b.decode("utf-8")
    return s, hashlib.sha256(b).hexdigest()[:16]


def show(lines, n):
    t = lines[n - 1]
    print("    L%d lead=%d |%s|" % (n, len(t) - len(t.lstrip(" ")), t))


def main():
    s, sha = read(S26)
    lines = s.split(chr(10))
    print("MOTHER S26 split=%d wc=%d sha16=%s" % (len(lines), s.count(chr(10)), sha))

    hits = [i + 1 for i, t in enumerate(lines) if NET3.search(t)]
    print("NET3 S26 hits=%d lines=%s" % (len(hits), hits))

    heads = [i + 1 for i, t in enumerate(lines) if NET6 in t]
    print("NET6 S26 heads=%s" % (heads,))

    for n in SITES:
        head = lines[n - 1]
        print("=== SITE L%d ===" % n)
        print("  head lead=%d |%s|" % (len(head) - len(head.lstrip(" ")), head))
        kind = "uketsuke(受け口の型)" if (" AS " in head and head.rstrip().endswith("(")) else "OTHER"
        print("  kind=%s" % kind)
        print("  上 4 行（文脈）:")
        for k in range(n - 4, n):
            show(lines, k)
        j = n
        names = []
        while j < len(lines):
            t = lines[j]
            if CLOSE.match(t):
                break
            m = NET7.match(t)
            if m:
                names.append((j + 1, len(m.group(1)), m.group(2)))
            j += 1
        print("  塊 = L%d-L%d fieldcount=%d close=L%d" % (n + 1, j, len(names), j + 1))
        for (ln, lead, nm) in names:
            print("    L%d lead=%d name=%s" % (ln, lead, nm))
        has = [ln for (ln, lead, nm) in names if nm == "documentation_field_id"]
        anchor = [ln for (ln, lead, nm) in names if nm == "logical_item_id"]
        print("  当該鍵 在るか=%s / logical_item_id の行=%s" % ("yes" if has else "no", anchor))
    print("END (RC=0)")


main()
