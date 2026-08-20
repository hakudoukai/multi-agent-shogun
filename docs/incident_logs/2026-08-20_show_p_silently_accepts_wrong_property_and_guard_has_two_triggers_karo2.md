# ★己の物差しの訂★ ―― 「宣言値は空」は器の事実に非ず ★当職の綴り誤り★（`show -p` は誤名を沈黙して rc=0）／★併せて番人は引金を二つ持つ★（家老second）

- **as_of: 2026-08-20T09:22 JST**（実測は **2026-08-20T09:21 JST**）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 本部長殿 `msg_20260820_092011_4508c352`（2026-08-20T09:20:11 JST・nonce `HB-20260820-0919-KARO`）― timer を独立実読し **`OnUnitActiveSec=1800` / `AccuracySec=120`** を得た旨。
- 本紙の性格: **読取と訂のみ**。write 0 ／ cutover 0 ／ restart 0 ／ **番人停止 0** ／ timer への一指 0（読取のみ）。
- **前紙 `e87789828c76`（commit `f2ede59`）は sha 公表済ゆゑ ★一字も書換へず★、本紙にて訂す**。

---

## 一 ★訂 ―― 何が誤りで、何は誤りでなかったか★

**前紙にて当職が書いた事**: 「**宣言値（`OnCalendar` ／ `OnUnitActiveSec` ／ `NextElapseUSecRealtime`）は空で返り、取れたるは二点の刻のみ・標本 1**」⇒ ★**弱き証**★ と札した。

**★誤りであった部分★**: 「**宣言値は空で返る**」は ★**器の事実に非ず、当職が名指した property の綴りが器の綴りと合はざりし為**★。

**★誤りでなかった部分★**: **周期 30 分といふ ★値★ は正しかった**（下記の宣言値と一致）。⇒ ★**値は当って居ったが、其れを支へる理由の側が誤って居った**★。**値が当ったゆゑに安堵して理由を検めぬ事こそ危ふし**。

---

## 二 ★因 ―― `systemctl show -p <名>` は 誤名を ★沈黙して rc=0★ で返す★（当職の実測・2026-08-20T09:21 JST）

| 打った物 | 出力 | rc |
|---|---|---|
| `show -p OnUnitActiveSec -p OnCalendar` | **何も出ず** | **0** |
| `show -p ThisPropertyDoesNotExist`（対照） | **何も出ず** | **0** |
| `show -p TimersMonotonic -p AccuracyUSec` | **値が出る** | 0 |

- ★**在らざる property を名指しても、器は誤りを申さず 黙って rc=0 を返す**★ ⇒ ★**「空 ＝ 設定が無い」と読めてしまふ**★。
- **対照（存在せぬ名）を並べて初めて分かれ申した** ―― ★**空の出力を「不在の証」に据ゑるには、必ず対照を要す**★。
- 之は当職の **三度目の同型**に御座る: ㋐ 便の欄名を `message` と誤り `None`（4字）を得た件、㋑ 素の `grep` の 1 が**引用**であった件、㋒ 本件。★**綴りを誤った問ひは、誤りでなく ★尤もらしき小さき答★ を返す**★。

---

## 三 ★正しき宣言値 ―― 併せて 番人は 引金を二つ持つ★

```
TimersMonotonic={ OnUnitActiveUSec=30min ; next_elapse=... }
TimersMonotonic={ OnBootUSec=5min      ; next_elapse=5min 8.186659s }
AccuracyUSec=2min
```

- **`OnUnitActiveUSec=30min`** ―― 本部長殿の `OnUnitActiveSec=1800` と**一致**。当職の二点差読み（30 分）とも**一致** ⇒ ★**三つの経路が同じ値に着いた**★。
- ★**新たに出でし物 ㊀ ― `OnBootUSec=5min`**★ ―― **番人は「起動の 5 分後」にも撃つ**。**周期 30 分だけを前提とする受入条件は、★再起動を跨ぐと外れる★**。**入替の手順が reboot を含むなら、番人は 30 分でなく ★5 分後★ に来申す**。
- ★**新たに出でし物 ㊁ ― `AccuracyUSec=2min`**★ ―― **systemd は最大 2 分 遅らせて撃ち得る** ⇒ ★**「30 分丁度」で検収を切るは早すぎる**★。

---

## 四 ★受入条件の書き様（前紙の具申を 本紙にて 強める）★

- **正**: ★**入替後、timer の直近発火の刻が ★入替時刻より後へ進んだ★ 事を確かめてより検収せよ**★（**事象**で書く）。
- **刻で書くを要さば**: ★**30 分 ＋ 猶予 2 分（`AccuracyUSec`）＋ 余裕**★。**且つ reboot を跨ぐ手順なら ★5 分★ の引金も在る事を明記せよ**。
- ★**刻のみで書いた条件は、引金が二つ在るゆゑ ★黙って外れる★**★ ―― 之が「事象で書け」の理由の本体に御座る。**前紙では「周期が変はれば壊れる」と書いたが、実は ★変はらずとも 引金が二つ在る時点で已に壊れて居る★**。

---

## 五 UNMEASURED（猶 解けず）

- **方式紙 `b148a28e…` ／ 更新版 `a6b8374f…`** ―― **path／commit 未賜り**ゆゑ **sha 検算 0**（**伝聞**）
- **番人が次回予定どほり撃つか** ―― **未だ見ず**
- **`OnBootUSec` の引金が cutover 手順に掛かるか否か** ―― **手順が reboot を含むかを当職は知らず**（手順は owner の領分）
- **guard 消費 script の owner ／ a7 relaunch の owner** ―― 猶 UNMEASURED（execution blocker）
- **0.20.4 source の在処** ―― **伝聞**（`6a3d50c` は本 repo に非在）

---

## 六 変ぜぬ物

write 0 ／ cutover 0 ／ restart 0 ／ **番人停止 0** ／ **timer への一指 0**（読取のみ・`enable`／`disable`／`start`／`stop` 悉く 0）／ 強制終了 0 ／ install・pip・npm・uv 一指 0 ／ tmux 一指 0 ／ pane 入力 0 ／ Hermes 体への書込 0 ／ wrapper・launcher への書込 0 ／ `sweep_manifest.json` 一指 0 ／ `active-hermes-runtime` 一指 0 ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks・queue/reports 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ a6 追ひ立て 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0 ／ /mnt/c 一指 0 ／ **公表済の紙への追記 0**。
