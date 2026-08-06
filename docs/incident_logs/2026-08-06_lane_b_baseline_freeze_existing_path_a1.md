# Lane B 受入条件⒢「既存経路＝byte不変」— 『前』の断面凍結（足軽1号）

- 下命: 家老second msg_20260806_225521_27a8f102（task YAML key `current_order_11_20260806_225400_LANE_B_BASELINE_FREEZE`）
- 出所: Commander seq152416 synthetic E2E 七つの内の⒢
- 測時（本票起筆）= 2026-08-06T22:57:41+09:00（`date -Iseconds` 実行結果）
- 測時（本測定実行）= 2026-08-06T23:00:33+09:00 〜 2026-08-06T23:00:33+09:00（`date -Iseconds` 前後計測・ドリフト0秒）

## ⒜ 母集団（既存経路＝何を「既存経路」と見たか）

**根拠**: 足軽3号の票 `docs/incident_logs/2026-08-06_morning_digest_reader_sender_impl_a3.md` の以下二文：
> 「`scripts/diagnose.sh` の `MORNING_DIGEST=...` と同一 path を読む（**既存の書込側 `diagnose.sh` は1行も変更していない＝byte不変**）」
> 「送信は既存の `scripts/inbox_write.sh` を**そのまま呼ぶだけ**（此方も1行も変更していない）」

∴ 足軽3号本人が「byte不変」と明示的に主張した対象＝以下2 file を母集団とした。

**裏取り（当職の実測・票に書かれた主張を鵜呑みにせず自分で確認）**:
1. `git -C /tmp/hakudokai-worktrees/morning-digest-reader-sender status --short -- scripts/diagnose.sh scripts/inbox_write.sh` → **出力0行**（worktree内で未変更を確認）
2. 主 repo（現HEAD `b5afecf9`・branch `feat/dd169-d006-conditional-exception`）と base_commit `4061f26` の間で
   `git diff --stat 4061f26 HEAD -- scripts/diagnose.sh scripts/inbox_write.sh` → **出力0行**（主repo側でも base 以降不変を確認）
3. `scripts/morning_digest_send.sh`（新規file・committed版）の全文を `grep -n "scripts/\|\.openclaw\|/tmp/"` した結果、
   既存fileへの参照は `scripts/diagnose.sh`（コメント内・言及のみ）と `scripts/inbox_write.sh`（呼出先変数 `MORNING_DIGEST_INBOX_WRITE_SH`）の**2件のみ**。他の既存scriptへの参照は0件。
4. `/usr/bin/grep -rln "diagnose\.sh" --include="*.sh" --include="*.service" --include="*.timer" .`（主repo・`.git`除く）→ **ヒットは `scripts/diagnose.sh` 自身のみ**＝diagnose.shを呼ぶ既存watchdog/service/timerは0件（`scripts/watchdogs/` 配下に diagnose 関連 file 0件・`systemctl --user list-timers --all` にも diagnose 関連 timer ヒット0件）。

∴ 母集団＝**2 file**（`scripts/diagnose.sh`／`scripts/inbox_write.sh`）。之を上回るfile（例: diagnose.shを起動するwatchdog）は実測で**存在しない**ことを確認した上での2件確定であり、探索不足による2件ではない。

## ⒜ 全件一覧（path／size／mtime／sha256＝64桁）

### 主 repo（`/home/hakudokai/projects/multi-agent-shogun`・branch `feat/dd169-d006-conditional-exception`・HEAD=`b5afecf94967b0129233c4e8192ed9eb330a05cc`）

| path | size(bytes) | mtime | sha256（64桁） |
|---|---|---|---|
| `scripts/diagnose.sh` | 10854 | 2026-05-07T23:30:52.110468307+09:00 | `0795192479a94c86127f3bf0799d219bc1225e9eb7809896dc290bef647f6307` |
| `scripts/inbox_write.sh` | 38703 | 2026-08-06T02:32:15.826737498+09:00 | `6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d` |

### worktree（`/tmp/hakudokai-worktrees/morning-digest-reader-sender`・branch `feat/morning-digest-reader-sender`・HEAD=`7492556ae5f6df274a181f826e991790f6cbf125`）

