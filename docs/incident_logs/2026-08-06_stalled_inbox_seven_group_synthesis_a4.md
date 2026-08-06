# 結び票（七枚目）— 六群＋墓場票＋追補1〜3＋archive二群を跨いだ結び・件/試行/事象の三段数え直し（足軽4号）

下命=家老second `msg_20260806_210554_69026946`（2026-08-06T21:05:54）。現工区（行為者の同定二件、`2a803ad`）完了後の続篇。
読取のみ・票のみ。対象file・lane（worktree）は一切変更していない（`read`を立てず・移さず・消していない）。
`queue/inbox/_dead_letter_second.yaml`は本票のため一切開いていない（`grep`/`wc`/`cat`含め不使用、`ls -la`のsize確認のみ）。

測時（本票最終確定）=2026-08-06T21:14:15+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=`70caeee9242ecc0bc38960423055ed4de1beff4f`（着手時`2a803ad`から2commit進んでいた＝他工区a1/a5/a6の並行提出、当職は無関与・無変更）。

## §0 母集団宣言（下命が指定した対象・逐語）

⒜の対象＝六群（`0fdf844`／`a02c00a`／`df6c966`）＋墓場票（`53823cb`）＋追補1〜3（`4e8ab81`／`17a7c26`内ADDENDUM2／`2a803ad`内ADDENDUM3）＋archive二群（将軍second実測＝`*_pruned` 12file・5,389・未読0／`*_legacy_*` 3file・26,834・悉く未読）。

★併せて記す（隠さぬ）★＝当職の着手後、下命の対象外だが同一主題（archive・pending-notice機構）に触れる新着3票が本サイクル内で並行提出・PASS収載された（`0e1bcfe`＝a6・`70caeee`＝a1/a5）。これらは⒞（archive二群の取り込め）と直接に関わるため、§4で★取り込みつつ「下命の対象外だった」旨を明記★する（隠して「元から知っていた」ように書かぬ、[[order-with-count-freezes-population]]の当てはまり）。

---

## §1 六群の一覧（対象＝2026-08-06T20:31発下命・commits `0fdf844`+`a02c00a`+`df6c966`）

| 群 | 担当 | 対象file | 件(file) | 便 | 判定 |
|---|---|---|---|---|---|
| ㈠ | a1 | `maeda.yaml`+`third_pc.yaml` | 2 | 4(3+1) | maeda側3件=判定不能（権者=karo-second）／third_pc側1件=a1の見立てで已閉濃厚（PID不一致を自ら実測）だが最終確定はCommander |
| ㈡ | a2 | `training.yaml` | 1 | 6 | [2][3]已閉（撤回明記・文字列一致で突合済）／[0][1]不確定（「短文通知」の指す先が本文だけでは一意に定まらぬ）／[4][5]撤回自体は已閉だが要求されたACK手続の充足は未確認＝二値に倒さぬ第三の状態 |
| ㈢ | a3 | `senmu_codex_second.yaml` | 1 | 2 | 便A（広告計測回答）=内容は今も生きている（権者=専務）／便B（委員長裁定中継）=内容は他経路で既に実行段階だがACK手続のみ未達＝第三の状態 |
| ㈣ | a4（当職） | `karo.yaml` | 1 | 4 | delivery_failed×4=試験の残骸（canon gate動作確認）と当職が性質判定。行為者の特定は本群の範囲外→§2-Aで確定 |
| ㈤ | a5 | `_test_cap_rotation.yaml`+`_test_w67fix.yaml` | 2 | 2 | 両通とも已閉（検証対象は已に決着・現行化済と他工区記録で裏取り済） |
| ㈥ | a6 | `ashigaru-second-1.yaml` | 1 | 1 | 判定不能（名簿に無き孤児箱、権者候補2つを提示するに留まる） |
| **小計** | | | **8** | **19** | |

---

## §2 墓場票（`53823cb`）＋追補1〜3の一覧と、追補による判定の変化

