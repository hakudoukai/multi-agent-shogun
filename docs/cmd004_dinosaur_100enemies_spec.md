# cmd_004 小児恐竜王国 敵 100 体 設計 spec (DD-126 game logic 拡張)

- task_id: subtask_cmd004_dinosaur_100enemies_spec
- parent_cmd: cmd_004「小児恐竜王国」
- bloom_level: L4
- author: ashigaru1 (榊原康政 persona、MainPC)
- 起案日: 2026-05-11
- 範囲: **spec + 実装入口 stub のみ**。完全実装 (戦闘エンジン中身 / 100 体 seed JSON / RLS / 結合テスト) は別 cycle 配信。
- 連動 spec:
  - `docs/cmd004_ai_chat_spec.md` (ashigaru5 起案、AI チャット系)
  - `docs/cmd004_guardian_consent_spec.md` (ashigaru4 起案、保護者同意 gate)
- 根拠 file (= 機械 evidence 引用):
  - `<DENTALBI_REPO_ROOT>/backend/services/teriha_passport_engine.py` (502 行、L1-502 全数把握)
  - `<DENTALBI_REPO_ROOT>/backend/routers/teriha_passport.py` (431 行)
  - `<DENTALBI_REPO_ROOT>/backend/services/child_adventure_engine.py` (203 行、参考)

---

## 0. Anti-Duplication: 参照済み正本 / 本 spec scope out

| # | 正本 | 所在 file:line | 利用方法 |
|---|------|----------------|----------|
| A | `TerihaPassportEngine.add_xp()` | `teriha_passport_engine.py:148-205` | 敵討伐後 XP 加算 → rank 昇格判定の正本。本 spec は **add_xp を呼ぶ側** |
| B | `RANK_TABLE` (5 階級) | `teriha_passport_engine.py:39-45` | tamago/hiyoko/bokensha/yusha/okoku_senshi。敵出現 rank gate に使用 |
| C | `resolve_age_tier()` | `teriha_passport_engine.py:48-67` | egg/chick/adventurer/hero/kingdom_warrior。敵出現 age gate に使用 |
| D | `award_stamp()` (5 種) | `teriha_passport_engine.py:318-375` | reservation_achieved / visit / quest_complete / birthday / special。**boss 撃破時 `special` を流用** |
| E | `redeem_reward()` + `REWARD_COST_BY_TIER` | `teriha_passport_engine.py:380-435` | drop item の交換 endpoint は既存。本 spec は **drop → reward 在庫追加** の橋渡しのみ規定 |
| F | `record_game_score()` | `teriha_passport_engine.py:440-471` | 既存 minigame 用 (score-only)。本 spec の **戦闘 log は別 table** (= `passport_dino_battle_log`) として共存 |
| G | `passport_adventure_mapping` | engine L270-298 で参照 | 既存 procedure→mission 紐付け。**敵 master は別 table** とする (= mapping は処置由来、敵は探検由来) |

**本 spec で扱わない (= scope out):**
- 100 体 seed の **全 JSON 値** (= 本 spec は 100 件分の id/name/difficulty/age_tier/出現 rank を全数列挙、HP/xp/drop は計算式 + 代表値のみ。最終 seed は次 cycle 別 ashigaru 配信)
- 戦闘 engine の **乱数 RNG 内部実装** (= 本 spec は I/O 仕様と式のみ規定。stub 関数は `NotImplementedError` 雛形)
- Supabase **DDL apply** (= 本 spec §4 で DDL 案を起草、apply は cmd_004 別 task = ceremony_event_api task 等と束ねて家老 batch で実施)
- frontend 戦闘 UI / animation (= デザイン班専権)
- RLS policy (= cmd_004 別 task の保護者同意 gate 完了後に追加)

---

## 1. AC1: dinosaur_kingdom 既実装 inventory (file:line)

調査 base: `<DENTALBI_REPO_ROOT>/` HEAD (2026-05-11 16:35 push 後)。

### 1-1. Engine 層 (= 既存)

