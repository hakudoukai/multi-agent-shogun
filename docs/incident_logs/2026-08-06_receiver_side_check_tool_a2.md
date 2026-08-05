# 【乙】受信面の点検の道具化 (足軽2号)

工区= msg_20260806_022518_aa44a960 (将軍second 発令・家老second 中継)。
道具本体= `scripts/karo_second_reception_check.sh`。

## 断面 (先出し・秒単位)

- 測定時 HEAD = `60c1c8bfb47657a337a854da52948b203aec791a`
- 測時 = 2026-08-06T02:50:46+0900 (機械・`date`実測)
- 道具 file: `scripts/karo_second_reception_check.sh` 198行 sha256=`76b29e3185c42420587ad28d9f55f3e1e1eecf026127a58f5121eb973996d1aa`
- ★本工区は /clear を挟んでおり、道具本体は前 session が起草済 (scratchpad 生成 02:40 実測)。本票は当 session が★実行・再検証★した結果である★

## 経緯 (compact/clear をまたいだ確認)

1. 復帰後 `queue/tasks/ashigaru2.yaml` + inbox を読み、本工区が現工区であることを確認。
2. 道具 file が既に `scripts/karo_second_reception_check.sh` として存在し、ヘッダに ⒜〜⒡ の設計根拠が既述されていることを確認 (前 session の成果物)。
3. 当 session はこれを★書き換えず★、実行して当 session の目で再検証した (道具の中身を信じず走らせて確かめる、という本日一貫した方針に従う)。

## ⒜ 既存探索 (道具ヘッダに記載済・当職が再確認)

- `scripts/agent_status.sh`: busy/idle + task_id + unread件数は出すが、SKIP/escalation/log在り処/最古未読は出さない (実読して確認)。
- `scripts/agent_health_check.sh`: inbox unread>10 の閾値検知はあるが MainPC pane 固定・SecondPC 単体点検の道具ではない。
- `lib/_section18_roles.sh` の `SECTION18_SECONDPC_PANE_ORDER` は旧構成 (maeda/ashigaru5-8) を保持しており現行 `queue/pane_registry.yaml` と不一致 (型①旧版残存) — ∴ 本道具は roster を pane_registry.yaml から動的取得し、この配列を参照しない。
- ∴ 既存に「同じ事をする物」は無く、新規作成は Anti-Duplication に抵触しない。

## ⒝〜⒡ 実行結果 (当 session が再走査)

```
$ bash scripts/karo_second_reception_check.sh
測時=2026-08-06T02:49:00+0900  母集団=9名 (pane_registry.yaml pc=SecondPC かつ karo-second/shogun-second除外)

Agent          SKIP     busy       未読  最古未読
ashigaru1      26       稼働中     0     -
ashigaru2      48       稼働中     1     2026-08-06T02:48:12
ashigaru3      44       稼働中     0     -
ashigaru4      21       待機中     0     -
ashigaru5      302      待機中     0     -
ashigaru6      224      待機中     0     -
ashigaru7      250      待機中     0     -
gunshi-second  1227     待機中     1     2026-08-06T02:47:37
honbucho       -        待機中     0     -

⒟ 判定: 組合せ成立 0件
```
(列を省略・全文は当日実行ログとして再現可。上表は SKIP/busy/未読/最古未読のみ抜粋)

## 検算 (道具の出力を信じず実測)

- `ashigaru2` の SKIP=48 を `grep -c '\[SKIP\]' logs/inbox_watcher_ashigaru2.log` で直接再計測 → **48 で一致**。
- `gunshi-second` の SKIP=1227 (道具実行時) を約100秒後に再計測すると 1230 (live 増分3件・ログが稼働中ゆえの想定内ドリフト、道具の欠陥ではない)。
- ∴ SKIP件数の抽出ロジックは正しい。

## ★重大所見★ — 道具自身が gitignore silent drop の対象だった

```
$ git check-ignore -v scripts/karo_second_reception_check.sh
.gitignore:7:*    scripts/karo_second_reception_check.sh   (exit=0)
$ git status --porcelain --ignored=matching -- scripts/karo_second_reception_check.sh
!! scripts/karo_second_reception_check.sh
```

★本道具は commit されておらず、`.gitignore:7` の `*` whitelist方式によって★無警告で git 管理外★になっている★ (memory: `gitignore-whitelist-silent-drop` と同型)。
これは a1 が起草中の「00E gitignore silent drop 門」設計 (commit b13dc3d/f362fb6/de52257/16e76f6/6a8be08) が対象としている★当の欠陥の新規実例★である。

**∴ 当職は .gitignore を自ら書き換えない** (00E の先例は委員長殿裁可を経て個別 file 名指しで whitelist しており、当職が独断で真似れば二重実装かつ越権になる)。∴ 本件は家老second へ報告し、00E ラインへの追加対象として合流を委ねる。

### 併せて実測した範囲 (scope=`scripts/` 直下・00E 台帳への入力・裁定はしない)

```
$ git status --porcelain --ignored=matching -- scripts/ | grep '^!!'
```
の実行で、`.bak*`/`__pycache__` を除く★実体のある非バックアップ file★ が本道具の他に 10件見つかった (`alive_to_productive_monitor_v0_2_once.sh` / `design-pipeline/design_pipeline.sh` 他2本 / `karo_second_send_iincho.sh` (W25成果物・同じ穴) / `read_pruned_archive.sh` / `setup_shogun_sc.sh` / `setup_shogun_standard.sh` / `shogun_self_check.sh` / `test_secondpc_monitor_v2.py`)。
★列挙のみ・裁定・優先順位付けはしない★ (a1 の 00E 台帳の射程・Anti-Duplication)。

## ⒞ log 在り処の限界 (honbucho)

`honbucho` は watcher process の argv 突合で pid が1件解決したが、その fd1/fd2 は共に socket (`socket:[25533422]`) であり、通常ファイルではない。∴ SKIP/escalation は `-` のまま (推測で埋めない・第四値扱い)。名前で決め打たず `/proc/<pid>/fd/*` を辿った結果として正しく「未解決」を出力しており、道具の欠陥ではなく honbucho 側のログ出力方式 (journald/systemd 経由の可能性) に起因する構造的限界と見る。

## ⒠ / ⒡ 確認

- process 解決は `/proc/[0-9]*/cmdline` を全数列挙し argv を厳密突合 (`pgrep -f` 等の名前一致は不使用・道具本体コードで確認)。
- 本 file 実行中に発行したコマンドは `bash scripts/karo_second_reception_check.sh` (読取のみ) と検算用 `grep -c` のみ。停止・再起動・kill 系コマンドは一切発行していない。

## 対に成る他工区

★本工区と対に成る物★= 前工区「commit自己申告の検算」(msg_20260806_021824_6383312a・完了済・commit 2141617) — 同じ「道具の出力を信じず実測する」姿勢の連続。他に探した範囲=当職の inbox 履歴・docs/incident_logs 当日分。他に対と呼べる工区は見当たらず。

## 本工区で己が直した誤り

無し (道具本体は前 session の起草物であり当 session は書き換えていない。当 session の寄与は★実行・検算・gitignore drop の発見★のみ)。