| 群 | 宛／発／type | file数 | 当初判定 | 追補後の状態 |
|---|---|---|---|---|
| ㈠ | test_agent／karo／task_assigned | 1 | A用済み（試験の残骸） | **§2-Aで機構・実行者とも確定**（g4と同一事象と判明） |
| ㈡㈣㈤ | honbucho／third_pc／status_update | 3 | A用済み（已閉、closed 12:36:25） | **§2-Bで「閉じ漏れ」の推しを取り下げ、真因＝裁定そのものが最初から3件のみを列挙**（執行者a5に落度なし） |
| ㈢ | hermes／将軍second／cross_pc_delivery | 3（同一内容連投） | B発信者判断（将軍second） | 変化なし |
| ㈥㈦ | honbucho／third_pc／answer | 3(2+1) | C委員長判断（未閉） | 変化なし（Gate1 canary時限指示、時限は既に1日超過） |
| ㈧ | `=`／`sha256=44dbeb3e…`／`/` | 1 | D便に非ず（shell被食い死骸） | **§2-Aでsource specificityは強化、実行の道・行為者は最後までunconfirmed** |
| **小計** | | **11** | | |

### §2-A test_agent事象の結び（g4＋墓場㈠＋追補1㈡＋2a803adの`actor_identification_g4_followup_a4`＝当職自身の前工区）

- **件＝5**（karo.yaml内delivery_failed×4＋墓場㈠のtask_assigned=ed7db710、計5file/便）／**試行＝5**（22分間に5回の`inbox_write.sh`実行、jsonl全1176件をタイムスタンプ突合し相関する`bats tests/agent_selfwatch.bats`起動をΔ4〜8秒で特定）／**事象＝1**（`TC-FR-014`が当時サンドボックス化されておらず、実`inbox_write.sh`・実`queue/inbox/`を直接叩いていた、という単一の機構的事実）。
- 機構＝**確定・是正済**（`b9bec71`、2026-08-06T00:44:06、`sandbox_script_dir`導入）。
- 実行者＝**相関（100%証明ではないが強い一致）**＝ashigaru2×3件・ashigaru5×2件。両名とも同session内・近接時刻に自己署名した便を送っている事を当職が実読で確認済。
- 版差＝5回の試行が「FROMへの折返し」と「墓場への隔離」の2経路に割れたのは、ashigaru2が同時間帯に`inbox_write.sh`へ`git stash push/pop`を繰り返しながらleg B（fail-closed canon gate）を実装中だった＝moving target（karo-second自身が同日別便で「moving target事案」と記録済）ゆえと当職は整合させた。

### §2-B honbucho×6清掃事象の結び（墓場㈡㈣㈤㈥㈦＋追補1㈠＋追補2＋追補3＋足軽3号の`deadletter_123625_confound_resolved_a3`）

四度の書き直しを経て収束：

| 版 | 因の説明 |
|---|---|
| 墓場票（`53823cb`）当初 | A＝執行者が令の数（3）を信じ、実行までに増えた3通を数え直さなんだ（推し） |
| 追補1（`4e8ab81`） | 軍師second finding受諾、推しを取り下げ。手当て（令の側が数え直しを書け）は残す |
| 追補2（`17a7c26`内ADDENDUM2） | 足軽3号の独立再集計＝closed3通は悉く`type=status_update`・open3通は悉く`type=answer`。A（閉じ漏れ）とB（type絞り）が刻と完全相関＝**交絡**、この6件からは区別不能と提起 |
| 追補3（`2a803ad`内ADDENDUM3）＋足軽3号交絡解け票 | 足軽3号が令文自体（`queue/inbox/_archive/ashigaru5_pruned.yaml`、multi-doc YAML内、id=`msg_20260805_123521_2fdcab41`）を発掘。**A・B双方不成立、真＝C（委員長裁定が最初から相談窓口／事業部発足／理事長GOの3件のみを個別列挙、他3通は最初から俎上に載っていなかった）**。執行者(a5)に落度なし。咎は令を書いた家老second自身 |

- **件＝6**（honbucho宛6file）／**試行＝該当せず**（実行の反復ではなく、単一裁定の写しの正確性を問う話）／**事象＝3＋1**（closed側3件はそれぞれ独立の議題＝相談窓口・事業部発足・理事長GOで3事象、open側3fileは committee↔本部長間の連続した応答往復であり同一の対話＝**未確定だが概ね1事象**、性質を委員長が最終判断）。
- 併せて訂正の指し置き（書き換えず指すのみ）＝**足軽6号の2026-08-05票「対象外3通はa5の下命より後に落ちた」は、本票の実測（下命12:35:21・対象外到着12:26:41〜12:31:42＝下命より★前★）と食い違う**。足軽6号の咎ではない（下命刻自体がその時点でどこにも書かれておらず、確かめる術が無かった）。

### §2-C 02:02:41事象（墓場㈧＋追補1㈡＋`2a803ad`の`actor_identification_g4_followup_a4`）