| 機能 | symbol | file:line | 戦闘との関係 |
|------|--------|-----------|------------|
| 定数 clinic_id | `TERIHA_CLINIC_ID = 5` | engine L23 | **戦闘 API は clinic_id=5 固定 guard** |
| 定数 world_theme | `DINO_WORLD_THEME_ID = 3` | engine L24 | 戦闘 log で世界観 ID として記録 |
| 階級閾値 | `RANK_TABLE` 5 件 | engine L39-45 | 敵 `min_rank_gate` 比較で利用 |
| 年齢 tier 算出 | `resolve_age_tier()` | engine L48-67 | 敵 `age_tier_eligibility` 比較で利用 |
| XP 加算 + 昇格 | `add_xp()` | engine L148-205 | **討伐 reward 配布の正本 entry** |
| ミッション付与 | `assign_mission_from_procedure()` | engine L210-239 | 戦闘とは別系統、共存 |
| ミッション完了 | `complete_mission()` | engine L241-268 | (戦闘 boss 撃破時に `quest_complete` stamp 共用想定) |
| スタンプ授与 | `award_stamp()` (5 種) | engine L318-375 | boss 撃破 → `special` stamp 流用 (= 新規 stamp_kind 増やさず) |
| 報酬交換 | `redeem_reward()` | engine L380-435 | drop item は別 table に在庫追加 → ここで交換可 |
| ミニゲーム score | `record_game_score()` | engine L440-471 | 別 game (= スコアアタック)、戦闘と共存 |
| family link | `link_family()` | engine L476-502 | 戦闘との直接連動なし |

### 1-2. Router 層 (= 既存)

調査: `backend/routers/teriha_passport.py` (431 行)。
**現状 enemy/battle 系 endpoint は未実装** (= `grep -E 'enemy|battle|fight' teriha_passport.py` ヒット 0)。
本 spec §5 で `/api/teriha-passport/dino-fight` 系 4 endpoint を新規規定。

### 1-3. DB schema (= 既存 / 不在)

| table | 状態 | 用途 |
|-------|------|------|
| `passport_members` | 既存 (engine L109, 132, 191) | member 本体 + age_tier 紐付け |
| `passport_xp_log` | 既存 (engine L167, 188, 397) | XP 加算履歴、戦闘 reward の流入先 |
| `passport_mission_log` | 既存 (engine L238, 244) | 処置 quest、戦闘とは別系統 |
| `passport_stamp_log` | 既存 (engine L346) | 5 種 stamp、boss 撃破時 `special` 流用 |
| `passport_reward_history` | 既存 (engine L405, 423) | drop item の交換履歴 |
| `passport_game_score` | 既存 (engine L459) | score-only minigame、戦闘とは別 |
| `passport_adventure_mapping` | 既存 (engine L276, 288) | 処置 keyword → mission、戦闘とは別 |
| `passport_dino_enemy_master` | **不在** | 本 spec §4 で新規規定 (= 100 体 metadata 正本) |
| `passport_dino_battle_log` | **不在** | 本 spec §4 で新規規定 (= 戦闘記録) |
| `passport_dino_drop_inventory` | **不在** | 本 spec §4 で新規規定 (= drop 在庫、redeem_reward 入口) |

### 1-4. 結論 (AC1)

- **敵 100 体 game logic は engine / router / DB schema いずれも未実装** (= 完全新規制作領域)。
- 既存 engine 5 経路 (`add_xp` / `award_stamp` / `redeem_reward` / `complete_mission` / `record_game_score`) は **再利用前提**、本 spec は **追加 3 table + 4 endpoint + 1 stub method group** のみ提案。
- 既 RANK_TABLE / AGE_TIER_ORDER は再利用、新規 enum 増やさず。

---

## 2. AC2-a: 戦闘設計 5 軸 (difficulty / age_tier / rank_gate / HP / xp_reward)

### 2-1. difficulty class (5 段階) + 統計値 baseline

| difficulty | baseline HP | baseline xp_reward | crit 率 | drop 確率 | session 想定秒 |
|------------|-------------|--------------------|---------|-----------|---------------|
| `very_easy` | 10 | 5 | 0% | 5% | 30 |
| `easy` | 30 | 15 | 5% | 10% | 60 |
| `normal` | 60 | 30 | 10% | 20% | 120 |
| `hard` | 120 | 60 | 15% | 30% | 240 |
| `boss` | 250 | 150 | 20% | 60% | 420 |

**式 (= HP / xp は seed JSON で個別 override 可、baseline は default 値):**

```
final_hp(enemy, member) = enemy.base_hp * (1 + 0.10 * (member.rank.order - 1))
final_xp(enemy, member) = enemy.base_xp * (1 + 0.05 * (member.rank.order - 1))
crit_xp_multiplier      = 1.5
boss_first_kill_bonus   = +50 xp (= 同一 enemy_id 初回討伐のみ、boss tier 限定)
```

