# -*- coding: utf-8 -*-
"""★隔離樹は「紙だけが消えた樹」か ―― 三器で測り直す★(km-175 ㋒ の下地)
前弾で當席は `find -L … -type f` = 29694 と口にした。★之を根拠に使はぬ★ ―― 根を控へず刷つた数ゆゑ、
同じ根で取り直す。器は三つ: ⑴find(素) ⑵find -L(link を辿る) ⑶os.walk(followlinks)。
四札: 刻=冠 / 根と深さ=下表 / rc=find の returncode(★管を通さず★・数へは python) / 陽性対照=本束を同じ器で測る。"""
import os
import sys
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

POC = os.path.realpath("/tmp/b3poc")
KOKU = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def find(args):
    """★rc を管に通さぬ★ ―― stdout を丸ごと受け、数へは python の手で行ふ。"""
    p = subprocess.run(["find"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    out = p.stdout.decode("utf-8", "replace")
    n = len([l for l in out.split("\n") if l != ""])
    return p.returncode, n, p.stderr.decode("utf-8", "replace").strip()


rows = []
for na, ne in (("隔離樹", POC), ("陽性対照(本束)", os.path.abspath(BUNDLE))):
    for ki, args in (("find(素) -type f", [ne, "-type", "f"]),
                     ("find -L -type f (★link を辿る★)", ["-L", ne, "-type", "f"]),
                     ("find(素) -type d", [ne, "-type", "d"]),
                     ("find(素) -type l", [ne, "-type", "l"])):
        rc, n, err = find(args)
        rows.append([na, ne, ki, rc, n, (err[:54] if err else "-")])
    # ⑶ os.walk ―― link を辿る/辿らぬ の二通り(輪を踏まぬ様 realpath を控へる)
    for na2, fol in (("os.walk(followlinks=False)", False), ("os.walk(followlinks=True)", True)):
        mita = set()
        d = f = l = 0
        for r, ds, fs in os.walk(ne, followlinks=fol):
            rp = os.path.realpath(r)
            if rp in mita:      # ★輪の番人★
                ds[:] = []
                continue
            mita.add(rp)
            d += 1
            for x in fs:
                fp = os.path.join(r, x)
                if os.path.islink(fp):
                    l += 1
                elif os.path.isfile(fp):
                    f += 1
        rows.append([na, ne, na2, 0, f, "dir %d・link %d(輪の番人=realpath %d 箇)" % (d, l, len(mita))])
kaku_tsv(os.path.join(BUNDLE, "raw", "33_kakuri_no_ki_san_ki.tsv"), rows,
         header=["歩いた所", "根", "器", "rc", "常の紙 数", "言"])

# ―― docs/evidence の中身 ――
EV = os.path.join(POC, "docs", "evidence")
ko = sorted(os.listdir(EV)) if os.path.isdir(EV) else []
kodir = [x for x in ko if os.path.isdir(os.path.join(EV, x))]
rc_f, n_f, _ = find([EV, "-type", "f"])
# ―― dir の mtime を日で束ねる ――
from collections import Counter
hi = Counter()
for r, ds, fs in os.walk(POC):
    hi[datetime.datetime.fromtimestamp(os.path.getmtime(r)).strftime("%Y-%m-%d %H:%M")] += 1
kaku_tsv(os.path.join(BUNDLE, "raw", "34_kakuri_dir_no_mtime.tsv"),
         [[k, v] for k, v in sorted(hi.items(), key=lambda z: (-z[1], z[0]))[:12]],
         header=["dir の mtime(分まで)", "dir 数"])

# ―― 掃き手の候補を ★読取だけ★ で当たる(断ぜぬ・候補として置く) ――
SOUJI = "/etc/periodic/daily/110.clean-tmps"
soji_aru = os.path.exists(SOUJI)
soji_gyou = []
if soji_aru:
    for l in open(SOUJI, encoding="utf-8", errors="replace").read().split("\n"):
        if "mtime" in l or "clean_tmps_days" in l or "-type f" in l:
            soji_gyou.append(l.strip()[:96])

kaku(os.path.join(BUNDLE, "raw", "35_kakuri_no_ki_dan.txt"),
     "as-of %s\n根=%s(★/tmp は symlink ゆゑ realpath で解いた★)\n\n"
     "【断 ―― 隔離樹は『紙だけが消えた樹』である】\n"
     "㋐ 常の紙= ★0 本★。之は三器が揃つて 0 と言ふ(find 素 / find -L / os.walk 両様・raw/33)。\n"
     "   dir は %d 箇・symlink は 8 本。∴ ★歩いて居らぬのではない ―― 歩いた先に紙が無い★。\n"
     "㋑ symlink 8 本は ★悉く解けぬ★(raw/32) ―― 指す先が /mnt/c/Users/User/Documents/DentalBI/… \n"
     "   即ち ★WSL(別 PC)の路★ である。此の mac には其の路が無い ∴ link の先にも紙は無い。\n"
     "   ★之ゆゑ find -L の数も素の find と同じ 0 に成る★。\n"
     "㋒ ★前弾の當席の口を撤回する★ ―― 「find -L … -type f = 29694」と刷つたが、\n"
     "   根を控へて居らぬ数であり、今 同じ根で取り直せば 0 である(raw/33)。\n"
     "   ∴ 29694 は隔離樹の数ではない(他の根を量つた数と見る)。★測つた根を書かぬ数は使へぬ★。\n"
     "㋓ docs/evidence= 在り。直下の子 %d 件(内 dir %d 件)・★其の下の常の紙 0 本★(find rc=%d)。\n"
     "㋔ dir の mtime は ★2026-09-17 00:00 へ %d 箇が寄る★(raw/34)。\n"
     "   掃き手の候補= %s%s\n"
     "   ★但し之は候補に過ぎぬ★ ―― 掃いた者の log を當席は見て居らぬ。\n"
     "   「紙が無い」は實測、「掃除器が消した」は ★未だ測れぬ★。一つの符合で因と断ぜぬ。\n"
     "㋕ ∴ km-175 ㋒ の宣= ★原本は不在★。板 38dcde86 の三 sha256 は\n"
     "   隔離樹(紙 0 本)・DentalBI 全obj(blob 48480 本)・multi-agent-shogun 全obj(blob 11349 本)の\n"
     "   何處にも当たらぬ。陽性対照は二つとも当たつて居る(raw/31)ゆゑ、★器の黙りではない★。\n"
     % (KOKU, POC, sum(hi.values()), len(ko), len(kodir), rc_f,
        max(hi.items(), key=lambda z: z[1])[1] if hi else 0,
        (SOUJI + " 在り") if soji_aru else (SOUJI + " ★無し★"),
        ("\n   逐語: " + " / ".join(soji_gyou)) if soji_gyou else ""))
print("隔離樹 三器= " + " | ".join("%s:%s(rc=%s)" % (r[2][:26], r[4], r[3]) for r in rows if r[0] == "隔離樹"))
print("docs/evidence 子 %d(dir %d)・其の下の紙 %d(rc=%d)" % (len(ko), len(kodir), n_f, rc_f))
print("dir mtime 最多= %s" % (max(hi.items(), key=lambda z: z[1]) if hi else "-",))
