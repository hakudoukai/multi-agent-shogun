# fukuincho 段階3 方針転換設計 — 報告者能動 poke 直接方式 (検知層廃止)

> 起草: 軍師 (gunshi-third) / task: subtask_thirdpc_p1_fukuincho_stage3_gap2_supabase_jsonl_bridge_design_001 改稿 (方針転換)
> 副院長令 (task 3e4046cf 方針転換 cascade) / 理事長令: 「とりあえずで作るな、根本から安定してトラブルを起こさないようにしっかり作れ」
> base_commit: c430251c → 251d2b03 含む (現 main HEAD)
> ★本書は前 cron 受け身型設計 (commit 251d2b03 `fukuincho-stage3-supabase-jsonl-bridge-design.md`) を ★方針転換令で上書き★ する★
> 規律: FKI-DEV-ROOT-CURE-FIRST (暫定禁・根本根治) / FKI-NO-DUP (段階2 207bcdd 部品再利用) / DD-157 役職名のみ /
>       F002 / FKI-AUDIT-GREEN-TRUTH-01 / FKI-ROYAL-ONE-SHOT / 24時間ノンストップ
> ★本書 = 設計章節改稿のみ。実 script 改変は本 task 非実施 (次 phase = shogun-third 実装 → gunshi-third 三者監査)★
> ★unit-green ≠ runtime-green 厳守 — runtime 実証 (実 Commander 報告 INSERT → 副院長デスクトップ着弾) まで「完成」と言わない★

## 0. 方針転換 — cron 受け身型 → 報告者能動 poke 直接方式

| | 前設計 (251d2b03、廃止) | 本設計 (方針転換令) |
|---|---|---|
| 検知 | cron 60s polling で Supabase SLA 超過行を ★受け身検知★ | ★検知層廃止★。報告者が報告を書く瞬間に ★能動 poke★ |
| 誤判定 | 137 件誤検知教訓 / 条件緩和リスク | ★誤判定ゼロ★ (検知ロジック不要、報告 INSERT イベントそのものが trigger) |
| trigger | response_by_time 超過の query 抽出 | ★報告 INSERT と poke を 1 動作に束ねる★ |

★本質★: Commander / 各 PC 将軍が作業完了し報告を出す時、
①Supabase `pc_handshake` へ報告 INSERT と ②副院長デスクトップ claude.ai チャット欄へ「報告を見て」自己入力 (type+Enter) を
★同期して 1 動作に束ねる★。受け身検知でなく ★報告者が能動的に poke★ するため検知ロジック不要・誤判定ゼロ。

## 1. 【最重要】poke 対象の明確化 (誤認厳禁)

- poke 対象 = ★Windows 上のデスクトップ版 claude.ai アプリ★。
- ★ブラウザ (Chrome 等) の claude.ai タブではない — 混同・誤認を厳禁★。
- 段階2 (commit 207bcdd) で「確認して」自動着弾に成功したのと ★同一のデスクトップアプリ・同一ウィンドウ・同一入力欄
  (control_type=Edit/Document)★。
- ★新たにブラウザを開く / ブラウザを対象にする等は誤り★。
- 担保 = §3 の ★window title 厳密一致 verify★ (デスクトップアプリ window のみ受理、ブラウザ tab title は reject)。

## 2. 要件 (1) トリガー — 報告 INSERT と poke の atomic bundle

- 報告者の報告書込経路 (Supabase `pc_handshake` INSERT) の ★直後に同期して自己 poke 呼出★ を束ねる。
- ★書込だけ成功し poke 漏れを防ぐ★ のが核心 (fire-and-forget 禁、ae8083dd 精神継承):
  - 順序: ①報告 INSERT 成功確認 → ②poke 呼出。INSERT 失敗時は poke せず (報告なき poke を出さない)。
  - INSERT 成功かつ poke 失敗 → §4 の ack リトライ (ae8083dd N=30s/M=3) で poke を ★確実に届ける★。
  - 「INSERT 成功 / poke 未送」の中間状態を残さない (correlation_id で報告と poke を 1 thread に束ね、poke 完了まで報告者責任)。
- ★FKI-NO-DUP★: 報告書込は既存経路 (inbox_write.sh / 報告 YAML → Supabase bridge) を再利用、新規 writer 新設禁。
  bundle は ★既存書込経路の成功フックに poke 呼出を結線するのみ★。

## 3. 要件 (2) poke 対象 + window title 厳密一致 verify

