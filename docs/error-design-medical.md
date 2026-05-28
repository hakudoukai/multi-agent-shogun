# Error Design & Observability Mandate (理事長直接指示 — 2026-05-05)

**原則: 全ての新規実装は「エラー時の観察容易性」を最初から組み込むこと。事後追加は禁止。**

## 必須実装事項（全 watcher / API / バッチ / UI コード共通）

1. **構造化ログ (structured logging)**
   - JSON 形式で `timestamp`, `level`, `agent`, `task_id`, `correlation_id`, `error_type`, `stack_trace`, `context` を出力
   - 単純な print/console.log 禁止 (logger 経由必須)
   - ログレベル: DEBUG/INFO/WARN/ERROR/CRITICAL の5段階
   - フォーマット例: `{"ts":"2026-05-05T17:30:00+09:00","level":"ERROR","agent":"ashigaru1","task_id":"subtask_xxx","corr_id":"c-abc","error":"connection refused","ctx":{...}}`

2. **相関ID (correlation_id) 伝播**
   - リクエスト発生源で UUID を生成、全ログ・全API呼出・全DB操作に付与
   - 異常発生時に corr_id で一連の処理を即座に追跡可能
   - 多段処理 (A→B→C) でも同じ corr_id を渡す

3. **アラート発火条件の明示**
   - 各エラーケースで「ユーザー通知すべきか」「shogun inbox に通知すべきか」「忍びアラートか」を明記
   - 重要度別の配信先:
     - **CRITICAL**: shogun inbox + ntfy 通知 (即対応)
     - **ERROR**: shogun inbox (1日以内対応)
     - **WARN**: dashboard.md 表示 (週次レビュー)
     - **INFO**: ログのみ

4. **エラー時 fallback**
   - 失敗時のデフォルト値・代替経路を明示
   - 例: Supabase接続失敗 → ローカルSQLiteへフォールバック
   - 例: ntfy送信失敗 → ログに記録 + 次回再試行

5. **retry policy の明示**
   - retry cap (max 3-5)
   - 指数バックオフ (1s → 2s → 4s)
   - retry 超過時の終端処理 (dead-letter / アラート発火)

6. **ヘルスチェック endpoint or ファイル**
   - watcher 系: `/tmp/<watcher名>.health` に JSON で `{"alive":true,"uptime":N,"last_action":"..."}` を定期更新
   - API 系: `/api/health` で稼働状況返却
   - 5分以上更新されない = 死亡判定

7. **エラー再現可能性 (reproducibility)**
   - エラー発生時の入力・環境変数・関連DB状態を JSON dumpして `/tmp/error_dumps/` に保存
   - 後日デバッグ時に同じ状態を再現できるように

8. **ユーザー向けエラーメッセージ**
   - フロントエンドのエラー表示は「何が起きたか」「何をすべきか」「サポート連絡先」を含む
   - 内部スタックトレースを直接表示しない (セキュリティ)
   - 例: 「保存に失敗しました。再試行ボタンを押すか、しばらく経ってからお試しください。問題が続く場合は管理者にご連絡ください。」

## チェックリスト（実装着手前）

- [ ] logger 設定済み (構造化JSON出力)
- [ ] correlation_id 生成・伝播ロジック組込
- [ ] 各エラーケースに重要度ラベル付与
- [ ] fallback 経路明示
- [ ] retry cap 設定
- [ ] ヘルスチェック実装
- [ ] エラー dump 保存先確保
- [ ] ユーザー向けエラー文言レビュー済
- [ ] **エラーコード採番済**（後述§9）
- [ ] **メール通知配線済**（後述§10）
- [ ] **エラーダッシュボード統合**（後述§11）

これらを満たさない実装は本番投入禁止。三者監査でデコポン Axis 2 + ジェミちゃん observability_error_handling 観点で必ずチェック。

## §9. エラーコード体系（理事長直接指示 2026-05-05 — 短時間対応のため）

全エラーに一意なコードを付与。トラブル時にユーザー・サポート・開発者が即座に共通認識を持つ。

### コード形式
```
ERR-{機能ドメイン}-{連番3桁}
例: ERR-EKARTE-001  (ekarte 関連 No.1)
    ERR-AUTH-005   (認証関連 No.5)
    ERR-PDF-012    (PDF生成関連 No.12)
    ERR-WATCHER-003 (watcher系 No.3)
    ERR-SUPABASE-007 (Supabase通信 No.7)
    ERR-CARTE-022  (カルテット連動 No.22)
    ERR-INFRA-001  (インフラ層 No.1)
```

