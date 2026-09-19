# 納 ―― 裁337507⑶疵② ★前方一致で生きた席を掴む形を廃す★

刻(作): 2026-09-19T13:25:46+0900 ／ 席: 家老mac(karo-mac, %68) ／ 親裁: seq337507⑶疵②(★最優先★)
逐語: 「⑶疵②前方一致で生きた%72を掴む形=★最優先★。-t は =名 か %N へ。固定寫像は該当session無ければfail-closed。併せ前方一致を使ふ器を横展開で數へよ。」

## 一 ★先に己の疵を四つ申す★

1. 前便で死に行を「L139」と書いた。原版(sha256 4ff08530…)では **L137** である。L139 は
   ★疵②を彫つた後の版★の行であり、行は版で動く。（紙の内では行を焼かず字面で locate して居る）
2. 自己除去の門が頭の `./` 違ひで一度も鳴らず、`除いた(己の束)=0` を刷つた ―― ★除いた證ではなく偽の通★。
3. 直した後も數へ方が束直下の file のみで再び 0 と出た（★同じ偽の通を二度★）。
   ∴ 陽性対照「除いた(己の束) が束内 file 実数と一致すること」を据ゑ、9→10 で一致を得た。
4. `rc=${PIPESTATUS[0]}` を zsh で書き rc が空に成つた。zsh は `pipestatus` ―― 既に記憶に在る罠を再び踏んだ。
   raw/30 に訂として管を通さぬ再測を追記して居る。

## 二 ★疵の實體（測つた）★

疵②は `scripts/agent_status.sh` の MainPC 路に在つた一行:

    pane_target="multiagent:agents.${pane_idx}"    （原版 L358）

当機に `multiagent` という session は**無い**。然し tmux は `multiagent-mac` へ**前方一致**し、
かつ `display-message` は**不在の的でも rc=0** を返す ∴ 六席が悉く偽の値を刷つて居た。

| 行 | 旧 | 何處を掴んで居たか |
|---|---|---|
| hideyoshi | 稼働中 | **%68 = 家老mac 自身** |
| ashigaru1 | 待機中 | **%72 = 專任1** |
| ashigaru2 | 待機中 | **%7 = 專任2** |
| ashigaru3 | 待機中 | **%125 = 專任3** |
| ieyasu | 待機中 | index 4 は無い → **%7 專任2 へ黙つて倒れた** |
| takenaka | 待機中 | index 5 は無い → **同上** |

★之は「見えるだけ」の疵ではない★ ―― 同じ的の組み方で C-c や /exit を送る器が在れば
**生きた席へ着弾する**（裁337430 が㋑と呼んだ破壊）。

併せて同じ file の standalone 路にも同類が二つ在つた（原版 L111 / L137）:

    while IFS= read -r line; do PANE_TARGETS+=("$line"); done < <(tmux list-panes -s -t "$SESSION_NAME" ...)

- `--session multiagent`（当機に無い名）→ **rc=0 で multiagent-mac の四席を刷る**（偽の通）
- `--session zzzznosuch` → **bash 3.2 の空配列＋set -u** で `PANE_TARGETS[@]: unbound variable` と死ぬ（表の冠は既に出て居た）

## 三 ★tmux 3.7b の的語法 ―― 測つて初めて判つた四事（裁の処方の一半を撃ち落す）★

裁337507 は「-t は =名 か %N へ」と処方された。**実測では `=名` は一箇所でしか効かぬ。**

| # | 測つた事 | 出目 | 意味 |
|---|---|---|---|
| ⑴ | `has-session -t '=multiagent'` | **rc=1** "can't find session: multiagent" | ★効く★ |
| ⑵ | `list-panes -s -t '=multiagent'` | **rc=0・multiagent-mac の四席を返す** | ★効かぬ★（誤りの字面が "can't find **window**" ゆゑ window 的と解され session 部へ `=` が掛からぬ） |
| ⑶ | `display-message -t '=zzzz:agents.0'` / `-t '%99999'` | **共に rc=0・出は空** | ★rc で不在を判じ得ぬ★ |
| ⑷ | `display-message -t 'multiagent:agents.4'` | **rc=0 → `%7 ashigaru-mac-2`** | ★index 溢れが其の session の現用 pane へ黙つて倒れる★ |
| ⑸ | `capture-pane -t 'multiagent:agents.4'` / `-t '%99999'` | 共に rc=1 "can't find pane" | ★鳴るのは此れのみ★ |

**∴ 信ずるに足る形は `%N`（悉皆列挙＋`@agent_id` 完全一致）のみ。
session 名を要する所は `has-session -t '=名'` **だけ** を門に使ふ。**
（裁337482 で「名でなく★識別子★で当てる方が良い」と裁かれた路が、此の実測で裏付いた）

