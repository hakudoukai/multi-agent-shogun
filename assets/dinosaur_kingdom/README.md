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
| dinosaur_kingdom/backgrounds/kids_dino_hero | backgrounds | shogun-main (3rd次取込) | 2026-05-17 | placeholder (visual-kids-dino-hero-001 サブスク生成待ち、差し替え手順=asset_manifest.json) |
| dinosaur_kingdom/ui/icon_set | ui | shogun-main (3rd次取込) | 2026-05-17 | placeholder (visual-kids-dino-icons-001 サブスク生成待ち、6要素 stamp/badge/star/crown/check/treasure_box) |

| dinosaur_kingdom/backgrounds/bg_hero | backgrounds | 3rd-PC画像部→shogun-main貼込 | 2026-05-17 | **integrated** bg_hero.png (BG-HERO-001, gpt-image-2, pending_codex_review) |
| dinosaur_kingdom/backgrounds/bg_s01 | backgrounds | 3rd-PC→shogun-main貼込 | 2026-05-17 | **integrated** bg_s01.png (BG-S01, pending_codex_review) |
| dinosaur_kingdom/backgrounds/bg_s02 | backgrounds | 3rd-PC→shogun-main貼込 | 2026-05-17 | **integrated** bg_s02.png (BG-S02, pending_codex_review) |
| dinosaur_kingdom/backgrounds/bg_s03 | backgrounds | 3rd-PC→shogun-main貼込 | 2026-05-17 | **integrated** bg_s03.png (BG-S03, pending_codex_review) |
| dinosaur_kingdom/backgrounds/bg_s04 | backgrounds | 3rd-PC→shogun-main貼込 | 2026-05-17 | **integrated** bg_s04.png (BG-S04, pending_codex_review) |
| dinosaur_kingdom/characters/ch_mascot_001 | characters | 3rd-PC→shogun-main貼込 | 2026-05-17 | **integrated** ch_mascot_001.png (CH-MASCOT-001, pending_codex_review) |

> 注: 3rd PC 画像部の全 job が status=planned (実画像未生成、reports/visual-assets/ 不在)。
> 第4次指令前提「P0実画像完成検知」は機械検証で UNMET。指令『不足は明示し止まらず進める』に従い
> 指令名指し ID (BG-HERO/BG-S01-04/CH-MASCOT-001) の名前付き placeholder スロット + 検知統合
> スクリプト (`check_integration.py`) を先行整備。実画像出現時は本物を expected_path へ保存し
> placeholder 削除のみで drop-in 反映 (asset_key 不変・コード変更不要)。詳細 = `asset_manifest.json`。
> 検証: `python3 assets/dinosaur_kingdom/check_integration.py` (real/placeholder/broken 件数を機械判定)。

## backend 連携 (実装側 next)

backend (`teriha_passport_engine`) は `drop_asset_key` / `stamp_asset_key` を本受け口の
論理キーとして格納するのみ。実バイナリ配信は frontend/CDN 層の責務。受け口整備 (本作業) →
seed 配信 → backend asset_key 書込 → frontend 配信、の順で結合する。

> 第4次貼込実施 (directive fd2f1998): 3rd-PC実画像6点を /mnt/c/Users/user/daishogun-inbox/visual-assets から採用、integrate_assets.py --apply で placeholder→実画像 swap。
> ⚠ 品質ゲート検出: BG系5点は 3rd-PC manifest が .webp 宣言だが実体 PNG → 拡張子を .png へ是正 (MIME/配信バグ回避)。全6点 review=pending_codex_review (次監査対象)。
