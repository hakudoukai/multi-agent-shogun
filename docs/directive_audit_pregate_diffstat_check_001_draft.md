# Directive 改訂草案 — `directive_audit_pregate_diffstat_check_001`

**Status**: DRAFT (= 信長承認後 CLAUDE.md / instructions/karo.md 反映予定)
**Draft author**: ashigaru2 (= 2026-05-07 誤検出事例の当事者 + 反論で正解導いた者)
**Parent cmd**: `cmd_pregate_directive_revision_001`
**Subtask**: `subtask_pregate_directive_draft_001`
**Base commit**: `0edef77` (= Phase 3 final + §18 polish close 直後)
**Drafted at**: 2026-05-07 22:50 JST
**改訂対象**: 既存 `directive_audit_pregate_diffstat_check_001` (= CLAUDE.md / instructions/karo.md 内、現状未明文化、本草案で初出案)
**Out of scope**: CLAUDE.md / instructions/karo.md 直接編集 (= 理事長専権)、実装 (= script / hook / 自動化、別 cmd 待ち)、法令最終総合監査 (= 全機能完成後別 cmd)

---

## §1. 背景・教訓

### §1.1 本 directive を新設する動機

2026-05-07 (= `subtask_section18_full_quality_polish_001` cycle1 + `subtask_ekarte_phase6_integration_test_001` cycle1 並行進行時) に、家康事前ゲート (= ashigaru 申告 vs `git diff --shortstat` 整合性確認) が **並行 commit 混在で誤検出** する制約が判明した。

具体:
- ashigaru2 が `subtask_section18_full_quality_polish_001` で test 領域 6 commit (= `7bc148f` / `01a4370` / `868b860` / `dcdaa35` / `0052ee9` / `0edef77`) を完遂
- 同時に信長 (shogun) が独立並行で 6 commit (= `c571d7d` / `9be172d` / `5460f8a` / `7fecf72` / `e59066e` / `83d50ca`) を実行 (= §19 lessons capture + agent observability infra + FKI mandate + §18 整合 fix)
- ashigaru2 申告「test 領域 only / production code 不変」は **拙者 6 commit の範囲では事実**
- しかし家老が `git diff --shortstat 579da38..HEAD` で **累積 diff** を見ると 16 files / 2785+/1144- (= 信長並行作業混入) で「申告矛盾」「scope creep」と誤判定
- 家康にも誤誘導された可能性あり (= cycle1 FAIL 三者監査結果 = Codex 5 high)
- ashigaru2 の反論報告 (= `msg_20260507_223628`) で家老が誤帰属を認識、撤回 + path フィルタ限定再監査で全 PASS、close 確定

### §1.2 教訓 3 点 (= 本 directive で必ず反映)

1. **`base..HEAD` 累積 diff だけでは並行 commit 混在時に誤検出する**
   - 同 repo に複数 author (= 信長 + 各 ashigaru) が並行 commit すると、本人の作業ではない commit が累積 diff に含まれ、申告と乖離する
   - 並行作業は本システムの既定運用 (= 信長/家老/ashigaru1/ashigaru2 が同時稼働) ゆえ、累積 diff 単独評価は構造的に破綻する

2. **author + path フィルタ併用必須、ただし author だけでは不十分**
   - 本リポジトリは全 commit author が `hakudoukai` 共通 (= git config 統一) で区別不能の場合あり (= 2026-05-07 事例で実証済)
   - timestamp + path で判別する必要あり
   - 家康事前ゲートは `git log --pretty=format:'%h|%ai|%s' base..HEAD -- <path>` で本人作業のみを抽出、それと申告の整合性を確認

3. **申告 path 明示 (= 拙者作業 path) で誤検出防止**
   - ashigaru 申告は `base..HEAD` 累積 diff ではなく、**拙者作業 path を明示** する
   - 例: 申告「`tests/test_section18_migration.py` + `tests/test_section18_roles.bats` のみ touch」
   - これで家康事前ゲートが path フィルタで本人作業のみを抽出、誤検出回避
   - 申告 path 明示は ashigaru 自身の責務 (= 自分が触った path は自分が一番知っている)

---

## §2. 全足軽の義務 (= ashigaru / gunshi report 提出時)

### §2.1 完了報告で必ず明示する 4 項目

