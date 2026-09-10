# 令284 fa06a3a1 ―― 境界の続きと ③-㋐ の patch v1

## §的 ★的一行★
③-㋐（module 頂の import を 呼出の在る函の中へ移す形）は ★patch として現に鋳れた★ ―― 24 行・apply --check の rc は 0。而して 283 の境界の符 db86b2099 は ★的の樹の HEAD の祖先に非ず（merge-base --is-ancestor の rc は 1）★ であり、其の符は同じ疵を ★import と test_10 を丸ごと削る形★ で既に直して居る ∴ ③-㋐ は ★同じ疵への二つ目の道★ である。

## §A 頭（何時・何を・幾つ讀んだか）
- as_of 2026-09-11T07:40:38+0900。的の樹 `/mnt/c/DentalBI`（HEAD `53412b7bcda2f8aec4c5f5cdd157e819e8e91c02`）。當 repo multi-agent-shogun の HEAD `1ad4edf` は不動・押しは打たぬ（本令は push 0）。
- 讀んだ物 = 符 1 本（db86b2099）・blob 1 本の二領域（80〜95 と 628〜652）・當該 file の numstat 1 本・祖先の可否 1 本・HEAD 1 本。★git 讀取の打数 = 10（上限 20・★数へながら打つた★）★。焚 2（紙 1・patch 1）。
- 禁の遵守 ―― backend へ一字も書かず・/mnt/c へ書かず・pytest 0・走 0・当てる 0・push 0・fetch 0・find 0・rm 0。

## §B 符 db86b2099 の中身（3 行）
- 題「test(backend): restore isolated harness collection」・刻 2026-09-05 15:15:05 +0900・全 `db86b2099c1faa593b0aa2ceb90af2915c842fd1`。name-only は 3 紙 ―― 當該 test file・下記の紙 1 本・`requirements.txt`。
> reports/drx-backend-isolated-harness-collection-green-20260905.md
- 當該 test file への効き = ★追加 12・削除 72★。削つた行の中に ㋐ module 頂の import 2 行（`from backend.api.treatment_validation import (` と 其の名の行）㋑ test_10 の中の呼出 2 行 が現に在る ∴ 其の符は ★名を丸ごと外す形★ で collect を直して居る。
- ★而して 其の符は的の樹の HEAD の祖先に非ず（rc は 1）★ ∴ 其の直しは HEAD には載つて居らぬ。「消えた」とは書かず ★HEAD からは見えぬ★ と書く（條 四百九十六）。

## §C ③-㋐ の patch（★当てて居らぬ★）
- 紙名 `scratch/ashigaru-third-3-12e9d4bd/order284_third_a_import_localize_v1.patch`・★24 行（wc）／25 片（split）★・sha256 頭16 `7ab363530dbc122b`（床(32)・釘83）。
- hunk ㊀ `@@ -83,10 +83,6 @@` ―― module 頂の import 3 行と其の後の空行 1 行を削る（計 4 行）。
- hunk ㊁ `@@ -637,6 +633,10 @@` ―― test_10 の説き書きの直後・呼出 2 箇所の直前へ 局所の import 3 行と空行 1 行を入れる（計 4 行）。
- ★anchor は実物で確かめた（床(28)）★ ―― 行番号を打ち込まず `from backend.api.treatment_validation import (` と `    fake_client = _FakeSupabaseClient(conn)` の逐語で当て、其の前後の行を assert で當てた上で鋳た。差分は difflib が組んだ ∴ hunk の頭の数は器が数へた（己が手で写した数ではない）。
- 註 ―― 頂に在つた `# noqa: E402` は函の中では要らぬ ゆゑ 局所の import には付けて居らぬ。之は形の判断であり測つた数ではない。

## §D apply --check の rc（1 打・当てぬ）
- 打つた形 = `git -C /mnt/c/DentalBI apply --check -p1 <patch の絶対 path>`。★rc は 0★。
- 根 = `/mnt/c/DentalBI`・剥がし数 = `-p1`（條 四百九十三 に依り 根と 剥がし数を同じ行に書く）。patch の path 側は `a/backend/…` `b/backend/…` の形ゆゑ 剥がしは 1 枚。
- 之は ★当たるか否かの一点のみ★ を測つた数である。当てて居らぬ・製品の挙動は一字も動いて居らぬ。

## §E collect 一回走の願ひ（3 行・★本令では走らせぬ★）
- ㋐ 何を打つか ―― 的の樹で `python3 -m pytest --collect-only backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` を ★1 打★・上限 120 秒・的は當該 file 一本のみ。
- ㋑ 何を書かせぬか ―― `-p no:cacheprovider` で pytest の cache 帯を作らせず、環境変数 `PYTHONDONTWRITEBYTECODE=1` で byte 譯の帯（下線二つで挟む pycache の名の帯）を作らせぬ ∴ 的の樹へ file を一つも残さぬ。DB 0・書込 0。
- ㋒ 何が判るか ―― collection error の件数が 0 か否か 其の一点のみ。板の逐語「1 件」は ★家老の便からの写しで己は確かめて居らぬ★ ゆゑ、之を己の目の数に変へる為の走である。家老が監督へ運ぶ。

## §F 見込みと実測の別
- ★実測★ = §B の 題・刻・name-only 3 紙・numstat 12/72・祖先の rc 1／§C の 24 行と sha／§D の rc 0。悉く己で当たつた。
- ★見込み★ = ③-㋐ が collection error を 0 にする事（走らせて居らぬ）・db86b2099 の直しを HEAD へ持ち来る道の有無（測つて居らぬ）・二つの道の何れを採るかの裁（席の分ではない）。
- ★確かめて居らぬ★ = 板 fa06a3a1 の逐語・collection error の件数・總監督裁 280975 の中身（悉く家老の便からの写し）。的の樹の作業樹の改行の形も測つて居らぬ ―― apply --check が rc 0 で通つた事のみが実測である。
- 完全 SHA256 ―― patch `7ab363530dbc122bd2dae34dd0173ac5629643aaa2507ff6ad1bdfc038c86175`／符 `db86b2099c1faa593b0aa2ceb90af2915c842fd1`／的の樹の HEAD `53412b7bcda2f8aec4c5f5cdd157e819e8e91c02`。本紙自身の sha は書き終へた後に測り 復命の便に載せる。
