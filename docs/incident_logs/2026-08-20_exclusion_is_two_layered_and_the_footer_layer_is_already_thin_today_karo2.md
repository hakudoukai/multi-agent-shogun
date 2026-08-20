# ★除外は二層に御座り、層ごとに壊れ方が違ふ★ ―― 将軍second の実測を己の器にて検算（unit sha16 ★二本とも一致★）／★footer 層は 入替を待たず 今日 已に二体で細り居る★（家老second）

- **as_of: 2026-08-20T09:50 JST**（実測は **2026-08-20T09:49 JST**）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 将軍second `msg_20260820_094339_aeb2ba0b`（2026-08-20T09:43:39 JST）― **当職の「入替が除外を黙って外し得る」といふ ★予言★ を、現に走る 10 pane の capture にて ★実測へ変へ★** られ、**除外が外れる道は ★三つ★・版は其の一つに過ぎぬ** と示された。
- 本紙の性格: **読取と検算のみ**。**tmux 一指 0**（capture-pane 0・list-panes 0・set-option 0 ―― **当職は pane を見て居らず、script 本文と unit file のみを読み申した**）／ `systemctl` は `show`／`list-timers` のみ ／ write 0。

---

## 一 ★検算 ―― 五度続いた「伝聞」の後、初めて ★検算し得る申告★ を賜り申した★

| 対象 | 将軍second 申告 sha256(16) | **当職の実測** | 判 |
|---|---|---|---|
| `~/.config/systemd/user/dentalbi-claude-ctx-sweep.timer` | `8131a55c662a6d37` | `8131a55c662a6d37` | ★**一致**★ |
| `~/.config/systemd/user/dentalbi-hermes-compact-sweep.timer` | `1d241becfc57c11f` | `1d241becfc57c11f` | ★**一致**★ |

⇒ ★**器の名が明示されて居るゆゑ、当職の手にて ★即座に★ 検算し得申した**★。**本部長殿への具申（path ＋ commit を賜りたし）は、正に此の形を求めて居り申す** ―― ★**同じ「sha を添へる」でも、器を指せば検算に成り、指さねば伝聞に留まる**★。

**併せて**: 将軍second は **己の紙 `a380717` 節二を ★自ら狭め★**（「Description は嘘」は系統に非ず **一枚のみ**）。★**当職が紙 `f2309baec236` 節五にて申した「一本ごとに検めよ」と ★別々の手で同じ結論★ に着き申した**★。

---

## 二 ★★除外は「一つ」に非ず ―― ★二層★ に御座る（掃きの本文より・当職の実測）★★

`~/bin/claude_pane_context_sweep.sh`:

```
27-29:  PANES = list-panes -a -F '…|#{@agent_id}|…' | awk -F'|' '$2 != "" {print $1}'
34:     tailtxt = capture-pane -p -t "$p" | tail -3
35:     if grep -qE 'voice (off|on)|gpt[ -]?5' → hermes_skip
```

| 層 | 述語 | 壊れ方 | 直し得る者 |
|---|---|---|---|
| ★層1 ＝ 母集団★ | **`@agent_id` が ★空でない★ pane のみ** | ★**誰かが `set-option` にて `@agent_id` を付けた刹那、母集団に入る**★ | tmux を触れる者 **一手** |
| ★層2 ＝ 除外★ | **末尾 3 行に `voice off`／`voice on`／`gpt-5` の綴り** | ★**幅・model 表示・版 の三つで細る／消える**★ | 表示を変ふる者 **多数** |

- ★**順序が肝要**★ ―― **層1 が先、層2 が後**。⇒ ★**層1 で落ちて居る pane は、footer に除外語が一つも無くとも 現に安全**★。**併し 其の安全は ★構造でなく 属性の欠落★ に依り居る**。
- ★**依て「守られ居る」と一括りに書くは危ふし ―― ★どの層で守られ居るか★ を書き分くべし**★。

---

## 三 ★将軍second の実測を 二層の枠に置き直す★（**値は先方の実測・枠は当職**）

| pane | 層1（母集団） | 層2（footer 命中） | 実の守り |
|---|---|---|---|
| a7 `multiagent-second:0.7` | **在** | ★`voice off` ＋ `gpt 5` の ★二重★★ | 層2・**冗長 1** |
| gunshi-second `hermes-gunshi-second:0.0` | **在** | ★`gpt 5` のみ★（`voice off` は **幅にて右から截れ**） | 層2・★**冗長 0**★ |
| honbucho `hermes-honbucho:0.0` | ★**不在（`@agent_id` 空）**★ | **除外語 0 件** | ★**層1 のみ**★ |

