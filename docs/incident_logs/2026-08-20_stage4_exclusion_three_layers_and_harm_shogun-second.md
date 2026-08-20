# 第4段 ―― 除外は ★二層に非ず 三層★ ／ ★危害の中身を測り申した（`/compact` は Hermes にて `/compress` の alias ＝ 現に走る）★

- **as_of: 2026-08-20T09:58 JST**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・pane 入力 0・network 0・fetch 0**
- 契機: 家老second `msg_20260820_095409_b3022e53`（09:54:09・紙 `6514c43` sha `a43b8a8d74de`）―― 「除外は**二層**（層1 母集団＝`@agent_id` 非空／層2 footer の綴り）。honbucho は**層1のみ**で守られ居る。**pane 毎に どの層で守らるるか併記されたし**。**危害の中身は UNMEASURED ゆゑ上へ問ひ申した**」
- 本紙は其の**二つの答**: ①層は**三つ**在る ②**危害の中身を測った**。

---

## 一 ★層は三つ ―― 家老の二層の下に「判定器の語彙」が在る★

| 層 | 実体 | 逐語の在処 |
|---|---|---|
| **層1 母集団** | `@agent_id` 非空の pane のみ掃く | `claude_pane_context_sweep.sh:20-21` |
| **層2 除外** | `tail -3` へ `voice (off\|on)\|gpt[ -]?5` ⇒ `hermes_skip` | 同 `:33-34` |
| **★層3 発火★** | 判定器の `FULL_RE` ＝ `100%\s*(?:context\|used)` ／ `context\s*(?:used)?\s*100%` に**当たらねば `not_full` にて撃たぬ** | `~/bin/claude_context_auto_compact.py`（sha256(16)=`b430a58765aaa119`） |

## 二 ★pane 毎に「どの層で守らるるか」（家老の求めに応ず）★

| pane | 層1 | 層2 | 層3 | 守りの厚み |
|---|---|---|---|---|
| `multiagent-second:0.7` (a7) | 入る | **二重**（`voice off` ＋ `gpt 5`） | 見込 有効 | ★厚し★ |
| `hermes-gunshi-second:0.0` | 入る | **一本のみ**（`gpt 5`。`voice off` は幅で截れ欠） | 見込 有効 | ★冗長 0★ |
| `hermes-honbucho:0.0` | **外**（`@agent_id` 空） | **0 件** | 見込 有効 | ★層1 の一手のみ ―― `set-option` 一つで消ゆ★ |
| `shogun-second:0.0`（当職） | 入る | 当たらず（正当） | **有効＝現に守り** | 判定器の的 |

**⇒ 家老の申す通り、honbucho の守りは ★一手★ に懸かる。** 而して**層3 が在るゆゑ、層1・層2 が悉く外れても直ちに撃たれる訳ではない** ―― 之が家老の二層図に足すべき一段にござる。

## 三 ★層3 の実測 ―― 判定器の語彙は Claude の footer の物であって Hermes の物に非ず★

現の 3 pane の `tail -20` へ判定器の regex を**そのまま当て申した**:

| pane | `FULL_RE` 命中 | `context`／`used` の語 |
|---|---|---|
| a7（Hermes） | 0 | **0** |
| gunshi-second（Hermes） | 0 | **0** |
| **shogun-second（Claude・★対照★）** | 0（当職は満杯に非ず） | **1** |

**★対照の値打ち★**: 同じ器・同じ窓で Claude の pane にのみ `context`／`used` の語が出る ⇒ **器は生きて居り、Hermes 側の 0 は「掃きの死」ではなく「語が無い」**。
**⇒ 推論（★印）**: Hermes の footer は百分率を `[▒▒▒] 7%` の形で出し、**`context`／`used` の語を一切伴はぬ**。∴ 満杯に成っても綴りは `100%` 単独と成り、**`FULL_RE` は当たらぬ公算**。
**★併し断ぜず★**: 満杯時に Hermes が警告語を足すか否かは**観測し得ぬ**（当職の器の Hermes は 7%〜8%）。**★層3 の Hermes に対する発火 ＝ UNMEASURED★**。**「層3 が在るゆゑ安全」と段取りを組むべからず。**

## 四 ★危害の中身 ―― 家老が上へ問うた UNMEASURED を、当職の器にて閉じ申した★

問: 若し層1・層2・層3 が悉く外れ、Hermes pane へ `/compact` が刺さったら **何が起きるか**。

**答: ★弾かれぬ。実行される。★** 当職の器の Hermes source（第四の樹）にて実測 ―― **`/compact` は Hermes の実在の slash command にして、`/compress` の ★alias★**:

```
tests/cli/test_compress_flags.py:39:    assert "/compact" in COMMANDS
tests/cli/test_compress_flags.py:40:    assert "alias for /compress" in COMMANDS["/compact"]
```

**★両 ref に在り★**（HEAD＝0.20.0 命中 34 件／`origin/main`＝**0.20.4** 命中 35 件。対照＝`"/help"` は両 ref の複数 file に実在＝器の生存）。

**∴ 危害は「見知らぬ命令が無視される」ではなく ―― ★Hermes の会話が現に圧縮される★**。
之は委員長 seq199833 ⑴「**★会話を失うな★**」に真っ向から当たる（圧縮は喪失に非ずと言へど、**執行者の意図せぬ刻に・意図せぬ体へ**掛かる）。**家老の危惧は「起こり得るか」ではなく「起これば効く」段階にござる。**

## 五 受入条件の具申（三度目の更新・四項）

1. **入替後・当該 pane の現の幅・現の model のまま** `capture-pane -p | tail -3` を捕へ、除外 regex を当てて命中を確かめよ（前紙 `305c7c4`）。
2. **pane 毎に ★どの層で守らるるか★ を併記せよ**（家老の求め）。**層1 のみの pane（現 honbucho）は「守られ居る」と書かず ★一手★ と札せ**。
3. **層3 を安全の根拠に据ゑるな** ―― Hermes に対する発火は **UNMEASURED**（節三）。
4. **危害は ★UNMEASURED に非ず★** ―― `/compact` は `/compress` の alias にて**現に走る**（節四）。**∴ 段取りは「刺さっても無害」を前提に組むべからず。**

## 六 為さぬ事

pane 入力 / `set-option` / resize / model 切替 / 番人の停止・disable・timer 改変 / `sweep_manifest.json` 改変 / launcher 改変 / restart / cutover / install / fetch / `systemctl` 実行 ―― **悉く 0**。`capture-pane` と `list-panes` は**読取のみ**、source は**ローカル object の読取のみ**（fetch 0）。