理由: 階級が上がっても弱敵が即死とならぬよう scale、ただし弱敵を周回する旨味は減衰させる。

### 2-2. age_tier eligibility matrix (= 出現条件①)

各敵は `age_tier_eligibility: list[str]` (e.g. `["egg", "chick"]`) を持つ。`resolve_age_tier(member.birth_date)` が含まれぬ場合は **出現抽選対象外**。

| age_tier (engine L26 順) | eligibility 命名規約 |
|--------------------------|--------------------|
| `egg` (0-2 歳) | very_easy のみ、boss 出現禁 (= 安全側) |
| `chick` (3-6 歳) | very_easy + easy、normal は弱型のみ |
| `adventurer` (7-9 歳) | easy + normal + hard 序盤 |
| `hero` (10-12 歳) | normal + hard + boss 序盤 |
| `kingdom_warrior` (13+) | 全 difficulty |

### 2-3. rank_gate (= 出現条件②)

各敵は `min_rank_gate: str` (`RANK_TABLE` rank_code) を持つ。`member.current_rank_code` の `order` がそれ未満なら抽選対象外。

| difficulty | 推奨 min_rank_gate |
|------------|-------------------|
| `very_easy` | `tamago` (order 1) |
| `easy` | `tamago` (order 1) |
| `normal` | `hiyoko` (order 2) |
| `hard` | `bokensha` (order 3) |
| `boss` | `yusha` (order 4) |

### 2-4. clinic_id 固定 guard (= 出現条件③)

本機能は **clinic_id=5 (= 香椎照葉) 専用**。engine `TERIHA_CLINIC_ID` (L23) と一致確認、ぶれた場合は engine L105-108 既存 raise を踏襲。

### 2-5. tier (= 出現条件④、appointment 連動)

`member.subscription_status` (engine L128 既存) が `active` の場合のみ boss 抽選対象、`pending` (= 出生未登録) は boss skip。

### 2-6. 結論 (AC2-a)

出現抽選 = 4 ゲート (age_tier ∩ rank_gate ∩ clinic_id ∩ subscription_status) の AND。
**AND fail なら抽選対象 0、empty result の場合は呼出側で `no_enemy_available` を返却** (= 戦闘画面に「今日は休戦中」案内)。

---

## 3. AC2-b: 100 体 enemy roster (= id / name / difficulty / age_tier / min_rank)

**命名規約:**
- `enemy_id`: `dino_{difficulty_short}_{NN}` (例 `dino_ve_01`, `dino_bs_04`)
- `name`: 児童向け カタカナ表記、語尾「〜くん」「〜さま」(boss) で親しみ
- 各 difficulty 20 体 × 5 difficulty = **100 体**

### 3-1. very_easy (20 体) — egg + chick 専用、min_rank=tamago

| # | enemy_id | name | base_hp | base_xp | age_tier_eligibility | drop_tier |
|---|----------|------|---------|---------|---------------------|-----------|
| 1 | `dino_ve_01` | コドモタマゴくん | 8 | 4 | egg, chick | 1 |
| 2 | `dino_ve_02` | ピヨピヨザウルス | 10 | 5 | egg, chick | 1 |
| 3 | `dino_ve_03` | キノコザウルス | 10 | 5 | egg, chick | 1 |
| 4 | `dino_ve_04` | クサクサくん | 9 | 5 | egg, chick | 1 |
| 5 | `dino_ve_05` | ミニトカゲ | 10 | 5 | egg, chick | 1 |
| 6 | `dino_ve_06` | コアラザウルス | 11 | 5 | egg, chick | 1 |
| 7 | `dino_ve_07` | ハナガメくん | 12 | 6 | egg, chick | 1 |
| 8 | `dino_ve_08` | ホタルザウルス | 8 | 5 | egg, chick | 1 |
| 9 | `dino_ve_09` | コビトザウルス | 10 | 5 | egg, chick | 1 |
| 10 | `dino_ve_10` | スイカザウルス | 11 | 5 | chick, adventurer | 1 |
| 11 | `dino_ve_11` | ヒマワリくん | 10 | 5 | egg, chick | 1 |
| 12 | `dino_ve_12` | ハマグリスケ | 9 | 5 | egg, chick | 1 |
| 13 | `dino_ve_13` | フルーツザウルス | 11 | 6 | chick, adventurer | 1 |
| 14 | `dino_ve_14` | ウサミミ恐竜 | 10 | 5 | egg, chick | 1 |
| 15 | `dino_ve_15` | プチプチくん | 8 | 4 | egg, chick | 1 |
| 16 | `dino_ve_16` | チビザウルス | 10 | 5 | egg, chick | 1 |
| 17 | `dino_ve_17` | アメちゃんザウルス | 10 | 5 | egg, chick | 1 |
| 18 | `dino_ve_18` | リンゴくん | 11 | 5 | egg, chick | 1 |
| 19 | `dino_ve_19` | コドモリュウ | 10 | 5 | egg, chick | 1 |
| 20 | `dino_ve_20` | ニコニコザウルス | 12 | 6 | chick, adventurer | 1 |

