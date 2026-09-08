# -*- coding: utf-8 -*-
u"""order194 規 — source_docs / source_evidence_ids の行根拠と匿名 fixture/row の欠落

定め (型 8 項に沿ふ):
 1) 的の樹 = /home/hakudoukai/a3/wt-bundle-fix4 (repo の外の別樹)
 2) 二語を ★別々に★ 数へる (足さぬ)
 3) 「行根拠」は file:行:逐語 で出す (「在る筈」を書かぬ)
 4) ★境界形と平形を両方★ 取り、差を出す
    (legal_source_docs の如く 前に語が付く形を 別値で見る = 條 o177/o178)
 5) 各 file の sha256 ★64 桁★ を出す (頭 16 で済ませぬ)
 6) 数は wc(改行数) と split 片数の双方 (床(32))
 7) 讀取のみ・走行 0・書込 0・DB 0
 8) 値・患者本文・secret を採らぬ (語の在処と度数のみ・逐語は当該行の字面に限る)
"""
import io, os, re, hashlib

ROOT = u"/home/hakudoukai/a3/wt-bundle-fix4"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__"])
WORDS = [u"source_docs", u"source_evidence_ids"]
BOUND = u"[^A-Za-z0-9_]"

def files():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [x for x in dn if x not in SKIPD]
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(out)

def sha(rel):
    h = hashlib.sha256()
    h.update(io.open(os.path.join(ROOT, rel), "rb").read())
    return h.hexdigest()

def bucket(rel):
    for pre in (u"backend/api/", u"backend/services/", u"backend/tests/",
                u"tests/", u"docs/", u"reports/", u"src/", u"frontend/"):
        if rel.startswith(pre):
            return pre.rstrip(u"/")
    return u"<other>"

def main():
    fl = files()
    print(u"tree=%s" % ROOT)
    print(u"walked_files=%d" % len(fl))
    hits = {}          # word -> list of (rel, lineno, verbatim, is_bounded)
    for w in WORDS:
        hits[w] = []
    re_b = dict((w, re.compile(u"(^|" + BOUND + u")" + w + u"(" + BOUND + u"|$)")) for w in WORDS)
    scanned = 0
    for rel in fl:
        ap = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(ap) > 4 * 1024 * 1024:
                continue
            src = io.open(ap, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        if not any(w in src for w in WORDS):
            continue
        lines = src.split(u"\n")
        for i, l in enumerate(lines):
            for w in WORDS:
                if w in l:
                    hits[w].append((rel, i + 1, l.strip()[:200], bool(re_b[w].search(l))))
    print(u"scanned_text_files=%d" % scanned)
    print(u"")
    for w in WORDS:
        h = hits[w]
        fs = sorted(set(x[0] for x in h))
        bn = [x for x in h if x[3]]
        ub = [x for x in h if not x[3]]
        print(u"## WORD=%s" % w)
        print(u"files=%d lines=%d bounded_lines=%d unbounded_only_lines=%d" % (len(fs), len(h), len(bn), len(ub)))
        print(u"### by bucket")
        bk = {}
        for x in h:
            bk[bucket(x[0])] = bk.get(bucket(x[0]), 0) + 1
        for k in sorted(bk):
            print(u"  %s = %d lines" % (k, bk[k]))
        print(u"### files (rel | sha256-64 | wc | split | hit_lines)")
        for rel in fs:
            n = len([x for x in h if x[0] == rel])
            try:
                src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
                lc = src.split(u"\n")
                print(u"  %s | %s | %d | %d | %d" % (rel, sha(rel), len(lc) - 1, len(lc), n))
            except Exception:
                print(u"  %s | <unreadable> | 0 | 0 | %d" % (rel, n))
        print(u"### lines (rel:line | bounded | verbatim)")
        for (rel, ln, v, b) in h:
            print(u"  %s:%d | %s | %s" % (rel, ln, u"bounded" if b else u"UNBOUNDED", v))
        print(u"")

if __name__ == "__main__":
    main()
