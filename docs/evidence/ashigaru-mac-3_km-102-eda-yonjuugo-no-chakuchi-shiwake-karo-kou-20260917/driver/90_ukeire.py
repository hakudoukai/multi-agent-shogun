# -*- coding: utf-8 -*-
"""㋔ 受入条件 ―― ★checkout せず、枝の木を読取で引いて★ 出す前に満たすべき条を一本づつ測る。

  usage: python3 driver/90_ukeire.py <raw dir> <main sha>

測る条(悉く ★在る/無い・形★ であつて、是非ではない):
  甲 束      : ⑵ path の内 docs/evidence/<束>/ に当たる束の名(此の枝が齎す紙束)
  乙 臺帳    : 其の束に MANIFEST.txt が★枝の木に★在るか
  丙 臺帳の根: 臺帳の path 欄が ★束内相対★ か ★repo根相対★ か(裁 seq322699 = 束内相対が條)。
               ★字面の判別であり、否定で判ずる★ ―― `docs/evidence/` 起し or 絶対 path を根相対、
               其れ以外を束内相対と数へる。∴ probe 名(`+1` `" "`)も束内相対側に入る。
               ★此の欄は path の實在を言はぬ・束の中身の良否も言はぬ。根の取り方だけを言ふ。★
  丁 門の器  : scripts/checks/karo_mac_dasumae_gate.sh が★其の枝の木に★在るか(無ければ門を通せぬ)
  戊 臺帳の器: scripts/checks/karo_mac_manifest_append.py が其の枝の木に在るか
  己 対照    : 束内の file 名 or README に「対照」の字が在るか
               ★字の在否であつて、対照が★効いて居る★事の證では★ない★(数の規律3)。
  庚 衝突    : 62 の「重なる枝の数」と其の相手(同じ file を触る他枝)

★此の器が測れぬ物★: 門 rc は ★実際に通すまで判らぬ★(通すには其の枝の木が要り、checkout は禁)。
  ∴ 門 rc は「受入条件」として★書く★が、★此の紙では 0 と宣し得ない★。
出目: 91_ukeire.tsv / 92_taba.tsv(枝×束の明細)
"""
import subprocess
import sys
from importlib import import_module

sys.path.insert(0, __file__.rsplit("/", 1)[0])
K = import_module("00_kaki")