1. **base_commit / head_commit (= hash)**
2. **拙者作業 path (= 明示、glob 可)**
3. **`git diff --shortstat <base>..<head> -- <拙者 path>` の出力結果** (= path フィルタ適用済の差分)
4. **テスト結果 (= pytest / vitest / bats 件数、PASS/FAIL/SKIP 内訳)**

### §2.2 義務違反時の扱い

- (1)-(4) のいずれかを欠く完了報告は **家老が即時差戻し** (= `task_assigned` で再依頼)
- 累積 diff 単独申告 (= path 明示なし) も差戻し対象
- 将来的に PreToolUse hook (= `bulk_ack` 同様の自動チェック、別 cmd) で commit 時に自動警告予定 (= 提案のみ、本草案では実装なし)

### §2.3 ashigaru の自己検証責務

- 完了報告送信前に `git log --author=$(git config user.email) base..HEAD -- <拙者 path>` で本人 commit のみを抽出し申告と一致するか確認
- 著者統一リポジトリ (= 本 multi-agent-shogun 等) では `--since=<task 着手 timestamp>` を併用
- 不整合検知時は **報告送信せず家老に状況確認** (= 並行 commit 混在の可能性、事前申告で誤検出回避)

---

## §3. 家康事前ゲート手順 (= path フィルタ併用版)

### §3.1 事前ゲートの目的

三者監査 (= Codex / Gemini / 家康) 着手前に、**ashigaru 申告 scope と git 実態の整合性**を機械的に確認する。整合確認後にのみ Codex / Gemini を起動 (= 不整合のまま監査着手すると無関係 commit を監査対象にして誤判定する)。

### §3.2 手順 (= 5 ステップ)

```
1. ashigaru 申告 path を抽出 (= 申告フォーマット §6 の「拙者作業 path」を parse)
2. git log --pretty=format:'%h|%an|%ai|%s' <base>..<head> -- <申告 path> を実行
3. 結果の commit 範囲が申告 commit 範囲と一致するか確認
   - 一致 → step 4 へ
   - 不一致 → 差戻し or path フィルタ scope 限定再評価の選択を家老に裁可仰ぐ
4. git diff --shortstat <base>..<head> -- <申告 path> を実行し、申告 shortstat と数値整合確認
   - 一致 → step 5 へ
   - 不一致 → 差戻し
5. 整合性確認 PASS → Codex / Gemini 三者監査着手
   - audit_codex.sh / audit_gemini.sh 呼出時に --paths "<申告 path>" を必ず指定
   - 監査対象も path フィルタ適用 (= スコープ純化、誤判定防止)
```

### §3.3 author フィルタ補助 (= 異著者 repo の場合)

multi-agent-shogun は author 統一 (= 全 commit `hakudoukai`) ゆえ author フィルタ単独では不十分だが、他リポジトリ (= DentalBI 等で異著者運用なら) では `--author=<ashigaru email>` を path フィルタと併用すると更に確実:

```
git log --pretty=format:'%h|%an|%ai|%s' --author='<ashigaru email>' <base>..<head> -- <申告 path>
```

ただし path フィルタが第一義 (= author フィルタは補助)、author フィルタ単独運用は禁止 (= 著者統一リポジトリで効かない)。

### §3.4 timestamp フィルタ補助 (= 並行 commit 増加時)

並行 commit が爆発的に多い (= 5 ashigaru + 信長 + 家老 + 家康 が同時 commit) 場合は `--since=<task 着手 timestamp>` を併用:

```
git log --pretty=format:'%h|%an|%ai|%s' --since='2026-05-07 22:14:50' <base>..<head> -- <申告 path>
```

timestamp は ashigaru 申告に含めること (= §6 申告フォーマットに「task 着手時刻」を追加)。

---

## §4. 家老の検証責務

### §4.1 ashigaru 申告と家康事前ゲート結果の照合

ashigaru 完了報告受領時、家老は以下を機械的に確認:

1. **申告フォーマット 4 項目** (= §2.1) の完備性確認
2. **家康事前ゲート結果** (= §3.2 step 5 PASS) の確認
3. **path フィルタ後 shortstat と申告 shortstat の数値一致確認**
4. **base_commit が前 cmd の close 時 head_commit と接続するか確認** (= cmd 間の commit chain 連続性)

