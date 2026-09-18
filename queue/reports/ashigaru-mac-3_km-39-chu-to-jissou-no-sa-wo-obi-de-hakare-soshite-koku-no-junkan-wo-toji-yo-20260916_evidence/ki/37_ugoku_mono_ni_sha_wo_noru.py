#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第39弾 問三 丁 ―― ★動く物に sha を宣ると、名だけが残る★ を己の疵で測る。

第38弾の便(msg_…171945)は 報 yaml を ★4f768691d59ea64f★ と宣つた。
家老は其の後 ★88502ed2e2018aac(18432B・mtime 17:21:24)★ と測つた。
今、同じ物を三つの鍵で引く ―― ★名 / 宣つた sha / 家老の測つた sha★。

陽性対照 = 今の sha(此の器が己で測つた値)で引けば ★1 本★ 当たる筈
陰性対照 = f×64 は ★0 本★
"""
import hashlib
import os
import sys

ROOT = "queue/reports"
NAME = ("ashigaru-mac-3_km-38-kanou-to-itta-fudou-wo-ono-no-tama-de-enjiro-"
        "soshite-kami-ni-kaita-hou-wa-te-wo-kaenu-20260913_report.yaml")
DECLARED_IN_LETTER = "4f768691d59ea64f"      # 席が便で宣つた(疵十三)
MEASURED_BY_KARO = "88502ed2e2018aac"        # 家老が後に測つた
NEG = "f" * 64


def sha_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    names = sorted(f for f in os.listdir(ROOT)
                   if os.path.isfile(os.path.join(ROOT, f)))
    print("【歩き根】 %s ―― ★maxdepth 1 のみ★(下の束は歩かぬ ―― 13.8 GB 故)" % ROOT)
    print("  母數 = ★%d 本★" % len(names))
    table, unread = {}, 0
    for f in names:
        try:
            table[f] = sha_of(os.path.join(ROOT, f))
        except OSError:
            unread += 1
    print("  讀めた %d / ★讀めぬ %d★" % (len(table), unread))
    print()

    print("【鍵 一 ―― ★名★ で引く】")
    hit_name = NAME in table
    print("  %s" % NAME)
    print("  当たり = ★%s★" % ("1 本" if hit_name else "0 本"))
    if not hit_name:
        print("  ★陽性対照の的が名で引けぬ ―― 數を讀むな★"); return 3
    now = table[NAME]
    size = os.path.getsize(os.path.join(ROOT, NAME))
    print("  今の sha = ★%s★ / %d byte" % (now[:16], size))
    print()

    print("【対照】")
    neg = [f for f, s in table.items() if s == NEG]
    pos = [f for f, s in table.items() if s == now]
    print("  陰性(f×64) = ★%d 本★ / 陽性(今の sha %s…) = ★%d 本★" % (len(neg), now[:16], len(pos)))
    if neg or len(pos) < 1:
        print("  ★対照が通らぬ ―― 數を讀むな★"); return 3
    print("  ★対照 二本 通つた ―― 此の根では sha で歩けば当たる★")
    print()

    print("【鍵 二 ―― ★便が宣つた sha★ で引く】")
    h1 = [f for f, s in table.items() if s.startswith(DECLARED_IN_LETTER)]
    print("  %s… 当たり = ★%d 本★" % (DECLARED_IN_LETTER, len(h1)))
    print("【鍵 三 ―― ★家老が測つた sha★ で引く】")
    h2 = [f for f, s in table.items() if s.startswith(MEASURED_BY_KARO)]
    print("  %s… 当たり = ★%d 本★" % (MEASURED_BY_KARO, len(h2)))
    print()

    print("【裁】")
    print("  名        → ★当たる★")
    print("  便の sha  → %s" % ("★当たる★" if h1 else "★当たらぬ★"))
    print("  家老の sha→ %s" % ("★当たる★" if h2 else "★当たらぬ★"))
    if not h1 and h2:
        print("  ∴ ★物は一度動き、其の後は動いて居らぬ。★")
        print("    宣つた刹那の sha は死に、★名は三度の刻を跨いで生きた★。")
    elif not h1 and not h2:
        print("  ∴ ★物は二度以上動いた。★ 二つの sha 悉く死に、★名のみ生きた★。")
    else:
        print("  ∴ ★便の sha が今も当たる ―― 疵十三 は『宣が偽』ではなく別の形であつた★")
    print("  ★∴ sha は『何時の物か』を持たぬ。名は持つ。★")
    print("    ★故に既定は『札が宣つた path』であり、sha は ★其の path の中身を検める鍵★ である。★")
    print("    ★sha を既定に据ゑてよいのは ―― 物が凍つて居る時に限る。★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
