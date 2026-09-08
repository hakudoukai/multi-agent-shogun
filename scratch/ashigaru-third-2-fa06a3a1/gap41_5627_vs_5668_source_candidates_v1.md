# 差 41 (226ref 合併 5,627 対 實測 5,668) の出所候補 ―― 讀取のみ (order57)
as_of 2026-09-07T18:22:36+09:00 / 席=ashigaru-third-2 / 對象 repo=/mnt/c/DentalBI (.git のみ)
前紙: after_delete_5668_gap_1483_readonly_v1.md sha16=306816953dc056f5 (59行) §3
前紙: residual_5668_three_options_comparison_v1.md sha16=4cd5df0a785c131f (33行) §2
※ 兩紙は開いて讀んだのみ・書き換へて居らぬ。

## §1 候補の一覧 (和=10) と三値
數へた 1 = 「差を生み得る出所」1 つ。三値 = 測れる / 測れぬ(git に無く DB に在る) / 測定不能(何處にも無い)。

| # | 候補 | 三値 | 一行 |
|---|---|---|---|
| C1 | ref 一覧の取り方・時點差 (226 本 対 248 本) | 測れる | §2-1 |
| C2 | ref 種別の取捨 (heads/remotes/tags/pull/stash/jinji) | 測れる | §2-2 |
| C3 | worktree の detached HEAD が ref 一覧に載らぬ | 測れる | §2-3 |
| C4 | remote-only 枝の更新 (fetch せねば見えぬ分) | 測定不能 | fetch 0 の床ゆゑ當席は測れぬ |
| C5 | 削除済 ref の殘行 (枝が刈られ行だけ表に殘る) | 測れぬ | §3 S57-2 |
| C6 | CI #2 が v3 の外の filter で書いた行 | 測れぬ | §3 S57-2 (commit_hash 分布で分かつ) |
| C7 | path の正規化差 (大小違ひ) | 測れる | §2-4 |
| C8 | path に非 ASCII を含む物 (REST の符号化を跨ぐ) | 測れる | §2-5 |
| C9 | delete_stale の in.() csv を壊す文字 (\" , \\ 空白) | 測れる | §2-6 |
| C10 | 實測 5,668 を數へた時點と今の時點の差 | 測れぬ | §3 S57-1 |

## §2 測れた候補 ―― git 讀取動詞と結果 (件數のみ・path 値は寫さぬ)
用ゐた動詞: `git for-each-ref` / `git ls-tree -r --name-only` / `git ls-files` / `git symbolic-ref -q HEAD` / `git stash list` / `git worktree list` / `git cat-file -p`。write 動詞 0・fetch 0。
filter は v3 blob 0754d928… を `git cat-file -p` で出し `ast.literal_eval` で INCLUDE/EXCLUDE の literal だけを取つた (★v3 は import も走行もして居らぬ★)。INCLUDE=35 本(重複除き 31)・EXCLUDE_PATTERNS=5・EXCLUDE_DIRS=8。

- §2-1 全 248 ref の tree を合併 → INCLUDE(入口 regex L390-391/L409-414 の寫し) = ★5,678★。前紙の 226 ref = 5,627 ∴ ref 22 本増で ★+51★。
- §2-2 種別ごとの獨自寄與 (其の種別を落とすと消える path 數): remotes ★1,174★ / heads ★1★ / tags ★1★ / pull ★0★ / stash ★0★ / jinji ★0★。heads∪remotes(235本)=5,677 ∴ 殘り 13 本の寄與は ★1★。
- §2-3 `git symbolic-ref -q HEAD` 成功 = HEAD は attached。`git worktree list` 10 件・`git stash list` 8 件。stash は refs/stash 1 本として §2-2 に入つて居り獨自寄與 0。
- §2-4 合併 INCLUDE 內で lower() が衝突する組 = ★1 組・行にして 2★。
- §2-5 合併 INCLUDE 內で非 ASCII を含む path = ★10★。
- §2-6 `"` `,` `\\` 空白 の何れかを含む path = ★0★ ∴ C9 は現に無い。
- 併記 (出口 fnmatch L258-259 の寫し): 合併 INCLUDE(出口) = 5,050。入口のみ 696・出口のみ 68 ―― 之は「㋒ でも殘る側」の說明であり 41 の差の說明ではない。
- 併記 (現 HEAD 追跡簿): INCLUDE = 4,113。合併−現 = 1,565・現−合併 = 0。

## §3 測れぬ候補への SELECT 案文 (3 本・件數のみ・當席 0 打・打つは總監督殿)
- S57-1 (C10 時點差): `select count(*) from source_code_cache;`
- S57-2 (C5/C6 削除済 ref・外部書込): `select count(*) as n, count(distinct commit_hash) as h from source_code_cache;`
- S57-3 (C7/C8 正規化): `select count(*) filter (where file_path ~ '[^\x20-\x7e]') as non_ascii, count(*) filter (where lower(file_path) <> file_path) as has_upper from source_code_cache;`

## §4 結び ―― 41 を說明し切れるか
- 差 41 は ★現に無い★。之は「解つた」ではなく「★其の數が別の數に置き換はつた★」の意である。
- 内譯: 226 ref 時點の 5,627 は ref 集合の取り方に依る數であり、248 ref で測り直すと ★5,678★。實測の殘 5,668 に對し ★+10★ ―― ★向きが逆に成る★ (合併が實測を上回る)。
- ∴ 「41 が不足」ではなく「★10 が過剩★」が今の姿。C1+C2 (ref 集合) が 41 を呑み込み、10 を新たに出した。
- 10 の出所は ★測定不能★。§2-5 の非 ASCII path 10 本と數が一致するが、★數の一致であつて因果は測つて居らぬ★ (DB を讀めぬ ∴ 表側に其の 10 本が在るか否かを當席は言へぬ)。S57-3 が之を分かつ。
- 推しは置かぬ。

## §5 境界
- 5,678 も 5,677 も ★局所の .git が今 持つ ref★ の合併であり、遠隔にのみ在る枝 (C4) は測つて居らぬ。
- 前紙の 5,627 は當席が測り直して居らぬ (前紙不觸の床)。∴ 「226→248 で +51」は ★同じ器で測つた 2 數の引き算ではない★ ―― 前紙の器と本紙の器が同一である事は證して居らぬ。
- 實測の殘 5,668 は order50 の時點の數であり、本紙では測り直して居らぬ (DB 0 の床)。S57-1 が之を分かつ。
- 42P10・PostgreSQL の擧措に關する記述は本紙に無い。
- ★開示 2 件★: ⑴ 前區間で所要時間を測る際 `> /dev/null` と shell の `>` を ★1 度使つた★ (file への書込ではないが床⑾ の文言に觸れる・以後 redirect を用ゐず `| wc -l` で受けた)。⑵ `inbox_write.sh` が自ら `CAP_ROTATED: 20 read messages moved to queue/inbox/_archive/karo-third_pruned.yaml` を行つた (helper の掃除であり當席の手ではない)。
