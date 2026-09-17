# -*- coding: utf-8 -*-
"""㋐ 母數を閉ぢる ―― 三紙の割当を寄せ、60−不要15=45 と突合する。

★三形を宣してから読む(手で写さぬ)★:
  a1 `raw/05_warimochi18.tsv`      冠★無★ / 0=sha40 1=枝名
  a2 `raw/10_bosuu_warimochi.tsv`  冠★有★ / 0=枝名 1=sha40
  當 `raw/11_bogen.tsv`            冠★有★ / 1=sha40 2=枝名
  60本 a1 `raw/02_karo_60tips_utsushi.tsv`(冠有 0=sha40 1=枝名) ／ a2 `raw/10_bosuu_mac60.tsv`(冠有 0=枝名 1=sha40)
       當 `raw/21_roster.tsv`(冠有 0=sha40 1=枝名)
  不要15 a1 `raw/03_karo_fuyou15_utsushi.tsv`(冠有 0=sha12 1=枝名)

★此の器が測るもの★: 三紙の割当の★和集合★と、60−15 の★差集合★が同じ物かどうか。
★測らぬもの★: 枝の中身・着地の可否。本器は名と sha の突合のみ。

対照(倒れたら止まる):
  甲 三本の 60本写しが互ひに一致せぬ → 止(どれかの写しが古い)
  乙 割当の和が 45 でない → 止めはせぬが★差を一本づつ名で書く★(それが的)
  丙 同じ枝名に二つの sha → 止(名の揺れではなく実体の食ひ違ひ)
  丁 仕込んだ偽名 `zzz-nonexistent/xxx` が差集合に現れたら 止(集合演算の向きが逆)
"""
import os, sys, importlib.util
_d = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("K", os.path.join(_d, "00_kaki.py"))
K = importlib.util.module_from_spec(_s); _s.loader.exec_module(K)

REPO = os.path.abspath(os.path.join(_d, "..", "..", "..", ".."))
A1 = os.path.join(REPO, "docs/evidence/ashigaru-mac-1_km-100-eda-chakuchi-shiwake-20260917")
A2 = os.path.join(REPO, "docs/evidence/a2_km-101-eda-yonjuugo-no-chakuchi-shiwake-20260917")
A3 = os.path.join(REPO, "docs/evidence/ashigaru-mac-3_km-102-eda-yonjuugo-no-chakuchi-shiwake-karo-kou-20260917")

