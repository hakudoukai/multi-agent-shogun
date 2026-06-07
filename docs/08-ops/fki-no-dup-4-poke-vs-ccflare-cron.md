# FKI-NO-DUP 第4条 判定書 — fukuincho_desktop_poke (新規解) vs ccflare headless OAuth cron (既存解)

> 起草: 軍師 (gunshi-third) / 監査: Codex 6軸 + Gemini 8観点 dual / base_commit: 206ffe2
> parent_cmd: cmd_thirdpc_p1_fukuincho_desktop_poke_stage1_diag_plus_stage3_engine_001
> task: subtask_thirdpc_p1_fki_no_dup_4_plus_stage3_design_dual_audit_001
> 規律: DD-157 役職名のみ / F002 報告経路 / V5 (task_tracker 8012f18c) 保護 / FKI-AUDIT-GREEN-TRUTH-01

本書は理事長令「fukuincho_desktop_poke を最優先で先に作る」(副院長御差配 c690dc28 seq=36217)
に付随する **FKI-NO-DUP 第4条 判定** を、speculation 禁・実態調査の上で確定する。

## 0. 出典 (実態 grounding — speculation 排除)

| 出典 | 内容 |
|------|------|
| pc_handshake `d474d2f9` (commander→third, seq=35964) | poke script 全文 288 行 verbatim + 段階1-4 DoD + --diagnose 認可範囲 |
| pc_handshake `c690dc28` (fukuincho→commander, seq=36217) | 副院長御差配: 「ccflare headless OAuth cron も同系の解。統合 or 二択を判定 (二重実装回避)。speculation 禁・実態調査の上判定」 |
| pc_handshake `5777533f` (commander→third, seq=36202) | 第4条 (FKI-NO-DUP) 段階1 設計時判定 指示 + 段階 DoD |
| memory `hermes-ccflare-llm-resolution` | ccflare = per-PC LLM gateway (third=localhost:8082)。`provider: anthropic` / `base_url` で Claude API path を維持。OAuth 実注入は ccflare 側 |
| docs/infra/ccflare-account-topology.md (正本, 2026-05-27 実機 verify) | ccflare は `ANTHROPIC_BASE_URL=http://localhost:80XX` の認証 gateway。OAuth credential 注入層 |

## 1. 既存解の機能 surface — ccflare headless Claude Code OAuth cron

- **層**: 認証 / トークン (API gateway auth keepalive)。
- **機構**: ccflare (third = `localhost:8082`, account-1/priority0/active) が OAuth credential を実注入し、
  `ANTHROPIC_BASE_URL` 経由で agent/CLI の Claude API 経路を維持。headless OAuth cron は OAuth token を
  定期 (1時間毎) に refresh し、API 経路の認証断を防ぐ。
- **駆動対象**: API / CLI session の **認証状態** (token 有効性)。
- **駆動しないもの (実態確認済)**:
  - claude.ai Desktop (Electron) chat window への文字入力。
  - inbox staleness / SLA 超過の業務検知。
  - 着火 (poke) の ack 回収・再送。
- **根拠**: ccflare は `ANTHROPIC_BASE_URL` の HTTP gateway であり、UI surface を持たない
  (docs/infra/ccflare-account-topology.md)。認証を維持しても副院長エージェントが inbox を処理する
  **会話 turn は進まない**。

## 2. 新規解の機能 surface — fukuincho_desktop_poke.py (段階1-4)

- **層**: GUI / Desktop 操作 (pywinauto, Windows Python 3.13 専用)。
- **機構**: cron 検知 (detect_stale / SLA 超過 / 新着 urgent) → 副院長 claude.ai Desktop (Electron) window を
  pywinauto で特定 → 入力欄へ「確認して」type + Enter → 会話 turn を進行。
  - 段階1 = `--diagnose` で window title / 入力欄 auto_id を特定し実 row 提出 (偵察のみ、送信なし)。
  - 段階2 = 入力欄へ type + Enter で実チャット進行 (screenshot + 実応答 row)。
  - 段階3 = cron / SLA 連動 + 着火 ack リトライ再送エンジン (task ae8083dd): 反応返るまで再送し
    黄取りこぼし克服 + 短時間多重 poke 抑制 + 応答中 skip 誤爆防止。
  - 段階4 = 三者監査緑 + 自動 poke 実走ログ → 副院長照合 → 恒久運用。
- **駆動対象**: 副院長 claude.ai Desktop chat session の **turn 進行** (= 工程3, 唯一の欠落ピース)。
  現状は理事長手動入力依存。
- **絶対不変条件**: WSL Python 非介在維持 / V5 (8012f18c) 保護継続 (V5 は WSL file render で Windows
  デスクトップ窓を占有せず、Windows 側 `Desktop().windows()` 列挙は V5 capture に無干渉 — d474d2f9 で確認済)。
