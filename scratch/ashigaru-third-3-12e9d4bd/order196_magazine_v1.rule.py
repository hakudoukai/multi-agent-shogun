# -*- coding: utf-8 -*-
u"""order196: 己の弾倉 ―― 紙 order180〜195 の ★未測★ を悉皆で拾ふ。讀取のみ・走 0・書込 0・DB 0。
数へ方: 行を 1 と数へる(床30)。母集団 = 名が order18x/19x で始まる .md（名で判ず・下に列挙）。
"""
import os, io, re, hashlib
D = u"scratch/ashigaru-third-3-12e9d4bd"
PAT = re.compile(u"^order(1[89][0-9])_.*\\.md$")
MARK = [u"測定不能", u"測れなかつた", u"測れて居らぬ", u"数へて居らぬ", u"分けて居らぬ", u"保つて居らぬ"]

def sha(p):
    h = hashlib.sha256(); h.update(io.open(p, "rb").read()); return h.hexdigest()

names = sorted([f for f in os.listdir(D) if PAT.match(f)])
print(u"## §零 母集団")
print(u"紙 = %d 枚（名が order18x/19x の .md・名で判ず）" % len(names))
print(u"")
print(u"| 紙 | sha256 | wc | split | byte | as_of |")
print(u"|---|---|---:|---:|---:|---|")
docs = {}
for f in names:
    ap = os.path.join(D, f)
    b = io.open(ap, "rb").read(); t = b.decode("utf-8")
    docs[f] = t
    m = re.search(u"as_of[:：]?\\s*`?([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:+]+)", t)
    print(u"| %s | %s | %d | %d | %d | %s |" % (f, sha(ap), b.count(b"\n"), len(t.split(u"\n")), len(b), m.group(1) if m else u"(無)"))

print(u"")
print(u"## §一 ★未測★ の悉皆（語ごと・逐語）")
tot = {}
for w in MARK:
    tot[w] = 0
for f in names:
    lines = docs[f].split(u"\n")
    hit = []
    for i, l in enumerate(lines):
        for w in MARK:
            if w in l:
                hit.append((i + 1, w, l.strip()))
                tot[w] += 1
                break
    if hit:
        print(u"")
        print(u"### %s（%d 行）" % (f, len(hit)))
        for ln, w, l in hit:
            print(u"  %s:%d | %s | %s" % (f, ln, w, l[:180]))
print(u"")
print(u"## §二 語ごとの度数")
for w in MARK:
    print(u"  %-10s %4d 行" % (w, tot[w]))
print(u"  合計 %d 行" % sum(tot.values()))

print(u"")
print(u"## §三 『繰越』節の項目（見出しの下の番号行）")
for f in names:
    lines = docs[f].split(u"\n")
    inx = False
    got = []
    for i, l in enumerate(lines):
        if l.startswith(u"#") and u"繰越" in l:
            inx = True; continue
        if inx and l.startswith(u"#"):
            inx = False
        if inx and re.match(u"^\\s*[0-9]+[.)]\\s*\\S", l):
            got.append((i + 1, l.strip()))
    if got:
        print(u"")
        print(u"### %s（%d 項）" % (f, len(got)))
        for ln, l in got:
            print(u"  %s:%d | %s" % (f, ln, l[:200]))
