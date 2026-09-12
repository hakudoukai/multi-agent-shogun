## §的 ★此の PC の容量圧を 既存器で 1 回讀み 数を出し 其の数が何を意味せぬかを名指す★

## §頭
- 令 = scratch/k3_orders/order327_a3.txt ・符 204438153f83918a（己が sha256sum の頭16 で刷り 家老の符と一致）・54 行(wc)/55 片・3325 byte
- 讀んだ物 = 器 1 本(402 行)・令 1 枚(54 行)・生出力 1 枚(24 行)。讀取の打 = 25。走 = 1（--report のみ・他 MODE 0 打）。
- 席 = ashigaru-third-3 ／ 板 12e9d4bd ／ as_of 2026-09-12T09:50
- 當 repo の HEAD = 1ad4edfbadc69191183a42113e9979c3f91b7dbf（押しの前に rev-parse で當たつた）
- digest の種 = sha256 の頭 16。git の id は sha1 ゆゑ 是と混ぜて居らぬ。

## §零 器の身元（己が刷り 家老の母と突き合はせた・新条㉘ ∴ 撃ち直さず）
- 器 = scripts/sweeps/audit_disk_pressure.sh ・符 94fe338d2e1beafd ・402 行(wc)/403 片 ・25420 byte ・-rwxr-xr-x ―― 家老の母と悉く一致。
- 讀取専の裏付（己が當たつた・網の形を数と同じ行に書く）:
  - 網㋐ 書込の動詞 `(^|[^A-Za-z0-9_])(rm|mv|cp|tee|touch|mkdir|chmod|chown|dd|truncate|gzip|xz|fstrim|prune|ln)([^A-Za-z0-9_]|$)` を 註釈行(`^[[:space:]]*#`)を除いた行へ掛けて 0 件。註釈を含めると 1 件（L5）。
  - 網㋑ 外部送信 `(ssh|scp|curl|wget|nc)[[:space:]]` を 註釈を除いた行へ掛けて 0 件。
  - 網㋒ 落とし口 `>>?[[:space:]]*[A-Za-z0-9$/.]` を全 402 行へ掛けて 4 件（L111・L240・L290・L394）。逐語で當たると 4 件は悉く 2>/dev/null ＝ 誤りの捨て場であり、file を作る落とし口は 現に無い。
- 家老の便は「書込語の当たりは 4 件あるが悉く註釈（L5・L86・L202・L205）」と言ふ。己の二つの網では L5 の 1 件しか當たらぬ。★因は数の違ひではなく 網の語彙の違ひである。家老の網の語彙を己は知らぬ ∴ 4 件の内訳は確かめて居らぬ★

## §㋐ 走らせた語と rc
- 逐語 1 行 = bash scripts/sweeps/audit_disk_pressure.sh --report
- 起こし方 = python3 の subprocess で 1 回のみ。stdout と stderr を別の口で受けた。
- rc = 0。∴ selftest 二段は立つた（L354・L358 の ABORT は出て居らぬ）。
- stderr = 452 byte ・3 行。器で 2>&1 の右辺へ落とす行（stderr へ吐く行）は 13 本在り、内 11 本は selftest 二段の開示行である。★3 行が何れの行かは 逐語を刷らずに失つた ∴ 確かめて居らぬ★

## §㋑ 生出力
- path = docs/evidence/order327_disk_pressure_report_20260912.txt（docs/evidence を新設した）
- 総行 = 24 行(wc) / 25 片(split) ・2856 byte
- 符 = 6f4bfdca789e4f58（sha256 の頭 16・書いた後に disk から刷り直して一致）
- 器が入れた as_of（出力の中の値）= 2026-09-12T09:47:11+09:00

## §㋒ 種別ごとの数（行頭の第一語で分けた・24 行を悉く分けた＝取り零し 0）
- DISKPRESS = 1 行
- DISKUNMEASURED = 19 行
- DISKUNMEASURED_SUMMARY = 1 行
- SUMMARY = 1 行
- NOTE = 2 行
- 合計 = 1+19+1+1+2 = 24 行 ＝ 生出力の本文の行数と一致（取り零し 0）
- 19 の内訳（己が生出力の逐語を數へた）= 此の PC の mount で飛ばした物 16 ＋ 他 PC 3（main・second・mac、why=no_route_not_requested）。器の SUMMARY 行も pc_unmeasured=3 ／ local_skipped=16 と出し 両者は一致する。

