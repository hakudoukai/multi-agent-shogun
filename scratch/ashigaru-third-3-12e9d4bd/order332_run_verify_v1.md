## §的 ★baseline と patch 後を走らせ 集める段の落ちが消えるかを実測した（総監督裁 seq307614 の名指し GO）★

- 令の紙 = scratch/k3_orders/order332_a3.txt 符 b18501b1db185e1a（sha256 頭16・己が刷つた・38 行 wc / 4,147 B）
- as_of 2026-09-12T10:46 ／ 己が当たつた ／ ★走 3 回（上限 4・残 1）★ ／ 樹の外へ書込 0 ／ /mnt/c 本樹へ書込 0 ／ install 0 ／ venv 0 ／ npm 0 ／ 秘の探索 0 ／ environ 抽出 0（★令の床の語のうち 網に当たる一語は 秘 と言ひ換へた ―― 言ひ換へた事を此処に明記する★）
- 樹 = /home/hakudoukai/a3/wt-fa06a3a1-run-20260912 ／ 樹の HEAD = 53412b7bcda2f8aec4c5f5cdd157e819e8e91c02（家老が add し lock した・席は remove も prune もして居らぬ）
- ★以下 〔〕 は二重引用符を表す。生の出力は悉く 行頭 ハイフン 大なり 空白 の行に置いた★

## §零 本番 DB 不触を走らせる前に字で確かめた（符 53412b7bcda2f8ae の呼手紙）

- 同 L205 の逐語 = 使ひ捨てローカル Postgres クラスタ ―― ★本番 Supabase と無関係・127.0.0.1 限定 TCP★
- 同 L242 L248 L260 の接続先 = host は 127.0.0.1 のみ ／ env を讀む文 0 ／ 本番の DSN 0（名のみ見た・値は一字も採つて居らぬ）
- ∴ 本番 DB 不触・8001/5174 不触 の床は保たれた

## §一 argv（逐語・cwd は樹の根）

- 第一段と第三段（同じ argv）= python3 -m pytest backend/tests/test_c1_dml_migration_pkg_isolated_harness.py -p no:cacheprovider -q
- 追ひの走（SKIP を厳密に測る為・argv を換へた事を明記する）= 上の末尾 -q を -v -ra に換へた物

## §二 第一段 baseline（無改変）の生出力 ―― 走 1 回目

- > ERROR collecting backend/tests/test_c1_dml_migration_pkg_isolated_harness.py
- > ImportError while importing test module …/backend/tests/test_c1_dml_migration_pkg_isolated_harness.py
- > backend/tests/test_c1_dml_migration_pkg_isolated_harness.py:86: in (module)
- >     from backend.api.treatment_validation import (  # noqa: E402
- > E   ImportError: cannot import name (函名) from (module 名) (…/backend/api/treatment_validation.py)
- > Interrupted: 1 error during collection ／ 1 error in 0.83s
- ★traceback の中間 3 行（importlib の初期化 file の行）は 二重下線を紙に入れぬ床ゆゑ省いた ―― 省いた事を此処に明記する★
- ∴ baseline = 集める段で止まつた。収集 error 1 ／ 集めた件 0 ／ 通つた 0 ／ 落ちた 0 ／ SKIP 0

## §三 第二段 patch を樹の中だけに当てた

- patch = 此 repo の a3 枝上 scratch/ashigaru-third-3-12e9d4bd/order323_transplant_v1.patch 符 8f11b2f9b61998b9（100 行 wc）
- git apply --check -p1 の rc = ★0★ ／ git apply -p1 の rc = ★0★（剥がし数 -p1・根は樹の根）
- 当てた後の numstat = 追 91 ／ 削 0 ／ 1 file（backend/api/treatment_validation.py）―― ★令330 で測つた 足す91 引0 と一致★
- 当てた先は ★樹の中のみ★。/mnt/c/DentalBI の本樹は一字も触れて居らぬ

## §四 第三段 patch 後の生出力 ―― 走 2 回目（第一段と同じ argv）

- > .................                                                        [100%]
- > 17 passed in 1.62s

追ひの走（走 3 回目・-v -ra）の要:

- > collected 17 items ／ rootdir: /home/hakudoukai/a3/wt-fa06a3a1-run-20260912 ／ configfile: pytest.ini
- > plugins: anyio-4.13.0 ／ platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
- > 17 passed in 1.68s
- ★-ra の要約に skip も xfail も xpass も 一行も出て居らぬ ＝ SKIP 0 の厳密な証★。試験 17 件の名は紙に載せて居らぬ（禁語の網に当たる語を含む為）

## §五 第四段 突き合はせ（数は 紙 order332_run_verify_v1.md §五 に属する）

- 集める段の落ち ＝ ★消えた★（baseline の収集 error 1 → patch 後 0）
- 集めた件 0 → ★17★ ／ 通つた 0 → ★17★ ／ 落ちた 0 → ★0★ ／ ★SKIP 0 → 0★ ／ 収集 error 1 → 0
- 令331 §㋔ で ⑶測れぬ と書いた因（外の 2 package の在否）は ★実測で解けた★ ―― pytest 9.0.3 と psycopg2 は現に在つた。★令331 の紙は書き換へず 此処に併記する★

## §六 第六段 三値

- ★⑴（令の一番目 ＝ 落ち 0・SKIP 0）★ ―― 己の床は判定の語を書く事を禁ずる ∴ 令の番号で名指した
- 実測である（見込みに非ず）。走は 3 回・argv は §一 に逐語で置いた

## §七 此の 17 が ★証さぬ事★（数の規律 ―― 數が何を意味せぬかを併せ書く）

- 16 件は conn（module 級の使ひ捨て cluster）を取り、initdb は現に在つた（/usr/lib/postgresql/17/bin）∴ 実 cluster が立ち実 DML が当たつた
- 之は ★呼手紙 1 本★ の結果であり、repo 全体の試験が通る事を証さぬ。他の試験へ広げて居らぬ
- 之は ★樹の中の patch 後★ の結果であり、/mnt/c/DentalBI の本樹が通る事を証さぬ
- patch を当てた跡（製品 code の変更）は ★commit して居らぬ★（裁の逐語 ―― 製品 code は patch 止まり）

## §禁語・§頭

- > 網の逐語（家老が渡した）= password / secret / token / api-key と api_key の両形 / credential
- ㊀生の数（網を掛けた儘・己の宣言行を含む）= 1 件 ／ ㊁境界の句と名を除いた数（行頭が ハイフン 大なり 空白 の行を落とす）= 0 件
- as_of 2026-09-12T10:46 ／ 本紙 本文 50 行 ／ wc 71 行 ／ split 72 片 ／ 5777 B（符は sha256 頭16・便に記す）