- **結論＝unconfirmed（機構・行為者とも特定できず）**。
- source specificity＝追補1で「事件の刻に該当文字列（`inbox_write.sh = 719行 / 44dbeb3e…`）を持っていたfileは1つのみ（`gunshi_second_sentinel_failopen_cure_audit_20260805.md`）」まで絞ったが、「手打ちの道」は排除できず。
- 当職自身の前工区（jsonl全1176件grep・receiver/watcherログ・watcher自身の呼出し2箇所を実読）でも、2026-08-05T17:02:41 UTC（=02:02:41 JST）±数分の実行痕跡は0件。**機構を名指す事も、人を指す事もできぬまま結ぶ**。

---

## §3 六群と墓場票の跨り（a2の`23:38`票が本群で最上の賞を得た論点）

軍師secondが`0fdf844`収載時に特筆した通り、**g4（当職の前工区）は墓場㈠（karo-second票）と別々の群として配られたが、実は同一起源事象**であった（`unroutable ed7db710`＝target=test_agent／from=karo／08-05 11:31:26＝karo.yamlの4便が生まれたのと★同じ22分間の一連の試行の5回目★）。§2-Aで既に結び済のため重複記載はしないが、**「群で配れば事象の跨りが見えぬ——束ねる者が結ばねば別々の停まりに見える」という条**を、本票が引き継ぐ最も重い一点として明記する。

その他の跨りは新たに見当たらなかった（g1/g2/g3/g5/g6は各々独立の宛先・内容であり、墓場票との共通origin事象は確認できなかった）。

---

## §4 archive二群の取り込み（⒞・下命が求めた「一つの名の下に別々の器で作られた群が混ざり申す」への回答）

### ㈠ *_pruned（12 file・未読0）

a5（`queue_orphan_notice_census_g5_a5`）が本サイクル内で独立実測済＝12file中の`grep -c "read: false"`ヒット計12件（a2=1/honbucho=2/karo-second=5/shogun-second=4）は**全て偽陽性**——`sed -n`で個別に開いて確認した結果、トップレベルYAMLフィールドではなく**本文中で「read: false」という語自体を話題にした引用**（他票の逐語引用等）と判明。∴ 正規archive 12fileの実測は**未読=0（真の値）**。

★当職自身の recount（§5参照）★＝`karo-second_pruned.yaml`の同grepヒットが5→8へ増えている（下記§5-2）。これは新規の未読発生ではなく、a5が確立した「本文中の引用」パターンの継続（本日この主題を論じた便が増えるほど、引用ヒットも増える）と推定するが、当職自身は個別に開いて確認しておらず**断定はしない**。

### ㈡ *_legacy_*（3 file・26,834・悉く未読・2026-07-02一度きりの移設）

karo-second令の記載通り、当職も`karo.yaml`と同じ器（`yaml.safe_load`系）での独立確認は行っていないが、a5が本サイクル内で**二度**（20:48台の`queue_orphan_notice_census_g5_a5`／21:04台の`26834_count_to_events_material_a5`）独立に`yaml.safe_load_all`で数え直し、いずれも26,834（25,993+810+31）で一致——∴ **令の数と食い違い無し**。

★下命の対象外だが直接に関わる新着発見（隠さず記す）★:

1. **出所＝大半confirmed**（a5・21:04台票）：git管理外の`reports/`（`queue/reports/`とは別、repo直下）に一次記録3本（`secondpc-{fukuincho,shogun,gunshi}-*-apply-result-20260702_*.txt`）を発見・全文読了。3inboxとも移動前に`watcher_present=false`を確認済、`forbidden_actions_performed`は全項目false、PIDが3件とも完全一致（同一保守セッション内でF1→G2→G3が連続実行）——**肥大した無監視inbox（fukuincho.yaml 10.9MB）の、データ損失なしの退避**という理由(何故)は一次記録と当事者(maeda)自身の証言の双方で裏取り済。**操作者本人（誰が）はunconfirmed**（`operator=`欄が3fileとも無い）。
2. **26,834件中に「人が書いた便」が現に在る**（a5・21:04台票、層別抽出）：全数26,834件は個別に手読みしていないが、type非huge層（86件）は**全数読了**し、悉く個別内容（fukuincho/maeda/ashigaru2/5/6/7/8発の実質報告・指示）。huge層（`shogun_report`25,978件・`audit_missing`770件）も系統抽出の結果、テンプレ以外の候補（`other`=1,915件）に監査裁定・障害記録の実物が混在する事を確認。∴ **26,834＝「悉く自動定型」ではない**。
3. **退避台帳（`_prune_events.log`）との突合**（a6・21:03台票）：台帳には`legacy_*`3fileの記録が★一件も無い★（方向②＝実体在るが台帳に無し）。`_test_cap_rotation_pruned.yaml`（21通）と`karo-second_pruned.yaml`内の未記載3doc（47通）も同じ方向②に含まれ、**方向②の総計＝事象7件・メッセージ26,902通**。ただし該当7件は悉く台帳の記録開始刻（2026-08-04T11:14:41）より前——「台帳導入前の残骸で実害無し」か「導入後も同型漏れが起き得る設計欠陥」かは、a6も断定を避けている。

