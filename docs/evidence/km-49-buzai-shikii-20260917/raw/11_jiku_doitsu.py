#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""字句同一の證 ―― `is_num` の一行が生器と本器で ★一字も違はぬ★ 事を sha で示す。
家老裁 322099/322214 は sha16=9ebb7840f743508b と告げた。★受けた數は受けた刻に検める★(第48弾 ㋖-4 の直し)。
末尾改行を ★含めた★ 和と ★含めぬ★ 和の両方を出す ―― 「同じ sha16」が何の sha かを曖昧にせぬ為。"""
import hashlib, os, sys

NORI = "9ebb7840f743508b"
MATO = [
    "scripts/agent_health_check.sh",
    "scripts/inbox_watcher.sh",
    "scripts/checks/context_usage_warn.sh",
    "scripts/redundancy/shogun_report_watcher.sh",
    "scripts/checks/karo_mac_gate4.sh",
    "scripts/checks/karo_mac_dasumae_gate.sh",
    "scripts/watchdogs/enter_restart_common_watchdog.sh",
    "docs/evidence/km-49-buzai-shikii-20260917/raw/10_buzai_mon.sh",
]
root = sys.argv[1] if len(sys.argv) > 1 else "."
atta = 0
itchi = 0
print("宣 sha16 = %s(家老裁 322099/322214)" % NORI)
print("%-52s %-6s %-18s %-18s" % ("file", "行", "sha16(改行無)", "sha16(改行有)"))
for rel in MATO:
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        print("%-52s ★無★" % rel)
        continue
    for i, l in enumerate(open(p, encoding="utf-8").read().split("\n")):
        if l.startswith("is_num()"):
            atta += 1
            a = hashlib.sha256(l.encode()).hexdigest()[:16]
            b = hashlib.sha256((l + "\n").encode()).hexdigest()[:16]
            if a == NORI:
                itchi += 1
            print("%-52s L%-5d %-18s %-18s" % (rel, i + 1, a, b))
print("―― 見付けた `is_num` の行 = %d / 宣 sha16 に一致 = %d / 母數(当たつた file) = %d" % (atta, itchi, len(MATO)))
print("★宣の sha16 は ★末尾改行を含めぬ★ 和である(含めれば 4ec3d60221976dc3)。同じ「sha16」の名で二つが動く。★")