### 3-2. easy (20 体) — chick + adventurer 主、min_rank=tamago

| # | enemy_id | name | base_hp | base_xp | age_tier_eligibility | drop_tier |
|---|----------|------|---------|---------|---------------------|-----------|
| 21 | `dino_e_01` | アンキロくん | 30 | 15 | chick, adventurer | 2 |
| 22 | `dino_e_02` | パラサウロくん | 32 | 16 | chick, adventurer | 2 |
| 23 | `dino_e_03` | ステゴくん | 30 | 15 | chick, adventurer | 2 |
| 24 | `dino_e_04` | ハドロくん | 28 | 14 | chick, adventurer | 2 |
| 25 | `dino_e_05` | プテラくん | 30 | 15 | adventurer, hero | 2 |
| 26 | `dino_e_06` | イグアノくん | 32 | 16 | chick, adventurer | 2 |
| 27 | `dino_e_07` | プシッタコくん | 30 | 15 | chick, adventurer | 2 |
| 28 | `dino_e_08` | プロトケラくん | 30 | 15 | adventurer, hero | 2 |
| 29 | `dino_e_09` | コンプソくん | 25 | 12 | chick, adventurer | 2 |
| 30 | `dino_e_10` | オルニトくん | 30 | 15 | chick, adventurer | 2 |
| 31 | `dino_e_11` | ノドサウルくん | 35 | 17 | adventurer, hero | 2 |
| 32 | `dino_e_12` | ピナコくん | 28 | 14 | chick, adventurer | 2 |
| 33 | `dino_e_13` | サウロロフくん | 32 | 16 | adventurer, hero | 2 |
| 34 | `dino_e_14` | ガリミムくん | 30 | 15 | adventurer, hero | 2 |
| 35 | `dino_e_15` | エウオプロケファルくん | 35 | 17 | adventurer, hero | 2 |
| 36 | `dino_e_16` | コリトくん | 30 | 15 | chick, adventurer | 2 |
| 37 | `dino_e_17` | アヴァケラくん | 28 | 14 | adventurer, hero | 2 |
| 38 | `dino_e_18` | アロコドンくん | 30 | 15 | adventurer, hero | 2 |
| 39 | `dino_e_19` | ヘテロドンくん | 30 | 15 | chick, adventurer | 2 |
| 40 | `dino_e_20` | ミクロラプトルくん | 25 | 13 | chick, adventurer | 2 |

### 3-3. normal (20 体) — adventurer + hero 主、min_rank=hiyoko

| # | enemy_id | name | base_hp | base_xp | age_tier_eligibility | drop_tier |
|---|----------|------|---------|---------|---------------------|-----------|
| 41 | `dino_n_01` | トリケラくん | 60 | 30 | adventurer, hero | 3 |
| 42 | `dino_n_02` | アロサウルくん | 62 | 31 | adventurer, hero | 3 |
| 43 | `dino_n_03` | ケラトくん | 60 | 30 | adventurer, hero | 3 |
| 44 | `dino_n_04` | スピノくん | 65 | 32 | hero, kingdom_warrior | 3 |
| 45 | `dino_n_05` | カルノくん | 60 | 30 | adventurer, hero | 3 |
| 46 | `dino_n_06` | ディプロドクスくん | 70 | 35 | hero, kingdom_warrior | 3 |
| 47 | `dino_n_07` | バリオニクスくん | 60 | 30 | adventurer, hero | 3 |
| 48 | `dino_n_08` | アクロカントくん | 65 | 32 | hero, kingdom_warrior | 3 |
| 49 | `dino_n_09` | コエロフィシスくん | 55 | 28 | adventurer, hero | 3 |
| 50 | `dino_n_10` | ディロフォくん | 60 | 30 | adventurer, hero | 3 |
| 51 | `dino_n_11` | メガロサウルくん | 65 | 32 | hero, kingdom_warrior | 3 |
| 52 | `dino_n_12` | クリオロフォくん | 58 | 29 | adventurer, hero | 3 |
| 53 | `dino_n_13` | ユタラプトルくん | 60 | 30 | hero, kingdom_warrior | 3 |
| 54 | `dino_n_14` | アウストロラプトルくん | 60 | 30 | hero, kingdom_warrior | 3 |
| 55 | `dino_n_15` | デイノニクスくん | 55 | 28 | adventurer, hero | 3 |
| 56 | `dino_n_16` | バンビラプトルくん | 60 | 30 | adventurer, hero | 3 |
| 57 | `dino_n_17` | ヒパクロくん | 60 | 30 | adventurer, hero | 3 |
| 58 | `dino_n_18` | テノントくん | 65 | 32 | hero, kingdom_warrior | 3 |
| 59 | `dino_n_19` | ドリオサウルくん | 60 | 30 | adventurer, hero | 3 |
| 60 | `dino_n_20` | プラテオくん | 70 | 35 | hero, kingdom_warrior | 3 |

