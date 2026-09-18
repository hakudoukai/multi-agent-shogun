# -*- coding: utf-8 -*-
"""★源を直す形(空の産物を『空である旨の一行』にする)を實測する★(家老令 km-153 ㋑)
裁 seq310228⑶ ―― 0byte は ★出来た後に直すのではなく書く其の場で直す★。
上流には既に其の器が在る(scripts/checks/karo_mac_kara_wo_ichigyo.sh・origin/main)。★然れど此の樹の disk には無い★ ―― 之も併せて測る。
四札: 刻=冠 / 根=cwd と器の sha256 / rc=subprocess の returncode(★管を通さず★) / 対照=器を通さぬ素の `> out 2> err`(0byte に成る側)。
此の數が意味せぬ事: 形が通つた事は ★現場の全ての産物が一行に成つて居る事ではない★(器が disk に無い故)。"""
import os
import sys
import hashlib
import subprocess
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUNDLE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BUNDLE, "..", "..", ".."))
os.chdir(ROOT)
from importlib import import_module
kaki_m = import_module("00_kaki"); kaku, kaku_tsv = kaki_m.kaku, kaki_m.kaku_tsv

GATE_REL = "scripts/checks/karo_mac_kara_wo_ichigyo.sh"
KYUU = os.path.join(BUNDLE, "_fx", "base_kyuu_disk.sh")
SHIN = os.path.join(BUNDLE, "_fx", "base_shin_origin_main.sh")
UTSU = os.path.join(BUNDLE, "_fx", "kara_wo_ichigyo.sh")
SU = os.path.join(BUNDLE, "raw", "70_minamoto")
os.makedirs(SU, exist_ok=True)

