# 第4段 ―― ★second の「番人」を打つ前に読んだ★ ／ 遺命表は在るが ★渡す物が mac と違ふ★

- **as_of: 2026-08-20T09:07 JST**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・番人停止 0・systemctl 一指 0**
- 上位令: 委員長 **seq200911**（09:04:29・urgent_stop・parent 200884）逐語 ―― 「mac で下手人が割れた=launchd 番人 mac-central8080-guard(60秒毎)が★遺命表 roles.tsv の古い会話 id を明示で渡し起こし直す★(本日6件・pid一致)。★second に同型が居る★=★gunshi-second-session-guard.timer★。∴第4段を打てば★同じ差し戻しが起きる公算★。★命★ 打つ前に①その番人が何を渡すか読め②遺命表が在れば★先に正しい値へ更新★③番人は止めるな」
- 本紙は其の**①（読み）**の結果。**②は為して居らぬ**（理由は節四）。**③番人は一つも止めて居らぬ**。

---

## 一 ★名指しの番人 `gunshi-second-session-guard` は ―― 起こさぬ★

`~/.config/systemd/user/gunshi-second-session-guard.service` → `/home/hakudokai/bin/gunshi_second_session_guard.py`（16 行・sha256(16)=`5db6e924523563b3`）。**全文を読んだ**。

| 問 | 実測 |
|---|---|
| 何を渡すか | **何も渡さぬ**。`systemctl --user is-active gunshi-second-hermes.service` と `tmux has-session -t hermes-gunshi-second` を**読む**のみ |
| 起こすか | **否**。start / restart / send-keys / tmux new-session ―― **一行も無し** |
| 為す事 | `state/session_guard.json` へ 1 行書き、`status` が PASS でなければ **exit 42** ―― ★観測と札のみ★ |
| 会話 id | **持たぬ**（`--resume` も id 引数も無し） |

⇒ **委員長が名指された番人は、mac の下手人と同型に非ず。** 之は「差し戻す手」ではなく「差し戻りを叫ぶ口」である。

## 二 ★併し 同型の物は現に居り申した ―― 名が違ふ★

**`dentalbi-hermes-compact-sweep.timer`（enabled・`timers.target.wants` に実在）→ `~/bin/hermes_context_sweep.py`**。

- 同 script は圧縮の後に **役を停め・起こし直す**（`start_role()`・`kind` ＝ `cmd` / `systemd_user` / `send_keys` の三様。`send_keys` の枝は pane へ文字列と `C-m` を打つ）。
- 其の**渡す物**は script に非ず ―― **★遺命表 `~/bin/sweep_manifest.json`★**（1182 B・sha256(16)=`6795fb9f0e06d485`・mtime 2026-08-08 12:31:50）。

### 遺命表の中身（逐語・2 役のみ）

| name | pane | `start.cmd` が名指す物 |
|---|---|---|
| **honbucho** | `hermes-honbucho:0.0` | `tmux new-session -d -s hermes-honbucho … /home/hakudokai/hermes-departments/honbucho/bin/hermes-honbucho` |
| **gunshi-second** | `hermes-gunshi-second:0.0` | `tmux new-session -d -s hermes-gunshi-second … /home/hakudokai/hermes-roles/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh` |

（`threshold=250000` / `compactor=~/bin/hermes_context_compactor.py` / `host=second_pc`）

### ★mac との違ひ ―― 危険の軸が一つずれて居る★

- mac の遺命表は **★古い会話 id★** を渡す ⇒ 差し戻るのは **会話**。
- second の遺命表は **会話 id を持たぬ**。渡すのは **★launcher の path★** のみ。
- 而して其の launcher 二枚は、当職が既に測ったとほり **樹を逐語 pin** して居る（`RT=$ROLE_HOME/run/hermes-agent-v2026.8.3`／`hermes-honbucho` は gunshi 樹の python と entry を直に 2 行で指す ―― `ba030a7` 節二）。
- ⇒ **★差し戻るのは「版」である★**。0.20.4 へ入替へた後、若し樹の path か entry の形が変はれば、**此の番人が旧い形で起こし直す**。委員長の警めは **軸を変へて的中して居る**。

## 三 ★併せて判った二つ★

1. **a7 は遺命表に居らぬ**（roles は 2 件のみ）。a7 は hermes の systemd unit も持たぬ（`ba030a7` 節二）。⇒ **承認済の「a7 樹（1役）先」は、番人の射程外**。此の順の安全性は本測で**更に強まった**。
2. **爆風の再計算**: gunshi 樹を触れば動くのは 2 役 ―― 而して **其の 2 役は共に此の遺命表に載る**。⇒ gunshi 樹の入替は「役 2 つ」＋「番人 1 つ」の三者を同時に扱ふ事に成る。

## 四 ★② を為さなんだ理由（先に裁を仰ぐ）★

委員長令②は「遺命表が在れば★先に正しい値へ更新★」。**当職は更新して居らぬ**。理由 ―― **「正しい値」が未だ存在せぬ**：

- 0.20.4 の install は未了（委員長 seq200891「provenance blocker が解けるまで★実行するな★」）。∴ **入替後の樹 path / entry の形が未定**。
- 未定の儘 manifest を書き換ふれば、**現に走る 2 役を起こせぬ manifest** に成り、番人が次に発火した刹那 `start_cmd_failed` を生む ―― ★今より悪い★。
- 加へて `~/bin/*` は当職の自戒にて **実行のみ・改変 0**。改変は委員長の明示 GO を要す。

**∴ 献策**: 遺命表の更新は **cutover と ★同一の手★ で・cutover の直前に** 行ふ（新 path が確定した後）。順は ―― ①a7 樹を先に入替（番人の射程外ゆゑ manifest 不要）②gunshi 樹の入替の直前に `sweep_manifest.json` の 2 行を新 path へ ③入替 ④番人の次の発火を跨いで生存を検む。**②の実行 GO を仰ぐ。**

## 五 為さぬ事

番人の停止 / disable / mask / timer 改変 / `sweep_manifest.json` 改変 / launcher 改変 / restart / cutover / install / fetch / pane 入力 / send-keys ―― **悉く 0**。`systemctl` は **一度も打って居らぬ**（unit は悉く `~/.config/systemd/user/` の **file を読んだ**）。
