# W207 — 「指す先」検証(足軽2号、2026-08-04)

★冒頭★= 実施=稼働直前(委員長解釈・理事長裁定待ち)・理事長GOはなお有効(「委員長が撤回」とは書
かない)。本工区は`docs/incident_logs/`配下の.md群・`queue/inbox/*.yaml`(+`_archive/`)・
`queue/tasks/*.yaml`を読み・比較するのみで、hakudokai-dev(製品repo)への実装・commit・push・
stage・DB接続・process操作は一切行っていない(唯一の例外=`audit_middleware.py`の該当行を
★読取のみ★で参照、下記§4)。裁定せず・咎めず・他者成果物は読むのみ(書換えず)。

- worker: ashigaru2 / task_id: `subtask_w207_cite_target_verify_a2_20260804`
- 発令: karo-second `msg_20260804_185826_eb028e0d`(18:58:26)
- base_commit: `502cbfe`(実測`git rev-parse HEAD`確認済・現HEAD)
- compact_recovery_read: `karo-second_day_ledger.md`(163行・sha256_16=3b4534e6b9c7c567)・
  `secondpc-day-state-snapshot.md`(113行・sha256_16=2798c91eeb5d19a6)を本工区着手前に実読済
  (両sha256は下記§3で自ら再計算し一致確認済)。
- 断面(母集団凍結時刻): **2026-08-04T19:00:44+0900**(`date`実測)。以降に作成された file
  (例=`2026-08-04_w209_decision_packet_a7.md`(mtime 19:06)・`2026-08-04_w208_uplink_number_audit_a4.md`
  (mtime 19:09))は★母集団外として明示的に除外★した(断面凍結の実践。W173/W200と同型)。

**対工区欄(空欄禁)**: 直接の前身・端緒=足軽7号W204(陽性対照やり直し、B便citation誤りを発見)・
足軽6号W196(該当citationの当事者・W204を受けて自己訂正済)・軍師second `gunshi_second_w196_relay_gap_audit`
(W196のPASS監査、citation誤りを見落としていた側)。並行=足軽4号W208(karo-second→shogun-second
上申数値の総点検、性質は近いが対象範囲が異なり・mtime 19:09で母集団外につき★直接参照せず★)。

## ★必須8項目★(新正本 id=60d41aee-5128-427d-82ae-dc0946d94682)

1. **EXISTING_ASSET_CHECK**: W204(`2026-08-04_w204_positive_control_redo_a7.md`)が既に
   msg_20260804_180115_71fb35dc→msg_20260804_181154_49780cfbのcitation誤りを1件発見済。
   本工区はこれを★複製せず、陽性対照として再現(§1)した上で、他の未検出箇所を広く探す★
   という別工程(端緒note原文どおり)。
2. **CANON_CHECK**: Root Cause 4 Patterns(③task_trackerと実態の乖離)・Anti-Duplication
   Rule・Batch Processing Protocol(30+件時必須。★本工区は選択的抽出であり悉皆30+件処理では
   ないため同プロトコル非該当★)を確認した。
3. **ACTIVE_OWNER_CHECK**: `queue/tasks/ashigaru2.yaml`の`latest_dispatch`(工区=W207)が
   本工区着手時点の当職唯一の割当。
4. **DUPLICATE_IMPLEMENTATION_RISK**: 低(上記1参照。W204と同一手法だが対象母集団が異なる)。
5. **SEARCHED_TARGET_COUNT**: `docs/incident_logs/2026-08-04_*.md`(46件、断面凍結時点)+
   `queue/inbox/*.yaml`(+`_archive/`、id実在照合用)+ hakudokai-dev 1箇所(`audit_middleware.py`、
   読取のみ)。
6. **SEARCH_RESULT_STATE**: `scanned_46_files_90_unique_msgid_cites_2_new_gaps`
   (msg_id母集団90件中、既存存在チェックは90/90=悉皆・内容突合の深掘りは15/90+陽性対照1件=
   16/90・新規発見の不整合2件。詳細は§2-§3)。**`0件`ではなく`2件`を報告する — 0件を健全と
   読まぬ規律の実践**。
