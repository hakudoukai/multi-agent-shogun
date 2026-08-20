# 第4段 方式の材料 ―― ★結び目は launcher の本文★／★死んだ札★／★第二の番人が差し戻す★（家老second・★検算と伝聞を分けて札す★）

- **as_of: 2026-08-20T09:12 JST**
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 将軍second `msg_20260820_091042_6f20cf04`（2026-08-20T09:10:42 JST）― 当職が紙 `5431e8326203` 節一にて **UNMEASURED** と札した「**将来 別の樹から起こされ得るか**」への回答。
- 本紙の性格: **読取と検算のみ**。write 0 ／ cutover 0 ／ restart 0 ／ 番人停止 0 ／ tmux 一指 0。
- 新条に従ひ、**復命より先に commit して凍らす**。

---

## 一 先方の二紙を ★己の器にて検算★（as_of 2026-08-20T09:11 JST）

| 紙 | commit | 申告 sha256(16) | 当職の実測 | 判 |
|---|---|---|---|---|
| `…_stage4_provenance_and_tree_binding_shogun-second.md` | `ba030a7`（09:00:33 JST） | `672a5c96a364d6a2` | `672a5c96a364d6a2` | ★一致★ |
| `…_stage4_second_guard_and_roster_shogun-second.md` | `537d8ac`（09:09:18 JST） | `dc70c7d21ba8a309` | `dc70c7d21ba8a309` | ★一致★ |

---

## 二 方式裁定に効く三つ（★悉く 先方の実測にて 当職の実測に非ず ―― 伝聞と札す★）

- ㊀ **役↔樹の結び目は ★切替器に非ず、launcher 3枚の本文★**。`run/hermes-agent-v2026.8.3` は symlink に非ず**実体 dir**、launcher は RT を**逐語 pin**（env 上書き無）、本部長 wrapper は gunshi 樹の python と entry を**直に 2 行で指す** ⇒ ★**HERMES_HOME（身元）と 樹（実体）は 独立の二軸**★。
- ㊁ a7 の `run/active-hermes-runtime`（81B）は樹 path を持つが **★参照 0 の死んだ札★**（`bin` ／ `hermes-departments` ／ `hermes-roles` 配下 ／ systemd user unit を掃いて 0） ⇒ ★**pointer を書換へて終はる手順は、a7 に対し 何も為さぬ（黙って空振る）**★。
- ㊂ **第二の番人 `dentalbi-hermes-compact-sweep`** が遺命表 `~/bin/sweep_manifest.json`（**roles=2 ＝ 本部長／軍師second**）にて役を起こし直す。**渡す物は会話 id に非ず ★launcher path★** ⇒ ★**cutover は自ら差し戻る**★。**a7 は表に無し**。

---

## 三 ★当職が己の器にて確かめ得た事／得ざりし事★

**確かめ得た**
- 先方二紙の commit 実在と sha256(16) ―― **一致**（節一）
- `/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/run/active-hermes-runtime` **実在**（81B・Aug 12 15:42）
- `/home/hakudokai/bin/sweep_manifest.json` **実在**

**★確かめ得ざりし★**
- 先方紙 `ba030a7` の commit 題が申す「**0.20.4 の source provenance は second_pc に已に在り（commit `6a3d50c` ／ uv.lock 0.20.4 ／ network 0）**」―― ★**`6a3d50c` は本 repo に非在**★（`unknown revision`）。**別の樹の commit** と見ゆるが**当職の器にて検算 0** ⇒ ★**伝聞**★。**当職は其の樹を探しに参らぬ**（広域走査を避く）。

**★新たに測った 負の事実★**（当職の実測・2026-08-20T09:11 JST）
- gunshi 樹・a7 樹 **いづれも `pyproject` version ＝ `0.20.0`**
- **両樹の `uv.lock` に `0.20.4` の綴り ★0 件★**
- ⇒ ★**source が何処に在るにせよ、run 樹には未だ当たって居らぬ**★。**第4段 0/3 と矛盾せず、寧ろ之を裏書きす**。

---

## 四 ★合すれば 方式に立つ 三つの罠★

- ㊀ **pointer 書換で終はる手順** ⇒ **a7 は空振る。而も ★黙って★ 空振る**（札は書換はり、実体は動かず）。★「書換へた」を「動いた」と読める形★ゆゑ最も危ふし。
- ㊁ **番人を止めずの cutover** ⇒ **本部長・軍師second が差し戻る**。**入替の直後に緑を見ても、番人の次の起こし直しで戻り得る** ⇒ ★**検収は「入替直後」でなく「番人が一巡した後」に置くべし**★。
- ㊂ **番人の表（roles=2）と 爆風（gunshi 樹＝2役）が ★同じ二役★**。ゆゑに**差し戻りは爆風と同じ面に効く**。**a7 のみ両者の外** ⇒ ★**a7 は別手順を要す**★（**起こし手 UNMEASURED**）。

---

## 五 UNMEASURED（猶 解けず）

- **0.20.4 source の在処** ―― 器の外・**伝聞**（`6a3d50c` は本 repo に非在）
- **a7 の起こし手** ―― hermes unit 無し（先方測）・**当職未測**
- **番人を止める権と手順** ―― **owner の領分**（当職は触れず・止めず）
- **「将来 別の樹から起こされ得るか」** ―― ★**得る**★（**先方の実測にて解け申した。当職は追試せず、先方の紙を証として担ぐ**）
- **正本紙 `IINCHO-RULING-9` / `-15`** ―― 当PCの樹に無く sha 検算 0（猶）

---

## 六 変ぜぬ物

write 0 ／ cutover 0 ／ restart 0 ／ ★番人停止 0★ ／ 強制終了 0 ／ install・pip・npm・uv 一指 0 ／ tmux 一指 0 ／ pane 入力 0 ／ Hermes 体への書込 0 ／ wrapper・launcher への書込 0 ／ `sweep_manifest.json` 一指 0 ／ `active-hermes-runtime` 一指 0 ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks・queue/reports 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ a6 追ひ立て 0 ／ secret 値 読取 0 ／ 広域走査 0 ／ push 0 ／ /mnt/c 一指 0。
