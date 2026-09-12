## §的 ★板 354dc26f の受入（3鍵に COALESCE）を patch に鋳る ―― 当てず・適用せず・GO の門へ出せる形にする★

## §A 頭（条㉝）―― 母の ref と path と樹・as_of・網の逐語・器と patch
- 母の ref（逐語）＝ origin/main ／ 定めの path（逐語）＝ supabase/migrations/20260909170000_snapshot_live_public_functions.sql（1317 行・split 片 1318）／fetch は撃たず在る儘を讀んだ
- 樹（逐語・令が名指した）＝ /home/hakudoukai/a1/wt-handover-fe-2（HEAD ＝ dcf30da8d1c1da09f8c24e49bb5087fdef84bd61・status の変はり ＝ 0 ―― ★一字も触れて居らぬ★）
- as_of ＝ 2026-09-12T14:45 ／ 當 repo の HEAD ＝ 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）
- > 網㊀函の行域 ＝ 字面 CREATE OR REPLACE FUNCTION の行から 次に来る 字面 $function$; のみの行まで
- > 網㊁包みの判 ＝ jsonb agg の在る行の直前行に字面 COALESCE が在るか（令339 と同じ網）
- 焚 1 ＝ 器 order340_probe.py（符 sha256 先16 ＝ 8034f0107f4a28fe・4,163 B・席 dir 内に残す）
- patch ＝ order340_coalesce_3keys.patch（★席 dir 内★・符 sha256 先16 ＝ bac29134242ea12e・1,936 B・patch 48 行／中の SQL 43 行）

## §零 令340 v1 の撤を受けた（★家老の紙の逐語を写した ―― 己は当たつて居らぬ★・床⑸）
- 家老の紙が掲げる取消の理由 ＝ 差 73 は網の性質であり害では無い（拠に A1 F5-342・紙 f5_342_rpc_presence_v1.md 33 行 符 0d48a536e1cecd40 を挙げる）
- ★己は F5-342 の紙を讀んで居らぬ ∴ 確かめて居らぬ★（作法六条目）。本紙は v2 の芯のみを果たす

## §㋐ 三鍵の現在の定義を行番で引き直した（体系＝本紙 §A 網㊀・母は §A の snapshot）
- 頭註 ＝ L722（字面 -- ===== で始まる一行）／CREATE ＝ L723 ∴ ★隔たりは 1 行（間に空行は無い）★
- 函の尻 ＝ L761（字面 $function$; のみの行）∴ 函の行域 ＝ ★L723-L761（39 行）／頭註込みなら L722-L761（40 行）★
- 三鍵の jsonb agg ＝ L732（official）・L743（corrections）・L754（detail required）―― ★直前行に字面 COALESCE は三つとも無い★
- 正対照の字の形 ＝ L781 が 鍵名に続けて COALESCE と二重の開き括弧／L792 が 閉じ括弧に続けて 空の並びの既定値と jsonb への型付け

## §㋑ patch の形は二択の ★⑴函を CREATE OR REPLACE で丸ごと置き直す★ を選んだ
- 拠㊀ ★postgres は函の本体を部分置換出来ぬ★ ―― 三行だけ替へる形は定めの file の字を替へるのみで DDL に成らぬ
- 拠㊁ 20260909170000 は既に着地して居る ∴ 其の file を書き替へる形は 着地済の紙を後から替へる事に成る
- 拠㊂ 丸ごと置き直す形は snapshot 自身と同じ書き振りであり 正対照 get defense checks の包みの字を其の儘移せる
- ★刻★ ＝ 新 file の名を 20260912150000_get_abbreviation_rules_coalesce.sql に置く ―― 20260909170000 より ★字の並びで後★ ∴ 板の依存の逐語（snapshot 板の着地後）を満たし 同一函数を二度定義しない順に成る
- 現在の migrations の刻の尻（体系＝origin/main の ls-tree）＝ 20260909170000 ∴ 20260912150000 は ★既存の何れよりも後★

## §㋑-2 patch の置き所 ―― ★席 dir 内の file 一本のみ★。supabase/migrations へは file を一本も作つて居らぬ（新 file は patch の中の字としてのみ在る）
- apply --check ＝ ★2 回・上限通り★（條四百九十三に従ひ根と剥がし数を同じ行に）―― 根 ＝ /home/hakudoukai/a1/wt-handover-fe-2 ・剥がし数 -p1 → rc=0 ／ 根 ＝ /mnt/c/DentalBI ・剥がし数 -p1 → rc=0
- ★--check を伴はぬ git apply は一度も撃つて居らぬ★

## §㋒ 負テスト（該当行 0 の日の呼出が落ちぬ）は ★python 側で書ける★（本紙は設計のみ・file を新設せず・走らせて居らぬ）
- 足す先の path（逐語）＝ tests/test_abbreviations.py（140 行・試験関数 7 本・L22-L28 で消費側から 5 つの名を引く）
- 既に在る足場 ＝ L54-L58 の fixture setup cache が set cache へ模擬の辞書を渡し L59 で clear cache へ戻す
- 設計 ＝ 同 file に一本足し ★三鍵の値を null に置いた辞書★ を set cache へ渡した上で check unofficial abbreviations と check disease abbreviation detail を呼び 落ちぬ事を見る
- 拠 ＝ 令339 の断（覆ひ無しの反復は L171 と L220）∴ SQL 側ではなく python 側で当たる。DB も RPC も要らぬ
- ★SQL 側の層で書く道は 該当行 0 の日を作る為に行を消すか日付を動かす要が有り DB 0 の床の下では測れぬ★

## §㋓ 三値 ＝ ★⑴成つた★ ―― patch は席 dir 内に在り・両根で --check rc=0・supabase 配下へ file を作らず・GO の門へ出せる形に在る

## §㋔ 残弾（撃たずに名だけ）＝ ★0★。令430 に従ひ境界 clear で停まり次の令を待つ

## §禁語の網 ―― ㊀生 ＝ 1（下の一行のみ）／㊁境界の句と名を除いた数 ＝ 0
- > 網の語彙は令の側が渡した六語 password secret token api-key api_key credential

## §床の実績 ―― 焚 1／走 ＝ git apply --check のみ 2 回（上限通り）／DB 0／MCP 0／製品 code 書込 0／supabase 配下へ書込 0／install 0／find 0／rm 0／ssh 0／git は讀取動詞のみ（fetch 0）／患者の字 0／鍵の個々の値 0／他席の樹は讀取と --check のみで status の変はり 0／他席の箱 0
