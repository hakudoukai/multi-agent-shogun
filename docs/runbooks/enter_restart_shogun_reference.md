# Enter再起動システム — main_pc / second_pc 配備参考実装

**parent task**: ee4d6ce4 (Enter再起動システム命名統一 + enter_restart_shogun_third 新設)
**author**: ashigaru-third-1
**canonical 4 units**:

| unit | target | 担当 |
|------|--------|------|
| `enter_restart_commander` | commander-third:0.0 | third_pc 配備済 (本 task) |
| `enter_restart_shogun_third` | shogun-third:0.0 | third_pc 配備済 (本 task) |
| `enter_restart_shogun_main` | shogun:0.0 (or shogun-main:0.0) | **main_pc 担当** (本 doc の参考実装) |
| `enter_restart_shogun_second` | shogun-second:0.0 | **second_pc 担当** (本 doc の参考実装) |

## 1. 設計原則 (全 4 unit 共通)

- ★ 新規コマンド送信 絶対禁。**C-m (Enter) のみ** 既入力 buffer 確定のため送信 ★
- ★ tmux send-keys `-l` (literal text) 不使用 ★
- ★ Claude UI prompt + 非空 input buffer を検出した時のみ発火 ★ (false positive 防止)
- ★ 過去 15min 内 fire 数 >= 3 → 本 cycle 停止 ★ (2026-05-05 SecondPC 暴走事件教訓)
- ★ shireiko_audit_log + pc_handshake 双方に証跡 row INSERT ★ (DB constraint 整合済)
- ★ Watcher Design Principles §1-7 順守 ★ (retry 無限ループ禁、self-send 即 ack、idempotency)

## 2. 配備手順 (各 PC 共通)

### 2.1 前提

| 項目 | 必須 |
|------|------|
| account ログイン | §18 配置表に合致 (main_pc=sasebo, second_pc=hakudoukai, third_pc=hakudoukai) |
| `loginctl show-user $USER --property=Linger` | `Linger=yes` (未設定なら `sudo loginctl enable-linger $USER`) |
| `~/.local/share/hermes-agent/venv/bin/python3` | 既存 (commander_failsafe と同経路) |
| `doppler` CLI + `openhands/dev` config | 既存 (Supabase 接続用) |
| tmux session | shogun / shogun-main / shogun-second 等が起動済 |

### 2.2 配備 step

```bash
# 1) repo pull
cd ~/multi-agent-shogun && git pull origin <branch>

# 2) scripts copy
cp scripts/watchdogs/enter_restart_shogun_third_watchdog.sh  ~/scripts/enter_restart_shogun_<pc>_watchdog.sh
chmod +x ~/scripts/enter_restart_shogun_<pc>_watchdog.sh

# 3) systemd user units copy
cp scripts/watchdogs/enter_restart_shogun_third.service ~/.config/systemd/user/enter_restart_shogun_<pc>.service
cp scripts/watchdogs/enter_restart_shogun_third.timer   ~/.config/systemd/user/enter_restart_shogun_<pc>.timer

# 4) PC 別差分編集 (下記 §3 参照): pane target / from_pc filter / log subdir 名 / unit 名
$EDITOR ~/scripts/enter_restart_shogun_<pc>_watchdog.sh
$EDITOR ~/.config/systemd/user/enter_restart_shogun_<pc>.{service,timer}

# 5) reload + enable
systemctl --user daemon-reload
systemctl --user enable --now enter_restart_shogun_<pc>.timer

# 6) verify (cycle 1 回実行 + log/audit row 確認)
systemctl --user start enter_restart_shogun_<pc>.service
sleep 8
tail -20 ~/.local/share/enter_restart_shogun_<pc>/$(date +%Y%m%d).log
# Supabase shireiko_audit_log で event_type=enter_restart_shogun_<pc>_fire row 確認
```

## 3. PC 別必要差分

| 変数 | third_pc (実装済 / 本 task) | main_pc 配備値 | second_pc 配備値 |
|------|----------------------------|----------------|-------------------|
| `PANE_TARGET` | `shogun-third:0.0` | `shogun:0.0` (※または `shogun-main:0.0` 既存命名次第) | `shogun-second:0.0` |
| `FROM_PC_FILTER` | `third_pc` | `main_pc` | `second_pc` |
| `LOG_DIR` | `~/.local/share/enter_restart_shogun_third` | `~/.local/share/enter_restart_shogun_main` | `~/.local/share/enter_restart_shogun_second` |
| systemd unit 名 | `enter_restart_shogun_third.{service,timer}` | `enter_restart_shogun_main.{service,timer}` | `enter_restart_shogun_second.{service,timer}` |
| audit event_type | `enter_restart_shogun_third_fire` | `enter_restart_shogun_main_fire` | `enter_restart_shogun_second_fire` |
| heartbeat topic | `[enter_restart] shogun_third alive...` | `[enter_restart] shogun_main alive...` | `[enter_restart] shogun_second alive...` |
| target_pc | `third_pc` | `main_pc` | `second_pc` |

★ `from_pc` は `pc_handshake_from_pc_check` constraint 整合値必須:
`main_pc | second_pc | third_pc | director | fukuincho | kuro_desktop | codex_gpt_advisor | gemini_advisor | commander` のいずれか ★

## 4. systemd user unit skeleton (skeleton inline)

### 4.1 `enter_restart_shogun_<pc>.service`

```ini
[Unit]
Description=Enter Restart — shogun-<pc> Watchdog (10min idle → C-m only, label-match strict / ee4d6ce4)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=%h
ExecStart=/bin/bash %h/scripts/enter_restart_shogun_<pc>_watchdog.sh
StandardOutput=append:%h/.local/share/enter_restart_shogun_<pc>/service.log
StandardError=append:%h/.local/share/enter_restart_shogun_<pc>/service.err
```

