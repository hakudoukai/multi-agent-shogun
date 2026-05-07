# Incident Log: queue/inbox split-brain (2026-05-08)

## 概要

| 項目 | 値 |
|------|----|
| 発生時刻 | 2026-05-08 ~00:14 JST |
| 検知時刻 | 2026-05-08 ~00:55 JST (信長最終監査中) |
| 復旧完了 | 2026-05-08 00:52 JST |
| 影響継続 | 約 37 分 |
| 重要度 | ERROR (= 通信路停止、業務阻害) |
| エラーコード候補 | ERR-INBOX-001 |
| 検知者 | 信長 (理事長殿勅命の最終監査により発見) |
| 復旧者 | 信長直筆 (Phase A merge + B symlink + C script fix + D verify) |

## 影響

### 失われた通信
- **karo.yaml ↔ hideyoshi.yaml split-brain (5 件)**:
  - karo.yaml unique 2 件 (秀吉のみ受信、hideyoshi.yaml 未到達):
    - msg_20260508_001408 (家康 self-audit 完了報告)
    - msg_20260508_001518 (nobunaga report_completed)
  - hideyoshi.yaml unique 3 件 (秀吉に未到達、orphan):
    - msg_20260508_002322 = **信長 v2 directive (ashigaru2 草案 v2 fix 督促)**
    - msg_20260508_002835 = **信長 cmd_phase4_persona_display_rename_001 (旧名 display 全駆逐 cmd)**
    - msg_20260508_003718 = ashigaru1 report
- **gunshi.yaml ↔ ieyasu.yaml split-brain (2 件)**:
  - gunshi.yaml unique 1 件 (家康受信、ieyasu.yaml 未到達)
  - ieyasu.yaml unique 1 件 (家康未到達、orphan)

### 業務阻害
- 家老秀吉が信長 cmd_phase4 (旧名 display 全駆逐) を受信できず、322 hits の rename 作業が停滞
- 家康が一部監査依頼を受信できず、PDCA 循環一部停滞
- 「家老処理進まず idle 4+ 分」現象の真因 = 通信路の物理的途絶

## 5 Why 分析

| # | 質問 | 答え |
|---|------|------|
| 1 | なぜ split-brain ? | 信長 inbox_write target=hideyoshi で書込、新規ファイル hideyoshi.yaml が作成、秀吉 (= karo agent_id) が読む karo.yaml と分離 |
| 2 | なぜ新規 hideyoshi.yaml? | Phase 3 full commit (5be193c, 2026-05-07 23:58) で設置された symlink `karo.yaml → hideyoshi.yaml` が消失していた |
| 3 | なぜ symlink 消失? | `scripts/inbox_write.sh` の atomic replace `os.replace(tmp_path, '$INBOX')` が、INBOX が symlink の場合 **symlink 自体を tmp ファイルで置換** していた (= symlink kill) |
| 4 | なぜ os.replace で symlink 破壊? | `os.replace` は dst path を atomic に置換する仕様、dst が symlink でも同様に上書き。`os.path.realpath` で canonical path に解決せず、symlink path を直接 replace target にしていた |
| 5 | なぜ realpath 未使用? | 設計時 (Phase 3 partial 以前) は symlink alias 運用が想定外。tempfile + os.replace の素朴な atomic write pattern を採用、symlink 保持考慮なし。Phase 3 で alias 設置されたが、inbox_write.sh は更新されず |

### 根本原因 (root cause)
**Phase 3 全 rename で symlink alias を導入したが、inbox_write.sh の atomic replace logic が symlink 非対応のまま放置された** (= cross-cutting 設計変更時の影響波及検証漏れ)。

## 復旧手順 (実施済)

### Phase A: データ救出 (lossless merge)
- Python + flock で hideyoshi.yaml unique 3 件 → karo.yaml superset 化
- 同様に ieyasu.yaml unique 1 件 → gunshi.yaml superset 化
- timestamp 昇順で sort、整合性確認

### Phase B: symlink 復旧
- 設計方針: 新 persona 名を canonical (= shogun.yaml→nobunaga.yaml と同型)、旧名を alias
- 実装:
  ```bash
  rm queue/inbox/hideyoshi.yaml             # subset 廃棄
  mv queue/inbox/karo.yaml queue/inbox/hideyoshi.yaml  # superset を canonical 名へ rename
  ln -s hideyoshi.yaml queue/inbox/karo.yaml           # 旧名を alias 化
  ```
  (gunshi/ieyasu 同型)

