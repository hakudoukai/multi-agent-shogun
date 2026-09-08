# ㋒ (--full-stale-scan) の「作業樹に無い」判定機序 (讀取のみ・走行 0)

- 前紙: order51 residual_5668_handling_three_options_v1.md `ae4210d3fc811b36` (着手時 再測 一致)・order50 `306816953dc056f5`
- 器: v3 main blob `0754d9284`。行番号は皆 此の blob 基準。as_of 2026-09-07 16:55 JST / 席 ashigaru-third-2 / 令 order52
- 走らせて居らぬ (--dry-run も打たず)。数は order50 の値のみを用ゐ、★新規計測 0★。当席の推しは書かぬ。

## §1 L524 → L659-661 の呼出鎖 (行番号)

| # | 行 | 事 |
|---|---|---|
| 1 | L524 | `full_stale_scan = "--full-stale-scan" in sys.argv` (argparse では無く sys.argv 直見) |
| 2 | L640 | `all_local_paths = set(collect_files(repo_root))` ―― ★--changed-only でも縮まぬ★ (L631-634 の註: 縮小集合を渡すと大量誤削除・相談役 seq129633 の根治) |
| 3 | L644-656 | prev_commit を DB (L322-339) → state file (L302-314) の順で引く。引けぬ・解決できぬ時は L650/L656 で `STALE_FALLBACK_FULL_SCAN` を出し prev_commit=None |
| 4 | L657 | `if full_stale_scan or not prev_commit:` ★flag 明示 と 引けぬ時 の 2 入口★ |
| 5 | L660 | `cached_paths = get_cached_paths()` (L451-473・offset/limit=1000 の頁繰・L467/L470-471 で break) |
| 6 | L661 | `stale = compute_stale_paths(cached_paths, all_local_paths)` (L247-262) |
| 7 | L667-668 | `delete_stale(stale)` (L476-495) |

- 対する (a) 差分経路は L664 `stale_paths_from_git` (L417-432)。判定器が (b) と ★別物★ である事が §3 の要。

## §2 「作業樹に無い」判定の入力 5 点

1. **walk 起点**: L519 `repo_root = Path(__file__).parent.parent`。母集合は作業樹 walk ではなく ★git 追跡簿★ L132-146 `git ls-files -z` (L134-140 註: git を通せぬ時は例外で止まり、作業樹 glob へ黙つて退かぬ)。∴「在る」= 追跡簿に在り かつ L169 `path.is_file()` が真。
2. **INCLUDE**: 入口 = L48 `INCLUDE_PATTERNS` × L174 `matches_include_patterns` (L409-415 正規表現・L390-391 で `**/`→`(?:[^/]+/)*`)。出口 (b) = L258-260 `fnmatch.fnmatch` ★別実装★。
3. **除外**: 入口は L172 `EXCLUDE_DIRS` (L101-104・path の parts 一致) と L176 `should_exclude` (L124-129 fnmatch)。★(b) は除外を 1 つも掛けぬ★ (L253-262 に EXCLUDE の呼出 無し) ⇒ 除外 dir 配下の古い行も fnmatch が当たれば消える側に入る。
4. **大小文字**: L127/L258 の `fnmatch.fnmatch` は `os.path.normcase` 依存 (Windows で走らせれば大小を無視・Linux では区別)。入口 L409 の正規表現は常に区別。★どの OS で打つかで判定が変はる★ ―― 打つ場所は当席の測る所に非ず (測定不能)。
5. **symlink**: L169 `path.is_file()` は symlink を辿る ⇒ 生きた symlink は「在る」、壊れた symlink は「無い」= 消える側。追跡簿は symlink も列挙する。

## §3 order51 §2 ㋒「悉く消す」の狭め (前紙は書き換へず 併記)

- L379-385 の註 (逐語趣旨): `fnmatch.fnmatch("scripts/a.py","scripts/**/*.py")` は偽だが `Path.glob` は同 file を拾ふ ―― `**` の意味が違ふ。
- ∴ ★INCLUDE の直下 file (`**/` が 0 階層に当たる物) は入口で表へ入るが、(b) の fnmatch では拾はれぬ★ ⇒ ㋒ を走らせても ★残る★。
- 逆向きに §2-3 の通り (b) は除外を掛けぬゆゑ、除外 dir 配下の行は ★消える側★ に入る。
- ∴ order51 の「作業樹に無い INCLUDE path を悉く消す」は ★「直下 file を除き・除外 dir 配下を含む」★ と読み直すのが讀取の結び。前紙 `ae4210d3fc811b36` は 1 字も触れて居らぬ。

## §4 order50 の区分ごと 三値表 (数は order50 の値・新規計測 0)

| 区分 | 数 | (b) の判定 | 三値 |
|---|---|---|---|
| ㋑ 他枝にのみ在る path | 1,442 | 作業樹に無い=真。INCLUDE は fnmatch ゆゑ 階層 ≥1 は真・直下は偽 | ★判定不能★ (消/残の内訳は新規計測を要す) |
| ㋺ 履歴 D で現 tree に無い | 357 | 同上 | ★判定不能★ |
| ㋩ CI が v3 の外を書く | order50 で「現に無い」(CI 3,301 ⊂ 4,185) | 現 tree に在る | 残る |
| 差 41 (226ref 合併 5,627 対 實測 5,668) | 41 | 出所を測つて居らぬ | ★判定不能★ |
| main tree の分 | 4,185 | 作業樹に在る (L169 真) | 残る |

## §5 DELETE の順序と 途中失敗時の残り方

- 順: upsert の全束 (L612-621) → 印字 L624 → `exit_code` L628 → ★其の後に★ stale 塊 L636-680。∴ ★書き終へてから消す★。
- `delete_stale` は ★1 request★ (L486 `",".join(...)`・L489-492 `params={"file_path": f"in.(…)"}`)。★分割せぬ★ ⇒ 5,668 規模なら 1 本の query string に全 path を載せる形。長さ上限に触れた時の挙動は 走らせて居らぬゆゑ 測定不能。
- ★script 側に transaction は無い★ (blob 全文で `BEGIN`/`COMMIT;`/`ROLLBACK` = 0 件・讀取で数へた)。半端に消えるか否かは server 側 1 文の可否に依る。
- 失敗時: L493 `raise_for_status` の例外は L676-679 で捕られ `STALE_CLEANUP_FAILED: attempted=… deleted=… not_deleted=…` を stderr へ出す (upsert 済の行は其のまま)。
- L495 `return len(stale_paths)` = ★試みた数★。L483 `Prefer: return=minimal` ゆゑ ★実際に消えた行数は返らぬ★ ⇒ log の `deleted=` は「試み」と読むべき数。
- 頁繰 (L456-472) が短く返れば cached_paths が縮み stale も縮む = 消し足りぬ側へ倒れる。例外なら stale 塊ごと L676 へ落ちる。

## §6 境界

- 走行 0・--dry-run 0・DB 書込 0 讀取 0・DDL 0・本番 code 書込 0・前紙 3 本 不触・新規計測 0・当席の推し 0。
- 「どの OS で打つか」「query string の上限」「1,442/357 の直下 file 内訳」は いづれも ★測定不能★ (打つか数へ直すかを要す)。