| path | size(bytes) | mtime | sha256（64桁） |
|---|---|---|---|
| `scripts/diagnose.sh` | 10854 | 2026-08-06T21:33:35.152074255+09:00 | `0795192479a94c86127f3bf0799d219bc1225e9eb7809896dc290bef647f6307` |
| `scripts/inbox_write.sh` | 38703 | 2026-08-06T21:33:35.156074274+09:00 | `6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d` |

**確認**: 主repo と worktree で sha256 完全一致（2 file とも）。mtime は異なる（worktree作成時のcheckoutでmtimeが打ち直されるのは正常）が、**中身は同一**。∴ 本測時点で「既存経路＝byte不変」は成立している。

### 参考（git blob hash・sha256とは別種・base_commit `4061f26128a3c824061f941b746c1bfdff2b76fd` 側）
- `scripts/diagnose.sh` blob=`42e882ef6d8f3a6e5d5fdf6cbca0746479d7fe85`
- `scripts/inbox_write.sh` blob=`7ee9ad90f220f62176db1a17cad86d5a8558f9ab`
（git blob hashはsha1・object形式が異なるためsha256と直接比較不可。上表のsha256を一次証拠とする。）

## ⒝ 断面の刻

測定は `date -Iseconds` の実値のみを用いた（丸め0件）。上記表中の mtime は `stat -c '%y'` の生出力（ナノ秒まで）をそのまま記載。測定の呼出は2026-08-06T22:59:48+09:00〜23:00:33+09:00の間に複数回行い、**全て同一sha256**（ドリフト0）を確認した。

## ⒞ 写しについて

**repo外（`/tmp` 等）へのfile copyは作成していない**。凍結の証跡は本票に記した sha256（指紋）のみであり、file実体の複製は行っていない（令⒞順守）。

## ⒟ 判らぬ（第四値）— 既存経路か判じ得ぬ物

以下は「既存経路」の母集団判定には**含めなかった**が、測定中に発見した事実であり、判断材料として別枠で記す。

1. **`docs/runbooks/err-ekarte-001.md`**（主repoのbase_commit `4061f26` 時点で既に存在＝pre-existing file）が、
   worktree内で**未commitのまま変更中**（`git status --short` → ` M docs/runbooks/err-ekarte-001.md`）。
   diff内容＝night_mode flagの実装（opt-in／`~/.openclaw/night_mode` 存在判定）を正しく記述する訂正（旧記述の誤りを是正）で、
   **コード経路ではなくdocument**。足軽3号の票にはこのfileへの言及が一切無い（票がcommit後の内容のみを報告しているため）。
   ∴ 「既存経路（＝コードのbyte不変を問う対象）」に含めるべきかは**当職には判じ得ぬ**——document訂正であり実行時の入出力に影響しないと考えるが、断定はしない。第四値として挙げる。
2. 上記1と合わせ、worktree内には他に `scripts/morning_digest_send.sh`（committed版から**さらに14行追加**の未commit変更）・
   `scripts/watchdogs/morning_digest_send_install.sh`（**さらに107行追加/22行削除**の未commit変更）も存在するが、
   **両方とも新規追加file（母集団の対象外）ゆえ「既存経路」の判定には影響しない**。参考として記す。

## ★重要な時系列所見（当職が実測して初めて気付いた事）★

worktree内のmtimeを実測した結果、以下が判明した：

| 事象 | mtime／刻 |
|---|---|
| 本工区の下命（家老second→当職） | 2026-08-06T22:54:00〜22:55:21+09:00 |
| `docs/runbooks/err-ekarte-001.md` 変更 | 2026-08-06T22:31:42+09:00（**下命より前**） |
| `scripts/morning_digest_send.sh` 追加編集 | 2026-08-06T22:32:10+09:00（**下命より前**） |
| `scripts/watchdogs/morning_digest_send_install.sh` 追加編集 | 2026-08-06T22:33:27+09:00（**下命より前**） |
| `tests/e2e/test_morning_digest_send_synthetic_e2e.bats`（新規・未commit） | 2026-08-06T22:58:02+09:00（**当職の測定作業中に発生**） |

