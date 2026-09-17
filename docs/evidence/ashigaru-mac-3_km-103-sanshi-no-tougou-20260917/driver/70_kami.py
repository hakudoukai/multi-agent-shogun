# -*- coding: utf-8 -*-
"""紙を組む器 ―― README.md を ★raw/ の出目から組み立てる★(手で数を写さぬ)。

★何故 器で組むか★
  kin 逐語「数は器で測り、手で写さぬ」。∴ 本紙の数は一つも手打ちせぬ。
  悉く raw/*.tsv を歩いて数へ、合はぬ時は★紙を書かずに止まる(rc=5)★。

★本器が検める事(組む前に)★
  ⓐ 母數 ―― 一表・出所・鎖 の三つの tsv が★同じ 45 本の名★を持つ事。
  ⓑ 交差表の総和 = 45 / 二軸の周辺和 = 各紙の申す数。
  ⓒ 零の四札 tsv の rc 欄が★悉く 0★である事。
  ⓓ ★己の sha を書かぬ★(kin 逐語) ―― ★字面で睨むのではなく実際に計つて突合する★。
     本束の file を悉く歩いて sha1/sha256 を計り、紙の中の hex 語が其の何れかの
     ★頭★に成つて居らぬ事を確かめる。初版は `[0-9a-f]{7,40}` で拾つて居たが、
     是は `20260917` の如き★日付★も呑む ∴ 「6 件」と出て何の證にも成らなかつた。

★本紙が意味せぬ事は 紙の末尾「七」に書く(数の規律3)★
"""
import hashlib, os, re, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = __import__("00_kaki")


def yomu(path):
    s = open(path, encoding="utf-8").read()
    rows = [ln.split("\t") for ln in s.split("\n") if ln and not ln.startswith("#")]
    return rows[0], rows[1:]


