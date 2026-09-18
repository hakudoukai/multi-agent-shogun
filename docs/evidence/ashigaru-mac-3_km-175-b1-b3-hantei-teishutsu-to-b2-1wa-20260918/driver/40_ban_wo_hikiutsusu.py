# -*- coding: utf-8 -*-
"""★板 38dcde86 の逐語を控へる★(再生の材・km-175 ㋒③)
`~/bin/sb read board-one 38dcde86` の出目を丸ごと控へ、current_step を抜いて別紙にする。
★抜き出しは器で行ふ★(目で写さぬ)。四札: 刻=冠 / rc=下記(管を通さず) / 陽性対照=下記 / 根=板の id。"""
import os
import re
import sys
import subprocess
import hashlib
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

SB = os.path.expanduser("~/bin/sb")
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def yomu(args):
    p = subprocess.run([SB, "read"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace").strip()


rc, out, err = yomu(["board-one", "38dcde86"])
kaku(os.path.join(BUNDLE, "raw", "40_ban_38dcde86.txt"), out if out.strip() else "KARA")
# ★陰性対照★ 在らぬ板の頭を同じ器へ通す
rc_n, out_n, err_n = yomu(["board-one", "98765432"])
kaku(os.path.join(BUNDLE, "raw", "41_ban_inseitaishou.txt"),
     "rc=%d\n--- stdout ---\n%s\n--- stderr ---\n%s\n" % (rc_n, out_n if out_n.strip() else "KARA", err_n or "KARA"))

# ―― current_step を抜く(鍵の行から次の鍵の行まで) ――
gyou = out.split("\n")
# ★鍵の名を焼き込まぬ★ ―― 「二字下げ + 小文字鍵 + コロン空白」の形で切る(焼き込めば知らぬ鍵で溢れる)
KAGI_RE = re.compile(r"^ {2}[a-z_]+: ?")
hajime = [i for i, l in enumerate(gyou) if l.strip().startswith("current_step:")]
assert len(hajime) == 1, "current_step の起しが %d 件 ―― 逐語で当て直せ" % len(hajime)
i = hajime[0]
owari = len(gyou)
for j in range(i + 1, len(gyou)):
    if KAGI_RE.match(gyou[j]):
        owari = j
        break
hon = "\n".join([gyou[i].split("current_step:", 1)[1].lstrip()] + gyou[i + 1:owari]).strip()
kaku(os.path.join(BUNDLE, "raw", "42_ban_current_step_chikugo.txt"), hon if hon else "KARA")

sha = hashlib.sha256(hon.encode("utf-8")).hexdigest()
kaku_tsv(os.path.join(BUNDLE, "raw", "43_ban_no_hakari.tsv"),
         [["board-one 38dcde86", rc, len(out), len(out.split("\n")), (err or "-")],
          ["current_step 逐語", "-", len(hon), len(hon.split("\n")), "sha256 " + sha],
          ["★陰性対照★ board-one 98765432", rc_n, len(out_n), len(out_n.split("\n")),
           ("★何も出ぬ(正)★" if not out_n.strip() else "★出た ―― 対照が効いて居らぬ★")]],
         header=["何を", "rc", "字数", "行数", "言"])
print("板 rc=%d 出目 %d字 %d行 / current_step %d字 %d行 sha256=%s"
      % (rc, len(out), len(out.split("\n")), len(hon), len(hon.split("\n")), sha[:16]))
print("陰性対照 rc=%d 出目 %d字(空=%s)" % (rc_n, len(out_n), not out_n.strip()))