∴ 足軽3号は下命（22:54/22:55）より**前**（22:31〜22:33）に既にdocs訂正と追加編集へ着手しており、
かつ当職が本票を書いている最中（22:58:02）に**E2E test fileを新規作成**した形跡がある
（家老second令の「急ぎ＝足軽3号がLane BのE2Eに入る前でなければ価値が半減」の想定していた事態に、
本測定はほぼ間に合ったが、猶予は極めて短かった）。
**但し母集団の2 file（diagnose.sh／inbox_write.sh）自体はこのE2E着手の後（23:00:33測定）も byte不変のままであることを確認済**——
∴ ⒢の凍結断面としては本票の値を『前』として有効に使えると判ずる。

## 己の手で為した事（証跡コマンド）

```
tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}'                              # ashigaru1 確認
cat queue/tasks/ashigaru1.yaml                                                       # 本工区の原文確認
cat queue/inbox/ashigaru1.yaml                                                       # 下命便の原文確認（未読1件をflockでread=True化）
cat docs/incident_logs/2026-08-06_morning_digest_reader_sender_impl_a3.md            # 母集団判定の根拠読了
git -C /tmp/hakudokai-worktrees/morning-digest-reader-sender status --short --branch # worktree現況（読取のみ）
git -C /tmp/hakudokai-worktrees/morning-digest-reader-sender rev-parse HEAD          # worktree HEAD確認（読取のみ）
git diff --stat 4061f26 HEAD -- scripts/diagnose.sh scripts/inbox_write.sh           # 主repo側 byte不変の裏取り（読取のみ）
git -C /tmp/hakudokai-worktrees/morning-digest-reader-sender diff --stat -- docs/runbooks/err-ekarte-001.md scripts/morning_digest_send.sh scripts/watchdogs/morning_digest_send_install.sh  # worktree内 未commit差分の把握（読取のみ）
sha256sum scripts/diagnose.sh scripts/inbox_write.sh                                 # 主repo sha256
sha256sum /tmp/hakudokai-worktrees/morning-digest-reader-sender/scripts/{diagnose.sh,inbox_write.sh}  # worktree sha256
stat -c 'size=%s mtime=%y' <対象file>                                                # size/mtime実測（両側）
git rev-parse 4061f26...:scripts/diagnose.sh / :scripts/inbox_write.sh               # git blob hash参考値（読取のみ）
/usr/bin/grep -rln "diagnose\.sh" --include="*.sh" --include="*.service" --include="*.timer" .  # diagnose.sh呼出元の全数探索
crontab -l / systemctl --user list-timers --all                                      # cron/systemd未装着の確認（起動・変更は一切せず）
ls /tmp/morning_digest.json / ls ~/.openclaw/night_mode                              # 実行時data fileの不在確認（読取のみ）
date -Iseconds                                                                       # 全測時点で実行
```

**実行しなかった事（禁の順守）**: worktreeへのcommit＝0件・branch書換＝0件・主repo HEADの移動＝0件・
実装追加＝0件・systemd/cron/timer操作＝0件（読取のみ・起動/停止/install一切せず）・`slim_yaml.sh` 実行＝0件。

## 令④（数の扱い）

令には「対象2 file」という事前の数は書かれておらなんだが、当職が実行の刻に母集団を導出した結果は**2 file**であった
（上記「⒜ 母集団」節に導出過程を明記）。増減があれば数え直した方を採る旨、本票がその記録である。

## 発注三行（軍師second 提出時 必須）

1. 同意を探すな・潰しに掛かれ。
2. 返信に己の手で為した事（試した command／当たった file／立てた反例）を書け。
3. 被監査者（当職）の語を引いて「成立」と書くな——引くなら己が引き直したと明記せよ。

## 渡し先・報告

- **渡し先**: 足軽3号（Lane B owner）— 出来次第 直に渡す。
- **申し伝え**: 足軽3号にも「己で測れ」と伝える——当職の数を唯一の根拠とせぬこと。
- **監査体制**: 暫定二者制（軍師second + Gemini）。Codex leg 停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。

report_to: karo-second
