# 三者監査フレームワーク（完全版）

**作成**: 2026-05-05（理事長直接指示「緻密に・抜け漏れなく設計」）
**対象**: 信長・家老・家康・足軽・忍び 全エージェント
**改訂責務**: 信長直轄。家老・家康は提案のみ可、改訂は信長の発令を要す

---

## 0. 設計原則（5原則）

| # | 原則 | 理由 |
|---|------|------|
| **P1** | **第三者性**: コードを書いた者が監査してはならぬ | 自作自演バイアスの完全排除 |
| **P2** | **差分主義**: 監査対象は差分のみ。フル走査禁止 | API料金抑制 + 偽陽性ノイズ抑制 + cycle進行に伴う収束保証 |
| **P3** | **三者全員PASS必須**: 一者NGなら未完了 | 単一視点の見落とし防止 |
| **P4** | **再現可能性**: 同じ diff を渡せば誰でも同じ判定が出る | 家康交代・監査者不在時の継続性 |
| **P5** | **トレーサビリティ**: 全監査結果はYAMLに永続記録 | 後日問題発生時の責任追跡・学習資料化 |

---

## 1. 監査ライフサイクル

### 1.1 トリガー

監査は以下のイベントで**自動的に**発動する：

| トリガー | 監査対象 | 起動責務 |
|---------|---------|---------|
| 足軽が `status: done` 報告 | 該当タスクのコミット範囲 | 足軽 → 家康 inbox_write |
| 設計書（DD-XXX）変更 commit | 影響受けるコード全て | 家老が検知 → 家康に発令 |
| DBスキーマ変更（migration） | RLS・型・参照整合性 | 家老が検知 → 家康に発令 |
| セキュリティパッチ commit | 緊急監査（SLA: 30分） | 足軽 → 家康 inbox_write priority=critical |
| cycle1 PASS後 mainブランチmerge前 | 最終確認（家康のみ、Codex/Gemini省略可） | 家老が判断 |

### 1.2 ステート遷移

```
not_started
   ↓ (足軽完了報告)
cycle1_in_progress  ← 初回監査
   ↓
   ├─ 三者PASS → final_pass → 完了
   └─ 一者以上FAIL → cycle2_pending (足軽に修正指示)
                        ↓ (足軽修正完了)
                     cycle2_in_progress
                        ↓
                        ├─ PASS → final_pass
                        └─ FAIL → cycleN_pending ... (max 5サイクル)
                                                       ↓ (5回超過)
                                                    escalated → 家老判断
```

### 1.3 各ステージの責務

| ステージ | 責務 | 期限SLA |
|---------|------|---------|
| 完了報告書作成 | 足軽 | 完了から10分以内 |
| 家康受領→監査開始 | 家康 | 通知から15分以内 |
| 家康レビュー | 家康 | 開始から30分以内 |
| Codex監査呼出 | 家康 | 家康レビュー後5分以内 |
| Gemini監査呼出 | 家康 | Codex後5分以内（並列可） |
| 家康最終判定→家老報告 | 家康 | 全監査完了から10分以内 |
| 家老の次タスク発令（FAIL時） | 家老 | 家康報告から15分以内 |

SLA超過は忍びがアラート（cooldown 30分）。

---

## 2. 監査スコープ（差分主義の具体実装）

### 2.1 スコープ判定アルゴリズム

```
監査対象決定:
  IF cycle == 1:
      base_commit = タスク開始時のHEADコミット (queue/tasks/<agent>.yaml の base_commit フィールド)
      head_commit = 報告書の最終commitハッシュ
  ELSE (cycle >= 2):
      base_commit = 前cycleの最終fix commit (gunshi_report.yaml の last_fix_commit)
      head_commit = 今回のfix commit
  
  changed_paths = git diff --name-only base_commit..head_commit
  
  # 除外パス
  changed_paths -= [
    "**/node_modules/**",
    "**/.venv/**",
    "**/dist/**", "**/build/**",
    "**/*.lock", "**/package-lock.json",
    "**/.git/**",
    "**/coverage/**",
    "**/__pycache__/**"
  ]
  
  diff_content = git diff base_commit..head_commit -- $changed_paths
```

