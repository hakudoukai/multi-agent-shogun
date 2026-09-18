# -*- coding: utf-8 -*-
"""紙の一行目へ ★門の出目を焼く★ 器。

★何を焼くか★ ―― 門の rc と 條① の内訳(一致/相違/実体無/讀めぬ行)と母數。
★何を焼かぬか★ ―― ★byte 和★と★本束 file の sha★。
   焼けば紙が変はり、紙が変はれば byte 和 も sha も変はる ∴ ★焼いた瞬間に古びる★。
   一致・相違・母數は ★紙を直しても動かぬ★(file の本数が変はらぬ限り) ∴ 焼ける。

★焼くと紙の sha が変はる★ ∴ 手順は必ず:
   ⑴ 門(第一巡) → ⑵ 本器で焼く → ⑶ 臺帳を建て直す → ⑷ 門(最終巡)
   → ⑸ `driver/90_awase.py` で ★焼いた数 = 最終巡の数★ を検める。
   ⑸ を欠けば「第一巡の数を焼いた紙」を出す事に成る ―― ★紙と門が別の回を指す★。

数は門の出目 file から★引く★(手で打たぬ)。引けねば ★焼かずに止まる(rc=5)★。
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = __import__("00_kaki")

YAKI_ATAMA = "門 rc="          # ★既に焼いて在る行★の見分け(二度焼きで行が増えぬやう)


def hiku(s, seiki, na):
    m = re.search(seiki, s)
    if not m:
        sys.stderr.write("★門の出目から %s を引けぬ ∴ 焼かずに止まる★\n" % na)
        return None
    return m.group(1)


def main(bundle, sechi, saki):
    g = os.path.join(bundle, "_gate")
    rc_s = open(os.path.join(g, sechi + ".rc"), encoding="utf-8").read().strip()
    out = open(os.path.join(g, sechi + ".out"), encoding="utf-8").read()
    err = open(os.path.join(g, sechi + ".err"), encoding="utf-8").read()

    rc = hiku(rc_s, r"rc=(\d+)", "門 rc")
    icchi = hiku(out, r"一致 ★(\d+)★", "條① 一致")
    soui = hiku(out, r"相違 (\d+)", "條① 相違")
    jittai = hiku(out, r"実体無 (\d+)", "條① 実体無")
    yomenu = hiku(out, r"読めぬ行 (\d+)", "條① 讀めぬ行")
    bogen = hiku(out, r"母數 (\d+)", "條① 母數")
    kyuukei = hiku(out, r"★旧形\(引用符を含む行\)★ (\d+) 行", "旧形")
    vrc = hiku(err, r"manifest_verify\.py rc=(\d+)", "manifest_verify rc")
    honsuu = hiku(err, r"全file\((\d+)本\)通", "條②③④ の本数")
    kiten = hiku(err, r"條① 基点=★([^★]+)★", "條① 基点")
    if None in (rc, icchi, soui, jittai, yomenu, bogen, kyuukei, vrc, honsuu, kiten):
        return 5

    gyou = ("門 rc=%s ／ 母數=★三席の割当 枝 45 本★・★臺帳 %s 行★ ／ "
            "條①=一致 %s(相違 %s・実体無 %s・讀めぬ行 %s・旧形 %s・manifest_verify.py rc=%s) ／ "
            "條②③④=全 %s 本 通 ―― 出す前門を `KM_GATE_MANIFEST_BASE=.` 付きで★束の中から★"
            "通した(裁 seq322699・基点=%s)。★最終巡=本行を焼いた後★の出目(`_gate/%s.*`)。"
            % (rc, bogen, icchi, soui, jittai, yomenu, kyuukei, vrc, honsuu, kiten, "%s"))

    p = os.path.join(bundle, "README.md")
    s = open(p, encoding="utf-8").read()
    lines = s.split("\n")
    # ★最終巡の名は引数で受ける★ ―― 器に焼き込むと、巡を一つ足した時に紙が嘘を吐く。
    #   (初版は "81_gate2" を器の中へ書いて居た。焼く事自体が raw/ を一本増やし
    #    臺帳が 38→39 に成る ∴ 焼いた「臺帳 38 行」は焼いた瞬間に古びる。
    #    ∴ 巡は「焼く→建直す→門」を★数が動かなく成る迄★回す要が在る。)
    gyou = gyou % saki
    if lines and lines[0].startswith(YAKI_ATAMA):
        lines[0] = gyou                      # 二度目以降は★置換★(行を増やさぬ)
        nani = "置換(既に焼いて在つた)"
    else:
        lines = [gyou, ""] + lines
        nani = "追加(初めて焼いた)"
    K.kaku(p, "\n".join(lines))

    K.kaku(os.path.join(bundle, "raw", "81_yaki.txt"), "\n".join([
        "焼いた元 = _gate/%s.{rc,out,err} ／ 焼いた先 = README.md の一行目(%s)" % (sechi, nani),
        "指す先   = _gate/%s.*(★最終巡★)" % saki,
        "",
        "焼いた数(悉く門の出目から引いた ―― 手で打つて居らぬ):",
        "  門 rc=%s / 臺帳 %s 行 / 一致 %s / 相違 %s / 実体無 %s / 讀めぬ行 %s"
        % (rc, bogen, icchi, soui, jittai, yomenu),
        "  旧形 %s / manifest_verify.py rc=%s / 條②③④ 全 %s 本 / 基点=%s"
        % (kyuukei, vrc, honsuu, kiten),
        "",
        "★焼かなかつた数と其の理由★:",
        "  ・byte 和 ―― 焼けば紙が太り、太れば和が変はる(★己を含む量は焼けぬ★)。",
        "  ・本束 file の sha ―― 同じ理由。臺帳に任す(kin 逐語「紙に己の sha を書くな」)。",
        "",
        "★此の行が意味せぬ事★: 焼いた数は★門が通つた事★を示すのみで、",
        "  中身が正しい證ではない。門は空白・CR・EOF・寸法・臺帳の差しか見て居らぬ。",
    ]))
    sys.stderr.write("焼 了 %s / rc=%s 臺帳%s行 一致%s 相違%s\n" % (nani, rc, bogen, icchi, soui))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
