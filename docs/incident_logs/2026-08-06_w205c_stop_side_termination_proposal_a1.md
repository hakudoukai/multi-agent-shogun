# W205c 停止側(名前でprocessを終える経路)起案 — 実装案+負テスト設計 (足軽1号)

- 断面 (機械時刻): 2026-08-06T02:29:06+09:00 / HEAD=f3501fd322ae0bab6ed2e06b99c581ae1b720104
- 位置づけ: ★これは実装ではなく起案(設計案)★。家老second⑤発令(msg_20260806_022008_a5007081、将軍second裁定反映)に基づく。
- 材料: W205b列挙(`docs/incident_logs/2026-08-06_w205b_name_kill_enumeration_a1.md`)をそのまま流用。★本起案作成にあたり新たな母集団測定(全域grep再走査)は行っていない★。ただし提案diffを正確に書くため、対象6ファイルの該当行を直接読取った(実行はしていない・読取のみ)。

## 0. 為さぬ事 (発令の禁則・遵守宣言)
- (a) 対象script(hakudokai_start_watchers.sh / hakudokai_watchdog.sh / hakudokai_secondpc_setup.sh 等)は一切実行していない。
- (b) `pkill` / `pgrep` / `tmux kill-*` 等、processを名前で終える系のコマンドは、DRY-RUNも含め一切打っていない。
- (c) hermes側のpane・session(honbucho含む)には触れていない。本起案の対象範囲(グループA/B/C)にhermes系エージェントは含まれない(LEGACY_INBOX_AGENTS等の対象は karo/ashigaru1/gunshi/shogun/ashigaru2/ashigaru8 のみ、W205bで確認済)。
- (d) 本file・関連fileともcommitしていない(`git status --short` = `??`、軍師PASSまで維持)。

## 1. 課題の要約 (W205bより)
W205bの⒟表で判明した通り、`inbox_watcher.sh <agent>` を **末尾spaceなし** で`pgrep -f`/`pkill -f`に渡すグループA/B/C(計6ファイル箇所)は、`<agent>` が他agentの前方部分文字列である場合に巻き添えが生じる(実測=`karo`/`shogun`/`gunshi`パターンが各々`karo-second`/`shogun-second`/`gunshi-second`を部分一致で捕捉)。
一方、同一repo内のグループD(`watcher_supervisor.sh`/`watcher_supervisor_third.sh`)は **末尾spaceあり** のパターンで同種の衝突を構造的に遮断しており、グループE(`inbox_watcher.sh`自己watch)は `.yaml` 固定接尾辞でanchorしている。★健全な解法が既にrepo内に存在する★。

## 2. 起案 (設計のみ・最小差分方針・「五 大きく作るな」準拠)
新規の抽象化・新規helper・新規fileは提案しない。★既存の健全パターン(グループDの末尾space方式)を、グループA/B/Cの該当箇所へ機械的に適用するだけ★の最小差分とする。

### 2-a. 対象箇所と提案diff (Before→After、★未適用・提案のみ★)