7. **KNOWLEDGE_GAP_WARNINGS**: 母集団は断面凍結時点の46 file・90 msg_id citeに限る。76件の
   sha256/sha256_16出現のうち深掘り検証したのは4組(day_ledger・snapshot・w163・w165)のみ。
   msg_id 90件中74件は「id実在確認」のみでcontent突合は未実施(判定不能、§7で明記)。
8. **REUSE_OR_INTEGRATION_TARGET**: 本工区で書いたmsg_id抽出・block抽出(awk)・sha256照合の
   3手法は、後続の同種citation監査に再利用可能(スクリプト自体は成果物に含めず、手順のみ§0/§2/§3
   に明記)。

---

## §0 母集団導出法(先に導く)

**対象母集団**= 断面凍結時点(2026-08-04T19:00:44+0900)で`docs/incident_logs/2026-08-04_*.md`
に存在した**46 file**(`ls`実測、`git status --short`の`??`件数と一致確認済)。

**citeの定義(三種)**= `docs/incident_logs/`配下.mdに埋め込まれた (a) `msg_YYYYMMDD_HHMMSS_[0-9a-f]{8}`
形式のmsg_id引用、(b) `sha256=`/`sha256_16=`/`sha=`形式のハッシュ引用、(c) `path:行番号`形式の
コード/YAML位置引用。

**msg_id母集団の抽出**= `/usr/bin/grep -rohE 'msg_[0-9]{8}_[0-9]{6}_[0-9a-f]{8}'`を46 fileへ
実行→**90件のuniqueな引用先**(延べ引用回数は別途カウント)。`git grep`ではなく`/usr/bin/grep`を
用いた(既知memory「git grep/wrapped grepはqueue/等gitignore対象を無警告skip」を踏まえた予防)。

**id実在確認の方法**= 各msg_idについて`/usr/bin/grep -rn "id: <msg_id>"`をrepo全体(`queue/`
の`_archive/`含む)へ実行。**90/90件が実在確認できた(悉皆)** — ★id自体が存在しない(型③)は
本工区の母集団では0件だった★。

**優先順位(確度の高い物から)**= (1)複数file(2回以上)から引用されているmsg_id 15件を優先
(誤りの波及範囲が広いため)、(2)sha256/sha256_16は最も頻出する2件(day_ledger・snapshot、
9 file以上から引用)+その他の個別sha(w163・w165)、(3)患者安全に直結するpath:行引用
(`audit_middleware.py` L133-144、6 fileから引用)、を深掘り検証。残り(msg_id単発引用74件・
未検証sha citation大半)は§7で「未確認」と明記し、悉皆を装わない。

---

## §1 陽性対照の再現(必達③・独自の手法で拾えるか)

**端緒**= W204(足軽7号)が発見・W196(足軽6号)が既に自己訂正済の以下の事例:

| citeされたid | 実測結果 |
|---|---|
| `msg_20260804_180115_71fb35dc`(18:01:15) | 実在する(`queue/inbox/ashigaru6.yaml:578`)。内容=
  「将軍secondを母集団に必ず入れられたし」+ L1/L0陽性対照2件の提示。★W196が引用したとする文言
  「彼の更なる精密化(これが本命やも)=当職のAは他者へ因を置く断定・彼のは己へ因を置く断定」は
  **一字も存在しない**(当職が本文全文を独立に読了して確認)★ |
| `msg_20260804_181154_49780cfb`(18:11:54) | 実在する(`queue/inbox/ashigaru6.yaml:611-625`)。
  当該文言が★完全一致で存在する★(当職が本文全文を独立に読了して確認。「③彼の更なる精密化(これが
  本命やも)=当職のAは他者へ因を置く断定・彼のは己へ因を置く断定。」と一字一句一致) |

