## §的 ★89 行の鎖の出口 7 つを 走らせず DB を讀まず 字の上だけで 一枚の表に閉ぢる★

## §頭
- 令 = scratch/k3_orders/order328_a3.txt ・符 445686e2fe53ba81（己が sha256sum の頭16 で刷り 家老の符と一致）・48 行(wc)/49 片・2660 byte
- 源 = 樹 /mnt/c/DentalBI ／ 符 7f39168d3（git の id ゆゑ sha1）／ backend/api/treatment_validation.py ／ 範 L4295-4383（89 行）。相対 1 = 絶対 4295。
- 引き方 = git -C /mnt/c/DentalBI show 7f39168d3:backend/api/treatment_validation.py を awk へ直結（一時 file 0・cd 0）。走 0・DB 0・apply 0。
- 讀取の打 = 8。席 = ashigaru-third-3 ／ 板 12e9d4bd ／ as_of 2026-09-12T09:57
- 當 repo の HEAD = 1ad4edfbadc69191183a42113e9979c3f91b7dbf（押しの前に rev-parse で當たつた）。digest の種 = 紙と器は sha256 の頭 16・源の 7f39168d3 は git の sha1。
- ★以下の逐語で 〔〕 は二重引用符を表す★ ―― 紙の門が生の二重引用符を許さぬ為であり、源には二重引用符が在る。

## §零 母の突き合はせ（家老が先に測つた・新条㉘ ∴ 撃ち直さず己の讀みと突き合はせた）
- 家老の母 = if 6 ／ elif 0 ／ else 0 ／ for 0 ／ return 4 ／ raise 3 ／ 出口 7（相対 30 40 43 59 60 74 75）／ 条件 6（相対 29 39 42 56 58 73）
- 己が 89 行を相対行で引いて當たつた所 ―― 出口 7 の相対行・条件 6 の相対行ともに ★悉く一致★。return は 30 40 59 74 の 4 本・raise は 43 60 75 の 3 本 ∴ 種の内訳も一致。
- ★何を一つと数へたか★ = 出口 ＝ 函から値が出る文（return 文と raise 文）を 1 つと数へた。復帰の道はもう一つ在る ―― 相対 31-37 の execute が投げる例外の伝播である。是は源に文として書かれて居らぬ（docstring 相対 24-27 が「fail-open 化せず そのまま呼び出し元へ伝播させる」と言ふ）∴ ★7 の中に数へて居らぬ★。

## §㋐㋑㋒㋓㋔ 出口の表（7 行・取り零し 0）

| ㋐出口(相対) | ㋑種 | ㋒返る物(逐語) | ㋓成り立つて居るべき条件の並び(相対) | ㋔入力の形(引数 3 つと 行の集合) |
|---|---|---|---|---|
| 30 | return | return None | 29 真 | set_code が偽（None か 空）。client と field_name は不問。★器を呼ぶ前に返る ∴ 行の集合は無関係★ |
| 40 | return | return None | 29 偽 ・39 真 | set_code が真値。execute が返した行が 0（相対 38 の resp.data or 空 list が 空）。field_name 不問 |
| 43 | raise | raise HTTPException status 409 ・condition = comment_documentation_no_active_row・detail に configured_row_count = 行の総数 | 29 偽 ・39 偽 ・42 真 | 行が 1 本以上在り ★其の悉くが 相対 41 の濾しで落ちる★（is_active が偽・NULL・鍵欠の何れか）。field_name 不問 |
| 59 | return | return matches[0].get(〔id〕) | 29 偽 ・39 偽 ・42 偽 ・56 真 ・58 真 | active 行が 1 本以上。field_name が真値。active 行の内 field_name が field_name と等しい物が ★丁度 1 本★ |
| 60 | raise | raise HTTPException status 409 ・condition = comment_documentation_identity_mismatch ・detail に resolved_count = 一致した本数 | 29 偽 ・39 偽 ・42 偽 ・56 真 ・58 偽 | field_name が真値。一致する active 行が ★0 本 か 2 本以上★ |
| 74 | return | return active_rows[0].get(〔id〕) | 29 偽 ・39 偽 ・42 偽 ・56 偽 ・73 真 | field_name が偽（None か 空）。active 行が ★丁度 1 本★ |
| 75 | raise | raise HTTPException status 409 ・condition = comment_documentation_identity_ambiguous ・detail に active_field_count = active の本数 | 29 偽 ・39 偽 ・42 偽 ・56 偽 ・73 偽 | field_name が偽。active 行が ★2 本以上★（42 偽ゆゑ 0 本は在り得ぬ・73 偽ゆゑ 1 本も在り得ぬ） |

- ★表が閉ぢて居る事の示し★ = 条件 29 で二分し 偽の側を 39 で二分し 其の偽の側を 42 で二分し 其の偽の側を 56 で二分し、56 真の側を 58 で・56 偽の側を 73 で二分する。分岐は悉く二分（elif 0 ・else 0）ゆゑ 葉は 1+1+1+2+2 = 7 つ。★網羅かつ排他★ ∴ 字の上で表は閉ぢて居る。
- ★但し 8 つ目の出方が在る★ = 相対 31-37 の execute が例外を投げた時。上の表の何れの葉にも落ちず 呼び出し元へ伝播する。∴ 「出口 7」は ★函が値を返す道の数★ であり ★函から制御が出る道の数★ ではない。

