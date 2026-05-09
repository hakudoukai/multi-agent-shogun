# scripts/redundancy — 冗長化・監視スクリプト群

## 概要

このディレクトリは Shogun Newbuild システムの冗長化・監視インフラを格納する。

## スクリプト一覧

### shogun_report_watcher.sh

auditor report YAML の変更を監視し、将軍 (shogun) inbox に通知する daemon。

**特徴**:
- inotify イベント駆動 (polling なし)
- dedup + cooldown (60s) + pending_checksum による確実な後送
- singleton flock で多重起動防止
- cycle4 (HND-SRW-C5): coproc builtin で inotifywait を起動、EXIT trap で fd close による graceful 終了

**監視対象 (WATCH_REPORTS — 編成 v1.1)**:
- `kuroda_report.yaml` (黒田官兵衛 / gunshi, MainPC)
- `takenaka_report.yaml` (竹中半兵衛 / gunshi2, MainPC)
- `naomasa_report.yaml` (井伊直政 / SecondPC gunshi)
- `acha_report.yaml` (茶々 / SecondPC gunshi2)
- `ieyasu_report.yaml` (徳川家康 / 副将軍, SecondPC)
- `honda_report.yaml` (本多忠勝 / SecondPC Karo)

**起動方法**:
```bash
nohup bash scripts/redundancy/shogun_report_watcher.sh >> logs/shogun_report_watcher.log 2>&1 &
```

**停止方法**:
- `watcher_supervisor.sh` が自動再起動を管理しているため、supervisor を止めてから `kill $(pgrep -f shogun_report_watcher.sh)` (shogun のみ実行可)
- D006 制約のため agents は kill 系コマンド不可

**ログ**: `logs/shogun_report_watcher.log`

---

### test_shogun_report_watcher.sh

shogun_report_watcher.sh のスモークテスト (bats 不使用、bash スクリプトによる unit test)。

**実行**:
```bash
bash scripts/redundancy/test_shogun_report_watcher.sh
```

**要件**: SKIP 0 件必須 (テストルール §1)

---

## 旧 activity_monitor について

`hakudokai_activity_monitor.sh` (旧 repo: `/mnt/c/Users/User/projects/multi-agent-shogun/`) は
Phase γ 移行後に shogun_report_watcher.sh に置き換えられた。

**停止方法 (D005/D006 制約下)**:
```bash
touch ~/.openclaw/disable_activity_monitor
# → 最大 30s 以内に graceful exit (Phase γ migration フラグ対応済)
```

**起動元**: PPid=1 (systemd orphan)。cron / systemd unit 未確認 — 自然 exit 待ち。

---

## 関連ファイル

- `scripts/watcher_supervisor.sh` — inbox_watcher + shogun_report_watcher の自動起動・再起動管理
- `queue/reports/*.yaml` — 監視対象 report ファイル
- `logs/shogun_report_watcher.log` — watcher ログ