### 2.2 タスク開始時の base_commit 記録（必須）

足軽は作業開始時に以下を `queue/tasks/<agent>.yaml` に記録：

```yaml
task:
  task_id: subtask_xxx
  base_commit: "abc12345"   # 作業開始時の HEAD ハッシュ
  status: assigned
  ...
```

これがないと cycle1 の base が確定できない。家老がタスク発令時に `git rev-parse HEAD` を埋め込む。

### 2.3 例外: スコープ拡大が必要な場合

以下のケースのみ、家康の判断で**スコープ拡大**を許可する。理由を `audit.scope.expansion_reason` に記載必須。

- 削除ファイルが他コードから参照されていないか確認（呼出元検索）
- 公開API変更時の呼出元影響範囲確認
- DBスキーマ変更時のクエリ全件チェック
- テスト網羅性確認（cycle1のみ、テストの存在確認）

---

## 3. 家康（Claude）監査チェックリスト

家康は Codex/Gemini に投げる前に**自ら以下を確認**する。家康の独立判断は不可欠。

### 3.1 構造監査（必須）

- [ ] アーキテクチャ整合: 既存パターンとの整合性（context/*.md 参照）
- [ ] 命名規約: 既存ファイル・関数命名との一貫性
- [ ] 依存方向: 循環依存・レイヤー違反なし
- [ ] エラーパス: 全エラーケースが処理されているか
- [ ] 設定値: ハードコーディングがないか（環境変数・config化）

### 3.2 既存資産活用（Anti-Duplication準拠）

- [ ] 既存類似コードを `grep` 検索済み（context/dentalbi-inventory.md 参照）
- [ ] 重複実装が発生していないか
- [ ] 流用すべき関数・コンポーネントが他にあるか
- [ ] 共通化可能なロジックが切り出されているか

### 3.3 Root Cause 4 Patterns 確認

CLAUDE.md §Root Cause 4 Patterns 必須チェック：

- [ ] パターン1: 旧版と新版の併存がないか
- [ ] パターン2: 廃止DDの参照残存がないか
- [ ] パターン3: task_tracker と実態の乖離がないか
- [ ] パターン4: 同名・同責務の重複定義がないか

### 3.4 テスト網羅性

- [ ] 新規追加コードに対応するテストが存在
- [ ] SKIP=0（CLAUDE.md §Test Rules）
- [ ] 境界値テスト（空・null・最大値・最小値）
- [ ] エラーパステスト
- [ ] 既存テストの回帰がない

### 3.5 家康判定基準

- すべてPASS → Codex監査へ進む
- 一つでもFAIL → 家康の判定で足軽に差戻し（Codex/Gemini呼出し前）。修正後再監査。
  - 早期差戻しは無料（API料金節約）
  - 家康指摘の証跡は `audit.gunshi.findings` に記録

---

## 4. Codex（デコポン）監査 — 6軸固定

### 4.1 軸定義（変更不可）

| 軸 | 名称 | 観点詳細 |
|----|------|---------|
| **Axis 1** | セキュリティ脆弱性 | OWASP Top 10、認証・認可、SQLi/XSS/CSRF、機密漏洩、暗号化、セッション管理、CORS、入力検証 |
| **Axis 2** | バグ・エラーハンドリング | 例外処理、null/undefined、境界値、リソースリーク、レースコンディション、デッドロック、無限ループ |
| **Axis 3** | 型整合性・契約 | TypeScript/Python型、関数シグネチャ、暗黙キャスト、any濫用、ジェネリクス、Optional処理 |
| **Axis 4** | テスト網羅性 | 新規テストの妥当性、SKIP=0、境界・異常系カバレッジ、モック適切性、回帰テスト |
| **Axis 5** | 既存コードとの重複 | Anti-Duplication Rule準拠、再利用妥当性、共通化候補、命名衝突 |
| **Axis 6** | Git Persistence・コミット粒度 | atomic commits、commitメッセージ品質、ブランチ戦略、不要ファイル混入なし |

### 4.2 Codex呼出しコマンド（標準化）

```bash
# 家康が実行
DIFF=$(git -C /mnt/c/Users/User/Documents/DentalBI \
  diff <base_commit>..<head_commit> -- <changed_paths>)

cat <<EOF | npx @openai/codex exec --json --output-last-message /tmp/codex_audit_<task_id>_<cycle>.json
あなたはコードレビュー専門家。以下の git diff を6軸監査してください。

タスクID: <task_id>
サイクル: <cycle>
変更パス: <changed_paths>

=== 監査軸 ===
Axis 1: セキュリティ脆弱性
Axis 2: バグ・エラーハンドリング  
Axis 3: 型整合性・契約
Axis 4: テスト網羅性
Axis 5: 既存コードとの重複（Anti-Duplication Rule）
Axis 6: Git Persistence・コミット粒度

=== 出力形式（JSON） ===
{
  "task_id": "<task_id>",
  "cycle": <cycle>,
  "axes": {
    "axis1_security": {"verdict": "pass|fail", "findings": [{"severity": "critical|high|medium|low", "id": "S1", "description": "...", "file": "...", "line": <num>, "fix_suggestion": "..."}]},
    "axis2_bugs": {...},
    "axis3_types": {...},
    "axis4_tests": {...},
    "axis5_duplication": {...},
    "axis6_git": {...}
  },
  "overall_verdict": "pass|fail",
  "summary": "総括"
}

=== 差分 ===
$DIFF
EOF
```

### 4.3 Codex usage limit 時のフォールバック

OpenAI API usage limit に達した場合：

1. **家康が前cycleのCodex判定を引用可能** — ただし以下の全てを満たす場合のみ：
   - 当該cycleの fix が前cycleでCodexが指摘した内容と完全一致
   - fix の diff が極小（< 50行）
   - 家康が独立に動作確認済
2. その旨を `audit.codex.fallback_reason` に明記
3. 24時間以内に必ず Codex 再監査をスケジュール（家老が cron 登録）

---

## 5. Gemini（ジェミちゃん）監査 — システム整合性審査（完成まで）

> **【重要・理事長殿確定 2026-05-05】役割変更**:
> 完成までの開発期間中、ジェミちゃんは **システム整合性・関連性審査** に専念する。
> 法令準拠・医療情報取扱い・個人情報保護は **全機能完成後の最終総合監査** に回す。
> 理由: 稼働中のプログラム不整合トラブル防止が最優先（理事長殿御指示）。
> デコポン（コードレベル6軸）と異なる **俯瞰視点** で同じ diff を審査する。

### 5.1 観点定義（開発期間中 = システム整合性版・8観点）

| 観点 | 重点項目 |
|------|---------|
| **仕様準拠** | DD-XXX設計書突合、acceptance_criteria全項目充足、context/*.md記載との整合 |
| **システム関連性** | 変更が他モジュールに与える影響範囲、API契約変更時の呼出元、共有state/contextの破壊有無 |
| **副作用・依存関係** | DB トリガ・watcher・cron・hookで連鎖発動する処理、循環依存、レースコンディション |
| **網羅性** | エッジケース、空入力、境界値、エラーパス、並行実行、タイムアウト、リソースリーク |
| **データフロー整合** | 入力→処理→保存→読出 の全経路でデータが正しく流れるか、SSOT (single source of truth) 維持 |
| **拡張性 (extensibility)** | 将来の機能追加に耐える設計か。抽象化レベル、ハードコード値の有無、インターフェース柔軟性、段階的migration可能性、新医院/新ロール/新処置追加時の影響 |
| **観察可能性・エラー処理 (observability_error_handling)** | 構造化ログ・correlation_id 伝播・アラート発火条件・fallback経路・retry cap・ヘルスチェック・エラーdump保存・ユーザー向けエラーメッセージ。CLAUDE.md §Error Design & Observability Mandate 8項目チェック |
| **ドキュメント整合** | コメント、JSDoc/docstring、README、型定義、変更履歴、設計書の同期 |

### 5.1.1 拡張性 (extensibility) 観点の詳細

理事長殿御指示 2026-05-05 — 「将来の拡張に耐える設計か」を必ず審査せよ：

- **新医院展開**: clinic_id=5 (香椎照葉) 以外の医院追加時に動くか。clinic_id ハードコード禁止
- **新処置追加**: 処置マスタの新規エントリ追加で対応できるか。処置種別ごとの switch文濫用禁止
- **新ロール追加**: Dr/DH/受付以外のロール（理事長/事務長 等）追加時の権限チェック
- **新書類追加**: PDF テンプレート1本追加で済むか、コード変更が必要か
- **新法令対応**: 診療報酬改定（2年毎）への追従容易性
- **新デバイス対応**: iPad 横画面以外（PC/iPad縦/iPhone）への対応余地
- **新言語対応**: 多言語化の前提を阻害しない実装か (ハードコード日本語文字列の有無)
- **DB スキーマ進化**: マイグレーション履歴の整合性、後方互換性、ENUM 値追加の容易性
- **API バージョニング**: v1/v2 共存の余地、breaking change 検知

### 5.1bis 法令観点（最終総合監査でのみ実施）

全機能完成後の最終フェーズで以下を別 cmd として実施:
- 医療法、個人情報保護法、医療情報取扱いガイドライン
- 保護者同意（15歳未満）、診療録管理規則
- PII 取扱い、暗号化、保存期間

これらは開発期間中はスキップ（運用品質優先）。

### 5.2 Gemini呼出しコマンド（標準化）

```bash
DIFF=$(git diff <base_commit>..<head_commit> -- <changed_paths>)
SPEC_REF=$(cat context/<project>.md 2>/dev/null | head -200)

cat <<EOF | gemini -p
あなたはシステム整合性審査専門のレビュアー（デコポンとは異なる俯瞰視点）。以下のdiffを審査せよ。
法令観点は今回スキップ（完成後の最終監査で実施）。

タスクID: <task_id>
サイクル: <cycle>

=== 審査観点（開発期間中・システム整合性版・7観点） ===
1. 仕様準拠: 設計書と乖離がないか
2. システム関連性: 他モジュールへの影響範囲、API契約変更の呼出元影響
3. 副作用・依存関係: watcher/trigger/hook連鎖、循環依存、レース
4. 網羅性: エッジケース、リソースリーク
5. データフロー整合: 入力→処理→保存→読出 経路、SSOT維持
6. 拡張性: 将来の機能追加に耐えるか (新医院/新処置/新ロール/新書類/法令改定/新デバイス/多言語/DBスキーマ進化/API バージョニング)
7. ドキュメント整合: コメント・型・README・設計書の同期

=== 設計書抜粋 ===
$SPEC_REF

=== 差分 ===
$DIFF

=== 出力形式（JSON） ===
{
  "task_id": "<task_id>",
  "cycle": <cycle>,
  "categories": {
    "spec_compliance": {"verdict": "pass|fail", "findings": [...]},
    "system_relations": {"verdict": "pass|fail", "findings": [...]},
    "side_effects": {"verdict": "pass|fail", "findings": [...]},
    "completeness": {"verdict": "pass|fail", "findings": [...]},
    "data_flow": {"verdict": "pass|fail", "findings": [...]},
    "extensibility": {"verdict": "pass|fail", "findings": [...]},
    "observability_error_handling": {"verdict": "pass|fail", "findings": [...]},
    "documentation": {"verdict": "pass|fail", "findings": [...]}
  },
  "overall_verdict": "pass|fail",
  "summary": "総括"
}
EOF
```

### 5.3 法令該当時の必須化

以下を扱う差分は Gemini 監査必須・省略禁止：

- 患者情報（氏名、生年月日、診療内容、画像）
- 認証・認可（ログイン、権限、トークン）
- 同意フロー（保護者同意、診療同意）
- 暗号化・PII処理

---

## 6. PASS/FAIL 判定基準

### 6.1 個別判定

| 監査者 | PASS基準 |
|--------|----------|
| 家康 | 構造監査・既存資産活用・Root Cause 4P・テスト網羅 全PASS |
| Codex | 6軸全PASS、Critical/High指摘0件 |
| Gemini | 5観点全PASS、Critical/High指摘0件 |

Severity 定義：
- **Critical**: セキュリティ脆弱性・データ破損・障害発生
- **High**: 機能不全・仕様未充足
- **Medium**: 改善余地大
- **Low**: 軽微（コメント、命名提案）

Medium/Low は PASS だが `findings` に記録、後続改善タスクに回す。

### 6.2 総合判定

```
overall_pass = (gunshi == PASS) AND (codex == PASS) AND (gemini == PASS)
```

一つでも FAIL → cycleN+1 へ。

### 6.3 監査者間の不一致（コンフリクト解消）

| 状況 | 対応 |
|------|------|
| Codex PASS / Gemini FAIL | Gemini指摘を採用（より厳しい方） |
| Codex FAIL / Gemini PASS | Codex指摘を採用 |
| 家康 PASS / Codex or Gemini FAIL | 家康は再考、最終的に外部判定優先 |
| 三者で評価が割れた | 家老エスカレーション、理事長判断 |

---

## 7. PDCA循環の制御

### 7.1 サイクル上限

- **通常タスク**: 最大 **5サイクル**
- **緊急パッチ**: 最大 **3サイクル**

### 7.2 5サイクル超過時のエスカレーション

```
cycle5 で FAIL → 家康から家老に escalation 報告
  → 家老が以下を判断:
    1. タスクスコープが大き過ぎる → 分割
    2. 実装方針が誤り → 設計やり直し（前cycle破棄）
    3. 監査が過剰 → 受容可否を理事長に相談
    4. 足軽の能力不足 → 別足軽 or 家康が直接実装
```

### 7.3 サイクル間の進捗監視

忍び（activity_monitor）が以下を監視：

- 同一サブタスクで cycle が 30分進行しない → `pdca_stalled` アラート
- 同一サブタスクで cycle3 を超えた → `pdca_extended` アラート
- 5サイクル超過 → `pdca_escalation_required` アラート

---

## 8. 監査者不在時のフォールバック

| 状況 | フォールバック |
|------|---------------|
| Codex API usage limit | §4.3 のフォールバック条件下で家康が前cycle引用 |
| Codex 一時的停止（504, タイムアウト） | 5分後に最大3回リトライ → ダメなら家康が前cycle引用 |
| Gemini API停止 | 1時間待機 → ダメなら家老エスカレーション（法令該当差分は強制待機） |
| 家康Claude停止 | Codex/Geminiは実行不可。家老が監視→Claude復旧待ち |
| 全監査者停止 | 家老が緊急停止指令、足軽の作業も一時停止 |

---

## 9. 監査レポートYAML スキーマ（標準化）

`queue/reports/gunshi_report.yaml` に以下構造で記録：

```yaml
task_id: gunshi_qc_<ashigaru_task_id>_cycle<N>
ashigaru_task_id: <task_id>
cycle: <N>
type: quality_check_three_party_cycle<N>
timestamp: "<ISO8601>"

audit:
  scope:
    base_commit: "<hash>"
    head_commit: "<hash>"
    changed_paths: ["path1", "path2"]
    diff_lines_added: <N>
    diff_lines_removed: <N>
    expansion_reason: null  # スコープ拡大時のみ理由記載
  
  gunshi:
    verdict: pass|fail
    structural: pass|fail
    anti_duplication: pass|fail
    root_cause_4p: pass|fail
    test_coverage: pass|fail
    findings:
      - {id: G1, severity: high, description: "...", file: "...", line: 42}
  
  codex:
    verdict: pass|fail
    invocation_log: "/tmp/codex_audit_<task>_<cycle>.json"
    verified_by_reading: true_via_diff  # 必須。falseなら違反
    axes:
      axis1_security: {verdict: pass, findings: []}
      axis2_bugs: {verdict: pass, findings: []}
      axis3_types: {verdict: pass, findings: []}
      axis4_tests: {verdict: pass, findings: []}
      axis5_duplication: {verdict: pass, findings: []}
      axis6_git: {verdict: pass, findings: []}
    fallback_reason: null  # usage limit時のみ
    summary: "..."
  
  gemini:
    verdict: pass|fail
    invocation_log: "/tmp/gemini_audit_<task>_<cycle>.txt"
    verified_by_reading: true_via_diff
    categories:
      spec_compliance: {verdict: pass, findings: []}
      completeness: {verdict: pass, findings: []}
      legal_compliance: {verdict: pass, findings: []}
      documentation: {verdict: pass, findings: []}
      ux: {verdict: pass, findings: []}
    summary: "..."

qa_decision: pass|fail
final_verdict_rationale: |
  ...

cycle_history:
  cycle1: {issues_found: <N>, issues_resolved: <M>, last_fix_commit: "<hash>"}
  cycle2: {...}
  ...

next_action:
  if_pass: "家老に完了報告"
  if_fail: "足軽<X>に修正指示。findings G1, S2, L1 を fix せよ"
```

---

## 10. 家老による監査検証（メタ監査）

家老は家康の監査結果を**機械的に検証**する。以下のチェックを `cmd完了処理時` に実施：

### 10.1 必須チェックリスト

- [ ] `audit.gunshi.verdict` 存在
- [ ] `audit.codex.verdict` 存在
- [ ] `audit.codex.verified_by_reading == true_via_diff` （フル走査でない証跡）
- [ ] `audit.gemini.verdict` 存在
- [ ] `audit.gemini.verified_by_reading == true_via_diff`
- [ ] `audit.scope.base_commit` と `audit.scope.head_commit` 存在・有効ハッシュ
- [ ] 三者全PASS （`overall_pass == true`）
- [ ] PII/法令該当差分の場合、`audit.gemini.categories.legal_compliance == pass`
- [ ] cycle数 が 5以下

### 10.2 違反検知時の対応

```
違反検知 → 監査結果を無効化 → 家康に再監査指令（specific reason付き）
            ↓
       足軽 status: done のままだが audit_status: invalid
       忍びが audit_invalid_redo アラート発火
```

---

## 11. 忍び（activity_monitor）統合

忍び `hakudokai_activity_monitor.sh` が以下を監視：

| アラート | 検知条件 | クールダウン |
|---------|---------|------------|
| `audit_missing` | 完了報告から15分後も家康レポートなし | 30分 |
| `audit_incomplete` | gunshi_report に codex/gemini フィールド欠落 | 30分 |
| `audit_invalid_diff` | `verified_by_reading != true_via_diff` | 即時、再発しない |
| `pdca_stalled` | 同一タスクで30分進展なし | 30分 |
| `pdca_extended` | cycle3 超過 | 1時間 |
| `pdca_escalation_required` | cycle5 超過 | 即時、family_alert |

実装は `hakudokai_activity_monitor.sh` に既存。新アラート追加は別タスクで。

---

## 12. 監査ダッシュボード可視化

`/tmp/hakudokai_activity_dashboard.json` の `audit_compliance` セクションに以下を集約：

```json
{
  "audit_compliance": {
    "ashigaru1": {
      "task_id": "subtask_xxx",
      "status": "cycle3_in_progress|final_pass|escalated",
      "current_cycle": 3,
      "max_cycles": 5,
      "last_audit_at": "<ISO8601>",
      "auditors": {
        "gunshi": "pass",
        "codex": "pending",
        "gemini": "pass"
      },
      "scope_validated": true,
      "alerts": ["pdca_extended"]
    }
  }
}
```

家老ダッシュボード（dashboard.md）には**サマリのみ**表示。詳細はYAML参照。

---

## 13. 例外・特殊ケース

### 13.1 ホットフィックス（緊急修正）

通常監査フローを省略可能だが、**事後監査必須**：
- マージ即時許可（速度優先）
- 24時間以内に三者監査実施・記録
- 監査結果が FAIL の場合、緊急 revert または follow-up commit

### 13.2 リファクタリング（機能変更なし）

- Codex Axis 4（テスト）のテスト変更不要を許容
- Gemini 仕様準拠は「仕様変更なし」で PASS

### 13.3 ドキュメントのみの変更

- Codex Axis 1-4 はスキップ可
- Codex Axis 5（重複）と Axis 6（Git）は必須
- Gemini ドキュメント整合のみ

### 13.4 自動生成コード（package-lock.json 等）

監査対象外。`changed_paths` から除外。

### 13.5 第三者OSSプルリクエスト受領

CLAUDE.md §OSS Pull Request Review に従う（既定済）。

---

## 14. 監査者の独立性保証

### 14.1 自作自演禁止の機械的保証

- コミット author と監査者が同一エージェントの場合、エラーで監査拒否
- ただし家康は自身が手を出さない限り監査者として有効
- 家康が小修正を加えた場合（コメント追加等）、その修正を別足軽がレビュー

### 14.2 監査者ローテーション（将来検討）

- Codex モデル切替（GPT-4 → Claude → 他）
- Gemini モデル切替（Pro → Ultra）
- 同一 cycle での結果比較で精度向上を測定

---

## 15. 実装済みスクリプト（2026-05-05）

### 15.1 `scripts/audit_codex.sh`

家康がCodex(デコポン)に6軸監査を依頼する標準実装。

```bash
bash scripts/audit_codex.sh <task_id> <cycle> <base_commit> <head_commit> [<repo_path>]
```

**特徴**:
- diff抽出に exclude pattern 適用（node_modules, .venv, lock等を自動除外）
- 標準プロンプト（6軸固定、JSON出力強制）
- usage limit 検知 → exit 3 で fallback 信号
- 3回リトライ
- 出力: `/tmp/codex_audit_<task_id>_cycle<N>.json`

### 15.2 `scripts/audit_gemini.sh`

家康がGeminiに仕様準拠+法令監査を依頼する標準実装。

```bash
bash scripts/audit_gemini.sh <task_id> <cycle> <base_commit> <head_commit> [<repo_path>] [<spec_file>]
```

**特徴**:
- diff抽出 + PII自動検知（patient/kanja/name/consent/doui/medical/karte等のキーワード）
- 設計書(`context/<project>.md`先頭300行)を仕様準拠の判断材料として埋込
- Markdown fence 内JSONを抽出する parser 内蔵
- 出力: `/tmp/gemini_audit_<task_id>_cycle<N>.json`

### 15.3 `scripts/audit_verify.sh`

家老が家康の監査結果をメタ監査する標準実装。

```bash
bash scripts/audit_verify.sh <gunshi_report_path>
```

**10項目の機械チェック**:

1. 必須トップレベルフィールド (task_id, ashigaru_task_id, cycle, audit, qa_decision)
2. audit.scope の base_commit, head_commit, changed_paths 存在
3. commit hash の正規表現検証 (7-40 hex)
4. audit.gunshi.verdict の妥当性 (pass|fail)
5. audit.codex.verdict 存在
6. **audit.codex.verified_by_reading == "true_via_diff"** （フル走査検知）
7. Codex 6軸 (axis1〜axis6) 全存在
8. audit.gemini.verdict + verified_by_reading
9. Gemini 5観点 (spec_compliance, completeness, legal_compliance, documentation, ux) 全存在
10. PII該当時の legal_compliance 検証
11. cycle 1〜5 範囲、3超過は警告
12. qa_decision=pass の時、三者全PASS整合性

**家老の使い方**:
- `cmd完了処理時` に必ず実行
- exit 0 → cmd を done にしてよし
- exit 1 → 監査結果無効、家康に再監査指令
- exit 2 → スクリプト引数エラー

### 15.4 家康の標準フロー（厳守）

```bash
# 1. 家康レビュー（手作業、§3チェックリスト）
# 2. Codex監査
bash scripts/audit_codex.sh "$TASK_ID" "$CYCLE" "$BASE" "$HEAD" "$REPO"
CODEX_VERDICT=$?

# 3. Gemini監査
bash scripts/audit_gemini.sh "$TASK_ID" "$CYCLE" "$BASE" "$HEAD" "$REPO"
GEMINI_VERDICT=$?

# 4. gunshi_report.yaml に三者結果を集約記録（§9 schema）
# 5. 家老に inbox_write で qa_decision 報告
```

### 15.5 家老の標準フロー（厳守）

```bash
# 1. 家康から完了通知受領
# 2. メタ監査
bash scripts/audit_verify.sh queue/reports/gunshi_report.yaml
META_VERDICT=$?

# 3. exit 0 なら cmd を完了化
# 4. exit 1 なら家康に「再監査せよ。理由: <stdout>」と差戻
```

---

## 16. テスト方法（運用前検証）

新スクリプトの動作確認手順：

### 16.1 audit_codex.sh ドライラン

```bash
# 適当な小さい diff で試験
cd /mnt/c/Users/User/Documents/DentalBI
RECENT=$(git log --oneline -3 --pretty=%H | tail -1)
HEAD=$(git rev-parse HEAD)
bash /mnt/c/Users/User/projects/multi-agent-shogun/scripts/audit_codex.sh \
  test_task 1 "$RECENT" "$HEAD" "$(pwd)"
cat /tmp/codex_audit_test_task_cycle1.json | python3 -m json.tool
```

### 16.2 audit_gemini.sh ドライラン

```bash
bash /mnt/c/Users/User/projects/multi-agent-shogun/scripts/audit_gemini.sh \
  test_task 1 "$RECENT" "$HEAD" "$(pwd)"
cat /tmp/gemini_audit_test_task_cycle1.json | python3 -m json.tool
```

### 16.3 audit_verify.sh ドライラン

```bash
# 既存の gunshi_report.yaml で試験
bash /mnt/c/Users/User/projects/multi-agent-shogun/scripts/audit_verify.sh \
  /mnt/c/Users/User/projects/multi-agent-shogun/queue/reports/gunshi_report.yaml
echo "exit: $?"
# 期待: exit 1 (旧フォーマットのため必須フィールドが足りない)
```

### 16.4 三者監査エンドツーエンド試験

進行中の `cmd_sync_reverse_001` の三者監査を新スクリプトで実施し、`audit_verify.sh` でPASSを確認することが最初の実機試験。

---

## 17. 改訂履歴

| 日付 | 改訂者 | 内容 |
|------|--------|------|
| 2026-05-05 13:50 | 信長 | 初版作成（理事長指示「緻密に・抜け漏れなく」） |
| 2026-05-05 14:13 | 信長 | §15-16追加: 実装済みスクリプト3本（audit_codex.sh / audit_gemini.sh / audit_verify.sh）、ドライラン手順 |

信長以外による改訂は禁止。改訂提案は inbox_write で信長へ。

---

## 関連ドキュメント

- [CLAUDE.md §Third-Party Audit Rule](../CLAUDE.md#third-party-audit-rule-all-agents--理事長直接指示) — 概要・原則
- [CLAUDE.md §Anti-Duplication Rule](../CLAUDE.md#anti-duplication-rule-all-agents--理事長直接指示) — 重複検知（Axis 5）
- [CLAUDE.md §Root Cause 4 Patterns](../CLAUDE.md#root-cause-4-patterns-all-agents--理事長直接指示) — 家康§3.3
- [instructions/gunshi.md](../instructions/gunshi.md) — 家康の役割定義
- [docs/restart-and-mcp.md](./restart-and-mcp.md) — 再起動・MCP接続
- [shim/hakudokai/hakudokai_activity_monitor.sh](../shim/hakudokai/hakudokai_activity_monitor.sh) — 忍び実装
