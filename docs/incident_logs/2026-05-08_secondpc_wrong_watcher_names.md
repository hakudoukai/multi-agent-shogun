# 2026-05-08 SecondPC inbox_watcher 名前誤起動事件

## 概要

SecondPC で **MainPC の agent 名 (= ashigaru1, ashigaru2, ashigaru3, shogun, karo)** で `inbox_watcher.sh` が複数起動しており、本来必要な **maeda + ashigaru5/6/7 の watcher が不在**だった。これにより 22:41 信長 → 前田殿 dispatch (= 家康 v3 FAIL 修正の SecondPC 委譲、3 task) が **CLI process 受領されず**、22:50 催促も同様に届かず、SecondPC 全 4 pane (= maeda + ashigaru5/6/7) が **約 7 時間 idle 化**した。

## 発生時刻 + 検知経緯

- **発生**: 不正 watcher 起動は 19:29 / 21:36 (= 過去 shutsujin or 手動起動時、推定)
- **影響開始**: 22:41:30 maeda inbox 配達分が CLI process 未受領
- **検知**: 23:00 信長殿が「足軽567見て」御命令で SecondPC 視察、`ps -ef | grep inbox_watcher` で MainPC 名 watcher を発見
- **真因確定**: 23:02 watcher 起動 process の引数 (= agent name) が SecondPC 配置 SSoT (= pane_registry.yaml + §18.1) と不整合と判明

## 影響範囲

| 項目 | 影響 |
|------|------|
| **maeda (前田殿)** | 22:41 信長 dispatch 受領せず、ashigaru5/6/7 への転送未実施 |
| **ashigaru5/6/7** | 7 時間 idle、家康 v3 FAIL 修正 task 未着手 |
| **MainPC quota 配慮戦略** | 想定通り進まず、戦略的タイムロス |
| **データ損失** | なし (= inbox.yaml には書込済、CLI 未読のみ) |
| **復旧時間** | 約 5 分 (= 不正 watcher kill + 正 watcher 起動 + 直送) |

## 5 Why 分析

| Why | 質問 | 回答 |
|-----|------|------|
| 1 | なぜ MainPC 名 watcher が SecondPC で起動した? | 起動スクリプトが PC 識別なしで agent name を引数指定 |
| 2 | なぜ起動スクリプトに PC 識別が無い? | `shim/hakudokai/hakudokai_start_watchers.sh` が固定 agent name を使い、`config/settings_local.yaml` の `pc_mapping` を未参照 |
| 3 | なぜ `inbox_watcher.sh` 自身がチェックしない? | 引数で渡された agent を無条件信用、`pane_registry.yaml` SSoT 未照合 |
| 4 | なぜ pane_registry SSoT 照合が無い? | §18.1 + `pane_registry.yaml` は SSoT 制定済だが、watcher 起動側のチェックメカニズム未整備 |
| **5 (真因)** | **なぜ watcher 起動チェック未整備?** | **Phase 1 (2026-05-07) SecondPC 拡張時に watcher 起動側の PC guard 実装が漏れた。元設計が 1-PC 想定、SecondPC 拡張時に inbox_watcher.sh + start_watchers.sh の PC 別分岐を追加する責務が未定義** |

## 復旧手順 (= 即時実施分)

```bash
# Step 1: 不正 watcher PID 取得 + kill
WRONG_AGENTS="ashigaru1 ashigaru2 ashigaru3 shogun karo gunshi"
for a in $WRONG_AGENTS; do
  pids=$(ps -ef | grep -E "inbox_watcher\.sh ${a} " | grep -v grep | awk '{print $2}')
  for pid in $pids; do
    kill -TERM $pid 2>/dev/null
  done
done

# Step 2: 正しい watcher (= maeda + ashigaru5/6/7) 起動
for spec in "maeda multiagent:0.0 claude" "ashigaru5 multiagent:0.1 claude" "ashigaru6 multiagent:0.2 claude" "ashigaru7 multiagent:0.3 claude"; do
  agent=$(echo $spec | awk '{print $1}')
  pane=$(echo $spec | awk '{print $2}')
  cli=$(echo $spec | awk '{print $3}')
  nohup bash scripts/inbox_watcher.sh "$agent" "$pane" "$cli" > "/tmp/inbox_watcher_${agent}.log" 2>&1 &
done

# Step 3: 信長 → ashigaru5/6/7 直送 (= F002 緩和、家老 bypass で task 発令)
# ただし pc_handshake 2000 字 truncate 問題判明 → task YAML を SecondPC に scp 配置に切替

# Step 4: task YAML 完全版を MainPC で生成 → SecondPC へ scp 配置
# Step 5: 短信『YAML 読め』を ashigaru5/6/7 へ inbox_write
```

## 再発防止策 (= 3 層)

### L1: skill (= AI 判断補助)
- **`skills/watcher-pc-name-verify/SKILL.md`** 新設
- inbox_watcher.sh 起動時の agent×PC 妥当性検証手順を AI に指示
- 既存 `skills/pane-identity-verify/` (= pane 番号誤認防止) とは別観点

### L2: check スクリプト (= 機械的検証)
- **`scripts/checks/watcher_pc_name.sh`** 新設
- 全 inbox_watcher.sh process を ps で取得 → agent name 抽出 → settings_local.yaml + pane_registry.yaml で valid agent set 抽出 → 不一致を stderr 警告
- exit 0/1/2、timeout 5 秒、絶対 block しない (= advisory only)

### L3: 構造的 (= 別 cmd で起案、本記録範囲外)
- `shim/hakudokai/hakudokai_start_watchers.sh` に PC guard 実装
- `config/settings_local.yaml` の `pc_mapping` から自 PC を識別、許可 agent set のみ起動
- `inbox_watcher.sh` 自身が pane_registry SSoT を照合する mechanism 追加

## 教訓

1. **複数 PC 構成では watcher 起動側にも PC guard が必須**: agent name 引数を無条件信用してはならぬ
2. **SSoT は照合機構と一体で運用すべし**: pane_registry.yaml + §18.1 を制定しても、起動側が照合しなければ防御は効かぬ
3. **dispatch 失敗の検知は配達確認だけでは不十分**: pc_handshake ack ≠ CLI 受領、pane 内 process の活性確認まで必要
4. **pc_handshake 2000 字制限の存在**: 長文 task は YAML 直送が確実 (= scp + 短信通知)

## 関連資産

| 資産 | 役割 |
|------|------|
| [skills/watcher-pc-name-verify/SKILL.md](../../skills/watcher-pc-name-verify/SKILL.md) | L1 skill |
| [scripts/checks/watcher_pc_name.sh](../../scripts/checks/watcher_pc_name.sh) | L2 check |
| [skills/pane-identity-verify/SKILL.md](../../skills/pane-identity-verify/SKILL.md) | 兄弟 skill (= pane 番号誤認防止) |
| [docs/incident_logs/2026-05-07_pane_misidentification.md](2026-05-07_pane_misidentification.md) | 第 1 号インシデント (= pane 番号誤認) |
| [docs/incident_logs/2026-05-08_pane_mapping_drift.md](2026-05-08_pane_mapping_drift.md) | 第 2 号インシデント (= mapping drift) |
| `queue/pane_registry.yaml` | machine-readable SSoT |
| CLAUDE.md §18.1 | human-readable SSoT |
| CLAUDE.md §19 | Post-Incident Lessons Capture mandate |

## CLAUDE.md 追記候補 (= 別途承認後 optional)

§18.x として「watcher 起動時の PC × agent 妥当性検証ルール」を追加候補。実装は L3 構造修正と一体運用すべし。