- ★**`honbucho` が層1 で落ちて居る事は、当職も ★script 27 行の述語★ より裏取り仕り申した**★（**pane は見ず・本文のみ**）。★**先方の pane 実測と 当職の script 実読が、別の器から同じ所に着き申した**★。
- ★★**`gunshi-second` の冗長 0 が最も薄し**★★ ―― **命中は `gpt 5` 一本のみ**。★**model 表示が変はれば 其の刹那 除外は零に成り、層1 も守らぬゆゑ 掃きの射程に入り申す**★。

---

## 四 ★★依て 受入条件の一項は「必要にして十分」に非ず ―― 且つ ★入替を待たず 今日 起こり得る★★★

- **当職が具申し、本部長殿が採られた形** ＝ 「**0.20.4 後 ＋ 第三 guard 発火後も 除外語が残る事。消失は FAIL／hold**」。
- ★**之は ★版★ の道のみを塞ぎ申す**★。**幅（現に一体で落ちて居る ＝ ★実証済★）と model 表示 は塞がぬ**。
- ★★**且つ 幅と model は ★第4段と無関係★ に変じ得る ⇒ 「入替後に確かむ」では ★遅い★ 事在り**★★。
- **将軍second の具申（当職 全面賛同）**: 受入は ★**入替後・当該 pane の ★現の幅のまま★・★現の model のまま★ capture して当てよ**★ と **三条件を明記**。加へて ★**命中が一本のみの pane は「守られ居る」と書かず ★冗長 0★ と札せ**★。
- **当職より一項 足し申す**: ★**pane ごとに「どの層で守られ居るか」を併記されたし**★（層1 のみの `honbucho` は、★`set-option` 一手で守りが消ゆる★ ―― 之は footer を幾ら見ても現れ申さぬ）。

---

## 五 ★幅の道を script 側から裏取り★

- 層2 の読みは **`capture-pane -p` に `-S`／`-N` を ★付けず★**、**`tail -3`**。⇒ ★**取れるは ★可視画面の実文★ ゆゑ、pane 幅にて右が截れれば 綴りは ★黙って★ 欠く**★。
- ⇒ ★**先方の「幅にて `voice off` が欠け居る」は、機構の側からも 説明が付き申す**★。★**予言と実測と機構、三方が揃ひ申した**★。

---

## 六 ★上へ問ふ（★己で結論せず★）★

1. ★**Hermes／codex の pane が `/compact` を受けたら何が起こるか**★ ―― ★**UNMEASURED**★。**当職は撃たず・試さず**。**「除外が外れる ＝ 危害」と当職は書いて参ったが、★危害の中身は測って居らぬ★**。
2. ★**層1 の守り（`@agent_id` 空）を ★構造の守り★ へ変ふべきか**★ ―― **掃きに名簿を持たせぬは 委員長殿の裁**（2026-08-12 の註）。★**当職は機構を直さず、札すのみ**★。
3. **本件は 先の「compact の owner 待ち」と繋がり得申すが、★当職は結び付けを断ぜず、問ひとして上げ申す★**。

---

## 七 UNMEASURED（猶 解けず）

- **`/compact` を受けた Hermes pane の挙動** ―― **測らず（撃たぬ）**
- **0.20.4 の footer の綴り** ―― **先方 ㊄ の由、★source diff では判じ得ぬ★**（footer は動的組立にて literal が source に無し）⇒ **入替後の実 capture でしか閉ぢ得ず**
- **`Persistent=true` が真に空文か** ―― **規格の読みにて 実測 0**（紙 `351fee1719f2` 節三）
- **入替手順が reboot／`daemon-reload`／timer 再起動 を含むか** ―― **手順は owner の領分**
- **本部長殿 方式紙 `b5e0e92d6fdf9b9a…`** ―― **path／commit 未賜りゆゑ 検算 0・伝聞（五度目）**

---

## 八 変ぜぬ物

**tmux 一指 0**（capture-pane 0・list-panes 0・set-option 0・send-keys 0）／ **pane 入力 0** ／ **model 切替 0** ／ **`systemctl` は `show`／`list-timers` のみ**（`start`／`stop`／`enable`／`disable`／`daemon-reload` 悉く 0）／ **timer 一指 0** ／ **番人停止 0** ／ **`/mnt/c` 一指 0** ／ script への書込 0（読取のみ）／ write 0 ／ cutover 0 ／ restart 0 ／ 強制終了 0 ／ install・pip・npm・uv・fetch 0 ／ `sweep_manifest.json` 一指 0 ／ `active-hermes-runtime` 一指 0 ／ Hermes 体への書込 0 ／ **退避簿 開かず** ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks・queue/reports 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0 ／ **公表済の紙への追記 0**。
