# Incident: Pane 番号誤認による gunshi 重複作成 (2026-05-07)

## サマリ

将軍 (拙者) が `multiagent:agents.4 = gunshi` と誤認し、実際は `agents.3` で生存中の gunshi に対して agents.4 に重複 gunshi pane を新設。整合性が壊れた状態が約 30 分間継続した。

## 発生・発見

| 項目 | 時刻 (JST) |
|------|-----------|
| 発生 | 2026-05-07 21:14 (拙者が `tmux split-window` 実行) |
| 発見 | 2026-05-07 22:00 (理事長殿「gunshi は CODEX だよね」発言を契機に再調査) |
| 完全復旧 | 2026-05-07 22:10 (重複 pane 削除 + commit 7fecf72) |
| 継続時間 | 約 56 分 |

## 事象

1. 21:13 拙者が全 agent 状態確認時、`multiagent:agents.4` を pane 番号だけで「gunshi のはず」と判定 (= **@agent_id 確認なし**)
2. agents.4 は実際には存在しなかった (= split されてなかった) ため capture-pane が空に → 「gunshi pane が死亡している」と誤判定
3. 21:14 拙者が agents.3 の下に新 pane を split し、agents.4 に「復活 gunshi」を起動
4. 同時に gunshi は **agents.3 で生存中**、cmd 議論を進めていた (= 「影武者の退職理由が…」と思考表示)
5. 結果: gunshi が 2 pane に重複存在 (agents.3 = 元から、agents.4 = 拙者が誤作成)
6. 22:00 理事長殿の質問「gunshi は CODEX」契機で settings.yaml 確認 → @agent_id 紐付け乖離が発覚
7. 22:10 重複 pane 削除、設計記述 (shutsujin / settings.yaml) を実装に統一 commit

## 根本原因 (= 5 Why)

| Why | 答え |
|-----|------|
| なぜ重複 pane を作ってしまったか? | gunshi が agents.4 にいると **誤認** したから |
| なぜ誤認したか? | pane 番号と agent 名のマッピングを **推測** したから (= `tmux display-message -p '#{@agent_id}'` で確認しなかった) |
| なぜ推測したか? | CLAUDE.md §18.1 が「multiagent:0.4 = gunshi」と記述、shutsujin_departure.sh L571 も「5 panes」と書いていた (= **設計と実装の乖離**) |
| なぜ乖離していたか? | §18 移行時に shutsujin/supervisor/agent_periodic_push を 4 panes 通常に統一したが、CLAUDE.md §18.1 の表と shutsujin の冒頭コメントが旧 5 panes 記述のまま残った (= **メタ情報の更新漏れ**) |
| なぜ更新漏れが起きたか? | 「コードを直したらドキュメントも直す」を機械的に保証する仕組みがなかった (= **整合チェックの自動化未整備**) |

## 影響範囲

- 重複 gunshi pane 1 つ (= 拙者作成)
- Anthropic API rate limit 1 回 (= 重複 pane の claude が起動直後に大量 read で throttle)
- 実害: 設計に沿った agent 配置と watcher 紐付けの破壊。gunshi 監査機能は agents.3 で継続稼働していたため、**業務影響は最小限** (= 30 分間の重複状態のみ、誤監査・誤発令はなし)

## 復旧アクション

1. agents.4 の claude プロセス SIGTERM (= python3 os.kill)
2. `tmux kill-pane -t multiagent:agents.4` で重複 pane 削除
3. `shutsujin_departure.sh` L571 コメントを「§18 4 panes 通常運用」に修正
4. `config/settings.yaml` L100-105 に「a3/a8 は非常時のみ起動だが配信先として保持」を補足
5. commit 7fecf72 + push

## 防止策 (= 本事例から生成した skill)

| skill | 役割 |
|-------|------|
| `skills/pane-identity-verify/SKILL.md` | tmux 操作前に必ず `#{@agent_id}` を確認するルール化 |
| `scripts/checks/pane_identity.sh` | 4 panes の整合性を自動検証 (= 期待 vs 実態) |
| `skills/lessons-to-skill/SKILL.md` (= meta) | 今後同種事故の再発防止スキルを自動生成 |
| CLAUDE.md §19 | Post-Incident Lessons Capture (mandatory) |

## 教訓

1. **pane 番号 = agent 名** の暗黙マッピングを **絶対に推測しない**。毎回 `tmux display-message -p '#{@agent_id}'` で確認する。
2. **設計と実装の乖離** が放置されると、後続の判断者が誤る。コード修正時にドキュメント (CLAUDE.md, shutsujin コメント) も同時に修正する。
3. **疑わしい時は確認** を優先する。今回拙者は「死亡してる」と急いで判定した。1 行 `tmux display-message` を打てば 30 分の事故は防げた。

## 関連 commit

- 7fecf72 — fix(integrity): §18 設計記述を実装に統一
- (このコミット) — feat(skills): pane-identity-verify + lessons-to-skill + CLAUDE.md §19
