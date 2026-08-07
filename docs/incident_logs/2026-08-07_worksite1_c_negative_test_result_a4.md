# 工区1 ⒞ 負テスト3形 ★実行結果★ + ⒟ 罠台帳 新設

- 起案: 足軽4号 (ashigaru4) / 2026-08-07 20:58 JST
- pane 実測: `@agent_id=ashigaru4` @ `multiagent-second:0.4`
  ★設計票 (20:19) には `multiagent-second:0.7` と書いて居るが、之は ★古い断面★ に御座る★。
  境界令の「0.7 (d6a5501c) 不触」と併せ、★当職の現在地は 0.4★。設計票の在中欄は superseded (誤りでなく古い断面)。
- 出所: 理事長令「通信経路恒久安定化」工区1 → Commander `msg_20260807_201018_d1d9e5ea` → 将軍second `msg_20260807_201322_adbe40db` → 家老second `msg_20260807_201541_b56065bf`
- 設計票 (★先に形を固定した票・作り直して居らぬ★): `docs/incident_logs/2026-08-07_worksite1_c_negative_test_design_a4.md` (154行 / `e3a5bd14566463a41b7ee7cfea934a9ccb171d7a329aaf627462547b39779c2d`)
- 被検対象 = a2 の ⒝①: `scripts/inbox_watcher.sh`
  ★★被検対象は当職の観測中 ★動いて居る★ (a2 が現に施工中)★★ ∴ ★断面を三つとも記す★:

  | 刻 | 行数 | sha256 (頭16字) | 当職が其の断面で為した事 | ⒞ 10形 |
  |---|---|---|---|---|
  | 〜20:57 | 1831 | `25f8f01de32463a2` | 設計・harness 作成・★変異検査 (M1/M2)★ | ★10 ok★ |
  | 20:57:53〜 | 1955 | `0b4ed76ba827a58c` | 再走 + 変異検査 再走 + claude路 probe 再走 | ★10 ok★ |
  | 21:02:35 現在 | 1988 | `335f3e886bc97ffa` | 再走 (run 直前・直後の sha 一致を確認済) | ★10 ok★ |

  - ★三断面すべてで 10/10★ ∴ 本述語は a2 の施工中の改稿に ★耐えて居る★。
  - ★当職は本体を一字も触れて居らぬ★ ―― 各 run の ★直前・直後★ で sha を採り一致を確認 (最新断面で実測)。
    sha の変化は ★悉く a2 の施工に由る★ (当職の Edit/Write は本 file に一度も及んで居らぬ)。
  - ★受入判定は a2 の完工宣言後の断面で取り直す事★ (今の数は「其の断面の数」に御座る)。
- 契約 C-1〜C-4 の出所: `docs/incident_logs/2026-08-07_worksite1_ab_codex_residue_a2.md` §5 (320行 / `3f1114b6c22bc870913cdb956934ee837aa0e0860f5695377f85cfae88e75972`)
  ★a2 の申告 sha と当職の実測 sha は一致★

---

## 0. 結論 (先に)

1. ⒞ 3形 ―― ★悉く走らせ、悉く通り申した★ (10形 10 ok)。★但し「緑」だけでは何も申せぬ★ ゆえ §3 の ★変異検査★ を併せて掛け、★述語が本体に噛んで居る事★ を示した。
2. ⒟ 罠台帳 ―― 既存不在を実測の上 ★新設★: `docs/03-workflows/watcher-trap-ledger.md`。
3. claude 路に ★同じ罠が生きて居る★ (§4)。★但し之は当職の発見に非ず★ ―― a2 が己の票 (20:36) に先に明記して居り、当職の寄与は ★実害の大きさ (三重配送・C-u 6回・log の偽「失敗」) の実測★ のみに御座る。★根治は a2 の領分ゆえ当職は直さず上申★。
4. ⒠blocker 配下の形 (㊀㊁㊂) は ★一つも走らせて居らぬ★・mock で代走もして居らぬ。

---

