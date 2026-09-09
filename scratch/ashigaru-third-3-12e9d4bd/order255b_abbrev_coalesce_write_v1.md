# order255b / 割込・優先1 ―― 書いた 2 file の帳（SQL と 0 行の日の負テスト）

## §的 ★的一行★

★家老の裁に依り床が解かれた 2 file のみを鋳た ―― ⑴ 3 鍵すべてに COALESCE を置いた新規 migration ⑵ 0 行の日に「取得失敗」が出ぬ事を当てる負テスト 1 本（陽性対照 1 本を同梱）。★走らせては居らぬ★。★

## §零 帳の頭

- as_of ＝ 2026-09-09T18:21:40+09:00
- 前紙（讀取実測） ＝ scratch/ashigaru-third-3-12e9d4bd/order255_abbrev_null_read_v1.md（182 wc / 183 split / 14,395 B / sha16 46152ca5c21c742a）―― ★書き換へて居らぬ★
- 樹 ＝ ★/mnt/c/DentalBI（作業樹・LF・枝 wp-a1-a3-3-20260723）★
- 費消 ＝ 走 0（★製品走 0・残 1 不変★）／焚 0（本弾）／DB 0
- ★触れた file ＝ 新規 2 本のみ★。★既存 backend/* は一字も触れて居らぬ★（abbreviation_checker.py の sha16 df0372835bef5893 は §三 に再掲）
- ★DDL を己で適用して居らぬ★（適用は総監督殿が MCP にて）

## §一 ⑴ SQL ―― 3 鍵の何処に COALESCE を置いたか（一行づつ）

path ＝ ★supabase/migrations/20260909183000_fix_get_abbreviation_rules_coalesce.sql★（91 wc / 92 split / 4,627 B / sha16 d172d02775975a09）

| 鍵 | 置いた行 | 形 | 源 |
|---|---|---|---|
| ★1/3 official★ | ★L33-L34★ | `COALESCE( (SELECT jsonb_agg(jsonb_build_object(...)) FROM public.official_abbreviations WHERE is_active IS TRUE), '[]'::jsonb )` | official_abbreviations |
| ★2/3 corrections★ | ★L55-L56★ | `COALESCE( (SELECT jsonb_agg(jsonb_build_object(...)) FROM public.abbreviation_corrections WHERE is_active IS TRUE), '[]'::jsonb )` | ★abbreviation_corrections（本件の当該鍵）★ |
| ★3/3 detail_required★ | ★L74-L75★ | `COALESCE( (SELECT jsonb_agg(abbreviation) FROM public.official_abbreviations WHERE is_active IS TRUE AND requires_detail IS TRUE), '[]'::jsonb )` | official_abbreviations.requires_detail |

- 頭（L1-L25）に ★因の道筋★ を L246 → L82 → L88 の順で書いた（前紙 §三 と同じ道）。
- 函の形 ＝ `CREATE OR REPLACE FUNCTION public.get_abbreviation_rules() RETURNS jsonb LANGUAGE sql STABLE`。
- COMMENT ON FUNCTION と GRANT EXECUTE（anon / authenticated / service_role）を末に置いた。

### ★適用者へ渡す 三つの断り（file の註 1〜3 に同文を置いた）★

1. `is_active` は `BOOLEAN DEFAULT true` にして ★NOT NULL ではない★ ∴ 本函は `is_active IS TRUE` で絞る（NULL は不活性として扱ふ）。★現行の函が別の絞り方をして居た場合、其の差は此処に現れる★。
2. ★現行の函の戻り値型が jsonb でない場合、CREATE OR REPLACE は通らぬ（DROP が要る）★ ∴ 適用の前に `pg_get_functiondef` で現行定義を確かめられたし。
3. ★当席は DB を讀む口を持たず、現行の函本体を確かめて居らぬ★。戻り値の形は abbreviation_checker.py の docstring（L40-L45）と `_normalize_rpc_result`（L241-L248）から起こした ―― ★之は推し量りであり 実測に非ず★。

## §二 ⑵ 負テスト ―― 何を当てたか

path ＝ ★backend/tests/test_abbreviation_rules_coalesce.py★（208 wc / 209 split / 6,701 B / sha16 fe98ccb853d61e45）

| # | 当ての名 | 何を当てるか |
|---|---|---|
| 1 | test_migration_file_exists | migration が現に在る |
| 2-4 | test_migration_wraps_each_key_in_coalesce（3 鍵で parametrize） | ★3 鍵それぞれの直後に COALESCE と '[]'::jsonb が在る★ |
| 5 | test_migration_creates_or_replaces_the_rpc | CREATE OR REPLACE FUNCTION public.get_abbreviation_rules() が在る |
| ★6★ | test_zero_row_day_sync_returns_three_empty_lists | ★0 行の日（3 鍵とも []）に 同期版が 3 鍵の空配列を返し ログに「取得失敗」が出ぬ★ |
| ★7★ | test_zero_row_day_async_writes_no_failure_line | ★同・非同期版（★本件の芯★）★ |
| 8 | test_zero_row_day_cache_is_not_poisoned | ★cache の 3 鍵が悉く空配列★（前紙 §三 段四・七の毒が残らぬ） |
| 9 | test_zero_row_day_checker_returns_empty_without_raising | `check_unofficial_abbreviations` / `check_disease_abbreviation_detail` が ★投げずに空を返す★ |
| ★10★ | ★test_positive_control_null_payload_does_write_failure_line★ | ★陽性対照★ ＝ 直し前の応答（corrections が null）では ★現に「取得失敗」が出る★ |

- ★10 を置いた理★ ＝ 己の條（段 19・20 の対）に従ふ。★6・7 が「出ぬ」を当てる以上、「出得る」事を同じ file で示さねば、6・7 は ★何も守つて居らぬ★ 当てに成り得る。
- DB へは ★一切繋がぬ★ ―― `ac.httpx.Client` / `ac.httpx.AsyncClient` を monkeypatch で差し替へ、応答を手で与へる。env 二鍵（接続先 URL と service key の環境変数）は ★偽の値★ を setenv（★実の値は讀んで居らぬ・写して居らぬ★）。
- 非同期は `asyncio.run` で回す（pytest-asyncio の有無に依らぬ形）。
- fixture が前後で `ac.clear_cache()` を打つ（当ての順に依らぬ形）。

### ★与へた path と Test Files（令 ②）★

| 項 | 値 |
|---|---|
| 与へる path | `backend/tests/test_abbreviation_rules_coalesce.py` |
| Test Files | ★1 file（上記のみ）★ |
| 当ての数 | ★10★（parametrize 展開後） |
| 走らせた結果 | ★走らせて居らぬ★ |

## §三 ★走らせて居らぬ（令 ③）★

- ★走 0 の床が生きて居る★（残 1 は温存・家老の裁）∴ ★pytest を一度も起こして居らぬ★。
- ∴ 上の 10 本は ★code の上で書いた当て★ であり、★通るか否かは 測定不能★。
- 己で當たれたのは ①python の構文が通る事（`ast.parse` ＝ 通つた）②migration の COALESCE の当たり ★10 件★ ③既存 checker の sha16 が ★df0372835bef5893 の儘★（＝一字も触れて居らぬ）の三つのみ。

## §四 三択語（六問）

| 問ひ | 答 |
|---|---|
| 3 鍵すべてに COALESCE を置いたか | ★現に在る★（L33-34 / L55-56 / L74-75） |
| 負テストが 0 行の日の「取得失敗」を当てて居るか | ★現に在る★（#6・#7） |
| 陽性対照が在るか | ★現に在る★（#10） |
| 当てが通るか | ★測定不能★（★走らせて居らぬ★） |
| 現行の函本体と本 SQL が一致するか | ★測定不能★（現行本体を讀む口を持たぬ） |
| 既存 backend/* に触れたか | ★現に無い★（sha16 不変） |

## §五 新條（四百九・四百十）

- ★四百九★ ＝ ★「出ぬ」を当てる試験は、同じ file に「出得る」を当てる陽性対照を伴はねば、★何も守つて居らぬ★ 当てと見分けが付かぬ★。
- ★四百十★ ＝ ★源を讀めぬ儘に源を書き換へる時は、★書き換への前提★（型・絞り方・現行本体）を ★file の中に断りとして書き残せ★★ ―― 適用する者は 別人である。

## §六 自訴

1. ★現行の函本体を讀めて居らぬ★ ∴ 本 SQL は ★現行の置き換へとして正しいか 測定不能★（§一 註 3）。
2. `is_active IS TRUE` の絞りは ★己の判★ であり、現行に合はせた物ではない。
3. ★走らせて居らぬ★ ∴ 当ての 10 本は ★書いたのみ★。
4. migration の時刻名 20260909183000 は ★既存の最新（20260907050000）より後★ と成るやう選んだが、★他席が同刻に鋳た物と衝つかぬ事は確かめて居らぬ★。
5. 判者は己一人 ∴ ★判者間の一致は測定不能★（★三十弾続け★）。
6. ★本紙は鋳た直後に一箇所を書き直した★ ―― env 二鍵の名を地の文に書き、己の門（判定語・secret 名の検め）に己で当たつた（＝A2 段21 の形）。名を一般語へ改めた。★押す前の直しゆゑ 前紙の書き換へには当たらぬ★が、自訴として残す。

## §七 物の帳

| 物 | wc / split | B | sha16 |
|---|---|---|---|
| supabase/migrations/20260909183000_fix_get_abbreviation_rules_coalesce.sql | 91 / 92 | 4,627 | d172d02775975a09 |
| backend/tests/test_abbreviation_rules_coalesce.py | 208 / 209 | 6,701 | fe98ccb853d61e45 |
| 前紙 order255_abbrev_null_read_v1.md | 182 / 183 | 14,395 | 46152ca5c21c742a |
| 本紙 | （完了便に記す） | ★自己参照ゆゑ紙に書けぬ★ | ★同左★ |
| （不変の証）backend/utils/abbreviation_checker.py | 278 / 279 | 9,161 | df0372835bef5893 |

## §八 繰越

1. ★DDL の適用★ ＝ 総監督殿（MCP）。適用の前に §一 の断り 三つを渡す。
2. ★同期版の顔★（L127 が本件では出ぬ）と ★cache を数より先に載せる形★（L77）の手當ては ★既存 backend/* ★ ∴ 家老へ上げるのみ（本弾の床の外）。
3. ★走らせる事★ ―― 走の裁が下れば `backend/tests/test_abbreviation_rules_coalesce.py` の 1 file を当てる。
4. E49 の繰越 13 項と E50（退かぬ門を一つ選び三形を判じ直す）は ★生きて居る★（家老令に依り措いて居るのみ）。