## §㋓ 此の数が何を意味せぬか
- ㋓1 pc_measured=1 は「此の PC のみを測つた」の意であり、残 3 台は unmeasured である（0 ではない）。器自身が末行の NOTE で其れを言つて居る。∴ 「艦隊 4 台の容量を測つた」とは書けぬ。
- ㋓2 母は二つ在り 足して居らぬ ―― PC の母数 4 と 此の PC の mount の母数 18。19 行の unmeasured は 3（PC）と 16（mount）の和であり、★二つの母を跨ぐゆゑ 一つの率の分子には使へぬ★
- ㋓3 DISKPRESS=1 は「閾を超えた mount が 1 本」の意であり「容量が尽きかけて居る」の意ではない。逐語 = target=/ ・total_gib=1006 ・used_gib=283 ・pct=28 ・reason=abs。閾は L104-105 に DP_PCT_MAX 既定 85 ・DP_ABS_MAX_GIB 既定 80。★pct 28 は 85 に達して居らぬ。當たつたのは絶対量の閾 80 GiB のみである★
- ㋓4 1006 GiB の盤では 80 GiB は全体の 8 分に當たる ∴ 此の絶対閾は 使用が 8 分を超えた盤では常に當たる。是は「此の盤に固有の事」を言ふ数ではない。
- ㋓5 SUMMARY の exceeded=1 と DISKPRESS の 1 行は ★同じ一つ★ である（二つの数ではない）。
- ㋓6 local_mounts_seen=18 は df が並べた行の数であり、判定へ掛けた mount の数ではない。判定へ掛けたのは 18 引く 16 で 2 本 ―― ★此の引き算は己がした。器は「判定へ掛けた数」を出して居らぬ★。内 閾に當たつたのが 1 本 ∴ 當たらなかつたのが 1 本。
- ㋓7 是は一点の測りであり 増え方は測つて居らぬ（--growth は 0 打）∴ 「日に何 GiB 増えるか」は 測定不能。

## §㋔ 禁語（網は令327 が渡した 5 つ）
- > 網の語彙: password secret token api-key api_key credential
- ㊀ 生（網を掛けた儘・★己の境界宣言行と 直上の語彙行を含む★）= 1 件
- ㊁ 境界の句と名を除いた数 = 0 件。除く形 = 行頭が 半角ハイフン 空白 大なり 空白 の行（語彙を並べた行）を落とす。
- 併せて席の門の網（判定 13 語 ＋ 1 語 ＋ 先送 3 語 ＝ 17 語）でも數へた: 生 1 件 ／ 除 0 件。★二つの網は語彙が違ふ ∴ 数も違ふ★

## §㋕ 残弾
- 令326 ㋔で 11 と書いた。本弾で 1 本使ひ 現に 10 本。
- 繰越（生きて居る）= 令323 の patch 8f11b2f9b61998b9 は未だ當てて居らぬ ／ 令297 の 67db351e5480d002 と 令300 の dbf36ed5cf1c50fa は同じ足す先を争ひ 二本とも未だ當てて居らぬ ／ 令284 の 7ab363530dbc122b は未押し ／ 令326 ㋔の内 1 本＝実の DB の列の型と NULL の実在を當てる件は DB 0 の床の下では 現に測定不能。

## §結（三択語で結ぶ）
- 此の PC の mount で 絶対量の閾に當たる物 = 現に在る（1 本・reason=abs・used_gib=283）。
- 率の閾（85）に當たる物 = 現に無い（此の PC の最大は 28）。
- 他 3 台の容量圧 = 測定不能（why=no_route_not_requested・路を引いて居らぬ）。
- 増え方（日に何 GiB か）= 測定不能（--growth 0 打・二点を持たぬ）。
- 器が file を作る事 = 現に無い（落とし口 4 件は悉く 2>/dev/null）。
