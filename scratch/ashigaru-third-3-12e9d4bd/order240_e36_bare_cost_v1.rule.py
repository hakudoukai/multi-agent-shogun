# -*- coding: utf-8 -*-
# order240 E36: decide whether the bare-N branch goes INTO the instrument.
#   measures the MARGINAL effect of F7_bare AFTER F6/F8/F9 are already cast,
#   i.e. how much of the residue (the only region where a true no-denominator
#   claim was ever found by hand) F7 would swallow.
# read-only. no product run. cwd = /home/hakudoukai/multi-agent-shogun
import io, os, glob, re, collections, contextlib
D = u"scratch/ashigaru-third-3-12e9d4bd"
G = os.path.join(D, u"order239_e35_gap_v1.rule.py")
g = {"__name__": "__main__"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(io.open(G, encoding="utf-8").read(), G, "exec"), g)
scan = g["scan"]; mask = g["mask"]; F6 = g["F6"]; F8 = g["F8"]; OLDBO = g["OLDBO"]
papers_docs = g["papers"]; letters_docs = g["letters"]
F7 = re.compile(u"(^|[^0-9A-Za-z_])[0-9][0-9,]*([^0-9A-Za-z_]|$)")
def split4(docs):
    c = collections.Counter(); res_f7 = []; res_no = []
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln)
            prev = mask(lines[i-1]) if i > 0 else u""
            f9 = bool(OLDBO.search(prev) or F6.search(prev) or F8.search(prev))
            covered = bool(F6.search(m) or F8.search(m)) or f9
            c[u"claims_without_F1_F5"] += 1
            if covered:
                c[u"covered_by_F6_F8_F9"] += 1
                continue
            c[u"residue"] += 1
            if F7.search(m): c[u"residue_swallowed_by_F7"] += 1; res_f7.append((w, ln))
            else:            c[u"residue_survives_F7"] += 1;    res_no.append((w, ln))
    return c, res_f7, res_no
for name, docs in ((u"papers", papers_docs), (u"letters", letters_docs)):
    c, rf, rn = split4(docs)
    print(u"[%s]" % name)
    for k in (u"claims_without_F1_F5", u"covered_by_F6_F8_F9", u"residue",
              u"residue_swallowed_by_F7", u"residue_survives_F7"):
        print(u"   %-26s %5d" % (k, c[k]))
    if name == u"letters":
        print(u"   ---- sample: residue that SURVIVES F7 (数が一つも無い行) ----")
        step = max(1, len(rn)//8); n = 0
        for k in range(0, len(rn), step):
            n += 1
            if n > 8: break
            print(u"   S%d [%s] %s" % (n, rn[k][0], rn[k][1].strip()[:105]))
# the 7 hand-labelled lot rows: are the 5 bare-number ones reached without F7?
LOT = {u"msg_20260908_042426_3696d114": u"96",  u"msg_20260908_042649_8abd966e": u"96",
       u"msg_20260908_042815_64a33631": u"53",  u"msg_20260908_043316_f532a142": u"54",
       u"msg_20260908_085717_abac3049": u"(act)", u"msg_20260908_202104_acb3734e": u"14file",
       u"msg_20260909_065735_c32689d0": u"12"}
ME = u"ashigaru-third-3"
SRC = (u"queue/inbox/karo*.yaml", u"queue/inbox/_archive/karo*.yaml",
       u"queue/inbox/archive/karo*.yaml", u"queue/archive/*.yaml")
pb = g["parse_block"]; seen = set()
print(u"---- ground truth: are the 7 lot rows reached WITHOUT F7? ----")
for pat in SRC:
    for f in sorted(glob.glob(pat)):
        t = io.open(f, encoding="utf-8", errors="replace").read()
        for raw in re.split(u"(?m)^- ", t)[1:]:
            d = pb(u"  " + raw)
            if d.get(u"from", u"").strip() != ME: continue
            i = d.get(u"id", u"").strip()
            if i not in LOT or i in seen: continue
            seen.add(i)
            lines = d.get(u"content", u"").split(u"\n")
            for (k, w, ln) in scan(lines):
                m = mask(ln)
                prev = mask(lines[k-1]) if k > 0 else u""
                f9 = bool(OLDBO.search(prev) or F6.search(prev) or F8.search(prev))
                print(u"   %s bo=%-6s F6=%d F8=%d F9=%d F7=%d | %s"
                      % (i[-8:], LOT[i], bool(F6.search(m)), bool(F8.search(m)),
                         f9, bool(F7.search(m)), ln.strip()[:60]))
