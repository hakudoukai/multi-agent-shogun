# order14 記録 ―― X head 実走 (collect に非ず) と件数の固定 (v1)

令: subtask_thirdpc_fa06a3a1_a2_x_head_harness_test_run_green_skip_census_detached_worktree_001 (order_in_seat=14・assigned 2026-09-07T05:36+09:00・家老third)
親裁: 総監督 seq280975(X 版 db86b2099 が正・SKIP=FAIL) + seq281003(detached 1席1樹・同時2本まで・作業後 remove) / 軍師 seq281088(skip 化不可・現行契約を検証する固定 GREEN を要す)
席: ashigaru-third-2

## 節一 標的の同定 (床(27))

- file: `backend/tests/test_c1_dml_migration_pkg_isolated_harness.py`
- X head = `fffd757f216d1412f3b586cc8eba38538de3dbba`(drx/p1-7-cross-search-20260907 の head)
- 当席が今 measure した file の sha256 = `a24443f3f619ddbb32085c6d8aeb1b877b070a006abebae9f1d689449d846423` ―― order11 紙 `rebase_onto_x_v1.md`(sha16 `1ca8897ff4bff7b9`)に載る値と**一致**。∴ order11 で collect した物と**同一の file** を今度は実走した。

## 節二 走らす前の讀取判定 (令 step3「外部 DB 要なら走らせず停まれ」)

`git show fffd757f2:<file>` の讀取のみで接続の形を判じた(走行前・0 走)。

- 本 harness は fixture `isolated_pg` で**使ひ捨ての local Postgres cluster** を自ら立てる: `tempfile.mkdtemp` → `initdb -D <tmp>/pgdata -U postgres --auth=trust` → `pg_ctl start -o "-p <空 port> -c listen_addresses=127.0.0.1 -c unix_socket_directories=''"`、teardown で `pg_ctl stop -m immediate` + `shutil.rmtree`。
- 接続先は `psycopg2.connect(host="127.0.0.1", port=<其の cluster>, user="postgres")` のみ。**本番/共有 Supabase/外部 host へ向かふ接続は file 中に 0**(`os.environ`/`getenv` で接続先を採る箇所も 0)。∴ 令の「外部 DB 要なら停まれ」には**当たらぬ**と判じ、走らせた。
- 前提の在否(讀取・**install 0**): `/usr/lib/postgresql/17/bin/initdb` **在**・`16`/`18` は不在(harness は 17 を採る)、`psycopg2` 2.9.9、`pytest` 9.0.3、`python` 3.12.3。
- **秘の値は 1 字も写して居らぬ**(env の名すら接続に用ゐられて居らぬゆゑ書く物が無い)。

## 節三 樹の新設 (令 step1・同時 2 本目)

- `git -C /mnt/c/DentalBI worktree add --detach /home/hakudoukai/a2/wt-fa06a3a1-xrun fffd757f2…` → exit **0**。
- 直後の `worktree list` の**行数 11**(1 と数へたのは list の 1 行=登録 worktree 1 本)。内訳: order13 直後の **9** + **当席の新設 1** + **A1 席が並行して立てた `/home/hakudoukai/a1/audit-wt-281476` 1**(当席の物に非ず・触れて居らぬ)。
- 新樹の HEAD = `fffd757f2…`(detached)・`status --porcelain` **0 行**。
- 当席の樹はこの時 **2 本**(`wt-964a06d0-d3adf65b` と `wt-fa06a3a1-xrun`)=総監督裁の「同時 2 本まで」の内。

## 節四 実走 2 回 (令 step2)

command(両走とも同一): `/usr/bin/python3 -m pytest -p no:cacheprovider -q backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` / cwd = 新樹

| 走 | raw 絶対 path(退避先) | SHA256 | 行数 | 逐語の summary | exit |
|---|---|---|---|---|---|
| 1 | /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/raw_fa06a3a1/fa06a3a1_xhead_run1_a2_20260907.log | d4f1f9d56730e95a4d1659b9ce8afac8f53933cc50bcf3b409c0a52e7fe478a1 | 18 | `17 passed in 1.15s` | 0 |
| 2 | /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/raw_fa06a3a1/fa06a3a1_xhead_run2_a2_20260907.log | 2477efea6a642b5f3abffb7011a9fba77f3a8e73c4806d2847f4b87b5245877e | 18 | `17 passed in 1.24s` | 0 |

件数(**1 と数へたのは test item 1 個**・両走とも同値):