### 採番台帳
`docs/error_codes.md` に全エラーコードと意味・対処法を一元管理。
新規エラー追加時は採番→台帳追記→コードに反映の順。重複禁止。

### コード記載必須箇所
- 構造化ログ: `{"err_code":"ERR-EKARTE-001",...}`
- ユーザー画面: 「エラーコード: ERR-EKARTE-001」を必ず表示 + コピーボタン
- メール通知: 件名に `[ERR-EKARTE-001]` を含める
- Slack/ntfy: 同上
- API レスポンス: HTTP body に `error_code` フィールド

### 台帳エントリ形式（docs/error_codes.md）
```markdown
## ERR-EKARTE-001
- **発生条件**: ekarte 入力時、Supabase visit 作成失敗
- **重要度**: ERROR
- **メール通知**: あり (system-admin宛)
- **ユーザー表示文言**: 「カルテの記録に失敗しました。再試行してください。」
- **対処法**:
  1. Supabase 接続確認 (curl /api/health)
  2. ローカルSQLite フォールバック動作確認
  3. backend/api/ekarte_records.py:create_visit のログ確認
- **発生時 dump 取得項目**: patient_id, clinic_id, visit_date, payload
- **関連 corr_id 検索**: dashboard "ERR-EKARTE-001 last 7days"
```

## §10. メール通知配線（理事長直接指示 2026-05-05）

### 通知配信先と重要度マッピング
| 重要度 | 配信先 | SLA |
|--------|--------|-----|
| **CRITICAL** | 理事長メール + ntfy + shogun inbox + Slack | 即時（5分以内） |
| **ERROR** | 管理者メール + shogun inbox | 15分以内 |
| **WARN** | dashboard.md ハイライト | 翌日確認 |
| **INFO** | ログのみ | 不要 |

### メール送信実装方針（家老が実装発令時に指定）
推奨実装方法（順位順）:
1. **SendGrid / Resend / Mailgun 等のSaaS** （SMTP設定不要、配信成功率高、コスト低）
2. **Gmail SMTP** （アプリパスワード設定必要、社内利用なら可）
3. **Supabase Edge Function** （既存インフラ流用、追加サブスク不要）

メールテンプレート（必須項目）:
- 件名: `[{重要度}][{ERR-CODE}] {機能名} で異常検知 — {医院名}`
- 本文:
  - エラーコード（クリック可リンクで台帳へ）
  - 発生時刻（JST）
  - 影響範囲（医院ID、患者ID、操作中ユーザー）
  - エラー概要（1行）
  - 詳細スタックトレース（折りたたみ）
  - **対処手順**（台帳の対処法を埋込）
  - 関連ログ検索リンク（dashboard 連携）
  - correlation_id（同一リクエスト追跡用）
  - 発生件数（過去24h、過去1h）

### Rate Limit（メール爆撃防止）
- 同一エラーコード × 同一医院: 5分以内に1通のみ
- 5分間で5件以上発生 → サマリメール1通に集約
- 1日累計100通超過 → 配信停止 + 緊急アラート（ntfy）

## §11. エラーダッシュボード（短時間対応のため）

### ダッシュボード配置
- **管理画面**: `/admin/errors` (frontend に新規追加)
- **dashboard.md**: 「🔥 直近エラー」セクションに最新10件 + 集計

### 表示項目
- 過去24h のエラーコード別発生件数（棒グラフ）
- 直近10件の一覧（時刻、コード、医院、患者、ユーザー）
- 各行クリックで詳細モーダル（dump 表示）
- フィルタ: 重要度、エラーコード、医院、期間
- エクスポート: CSV / JSON

### バックエンドDB
- Supabase に `error_log` テーブル新規作成
  - id, timestamp, err_code, severity, agent, clinic_id, patient_id, user_id, corr_id, error_message, stack_trace (text), dump_path, resolved_at, resolved_by, notes
  - インデックス: (timestamp), (err_code), (clinic_id, timestamp)
  - RLS: 各医院は自医院のエラーのみ参照可、理事長は全件参照可

### 解決ワークフロー
- エラー発生 → DB INSERT + メール送信 + ダッシュボード反映
- 開発者が `resolved_by`, `notes`, `resolved_at` を更新 → 解決済マーク
- 同一エラーが7日以内に再発した場合は「再発」フラグ表示

## §12. ユーザー向けエラー画面標準

