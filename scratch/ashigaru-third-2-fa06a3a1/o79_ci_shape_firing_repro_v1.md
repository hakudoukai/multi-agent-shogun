# order79: CI の形で v3 の第一親の直しが発火するかの実測 (作り物 repo・本物 CI 0・DB 0・push 0)

as_of 2026-09-08T06:0x JST / 席 ashigaru-third-2 / 令 order79 (msg_20260908_055352_98b45646)
底本 v3 = `git show origin/main:scripts/sync_source_cache.py` の抽出 766 行 sha256_16=16e2db65f8cb48fa
底本 CI = `origin/main:.github/workflows/sync-source-cache.yml` blob 3d2dbae7ae84 (63 行)
前紙 o78 `e2fef4b05c09f3b5` 不触 (書換へず)

## §0 結び (一語)
★CI の現形では 発火する★。而して発火は ★第一親が clone に在る事★ に懸かる ―― 之が一語である。
具体には 二つが同時に要る: ⑴`refs/remotes/origin/main` が解ける事 ⑵`HEAD^1` が clone に在る事 (= fetch-depth が 2 以上)。
CI は現に ⑵ を `fetch-depth: 2` で満たし、⑴ を actions/checkout@v4 の枝押し形で満たす ∴ 発火する。

## §1 何を 1 と数へたか / 網の形
1 = 形 1 通り / file 1 本 / 走 1 回。
「発火」= v3:572 の `-- CHANGED_ONLY_FIRST_PARENT:` が stderr へ出た事 (文字列 `CHANGED_ONLY_FIRST_PARENT` の在否で判じた)。
「返した本数」= `changed_paths_from_git()` が返した集合の要素数。
作り物 repo は `scratch/ashigaru-third-2-fa06a3a1/o79_lab*/` の内のみ。遠隔は同 dir 内の bare repo であり、本物の remote へは押して居らぬ。

## §2 CI の現形 (逐語・origin/main)
- `:32 uses: actions/checkout@v4` / `:35 fetch-depth: 2`
- `:63 run: python3 scripts/sync_source_cache.py --changed-only --no-stale`
- v3 側の窓 = `:540 changed_paths_from_git` ―― `:551` 三点 `origin/main...HEAD` → 空なら `:565-575` で `HEAD^1` へ落とす。

## §3 走 1: checkout の形を 3 通り (規 o79_ci_shape_repro.py 93 行)
| 形 | shallow | detached | 三点rc | 三点本数 | HEAD | origin/main | 一致 | 発火 | 返した本数 |
|---|---|---|---|---|---|---|---|---|---|
| 甲 branch形 depth2 (checkout@v4 の枝押し形) | True | False | 0 | 0 | 794a79521 | 794a79521 | True | ★True★ | ★2★ |
| 乙 detached形 depth2 (remote-tracking ref 無し) | True | True | 128 | 0 | 794a79521 | (解けぬ) | False | False | 2 |
| 丙 full clone (対照) | False | False | 0 | 0 | 794a79521 | 794a79521 | True | True | 2 |

読み: 甲 で ★三点が 0 本★ になる事を現に再現した (己と己の差)。而して直しが発火し 2 本を返した。
乙 は `origin/main` が解けず 三点 rc=128 ∴ 直しの塊へ入らぬ。但し `:559` の従前 fallback `HEAD~1..HEAD` が同じ 2 本を拾ふ ∴ 0 本にはならぬ。

## §4 走 2: 直しの有無 × fetch-depth × 合流の形 (規 o79_ci_shape_repro2.py 84 行)
| 合流の形 | fetch-depth | 版 | HEAD^1 在り | 発火 | 返した本数 |
|---|---|---|---|---|---|
| merge (--no-ff) | 2 | 直し在り | True | True | ★2★ |
| merge (--no-ff) | 2 | ★直し無し (PR#143 以前)★ | True | False | ★0★ |
| merge (--no-ff) | 1 | 直し在り | ★False★ | False | ★0★ |
| squash (直線 commit) | 2 | 直し在り | True | True | 2 |
| squash (直線 commit) | 1 | 直し在り | ★False★ | False | ★0★ |

読み: ★陰性対照 (直し無し・depth2) が 0 本を返した★ ―― 之が PR#140 の `Upserted 0` と同じ形である。
同じ形で直しを入れると 2 本 ∴ ★直しは現に 0 本を 2 本へ変へる★。
squash 形でも同じく発火する ∴ merge の作り方には依らぬ。

## §5 発火せぬ形 (危ふしと記す)
- ★fetch-depth を 1 に落とすと 直しは発火せず 0 本へ戻る★ (merge/squash いづれも)。因 = `HEAD^1` が shallow の外ゆゑ `git diff HEAD^1 HEAD` が rc≠0 となり `:573` の門を通らず `:576 return set()` へ落ちる。
  ∴ CI yml の `:35 fetch-depth: 2` は ★直しの前提であり 飾りでは無い★。1 へ縮めれば PR#140 の形へ戻る。
- 乙 (detached・ref 無し) は発火せぬが 従前 fallback が拾ふゆゑ 0 本にはならぬ。∴ 「発火せぬ = 0 本」では無い。

## §6 己の見立ての外れ (開示)
申し出 (msg_20260908_055241_185b472d) の ② で当席は
「CI に origin/main ref が無ければ _rev_parse が空を返し 直しは不発 → Upserted 0 が残る」と見立てた。
★実測は半ば外れである★ ―― ⑴checkout@v4 の枝押し形は remote-tracking ref を ★作る★ ゆゑ ref は在る。
⑵仮に無くとも 従前 fallback `HEAD~1` が同じ本数を拾ふ ∴ 「ref 無し = 0 本」は成り立たぬ。
0 本を招く実際の因は ★ref の有無では無く 第一親が clone に在るか否か (fetch-depth)★ であつた。
前便は書換へず 本紙に併記する。

## §7 境界・確かめて居らぬ
本物の CI 走行 0・DB 讀 0 書 0・SQL 0・push 0 (作り物の bare repo へ 1 回押したのみ・本物の remote へは 0)・製品 file 書換 0・fetch/pull/prune 0 (共有 .git へ書込動詞 0)・Commander の箱 0 打。走 = ★2 回★ (上限 5)。
★確かめて居らぬ★: 本物の GitHub Actions runner 上での actions/checkout@v4 の実挙動は 当席の作り物での再現であり 現物の log を讀んで居らぬ。
★確かめて居らぬ★: 次に main へ push が在つた折に DB の `Upserted` が現に幾つになるかは DB を讀まぬゆゑ測つて居らぬ。
★確かめて居らぬ★: 他 PC (main/second/mac) の実装済 hook は手が届かぬ。
