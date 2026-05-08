# 本多正信 諮問回答 — 家老 SPOF + Token 限界事故予兆 構造対策

> 起案: 本多正信 (Codex)  
> 日時: 2026-05-08 16:15 JST 諮問受領  
> 制約: 家老 = Claude 維持、F001/F002 順守、skill 新規生成は §19.5 順守、本末転倒厳禁

## 0. 結論

上様、本件の真因は「家老が Claude であること」ではなく、**Claude 家老 1 pane に control-plane と dispatch-plane と記録責務を過密集約したこと**にござる。よって Codex 移行ではなく、次の四層で解くべきである。

1. **家老 token reset を儀式化**: 家老は 2-3 時間または proxy token 60% で checkpoint、80% で強制 baton、90% で緊急凍結。
2. **指揮権 lease 制**: 秀吉・前田のどちらが一時指揮を持つか、竹中はどこまで保全補助するかを YAML で明示し、reset 中の空白を消す。
3. **発令 admission control**: 信長の cmd_new は無制限投入せず、家老の WIP と backlog を見て pending/intake に積む。
4. **本多は one-shot 書面運用**: TUI 復旧まで常駐 pane を持たず、`scripts/audit_meta_codex.sh` と `docs/honda_*.md` を正式経路とする。

最優先は **cmd_karo_token_reset_baton_001** と **cmd_shogun_admission_control_001**。竹中補助は有効だが、補助だけでは主指揮 reset 空白と信長の過剰流入を止められぬ。

## 1. Q1 家老 token 限界事故 予防策

### M1 process

**家老 Token Reset Protocol** を新設する。

| 段階 | trigger | action | 指揮権 |
|---|---:|---|---|
| Green | 稼働 0-2h / proxy 0-60% | 通常運用 | 秀吉 |
| Yellow | 稼働 2h or proxy 60% | `checkpoint` 作成、未読 inbox と active cmd を YAML 化 | 秀吉継続 |
| Orange | 稼働 3h or proxy 80% or unread >= 6 | **baton lease** を前田へ 15-30 分移譲、竹中は intake 保全、秀吉 `/clear` | 前田 |
| Red | 稼働 4h or proxy 90% or context-limit menu 兆候 | 新規 cmd intake 凍結、既存 dispatch のみ維持、強制 reset | 代理指揮 |

Claude の実 token 使用率を外部から正確に取れぬ場合は、proxy を採用する。

- pane 稼働時間: `tmux` process start からの経過
- inbox unread 数
- 1h 内 cmd_new 数
- dashboard 未更新時間
- session transcript サイズまたは capture-pane 文字数
- `context-limit` / menu / input lost の文字列検知

`/clear` 前に必ず作る checkpoint は以下。

- `queue/karo_state/hideyoshi_checkpoint.yaml`
- active cmd 一覧、担当者、次の一手、未処理 inbox id
- pending/blocked 理由
- dashboard 未反映事項
- reset 後の resume 指示

### M2 efficiency

token reset は「事故後復旧」ではなく「定期休憩」にする。2-3 時間ごとの 90 秒 reset は、12 時間蓄積後の context-limit 事故より遥かに安い。家康事故と同型化する前に、reset を作業工程へ織り込むべきである。

### M3 responsibility

reset 中に F002 を破らぬため、代理指揮を三段に分ける。

| 代理 | 許す範囲 | 禁止 |
|---|---|---|
| 前田 | SecondPC/独立 cmd の家老代行、軽量 dispatch、状態集約 | MainPC 専管 cmd の強権発動を単独判断 |
| 竹中 | intake triage、依存整理、隘路検出、dashboard 補助、信長への進言 | ashigaru dispatch、redo、罰則、三者監査最終判定 |
| 信長 | emergency freeze / resume の承認 | ashigaru 直接命令、直接実装 |

家老 reset 中の代理権は `queue/control_plane.yaml` に **lease owner / expires_at / scope** を書く。期限切れ lease は無効。代理が曖昧だと、越権か停止のどちらかになる。

### M4 improvement

新設すべき資産。