各画面のエラー表示は以下フォーマットで統一:

```
┌──────────────────────────────────────┐
│ ⚠ エラーが発生しました                 │
├──────────────────────────────────────┤
│ エラーコード: ERR-EKARTE-001 [📋コピー]│
│                                      │
│ カルテの記録に失敗しました。           │
│ お手数ですが、再試行してください。     │
│                                      │
│ 問題が続く場合：                       │
│  - スタッフへ口頭連絡                  │
│  - 管理者メール: support@example.jp   │
│    エラーコードをお伝えください        │
├──────────────────────────────────────┤
│ [ 再試行 ]  [ 詳細を見る ]  [ 閉じる ]│
└──────────────────────────────────────┘
```

「詳細を見る」展開でスタックトレース・corr_id・操作履歴を表示（コピー可）。

## §13. オンコール対応支援

トラブル時の短時間対応支援機能：

1. **ワンクリック診断スクリプト**: `scripts/diagnose.sh ERR-EKARTE-001`
   - 該当エラーコードの定義を表示
   - 過去24hの発生履歴
   - 推奨対処手順
   - 関連プロセス・ログを自動収集
2. **自動修復試行（限定的）**: 「Supabase接続失敗」など特定エラーで安全な再試行を自動実行
3. **エスカレーション通知**: 同一エラーが10分以内に5回再発 → 理事長 ntfy 自動発火
4. **障害報告書テンプレート**: エラー解決後、`docs/incident_logs/` に自動雛形生成

## §14. 既存コード段階的整備ルール（Boy Scout Rule） — 理事長直接指示 2026-05-05

**原則: 機能追加時、その機能と関連する既存コードにも同じ仕掛けを「ついでに」組み込む。**

過去経緯：エラー設計義務（§1〜§13）は2026-05-05に新設したため、それ以前の既存コードには未組込みの箇所が多数ある。一気にリファクタは現実的でないため、**機能追加 commit に「ついで整備」を必ず含める**運用とする。

### 必須範囲（変更ファイル + 直接依存ファイル）

新機能 commit に含める「ついで整備」の範囲：

1. **直接編集するファイル**: 当然、エラー設計8項目を全充足
2. **当該機能から呼び出されるファイル（直接依存）**: エラーコード・構造化ログ・correlation_id 伝播を組込
3. **同じディレクトリ配下で類似機能のファイル**: 関連性が明確なら整備対象（例: `panels/CariesPanel.tsx` 触ったら `CRFillingPanel.tsx` も整備）

### 範囲外（次回担当者が整備）

- 関連性が薄い別ドメインのファイル
- 影響範囲不明な巨大共通モジュール（別 cmd で計画的整備）
- 試験用・廃止予定コード

### タスクYAML 必須記載項目（家老責務）

家老が新機能タスク発令時、以下を必ず明記：

```yaml
boy_scout_targets:
  primary_files:        # 新規/直接編集ファイル
    - path/to/new_feature.tsx
  related_existing_files:  # ついで整備対象
    - path/to/existing_caller.tsx
    - path/to/sibling_panel.tsx
  rationale: "新機能 X は既存 Y/Z を経由するため、エラーコード採番＋構造化ログ統一を同時実施"
  excluded_with_reason:  # 範囲外と判断した既存ファイル + 理由
    - path: path/to/big_legacy.py
      reason: "影響範囲過大、別 cmd で計画的整備"
```

### 三者監査時の整備度チェック

ジェミちゃんの **observability_error_handling 観点** で必ず確認：

- 新規ファイル: 8項目全充足（必須）
- 直接依存既存ファイル: 8項目のうち最低 5項目組込（構造化ログ + correlation_id + エラーコード + アラート発火 + retry/fallback）
- 関連既存ファイル: 8項目のうち最低 3項目組込（構造化ログ + correlation_id + エラーコード）
- 範囲外と宣言したファイル: 妥当性確認（過剰除外なら指摘）

### 重要：scope 爆発の防止

「ついで整備」が新機能本体の3倍を超えるなら：
1. 当該cycle は最小限のみ整備
2. 残りは別 cmd `cmd_legacy_observability_<domain>_001` として家老が計画的発令
3. ただし「最低限」 = エラーコード採番 + 構造化ログ への切替 は必ず実施

### 累積整備状況の可視化

`docs/observability_coverage.md` に整備済ファイル一覧を更新（家老責務）：

