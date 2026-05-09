# 7医院展開時 clinic_id 別 ashigaru 割当設計案

## 前提
- 博道会: 7医院 (T15/T17/T19 等、拡張予定)
- multi-agent-shogun: ashigaru1-7 の7 pane使用可能
- clinic_id で Supabase RLS テナント分離済み

## 設計案A: 1医院1足軽 (推奨)

```
ashigaru1 → clinic_hakudoukai_main   (本院)
ashigaru2 → clinic_hakudoukai_t15    (T15分院)
ashigaru3 → clinic_hakudoukai_t17    (T17分院)
ashigaru4 → clinic_hakudoukai_t19    (T19分院)
ashigaru5 → clinic_hakudoukai_t21    (予備1)
ashigaru6 → clinic_hakudoukai_t23    (予備2)
ashigaru7 → clinic_shared_pool       (共通タスク/監査)
```

### 利点
- clinic_id と ashigaru が1:1、指揮系統明確
- RLS境界と一致、データ漏洩リスク最小
- 各医院の作業が他医院をブロックしない

### 実装
1. config/settings.yaml に clinic_mapping セクション追加
2. queue/tasks/{agent}.yaml に clinic_id フィールド追加
3. karo のタスク割当ロジックに clinic_id → agent 自動ルーティング追加
4. hakudokai_init_agents.sh に --clinic-id オプション追加

## 設計案B: プール方式

```
ashigaru1-5 → 汎用プール (karo が空きagentに割当)
ashigaru6   → 監査専用 (Codex/Gemini dispatch)
ashigaru7   → 緊急対応専用
```

clinic_id は タスクYAML で指定、agent は固定しない。

### 利点
- リソース効率最大 (idle agent 最小化)
- 医院数 > 7 でも対応可能

### 欠点
- karo のルーティング複雑化
- 同一agentが複数clinic_id を扱うRLSリスク

## 推奨: 設計案A (Phase 1)
7医院以下なら A で十分。A の1:1 mapping は運用シンプル、トラブル時の原因特定容易。
7医院超過時に B へ移行検討。

## config/settings.yaml 拡張案

```yaml
clinic_mapping:
  hakudoukai_main:
    ashigaru: ashigaru1
    display_name: "博道会本院"
  hakudoukai_t15:
    ashigaru: ashigaru2
    display_name: "T15分院"
  # ...

multi_clinic:
  enabled: false  # Phase 1 は false (本院のみ)
  routing: "fixed"  # fixed | pool
```