| 項 | 数 | 典拠 |
|---|---|---|
| passed | 17 | summary 行の逐語 `17 passed` |
| failed | 0 | summary 行に `failed` の語 0・進捗行は `.` が 17 個のみ |
| skipped | 0 | summary 行に `skipped` の語 0・進捗行に `s` 0 個 |
| error | 0 | summary 行に `error` の語 0・stderr は空 |
| warning | 0 | summary 行に `warning` の語 0 |
| exit_code | 0 | raw 末尾 `exit_code: 0`(両走) |

- order11 の collect が数へた **17 collected** と、今回の実走 **17 passed** は**同数**である。
- 走行中の tree は不動(raw 末尾の `git status --porcelain 行数: 0`。raw file 自身は status 採取の後に書いた故 0 に数へられて居る=其の 1 点を明記する)。

## 節五 SKIP=FAIL 条への当て

令は「skipped≥1 なら SKIP=FAIL として『未完』と紙に書け(隠すな)」と命ずる。**両走とも skipped 0** ゆゑ、当席が「未完」と書くべき事象は**生じて居らぬ**。skip/skipif を新たに置いた数も **0**(file は X 版のまま・1 字も触れて居らぬ=sha256 が節一と節四で同値)。

## 節六 後始末 (令 step5・order13 同形)

- 退避: 上表 2 本を `scratch/ashigaru-third-2-fa06a3a1/raw_fa06a3a1/` へ写し、源と写しの sha256 を**両側で採り 2 組とも SAME**(消す直前に再検し 2/2 SAME)。写し先 dir の entry は **5**(order13 の 3 本 + 今回の 2 本)。**令外の file を写した数 0**。
- 削除: 樹内の未追跡 **2 本のみを名指しで** 消し(各 `exists=False`)、**再帰削除 0・glob 0・dir 削除 0**。直後の `status --porcelain` **0 行**。
- `git worktree remove /home/hakudoukai/a2/wt-fa06a3a1-xrun`(素) → exit **0**(**`--force` 0**)。
- `worktree list` **11 → 9**。当席が消したのは **1 本**のみ。残る 1 本の減は **A1 席の `audit-wt-281476` が同時に消えた**もので当席の業ではない(併せて `a1/wt-handover-fe` の commit 表示が `ee9c4b722`→`edb57fd94` へ動いて居る=他席の業)。
- `test -e /home/hakudoukai/a2/wt-fa06a3a1-xrun` → exit **1** = dir 不在。`cat-file -e a2-fa06a3a1-collect-fixed` → exit **0**。当席の樹は **1 本**(`wt-964a06d0-d3adf65b`・不触)。

## 節七 三択

- **測つた**: file sha256 の一致・接続の形(讀取)・前提 3 種の在否・list 11 と其の内訳・実走 2 走の summary 逐語/件数/exit・status 0 行・退避 2 組 SAME・名指し削除 2 本・素 remove exit 0・list 9・dir 不在・ref 健在。
- **測つて居らぬ**: 17 本の各 test が何を契約として検べて居るか(件数のみを採り、中身は讀んで居らぬ)。使ひ捨て cluster の後片付けが tempdir を残さず消したか(harness の finally に委ね、当席は確かめて居らぬ)。
- **測れぬ**: 本 raw が軍師 281088 の求める材として足るか否か ―― 之は上の判ずる事であり、当席の器では測れぬ。

## 節八 禁の遵守と、境の自己申告

- commit **0**・push **0**・remote 書込 **0**・X 枝への書込 **0**・共有 checkout(/mnt/c/DentalBI)への checkout/reset **0**(worktree add/remove は登録の増減であり、file を展いたのは自席 dir)。
- **本番/共有 DB への接続 0**。ただし**使ひ捨て cluster の中では harness 自身が DDL(CREATE DATABASE/CREATE EXTENSION/schema 作成)を打つて居る** ―― 令の「DDL 0」は共有・本番に対する禁と当席は読んだが、読み違ひで在れば正されたく、**隠さず此処に書く**。当該 DDL の宛先は tempdir 上の cluster のみで、走行後に `pg_ctl stop -m immediate` と `rmtree` で消える。
- 同じく harness は `tempfile.mkdtemp` で**当席 dir の外**(/tmp 配下)に一時 dir を作る。当席が作つた物ではなく test の振舞ひであるが、床⑾ の趣旨に照らし併記する。当席自身が書いた file は raw 2 本と本紙のみ(shell の追記 redirect は使つて居らぬ)。
- `--force` 0・`prune` 0・install 0・D 樹 `wt-964a06d0-d3adf65b` 不触・secret 値 0 字・患者本文 0 字。
- 判定語 0・先送り語 0・勧める語 0(件数と exit の逐語のみを記す)。

as_of: 2026-09-07T05:41:01+09:00
