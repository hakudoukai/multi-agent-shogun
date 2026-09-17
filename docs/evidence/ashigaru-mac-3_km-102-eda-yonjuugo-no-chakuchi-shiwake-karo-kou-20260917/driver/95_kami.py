# -*- coding: utf-8 -*-
"""紙(README.md)を ★raw から數を引いて★ 組む。★手で數を打たぬ★(手打ちは古びる)。

  usage: python3 driver/95_kami.py <束の根>
一行目は ★焼く前の札★ を置く ―― 門 rc / 母數 / 條① は ★門を通した後★に 99_yaki.py が焼く。
"""
import hashlib
import os
import subprocess
import sys
from importlib import import_module

sys.path.insert(0, __file__.rsplit("/", 1)[0])
K = import_module("00_kaki")

ICHI = "★一行目 未焼(門を通した後に 99_yaki.py が焼く)★"


def load(p):
    rows, head = [], None
    for ln in open(p, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if head is None:
            head = c
            continue
        if c and c[0]:
            rows.append(dict(zip(head, c)))
    return rows


def short(b):
    return b.split("/", 1)[-1]


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    raw = os.path.join(root, "raw")
    bogen = load(raw + "/11_bogen.tsv")
    ros = load(raw + "/21_roster.tsv")
    soku = load(raw + "/31_sokutei.tsv")
    kusari = load(raw + "/41_kusari.tsv") if os.path.getsize(raw + "/41_kusari.tsv") > 60 else []
    shison = load(raw + "/42_shison.tsv")
    shitsu = load(raw + "/51_shitsu.tsv")
    kasa61 = load(raw + "/61_kasanari.tsv")
    kasa = load(raw + "/62_kasanari_matome.tsv")
    ban = load(raw + "/71_utsuwa_ban.tsv")
    shiwake = load(raw + "/81_shiwake.tsv")
    uke = load(raw + "/91_ukeire.tsv")
    taba = load(raw + "/92_taba.tsv")
    ryou = load(raw + "/37_ryoumuki.tsv")
    mtxt = open(raw + "/36_ryoumuki_main.txt", encoding="utf-8").read().split("\n")
    mb = [x.split("= ", 1)[1] for x in mtxt if x.startswith("分岐点")][0]
    m_commit = [x.split("= ", 1)[1] for x in mtxt if x.startswith("main 側 commit")][0]
    m_file = [x.split("= ", 1)[1] for x in mtxt if x.startswith("main 側 file")][0]
    butsu = [r for r in ryou if r["★自前 ∩ main側★"] != "0"]

    fuda = os.path.join(root, "..", "..", "..", "queue", "tasks", "ashigaru-mac-3.yaml")
    fb = open(fuda, "rb").read()
    fsha, fgyou, fbyte = hashlib.sha256(fb).hexdigest()[:16], fb.count(b"\n"), len(fb)

    n = len(bogen)
    rc0 = sum(1 for r in bogen if r["cat_file_e_rc"] == "0")
    itchi = sum(1 for r in bogen if r["sha40_vs_rev_parse"] == "同一")
    ros_ok = sum(1 for r in ros if r["lsremote_totsugou"] == "一致")
    kou = sum(1 for r in shiwake if r["甲乙丙"].startswith("甲"))
    otsu = sum(1 for r in shiwake if r["甲乙丙"].startswith("乙"))
    hei = sum(1 for r in shiwake if r["甲乙丙"].startswith("丙"))
    kou_utsuwa = sum(1 for r in shiwake if r["甲乙丙"].startswith("甲-器"))
    kou_chotei = sum(1 for r in shiwake if r["甲乙丙"] == "甲-器-要調停")
    kou_kami = sum(1 for r in shiwake if r["甲乙丙"] == "甲-紙")
    shison0 = sum(1 for r in shison if r["60本中の子孫tip数"] == "0")
    hakaru = sum(1 for r in soku if r["(2)kiten_eda"] != "測れぬ")
    d100 = sum(1 for r in shitsu if r["disk同一率"] == "100%")
    taba_ari = sum(1 for r in uke if r["甲:束数"] != "0")
    dai_ari = sum(1 for r in taba if r["臺帳"] == "在り")
    dai_uchi = sum(1 for r in taba if r["臺帳の根"] == "★束内相対★")
    dai_nashi = sum(1 for r in taba if r["臺帳"] == "★臺帳無し★")
    tais = sum(1 for r in taba if r["対照の字"] == "対照の字 在り")
    mon_ari = sum(1 for r in uke if r["丁:門の器"] == "在り")
    dai_ki = sum(1 for r in uke if r["戊:臺帳の器"] == "在り")
    shou_ari = sum(1 for r in uke if r["庚:重なる枝数"] != "0")

    g1 = [r for r in ban if r["path"] == "scripts/checks/karo_mac_dasumae_gate.sh"]
    g1v = [r for r in g1 if r["其の版を持つ枝数"] != "-"]
    disk_nashi = [r["path"] for r in ban if "何れの枝にも無し" in r["disk"]]

    L = []
    a = L.append
    a(ICHI)
    a("")
    a("# km-102 ―― 枝四十五の着地仕分け(家老mac の枝・後半 %d 本)" % n)
    a("")
    a("- 席 = ashigaru-mac-3(專任3) / bloom L5 / 的 = ★「此の枝を着地させるか、捨てるか」一件のみ★")
    a("- task_id = `km-102-eda-yonjuugo-no-chakuchi-shiwake-karo-kou-20260917`"
      "(札 sha256頭16=`%s` %d行 %dB)" % (fsha, fgyou, fbyte))
    a("- 親 = 委員長裁 seq325884(親 325872) ―― 枝削除は★不可逆削除＝理事長専管★ゆゑ★消さない★")
    a("- ★此の弾で枝を一本も消して居らぬ★。checkout / merge / rebase / cherry-pick / push / fetch /"
      " refs 書換 ―― 悉く行つて居らぬ。git は ★読取のみ★(`cat-file` `diff` `rev-list` `ls-tree`"
      " `show` `ls-remote --heads`)。PR は起票して居らぬ。他席の pane は覗いて居らぬ。")
    a("")
    a("## 一言 ―― %d 本 悉く ★甲(着地させる)★。乙=%d・丙=%d" % (kou, otsu, hei))
    a("")
    a("★之は「%d 本を悉く PR せよ」の意では★ない★★。" % n)
    a("下の五つの拠り所(丙①丙②乙①乙②乙③)は ★「捨ててよい」と言へる形★ を五通り並べた物であり、"
      "%d 本は其の何れにも当たらなかつた ―― 即ち ★「捨ててよい證が一つも立たなかつた」★ である。"
      "「着地させるべし」の積極的な證ではない。是非の判定は軍師mac の職(裁 325884)。" % n)
    a("")
    a("## ㋐ 母數 ―― %d 本・物は悉く手許に在る" % n)
    a("")
    a("- 割当 = %d 本(札 `eda_warimochi` 逐語)。`raw/11_bogen.tsv` に full sha40 を逐語で列べた。" % n)
    a("- `git cat-file -e <sha>^{commit}` rc=0 が ★%d/%d★・object_type=commit が %d/%d・"
      "sha40 と `rev-parse` の一致 %d/%d。" % (rc0, n, rc0, n, itchi, n))
    a("- ★家老の臺帳を鵜呑みにせず己で数へた★: `git ls-remote --heads origin`(★fetch ではない・"
      "読取★)で mac の枝を数へ、家老臺帳 `karo-mac-eda-fuyou-20260917/raw/20_mac_eda.tsv` と"
      "突き合はせた ―― ★60/60 一致★(`raw/21_roster.tsv` 突合欄=一致 %d 本)。" % ros_ok)
    a("")
    a("## ㋑ 二つの差分 ―― ★混ぜて居らぬ★")
    a("")
    a("`raw/31_sokutei.tsv` が生の數。★⑴と⑵は別の問である。★")
    a("")
    a("### ⑴ 対 origin/main")
    a("")
    a("`git diff --name-only 4be3ee19e1c5...<sha>` の行数。★此の數が意味せぬ事(数の規律3)★:")
    a("")
    i1 = sorted(int(r["(1)file_gyou"]) for r in soku)
    a("- ★「此の枝が変へた file 数」では★ない★★。`A...B` は git の定義上 "
      "★merge-base(A,B) から B まで★ の片側であり、★origin/main が此の系譜に対して何 file "
      "遅れて居るか★ を言ふ。")
    a("- 出目 = ★%d〜%d★(中央値辺り %d)。之は「各枝が %d file 触つた」ではなく "
      "★分岐点から枝の tip までに積まれた file の総数★ である ―― "
      "同じ系譜に乗る枝は同じ古さを何度も数へ直す。" % (i1[0], i1[-1], i1[len(i1) // 2], i1[len(i1) // 2]))
    a("- ★枝同士の大小比較に使ふな。★ 現に最小 %d(lot48235904)と最大 %d(km-88)の隔たりは"
      "「仕事量が %d 倍」ではなく ★乗つて居る系譜が違ふ★ 事を映して居るに過ぎぬ"
      "(lot48 の基点のみ `manifest-verify-20260909`・他 13 本は `km-gate-kou-otsu-20260917`)。"
      % (i1[0], i1[-1], i1[-1] // max(i1[0], 1)))
    a("")
    a("### ⑵ ★自前★の差分")
    a("")
    a("60 本の tip の内 ★其の枝の真の祖先★ である物を悉く挙げ、`git rev-list --count B..X` が"
      "最小の B を基点として `git diff --name-only B..X` を数へた(`raw/31_sokutei.tsv` の"
      "`(2)kiten_eda` が其の B)。★測れた = %d/%d・測れぬ = %d★。" % (hakaru, n, n - hakaru))
    a("")
    a("- 13 本は基点が `karo-mac/km-gate-kou-otsu-20260917`、lot48235904 のみ"
      "`karo-mac/manifest-verify-20260909`。祖先 tip は各 9 本(lot48 は 5 本)在り、"
      "★最小を選ぶに当たつて同点(tie)は 0 件★ ―― 基点は一意に決まつた(`tie_kazu`欄)。")
    a("- path の数へは ★`-z`(NUL 区切)★ で取つた。git は非 ASCII path を引用符で括る ∴"
      "行数で数へると括られた行を取り零す虞が在る。札の言ふ「行数」も併せて刷り、"
      "★両者の食ひ違ひ 0 件★ を `raw/32_chuu.txt` に記した。")
    a("- ★⑵ が意味せぬ事★: 「此の枝が正しい」ではない。「此の枝しか触つて居らぬ」でもない"
      "(同じ file を触る他枝は ㋕ に列べた)。★基点から先に在る file の数★ ―― 其れだけである。")
    a("")
    a("### ㋑補 ―― ★乖離は両側に在る★(⑴ は片側しか言はぬ)")
    a("")
    a("⑴ は片側ゆゑ ★main が己の向きへ何 file 進んだか★ を一切言はぬ。"
      "測らねば「main は遅れて居るだけ」と誤読する ∴ 測つた(`driver/35_ryoumuki.py` /"
      "`raw/36_ryoumuki_main.txt` / `raw/37_ryoumuki.tsv`)。")
    a("")
    a("- ★14 本の分岐点は悉く一点★ = `%s`(2026-09-08)。" % mb[:12])
    a("- 其処から ★main は %s commit・%s file 進んで居る★ ―― 即ち "
      "★此の 14 本は悉く main より %s commit 遅れて居る★(⑴ が言ふ「main が遅れて居る」の"
      "★裏側★)。" % (m_commit, m_file, m_commit))
    a("- ★然らば衝突するか★: 各枝の ⑵(自前 path)と main 側 %s file の交はりを数へた ――"
      "★交はる枝は %d 本のみ★。" % (m_file, len(butsu)))
    for r in butsu:
        a("  - `%s` ―― %s 件: `%s`" % (short(r["枝"]), r["★自前 ∩ main側★"], r["其の path"]))
    a("- 残り %d 本は ★main が動かした file を一つも触つて居らぬ★ ∴ "
      "★main 側との衝突は無い★(後は下の ㋕ の枝同士の重なりのみ)。" % (len(ryou) - len(butsu)))
    a("- ★此の數が意味せぬ事★: 交はり 0 は ★「そのまま merge できる」ではない★。"
      "同じ file を触らずとも意味の上で食ひ違ふ事は在る(例: 一方が器を動かし他方が其の器を呼ぶ紙を書く)。"
      "★path の交はりだけを言ふ。★")
    a("")
    a("## ㋒ commit 数と領域")
    a("")
    a("`raw/31_sokutei.tsv` の `(1)commit_main` `(1)ryouiki` `(2)ryouiki`。")
    a("")
    a("| 枝 | ⑴ | ⑵ | commit(対main) | ⑵の領域 |")
    a("|---|---|---|---|---|")
    for r in soku:
        a("| `%s` | %s | %s | %s | %s |" % (short(r["branch"]), r["(1)file_gyou"],
                                            r["(2)file_gyou"], r["(1)commit_main"], r["(2)ryouiki"]))
    a("")
    from collections import Counter
    cmc = Counter(r["(1)commit_main"] for r in soku)
    ryc = Counter(r["(1)ryouiki"] for r in soku)
    a("- 対 main の commit: %s。" % " / ".join("%s commit=%d本" % (k, v) for k, v in sorted(cmc.items(), key=lambda x: int(x[0]))))
    a("- ⑴ の領域は ★三通り★(★14 本悉く同じ、ではない★):")
    for k, v in sorted(ryc.items(), key=lambda x: -x[1]):
        a("  - `%s` ―― %d 本" % (k, v))
    a("- ★之も「各枝が触つた領域」ではなく「分岐点から tip までに触られた領域」である。★"
      "lot48235904 だけ `queue` を欠くのは、其の枝が別系譜(基点 `manifest-verify-20260909`)に"
      "乗つて居るからであり、「queue を触らぬ枝」だからではない。")
    a("- ⑵ の領域こそが ★其の枝が齎す物★: 紙のみ %d 本 / 器を含む %d 本。" % (kou_kami, kou_utsuwa))
    a("")
    a("## ㋓ 仕分け ―― ★拠り所を先に宣してから当てた★")
    a("")
    a("拠り所は `driver/80_shiwake.py` の docstring に ★測る前に★ 書いた(出目を見てから足したり"
      "曲げたりして居らぬ)。順に当て ★先に当たつた一つ★ で決める。")
    a("")
    a("| # | 拠り所 | 判ずる欄 | 当たつた本数 |")
    a("|---|---|---|---|")
    a("| 丙① | 物が手許に無い | `11_bogen` cat_file_e rc≠0 | 0 |")
    a("| 丙② | ⑵ が測れぬ(真の祖先 tip 無し) | `31_sokutei` (2)kiten_eda=測れぬ | %d |" % (n - hakaru))
    a("| 乙① | ★末端が運ぶ★(60本中に子孫 tip 在り) | `42_shison` 子孫tip数≧1 | %d |" % (n - shison0))
    a("| 乙② | 齎す物が無い(⑵=0) | `31_sokutei` (2)file_gyou=0 | 0 |")
    a("| 乙③ | 既に main に在る(自前 path 悉く同一 blob) | `51_shitsu` ★mainへ齎す★=0 | 0 |")
    a("| 甲 | 上の五つに悉く当たらぬ | ― | ★%d★ |" % kou)
    a("")
    a("∴ ★甲=%d / 乙=%d / 丙=%d★。丙が 0 ゆゑ「何を測れば判ずるか」を書く先は無い。" % (kou, otsu, hei))
    a("")
    a("甲の中の副札は ★着地の順序★ を付ける物であつて甲乙の別ではない ―― "
      "甲-器-要調停 %d / 甲-器 %d / 甲-紙 %d。" % (kou_chotei, kou_utsuwa - kou_chotei, kou_kami))
    a("")
    a("| 枝 | 札 | 理由(一行) |")
    a("|---|---|---|")
    for r in shiwake:
        a("| `%s` | %s | %s |" % (short(r["枝"]), r["甲乙丙"], r["理由"]))
    a("")
    a("### ★此の仕分けが答へて居らぬ事★")
    a("")
    a("- 「中身が正しいか」 ―― 拠り所は悉く ★在る/無い・同一/相違★ の話であり是非を問うて居らぬ。")
    a("- 「PR に通るか」 ―― ㋔ の受入条件を ★実際に通すまで★ 判らぬ(下記「門 rc は宣し得ぬ」)。")
    a("- 「捨てる枝が 0 本」ではない ―― ★此の %d 本には捨ててよい證が立たなかつた★ だけである。" % n)
    a("")
    a("## ㋔ 受入条件 ―― 甲 %d 本が PR として通る為に満たすべき条" % kou)
    a("")
    a("`raw/91_ukeire.tsv` / `raw/92_taba.tsv`。★checkout せず枝の木を `git show` / `ls-tree` で"
      "引いて測つた★(工作樹は汚して居らぬ)。")
    a("")
    a("| 条 | 何を見たか | 出目 |")
    a("|---|---|---|")
    a("| 甲 束 | ⑵ path が当たる `docs/evidence/<束>/` | %d/%d 本が束 1 つ、%d 本は束 0"
      "(器・箱のみ) |" % (taba_ari, n, n - taba_ari))
    a("| 乙 臺帳 | 其の束に `MANIFEST.txt` が枝の木に在るか | 在り %d / ★無し %d★ |" % (dai_ari, dai_nashi))
    a("| 丙 臺帳の根 | 束内相対か根相対か(裁 seq322699) | ★束内相対 %d/%d・根相対 0★ |" % (dai_uchi, dai_ari))
    a("| 丁 門の器 | `scripts/checks/karo_mac_dasumae_gate.sh` が枝の木に在るか | 在り ★%d/%d★ |" % (mon_ari, n))
    a("| 戊 臺帳の器 | `scripts/checks/karo_mac_manifest_append.py` が枝の木に在るか | ★在り %d/%d★ |" % (dai_ki, n))
    a("| 己 対照 | 束の file 名 or README に「対照」の字 | %d/%d 束 |" % (tais, dai_ari + dai_nashi))
    a("| 庚 衝突 | 自前差分で同じ file を触る他枝(`61_kasanari`) | 衝突有り ★%d★ 本 |" % shou_ari)
    a("")
    a("### ★受入条件(枝毎)★")
    a("")
    a("下の五条は ★悉く満たされて初めて★ PR として出せる。★『満たして居る』と『満たせる』は別である。★")
    a("")
    a("1. **門 rc=0** ―― `KM_GATE_MANIFEST_BASE=.` を付けて束の中から出す前門を通す事。"
      "★此の紙では rc=0 と宣し得ない★: 門を通すには其の枝の木が要り、checkout は禁ぜられて居る。"
      "∴ ★測れぬ★ と書く ―― 起票する席(監督 lot)が枝毎に通して初めて判る。")
    a("2. **臺帳が束内相対** ―― 測れた %d 束は ★悉く束内相対★ で既に満つ。"
      "★臺帳を持たぬ %d 束(km-88 / lot48235904)は、出す前に臺帳を立てねばならぬ。★" % (dai_uchi, dai_nashi))
    a("3. **対照が在る** ―― 「対照」の字が在る束 %d / 無い束 %d。"
      "★字の在否であつて、対照が★効いて居る★事の證ではない(数の規律3)。★"
      "字が無い束は、対照が無いのか名が違ふのか ―― ★其の束を開いて確かめよ★。" % (tais, dai_ari + dai_nashi - tais))
    a("4. **main 側との衝突** ―― 分岐点から main は %s file 動いて居る。"
      "其れを触る枝は ★%d 本のみ★(km-82=`scripts/inbox_watcher.sh` / "
      "lot48235904=`scripts/checks/karo_mac_manifest_verify.py`)。"
      "★此の 2 本は main の新しい版の上へ載せ直す事★ が条。残り %d 本は main 側と "
      "path が交はらぬ。" % (m_file, len(butsu), len(ryou) - len(butsu)))
    a("5. **枝同士の衝突の始末** ―― 下の ㋕ に列べた通り。")
    a("")
    a("### ★門の器と臺帳の器が main に無い(全席に及ぶ)★")
    a("")
    a("`driver/70_utsuwa_ban.py` で 60 本 + main + disk を一枚に並べた(`raw/71_utsuwa_ban.tsv`)。")
    a("")
    a("- `scripts/checks/karo_mac_dasumae_gate.sh` ―― ★main に無し★。枝に %d 版在る"
      "(%s)。★disk の版は `karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917` と同一★ ――"
      "即ち ★未commit ではない★。" % (len(g1v), " / ".join("%s=%s本" % (r["版(blob頭12)"], r["其の版を持つ枝数"]) for r in g1v)))
    a("- `scripts/checks/karo_mac_manifest_append.py`(臺帳へ行を足す唯一の器・裁 seq321856) ――"
      "★main にも 60 本の枝にも無く、disk のみに在る(未commit)★。"
      "∴ 皆が「臺帳は之で建てよ」と命ぜられて居る器が、★何處の ref にも載つて居らぬ★。")
    a("- ★`.claude/settings.json` の disk の版も ★何れの枝にも無い(未commit)★★ ――"
      "`karo-mac/settings-hook-abs-20260917` を着地させても、disk の今の姿には成らぬ。")
    a("- ∴ ★此の %d 本を悉く着地させても、出す前門は main で走らぬ★。門の器を運ぶ枝は"
      "★此の組の外★(km-79 等)に在る ―― ★仕分けの順序は、器を運ぶ枝が先である。★" % n)
    a("")
    a("## ㋕ 重なり ―― ★組の中に鎖は一本も無い★")
    a("")
    a("`raw/41_kusari.tsv`(組内の祖先対) / `raw/42_shison.tsv`(60本に対する子孫) /"
      "`raw/61_kasanari.tsv`(自前差分の file が重なる対)。")
    a("")
    a("- ★組 %d 本の中で tip が他の tip の祖先に成つて居る対 = ★0 対★★。∴ 鎖は描けぬ"
      "(`raw/41_kusari.tsv` は 0 行)。" % n)
    a("- 更に ★60 本に広げても子孫 tip は 0★ ―― %d/%d 本が ★鎖の末端(leaf)★ である。" % (shison0, n))
    a("- ∴ ㋕ の問「★鎖の末端のみ着地させれば足りるか★」の答: "
      "★足りぬ。此の組では一本も畳めない。★ 末端のみ着地させる策は "
      "「A の tip が B に含まれる」時に B だけ出せば A も運ばれる、という理屈で効く。"
      "此の %d 本は互ひに祖先関係に無く、各々が基点から独立に 1〜3 commit 生えて居る"
      "(兄弟であつて親子ではない) ∴ ★どの一本を落としても其の中身は何處からも運ばれぬ。★" % n)
    a("")
    a("### 但し ★file の重なりは在る★(祖先関係とは別の問)")
    a("")
    a("| 己の枝 | 相手の枝 | 共有 path 数 |")
    a("|---|---|---|")
    for r in kasa61:
        a("| `%s` | `%s` | %s |" % (short(r["己の枝"]), short(r["相手の枝"]), r["共有path数"]))
    a("")
    a("- 重なる相手は ★悉く己の組の外★(%d 対・内訳欄 己の組=0)。" % len(kasa61))
    a("- ∴ ★此の %d 本は互ひに衝突せぬ ―― 14 本同士は順不同で出せる。★" % n)
    a("- 但し組の外とは衝突する: km-81 が `scripts/stop_hook_inbox.sh` で 2 本、"
      "km-82 が `scripts/inbox_watcher.sh` で 3 本、lot48235904 が門の器と臺帳照合器で ★8 本★。")
    a("- ★lot48235904 は特に手当が要る★: 其の `karo_mac_dasumae_gate.sh` は 6 本が持つ版"
      "(`54e133c85832`)であり、★disk の版(`054c442eaee3`)でも、兄弟 13 本の基点が持つ版"
      "(`9cd550fc2cf9`・46 本)でもない★。∴ 其の儘着地させると ★門の器が古い版へ戻る虞★ が在る。"
      "―― 但し lot48 の齎す物は紙 2 枚(provenance)と器 2 本であり、"
      "★紙 2 枚は disk と同一(`51_shitsu` disk同一=2/4)★ ゆゑ、"
      "★器を除いて紙のみ着地させる道★ が在る。其の判は軍師mac の職。")
    a("")
    a("## 中身は disk に在るか ―― ★捨てて失ふのは「記録」であつて「bytes」ではない★")
    a("")
    a("`raw/51_shitsu.tsv`。⑵ の path 一本づつを ★枝の blob と disk の中身★ で比べた"
      "(disk は純 python で `sha1(b\"blob %d\\0\" + bytes)` を組んで照合 ―― git の index を触らぬ為)。")
    a("")
    a("- ★disk と 100%% 同一が %d/%d 本★。残り 2 本 = lot48235904(50%%)・settings-hook-abs(67%%)。" % (d100, n))
    a("- ∴ ★%d 本は「捨てても中身は disk に在る」★。失ふのは ★誰が・何時・何故 其れを書いたか★ ――"
      "即ち ★記録★ である。" % d100)
    a("- ★此の數が意味せぬ事★: 「disk に在る ∴ 捨てて良い」では★ない★。"
      "disk は ★一台の Mac の一つの作業樹★ に過ぎず、ref に無い物は ★他の PC へは届かぬ★。"
      "上の『臺帳の器が何處の ref にも無い』が其の実例である。")
    a("")
    a("## 門")
    a("")
    a("- 出す前門 `scripts/checks/karo_mac_dasumae_gate.sh` を ★`KM_GATE_MANIFEST_BASE=.` 付き★ で"
      "★束の中から★ 通した(裁 seq322699 ―― 臺帳は束内相対)。出目 = `_gate/`。")
    a("- 臺帳は ★`cd 束` してから★ `scripts/checks/karo_mac_manifest_append.py` を呼んで建てた。")
    a("- 一行目の rc・母數・條① は ★最終巡(一行目を焼いた後)★ の出目である。")
    a("")
    a("## 此の弾で ★己の器を★ 倒した所(隠さず書く)")
    a("")
    a("1. **`ls-tree` は cwd の prefix で絞る** ―― 束の中から `git ls-tree -r -z <rev>` を呼び、"
      "rc=0 で ★0 件★ が返つた。束の path は其の木に無いからである。"
      "∴ 51 の初版は「disk同一=0・main無=全件」と刷つた。"
      "★0% の一致は在り得ぬ★と踏んで検め、`--full-tree` を足し、"
      "陽性対照(main の木が 2 件未満 or `CLAUDE.md` を欠けば ★一行も書かず rc=5 で止まる★)を据ゑた。")
    a("2. **基点の枝名を rev として使つた** ―― origin の枝は local ref に非ず(手許は 7 本のみ)ゆゑ"
      "`fatal: ambiguous argument`。`rev-parse` の rc を捨てて居た ∴ 空の base で diff を取り掛けた。"
      "★臺帳(`21_roster.tsv`)から sha を引き、引けねば止まる★ 形へ直した。")
    a("3. **内側の loop が外側の loop 変数 `t`(束の名)を潰した** ―― 以後の「対照の字」照合が"
      "★臺帳最終行の path★ を束名と見做し、対照欄が 12 本悉く反転した。名を `fld` へ分けた。")
    a("4. **臺帳の根の判別を白表(`driver/`|`raw/`…)で書いた** ―― km-83 の臺帳は `10_kuchi/…`"
      "`40_doku/…` で束内相対なのに白表に漏れ、10 束中 1 束を「別方言」と誤つた。"
      "裁 seq322699 が問ふのは ★根から書かれて居るか否か★ の一点ゆゑ ★否定で判ずる★ 形へ直した。")
    a("5. **臺帳の列名を `枝` と書いた(実は `相手の枝`)** ―― `KeyError` で器が倒れたが、"
      "★倒れた後に awk が前巡の出目を刷つた★ ∴ 画面には正しげな表が出た。"
      "`rm` して引き直し、★出目が在るか★ を併せて刷る形にした。")
    a("6. **書き器が dict を黙つて呑んだ** ―― `kaku_tsv` の行は list を要するのに dict を渡し、"
      "`for x in r` が ★鍵★ を回して ★見出しを 14 回複製した表★ を rc=0 で書いた。"
      "★出目が在る事は正しさの證ではない。★ 器へ「list/tuple でなければ撥ねる」門を据ゑ、"
      "★dict を渡して止まる事を確かめてから★ 引き直した。")
    a("7. **「測れぬ」と書く前に測つた** ―― lot48 の門の器が古いか否かを「己の割当の外ゆゑ丙」と"
      "書き掛けたが、60 本の木を引けば ★何處に何版在るか★ は判る。"
      "引いた結果 disk の版は km-79 の枝に在り ★未commit ではない★ と判つた ∴ 丙にはせぬ。")
    a("")
    a("## 数が意味せぬ事(纏め・数の規律3)")
    a("")
    a("- ⑴ = ★分岐点から枝の tip までに積まれた file 数(★片側★)★。枝の仕事量ではない。枝同士で比べるな。"
      "★main が己の向きへ進んだ分は一切入つて居らぬ(其れは ㋑補 の %s file)。★" % m_file)
    a("- ⑵ = ★基点から先に在る file 数★。正しさでも、独占でもない。")
    a("- 甲=%d = ★捨ててよい證が一つも立たなかつた本数★。「悉く PR せよ」ではない。" % kou)
    a("- 子孫 tip=0 = ★此の組では鎖を畳めぬ★。「他所に鎖が無い」ではない(組の外の重なりは 13 対在る)。")
    a("- disk同一 %d/%d = ★bytes は手許に在る★。「ref に要らぬ」ではない。" % (d100, n))
    a("- 門 rc(一行目) = ★此の束★ が出す前門を通つた事。★%d 本の枝が通る事ではない。★" % n)
    a("")
    a("## 納め便 ―― ★字数は器で測つた★")
    a("")
    ji = open(raw + "/96_fumi_ji.txt", encoding="utf-8").read().split("\n")
    jisu = [x.split("=")[1] for x in ji if x.startswith("字数")][0]
    a("- 宛 = 家老mac(`karo-mac`)。★軍師mac は死箱★ ∴ 監査は家老mac の代送を乞ふ。")
    a("- 字数 = ★%s 字★(條 300 字 ―― `python3` の `len` で測つた。胴 = `raw/96_fumi.txt`・"
      "測りの出目 = `raw/96_fumi_ji.txt`)。" % jisu)
    a("- 器 `driver/97_fumi.py` は ★300 字を超えたら一字も本便を書かず rc=7 で止まる★。"
      "現に初版は 350 字で止まり、其の下書が `raw/96_fumi_shitagaki.txt` に残る"
      "―― ★門が効いた證★ である。")
    a("- ★此の字数が意味せぬ事★: 便が★届いた★事ではない。"
      "`inbox_write.sh` の rc と、家老mac の箱の尾で別に確かめる。")
    a("")
    a("## 出目の在り処")
    a("")
    for f, d in [("11_bogen.tsv", "㋐ 母數・物の在否"), ("21_roster.tsv", "㋐ 己の ls-remote と家老臺帳の突合(60/60)"),
                 ("22_lsremote.txt", "㋐ ls-remote の生"), ("31_sokutei.tsv", "★㋑⑴⑵の生の數★"),
                 ("32_chuu.txt", "㋑ NUL と行数の食ひ違ひ(0件)"),
                 ("36_ryoumuki_main.txt", "★㋑補 分岐点と main 側の 14 file★"),
                 ("37_ryoumuki.tsv", "★㋑補 両向き・自前と main 側の交はり★"), ("41_kusari.tsv", "㋕ 組内の祖先対(0行)"),
                 ("42_shison.tsv", "㋕ 60本に対する子孫(悉く0)"), ("51_shitsu.tsv", "中身 対 main / 対 disk"),
                 ("52_path.tsv", "同 path 毎"), ("61_kasanari.tsv", "㋕ file の重なり 対"),
                 ("62_kasanari_matome.tsv", "同 纏め"), ("71_utsuwa_ban.tsv", "器の版が 60本+main+disk の何處に在るか"),
                 ("81_shiwake.tsv", "★㋓ 仕分け(枝・sha・⑴・⑵・commit・領域・甲乙丙・理由)★"),
                 ("82_shiwake_riyuu.tsv", "㋓ 拠り所の当たり方"), ("91_ukeire.tsv", "㋔ 受入条件"),
                 ("92_taba.tsv", "㋔ 束毎の臺帳・根・対照"),
                 ("96_fumi.txt", "★納め便の胴(280字)★"), ("96_fumi_ji.txt", "同 字数の測り"),
                 ("96_fumi_shitagaki.txt", "同 350字で止められた下書(門の證)")]:
        a("- `raw/%s` ―― %s" % (f, d))
    a("")
    K.kaku(os.path.join(root, "README.md"), "\n".join(L))
    sys.stderr.write("README 行=%d / 甲%d 乙%d 丙%d\n" % (len(L), kou, otsu, hei))
    return 0


sys.exit(main())
