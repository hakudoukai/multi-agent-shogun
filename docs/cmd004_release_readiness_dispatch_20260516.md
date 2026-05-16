# cmd_004 二大戦線 リリース可否評価 + 出陣計画書

- directive_id: 0fa1c9e3-fe58-4f09-82f5-c3575424e530
- operation_id: zero-wait-dino-app
- 作成: 2026-05-16 (shogun-main / 信長 orchestrator)
- mission: 会計待ち時間ゼロ作戦 + 小児恐竜王国アプリを早期リリースへ戻す
- 評価原則: 機械 evidence のみ、本能寺戒め遵守、外部 repo 改変は安全範囲外につき出陣 chain 経由

---

## 0. 結論 (TL;DR)

両戦線とも **コード退行なし**。停滞の真因は **オーケストレーション層凍結**であり、
spec 完了済の deferred 実装 cycle が 2026-05-12 以降一度も配信されていない。

| 戦線 | spec | 実装 | テスト | リリース blocker |
|------|------|------|--------|------------------|
| 会計待ちゼロ (kartetto PDF v0.2) | ✅ 完遂 (shogun_verified) | 🟡 外部 repo に反映済 (parser_full_integration) | 🟢 9 passed (dashboard L228) | E2E 結合検証 + 黒田 audit 再走 未配信 |
| 小児恐竜王国 (敵100体) | ✅ 完遂 (shogun_verified) | 🔴 spec+stub のみ、戦闘 engine / 100体 seed / RLS / 結合 test 全未着手 | 🔴 未 | 実装 cycle 自体が未配信 |

## 1. 機械 evidence (checked)

- `docs/cmd004_kartetto_pdf_v0_2_spec.md` — 会計戦線 spec。実装連動先=外部 `<DENTALBI_REPO_ROOT>/backend/etl/quartetto_pdf_parser_v2.py`。
- `docs/cmd004_dinosaur_100enemies_spec.md` L6 — 明記: 「範囲: spec + 実装入口 stub のみ。完全実装 (戦闘エンジン中身 / 100 体 seed JSON / RLS / 結合テスト) は別 cycle 配信」。
- `git log --oneline -15` — 直近 commit は全て cmd_014 / cmd_015 / cmd_020 (infra + gunshi audit)。cmd_004 進捗 commit は 2026-05-12 (`0e98d1c` / `60b02a6`) 以降 4 日間ゼロ。
- `tmux capture-pane -t multiagent:agents.0` — Karo pane が Claude Code auto-mode 権限ダイアログ (1=default / 2=enable / 3=exit) で停止。Shogun→Karo→Ashigaru 配信 chain が凍結。
- SessionStart hook WARNING #1/#2 — agent_id=shogun-main に対応する inbox file 不在 (正は `queue/inbox/shogun.yaml`)、inbox_watcher process 未起動。orchestrator persona の message routing が断。
- `android/` 配下 = `com.shogun.android` (multi-agent 統制アプリ)。恐竜王国アプリ本体は外部 dentalbi PWA/backend feature であり本 repo は spec/統制のみ保持。

## 2. リリース blocker (優先順位付き)

### B1 [高] オーケストレーション層凍結 — 配信不能の根本
- Karo session が CLI 権限ダイアログで停止 → 全 deferred cycle 配信不能。
- agent_id=shogun-main の inbox/watcher 不整合 → orchestrator の指令 routing 断。
- **これは infra coherence 問題。tmux 操作 / watcher 再起動 / persona 切替の自律実行は F002/D006 risk のため範囲外。大将軍判断を要す。**

### B2 [中] 小児恐竜王国 実装 cycle 未配信
- spec は L4 完備。次に必要なのは: (a) 100体 seed JSON 全量、(b) 戦闘 engine RNG 実装、(c) `passport_dino_battle_log` DDL apply、(d) RLS (保護者同意 gate 完了後)、(e) 結合テスト。
- 各々 ashigaru 配分可能な独立単位。出陣 chain 復旧次第 batch 配信。

### B3 [中] 会計待ちゼロ E2E 検証未配信
- parser_full_integration は外部 repo 反映済、unit 9 passed。残:「会計完了→カンバン billing 自動移動」E2E (家老担当領域) + 黒田 deliverable audit 再走。

## 3. 出陣計画 (dispatch plan) — 出陣 chain 復旧後即時実行

| # | task | 担当 | bloom | ETA | 依存 |
|---|------|------|-------|-----|------|
| D1 | 恐竜王国: 100体 seed JSON 全量生成 (spec §列挙準拠) | ashigaru1 | L4 | 60-90min | B1解消 |
| D2 | 恐竜王国: 戦闘 engine 本体実装 + stub 解消 | ashigaru担当 | L4 | 90min | D1 |
| D3 | 恐竜王国: `passport_dino_battle_log` DDL 起草→家老 batch apply | ashigaru+karo | L3 | 30min | D1 |
| D4 | 会計: 会計→カンバン billing E2E 結合検証 | 家老 (E2E 専権) | L3 | 45min | B1解消 |
| D5 | 両戦線: 黒田 deliverable audit 再走 + privacy gate | gunshi/kuroda | L3 | 30min | D2,D4 |

## 4. 本評価で実施した安全アクション

- 本評価書 (tracked file) 作成 = evidence artifact。
- 出陣指令を `queue/inbox/karo.yaml` へ `inbox_write.sh` で投函 (flock 保証、Karo pane 凍結中でも persist、復旧時自動処理)。
- 外部 dentalbi repo (`<DENTALBI_REPO_ROOT>/`) は本 project tree 外 → D002/Tier2 につき自律改変せず、出陣 chain 経由に限定。

## 5. next_actions (大将軍へ)

1. **B1 解消が全ての前提**: Karo session の CLI ダイアログ解除 + agent_id=shogun-main の inbox/watcher 不整合是正 (infra layer、人手 or 大将軍経由 SC 復旧 trigger)。
2. B1 解消後、§3 D1-D5 を Karo 経由で batch 配信 (指令は karo.yaml に投函済)。
3. 恐竜王国は実装 cycle が丸ごと未配信のため最長 path。D1→D2 を最優先化推奨。
