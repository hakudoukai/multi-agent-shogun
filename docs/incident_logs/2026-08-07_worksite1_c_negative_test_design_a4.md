# 工区1 ⒞ 負テスト3形 ★設計宣言★ (実行前・数が出る前に形を固定)

- 起案: 足軽4号 (ashigaru4, `multiagent-second:0.7`, `%16`)
- 日時: 2026-08-07 20:19 JST
- 出所: 理事長令「通信経路恒久安定化」工区1 → Commander `msg_20260807_201018_d1d9e5ea` → 将軍second `msg_20260807_201322_adbe40db` → 家老second `msg_20260807_201541_b56065bf`
- task YAML key: `current_order_15_20260807_201500_WATCHER_RESIDUE_TESTS_LEDGER`
- 測定断面: HEAD=`4c91e9e` / `scripts/inbox_watcher.sh` 1728行 (最終改修 `b9bec71`)
- 本票の性格: ★設計の宣言のみ★。★一形も走らせて居らぬ★ (§5 に試した形/試して居らぬ形を明記)

---

## 0. 本票の位置づけ ―― 「PASSと書くな」の条

本票は ⒞ の ★形を先に固定する★ ための宣言に御座る。数 (PASS/FAIL件数) は ★一つも★ 載せ申さぬ。
実行は a2 の ⒝ 完了報 + interface 契約 (検知条件・prefix 定義) 受領の後。
本票を出す時点で a2 の工区1票は ★未在★ (`docs/incident_logs/` 検索・20:19 実測) ゆえ、
§2 の契約欄は ★当職の想定★ であり、a2 の票が出た時点で ★契約欄のみ差し替え・述語は不変★ とする。

---

## 1. 対象欠陥の形 (当職の理解)

codex 型配送路で、C-m (Enter) 送出後も ★注入した prefix が composer に残骸として残る★。
a2 の ⒝ 根治 = 「C-m 後に capture し、composer 残存が ★注入 prefix と完全一致★ の時のみ C-u 掃除」。

★危うきは掃除の側★ ―― C-u は composer を無差別に消す。ゆえに ★掃除が走ってはならぬ三つの場合★ を
先に固定するのが本工区 ⒞ に御座る。

### 1.1 ★実測所見★ ―― 既存 C-u は悉く「盲」に御座った (anti-dup の要)

`scripts/inbox_watcher.sh` の現況 C-u 送出site を行で列挙 (件数でなく行で書く):

| # | `path:line` | 文脈 | 条件 |
|---|---|---|---|
| ⑴ | `scripts/inbox_watcher.sh:635` | `send_keys_verified()` 各 attempt の冒頭 | ★無条件★ (composer 中身を見ずに送出) |
| ⑵ | `scripts/inbox_watcher.sh:835` | `send_codex_startup_prompt()` | ★無条件★ + `\|\| true` (失敗も握り潰す) |
| ⑶ | `scripts/inbox_watcher.sh:887` | `send_context_reset()` codex `/new` 枝 | ★無条件★ + `\|\| true` |
| ⑷ | `tests/unit/test_send_wakeup.bats:498` が模す unread=0 idle 路 | 掃除 | `agent_is_busy` のみで gate (composer 中身は ★見ぬ★) |

∴ ★現況の C-u は一つとして「composer の中身」で条件付けられて居らぬ★。
a2 の ⒝ が入れるのは ★repo 初の「中身条件付き C-u」★ に御座る。本票の3形は其れに対する負テスト。

---

## 2. interface 契約 (a2 ⒝ に対する当職の想定・a2 票到着で差し替え)

負テストが噛むためには、a2 実装が次の形を満たす必要が御座る。★契約として先に宣し、満たさぬ場合は FAIL でなく `contract_mismatch` として上申する★。

- **C-1**: 掃除判定が ★単一の production 関数★ に閉じて居る事 (例: `codex_residue_cleanup()`)。
  述語は其の関数を ★直に呼ぶ★。★テスト側で if/else を書き写す事は禁★ (§6 の条)。
- **C-2**: 関数が「注入した prefix 文字列」を ★引数か大域変数で受け取る★ 事 (期待値が外から与えられる)。
- **C-3**: 掃除の実行が ★観測可能★ な事 ―― `tmux send-keys ... C-u` が MOCK_LOG に現れる/現れぬで判別可能。
- **C-4**: 「完全一致」の定義が票に逐語で在る事 (前後の空白・末尾スペース・改行を ★どう正規化するか★)。
  ★本欠陥は末尾スペースが源の一つと目されて居る★ ゆえ、正規化規則が述語の成否を直に変える。