### 3-4. hard (20 体) — hero + kingdom_warrior、min_rank=bokensha

| # | enemy_id | name | base_hp | base_xp | age_tier_eligibility | drop_tier |
|---|----------|------|---------|---------|---------------------|-----------|
| 61 | `dino_h_01` | ティラノドン | 120 | 60 | hero, kingdom_warrior | 4 |
| 62 | `dino_h_02` | ギガノトドン | 130 | 65 | hero, kingdom_warrior | 4 |
| 63 | `dino_h_03` | マプサウルドン | 125 | 62 | hero, kingdom_warrior | 4 |
| 64 | `dino_h_04` | カルカロドン | 130 | 65 | hero, kingdom_warrior | 4 |
| 65 | `dino_h_05` | スコミムスドン | 115 | 58 | hero, kingdom_warrior | 4 |
| 66 | `dino_h_06` | スーパーサウルドン | 140 | 70 | kingdom_warrior | 4 |
| 67 | `dino_h_07` | アルゼンチノドン | 145 | 72 | kingdom_warrior | 4 |
| 68 | `dino_h_08` | パタゴティタンドン | 145 | 72 | kingdom_warrior | 4 |
| 69 | `dino_h_09` | ドレッドノートゥスドン | 140 | 70 | kingdom_warrior | 4 |
| 70 | `dino_h_10` | ケツァルコアトルドン | 110 | 55 | hero, kingdom_warrior | 4 |
| 71 | `dino_h_11` | ハツェゴプテリクスドン | 115 | 58 | hero, kingdom_warrior | 4 |
| 72 | `dino_h_12` | アンキロサウルドン | 120 | 60 | hero, kingdom_warrior | 4 |
| 73 | `dino_h_13` | ステゴサウルドン | 120 | 60 | hero, kingdom_warrior | 4 |
| 74 | `dino_h_14` | パキケファロドン | 110 | 55 | hero, kingdom_warrior | 4 |
| 75 | `dino_h_15` | スティギモロクドン | 110 | 55 | hero, kingdom_warrior | 4 |
| 76 | `dino_h_16` | アロサウルスドン | 120 | 60 | hero, kingdom_warrior | 4 |
| 77 | `dino_h_17` | ヤンチュアノドン | 125 | 62 | hero, kingdom_warrior | 4 |
| 78 | `dino_h_18` | シノラプトルドン | 115 | 58 | hero, kingdom_warrior | 4 |
| 79 | `dino_h_19` | ピアトニツキーサウルドン | 125 | 62 | hero, kingdom_warrior | 4 |
| 80 | `dino_h_20` | バハリアサウルドン | 130 | 65 | kingdom_warrior | 4 |

### 3-5. boss (20 体) — hero 一部 + kingdom_warrior、min_rank=yusha、subscription=active 必須