raw: `raw/30_tmux_gohou.txt`

## 四 ★据ゑた形★

⑴ 識別子で解く器を据ゑた（n>1 は★当てず rc=3★＝曖昧を黙らせぬ）:

    km_pane_id_by_agent_id() { ... tmux list-panes -a -F '#{pane_id} #{@agent_id}' | awk '$2==w{print $1}' ...
        n==1 → pane_id を返す / n>1 → return 3 / n==0 → return 1 }

⑵ MainPC 路: 固定寫像を廃し、①`@agent_id` 完全一致 → ②当たらねば `has-session -t '=名'` の門 →
   ③門が閉ぢて居れば**寫像せず不在**（fail-closed）。母數行へ
   `的: @agent_idで解けた=N ★曖昧=N★ 寫像不能(session無)=N 寫像不能(pane無)=N` を常設し、曖昧>0 で黙らぬ行を出す。

⑶ standalone 路: ①`has-session -t '=名'` で門を立て、前方一致では当てぬ（rc=1）
   ②的は `%N` を悉皆列挙で組み、見出しのみ `session:window.pane`
   ③該当 pane 0 本なら**空配列を触る前に rc=1**（bash 3.2 の死を封ず）。

## 五 ★両対照（裁337430「外れる路=rc≠0で無害／当たる路=従来通り」）★

raw: `raw/10_before.txt`（原版 4ff08530… を `scripts/` へ仮置きして走らせた・直後に退けた）
     `raw/20_after.txt`（治した版 55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31）

| 路 | 旧 | 新 |
|---|---|---|
| MainPC 既定 | rc=0・**六席が偽**（生席 %68/%72/%7/%125 を掴む） | rc=0・**十一席悉く不在**・母數行に `寫像不能(session無)=6` |
| `--session multiagent` | rc=0・**他 session の四席を刷る** | **rc=1**「完全一致で存在せぬ」・表の冠も出さぬ |
| `--session zzzznosuch` | **rc=1 だが `PANE_TARGETS[@]: unbound variable`**（器の死・冠は既出） | **rc=1**・一行の誤りのみ |
| `--session multiagent-mac` | rc=0・四席 | **rc=0・四席（従来通り）** |
| `--session multiagent-mac --panes 99` | （旧は空配列で死ぬ） | **rc=1**「該当する pane が無い」 |

★当たる路は字面まで従来通り★（見出しは `multiagent-mac:agents.N` の儘・的のみ `%N` へ）。

## 六 ★横展開（併せ數へよ）―― 三つの母數を分けて申す★

★同じ「前方一致」を三通りの母數で數へた。並べて讀むな。★

### 甲 repo 全体（queue/ 13G と .claude/worktrees/ を含む＝裁337481「★歩かせよ★」への答）
raw: `raw/40_census_kou.txt`（刻 13:23:03）
全file **52809** / 読めた 51368 / 除いた(>1MB) 141 / 除いた(binary) 1299 / 除いた(己の束) **10**（陽性対照=束内実数と一致）
**rc(歩行)=1 ―― 躓いた file を名指せた: 1 本のみ**
`queue/reports/ashigaru-mac-3_km-mon-wo-tomeru-katachi-wo-genri-de-tojiro-20260913_evidence/shiryou/tomari24/p10_reg_noread`
（PermissionError 13 ―― 專任3が意図して据ゑた「読めぬ file」の fixture）∴ **rc=1 の因は尽きた**。
tmux `-t` の的 **9005** = ★前方一致risk **3501**★ / pane_id 69 / 完全一致 2 / 変数 5433 ／ risk を持つ file **279 本**
`ashigaru-mac-4/5/6` の字面 **30789 件 / 1143 本**（-4=18665 / -5=5600 / -6=6524）

### 乙 当repo 本体（`.claude/worktrees` と `queue` を除く）
raw: `raw/41_census_otsu_honntai.txt`
全file **17141** / 読めた 16733 / **rc(歩行)=0** / 除いた(名指の根)=35811
的 5380 = ★risk **1881**★ / pane_id 3 / 完全一致 2 / 変数 3494 ／ risk を持つ file **139 本**
`-4/5/6` = **12878 件 / 105 本**

### 丙 ★走る器★のみ（実行bit か .sh/.py/.bats/.zsh/.bash）
raw: `raw/42_census_hei_hashiru_kiki.txt`
全file 35288 / 器 **2435** / 読めた 2435