```markdown
## カバレッジ
- エラーコード採番済: 78 / 350 ファイル (22%)
- 構造化ログ移行済: 105 / 350 ファイル (30%)
- correlation_id 伝播: 62 / 350 ファイル (18%)
- ヘルスチェック: 8 / 12 watcher系 (67%)

## 直近整備（2026-05-05）
- frontend/src/features/ekarte-v6/* 全件 (Phase 2)
- backend/utils/knowledge_fetcher.py (Phase 1 ついで整備)
```

毎週月曜に家老が更新、信長がレビュー。100%到達まで継続。

## §15. 自動復旧（Self-Healing）パターン — 理事長直接指示 2026-05-05

**原則: トラブル時の可能な範囲で自動復旧を組み込む。ただし「暴走防止 > 自動性」を最優先。**

過去事故（2026-05-05 SecondPC 暴走）の教訓：watchdog の自動再起動が暴走を増幅させた。**自動復旧は強力だが、安全装置がなければ事態を悪化させる**。

### 安全な自動復旧パターン（推奨・実装可）

| # | パターン | 適用例 | 必須安全装置 |
|---|---------|--------|-------------|
| **SH1** | Circuit Breaker | DB接続失敗時に一時遮断、間隔をおいて再試行 | 失敗閾値 + cooldown + 手動 reset 経路 |
| **SH2** | Exponential Backoff Retry | API呼出失敗時 1s→2s→4s→8s で再試行 | retry cap (5回) + dead-letter |
| **SH3** | Fallback (Graceful Degradation) | Supabase不通時 ローカルSQLite に切替 | 復旧時の自動同期 + 状態整合性チェック |
| **SH4** | Stale Lock 自動解除 | 30分以上更新なしの lock を自動釈放 | lock holder のヘルスチェック必須 |
| **SH5** | Connection Pool 自動再接続 | DB接続切れを検知して新規確立 | 接続上限 + leak 検知 |
| **SH6** | Self-Restart (限定的) | watcher 死亡検知時に再起動 | **手動停止フラグ尊重 + 再起動上限 + escalation** |
| **SH7** | Cache 自動無効化 | TTL 経過 or 特定イベント時に再取得 | キャッシュ汚染検知 |
| **SH8** | Idempotent Retry | 同じ操作を冪等に再試行 | DB側 UNIQUE制約 必須 |
| **SH9** | State Machine 復元 | 不整合な状態 → 既知の正常状態へ遷移 | 遷移ログ + 手動承認モード |
| **SH10** | Health-based Routing | 死んだ replica を自動排除 | minimum 1台維持 + アラート |

### 危険な自動復旧パターン（禁止・人間判断必須）

| # | パターン | 危険な理由 |
|---|---------|----------|
| **D1** | データ書き換えの自動修復 | 真値判定不能、データ破壊リスク |
| **D2** | 連続失敗時の無限再起動 | 2026-05-05 暴走と同型 |
| **D3** | 認証失敗時の自動権限昇格 | セキュリティ脆弱性 |
| **D4** | 患者データの自動マージ | 医療事故リスク |
| **D5** | 課金処理の自動再試行（同一トランザクション） | 二重課金リスク |
| **D6** | 設計変更を伴う migration の自動 rollback | スキーマ整合性破壊 |

### 必須実装事項（全 self-healing パターン共通）

1. **手動停止フラグ尊重**:
   - `~/.openclaw/global_disable` または `~/.openclaw/disable_<feature>` があれば自動復旧 OFF
   - 全 SH パターンが起動時にチェック必須
2. **復旧上限**:
   - 同一エラーの自動復旧試行は1時間以内に最大5回
   - 超過したら escalation（理事長 ntfy + 手動介入待ち）
3. **復旧ログの永続化**:
   - 全自動復旧アクションを `error_log` テーブルに記録（trigger='self_healing'）
   - dashboard で復旧頻度を可視化（多すぎる = 根本問題あり）
4. **エスカレーション条件**:
   - 自動復旧後も10分以内に同じエラー再発 → CRITICAL alert
   - 異なるエラー連鎖（A→B→C）が3つ以上 → CRITICAL alert
5. **「復旧失敗」も明示通知**:
   - 自動復旧を試みたが失敗 → メール+ntfy で「自動対応失敗、人間介入要」
6. **Dry-run mode**:
   - 全 SH パターンに `--dry-run` フラグ実装、本番投入前にログのみ出力で動作確認

### タスクYAML 必須記載（家老責務）

新機能タスクで自動復旧を組み込む場合、明記する：