- `scripts/karo_token_guard.sh`: token proxy と稼働時間を監視し、Yellow/Orange/Red を出す。
- `scripts/karo_checkpoint.sh`: inbox/tasks/reports/dashboard 差分から checkpoint YAML を生成。
- `queue/control_plane.yaml`: 指揮権 lease の唯一の真。
- `instructions/karo.md`: reset 前後の必須手順を追記。
- `instructions/maeda.md` / `instructions/takenaka.md`: 代理指揮の範囲を追記。

## 2. Q2 家老 SPOF 解消

### M1 process

家老を「1 人の作業者」ではなく **control-plane role** として分解する。

| 領域 | 主担当 | 副担当 | 備考 |
|---|---|---|---|
| cmd intake | 秀吉 | 竹中 | 竹中は分類・依存整理まで |
| MainPC dispatch | 秀吉 | 期限付き前田 | 前田代行は lease 必須 |
| SecondPC dispatch | 前田 | 秀吉 | 別 quota を活かす |
| overload triage | 竹中 | 本多 | 竹中は即応、本多は後追い改革 |
| dashboard 主管 | 秀吉 | 前田が部分更新、秀吉 final | dashboard authority は家老に残す |
| redo/強権 | 秀吉 | 信長承認付き前田 | 竹中へ渡さない |

### M2 efficiency

既存 `cmd_karo_overload_takenaka_assist_001` は「軽量 task の逃がし先」として有効。しかし、家老 SPOF の中核は **dispatch 決裁・redo・dashboard 主管・reset 空白** であり、竹中補助だけでは半分しか解けぬ。

推奨は **dual-karo lane**。

- `queue/shogun_to_hideyoshi.yaml`: MainPC / 全体統括
- `queue/shogun_to_maeda.yaml`: SecondPC / 独立可能 cmd / 秀吉 reset 時の lease 代行
- `queue/control_plane.yaml`: 今どちらが主指揮か
- `queue/tasks/pending.yaml`: 家老未処理 backlog の一時退避

### M3 responsibility

ashigaru 直接実行による家老 bypass は、原則 F002 を壊す。緩和するなら「信長が ashigaru に命じる」のではなく、**家老が事前承認した bulk dispatch template** を使う。

許容案:

1. 家老が `queue/dispatch_templates/*.yaml` を承認済みにする。
2. 信長は cmd_new に `template_id` を指定できる。
3. watcher が template に従って pending task を作るが、初回承認者は家老。
4. 例外発動は `control_plane.yaml` に `emergency_bulk_dispatch: true` がある時だけ。

これなら直接命令ではなく「家老承認済みの自動手順実行」と位置付けられる。

### M4 improvement

家老 SPOF の解消は次の順が良い。

1. 竹中補助 monitor を完成させる。
2. `control_plane.yaml` による lease 制を入れる。
3. 秀吉/前田 dual-karo lane を明文化する。
4. bulk dispatch template は最後に入れる。これは強力だが誤実装時の越権 risk が高い。

## 3. Q3 信長並列発令の構造制約

### M1 process

信長発令時に **admission control** を入れる。命令を拒否するのではなく、`accepted / queued / requires_lord_decision` に分類する。

判定例:

| 指標 | Green | Yellow | Red |
|---|---:|---:|---:|
| active cmd_new | 0-3 | 4-5 | 6+ |
| karo unread | 0-5 | 6-9 | 10+ |
| dispatch latency | <5m | 5-10m | 10m+ |
| Claude 家老稼働 | <2h | 2-3h | 3h+ |

Red では新規 cmd を家老へ即送らず、`queue/tasks/pending.yaml` または `queue/intake_pending.yaml` に積む。dashboard の 🚨要対応へ「発令上限到達、優先順位選択が必要」と出す。

### M2 efficiency

信長 inbox に現在値を見せるだけでなく、**発令前 preflight hook** にする。

- `scripts/shogun_cmd_preflight.sh`: cmd 草案書込前に WIP と unread を表示。
- `scripts/cmd_admission_control.py`: active 数、unread、latency を評価し status を返す。
- `dashboard.md`: 「現在進行中 cmd_new / queue 待ち / 家老 reset 状態」を固定表示。

### M3 responsibility

本末転倒厳禁訓示との整合は、「成果最大化のために流入を制限する」と定義すればよい。量産 pressure による backlog 膨張は価値創出ではない。Red で止めるのは怠慢ではなく、完遂率を守る統治である。

