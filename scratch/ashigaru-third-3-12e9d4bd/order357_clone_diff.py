# -*- coding: utf-8 -*-
# order357_clone_diff.py
# muki: hitotsu no kan no honbun to sousou no honbun wo gyou de tsukiawase,
#       sa no gyou dake wo suru. marautsushi no utsushisokone wo ateru ki.
# NOTE: this file was NOT executed under order 357 (floor: hashiri 0).
import hashlib
import io
import sys

ROOT = "/home/hakudoukai/a3/wt-fa06a3a1-caller-test-20260912"
MOTHER = ROOT + "/supabase/migrations/20260726014452_v6_amendment_exact_clone_carry_forward_20260726.sql"
DRAFT = ("/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/"
         "order357_draft/20260912090000_v6_amendment_doc_field_carry_forward_20260912.sql.draft")

HEAD_M = "CREATE FUNCTION public.save_v6_draft_treatment_set("
HEAD_D = "CREATE OR REPLACE FUNCTION public.save_v6_draft_treatment_set("
TERM = "$function$;"


def read_lines(path):
    # splitlines wo hontai to suru (order 357 mei)
    text = io.open(path, encoding="utf-8").read()
    return text, text.splitlines()


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def carve(lines, head, label):
    starts = [i for i, x in enumerate(lines) if x == head]
    if len(starts) != 1:
        print("CARVE %s head_hits=%d (want 1)" % (label, len(starts)))
        return None
    s = starts[0]
    ends = [i for i, x in enumerate(lines) if i > s and x == TERM]
    if not ends:
        print("CARVE %s term_hits=0 (want >=1)" % label)
        return None
    e = ends[0]
    return (s, e, lines[s:e + 1])


def main():
    mt, ml = read_lines(MOTHER)
    dt, dl = read_lines(DRAFT)
    print("MOTHER split=%d wc=%d sha16=%s" % (len(mt.split(chr(10))), mt.count(chr(10)), sha16(mt)))
    print("DRAFT  split=%d wc=%d sha16=%s" % (len(dt.split(chr(10))), dt.count(chr(10)), sha16(dt)))

    a = carve(ml, HEAD_M, "MOTHER")
    b = carve(dl, HEAD_D, "DRAFT")
    if a is None or b is None:
        return 2
    print("MOTHER region L%d-L%d n=%d sha16=%s"
          % (a[0] + 1, a[1] + 1, len(a[2]), sha16(chr(10).join(a[2]))))
    print("DRAFT  region L%d-L%d n=%d sha16=%s"
          % (b[0] + 1, b[1] + 1, len(b[2]), sha16(chr(10).join(b[2]))))

    x, y = a[2], b[2]
    if len(x) != len(y):
        print("LEN_MISMATCH mother=%d draft=%d delta=%d" % (len(x), len(y), len(y) - len(x)))
    n = min(len(x), len(y))
    diff = 0
    for i in range(n):
        if x[i] != y[i]:
            diff += 1
            print("DIFF idx=%d motherL%d draftL%d" % (i, a[0] + 1 + i, b[0] + 1 + i))
            print("  M|%s|" % x[i])
            print("  D|%s|" % y[i])
    for i in range(n, len(x)):
        diff += 1
        print("ONLY_M idx=%d motherL%d" % (i, a[0] + 1 + i))
        print("  M|%s|" % x[i])
    for i in range(n, len(y)):
        diff += 1
        print("ONLY_D idx=%d draftL%d" % (i, b[0] + 1 + i))
        print("  D|%s|" % y[i])
    print("DIFF_LINES=%d" % diff)
    # kiite iru ka wo ki jishin ni iwaseru: atama no ichi gyou dake ga chigau nara 0
    only_head = (diff == 1 and len(x) == len(y) and x[0] != y[0])
    print("ONLY_HEAD_DIFFERS=%s" % ("yes" if only_head else "no"))
    return 0 if only_head else 1


if __name__ == "__main__":
    sys.exit(main())
