#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋑/㋒ ★現物★で v5 と 案甲鎖 の出目が違ふ行を、★臺帳と非臺帳を分けて★数へる器。

30_genbutsu.py の二つの疵を治した版(治した事も数で示す):
  疵一 ★第二の for の基準器が誤り★
        30 は「案甲列 に無い候補」を第二の for の寄与と看做してゐた。
        然し `grep -c 'for tok in line.split()'` は ★九本悉く 1★(raw/32_daini_for_dokoni.txt)
        ―― 案甲列 も持つ。∴ 其の差は構造上常に空で、★何も測つて居らぬ★。
        本器は ★第二の for を除いた版★(_an/v5_daini_nashi.py・_an/an_kusari_daini_nashi.py)
        を基準に取る。
  疵二 ★臺帳と非臺帳を分けて居らぬ★
        30 は己束/外 の二分のみ。現物の差 6 行は悉く ★臺帳ではない TSV★ に在つた。
        本器は 臺帳甲(名が manifest を含み .txt) / 乙其他(path= を持つ其他の file) /
        丙己束(己の束) の ★三区域★ に分ける(除くのではない・別に数へる)。
  疵三 ★TSV の欄に TAB が混じる★ ―― 候補文字列自身が TAB を含み得る。
        本器は ★出す全ての欄★ を通して TAB/改行を可視記号へ置換する。

