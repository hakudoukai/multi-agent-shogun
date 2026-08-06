# P0 機能テスト設計（5値到達実証・★設計のみ・走らせず★）— 足軽4号

**下命**: karo-second msg_20260806_101557_e0176c1a (2026-08-06T10:15:57)
**本便は 貴職の 10:15:57 便までを踏まえており申す**
**測時**: 2026-08-06T10:21:23+09:00 (`date -Is` 実行・当職実測)
**当repo HEAD**: `f3bbecb926f0596adbd249a9682920e8302203fc`
**監査体制**: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 で停止中)★。「二者PASS」を「三者PASS」と書かぬ。

**禁の遵守申告**:
- ★newbuild へ 一文字も書かず★（出所=軍師second FAIL 裁定 `queue/reports/gunshi_second_low_level_approval_second_case_ruling_20260805.md` 40行 sha256=f130b63217aadde2b3b201d75a316733162c66e30352ebfd3e094b90bcf06910・逐語「newbuild に触れるな（強）の既存禁」）。
- ★走らせず（設計のみ）★（出所=将軍second 令 10:13:31 ㈤）。★本 doc 中の手順は 一つも 本 turn で 実行しており申さぬ★（下記§3・§4 は「裁が立った後に 誰かが 行う手順」の記述であって、当職が今 実行した実測ではない。実測部分は §1 のみ = 当repo 側 read-only）。
- newbuild は本 turn で ★1バイトも読んでいない★（下記§1は当repo側の既に根治済み実装のみを対象。newbuildの実測は足軽2号 addendum2 §2 が既に断面を取っており、当職は重複測定しない）。

---

## §0 前提検証・既存資産確認（EXISTING_ASSET_CHECK 等）

**下命末尾に「前提を一つ検めよ」の指示は明記されていないが、当隊の型（家老second §10-2 item「規律衝突」等）に倣い、着手前に一点検めた。**

**検めた前提**: 「本工区は新規に機能テストを組み立てる工区である」という(当職自身の)想定。

**結果**: ★この前提は半分のみ正★。

| 検査項目 | 結果 |
|---|---|
| EXISTING_ASSET_CHECK | ★既存あり★。足軽2号 `docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2_addendum2.md` §3 が「5変数すべてが payload に実値として到達」を scratchpad 最小再現で ★既に実行済み★ (`FUNCTEST_ALL_FIVE_VARS_REACHED_PYTHON=true`)。軍師second PASS 済 (`queue/reports/gunshi_second_p0_ishoku_heredoc_fix_plan_addendum2_audit_20260805.md`、2026-08-05T07:40:24)。 |
| CANON_CHECK | 当repo `scripts/watchdogs/enter_restart_common_watchdog.sh` (sha256=`ba89766923fdf4ea9354e8afdccb85536ca4f833f81161fc22fad45da36be378`・382行) が根治済み正本。本 turn に当職が独立に再測し、a2 の引用値と★完全一致★を確認済み (下記§1)。 |
| ACTIVE_OWNER_CHECK | a3 が ㈢前段（当repo根治済み差分の対応表抽出）を並行担当。本 turn 時点で a3 の成果物は未確認 (`docs/incident_logs/2026-08-06_*a3*.md` を走査したが該当なし)。当職は diff 抽出そのものを行わず、§1 は「5値が何か」の確認に必要な最小限の行のみを引用する。 |
| DUPLICATE_IMPLEMENTATION_RISK | ★中★。a2 addendum2 §3 と目的文（「5値が実際に届くか」）が字面上一致する。∴ 下記§0-1 で射程の違いを明示し、二重にならぬよう当職の設計は a2 の成果物を★前提として引用し、書き直さない★。 |
| SEARCHED_TARGET_COUNT / SEARCH_RESULT_STATE | `docs/incident_logs/2026-08-06_*.md` を `grep -l "enter_restart_common_watchdog\|5値\|os\.environ"` で走査 → 5件ヒット (a2本体・addendum1-3・queue_reports_INDEX)。うち機能テストを名指しで扱うのは addendum2 のみ。`scanned_5_targets_1_relevant_gap(射程差)` と記す。 |
| KNOWLEDGE_GAP_WARNINGS | 委員長殿の原訂正便 (seq149808系「quoteのみでは値が失われる」) を当職は★見ていない★ (将軍second 令 10:13:31 ㈡ 経由の二次引用のみ)。∴ 引用は a2 addendum2 §3 の再現実験結果 (直接引用) を根拠とし、原文の言い回しを断定しない。 |
| REUSE_OR_INTEGRATION_TARGET | a2 addendum2 §3 の実測結果・当repo の§1（本doc）を再利用対象とする。新規の防御パターンは考案しない。 |

