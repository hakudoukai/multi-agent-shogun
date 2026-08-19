# 第2段 v2 ―― second_pc 8体 role-by-role 再起動 ★計画★（未執行）

- **as_of: 2026-08-20T05:21:51+09:00**（全数値は此の刻の実測）
- host: USER-O6AK917NTU (second_pc) / 起案: shogun-second (pid 3686358)
- 典拠: 委員長 seq200577（第2段の完了報告を撤回）／委員長 seq200545（新条＝検証物は先に commit(freeze) し as_of 併記）／Commander seq200579（★計画を保存し target confirmation を得るまで restart/respawn/kill/clear を為すな★）
- **状態: ★未執行★** ―― 本紙は計画のみ。**restart 0 / respawn 0 / kill 0 / clear 0 / send-keys 0**。

---

## 一 何が起きたか（second の因は third と異なる）

| 刻 | 事 | 証 |
|---|---|---|
| 02:00〜02:10 | 当職が 8 体を `--resume` 付きで再起動（seq200226） | 紙㋐㋑・当時 exe=`…/claude-code/bin/claude.exe`（deleted 無）・size 330,946,864・`claude --version`=**2.1.235** |
| **05:10:19** | **★何者かが 2.1.236 を install★** | `…/@anthropic-ai/claude-code/bin/claude.exe` の mtime=**2026-08-20 05:10:19**・size=**334,645,552** |
| 05:21:51 | 8 体は悉く**旧 image**（2.1.235 の inode が unlink 済） | 全 8 体の `/proc/<pid>/exe` = `…/@anthropic-ai/.claude-code-wTkEzMFd/bin/claude.exe` **(deleted)** |

⇒ **委員長 seq200577 の判は second について正しい**。**★但し因は「doppler を NEW と数へた」ではない★** ―― second は
**02:10 の時点では真に 8/8 NEW（対 2.1.235）であり、05:10 の新 install が再び差を開いた**。当職の doppler 祖先は 8 体とも **False**（前紙記載）。
⇒ **手順の教訓＝★install を先に済ませ、然る後に relaunch せよ★**。逆順では永久に追ひ付かぬ。

★install の主は当職に非ず★（当職 install 一指 0）。**誰が 05:10 に入れたかは UNMEASURED**。

---

## 二 preimage（05:21:51 実測・全 8 体）

共通: cwd=`/home/hakudokai/projects/multi-agent-shogun` ／ 親=`-bash`（tmux pane 配下）／ exe=`…/.claude-code-wTkEzMFd/bin/claude.exe` **(deleted)** ／ doppler 祖先 **False**。

| 順 | pane | tmux `@agent_id` | PID | session UUID | 起動一行（逐語・`/proc/<pid>/cmdline` 直読） | start |
|---|---|---|---|---|---|---|
| 1 | `multiagent-second:0.6` | ashigaru-second-6 | 3655376 | `004324f9-44e5-4688-8076-97159351845d` | `claude --model claude-sonnet-5 --resume 004324f9-44e5-4688-8076-97159351845d --permission-mode auto` | 01:59:16 |
| 2 | `multiagent-second:0.5` | ashigaru-second-5 | 3657843 | `9e544564-f15c-43f1-ae72-d7de48ff00cc` | 同形（sonnet-5 / auto） | 01:59:58 |
| 3 | `multiagent-second:0.4` | ashigaru-second-4 | 3658974 | `c251eaf0-e921-45db-b9e6-d8a7268eba0e` | 同形 | 02:00:13 |
| 4 | `multiagent-second:0.3` | ashigaru-second-3 | 3660072 | `b40a02ee-97bd-4cf1-9336-d9b9c06e39f8` | 同形 | 02:00:28 |
| 5 | `multiagent-second:0.2` | ashigaru-second-2 | 3660796 | `657cf7de-4832-4ae8-8a41-1660250ef1c5` | 同形 | 02:00:45 |
| 6 | `multiagent-second:0.1` | ashigaru-second-1 | 3661563 | `2ca6c188-f3cb-415d-b0df-d334e4068a35` | 同形 | 02:00:56 |
| 7 | `multiagent-second:0.0` | karo-second | 3662641 | `e25d7399-058a-4bef-bc33-81d5d6a89eed` | `claude --model claude-opus-5 --resume e25d7399-058a-4bef-bc33-81d5d6a89eed --permission-mode bypassPermissions` | 02:01:16 |
| 8 | `shogun-second:0.0` | shogun-second（★当職★） | 3686358 | `f7795d6a-27dc-4422-ab5e-b25fbe9b6795` | `claude --model claude-opus-5 --resume f7795d6a-27dc-4422-ab5e-b25fbe9b6795 --permission-mode bypassPermissions` | 02:10:09 |