歩き根は argv[1](既定 = <repo>/docs/evidence) ―― ★一本★。深さ無制限。
出 = raw/31_genbutsu.txt / raw/31_chigau_gyou.tsv / raw/31_daini_for.tsv
"""
import importlib.util
import os
import re
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))
SEED = os.path.join(BUNDLE, "..",
                    "karo-mac_km-113-kuuhaku-wo-fukumu-na-ga-arawasenu-kizu-20260917",
                    "_ver")
SHA = re.compile(r"sha256=([0-9a-f]{64})")
M2 = re.compile(r"(?:^|\s)path=(.+?)[ \t]+sha256=")
HAS_PATH = re.compile(r"(?:^|\s)path=\S")

KI = [
    ("v5", os.path.join(BUNDLE, "_ki", "v5_pr23.py")),
    ("鎖", os.path.join(BUNDLE, "_an", "an_kou_kusari.py")),
    ("v5第二無", os.path.join(BUNDLE, "_an", "v5_daini_nashi.py")),
    ("鎖第二無", os.path.join(BUNDLE, "_an", "an_kusari_daini_nashi.py")),
]
ZONES = ["臺帳甲", "乙其他", "丙己束"]
KINDS = ["㋐飛ばし", "㋑m2當り", "㋒m2外れ"]


def load(name, path):
    spec = importlib.util.spec_from_file_location("ki31_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.paths_of


def mieru(s, cap=70):
    """★出す全ての欄★ を通す ―― TAB/改行/CR を可視記号へ(TSV の列が壊れぬ様に)。"""
    s = str(s)
    s = s.replace("\t", "␉").replace("\r", "␍").replace("\n", "␊")
    return s if len(s) <= cap else s[:cap] + "…"


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    t0 = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    fn = {k: load(k, p) for k, p in KI}

    # ★陽性対照★ ―― 器が現に別物を返す事を、己で建てた四行で先に示す
    taishou = [
        ("②が當る行(空白名)", "path=a b.txt sha256=" + "0" * 64 + " bytes=1 lines=1"),
        ("②が當らぬ行(sha先)", "sha256=" + "0" * 64 + " path=a b.txt bytes=1 lines=1"),
        ("②當り＋'/'語有り", "path=nai.txt sha256=" + "0" * 64 + " bytes=1 lines=1 aru/x.txt"),
        ("②外れ＋'/'語有り", "sha256=" + "0" * 64 + " path=nai.txt bytes=1 aru/x.txt"),
    ]
    trows = [[k, mieru(ln, 60)] + [mieru("|".join(fn[g](ln)) or "(空)") for g, _ in KI]
             for k, ln in taishou]

    files, pycache, irreg, maxdepth = [], 0, 0, 0
    for dirpath, dirnames, filenames in os.walk(walk_root):
        if os.path.basename(dirpath) == "__pycache__":
            pycache += len(filenames)
            dirnames[:] = []
            continue
        maxdepth = max(maxdepth, dirpath[len(walk_root):].count(os.sep) + 1)
        for f in filenames:
            p = os.path.join(dirpath, f)
            try:
                st = os.lstat(p)
            except OSError:
                irreg += 1
                continue
            if not stat.S_ISREG(st.st_mode):
                irreg += 1
                continue
            files.append(p)

    MINE = BUNDLE + os.sep
    cache = {}

    def aru(b, p):
        k = (b, p)
        if k not in cache:
            try:
                cache[k] = os.path.isfile(os.path.join(b, p)) if p else False
            except (OSError, ValueError):
                cache[k] = False
        return cache[k]

    def noboru(bases, cands):
        for p in cands:
            for b in bases:
                if aru(b, p):
                    return p
        return None

    def zone_of(p):
        if p.startswith(MINE):
            return "丙己束"
        b = os.path.basename(p).lower()
        return "臺帳甲" if ("manifest" in b and b.endswith(".txt")) else "乙其他"

    n = {k: 0 for k in KINDS}
    nz = {}
    nfz = {z: 0 for z in ZONES}
    comment = 0
    chigau, daini = [], []
    # 断の器(区域別に持つ)
    z_kouho = {z: 0 for z in ZONES}      # v5 と鎖 で候補列が違ふ
    z_noboru = {z: 0 for z in ZONES}     # 昇る物まで違ふ
    z_d_v5 = {z: 0 for z in ZONES}       # v5 で第二の for が候補を足した
    z_d_v5_nob = {z: 0 for z in ZONES}   # 其の足した候補が昇つた
    z_d_ks = {z: 0 for z in ZONES}       # 鎖 で第二の for が候補を足した
    z_d_ks_nob = {z: 0 for z in ZONES}
    # 包含の向き(★v5 が鎖より緩いか厳しいか★)
    houkou = {"v5⊂鎖(v5 が厳しい)": 0, "鎖⊂v5(v5 が緩い)": 0,
              "互ひに含まぬ": 0, "同じ": 0}
    nfile_hit = 0
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            irreg += 1
            continue
        if "sha256=" not in txt and "path=" not in txt:
            continue
        zone = zone_of(p)
        bases = [os.path.dirname(p), REPO]
        hit = False
        for no, raw in enumerate(txt.split("\n"), 1):
            line = raw.strip()
            if not line:
                continue
            if not HAS_PATH.search(line) and not SHA.search(line):
                continue
            hit = True
            if line.startswith("#"):
                comment += 1
                continue
            if not SHA.search(line):
                n["㋐飛ばし"] += 1
                nz[(zone, "㋐飛ばし")] = nz.get((zone, "㋐飛ばし"), 0) + 1
                continue
            kind = "㋑m2當り" if M2.search(line.replace("\r", "")) else "㋒m2外れ"
            n[kind] += 1
            nz[(zone, kind)] = nz.get((zone, kind), 0) + 1
            c = {g: fn[g](line) for g, _ in KI}
            sv, sk = set(c["v5"]), set(c["鎖"])
            if sv == sk:
                houkou["同じ"] += 1
            elif sv < sk:
                houkou["v5⊂鎖(v5 が厳しい)"] += 1
            elif sk < sv:
                houkou["鎖⊂v5(v5 が緩い)"] += 1
            else:
                houkou["互ひに含まぬ"] += 1
            if c["v5"] != c["鎖"]:
                z_kouho[zone] += 1
                a, b = noboru(bases, c["v5"]), noboru(bases, c["鎖"])
                if a != b:
                    z_noboru[zone] += 1
                chigau.append([mieru(os.path.relpath(p, REPO), 120), no, zone, kind,
                               mieru("|".join(c["v5"])), mieru("|".join(c["鎖"])),
                               mieru(a), mieru(b),
                               "★昇る物も違ふ★" if a != b else "昇る物は同",
                               mieru(line)])
            # ★第二の for の寄与★ ―― 除いた版との差(★之が正しい基準★)
            for g, gn, ck, cn in (("v5", "v5第二無", z_d_v5, z_d_v5_nob),
                                  ("鎖", "鎖第二無", z_d_ks, z_d_ks_nob)):
                add = [x for x in c[g] if x not in c[gn]]
                if not add:
                    continue
                ck[zone] += 1
                nb = noboru(bases, c[g])
                got = nb in add
                if got:
                    cn[zone] += 1
                daini.append([mieru(os.path.relpath(p, REPO), 120), no, zone, kind, g,
                              mieru("|".join(add)), mieru(nb),
                              "★足した候補が昇つた★" if got else "昇らず", mieru(line)])
        if hit:
            nfile_hit += 1
            nfz[zone] += 1

    dt = time.time() - t0
    S = sum
    o = [f"# ㋑/㋒ 現物 ―― ★臺帳と非臺帳を分けて★数へる / 刻 {stamp} / 所要 {dt:.1f}s",
         f"# 歩き根(★一本★) = {walk_root}",
         f"#   深さ(最大) = {maxdepth} 段 / 歩いた file = {len(files)} 本 / "
         f"path= か sha256= を持つ file = {nfile_hit} 本",
         f"#   __pycache__ 配下で除いた = {pycache} 本 / S_ISREG でない・讀めなんだ = {irreg} 本",
         f"# '#' で始まる行(讀み手が飛ばす) = {comment} 行 ―― 下の母數の★外★",
         "",
         "# ★区域の定め★(排他・先に當つた物を採る)",
         "#   丙己束 = 己(km-117)の束の下 ―― ★除かず別に数へる★(己を測る器は己を含む)",
         f"#   臺帳甲 = 名が 'manifest' を含み '.txt' で終る file ―― ★門が現に照合する物★",
         "#   乙其他 = 其の外で path= か sha256= を持つ file(TSV・紙・引用・log 等)",
         "\t".join(["区域", "file 数"])]
    for z in ZONES:
        o.append("\t".join([z, str(nfz[z])]))
    o += ["",
          "# ★陽性対照★ ―― 器が現に別の候補列を返す事を、己で建てた四行で示す",
          "#   (之が無ければ『差 0 行』は『器が差を見られぬ』の意かも知れぬ)",
          "\t".join(["対照", "行(頭60字)"] + [g for g, _ in KI])]
    for r in trows:
        o.append("\t".join(str(x) for x in r))
    o += ["",
          "# 讀み手 main が辿る道での仕分(★排他・網羅★) × 区域",
          "\t".join(["区域"] + KINDS + ["計"])]
    for z in ZONES:
        r = [nz.get((z, k), 0) for k in KINDS]
        o.append("\t".join([z] + [str(x) for x in r] + [str(S(r))]))
    o.append("\t".join(["計"] + [str(n[k]) for k in KINDS] + [str(S(n.values()))]))
    o += ["",
          "#   ㋐飛ばし = sha256=<64hex> が無い ―― ★main が paths_of を呼ぶ前に continue★",
          "#              ∴ 此処に何行在つても v5 と案甲鎖 の差には★成り得ぬ★",
          "#              (家老の『③sha無 280行』の面は、此の一行で差の外に出る)",
          "#   ㋑m2當り = v5 は ★唯一の候補★ を返し、★第二の for も飛ばす★(return が先)",
          "#   ㋒m2外れ = v5 は列べる形＋第二の for へ落ちる",
          "",
          "# ★断㋑★ v5 と 案甲鎖 ―― 候補列が違ふ行 / 昇る物まで違ふ行(区域別)",
          "\t".join(["区域", "候補列が違ふ", "昇る物も違ふ", "母數(paths_of へ入つた行)"])]
    for z in ZONES:
        m = S(nz.get((z, k), 0) for k in ("㋑m2當り", "㋒m2外れ"))
        o.append("\t".join([z, str(z_kouho[z]), str(z_noboru[z]), str(m)]))
    o.append("\t".join(["計", str(S(z_kouho.values())), str(S(z_noboru.values())),
                        str(n["㋑m2當り"] + n["㋒m2外れ"])]))
    o += ["",
          "# ★断㋑'★ 候補列の包含の向き(母數 = paths_of へ入つた行)",
          "#   v5⊂鎖 = ★v5 の方が候補が少ない = 厳しい★ / 鎖⊂v5 = v5 の方が緩い",
          "\t".join(["向き", "行数"])]
    for k, v in houkou.items():
        o.append("\t".join([k, str(v)]))
    o += ["",
          "# ★断㋒★ ★第二の for(tok.split の '/' 語)★ が候補を足した行(区域別)",
          "#   基準 = ★第二の for を除いた版★(_an/v5_daini_nashi.py・_an/an_kusari_daini_nashi.py)",
          "#   ―― 案甲列 を基準に取つた 30_genbutsu.py の数は ★無効★(九本悉くが第二の for を持つ)",
          "\t".join(["区域", "v5 が足した", "内 昇つた", "鎖 が足した", "内 昇つた"])]
    for z in ZONES:
        o.append("\t".join([z, str(z_d_v5[z]), str(z_d_v5_nob[z]),
                            str(z_d_ks[z]), str(z_d_ks_nob[z])]))
    o.append("\t".join(["計", str(S(z_d_v5.values())), str(S(z_d_v5_nob.values())),
                        str(S(z_d_ks.values())), str(S(z_d_ks_nob.values()))]))
    o += ["",
          "# ★此の数が言はぬ事★",
          "#  ・数は ★此の歩き根・此の刻★ の物である。別の根・別の刻では動く(束は走る間も増える)。",
          "#  ・㋐飛ばし の行数は ★v5 と鎖 の差とは無縁★ ―― main が paths_of を呼ばぬ故。",
          "#  ・『昇る物が同じ』は ★此の二基点(臺帳の隣・repo根)★ での話 ―― 門は他の基点も取り得る。",
          "#  ・区域は ★名★ で分けた ―― 名が manifest でない臺帳、名が manifest な非臺帳は取り違へる。",
          "#  ・現物に無い形は測れて居らぬ ―― 型見の 12 区(raw/10_menseki_yoyaku.txt・raw/13_otori.txt)が受け皿。",
          "#  ・『足した候補が昇つた』は ★sha が合つたか★ を言はぬ(昇つた後に照合が有る)。"]
    kaku(os.path.join(outdir, "31_genbutsu.txt"), "\n".join(o))
    kaku_tsv(os.path.join(outdir, "31_chigau_gyou.tsv"), chigau,
             header=["file", "行", "区域", "区分", "v5 の候補", "鎖 の候補",
                     "v5 で昇る物", "鎖 で昇る物", "判", "行(頭70字)"])
    kaku_tsv(os.path.join(outdir, "31_daini_for.tsv"), daini,
             header=["file", "行", "区域", "区分", "器", "第二の for が足した候補",
                     "昇る物", "判", "行(頭70字)"])
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
