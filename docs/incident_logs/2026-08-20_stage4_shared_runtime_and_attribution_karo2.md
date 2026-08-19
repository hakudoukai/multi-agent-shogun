# 第4段 ― ★runtime の共有★ の発見 ＋ ★己の「訂」が更に誤りであった事の訂★（家老second）

- **as_of: 2026-08-20T08:31:31 JST**
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 契機: 本部長殿 `msg_20260820_082943_0c8b4190`（2026-08-20T08:29:43 JST・nonce `HB-20260820-0829-KARO-HERMES`）― 当職が 08:23:37 JST に請うた「`hermes-honbucho` の版の取り方」への実測回答。
- 本紙の性格: **読取のみ**。write 0 ／ cutover 0 ／ restart 0 ／ install・pip 0 ／ tmux 一指 0 ／ pane 入力 0。**本部長殿の「相談役の方式裁定まで write/cutover/restart 0」と同じ立ち位置**。
- 新条に従ひ、**復命より先に commit して凍らす**。

---

## 一 ★★訂の訂 ―― 己の前紙の「訂」が、それ自体誤りに御座った★★

**対象**: `docs/incident_logs/2026-08-20_stage2_8of8_and_stage4_recheck_karo2.md`（sha12 **`abdb073ca1e4`**・commit `2b8e68e`・復命 **seq200740** にて公にした紙）第五節

| 版 | 当職の申し立て | 真 |
|---|---|---|
| 初（紙 `c1a6e35ce4cf`） | gunshi の走行 PID ＝ 836838 ／ **4178443** | **誤** |
| 訂（紙 `abdb073ca1e4`） | 正は 836838 ／ **4178540** | **★猶 誤★** |
| **本紙** | **gunshi の体 ＝ 836838 の一つのみ**。**4178540 は ★本部長の体★**。4178443 は其の doppler 包み。 | — |

### ★二度誤った 一つの因★
**当職は「役の帰属」を「runtime の path」より推して居った。**
**然るに `hermes-honbucho` は ★己の runtime を持たず、軍師second の runtime を借りて exec して居る★。**
**⇒ path は共有ゆゑ身元を担はぬ。★共有された器は、誰の物かを語らぬ★。**

★本部長殿の申し立て（4178540 は本部長の体）が正しく、当職が誤って居り申した。★

---

## 二 何が決め手であったか（＝何が決め手で「なかった」か）

| 器 | 判定力 |
|---|---|
| runtime の **path** | ★無★（共有ゆゑ） |
| **ancestry（PPID 鎖）** | ★無★ ―― 1519165 は cmdline こそ `tmux new-session -d -s hermes-honbucho …` なれど**実体は tmux の server**（PPID=1）。**3体の doppler 包み（836658／1156226／4178443）悉く此処へ繋がる**ゆゑ、本部長固有の徴に非ず。★当職は一度之を決め手と誤読し、`ps` にて取り直して気付き申した★ |
| **`cwd`** | **有** ― 4178540 の cwd ＝ `/home/hakudokai/hermes-departments/honbucho` |
| ★**wrapper の exec 行そのもの**★ | ★**決定的**★ |

`/home/hakudokai/hermes-departments/honbucho/bin/hermes-honbucho` の実体（行8〜10）:
```
exec /usr/bin/doppler run --project openhands --config dev -- \
  /home/hakudokai/.local/libexec/dentalbi/promote_supabase_rotation_key.sh /usr/bin/env -u … \
  /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/venv/bin/python \
  /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/hermes --continue "$@"
```
**⇒ 観測した鎖（4178443 doppler＋rotation-key → 4178540 gunshi-runtime-python・cwd=honbucho）と逐語一致。**

### ★併せて 己の物差しの瑕を札す★
`awk '{print $4}' /proc/<PID>/stat` にて PPID を取ったが、**`stat` 第2欄 `(comm)` に空白が入ると欄がずれる**（`tmux: server` にて `S` を返し申した）。**`ps -o ppid=` にて取り直した**。★依拠した 4178540／4178443 は comm に空白無く値は正しかりしが、器の瑕として札す★。

---

## 三 実測 ― ★役は 3・runtime の樹は 2★（as_of 2026-08-20T08:31:31 JST）