| # | file:行 | Before | After (提案) | 種別 |
|---|---|---|---|---|
| 1 | shim/hakudokai/hakudokai_start_watchers.sh:57 | `pkill -f "inbox_watcher.sh ${agent}" 2>/dev/null \|\| true` | `pkill -f "inbox_watcher.sh ${agent} " 2>/dev/null \|\| true` | 実行系(停止) |
| 2 | shim/hakudokai/hakudokai_start_watchers.sh:86 | `if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | `if pgrep -f "inbox_watcher.sh ${agent} " > /dev/null 2>&1; then` | 判定のみ(check only) |
| 3 | shim/hakudokai/hakudokai_start_watchers.sh:185-188 | `pgrep -f 'inbox_watcher.sh karo'` 等4行 | `pgrep -f 'inbox_watcher.sh karo '` 等(末尾space追加、4行同型) | 表示のみ(log) |
| 4 | shim/hakudokai/hakudokai_watchdog.sh:530 | `if ! pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | `if ! pgrep -f "inbox_watcher.sh ${agent} " > /dev/null 2>&1; then` | 判定のみ |
| 5 | shim/hakudokai/hakudokai_watchdog.sh:566 | `if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | `if pgrep -f "inbox_watcher.sh ${agent} " > /dev/null 2>&1; then` | 判定のみ |
| 6 | shim/hakudokai/hakudokai_watchdog.sh:624 | `pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1 && alive="true"` | `pgrep -f "inbox_watcher.sh ${agent} " > /dev/null 2>&1 && alive="true"` | 判定のみ |
| 7 | shim/hakudokai/hakudokai_secondpc_setup.sh:369-370 | `pkill -f "inbox_watcher.sh ${AGENT1_ID}"` / `${AGENT2_ID}` | 各々末尾space追加 | 実行系(停止) |
| 8 | shim/hakudokai/hakudokai_secondpc_setup.sh:384-385 | `pgrep -f "inbox_watcher.sh ${agent_id}"` 2箇所 | 各々末尾space追加 | 判定のみ |
| 9 | shim/hakudokai/hakudokai_secondpc_setup.sh:471-472 | `pgrep -f "inbox_watcher.sh ${AGENT1_ID}"` / `${AGENT2_ID}` | 各々末尾space追加 | 表示のみ |

★対象外として提案(本起案のscope外・現状維持)★:
- shim/hakudokai/hakudokai_watchdog.sh:88 (`LEGACY_INBOX_AGENTS`定義文字列そのもの): これはagent名リストのデータであり、pgrep/pkillへの引数はL530/566/624側で組み立てられる。データ定義側の変更は不要、上記#4-6の適用で足りる。
- shim/hakudokai/hakudokai_secondpc_setup.sh:487-488 (`echo`文): 実行系コマンドではなく人間向け表示文字列。変更は必須ではない(表示の一貫性のためAfter側に揃えても害はないが、本起案の必達範囲には含めない)。
- グループF (shutsujin_departure.sh:971-973,1077・agent名なし広域一括pkill): W205bで「撤収=意図的全停止と推される」と記した通り、意図的設計の可能性が高く、本起案では裁定・変更提案をしない(現状維持)。
- グループG (tmux kill-session系、`$SHOGUN_SESSION`等変数): 変数の実値をW205b時点で追跡できておらず(第四値)、本起案の対象外。次工区へ持ち越しを提案する。

### 2-b. なぜこれが「大きく作らない」設計か
- 変更点は全て「文字列末尾に半角space 1個を足す」のみ。ロジック分岐・新規関数・新規設定ファイルは一切追加しない。
- 修正パターンはグループDで★既に本番稼働中★(watcher_supervisor.sh)であり、新規発明ではなく既存の実証済み解法の横展開。
- 環境部長殿より「当方でやる」の一報があれば、本表(2-a)がそのまま引き渡し可能な差分リストとして機能する設計にした(引き渡しコストを最小化)。

## 3. 負テスト設計 (★設計のみ・本工区時間内は未実行・実processへの操作なし★)

### 3-a. 文字列突合テスト (`grep`/シェル文字列比較のみ、pgrep/pkill等の実行なし)
目的: 修正前パターンが衝突を起こし、修正後パターンが衝突を起こさないことを、実際のprocessを一切使わずに検証する。

設計:
1. 「起こり得る引数文字列」のテストベクタを用意する(実processではなく文字列リテラル):
   - `V1 = "./scripts/inbox_watcher.sh karo multiagent-second:0.0 claude"` (意図した対象)
   - `V2 = "./scripts/inbox_watcher.sh karo-second multiagent-second:0.0 claude"` (巻き添え候補・実在確認済=W205b⒞)
   - `V3 = "./scripts/inbox_watcher.sh shogun shogun-second:0.0 claude"` / `V4 = ".../inbox_watcher.sh shogun-second shogun-second:0.0 claude"` (shogun系も同型で用意)
   - `V5/V6` = gunshi系も同型で用意
2. Before pattern (`"inbox_watcher.sh karo"`) を `[[ "$V1" == *"inbox_watcher.sh karo"* ]]` 形式で照合 → V1・V2 双方に一致することを期待(衝突の再現)。
3. After pattern (`"inbox_watcher.sh karo "`、末尾space) を同様に照合 → V1のみ一致・V2は不一致になることを期待(衝突解消の証明)。
4. 上記をshogun/gunshiパターンでも同型に繰返す(計3組×2パターン=6ケース、+ashigaru2/ashigaru8の接尾候補2ケースを追加可)。
5. ★実行にあたっては `grep -F`/bashの`[[ ... == *...* ]]`のみを使用し、`pgrep`/`pkill`/実process操作は一切行わない★。テスト対象はあくまで「文字列とパターンの一致・不一致」であり、実在するprocessではない。

### 3-b. 隔離環境テスト (本日実施の隔離手法を流用)
目的: 対象shell scriptの構文が壊れないことを、対象scriptを一切実行せず確認する。

設計:
1. 対象file限定でtemp branch/temp commitを作る隔離手法(本日実測済の型=対象file限定・実測base・reset --soft復元・HEAD不変証明)を流用する想定。★但し本工区は「commitせぬ(軍師PASSまで)」の縛りがあるため、実施は軍師PASS後、または家老second/軍師secondの明示許可が出てからとする★。
2. 隔離環境内でも実行するのは `bash -n <file>` (構文チェックのみ・プロセス起動なし)と、3-aの文字列突合テストのみ。対象scriptの本体(pkill/pgrep部分を含む関数)自体を呼び出す実行テストは行わない。
3. 隔離環境外(本番pane/session)への影響が原理的に発生しない設計であることを、事前に`git diff`で変更範囲(2-aの表)が該当6ファイル・9箇所の文字列リテラルのみであることを示してから実施する。

## 4. 成果物欄
- ① 成果物path: 本file `docs/incident_logs/2026-08-06_w205c_stop_side_termination_proposal_a1.md`
- ② 行数+sha256: 本file確定後、別途report(inbox本文)に記す(自己参照回避のため本文中には記さない)。
- ③ HEAD hash: f3501fd322ae0bab6ed2e06b99c581ae1b720104 / 測時: 2026-08-06T02:29:06+09:00
- ④ 実行状況: 対象script・pkill/pgrep/tmux kill-*系コマンドは本工区時間内、一切実行していない(§0確認済)。

## 5. 撤退条件 (家老second指示「五 大きく作るな」の実務化)
環境部長殿より「当方でやる」の一報が届き次第、本起案(2-a表)以降の作業(実装着手)を直ちに停止し、本fileをそのまま引き渡し材料として提出する。本起案自体を「大きく」拡張する(例: 全grepパターンの一括リファクタ・新設ヘルパー関数の導入等)提案はしない。