| # | enemy_id | name | base_hp | base_xp | age_tier_eligibility | drop_tier |
|---|----------|------|---------|---------|---------------------|-----------|
| 81 | `dino_bs_01` | ティラノサウルスさま | 250 | 150 | hero, kingdom_warrior | 5 |
| 82 | `dino_bs_02` | ギガノトサウルスさま | 270 | 160 | kingdom_warrior | 5 |
| 83 | `dino_bs_03` | スピノサウルスさま | 280 | 170 | kingdom_warrior | 5 |
| 84 | `dino_bs_04` | カルカロドントサウルスさま | 260 | 155 | kingdom_warrior | 5 |
| 85 | `dino_bs_05` | アルゼンチノサウルスさま | 320 | 200 | kingdom_warrior | 6 |
| 86 | `dino_bs_06` | パタゴティタンさま | 320 | 200 | kingdom_warrior | 6 |
| 87 | `dino_bs_07` | アンキロサウルスさま | 250 | 150 | hero, kingdom_warrior | 5 |
| 88 | `dino_bs_08` | ステゴサウルス王さま | 250 | 150 | hero, kingdom_warrior | 5 |
| 89 | `dino_bs_09` | トリケラトプス王さま | 260 | 155 | hero, kingdom_warrior | 5 |
| 90 | `dino_bs_10` | パキケファロサウルスさま | 240 | 145 | hero, kingdom_warrior | 5 |
| 91 | `dino_bs_11` | プテラノドン王さま | 230 | 140 | hero, kingdom_warrior | 5 |
| 92 | `dino_bs_12` | ケツァルコアトルス大王 | 270 | 165 | kingdom_warrior | 6 |
| 93 | `dino_bs_13` | モササウルス大王 | 290 | 180 | kingdom_warrior | 6 |
| 94 | `dino_bs_14` | プリオサウルス大王 | 280 | 170 | kingdom_warrior | 6 |
| 95 | `dino_bs_15` | デイノスクスさま | 260 | 155 | kingdom_warrior | 5 |
| 96 | `dino_bs_16` | サルコスクスさま | 260 | 155 | kingdom_warrior | 5 |
| 97 | `dino_bs_17` | テリジノサウルスさま | 250 | 150 | kingdom_warrior | 5 |
| 98 | `dino_bs_18` | ユウオプロケファルスさま | 250 | 150 | kingdom_warrior | 5 |
| 99 | `dino_bs_19` | アンフィコエリアスさま | 340 | 210 | kingdom_warrior | 7 |
| 100 | `dino_bs_20` | 王国最強キョウリュウオウ | 400 | 280 | kingdom_warrior | 8 |

**合計: 100 体 (very_easy 20 + easy 20 + normal 20 + hard 20 + boss 20)。**

---

## 4. AC2-c: DB schema 案 (= 新規 3 table、apply は別 task)

### 4-1. `passport_dino_enemy_master` (= 静的 seed)

```sql
CREATE TABLE passport_dino_enemy_master (
    enemy_id              TEXT PRIMARY KEY,
    name                  TEXT NOT NULL,
    difficulty            TEXT NOT NULL CHECK (difficulty IN ('very_easy','easy','normal','hard','boss')),
    base_hp               INTEGER NOT NULL CHECK (base_hp > 0),
    base_xp               INTEGER NOT NULL CHECK (base_xp >= 0),
    age_tier_eligibility  TEXT[] NOT NULL,
    min_rank_gate         TEXT NOT NULL,
    drop_tier             INTEGER NOT NULL CHECK (drop_tier BETWEEN 1 AND 8),
    drop_asset_key        TEXT,
    requires_subscription BOOLEAN NOT NULL DEFAULT FALSE,
    world_theme_id        INTEGER NOT NULL DEFAULT 3,
    crit_rate             NUMERIC(4,3) NOT NULL DEFAULT 0.00,
    drop_rate             NUMERIC(4,3) NOT NULL DEFAULT 0.00,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_dino_enemy_diff   ON passport_dino_enemy_master(difficulty) WHERE is_active;
CREATE INDEX idx_dino_enemy_active ON passport_dino_enemy_master(is_active);
```

### 4-2. `passport_dino_battle_log` (= 戦闘記録)

```sql
CREATE TABLE passport_dino_battle_log (
    battle_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id            UUID NOT NULL REFERENCES passport_members(member_id),
    enemy_id             TEXT NOT NULL REFERENCES passport_dino_enemy_master(enemy_id),
    started_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at             TIMESTAMPTZ,
    outcome              TEXT CHECK (outcome IN ('win','lose','flee','timeout')),
    turns                INTEGER NOT NULL DEFAULT 0,
    dmg_dealt            INTEGER NOT NULL DEFAULT 0,
    dmg_taken            INTEGER NOT NULL DEFAULT 0,
    xp_awarded           INTEGER NOT NULL DEFAULT 0,
    crit_count           INTEGER NOT NULL DEFAULT 0,
    drop_awarded         BOOLEAN NOT NULL DEFAULT FALSE,
    first_kill_bonus     BOOLEAN NOT NULL DEFAULT FALSE,
    rng_seed             BIGINT,
    related_xp_log_id    UUID,
    related_stamp_log_id UUID
);
CREATE INDEX idx_battle_member  ON passport_dino_battle_log(member_id, started_at DESC);
CREATE INDEX idx_battle_enemy   ON passport_dino_battle_log(enemy_id);
CREATE INDEX idx_battle_outcome ON passport_dino_battle_log(outcome) WHERE outcome IS NOT NULL;
```

