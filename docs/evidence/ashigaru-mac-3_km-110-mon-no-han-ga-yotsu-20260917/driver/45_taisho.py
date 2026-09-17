# -*- coding: utf-8 -*-
"""★對照★ ―― 數が「零」や「通」に成つた時、器が生きて居る事を先に示す。

㊀ 有無の檢出子(㋐で 244 本に当てた物)が ★三つの出目を悉く出せる★ 事:
   ⑴門を載せる commit → 有 ⑵origin/main の頭 → 無 ⑶手元に無い 40hex → 測れぬ
   (「測れぬ=0 本」は、測れぬを表せる器が零を出した時のみ意味を持つ)
㊁ 「取れなんだ=0 本」の檢出子(集合差)が ★非零を出せる★ 事: 贋の枝名を名簿へ一本混ぜる。
㊂ 條① の陽性對照: 臺帳を建てた★後★に一字足した束(shiken_kizu)へ四版を当て、★必ず鳴る★事。
   鳴らねば ㋒ の rc=0 は「通つた」ではなく「檢出子が死んで居る(fail-open)」である。
㊃ 丙 ―― ★立つ場所を変へる★: cwd=repo 根 から同じ四版を当て、cwd 依存の版を炙る。

usage: python3 driver/45_taisho.py <bundle_root> <repo_root>
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
K = import_module("00_kaki")

GATE_NAME = "karo_mac_dasumae_gate.sh"
DISK_VER = "ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579"
ORDER = ["9cd550fc2cf963ca0475b3448bb33483b9aede6b",
         "54e133c85832d48aa731d0ab0d105d399b9b8fbd",
         "b0bf5b05ededce4b06286dbab05cf0b616414ef2",
         "054c442eaee3886b2283f98f7c3a1ab8cb813b68"]
GATE_PATH = "scripts/checks/karo_mac_dasumae_gate.sh"
NAI_SHA = "0123456789abcdef0123456789abcdef01234567"   # 40hex・手元に無い(器が「測れぬ」を出せるか)


def git(repo, *a):
    p = subprocess.run(["git", "-C", repo] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "surrogateescape").strip(), p.stderr.decode("utf-8", "surrogateescape").strip()


def umu(repo, sha):
    """㋐ で使つたのと ★同じ問ひ方★(git rev-parse --verify --quiet <sha>:<path>)。"""
    rc, out, err = git(repo, "rev-parse", "--verify", "--quiet", "%s:%s" % (sha, GATE_PATH))
    rc2, _, _ = git(repo, "cat-file", "-e", "%s^{commit}" % sha)
    if rc2 != 0:
        return "測れぬ", "(commit が手元に無い)", err
    return ("有" if rc == 0 else "無"), (out or "-"), err


def run_gate(repo, bundle, blob, base, cwd, man, files, tag):
    d = os.path.join(repo, ".km110_scratch", "甲_%s_%s" % (blob[:16], DISK_VER[:8]))
    env = dict(os.environ)
    env.pop("KM_GATE_MANIFEST_BASE", None)
    umu_s = "無"
    if base is not None:
        env["KM_GATE_MANIFEST_BASE"] = base
        umu_s = "有"
    nm = "mon_%s_%s_%s_%s.log" % (blob[:16], umu_s, time.strftime("%H%M%S"), tag)
    log = os.path.join(bundle, "_gate", nm)
    cmd = ["bash", os.path.join(d, GATE_NAME), man] + files
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    body = p.stdout.decode("utf-8", "surrogateescape")
    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join([
            "# 對照走(%s) 版=%s verify=%s(固定) 基点=%s" % (tag, blob, DISK_VER, base if base is not None else "(渡さぬ)"),
            "# cwd=%s" % cwd,
            "# 打つた語: %sbash %s %s %s" % (("KM_GATE_MANIFEST_BASE=%s " % base) if base is not None else "", cmd[1], man, " ".join(files)),
            "# 刻: %s / rc=%d" % (time.strftime("%F %T %z"), p.returncode),
            "# ―― 以下 門の出目(一字も直して居らぬ)",
        ]) + "\n" + (body if body else "(出目 無)\n"))
    time.sleep(1)
    return p.returncode, body, os.path.basename(log)


def hiku(body, key):
    for ln in body.split("\n"):
        if key in ln:
            return ln.strip()
    return "-"


def main(argv):
    bundle, repo = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    raw = os.path.join(bundle, "raw")
    out = []

    # ㊀ 有無の檢出子
    rc, gate_eda, _ = git(repo, "rev-parse", "refs/km110/karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917")
    rc2, main_sha, _ = git(repo, "rev-parse", "refs/km110/main")
    t = []
    for na, sha in (("門を載せる枝の頭(km-79)", gate_eda), ("main の頭", main_sha), ("手元に無い 40hex", NAI_SHA)):
        u, blob, err = umu(repo, sha)
        t.append([na, sha[:16], u, blob[:16] if blob != "-" else "-"])
        out.append("㊀ %s → %s (blob %s)" % (na, u, blob[:16]))
    K.kaku_tsv(os.path.join(raw, "46_taisho_umu.tsv"), t, header=["対象", "sha(16)", "出目", "門blob(16)"])
    assert [r[2] for r in t] == ["有", "無", "測れぬ"], "★檢出子が三つの出目を出せぬ ―― 零を語る資格が無い★"
    out.append("  ∴ 檢出子は 有/無/測れぬ の★三つを悉く出せる★ ―― ㋐の「測れぬ=0 本」は器の沈黙ではない。")

    # ㊁ 集合差の檢出子
    rem = set()
    with open(os.path.join(raw, "10_ls_remote_heads.txt"), encoding="utf-8", errors="surrogateescape") as fh:
        for ln in fh:
            if ln.strip():
                rem.add(ln.rstrip("\n").split("\t", 1)[1][len("refs/heads/"):])
    loc = set()
    with open(os.path.join(raw, "12_km110_refs.txt"), encoding="utf-8", errors="surrogateescape") as fh:
        for ln in fh:
            if ln.strip():
                loc.add(ln.rstrip("\n").split(" ", 1)[1][len("refs/km110/"):])
    nise = rem | {"★贋の枝名(対照・遠隔にも手元にも無い)★"}
    out.append("㊁ 集合差 ―― 素の名簿: 取れぬ=%d 本 / 贋を一本混ぜた名簿: 取れぬ=%d 本"
               % (len(rem - loc), len(nise - loc)))
    assert len(nise - loc) == len(rem - loc) + 1, "★集合差の器が非零を出せぬ★"
    out.append("  ∴ 零は器の沈黙ではない(贋を混ぜれば 0→1 へ動く)。")

    # ㊂ 條① の陽性對照(臺帳を建てた後に一字足した束)
    rows = []
    for blob in ORDER:
        rc, body, log = run_gate(repo, bundle, blob, ".", os.path.join(bundle, "shiken_kizu"),
                                 "MANIFEST.txt", ["a.txt", "b/c.txt"], "kizu")
        rows.append([blob[:16], "有", str(rc), hiku(body, "相違"), hiku(body, "條①"), log])
    K.kaku_tsv(os.path.join(raw, "47_taisho_jou1.tsv"), rows,
               header=["門版(16)", "基点", "rc", "相違の行", "條①の行", "控"])
    out.append("㊂ 條① 陽性對照(shiken_kizu ―― 臺帳の後に一字足した束・基点=. 有):")
    for r in rows:
        out.append("   版%s rc=%s %s" % (r[0], r[2], r[3]))

    # ㊃ 丙 ―― cwd を repo 根へ移す
    rel = os.path.relpath(os.path.join(bundle, "shiken"), repo)
    hei = []
    for blob in ORDER:
        for base in (os.path.join(bundle, "shiken"), None):
            rc, body, log = run_gate(repo, bundle, blob, base, repo,
                                     os.path.join(rel, "MANIFEST.txt"),
                                     [os.path.join(rel, "a.txt"), os.path.join(rel, "b", "c.txt")], "hei")
            hei.append([blob[:16], "有(絶対path)" if base else "無", str(rc),
                        hiku(body, "基点"), hiku(body, "條① 台帳とdiskの差"), log])
    K.kaku_tsv(os.path.join(raw, "48_hei_cwd_repo.tsv"), hei,
               header=["門版(16)", "基点", "rc", "基点の行", "條①の判定行", "控"])
    out.append("㊃ 丙(cwd=repo 根・臺帳は束内相対の儘):")
    for r in hei:
        out.append("   版%s 基点%s → rc=%s" % (r[0], r[1], r[2]))

    K.kaku(os.path.join(raw, "49_taisho_matome.txt"), "\n".join(out))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