```yaml
self_healing:
  patterns: [SH1, SH2, SH3]
  rationale: "DB接続失敗時のローカルSQLiteフォールバック + Circuit Breaker"
  manual_override: "~/.openclaw/disable_ekarte_fallback"
  retry_cap: 5
  escalation_target: "ntfy:director, email:admin@example.jp"
  dry_run_first: true  # 本番投入前にdry-runで1週間観察
  excluded_dangerous_patterns: [D1, D4]  # 適用禁止理由つき明示
```

### 既存システムへの導入順序（家老の段階的整備計画）

優先順位：

1. **Phase 1 (即時)**: SH2 (retry+backoff), SH8 (idempotent retry) — リスク低
2. **Phase 2 (1ヶ月)**: SH1 (circuit breaker), SH3 (fallback) — DB系
3. **Phase 3 (3ヶ月)**: SH5 (connection pool), SH7 (cache) — インフラ系
4. **Phase 4 (慎重)**: SH4 (stale lock), SH6 (self-restart) — 安全装置を厳格に
5. **Phase 5 (最後)**: SH9, SH10 — 状態遷移系（最も慎重に）

各 Phase で三者監査必須（特にデコポン Axis 2 + ジェミちゃん system_relations + side_effects）。

### ダッシュボード追加項目

`/admin/self-healing` または dashboard.md に以下を表示：

- 過去24hの自動復旧成功/失敗件数
- パターン別発生頻度（SH1～SH10）
- escalation した件数
- 失敗連鎖の検知件数
- 「自動復旧頻度が高すぎる」アラート（根本問題のサイン）

### 既存コード適用時の Boy Scout Rule

§14 ルールに従い、新機能追加時に関連既存コードにも SH パターンを「ついで導入」：

例: ekarte-v6 Phase 6（カルテット連動）追加時：
- 新規: SH2 + SH3 必須
- 直接依存: 既存 `karte_transfer_v2.py` にも SH1 + SH2 を追加
- 関連既存: 既存 `inbox_write.sh` にも SH8 (idempotent) を追加

## §16. トラブル自動応答パイプライン（信長直結） — 理事長直接指示 2026-05-05

**原則: トラブル発生 → 信長へ即通知 → 自動診断 → 自動対応試行 → 失敗時理事長へ報告。**

### 流れ

```
[エラー発生]
   ↓
[error_log INSERT + メール送信 (§10)]
   ↓
[severity=CRITICAL/ERROR ?]
   ├─ YES → [shogun inbox に critical_alert 即時 inbox_write]
   │         ↓
   │     [信長が inbox 受信]
   │         ↓
   │     [自動診断: scripts/diagnose.sh ERR-XXX-001 実行]
   │         ↓
   │     [既知パターン (runbook 存在) ?]
   │         ├─ YES → [自動対応試行 (runbook 実行)]
   │         │         ↓
   │         │     [対応成功 ?]
   │         │         ├─ YES → [error_log resolved 記録 + 理事長へ「自動解決済」報告]
   │         │         └─ NO  → [理事長 ntfy 緊急発火 + 詳細レポート]
   │         └─ NO  → [信長が情報収集して理事長へ初期報告]
   └─ NO  → [dashboard.md 表示のみ、自動応答なし]
```

### 信長 (shogun) のトラブル受信時の標準対応

shogun の inbox に `type=critical_alert` メッセージが届いたら、Session Start 手順より優先で以下を実行：

1. **即時診断**:
   ```bash
   bash scripts/diagnose.sh <ERR-CODE>
   # 出力: 過去24h発生履歴 / 推奨対処手順 / 関連プロセス・ログ自動収集
   ```
2. **runbook 照会**:
   ```bash
   ls docs/runbooks/<ERR-CODE>.md
   ```
   - 存在 → runbook 手順を実行（自動化可部分）
   - 不在 → 標準テンプレで初期報告生成
3. **runbook 実行ログ**: 各ステップを error_log に追記（trigger='shogun_runbook'）
4. **対応結果に応じた報告**:
   - 成功 → 理事長 inbox + ntfy「✅ 自動解決: ERR-XXX」
   - 部分成功 → 理事長 ntfy「⚠ 一部対応済、追加対応必要」+ 残課題明記
   - 失敗 → 理事長 ntfy「🔴 自動対応失敗、緊急介入要」+ 完全レポート

### Runbook 形式（docs/runbooks/<ERR-CODE>.md）

```markdown