- **別物注記**: enter_restart (ee4d6ce4) は tmux 間 Enter であり別機構。混同禁。

## 3. FKI-NO-DUP 第4条 重複判定 — 機能 surface 分解

| 機能 surface | ccflare OAuth cron | poke 方式 | 重複? |
|--------------|:------------------:|:---------:|:-----:|
| (1) 1時間毎 cron 起動 (スケジューラ) | ○ | ○ (段階3) | **▲ 表層のみ** |
| (2) Claude 認証 / トークン維持 (API path) | ○ | ✕ | 非重複 |
| (3) inbox staleness / SLA 業務検知 | ✕ | ○ (fukuincho_watch 連携) | 非重複 |
| (4) claude.ai Desktop chat への文字入力駆動 (工程3) | ✕ | ○ (**唯一**) | 非重複 |
| (5) 着火 ack 回収・再送 (段階3) | ✕ | ○ | 非重複 |

- 重複範囲 = **(1) cron スケジューラ層のみ**。アクチュエータ層 ((2) 認証維持 vs (4) 会話駆動) は
  完全に **異層・非重複**。
- 「同系の解」(副院長御差配) は cron トリガという **表層共通** に由来する。真の機能 surface
  (= 工程3: 副院長 claude.ai Desktop 会話駆動) は **poke が唯一の解**。ccflare OAuth cron は工程3を
  一切 cover しない (認証を維持しても副院長が inbox を処理する turn は進まない)。

### 判定

> **二重実装ではない (NOT a duplicate)。両者は補完関係 (complementary)。**
> 削除対象なし。ただし poke 段階3 が **独立した第2 cron poller を新設すると (1) で二重実装が発生する**
> ため、これを回避することが FKI-NO-DUP 上の唯一の要件。

## 4. 採用案 — 検知層統合 + アクチュエータ並存 (統合案)

副院長御差配の選択肢「統合 or 二択」のうち **統合 (検知層) + 補完並存** を採用する。

1. **検知 (detection)**: 既存 `fukuincho_watch` / detect_stale の **単一 cron** に統合する。
   poke 段階3 は ★独立した第2 cron poller を新設せず★、fukuincho_watch 検知結果を購読する形で連動する。
   — これが FKI-NO-DUP 上の唯一の重複回避要件 ((1) スケジューラ層の二重化を防ぐ)。
2. **認証 keepalive**: ccflare headless OAuth cron は **直交層** ゆえ現状維持・不接触・**削除不要**。
3. **駆動 (actuation)**: poke 方式 (`fukuincho_desktop_poke.py`) を工程3 の **正解として採用**。
4. **削除責務**: なし (両者非重複)。新設 cron poller を作らない限り二重実装は発生しない。

### root cause matrix

| 項目 | 内容 |
|------|------|
| 解消する failure mode | 「副院長 claude.ai Desktop chat が理事長手動入力なしに turn を進められない」(工程3 欠落) → poke が解消 |
| 残す failure mode | なし。ccflare OAuth cron は別 failure domain (認証断) で、現状維持により対処済 |
| 副院長御差配 (c690dc28) 趣旨整合 | 「統合 or 二択を判定 (二重実装回避)」→ 本判定は「検知層統合 + 補完並存」で回避達成。speculation 禁順守 (実態 = handshake script 288 行 + canonical doc + memory で grounding) |
| DD-157 / F002 / V5 整合 | 役職名のみ使用 / 報告は karo-third 経由 / V5 (8012f18c) 無干渉を d474d2f9 で確認済 |

## 5. 段階1 提出 row 併記文 (karo-third → 副院長照合 routing 用)

> 【FKI-NO-DUP 第4条 軍師 dual 判定】ccflare headless OAuth cron (既存) と fukuincho_desktop_poke
> (新規) は ★非重複・補完関係★。重複は cron トリガ表層のみ、真の機能 surface (工程3 = 副院長
> claude.ai Desktop 会話駆動) は poke が唯一解。ccflare OAuth cron は認証維持層で工程3を cover せず。
> 採用案 = 検知層を既存 fukuincho_watch に統合 / poke 段階3 は新規 cron poller を新設せず
> fukuincho_watch 検知連動 (重複回避の唯一要件) / ccflare OAuth cron は直交層ゆえ現状維持・削除不要。
> 軍師 Codex 6軸 + Gemini 8観点 dual audit、base_commit=206ffe2。

## 6. 完了条件

- (A) 本判定書 + 採用案 + 段階1 併記文 → Codex + Gemini dual GREEN。
- 監査 row を Supabase codex_audit_results / gemini_audit_results へ格納 (overall_signal / issues_count_a-c
  / triaged_issues jsonb)。
- karo-third inbox 経由で全量 relay (F002)。1 観点でも RED → status: blocked + 即家老 escalate。
