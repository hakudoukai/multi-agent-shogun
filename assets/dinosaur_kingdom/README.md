# 小児恐竜王国 P0 画像素材 受け口 (handoff staging)

- directive: bf0617af-502b-4175-a635-b64457e8a8a6 (第2次実装)
- spec: `docs/cmd004_dino_p0_assets_receptacle_spec.md`
- 連動 spec: `docs/cmd004_dinosaur_100enemies_spec.md`
- 用途: デザイン班 (画像部) が P0 画像素材を投入する受け口。backend (teriha-passport) は
  `asset_key` 論理キー経由で本ディレクトリ配置物を参照する。

## asset_key 命名規約 (= spec 既定、変更禁)

`docs/cmd004_dinosaur_100enemies_spec.md` L421 が既定:
`stamp_asset_key = f"dinosaur_kingdom/boss/{enemy_id}"`

本受け口はこの規約を物理ディレクトリに対応させる:

| category | asset_key 形式 | 物理パス | DDL 参照列 |
|----------|----------------|----------|------------|
| enemies | `dinosaur_kingdom/enemies/{enemy_id}` | `assets/dinosaur_kingdom/enemies/{enemy_id}.<ext>` | (sprite) |
| boss | `dinosaur_kingdom/boss/{enemy_id}` | `assets/dinosaur_kingdom/boss/{enemy_id}.<ext>` | `award_stamp` stamp_asset_key (spec L421) |
| drops | `dinosaur_kingdom/drops/{drop_id}` | `assets/dinosaur_kingdom/drops/{drop_id}.<ext>` | `drop_asset_key` (spec L301/L346) |
| backgrounds | `dinosaur_kingdom/backgrounds/{scene_id}` | `assets/dinosaur_kingdom/backgrounds/{scene_id}.<ext>` | (戦闘背景) |
| ui | `dinosaur_kingdom/ui/{element_id}` | `assets/dinosaur_kingdom/ui/{element_id}.<ext>` | (HUD/UI) |

## P0 スコープ (最小受け口)

- enemies: P0 は代表 difficulty 帯ごと 1 体ずつ (= 5 体程度)。100 体全量は seed 配信後に追補。
- boss: P0 は最終 boss 1 体。
- drops: P0 は drop_tier 1〜3 の代表 3 種。
- backgrounds: P0 は標準戦闘背景 1 枚。
- ui: P0 は HP バー + 攻撃ボタンの 2 素材。

## 投入規約 (デザイン班 → 本受け口)

1. ファイル名 = `asset_key` の末尾 id + 拡張子。例: enemy_id=`raptor_01` → `enemies/raptor_01.webp`。
2. 推奨形式: `.webp` (透過/軽量)。背景は `.webp` または `.jpg`。
3. 解像度ガイド: enemies/boss = 512x512 上限、backgrounds = 1080x1920 上限、ui = 用途準拠。
4. 患者情報・実患者写真・実名は投入禁止 (= privacy gate 対象)。架空恐竜/ゲーム素材のみ。
5. 投入後、本 README 末尾の受領表に 1 行追記 (id / category / 投入者 / 日付)。

## 受領表 (P0 投入トラッキング)

| asset_key | category | 投入者 | 投入日 | 状態 |
|-----------|----------|--------|--------|------|
| (P0 素材未投入。デザイン班配信待ち。本受け口は構造のみ整備済) | - | - | - | pending |

## backend 連携 (実装側 next)

backend (`teriha_passport_engine`) は `drop_asset_key` / `stamp_asset_key` を本受け口の
論理キーとして格納するのみ。実バイナリ配信は frontend/CDN 層の責務。受け口整備 (本作業) →
seed 配信 → backend asset_key 書込 → frontend 配信、の順で結合する。
