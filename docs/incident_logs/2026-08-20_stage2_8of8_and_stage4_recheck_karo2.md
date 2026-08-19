# 第2段 8/8 到達の独立検収 ＋ 第4段 再測 ＋ 己の紙の訂（家老second）

- **as_of: 2026-08-20T07:35:46 JST**（第2段の測り）／ **2026-08-20T07:36:33 JST**（第4段の測り）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 将軍second → 当職 `msg_20260820_073158_c0e6ea99`（2026-08-20T07:31:58 JST）「8体目＝当職自身、07:28:34 JST に graceful 退出、07:28:38 JST 起動、07:29:08 JST 検収 PASS。★second_pc 8/8 完了★」
- 本紙の性格: **読取のみ**。restart 0 ／ 強制終了 0 ／ tmux 一指 0 ／ send-keys 0 ／ pane 入力 0。**当職は執行者に非ず**。
- 新条（seq200550「検証させる物は先にcommit(freeze)しas_ofを併記せよ」）に従ひ、**復命より先に commit して凍らす**。

---

## 一 ★他者の主張は主張ゆゑ、己の器にて検む★

将軍second の申し立ては**当職の器の外の行い**（当職は pane を見ぬ）。ゆゑに**受理せず、独立に測り直した**。

### 実測（as_of 2026-08-20T07:35:46 JST・`/proc` 直読）

| PID | size | 起動 | `--resume` UUID |
|---|---|---|---|
| 43213 | 334,645,552 | 2026-08-20T05:29:41 JST | `004324f9-…` |
| 54326 | 334,645,552 | 2026-08-20T05:33:20 JST | `9e544564-…` |
| 56457 | 334,645,552 | 2026-08-20T05:33:55 JST | `c251eaf0-…` |
| 58218 | 334,645,552 | 2026-08-20T05:34:30 JST | `b40a02ee-…` |
| 59890 | 334,645,552 | 2026-08-20T05:35:05 JST | `657cf7de-…` |
| 61670 | 334,645,552 | 2026-08-20T05:35:40 JST | `2ca6c188-…` |
| 63955（★当職★） | 334,645,552 | 2026-08-20T05:36:16 JST | `e25d7399-…` |
| **389804（将軍second・★新★）** | 334,645,552 | **2026-08-20T07:28:38 JST** | `f7795d6a-…` |

- **旧 PID 3686358 は消え、389804 が在る**。**`--resume` UUID `f7795d6a-…` は旧体と逐語同一** ⇒ **身元は保たれ居る**。
- 起動刻 07:28:38 JST は将軍second の申告と**一致**。
- **⇒ second_pc 8/8。将軍second の主張は当職の器にて裏付け申した。**

### 母集団の述語（隠さず札す）
`pgrep -x node` ＋ `pgrep -f claude` の和集合より `readlink /proc/<PID>/exe` が `claude` を含む物のみ。**前回（05:43:05 JST・07:26:56 JST）と同一述語**にて、いづれも 8 体。★述語の外に体が在れば当職は見えぬ★。

---

## 二 ★物差しを「推」から「実測」へ上げ申した★

前紙まで、当職は **size 334,645,552 B ＝ 2.1.236** と**推**して居った（サイズと版の対応は他者の申告に拠る）。本回、**版の文字列そのもの**を取り申した。

| 体 | `/proc/<PID>/exe --version` |
|---|---|
| 63955（当職） | **`2.1.236 (Claude Code)`** |
| 389804（将軍second） | **`2.1.236 (Claude Code)`** |

**⇒ size ↔ 版 の対応が実測にて縛られ、残る 6 体（同 size）も 2.1.236 と断じ得る。**

---

## 三 ★★大なる罠 ―― `(deleted)` の札は「旧版」の徴に非ず★★

| 体 | `readlink /proc/<PID>/exe` | 版 |
|---|---|---|
| 63955（当職・05:36 JST 起動） | `…/@anthropic-ai/**.claude-code-wTkEzMFd**/bin/claude.exe **(deleted)**` | **2.1.236** |
| 389804（07:28 JST 起動） | `…/@anthropic-ai/**claude-code**/bin/claude.exe`（deleted 無し） | **2.1.236** |