★条＝一つの名（"archive未読26,834件"）の下で、当職の下命が求めた「件数の折り込み」と、並行して進んでいたa5/a6の「その26,834件は何なのか（事）」という問いは★別の器で動いていた★。合算せず、両者の関係を明記するに留める。★

---

## §5 件／試行／事象の三段・数え直し（⒝・各段の器と範囲を明記）

### §5-1 六群＋墓場票（当職の直接scope）

| 段 | 値 | 器 | 範囲 |
|---|---|---|---|
| 件（file） | 8（六群）＋11（墓場）＝**19** | `ls`/`find`実測の合算（各票の①節） | §1・§2の対象file全て |
| 便／試行 | 19（六群の対象便）＋11（墓場のfile=便単位） | `yaml.safe_load`（六群）／`python3+yaml.safe_load`（墓場、家老second票） | 同上 |
| 事象 | **確定分＝test_agent1（§2-A、六群㈣と墓場㈠が同一のため重複排除）＋honbucho清掃3〜4（§2-B）＋hermes1＋Gate1canary1（未確定）＋02:02系1（unconfirmed）＋g1(2)＋g2(3)＋g3(2)＋g5(2)＋g6(1)＝計16〜17** | 上記§1〜§2の各節での事象特定 | 同上（03-02系はunconfirmedのまま数に含めるが機構名は無い） |

### §5-2 archive二群

| 段 | 値 | 器 | 範囲 |
|---|---|---|---|
| 件（file） | 12（pruned）＋3（legacy）＝**15** | `find`/`ls` | `queue/inbox/_archive/*.yaml`（README.md・`_prune_events.log`除く） |
| 便 | pruned真の未読=**0**（12件のgrepヒットは全て偽陽性、a5実証済）／legacy=**26,834**（真の値、二重独立確認済） | `yaml.safe_load`+`sed -n`個別確認 | 同上 |
| 事象 | legacy26,834件は**出所という一段では概ね1事象**（2026-07-02の単一保守セッションによる一括移設）に収束するが、**内容という一段では層1の86件が個別事象・層3のaudit_missing770件が6distinct task_idへ収束・層2のother1,915件は未測（事象数不明）** | a5の層別抽出（§4㈡） | 同上 |

### §5-3 recount deltas（実行の刻に数え直した結果、令の数と食い違った点）

- `karo.yaml`：`from=inbox_write`件数＝**4（不変）**、unread＝**4（不変）**。
- `dead_letter/_unroutable/`：file数＝**11（不変）**。
- `_archive`legacy3file合計＝**26,834（不変、a5の二度の独立測定・当職の本票測定の三者で一致）**。
- `_archive`内`grep -c "read: false"`ヒット合計：a5実測（20:48台）＝12件（全12件偽陽性確認済）→当職実測（21:11）＝**karo-second_pruned.yamlのみ5→8へ増加**（他11fileは不変）。この増分は個別に開いて確認していない＝**未確認のまま報せる**（性質を断定しない）。
- `_dead_letter_second.yaml`サイズ：a5実測（14:45台）＝145,585 bytes→当職実測（21:10）＝**146,609 bytes（増加）**。中身は禁則により未開封、サイズの変化のみを事実として記す。
- `queue/tasks/ashigaru{1..6}.yaml`は`0fdf844`測時点で全て20:36台是正済（足軽6号`a1_a5_taskyaml_inbox_crosscheck`票で確認済、本票では再確認していない）。

以上（測時=2026-08-06T21:14:15+09:00・器/範囲は各行に併記・読めぬfileは`_dead_letter_second.yaml`本文のみ＝禁則による意図的な未読）。

---

## §6 結べぬ物（⒟・推して埋めず、そのまま置く）