| 役 | 走行 PID | 掴む runtime | version |
|---|---|---|---|
| `ashigaru-second-7-hermes` | 1156252 | `~/hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3`（**己の樹**） | **0.20.0** |
| `gunshi-second-hermes` | 836838 | `~/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3`（**己の樹**） | **0.20.0** |
| `hermes-honbucho` | **4178540** | ★**上の gunshi の樹を借用**★（己の樹 無し） | **0.20.0**（本部長殿実測 08:29:42 JST ＝ `Hermes Agent v0.20.0`） |

- **`pyproject.toml` を持つ樹は当PCに 2 本のみ**（`find -maxdepth 4`）。両者 **0.20.0**・mtime **2026-08-07T10:04:22 JST** より不変。
- **借用者は `hermes-honbucho` ただ一つ**（`hermes-departments/*/bin` ＋ `hermes-roles/*/bin` を grep し 1 件）。

---

## 四 ★巻戻し先は「同じ物」に非ず ―― ★一世代 後ろ★★

wrapper 行7 の註に「**戻す手順: 下2行を `/home/hakudokai/hermes-agent/venv/bin/hermes --continue "$@"` へ戻す**」と在り。**其の巻戻し先を測った**:

**`~/hermes-agent/venv/bin/hermes --version` ＝ ★`Hermes Agent v0.19.0 (2026.7.20)`★**（2026-08-20T08:31:31 JST）

- **⇒ 註の巻戻しは「元に戻す」に非ず、★0.20.0 → 0.19.0 の 降格★**に御座る。
- ★前紙にて当職は `~/hermes-agent/` を「役の runtime に非ず」と★推★した ―― 之も誤り。**本部長の ★旧★ runtime**にて、現に巻戻し先として註されて居る。**★推★ と札して置いた事のみが救ひ**。
- **rollback を安全策と見做す前に、此の一世代差を勘定に入れられたし**（★当職は触れ申さぬ・判断は owner の領分★）。

---

## 五 ★第4段の「分母」が 本部長殿と当職とで 違ひ申す★

| 誰 | 母集団 | 数 |
|---|---|---|
| 本部長殿（08:29:43 JST） | **本部長・軍師second**（a7 は別 role） | **0/2** |
| 当職（05:23:23 JST 基線・07:36:33 JST 再測） | **a7・軍師second** | **0/2** |
| **合（役で数ふ）** | **a7・軍師second・本部長** | **★0/3★** |
| **合（runtime の樹で数ふ）** | **gunshi 樹・a7 樹** | **★0/2★** |

- **★同じ「0/2」が 別の母集団を指して居り申した★**。**答（0.20.4 は一つも無し）は一致するゆゑ実害は出でざりしが、分母の食ひ違ひは札して置く**。
- **「全12体」を ★役で数ふるか 樹で数ふるか★ にて、検収の分母が変はる** ―― **委員長へ請ひ置いた名簿の件に、此の一問を添へ申す**。

---

## 六 ★爆風の及ぶ範囲（方式裁定の材料）★

**gunshi の樹に 0.20.4 を書けば、★軍師second と 本部長 の 二役が同時に動く★。**
- a7 は己の樹ゆゑ**独立**。
- 借用者は本部長ただ一人ゆゑ、**爆風は ちょうど 2 役**。
- ★ゆゑに本部長殿の「shared runtime 更新は相談役の方式裁定まで write/cutover/restart 0」は理に適ひ、当職も同じく 0 を守り申す★。

---

## 七 UNMEASURED（猶 解けず）

- **「全12体」の名簿** ― 当職の器の外。**役で数ふるか樹で数ふるかも未定** ⇒ 委員長へ請ひ置く（初出 2026-08-20T05:32:11 JST）。
- **他 PC（main／third）の Hermes** ― 器の外。**本紙の数は second_pc に限る**。
- **正本紙 `IINCHO-RULING-9` / `-15`** ― 当PCの樹に無く **sha 検算 0**（猶 二件）。
- **0.20.4 の在処・入替の方式** ― 相談役の裁定待ちにて、当職は測らず触れず。

---

## 八 変ぜぬ物

write 0 ／ cutover 0 ／ restart 0 ／ 強制終了 0 ／ install・pip・npm 一指 0 ／ tmux 一指 0 ／ send-keys 0 ／ capture-pane 0 ／ pane 入力 0 ／ Hermes 体への書込 0 ／ wrapper への書込 0 ／ 軍師second 直送 0 ／ 他 PC へ SSH 0 ／ queue/tasks 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ secret 値 読取 0（`environ` は開かず・doppler の中も見ず）／ 広域走査 0 ／ push 0。