---

## 3. ★負テスト3形★ (fixture / 手順 / PASS・FAIL 述語)

共通土台: `tests/unit/test_send_wakeup.bats` の既存 harness を ★流用★ (新規発明せず・Anti-Duplication)。
= `__INBOX_WATCHER_TESTING__=1` で ★本物の `scripts/inbox_watcher.sh` を source★ し、`tmux` を関数 mock、
`MOCK_CAPTURE_PANE` で composer 現況を注入、`MOCK_LOG` に全 tmux 呼出を記録する形。

★之ゆえ 3形は live watcher process を要し申さぬ★ (§4 で詳述)。

### ㈠ 本物 draft が composer に在る時、C-u 掃除が走らぬ事

| 欄 | 内容 |
|---|---|
| 狙い | ★人 (または agent) が書きかけた文★ を watcher が消さぬ事。三形中 ★最も損害が大きい★ 誤作動。 |
| fixture | 注入 prefix = `inbox2` (仮)。`MOCK_CAPTURE_PANE` = composer に ★全く別の文★ が在る状態。逐語例: `› 副院長殿へ 本日の残件を纏めて` |
| 手順 | harness を source → 注入 prefix を C-2 の経路で与える → 掃除判定関数を ★直に呼ぶ★ → `MOCK_LOG` を検める |
| ★PASS★ | `MOCK_LOG` に `send-keys` の `C-u` が ★一つも現れぬ★ 事。かつ関数の返値が「掃除せず」を表す事。 |
| ★FAIL★ | `C-u` が ★一つでも★ 現れた時。= ★本物 draft 破壊★。 |
| 補助形 | 「composer に prefix ★と★ 別文が併存」(例: `› inbox2 と書いた後に続けて人が打った`) でも ★走らぬ★ 事を別 case で測る。★完全一致でない★ ゆえ。 |

### ㈡ prefix ★部分一致★ で走らぬ事

| 欄 | 内容 |
|---|---|
| 狙い | 「完全一致時のみ」の条が ★実際に完全一致で実装されて居る★ 事の検め。部分一致で走れば ㈠ の守りが崩れる。 |
| fixture | 注入 prefix = `inbox2`。composer 側を次の ★四通り★ に振る (行で列挙・件数で書かず): |
| | ⓐ 前方に余分: `› xinbox2` |
| | ⓑ 後方に余分: `› inbox2x` |
| | ⓒ 真部分列 (prefix の一部のみ): `› inbox` |
| | ⓓ 別の unread 数: `› inbox3` (★同型・別便の残骸★。之を消すのは別便の破壊に当たる) |
| 手順 | ⓐ〜ⓓ 各々で ㈠ と同じ手順 |
| ★PASS★ | ⓐ〜ⓓ ★悉く★ で `C-u` が現れぬ事 |
| ★FAIL★ | いずれか一つでも `C-u` が現れた時。★どの case で漏れたかを行で記す★ (「N件 FAIL」と書かぬ) |
| 未確定 | ⓔ 末尾スペース差 (`› inbox2 ` ―― 末尾に空白一つ) は ★C-4 の正規化規則次第で PASS/FAIL が反転する★。∴ ★契約受領前に述語を固定せず★、a2 の正規化規則を受けてから ⓔ の期待値を定める。★本票では ⓔ を「述語未定」と明記する★。 |

### ㈢ 着弾成功時に掃除が走らぬ事

| 欄 | 内容 |
|---|---|
| 狙い | 正常配送 (Enter が効いて会話面に着弾・composer は空) で余計な C-u を撃たぬ事。撃てば ★次の入力を待つ人の手元を消す★。 |
| fixture | 注入 prefix = `inbox2`。`MOCK_CAPTURE_PANE` = ★着弾済の会話面★ + ★composer 空★。逐語例: 会話面に `inbox2` が現れ、入力行は `› ` のみ。 |
| 手順 | ㈠ と同じ |
| ★PASS★ | `C-u` が現れぬ事 |
| ★FAIL★ | `C-u` が現れた時 |
| ★罠★ | 本形は ★偽陽性を生み易い★ ―― 着弾した `inbox2` は ★会話面にも★ 在る。判定が capture 全体を見れば「prefix 在り」と誤り、掃除が走る。∴ 本形は ★「判定が composer 行のみを見て居るか」の検め★ を兼ねる。a2 の実装が capture 全体を grep する形なら ★本形は FAIL する筈★ = 之が本形の存在意義に御座る。 |

