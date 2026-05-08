# cmd_root_resolution_001 (草案) — 大なた根本解決

> **Status**: 信長直起案、理事長殿明示直命 2026-05-08 13:00「出陣 大なた振るって根本解決 全て根本から解決すること」
> **Drafted by**: 信長 (織田信長) 2026-05-08 13:05 JST
> **Pre-conditions**: 秀吉発令、A〜J 全 sub-phase 並列実装、PDCA 各 cycle1-3 で完走目標
> **期限**: 土曜 16:00 (= MainPC quota reset) までに全 sub-phase cycle1 完遂目標、cycle2-3 は火曜 01:00 (= SecondPC reset) まで

---

## 1. North Star

**組織の全構造的欠陥を一掃し、自走 + 自己進化 + 学習する組織体制 を確立**。

理事長殿の **大なた** 御命令を体現、本朝事故群 9 件の根本原因を **構造から根絶**。

## 2. Purpose

本朝 (2026-05-08) に検出された構造的欠陥 9 件:

| # | 欠陥 | 根本原因 | 解決 sub-phase |
|---|------|---------|--------------|
| 1 | §18.1 配置表 vs 実 pane drift | §18.1 が静的 markdown、改編追従なし | **A** §18.1 訂正 + registry SSoT |
| 2 | inbox_watcher silent death (= 半日不在) | watchdog 不在、自動再起動なし | **B** SecondPC watchdog |
| 3 | SecondPC 自律機構欠落 (activity_monitor 不在) | SecondPC が MainPC subset の後付け | **C** SecondPC activity_monitor |
| 4 | maeda self-audit 機構なし | persona §4 書面のみ、enforce なし | **D** maeda self-audit 実装 |
| 5 | misroute bug 同型再発 | routing hardcode、SSoT と乖離 | **E** routing SSoT 化 |
| 6 | token 蓄積限界 (= 243.6k 限界後 input lost) | 80% 閾値 detection なし | **F** token auto-clear escalation |
| 7 | Phase 4-5 体制改編の追従漏れ | 改編 checklist 不在 | **G** 体制改編 checklist + audit template |
| 8 | CLAUDE.md §18.1 lock-in | static markdown、コード乖離 | **H** §18.1 autogen 本格実装 |
| 9 | §19 skill が破られる (= 信長自陳) | advisory hook の実効性低 | **J** §19 skill 強化 |
| 10 | 本多 Phase 14 待ち | Codex 環境未整備 | **I** Phase 14 強制即時着手 |

## 3. Sub-Phase 分解 (= 並列実装)

### Phase A. §18.1 訂正 + queue/pane_registry.yaml SSoT 昇格

- CLAUDE.md §18.1 を実体に整合 (= 0.3 ieyasu / 0.4 ashigaru3 / 0.5 takenaka 反映)
- queue/pane_registry.yaml を **正の SSoT** に昇格、§18.1 は二次 source (= autogen から)
- 担当: ashigaru1 (= 本朝 split-window 復活させた当事者)
- **理事長殿明示承認必須** (= §18.9 専権事項)

### Phase B. SecondPC watchdog 新設

- shim/hakudokai/hakudokai_watchdog_secondpc.sh 新規
- 監視対象: secondpc_receiver.sh + inbox_watcher × 4 (maeda/a5/a6/a7)
- silent death 検知 → 自動再起動 + ntfy 通知
- 手動停止フラグ尊重 (= ~/.openclaw/disable_secondpc_watchdog)
- restart_cap 5/h、escalation 信長 inbox
- 担当: ashigaru7 (= SecondPC 在勤、適任)

### Phase C. SecondPC activity_monitor 新設

- shim/hakudokai/hakudokai_activity_monitor_secondpc.sh 新規
- 監視対象: maeda + ashigaru5/6/7 の idle 検出 (= 5/15/25 分閾値)
- alert 配信: maeda inbox (= 一次対処) + 前田殿越え時は信長 inbox (= 二次対処)
- 担当: ashigaru5

