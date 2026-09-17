#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""km-117 届きの検め ―― ★時の窓で推さず、箱の尾を読んで胴を突き合はせる★。
★臺帳凍結後に生れた器★ ∴ 己も出目も臺帳の外。
"""
import hashlib, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kaki as K
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(B)
REPO = os.path.abspath("../../..")
box = os.path.join(REPO, "queue/inbox/karo-mac.yaml")
sent = open("raw/90_fumi_hondou.txt", encoding="utf-8").read()

L = ["# km-117 届きの検め ―― 刻 " + time.strftime("%Y-%m-%dT%H:%M:%S%z"),
     "箱\t" + box,
     "箱の在否\t" + ("在り" if os.path.exists(box) else "★無し★")]
if not os.path.exists(box):
    K.kaku("raw/92_todoke.txt", "\n".join(L)); raise SystemExit("★箱が無い★")

raw = open(box, encoding="utf-8").read()
L.append("箱 bytes\t%d" % len(raw.encode("utf-8")))
L.append("箱 行(LF数)\t%d" % raw.count("\n"))

import yaml
d = yaml.safe_load(raw)
msgs = d.get("messages") if isinstance(d, dict) else None
L.append("★messages 鍵で数へた項★\t%s" % (len(msgs) if isinstance(msgs, list) else "★yaml が解けぬ/鍵無し★"))
if not isinstance(msgs, list) or not msgs:
    K.kaku("raw/92_todoke.txt", "\n".join(L)); raise SystemExit("★項が読めぬ★")

# ★時の窓で推さぬ★ ―― 尾から順に、胴が一致する項を探す
hit = None
for i in range(len(msgs) - 1, -1, -1):
    m = msgs[i]
    if not isinstance(m, dict):
        continue
    c = m.get("content")
    if isinstance(c, str) and c.strip() == sent.strip():
        hit = (i, m); break
L.append("★胴の一致で当てた項★\t" + ("尾から%d番目(添字%d)" % (len(msgs) - 1 - hit[0], hit[0]) if hit else "★無し ―― 届いて居らぬか胴が変つた★"))
if hit:
    i, m = hit
    L.append("\tid\t%s" % m.get("id"))
    L.append("\ttimestamp\t%s" % m.get("timestamp"))
    L.append("\tfrom\t%s" % m.get("from"))
    L.append("\ttype\t%s" % m.get("type"))
    L.append("\tread\t%s" % m.get("read"))
    L.append("\t胴 字数(箱)\t%d" % len(m["content"]))
    L.append("\t胴 字数(送つた物)\t%d" % len(sent))
    L.append("\t胴 sha256(箱)\t%s" % hashlib.sha256(m["content"].strip().encode("utf-8")).hexdigest())
    L.append("\t胴 sha256(送つた物)\t%s" % hashlib.sha256(sent.strip().encode("utf-8")).hexdigest())
    L.append("\t★逐語一致★\t%s" % ("字面まで同じ" if m["content"] == sent else "★strip して同じ(端の改行のみ差)★"))
    L.append("\t★尾か★\t%s" % ("尾である" if i == len(msgs) - 1 else "★尾でない ―― 後から%d通着いた★" % (len(msgs) - 1 - i)))
L.append("-- 箱の尾 三項(送り手/型/刻/胴頭) --")
for m in msgs[-3:]:
    if isinstance(m, dict):
        c = (m.get("content") or "").replace("\n", "⏎")
        L.append("\t%s\t%s\t%s\t%s" % (m.get("from"), m.get("type"), m.get("timestamp"), c[:60]))
L += ["★之が意味せぬ事★",
      "・「届いた」は★箱に在る★の一事 ―― 家老が読んだ事も、監査へ回された事も言はぬ。",
      "・read: false は未読の印であつて、届かなんだ印ではない。",
      "・軍師mac は死箱(rc=68)∴ 監査は家老の中継を待つ ―― 此の数は其の中継を測らぬ。",
      "・此の器と此の出目は ★臺帳が凍つた後★ に生れた ∴ 臺帳にも門にも載らぬ。"]
K.kaku("raw/92_todoke.txt", "\n".join(L))
print("\n".join(L))