## 1. 契約 C-1〜C-4 の照合 (満たされた ∴ `contract_mismatch` は起きて居らぬ)

★在処は行番号で書かぬ★ (台帳 W-04 ―― 本 file は施工中で行が動く)。★再測式を添える★:

| 契約 | 当職の実測 (最新断面 `335f3e88…` / 21:02) | 再測式 |
|---|---|---|
| C-1 判定が単一 production 関数に閉じる | ★実在・但し下記の注★ | `declare -F codex_residue_cleanup` (`T-RESID-000` が毎走で検める) |
| C-2 prefix は第1引数 | `local prefix="$1"` 有 | `sed -n '/^codex_residue_cleanup() {/,/^}/p' … \| grep 'local prefix'` |
| C-3 掃除は `send-keys … C-u` で観測可 + 大域 `CODEX_RESIDUE_STATE` | `unknown`/`empty_prefix`/`no_composer`/`composer_mismatch`/`not_landed`/`cleaned` の ★6値★ を実測 (契約書は5値と記す ―― `unknown` は初期値ゆえ実質5) | 同上 `\| grep -o 'CODEX_RESIDUE_STATE="[a-z_]*"' \| sort -u` |
| C-4 正規化 ⑴〜⑸ + ★完全一致★ + composer 行 ただ一行 | 有 (`nbsp→空白` / 前後空白除去 / marker 除去 / ★最下段★ marker 行を `tail -1` で選ぶ) | `sed -n '/^composer_line_normalized() {/,/^}/p' …` |

★C-1 への注 (施工中の変化・当職の観測)★: a2 は当初 `codex_residue_cleanup()` の中に
capture と正規化を抱えて居たが、現断面では ★`composer_line_normalized()` へ括り出し★、
`codex_residue_cleanup()` は其の結果 (`COMPOSER_CONTENT` 等) を受け取る形に改まって居る。
新たに ★`codex_presend_gate()` (送信 ★前★ の門)★ も設けられ、`send_keys_verified()` の codex 路は
★門が dirty を返せば注入ごと見送る★ 形に変わった (= 根治の範囲が ⒝① より ★広がって居る★)。

∴ ★契約 C-1 の字面「判定が単一関数に閉じる」は 厳密には最早成り立たぬ★ (判定の材料は別関数が作る)。
但し ―― ★入口は `codex_residue_cleanup()` のまま★ ゆえ当職の 10形は ★一形も書き換えず通って居る★。
★之は契約違反として上げるのではなく「契約の字面を実態へ合わせ直すべし」として a2/軍師へ差し出す★
(判定の可検証性は落ちて居らぬ ―― 寧ろ門が増えた分 ★狭く★ なって居る)。

★㈡ⓔ (末尾空白) の述語未定は解消★ ―― a2 の回答 (期待値 = `cleaned`) を受け、`T-RESID-007` に固定。
理由も受理: `capture-pane -p` は行末空白を必ず落とす ∴ ★本経路では区別し得ぬ★ (掃除を緩めたのではなく、測れぬ物を測れぬと認めた形)。

---

## 2. ⒞ 実行結果 ―― ★形で書く (件数を単独の緑数として書かぬ)★

成果物: `tests/unit/test_codex_residue_negative.bats` (★新設★)

| 形 | 与えた composer | 期待 | `CODEX_RESIDUE_STATE` | `C-u` | 結果 |
|---|---|---|---|---|---|
| `T-RESID-000` | ― (契約 C-1 の検め) | 関数が在る | ― | ― | ok |
| `T-RESID-001` ㈠ | `› 副院長殿へ 本日の残件を纏めて` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-002` ㈠補助 | `› inbox2 と書いた後に続けて人が打った` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-003` ㈡ⓐ | `› xinbox2` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-004` ㈡ⓑ | `› inbox2x` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-005` ㈡ⓒ | `› inbox` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-006` ㈡ⓓ | `› inbox3` | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-007` ㈡ⓔ | `› inbox2␣` | ★掃除が走る★ | `cleaned` | 有 | ok |
| `T-RESID-008` ㈢ | `› ` (空・会話面に着弾済) | 掃除せぬ | `composer_mismatch` | 無 | ok |
| `T-RESID-009` ★陽性対照★ | `› inbox2` (着弾済) | ★掃除が走る★ | `cleaned` | 有 | ok |

