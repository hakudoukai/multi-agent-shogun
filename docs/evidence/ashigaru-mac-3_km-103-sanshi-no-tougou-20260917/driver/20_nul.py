# -*- coding: utf-8 -*-
"""㋒ ⑴ を★三器★で測り直し、三紙の宣した数と突き合はせる。

⑴ の定義(三紙共通・札 km-102 ㋑⑴ の逐語): `git diff --name-only 4be3ee19e1c5...<sha>` の行数。
★此の数が意味せぬ事★: 「此の枝が変へた file 数」ではない。★origin/main が何 file 遅れて居るか★である。

★三器★(同じ一回の git 出力を三通りに数へる ―― 別々に git を呼べば刻の差が紛れ込む):
  甲 NUL   : `--name-only -z` の出目を b"\\0" で割り、末尾の空を落とした数 = ★実測★
  乙 grep  : `--name-only`(-z 無し)の出目の★行数★(改行で割り末尾の空を落とす)
  丙 split : 同じ出目に Python `str.splitlines()` を当てた数
★丙が甲より多い枝は U+2028 等を行末と見做した疵が在る★(a1 第二走で現に起きた)。
乙と甲が違ふ枝は git の★引用★(非ASCII名を "..." で括る)ではなく行数の数へ方の差を示す。

対照(倒れたら止まる):
  ⓐ 仕込んだ偽 sha `0000…0` は git が撥ね rc≠0 ―― 撥ねねば止(sha を見て居らぬ)
  ⓑ U+2028 を含む名を一本でも持つ枝が在れば 丙>甲 が★必ず★立つ ―― 立たねば止(丙が splitlines で無い)
  ⓒ 45 本悉く測れねば止(欠測を 0 と混ぜぬ)
"""
import os, sys, subprocess, importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("K", os.path.join(_d, "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)
REPO = os.path.abspath(os.path.join(_d, "..", "..", "..", ".."))
MAIN = "4be3ee19e1c5"

def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 20_nul.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")

    # ── 対照ⓐ: 偽 sha は撥ねられるか ──────────────────────
    rc, _, _ = git(["diff", "--name-only", "%s...%s" % (MAIN, "0" * 40)])
    if rc == 0:
        sys.stderr.write("★偽 sha が通つた ∴ sha を見て居らぬ ∴ 止まる★\n"); return 5

    wari = []
    with open(os.path.join(raw, "11_bogen_warimochi.tsv"), encoding="utf-8") as f:
        for i, ln in enumerate(f.read().split("\n")):
            if i == 0 or not ln.strip():
                continue
            seat, br, sha = ln.split("\t")[:3]
            wari.append((seat, br, sha))
    if len(wari) != 45:
        sys.stderr.write("★割当が 45 でない(%d) ∴ 止まる★\n" % len(wari)); return 5

    rows, u2028 = [], 0
    for seat, br, sha in wari:
        rcz, outz, errz = git(["diff", "--name-only", "-z", "%s...%s" % (MAIN, sha)])
        rcn, outn, errn = git(["diff", "--name-only", "%s...%s" % (MAIN, sha)])
        if rcz != 0 or rcn != 0:
            sys.stderr.write("★%s が測れぬ(rc %d/%d) ∴ 止まる★\n" % (br, rcz, rcn)); return 5
        parts = outz.split(b"\0")
        if parts and parts[-1] == b"":
            parts = parts[:-1]
        n_nul = len(parts)
        s = outn.decode("utf-8", "surrogateescape")
        lines = s.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        n_grep = len(lines)
        n_split = len(s.splitlines())
        if n_split > n_nul:
            u2028 += 1
        areas = sorted(set((p.decode("utf-8", "surrogateescape").split("/")[0]
                            if b"/" in p else "(根)" + p.decode("utf-8", "surrogateescape"))
                           for p in parts))
        rows.append([seat, br, sha[:12], n_nul, n_grep, n_split,
                     n_split - n_nul, "有" if n_split != n_nul else "無", " ".join(areas)])

    if len(rows) != 45:
        sys.stderr.write("★測れたのが 45 でない(%d) ∴ 止まる★\n" % len(rows)); return 5

    # ── 対照ⓑ: splitlines が本当に U+2028 を割るか(器そのものを試す) ──
    probe = "a b.txt\nc.txt\n"
    if len(probe.splitlines()) <= len([x for x in probe.split("\n") if x]):
        sys.stderr.write("★splitlines が U+2028 を割らぬ ∴ 丙が丙でない ∴ 止まる★\n"); return 5

    K.kaku_tsv(os.path.join(raw, "21_nul_jissoku.tsv"), rows,
               ["席", "枝名", "sha12", "甲NUL実測", "乙grep行", "丙splitlines",
                "丙−甲", "U2028疵", "領域(対main)"])
    K.kaku(os.path.join(raw, "22_nul_matome.txt"), "\n".join([
        "母數(割当) = %d 本 ―― 悉く測れた(欠測 0)" % len(rows),
        "★丙(splitlines) が 甲(NUL実測) より多い枝 = %d 本★" % u2028,
        "甲と乙(grep 行数)が違ふ枝 = %d 本" % sum(1 for r in rows if r[3] != r[4]),
        "対照ⓐ 偽 sha は撥ねられた(rc≠0)／対照ⓑ splitlines は U+2028 を割る(器で確かめた)",
        "",
        "★此の数が意味せぬ事★:",
        "  ・⑴ は「此の枝が変へた file 数」ではない。origin/main が遅れて居る file 数である。",
        "  ・丙−甲 が 0 でも「名に U+2028 が無い」の意ではない。★其の枝の差分に出て来なかつた★だけである。",
        "  ・本器は ⑴ のみを測る。⑵(自前差分)は測つて居らぬ。",
    ]))
    sys.stderr.write("45本 測了 / U2028疵=%d / 甲乙差=%d\n" % (u2028, sum(1 for r in rows if r[3] != r[4])))
    return 0

sys.exit(main())
