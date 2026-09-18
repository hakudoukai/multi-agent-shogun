# -*- coding: utf-8 -*-
"""實射 ―― 門を種ごとに一発づつ撃ち、out と err と rc を ★別々に★ 焼く。
★門の出目は二流★ ―― 門自身の行と結語は stderr / manifest_verify.py の要約は stdout。
∴ 鳴りは ★語★ で数へる(番号で数へると落ちた門が清く読める ―― 番号は通り行にしか出ぬ)。"""
import csv
import importlib.util
import os
import re
import subprocess

spec = importlib.util.spec_from_file_location("K", "driver/00_kaki.py")
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)

GATE = "/Users/momizimac/multi-agent-shogun/scripts/checks/karo_mac_dasumae_gate.sh"

FUDA = [
    ("條②", "★末尾空白 ―― "),
    ("條②測れぬ", "★條② 測れぬ"),
    ("條③", "★CR混入 ―― "),
    ("條③測れぬ", "★條③ 測れぬ"),
    ("條④", "★EOF改行"),
    ("條④測れぬ", "★條④ 測れぬ"),
]


def utsu(args, env=None, tag=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(["bash", GATE] + args, capture_output=True, env=e)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if tag:
        K.kaku("raw/%s.out" % tag, out)
        K.kaku("raw/%s.err" % tag, err)
        K.kaku("raw/%s.rc" % tag, str(r.returncode))
    return r.returncode, out, err


def hiku(err):
    got, togame = {}, {}
    for nm, word in FUDA:
        n, names = 0, []
        for ln in err.split("\n"):
            if word in ln:
                n += 1
                m = re.search(r"―― (\S+)", ln)
                if m:
                    names.append(m.group(1).rstrip("★"))
        got[nm] = n
        togame[nm] = names
    return got, togame


def tane_yomu():
    with open("raw/10_tane.tsv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main():
    tane = tane_yomu()

    # ―― ㋑⑵⑶ 一発づつ(両方向) ――
    rows = []
    for i, t in enumerate(tane, 1):
        nm = t["名"]
        tag = "20_%02d_%s" % (i, nm.replace(".", "_"))
        rc, out, err = utsu(["--", "_tane/" + nm], tag=tag)
        got, _ = hiku(err)
        hou2 = t["法_條②"]
        jitsu2 = "鳴る" if got["條②"] > 0 else ("測れぬ" if got["條②測れぬ"] else "黙る")
        rows.append([nm, t["問ひ"], hou2, jitsu2,
                     "○" if hou2 == jitsu2 else "★×★",
                     got["條②"], got["條③"], got["條④"], rc, tag])
    K.kaku_tsv("raw/20_ippatsu.tsv", rows,
               header=["種", "問ひ", "法_條②", "實_條②", "合", "鳴②", "鳴③", "鳴④", "rc", "出目"])

    # ―― ㋑⑷ NUL の濡れ衣 ―― NUL の紙と清い紙を ★同じ一発★ に載せる ――
    kirei = [t["名"] for t in tane if t["法_條②"] == "黙る" and int(t["NUL"]) == 0]
    nul = [t["名"] for t in tane if int(t["NUL"]) > 0]
    mixed = ["_tane/" + n for n in (nul + kirei)]
    rc, out, err = utsu(["--"] + mixed, tag="21_nurekinu_mazeta")
    got, togame = hiku(err)
    K.kaku("raw/22_nurekinu.txt", "\n".join([
        "# ㋑⑷ NUL の濡れ衣 ―― ★母數と根と深さと刻★",
        "",
        "根   = %s" % os.path.join(os.getcwd(), "_tane"),
        "深さ = 1(_tane 直下のみ・下に dir 無し)",
        "母數 = %d 本(NUL 有 %d + NUL 無で法「黙る」%d)" % (len(mixed), len(nul), len(kirei)),
        "渡した順 = %s" % " ".join(nul + kirei),
        "rc   = %d" % rc,
        "",
        "## 條② が咎めた紙(全て挙げる)",
        "",
        ("\n".join("  - %s" % x for x in togame["條②"]) if togame["條②"]
         else "  (一本も無し)"),
        "",
        "## ★咎めの内訳★",
        "",
        "  NUL を持つ紙で咎められた  = %d 本" % len([x for x in togame["條②"] if os.path.basename(x) in nul]),
        "  ★NUL を持たぬ紙で咎められた★ = %d 本" % len([x for x in togame["條②"] if os.path.basename(x) in kirei]),
        "",
        "∴ ★『NUL の紙が他の紙に濡れ衣を着せる』か否かは、上の二行目で決まる。★",
    ]))

    # ―― ㋑⑸ GREP_OPTIONS=-v で ②③ が入替はるか ――
    swap = []
    for i, t in enumerate(tane, 1):
        nm = t["名"]
        tag = "23_%02d_%s_v" % (i, nm.replace(".", "_"))
        rc, out, err = utsu(["--", "_tane/" + nm], env={"GREP_OPTIONS": "-v"}, tag=tag)
        g, _ = hiku(err)
        rc0, _o0, e0 = utsu(["--", "_tane/" + nm])
        g0, _ = hiku(e0)
        swap.append([nm, g0["條②"], g0["條③"], rc0, g["條②"], g["條③"], rc,
                     "★入替★" if (g0["條②"], g0["條③"]) != (g["條②"], g["條③"]) else "不動"])
    K.kaku_tsv("raw/24_grep_options_v.tsv", swap,
               header=["種", "素_鳴②", "素_鳴③", "素_rc", "v_鳴②", "v_鳴③", "v_rc", "判"])
    print("實射 了")


main()