### §0-1 ★射程の違い（二重実装ではない理由）★

| | a2 addendum2 §3（既存・実行済） | 本設計（今回・未実行） |
|---|---|---|
| 対象コード | scratchpad 上の★最小再現サンプル★（newbuild/当repo 本体を模した手書きの断片） | 裁が立った後、★実際に patch された newbuild ファイルから sed 抽出した生バイト★（手書きしない） |
| doppler 経由の env 伝播 | 対象外（`urllib.request` 部分を省き、python 部分だけを直接実行） | ★対象に含める★（`doppler run ... --` の env prefix 連鎖ごと実行し、cycle2 (`0c3f371`) が是正した「env prefix が subshell に伝播しない」型のバグも検出範囲に入れる） |
| 実行タイミング | 已に実行済み（07:36台） | ★newbuild への patch 適用後にのみ★（現時点では実行しない） |
| 目的 | 「quote+env のパターンは機能するか」の★事前実証★（パターン単体の可否） | 「実際に newbuild へ適用された成果物が、本当にこのパターン通りに動くか」の★事後受入検査★（適用結果の検証） |

∴ **両者は同じ問いを別の対象・別の時点で問うており、後者は前者の代替ではなく★次の工程★に当たる。a2 の成果は前提として引用し、再現しない。**

---

## §1 ⒞ 5値とは何か（当repo 側・根治済み実装からの読取のみ・当職独立実測）

**対象**: `scripts/watchdogs/enter_restart_common_watchdog.sh` (当repo, HEAD=`f3bbecb9`)
**独立実測**: `sha256sum` = `ba89766923fdf4ea9354e8afdccb85536ca4f833f81161fc22fad45da36be378` (382行) — ★a2 addendum2/addendum3 の引用値と完全一致（当職が本 turn に自分で打った結果）★。

Step 0 (L79-124, 連続発火上限チェック) の env-prefix 行 (L96-100) と python 側受取行 (L106-110) を当職が実読した結果:

| # | bash 側ソース変数 (L96-100 で `="$VAR"` により参照) | env-prefix 名 (L96-100) | python 側受取 (L106-110, `os.environ.get`) |
|---|---|---|---|
| 1 | `$EVENT_TYPE` | `ER_EVENT_TYPE_PY` | `event_type` |
| 2 | `$RECENT_FIRES` | `ER_RECENT_FIRES_PY` | `recent_fires` |
| 3 | `$FIRE_CAP_COUNT` | `ER_FIRE_CAP_COUNT_PY` | `fire_cap_count` |
| 4 | `$FIRE_CAP_WINDOW_MIN` | `ER_FIRE_CAP_WINDOW_MIN_PY` | `fire_cap_window_min` |
| 5 | `$ER_TARGET_PC` | `ER_TARGET_PC_PY` | `target_pc` |

**∴ 「5値」= Step 0 の上記5変数。** ★これは a2 addendum2 §3 の記述「下命が明示した『EVENT_TYPE/RECENT_FIRES/FIRE_CAP_*/ER_TARGET_PC』と一致」と当職の独立読取が一致した★。

**★不確実性の明記（KNOWLEDGE_GAP・第四値）★**: 委員長殿の原訂正便を当職は見ていないため、「5値」が★Step 0 限定を指す★と委員長殿ご本人が明言したかどうかは★確認できていない（判らず、と書く）★。他の3箇所は変数の個数が異なる (Step 2=1個・Step 7=8個・Step 8=9個)。∴ 本設計は「Step 0 の5変数」を対象に組むが、もし委員長殿の意図が Step 7/8 も含む広い意味の「5」であった場合はこの前提が誤る可能性がある。**その場合の対応**: 下記§3の設計手順は Step 0 専用ではなく「対象ステップの env-prefix 変数群」を引数化した形にしてあるため、Step 7/8 へ適用する際も設計の書き直しは不要（対象ステップ名と変数リストを差し替えるのみ）。

