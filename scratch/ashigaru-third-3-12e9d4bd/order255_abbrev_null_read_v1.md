# order255 / 割込・優先1 讀取実測 ―― abbreviation_corrections が 0 行の日の NULL の道筋

## §的 ★的一行★

★abbreviation_corrections が 0 行の日、RPC の corrections が NULL で返り、其の NULL は ★取得の失敗に非ず★ ―― 然れど log には「取得失敗」と出る。之を三点（①三鍵の在り処 ②NULL の道筋 ③偽の病名が出る行）に分け、★讀取のみ・走0★ で行を名指した。★

## §零 帳の頭

- as_of ＝ 2026-09-09T18:17:50+09:00
- 板 ＝ 354dc26f（家老third 令・総監督令の割込）
- ★己は何処まで測つたか（家老 新條）★ ＝ ★code は現に己で當たつた★／★RPC の本体と DB の行数は 己で當たれて居らぬ（讀取の口を持たぬ）★

### 讀んだ物（悉皆・己で當たつた）

| 物 | wc / split | B | sha16(sha256 頭16) |
|---|---|---|---|
| /mnt/c/DentalBI/backend/utils/abbreviation_checker.py | 278 / 279 | 9,161 | df0372835bef5893 |
| /mnt/c/DentalBI/supabase/migrations/20260323074402_create_official_abbreviations_table.sql | 28 / 29 | 1,530 | (§八に記す) |
| /mnt/c/DentalBI/supabase/migrations/20260324071604_add_receipt_abbreviation_and_bulk_insert_disease_names.sql | 99 / 100 | (§八) | (§八) |
| /mnt/c/DentalBI/backend/services/ai_polish_service.py（呼手・行のみ） | ― | ― | ― |
| /mnt/c/DentalBI/backend/services/dental_text_corrector.py（呼手・行のみ） | ― | ― | ― |

### ★樹の別（床⑵）★

| 樹 | migrations 件数 | 最も新しい migration | checker の sha16 |
|---|---|---|---|
| ★/mnt/c/DentalBI（作業樹・生きて居る）★ | ★779★ | 20260907050000_pc_handshake_watcher_indexes.sql | df0372835bef5893 |
| <本repo>/dentalbi（写し・古い） | 41 | 20260727221800_fix_r4_sc_objective_quadrant_teeth.sql | df0372835bef5893 |

★両樹の checker は 同じ sha ∴ 本紙の判は 樹に依らぬ★。★然れど 略称の 2 table を鋳た migration は ★作業樹にしか無い★ ∴ 本件の樹は ★/mnt/c/DentalBI★ と読む。枝は両樹とも wp-a1-a3-3-20260723。

### 母の動き（床(27) 八件目）

A2 索引 1061 → ★1075★ wc（段 20 → ★21★）／家老台帳 1917 → ★1966★ wc。★本紙は E50 の母を一切用ゐぬ ∴ 判に及ばぬ★（E50 は家老令に依り措いた）。

### 費消・帳

- 走 ＝ ★0★（製品走 0・残 1 不変）／焚 ＝ 1（E50 の器 o254_e50.rule.py を一度・本件の前）／DB ＝ 0／書込 ＝ 本紙のみ
- HEAD ＝ 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）／porcelain ＝ 170（不変）
- harness の /tmp 置き物（消さず・当席の物に非ず） ＝ /tmp/a3-tree.txt 3,183 B・/tmp/a31_respawn_cmd.txt 318 B

## §一 令 逐語

> [家老third→A3] ★割込・優先1(総監督令・今)★=板 354dc26f。実測=★abbreviation_corrections は今日 is_active=0 ∴ get_abbreviation_rules の corrections が NULL＝abbreviation_checker が『取得失敗』の ★偽の病名★ で fallback 中★。★先づ讀取のみで測れ(走0)★=①三鍵の在り処 ②NULL の道筋 ③偽の病名が出る行。E49 は一旦措け。