### 4-3. `passport_dino_drop_inventory` (= drop 在庫、redeem_reward 入口)

```sql
CREATE TABLE passport_dino_drop_inventory (
    inventory_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id        UUID NOT NULL REFERENCES passport_members(member_id),
    enemy_id         TEXT NOT NULL REFERENCES passport_dino_enemy_master(enemy_id),
    drop_asset_key   TEXT NOT NULL,
    drop_tier        INTEGER NOT NULL,
    acquired_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    related_battle_id UUID REFERENCES passport_dino_battle_log(battle_id),
    redeemed_at      TIMESTAMPTZ,
    related_reward_history_id UUID
);
CREATE INDEX idx_drop_member ON passport_dino_drop_inventory(member_id, acquired_at DESC);
CREATE INDEX idx_drop_pending ON passport_dino_drop_inventory(member_id) WHERE redeemed_at IS NULL;
```

---

## 5. AC2-d: 戦闘 logic + API 仕様

### 5-1. Endpoint inventory (= 新規 4 件)

| method | path | handler stub | 目的 |
|--------|------|--------------|------|
| GET | `/api/teriha-passport/dino-fight/candidates/{member_id}` | `list_candidates()` | 4 ゲート (§2-6) 通過する敵 master を list |
| POST | `/api/teriha-passport/dino-fight/start` | `start_battle()` | `passport_dino_battle_log` row INSERT、`battle_id` 返却 |
| POST | `/api/teriha-passport/dino-fight/resolve` | `resolve_battle()` | 戦闘決算 → `add_xp` + `award_stamp(special)` + drop 抽選 → reward chain 実行 |
| GET | `/api/teriha-passport/dino-fight/history/{member_id}` | `get_history()` | 直近戦闘履歴 (default limit=20) |

### 5-2. 戦闘 turn logic (= resolve_battle 内部)

入力 (= frontend 側で turn 演算した結果を渡す形式、server は再計算+検証):

```json
{
  "battle_id": "<uuid>",
  "member_id": "<uuid>",
  "actions": [
    {"turn": 1, "action": "attack", "rng_dmg": 8},
    {"turn": 2, "action": "defend"},
    {"turn": 3, "action": "attack", "rng_dmg": 12, "crit": true},
    ...
  ],
  "client_outcome": "win"
}
```

サーバ側 turn 演算 (= 再現性のため `rng_seed` を `battle_id` から SHA256 派生で固定):

```
for turn in actions:
    if action == "attack":
        base_dmg = 5 + rank_bonus(member.rank)
        dmg = base_dmg if not crit else int(base_dmg * 1.5)
        enemy_hp -= dmg
    elif action == "defend":
        next_taken *= 0.5
    elif action == "heal":
        member_hp = min(member_hp + 10, max_hp)
    elif action == "taunt":
        enemy_crit_rate += 0.05  # 副作用、後攻 dmg 増

    if enemy_hp <= 0: break

outcome_server = "win" if enemy_hp <= 0 else "lose" if member_hp <= 0 else client_outcome
if outcome_server != client_outcome:
    record discrepancy in battle_log.note, server outcome wins.
```

検証 anti-cheat: `rng_dmg` が `[1, base_dmg + crit_band]` 外 → 戦闘 invalid、xp_awarded=0、`outcome='timeout'` 扱い。

### 5-3. Reward chain (= resolve_battle 後段)

```
1. xp_awarded = final_xp(enemy, member) (+ crit_bonus + first_kill_bonus if applicable)
2. engine.add_xp(member_id, delta_xp=xp_awarded, reason_code='dino_fight_win',
                 source_event_type='dino_battle', source_event_ref=battle_id)
   → rank_after 取得、leveled_up 判定 (engine L204 既存)
3. if difficulty == 'boss':
       engine.award_stamp(member_id, stamp_kind='special',
                          stamp_asset_key=f"dinosaur_kingdom/boss/{enemy_id}",
                          source_event_type='dino_battle', source_event_ref=battle_id)
4. drop 抽選: random() < enemy.drop_rate なら
       INSERT INTO passport_dino_drop_inventory (member_id, enemy_id, drop_asset_key, drop_tier, related_battle_id)
       → drop_awarded=TRUE
5. battle_log row UPDATE: ended_at=now(), outcome, xp_awarded, drop_awarded, related_*_id
6. 返却: { outcome, xp_awarded, rank_before, rank_after, leveled_up, drop }
```

