# sync_source_cache.py 讀取 census（order24・監督 lot の材）

席: ashigaru-third-2 ／ 令: subtask_thirdpc_a2_sync_source_cache_script_readonly_census_for_supervisor_lot_001
対象: /mnt/c/DentalBI/scripts/sync_source_cache.py（共有樹・追跡下）
用: 総監督裁 hs_b784474a（hook 設計の疵 → 監督 lot: state file へ移す）の材。★所在を測るのみ・案文は書かぬ★

## 一. 実体（当席が今 measure し直した数・1 = file 1 本）

- sha256 `0d5a2258ef1adccb4c4093b82568d575d1a566e1a67eb03254d9b367e00f47a3` … 測つた
- 16892 byte ／ 455 行 ／ mode 777 ／ mtime 2026-09-05 02:16:39 … 測つた
- 冒頭 docstring は「v3.0」を名乗る（L1-9）。import は L10-21（httpx・dotenv を含む） … 測つた

## 二. 何を読むか（走査 dir と除外・1 = glob 1 本 / 行 1 本）

- L47-84 `INCLUDE_PATTERNS` = 35 要素。相異なる glob は 31 本、二度書かれて居るものが 4 本
  （`supabase/migrations/*.sql`・`supabase/functions/**/*.ts`・`docs/audits/**/*.md`・`docs/audits/**/*.txt`）… 測つた
- L76 に「副医院長 453ca4a4 命令」の註が在り、其の下 L77-83 が後から足された 7 本である … 測つた
- 走査対象に `CLAUDE.md`(L71)・`.claude/rules/*.md`(L72)・`.claude/agents`・`.claude/commands`・`.claude/skills` が含まれる … 測つた
- L87-93 `EXCLUDE_PATTERNS` = 5 要素 ／ L96 `EXCLUDE_DIRS` = 4 語（node_modules・__pycache__・dist・.git） … 測つた
- L102-107 `should_exclude`（fnmatch 一致）／ L110-122 `collect_files`（repo_root.glob → 相対 path 化 → sorted） … 測つた
- L125-131 `get_commit_hash`（`git rev-parse --short HEAD`・失敗時 "unknown"） … 測つた
- L312-313 引数は `--dry-run` と `--changed-only` の 2 つ … 測つた
- L322-337 `--changed-only` 時は `git diff --name-only origin/main...HEAD`、returncode 非 0 なら `HEAD~1 HEAD` へ落ちる … 測つた
- L338-340 既定は全走査（`collect_files` の全件） … 測つた
- L366-390 file ごとに 実在せねば SKIP(L369)・空なら SKIP(L382)・UnicodeDecodeError は errors=replace で SANITIZE(L378-379)・NUL は除去(L388-390) … 測つた

## 三. 追跡 file `scripts/sync_file_list.txt` の読み書き（1 = 出現行 1 本）

- 当 script 中の出現は 3 行のみ: L436(註)・L437(path 組立)・L440(stderr 表示) … 測つた
- ★書く箇所は L439 の 1 行のみ★。逐語:
  `list_path.write_text("\n".join(all_files) + "\n", encoding="utf-8")`
- L438 で `collect_files(repo_root)` を★もう一度★走らせ、其の全件を書いて居る（同期対象の縮小集合ではない） … 測つた
- ★読む箇所は 0 行★（当 script は此の file を一度も読まぬ） … 測つた
- L436 の註 逐語: `# 同期対象リストをsync_file_list.txtに自動更新（参照用）`
- repo の code 側（.github/scripts/backend/frontend/tools）で `sync_file_list` に触れる file は当 script のみ（`git grep` の該当 3 行＝上記と同一）… 測つた
- 追跡下の doc 側には言及が在る（REVIEW.md 等）が、code の読手ではない … 測つた
- 書込は L418 で exit_code を決めた★後★に置かれ、try で囲まれて居らぬ（L436-440） … 測つた

## 四. 何を書くか（DB 側・1 = 呼出 1 本）

- table は `source_code_cache` の 1 本のみ（L145・L243・L270） … 測つた
- POST L143-157: `on_conflict=file_path`・`Prefer: return=minimal,resolution=merge-duplicates`・timeout 60.0・batch 上限 L99 = 50 … 測つた
- 送る列は L392-399 の 6 つ（file_path・content・line_count・file_size・commit_hash・updated_at）＝★file の中身其の物を送る★ … 測つた
- GET L241-263: `select=file_path` を limit 1000 で頁繰り・timeout 30.0 … 測つた
- DELETE L266-284: `Prefer: return=minimal`・timeout 30.0・条件は L280 の 1 行。逐語:
  `params={"file_path": f"in.({paths_csv})"}`
