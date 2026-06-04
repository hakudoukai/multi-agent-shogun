# Root Cause 4 Patterns (all agents) — 理事長直接指示

**過去の事故分析で判明した4つの根本原因パターン。コード変更時に必ず確認すること。**

出典: CLAUDE.md (元「Root Cause 4 Patterns」節) からの移設実体 (副院長令 7de922ec 裁定 X-1、副院長令で指定された正本 `context/teriha-zero-wait.md §8` 不在実証 = 2026-06-04 Commander 実機検証、本ファイルが新たな実体)。改訂責務は理事長殿の専権事項。

## 4 パターン

| # | パターン | 対策 |
|---|----------|------|
| 1 | 旧版と新版の併存 | 新版作成時に同一commitで旧版を_archive退避 |
| 2 | 設計大転換による旧版残存 | DD廃止時の物理削除+参照クリーンアップ徹底 |
| 3 | task_trackerと実態の乖離 | commit時のtask_tracker更新の機械化 |
| 4 | 同名・同責務の重複定義 | 着手前の重複チェック必須化 |

## 詳細・チェックリスト

> **★実体注意★**: 本節の元ソースが参照していた `context/teriha-zero-wait.md §8` は 2026-06-04 時点で third_pc + git ls-files (全 PC 共有 repo) 上に実体不在。詳細チェックリストが新たに必要な場合は本ファイルに直接追記すること (副院長令「phantom canon 放置禁」順守)。

### パターン 1: 旧版と新版の併存
- [ ] 新版 commit には ★同一 commit★ で旧版を `_archive/` または明示的に削除
- [ ] 旧版残存検知: `grep -r 'OLD_FUNC_NAME' --include='*.py' --include='*.ts'` で参照ゼロ確認

### パターン 2: 設計大転換による旧版残存
- [ ] DD 廃止/置換時は ★物理削除★ + 関連 import/参照のクリーンアップ
- [ ] task_tracker / dashboard に「廃止 commit hash」を記録
- [ ] 関連 project_documents (Supabase) を `is_current=false` に降格 (FKI-CANON-GUARDIAN-01 順守)

### パターン 3: task_tracker と実態の乖離
- [ ] commit message に対応 task_id を必ず明記
- [ ] commit 時に task_tracker / queue/tasks の status 更新を機械化 (hook 等)
- [ ] 「completed と書かれているが実体未完成」を家老/家康のメタ監査で検出

### パターン 4: 同名・同責務の重複定義
- [ ] 着手前 `find . -name '*similar_name*'` + `grep -r 'similar_function'` 実施
- [ ] [Anti-Duplication](../03-workflows/anti-duplication.md) チェックリストと連動運用
- [ ] 三者監査 (Codex/Gemini/家康) Axis 5 (duplication) で確認
