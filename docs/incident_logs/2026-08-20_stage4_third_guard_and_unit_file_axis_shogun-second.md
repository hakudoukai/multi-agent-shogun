# 第4段 ―― 番人は ★二つに非ず 三つ★ ／ 刻を「unit file」の軸からも検算 ／ Description は 12 倍の嘘

- **as_of: 2026-08-20T09:26 JST**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・番人停止 0・`systemctl` 一指 0**
- 契機: 家老second `msg_20260820_092304_cc71572c`（09:23:04・commit `a2d78b8`）―― 番人の刻を runtime property より実測（`OnUnitActiveUSec=30min` / `OnBootUSec=5min` / `AccuracyUSec=2min`・直近発火 09:13:27・次 09:43:27）＋ ★`systemctl show -p` は誤名を黙って受け rc=0 を返す ⇒ 空を不在の証に据ゑるには対照を要す★。
- 本紙は其の**検算（第三の物差し）**と、**当職が新たに見付けた三つ目の番人**。

---

## 一 ★第三の物差し ―― unit file の本文★（家老＝runtime property / 本部長＝同／当職＝**file**）

`~/.config/systemd/user/dentalbi-hermes-compact-sweep.timer`（sha256(16)=`1d241becfc57c11f`・mtime 2026-08-12 23:12:49）**全文 9 行**:

| 行 | 逐語 | 家老の runtime 値 | 一致 |
|---|---|---|---|
| 4 | `OnBootSec=300` | `OnBootUSec=5min` | ★一致★ |
| 5 | `OnUnitActiveSec=1800` | `OnUnitActiveUSec=30min` | ★一致★ |
| 6 | `AccuracySec=120` | `AccuracyUSec=2min` | ★一致★ |

⇒ **★file と runtime が一致 ＝ 未 reload の差分は無い★**。之が第三の軸の値打ちにござる ―― 若し file だけが新しければ、**誰かが `daemon-reload` を打った刹那に周期が変はる**（隠れた第四の引金）。今は其の危険 **無し**。

**併し ―― 家老の測りは「今 load されて居る物」、当職の測りは「次に load される物」**。同値ゆゑ今回は同じ結だが、**軸は別**である。

## 二 ★行 1 の Description は嘘を吐いて居る★（当職の新出）

行 2 ＝ `Description=Run Hermes context compaction sweep every 6h`。**而して値は 30 分 ―― ★12 倍の食ひ違ひ★**。
併存する `.timer.bak-interval2h-20260812`（sha256(16)=`c34985ed8540fcb4`）は `OnUnitActiveSec=7200`（2h）―― **此方も Description は「6h」の儘**。
⇒ **周期は 6h → 2h → 30min と二度書き換へられ、Description は一度も直されて居らぬ。**
⇒ ★危険★: `systemctl list-timers` は **Description の列**を出す。**其の列を読んで段取りを組めば 12 倍 外れる。** 家老の「刻でなく事象で書け」は、此の面からも正しい。

## 三 ★`Persistent=true`（行 7）―― 引金に見えるが、規格上は空撃ち★

`Persistent=` は systemd 規格にて **`OnCalendar=` を伴ふ timer にのみ効く**。本 timer は単調 timer（`OnBootSec`/`OnUnitActiveSec`）のみゆゑ、**規格上は無効の飾り**である。
**★但し之は規格の読みであって当職の実測に非ず★** ―― 実測するには停止と再起動を要し、番人に手を触れる事に成るゆゑ **為さぬ**。**UNMEASURED（本 host に於ける実挙動）**と札す。
⇒ 段取りに用ゐる時は **「効かぬ筈」ではなく「効いても壊れぬ順」**で組まれたし。

## 四 ★三つ目の番人 ―― 当職の pane を撃ち得る★（新出）

`dentalbi-claude-ctx-sweep.timer`（**enabled**）→ `~/bin/claude_pane_context_sweep.sh --apply`（52 行・sha256(16)=`0273d26b29322e98`）:

- tmux の pane を列挙し、判定器 **`/mnt/c/DentalBI/scripts/claude_context_auto_compact.py`** に掛け、**「100% かつ idle」と判れば pane へ ★`/compact` を送出★** する（行 41-43）。
- 註に曰く「★idle の時だけ送る（busy なら次周期。作業中の投入は turn を壊す実測あり）★」「プロセスは一切殺さない」。
- ★爆風★: **`shogun-second`（当職）を含む Claude 系 pane が対象**。第4段の執行中に「idle」と判ぜられれば、**執行者の会話へ `/compact` が刺さる**。
- ★測れぬ穴★: 判定器の本体は **`/mnt/c` に在り、既存 task の禁により当職は読めぬ（本部長 08:25:11）** ⇒ **「idle の判定が何を見て居るか」は UNMEASURED**。**当職は「busy ゆゑ安全」と断ずる事が出来ぬ。**

## 五 ★己の掃きに対照を置き直した★（家老 ㊂ の警めの適用）

家老の「空を不在の証に据ゑるには対照を要す」を、当職の**前便の掃き**（enabled timer 9 本の起動動詞 grep）に当て直した:

- **存在の検め**: 零を返した 6 本の script ―― **悉く READABLE**（path 誤りに因る偽の零に非ず）。
- **陽性対照**: `^#!` にて掃くと **6/6 命中** ⇒ **器は生きて居る**。
- **本問の再掃き**（`systemctl` / `tmux ` / `.sh` / `doppler run`）⇒ 命中は註と `has-session` / `capture-pane` のみ。**役を起こす動詞は 0**。
- ★残る穴★: 掃きは**当職が思ひ付いた綴り**しか捕へぬ。**綴りの外は依然 UNMEASURED**（→ 之が節四の三つ目の番人を、前便で取り零した理由。**前便の「番人は二つ」は ★誤り★ にして、本紙で三つへ訂す**）。

## 六 献策の更新（受入条件）

1. **刻で書くな・事象で書け**（家老 ㊁ を受く）―― 「**当該 timer の直近発火の刻が、入替の刻より後へ進んだ**」を検収の条件とせよ。
2. **加へて ―― 検収の対象は ★二つの timer★**（compact-sweep ／ claude-ctx-sweep）。後者は**当職の pane を撃ち得る**ゆゑ、**執行者の pane を対象外に出来ぬか**を環境 owner（本部長／委員長）へ諮られたし。**当職は timer に一指も触れぬ。**
3. `list-timers` の **Description を根拠に据ゑるな**（12 倍の嘘・節二）。

## 七 為さぬ事

番人の停止 / disable / mask / timer 改変 / `sweep_manifest.json` 改変 / launcher 改変 / restart / cutover / install / fetch / pane 入力 / `systemctl` の実行 ―― **悉く 0**（unit は file を読んだ）。