### §4.2 不整合検知時の家老対応

| 不整合パターン | 家老対応 |
|---|---|
| 申告 path に明示なし | 差戻し (= 申告フォーマット再提出依頼) |
| `base..HEAD` 累積 diff 申告 (= path フィルタなし) | 差戻し + path 明示再申告依頼 |
| 申告 path フィルタ後の shortstat と実 shortstat が乖離 | ashigaru へ照会 (= 並行 commit 混入か申告誤りかを切り分け) |
| 並行 commit 混入確定 | 家康再監査を path フィルタ限定で再実行依頼 (= 本タスクは継続、誤判断回避) |
| ashigaru 作業外の path に変更検出 | scope creep 認定、別 cmd 化 or revert 判断を理事長に裁可仰ぐ |

### §4.3 家老自身の誤判断回避

2026-05-07 事例で家老が `base..HEAD` 累積 diff で「申告矛盾 / scope creep」と誤判定し ashigaru2 に reverter 指示を出した教訓 (= `msg_20260507_223221`) を踏まえ:

- **ashigaru の反論を尊重する** (= 反論内容に根拠 (= commit hash + path) があれば即時精査)
- **revert 指示を出す前に必ず path フィルタで再確認** (= revert は不可逆、誤指示は信長並行作業を打ち消すリスク)
- 誤判断が確定した場合は **公式陳謝 + 撤回** (= `msg_20260507_223750` のような明示撤回)
- 教訓を本 directive に記録し恒久対策化

---

## §5. 違反検知時の対応

### §5.1 違反パターンと対応

| パターン | 対応 |
|---|---|
| **P1**: 申告 path 明示なし | 差戻し (= 即時、再提出待ち、新規 cycle 計上なし) |
| **P2**: 申告 shortstat と実 shortstat が乖離 (= scope 越境疑い) | 家康事前ゲート再実行 + ashigaru 説明請求 |
| **P3**: scope 越境確定 (= ashigaru 自身の作業で本タスク外 path を touch) | 当該 commit を別 cmd 化 (= 別 task_id 採番、scope 純化) or revert 判断、理事長裁可 |
| **P4**: 並行 commit 混入 (= 他 author の正当作業) | path フィルタ限定再監査 (= 本タスク scope は変えず、純粋 path のみ評価) |
| **P5**: 家老誤判断 (= 累積 diff 単独評価で誤指示) | 公式撤回 + 教訓記録 + 本 directive 適用継続 |

### §5.2 教訓記録の責務分担

- **家老**: 誤判断履歴を `docs/incident_logs/` に記録 (= `2026-05-07_pregate_misjudge.md` 等、別 cmd で発令)
- **家康**: 事前ゲート誤検出パターンを `queue/reports/gunshi_report.yaml` に記録
- **ashigaru**: 申告フォーマット遵守状況を完了報告に自己記録 (= 「申告 path 明示済」「shortstat 添付済」のチェックボックス)
- **信長**: 重大教訓を CLAUDE.md / instructions/karo.md に追記 (= 理事長承認後)

### §5.3 ERR-PREGATE-* エラーコード採番案 (= 提案のみ、別 cmd 実装)

| エラーコード | 発生条件 | 重要度 |
|---|---|---|
| `ERR-PREGATE-001` | 申告 path 明示なし | WARN |
| `ERR-PREGATE-002` | 申告 shortstat と実 shortstat 乖離 (= 1 行以上差) | ERROR |
| `ERR-PREGATE-003` | scope 越境確定 (= ashigaru 作業で本タスク外 path 検出) | ERROR |
| `ERR-PREGATE-004` | 並行 commit 混入 (= 他 author commit が累積 diff に含まれる) | INFO (= 自動 path フィルタで吸収) |
| `ERR-PREGATE-005` | 家老誤判断 (= 撤回履歴あり) | WARN (= 月次レビュー対象) |

採番台帳 `docs/error_codes.md` への追記は別 cmd `cmd_pregate_error_codes_001` で実施 (= 本草案では提案のみ)。

---

## §6. ashigaru 申告フォーマット (= 草案)

### §6.1 標準形式 (= 全 ashigaru 完了報告で必須)

