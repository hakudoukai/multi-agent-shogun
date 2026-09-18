# -*- coding: utf-8 -*-
"""★『保護者解説 1:1 維持』を app 自身の器で測る★(km-175 ㋔③)
己の regex で鍵を数へるのは ★二の器★ に過ぎぬ ―― 「鍵が在る」は「解決する」の證に成らぬ
(hooks/useParentExplanationLink.ts の isS3S4EntryEmpty が ★空の雛形を fail-closed で null にする★)。
∴ 一の器は ★製品樹の既存 test★(episodes/__tests__/episodes.test.tsx)であり、本器は其れを呼ぶだけ。
四札: 刻=冠 / 根=frontend / rc=vitest の returncode(★管を通さぬ★) / 対照= ⑴suite 内蔵の負対照(空表→未解決15)
      ⑵『26 本走つた』= 器が現に測つた證(0 本で緑は緑に非ず)。"""
import os
import re
import sys
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

FE = "/Users/momizimac/DentalBI/frontend"
MATO = "src/features/child-passport/story-engine/episodes/__tests__/episodes.test.tsx"
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

p = subprocess.run(["npx", "vitest", "run", MATO], cwd=FE,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
out = p.stdout.decode("utf-8", "replace"); err = p.stderr.decode("utf-8", "replace")
kaku(os.path.join(BUNDLE, "raw", "66_1to1_test.out"), out)
kaku(os.path.join(BUNDLE, "raw", "66_1to1_test.err"), err)
kaku(os.path.join(BUNDLE, "raw", "66_1to1_test.rc"), str(p.returncode) + "\n")

m_t = re.search(r"Tests\s+(\d+) passed \((\d+)\)", out)
m_f = re.search(r"Test Files\s+(\d+) passed \((\d+)\)", out)
hon = int(m_t.group(1)) if m_t else 0
zen = int(m_t.group(2)) if m_t else 0
skip = re.findall(r"(\d+) skipped", out)

# suite 内蔵の負対照 ―― 逐語で在る事を確かめる(★在ると信ぜず、字面を当てる★)
tp = os.path.join(FE, MATO)
src = open(tp, encoding="utf-8").read()
# ★疵(己)★ 初版は ★一行の中で★ emptyTable と unresolved の AND を取つた ―― 二語は別行ゆゑ
# 「対照が見えぬ」と刷つた(對照は現に在る)。∴ ★it の塊で切る★。
buro = re.split(r"\n  it\(", src)
fu = ["it(" + b.split("\n")[0] for b in buro if "emptyTable" in b and "unresolved" in b]
fu_kazu = re.findall(r"expect\(unresolved\.length\)\.toBe\((\d+)\)", src)
ichi_ichi = [l.strip() for l in src.split("\n") if re.search(r"it\('2\. 1:1", l)]

kaku_tsv(os.path.join(BUNDLE, "raw", "67_1to1_app_no_ki.tsv"),
         [["器", "npx vitest run " + MATO, "cwd=" + FE, KOKU],
          ["rc(★管を通さぬ★)", p.returncode, "0 が緑", "★緑★" if p.returncode == 0 else "★赤★"],
          ["走つた本数", hon, "母數 %d" % zen, "★0 本で緑は緑に非ず★ ―― %d 本現に走つた" % hon],
          ["skip", ", ".join(skip) or "0", "SKIP=FAIL の條", "★skip 無し★" if not skip else "★skip 在り=未完了★"],
          ["1:1 の断(逐語)", ichi_ichi[0][:120] if ichi_ichi else "★見えぬ★", "episodes.test.tsx", "-"],
          ["★内蔵 負対照★", (fu[0][:100] if fu else "★見えぬ★"),
           "空表を渡すと未解決が %s に成る断" % (", ".join(fu_kazu) or "-"),
           "★対照在り★" if fu and fu_kazu else "★対照が見えぬ★"],
          ["己の二の器(regex)", "driver/60 → raw/63_b2_hogosha_1to1.tsv", "話15・鍵15・未解決0・孤児0・重なり0",
           "★鍵の在否のみ ―― 中身の空は見ぬ(∴一の器が要る)★"]],
         header=["何を", "値", "言", "判"])
print("app の器: rc=%d / %d 本通(母數 %d) / skip=%s" % (p.returncode, hon, zen, ", ".join(skip) or "無し"))
print("内蔵 負対照: %s(未解決 %s)" % ("在り" if fu else "見えぬ", ", ".join(fu_kazu) or "-"))