---

## 4. ⒠blocker 配下として ★実行せぬ★ 形 (代走・偽装せず)

★上の3形は live watcher process を要し申さぬ★ ―― 既存 harness が本物 script を source して関数を直に呼ぶ形ゆえ。
★之は当職の実測に基づく判定★ (`tests/unit/test_send_wakeup.bats:70-160` の harness を読んだ上での判断) に御座る。

★されど★ 次の形は live watcher / 実 pane を要する ∴ ★⒠blocker (watcher lifecycle = 委員長・将軍上申済) 配下★ として ★実行せず blocked と記す★:

| 形 | 要る物 | 状態 |
|---|---|---|
| ㊀ 実 codex pane での端対端 (実配送→実残骸→実掃除) | live watcher + hermes 実 pane への送出 | ★blocked★ (境界: hermes pane は capture のみ・送るな) |
| ㊁ 実 composer に人の draft を置いた上での破壊有無 | 実 pane への打鍵 | ★blocked★ (同上) |
| ㊂ watcher 再起動を挟んだ残骸の持ち越し | watcher 起動/停止 | ★blocked★ (境界: watcher 起動・停止・再起動 0) |
| ㊃ 末尾スペースの ★源★ の切り分け (send-keys 組立て か CLI 補完か) | 実 pane 観測 | ★a2 の ⒝② の領分★ ―― 当職は測らぬ (二重実装回避) |

★㊀〜㊂ を mock で代走して「端対端 PASS」と書く事は禁★。mock で測れるのは §3 の3形まで、と本票に固定する。

---

## 5. ★試した形 / 試して居らぬ形★ (「PASSと書くな」の条)

- ★試した形★: ★無し★。本票は設計宣言に御座る。一形も走らせて居らぬ。
- ★試して居らぬ形★: ㈠ ㈡(ⓐⓑⓒⓓ) ㈢ ―― 悉く。a2 の ⒝ 完了報 + interface 契約 受領後に走らせる。
- ★述語未定の形★: ㈡ⓔ (末尾スペース差) ―― C-4 の正規化規則を受けてから定める。
- ★実行せぬと決めた形★: ㊀㊁㊂ (⒠blocker 配下) / ㊃ (a2 の領分)。

---

## 6. 設計上の ★所見★ ―― 既存2形は「己の写しを測って」居る

`tests/unit/test_send_wakeup.bats` の T-CODEX-003 (`:489`) / T-CODEX-004 (`:514`) は、
production 関数を呼ばず ★test 本体の中に if/else を書き写して★ 其れを測って居り申す
(`:496-503` / `:521-529` の `if ! agent_is_busy; then ... tmux send-keys ... C-u` は
`scripts/inbox_watcher.sh` の当該路の ★複製★ に御座る)。

∴ 本体が変わっても ★此の二形は緑のまま★ に御座る = ★述語が本体に噛んで居らぬ★。
之を ⒟ 台帳の一項として登録し (§ 台帳票 参照)、当職の3形は ★必ず production 関数を直に呼ぶ★ 形で組む
(§2 C-1)。★同じ轍を踏まぬ★ ため本票に先に焼き申した。

---

## 7. 次の一手

1. a2 の ⒝ 完了報 + interface 契約 (検知条件・prefix 定義・C-4 正規化規則) を待つ
2. 契約を §2 に差し替え (★述語は不変・契約欄のみ★)、㈡ⓔ の期待値を定める
3. §3 の3形を `tests/unit/` へ組み、走らせ、★行で★ 結果を記す (件数で書かず)
4. 契約が C-1〜C-4 を満たさぬ場合は FAIL でなく `contract_mismatch` として家老second へ上申

---

*足軽4号 2026-08-07 20:19 JST ―― 本票は ★設計宣言★ ゆえ、以後 a2 契約受領時に §2 と §5 を改める (其の折は改訂の旨を明記する)*
