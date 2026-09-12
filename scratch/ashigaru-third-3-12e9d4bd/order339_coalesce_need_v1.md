## §的 ★板 354dc26f の COALESCE 欠落は現に害を成すか ―― 走らせず DB に触れず字で測る★

## §A 頭（条㉝）―― 母の ref と path・as_of・網の逐語・器
- 母の ref（逐語）＝ origin/main ／ dir path（逐語）＝ /mnt/c/DentalBI ／ fetch は撃たず在る儘を讀んだ
- 定めの path（逐語）＝ supabase/migrations/20260909170000 snapshot live public functions.sql（blob16 8f53215dabd0b80f）／消費側の path（逐語）＝ backend/utils/abbreviation checker.py（278 行）
- ★己の測つた origin/main の tip16 ＝ 5722708374826c11（2026-09-12 14:18:26）―― 家老の先測 3cd79d339（14:01:54）とは ★別の commit★。母は本弾の間に進んだ。而して母五つは悉く当たつた ∴ 当該二 file は其の間に動いて居らぬ
- as_of ＝ 2026-09-12T14:25 ／ 當 repo の HEAD ＝ 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）
- > 網㊀函 ＝ 字面 CREATE OR REPLACE FUNCTION を含む行の数
- > 網㊁COALESCE と jsonb agg は ★行数と総出現を別々に★ 数へた（床30）
- > 網㊂包みの判 ＝ jsonb agg の在る行の ★直前行★ に字面 COALESCE が在るか
- 焚いた器（席 dir 内・★消さず残した★）＝ order339 probe.py（符 be0856b6b4efe2b8・焚 1）

## §㋐ 母五つを己の網で数へ直した（体系＝本紙 §A 網㊀㊁）
- ⑴snapshot の行数 ＝ ★1317★（wc の改行数。split 片は 1318）―― 家老の先測と当たつた
- ⑵函 ＝ ★24★（網㊀）―― 当たつた
- ⑶COALESCE ＝ ★行数 37／総出現 39★ ―― 家老の 37 は ★行数の側★ と当たつた。同じ行に二つ立つ所が二箇所在る
- ⑷jsonb agg ＝ ★行数 11／総出現 11★ ―― 当たつた
- ⑸字面 COALESCE の直後に jsonb agg が続く並び ＝ ★0★ ―― 当たつた

## §㋑ get_abbreviation_rules（L723-761）の中で NULL に成り得る key ＝ ★三つ悉く★
- official（L732）／corrections（L743）／detail required（L754）―― 三つとも jsonb build object の値が 裸の SELECT jsonb agg
- NULL に成る条件の型 ＝ 絞り込み（is active が真・in revision scope が真・detail required は更に requires detail が真）に当たる行が ★0 件★ の時。jsonb agg は 0 件で NULL を返す

## §㋑-2 同じ形（jsonb agg を裸で返す）を持つ函 ＝ ★1 本のみ★（体系＝§A 網㊂）
- 11 の jsonb agg の内 ★8 は直前行が COALESCE で包み既定値を持つ（悉く get_defense_checks）★・★裸は 3 つで悉く get_abbreviation_rules（L732・L743・L754）★
- ∴ 板の掲げる欠落は ★此の一函に固有★ である。★加へて家老の網㊄（字面 COALESCE の直後に jsonb agg）が 0 を返すのは「11 本とも裸」の意ではない ―― 8 本は改行を挟んで包まれて居る★

## §㋒ 消費側は NULL を受け止めて居るか ＝ ★⑵受け止めて居らぬ★（拠は行番と字の形のみ）
- L241-252 normalize rpc result ―― L245-247 は data.get(key, 既定の空の並び) の形。★既定は key が無い時にしか効かぬ★。定めは jsonb build object ゆゑ ★key は必ず在り値が null★ ∴ null が其の儘入る
- L236-238 empty rules は三 key を空の並びで作るが、L252 の道（dict でも 1 要素の並びでもない時）にしか達せぬ ∴ 本件の null には届かぬ
- 下流 ―― L81-83 は len を掛け・L171 は corrections を反復し・L220 は detail required を反復する ∴ null が入れば其の場で TypeError に成る

## §㋒-2 此の RPC を叩く口（体系＝識別子境界の網・repo 全体）＝ backend ★1 file★（abbreviation checker.py・口は L64 と L110 の二つ）／src・frontend ＝ ★0★／他の当たりは紙 4 本と定め自身のみ

## §㋓ 三値 ＝ ★⑴要る★
- 拠㊀定めの側 ―― 三 key は裸の jsonb agg ゆゑ 絞り込み 0 件で null を返す（§㋑）
- 拠㊁消費側 ―― L245-247 の既定は key が在り値が null の時に落ちぬ（§㋒）
- 拠㊂下流 ―― L81-83・L171・L220 が null を len に掛け或いは反復する（§㋒）

## §㋓-2 要件（三行以内・SQL は鋳らず patch も書かず GO も請はぬ）
- ㊀三 key の各 SELECT jsonb agg を既定値付きで包む事 ―― 同じ file の get_defense_checks が L781 他で既に同じ形を持つ
- ㊁或いは消費側 L245-247 を「key が在り値が null の時も既定へ落とす」形に改める事 ―― ㊀か㊁の一方で足る
- ㊂何れを採るにせよ 当てる先の ref と 絞り込みが 0 件に成る条件を先に名指す事

## §㋔ 残弾 ＝ 本弾の 1 を撃ち終へて ★0★。令430 に従ひ境界 clear で停まり次の令を待つ

## §禁語の網 ―― ㊀生 ＝ 1（下の一行のみ）／㊁境界の句と名を除いた数 ＝ 0
- > 網の語彙は令の側が渡した六語 password secret token api-key api_key credential

## §床の実績 ―― 走 0（pytest も psql も MCP も一度も起こさず）／DB 0（讀取も書込も 0）／MCP 0／製品 code 書込 0／supabase 書込 0／install 0／find 0／rm 0／ssh 0／git は讀取動詞のみ（fetch 0）／作業樹は開かず ref の値のみ／他席の箱 0／焚 1（器は席 dir 内・消さず残す）