```
完了報告:
- task_id: <ID, e.g. subtask_section18_full_quality_polish_001>
- parent_cmd: <cmd_id>
- base_commit: <hash, e.g. 579da38>
- head_commit: <hash, e.g. 0edef77>
- task 着手時刻: <ISO8601 JST, e.g. 2026-05-07T22:08:50+09:00>
- 拙者作業 path (= 明示):
  - tests/test_section18_migration.py
  - tests/test_section18_roles.bats
- git diff --shortstat <base>..<head> -- <拙者 path> 出力:
  ```
  2 files changed, 813 insertions(+), 83 deletions(-)
  ```
- git log --pretty=format:'%h|%ai|%s' <base>..<head> -- <拙者 path> 出力:
  ```
  0edef77|2026-05-07 22:24:52 +0900|test(section18): T1 polish — bats 実関数テスト追加
  dcdaa35|2026-05-07 22:23:00 +0900|test(section18): D1 polish — Python↔Shell SoT mirror drift 検知強化
  868b860|2026-05-07 22:21:46 +0900|test(section18): T1 polish — pane_id assertion 実行時 tmux スタブテスト追加
  01a4370|2026-05-07 22:19:05 +0900|test(section18): B2 polish — argv 経由読込の adversarial 注入耐性テスト追加
  7bc148f|2026-05-07 22:17:10 +0900|test(section18): B1 polish — pane_id regex / agent_id parity 境界値テスト追加
  0052ee9|2026-05-07 22:14:50 +0900|refactor(test_section18): D1 polish — settings/bash helper を module-level に集約
  ```
- pytest / vitest / bats 結果:
  - pytest: 89 PASS / 0 FAIL / 0 SKIP
  - bats: 19 PASS / 0 FAIL
- 三者監査依頼: 家康 (= path フィルタ限定で再評価願う)
- 自己検証チェックボックス:
  - [x] 申告 path 明示済
  - [x] shortstat 添付済 (= path フィルタ適用済)
  - [x] git log 添付済
  - [x] 並行 commit 混入の可能性確認済 (= base..HEAD 累積 diff 結果と path フィルタ結果の差を自己点検済)
```

### §6.2 簡易形式 (= cycle 内 fix 報告等)

cycle 内の小規模 fix (= 1 commit 程度、scope 同一) は簡易形式で可:

```
完了報告 (cycle{N} fix):
- task_id: <ID>
- 前 cycle head: <hash>
- 今 cycle head: <hash>
- 追加 path: <list>
- shortstat: <出力>
- 修正対象 finding: <gunshi finding ID, e.g. B1 / S1>
```

---

## §7. 家康事前ゲート手順 (= 草案、コマンド付き)

### §7.1 標準手順 (= bash one-liner)

```bash
# Step 1: ashigaru 申告 path と base/head を変数に格納
ASHIGARU_PATHS="tests/test_section18_migration.py tests/test_section18_roles.bats"
BASE="579da38"
HEAD="0edef77"

# Step 2: path フィルタで本人 commit のみ抽出
git log --pretty=format:'%h|%ai|%s' "$BASE..$HEAD" -- $ASHIGARU_PATHS

# Step 3: path フィルタで shortstat 確認
git diff --shortstat "$BASE..$HEAD" -- $ASHIGARU_PATHS

# Step 4: 申告との数値一致確認 (= 家康目視 or 自動 diff)
# Step 5: 整合 PASS → Codex / Gemini 三者監査着手 (--paths 指定必須)
bash scripts/audit_codex.sh --base "$BASE" --head "$HEAD" --paths "$ASHIGARU_PATHS"
bash scripts/audit_gemini.sh --base "$BASE" --head "$HEAD" --paths "$ASHIGARU_PATHS"
```

### §7.2 不整合検知時の決定木

```
申告 path フィルタ後の commit 数 == 申告 commit 数 ?
├─ Yes → shortstat 一致 ?
│        ├─ Yes → PASS、三者監査着手
│        └─ No  → ashigaru へ照会 (= 並行 commit 混入か申告誤りか)
└─ No  → 並行 commit 混入の可能性
         → git log <base>..<head> -- <他 path> で他 author 作業を確認
         → 本タスク scope は path フィルタで純化、別 author 作業は別 cmd 化
         → path フィルタ限定で再監査 (= 本タスク継続)
```

### §7.3 家康事前ゲートのレポート形式

