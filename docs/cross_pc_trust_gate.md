# Cross-PC Trust Gate Design

根拠: `docs/final_solution_synthesis_20260511.md` P2-2  
対象構成: MainPC (MC) / SecondPC (SC) 2台構成 (local, no mTLS required)  
起案: ashigaru5 (鳥居 元忠) — 2026-05-11

---

## Trust Requirements

Cross-PC レポート転送に必要な 4 つの gate 条件。**全条件を満たさない限り、MC 側の completion gate は `blocked` を維持する。**

| Gate ID | 条件 | 失敗時の evidence_state |
|---------|------|------------------------|
| G1 | report ファイル名に PC suffix が含まれていること | `cross_pc_missing` (naming violation) |
| G2 | transfer 前後で report の sha256 hash が一致すること | `cross_pc_missing` (hash mismatch) |
| G3 | outbound sync 前に PII / secret scan を完了していること | `cross_pc_missing` (scan not run) |
| G4 | 転送ごとに audit record が追記されていること | `cross_pc_missing` (no audit trail) |

**前提**: mTLS daemon / federation daemon は現在の 2-PC local 構成では不要。  
identity drift や report spoofing の証拠が出た場合は、P2-3 Background Worker Evaluation Gate を経由して再評価する。

---

## PC Suffix Naming Convention

### 命名規則

```
{agent_id}_{pc_suffix}_report{_optional_qualifier}.yaml
```

| フィールド | 値 | 例 |
|------------|----|----|
| `pc_suffix` (MainPC) | `mainpc` | `kuroda_mainpc_report.yaml` |
| `pc_suffix` (SecondPC) | `secondpc` | `naomasa_secondpc_report.yaml` |

### 正規表現パターン (検証用)

```bash
# SC report の命名検証
echo "$filename" | grep -qE '^[a-z_]+_secondpc_report.*\.yaml$'

# MC report の命名検証
echo "$filename" | grep -qE '^[a-z_]+_mainpc_report.*\.yaml$'
```

### 現行ファイル一覧 (known reports)

| ファイル | PC | 状態 |
|---------|-----|------|
| `queue/reports/kuroda_mainpc_report.yaml` | MC | 正規 |
| `queue/reports/takenaka_mainpc_report.yaml` | MC | 正規 |
| `queue/reports/naomasa_secondpc_report.yaml` | SC | 正規 |
| `queue/reports/acha_secondpc_report.yaml` | SC | 正規 |

**suffix なしのファイルは gate G1 違反。転送元 PC で rename してから再送すること。**

---

## Hash Verification

### 目的

転送途中のファイル破損・改ざんを検出する。sha256sum で before/after を比較する。

### 手順

**Step 1: SC 側 (送信前) — hash を記録する**

```bash
# SC 上で実行
sha256sum queue/reports/naomasa_secondpc_report.yaml > /tmp/naomasa_secondpc_report.sha256
cat /tmp/naomasa_secondpc_report.sha256
# 例: a3f1c2d4e5b6... queue/reports/naomasa_secondpc_report.yaml
```

**Step 2: 転送 (rsync / scp / 手動コピー)**

```bash
# rsync 例 (SC → MC)
rsync -av queue/reports/naomasa_secondpc_report.yaml \
  mainpc:/home/hakudokai/projects/multi-agent-shogun-newbuild/queue/reports/
```

**Step 3: MC 側 (受信後) — hash を検証する**

```bash
# MC 上で実行
sha256sum -c /tmp/naomasa_secondpc_report.sha256
# OK: naomasa_secondpc_report.yaml: OK
# NG: naomasa_secondpc_report.yaml: FAILED
```

**Step 4: 検証結果を audit record に記録する** (→ Audit Trail セクション参照)

### 失敗時の対応

```
hash mismatch → 転送をキャンセル
              → evidence_state: cross_pc_missing
              → completion_gate: blocked
              → audit record に mismatch 事実を記録
              → SC に再送を要求
```

---

## PII/Secret Scan

### スキャン対象パターン

以下のパターンに一致する値が report YAML に含まれていないことを確認する。

```bash
# scan コマンド (SC 上で outbound sync 前に実行)
REPORT_FILE="queue/reports/naomasa_secondpc_report.yaml"

grep -nEi \
  'ANTHROPIC_API_KEY|sk-ant-|api_key\s*[:=]|password\s*[:=]|secret\s*[:=]|token\s*[:=]|bearer\s+[A-Za-z0-9_\-]{20,}' \
  "$REPORT_FILE" && echo "SCAN_FAIL: secret found" || echo "SCAN_PASS: no secrets"
```

```bash
# PII パターン (患者データ・個人情報)
grep -nEi \
  '[0-9]{3}-[0-9]{2}-[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|patient_id|birth_date|phone_number|address\s*[:=]' \
  "$REPORT_FILE" && echo "SCAN_FAIL: PII found" || echo "SCAN_PASS: no PII"
```

### スキャン実施タイミング

| タイミング | 実施者 | アクション |
|------------|--------|-----------|
| outbound sync の **直前** | SC 側エージェント | scan を実行し、PASS のみ転送を続行 |
| scan FAIL の場合 | SC 側エージェント | 転送を中止 → karo inbox に報告 |
| scan 未実施の場合 | MC 側 gate 検証 | `evidence_state: cross_pc_missing` をセット |

### スキャン対象外

- `verdict`, `evidence_state`, `completion_gate` フィールド (システム制御値)
- `task_id`, `audit_id`, `timestamp` フィールド (メタデータ)
- `log_path`, `commit_hash` フィールド (参照のみ、値なし)

---

## Audit Trail

### 目的

cross-PC 転送の証跡を残す。MC 側 completion gate が `open` に遷移するための必須証拠。

### Audit Record Schema

```yaml
# queue/reports/cross_pc_transfer_audit.yaml に追記
transfers:
  - transfer_id: xfer_20260511_001
    timestamp: "2026-05-11T09:45:00+09:00"
    source_pc: secondpc
    target_pc: mainpc
    report_file: queue/reports/naomasa_secondpc_report.yaml
    source_hash: "a3f1c2d4e5b6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2"
    target_hash: "a3f1c2d4e5b6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2"
    hash_verified: true
    pii_scan_passed: true
    gate_result: pass  # pass | fail
    operator: ashigaru3  # 転送を実行したエージェント
    notes: ""
```

### 記録先

| ファイル | 役割 |
|---------|------|
| `queue/reports/cross_pc_transfer_audit.yaml` | 全転送の audit log (追記専用) |

**追記ルール:**
- 既存エントリを編集・削除してはならない (append-only)
- `transfer_id` は `xfer_{YYYYMMDD}_{NNN}` 形式 (NNN は当日連番)
- `hash_verified: false` または `pii_scan_passed: false` の場合は `gate_result: fail` を記録し、転送ファイルを MC から削除する

### Completion Gate との連携

```
G1 (naming) PASS
  + G2 (hash) PASS
  + G3 (PII scan) PASS
  + G4 (audit record appended) PASS
  → completion_gate: open (cross-PC 条件クリア)

いずれか FAIL
  → completion_gate: blocked
  → evidence_state: cross_pc_missing
  → shogun_verified: false を維持
```
