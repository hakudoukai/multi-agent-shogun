# Auto Git Sync Design (= cmd_019 起案前案、2026-05-11)

## Executive Summary

両 PC (MainPC + SecondPC) と GitHub origin (= `hakudoukai/multi-agent-shogun-newbuild`) の commit / push / pull を **systemd user timer** で event-bounded 自動化し、手動 sync 依存と drift を仕組みで根絶する。

ミス防止規範 (= 陛下御差配 2026-05-11)「すべてのミスは仕組みで防ぐ」を本領域に適用。

## Background — 真因確定

2026-05-11 13:30 調査 (= read-only verify) で判明:

| 軸 | MC | SC | 判定 |
|---|---|---|---|
| crontab | 空 | 空 | ❌ |
| systemd timer (= git/sync 系) | 不在 | 不在 | ❌ |
| .git/hooks/* | 空 (.sample のみ) | 空 | ❌ |
| 既存 `agent-periodic-push.timer` | disabled (= 5/09 16:18 手動停止) | 不在 | ⚠️ ただし中身は **agent 催促** service、**git 自動化に非ず** |
| `git pull` の現在状況 | **94 commit behind newbuild/main** | 0/0 (= 同期) | ❌ MC drift |

= **両 PC で git 自動 sync mechanism は実装されていない**。「自動化済」御認識と実態が乖離、本能寺戒め級の盲点。

## Design Principles

| 原則 | 適用 |
|---|---|
| **仕組みで防ぐ** | 人間 push に依存しない、systemd timer + 機械判定 gate |
| **時間ロス減 = 社会貢献** | 手動操作 0 化、shogun pane active 中も background で進行 |
| **Zero polling 哲学** | event-driven 不能ゆえ timer 使用、最低 5min interval で CPU 過剰防止 |
| **Anti-Duplication** | 既存 `validate_report_privacy.py` / `inbox_write.sh` / `normalize_shogun_verification_logs.py` 流用 |
| **WSL interop 耐性** | git は LAN 経由、vsock 故障時も独立稼働 (= MC 5/11 vsock 故障時にも理論的に動く) |
| **再起動 resilience** | systemd user timer + Persistent=true で WSL 再起動跨ぎ自動復活 |
| **対称性** | MC + SC で同一 unit + 同一 script、PC 区別は env で自動判定 |
| **prompt injection 防** | task YAML や agent 出力に含まれる shell 文字列を `git commit -m` に直接展開せず、固定 template + 検証済み diff のみ |

## Components

### 1. `scripts/auto_git_sync.sh` (= 新規 single-shot script)

責務:
1. preflight gate
2. fetch + pull (= safe merge OR halt-and-notify)
3. local change 検出 + commit (= privacy validator gate)
4. push (= bounded retry)
5. log + notify

実装言語: bash (= 既存 scripts/ と統一)、依存: git, python3 (= privacy validator 実行用), `flock` (= 排他制御)。

flow:

```
[Step 1: Preflight]
  - lock: flock /run/user/$UID/auto_git_sync.lock (= 二重起動禁、即 exit)
  - env: ~/.openclaw/env または config/settings.yaml 経由で PC_ID 取得
  - shogun_active_check: 陛下御差配「color触らない」期は manual override で skip 可
  - working tree size check: > 1000 file changed 時は halt (= 暴走防止)

[Step 2: Fetch + Pull]
  - git fetch <remote=newbuild|origin>
  - HEAD ↔ remote 差分:
    - same: skip (= Step 3 に)
    - fast-forward 可能: git pull --ff-only (= 安全 merge のみ許容)
    - non-FF (= divergent): HALT + inbox notify、auto-merge 厳禁

[Step 3: Local change check + commit]
  - git status --porcelain で変更検出
  - 0 件: skip
  - >0 件: 
    - privacy gate: python3 scripts/validate_report_privacy.py --staged (= 既存 P2-2 流用)
    - PII/secret 検出: HALT + inbox notify、commit せず
    - PASS: git commit -m "auto(<PC_ID>): <timestamp> <changed_files_count>files" (= 固定 template、prompt injection 防)

[Step 4: Push]
  - git push <remote> main
  - 失敗時 max 3 retry (= 30s, 60s, 120s backoff)
  - 全 retry 失敗: HALT + inbox notify

[Step 5: Log]
  - queue/reports/auto_sync_log.yaml に append (= flock 経由 atomic)
  - schema: { ts, pc_id, fetched, pulled_count, committed, pushed, errors, duration_ms }
  - 異常時のみ inbox_write で karo に notify
```

### 2. `~/.config/systemd/user/auto-git-sync.service`

```ini
[Unit]
Description=Auto Git Sync (commit/push/pull, 5min interval)
After=network-online.target

[Service]
Type=oneshot
EnvironmentFile=-%h/.openclaw/env
ExecStart=/bin/bash %h/projects/multi-agent-shogun-newbuild/scripts/auto_git_sync.sh
StandardOutput=journal
StandardError=journal
TimeoutStartSec=180
```

### 3. `~/.config/systemd/user/auto-git-sync.timer`

```ini
[Unit]
Description=Trigger auto_git_sync.sh every 5 min

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Unit=auto-git-sync.service
AccuracySec=10s
Persistent=true

[Install]
WantedBy=default.target
```

### 4. `queue/reports/auto_sync_log.yaml` (= 新規 observability layer)

schema:

```yaml
generated_at: 2026-05-11T14:00:00+09:00
events:
  - ts: 2026-05-11T13:55:00+09:00
    pc_id: main_pc
    operation: full_cycle
    fetched: true
    pulled_count: 3
    committed: true
    commit_hash: abc123
    pushed: true
    errors: []
    duration_ms: 2400
  - ts: 2026-05-11T14:00:00+09:00
    pc_id: main_pc
    operation: halt
    halt_reason: non_ff_divergent
    pulled_count: 0
    committed: false
    pushed: false
    errors:
      - "remote diverged: local=abc123, remote=def456, common_ancestor=xyz789"
    duration_ms: 850
```

## Failure Mode Handling (= 黒田 4_logic + 6_test 観点)

| Failure | Detection | Action | Recovery |
|---|---|---|---|
| `git pull` conflict | non-FF diverge | HALT + inbox notify | 人間 / karo が手動 merge → 再 enable |
| `git push` rejected (= remote 先行) | exit code 1 + "Updates were rejected" | pull 先行で retry、3 回まで | bounded retry 内で自然解決 |
| privacy validator fail | python3 exit 非 0 | HALT + inbox notify、commit せず | 人間が secret 除去 → 再 trigger |
| SUPABASE_URL 等 env 不在 | preflight check | warn log、push/pull 自体は env 不要ゆえ続行 | env 復帰で自動回復 |
| working tree > 1000 file changed | preflight size check | HALT + inbox notify | 人間 review → 再 trigger |
| network error | git command exit | bounded retry 3 回、全失敗で HALT | network 回復後の次 trigger で自然回復 |
| 同時起動 | flock | 即 exit (= duplicate prevention) | 次 trigger で再走 |
| WSL interop 故障 (= vsock) | git は LAN 経由ゆえ無関 | 影響なし | N/A |

## Cross-PC Symmetry

両 PC で **同一 script + 同一 unit** を配置。PC 区別は env で自動判定:

```bash
# auto_git_sync.sh 冒頭
if [ -z "${PC_ID:-}" ]; then
  case "$(hostname)" in
    USER-0T4SR8MIQA) PC_ID=main_pc ;;
    USER-O6AK917NTU) PC_ID=second_pc ;;
    *) PC_ID=unknown ;;
  esac
fi
```

= hostname から自動推論、env override も許容。配置作業は両 PC 同一ファイル copy のみ、divergence 構造的不能。

## Observability + Notify

- **正常時**: log file append のみ、inbox notify せず (= 静音)
- **HALT 時**: inbox_write で karo に notify (= karo dashboard 集約) + log file に halt_reason 記録
- **連続 HALT (= 3 回連続)**: shogun (= 拙者) inbox に escalation notify (= 構造的問題の早期検出)

## gitignored File Sync (= 別 cmd 範囲、本 cmd では除外)

`memory/MEMORY.md` 等 gitignored file の cross-PC sync は **本 cmd 範囲外**。
別 cmd で `docs/memory_sync_design.md` の B+D 案 (= shared block + Supabase) を実装する。

理由:
- gitignored ゆえ git sync 経路外
- shared block 抽出 mechanism 未実装、本 cmd で扱うと scope 肥大
- 既存 設計書 `docs/memory_sync_design.md` あり、別 cmd で着手

## Anti-Pattern 排除

| Anti-Pattern | 排除策 |
|---|---|
| 無限 retry loop | max 3 retry + exponential backoff、全失敗で HALT |
| polling (= 短 interval) | 最低 5min interval、`AccuracySec=10s` で精度より省 CPU |
| 別 daemon 増設 | systemd user timer + 既存 inbox / validator 流用 |
| auto-merge conflict | 厳禁、必ず HALT + notify |
| commit message に PII | 固定 template、prompt injection 防 |
| shogun 対話中 push の妨害 | 必要なら `shogun_active_check` を retain (= 既存 `agent_periodic_push.sh` idea 流用)、ただし default では git 自動化は対話と独立 (= 別 layer) |

## Known Differences vs. Initial Design (= cycle2 fix, 2026-05-11)

実装後の cycle1 状態 (= 黒田事後監査 `kuroda_audit_auto_git_sync_20260511` で
completion_gate=blocked) に対する cycle2 fix の結果、設計書と実装の現状差分:

| 項目 | 設計書 | 現状 (cycle2 後) | 補足 |
|---|---|---|---|
| auto-commit | 5min timer で固定 template commit | **削除** (= F007 遵守 refactor) | agent workflow + 陛下御差配が trust gate、commit 自動化禁 |
| auto-push | 5min timer で bounded retry push | **削除** (= F007 遵守 refactor) | 同上、push は agent / 陛下御差配下で手動 |
| privacy gate | `validate_report_privacy.py --staged` で commit 前 secret scan | **撤去** (commit 経路自体が削除) | scan は手動 commit 経路で別途実施 |
| 5min timer 動作 | full_cycle (fetch+pull+commit+push) | **pull-only cycle** (fetch+FF pull or HALT、dirty tree は stash 経路) | drift 防止本来の責務に絞り込み |
| log schema | fetched/pulled_count/committed/pushed/errors/duration_ms | 簡略 (ts/pc_id/operation/halt_reason/extra) | extra に status=ff_pulled/up_to_date/local_ahead_awaiting_manual_push を含める |
| test 整備 | `tests/test_auto_git_sync.py` 全 PASS/SKIP=0 (AC9) | **完備** (6 scenario + 1 syntax = 7 PASS / SKIP=0) | (a) FF pull / (b) divergent HALT / (c) up_to_date / (d) local_ahead F007 / (e) flock 二重起動禁 / (f) stash-dirty FF pull / (sanity) bash -n |
| script tracking | git tracked 想定 | **`.gitignore:7` で gitignored** | 「壊すな」対象、cross-PC は本能寺戒め級慎重判断で人間 sync |

### cycle2 で構造的解消した P0 (= 旧版前提の懸念)

cycle1 黒田 audit で挙がった P0 懸念のうち、pull-only refactor (= F007 遵守) で
**構造的に解消** (= 改めて fix 不要) のもの:

- **P0-2 (privacy gate head-200 truncate)**: privacy gate そのものが削除済 ゆえ head-200 truncate 懸念 moot
- **P0-3 (auto commit が transient state を捕まえる)**: auto commit 経路が削除済 ゆえ moot

残 P0:

- **P0-1 (`tests/test_auto_git_sync.py` 不在)**: 本 cycle で完備 (= 6 scenario + bash -n)

### cycle2 で test scope に追加した新観点

旧版 (auto-commit + auto-push) 用 test 観点では cover できぬ pull-only mode 固有挙動:

- `status=up_to_date` (= local == remote の no-op cycle が log に正しく刻まれる)
- `local_ahead_awaiting_manual_push` (= local ahead で F007 遵守 = auto-push せず log のみ、remote head 不変)
- stash → FF pull → stash pop (= dirty working tree でも FF pull が破壊せず動く)

## Acceptance Criteria (= cmd_019 ドラフト)

| AC | 条件 |
|---|---|
| **AC1** | 両 PC で `auto-git-sync.timer` enabled + active + 5min interval で起動 (= `systemctl --user is-enabled` + `is-active` で機械判定) |
| **AC2** | non-conflict commit が 10min 以内に origin に到達 (= 平均 5min trigger + 1 cycle 完遂時間) |
| **AC3** | pull conflict 時は auto-merge せず HALT + inbox notify (= 人間介入 trigger) |
| **AC4** | privacy validator で PII/secret 含む変更 commit を構造的に拒否 |
| **AC5** | 全 trigger を `queue/reports/auto_sync_log.yaml` に append、schema 適合 |
| **AC6** | WSL 再起動後 systemd user timer 自動復活 (= `Persistent=true` 効果 verify) |
| **AC7** | SUPABASE_URL 等 env 不在でも core git 操作は走る (= push/pull は env 不要) |
| **AC8** | 連続 HALT 3 回で shogun inbox escalation notify |
| **AC9** | pytest tests/ で test_auto_git_sync.py 全 PASS、SKIP=0 |
| **AC10** | 両 PC 配置後、24h 運用で drift = 0 (= MC HEAD == SC HEAD == origin HEAD) |

## Implementation Stream (= ashigaru 担当割り当て候補)

| Stream | 内容 | Owner 候補 |
|---|---|---|
| **A** | `scripts/auto_git_sync.sh` 実装 | ashigaru1 (鬼柴田) |
| **B** | `~/.config/systemd/user/auto-git-sync.{service,timer}` 配備 (= MC + SC 両配置) | ashigaru2 |
| **C** | `queue/reports/auto_sync_log.yaml` schema 定義 + initial entry | ashigaru2 |
| **D** | `tests/test_auto_git_sync.py` pytest 整備 (= mocked git + privacy validator + flock 検証) | ashigaru3 |
| **E** | 両 PC 配置 + 24h 運用 verify | 家康 + 本多 連携 |
| **F** | 黒田 final pass (= 9 観点 + 10 lens) | 黒田 |

## Open Questions for 黒田 監査

設計の論点を **黒田 9 観点監査** に先立ち列挙:

- **Q1 (= 4_logic)**: `git pull` の non-FF auto-merge を完全禁止する案だが、両 PC が同 file の異なる行を編集した non-conflict merge も reject すべきか? それとも `--no-rebase --no-ff` で merge commit 許容?
- **Q2 (= 8_UX)**: 5min interval は短すぎ? 10min / 15min も検討余地あり。trade-off: 短 = drift 最小化、長 = CPU + commit noise 減
- **Q3 (= 3_discipline)**: `shogun pane active 時 skip` は既存 `agent_periodic_push.sh` の idea。本 cmd では default disable 推奨 (= git 自動化と対話は別 layer ゆえ干渉せず)、御意?
- **Q4 (= 5_schema)**: PC 自動判定の env 名 `PC_ID` を新規 introduce vs 既存 `MAIN_PC_ID` / `HAKUDOKAI_ROLE` 流用、いずれが堅牢か?
- **Q5 (= 2_anti_dup)**: 既存 `validate_report_privacy.py` の `--staged` mode 実装状況確認 (= 既存ない場合は本 cmd で追加実装)
- **Q6 (= 10_ecosystem)**: 既存 `normalize_shogun_verification_logs.py` の canonical index 再生成を auto-pull 後の post-hook で trigger すべきか? それとも 別 timer? trade-off: 統合 = drift 最小、分離 = 単一責任原則
- **Q7 (= 6_test)**: pytest で `git push` を mock するか、テスト用 bare repo を fixture で立てるか? 後者の方が真の動作 verify 可能
- **Q8 (= 7_law)**: `auto_sync_log.yaml` に commit hash + PC ID を記録するが、外部 push (= GitHub) で `auto(main_pc): timestamp 5files` commit が個人情報含むか? 含まぬ前提だが念のため

## SLA + 規範整合

- **10 分 SLA**: 本 mechanism は MC↔SC drift を 10min 以内に解消、陛下御差配 10min SLA 整合
- **PDCA max 7 cycle**: 本 cmd は 1 回完遂想定、cycle 超過 risk 低
- **完遂 4 項 verify**: AC10 (= 24h 運用で drift=0) を信長 shogun_verified で確定

## Final Proposed Rule

**No human, no drift. systemd timer carries the load. PII gate before commit. HALT, not auto-merge, on conflict.**

両 PC + origin の三角同期を仕組みで gate 化、ミスは構造的に起こり得ぬ。

---

*Drafted by 信長 (= shogun) — 2026-05-11、黒田監査依頼前案、cmd_019 起案候補。*
