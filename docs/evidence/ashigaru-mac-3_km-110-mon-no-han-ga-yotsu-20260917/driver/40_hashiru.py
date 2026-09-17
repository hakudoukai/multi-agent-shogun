# -*- coding: utf-8 -*-
"""㋒ 走らせて確かめる ―― 四版 × 基点(有/無) の八つの出目。加へて ★對照★ として
同枝同梱の verify.py を据ゑた八つ(乙)も取る。

★一つの変数だけを動かす★: 甲 = verify.py を disk 版(ebfc4c0…)で ★固定★ し、動かすのは
門の版と KM_GATE_MANIFEST_BASE の有無のみ。乙 = verify.py を ★其の枝が同梱する版★ へ替へ、
「差の因が門か照合器か」を分ける(因を一つの違ひから決めつけぬ為)。

置き場: <repo>/.km110_scratch/<門16>_<verify8>/ ―― ★repo 根から二階下★(scripts/checks と同じ深さ)。
    照合器の既定基点は os.path.dirname^3(己の abspath) ゆゑ、深さを違へると既定基点が変はる。
    ∴ 深さを合はせねば「既定で落ちる」の出目が器の置き場の産物に成る。

走らす場: <bundle>/shiken(験束の中) ―― 臺帳は束内相対(裁 seq322699)。

usage: python3 driver/40_hashiru.py <bundle_root> <repo_root>
"""
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

GATE_NAME = "karo_mac_dasumae_gate.sh"
VER_NAME = "karo_mac_manifest_verify.py"
DISK_VER = "ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579"   # disk の verify.py(甲で固定する版)
SIB = {  # 門blob -> 其の枝が同梱する verify.py blob(21_zenpon.tsv の実測より)
    "9cd550fc2cf963ca0475b3448bb33483b9aede6b": "b19ec9ea259653d9e65d052459128c635a44e93f",
    "54e133c85832d48aa731d0ab0d105d399b9b8fbd": "b19ec9ea259653d9e65d052459128c635a44e93f",
    "b0bf5b05ededce4b06286dbab05cf0b616414ef2": "ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579",
    "054c442eaee3886b2283f98f7c3a1ab8cb813b68": "b19ec9ea259653d9e65d052459128c635a44e93f",
}
ORDER = ["9cd550fc2cf963ca0475b3448bb33483b9aede6b",
         "54e133c85832d48aa731d0ab0d105d399b9b8fbd",
         "b0bf5b05ededce4b06286dbab05cf0b616414ef2",
         "054c442eaee3886b2283f98f7c3a1ab8cb813b68"]


def cat_blob(repo, blob, dest):
    with open(dest, "wb") as fh:
        p = subprocess.run(["git", "-C", repo, "cat-file", "blob", blob], stdout=fh)
    assert p.returncode == 0, blob
    return os.path.getsize(dest)


def jou1_lines(text):
    """出目から 條① に係る行のみ抜く(門の出目は悉く stderr ゆゑ out+err を一本にして渡す)。"""
    keep = []
    for ln in text.split("\n"):
        if ("條①" in ln or "基点" in ln or "一致" in ln or "相違" in ln
                or "実体無" in ln or "讀めぬ" in ln or "読めぬ" in ln or "旧形" in ln
                or "manifest_verify" in ln):
            keep.append(ln.rstrip())
    return keep


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    gate_dir = os.path.join(bundle, "_gate")
    raw = os.path.join(bundle, "raw")
    shiken = os.path.join(bundle, "shiken")
    scratch = os.path.join(repo, ".km110_scratch")
    os.makedirs(gate_dir, exist_ok=True)
    os.makedirs(scratch, exist_ok=True)

    rows = []
    kizami = []
    for kou_otsu in ("甲", "乙"):
        for blob in ORDER:
            ver = DISK_VER if kou_otsu == "甲" else SIB[blob]
            d = os.path.join(scratch, "%s_%s_%s" % (kou_otsu, blob[:16], ver[:8]))
            os.makedirs(d, exist_ok=True)
            gb = cat_blob(repo, blob, os.path.join(d, GATE_NAME))
            vb = cat_blob(repo, ver, os.path.join(d, VER_NAME))
            for umu in ("有", "無"):
                env = dict(os.environ)
                env.pop("KM_GATE_MANIFEST_BASE", None)
                if umu == "有":
                    env["KM_GATE_MANIFEST_BASE"] = "."
                hhmmss = time.strftime("%H%M%S")
                nm = "mon_%s_%s_%s.log" % (blob[:16], umu, hhmmss)
                if kou_otsu == "乙":
                    nm = "mon_%s_%s_%s_v%s.log" % (blob[:16], umu, hhmmss, ver[:16])
                log = os.path.join(gate_dir, nm)
                cmd = ["bash", os.path.join(d, GATE_NAME), "MANIFEST.txt", "a.txt", "b/c.txt"]
                p = subprocess.run(cmd, cwd=shiken, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                body = p.stdout.decode("utf-8", "surrogateescape")
                rc = p.returncode
                head = [
                    "# 走: %s 版=%s(門 %d byte) verify=%s(%d byte) 基点=%s cwd=%s"
                    % (kou_otsu, blob, gb, ver, vb, umu, "<bundle>/shiken"),
                    "# 打つた語: (cwd=<bundle>/shiken) %sbash %s MANIFEST.txt a.txt b/c.txt"
                    % ("KM_GATE_MANIFEST_BASE=. " if umu == "有" else "", os.path.join(".km110_scratch", os.path.basename(d), GATE_NAME)),
                    "# 刻: %s / rc=%d" % (time.strftime("%F %T %z"), rc),
                    "# ―― 以下 門の出目(stdout+stderr を一本にした儘・一字も直して居らぬ)",
                ]
                with open(log, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("\n".join(head) + "\n" + (body if body else "(出目 無)\n"))
                j = jou1_lines(body)
                rows.append([kou_otsu, blob[:16], umu, ver[:16], str(rc),
                             (j[0] if j else "(條①の行 無)"),
                             " ¶ ".join(j[1:]) if len(j) > 1 else "-",
                             os.path.basename(log)])
                kizami.append((kou_otsu, blob, umu, ver, rc, j, os.path.basename(log)))
                time.sleep(1)   # ★控の名を走る毎に別にする為(HHMMSS 一秒刻み)★

    K.kaku_tsv(os.path.join(raw, "41_yatsu_no_deme.tsv"), rows,
               header=["甲乙", "門版(16)", "基点", "verify版(16)", "rc", "條①の一行目", "條①の残り(¶区切)", "控"])

    out = ["㋒ 八つの出目(甲 = verify.py を disk 版 %s で固定)" % DISK_VER[:16], ""]
    for r in rows:
        if r[0] != "甲":
            continue
        out.append("門%s 基点%s → rc=%s  %s" % (r[1], r[2], r[4], r[5]))
    out.append("")
    out.append("★對照(乙 = 其の枝が同梱する verify.py を据ゑた時)★")
    for r in rows:
        if r[0] != "乙":
            continue
        out.append("門%s 基点%s verify=%s → rc=%s  %s" % (r[1], r[2], r[3], r[4], r[5]))
    K.kaku(os.path.join(raw, "42_deme_matome.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
