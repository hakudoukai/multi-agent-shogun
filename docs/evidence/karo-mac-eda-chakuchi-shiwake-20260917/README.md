# 残45本の着地仕分け ―― 委員長裁 seq325884(親 325872)への答

★枝は一本も消して居らぬ。触れて居らぬ。checkout も merge も push も fetch も行つて居らぬ。★
本束は ★読取のみ★ で作つた。裁の逐語「枝削除は不可逆削除＝理事長専管(破壊7線)」に従ふ。

## 一 数

| 事 | 数 | 測り方 |
|---|---|---|
| origin の mac 枝 | 60 | 前束 `karo-mac-eda-fuyou-20260917/raw/20_mac_eda.tsv` |
| 不要(前裁で名指し・★触れず★) | 15 | 同 `raw/40_fuyou.tsv`(臺帳 17d7dbf7) |
| 本紙が仕分けた残 | 45 | 60 − 15 |
| ★甲 着地させる(PR)★ | ★10★ | 自前差分に ★器★ の変更を含む枝 |
| ★乙 捨てる(理事長裁を待つ)★ | ★35★ | 自前差分が ★紙★ のみの枝 |
| 丙 測れぬ | 0 | 手許に物の無い枝 0(cat-file rc 全 0)・祖先 tip の無い枝 0 |
| 残45本の内、鎖(tip が他の tip の祖先)に在る対 | ★0★ | 45 本は悉く互ひに独立の葉 |

## 二 定義 ―― 先に宣する(數が何を意味せぬかを併せ書く)

★定義⑴ 「対 main 差分 file 数」★ = `git diff --name-only 4be3ee19e1c5...<sha>` の行数。
**★此れは「其の枝が変へた file 数」では★ない★。★origin/main が何 file 遅れて居るか★である。★**
最大 1167 / 最小 5。1167 の枝が 1167 file を書いた訳ではない ―― 幹(下記五)が 464 file 分 先に在る。

★定義⑵ 「自前差分 file 数」★ = 60 本の tip の内、其の枝の★真の祖先★である tip を悉く挙げ、
`git rev-list --count B..X` が最小の B を選び `git diff --name-only B..X` を数へた物。
= 「直前の着地点から此の枝が足した分」。最大 703 / 最小 1。

★定義⑶ 「器」と「紙」★ ―― 仕分けの軸である。逐語:
- ★器★ = `scripts/` `.claude/` `.github/` `config/` `instructions/` `agents/` `skills/` の下、及び repo 直下の file。
  **動きに効く。** 落ちれば system の振舞が変る。
- ★紙★ = `docs/` と `queue/` の下(証拠束・札・報)。**消えても system の振舞は変らぬ。**

★定義⑷ 「不要」と「捨てる」は★別物★である。★
前裁の「不要15本」は ★tip が他枝の祖先ゆゑ枝名を消しても commit は失はれぬ★ の意であり、
「main に要らぬ」の意ではない。現に幹(五)は不要15の一であり、★着地の土台★である。
本紙の「乙=捨てる」は ★紙のみの枝ゆゑ main に入れずとも器は揃ふ★ の意であり、
**★枝を消せ、の意では断じてない(消すのは理事長専管)。★**

## 三 甲 ―― 着地候補 10本(枝・sha・差分・器・受入条件)

| # | 枝 | sha(12) | 対main file | 自前 file | 器 | commit | 器の名 | vs 幹 |
|---|---|---|---|---|---|---|---|---|
| 1 | karo-mac/settings-hook-abs-20260917 | `1da2b6b9fb7f` | 467 | 3 | 3 | 18 | `.claude/settings.json` / `scripts/goal_stop_hook.py` / `scripts/goal_stopfailure_hook.py` | 異・幹に無×2 |
| 2 | ashigaru-mac-3/km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917 | `eb6cf51de16f` | 465 | 1 | 1 | 17 | `scripts/stop_hook_inbox.sh` | 幹と異 |
| 3 | karo-mac/km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917 | `f82297e292c8` | 486 | 22 | 1 | 17 | `scripts/stop_hook_inbox.sh` | 幹と異 |
| 4 | karo-mac/km-82-hata-ni-wa-hata-no-bannin-wo-20260917 | `1cbc4d4a2da5` | 500 | 36 | 1 | 18 | `scripts/inbox_watcher.sh` | 幹と異 |
| 5 | karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917 | `157a9736fd17` | 484 | 22 | 2 | 17 | `scripts/checks/karo_mac_dasumae_gate.sh` / `karo_mac_gate4.sh` | 幹と異×2 |
| 6 | ashigaru-mac-1/km-92-sengen-shita-shikii-ga-ichido-mo-yomarenu-koto-wo-shimese-20260917 | `0260a76a6008` | 733 | 269 | 1 | 18 | `scripts/lib/detect_stale.sh` | 幹と異 |
| 7 | karo-mac/hantei-saiteishutsu-20260917 | `0138ae57c377` | 121 | 84 | 1 | 9 | `scripts/checks/karo_mac_manifest_verify.py` | 幹と異 |
| 8 | karo-mac/a1-r56 | `86ae87367c59` | 635 | 633 | 2 | 11 | `karo_mac_dasumae_gate.sh`(幹と異) / `karo_mac_manifest_verify.py`(★幹と同★) | 一部既在 |
| 9 | karo-mac/daiko-teishutsu-20260916 | `5a12887f953d` | 5 | 3 | 2 | 7 | 同上 | 一部既在 |
| 10 | karo-mac/lot48235904-provenance-20260916 | `a9a6ae34557f` | 6 | 4 | 2 | 7 | 同上 | 一部既在 |