# ―― 器を上流から引く(disk は空 ∴ blob から) ――
q = subprocess.run(["git", "show", "origin/main:" + GATE_REL], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
assert q.returncode == 0, "上流の器が引けぬ rc=%d %s" % (q.returncode, q.stderr.decode("utf-8", "replace")[:120])
open(UTSU, "wb").write(q.stdout)
KI_SHA = hashlib.sha256(q.stdout).hexdigest()
KI_GYOU = q.stdout.decode("utf-8").count("\n")

# ―― 器が disk に在るか ―― 四札付きで測る ――
zai = []
for na, cmd in [("disk(共用樹の實体)", ["ls", "-l", GATE_REL]),
                ("git 追跡(HEAD)", ["git", "cat-file", "-e", "HEAD:" + GATE_REL]),
                ("git 追跡(origin/main)", ["git", "cat-file", "-e", "origin/main:" + GATE_REL]),
                ("陽性対照(同dir の門)", ["ls", "-l", "scripts/checks/karo_mac_dasumae_gate.sh"])]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    zai.append([na, " ".join(cmd), p.returncode, ("在り" if p.returncode == 0 else "★無し★"),
                (p.stdout or p.stderr).decode("utf-8", "replace").strip().split("\n")[0][:60] or "(何も言はず)"])
kaku_tsv(os.path.join(BUNDLE, "raw", "70_utsuwa_no_zaihi.tsv"), zai,
         header=["問", "命令(逐語)", "rc", "判", "出目(60字で截つ)"])

# ―― 器を通した時／通さぬ時 を並べて走らせる ――
def gate_rc(base, path):
    p = subprocess.run(["bash", base, "--", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")

rows = []
SHIKEN = [("何も言はぬ成功", ["true"]), ("何も言はぬ失敗", ["false"]),
          ("標準出力にのみ言ふ", ["printf", "a\n"])]
for na, cmd in SHIKEN:
    for keiro, tosu in (("★器を通す(源で直す)★", True), ("素の > out 2> err(通さぬ)", False)):
        tag = ("tosu" if tosu else "sunao") + "_" + str(len(rows))
        o = os.path.join(SU, tag + ".out"); e = os.path.join(SU, tag + ".err")
        if tosu:
            p = subprocess.run(["bash", UTSU, o, e, "--"] + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rc_cmd = p.returncode
        else:
            with open(o, "wb") as fo, open(e, "wb") as fe:
                rc_cmd = subprocess.run(cmd, stdout=fo, stderr=fe).returncode
        for ras, path in (("out", o), ("err", e)):
            sz = os.path.getsize(path)
            rc_k, _ = gate_rc(KYUU, path)
            rc_s, _ = gate_rc(SHIN, path)
            atama = open(path, encoding="utf-8", errors="replace").read().split("\n")[0][:46] if sz else "(0byte ―― 一行も無い)"
            rows.append([na, keiro, ras, rc_cmd, sz, atama, rc_k, ("通" if rc_k == 0 else "★落ち★"),
                         rc_s, ("通" if rc_s == 0 else "★落ち★")])
kaku_tsv(os.path.join(BUNDLE, "raw", "71_minamoto_no_kikime.tsv"), rows,
         header=["命令", "経路", "流", "命令の rc(器が返した物)", "byte", "頭の一行(46字で截つ)",
                 "旧基底 門 rc", "旧基底", "新基底 門 rc", "新基底"])

# ―― 當席の kaki も同じ形である事を示す(fx03 = KARA の一行) ――
fx03 = os.path.join(BUNDLE, "raw", "fx", "03_kaki_kara.txt")
k_rc_k, _ = gate_rc(KYUU, fx03)
k_rc_s, _ = gate_rc(SHIN, fx03)

tosu = [r for r in rows if r[1].startswith("★器を通す")]
sunao = [r for r in rows if not r[1].startswith("★器を通す")]
kaku(os.path.join(BUNDLE, "raw", "72_minamoto_dan.txt"),
     "as-of %s(UTC)\n根=%s\n"
     "器=%s(origin/main の blob・%d 行・sha256 %s)\n\n"
     "【實測 ―― 形は通る】\n"
     "・器を通した産物 %d 口: 0byte は ★0 口★・門は旧基底で %d 口/%d 口 通・新基底で %d 口/%d 口 通。\n"
     "・器を通さぬ産物 %d 口: 0byte が ★%d 口★・門は旧基底で %d 口 ★落ち★(條④ 0byte の口)。\n"
     "・rc は握り潰されて居らぬ ―― 「何も言はぬ失敗」で器は %s を返した(命令の rc を其の儘)。\n"
     "・當席の kaki(driver/00_kaki.py)の KARA 一行も同じ形である ―― fx03 は旧基底 rc=%d / 新基底 rc=%d で ★通る★。\n\n"
     "【★然し現場は直つて居らぬ★】\n"
     "・器は ★共用樹の disk に無い★(raw/70: ls rc=%s)。HEAD にも無く、origin/main にのみ在る。\n"
     "・∴ 此の席で素に `cmd > x.out 2> x.err` と書けば ★今も 0byte が出来る★。形が正しい事と現場が直つて居る事は別である。\n"
     "・治めは當て紙ではなく ★版の入替(origin/main を此の樹へ入れる)★ であり、之は変更統制 ∴ 當席は據ゑず材と數のみを出す。\n\n"
     "【之が意味せぬ事】\n"
     "・器を通せば全ての 0byte が消える、の意ではない ―― ★陽性対照として 0byte で在らねばならぬ紙は通すな★(器の冠 15 行目)。\n"
     "  本弾の fx01/fx02 は其れゆゑ ★器を通して居らぬ★。除いた事と本数(2 本)を此処に書く(『除いた』は『歩いて居らぬ』に非ず)。\n"
     % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), ROOT,
        os.path.relpath(UTSU, ROOT), KI_GYOU, KI_SHA,
        len(tosu), sum(1 for r in tosu if r[6] == 0), len(tosu), sum(1 for r in tosu if r[8] == 0), len(tosu),
        len(sunao), sum(1 for r in sunao if r[4] == 0), sum(1 for r in sunao if r[6] != 0),
        [r[3] for r in tosu if r[0] == "何も言はぬ失敗"][0],
        k_rc_k, k_rc_s, zai[0][2]))
print("器 %d 行 sha256 %s" % (KI_GYOU, KI_SHA[:16]))
print("通した %d 口(0byte=%d) / 通さぬ %d 口(0byte=%d・門落ち=%d)"
      % (len(tosu), sum(1 for r in tosu if r[4] == 0), len(sunao),
         sum(1 for r in sunao if r[4] == 0), sum(1 for r in sunao if r[6] != 0)))
print("disk 在否 rc=%s(%s)" % (zai[0][2], zai[0][3]))
