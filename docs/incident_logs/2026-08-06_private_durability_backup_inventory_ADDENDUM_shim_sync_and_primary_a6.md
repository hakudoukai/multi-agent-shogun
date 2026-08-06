# 追補 — shim/**広域*sync*再索＋運用primary列挙（足軽6号）

下命=家老second msg_20260806_212036_f206f46d（2026-08-06T21:20:36）。前票（`2026-08-06_private_durability_backup_inventory_queue_dashboard_memory_a6.md`、HEAD=5eaf396a時点）への★追補★。
条＝「上長が挙げた手掛かり（auto-git-sync）を母集団と読むな」——本票はこれを踏まえ広域再索を行う。
禁は前便のまま（backup走らせるな・復旧試すな・queue不触・★script一度も実行するな★・`.gitignore`不触・lane不触・`_dead_letter_second`不触）。

測時=2026-08-06T21:26:22+09:00。git rev-parse HEAD=4061f26128a3c824061f941b746c1bfdff2b76fd。
hostname=USER-O6AK917NTU（SecondPC、実測、以下の運用主体判断に関わる）。

## 広域再索（filename-based、前票のkeyword検索の穴を埋める）

前票は`rsync|tar -c|cp -a |backup`等の★動詞キーワード★で検索した。本票は★filename★（`*sync*`）で`shim/`全体を再索。

```
$ find shim/ scripts/ -iname "*sync*"
shim/hakudokai/hakudokai_dashboard_sync.py   （前票で既読・DB→dashboard生成、backupに非ずと判定済）
shim/hakudokai/hakudokai_reports_sync.sh     ★前票未読・新規発見★
shim/hakudokai/hakudokai_task_sync.sh        ★前票未読・新規発見★
```
（前票のkeyword検索が動詞形`backup`のみを拾い、Supabase REST経由の同期は`curl`/`sb_curl`呼出のため引っ掛からなかった旨、自認する。之が前票の穴であった。）

## 新規発見2件の中身（全文実読・267行+276行）

**`hakudokai_reports_sync.sh`**（SecondPC上で稼働する設計・ヘッダ明記）＝
`queue/reports/{agent}_report.yaml` と `queue/tasks/{agent}.yaml` の変更をinotifywait監視し、
Supabase `pc_handshake` テーブルへ `file_sync` message（★全文content同梱★）としてPOST。
対象＝`SECONDPC_AGENTS="ashigaru2 ashigaru8"`の★2 agentのみ★（24行実測）。
MainPC側`secondpc_watcher_poll.py`がfile_syncを検知しローカル書き出し（コメント記載、本票では未検証）。

**`hakudokai_task_sync.sh`**（MainPC上で稼働する設計、ミラー実装）＝
MainPC側`queue/tasks/{ashigaru2,ashigaru8}.yaml`＋`CLAUDE.md`をSupabase `pc_handshake`へPOST、
SecondPC側`secondpc_receiver_poll.py`が受信しローカル書き出し（198-215行実測、対象2 agent＋CLAUDE.md）。

