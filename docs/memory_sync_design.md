# Memory Sync Design — SC/MC 間 shared memory 同期

起案: ashigaru4 (大久保 忠世) / 2026-05-11
根拠: `docs/final_solution_synthesis_20260511.md` P1-1
承認待: Shogun (信長)

---

## Problem: 何が同期されていないか / 過去に起きた不整合事例

### 現状の構成

```
SC (SecondPC) memory/
  MEMORY.md                          — index (SC-specific パス参照含む)
  MEMORY_FROM_MAINPC_NOBUNAGA.md     — MC raw dump (39KB、最終コピー日時不明)
  principle_*.md                     — universal principle files (14 files)
  rule_*.md                          — universal rule files
  cross_pc_communication_path.md     — cross-PC 規範
  persona_ieyasu.md                  — SC 固有 persona
  project_tokugawa_force.md          — project info (PII/secret リスク有)
  reference_supabase_tokugawa.md     — Supabase doc ID (機密)
  user_majesty_and_nobunaga.md       — 実ユーザー情報 (PII)
```

SC と MC はそれぞれ独立した memory/ を持ち、現状の同期は以下の問題を抱える:

### 過去の不整合事例

| 日付 | 不整合内容 | 影響 |
|------|-----------|------|
| 2026-05-11 | `partial` verdict 廃止が MC で決定されたが SC に未伝達 | SC エージェントが `partial` を有効 verdict として使用し続けた |
| 2026-05-11 | shogun P002 privilege (infra daemon kill) が MC memory に記録されたが SC に未反映 | SC shogun が infra kill 権限を保持していないと誤認した期間が発生 |
| 2026-05-11 | `rule_verdict_vocabulary.md` が SC 側で後追い作成 (MC → SC 伝達遅延) | Rule 有効化タイミングがずれ、SC 側報告が旧語彙を使用 |
| 随時 | `MEMORY_FROM_MAINPC_NOBUNAGA.md` が raw dump (39KB) として手動コピー — コピー日時不明 | どの version が正本か不明確、追跡不能 |

### 根本問題

- **shared memory block の定義がない**: どのファイルが cross-PC 共有対象か明示されていない
- **sync トリガーが存在しない**: rule 更新時に対側 PC へ届ける仕組みがない
- **secret/PII scan ゼロ**: cross-PC 送出前にスキャンしない
- **raw MEMORY.md sync**: index ファイルはパスが PC 固有、そのまま送ると参照破綻

---

## Design Constraints

P1-1 規定および陛下哲学 (2026-05-11):

| 制約 | 詳細 |
|------|------|
| **shared memory blocks のみ同期** | raw `MEMORY.md` 丸ごと sync は禁止。`shared: true` タグ付きブロックのみ対象 |
| **secret/PII scan 必須** | outbound sync (push) 前に scan 実行。fail なら sync 中止・karo に報告 |
| **event-triggered push/pull のみ** | polling daemon 禁止。cron / inotifywait 常駐プロセス禁止 |
| **background worker は value-and-side-effects gate 通過後のみ** | 価値 + 副作用が明確に answer できた場合のみ採用可 |

陛下哲学 (追加):
- 仕組みで防ぐ (principle_system_over_human.md)
- daemon = always-on process = 見えない副作用 → 採用コストが価値を上回ると判断されない限り禁止

---

## Candidate Mechanisms

### a) git tracked + secrets check

**概要**: shared memory blocks を git 管理し、push/pull で MC/SC 間同期。
secrets は `gitleaks` / pattern scan で push 前検出。

| 項目 | 内容 |
|------|------|
| トリガー | agent が明示的に `memory_sync.sh push` を呼ぶ (task 完了報告ステップに組み込み可) |
| Pros | 差分・履歴・rollback が標準で得られる。既存 git インフラ再利用。daemon 不要。 |
| Cons | memory/ は現状 `.gitignore` 対象。共有 remote branch が必要。public repo はリスク。 |
| value | rule 変更の伝達漏れ防止、version 追跡 |
| side-effects | push 時に GitHub に記録が残る (private repo なら許容範囲内) |

### b) Supabase project_documents UPSERT

**概要**: shared blocks を Supabase `project_documents` テーブルに UPSERT。対側 PC が SELECT で pull。

| 項目 | 内容 |
|------|------|
| トリガー | agent が明示的に `memory_sync.sh push` / `pull` を呼ぶ |
| Pros | 既存 Supabase インフラ活用 (reference_supabase_tokugawa.md)。外部 git remote 不要。 |
| Cons | Supabase 依存 (network 断で動作不能)。schema 設計要。row-level secret scan が複雑。 |
| value | cloud 経由で MC/SC 両側から即アクセス可能 |
| side-effects | クラウドに memory 内容が保存される (PII リスク → scan 必須) |

### c) inotify watch + rsync trigger

**概要**: `inotifywait` で memory/ の変更を検知し、SSH rsync で対側 PC に即転送。

| 項目 | 内容 |
|------|------|
| トリガー | ファイル変更検知 (inotifywait 常駐) |
| Pros | 遅延最小。明示的な呼び出し不要。 |
| Cons | **inotifywait 常駐 = polling daemon と等価 → P1-1 制約違反**。silent fail リスク (SSH 断等)。 |
| value | 低 (event-triggered helper で代替可能) |
| side-effects | always-on process、観測困難、rollback 手順なし |

**判定: 却下** — P1-1「polling daemon 禁止」「event-triggered のみ」に反する。

### d) 専用 helper script (単体)