| 類 | 件/本 | 中身 |
|---|---|---|
| 甲 `-t` に裸の session 名 | **99件 / 7本** | 下記 |
| 乙 的を組む代入に裸名（`-t` は変数ゆゑ甲に出ぬ） | **16件 / 11本** | 下記 |
| 丙 `-t %N` | **0件 / 0本** | ★「安全な器が 0」の意ではない★（動的解決は変数へ落ちる） |
| 丁 `-t =名` | **2件 / 1本** ←★0 から増えた★ | `scripts/agent_status.sh:106` `:418`＝**本件の是正そのもの** |

甲 7本の内訳: `shutsujin_departure.sh` **44** / `shutsujin_departure.sh.karo-mac-bak-20260820T000340` **44**（★器⑵の除外が `.bak` の字面のみを見て `-bak-` を見ぬ疵・控 file が母數に混じつた★） / `first_setup.sh` **6** / 紙の中の器 `queue/reports/…/31_write_paper.py` **2** / `tests/test_section18_migration.py` 1 / `tests/e2e/e2e_bloom_routing.bats` 1 / `scripts/agent_periodic_push.sh` 1
**∴ 是正すべき★生きた器★= 5本 / 53件**（控と紙を除く）

乙 11本の内訳: 紙の中の器 `…/.write_paper.py` 4 / `tests/unit/test_send_wakeup.bats` 2 / `shim/hakudokai/hakudokai_activity_monitor.sh` 2 / `tests/e2e/mock_cli.sh` 1 / `tests/checks/test_agent_health_check.bats` 1 / `scripts/ratelimit_check.sh` 1 / `scripts/karo_standby_dashboard.sh` 1 / `scripts/checks/pane_identity.sh` 1 / `scripts/bulk_ack.sh` 1 / `lib/cli_adapter.sh` 1 / **`scripts/agent_status.sh` 1 ＝★偽陽性★**（`FIXED_SESSION="multiagent"` の代入だが直後に `has-session -t "=…"` の門を通る。器⑵は「代入の先で門を通るか」を見ぬ）
**∴ 是正すべき★生きた器★= 9本 / 11件**

★母數の食違を隠さず申す★: 本日午前の狭い根での走は 甲53件/5本・乙12件/10本 であつた。
今回 乙 は 11件/9本(生きた器)で、**test 1本が前走に在り今走に無い**。因は★未突合★（根の差か SKIPDIR か）。

## 七 ★残る弾（本件では直さぬ・別弾として申す）★

1. **`lib/agent_status.sh` の死んだ `return 2`** ―― `agent_is_busy_check` は
   `if ! tmux display-message -t "$pane_target" ... ; then return 2 # pane truly absent` で不在を判ずるが、
   `display-message` は**常に rc=0** ∴ **`return 2` は一度も通らぬ**。結果 capture が空→`return 1`＝
   ★偽の待機中★（不在ではなく「尤もらしい偽値」＝裁337429 が本日二番目に重いと裁いた形）。
   ★lib は触れて居らぬ★ ―― `scripts/inbox_watcher.sh:71/:1673` が source して**稼働中**ゆゑ。
   本件は**呼ぶ側で fail-closed** にし、lib へは検めた `%N` しか渡さぬ形で止血した。
   消費する器: `tests/unit/test_send_wakeup.bats:556/557` `tests/e2e/e2e_bloom_routing.bats:31`
   `scripts/ratelimit_check.sh:28` `scripts/agent_status.sh:47` `scripts/inbox_watcher.sh:71/1673` `lib/cli_adapter.sh:1070`
2. **疵①**（`--lang/--session/--panes` の値無しで `$2: unbound variable` 死）―― usage で閉ぢ
   ★使ひ方の誤=1 / 器の死=2★ に rc を分ける。別弾。
3. **横展開の是正**（甲 生きた器 5本 / 乙 生きた器 9本）―― 別弾。`shutsujin_departure.sh` 44件が最大。
4. **器⑵の `.bak` 除外**が `-bak-` を見ぬ疵。器⑴の `rc` が躓きを名指さぬ疵は**本件で直した**。

## 八 成果物

| path | sha256 | byte | 行 |
|---|---|---|---|
| `scripts/agent_status.sh`（後） | `55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31` | 21898 | 467 |
| `scripts/agent_status.sh`（前・疵②彫る前） | `4ff08530e5ea70106c04c5de1b54a49dcdadfc5a6f3468ac4b809364717faac5` | 16339 | 375 |
| （中間・疵②のみ彫つた版） | `0fb99fa509ec761ed274494d374f8e39914a8776b3fc57eac99f07c961167f76` | 20565 | 445 |

`bash -n scripts/agent_status.sh` → **rc=0**

## 九 法令根拠

該当せず（内部の的解決の是正であり、算定・記載要件に触れぬ）。