MON = "scripts/checks/karo_mac_dasumae_gate.sh"
DAI = "scripts/checks/karo_mac_manifest_append.py"


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def load(path):
    rows, head = [], None
    for ln in open(path, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if head is None:
            head = c
            continue
        if c and c[0]:
            rows.append(dict(zip(head, c)))
    return rows


def paths_of(base_sha, sha):
    rc, out, err = git("diff", "--name-only", "-z", "%s..%s" % (base_sha, sha))
    if rc != 0:
        return None
    return [p for p in out.split("\0") if p]


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    raw, main_sha = sys.argv[1], sys.argv[2]
    soku = {r["branch"]: r for r in load(raw + "/31_sokutei.tsv")}
    kasa = {r["branch"]: r for r in load(raw + "/62_kasanari_matome.tsv")}
    shiwake = load(raw + "/81_shiwake.tsv")
    ban = load(raw + "/71_utsuwa_ban.tsv")
    meibo = {r["branch"]: r["sha40"] for r in load(raw + "/21_roster.tsv")}
    if len(meibo) != 60:
        sys.stderr.write("★臺帳の枝が %d 本(60 を期す)★ ―― 一行も書かず止まる\n" % len(meibo))
        return 5

    # 陽性対照: main の木には MON が★無い★筈(先の測りで確認済)。此の器でも独立に確かめる。
    rc_mon_main, _, _ = git("cat-file", "-e", "%s:%s" % (main_sha, MON))
    if rc_mon_main == 0:
        sys.stderr.write("★対照が倒れた: main に門の器が在る(先の測りと食ひ違ふ)★ ―― 一行も書かず止まる\n")
        return 5

    # ★庚の「相手」は 61(自前差分で同じ file を触る枝)から引く★。
    # 71 の「枝の名」は ★其の版を木に持つ枝★ であつて ★触つた枝★ ではない ―― 別定義を
    # 同じ欄に流せば衝突を水増しする(実測: settings-hook-abs が 62=0 なのに相手が出た)。
    kumi = load(raw + "/61_kasanari.tsv")
    aite_br = {}
    for r in kumi:
        aite_br.setdefault(r["己の枝"], []).append((r["相手の枝"], r["組"], r["共有path数"]))

    rows, taba_rows = [], []
    for r in shiwake:
        br, sha = r["枝"], r["sha40"]
        kiten_br = soku[br]["(2)kiten_eda"]
        # ★枝名を rev 範囲に使ふな★: origin の枝は local ref に非ず(手許は 7 本のみ)。
        # 先の弾で `fatal: ambiguous argument` を踏んだ ∴ ★臺帳から sha を引き、引けねば止まる★。
        base_sha = meibo.get(kiten_br)
        if not base_sha:
            sys.stderr.write("★基点 %s の sha が臺帳に無い★ ―― 一行も書かず止まる\n" % kiten_br)
            return 5
        ps = paths_of(base_sha, sha)
        if ps is None:
            sys.stderr.write("★%s の ⑵ path が引けぬ★ ―― 一行も書かず止まる\n" % br)
            return 5

        tabas = sorted({p.split("/")[2] for p in ps
                        if p.startswith("docs/evidence/") and len(p.split("/")) > 3})
        dai_ari, dai_uchi, dai_ne, dai_hougen, taishou = 0, 0, 0, 0, 0
        for t in tabas:
            mpath = "docs/evidence/%s/MANIFEST.txt" % t
            rcm, body, _ = git("show", "%s:%s" % (sha, mpath))
            if rcm != 0:
                taba_rows.append([br, t, "★臺帳無し★", "-", "-", "-", "-"])
                continue
            dai_ari += 1
            # ★臺帳は方言を持つ★(一行目が `# dialect: path= sha256= bytes= lines=` と宣する形が在る)。
            # 先の形は `path=` 接頭を剥がねば path 欄に当たらぬ ―― 剥がさず測つて 10/10 を
            # 「判別不能」と出したのは★器の疵であつて知見ではない★ ∴ 剥いでから当てる。
            hougen = ""
            uchi = ne = 0
            for ln in body.split("\n"):
                # ★内側で `t` を使ふな★: 外側の loop 変数(束の名)を潰し、
                # 以後の has_t / README 参照が★臺帳最終行の path★を束名と見做す(実測で対照欄が反転した)。
                fld = ln.strip()
                if not fld:
                    continue
                if fld.startswith("#"):
                    if not hougen and "dialect" in fld:
                        hougen = fld[:70]
                    continue
                if fld.startswith("path="):
                    fld = fld[5:]
                fld = fld.split("\t")[0].split(" ")[0].strip().strip('"')
                # ★白表(driver/|raw/…)で数へるな★: km-83 の臺帳は `10_kuchi/…` `40_doku/…` で
                # 束内相対なのに白表に漏れ、10 本中 1 本を「別方言」と誤つた。
                # 裁 seq322699 が問ふのは ★根から書かれて居るか否か★ 一点ゆゑ ★否定で判ずる★。
                # ∴ probe 名(`+1` `" "` 等)も「根相対でない」側に数へる ―― 此の欄は
                # ★path の實在★でも★束の中身★でもなく、★根の取り方★だけを言ふ。
                if fld.startswith("docs/evidence/") or fld.startswith("/"):
                    ne += 1
                else:
                    uchi += 1
            kind = "★束内相対★" if uchi and not ne else ("★根相対(裁322699に反)★" if ne and not uchi
                                                    else ("★両形混在★" if ne and uchi else "★別方言(判別不能)★"))
            if kind.startswith("★束内"):
                dai_uchi += 1
            elif kind.startswith("★根相対"):
                dai_ne += 1
            else:
                dai_hougen += 1
            has_t = any("対照" in p for p in ps if ("/%s/" % t) in p)
            rcr, rbody, _ = git("show", "%s:docs/evidence/%s/README.md" % (sha, t))
            if not has_t and rcr == 0 and "対照" in rbody:
                has_t = True
            if has_t:
                taishou += 1
            taba_rows.append([br, t, "在り", kind, "%d/%d(束内/根)" % (uchi, ne),
                              "対照の字 在り" if has_t else "対照の字 無し",
                              hougen or "(方言の宣 無し)"])

        rc_mon, _, _ = git("cat-file", "-e", "%s:%s" % (sha, MON))
        rc_dai, _, _ = git("cat-file", "-e", "%s:%s" % (sha, DAI))
        shou = sorted("%s(%s)" % (n, c) for n, _k, c in aite_br.get(br, []))
        rows.append([br, len(tabas), "%d/%d" % (dai_ari, len(tabas)),
                     "%d/%d/%d" % (dai_uchi, dai_ne, dai_hougen),
                     "%d/%d" % (taishou, len(tabas)),
                     "在り" if rc_mon == 0 else "★無し★",
                     "在り" if rc_dai == 0 else "★無し★",
                     kasa[br]["重なる枝の数"],
                     " ".join(s.split("/", 1)[-1][:34] for s in shou) if shou else "-"])

    K.kaku_tsv(raw + "/91_ukeire.tsv", rows,
               header=["枝", "甲:束数", "乙:臺帳在/束", "丙:束内/根/別方言", "己:対照の字/束",
                       "丁:門の器", "戊:臺帳の器", "庚:重なる枝数", "庚:衝突の相手"])
    K.kaku_tsv(raw + "/92_taba.tsv", taba_rows,
               header=["枝", "束", "臺帳", "臺帳の根", "行数(束内/根)", "対照の字", "方言の宣"])
    sys.stderr.write("枝=%d / 束の行=%d / 対照(main に門の器無し)=立つ\n" % (len(rows), len(taba_rows)))
    return 0


sys.exit(main())
