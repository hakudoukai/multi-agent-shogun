# cmd_004 小児恐竜王国 P0 画像素材 受け口 spec + handoff manifest

- directive_id: bf0617af-502b-4175-a635-b64457e8a8a6 (第2次: 会計待ち時間ゼロ + 小児恐竜王国 実装)
- operation_id: zero-wait-dino-implementation
- 作成: 2026-05-17 (shogun-main / 信長 orchestrator)
- 連動 spec: `docs/cmd004_dinosaur_100enemies_spec.md` (L421 asset_key 既定)
- 受け口実体: `assets/dinosaur_kingdom/` + `assets/dinosaur_kingdom/README.md`
- 評価原則: 機械 evidence のみ、本能寺戒め遵守、外部 repo 不在につき本 repo 内完結 MVP

---

## 0. 本実装の位置づけ (第2次 directive 優先順 3 の MVP)

第2次 directive mission 優先順:
1. 会計待ち時間0導線 — 実装先=外部 dentalbi backend/etl
2. 小児恐竜報告の画面/状態接続 — 実装先=外部 dentalbi PWA
3. **画像部P0素材の受け口（assets/backgrounds等）整備 — 本 repo 内完結 ← 本 spec で実装**

**制約による判断 (推奨案 + 理由)**: 外部 dentalbi repo `<DENTALBI_REPO_ROOT>` は
main_pc に clone 不在 (機械確認: `ls <DENTALBI_REPO_ROOT>` → No such file)。
ゆえに優先順 1/2 は main_pc で直接実装不可。止まらず、低リスク・本 repo 内完結・
mission 直結の優先順 3 を MVP として完遂する。これにより外部 repo 復旧 or seed 配信を
待つ間も、デザイン班の P0 素材投入を即受け入れ可能な状態を先行整備できる。

## 1. AC1: 受け口構造 (実装済)

```
assets/dinosaur_kingdom/
├── README.md          # handoff 規約 + 受領表
├── enemies/.gitkeep   # 敵 sprite (100 体、P0 は代表 5 体)
├── boss/.gitkeep      # boss 画像 (spec L421 stamp_asset_key 準拠)
├── drops/.gitkeep     # drop アイテム (drop_asset_key 準拠)
├── backgrounds/.gitkeep  # 戦闘背景
└── ui/.gitkeep        # HUD/UI 素材
```

## 2. AC2: asset_key 命名規約 (spec 既定との整合)

`docs/cmd004_dinosaur_100enemies_spec.md` の機械 evidence:
- L421: `stamp_asset_key=f"dinosaur_kingdom/boss/{enemy_id}"`
- L301: `drop_asset_key TEXT` (DDL `passport_dino_enemy` 列)
- L346: `drop_asset_key TEXT NOT NULL` (DDL `passport_dino_drop_inventory` 列)

本受け口は上記論理キーを物理パスへ 1:1 対応 (README 規約表参照)。
**命名規約は spec 既定を変更せず踏襲** (= 後続 backend 実装の asset_key 書込と無改修で結合)。

## 3. AC3: P0 スコープ (最小受け口で early release 寄与)

| category | P0 件数 | full 件数 | 配信トリガ |
|----------|---------|-----------|------------|
| enemies | 代表 5 | 100 | 100体 seed JSON 配信後 |
| boss | 1 | difficulty 別複数 | 同上 |
| drops | 3 (tier1-3) | drop_tier 1-8 | drop 抽選実装後 |
| backgrounds | 1 | scene 別 | 戦闘 UI 実装後 |
| ui | 2 (HPバー/攻撃) | HUD 全要素 | 戦闘 UI 実装後 |

P0 = 戦闘 1 ループを画面表示できる最小素材セット。これ以上は seed/engine 実装に依存。

## 4. AC4: 低リスク検証 (本能寺戒め)

| risk 項目 | 判定 | evidence |
|-----------|------|----------|
| 患者情報 | 不該当 | 架空恐竜ゲーム素材のみ、README 投入規約 4 で実患者写真/実名禁止明記 |
| 本番 DB 破壊 | 不該当 | DDL apply 一切なし、ディレクトリ + md のみ |
| 外部公開 | 不該当 | 本 repo 内 staging、外部 push/publish なし |
| 既存破壊 | 不該当 | 新規ファイル/ディレクトリのみ、既存改変は .gitignore allowlist 追記のみ |
| privacy gate | PASS 目標 | `scripts/validate_report_privacy.py` で HIGH=0 検証 |

## 5. AC5: .gitignore allowlist 整合

repo は default-deny .gitignore。本受け口を commit 可能にするため allowlist 追記:
- `!docs/cmd004_dino_p0_assets_receptacle_spec.md` (本 spec)
- `!docs/cmd004_release_readiness_dispatch_*.md` (前 directive 0fa1c9e3 評価書、継続性のため同時 allowlist)
- `!assets/` `!assets/dinosaur_kingdom/` `!assets/dinosaur_kingdom/**` (受け口本体)

既存 `!docs/cmd004_*` パターンに倣い、並行 agent 競合回避のため cmd_004 block 内に追記。

## 6. 残ブロッカー

- B1[高]: 外部 dentalbi repo が main_pc に clone 不在 → 優先順 1/2 (会計導線/恐竜画面接続) は
  main_pc 直接実装不可。SC 側実装 or main_pc への clone 配備が前提。
- B2[中]: Karo pane が任意フィードバックプロンプト (0:Dismiss) で入力待ち。watcher 層は復旧済
  (inbox_watcher.sh shogun/karo 等稼働確認)、escalation 機構で自動解除見込み。
- B3[中]: 100体 seed JSON / 戦闘 engine 未実装ゆえ P0 素材は代表数のみ。full は seed 配信依存。

## 7. next 30min 実装予定

1. 外部 repo clone 配備可否を大将軍へ確認 (blocked ではなく next_action、main_pc 実装の前提)
2. clone 配備後: 優先順 1 = 会計→カンバン billing 自動移動の E2E 導線 MVP
3. seed 配信後: enemies/boss 受け口へ P0 代表素材の placeholder 投入 + 受領表更新
