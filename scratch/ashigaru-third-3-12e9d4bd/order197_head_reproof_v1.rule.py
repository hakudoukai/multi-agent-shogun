# -*- coding: utf-8 -*-
u"""order197: E1 ―― 8 枚の紙の「樹/HEAD/tree = 測定不能」を 今の git で遡り打ち直す。
讀取のみ(rev-parse/reflog/log/status/show)・走 0・書込 0・DB 0・gc/prune 0。
"""
import os, io, re, subprocess

D = u"scratch/ashigaru-third-3-12e9d4bd"
PAPERS = [u"order187_second_pair_and_source_v1", u"order188_split_sixteen_v1",
          u"order189_falsepos_cure_v1", u"order190_seventeen_sources_v1",
          u"order191_lot_self_close_v1", u"order192_test_escape_census_v1",
          u"order193_escape_surface_fix_v1", u"order195_typed_reproof_v1"]
TREES = [u"wt-bundle-fix4", u"wt-index-fix3", u"wt-pin-trace"]

def g(args, cwd):
    p = subprocess.Popen(["git"] + args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    o = p.communicate()[0].decode("utf-8", "replace")
    return p.returncode, o.strip()

print(u"## 甲 三樹の今の HEAD / tree / 枝 / porcelain / reflog 最新")
tinfo = {}
for w in TREES:
    t = u"/home/hakudoukai/a3/" + w
    rc_h, h = g(["rev-parse", "HEAD"], t)
    rc_t, tr = g(["rev-parse", "HEAD^{tree}"], t)
    rc_b, b = g(["rev-parse", "--abbrev-ref", "HEAD"], t)
    rc_p, po = g(["status", "--porcelain"], t)
    rc_r, rl = g(["reflog", "--date=iso", "-1"], t)
    # 家老 條 二百: 引けぬ時 引数を其の儘返す
    bad = (h == u"HEAD")
    npo = len([x for x in po.split(u"\n") if x.strip()])
    tinfo[w] = (h, tr, b, npo, rl)
    print(u"  %-16s rc=%d HEAD=%s" % (w, rc_h, h))
    print(u"    argv_echo_check(引けなんだか) = %s" % (u"★引けなんだ★" if bad else u"引けた"))
    print(u"    tree=%s  branch=%s  porcelain=%d 行" % (tr, b, npo))
    print(u"    reflog最新: %s" % rl)

print(u"")
print(u"## 乙 8 枚の紙 ―― as_of / 樹の名指し / HEAD の写しの在否")
for f in PAPERS:
    ap = os.path.join(D, f + u".md")
    s = io.open(ap, encoding="utf-8").read()
    m = re.search(u"as_of[^0-9]*([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+)", s)
    named = sorted(set(re.findall(u"/home/hakudoukai/a3/(wt-[a-z0-9-]+)", s)))
    shas = sorted(set(re.findall(u"47c8bc3b[0-9a-f]*", s)))
    npath = len(set(re.findall(u"(?:docs|frontend|backend|tests|scripts)/[A-Za-z0-9_./-]+", s)))
    print(u"  %-40s as_of=%s" % (f, m.group(1) if m else u"(無)"))
    print(u"      樹の名指し=%s / HEAD写し=%s / 測つた path 種=%d" %
          (u",".join(named) if named else u"★無★", u",".join(shas) if shas else u"★無★", npath))

print(u"")
print(u"## 丙 wt-bundle-fix4 の porcelain の中身（作業樹が HEAD からずれた枚数）")
rc, po = g(["status", "--porcelain"], u"/home/hakudoukai/a3/wt-bundle-fix4")
for l in po.split(u"\n"):
    if l.strip():
        print(u"  %s" % l)
