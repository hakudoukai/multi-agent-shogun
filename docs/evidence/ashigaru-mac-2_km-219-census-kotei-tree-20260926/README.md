# km-219(板 9664569e): worktree 全census と ff 可否 ―― 固定tree で取り直した(專任2)

担当: ashigaru-mac-2 ／ 発注: goal 2026-09-26 17:00 gakushu-bucho ／ 板 current_step の owner は karo-mac

## 0. 着手前に見た食い違ひ(受入は変へて居らぬ)

- 板の題と current_step は「席3」と書く。goal は席2(拙者)へ来た。
- 席3 は km-219 を 2026-09-20 に既に納めて居る: 枝 `ashigaru-mac-3/km-219-worktree-census-to-ff-hantei-20260920` 尖 f77a3456992287fc091de5913f5f3fc502ff160c(軍師 REVISE への追補まで)。然るに板は status=assigned・checkpoint 空の儘である(板と実態の乖離)。
- 席3 の今の goal は別の板 f1c9b1b5(km-224)。本束は自席の新しい枝・新しい dir にのみ書き、席3 の file には触れて居らぬ。
- ∴ 本束は席3 の紙の★置き換へではない★。同じ器で「今の刻」を取り直した物である。どちらを受入に使ふかは家老の判である。

## 1. 固定 tree

- base = origin/main を 17:01 に rev-parse した b9573b2d376e9a0a372234b696a733677feb7919(fetch はして居らぬ・local main も同じ)。`raw/00_kiten.txt`
- 器 = 席3 の `10_census_kotei.py`(f77a3456)を写し、二点だけ足した(`raw/05_driver_diff.txt`): base を sha で argv から取る/`GIT_OPTIONAL_LOCKS=0`(他席の index を掴まぬ)。
- 本束を書く worktree(/Users/momizimac/wt/a2-km219c)は測る直前に切ったゆゑ、母数に入る。

## 2. 結果(`raw/30_shukei.txt`・表は `raw/40_checkout_table.tsv` header除き161行)

- 母数 161本(席3 の 09-20 は 61本)。detached 18 / branch 付き 143 / /private/tmp 下 13。重複 checkout 0。実質的な ff 判定数では HEAD=base の自己行1本を除外する。
- is_ancestor rc: ★rc=0 は7件、そのうち HEAD=base の自己行1件は自明なので実質6件★ / rc=1(ff 不可)=142 / rc=128=12。
- rc=128 の12本は prunable の12本と集合一致した(dir が消えて cwd に使へぬ)。此の12本は判定不能であり、ff 不可とは数へて居らぬ。
- 未 commit の変更を持つ worktree は 60本。
- rc=0 の7本:
  - /Users/momizimac/wt/a2-km186-gyaku (detached)
  - /Users/momizimac/wt/a2-km186-t1 (detached)
  - /Users/momizimac/wt/a2-km186-t2 (detached)
  - /Users/momizimac/wt/a2-km186-t4 (detached)
  - /Users/momizimac/wt/a2-km186-t5 (detached)
  - /Users/momizimac/wt/a2-km219c (ashigaru-mac-2/km-219-census-kotei-tree-20260926) ←本束の樹・HEAD=base そのもの(自明の rc=0。実質判定数から除外)
  - /Users/momizimac/wt/karo-main-ff (detached)

## 3. 此の数が意味せぬ事

- rc=0 は「HEAD が固定 base の祖先ゆゑ base へ ff できる」の意だけである。main へ入れてよいかの判ではない。
- status は `-uall` のみ。`--ignored` は測って居らぬ。
- prunable 12本を片づける(`git worktree prune`)のは変更ゆゑ、して居らぬ。
