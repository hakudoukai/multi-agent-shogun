# -*- coding: utf-8 -*-
"""合はせ器 ―― ★紙に焼いた数★と★最終巡の門の出目★が同じ物である事を検める。

★何故 要るか★
  焼けば紙が変はる ∴ 焼いた時の門と、焼いた後の門は★別の回★である。
  「門 rc=0」と書いた紙が、其の一行を書いた所為で門に落ちる ―― は現に起き得る。
  ∴ ★焼いた数 = 最終巡の数★ を、紙と門の双方から★引き直して★突き合はせる。

★引き方★
  甲: `README.md` の一行目から(焼いた側)
  乙: `_gate/<最終巡>.{rc,out,err}` から(門の側)
  二つは★別の正規表現★で引く。同じ器で引けば、器の疵が両方に等しく乗り
  「一致」が自動的に出る ―― 其れは突合に非ず。

★対照★
  ⓐ ★負対照★ 焼いた行の数を一つ書き換へた贋の行を作り、★必ず食ひ違ふ★事を見る。
     食ひ違はねば比べ器が死んで居る ∴ 止まる(rc=5)。
  ⓑ ★本数★ 引けた欄が悉く揃はねば止まる(黙つて少ない欄で「一致」と言はぬ)。
  ⓒ ★便も検める★ ―― 納め便は臺帳が凍る前に組む ∴ 「門rc=0」は★見込み★である。
     便の申す門rcと最終巡の名が、実際に当てた門と同じ事を此處で突き合はせる。
     食ひ違へば ★便を送らぬ★(書いて在る事は送つた事ではない)。

★本器の出目は `_gate/` へ置く★ ―― 臺帳の外である(門の log と同じ扱ひ)。
  理由: 本器は★門の後に走る★。raw/ へ書けば臺帳と disk が其の場で食ひ違ひ、
  條① を己で破る(km-67 で踏んだ形)。∴ 宣して臺帳の外へ出す。
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = __import__("00_kaki")

# 甲 ―― 紙の一行目から引く形
KAMI = [
    ("門 rc",            r"門 rc=(\d+)"),
    ("臺帳 行",          r"臺帳 (\d+) 行"),
    ("條① 一致",        r"一致 (\d+)\("),
    ("條① 相違",        r"相違 (\d+)"),
    ("條① 実体無",      r"実体無 (\d+)"),
    ("條① 讀めぬ行",    r"讀めぬ行 (\d+)"),
    ("manifest_verify rc", r"manifest_verify\.py rc=(\d+)"),
    ("條②③④ 本数",    r"條②③④=全 (\d+) 本"),
]
# 乙 ―― 門の出目から引く形(★別の字を手掛りにする★)
MON = [
    ("門 rc",            "rc",  r"^rc=(\d+)$"),
    ("臺帳 行",          "out", r"\(母數 (\d+)\)"),
    ("條① 一致",        "out", r"一致 ★(\d+)★"),
    ("條① 相違",        "out", r"/ 相違 (\d+) /"),
    ("條① 実体無",      "out", r"/ 実体無 (\d+) /"),
    ("條① 讀めぬ行",    "out", r"読めぬ行 (\d+)"),
    ("manifest_verify rc", "err", r"manifest_verify\.py rc=(\d+)\)"),
    ("條②③④ 本数",    "err", r"全file\((\d+)本\)通"),
]


def hiku_kami(gyou):
    out = {}
    for na, seiki in KAMI:
        m = re.search(seiki, gyou, re.M)
        if m:
            out[na] = m.group(1)
    return out


def main(bundle, saigo):
    g = os.path.join(bundle, "_gate")
    gyou = open(os.path.join(bundle, "README.md"), encoding="utf-8").read().split("\n")[0]

    kami = hiku_kami(gyou)
    if len(kami) != len(KAMI):                       # ── 対照ⓑ
        sys.stderr.write("★紙の一行目から %d 欄しか引けぬ(要 %d) ∴ 止まる★\n"
                         % (len(kami), len(KAMI)))
        return 5

    moji = {k: open(os.path.join(g, saigo + "." + k), encoding="utf-8").read()
            for k in ("rc", "out", "err")}
    mon = {}
    for na, doko, seiki in MON:
        m = re.search(seiki, moji[doko], re.M)
        if not m:
            sys.stderr.write("★門の出目(%s)から %s を引けぬ ∴ 止まる★\n" % (doko, na))
            return 5
        mon[na] = m.group(1)

    # ── 紙が指す最終巡の名が、実際に当てた門と同じか
    m = re.search(r"`_gate/([0-9A-Za-z_]+)\.\*`", gyou)
    sasu = m.group(1) if m else "★引けず★"
    sashi_au = (sasu == saigo)

    rows, chigau = [], 0
    for na, _ in KAMI:
        au = kami[na] == mon[na]
        if not au:
            chigau += 1
        rows.append([na, kami[na], mon[na], "一致" if au else "★食ひ違ふ★"])

    # ── 対照ⓐ 負対照: 焼いた行の「臺帳 N 行」を一つずらした贋の行
    nise = re.sub(r"臺帳 (\d+) 行", lambda m: "臺帳 %d 行" % (int(m.group(1)) + 1), gyou, count=1)
    nise_k = hiku_kami(nise)
    nise_chigau = sum(1 for na, _ in KAMI if nise_k.get(na) != mon[na])
    if nise_chigau != chigau + 1:
        sys.stderr.write("★負対照が鳴らず(贋の行の食ひ違ひ %d・本番 %d) ∴ 比べ器が死んで居る★\n"
                         % (nise_chigau, chigau))
        return 5

    # ── 便の申す事も検める(便は★門より先に★組んだ ∴ 見込みで「門rc=0」と書いて在る)
    bin_p = os.path.join(bundle, "raw", "96_osame.txt")
    bin_gyou = open(bin_p, encoding="utf-8").read().strip() if os.path.exists(bin_p) else ""
    m = re.search(r"門rc=(\d+)\(_gate/([0-9A-Za-z_]+)\)", bin_gyou)
    if not bin_gyou:
        bin_han = "―― 便が未だ無い"
    elif not m:
        bin_han = "★便から門rcと最終巡を引けぬ★"; chigau += 1
    else:
        b_rc, b_saki = m.group(1), m.group(2)
        au = (b_rc == mon["門 rc"]) and (b_saki == saigo)
        bin_han = ("便 門rc=%s 最終巡=%s → %s"
                   % (b_rc, b_saki, "★門と同じ★" if au else "★門と食ひ違ふ★"))
        if not au:
            chigau += 1

    K.kaku_tsv(os.path.join(g, "85_awase.tsv"), rows,
               ["欄", "甲 紙に焼いた値", "乙 門の出目の値", "判"])
    K.kaku(os.path.join(g, "85_awase.txt"), "\n".join([
        "合はせ ―― 紙の一行目 ⇔ 最終巡の門 `_gate/%s.*`" % saigo,
        "",
        "食ひ違ひ = ★%d 欄 / %d 欄★" % (chigau, len(KAMI)),
        "紙が指す最終巡の名 = `%s` ／ 実際に当てた門 = `%s` → %s"
        % (sasu, saigo, "★同じ★" if sashi_au else "★食ひ違ふ★"),
        "対照ⓐ 負対照(臺帳の行数を +1 した贋の行) = ★食ひ違ひが丁度一つ増えた★ ∴ 比べ器は生きて居る",
        "対照ⓑ 紙から引けた欄 = %d / %d" % (len(kami), len(KAMI)),
        "",
        "★納め便の申す事★(便は門より先に組んだ ∴ 見込みで書いて在る ―― 此處で検める):",
        "  " + bin_han,
        "",
        "★本器の出目は臺帳の外★(`_gate/` ―― 門の log と同じ扱ひ)。",
        "  門の後に走る器の出目を raw/ へ書けば、其の場で臺帳と disk が食ひ違ひ條①を己で破る。",
        "",
        "★此の合はせが意味せぬ事★:",
        "  ・「一致」は★紙と門が同じ回を指す★事のみを示す。中身の正しさとは別である。",
        "  ・byte 和 と file の sha は焼いて居らぬ ∴ 本器も突き合はせて居らぬ(臺帳の役)。",
    ]))
    if chigau or not sashi_au:
        sys.stderr.write("★合はず 食ひ違ひ%d 指す先=%s★\n" % (chigau, sasu))
        return 7
    sys.stderr.write("合 了 %d欄 悉く一致 / 指す先=%s / 負対照 鳴る\n" % (len(KAMI), sasu))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