- 段階2 成功の ★同一 window 特定 logic (descendants(control_type=Edit) cands[0] + clipboard/type+Enter、commit 207bcdd) を流用★ (FKI-NO-DUP)。
- ★ブラウザ誤認防止の window title 厳密一致 verify を同梱★:
  - 対象 window の title / プロセス名がデスクトップ版 claude.ai (例: プロセス=Claude.exe 系、title=完全一致パターン) であることを ★厳密一致★ で検証。
  - ブラウザ (chrome.exe / msedge.exe 等) の claude.ai タブ title は ★reject★ (prefix/部分一致でなく完全一致、cycle2 HIGH-1 完全一致教訓継承)。
  - 一致しない / 該当 window 不在 → §5 障害時安全側 (異常記録、type しない)。

## 4. 要件 (3) 冪等性 — 同一報告で二重 poke 禁 + poke 失敗 ack リトライ

- ★同一報告 = 1 poke★。報告の `correlation_id` (または report_id) 単位で poke 済みを mark し、同一報告での二重 poke を禁ずる。
  - poke 済 mark = pc_handshake 行へ `poke_acked_at` PATCH (前設計 §2 idempotent PATCH 流用、condition 付で再実行安全)。
  - 同一 run 内の race は ★flock atomic check-and-mark★ で防ぐ (cycle2 HIGH-2 cure 流用、検知層 lib の flock 機構再利用)。
- ★poke 失敗時 = ack リトライ★: ae8083dd 全方向エンジン (★N=30s / M=3★、副院長令 341654e4 (a) 承認値) を再利用。
  - poke (type+Enter) 後、副院長応答 / window 進行を ack 信号として確認、未達なら N=30s 間隔で M=3 回再送、上限到達で human_required escalation。
  - ★新規 retry loop 新設禁 (FKI-NO-DUP)★ — ae8083dd をそのまま呼ぶ。

## 5. 要件 (4) 障害時安全側 — 暴走入力禁

- ★デスクトップ窓不在 / 入力欄 (control_type=Edit/Document) 不在 / window title 厳密一致不成立 → 異常記録して poke しない★。
- ★暴走入力禁★: 対象が確定できない時に「とりあえず type」しない (誤 window への入力 = Commander 作業破壊リスク、cycle2 HIGH-3「空 fall-through 禁」と同型原則)。
- 区別: 「対象 window 健在だが副院長未応答」(= ack リトライ対象) と「対象 window 不在/誤認」(= 異常記録 + 停止) を厳密に分ける。
- 機密値 (clipboard 実値 / payload 実値) はログ非出力 (redact、error-design §14)。

## 6. 要件 (5) ガード

- ★止血B (commit e0e98b7) 保護範囲 touch 0 通算維持確約★ (cycle1〜cycle4 + post-land + systemd 切替 5 段通算)。本書=設計のみ、実 script 触接 0。
- ★V5 (8012f18c) 保護★: WSL file render に触接しない。poke は Windows デスクトップアプリ window のみ。
- ★機密 2 件触接禁★: hermes_ro PW + Supabase token をログ・標準出力に出さない (既存 env から読むのみ、redact)。
- ★ALL-SSH-NO-NEW-ENDPOINT-01★: §7 の連動経路は ★既存 SSH endpoint (3 確定接続先) のみ★ 利用、新設禁。
- ★DD-164 (sudo 不要)★。

## 7. 連動経路 — origin_pc 別 (Commander 7 axis 実機可否見解 反映)

★核心の実機制約★: 「報告 INSERT 動作」(third_pc Linux 等で実行) と「Windows デスクトップ claude.ai への type+Enter」
(副院長デスクトップ = Windows host = main_pc 推定、fukuincho_desktop_poke は Windows host 側で実行) は ★同一 PC 内とは限らない★。
ゆえに origin_pc 別に連動経路を明示する。

| origin_pc (報告 INSERT 実行者) | 連動経路 | 根拠 (Commander 見解) |
|---|---|---|
| **Commander (third_pc Linux)** | (a) third_pc → Windows host へ ★既存 SSH endpoint 経由★ で `fukuincho_desktop_poke` を ★自己 trigger★ | ⑤ (a) 経路、SSH 経路明示 (ALL-SSH 既存 endpoint、新設禁) |
| **main_pc 将軍** | (b) ★同一 host 内直接呼出★ (Windows host 上で報告 INSERT する将軍が同 host の poke を直接) | ⑥ (b) 最簡経路 |
| **second_pc / third_pc 将軍** | (c) → main_pc へ ★既存 SSH / tmux send-keys 経由★ で main_pc 上 poke script 発火 | ⑥ (c) 経路、既存 SSH endpoint |