- L277 で path を `"` で括り `,` 連結（註 L275-276 に PostgREST の in 演算子の由 が書かれて居る） … 測つた
- 「stale cleanup」の字面の意味 = L420-434: cache に在り local に現に無く、且つ INCLUDE_PATTERNS に当たる path を消す（L190-205 `compute_stale_paths`） … 測つた
- L191-196 の註に「母集合は必ず repo 全体の collect_files を渡せ／--changed-only の縮小集合を渡すと 2113 件が誤削除候補になつた」旨が書かれて居る … 測つた
- L426 は其の註の通り repo 全体を渡して居る … 測つた
- L287-305 の SQL 生成は `--dry-run` 専用（標準出力へ印字するのみ） … 測つた

## 五. env（★名のみ・値 0 字★）

- L39-41 `backend/.env` を `load_dotenv` で読む（path は `__file__` の親の親） … 測つた
- L43 `SUPABASE_URL` ／ L44 `SUPABASE_SERVICE_KEY` の 2 名。当席は値を開いて居らぬ・本紙に値 0 字 … 測つた
- L134-140 で 其の値を `apikey` と `Authorization: Bearer` の 2 header へ載せる … 測つた
- L316-319 dry-run 以外で 2 つの何れかが空なら stderr へ出して `sys.exit(1)`（此処は hook より前に止まる） … 測つた

## 六. 失敗時の挙動（1 = 分岐 1 本）

- L162 一過性と看る HTTP status = 11 個（429・500・502・503・504・520-525） … 測つた
- L163 `MAX_UPSERT_TRIES = 3`（初回＋2 回・backoff 1s→2s・L177-186） … 測つた
- L208-238 batch 失敗時: 一過性なら fan-out せず即戻る(L218-223)／非一過性なら 1 件ずつ隔離し「POISON FILE」を印字(L227-237) … 測つた
- L414 集計を stderr へ ／ L418 errors>0 なら exit_code=1 ／ L449-451 で印字して return ／ L454-455 `sys.exit(main())` … 測つた
- ★stale 節(L424-434) と 最終カウント(L443-447) は try/except で握り潰し、WARNING を印字するのみ・exit_code を上げぬ★ … 測つた
- ∴ DELETE が失敗しても・cache 数が読めなくても、L439 の書込は其の後で必ず走る … 測つた

## 七. 「追跡 file を書く」を state file へ移すに要る箇所の★所在だけ★（案文は書かぬ）

- 書込 1 箇所: L437（path 組立）・L438（再走査）・L439（write_text） … 測つた
- 印字 1 箇所: L440（stderr の件数表示） … 測つた
- 内容を決めるもの: L47-84 INCLUDE_PATTERNS ／ L87-96 除外 ／ L110-122 collect_files … 測つた
- 現に居る読手: code 側 0・doc 側は言及のみ … 測つた
- hook 側の呼び方（`SYNC_SCRIPT` の行・止めぬ扱ひ）は order20 の紙 sha16 `80813308657ee1a4` に測つて在る … 測つた
- 移し先の path・書式・後方互換の可否は 測つて居らぬ（当席の職に非ず）

## 八. 禁の遵守と 逐語の量

- 実行 0（当 script を一度も走らせて居らぬ）／編集 0 ／ REST 0 ／ hook 発火 0（push 0）／ D 樹 0 打 … 測つた
- 逐語で引いた code は 3 箇所・合計 146 字（上限 150 字。1 = 逐語 1 字） … 測つた
- secret の値 0 字（env は名のみ・`backend/.env` は開いて居らぬ） … 測つた

## 九. 結び（三択）

- sha・行数・走査 dir と除外・追跡 file の書込 1 箇所と読手 0・table 1 本と POST/GET/DELETE の条件・env 名 2・retry と exit の道筋 = 測つた
- 移し先の設計（path・書式・互換）・hook 以外の呼出元の有無 = 測つて居らぬ
- 此の書込を state file へ移すか否かの裁 = 当席の職に非ず（総監督の裁を待つ）

as_of: 2026-09-07T06:42:36（当席 third_pc 実測時刻）