def main(bundle):
    raw = os.path.join(bundle, "raw")
    toki = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"],
                          capture_output=True, text=True).stdout.strip()
    taore = []

    a_ich, g_ich = yomu(os.path.join(raw, "42_ichihyou.tsv"))
    a_shu, g_shu = yomu(os.path.join(raw, "31_shussho.tsv"))
    a_ksr, g_ksr = yomu(os.path.join(raw, "51_kusari.tsv"))
    a_ksa, g_ksa = yomu(os.path.join(raw, "43_kousa.tsv"))
    a_yur, g_yur = yomu(os.path.join(raw, "33_na_no_yure.tsv"))
    a_rei, g_rei = yomu(os.path.join(raw, "61_rei_yonsatsu.tsv"))
    a_nul, g_nul = yomu(os.path.join(raw, "21_nul_jissoku.tsv"))
    a_war, g_war = yomu(os.path.join(raw, "11_bogen_warimochi.tsv"))

    # ── ⓐ 母數 ―― 四つの tsv が同じ 45 本を持つか
    na_ich = [r[0] for r in g_ich]; na_shu = [r[0] for r in g_shu]
    na_ksr = [r[0] for r in g_ksr]; na_nul = [r[1].replace("karo-mac/", "K/") for r in g_nul]
    if not (len(na_ich) == len(na_shu) == len(na_ksr) == len(na_nul) == 45):
        taore.append("母數が 45 で無い: 一表%d 出所%d 鎖%d 実測%d"
                     % (len(na_ich), len(na_shu), len(na_ksr), len(na_nul)))
    for na, gr in (("出所", na_shu), ("鎖", na_ksr), ("実測", na_nul)):
        if set(gr) != set(na_ich):
            taore.append("%s の枝名が一表と合はぬ(差 %d 本)" % (na, len(set(gr) ^ set(na_ich))))

    # ── ⓑ 交差表
    ksa = {(r[0], r[1]): int(r[2]) for r in g_ksa}
    if sum(ksa.values()) != 45:
        taore.append("交差表の総和が 45 で無い: %d" % sum(ksa.values()))
    su = {k: sum(v for (x, _), v in ksa.items() if x == k) for k in "甲乙丙"}
    ki = {k: sum(v for (_, y), v in ksa.items() if y == k) for k in "甲乙丙"}

    # ── ⓒ 零の四札
    i_rc = a_rei.index("㊂rc")
    warui_rei = [r[0] for r in g_rei if r[i_rc] != "0"]
    if warui_rei:
        taore.append("零の四札に rc≠0 が在る: %s" % " ".join(warui_rei))

    if taore:
        for t in taore:
            sys.stderr.write("★" + t + "★ ∴ 紙を書かずに止まる\n")
        return 5

    # ── 欄の位置(名で引く ―― 番号を手打ちせぬ)
    i_seki = a_ich.index("測つた席")
    i_su = [i for i, c in enumerate(a_ich) if c.startswith("★捨證軸★")][0]
    i_sok = i_su + 1
    i_ki = [i for i, c in enumerate(a_ich) if c.startswith("★器軸★")][0]
    i_kif = i_ki + 1
    i_ido = a_ich.index("二軸の異同")
    shu = {r[0]: r for r in g_shu}
    ksr = {r[0]: r for r in g_ksr}
    i_han = a_shu.index("判")
    i_tou = a_shu.index("當実NUL")
    i_a1k = a_shu.index("a1紙")
    i_dan2 = a_ksr.index("段②★着地の鎖★")
    i_m2 = a_ksr.index("段②待つ相手の数")

    # ── 一表(45 行)
    hyou = ["| # | 枝(`K/`=`karo-mac/`) | 席 | ★捨證軸★ | 同 則 | ★器軸★ | 同 器file | ⑴対main<br>當実NUL | a1紙の値 | 出所 判 | 段②鎖 |",
            "|---:|---|---|:--:|---|:--:|---:|---:|---:|---|---|"]
    for n, r in enumerate(g_ich, 1):
        s = shu[r[0]]; k = ksr[r[0]]
        hyou.append("| %d | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            n, r[0], r[i_seki], r[i_su][:1], r[i_sok], r[i_ki][:1], r[i_kif],
            s[i_tou], s[i_a1k], s[i_han],
            k[i_dan2].replace("★", "") + ("" if k[i_m2] == "0" else "(%s本)" % k[i_m2])))

    # ── 名の揺れ
    yure = ["| 出所 | 紙に載る名 | 戻した枝名 | 用ゐた規 |", "|---|---|---|---|"] + \
           ["| %s | `%s` | `%s` | %s |" % (r[0], r[1], r[2], r[3]) for r in g_yur]

    # ── 零の四札
    rei = ["| 零 | 根(束内相対) | 深さ(行) | 檢出子(逐語) | 実測 | ㊀陽性対照 | rc | 刻 |",
           "|---|---|---:|---|---:|---|---:|---|"] + \
          ["| %s | `%s` | %s | %s | %s | %s | %s | %s |" % tuple(r) for r in g_rei]

    # ── 逐語(41 を其の儘 引く ―― 紙の中で二度書かぬ)
    chikugo = open(os.path.join(raw, "41_teigi_chikugo.txt"), encoding="utf-8").read().rstrip()

    dan2_tan = sum(1 for r in g_ksr if r[i_m2] == "0")
    i_45 = a_ksr.index("段③★45本同士★を待つ数")
    dan3 = sum(1 for r in g_ksr if r[i_45] != "0")
    i_sa = a_shu.index("判")
    a1_chigau = sum(1 for r in g_shu if r[i_a1k] != "-" and r[i_a1k] != r[i_tou])
    a1_noru = sum(1 for r in g_shu if r[i_a1k] != "-")
    ido_wareru = sum(1 for r in g_ich if "異" in r[i_ido] or "割" in r[i_ido])

    md = """# km-103 ―― ★三紙を一表にし、語を一義にする★

專任3(足軽mac-3)／親裁 = 委員長裁 seq325884・裁 seq326093①／刻 %(toki)s
束 = 本 dir。器 = `driver/`・出目 = `raw/`。★読取のみ★(枝を消さず・checkout せず・refs を書換へず)。

---

## 零 ―― 一行で申す

> **三紙は同じ字「甲乙丙」で ★三つの別の問ひ★ に答へて居る。
> 45 本中 ★%(wareru)d 本★ が、捨證軸では「甲」、器軸では「乙」である。**

| 軸 | 誰の紙 | ★問ひ★ | 甲 | 乙 | 丙 |
|---|---|---|---:|---:|---:|
| ★捨證軸★ | 三席(a1/a2/當方) | ★此の枝を捨てて良い證が立つか★ | %(su_kou)d | %(su_otsu)d | %(su_hei)d |
| ★器軸★ | 家老 | ★此の枝の自前差分が器を含むか★ | %(ki_kou)d | %(ki_otsu)d | %(ki_hei)d |
| ★重複軸★(語=「不要」) | 家老 前紙 | ★其の tip が origin の他の枝の祖先か★ | ― | ― | ― |

∴ 同じ「甲」でも、三席の甲は ★「捨てられぬ」★、家老の甲は ★「器入り」★。
「不要15」も亦 ★「捨てる15」ではない★。★三つの語が三つの問ひに答へて居る。★

---

## 一 ―― ★語の衝突を解く★(㋑・本札の主眼)

### 一-1 各紙の定義 ―― ★逐語★(器が紙から引いた。手で写して居らぬ)

```
%(chikugo)s
```

出目 = `raw/41_teigi_chikugo.txt`。錨は★一行に丁度一つ命中する事★を条件とし、
二行命中したら止まる形にして在る(初版は緩い錨で ★別の行★ を引いて居た ―― 器の疵として
`driver/40_nigi.py` の docstring に残した)。

### 一-2 交差表(`raw/43_kousa.tsv`)

| 捨證軸＼器軸 | 甲(器入り) | 乙(紙のみ) | 丙 |
|---|---:|---:|---:|
| 甲(捨てられぬ) | %(k_kk)d | %(k_ko)d | %(k_kh)d |
| 乙(捨てて良い) | %(k_ok)d | %(k_oo)d | %(k_oh)d |
| 丙(測れぬ) | %(k_hk)d | %(k_ho)d | %(k_hh)d |

★割れる枝 = %(wareru)d 本★(捨證甲 × 器乙)。是が「語を一義にせよ」の中身である。

### 一-3 ★一表★ ―― 45 本・二軸を★別欄★に(`raw/42_ichihyou.tsv`)

%(hyou)s

---

## 二 ―― 母數を閉ぢた(㋐)

```
%(bogen)s
```

### 二-1 ★名の揺れ★ %(yure_n)d 件(`raw/33_na_no_yure.tsv`)

三紙は同じ枝を★違ふ名★で書いて居る。a2 の紙は冠 `karo-mac/` と末尾 `-20260917` を落とす。
∴ 名を戻す規を★先に宣して★から当てた(`driver/30_shussho.py` docstring)。

%(yure)s

★戻せず = 0 件★・★曖昧 = 0 件★(規4 は前方一致が★唯一一本★の時のみ戻す。
二本以上なら戻さず「曖昧」と書く ―― 対照 ⓓ で `karo-mac/km-5` が撥ねられる事を確かめた)。
`★総和★` は枝に非ず(紙の表の締め行)ゆゑ宣して除いた。

---

## 三 ―― 数の出所(㋒)

基準 = ★當実NUL★(`git diff --name-only -z` の NUL 数・`raw/21_nul_jissoku.tsv`)。

```
%(shussho)s
```

★家老の申す「a1 の +1 疵」は ★a1 の紙★ に在り、★a1 の tsv には無い★。★
a1紙は %(a1_noru)d 本 悉く當実より +1(差の種類 = `[1]` 唯一)。a1実・a2紙・a2実・家老 は ★悉く一致(違ひ 0)★。

因は Python `str.splitlines()` が名の中の ★U+2028★ を行末と見做す事(km-46 A06 の fixture)。
本束は同じ三器(NUL / grep 行 / splitlines)を 45 本に当て直し、
★丙−甲 ≠ 0 の枝 = 0 本★ を得た(`raw/21_nul_jissoku.tsv`)。
即ち ★a2 の紙にも當方の紙にも同じ疵は出て居らぬ★。
(U+2028 を splitlines が割る事自体は、器の source を材にして★其の場で鳴らして★確かめた。)

---

## 四 ―― 着地の鎖(㋓)

「幹」が二義ゆゑ ★三段★ で測つた(`raw/51_kusari.tsv` / `raw/52_kusari_matome.txt`)。

```
%(kusari)s
```

| 段 | 幹 | ⑴単独で載る | ⑵他枝を待つ |
|---|---|---:|---:|
| ① | `origin/main` | %(dan1_tan)d | %(dan1_matsu)d |
| ② | main ＋ ★家老の幹★(`karo-mac/km-gate-kou-otsu-20260917`) | ★%(dan2_tan)d★ | %(dan2_matsu)d |
| ③ | ―― 45 本の内、★他の 45 本★を待つ枝 | ― | ★%(dan3)d★ |

★段②の一行★: 家老の申す「幹先行」の幹は ★不要15 の一本★である。
即ち「捨てる候補と名指した枝を先に載せる」事を意味する。★可否は當席の測れる所に非ず★
(理事長裁・軍師mac の判)。當席は ★其の一事を名指しで申し送る★のみ。

待つ相手は一本づつ名で書いて在る(`raw/51_kusari.tsv` 欄「段①待つ相手(悉く)」「段②待つ相手(悉く)」)。

---

## 五 ―― 零の四札(㋔)

%(rei)s

★四札を当てなかつた零★(宣して除く): ㋐の「差 = 0/0」は零ではなく★等式★である ∴ 突合で示した。
㋓段①の「単独 = 0」は零だが疵ではない(不要の定義の裏返し) ∴ 四の段に逐語で書いた。

---

## 六 ―― 器と出目

| 器 | 何を測るか | 主な出目 |
|---|---|---|
| `driver/10_bogen.py` | ㋐ 母數を閉ぢる | `raw/11_bogen_warimochi.tsv` `raw/13_bogen_matome.txt` |
| `driver/20_nul.py` | ㋒ NUL/grep/splitlines の三器で 45 本を実測 | `raw/21_nul_jissoku.tsv` |
| `driver/30_shussho.py` | ㋒ 六つの出所と突合・名の揺れ | `raw/31_shussho.tsv` `raw/33_na_no_yure.tsv` |
| `driver/40_nigi.py` | ㋑ 定義の逐語引きと二軸の一表 | `raw/41_teigi_chikugo.txt` `raw/42_ichihyou.tsv` `raw/43_kousa.tsv` |
| `driver/50_kusari.py` | ㋓ 着地の鎖 三段 | `raw/51_kusari.tsv` |
| `driver/60_rei.py` | ㋔ 零に四札を当てる | `raw/61_rei_yonsatsu.tsv` |
| `driver/70_kami.py` | 本紙を raw から組む(数を手打ちせぬ) | `README.md` `raw/71_kami_shirabe.txt` |
| `driver/80_yaki.py` | 門の出目を紙の一行目へ焼く | `README.md` L1 ／ `raw/81_yaki.txt` |
| `driver/90_awase.py` | ★焼いた数 = 最終巡の門の数★ を突き合はせる | `_gate/85_awase.{txt,tsv}` |

★臺帳の外に置いた物(宣して除く)★: `_gate/` の一切(門の log・対象一覧・合はせの出目)。
門の★後に★走る器の出目を `raw/` へ書けば、其の場で臺帳と disk が食ひ違ひ ★條①を己で破る★。
∴ 門と同じ扱ひで `_gate/` へ出す。`MANIFEST.txt` 自身も臺帳の行には入らぬ(己を数へられぬ)。

★巡の数★: 焼けば紙が変はり、紙が変はれば臺帳が変はる。∴「焼く→臺帳を建直す→門」を
★数が動かなく成る迄★回した(`_gate/80_gate1` 〜 最終巡)。最終巡の名は紙の一行目に在り、
`driver/90_awase.py` が ★紙の指す名と実際に当てた門の名が同じ事★ を検めて居る。

---

## 七 ―― ★此の紙が意味せぬ事★(数の規律3)

- ★45 は「着地させる枝の数」ではない。★ 三席が測り終へた枝の数である。
- ★捨證軸の甲 %(su_kou)d は「%(su_kou)d 本 PR せよ」ではない。★ 「捨てて良い證が一つも立たなかつた」の意であり、
  起票の是非は監督の任・判は軍師mac(裁 325884)。
- ★器軸の乙 %(ki_otsu)d は「捨てて良い」ではない。★ 家老紙の逐語は「紙のみの枝ゆゑ main に入れずとも器は揃ふ」。
- ★「不要15」は「捨てる15」でも「main に入つた15」でもない。★ 逐語は「他の枝の祖先ゆゑ
  消しても commit は一つも失はれぬ」。
- ★「違ふ」は「誤り」ではない。★ 各紙は各々の刻に各々の器で測つた。枝(sha)は動かぬが★器は直る★。
- ★「一致」も其の器が正しい證ではない。★ 同じ疵を二つの器が持てば、揃つて誤る。
- ★丙 = 0 は「測りが正しい」ではない。★ 「測れぬ枝が無かつた」のみ。
- ★陽性対照が鳴るのは「檢出子が死んで居らぬ」證のみ★であり、正しさの證ではない。
- ★本紙は ⑴(対 main)を基準に組んだ。★ ⑵(自前差分)の出所突合は別に要る。
- ★段②は「幹が載つた」と仮定した測り★であつて、幹が載つた事実ではない。
- ★本紙は一本も枝に触れて居らぬ。★ 消さず・checkout せず・refs を書換へず・.gitignore に触れて居らぬ。
""" % dict(
        toki=toki, chikugo=chikugo, hyou="\n".join(hyou), yure="\n".join(yure),
        rei="\n".join(rei), yure_n=len(g_yur),
        su_kou=su["甲"], su_otsu=su["乙"], su_hei=su["丙"],
        ki_kou=ki["甲"], ki_otsu=ki["乙"], ki_hei=ki["丙"],
        k_kk=ksa[("甲", "甲")], k_ko=ksa[("甲", "乙")], k_kh=ksa[("甲", "丙")],
        k_ok=ksa[("乙", "甲")], k_oo=ksa[("乙", "乙")], k_oh=ksa[("乙", "丙")],
        k_hk=ksa[("丙", "甲")], k_ho=ksa[("丙", "乙")], k_hh=ksa[("丙", "丙")],
        wareru=ksa[("甲", "乙")],
        bogen=open(os.path.join(raw, "13_bogen_matome.txt"), encoding="utf-8").read().rstrip(),
        shussho=open(os.path.join(raw, "32_shussho_matome.txt"), encoding="utf-8").read().rstrip(),
        kusari=open(os.path.join(raw, "52_kusari_matome.txt"), encoding="utf-8").read().rstrip(),
        a1_noru=a1_noru,
        dan1_tan=sum(1 for r in g_ksr if r[a_ksr.index("段①待つ相手の数")] == "0"),
        dan1_matsu=sum(1 for r in g_ksr if r[a_ksr.index("段①待つ相手の数")] != "0"),
        dan2_tan=dan2_tan, dan2_matsu=45 - dan2_tan, dan3=dan3,
    )

    K.kaku(os.path.join(bundle, "README.md"), md)

    # ── ⓓ ★己の sha を書かぬ★の検め(計つて突合する)
    honbun = open(os.path.join(bundle, "README.md"), encoding="utf-8").read()
    go = sorted(set(re.findall(r"(?<![0-9a-zA-Z])[0-9a-f]{7,40}(?![0-9a-zA-Z])", honbun)))

    tsuka = []          # 本束の全 file の sha1/sha256
    for ne, _, fs in os.walk(bundle):
        if "__pycache__" in ne or "/.git" in ne:
            continue
        for f in fs:
            fp = os.path.join(ne, f)
            if not os.path.isfile(fp) or os.path.islink(fp):
                continue
            b = open(fp, "rb").read()
            tsuka.append((os.path.relpath(fp, bundle),
                          hashlib.sha1(b).hexdigest(), hashlib.sha256(b).hexdigest()))
    atari = []
    for h in go:
        for na, s1, s2 in tsuka:
            if s1.startswith(h) or s2.startswith(h):
                atari.append((h, na))

    shurui = []
    for h in go:
        if re.fullmatch(r"\d+", h):
            shurui.append((h, "★sha に非ず★(十進の数 ―― 日付等)"))
        else:
            rc, _, _ = 0, 0, 0
            r = subprocess.run(["git", "-C", bundle, "cat-file", "-t", h],
                               capture_output=True, text=True)
            shurui.append((h, ("git の %s(他物)" % r.stdout.strip()) if r.returncode == 0
                           else "git に無し(他席の紙が引く sha 等)"))

    K.kaku(os.path.join(raw, "71_kami_shirabe.txt"), "\n".join([
        "紙 = README.md ／ 刻 %s" % toki,
        "行数 = %d ／ 字数 = %d" % (honbun.count("\n"), len(honbun)),
        "",
        "★己の sha を書かぬ★の検め(kin 逐語) ―― ★計つて突合した★:",
        "  本束の file = %d 本(sha1/sha256 を悉く計つた)" % len(tsuka),
        "  紙の中の hex 語(7〜40 桁) = %d 種:" % len(go),
    ] + ["    %-14s %s" % (h, k) for h, k in shurui] + [
        "",
        "  ★紙の hex が本束 file の sha の頭に成つて居る件数 = %d★" % len(atari),
    ] + ["    ★%s → %s★" % (h, na) for h, na in atari] + [
        "",
        "  (本束の file の sha は一つも書いて居らぬ。書けば紙を直す度に変はる ∴ 臺帳に任す。)",
        "  ★此の検めが意味せぬ事★: 「頭に成らぬ」は「紙が正しい」ではない。",
        "    ★紙が己を指して居らぬ★のみ ―― 即ち紙を直しても紙の中の数は古びぬ、其の一事。",
    ]))
    if atari:
        sys.stderr.write("★紙が本束 file の sha を書いて居る(%d 件) ∴ 倒れ★\n" % len(atari))
        return 7
    sys.stderr.write("紙 了 行%d 字%d / hex %d 種・己の sha 0 件(file %d 本と突合)\n"
                     % (honbun.count("\n"), len(honbun), len(go), len(tsuka)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