drop redemption は **engine 既存 `redeem_reward()`** (L380) を呼ぶ別 endpoint で実施 (= 本 spec は drop_inventory への投入のみ、交換は既存経路再利用)。

### 5-4. clinic_id guard

全 endpoint で先頭 guard:

```python
member = engine.get_member(member_id, TERIHA_CLINIC_ID)
if member is None:
    raise HTTPException(404, "passport member not found")
```

`enroll_member` (engine L105-108) の既存 guard と整合。

---

## 6. AC3: 実装入口 stub 設計 (= teriha_passport_engine.py への追加)

本 task では **engine class 内に空 stub method group** を追加し、commit のみ行う。各 method は `NotImplementedError("stub: implement in cycle N+1")` を raise。

### 6-1. 追加 method 一覧

| method | signature | 役割 |
|--------|-----------|------|
| `list_dino_candidates` | `(self, *, member_id: str, clinic_id: int = TERIHA_CLINIC_ID) -> list[dict]` | §2-6 の 4 ゲートで filter した敵 master list |
| `start_dino_battle` | `(self, *, member_id: str, enemy_id: str, clinic_id: int = TERIHA_CLINIC_ID) -> dict` | `passport_dino_battle_log` row INSERT、battle_id 返却 |
| `resolve_dino_battle` | `(self, *, battle_id: str, member_id: str, actions: list[dict], client_outcome: str, clinic_id: int = TERIHA_CLINIC_ID) -> dict` | §5-2/5-3 の reward chain 実行 (= add_xp/award_stamp/drop 抽選) |
| `list_dino_battle_history` | `(self, *, member_id: str, limit: int = 20, clinic_id: int = TERIHA_CLINIC_ID) -> list[dict]` | 直近戦闘 list |
| `_score_battle_actions` | `(self, *, enemy: dict, member: dict, actions: list[dict]) -> dict` | 内部、turn 演算 + server outcome 判定 |
| `_award_dino_drop` | `(self, *, member_id: str, enemy: dict, battle_id: str) -> dict | None` | 内部、drop 抽選 + inventory insert |

### 6-2. 配置位置

engine class L502 (file 末尾) に新 section `# dino battle (DD-126 ext, stub)` として追加。
import 追加: `import hashlib` (RNG seed 派生)、`import secrets` (battle_id 生成)。

### 6-3. テスト

本 task では stub 動作のみ確認 = **stub が `NotImplementedError` を確実に raise する単体テスト 1 件** を `backend/tests/test_teriha_passport_engine.py` に追加 (既存 file)。
完全実装の test は別 cycle。

---

## 7. acceptance summary (= AC1〜AC4 へのマップ)

| AC | 本 spec の対応箇所 | deliverable |
|----|-------------------|------------|
| AC1: 既実装 inventory | §1 全節 (engine / router / DB 三層分離) | (本 spec) |
| AC2: 100 体 spec | §2-§5 (5 軸 + 100 件 roster + DB + endpoint) | `docs/cmd004_dinosaur_100enemies_spec.md` |
| AC3: 実装入口 stub | §6 (engine 6 method skeleton + import + 単体テスト 1 件) | `backend/services/teriha_passport_engine.py` 編集 commit |
| AC4: 報告 | (本 spec 外、§8 で記載) | `queue/reports/ashigaru1_cmd004_dinosaur_100enemies_report.yaml` |

## 8. F007 + 本能寺戒め 遵守宣言

- 本 spec 起案中に **`<DENTALBI_REPO_ROOT>/` への破壊的操作なし** (= read-only inventory + ローカル `docs/` 起案のみ)。
- engine への stub 追加 commit 後、**push は陛下御差配仰ぎ** (F007)、ashigaru 単独 push 禁。
- 戦闘 logic の数値根拠 (HP 10/30/60/120/250) は本 spec 内で baseline + 計算式として明示 (= 推測不在、合議で調整可)。
- 100 体名称はカタカナ + 児童向け、医療文脈との混同を避けるため **歯科処置名は使用せず** (= 既存 `assign_mission_from_procedure` 経路と分離)。

---

(EOF)