### M4 improvement

cmd format に任意項目を足す。

```yaml
admission:
  mode: accepted|queued|blocked
  reason: "karo_unread=8, active_cmd=5"
  admitted_at: "2026-05-08T16:xx:xx+09:00"
  control_plane_owner: hideyoshi|maeda
  support_owner: takenaka|none
```

これにより「信長が何件出したか」ではなく「組織が何件受けられるか」を機械的に記録できる。

## 4. Q4 本多 1.0 TUI 描画問題の根本解決

### M1 process

切分は次の順で実施する。

1. 家康 0.3 の環境値を保存: `TERM`、`COLORTERM`、pane size、shell、`@agent_id`、`@agent_cli`、起動 command。
2. 本多 pane の同値を取得。
3. 同じ window で本多を起動して再現するか確認。
4. 別 window `multiagent:1` だけで再現するか確認。
5. `codex exec` は動くか、TUI だけが壊れるか確認。
6. `script -q /tmp/honda_tui.typescript codex` 等で tty 制御文字の有無を採る。

### M2 efficiency

復旧調査は 30-45 分で打ち切る。TUI 復旧が長引くなら、組織改革担当の価値は書面起案で十分出せる。TUI に固執して家老事故対策が遅れる方が本末転倒である。

### M3 responsibility

本多は直接実装者ではない。TUI 調査も、原因候補と再現手順を出し、実装修正は家老経由で足軽へ渡す。信長直轄への進言は可、ashigaru 直接命令は不可。

### M4 improvement

新設候補:

- `docs/runbooks/honda_codex_tui_troubleshooting.md`
- `scripts/checks/codex_tui_env_compare.sh`
- `scripts/honda_one_shot.sh`: TUI 不要の Codex exec wrapper

判定基準:

- 家康 pane と同条件で描画 OK: 本多 pane/window 構成問題。
- 全 pane で TUI NG だが `codex exec` OK: Codex TUI と WSL2/tmux の互換問題。
- 家康だけ OK: 起動時 env または tmux option 差分。

## 5. Q5 本多自身の運用 mode

### 推奨

本多は当面 **one-shot exec + 書面起案 mode** とする。常駐 TUI は不要。

正式経路:

1. 信長が諮問または監査依頼を出す。
2. `scripts/audit_meta_codex.sh` または `scripts/honda_one_shot.sh` が Codex を one-shot 実行。
3. 出力は `docs/honda_*.md` または `queue/reports/honda_report.yaml`。
4. 重要提案だけ信長 inbox へ短文通知。

### M1 process

本多の職責は M1-M4 の retrospective / 組織改革であり、常時対話よりも再現可能な書面出力が向く。TUI pane 不調時も価値創出が止まらぬ。

### M2 efficiency

one-shot は token reset が毎回自然に発生するため、家老 Claude のような 12h 蓄積事故と無縁である。監査結果もファイルに残るため、同じ説明を何度も会話で復元する必要がない。

### M3 responsibility

本多は「信長直轄の改革進言者」であり、dispatch はしない。書面 mode は越権を抑える。`docs/honda_*.md` は信長が cmd 草案化する材料であって、実行命令そのものではない。

### M4 improvement

`scripts/audit_meta_codex.sh` は既に存在するため、まずこれを拡張し、新 skill 生成は避ける。追加が必要なら wrapper と runbook に留める。

## 6. 優先順位

| 優先 | 対策 | 緊急度 | 工数 | 価値 | 理由 |
|---:|---|---|---|---|---|
| 1 | 家老 token reset + baton lease | 最高 | 中 | 最高 | 秀吉が家康同型事故へ向かっており、主指揮空白が最大 risk |
| 2 | 信長 admission control | 最高 | 中 | 最高 | 流入過多を止めねば、補助を増やしても再輻輳する |
| 3 | 竹中 overload monitor 完遂 | 高 | 中 | 高 | 既起案を活かせる即効策 |
| 4 | 秀吉/前田 dual-karo lane 明文化 | 高 | 中 | 高 | Claude 維持制約下で SPOF を下げる本筋 |
| 5 | 本多 one-shot wrapper/runbook | 中 | 小 | 中 | TUI 問題に依存せず改革機能を即時稼働 |
| 6 | bulk dispatch template | 中 | 大 | 中 | 強力だが F002 境界が難しいため後回し |
| 7 | 本多 TUI 根本調査 | 低 | 中 | 低-中 | one-shot で代替可能、緊急事故対策が先 |