**概要**: `scripts/memory_sync.sh {push|pull|diff}` を手動または agent ステップで呼ぶ。
内部では SSH + rsync または git を呼び出すラッパー。

| 項目 | 内容 |
|------|------|
| トリガー | 人間 or agent が明示的に呼ぶ |
| Pros | 完全な制御。daemon ゼロ。scan を組み込みやすい。既存 SSH path 再利用。 |
| Cons | 呼び忘れリスク (task YAML に組み込まなければ漏れる)。転送先が git でない場合 version history なし。 |
| value | 実装コスト最小、P1-1 完全適合 |
| side-effects | 呼び出し責任が agent に移行 (task YAML で強制可能) |

---

## Recommendation

### 採択案: **a + d のハイブリッド** (git-backed helper script)

```
scripts/memory_sync.sh {push|pull|diff|scan}
```

#### 設計方針

1. **shared block タグ制**: 各 memory block frontmatter に `shared: true` を付与したファイルのみ同期対象。`shared: false` または未定義は同期対象外。
2. **secrets/PII scan ゲート**: `push` 実行時に scan を必ず通過。失敗で abort + karo inbox 報告。
3. **git private branch で管理**: `memory-shared` ブランチ (または専用 repo private) を MC/SC 共通 remote として使用。memory/ を gitignore から除外するのではなく、**shared ファイルのみを別パスに export** する方式 (`memory/shared/`) を採用し元の gitignore を維持。
4. **event trigger 組み込み**: task YAML の `steps` に `memory_sync.sh push` を任意追加可能なステップとして定義。Agent は rule 変更 task 完了時に呼ぶ。
5. **raw MEMORY.md は同期しない**: index は各 PC 独自。shared ブロックのみ同期し、各 PC が自 MEMORY.md に import エントリを追記する。

#### 実装手順草案

**Step 1 — shared block 分類 (Karo 確認後)**

対象ファイルに frontmatter `shared: true` を付与:
```
principle_system_over_human.md   shared: true
principle_naked_king.md          shared: true
principle_completion_verify.md   shared: true
principle_trust_honnoiji.md      shared: true
pdca_max7cycle_rule.md           shared: true
rule_10min_sla.md                shared: true
rule_verdict_vocabulary.md       shared: true
cross_pc_communication_path.md   shared: true
```

同期対象外 (local-only):
```
persona_ieyasu.md                shared: false  (SC固有 persona)
user_majesty_and_nobunaga.md     shared: false  (PII)
project_tokugawa_force.md        shared: false  (secrets/PII)
reference_supabase_tokugawa.md   shared: false  (Supabase IDs)
rule_gunshi_domain_sc.md         shared: false  (SC固有)
rule_gunshi_supervision_sc.md    shared: false  (SC固有)
MEMORY.md                        ← sync禁止 (index file)
MEMORY_FROM_MAINPC_NOBUNAGA.md   ← 廃止候補 (raw dump 方式廃止)
```

**Step 2 — scripts/memory_sync.sh 実装**

```bash
# コマンド仕様
memory_sync.sh scan          # secret/PII scan のみ実施 (push 前確認用)
memory_sync.sh push          # scan → shared blocks を remote に push
memory_sync.sh pull          # remote から shared blocks を取得 → memory/ に展開
memory_sync.sh diff          # push/pull で変更されるファイル一覧を表示
```

内部処理 (push):
1. `memory/` 内 `shared: true` ファイルを `memory/shared/` に export (コピー)
2. secrets scan: API key pattern, token pattern, IP/email の scan
3. scan NG → abort, karo inbox 報告
4. scan OK → `git -C memory/shared add . && git commit && git push origin memory-shared`
5. 完了ログを `queue/reports/memory_sync_log.yaml` に append

内部処理 (pull):
1. `git -C memory/shared pull origin memory-shared`
2. 差分ファイルを `memory/` に展開 (上書き)
3. `MEMORY.md` に未登録の shared block があれば import エントリ追記を karo に提案

**Step 3 — task YAML 標準ステップ追加**

rule 変更を含む task の `steps` に:
```yaml
  N: "memory_sync.sh push で shared blocks を対側 PC に同期"
```

**Step 4 — MEMORY_FROM_MAINPC_NOBUNAGA.md 廃止**

raw dump ファイルは shared block 方式に移行後、アーカイブして削除。
移行完了条件: shared blocks pull で MC の rule が SC に展開されていることを verify。

#### value-and-side-effects gate 評価

| 問い | 回答 |
|------|------|
| 防ぐ failure mode は? | rule 変更の cross-PC 伝達漏れ、不整合 verdict 使用 |
| trigger は event-based か? | はい (task 完了 or 明示的呼び出し) |
| max runtime / retry は? | git push = 通常 <10s、retry なし (fail → karo 報告) |
| audit trail は? | `queue/reports/memory_sync_log.yaml` に記録 |
| 停止方法は? | helper script を呼ばなければ動作しない (daemon ではない) |
| health signal は? | sync_log.yaml の最終 sync 日時 + result |

**判定: 採用** — 全 gate 項目に強い回答が得られた。

---

## 付記: 将来の Supabase 移行 (P2 検討)

現時点では git + SSH で十分。ただし以下条件が揃えば Supabase (案 b) への移行を評価:

- 3 台以上の PC に拡張される場合
- offline 同期が不要で常時クラウド接続が保証される場合
- `project_documents` テーブルが既に memory block に適した schema を持つ場合

その際も value-and-side-effects gate を通過してから実装する。
