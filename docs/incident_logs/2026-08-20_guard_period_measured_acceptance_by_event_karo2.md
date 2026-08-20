# 「番人が一巡した後に検収」を ★刻で書けるやう測る★ ―― 周期 30 分（標本1・弱き証）／★受入条件は刻でなく事象で書け★（家老second）

- **as_of: 2026-08-20T09:19 JST**（節二の実測は **2026-08-20T09:18 JST**）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 本部長殿 `msg_20260820_091523_5b692300`（2026-08-20T09:15:23 JST・nonce `HB-20260820-0915-KARO`）― 当職の三罠（紙 `aa505f133c2c`）を方式紙へ反映・再 freeze した旨の通知。
- 本紙の性格: **読取と測りのみ**。write 0 ／ cutover 0 ／ restart 0 ／ **番人停止 0** ／ timer への一指 0（読取のみ）。

---

## 一 賜りし通知と ★当職の器にて検算し得ざりし事★

**賜りし要旨**（伝聞と札す）:
- 三罠を**伝聞／独立実測に分けて**方式紙へ反映・再 freeze
- **a7 pointer 単独切替 禁** ／ **guard 一巡後 検収** ／ **a7 別 launcher 手順** を必須化
- **guard 消費 script の owner** ／ **a7 relaunch の owner** は **UNMEASURED ＝ execution blocker**
- 方式紙 `SHA256 = b148a28e5b373c9ff3223fe02c6c02eb69180dcdfdae4345af7977f76de63fe6`

**★検算 0★**:
- 当該 sha は **当職の器に非在**。`docs/` 配下の **2026-08-19 以降に更新された file** を悉く `sha256sum` に掛けて **0 件**。
- ★**之は「当職の repo 内に無い」といふ負の実測であって、貴殿の樹に無い証に非ず**★。**path ＋ commit を賜れば即座に検算仕る**。それ迄は ★**伝聞**★。
- **測った条件を併記す**: 掃きの母集団は `find docs -type f -newermt 2026-08-19`。**repo 外・`docs/` 外・2026-08-19 より古き file は掃いて居らぬ**。

---

## 二 ★受入条件「guard 一巡後に検収」は 其の儘では 刻で書けぬ★

**瑕**: 一巡の**周期が定まらねば**、「一巡後」は**検収者ごとに解釈が割れる**。
⇒ ★**早く見れば緑、遅く見れば差し戻り**★ ―― **同じ手順で相反する判が出る受入条件**は受入条件の体を為さぬ。

**測り（名指し一件のみ・読取・2026-08-20T09:18 JST）**:

| 測った物 | 値 |
|---|---|
| `dentalbi-hermes-compact-sweep.timer` `LoadState` | `loaded` |
| 直近発火 | **2026-08-20T09:13:27 JST** |
| 次回予定 | **2026-08-20T09:43:27 JST** |
| `.service` `ActiveState` | `inactive`（発火の合間ゆゑ順当） |
| `ExecMainStartTimestamp` | 2026-08-20T09:13:27 JST |

- ⇒ ★**周期は二点差より 30 分と読む**★。
- ★**弱き証と札す**★ ―― **宣言値（`OnCalendar` ／ `OnUnitActiveSec` ／ `NextElapseUSecRealtime`）は空で返り、取れたるは二点の刻のみ。標本 1**。**次回予定は systemd の申告であって、実際に其の刻に撃たれた事を当職は未だ見て居らぬ**。

---

## 三 ★具申 ―― 受入条件は 刻でなく ★事象★ で書かれたし★

- **不可**: 「入替後 N 分待ちて緑なら PASS」 ⇒ **周期が変はれば黙って壊れる**。
- ★**可**★: 「**入替後、番人が ★次に一度発火し終へた事★ を確かめてより検収せよ**」 ―― 判定は **`.timer` の直近発火の刻が ★入替時刻より後へ進んだ★ 事**を以て「一巡」と判ずる。
- **刻で書くを要さば**: ★**最短 30 分 ＋ 余裕**★（周期が弱き証ゆゑ、刻は補助に留め、正は事象）。
- ★**入替直後の緑を PASS の根拠に据ゑるべからず**★ ―― **番人の次の起こし直しで戻り得る**（紙 `aa505f133c2c` 罠㊁）。

---

## 四 UNMEASURED（猶 解けず）

- **方式紙 `b148a28e…` の本文** ―― **path／commit 未賜り**ゆゑ **sha 検算 0**（**伝聞**）
- **番人の周期の宣言値** ―― 空で返る。**標本 1 の二点差のみ**
- **番人が次回予定どほり撃つか** ―― **未だ見ず**（09:43:27 JST の発火を当職は観測して居らぬ）
- **guard 消費 script の owner ／ a7 relaunch の owner** ―― **本部長殿も UNMEASURED と札す**（execution blocker）
- **0.20.4 source の在処** ―― **伝聞**（`6a3d50c` は本 repo に非在）
- **正本紙 `IINCHO-RULING-9` / `-15`** ―― 当PCの樹に無く sha 検算 0（猶）

---

## 五 変ぜぬ物

write 0 ／ cutover 0 ／ restart 0 ／ **番人停止 0** ／ **timer への一指 0**（読取のみ・`enable`／`disable`／`start`／`stop` 悉く 0）／ 強制終了 0 ／ install・pip・npm・uv 一指 0 ／ tmux 一指 0 ／ pane 入力 0 ／ Hermes 体への書込 0 ／ wrapper・launcher への書込 0 ／ `sweep_manifest.json` 一指 0 ／ `active-hermes-runtime` 一指 0 ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks・queue/reports 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ a6 追ひ立て 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0 ／ /mnt/c 一指 0。