---

## §2 ⒜ 眼目原則の再確認（新規考案せず・既存記述を引用のみ）

★「引用だけでは壊れる ∴ 引用（`<<'PYEOF'`）＋ 環境変数経由（os.environ）の対が正」★ — 出所は a2 本体§1 + addendum2 §1 (commit `0eb6798`/`0c3f371` の逐語 diff)。当職はこの原則を新規に立てず、以下の設計もこの原則の★検証手段★として組む（原則そのものの再定式化はしない）。

---

## §3 ⒝+⒟ 機能テスト設計（実出力の示し方 ＋ 「欠陥が在れば必ずFAILか」の検討）

### §3-1 設計の骨格（誰が・いつ・何を・どう検証するか）

**前提条件（発火条件）**: 委員長殿（または権限を持つ者）が newbuild へ§1の型で patch を適用した★後★にのみ着手可。★本 turn 時点では着手しない★。

**対象**: newbuild `scripts/watchdogs/enter_restart_common_watchdog.sh` の Step 0 ブロック（patch 適用後の実物）。

**手段（4段構成）**:

1. **抽出（実行者が patch 適用直後に行う）**
   - `sed -n "/^\s*ER_EVENT_TYPE_PY=/,/^PYEOF$/p" enter_restart_common_watchdog.sh > /tmp/.../step0_block.sh` のように、★コメント文言ではなく env-prefix の先頭行と終端 `PYEOF` 行を锚（アンカー）にして抽出する★（コメントは patch 時に書き換わり得るため、コメント文字列を锚にしない — これは下記§5の「新たに開ける穴」への対策そのもの）。
   - 抽出後、`grep -c '^PYEOF$'` で★ちょうど1件★であることを assert し、複数/0件ならその場で abort する（母集団取り零し防止・複数 heredoc が同じ終端記号を持つ場合の誤抽出防止）。

2. **doppler の無害化（実 secret を叩かない）**
   - `doppler run --project P --config C -- CMD...` は「引数 `--` の後ろの CMD を、real secret を注入した環境で実行する」薄いラッパーである。本設計では★実 secret も実 Supabase も使わない★ため、テスト専用の一時 `$PATH` 先頭に以下のスタブを置く:
     ```bash
     #!/bin/bash
     # stub doppler: 'run --project P --config C -- CMD...' → CMD をそのまま (継承環境で) exec する
     shift  # drop 'run'
     while [ "$1" != "--" ]; do shift; done
     shift  # drop '--'
     exec "$@"
     ```
   - ★この `$PATH` 上書きは、この1コマンド呼び出しの subshell に限定する（`env PATH="$STUB_DIR:$PATH" bash -c '...'` の形。恒久的な export はしない）★。理由は下記§5-2。

3. **受け口（実際に POST される JSON を捕獲する）**
   - ローカル loopback (`127.0.0.1`) 上に一時 HTTP サーバ（`python3 -m http.server` 相当の最小 handler、または `http.server.BaseHTTPRequestHandler` を1回だけ待ち受ける使い捨てスクリプト）を立て、受信した POST body をファイルへ書き出す。
   - `SUPABASE_URL=http://127.0.0.1:<ephemeral_port>`・`SUPABASE_SERVICE_ROLE_KEY=dummy-not-a-real-secret` を抽出ブロック実行時の環境として与える（★実 secret・実 Supabase 疎通は一切発生しない★）。