## §㋕ is_active が NULL の行は どの条件で落ちるか
- 相対 41 の逐語 = active_rows = [r for r in rows if r.get(〔is_active〕)]
- 濾しは ★python の真偽の取り方★ である ―― r.get が返した物を そのまま if で見る。∴ None ・False ・0 ・空文字 は ★悉く偽★ に成る。
- ★答 = NULL と False は 同じ扱ひに成る★。字の上で区別されて居らぬ。加へて 鍵 is_active を持たぬ行も r.get が None を返す ∴ ★欠鍵 ・NULL ・False の三つが 一つに潰れる★。
- 落ちる先 = 相対 41 の内包表記で active_rows に入らぬ。行の悉くが さうであれば 相対 42 が真と成り ★出口 43（409 ・no_active_row）★ へ落ちる。一部だけなら active_rows の本数が減るのみで、其の減り方が 58 や 73 の当否を動かす。
- 令326 で己が當たつた実測と繋がる ―― 源の列は L91 に is_active boolean DEFAULT true と宣言され ★NOT NULL が無い★ ∴ NULL の行は 現に在り得る。其の行は此処で非 active として扱はれる。

## §㋖ 令323 の移植 patch と 呼手紙の 2 打
- 己が當たつた事 = patch = scratch/ashigaru-third-3-12e9d4bd/order323_transplant_v1.patch・符 8f11b2f9b61998b9 ・100 行 ・追 91 削 0。当て先を示す行は ★1 本のみ★ で backend/api/treatment_validation.py を指す。∴ ★patch は呼手紙に一字も触れぬ★。
- ★測れなかつた事と 其の理由★ = 呼手紙 backend/tests/test_c1_dml_migration_pkg_isolated_harness.pyは 當 repo に 現に無い（git ls-files で 0 件・作業樹にも backend/tests が無い）∴ 樹は /mnt/c/DentalBI である。本令 ■五 の床は ★/mnt/c を 上記 1 file の git 讀取のみ★ に限り、其の 1 file は backend/api/treatment_validation.py である。呼手紙は名指されて居らぬ ∴ ★床の内では引けぬ★。
- ∴ 「呼手紙の L641 L642 の 2 打が 7 つの出口の何れに触れるか」「触れぬ出口の数」は ★現に測定不能★。★床を超えて引く事はせず 家老へ上げる★（令の ■四 ㋖ と ■五 の床が 現に噛み合つて居らぬ）。
- 己が前弾で讀んだ呼手紙の逐語（相対 L295-341 の偽の三体）は手元に在るが、L641 L642 は其の範に入つて居らぬ ∴ ★確かめて居らぬ★。推し量りで埋めて居らぬ。

## §㋗ 二つの別（條四百九十六）
- ★「此の表が字の上で閉ぢて居る」と「実の DB を相手にさう振舞ふ」は 二つの別の主張である★ ―― 前者は源 89 行の分岐を數へただけであり、後者は 実の列の型 ・NULL の実在 ・器が返す物の形 を要する。本弾は DB を一度も讀んで居らぬ ∴ 後者は 現に測定不能。

## §㋘ 禁語（網は令328 が渡した 5 つ）
- > 網の語彙: password secret token api-key api_key credential
- ㊀ 生（網を掛けた儘・★己の境界宣言行と 直上の語彙行を含む★）= 1 件
- ㊁ 境界の句と名を除いた数 = 0 件。除く形 = 行頭が 半角ハイフン 空白 大なり 空白 の行（語彙を並べた行）を落とす。
- 併せて席の門の網（17 語）でも數へた: 生 1 件 ／ 除 0 件。★二つの網は語彙が違ふ ∴ 数も違ふ★

## §㋙ 残弾
- 令327 で 10 と書いた。本弾で 1 本使ひ 現に 9 本。
- 繰越（生きて居る）= 令323 の patch 8f11b2f9b61998b9 は未だ當てて居らぬ ／ 令297 の 67db351e5480d002 と 令300 の dbf36ed5cf1c50fa は同じ足す先を争ひ 二本とも未だ當てて居らぬ ／ 令284 の 7ab363530dbc122b は未押し ／ 実の DB の列の型と NULL の実在は DB 0 の床の下では 現に測定不能 ／ ★本弾の ㋖ は床の外ゆゑ 家老の裁を待つ★

## §結（三択語で結ぶ）
- 出口 7 つと 条件 6 つ = 現に在る（家老の母と悉く一致）。
- 表の網羅と排他（字の上）= 現に在る（葉 7 つ・elif 0 ・else 0）。
- 函から制御が出る 8 つ目の道（例外の伝播）= 現に在る（文としては書かれて居らぬ）。
- NULL と False の区別 = 現に無い（相対 41 で一つに潰れる）。
- 呼手紙 2 打が触れる出口 = 測定不能（本令の床が /mnt/c を 1 file に限る）。
- 実の DB での振舞ひ = 測定不能（DB 0）。
