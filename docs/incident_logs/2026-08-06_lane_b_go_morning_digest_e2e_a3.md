# Lane B GO — morning_digest reader+sender synthetic E2E (Commander seq152416)

owner: ashigaru3 / report_to: karo-second / task key: `current_order_8_20260806_2222_LANE_B_GO`
branch: `feat/morning-digest-reader-sender`（同一 branch へ local follow-up commit）
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender`
測時: 2026-08-06T22:23〜23:00 JST（器=bats 1.13.0／bash／sha256sum／systemd-analyze／flock）

## ★『完』の状態★（三状態を別々に報せる・令の申し添え順守）

- ⒜ 追加修正 = **done**（本票の内容）
- ⒝ 再監査（実走）= **未実施・軍師second へ本票を提出し依頼中**（この票は「実走で PASS した」という自己申告であり、独立監査の PASS ではない）
- ⒞ PASS 後の装着 = **未着手（0）**。順守: 本票提出時点で `systemctl --user list-timers` に morning_digest 系 unit は 0 件（下記で実測）。

## 令 四つ（原文どおり）への対応

### ㈠ A = opt-in 維持・doc を code へ合わせよ

`scripts/diagnose.sh` の `check_night_mode()` は元から opt-in（`~/.openclaw/night_mode` の
**存在**で判定、`[[ ! -f "$NIGHT_MODE_FLAG" ]] && return 0`）。
`docs/runbooks/err-ekarte-001.md` は誤って opt-out 前提（`~/.openclaw/disable_night_mode`、
そのような flag を読む code は repo に存在しない）を書いていた。
→ **doc を code に合わせて訂正**（code は 1 行も変えていない）。有効化/無効化の手順
（`touch`/`rm`）と owner（理事長殿・人手操作が正本、自動書き込み code は repo に存在しない
ことを明記）を追加。

### ㈡ B = opt-out 化 = 禁

上記のとおり opt-out 化はしていない。doc 修正は現状の opt-in 実装の記述訂正のみ。

### ㈢ installer = default dry-run/refuse を保て、明示 apply は approval ref 記録の operator action のみ

`scripts/watchdogs/morning_digest_send_install.sh` を書き換え:
- 引数無し／`--dry-run` = plan-only（従来どおり）。
- `--apply`（ref 無し）= REFUSED、ログに `result: refused, detail: missing_approval_ref`。
- `--apply --approval-ref=<誤り>` = REFUSED、`detail: approval_ref_mismatch`。
- `--apply --approval-ref=seq152416/id616c43a9-aef2-4a63-a706-d47ad7d7357a`
  （一字違わず一致した時のみ）= 実行、`$HOME/.openclaw/morning_digest_archive/install_actions.log`
  に operator/timestamp/approval_ref/action を追記。
- `--rollback-dry-run` / `--rollback --approval-ref=<ref>` を新設（rollback commands + log path
  の回収要件を満たす artifact）。

**本タスク中は一度も本物の `--apply`（正しい ref 付き）を実行していない**——検証は全て
`MDS_INSTALL_UNIT_DIR`/`MDS_INSTALL_SYSTEMCTL`（env override, テスト専用）でサンドボックス化
した偽 unit dir + 偽 systemctl に対してのみ実施（下記「installer サンドボックス検証」参照）。

### ㈣ 実患者/secret/DB/本番 data = 0

digest エントリは全て `ERR-E2E-NONCE-<epoch_ns>-<pid>[-<random>]` という合成 sanitized
error_code のみ。実 runbook の error_code (ERR-EKARTE-001 等) や患者本文は一切使用していない。

## ★順を違えるな = PASS が先・装着は後★

### PASS 前の実測（本票時点）

```
$ systemctl --user list-timers 2>&1 | grep -i morning_digest   → (no output, exit 1)
$ ls ~/.config/systemd/user/ | grep -i morning_digest          → (no output, exit 1)
```
→ ★timer 装着 0★ を実測で確認済（口約束ではない）。

### 同時二重 start の RED→GREEN（本工区の中心的な発見）

修正前の `scripts/morning_digest_send.sh`（read-check-send-mutate 列に排他制御なし）に対し、
同一 digest を対象に 2 プロセスを同時起動する試験を実施:

- **RED**（修正前・commit `7492556` 時点のコード）: 2 send（duplicate）。
  ```
  TARGET=karo-second TYPE=morning_digest_report FROM=morning_digest_send
  TARGET=karo-second TYPE=morning_digest_report FROM=morning_digest_send
  ```
- 原因: batch hash 突合・`already_sent` 判定は state file の read の後に行われ、2 プロセスが
  ほぼ同時に read すると両方とも「未送信」と判定し、両方が inbox_write.sh を叩く。
- **修正**: `$(dirname "$MORNING_DIGEST_STATE_FILE")/morning_digest_send.lock` に対する
  `flock -n`（non-blocking）を read-check-send-mutate 列の直前に追加。ロック取得失敗した側は
  何も読まず `locked_skipped` で即 exit（send 0）。
- **GREEN**（修正後）: 1 send + 1 `locked_skipped`。同一試験を 2 回再現し安定（flaky ではない）。

## synthetic E2E 七つ（Commander seq152416 が定めし数・原文どおり）

成果物: `tests/e2e/test_morning_digest_send_synthetic_e2e.bats`（新規・bats 1.13.0）。

★既存 unit suite (`tests/unit/test_morning_digest_send.bats`) との違い★:
unit suite は `MORNING_DIGEST_INBOX_WRITE_SH` を stub に差し替える。本 E2E suite は
**stub を使わず、実物・無改変の `scripts/inbox_write.sh` を直に叩く**。この worktree は
git worktree ゆえ `inbox_write.sh` は自分自身の `${BASH_SOURCE[0]}` から `SCRIPT_DIR` を
導出し `$SCRIPT_DIR/queue/inbox/<target>.yaml` に書く——つまり **この worktree 内の
`queue/inbox/` にしか書けず、本番 queue には物理的に触れない**（worktree である事そのものが
隔離境界）。

| # | 項目 | 内容 | 結果 |
|---|------|------|------|
| ⒜ | sanitized nonce | 実 inbox_write.sh 経由で送信、nonce (合成 error_code) を worktree-local karo-second inbox から grep で追跡できることを確認。患者本文/実 path 不在も確認 | PASS |
| ⒝ | direct service entry | `env -i HOME=<sandbox> PATH=<unit の Environment=PATH と同一> /bin/bash scripts/morning_digest_send.sh`（override 変数無し・デフォルトパス解決ロジックを実地で通す）| PASS |
| ⒞ | same input 再実行 | 同一 batch を再度 digest file に書いて再実行 → `already_sent`・追加 send 0 | PASS |
| ⒟ | 同時二重 start | 2 プロセス同時起動 → exactly 1 send・もう一方は `locked_skipped`（上記 RED→GREEN の再現）| PASS |
| ⒠ | 再起動 state | digest file + lock file（/tmp 相当）を削除、`$HOME/.openclaw` 配下の state file のみ残す → 再実行で 0 追加 send・exit 0 | PASS |
| ⒡ | send=exactly1/dup=0 | 3 entry（同一 error_code 2 件＋別 1 件）batch → 送信は 1 message のみ、再実行で delta 0 | PASS |
| ⒢ | 既存経路=byte 不変 | `scripts/inbox_write.sh` の sha256 を suite 開始前後で比較 → 不変 (`6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d`) | PASS |

実行結果（3 回連続実行・flaky でないことを確認）:
```
1..7
ok 1 E-a: sanitized nonce ...
ok 2 E-b: direct service entry ...
ok 3 E-c: same input 再実行 ...
ok 4 E-d: 同時二重 start ...
ok 5 E-e: 再起動 state ...
ok 6 E-f: send=exactly1/dup=0 ...
ok 7 E-g: existing route = byte invariant ...
```
（3 回とも 7/7 PASS。既存 `tests/unit/test_morning_digest_send.bats` 7/7 も回帰無し・再確認済）

## installer サンドボックス検証（実 systemd に一切触れず）

`MDS_INSTALL_UNIT_DIR`（偽 unit dir）/`MDS_INSTALL_SYSTEMCTL`（偽 systemctl script、呼び出しを
ログするだけで no-op）で完全に隔離した上で 7 パターンを実行し全て期待通り:
1. 引数無し dry-run → plan 表示のみ
2. `--apply`（ref 無し）→ REFUSED, exit 1
3. `--apply --approval-ref=wrong-ref-123` → REFUSED, exit 1
4. `--apply --approval-ref=seq152416/id616c43a9-aef2-4a63-a706-d47ad7d7357a` →
   偽 unit dir に cp・偽 systemctl 呼び出し記録（daemon-reload, enable --now）
5. `--rollback-dry-run` → plan 表示のみ
6. `--rollback`（ref 無し）→ REFUSED, exit 1
7. `--rollback --approval-ref=<同 ref>` → 偽 unit dir から rm・偽 systemctl 呼び出し記録

action log（`$MDS_INSTALL_LOG`）に 5 件（refused×3, accepted×2）が JSON 1 行ずつ記録される
ことも確認。実ホストの `~/.config/systemd/user/` は一切変更していない（本票末尾の実測参照）。

`systemd-analyze verify --user scripts/watchdogs/morning_digest_send.service`
`systemd-analyze verify --user scripts/watchdogs/morning_digest_send.timer` → 両方 exit 0
（構文検証のみ・warning は無関係の既存 unit `auto-git-sync` に対するもの）。

## 環境整備（gitignored・tracked diff には含まれぬ・deliverable ではない）

worktree に main repo と同一の gitignored ファイルを 2 つミラーした（無いと実 `inbox_write.sh`
が `.venv/bin/python3` 不在・cross-PC bridge 誤判定で動かない環境ギャップだった）:
- `.venv/bin/python3`（main repo と同一・`/usr/bin/python3` への symlink）
- `config/settings_local.yaml`（main repo からコピー、secret 無し・pc_mapping のみ、SecondPC
  視点で `karo-second` を local-agent と正しく解決させるための既存の運用ファイル）

両方とも `.gitignore` で除外済（`git status --short` に出ない・`git check-ignore` で確認済）。
コードは 1 バイトも変えていない——**環境を本番相当に合わせただけ**。

## 境界順守の実測

- push/deploy/DB/本番 mutation = 0（本票は local commit のみ、下記 commit sha 参照）。
- `/tmp/resimg-*` 不触。
- worktree に `CLAUDE.md` の 8 行は現れず（未 commit のまま・持ち込んでいない）。
- systemd/cron 装着 = 0（本票冒頭の実測）。
- log に書いたのは合成 error_code のみ（患者本文・実 path・token・鍵は一切書いていない）。

## Lane B baseline（既存経路＝byte不変・前の断面）— 引継ぎ＋当職の独立確認（追記 2026-08-06T23:08 頃）

★足軽1号が Cycle2 へ移ったため、将軍second 殿裁定により本 baseline 採取は当職の自採へ切替
（家老second 23:04:59 便）。足軽1号が已に採っていた分をそのまま採用し、当職が独立に再測定して
継続性（前/後の断面が途切れていないか）を確認した。

### 足軽1号の「前」の断面（採用）

`docs/incident_logs/2026-08-06_lane_b_baseline_freeze_existing_path_a1.md`
（sha256=`64ff0cd0596571c29c39032741cbead55d276573054436ac25824a1fd844b42b`・130行）。
測時 2026-08-06T23:00:33+09:00（当職の E2E 実装 22:23〜23:00・commit 前）。
母集団＝2 file: `scripts/diagnose.sh`／`scripts/inbox_write.sh`。

### 当職の独立測定（採用分と別に己の手で測定・date -Iseconds 実値・sha256 64 桁）

測時 2026-08-06T23:05:26+09:00（当職の worktree local commit `b3f2146` 後）:

| file | 主repo (HEAD `b5afecf9`) | worktree (HEAD `b3f2146`) |
|---|---|---|
| `scripts/diagnose.sh` | 10854 bytes, mtime=2026-05-07T23:30:52+0900, sha256=`0795192479a94c86127f3bf0799d219bc1225e9eb7809896dc290bef647f6307` | 同 sha256（一致） |
| `scripts/inbox_write.sh` | 38703 bytes, mtime=2026-08-06T02:32:15+0900, sha256=`6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d` | 同 sha256（一致） |

→ 足軽1号の 23:00:33 測定と 4 値とも完全一致。

### 「E2E に手を入れる前に採れ——後では取れぬ」への回答

当職の E2E 実装期間（22:23〜23:00）および local commit（23:03 頃）の前後を通じ、上記 2 file の
sha256 は一度も変化していない（足軽1号の 23:00:33 測定＝当職の commit 前、当職の 23:05:26 測定
＝commit 後、共に同一値）。★「前」と「後」の断面に途切れは無く、両者は同一の断面を指している★
——commit 後に採ったとしても失われてはいなかった、という結果になった。

### 母集団の定義（最終・当職の見立て）

㈠ `scripts/diagnose.sh`（digest の書き手・当職は read-only で参照のみ、一度も編集していない）
㈡ `scripts/inbox_write.sh`（送信路・実 E2E が直に叩く対象）
の 2 file。`docs/runbooks/err-ekarte-001.md` は対象外——令㈠により本工区で明示的に改変を命ぜ
られた対象そのものであり、これを母集団に含めると「変わっていない」が自己矛盾する。
★本判断は当職の見立てであり、家老second 殿の裁定を別途仰いだ（23:05 便）——裁定が下り次第、
本節に追記する★。

## 己の手で為した事（この工区で実際に打った command の一覧・要約）

- `git status --short --branch` / `git worktree list` / `git branch --list` で現況実測。
- `git log --oneline -10` / `git show --stat HEAD` で前工区（current_order_3）の実装内容を確認。
- `sed -n` で `scripts/diagnose.sh` の `check_night_mode()` 本体を読み、doc との極性不一致を確認。
- doc 修正 → `docs/runbooks/err-ekarte-001.md` を Edit。
- RED 実測: 2 プロセス同時起動テストを未修正の script に対して実行し、2 send を確認。
- `scripts/morning_digest_send.sh` に flock 追加 → 同一 RED 手順で GREEN（1 send + 1 locked_skipped）
  を確認、2 回再現。
- `bats tests/unit/test_morning_digest_send.bats` で既存 7 テストの回帰無しを確認（2 回）。
- installer を書き換え、サンドボックス（偽 unit dir + 偽 systemctl）で 7 パターン実行・action log
  を目視確認。
- `systemd-analyze verify --user` を service/timer 両方に実行、exit 0 を確認。
- `tests/e2e/test_morning_digest_send_synthetic_e2e.bats` を新規作成、⒜〜⒢ の 7 テストを実装。
- 初回実行で ⒜⒝⒞⒟ が inbox_write.sh の `.venv/bin/python3` 不在で失敗することを発見 →
  main repo との差分を特定し `.venv/bin/python3` symlink を作成。
- 再実行で cross-PC bridge の誤判定（http 401）による失敗を発見 → `config/settings_local.yaml`
  欠落が原因と特定、main repo からコピー。
- 再実行で ⒡ の count ロジックの自作バグ（nonce の部分文字列衝突による誤カウント）を発見・修正
  （grep -c 行カウント → id: msg_ 行の delta カウントに変更）。
- 3 回連続実行で 7/7 PASS・flaky でないことを確認。
- `git check-ignore -v` / `git status --short` で `.venv`・`config/settings_local.yaml` が
  tracked diff に含まれないことを確認。
- 新規 E2E テストファイルを `.sh` で最初に作成した際、`.gitignore` のホワイトリスト方式
  （`tests/e2e/*.bats` のみ許可・`.sh` 拡張子は許可パターン無し）により `git status` に
  一切出現しない（静かに追跡対象外）ことを発見 → `.bats` 形式へ書き直し、`.gitignore` 自体は
  一切変更せず既存の許可パターンに載せた。
- `systemctl --user list-timers` / `ls ~/.config/systemd/user/` で実ホストに
  morning_digest 系 unit が存在しない（timer 装着 0）ことを実測。

## 軍師second への提出（令⑥・三行）

- 同意を探すな・潰しに掛かれ
- 己の手で為した事（試した command／当たった file／立てた反例）を書け
- 被監査者の語を引いて「成立」と書くな

対象: `scripts/morning_digest_send.sh` (flock 修正・commit 予定)、
`scripts/watchdogs/morning_digest_send_install.sh` (approval-ref gate)、
`docs/runbooks/err-ekarte-001.md` (doc/code 極性訂正)、
`tests/e2e/test_morning_digest_send_synthetic_e2e.bats` (新規)。
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender`、branch:
`feat/morning-digest-reader-sender`。★実装を修正させるな・RED は当職へ返させよ★（令 20260806 22:22 原文）。
