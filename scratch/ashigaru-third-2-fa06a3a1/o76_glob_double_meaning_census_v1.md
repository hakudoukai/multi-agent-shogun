# v3 の glob 二重意味 (入口 regex 対 出口 fnmatch) の差の本数 と 揃へる案文

as_of 2026-09-08 05:4x JST / 席 ashigaru-third-2 / 令 order76 (弾B) / ★書換 0・案文と数まで★
器: v3 blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9` (709 行・行番号は皆 此の blob)・repo=/mnt/c/DentalBI (局所 ref のみ・fetch 0)
前紙 (不触): order53 `fnmatch_vs_regex_divergence_select_drafts_v1.md` / order52 `option_c_execution_packet_v1.md`。規: `o76_glob_census.py` (116 行・sha256 頭 16 `359fc3206ad5699b`・讀取のみ・DB 0・network 0)

## §1 何を 1 と数へたか・網の形

1 = path 1 本 (行数でも byte でもない)。網は v3 を import して當てた ―― 写し取りではない。
- 入口の目 `Ar` = `matches_include_patterns` (L409-415・`_glob_pattern_to_regex` L377-403 の正規表現)
- 入口 実装 `A` = `Ar` ∧ ¬`should_exclude` (L124-129 fnmatch) ∧ 頭に `EXCLUDE_DIRS` の part 無し = `collect_files` L157-179 の儘
- 出口の目 `B` = `any(fnmatch.fnmatch(cp, pat) for pat in INCLUDE_PATTERNS)` = `compute_stale_paths` L258-259 の儘 (★EXCLUDE を掛けて居らぬ★)
- `Bx` = `B` ∧ ¬`should_exclude` ∧ EXCLUDE_DIRS 外 (元素を分ける為だけの網)
母集合 3 種: `M0`=commit dbf05a029 の樹 (order52 と同じ・実在 filter 無し) / `M1`=現 HEAD b61f0a36e の追跡簿 ∧ 作業樹に実在 / `M2`=`o70_union_local.json` (当席が前の弾で畳んだ file・★其の網の形は本弾で確かめて居らぬ★)

## §2 差の本数 (元素を分けた・和は元素ごとに閉ぢる)

| 母集合 | 本数 | Ar | B | A | ★① regex のみ★ | ★① fnmatch のみ★ | ① 和 | ② EXCLUDE を掛けぬ差 (B\Bx) |
|---|---|---|---|---|---|---|---|---|
| M0 dbf05a029 | 14,738 | 4,202 | 3,637 | 4,201 | ★623★ | ★59★ | 682 | ★0★ |
| M1 現 HEAD | 13,990 | 4,114 | 3,533 | 4,113 | ★622★ | ★41★ | 663 | ★0★ |
| M2 代用 | 5,172 | 5,098 | 5,172 | 5,098 | 0 | 74 | 74 | ★0★ |

- ★元素は 2 つで、足して 1 つの数にはせぬ (四条③)★: ①=glob の意味の差 (regex は階層を跨がぬ・fnmatch の `*` は `/` を跨ぐ)、②=出口が EXCLUDE を掛けぬ事。②は 3 母集合とも ★0 本★ ―― 現に在る差は ★① だけ★ である。
- ① の中身 (M1): regex のみ 622 = scripts 212・docs 203・tests 175・tools 25・backend 4・frontend 3。pattern 別 = `tests/**/*.py` 175・`docs/codex_audits/**/*.md` 152・`scripts/**/*.py` 130・`scripts/**/*.sh` 60。形は皆 ★`<dir>/**/*.<ext>` の直下 file★ (例 `backend/main.py`)。
- ① の逆向き (M1): fnmatch のみ 41 = ★悉く `supabase/migrations/*.sql` の下位 dir★ (例 `supabase/migrations/proposals/…sql`)。M0 では 59・M2 では 74。

## §3 order52 の 623 と同じ意味の数か (四条③ の断り)

★同じ意味である。網が同じ事を再現で示した★ ―― M0 (order52 と同じ commit・同じ母集合) を當てると 入口 4,201・出口 3,637・入口のみ ★623★・出口のみ ★59★ で、order52 execution packet L17 の数と ★4 つとも一致★ した。
∴ M1 の 622 と order52 の 623 の 1 本差は ★網の差ではなく母集合の差★ (14,738 → 13,990・747 本入れ替はり・実在 filter 有無も違ふ)。★「1 本減つた」と読むな★。

## §4 差が効く所 (何処に届き、何処に届かぬか)

- 出口 `compute_stale_paths` を呼ぶのは L661 ただ 1 箇所 ―― `--full-stale-scan` か prev_commit を解けぬ時の ★全表走査経路のみ★。
- `stale_paths_from_git` (L417〜) は既に `matches_include_patterns` = ★入口と揃つて居る★ ∴ git 差分経路に此の差は無い。
- 現行 CI は `--changed-only --no-stale` ∴ ★今の CI 経路には届かぬ★。届くのは全表走査を打つた時。
- 向き: 「regex のみ 622」= 表に在り作業樹から消えても ★全表走査で消し損ねる側★ (残 5,668 の筋と同じ形)。「fnmatch のみ 41」= 入口が入れぬ形なのに ★消す側に数へられる★ (別経路で入つた行に効く)。
- ★紙と符の食ひ違ひが v3 の中にも在る★: `collect_files` の docstring L162-164 は逐語「matcher は stale 側と同じ matches_include_patterns を使ひ、入口と出口で glob の意味を 1 本に揃へる」と書くが、出口 L258-259 は fnmatch の儘である。

## §5 揃へる案文 (触れる行を逐語・★本弾では書換 0★)

(1) `scripts/sync_source_cache.py` L258-261 の 4 行 (L254-257 の `stale: set…` `for cp…` `if cp in all_local_paths: continue` と L262 `return stale` は不触):
```
-        for pattern in INCLUDE_PATTERNS:        # ← 出口だけの fnmatch (L258-259)
-            if fnmatch.fnmatch(cp, pattern):
-                stale.add(cp)
-                break
+        if matches_include_patterns(cp):        # 入口 (collect_files) と同じ目
+            stale.add(cp)
```
(2) docstring ―― L162-164 は既に「揃へる」と書いて在る文ゆゑ符が追ひ付く形 (不触)。L379-385 の註「collect_files は glob、compute_stale_paths は fnmatch を使つて居るゆゑ…非対称が在る」を ★現況へ書き直す★ (L247-252 の母集合の断りは残す)。
(3) `tests/test_sync_source_cache.py` L467-471 `test_legacy_compute_stale_paths_left_unchanged` ―― 逐語「`assert "scripts/a.py" not in stale  # fnmatch ゆゑ直下は拾はれぬ (既存のまま)`」は ★現行の性質を釘付けにして居る★ ゆゑ、揃へると此の test が反転する。名と本文を書き直し (`…_aligned_with_entry`)、`scripts/a.py` を stale に入る側へ、`supabase/migrations/sub/x.sql` を入らぬ側へ 2 行で釘付けする。L450-462 の `test_include_matcher_follows_glob_not_fnmatch` は入口のみを見る test ゆゑ不触。
- 触れる file ★2 本★・触れる行 ★概ね 15 行★ (v3 −4 行 + 註 3 箇所 + test 1 本)。

## §6 危険と戻し方

- 危険①: 揃へた後に全表走査を打つと、今まで消し損ねて居た「regex のみ」形が ★一度に消す側へ入る★。★DB に其の形が何行在るかは讀めぬ (確かめて居らぬ・六条)★ ―― 上限は order53 §3 の S3-1 を打てば出る。∴ 先に `--dry-run` で `STALE_ATTEMPTED` の数を見る手順を令に含める。
- 危険②: 逆向き 41 本 (`supabase/migrations` 下位) は揃へた後 ★消す側から外れる★。危険③: `should_exclude` の fnmatch は Windows で大小を無視する (order53 §4) ―― 本案は其処へ触れぬゆゑ OS 差は残る。
- 戻し方: 上記 hunk 1 つと test 1 本を戻せば元の挙動へ返る。★code の書換だけでは DB の行は動かぬ★ (動くのは次に全表走査を打つた時) ∴ 走らせる前なら戻しに副作用は無い。

## §7 境界

書換 0 (v3・test とも)・走行は規 script のみ (v3 を import して matcher を呼んだ・v3 本体の main は走らせて居らぬ)・DB 讀 0 書 0 SQL 0・network 0・fetch/push/prune 0・前紙 不触・他席の file 不触。
M2 の母集合は当席が前の弾で畳んだ json であり ★其の網の形を本弾で確かめて居らぬ★ (六条)。M0・M1 は本弾で git から数へ直した。