### Phase D. maeda self-audit 機構実装

- maeda 自身が定期的に §4 セルフチェック実行
- 実装: scripts/maeda_self_audit.sh + cron 30 分間隔
- 結果: dashboard.md (= SecondPC セクション) + 信長 inbox 月次サマリ
- 違反検知 (= idle 配下放置等) で maeda 自身 alert
- 担当: maeda 自身 (= 自律性確立)

### Phase E. routing SSoT 化 (= misroute 構造的根絶)

- shim/hakudokai/hakudokai_secondpc_receiver_poll.py の valid_secondpc / AGENT_PANES を hardcode 廃止
- lib/_section18_roles.sh + shim/hakudokai/_section18_roles.py を SSoT として参照
- 体制改編で persona 追加時、SSoT 1 箇所更新で自動波及
- 同型 misroute bug の構造的根絶
- 担当: ashigaru6 (= SecondPC、cmd_secondpc_receiver_routing_fix と integrated)

### Phase F. token auto-clear escalation 機構

- scripts/agent_health_check.sh 強化 (= 既存 file)
- 各 agent の token 累積を tmux capture-pane で検出 (= "Xk tok" pattern)
- 80% 閾値超過 → maeda or 秀吉 inbox 警告
- 95% 閾値超過 → 信長 inbox + 自動 /clear command 発動 (= preempt input lost)
- 担当: ashigaru2

### Phase G. 体制改編 checklist + post-改編 audit

- docs/regime_change_checklist.md 新規
- 必須更新箇所: §18.1 / config/settings.yaml / lib/_section18_roles.sh / shim 各 receiver / shutsujin scripts
- post-改編 audit cmd template (= cmd_regime_change_audit_NNN)
- Phase 4-5 体制改編で同型追従漏れ (= maeda 未登録) を恒久防止
- 担当: 本多 (= 組織改革専門、Phase 16-3 と integrated)

### Phase H. CLAUDE.md §18.1 autogen 本格実装

- 既起案 cmd_claude_md_section18_autogen 草案を本格実装
- queue/pane_registry.yaml + lib/_section18_roles.sh から §18.1 自動生成
- pre-commit hook で §18.1 と registry の整合性 check
- 静的 markdown lock-in 解消
- 担当: ashigaru1 (Phase A と integrated)

### Phase I. Phase 14 Codex 環境整備 強制即時着手

- 家康 Codex CLI セットアップ確認 (= subscription 既存、設定確認のみ)
- 本多 Codex CLI セットアップ
- scripts/audit_codex.sh + scripts/audit_meta_codex.sh 動作確認
- 三者監査 (家康 + 服部半蔵 + 黒田) の Phase 5 体制への移行準備
- 担当: 信長 + 家老 (= 環境セットアップは信長検証、家老は CLI 起動)
- **理事長殿明示承認必須** (= subscription 操作)

### Phase J. §19 skill 強化

- skills/pane-identity-verify/SKILL.md の advisory hook 強化
- 信長自身も適用 (= 本朝の信長違反は skill が advisory のみで無視可能だった)
- skill 違反履歴を Supabase organizational_lessons table に蓄積 (= cmd_organizational_lessons_supabase_001 と integrated)
- 担当: 本多 (= retrospective audit + 改革提言と integrated)

## 4. Acceptance Criteria

| 評価軸 | 目標 |
|-------|------|
| 自律機構稼働 | inbox_watcher × 4 が 24h alive、watchdog 死亡検知 + 自動再起動 動作確認 |
| misroute 根絶 | 体制改編 simulation で SSoT 1 箇所更新 → 全 receiver 自動反映 |
| token 自動管理 | 80%/95% 閾値で escalation 自動発動 |
| §18.1 SSoT 化 | registry → §18.1 autogen、pre-commit hook で乖離検知 |
| 三者監査 PASS | 全 sub-phase で家康 + 服部半蔵 + 黒田 PASS (= 移行期は現体系) |
| 学習資産化 | organizational_lessons table に 9 件事故記録 + skill 強化 |