> [家老third→A3] ★裁 着＝★當隊が書く★・床は ★2 file に限り明示で解かれ申した★★=⑴ supabase/migrations/<新規>.sql(CREATE OR REPLACE get_abbreviation_rules・★3鍵に COALESCE(…,'[]'::jsonb)★) ⑵ backend/tests/test_abbreviation_rules_coalesce.py(新規1本・★0行の日の負テスト★)。

> [家老third→A3] ★境(厳守)★=★abbreviation_checker.py 等 既存 backend/* は一字も触れるな★／★DDL を己で適用するな(適用は総監督が MCP で実行)★／DB 書込0／★他 file 0★。★先の讀取実測を紙に残してから書け★(三鍵の在り処/NULL の道筋/偽の病名が出る行)。

> [家老third→A3] ★書き方★=①SQL は ★3鍵の何処に COALESCE を置いたかを一行づつ★ ②負テストは ★0行の日に『取得失敗』が出ぬ事★ を当て ★与へた path と Test Files を並べよ★ ③★走らせられぬなら『走らせて居らぬ』と書け★。判定=軍師third ∴ 復命に ★紙名/行数/sha16/枝と tip★。押しは當職が代行。

## §二 ①三鍵の在り処

### 鍵の三つと 其の源

| 鍵 | 源（table・列） | 形（checker が期する物） | 定めた migration |
|---|---|---|---|
| official | official_abbreviations の行 | 物の配列（abbreviation / official_name / …） | 20260323074402（CREATE TABLE） |
| corrections | ★abbreviation_corrections の行★ | 物の配列（unofficial / official_abbreviation / official_name / correction_type） | 20260323074402（CREATE TABLE） |
| detail_required | official_abbreviations.requires_detail が真の行 | ★字の配列★（例 C / P / G / Pul / Per） | 20260323074402（requires_detail BOOLEAN DEFAULT false） |

checker 側の逐語（己で當たつた）:

> 8:  - official_abbreviations テーブル: 公認略称55件
> 9:  - abbreviation_corrections テーブル: 非公認→公認変換29件
> 10:  - get_abbreviation_rules() RPC: 上記を一括JSONB返却

> 44:            "detail_required": ["C", "P", "G", "Pul", "Per"],

> 238:    return {"official": [], "corrections": [], "detail_required": []}

両 table とも `is_active BOOLEAN DEFAULT true` を持つ（20260323074402 L9・L20）。

### ★核心（本節で最も重い事）★

★RPC `get_abbreviation_rules` の ★本体（函の定義）★ は ★本樹の何処にも無い★。★

- 作業樹 supabase/migrations ★779 件★ を當て、`get_abbreviation_rules` の当たり ＝ ★0 件★。
- 当たるは ①checker の docstring（L4・L10）②docs 3 枚の言及（handover_v42 の表 1 行・総合開発計画 L217・ナレッジ v6_2 L133）のみ ―― ★何れも「在る」と述べるのみで 本体を持たぬ★。

∴ ★三鍵の形を定める正本は DB の中にしか無く、版に載つて居らぬ★ ―― 之が「0 行の日に何が返るか」を ★紙からは決して読めぬ★ 理由である。

## §三 ②NULL の道筋（七段）

| 段 | 何処 | 何が起きるか |
|---|---|---|
| 一 | DB（RPC 内） | 0 行の日、集約が ★0 行★ に当たる。★SQL の jsonb_agg は 0 行に NULL を返す（空の配列に非ず）★ ―― ★但し本 RPC が jsonb_agg を用ゐて居るかは 讀めて居らぬ（§七-4）★ |
| 二 | 便 | json に `"corrections": null` が乗る（鍵は ★在る★・値のみ null） |
| 三 | L241-248 `_normalize_rpc_result` | `data.get("corrections", [])` ―― ★鍵が在つて値が None の時、既定値 [] は使はれぬ★ ∴ ★None が素通りする★ |
| 四 | L76-78 | `rules = _normalize_rpc_result(data)` の直後、★L77 で先に `_cache = rules`★（毒を含んだ儘 cache へ載る） |
| 五 | L79-84 | `logger.info` の引数 ★L82 `len(rules.get("corrections", []))`★ → `len(None)` → TypeError |
| 六 | L87-89 | 其の TypeError を ★広い except が捕へ★、★L88 が「取得失敗」と書く★／L89 が空辞書を返す |
| 七 | L168-171 | ★然れど cache は L77 で既に毒★ ∴ `corrections = _cache.get("corrections", [])` → None → ★L171 `for entry in corrections` で 二度目の TypeError（此方に捕手は無い）★ |

逐語（己で當たつた）:

> 76:        rules = _normalize_rpc_result(data)
> 77:        _cache = rules
> 82:            len(rules.get("corrections", [])),
> 87:    except Exception as e:
> 88:        logger.warning("Supabase略称ルール取得失敗: %s。空辞書を返します", e)
> 168:    corrections = _cache.get("corrections", [])
> 171:    for entry in corrections:
> 246:            "corrections": data.get("corrections", []),

### ★同期版は 別の顔で出る★

同期版 `load_abbreviation_rules_sync`（L92-128）には ★L79-84 に当たる logger.info の行が無い★。

> 121:        rules = _normalize_rpc_result(data)
> 122:        _cache = rules
> 124:        return rules
> 127:        logger.warning("Supabase略称ルール取得失敗(sync): %s。空辞書を返します", e)

∴ 同期版は ★段五・六を通らぬ★ ―― 「取得失敗」を ★書かず★、L124 で毒を ★返し★、L171 で初めて破れる。
★同じ一つの疵が 二つの別の顔（片方は偽の病名・片方は無言の破れ）を持つ★。

## §四 ③偽の病名が出る行

| 行 | 逐語 | 何ゆゑ偽か |
|---|---|---|
| ★L88★ | 上記 §三 の引用 | 便は現に成り、`raise_for_status()`（L71）も通つて居る ∴ ★「取得失敗」は事実に反する★。真の因は ★L82 の `len(None)`★ ―― ★取得の後の 数の書き方で破れて居る★ |
| L127 | 上記 §三 の引用 | 同じ文言。★然れど本件では出ぬ★（L82 に当たる行が無い）∴ ★同期の読手には 何の便りも届かぬ★ |
| L89・L128 | 「空辞書を返します」 | ★返り値については真★。然れど L77・L122 で ★cache は空でない★ ∴ ★cache を讀む者にとつては偽★ |

### 偽の病名を ★受け取る者★（cache 経由の読手）

| 呼手 | 行 |
|---|---|
| backend/services/ai_polish_service.py | 258（`await load_abbreviation_rules()`）／302（`check_unofficial_abbreviations`）／305（`check_disease_abbreviation_detail`） |
| backend/services/dental_text_corrector.py | 86 / 87（cache 前提・L77 の docstring に「事前に load_abbreviation_rules() でキャッシュを充填しておくこと」） |

∴ ★L88 を讀んだ者は「Supabase へ届いて居らぬ」と読む★ ―― 現に届いて居る。★病名が偽であるゆゑ、手当ての向きが変る★。

## §五 三択語（八問）

| 問ひ | 答 |
|---|---|
| 三鍵の在り処（table と列） | ★現に在る★（table 2 本 + 列 requires_detail 1 本） |
| RPC 本体の版管理（migrations の中） | ★現に無い★（779 件に当たり 0 件） |
| 0 行の日に corrections が NULL に成るか | ★測定不能★（RPC 本体を讀めず・DB 讀取の口を持たぬ。家老の実測を写した） |
| 鍵が在つて値が None の時 `.get(k, [])` が None を返すか | ★現に在る★（python の定め・L246） |
| L82 が `len(None)` で破れるか | ★現に在る★（code 上で確か・★走らせては居らぬ★） |
| 破れた時 L88 が「取得失敗」と書くか | ★現に在る★（L87 の except が広い） |
| 同期版が同じ道を通るか | ★現に無い★（L82 に当たる行が無い） |
| cache が毒を含んだ儘 残るか | ★現に在る★（L77 が数の行より ★先★ に在る） |

## §六 新條（四百五〜四百八）

- ★四百五★ ＝ `.get(k, 既定)` は ★鍵が無い時★のみ既定を返す。★値が None の時は None を返す★ ∴ NULL を持ち得る源には ★源の側（SQL）で COALESCE★ か ★受けの側で `.get(k) or 既定`★ を置け。★既定値の書式は「守つた」の証に成らぬ★。
- ★四百六★ ＝ ★cache に載せるのを 数を書くより先にするな★。後の行が破れた時、★返り値だけが空に成り cache には毒が残る★ ―― ★呼手ごとに違ふ物が見える★。
- ★四百七★ ＝ log の文言は「何が起きたか」でなく ★「何処で捕へたか」★ を書く形に成り易い。捕手（except）が広い程、文言は ★偽の病名★ に成る。
- ★四百八★ ＝ 同じ疵が 同期版と非同期版で ★別の顔★ を持つ時、★片方の顔だけ直すと もう片方が残る★。直す前に ★顔を数へよ★。

## §七 自訴

1. ★RPC 本体を讀めて居らぬ★（DB 讀取の口を持たぬ）∴ §三 段一 は ★推し量り★ であり 実測に非ず。
2. 家老の実測「abbreviation_corrections は今日 is_active=0」を ★写した★ ―― ★己で確かめて居らぬ★（作法 六条目）。
3. ★走らせて居らぬ★（走0）∴ `len(None)` の破れを ★現に起こして見て居らぬ★ ―― code の讀みのみ。
4. 「jsonb_agg は 0 行に NULL を返す」は SQL の一般則として書いた。★本 RPC が jsonb_agg を用ゐて居るか否かは 讀めて居らぬ★ ∴ ★別の書き方（例へば coalesce 済の集約・array_agg・row_to_json）なら道筋は変る★。
5. 2 本の migration の B と sha16 を §零 の表で欠いた（§八 に回した）―― ★一つの表で済ませ得た★。
6. 母の drift（A2 21 段・家老台帳 1966）を ★本紙では判じて居らぬ★（E50 が措かれた為）。
7. 判者は己一人 ∴ ★判者間の一致は測定不能★（★二十九弾続け★）。

## §八 物の帳

| 物 | wc / split | B | sha16 |
|---|---|---|---|
| 本紙 | （完了便に記す） | ★自己参照ゆゑ紙に書けぬ★ | ★同左（完了便に記す）★ |
| 20260323074402_create_official_abbreviations_table.sql | 28 / 29 | （完了便では触れぬ・讀取のみ） | ― |
| 20260324071604_add_receipt_abbreviation_and_bulk_insert_disease_names.sql | 99 / 100 | ― | ― |
| abbreviation_checker.py | 278 / 279 | 9,161 | df0372835bef5893 |

★何れも 讀取のみ・一字も書いて居らぬ★。

## §九 繰越

1. ★本件の次弾★ ＝ ⑴ supabase/migrations の新規 SQL（3 鍵に COALESCE）⑵ backend/tests の負テスト 1 本 ―― ★家老の裁に依り 此の 2 file に限り床が解かれて居る★。
2. ★RPC 本体が版に載つて居らぬ事★ 其の物の始末（新規 SQL が CREATE OR REPLACE を持てば、★以後は版に載る★）。
3. ★同期版の顔★（L127 が本件では出ぬ事）の手當ては ★本弾の 2 file の外★ ―― 既存 backend/* に触れぬ床ゆゑ、家老へ上げるのみ。
4. cache が毒を含む事（L77 の順）も ★既存 backend/* ★ ∴ 同じく上げるのみ。
5. E50（退かぬ門を一つ選び三形を判じ直す）と E49 の繰越 13 項は ★生きて居る★（家老令「E49 は一旦措け」に従ひ 措いて居るのみ）。
