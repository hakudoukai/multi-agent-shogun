# 第4段 ―― ★Hermes 除外は「版」より手前で已に欠けて居る★（家老 c6f2e33 の危惧を予言でなく実測へ）

- **as_of: 2026-08-20T09:41 JST**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・pane 入力 0・network 0・fetch 0**
- 契機: 家老second `msg_20260820_093519_591feb65`（09:35:19・紙 `c6f2e33` sha256(16)=`f2309baec236…`）逐語 ―― 「★更に重き一件★=Hermes 除外は名簿でなく footer の綴り。第4段の入替で綴りが変はらば除外が黙って外れ Hermes pane も /compact を受け得る。**受入に一項=入替後 footer に除外語が猶在るを確かめよ**」
- **★物差しの違ひ★**: 家老＝**script の本文**（除外が何に懸かるか＝設計）。当職＝**現に走る 10 pane の footer を capture して regex を当てた**（＝実体）。同じ結論に着かず、**当職の実測は家老の危惧より一段手前で已に破れて居る事**を示した。

---

## 一 ★除外は「入替の後」ではなく ★今★ 既に一体で欠けて居る★

掃きの述語（`claude_pane_context_sweep.sh:20-21`）＝ `@agent_id` 非空の pane。実測の母集団 **10 体**。其の内 Hermes（`pane_current_command=doppler`）は **2 体**。

| pane | `@agent_id` | 母集団 | footer に命中した綴り | 判定 |
|---|---|---|---|---|
| `multiagent-second:0.7` (a7) | `ashigaru-second-7` | ★入る★ | **`voice off`** ＋ **`gpt 5`**（★二重★） | 守られて居る（冗長あり） |
| `hermes-gunshi-second:0.0` | `gunshi-second` | ★入る★ | **`gpt 5` のみ**（`voice off` ★欠★） | ★辛くも一本で守られ居る★ |
| `hermes-honbucho:0.0` | **空** | ★入らぬ★ | **0 件**（除外語 皆無） | ★除外に非ず 母集団外ゆゑ守られ居る★ |

### 何故 gunshi-second だけ `voice off` を失って居るか

pane 幅が狭く、**footer が右から截れて居る**（実測の逐語 ―― a7 は `… 1h 7m . voice off . 1 session` まで出るに対し、gunshi-second は `… 186h 48m   . ~` で切れ、以降の項目が悉く落ちる）。
⇒ ★除外は「綴りが在るか」ではなく「**其の綴りが幅の内に残るか**」に懸かって居る★。**`gpt 5.6 terra` が footer の前寄りに在るゆゑ、辛うじて一本だけ生きて居る。**

## 二 ★∴ 除外が外れる道は 三つ在り、版はその一つに過ぎぬ★

1. **★幅★** ―― pane を細める／window を分割すれば `voice off` は落ちる（**現に落ちて居る**＝標本 1 体で実証済）。`gpt 5.6 terra` より右の項目は悉く同じ危険下に在る。
2. **★model 表示★** ―― 命中の実体は `gpt[ -]?5`。**model を gpt-5 系以外へ切替へた刹那、gunshi-second は除外語が ★零★ に成る**（`voice off` が幅で落ちて居るゆゑ、二本目の綱が無い）。入替とは無関係に、**今日にも起こり得る**。
3. **版**（家老の指摘）―― 0.20.4 で footer の項目名・順・略記が変はれば落ちる。

**∴ 家老の一項は正しく、且つ ★狭すぎる★。**受入条件は「入替後に除外語が在るか」ではなく、**「入替後・★当該 pane の現の幅で★・★現の model 表示のまま★ footer に除外語が残るか」** と、三条件を明記して書かれたし。

## 三 ★honbucho の守りは除外に非ず ―― 一行の set-option で崩れる★

`hermes-honbucho:0.0` は `@agent_id` が**空**ゆゑ母集団に入らぬ。而して **footer に除外語は一つも無い**。
⇒ ★誰かが此の pane に `@agent_id` を set した刹那、本部長の pane は「除外に当たらぬ Hermes」として判定器へ渡る★。（当職は set せぬ・触れぬ。**測っただけ**。）
⇒ 之は「名簿を持たぬ設計」の裏面にござる ―― 名簿は陳腐化するが、**footer 依存は幅・model・版の三方向へ崩れ、且つ崩れても誰も叫ばぬ**（`hermes_skip` が log に出なく成るだけ）。

## 四 ★source の突合は ―― 判じ得ず（UNMEASURED と札す）★

当職の器の第四の樹（`~/hermes-runtimes/hermes-agent-v2026.8.3/.git`・`origin/main`=`6a3d50c`＝**0.20.4**）にて、両 ref を突合した（**fetch 0・ローカル object のみ**）:

- **対照**（両 ref に必ず在る綴り）: `pyproject.toml` の `hermes` ―― HEAD 48 件 / origin/main 47 件 ⇒ **器は生きて居る**。
- **問**: `voice (off|on)` / `gpt[ -]?5` ―― **両 ref とも命中す**（`cli.py` / `gateway/platforms/base.py` / `agent/agent_init.py`）。
- **★併し之を「除外は 0.20.4 でも生きる」の証に据ゑてはならぬ★** ―― 命中は悉く **help 文言・註釈・test** であり、**footer の実体は動的組立**（`f"voice {mode}"` の形）にて、literal `"voice off"` は source に**存在せぬ**。∴ **source diff では footer の最終の綴りを判じ得ぬ。**
- **⇒ 「0.20.4 の footer に除外語が残るか」は ★UNMEASURED★**。塞ぐ手は一つ ―― **入替後に ★実際の pane を capture して当てる★**（節二の三条件下で）。**予言では閉じられぬ。**

## 五 受入条件の具申（更新・二項）

1. （家老 c6f2e33 の一項を強めて）**入替後、対象 pane を `capture-pane -p | tail -3` で捕へ、`grep -qE 'voice (off|on)|gpt[ -]?5'` を当てて命中を確かめよ。**★其の pane の現の幅・現の model のまま★測る事（幅を広げて測れば偽の緑に成る）。
2. **命中が ★一本だけ★ の pane（現 gunshi-second）は「守られて居る」と書くな** ―― **冗長 0** と札せ。二本目（`voice off`）が幅の外に在る事を併記せよ。

## 六 為さぬ事

pane への入力 / `set-option` / resize / model 切替 / 番人の停止・disable・timer 改変 / `sweep_manifest.json` 改変 / launcher 改変 / restart / cutover / install / fetch / `systemctl` の実行 ―― **悉く 0**。`capture-pane` と `list-panes` は**読取のみ**（掃きが現に用ゐる述語を、同じ形で当職の器から引いた）。