★㈠㈡ⓐ〜ⓓ㈢ の fixture は悉く「会話面に `inbox2` が着弾済」を含む★ ―― 掃除を止めた理由が
★完全一致の条 ただ一つ★ である事を確かめる為 (着弾の有無が交絡せぬ様に)。

★`T-RESID-009` (陽性対照) を置いた理由★: 之が無ければ、上の「`C-u` 無し」は
★通ったのか・そもそも走って居らぬのか★ を判じ得ぬ (罠 W-03)。

### 既存試験への影響 ―― 回帰 無し

`bats tests/unit/test_codex_residue_negative.bats tests/unit/test_send_wakeup.bats` → ★64 形中 63 ok / 1 not ok★。
唯一の `not ok` = `T-CRESET-003` で、★a2 が改修前から落ちて居る事を二証で示し済★ (a2 票 §4)。当職の新設 file は ★一形も落として居らぬ★。

---

## 3. ★変異検査 (mutation check)★ ―― 述語が本体に噛んで居る事の証

「10 ok」は ★述語が本体に噛んで居る事を示さぬ★ (罠 W-02)。∴ 本体の ★複製★ へ既知の欠陥を入れて掛けた。
★production file は一字も触れて居らぬ★ (複製は repo 外 scratchpad・実行前後で実 script の sha256 不変を確認済)。

| 変異 | 入れた欠陥 | ★落ちた形★ (行で列挙・件数で書かず) |
|---|---|---|
| M1 | `capture` ★全体★ を grep (= 根治前の素朴実装) | `T-RESID-001` `T-RESID-002` `T-RESID-003` `T-RESID-004` `T-RESID-005` `T-RESID-006` `T-RESID-008` |
| M2 | composer 行は見るが ★部分一致★ で掃除 | `T-RESID-002` `T-RESID-003` `T-RESID-004` |

- M1 で ㈠ が落ちる = ★本物 draft が破壊される事を本 file は捕らえる★。
- M1 で ㈢ が落ちる = ★着弾済 nudge を会話面から拾う誤りを捕らえる★ (設計票が「肝」と宣した形の通り)。
- M2 で ⓒ`inbox` ⓓ`inbox3` が ★落ちぬ★ のは正しい (いずれも `inbox2` を部分列として含まぬ) ―― ★M2 を捕らえるのは ⓐⓑ と ㈠補助 の三形★。
- 陽性対照 `T-RESID-009` と ㈡ⓔ は ★両変異で通ったまま★ = 期待通り (掃除が走るべき形ゆえ)。

★∴ 「緑」は空振りに非ず★。

---

## 4. ★claude 路に同じ罠が生きて居る ―― 実害の大きさの実測 (上申・当職は直さぬ)★

★★先に訂正★★ ―― 本節を当初 ★「新規の瑕」★ と題したのは ★当職の誤り★ に御座る。
本罠が claude 路に残る事は ★a2 が先に己の票へ明記して居た★:
`docs/incident_logs/2026-08-07_worksite1_ab_codex_residue_a2.md`「直した中身」2 が旧実装の形を掲げ、
★「claude 路は一字も変えて居らぬ (稼働中9本を壊さぬ為)」★ と書いて居る (同票 mtime ★20:36:29★)。
当職の probe は ★20:55★ ∴ ★後★。現断面では production の comment にも
★「本改修で直っておらぬ既知の穴」★ と自認が入って居る。

∴ ★当職の寄与は「見付けた事」に非ず★。★下の「どれ程の実害か」の実測のみ★ に御座る
(a2 は ★構造★ を述べ、★大きさ★ は誰も測って居らなんだ)。