★両者ともqueue/inbox/**・dashboard.md・memory/**は対象に★含まれない★（24行/109-110行実測で対象fieldを確認、inbox/dashboard/memoryへの言及は本文中0件）。

## 現に動いておるか（実行はせず、状態のみ実測）

```
$ ps aux | grep -E "reports_sync|task_sync" → 0件（該当process無し）
$ ls -la /tmp/hakudokai_reports_sync.health /tmp/hakudokai_task_sync.health → 両方"No such file or directory"
$ systemctl --user list-unit-files | grep -i sync → auto-git-sync.service/.timer のみ、reports_sync/task_sync系は★0件★
$ systemctl list-unit-files | grep -iE "reports_sync|task_sync|hakudokai" → 0件
```
★之は「今この瞬間動いていない」だけでなく「healthcheck fileが一度も生成されていない＝過去に一度も起動した痕跡が無い」ことを示す★（health fileはscript内でstartup直後に書かれる設計、79-80行/該当箇所実測）。
かつ★systemd等の定期実行機構に一切登録されていない★（手動起動前提のscriptと見受けられる、本票では起動理由・運用実態までは踏み込まず、事実のみ記す）。

## 運用primaryの列挙（己で行う、上長は挙げず）

問い＝「queue/inbox/**・dashboard.md・memory/** にとって、★何が運用上のprimary（正本）か★」。

★答え＝各PCローカルの当該fileそのものが運用primaryである★。上位に別の正本は存在しない（CLAUDE.md「Context Layers」節でも`Layer 3: YAML Queue — persistent task data (queue/ — authoritative source of truth)`と明記済、本票で再確認）。

Supabase `pc_handshake` テーブルは：
- 通常の agent間 mailbox（inbox_write.sh経由の同一PC内配送）には★経由しない★（CLAUDE.md「Delivery Mechanism」節よりinbox_write.shはlocal yamlへflockで直接書く設計、本票では再読のみで新規実測はせず）。
- cross-PC配送（pc_handshake経由の別PC宛通知）には経由するが、これは★配送経路（transport）★であり、queue/inbox/**の内容を丸ごと複製する仕組みではない。
- 上記2 sync scriptに限っては、ashigaru2/ashigaru8のtask+report yaml（＋CLAUDE.md）を★複製先として一時的に経由★するが、対象は狭く、かつ現に動いていない（上記実測）。

∴ ★primaryは唯一・各PCローカルfile。之を離れて別の場所に「同じ物」が常時在るわけではない★。

## 欠けておる、と出た（前票の結論を追認・補強）

前票の結論（体系的backup=0件）は本追補でも★覆らず、むしろ補強された★：
- 見つかった2件の新規候補（reports_sync/task_sync）も、対象範囲がqueue/inbox・dashboard.md・memory/**を含まず、かつ現在非稼働（起動痕跡0件・systemd登録0件）。
- ∴ queue/inbox/**（全agent）・dashboard.md・memory/** に対する★私有耐久は、稼働中の物・停止中の物を問わず、現時点で0件★。

## 私有保全の案（★選択肢の列挙のみ・実装は一切していない★）

条の通り、欠けておると出た場合のみ記す。優先順位を付けず並列に3案：

- **案A**＝既存の`reports_sync.sh`/`task_sync.sh`の対象agent一覧を拡張し、対象fileにqueue/inbox/**・dashboard.md（内容そのものではなく事実断面）・memory/MEMORY.mdを加え、かつsystemd timer化して定期実行を保証する（既存機構の射程拡大）。
- **案B**＝`docs/incident_logs/2026-08-06_role_canon_gitignored_preserved_copy_{instructions,dashboard}_a1.md`の型（先例2件）を踏襲し、memory/MEMORY.mdについても「内容の全文複写」でなく「sha256+行数+測定秒の事実断面」を定期的にdocs/incident_logs/へcommitする（dashboard.mdで既に採用された「生き物には全文複写でなく断面記録」の原則をmemoryにも適用）。
- **案C**＝queue/inbox/**全体を対象にした専用の定期export機構を新設し、Supabaseの別table（pc_handshakeとは別、専用backup table）またはgit管理下の圧縮archiveへ日次で退避する。

いずれも★案の列挙に留め、実装・試行・backup実行は一切行っていない★。裁定は当職の権外。

## 己の手で為した事

- `find shim/ scripts/ -iname "*sync*"` で filename ベースの広域再索（前票のkeyword検索の穴を埋める目的、4件ヒット・うち2件が新規）
- `hakudokai_reports_sync.sh`（267行）・`hakudokai_task_sync.sh`（276行）を全文実読
- 対象agent・対象file・送信先（Supabase pc_handshakeテーブル）・方向（Second→Main / Main→Second）を本文中の変数定義・関数実装から実測確認
- `ps aux | grep` で両scriptの現在プロセス有無を確認（0件）
- `ls -la` で両scriptのhealthcheck file（`/tmp/hakudokai_{reports,task}_sync.health`）の存在有無を確認（両方無し）
- `systemctl --user list-unit-files` / `systemctl list-unit-files` でsystemd登録の有無を確認（0件）
- `hostname` で当機がSecondPC（USER-O6AK917NTU）である事を確認（reports_sync.shの想定稼働ホストと符合）
- `ls -la ~/.hakudokai/env` で当該env fileの存在のみ確認（中身は読んでいない、secret保護）
- 本追補の執筆中、scriptは一度も実行していない（`bash shim/...`等のコマンドは一切発行せず、`cat`/`grep`/`find`/`ps`/`ls`/`systemctl list-unit-files`のみ使用）

## 数の扱い

測時=2026-08-06T21:26:22+09:00／器=`find`+`ps`+`ls`+`systemctl list-unit-files`／範囲=`shim/`・`scripts/`全体＋`/tmp/hakudokai_*_sync.health`＋systemd user/system unit一覧。
`*sync*`file＝4件（前票既読1件+新規2件+前票未言及の`.pyc`1件はキャッシュゆえ対象外）。稼働中process＝0件。systemd登録＝0件。
以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

## 裁定は為さず、材料のみ（前票と同じ姿勢を維持）