def rows(path, header, cols):
    """TSV を読み (枝名, sha) を返す。cols=(枝の欄, shaの欄)。"""
    with open(path, encoding="utf-8") as f:
        raw = f.read().split("\n")
    out = []
    for i, ln in enumerate(raw):
        if not ln.strip():
            continue
        if header and i == 0:
            continue
        c = ln.split("\t")
        if max(cols) >= len(c):
            raise ValueError("%s 行%d: 欄が足らぬ(%d)" % (path, i + 1, len(c)))
        out.append((c[cols[0]].strip(), c[cols[1]].strip()))
    return out

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: 10_bogen.py <束の根>\n"); return 2
    base = sys.argv[1]; raw = os.path.join(base, "raw")

    wari = {
        "a1": rows(os.path.join(A1, "raw/05_warimochi18.tsv"), False, (1, 0)),
        "a2": rows(os.path.join(A2, "raw/10_bosuu_warimochi.tsv"), True, (0, 1)),
        "a3": rows(os.path.join(A3, "raw/11_bogen.tsv"), True, (2, 1)),
    }
    tips = {
        "a1": rows(os.path.join(A1, "raw/02_karo_60tips_utsushi.tsv"), True, (1, 0)),
        "a2": rows(os.path.join(A2, "raw/10_bosuu_mac60.tsv"), True, (0, 1)),
        "a3": rows(os.path.join(A3, "raw/21_roster.tsv"), True, (1, 0)),
    }
    fuyou = rows(os.path.join(A1, "raw/03_karo_fuyou15_utsushi.tsv"), True, (1, 0))

    # ── 対照甲: 三本の 60本写しが一致するか ──────────────────
    sets = {k: dict(v) for k, v in tips.items()}
    if not (set(sets["a1"]) == set(sets["a2"]) == set(sets["a3"])):
        sys.stderr.write("★60本の写しが三紙で食ひ違ふ ∴ 止まる★\n"); return 5
    sha_mismatch = [b for b in sets["a1"]
                    if not (sets["a1"][b] == sets["a2"][b] == sets["a3"][b])]
    if sha_mismatch:
        sys.stderr.write("★同名で sha が違ふ(%d 本) ∴ 止まる: %s★\n" % (len(sha_mismatch), sha_mismatch[:3])); return 5
    tip60 = sets["a1"]

    # ── 対照丙: 割当内で同名二 sha ────────────────────────
    seen = {}
    for seat, v in wari.items():
        for b, s in v:
            if b in seen and seen[b][1] != s:
                sys.stderr.write("★割当に同名別sha: %s (%s / %s) ∴ 止まる★\n" % (b, seen[b], (seat, s))); return 5
            seen.setdefault(b, (seat, s))

    # ── 割当の和 / 60−15 の差 ─────────────────────────────
    wari_all = {}
    dup = []
    for seat, v in wari.items():
        for b, s in v:
            if b in wari_all:
                dup.append((b, wari_all[b][0], seat))
            else:
                wari_all[b] = (seat, s)
    fuyou_names = set(b for b, _ in fuyou)
    nokori = set(tip60) - fuyou_names

    # ── 対照丁: 偽名は差集合に現れぬ事 ────────────────────
    if "zzz-nonexistent/xxx" in nokori or "zzz-nonexistent/xxx" in set(wari_all):
        sys.stderr.write("★偽名が集合に現れた ∴ 止まる★\n"); return 5
    probe = (set(tip60) | {"zzz-nonexistent/xxx"}) - fuyou_names
    if "zzz-nonexistent/xxx" not in probe:
        sys.stderr.write("★偽名を足したのに差集合へ出ぬ ∴ 集合演算が効いて居らぬ ∴ 止まる★\n"); return 5

    nomi_wari = sorted(set(wari_all) - nokori)   # 割当に在り 45 に無い
    nomi_45   = sorted(nokori - set(wari_all))   # 45 に在り割当に無い

    K.kaku_tsv(os.path.join(raw, "11_bogen_warimochi.tsv"),
               [[seat, b, s] for b, (seat, s) in sorted(wari_all.items(), key=lambda x: (x[1][0], x[0]))],
               ["席", "枝名", "sha40"])
    K.kaku_tsv(os.path.join(raw, "12_bogen_sa.tsv"),
               ([["割当のみ(45に無し)", b, wari_all[b][0]] for b in nomi_wari] +
                [["45のみ(割当に無し)", b, "-"] for b in nomi_45]) or [["差無し", "-", "-"]],
               ["向き", "枝名", "席"])
    K.kaku(os.path.join(raw, "13_bogen_matome.txt"), "\n".join([
        "60本(三紙の写しが一致)      = %d" % len(tip60),
        "不要15(臺帳 17d7dbf7・a1写) = %d" % len(fuyou_names),
        "60 − 不要15                 = %d" % len(nokori),
        "割当の和(a1 %d / a2 %d / 當 %d) = %d" % (len(wari["a1"]), len(wari["a2"]), len(wari["a3"]), len(wari_all)),
        "重複(二席が同じ枝を持つ)     = %d" % len(dup),
        "割当のみ(45に無し)           = %d" % len(nomi_wari),
        "45のみ(割当に無し)           = %d" % len(nomi_45),
        "★閉ぢたか★                  = %s" % ("★閉ぢた(和 = 60−15 = 45)★" if (not nomi_wari and not nomi_45 and len(wari_all) == 45) else "★閉ぢて居らぬ★"),
        "",
        "★此の数が意味せぬ事★: 45 は「着地させる枝の数」ではない。",
        "  「三席が測つた枝の数」であり、甲乙丙の内訳とは別の話である。",
        "  不要15 は家老の臺帳 17d7dbf7 の写しを信じた数で、當席が測り直した数ではない。",
    ]))
    sys.stderr.write("60=%d 不要=%d 残=%d 和=%d 重複=%d 差=%d/%d\n" %
                     (len(tip60), len(fuyou_names), len(nokori), len(wari_all), len(dup), len(nomi_wari), len(nomi_45)))
    return 0

sys.exit(main())