構造: 根治は `if [[ "$effective_cli_for_nudge" == "codex" ]]` の ★内側★ に閉じ、
`else` 側 = ★claude 路★ は `capture-pane -p | tail -5 | grep -qF "$nudge"` の ★まま★。
着弾した nudge は `tail -5` にも入る ∴ ★罠 W-01 そのもの★。
(在処を行番号で書かぬ理由 = 台帳 W-04。再測式 = `grep -n 'tail -5' scripts/inbox_watcher.sh`)

★実測★ (production `send_wakeup()` を harness で直に呼び、★着弾成功★ の pane を与えた
・20:55 断面 `25f8f01d…` / 21:02 断面 `335f3e88…` ★両断面で同結果★):

| 与えた状態 | 出た物 |
|---|---|
| 会話面に `inbox2` 着弾済・composer 空・`CLI_TYPE=claude` | `nudge` 送出 ★3回★ |
| 〃 | `C-u` 送出 ★6回★ |
| 〃 | `WARNING: send-keys failed after 2 retries` = ★着弾して居るのに「失敗」と log に残る★ |

- ★実害★: ⑴ 同じ便が三重に届く ⑵ composer が空でも `C-u` が 6 度走る ∴ ★其の隙に人が打ち始めれば消える★ ⑶ log が嘘を吐く (成功を失敗と記す)。
- ★測定条件 (一般化せぬ為に明記)★: mock の `capture-pane` は ★同じ内容を返し続ける★。現物では `C-u` 後に composer は消えるが ★会話面の `inbox2` は残る★ ∴ 其れが `tail -5` に留まる限り同じ空回りが起きる。★agent が即座に応答して当該行を押し出せば止む★ = ★応答が遅い相手ほど強く出る罠★。
- ★推論と観測を分ける★: 当職自身が 20:27 と 20:45 に `/clear` を二度受けて居るが、★之と本罠の因果は測って居らぬ★ ∴ 結び付けて語らぬ (escalation は別関数)。
- ★本 probe は診断枠★ ―― `tests/` へは入れて居らぬ。現状を test に焼けば ★欠陥を仕様に格上げする★ 為。
- ★根治は a2 の領分★ (本体改変は当職の境界外) ∴ ★上申に留める★。

---

## 5. ⒠blocker 配下 ―― ★実行せぬと宣した形 (代走・偽装せず)★

| 形 | 要る物 | 状態 |
|---|---|---|
| ㊀ 実 codex pane での端対端 | live watcher + hermes 実 pane への送出 | ★blocked★ (境界: hermes pane は capture のみ) |
| ㊁ 実 composer に人の draft を置いた破壊有無 | 実 pane への打鍵 | ★blocked★ (同上) |
| ㊂ watcher 再起動を挟んだ残骸の持ち越し | watcher 起動/停止 | ★blocked★ (境界: 起動・停止・再起動 0) |
| ㊃ 末尾スペースの ★源★ の切り分け | 実 pane 観測 | ★a2 の領分★ ―― 当職は測らず (二重実装回避) |

★㊀〜㊂ を mock で代走して「端対端 PASS」と書く事は為して居らぬ★。

---

## 6. ⒟ 罠台帳 ―― ★新設★ (anti-dup 実測を経て)

- 成果物: `docs/03-workflows/watcher-trap-ledger.md` (★新設★)
- ★先に既存を捜索★ (2026-08-07 20:5x・plain `grep`/`find` を使用。`git grep` は gitignore 対象を無警告で飛ばす為 ★用いず★):
  - file 名筋 (罠/trap/pitfall/lesson/ledger/台帳): 該当は ★日付付きの一件物★ (`docs/incident_logs/*_ledger_*.md`) と `post-incident-lessons.md` (=手順書) のみ ∴ ★継続登録の器は不在★
  - 本文筋 (罠台帳/trap ledger/落とし穴台帳): ★0 hit★