★`--permission-mode` は**元の値をそのまま復元**する（変更に非ず）。model も同前。★

---

## 三 一体あたりの手順（同一の型・順は上表 1→8）

1. **pre 実測**: `tmux display-message -p -t <pane> '#{pane_pid}'` → `pgrep -P` → `/proc/<pid>/{exe,cmdline,cwd}` を控へる。
2. **graceful 終了**: pane へ `/exit` ＋ Enter を送る。**★kill を用ゐぬ★**（D006/DD-169 の①⑤を欠くゆゑ例外不成立。前回も kill 0 で成した）。
3. **子の消滅を待つ**: `pgrep -P <pane_pid>` が 0 になるまで最大 180 秒。
4. **起動**: 上表の**逐語の一行**を pane へ送り、別送で Enter。
5. **post 検収（4 点）**:
   - ㊀ `readlink /proc/<new>/exe` ＝ `…/@anthropic-ai/claude-code/bin/claude.exe`（**`(deleted)` 無し**）
   - ㊁ size ＝ **334,645,552 B**
   - ㊂ `claude --version` ＝ **`2.1.236 (Claude Code)`**
   - ㊃ **会話継続の徴**（pane に前段の応答／auto-compact 残 % が見える事）
6. 次の一体へ。**一度に一体のみ**。

## 四 canary

**1 番（ashigaru-second-6）のみを先に回し、㊀〜㊃ が悉く合格するまで 2 番以降へ進まぬ**。
不合格なら**即停止**し、blocker4（owner／root_cause／next_safe_action／human_GO_required）を上げる。

## 五 rollback（★正直に書く★）

- **image の rollback は不能**。2.1.235 の inode は既に unlink 済（`(deleted)`）ゆゑ、**旧版へ戻す道は当職の手中に無い**。戻すなら npm 側の操作となり **install＝当職の権外**。
- **会話の rollback**＝同じ `--resume <UUID>` で起こし直す（冪等）。`--resume` が失敗する時のみ `--continue` を同 cwd で試み、**それも駄目なら停止して上申**（★素で包むな＝委員長 seq199854★）。
- **落ちた儘にせぬ**: 起動一行の送出まで一体ずつ完了を確認する。
- **当職自身（8 番）**は `/exit` すれば己の pane に打つ者が居らぬゆゑ、**detached の遅延起こし役**（`tmux send-keys` と `pgrep` のみ・**終了命令 0**）を先に置く。前回の実績あり。

## 六 為さぬ事（本計画の外）

install / npm 操作 ／ doppler で包む事（seq199833 未了・`ANTHROPIC_API_KEY` 混入の可否は当職の権外） ／ tmux server・pane の生殺・respawn・set-option ／ `--permission-mode`・model の変更 ／ Hermes 一指（a7・gunshi-second 含む） ／ config・DB mutation ／ 一括既読札。

## 七 待ち（Commander seq200579 順守）

★本紙を保存・commit(freeze) した上で **target confirmation を待つ**。確認が来るまで一指も動かさぬ。★
