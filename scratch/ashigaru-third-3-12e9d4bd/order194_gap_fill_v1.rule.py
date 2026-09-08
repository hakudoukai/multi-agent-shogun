# -*- coding: utf-8 -*-
u"""order194 追補の器 ― 前紙 §十二 の自訴 2 件を埋める

㋑ reports/ 82 行の内訳（名指しで外した物を ★数へ直す★）
㋺ walk 漏れ 1,360 file の内訳を ★種別に分ける★（binary / 権限 / decode / その他）

何を「一つ」と数へたか (床(30)):
  ・walk 漏れ = os.walk が挙げた file のうち utf-8 で讀めなかつた物 1 枚を 1
  ・種別は ★例外の型★ で分ける（推し量りでなく器が返した物）
  ・reports の行は `source_evidence_ids` を含む 1 行を 1

定め: 讀取のみ・走行 0・書込 0・DB 0・値/患者本文/secret を採らぬ
"""
import io, os, re, hashlib

TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
WORD = u"source_evidence_ids"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__"])
BOUND = re.compile(u"(^|[^A-Za-z0-9_])" + WORD + u"([^A-Za-z0-9_]|$)")

def sha(ap):
    h = hashlib.sha256(); h.update(io.open(ap, "rb").read()); return h.hexdigest()

def main():
    walked = 0
    ok = 0
    fail = {}          # 例外型 -> 枚数
    fail_ext = {}      # 例外型 -> 拡張子 -> 枚数
    reports_files = {} # rel -> [行番号...]
    for dp, dn, fn in os.walk(TREE):
        dn[:] = [x for x in dn if x not in SKIPD]
        for f in fn:
            ap = os.path.join(dp, f)
            rel = os.path.relpath(ap, TREE)
            walked += 1
            try:
                src = io.open(ap, encoding="utf-8").read()
            except Exception as e:
                k = type(e).__name__
                fail[k] = fail.get(k, 0) + 1
                ext = (os.path.splitext(f)[1] or u"(拡張子なし)").lower()
                fail_ext.setdefault(k, {})
                fail_ext[k][ext] = fail_ext[k].get(ext, 0) + 1
                continue
            ok += 1
            if rel.startswith(u"reports/") and WORD in src:
                hits = [i + 1 for i, l in enumerate(src.split(u"\n")) if WORD in l]
                if hits:
                    reports_files[rel] = hits

    print(u"## ㋺ walk 漏れの内訳")
    print(u"walked_files=%d" % walked)
    print(u"scanned_text_files=%d" % ok)
    print(u"unreadable_files=%d" % (walked - ok))
    print(u"")
    print(u"### 例外の型ごと（★器が返した型★・推し量りに非ず）")
    for k in sorted(fail, key=lambda x: -fail[x]):
        print(u"  %s = %d 枚" % (k, fail[k]))
        for ext in sorted(fail_ext[k], key=lambda x: -fail_ext[k][x])[:12]:
            print(u"      %-16s %d" % (ext, fail_ext[k][ext]))
    print(u"")
    print(u"## ㋑ reports/ の内訳（前紙で ★名指しで外した★ 物）")
    tot_lines = sum(len(v) for v in reports_files.values())
    print(u"reports_files=%d  reports_lines=%d" % (len(reports_files), tot_lines))
    print(u"")
    print(u"### file ごと（rel | sha256-64 | wc | split | hit_lines | bounded | unbounded）")
    b_tot = u_tot = 0
    for rel in sorted(reports_files):
        ap = os.path.join(TREE, rel)
        src = io.open(ap, encoding="utf-8").read()
        lines = src.split(u"\n")
        b = u = 0
        for ln in reports_files[rel]:
            if BOUND.search(lines[ln - 1]):
                b += 1
            else:
                u += 1
        b_tot += b; u_tot += u
        print(u"  %s | %s | %d | %d | %d | %d | %d"
              % (rel, sha(ap), src.count(u"\n"), len(lines), len(reports_files[rel]), b, u))
    print(u"")
    print(u"bounded_total=%d unbounded_total=%d" % (b_tot, u_tot))
    print(u"")
    print(u"### 逐語（rel:line | bounded | 行の字）")
    for rel in sorted(reports_files):
        lines = io.open(os.path.join(TREE, rel), encoding="utf-8").read().split(u"\n")
        for ln in reports_files[rel]:
            t = lines[ln - 1].strip()
            print(u"  %s:%d | %s | %s" % (rel, ln, (u"BOUNDED" if BOUND.search(lines[ln-1]) else u"UNBOUNDED"), t[:200]))

if __name__ == "__main__":
    main()