### 4.2 `enter_restart_shogun_<pc>.timer`

```ini
[Unit]
Description=Enter Restart — shogun-<pc> 5min cycle (<pc> local / ee4d6ce4)
Requires=enter_restart_shogun_<pc>.service

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min
AccuracySec=10s
Unit=enter_restart_shogun_<pc>.service

[Install]
WantedBy=timers.target
```

## 5. watchdog script skeleton (要点)

完全な実装は `scripts/watchdogs/enter_restart_shogun_third_watchdog.sh` を参照。
**コピー後に変更が必要な箇所のみ列挙:**

```bash
# === ★PC 別差分: ここのみ書き換え★ ===
PANE_TARGET="shogun:0.0"               # main: "shogun:0.0", second: "shogun-second:0.0"
FROM_PC_FILTER="main_pc"               # main_pc | second_pc | third_pc
LOG_DIR="/home/<user>/.local/share/enter_restart_shogun_main"  # _main / _second 等
# ====================================

# 残りは third_pc 版と同一 (Step 0 cap → Step 1 pane verify → Step 2 idle 判定 →
#                            Step 3 pane meta + tail capture → Step 4 alive guard →
#                            Step 5 label-match strict → Step 6 fire (C-m only) →
#                            Step 7 shireiko_audit_log INSERT →
#                            Step 8 heartbeat INSERT (from_pc=$FROM_PC_FILTER))
```

加えて以下の値を全置換 (sed):

```bash
sed -i \
  -e "s/enter_restart_shogun_third/enter_restart_shogun_<pc>/g" \
  -e "s/shogun_third/shogun_<pc>/g" \
  -e "s/shogun-third/shogun-<pc>/g" \
  -e "s/target_pc\": \"third_pc/target_pc\": \"<pc>/" \
  ~/scripts/enter_restart_shogun_<pc>_watchdog.sh
```

## 6. account / PC 配置順守 (§18.1 / FKI-SECOND-PC-SINGLE-DISTRO-01)

| PC | account | 担当 ashigaru | distro |
|----|---------|---------------|--------|
| main_pc | sasebo@sasebo.or.jp | a1-1 / a1-2 / a1-3 | (Ubuntu 等) |
| second_pc | hakudoukai@gmail.com | a3-5 / a3-6 / a3-7 / a3-8 | **Ubuntu(無印) 一択 (DD-157 補遺 v1.2)** |
| third_pc | hakudoukai (third) | a3-1 / a3-2 / a3-3 / a3-4 | Ubuntu (commander 同居) |

★ main_pc 配備は `sasebo` account で実施。`hakudoukai` 切替禁止 (A001 違反) ★
★ second_pc 配備は Ubuntu(無印) distro 上で実施。新規 distro 作成禁止 (FKI-SECOND-PC-SINGLE-DISTRO-01) ★

## 7. 既知の DB constraint (script 編集時注意)

`shireiko_audit_log`:
- `judgment_level` ∈ {1, 2, 3} (integer。文字列 "warn" は 400 Bad Request)
- `result` ∈ {success, failure, partial, dry_run, escalated, detected_only}

`pc_handshake`:
- `from_pc` ∈ {main_pc, second_pc, third_pc, director, fukuincho, kuro_desktop, codex_gpt_advisor, gemini_advisor, commander}
- `to_pc` ∈ 上記 + {broadcast, all}
- `message_type` ∈ {request_permission, grant_permission, decline_permission, status_update, urgent_stop, question, answer, ack, file_sync}
- `priority` ∈ {low, normal, high, urgent}

★ 旧 commander_failsafe (May 30 〜 Jun 02) は `judgment_level="warn"` で audit row が silent fail していた (`|| true` で隠蔽)。ee4d6ce4 で integer 修正済。新規 unit は本表に合致させること。

## 8. 動作実証チェックリスト (各 PC 配備後の verify mandate)

- [ ] `systemctl --user status enter_restart_shogun_<pc>.timer` = active (waiting)
- [ ] `loginctl show-user $USER --property=Linger` = Linger=yes
- [ ] cycle 1 回手動実行 (`systemctl --user start ...`) で log file 生成確認
- [ ] log に `=== enter_restart_shogun_<pc> cycle start ===` 出力
- [ ] alive 時: `shogun-<pc> alive (elapsed=Xmin < 10min), no action`
- [ ] idle 時 label 不一致: `label_match=0 reason=...` + `result=skipped action=label_mismatch`
- [ ] idle 時 label 一致時: `C-m send rc=0` + `result=success action=enter_send` + `fires.log` に epoch INSERT
- [ ] shireiko_audit_log で event_type=`enter_restart_shogun_<pc>_fire` row 1 件以上
- [ ] pc_handshake で topic=`[enter_restart] shogun_<pc> alive: last_shogun=...` row 1 件以上
- [ ] service.err = 空 (Python traceback 無し)

## 9. 関連 commit / canon

- task YAML: `queue/tasks/ashigaru-third-1.yaml` (subtask_ee4d6ce4)
- parent handshake: shogun-third msg_20260602_160727_e56f1ee8
- 副院長令: 21e94f35 watcher 100% 完遂配下 / 司令庫 538b59ff §「番人死活監視」 / e6b027a6 [P1] 裁定1 GO + 2630d511 §「番人の番人」
- D006 5-AND: systemctl --user stop は user session lifecycle 管理ゆえ D006 射程外 (kill 経路一切不使用)
- 過去事故教訓: 2026-05-05 SecondPC 異常消費事件 (`docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md`)
