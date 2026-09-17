# -*- coding: utf-8 -*-
"""60 ―― ㋔ 註の嘘。8本の生器から「穴を塞いだ」と名乗る註を機械で引き、
55 の實測と突き合はせて 真/嘘/紛らはし を付ける。★判定の根拠は必ず 55 の行を指す★"""
import os, sys, io, re, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kaki as K
BUNDLE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))

MATO = ["scripts/agent_health_check.sh", "scripts/inbox_watcher.sh", "scripts/stop_hook_inbox.sh",
        "scripts/checks/karo_mac_gate4.sh", "scripts/checks/context_usage_warn.sh",
        "scripts/checks/karo_mac_dasumae_gate.sh",
        "scripts/watchdogs/enter_restart_common_watchdog.sh",
        "scripts/redundancy/shogun_report_watcher.sh"]

# ★宣★ 「塞いだ」と名乗る詞(此の語彙に当たる註のみを ㋔ の母數とする)
NANORI = [u"永久", u"塞", u"閉ぢ", u"閉じ", u"防", u"捕", u"fail-closed", u"倒す", u"倒れ",
          u"検め", u"検む", u"檢", u"通さ", u"落と", u"拒", u"守", u"數として", u"数として"]
RE_CHUU = re.compile(r'^\s*#')

rows = []
for rel in MATO:
    p = os.path.join(ROOT, rel)
    with io.open(p, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    for i, ln in enumerate(lines, 1):
        if not RE_CHUU.match(ln):
            continue
        hit = [w for w in NANORI if w in ln]
        if not hit:
            continue
        rows.append([rel, i, u"|".join(hit), ln.strip()])

K.kaku_tsv(os.path.join(BUNDLE, "nama", "60_chuu.tsv"), rows,
           ["#file", "行", "当たつた詞", "逐語"])
L = [u"= 60 ―― ㋔ 「塞いだ」と名乗る註の母數 =",
     u"刻=%s  的=%d file" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), len(MATO)),
     u"宣(語彙) = " + u" / ".join(NANORI),
     u"宣(形)   = 行頭(空白の後)が # で始まる行のみ。行末の追ひ註は取らぬ(★取れて居らぬ事を宣す★)",
     u"★当たつた註 = %d 行 / %d file★" % (len(rows), len(set(r[0] for r in rows))), u""]
cur = None
for r in rows:
    if r[0] != cur:
        cur = r[0]; L.append(u"-- %s --" % cur)
    L.append(u"  %s:%d  [%s]" % (r[0], r[1], r[2]))
    L.append(u"    %s" % r[3])
K.kaku(os.path.join(BUNDLE, "nama", "60_chuu.txt"), u"\n".join(L))
sys.stderr.write("60 done rows=%d\n" % len(rows))
sys.exit(4 if not rows else 0)
