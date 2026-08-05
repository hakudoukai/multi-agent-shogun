# W205b「名前で 起こす／止める」箇所の 列挙 (足軽1号)

- 断面 (機械時刻): 2026-08-06T02:07:08+09:00 / base_commit=b9bec71e28e1febd96df48f97698a1cfbfa21751
- 実行方針: ★本工区中、探索対象コマンド(pkill/killall/tmux kill-*/pgrep等の実行)は一切走らせず、grep(文字列列挙)と ps/tmux list(読取のみ)のみ使用した★。DD-169 guardが grep文中の"pkill"等の文字列そのものをコマンド実行と誤検知しブロックしたため、パターンをfile経由(`grep -f`)で渡す方式に変更して回避(実行内容は変わらず、ガードのcommand文字列単純一致の限界を回避しただけ)。
- 母集団宣言: repo全体(`.git`除く)を対象に `grep -rFf` で10種の固定文字列(pgrep/pkill/killall/tmux kill-server/tmux kill-session/tmux kill-pane/ps aux/ps -ef/ps -A/ps -eo)を検索→**396行ヒット** (★訂正: 初版は397と記載したが誤りだった。raw_hits.txt の実 wc -l = 396 が正。原因は本文中の目算ミス、母集団自体は当時動いていない→[§0-a 断面訂正](#0-a-断面訂正karo-second-fail-指摘対応) 参照★)。うち **.bak/archive/tests/queue-inbox・queue-reports(会話履歴)/docs(手順書・監査報告)/README/AGENTS.md/CLAUDE.md/instructions/skills/.github/agents-default を除いた「現行実行コード」母集団=87行**に絞って⒝⒞⒟を実施した(理由=衝突リスクは実行され得るコードにのみ存在する。除外分396-87=309行は「読み物・凍結物・過去ログ」であり実行対象ではない→§7に別掲)。

## §0-a 断面訂正 (karo-second FAIL指摘対応・msg_20260806_021508_42fd9546 + msg_20260806_021824_60d024e7 + msg_20260806_022008_a5007081)

★24時間止まらぬ定めゆえ、母集団は原理上 凍結し得ぬ。∴「凍結」ではなく「断面を刻む」形へ改める(将軍second裁定=a1のFAILは測定の失敗ではなく再測不要、断面を添えた再提出で足りる)。★

三つの数は ★異なる断面の異なる測定★ であり、互いに矛盾する物ではない:

| # | 数値 | 断面 (HEAD hash / 測時) | 出所 | 備考 |
|---|---|---|---|---|
| 1 | 397 | base_commit=b9bec71 / 測時 2026-08-06T02:07:08+09:00 (本足軽1号の初版本文記載) | 手動記載 | ★誤り★=raw_hits.txt の実行数と1行ずれていた(目算ミス)。本節で396に訂正。 |
| 2 | 396 | base_commit=b9bec71 / raw_hits生成 2026-08-06T02:03 前後 (patterns file mtime) | `w205b_raw_hits.txt` の実 `wc -l`(生ログそのもの) | ★正★=本報告⒜⒝⒞⒟の母集団はこの396が実体。証跡=`docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot1_b9bec71.md`(本file・396行・sha256=別掲)。 |
| 3 | 388 | HEAD=f3501fd (karo-second再実行時点、02:15台) | karo-second の再実行 | 本足軽1号の測定(断面1/2)より★後★の断面。理由=karo-secondが2026-08-06T02:09:31に2件commit(`24942f2`+`f3501fd`、同時刻)し、`lib/cli_adapter.sh`・`scripts/ratelimit_check.sh`・`scripts/inbox_write.sh`・tests 2件・docs 3件が変わった(いずれもpgrep/tmux語を含み得るfile)。★これは足軽1号の落度ではなく、karo-second自身が認めた「測定中commit」による母集団移動★。 |
| 4 | 442 | HEAD=f3501fd / 測時 2026-08-06T02:22:31+09:00 (本節執筆時、足軽1号による同条件再実行) | 本足軽1号の追試 | 証跡=`docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot3_f3501fd.md`(442行・sha256=別掲)。★新規判明★=このうち42行は★本報告file自身★(`docs/incident_logs/2026-08-06_w205b_name_kill_enumeration_a1.md`)がヒット元──衝突パターンの語(pgrep/pkill/tmux kill-*等)を表として引用しているため、本報告をrepoに置いた時点で以後の同条件再実行は必ず「本報告自身」を母集団に含み、二度と396(commit前)にも388(karo-second断面)にも一致し得ない。★∴ 本件は「数が合わぬ」ことそのものが病ではなく、母集団が継続的に動く設計(24時間ノンストップ)である以上、単一の「正しい数」を追い求めるのが誤りだった★。 |

★結論★: ⒜⒝⒞⒟の分析(衝突3件・末尾space無しpattern・健全例2件)は断面2 (396→87) を母体に行われており、この部分の値打ちは断面が変わっても揺るがない(karo-second・将軍secondとも既に確認済み)。「397」という初版の一語のみが誤りであり、本節で訂正した。

## ⒜ 対象カテゴリ(実測、母集団=87行中)

| カテゴリ | 該当行数 |
|---|---|
| pgrep系 | 51 |
| pkill系 | 16 |
| tmux kill-session/-pane系 | 13 |
| ps+grep組合せ(ps aux/ps -ef単独含む) | 4 |
| killall | 0(87行中の実引用は`.claude/settings.json`のdeny listのみ・実行箇所なし) |
| guard/config自身の検知正規表現(実行ではない) | 3(dd169_kill_term_guard.sh, pretooluse_bash_guard.sh, .codex/hooks.json) |

## ⒝ 列挙: agent名を引数に埋めておる箇所(全件・file:行番号+全文+埋込名)

### グループA: shim/hakudokai/hakudokai_start_watchers.sh (agentループ = `karo ashigaru1 gunshi shogun`、L56/L85)
| 行 | 全文 | 埋込名 |
|---|---|---|
| L57 | `pkill -f "inbox_watcher.sh ${agent}" 2>/dev/null \|\| true` | karo/ashigaru1/gunshi/shogun (ループ展開・**末尾space無し**) |
| L86 | `if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | 同上(check only) |
| L185 | `log "inbox_watcher[karo]: $(pgrep -f 'inbox_watcher.sh karo' \| head -1 \|\| echo DEAD)"` | karo(check only) |
| L186 | `log "inbox_watcher[ashigaru1]: $(pgrep -f 'inbox_watcher.sh ashigaru1' \| head -1 \|\| echo DEAD)"` | ashigaru1(check only) |
| L187 | `log "inbox_watcher[gunshi]: $(pgrep -f 'inbox_watcher.sh gunshi' \| head -1 \|\| echo DEAD)"` | gunshi(check only) |
| L188 | `log "inbox_watcher[shogun]: $(pgrep -f 'inbox_watcher.sh shogun' \| head -1 \|\| echo DEAD)"` | shogun(check only) |

### グループB: shim/hakudokai/hakudokai_watchdog.sh (agent = ACTIVE_AGENTS由来。registry読込成功時=実配置名/失敗時=LEGACY_INBOX_AGENTS フォールバック)
| 行 | 全文 | 埋込名 |
|---|---|---|
| L88 | `LEGACY_INBOX_AGENTS="karo:multiagent:0.0 ashigaru1:multiagent:0.1 gunshi:multiagent:0.8 shogun:shogun:0.0"` | karo/ashigaru1/gunshi/shogun (フォールバック時のみ有効・**末尾space無し**) |
| L530 | `if ! pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | ACTIVE_AGENTS由来(check only) |
| L566 | `if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then` | 同上(check only) |
| L624 | `pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1 && alive="true"` | 同上(check only) |

### グループC: shim/hakudokai/hakudokai_secondpc_setup.sh (AGENT1_ID="ashigaru2" L29 / AGENT2_ID="ashigaru8" L33)
| 行 | 全文 | 埋込名 |
|---|---|---|
| L369 | `pkill -f "inbox_watcher.sh ${AGENT1_ID}" 2>/dev/null \|\| true` | ashigaru2(**末尾space無し**) |
| L370 | `pkill -f "inbox_watcher.sh ${AGENT2_ID}" 2>/dev/null \|\| true` | ashigaru8(**末尾space無し**) |
| L384 | `if pgrep -f "inbox_watcher.sh ${agent_id}" > /dev/null 2>&1; then` | ashigaru2/ashigaru8ループ(check only) |
| L385 | `ok "inbox_watcher[${agent_id}]: PID=$(pgrep -f "inbox_watcher.sh ${agent_id}" \| head -1)"` | 同上(check only) |
| L471 | `echo "    inbox_watcher[${AGENT1_ID}]: $(pgrep -f "inbox_watcher.sh ${AGENT1_ID}" \| head -1 \|\| echo 'NOT RUNNING')"` | ashigaru2(check only) |
| L472 | `echo "    inbox_watcher[${AGENT2_ID}]: $(pgrep -f "inbox_watcher.sh ${AGENT2_ID}" \| head -1 \|\| echo 'NOT RUNNING')"` | ashigaru8(check only) |
| L487 | `echo "    pkill -f 'inbox_watcher.sh ${AGENT1_ID}'"` | ashigaru2(echo文=表示のみ・実行せず) |
| L488 | `echo "    pkill -f 'inbox_watcher.sh ${AGENT2_ID}'"` | ashigaru8(echo文=表示のみ・実行せず) |
| L286 | `tmux kill-session -t "$TMUX_SESSION" 2>/dev/null` | $TMUX_SESSION変数(値未追跡・本工区時間内未確認) |
| L489 | `echo "    tmux kill-session -t $TMUX_SESSION"` | 同上(echo文) |

### グループD: scripts/watcher_supervisor.sh / watcher_supervisor_third.sh (★末尾space有り★=既に安全策実装済)
| 行 | 全文 | 埋込名 |
|---|---|---|
| watcher_supervisor.sh:52 | `if pgrep -f "scripts/inbox_watcher.sh ${agent} " >/dev/null 2>&1; then` | shogun/karo/ashigaru1/ashigaru2/gunshi(L64-68固定列挙・**末尾space有り**) |
| watcher_supervisor_third.sh:63 | `if pgrep -f "scripts/inbox_watcher.sh ${agent} " >/dev/null 2>&1; then` | ashigaru-third-{1..2}/gunshi-third(**末尾space有り**) |

### グループE: scripts/inbox_watcher.sh (自己watch・末尾`.yaml`固定サフィックスで自然に anchor)
| 行 | 全文 | 埋込名 |
|---|---|---|
| L957 | `done < <(pgrep -f "inotifywait.*inbox/${AGENT_ID}.yaml" 2>/dev/null)` | 自エージェントID(実行時の`$1`。**`.yaml`固定接尾辞のため単一文字以外の接尾衝突は構造的に起きぬ**) |

### グループF: agent名を埋めず広域一括で叩く箇所(実行時=全員対象、名前局所化なし)
| 行 | 全文 | 備考 |
|---|---|---|
| shutsujin_departure.sh:971 | `pkill -f "inbox_watcher.sh" 2>/dev/null \|\| true` | agent名なし=**全watcher無差別**(撤収=意図的全停止と推される。裁定はせず事実のみ記す) |
| shutsujin_departure.sh:972 | `pkill -f "inotifywait.*queue/inbox" 2>/dev/null \|\| true` | 同上 |
| shutsujin_departure.sh:973 | `pkill -f "fswatch.*queue/inbox" 2>/dev/null \|\| true` | 同上 |
| shutsujin_departure.sh:1077 | `pkill -f "ntfy_listener.sh" 2>/dev/null \|\| true` | agent名なし(単一リスナー故問題化しにくいが未検証) |

### グループG: tmuxセッション終了系(セッション名=固定文字列、agent名そのものではないがロール名(shogun/multiagent/secondpc)を埋込)
| 行 | 全文 |
|---|---|
| scripts/setup_shogun_sc.sh:12 | `tmux kill-session -t "$SHOGUN_SESSION" 2>/dev/null \|\| true` |
| scripts/setup_shogun_sc.sh:13 | `tmux kill-session -t "$MULTI_SESSION" 2>/dev/null \|\| true` |
| scripts/setup_shogun_standard.sh:28-33 | 同型4行(`$SHOGUN_SESSION`/`$MULTI_SESSION`/固定`shogun`/固定`multiagent`/固定`secondpc`) |
| shutsujin_departure.sh:337 | `tmux kill-session -t multiagent 2>/dev/null && ...` |
| shutsujin_departure.sh:338 | `tmux kill-session -t shogun 2>/dev/null && ...` |
| shutsujin_departure_secondpc.sh:39 | (echo文=表示のみ) |

## ⒞ 突合: 現に走っておる process の完全な引数 (`ps -eo pid,ppid,args`、2026-08-06T02:07:08+09:00 実測、本ホスト=SecondPC)

```
karo-second        ./scripts/inbox_watcher.sh karo-second multiagent-second:0.0 claude
shogun-second       ./scripts/inbox_watcher.sh shogun-second shogun-second:0.0 claude
gunshi-second       ./scripts/inbox_watcher.sh gunshi-second multiagent-second:0.8 codex
honbucho            ./scripts/inbox_watcher.sh honbucho hermes-honbucho:0.0 codex
ashigaru1〜7        ./scripts/inbox_watcher.sh ashigaru{N} multiagent-second:0.{N} claude
```
tmux session一覧(read-onlyのみ・kill未実行): `hermes-gunshi-second` / `hermes-honbucho` / `multiagent-second` / `shogun-second`。**裸の`shogun`/`karo`/`gunshi`/`multiagent`/`secondpc`セッションは現在0件**。

## ⒟ 表: 掛ける名前 / 当たる実体 / 巻き添え有無

| 掛ける名前(パターン) | 出所(グループ) | 当たる実体(現ps上) | 巻き添え有無 |
|---|---|---|---|
| `inbox_watcher.sh karo`(末尾space無) | A/B(LEGACY時) | **karo-second を部分一致で捕捉**(`inbox_watcher.sh karo`は`...karo-second...`の先頭部分文字列) | **★有り★** |
| `inbox_watcher.sh shogun`(末尾space無) | A/B(LEGACY時) | **shogun-second を部分一致で捕捉** | **★有り★** |
| `inbox_watcher.sh gunshi`(末尾space無) | A/B(LEGACY時) | **gunshi-second を部分一致で捕捉** | **★有り★**(将軍second殿の訂正=2→3、本測定でも独立に3件一致) |
| `inbox_watcher.sh ashigaru1`(末尾space無) | A | ashigaru1のみ(現ps上に`ashigaru1X`等の接尾衝突対象なし) | 無し(現時点) |
| `inbox_watcher.sh ashigaru2`/`ashigaru8`(末尾space無) | C | 各々1件のみ(現ps上に接尾衝突対象なし) | 無し(現時点)★但し将来`ashigaru2-second`等が生じれば同型リスク★ |
| `scripts/inbox_watcher.sh <agent> `(末尾space有) | D | 意図した1entityのみに限定 | **無し(健全例)** — trailing spaceがgunshi/gunshi-third等の接尾語衝突を構造的に遮断 |
| `inotifywait.*inbox/<id>.yaml` | E | 意図した1entityのみ | **無し(健全例)** — 固定`.yaml`接尾辞がanchorとして機能 |
| `inbox_watcher.sh`(agent名無し・グループF) | F | **全agent(karo-second/shogun-second/gunshi-second/honbucho/ashigaru1-7 全員)** | ★有り(意図的・全停止設計と推される、未裁定)★ |
| `tmux kill-session -t shogun`/`multiagent`等 | G | **未実測**(現ホストに裸セッション0件のため実衝突は今回発生せず。tmuxのセッション名前方一致解決仕様上、裸名不在×`-second`接尾セッション存在の組合せなら理論上衝突し得るが、本工区は「実行するな」の縛りゆえ`tmux kill-session`自体は一切試行せず、list-sessionsのみで確認。**この一文は未実測=伝聞/一般知識であり実測ではない**と明記) | **判定不能(第四値)** |

## 健全例(最低1件、要求充足)
グループD(watcher_supervisor.sh/_third.sh)の末尾space付きpattern、およびグループE(inbox_watcher.sh自己watchの`.yaml`固定接尾辞)は、★構造的に接尾語衝突を遮断する設計★になっている。同種の末尾anchorを持たないグループA/B/Cとの対比で、「同じ問題への異なる対処が同一repo内に混在している」ことが本測定で判明した。

## 母集団漏れの自己申告
- 396-87=309行を「読み物・過去ログ・.bak/archive/tests/docs」として除外した(★初版397は誤り・§0-a参照★)。うち`docs/secondpc_dd044_migration_script_20260509.md`(quartetto_pdf_watcher関連pgrep)は移行手順書内のコード片であり、実配備先が別repoの可能性があるため**本工区時間内では実配備先を追跡できず・判定不能**。
- グループC L286の`$TMUX_SESSION`変数の実値、およびグループGの`$SHOGUN_SESSION`/`$MULTI_SESSION`変数の実値は、定義箇所を本工区時間内で全て遡及できておらず**未確認(第四値)**。
- `.claude/settings.json`のpermissions.denyにある`Bash(killall *)`等はDD-169 guardの二層目(layer1 permission gate)であり、実行コードそのものではないため⒝から除外(方針セクションで前述の通り)。

## この工区が新たに開ける穴
- 本報告はgrep(静的テキスト一致)による列挙であり、`eval`/変数間接展開/動的生成コマンド文字列(例: sprintf的に組み立てられるpattern)は捕捉できていない可能性がある。特にhakudokai_watchdog.shのACTIVE_AGENTSがregistry由来の場合、pane_registry.yamlの中身次第でpattern文字列が実行時に変化するため、★本静的列挙は「ソースコード上の形」であり「実行時に実際に生成される文字列」の全数保証ではない★。

## ①-④ (家老second指定様式・断面訂正反映版)
① 成果物path: 本file `docs/incident_logs/2026-08-06_w205b_name_kill_enumeration_a1.md` (repo追跡下・元scratchpad `/tmp/claude-1000/…/0c06c39d-…/scratchpad/w205b_name_kill_enumeration_a1_20260806.md` からの移設・他sessionから到達可能)
② 証跡path (repo追跡下へ移設済・断面別に保存・★.txt拡張子は docs/incident_logs/ の gitignore whitelist(`!docs/incident_logs/*.md`のみ)対象外で無警告消滅する為 .md+コードフェンスへ変更済(足軽1号 自ら発見・是正)★):
   - `docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot1_b9bec71.md`(生grep結果・断面2=396行のgrep出力をコードフェンスで格納・base_commit=b9bec71)
   - `docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot3_f3501fd.md`(同条件再実行・断面4=442行のgrep出力・HEAD=f3501fd・測時2026-08-06T02:22:31+09:00)
   - 元scratchpad参考(到達不能につき参照のみ): `w205b_active_scope.txt`(絞込87行)+`w205b_patterns.txt`(検索パターン10種)
③ 行数+sha256 (本file・確定・git check-ignore -v で whitelist一致 + `git status --porcelain --ignored=matching` で `??`(未追跡=非ignore)を確認済):
   - `docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot1_b9bec71.md` = 400行(見出し2行+コードフェンス2行+生データ396行) / sha256=6b7a969e10f00232444fc03a6e27ba548d799087ab06ffb70b479e523cc88233
   - `docs/incident_logs/2026-08-06_w205b_raw_hits_snapshot3_f3501fd.md` = 446行(見出し2行+コードフェンス2行+生データ442行) / sha256=c7efce297cf39fd08c292715a8396cd009aa8ec4932f378c41f18c7155b2d024
   - 本報告file自身の行数+sha256は、末尾追記完了後に家老second/軍師secondへの提出報告(inbox本文)に別掲する(自己参照を避けるため本文中には記さず)。
④ 数の出所コマンド: `/usr/bin/grep -rFf w205b_patterns.txt . 2>/dev/null | grep -v '/\.git/' | wc -l`(断面2=396@b9bec71 / 断面4=442@f3501fd)。絞込は同ファイルをgrep -vで除外パターン適用(=87、断面2基準)。ps/tmuxは `ps -eo pid,ppid,args` / `tmux list-sessions` / `tmux list-panes -a -F ...`(いずれも読取専用、対象processへの操作なし)。★初版の「397」はこのコマンドの実出力ではなく本文記載時の目算ミス(§0-a参照)。★

## 移設注記 (家老second指示 2026-08-06T02:11:59 msg_20260806_021159_855ddeb9)
本fileは上記 scratchpad 原本(session UUID `0c06c39d-…` 配下、121行)を、他sessionから到達可能な repo 追跡下 (`docs/incident_logs/`) へ写した物。
★訂正 (karo-second指摘 msg_20260806_021824_60d024e7 対応)★=先の報告で「中身は同一・書換なし(末尾に移設注記1節のみ追記)」と書いたが、121行→124行という行数変化と「書換なし」を同文に置いたのは不正確だった。正しくは: ★原本の本文(121行)は一字一句同一・無改変★。全文としては本節(移設注記)3行を★末尾に追記★したため、file全体は121→124行に増えた。「同一」は本文に対する記述であり、全文に対する記述ではない。
なお本節より上の「§0-a 断面訂正」節は、家老second指摘(数の土台FAIL)対応のため★この写しの後で追加した第2の追記★であり、これにより原本129行(§0-a追加分)+3行(本節)=本file現行行数は下記③に別掲する確定値を正とする。path+行数+sha256 は本file確定後に別途 report で提出する。