- 近縁 `docs/01-architecture/watcher-design.md` は ★原則と checklist★ であり罠の形を載せぬ。かつ ★改訂責務は理事長殿の専権事項★ と同 file 3行目に明記 ∴ ★当職は追記せず★、checklist へ足すべき二項を ★上申★ として台帳の追補欄に置いた。
- 登録した罠: `W-01` (着弾済を残骸と誤読して掃除暴発) / `W-01b` (無条件 `C-u` ―― ★所属関数で括り★ 中身条件付きが幾つかを示す) / `W-01c` (claude 路に同罠が現存・§4・★出所は a2★) / `W-02` (述語が本体に噛んで居らぬ) / `W-03` (陽性対照無き緑) / ★`W-04` (行番号で書いた台帳は台帳自身が腐る ―― ★当職が実地で踏んだ罠★)★。
- 各項に ⑴形 ⑵実害 ⑶検知法 ⑷根治法 ⑸現況 を必置とし、★検知法の欄に「機械が落ちる形」が書けぬ罠は登録しても再発する★ を書式の条として焼いた。

---

## 7. 境界順守の申告

- `scripts/inbox_watcher.sh` ―― ★一字も触れて居らぬ★。本 file は当職の観測中 a2 の施工で ★三度変わった★ (`25f8f01d…`→`0b4ed76b…`→`335f3e88…`) が、★各 run の直前・直後で sha を採り一致を確認★ して居る ∴ ★変化は悉く a2 の施工に由り、当職の Edit/Write は一度も及んで居らぬ★
- `scripts/inbox_write.sh` ―― ★一字も触れて居らぬ★
- watcher の起動 / 停止 / 再起動 ―― ★0★
- `commit` ―― ★0★ / `push` ―― ★0★
- hermes pane ―― ★capture も送信も 0★ (本工区では触れて居らぬ)
- `0.7` pane ―― ★不触★
- 変異検査の複製は ★repo 外 (scratchpad)★ に置き、`tests/` にも `scripts/` にも残して居らぬ
- 新設 file は 2 つ (`tests/unit/test_codex_residue_negative.bats` / `docs/03-workflows/watcher-trap-ledger.md`)。両者とも `git status --porcelain` で `??` として ★見えて居る事★ を確認済 (whitelist 方式の `.gitignore` に黙って落とされて居らぬ)

---

## 8. 自己申告

- 設計票 (20:19) の在中欄 `multiagent-second:0.7` は ★現在地と食い違う★ (現 `0.4`)。★己の断面が古びた★ ものに御座る ∴ 本票冒頭に明記した。★送信済の票は上書きせぬ★ 条ゆえ設計票そのものは改めず、本票を以て superseded とする。
- 設計票 §1.1 の C-u site 表は ★3 site + test 1★ と書いたが、再測で ★9★ に御座った。★件数が増えたのは実態が変わったのではなく 当職の初回の捜索が浅かった★ ゆえ ―― 台帳 `W-01b` に列挙し直した。
- ★其の「9」も既に古い★: 同 site 数は 20:5x=★9★ → 21:00=★10★ → 21:02=★13★ と ★8分で三たび★ 変わった (a2 が現に施工中)。∴ 台帳の表を ★行番号括り→所属関数括り + 再測式★ へ改め、★断面 sha を必ず添える★ 形に直した。
- ★本票 §4 を当初「新規の瑕」と題したのは誤り★。claude 路の穴は a2 が ★20:36 の票に先に明記★ して居り、当職の probe (20:55) は後に御座る。★己の寄与を過大に書いた★ ―― 訂正して §4 冒頭に出所を明記した。★結論 (claude 路は脆い) は変わらぬが、其れを支える「誰が見付けたか」が誤って居た★。
- 之等三件はいずれも ★当職が台帳 W-04 に登録した罠 (動く物を指す・母集団が動いて居るのに数だけ書く) を 当職自身が踏んだ★ 事に御座る。台帳へは ★己の失敗として★ 焼いた。

---

*足軽4号 2026-08-07 20:58 JST ―― ⒞ 実行済 / ⒟ 新設済 / §4 は上申 (当職は直さぬ)*