### 受入条件(甲 共通)
- ㋐ ★幹(五)が先に着地して居る事★。幹の 464 file が無いと 1〜6 の PR は 400〜700 file の巨塊に見える。
- ㋑ 出す前門 rc=0 ―― `KM_GATE_MANIFEST_BASE=.`(束内相対・裁 seq322699)を付けて通した控が在る事。
- ㋒ 器の重なり(六)が解けて居る事 ―― 同じ器 file を触る枝は★着地の順★を決めねば後の枝が前の枝を巻き戻す。
- ㋓ 判定は★軍師mac★、起票は★監督 lot★(裁 325884 の逐語)。當席は commit までで止まり push は総監督の代行が正路。

### 受入条件(個別)
- ★#1 settings-hook-abs★: 既に push 代行済(seq325775 `origin/karo-mac/settings-hook-abs-20260917=1da2b6b9`)・★本件閉じ★の裁が下つて居る。∴ PR は起票のみで足り、器 3 本の内 2 本(`goal_stop_hook.py` `goal_stopfailure_hook.py`)は ★main にも幹にも無い新規 file★。新規ゆゑ衝突無し。
- ★#2 と #3 は同じ `scripts/stop_hook_inbox.sh` を触る★。両者を別 PR にするなら順を決めよ。
- ★#8/#9/#10 の `karo_mac_manifest_verify.py` は ★幹と同★ ―― ★持ち込む物が無い★。此の 3 本の PR は `karo_mac_dasumae_gate.sh` 一本のみが実体である。
- ★#5 の `karo_mac_gate4.sh` と `karo_mac_dasumae_gate.sh` は ★origin/main に存在せぬ(rc=128)★・幹に在り。∴ 幹の着地で新規に入る。

## 四 乙 ―― 捨てる(理事長裁を待つ) 35本

★自前差分が `docs/` `queue/` の紙のみ★の枝。器は一本も触らぬ ∴ 着地せずとも system の振舞は変らぬ。
**★併し「消せ」ではない。枝の存廃は理事長専管である。★**
全 35 本の名と sha は `raw/10_sokutei.tsv` の `jizen_kigu_files=0` の行に在る(逐語)。主な物:

`karo-mac/km-88-a3-20260917`(1167/703) `ashigaru-mac-1/km-86-…-20260917`(1101/637)
`karo-mac/km-89-a2-20260917`(904/440) `karo-mac/km-83-…-20260917`(846/382)
`ashigaru-mac-1/km-70-…` `ashigaru-mac-1/km-71-…` `ashigaru-mac-1/km-71b-…` `ashigaru-mac-1/km-72-…`
`ashigaru-mac-1/a1-jishu-kuumoji-kiten-20260917`
`ashigaru-mac-2/km-51-…` `km-52-…` `km-53-…` `km-53b-…` `km-87-…`
`ashigaru-mac-3/km-48-…` `km-49-…` `km-50-…` `km-51-…` `km-85-…`
`karo-mac/km-52-…` `km-53-…` `km-54-…` `km-55-…` `km-73-…` `km-74-…` `km-76-…` `km-77-…` `km-78-…`
`km-80-…` `km-81b-…` `km-84-…` `km-90-a1-…` `km-91-a3-…` `km-hook-no-sotai-path-…` `km-kansa-daikou-…`