### Phase C: 恒久 fix (script hardening)
- `scripts/inbox_write.sh` の atomic write block に **`os.path.realpath` による canonical 解決** を追加:
  ```python
  # CRITICAL: dereference symlinks BEFORE atomic replace.
  inbox_canonical = os.path.realpath('$INBOX')
  tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(inbox_canonical), suffix='.tmp')
  ...
  os.replace(tmp_path, inbox_canonical)
  ```
- これにより TARGET=karo で書込しても canonical (hideyoshi.yaml) に着弾、symlink alias 保持

### Phase D: 実機検証
- D1: realpath 解決 — 全 3 alias 正解
- D2: 修正後 inbox_write.sh で test write → hideyoshi.yaml +1 件着弾、karo.yaml symlink 保持
- D3: md5 一致確認 (alias 経由 ≡ canonical)
- D4: 検証用 message を read=true 化で雑音除去

### Phase E: 文書化 (= 本 incident log)

### Phase F: commit
- `scripts/inbox_write.sh` (恒久 fix)
- `docs/incident_logs/2026-05-08_inbox_split_brain.md` (本ファイル)

## 検知方法 (将来の自動検知)

### 検知パターン
1. **alias と canonical の md5 不一致** = symlink 破断中
2. **alias が regular file** (= 期待 symlink) の検知
3. **同名 base のファイルが 2 つ独立に存在** (= karo.yaml + hideyoshi.yaml が両方 regular file)

### 推奨 check スクリプト
```bash
#!/usr/bin/env bash
# scripts/checks/inbox_alias_integrity.sh
PAIRS=(
  "queue/inbox/karo.yaml:queue/inbox/hideyoshi.yaml"
  "queue/inbox/gunshi.yaml:queue/inbox/ieyasu.yaml"
  "queue/inbox/shogun.yaml:queue/inbox/nobunaga.yaml"
)
for pair in "${PAIRS[@]}"; do
  alias="${pair%%:*}"
  canonical="${pair##*:}"
  if [ ! -L "$alias" ]; then
    echo "WARN: $alias is NOT a symlink (= split-brain risk)" >&2
    exit 1
  fi
  if [ "$(readlink -f "$alias")" != "$(readlink -f "$canonical")" ]; then
    echo "WARN: $alias does not resolve to $canonical" >&2
    exit 1
  fi
done
exit 0
```

## 再発防止策

### 即時 (= 本 commit で実施)
1. ✅ inbox_write.sh の atomic write を realpath 経由に修正
2. ✅ symlink alias 復旧 (karo↔hideyoshi, gunshi↔ieyasu, shogun↔nobunaga 全整合)

### 短期 (= 別 cmd 推奨)
3. `scripts/checks/inbox_alias_integrity.sh` 新設、PreToolUse hook 候補
4. `scripts/inbox_watcher.sh` 等の他 inbox 操作 script に同型 (atomic replace) パターンが無いか走査
5. instructions/hideyoshi.md L27 / instructions/ieyasu.md L27 を「(= alias `karo.yaml`/`gunshi.yaml` 経由読込可、canonical は `hideyoshi.yaml`/`ieyasu.yaml`)」に明文化

### 中期 (= §19 lessons-to-skill)
6. skill 候補: **symlink-aware atomic write** = pattern 化、全 watcher/inbox/queue 系 script で realpath 必須
7. skill 候補: **alias 整合性 weekly audit** (cron で md5 一致を毎週検証、不一致で ntfy 発火)

### 長期 (= Phase 5+)
8. queue/ 全体の persona 名統一: 旧名 alias 廃止、全 agent が直接 canonical (= 新名) を読書きする AGENT_ID 完全 migration
9. inbox 通信を Supabase 一元管理化検討 (= ファイル symlink 依存解消)

## 関連ファイル / commit

- 修正前 inbox_write.sh: commit 5be193c (Phase 3 full、symlink 設置のみで script 未更新)
- 復旧 commit: 2026-05-08 (本 incident 直後 — 別 commit で本ログ + script fix)
- 影響受けた message:
  - 信長 v2 directive: msg_20260508_002322_f2a9558f (= 救出済)
  - 信長 cmd_phase4: msg_20260508_002835_0f5d5f49 (= 救出済)
  - ashigaru1 report: msg_20260508_003718_b7579dc4 (= 救出済)
  - 家康 audit 系: msg_20260508_003751_b7a62fd2 (= 救出済)

## §19 Lessons Capture mandate

本 incident は §19 mandate 対象。skill 化候補 2 件 (symlink-aware atomic write / alias integrity audit) を理事長殿に提示、明示承認後に skill commit する段取り。

---
*記録: 信長 (織田信長) — 2026-05-08 復旧直後*