```yaml
gunshi_pregate_check:
  task_id: <ID>
  base_commit: <hash>
  head_commit: <hash>
  ashigaru_paths:
    - <path1>
    - <path2>
  pregate_result: PASS | FAIL_path_mismatch | FAIL_shortstat_mismatch | PARALLEL_COMMITS_DETECTED
  parallel_commits_excluded:  # PARALLEL_COMMITS_DETECTED の場合のみ
    - hash: <h>
      author: <a>
      path: <p>
      reason: "他 author 並行作業、本タスク scope 外"
  audit_command:
    codex: "bash scripts/audit_codex.sh --base <b> --head <h> --paths '<p1> <p2>'"
    gemini: "bash scripts/audit_gemini.sh --base <b> --head <h> --paths '<p1> <p2>'"
```

---

## §8. 運用フロー図

### §8.1 通常フロー (= 整合性 PASS)

```
[ashigaru 完了 (= 申告 path 明示 + shortstat 添付)]
        │
        ▼
[家康事前ゲート (§3.2 step 1-4)]
        │
        ▼
   path フィルタ後の commit / shortstat 整合確認
        │
        ▼ PASS
[Codex / Gemini 三者監査 (= --paths 指定で scope 純化)]
        │
        ▼ 全員 PASS
[家老最終裁可 (§4.1 4 項目確認)]
        │
        ▼ PASS
[task close]
```

### §8.2 不整合フロー (= 並行 commit 混入)

```
[ashigaru 完了 (= 申告 path 明示)]
        │
        ▼
[家康事前ゲート]
        │
        ▼
   path フィルタ後の commit 数 != 累積 commit 数 ?
        │
        ▼ Yes (= 並行 commit 混入)
[他 author commit を path フィルタ外で確認]
        │
        ▼
[本タスク scope = path フィルタ純化、別 author 作業は別 cmd 化]
        │
        ▼
[Codex / Gemini 三者監査 (= --paths 指定で scope 限定)]
        │
        ▼ PASS
[家老最終裁可]
        │
        ▼
[task close (= 並行 commit は影響なし、純粋 ashigaru scope のみ評価)]
```

### §8.3 違反フロー (= scope 越境確定)

```
[ashigaru 完了 (= 申告 path 明示)]
        │
        ▼
[家康事前ゲート]
        │
        ▼
   ashigaru 作業で本タスク外 path 検出
        │
        ▼ Yes
[家老 scope 判断]
        │
        ├─ (A) 別 cmd 化採用 (= scope 越境部分を別 task_id 化、本タスク純化)
        ├─ (B) 当該 cycle 拡張 (= 理事長裁可、scope 拡大確定)
        └─ (C) revert 指示 (= 不可逆ゆえ慎重、必ず path フィルタで再確認)
                │
                ▼ revert 確定後
            [ashigaru 再 commit (= 純化済 scope)]
                │
                ▼
            [家康事前ゲート再実行 → PASS → 三者監査]
```

---

## 付録 A: 本日事例の記録 (= 2026-05-07)

### A.1 `subtask_section18_full_quality_polish_001` cycle1

**ashigaru2 担当、test 領域 6 commit、§18 完遂後の品質磨き上げ**

| commit | timestamp (JST) | 種類 | path |
|---|---|---|---|
| `7bc148f` | 22:17:10 | test | `tests/test_section18_migration.py` |
| `01a4370` | 22:19:05 | test | `tests/test_section18_migration.py` |
| `868b860` | 22:21:46 | test | `tests/test_section18_migration.py` |
| `dcdaa35` | 22:23:00 | test | `tests/test_section18_migration.py` |
| `0052ee9` | 22:14:50 | refactor (test) | `tests/test_section18_migration.py` |
| `0edef77` | 22:24:52 | test | `tests/test_section18_roles.bats` (新規) |

**並行信長 (shogun) 作業 6 commit (= production / infra / mandate)**

| commit | timestamp (JST) | 種類 | path |
|---|---|---|---|
| `c571d7d` | 21:03:55 | feat (observability) | `scripts/agent_health_check.sh` 等 |
| `9be172d` | 21:10:03 | feat (observability) | `scripts/agent_periodic_push.sh` 等 |
| `5460f8a` | 21:25:10 | feat (karo) | `instructions/karo.md` 等 |
| `7fecf72` | 22:08:50 | fix (integrity) | CLAUDE.md §18 整合 fix |
| `e59066e` | 22:16:45 | feat (observability) | §19 + 第1号 skill |
| `83d50ca` | 22:24:14 | feat (integrity) | §19 SecondPC mandate |

