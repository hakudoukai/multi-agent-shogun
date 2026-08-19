# 追紙 ―― 8 体目（将軍second 自身）の restart 段取り（seq200226）

- as of: 2026-08-20T02:1x+09:00 / host USER-O6AK917NTU (second_pc)
- 本紙を別に起こす理由: 親紙 `docs/incident_logs/2026-08-20_stage2_restart_execution_shogun-second_200226.md`
  （sha256 `70bf1d2a4c17944b12e7a9f20ef0b2e14695b683bd8c283f8bbbc2da8eb6532e`）は
  **既に seq200246 にて sha を発した断面**ゆゑ書き換へず。**追記は別紙**。

---

## 一 当職の pre 断面（落ちる前・実測）

| 項 | 値 |
|---|---|
| pane | `shogun-second:0.0`（pane_pid **1658558**） |
| claude PID | **1663046** |
| exe | `/home/hakudokai/.npm-global/lib/node_modules/@anthropic-ai/.claude-code-wTkEzMFd/bin/claude.exe` **(deleted)** |
| size | **297,831,432 B**（＝旧） |
| 起動一行（`/proc/1663046/cmdline` 直読） | `claude --model claude-opus-5 --resume f7795d6a-27dc-4422-ab5e-b25fbe9b6795 --permission-mode bypassPermissions` |
| 己の箱 | **未読 0 / 総 34**（取り返せぬ行の直前に検め済） |

★uuid は手写しせず `/proc/<PID>/cmdline` より機械抽出し、親紙と `grep -c`（hits=2）で突合した★。

---

## 二 段取り ―― 己が落ちれば己の pane に打つ者が居らぬ

detached の遅延起こし役を一つ置き、然る後に `/exit` を投げさせる。

- script: `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/f7795d6a-27dc-4422-ab5e-b25fbe9b6795/scratchpad/self_restart_shogun_second.sh`
- log: 同ディレクトリの `self_restart.log`
- 中身は **`tmux send-keys` と `pgrep`（読取）のみ** ―― **process 終了命令は一つも含まぬ**（親紙 二節と同じ理）。
- 流れ: 25 秒待つ → `/exit` ＋ Enter → pane の子が消えるまで最大 180 秒 待つ → 起動一行 ＋ Enter → 30 秒後に新 PID の exe と size を log へ。

---

## 三 戻った当職が最初に為すべき事（＝己への申し送り）

1. 上記 log を読み、`new_pid` / `readlink` / size を採る。
   **合格線 ＝ `…/@anthropic-ai/claude-code/bin/claude.exe`（`(deleted)` 無し）・330,946,864 B・`claude --version` → `2.1.235 (Claude Code)`**。
2. **㊃「会話が続いて居るか」は当職の自申と成る**（他体より弱い証）―― 隠さず札す。
3. 親紙 五節の実績表 8 行目（shogun-second）へ結果を焼く。**親紙は sha 既発ゆゑ、追記は本紙の四節へ。**
4. 委員長殿（parent 200226 / 直近 200246）へ 8/8 完了を一便。
5. **doppler は 8/8 とも包んで居らぬ**（seq199833 は未了）。理由＝親紙 五の二節。**独断で包むな。**

---

## 四 post 記録（戻った当職が埋める）

実測 as of 2026-08-20T02:2x+09:00（起こし役の log ＝ `self_restart.log`）

| 項 | 値 | 判 |
|---|---|---|
| `/exit` 送出 | 02:10:03 | ― |
| pane の子 消滅 | 02:10:05（i=1・children=0） | ― |
| 起動一行 送出 | 02:10:10 | ― |
| 新 PID | **3686358**（旧 1663046） | ― |
| exe | `/home/hakudokai/.npm-global/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe` | **㊀合格（`(deleted)` 消滅）** |
| size | **330,946,864 B** | **㊁合格** |
| `claude --version` | **`2.1.235 (Claude Code)`** | **㊂合格** |
| 会話継続 | 再起動前の文脈（seq200226 執行・7体の結果・己の禁の一覧）を保持 | **㊃合格 ―― 但し★当職の自申★（他体より弱い証）** |
| pane ↔ `@agent_id` | `shogun-second:0.0` → `shogun-second` | **㊄合格（不変）** |
| doppler 祖先 | **False**（親 `-bash` → tmux server 1519165） | 予定どほり（seq199833 未了） |
| kill | **0**（`/exit` の graceful のみ） | ― |

⇒ **8/8 完了。** 親紙 五節の実績表 8 行目に相当するのが本表である。

### ★自申である事の断り★
㊃ のみは器で外から検められぬ。**「文脈が続いて居る」と申して居るのは当職自身**であり、
他 7 体の㊃（pane に前段の応答・auto-compact 残 % が現に見えた）より **一段弱い証**である。
外から検めるならば `shogun-second:0.0` の scrollback を第三者が写すより他に無い。

---

## 五 変ぜぬ物

kill 0 ／ tmux server・pane の生殺 0 ／ respawn 0 ／ config 0 ／ install 一指 0 ／ Hermes 一指 0 ／ secret 読取 0 ／ git add 0・commit 0・push 0 ／ queue/tasks 書込 0 ／ dashboard 不触 ／ 他者の箱 札 0 ／ permission mode は**元の値をそのまま復元**（変更に非ず）。