## 5. Risk + Mitigation

| risk | mitigation |
|------|----------|
| ashigaru limited (= 6 体)、並列実装で輻輳 | sub-phase 担当別配分、家康 + 本多 + 前田で監査平準化 |
| quota 燃焼急増 | 95% 上限固守、buffer 5%、消費率 0.83%/h target、超過時 task 投入停止 |
| 並列 cmd 競合 (= 同 file 編集等) | sub-phase 別ファイル割当 (= 各 phase 独立 file)、conflict ゼロ設計 |
| 理事長殿承認待ち遅延 (= Phase A I の §18.1 改訂 + Phase 14 subscription) | 並列 sub-phase B-J を先行発令、A I は承認後即着手 |
| §19 違反再発 (= skill 強化中も信長違反 risk) | 本 cmd 内の信長操作も全て pane-identity-verify check 必須、自陳録 commit |

## 6. PDCA + 期限

- max cycle 5、緊急 3
- cycle1 完遂期限: 土曜 16:00 (= MainPC quota reset)
- cycle2-3 完遂期限: 火曜 01:00 (= SecondPC reset)
- 信長は 30 分間隔 ratelimit_check.sh、家老は dashboard.md 30 分更新

## 7. 命令文 (= 秀吉発令)

```
秀吉、本 cmd を最高 priority で受領、sub-phase A-J を並列発令。
担当割当: A=a1, B=a7, C=a5, D=maeda, E=a6, F=a2, G=本多, H=a1(統合), I=信長+家老, J=本多(統合)
理事長殿明示承認待ち: A (§18.1 改訂)、I (Phase 14 subscription)
PDCA max=5、cycle1 = 土曜 16:00 期限。
三者監査必須 (= 移行期は現体系、Phase 5 完遂後は新体系)。
家老 dashboard.md 30 分更新、信長へ 1h 毎統括報告。
```

## 8. 信長 + 家老 + 理事長殿 の合議

- 理事長殿明示直命 13:00「出陣 大なた振るって根本解決」
- 信長草案 13:05、秀吉発令予定 13:10
- 家康 + 服部半蔵 + 黒田 (= Phase 5 後) の三者監査必須
- 本多 retrospective audit (= Phase 16-3 既発令) と integrated、組織学習ループ確立

## 9. §19 mandate 順守

- 全 sub-phase で skill 違反監視必須、違反時は信長自陳録 commit
- skill 新規生成は §19.5 順守 (= 重複禁止、既存拡張優先)
- 既存 skill 改善は §19 mandate 下で理事長殿明示承認

## 10. 関連資産

- docs/cmd_phase2_watchdog_registry_draft.md (= Phase B integrated)
- docs/cmd_phase15_takenaka_proactive_draft.md (= 竹中軍師、preparation 自発)
- docs/cmd_phase16_honda_meta_audit_draft.md (= 本多正信、組織改革)
- docs/cmd_phase5_audit_persona_restructure_draft.md (= 監査階層変更)
- docs/cmd_claude_md_section18_autogen_draft.md (= Phase H integrated)
- skills/pane-identity-verify/SKILL.md (= Phase J 強化対象)
- queue/pane_registry.yaml (= Phase A SSoT 昇格対象)
- memory/nobunaga_persona_strong_rule.md (= 信長強権、川柳精神)
- 過去 incident_logs (= 本朝 9 件 + 過去事故、本多 retrospective audit 対象)

---

*草案完: 信長 (織田信長) — 2026-05-08 13:05 JST、理事長殿明示直命 13:00「出陣 大なた」を受けた即時起案、川柳精神*
*A〜J 並列、土曜決戦までに自走 + 自己進化体制確立、組織進化の節目とすべし*