4. **実行と照合**
   - Step 0 の bash 側ソース変数 (`EVENT_TYPE`/`RECENT_FIRES`/`FIRE_CAP_COUNT`/`FIRE_CAP_WINDOW_MIN`/`ER_TARGET_PC`) に既知の sentinel 値（例: `halt`/`7`/`5`/`10`/`second_pc`）を与え、抽出ブロックを②のスタブ doppler・③の受け口環境の下で実行する。
   - 受け口が捕獲した POST body を `json.loads` で読み戻し、5フィールド (`event_type`/`recent_fires`… は f-string の中に埋まる形のため `detail` 文字列内の部分一致で確認・`target_pc` は完全一致) が sentinel 値と一致することを assert する。
   - ★スクリプト自身の標準出力 (`print` 文) ではなく、受け口が捕獲した実際の POST body を根拠にする★点が、a2 addendum2 §3 (script 内 print + assert のみ) との差分であり、下命冒頭「引用だけの見た目 PASS を成果と数えぬ」への直接対応である。

### §3-2 ⒟「欠陥が在れば必ずFAILか」— ★書けぬ部分を明記する★

**結論を先に**: ★上記§3-1の設計単体は、欠陥（unquoted heredoc による bash 直接展開）の不在を保証しない。書けぬ。★

**理由（推論の経過）**:

- 欠陥のある旧版コードは、Step 0 の値を `os.environ.get('ER_EVENT_TYPE_PY', ...)` からではなく、bash が heredoc 構築時に `${EVENT_TYPE}` を★直接展開して python ソース文字列へ埋め込む★形で受け取る（a2 本体§1 の diff 該当箇所参照）。
- ∴ もし sentinel 値に **英数字のみ（shell/JSON/Python いずれの特殊文字も含まない）** を選んだ場合、旧版・新版のどちらも「その sentinel 値が payload に現れる」という★同一の観測結果★を返し得る（旧版は bash 展開で直接埋め込み、新版は env 経由で埋め込み、どちらも最終的に同じ文字列が同じ位置に現れる）。
- ∴ **本設計（§3-1、良性値のみ使用）は、旧版・新版を判別する力を持たない場合がある。** ゆえに「値が届いたこと」の実証（機能の正常系証明）と「欠陥が存在しないことの証明」は別物であり、本設計は前者のみを担う。

**∴ 本設計を「欠陥不在の証明」として単独運用してはならない。既存の負テスト／陽性対照（a2 本体§2-3・addendum2 §3後段の「naive quote-only」反例）と★対で運用して初めて、⒟の要求（欠陥が在れば必ずFAIL）を満たす★**:

| 検査 | 何を判別できるか | 旧版(無引用)での結果 | 片手落ち(quoteのみ・env化せず)での結果 | 新版(quote+env)での結果 |
|---|---|---|---|---|
| 本設計（§3-1・良性値） | 正常系で値が届くか（機能の存在証明） | 届く場合がある（判別力なし） | ★届かない（リテラル文字列化）★ = FAIL | 届く = PASS |
| a2 本体§3 陽性対照（悪性値・`;`/引用符を含む） | 旧版が壊れるか（欠陥の存在証明） | ★SyntaxError で cycle 全体が壊れる★ = 旧版の危険を実証 | (未評価・対象外) | 安全に JSON エンコードされる |

**∴ 本設計は上表右列（片手落ち検出）とは重ならずに相補う** — 良性値の機能テストは「quote のみで env 化を忘れた」片手落ちパターンに対しては★確実に FAIL する★（値がリテラル文字列 `"${EVENT_TYPE}"` のまま届き、sentinel 値と一致しないため）。これは a2 addendum2 §3 後段の `NAIVE_QUOTE_ONLY_VALUE_LOST=true` と同じ型であり、本設計もこのケースを検出範囲に含める（§3-1手順4の assert がそのまま機能する）。**∴ 本設計が確実に FAIL するのは「片手落ち（quote のみ・env化なし）」のケースであり、「旧版そのもの（無引用）」は良性値では検出できない場合がある、と切り分けて書く。**

---

## §4 原子適用時の実行順序（★裁が立った後・当職は実行しない・順序の記述のみ★）

1. patch 適用（実行者=委員長殿または指名された者、本工区の範囲外）。
2. §3-1 手順1「抽出」を実行し、`PYEOF` 終端が★ちょうど1件★であることを確認する（複数/0件なら abort、家老second へ blocker 4点で報告）。
3. §3-1 手順2-4 を実行し、受け口の捕獲 JSON を保存する（証跡として残す）。
4. 併せて a2 本体§2-3 の負テスト・陽性対照を★同一の抽出済みブロック★（scratchpad の手書きサンプルではなく、実際に patch された生バイト）に対して再実行し、旧版との比較を最終確認する。
5. 全て PASS した場合のみ「本番適用済みコードが5値を正しく届ける」ことの受入証跡として提出する。