- **同じ版でありながら、片や `(deleted)`・片や健在**。差は**版に非ず、「npm の rename より前に起動したか後か」のみ**。
- 前紙（2026-08-20T05:28:57 JST 断面）にて当職は **`maps` の deleted 行数を OLD の徴として用ゐた**。★其の刻は偶々真であったが、一般には偽★ ―― 新版導入の直後は、**新版を掴む体も deleted と映る**。
- **⇒ 版の判定に `(deleted)` を用ゐるな。用ゐるは `--version` の文字列（次点で size）のみ。**
- 之は**当職の物差しの瑕**にて、隠さず札す。**但し前紙の結論（05:28:57 JST に OLD 8/8）は size 330,946,864 にて別途裏付け在り、覆らず。**

---

## 四 第4段（Hermes 全12体 → 0.20.4）― 再測（as_of 2026-08-20T07:36:33 JST）

| 体 | `run/<runtime>/pyproject.toml` の version | mtime | 走行 PID |
|---|---|---|---|
| `ashigaru-second-7-hermes` | **0.20.0** | 2026-08-07T10:04:22 JST | 1156252（`hermes --tui`） |
| `gunshi-second-hermes` | **0.20.0** | 2026-08-07T10:04:22 JST | 836838（`--tui --continue`）／ **4178540**（`--continue`） |

- **mtime すら変ぜず** ⇒ **second_pc 分 ＝ 猶 0/2・第4段 未了**。05:23:23 JST 基線より**一指も動かず**。
- **`hermes-honbucho` の版 ―― 猶 UNMEASURED**（`pyproject.toml` 見当らず・深掘りは機構owner の領分）。
- **全12体の名簿 ―― 猶 UNMEASURED**（当職の器の外・上位より賜りたし）。

---

## 五 ★★訂 ―― 己の公にした紙の PID 帰属が誤り★★

**対象**: `docs/incident_logs/2026-08-20_stage4_hermes_baseline_karo2.md`（sha256先頭 **`c1a6e35ce4cf`**・commit `cd9fa3f`・復命 seq200610 にて公にした紙）

| | 誤 | 正 |
|---|---|---|
| `gunshi-second-hermes` の走行 PID | 836838 ／ **4178443** | 836838 ／ **4178540** |

- **PID 4178443 の実体** ＝ `/usr/bin/doppler run … /home/hakudokai/.local/libexec/dentalbi/promote_supabase_rotation_key.sh …` ―― **Hermes runtime に非ず**。当職が**別種の process を配下の体と読み誤った**。
- **正しき体** ＝ **4178540**（`…/hermes-agent-v2026.8.3/venv/bin/python …/hermes --continue`・2026-08-20T05:09:33 JST 起動）。
- ★**結論は変ぜず**★: 4178540 の掴む runtime も同じ `hermes-agent-v2026.8.3` ＝ **0.20.0** ゆゑ、**「05:09 JST に起動した新しき体も版は上がり居らぬ」という判定は其のまま立つ**。**誤ったは典拠の PID であって、答に非ず。**
- ★**紙 `c1a6e35ce4cf` は書き換へず**★（既に sha を公にしたる紙ゆゑ）。**訂は本紙にて出す。**

---

## 六 UNMEASURED（猶 解けず）

- **正本紙 `reports/IINCHO-RULING-15-…md`（sha16 `c7884f1150d9341a`）―― 当PCの樹に無し** ⇒ **sha 検算 0**。裁定第9号（`2348ad3d6aadd804`）に続き**二度目の不在**。
- **`hakudoukai/hakudokai-dev`** の樹 ―― 当PCに見出せず。
- **third_pc・main_pc** ―― 当職の器の外。**8/8 は second_pc に限る主張**にて、線全体の到達を申すに非ず。

---

## 七 変ぜぬ物

restart 0 ／ 強制終了 0 ／ clear 0 ／ send-keys 0 ／ capture-pane 0 ／ tmux 一指 0 ／ install・pip・npm 一指 0 ／ Hermes 体への書込 0 ／ pane 入力 0 ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0。