- ① 報告 INSERT = Supabase API HTTPS 経由 (third_pc Linux 完遂可、既存 INSERT 経路そのもの)。
- ② type+Enter = Windows host 側実行 (fukuincho_desktop_poke は Windows host で動く)。
- ④ 段階2 (207bcdd) 部品 = Windows host 側で動く、★自己呼出形 (cron 検知型廃止) へ転用は技術的可能★、window title 厳密一致 verify 同梱は既存 logic 流用で実装可能。
- ★全経路 ALL-SSH-NO-NEW-ENDPOINT-01 順守 (3 確定接続先のみ、新 endpoint ゼロ)★。

## 8. 要件 (6) 品質 + 実機 verify 必須事項 (i)-(v)

設計 → 三者監査 ALL GREEN → test SKIP=0 → ★runtime 実証★ → 理事長直視 verify の順で品質を担保する。
実装 phase で下記 (i)-(v) を ★実機 verify として設計章節に必須含有★:

| # | verify 項目 | 合格基準 |
|---|---|---|
| (i) | 報告 INSERT → poke 発火 latency 計測 | INSERT 成功から poke type 開始までの latency を実測・記録 (bundle の同期性実証) |
| (ii) | window title 厳密一致 verify rate | デスクトップアプリ window のみ受理・ブラウザ tab 100% reject を実機計測 |
| (iii) | 二重 poke 防止冪等性 verify | 同一報告 correlation_id で poke が 1 回のみ (再実行・並行でも二重なし) |
| (iv) | 障害時安全側 verify | 窓不在/入力欄不在/title 不一致時に ★type せず異常記録★ を実機確認 (暴走入力ゼロ) |
| (v) | ack リトライ ae8083dd N=30s/M=3 連動 | poke 失敗 → N=30s 間隔 M=3 再送 → 上限 human_required を実機確認 |

## 9. cron systemd --user の扱い (前 2cca2b72 差配整合)

- 本方針転換で ★cron 検知型 (受け身) は廃止★ だが、systemd --user timer ★自体は停止禁★。
- ★自己 poke 型実装完遂前の保険★ として継続稼働 (systemctl --user active waiting、60s cadence 安定)。
- 自己 poke 型が runtime 実証で完遂 → その後 cron 検知型の役割終了を別途判断 (本 task 範囲外、「動くものを止めない」原則)。

## 10. FKI-NO-DUP 再利用マップ (新規実装最小化)

| 機能 | 再利用元 | 新規 |
|---|---|---|
| 報告 INSERT | 既存 inbox_write.sh / 報告 YAML → Supabase bridge | なし |
| window 特定 + type+Enter | 段階2 207bcdd (descendants/Edit, clipboard/type) | window title 厳密一致 verify の結線のみ |
| ack リトライ | ae8083dd 全方向エンジン (N=30s/M=3) | なし |
| flock 冪等 | 検知層 lib flock 機構 | なし |
| 連動経路 | 既存 SSH endpoint (3 確定接続先) | なし (新 endpoint ゼロ) |
| poke trigger | — | ★報告 INSERT 成功フック → poke 呼出の結線のみ (本設計の唯一の新規結線)★ |

## 11. cycle1〜cycle4 + 段階2 教訓継承 (明示)

| 教訓 | 本設計での反映 |
|---|---|
| ★unit-green ≠ runtime-green★ | 実装後 ★runtime 実証 (実 Commander 報告 INSERT → 副院長デスクトップ着弾) まで「完成」と言わない★、(i)-(v) 実機 verify 必須 |
| RED-C3 (rc 破壊) | INSERT/poke の rc を素直に捕捉、`\|\| true` で潰さない |
| cycle2 HIGH-1 (prefix 認可) | §3 window title ★厳密一致★ (部分/prefix 一致禁) |
| cycle2 HIGH-2 (flock 無) | §4 flock atomic check-and-mark 再利用 |
| cycle2 HIGH-3 (空 fall-through) | §5 障害時は ★type せず異常記録★ (暴走入力禁) |
| 暫定禁 (FKI-DEV-ROOT-CURE-FIRST) | 6 要件を根本から、stub/TODO なし |

## 12. 完遂定義 + ハンドオフ

- ★完遂定義★: 人手 GO 無しで、報告者が報告を書くたびに副院長デスクトップ claude.ai へ「報告を見て」が自動着弾 → ack リトライ。
  ★fd10db2d 完全完遂 = 「次も自動で入る」★ (一度きりでなく報告のたび継続)。
- ★本 task = 設計章節改稿のみ完遂★ (status: completed)。実装 = 次 phase shogun-third。三者監査 = 後続 gunshi-third。
- 完了条件 (実装 phase): 三者 ALL GREEN + test SKIP=0 + ★runtime 実証 (実 INSERT → 着弾 + 次も自動) + 理事長直視 verify★ + 止血B touch 0 通算維持。