---

## §5 ⒠ 本設計が新たに開ける穴

1. **`$PATH` スタブの汚染範囲**: §3-1 手順2の doppler スタブを恒久的に `export PATH=...` してしまうと、以後のシェルセッションで★実 doppler が呼ばれなくなり、他の real secret 呼び出しが静かに no-op 化する★恐れがある。∴ 対策として「1コマンド限定の PATH 上書き（`env PATH=... CMD`)」を明記した（§3-1 手順2）。実行者はこの限定を★崩してはならない★。
2. **抽出アンカーの脆さ**: コメント文字列（「副院長令 b0bdfa67」等）を锚に使うと、patch 適用時にコメントが書き換わっていた場合★誤ったブロックを抽出するか、抽出に失敗する★。∴ env-prefix 行と `PYEOF` 終端という構造的な锚を使い、かつ「ちょうど1件」の assert を必須にした（§3-1 手順1）。
3. **ローカル HTTP スタブの放置**: 受け口サーバをテスト終了後に確実に終了させないと、★ポートを掴んだプロセスが residual に残る★ (Watcher Design Principles の「専用テーブル分離」に類する「専用プロセス終了」の欠落)。∴ 実行者は `try/finally` 相当（bash なら `trap 'kill $SERVER_PID' EXIT`）でサーバプロセスを確実に終了させること。本設計書はこれを手順として明記するに留め、当職は実装コードそのものは書いていない（設計のみの下命ゆえ）。
4. **良性値のみでの過信**: §3-2 で述べた通り、本設計を「PASS したから欠陥が無い」と読み違えると★誤った安心を生む★。∴ 提出時は必ず a2 の負テスト・陽性対照と併記し、単独の PASS 表記を避けるよう次工程（適用実行者）へ申し送る必要がある（下記§7）。
5. **sentinel 値の選び方次第で判別力を失う**: §3-2 の通り、英数字のみの sentinel では旧版・新版が区別できない場合がある。実行者が★安易に "test123" のような単純値だけで済ませると、機能テストが実質的に何も検出しない飾りになる★恐れがある。∴ 実行時は a2 addendum2 §3 と同じ非自明な値（実運用に近い `halt`/`7`/`5`/`10`/`second_pc` 等）を使うことを推奨するに留め、判別力の限界そのものは解消しない（§3-2 の通り、判別力を持たせるには特殊文字を含む負テストとの併用が必須）。

---

## §6 【本工区で己が直した誤り】

- 無し。ただし §0 で「本工区は新規」という当職自身の初期想定を検め、a2 addendum2 §3 との重複を検出し、射程（対象コード=実物 vs 最小再現／実行時点=事後 vs 事前／doppler env 伝播を含むか）を明示することで二重実装を避けた（これは「誤りを直した」というより「前提を検めて訂正した」であり、家老second §10-2「求めた証拠を己が先に渡しておれば証拠に成らぬ」に照らし、当職の独立実測 (§1) を根拠に据えた）。

## §7 【この工区と対に成る他工区】

- **a3の ㈢前段**（当repo側根治済み差分の対応表抽出・読取のみ）— 本 turn 時点で a3 の成果物は未確認（探索範囲: `docs/incident_logs/2026-08-06_*a3*.md` を `ls`）。★争わず・重ならず★の下命に従い、当職は diff 抽出そのものを行っていない（§1 は「5値の同定」に必要な最小限の行のみを独立実測として引用）。
- **a2 addendum2 §3**（既存・実行済の機能テスト）— §0-1 で射程の違いを明示済み。前身工区というより★別の時点・別の対象を扱う工程★。

---

## §8 監査提出

成果物: 本file (`docs/incident_logs/2026-08-06_p0_functional_test_design_a4.md`)。
ETA: 即時（本便提出時点で完了・追加作業なし）。
提出先: karo-second + 軍師second（下命明記のとおり両者へ提出）。
監査体制: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 停止中)★。