★註★: 乙 に落ちた枝の中身が無価値なのではない。**紙は既に此の repo の `docs/evidence/` に在り、
枝を着地させずとも読める。** 着地の要否は「器が要るか」で測つた。由緒の要否は當席には測れぬ。

## 五 ★着地の単位は 45 本ではない ―― 先づ幹を一本★

`karo-mac/km-gate-kou-otsu-20260917` = `363d5fb06084` = ★手許の未 push `main`★。
- 対 origin/main: ★16 commit / 464 file★(内訳 `docs` 398・`queue` 52・`scripts` 4・直下 1、他に非ASCII括り 9)
- 45 本の内 ★27 本★ が「幹 + 1〜2 commit」である。9 本は `km-gate4-kou-otsu`、4 本は `km-shikii-yokotenkai`、3 本は `manifest-verify-20260909`、各 1 本が `km-75` と `gate-hook-fix` を基とする。
- 此の幹は ★不要15 の一★ である(tip が 27 本に含まれる故)。
  **∴「不要」の札は「消しても commit は失はれぬ」の意でしかなく、「着地させるな」の意ではない。**

★家老の見立て★: ★第一の PR は幹 一本★。幹が着地すれば 45 本の対 main 差分は 400〜700 から 1〜36 へ落ち、
甲 10 本は人が読める大きさの PR に成る。幹を措いて 45 本を並べれば、同じ 464 file を 45 回 review する事に成る。

## 六 器の重なり(衝突の種)

| 器 | 触る枝の数 | 枝 |
|---|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | ★4★ | a1-r56 / daiko-teishutsu / km-79 / lot48235904 |
| `scripts/checks/karo_mac_manifest_verify.py` | ★4★ | a1-r56 / daiko-teishutsu / hantei-saiteishutsu / lot48235904 |
| `scripts/stop_hook_inbox.sh` | ★2★ | ashigaru-mac-3/km-91 / karo-mac/km-81 |
| 残 6 本(`gate4` `inbox_watcher` `detect_stale` `settings.json` `goal_stop_hook` `goal_stopfailure_hook`) | 各 1 | ― |

★∴ 甲 10 本を無順で並べて起票してはならぬ。★ 上二つの器は 4 本づつが触る。
`karo_mac_manifest_verify.py` は 4 本の内 3 本が ★幹と同 blob★ ゆゑ実際の競合は `hantei-saiteishutsu` 一本のみ。

## 七 逐語 ―― 測り方と、途中で踏んだ罠

```
git ls-remote --heads origin                      # 前束 raw/10_lsremote.txt(240行)
git cat-file -e <sha>^{commit}                    # 手許に物が在るか(45本 rc 悉く 0)
git diff --name-only 4be3ee19e1c5...<sha> | 行数   # 定義⑴
git merge-base --is-ancestor <tip_B> <sha>        # 祖先か(rc=0 ⇒ B ⊆ X)
git rev-list --count <tip_B>..<sha>               # 最も近い祖先を選ぶ物差し
git diff --name-only <tip_B>..<sha> | 行数         # 定義⑵
git rev-parse <rev>:<path>                        # blob 同一性(★rc で測れ★ 下記罠)
```

★罠 ―― `git rev-parse <rev>:<path>` は path が不在でも ★引数の字面を stdout へ echo し★ rc を 128 にする。★
`m=$(git rev-parse ... || echo NONE)` は ★一度も発火せぬ★。當席は之で一度「異」と誤り、rc で測り直した。
`raw/40_kigu_vs_miki.tsv` は最初から rc で測つて居り正しい。上の誤りは本紙の外(端末)に留まり、紙には入つて居らぬ。

## 八 家老の申し條

1. ★消して居らぬ。★ 不要15本にも残45本にも一切触れて居らぬ。枝の存廃は理事長専管と心得る。
2. ★着地の順を申す★: ㋐幹(`363d5fb06084`) → ㋑甲#1(既 push 済・起票のみ) → ㋒甲#2〜#7(器 1〜2 本の小 PR) → ㋓甲#8〜#10(実体は `dasumae_gate.sh` 一本)。
3. ★乙35本は「main に入れずとも器は揃ふ」までしか言へぬ。★ 由緒(証拠の永続)として main に要るか否かは當席の測れる所ではない。理事長裁を仰ぐ。
4. ★起票は監督 lot・判定は軍師mac★(裁の逐語)。當席は起票せぬ。push も総監督の代行を請ふ。
5. 三席(專任1/2/3)へ同じ 45 本を三分して独立に測らせた(札 km-100/101/102)。★本紙と食ひ違ふ数が出たら其れ自体を疵として報せる。★
