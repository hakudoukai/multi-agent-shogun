#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""80_yaki.py ―― 門の出目を紙の一行目へ焼き、★數が動かなく成る迄★ 巡る。

巡り: 焼く → 臺帳を建て直す(70_daichou) → 門を当てる → 出た數を次の焼きへ。
      焼けば紙の byte が変る ∴ 門の byte和 も変る。★一巡では閉ぢぬ。★
      焼き行の字數が前巡と同じに成れば byte和 も動かぬ ―― 其處で止める。

門の控は _gate/ へ置く(★臺帳の外★)。名は走る毎に別(裁の下命)。
usage: 80_yaki.py <束の絶対path> <repo根> [上限巡數]
"""
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import importlib
K = importlib.import_module("00_kaki")

GATE_VER16 = "054c442eaee3886b"          # disk の門(㋓で正と選んだ版)


def kamiki(bundle):
    """臺帳へ載せる紙(= 門へ当てる紙)を数へる。_gate と臺帳自身は除く。"""
    out = []
    for root, dirs, files in os.walk(bundle):
        dirs[:] = sorted(d for d in dirs if d not in ("_gate", "__pycache__"))
        for f in sorted(files):
            p = os.path.relpath(os.path.join(root, f), bundle)
            if p == "MANIFEST.txt":
                continue
            out.append("./" + p)
    return out


def mon(bundle, repo, files):
    t = time.strftime("%H%M%S")
    log = os.path.join("_gate", "mon_%s_有_%s_taba.log" % (GATE_VER16, t))
    env = dict(os.environ, KM_GATE_MANIFEST_BASE=".")
    with open(os.path.join(bundle, log), "w", encoding="utf-8") as fh:
        rc = subprocess.call(
            ["bash", os.path.join(repo, "scripts", "checks", "karo_mac_dasumae_gate.sh"),
             "MANIFEST.txt"] + files,
            cwd=bundle, env=env, stdout=fh, stderr=subprocess.STDOUT)
    body = open(os.path.join(bundle, log), encoding="utf-8").read()
    g = lambda p, d="?": (re.search(p, body).group(1) if re.search(p, body) else d)
    return {
        "rc": rc, "log": log, "toki": time.strftime("%Y-%m-%dT%H:%M:%S+0900"),
        "kami": len(files),
        "icchi": g(r"一致 ★(\d+)★"), "soui": g(r"相違 (\d+)"),
        "jittai": g(r"実体無 (\d+)"), "yomenu": g(r"読めぬ行 (\d+)"),
        "byte": g(r"byte和 (\d+)"),
    }


def yakigyou(d):
    return ("★門 rc=%d★(%s) ―― 當てた紙 %d 本 / 條① 一致 %s・相違 %s・実体無 %s・読めぬ行 %s / "
            "條②③④ %d 本通 / 條⑤ byte和 %s / 控 %s ―― ★控は臺帳の外★"
            % (d["rc"], d["toki"], d["kami"], d["icchi"], d["soui"], d["jittai"],
               d["yomenu"], d["kami"], d["byte"], d["log"]))


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    kagiri = int(argv[3]) if argv[3:] else 5
    kami = os.path.join(bundle, "00_shodan.md")
    mae = None
    for junkai in range(1, kagiri + 1):
        files = kamiki(bundle)
        d = mon(bundle, repo, files)
        gyou = yakigyou(d)
        print("巡%d: rc=%d byte和=%s 焼行字數=%d %s"
              % (junkai, d["rc"], d["byte"], len(gyou),
                 "★前巡と同じ ―― 數が止まつた★" if gyou[:40] == (mae or "")[:40]
                 and d["byte"] == (mae_byte if mae else None) else ""))
        if mae is not None and d["byte"] == mae_byte and d["rc"] == mae_rc:
            print("★止まつた★ 最終: %s" % gyou)
            return 0 if d["rc"] == 0 else 1
        # 焼く → 臺帳を建て直す(焼けば sha が変る故・順を違へれば條①が落ちる)
        honbun = open(kami, encoding="utf-8").read().split("\n")
        if honbun and honbun[0].startswith("★門 rc="):
            honbun = honbun[1:]
        K.kaku(kami, "\n".join([gyou] + honbun))
        rc70 = subprocess.call([sys.executable, "-B",
                                os.path.join(bundle, "driver", "70_daichou.py"), bundle, repo],
                               stdout=open(os.path.join(bundle, "_gate", "70_daichou_j%d.out" % junkai), "w"),
                               stderr=subprocess.STDOUT)
        if rc70 != 0:
            print("★臺帳の建て直しが落ちた rc=%d ―― 止める★" % rc70)
            return 2
        mae, mae_byte, mae_rc = gyou, d["byte"], d["rc"]
    print("★上限まで巡つて數が止まらなんだ★")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