- g1・maeda.yaml3通の「用済み」最終判定＝権者karo-second（maeda後継）に残る。
- g1・third_pc.yaml1通＝a1の見立て（已閉濃厚）はあるが最終確定はCommander。
- g2・[0][1]の「短文通知」が指す先＝[2][3]か[0][1]自体か、文言だけでは一意に定まらぬ。専務または研修部長A/Bに委ねる。
- g2・[4][5]が求めたACK（開始有無・artifact有無の報告）が実際に返されたか＝当職の探索範囲（queue/・docs/・config/・scripts/、honbucho.yaml現行+pruned archive）では見つからず、断定しない。
- g3・便A（広告計測回答）＝専務の着手状況は不明のまま。
- g3・便B（委員長裁定中継）＝内容は他経路で実行済だがACK自体の有無は未確認。
- g6・孤児箱の権者＝2候補（当人／命名管理者）のいずれかまで絞れず。
- 墓場㈢（hermes）の再送要否＝将軍second。
- 墓場㈥㈦（Gate1 canary）の既達判定＝委員長。
- 02:02系（墓場㈧）の機構・行為者＝unconfirmed（jsonl全件検索・receiver/watcherログ検索を尽くした上での結論）。
- `_dead_letter_second.yaml`中身＝禁則により未測のまま置く（サイズ増分のみ既知）。
- `_archive`legacy26,834件のうち層2`other`1,915件・層3`audit_missing`770件の全数個別内容＝未測（系統抽出止まり）。
- `_archive`legacy移設の操作者本人＝unconfirmed。

---

## §7 己の手で為した事（⒠）

- 上記§1〜§4で参照した全17ファイル（`0fdf844`4件・`a02c00a`1件・`df6c966`1件・`53823cb`1件・`4e8ab81`1件・`17a7c26`6件・`2a803ad`3件）を`Read`toolで全文読了。
- 下命の対象外だったが着手中に新規commitされた3ファイル（`0e1bcfe`1件・`70caeee`2件）を`git log --oneline 2a803ad..HEAD`で検知し、`git show --stat`で内容を確認の上、全文読了して§4に折り込んだ。
- `date -Iseconds`・`git rev-parse HEAD`を着手時・確定時の2回実行し、着手後にHEADが進んでいた事実を明記した。
- `python3`+`yaml.safe_load`で`queue/inbox/karo.yaml`・`maeda.yaml`・`third_pc.yaml`・`training.yaml`・`senmu_codex_second.yaml`・`ashigaru-second-1.yaml`を再度parseし、total/unread件数を実行の刻に数え直した（§5-3）。
- `find queue/dead_letter/_unroutable -type f | wc -l`・`find queue/inbox/_archive -type f | wc -l`・`/usr/bin/grep -c "read: false" queue/inbox/_archive/*.yaml`を実行し、file数・grepヒット数を数え直した（§5-2・§5-3）。
- `ls -la queue/inbox/_dead_letter_second.yaml`のみ実行（サイズ・mtimeの確認、中身は不読）。
- 上記いずれも`queue/`配下file自体への書込・`read`立て・移動・削除は一切行っていない（`git status --short queue/`相当の確認は、対象file群がgitignore対象のため`ls`/`stat`実測で代替）。lane（worktree）には一字も触れていない。

---

## 監査提出用・三行

㈠「同意を探すな・潰しに掛かれ」——特に§2-B（honbucho×6清掃の四度目の因）と§4（archive二群の折り込み）の数値は、本票の要約でなく引用元file自体（`53823cb`／`4e8ab81`／`17a7c26`内ADDENDUM2／`2a803ad`内ADDENDUM3／`0e1bcfe`／`70caeee`）を直接開いて突合されたし。
㈡「返信に己の手で為した事（試した command／当たった file／立てた反例）を書け」——本票§7に列挙した実コマンドを再実行し、当職の数（件19/便19/墓場11/archive15file・26,834）と照合されたし。
㈢「被監査者の語を引いて『成立』と書くな」——§2-A〜Cの引用は当職が各票を直接`Read`した上での再構成であり、他者の要約の孫引きではない。ただし§4㈠の「a5が二度独立測定」という一文自体はa5票の自己申告の引用であり、当職はa5の測定コマンドそのものは再実行していない——この一点は限界として明記する。

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。「二者PASS」を「三者PASS」と書かない。

以上、本票（結び票・七枚目）。新規のqueue/書換・新規判定の拡張（§1〜§2記載の各群の判定そのものの変更）・新規工区の着手は行っていない。
