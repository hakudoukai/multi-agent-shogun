# 家老second 断面保全 (2026-08-06 11:25) — context 100% 到達につき外部化

**起草** = 家老second　**測時** = 2026-08-06T11:25 (機械)　**HEAD** = 3f932aa
**目的** = compact 注入前の外部化。**本 file は保全であって完了に非ず。未監査。**
**測り** = 将軍second 実視 11:21:15 — karo-second **100% context used** / a2 100% / a6 100% / a3 95% / 軍師second 未測。

## 0. 当職が /compact を己で入力し得ぬ事 (境界)

- 将軍second は「己で /compact を入力されたし」と命じられ申した。
- **然れど当職の pane へ打鍵する手段は tmux send-keys のみに御座り、CLAUDE.md は「Agents NEVER call tmux send-keys directly」と定め申す。**
- ∴ **当職は己の pane に /compact を注入し得申さぬ。** 注入は実user殿か owner 経路に拠る。
- ∴ **本 file が唯一の備え**に御座る。飛んでも本 file から復せる形に書く。

## 1. 役と経路

- 当職 = **karo-second** (家老second・second_pc)。上長 = 将軍second → 委員長 (third_pc) → 理事長 (実user)。
- 配下 = ashigaru1-7 + gunshi-second。
- 委員長宛 uplink = `bash scripts/karo_second_send_iincho.sh --live --type status_update -- '<本文>'`
  - **argv のみ・stdin 経路なし** ∴ 本文に `'` `"` backtick `$` を**一文字も書くな**。
- 便 = `INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh <target> "" <type> karo-second <<'EOF' … EOF`
- **type の選び方 (将軍裁 11:19)** = 「消したいか否か」で選ぶな、**便の中身が何か**で選べ。
  新工区 = `task_assigned` (watcher が配送前に /clear を打つ・**要る事は悉くその便に**) ／ 既存工区への情報追加 = `report_received` ／
  **判じ難き = 既定を置かず分けよ**(二つ分を含んでおる印)。

## 2. 本日の commit (62件・最新 3f932aa)

| commit | 中身 |
|---|---|
| 2fe3c59 | a4 段取り157行 / a3 F2反証195行 / a5 census追補187行 |
| 6f266ef | a2 条索引220行 / a4 段取り追記203行 |
| 2a915b6 | a1 F1 4点oracle v2 230行 (旧161行 23d5af10 併存) |
| 3f932aa | a2 292行 / a4 258行 / a5 230行 (悉く PASS不変の追記版) |

## 3. 開いておる件 (owner 別)

| # | 件 | owner | 状 |
|---|---|---|---|
| ① | hakudokai-dev 書込 GO | **実user殿** | 錠は一つ。**当職の turn の user message として現れるまで走らせるな (当職を含め全員)** |
| ② | 足軽7号 pane dialog | **実user殿** | blocked 8時間超。既定 ❯1.=⒝=**誤の側**、正は **2.=⒜**。当隊は押さぬ |
| ③ | 正本の記述欠落 (task_assigned と /clear) | **委員長殿** | 代送済 id 73115675。求むるは実装変更に非ず**正本に一行** |
| ④ | dead-letter parse 不能の根治 | **委員長殿** | 上申済 id a0fa5fa9。shim/hakudokai/hakudokai_secondpc_receiver_poll.py 232-254。git 外 ∴ 当隊は触れず |
| ⑤ | P0 実走 | a6 | 段0 完了 (三者独立一致)・段2 へ。**/tmp 内のみ・newbuild 読取のみ** |

## 4. 配下の現状 (11:25)

- **a1** = F1v2 230行 PASS 済 (commit 2a915b6)。待ち。
- **a2** = 手掛かりを変えた探索 (己が受けた便のみ・当職の19件を見ずに)。task_assigned 済。
- **a3** = grep shim の除外条件の絞り込み。task_assigned 済。**86-95%**。
- **a4** = 段取り書 258行 PASS。待ち。
- **a5** = census 230行 PASS。次は量の断定条件 ㈡標本30件 (owner=a5)・㈢独立第二検証者 (**owner=当職・未着手**)。
- **a6** = P0 実走 段2。
- **a7** = blocked (実user殿)。
- **gunshi-second** = 監査稼働中。

## 5. 本日立てた条のうち、当職が繰り返し破った物

1. **札は毎回引き直せ・書き写すな** — 「清浄」を10:34の測りのまま写し、誤報に至った (訂正便 440929ad → 撤回便 7c928d2a)。
2. **裁の前提は執行の刹那に引き直せ** — a1 compact 令は 10:56 の 82% に拠り、10:59:29 の /clear で対象が消えておった。
3. **機構の振舞いを見つけたら、補う前に設計意図と既存の安全弁を読め** — /clear 機構を「欠陥」と判じ、守る側に回って **type を誤り、迂回に及んだ** (自己申告済・task_assigned で再送済)。
4. **訂正便には元の便と同じ厳しさの検めを掛けよ** — 訂正の誤り (未知の手が在る) の方が元の誤り (清浄の一語) より重かった。
5. **己の記憶から出た物は、出所が付くまで条と呼ばぬ** — 口述19件のうち8件は出所が辿れず (a2 実測)。

## 6. 未測 (断じており申さぬ)

- a5/a6/a7 の CONTEXT-RESET 0回の因 (安全弁 / defer / cli 差 / log 所在の差)。
- 75回の「Sending」のうち何回が現に着弾したか (**log からは出ぬ**)。
- a3 の grep shim 除外は**どの条件で起きるか** (将軍の一例では 53対53 で再現せず)。
- 「四工区連続の過検出」は**母集団が実は一つ**やも知れぬ (a5 の四母集団測りで三つが 55-60% に近接)。
- 当職自身の context 実数値 (**pane に % が出ぬ** ∴ 将軍second の実視のみが出所)。

## 7. 境界 (解けておらぬ禁)

- hakudokai-dev の repo/branch へ書くな・commit するな (委員長 10:43:37)。
- newbuild へ書込零・稼働 pid へ手出し零。**/tmp の隔離は自由**。
- 姉妹 clone `/home/hakudokai/multi-agent-shogun` は**読取すら不可**。
- `audit_codex.sh` を走らせるな。guard 本体・`.claude/settings.json`・`.gitignore` を裁可なく編むな。`git add -f` 禁。
- push・PR・timer 停止・稼働中 process の停止/削除・不可逆削除・secret・患者実データ = **理事長へ上げる (軍師でも不可)**。
- git 履歴の書換 (amend/rebase/reset) 禁。**GO_RECORD を何人たりとも作るな** (agent 自己配置 = D-lane 違反)。
- 破れた後は**戻すより先に残して報せよ**。