**判定**= ★拾えた★。当職が独自にW196/W204を再読せず、citeされたidの実物content(全文)と
citing側の引用文言を突合するだけの単純な手法で、既知の不一致を再現できた。∴ 本工区の方法論は
機能する(陽性対照 成功)。

**手法の精度についての限界(正直に申告)**= digit近似(180115↔181154)を機械的に検出しようと
edit-distance(隣接2桁以内)で90件のHHMMSS部分同士を総当り比較したところ、**177組**が該当した
(スクリプト詳細は割愛)。★これは母集団のタイムスタンプが密集している(数分間に数十便)ため、
edit-distanceだけでは偽陽性が大量発生し実用にならないことを意味する★。∴ digit転置仮説は
「content不一致を発見した後に、近い時刻のidを探して真の出所を特定する」という**事後の説明手段**
としては有効(§1で実証済)だが、**事前のスクリーニング手法としては機能しない**(本工区の限界の
自己開示)。

---

## §2 msg_id cite の広域走査(必達①②)

### 2-1 悉皆(id実在確認レベル)

90件全てについて`id: <msg_id>`が repo 内(`_archive/`含む)に実在するかを確認。**90/90件=実在
(型③=指す先が無い、は0件)**。

### 2-2 内容突合(深掘り、優先度上位15件+§1の2件=計17件中1件の新規不整合)

複数file(2回以上)から引用されているmsg_id 15件について、citeされた側の全文を独立に読み、
citing側の文脈・引用文言との整合を確認した。結果:

| # | msg_id | 実在 | 内容整合 |
|---|---|---|---|
| 1 | `msg_20260804_175116_ed4d9bcc`(karo-second→a1) | ○(`queue/inbox/ashigaru1.yaml:412`) | ①一致(「34便退避」「18便+16便削除」等、W169/W181/W193/W202の引用と符合) |
| 2 | `msg_20260804_181154_49780cfb` | ○ | ①一致(§1参照) |
| 3 | `msg_20260804_180758_6903c2a7`(将軍second→karo-second) | ○(`_archive/karo-second_pruned.yaml:11092`) | ①一致(W204実測どおり全文読了・「n=2・独立」等符合) |
| 4 | `msg_20260804_180115_71fb35dc` | ○ | ②不一致(§1参照。ただし★W196本体が既に自己訂正済で現行文書には残らず★) |
| 5 | `msg_20260804_174845_70e1178c` | ○(`queue/inbox/shogun-second.yaml:357`) | ①一致(「②足軽5号のblocker、真因が判り申した」= W191の引用「判り申した」と符合) |
| 6 | `msg_20260804_174704_3721c8c8`(karo-second令) | ○(`queue/inbox/ashigaru4.yaml:456`) | ①一致(「W174に一条追補」= W167/W176/W189の引用と符合) |
| 7 | `msg_20260804_173906_c8949ae2` | ○(`_archive/karo-second_pruned.yaml:10984`のみ。**現行`queue/inbox/karo-second.yaml`には存在しない**) | **②パス不一致(新規発見、下記2-3)** |
| 8 | `msg_20260804_184434_bd00dc3c`(W204正式発令note) | ○(`queue/inbox/ashigaru7.yaml:581`) | ①一致 |
| 9 | `msg_20260804_184301_11093d40` | ○(`queue/inbox/ashigaru1.yaml:12`) | ①一致(「誰が保つか」への回答、W197 Addendum2の見出しと符合) |
| 10 | `msg_20260804_182950_6fbcec8f` | ○(`queue/inbox/ashigaru1.yaml:484`) | ①概ね一致(W197 Addendumの文脈と符合) |
| 11 | `msg_20260804_182102_5283cd9e`(当職宛・W193発令) | ○(`queue/inbox/ashigaru2.yaml:560`、★当職自身の受信箱★) | ①一致(自己観測=最も確度が高い) |
| 12 | `msg_20260804_175648_fb6ce7ab` | ○(`_archive/karo-second_pruned.yaml:11530`) | ①一致(「当職も同罪に御座る」= W192/W196の引用と符合) |
| 13 | `msg_20260804_174350_82a6a233` | ○(`_archive/karo-second_pruned.yaml:11268`。from=shogun-second/type=cmd_new/ts=17:43:50、`karo-second_inbox_snapshot.md`#035と完全一致) | ①一致 |
| 14 | `msg_20260804_173914_8fe599d9`(W174完遂報告) | ○(`_archive/karo-second_pruned.yaml:10999`、from=ashigaru4) | ①一致(W167の「当職発」= a4自身の報告と整合) |
| 15 | `msg_20260804_165146_5c98c9d1` | ○(`queue/inbox/ashigaru3.yaml:602`) | ①一致(「人を測る台帳の最も深い欠陥」が本文に一字一句存在、W192の引用と符合) |

**17件中15件=①一致・1件=②不一致(既知・自己訂正済)・1件=②新規不一致(下記)**。

### 2-3 新規発見①: `msg_20260804_173906_c8949ae2`のパス不一致

`docs/incident_logs/2026-08-04_w183_type_taxonomy_a4.md`(足軽4号)の候補⑧が以下のように
citeしている:

> ⑧= `dashboard.md` 項番00A (g)(h)(i)節 + `queue/inbox/karo-second.yaml` msg_20260804_173906_c8949ae2
> (将軍second→家老second、17:39:06)

★実測=`queue/inbox/karo-second.yaml`(現行/live)には当該idが**存在しない**。当該idが実在する
唯一の場所は`queue/inbox/_archive/karo-second_pruned.yaml:10984`(pruneで退避済)★。id自体・
from/type/timestampメタデータ(shogun-second/cmd_new/17:39:06)は完全一致するため**「id先の
中身が無い」(型③)ではなく「citeされたpathが指す実ファイルが違う」(型②のpath版)**と判定する。

内容面(このidの本文が「dashboard.md項番00A」を論じているか)は、本文を全文読了した限り
★言及なし★(本文は「落度42の直し」「飽和は働けぬではなく働けば忘れる」等が主題)。∴ W183の
候補⑧citeは「id・timestampのメタデータは正確だが、(a) pathが現行ファイルを指しておらずarchive
のみに実在、(b) 本文が候補⑧の主題(dashboard 00A)を直接論じているわけではなく補助的な位置付け」
という★二重の緩さ★を持つ。**断定はしない**= 執筆当時(W183断面=18:1x頃)に既にpruneされていた
のか(pruneログに個別id記録が無く時刻の前後は本工区では確定できず、判定不能=第四値)、それとも
執筆後にrotationで消えたのか、当職には確認できない。

## §3 sha citation の検証(必達①②)

### 3-1 健全例(必達・最低一つ)

| file | citeされたsha | 実測sha256 | 一致 |
|---|---|---|---|
| `karo-second_day_ledger.md` | `sha256_16=3b4534e6b9c7c567`(INDEX/w180/w183/w185/w189/w193/w197/w202・計8+file以上から引用) | `3b4534e6b9c7c5678300e8f75b142b6a3f8ee8372111822c5e73daafaa28fd66` | ①完全一致(先頭16桁も163行数も一致) |
| `secondpc-day-state-snapshot.md` | `sha256_16=2798c91eeb5d19a6`(同上・同数のfileから引用) | `2798c91eeb5d19a61da862ee125226a862ce418b89cbee59ddee05cf733ea9d4` | ①完全一致 |
| `2026-08-04_w163_commendation_recount_a1.md` | `sha256=33192092ed1e2c37c114b40ad93371e52bf0d8647e8da1af32de7cccedc52a33`(W171引用) | 同上(131行含め一致) | ①完全一致 |
| `audit_middleware.py` L133-144(hakudokai-dev、読取のみ) | 「before_value/after_value/patient_idを一切渡していない」(day_ledger/snapshot/W183等・複数file) | 当該行を実読=`log_audit(conn, action=, operator_id=, ..., target_detail=f"{method} {path}", ...)`。★before_value/after_value/patient_idの引数は無い★ | ①完全一致。本日最も患者安全に直結するciteが健全であったことを確認 |

∴ **今回検証した基盤2 fileのsha・w163のsha・患者安全citeは悉く①(指す先が在り中身も合う)**。
これは今回サンプルの中では良い偏りだが、★この4件は今日最も多くの人が読み・多くの目に晒された
citeでもある(選択バイアスの自己開示)★。

### 3-2 新規発見②: `2026-08-04_w165_index_crossgap_a6_20260804.md`が★repo外にしか存在しない★

`2026-08-04_w171_four_ledger_reconcile_a6.md`(足軽6号、自己citation)は「④ 自身のW165
(`w165_index_crossgap_a6_20260804.md`、161行、sha256=84f3d7270c426d442647a896d1e37b4a98dd35eac3c181e733a5fa9e0f853b7b)」
を①②③(day_ledger/snapshot/w163、いずれも`docs/incident_logs/`配下)と★並記★している。

★実測= `docs/incident_logs/`配下に該当fileは**存在しない**★。repo全体を検索した結果、実物は
`/tmp/claude-1000/.../e25d7399-058a-4bef-bc33-81d5d6a89eed/scratchpad/w165_index_crossgap_a6_20260804.md`
(★別sessionのscratchpad、gitの管理下外★)にのみ存在した。当該fileのsha256を実測したところ
`84f3d7270c426d442647a896d1e37b4a98dd35eac3c181e733a5fa9e0f853b7b`(161行)で**cite値と完全一致**。

**判定**= 中身(sha・行数)は正確だが、citeが暗黙に前提とする所在(①②③と並記=同じ
`docs/incident_logs/`配下)が★事実と異なる★。W173/W177(足軽2号・当職自身が本日実施した「救済」
work)がまさにこの型を予防する目的で発令されたが、★W165はその救済対象に入っていなかった★
(W166は救われたが、W165は同種の危険な状態のまま残っている)。当職の`git status --short`実測=
`docs/incident_logs/`に`w165`を含む行は0件(=証拠が無いことも確認済、0件を「無いことの証明」
ではなく「探索結果」として報告)。

**咎めない**= これは足軽6号個人の失念というより、★W173/W177が「W166 1件」に限定して発令され、
同種リスクを持つ他の完了工区(W165含む)への横展開が発令されていなかった★という運用側の
カバレッジの穴に見える(所見、裁定ではない)。

## §4 path:行 citation の検証(必達①、患者安全)

`audit_middleware.py L133-144`引用は§3-1に記載(健全・①一致)。加えて`_archive/karo-second_pruned.yaml`
内の行番号citation(W204の`:11064-11096`・`:11092`、当職の`queue/inbox/ashigaru6.yaml:611-625`)
は本工区の§1/§2で当職自身が同じ行番号を独立に開いて確認しており、いずれも①一致(該当行に
該当content が実在)。

---

## §5 三値+第四値・総括

| 判定 | 件数 | 内訳 |
|---|---|---|
| ①指す先在り・中身も合う | msg_id 15件(§2-2)+sha 4件(§3-1)+path:行 4件(§4) = **23件** | 本工区が全文読了・独立確認したもののみ |
| ②指す先在るが中身/所在が合わぬ | **3件** | (a)`msg_180115_71fb35dc`(既知・W196自己訂正済) (b)`msg_173906_c8949ae2`(新規・pathがarchiveのみ) (c)`w165_index_crossgap_a6`(新規・repo外scratchpadのみ) |
| ③指す先が無い | **0件**(msg_id悉皆90/90で0件。sha/path:行は検証した範囲で0件) | ただし§7参照(未検証分にも0件と断定はしない) |
| ④判じ得ぬ | **1件** | `msg_173906_c8949ae2`のpath誤りが「執筆時から誤っていたか/後でrotationしたか」は本工区の手段では確定不能 |

**母集団に対する被覆率**= msg_id 90件中、id実在悉皆=100%(90/90)、内容深掘り=約19%(17/90、
§1の1件含む)。sha256/sha256_16の延べ76出現中、深掘りしたのは4組(基盤2+w163+w165)。
path:行は代表2件(audit_middleware.py・自身が読んだarchive行)。

---

## §6 母集団漏れの自己申告

1. msg_id単発引用(1回のみ引用された75件)は**内容突合を実施していない**(id実在のみ確認)。
   優先順位(§0)に従い複数引用id・患者安全関連citeを先に検めたため、時間内では及ばなかった。
2. sha256/sha256_16の延べ76出現のうち、深掘りしたのは4組のみ。特に`w201_inbox_watcher_cure_a3.md`
   に頻出する`sha=288f455f`/`sha=6dcfc02c`/`sha=fe2ed51d`等は★未検証★。
3. `docs/incident_logs/`以外の場所(`queue/reports/*.md`監査記録本文中のcite、`dashboard.md`
   本文中のcite)は本工区の探索範囲に含めていない(母集団=`docs/incident_logs/2026-08-04_*.md`
   のみと§0で明示済)。
4. **己のciteも母集団に含めた(必達(4))**= 当職自身の過去工区(W187/W193/W198/W202)が引用する
   msg_idのうち`msg_20260804_182102_5283cd9e`(自分宛のW193発令)を検証対象に含め①一致を確認
   した(§2-2 #11)。他の自己citeは時間内では及ばず、これも漏れとして明記する。

## §7 この工区が新たに開ける穴

1. **W165と同型のリスクが他にも残っている可能性**= W173/W177は「W166」1件を名指しで救済したが、
   本日完了した工区のうちscratchpadにのみ残り`docs/incident_logs/`へ未移送のものが他に
   在るかは★本工区では悉皆探索していない★(母集団=`docs/incident_logs/`配下のみのため、
   救済対象そのものを網羅する設計になっていない)。
2. **citation誤りの発見自体が「見つけた者の手法依存」である**= 当職の手法(全文読了による
   quote突合)は、W204と同様に労働集約的で悉皆に向かない(§1で示した通りedit-distance等の
   機械的スクリーニングは偽陽性率が高すぎる)。∴ 本工区で見つからなかった不一致が「無い」
   とは言えない(§6参照)。**本工区自体が「言われた事の周辺しか深く見られない」という、
   W196が自ら指摘した限界(④広域走査)と同型の限界を負っている**。
3. **archive/live間のpath二重性が今後も誤citeを生む構造**= §2-3の`173906_c8949ae2`は、
   prune(退避)が起きた事実をciting側が把握していなかったために生じた可能性が高い。
   pruneが発生した時、当該idを既にciteしている成果物へ「pathが変わった」と通知する機構は
   ★存在しない★(本日何度も出た「様式を改めた者は検める機構の持ち主へ告げよ」の兄弟問題=
   ★『pathを動かした者は、それを既にciteした者へ告げよ』という機構が無い★)。

## 為し得たのに為さなんだ事

sha256/sha256_16の残り約72出現・msg_id単発引用75件の悉皆突合を選ばず、複数引用・患者安全・
陽性対照優先という★速さを選んだ★(W166で足軽1号が選んだ道と同型)。ETA内優先順位の結果であり、
時間があれば残余をpipelineで処理できた可能性がある。

## 禁止事項遵守確認

裁定 — 一切なし。他者成果物・発言の書換え — 一切なし(全て読むのみ)。実装/commit/push/stage —
一切なし。hakudokai-devへの接触は`audit_middleware.py`の該当行の**読取のみ**(書込0件、
`cd`せず絶対path指定、`git -C`類も不使用でOSレベルの`sed`/`ls`によるread-onlyアクセスに限定)。
DB接続 — 一切なし。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。本DRAFTは軍師second殿へ監査提出する。

以上、W207直命への応答。