**誤検出経過**:
1. ashigaru2 申告: 「test 領域 only / production code 不変」(= 拙者 6 commit 範囲では事実)
2. 家老 cycle1 三者監査依頼時、`base..HEAD` 累積 diff = 16 files / 2785+/1144- (= 信長並行作業混入)
3. Codex 5 high finding (= pane topology 内部矛盾、scope creep) を生成 (= 信長 production 作業を ashigaru2 scope と誤帰属)
4. 家老 cycle2 fix 厳格指示 (= `msg_20260507_223221` / `msg_20260507_223259` revert 命令)
5. ashigaru2 反論報告 (= `msg_20260507_223628`) で「test 領域 only は事実、並行 commit は他 author」根拠提示
6. 家老精査 → 撤回 (= `msg_20260507_223750`) + path フィルタ限定再監査
7. 家康再監査: path フィルタ後 self-audit 8 観点全 PASS (= ashigaru2 6 commit pure test 領域、813+/83-)
8. 家老最終裁可: close 確定 (= `msg_20260507_224148`)

**教訓**: 累積 diff 単独評価は構造的に破綻する。path フィルタ + 申告 path 明示が必須。

### A.2 `subtask_ekarte_phase6_integration_test_001` cycle1

**ashigaru1 担当、frontend ekarte-v6 領域、Phase 6 統合テスト本実装**

並行進行で同様の誤検出パターンが発生 (= cross-task backend ashigaru2 polish 由来 + scope 内 `docs/observability_coverage.md` ashigaru1 自作業の判別困難)。家老 path フィルタで scope 限定再監査の方針確定。

詳細は別 cmd の incident log で記録予定 (= `docs/incident_logs/2026-05-07_phase6_cycle1_pregate_path_filter.md` 案、家老責務)。

---

## 付録 B: ERR-PREGATE-* 採番案 (= 提案のみ)

§5.3 で示した 5 件のエラーコードを `docs/error_codes.md` に追記する別 cmd (= `cmd_pregate_error_codes_001`) を将来発令予定。本草案では提案のみ。

---

## 付録 C: 関連 directive との整合性

| 関連 directive | 関係 |
|---|---|
| `directive_no_concurrent_stage_001` (= 既存、CLAUDE.md 内未明文化) | 本 directive と協調 (= stage race 防止と pregate 整合性確認は補完関係) |
| `directive_commit_granularity_001` (= 既存、6 commit 分離模範) | 本 directive と協調 (= commit 分離が path フィルタを容易化) |
| `directive_audit_pregate_diffstat_check_001` (= 本 directive、現状未明文化) | 本草案で初出案 |
| §19 Post-Incident Lessons Capture (= CLAUDE.md 既出) | 本 directive 違反検知時の lessons skill 生成 trigger に組込 (= 別 cmd) |

---

## 付録 D: 改訂理由ブロック

| 草案 version | 改訂理由 | 反映元 |
|---|---|---|
| draft-001 | 初版作成 (= 2026-05-07 並行 commit 誤検出事例の恒久対策草案) | `subtask_pregate_directive_draft_001` task YAML + 本日事例 (`msg_20260507_224148` close 確定) |

---

## 草案完成基準 (= self-check)

- [x] §1-§5 + 申告フォーマット + 家康事前ゲート手順 + 運用フロー + 本日事例記録の 5 章立て + 4 付録
- [x] 実装着手なし (= markdown 1 ファイルのみ)
- [x] CLAUDE.md / instructions/karo.md 直接編集なし
- [x] Anti-Duplication 厳守 (= 既存 docs/runbooks/* / docs/incident_logs/* と非重複、初出案ゆえ重複対象なし)
- [x] §directive_no_concurrent_stage_001 + §directive_commit_granularity_001 との整合性確保
- [x] 本草案自身が申告フォーマットを実践する model task (= 完了報告で path 明示 + shortstat 添付)

信長承認後、本草案を base に CLAUDE.md / instructions/karo.md 改訂を理事長殿御判断で実施されたし。