## 7. cmd 起案候補

### cmd_karo_token_reset_baton_001

**Purpose**: 家老 Claude の context-limit 事故を予防し、reset 中も主指揮が途切れない体制を作る。

Acceptance Criteria:

- `queue/control_plane.yaml` が新設され、owner / lease_expires_at / scope / reset_state を保持する。
- `scripts/karo_token_guard.sh` が Yellow/Orange/Red を判定できる。
- `scripts/karo_checkpoint.sh` が active cmd、unread inbox、pending、dashboard 未反映事項を YAML 出力できる。
- `instructions/karo.md` / `instructions/maeda.md` / `instructions/takenaka.md` に reset/代理範囲が追記される。
- mock reset で秀吉 checkpoint → 前田 lease + 竹中 intake 保全 → 秀吉 `/clear` → resume が通る。

### cmd_shogun_admission_control_001

**Purpose**: 信長の並列発令を家老処理能力に合わせ、backlog による組織停滞を防ぐ。

Acceptance Criteria:

- `scripts/cmd_admission_control.py` が active cmd_new、karo unread、dispatch latency、家老稼働時間を評価する。
- Red 判定時は cmd を即時家老投入せず pending/intake に退避する。
- dashboard に active / queued / frozen / control_plane_owner / support_owner が表示される。
- Lord 決裁が必要な items は必ず dashboard 🚨要対応へ出る。

### cmd_dual_karo_lane_001

**Purpose**: 秀吉と前田の 2 家老体制を明文化し、SecondPC と reset 代行を構造的に使う。

Acceptance Criteria:

- `queue/shogun_to_hideyoshi.yaml` と `queue/shogun_to_maeda.yaml` の責務範囲が明文化される。
- `instructions/hideyoshi.md` / `instructions/maeda.md` に primary/secondary/lease protocol が追記される。
- 前田が独立可能 cmd と秀吉 reset 代行を受けられる条件が YAML で判定可能になる。

### cmd_honda_one_shot_ops_001

**Purpose**: 本多を TUI 非依存の Codex one-shot 書面起案役として安定稼働させる。

Acceptance Criteria:

- `scripts/honda_one_shot.sh` または既存 `scripts/audit_meta_codex.sh` 拡張で Markdown 出力ができる。
- `docs/runbooks/honda_codex_tui_troubleshooting.md` が作成される。
- 本多出力先が `docs/honda_*.md` / `queue/reports/honda_report.yaml` として明文化される。
- 信長 inbox には最重要 1-2 行のみ通知し、長文は docs 参照にする。

### cmd_bulk_dispatch_template_001

**Purpose**: 大規模反復 task に限り、家老承認済み template による semi-automatic dispatch を可能にし、F002 を壊さず処理量を上げる。

Acceptance Criteria:

- `queue/dispatch_templates/` 形式が定義される。
- template 承認者が家老であることを機械検証できる。
- emergency bulk dispatch は `control_plane.yaml` の明示 flag 必須。
- 直接 ashigaru 命令ではないことが instructions に明記される。

## 8. 実装順

1. `cmd_karo_token_reset_baton_001`
2. `cmd_shogun_admission_control_001`
3. `cmd_karo_overload_takenaka_assist_001` の完遂確認と不足補強
4. `cmd_dual_karo_lane_001`
5. `cmd_honda_one_shot_ops_001`
6. `cmd_bulk_dispatch_template_001`

## 9. 本多最終進言

上様、今すぐ止めるべきは Claude 家老ではなく、**家老へ無制限に流れ込む未整理 cmd と、reset 不能な単独主指揮構造**にござる。

竹中補助は良策。ただし竹中は「軽くする役」であり「継ぐ役」ではない。主指揮を継ぐには lease と checkpoint が要る。信長発令を絞るには精神論ではなく admission control が要る。本多は TUI を待たず、one-shot 書面でこの二 cmd を先に通すのが最短である。

以上、謀臣 正信、慎んで進言いたす。
