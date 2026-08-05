# task_tracker 2c645b8e / 6e7b46ec — 死んだblocker掘り出し②(生死判定) — 足軽1号

- worker: ashigaru1 / 発令: 家老second → 足軽1号 (inbox `msg_20260806_034023_b034bb95`、2026-08-06T03:40:23、相談形式)
- 種別: read-only。task_tracker の中身は不触(書換禁)・便での催促もせず。列挙と判定のみ。
- 前提: 本工区は先行工区(`docs/incident_logs/2026-08-06_dead_blockers_in_queue_reports.md` §3 #1・#2、同足軽1号)で
  「死んだblocker」として検出した3事案のうち task_tracker 系2件の掘り下げ。当該先行工区 §6 が自ら書いた通り
  「queue/reports/内テキスト一致のみに依っており、DBの実SELECTなしに最終結論とするのは危険」という穴を、
  本工区で埋めに行く趣旨。
- compact_recovery_read: 本セッション着手前に `2026-08-04_karo-second_day_ledger.md`(364行)と
  `2026-08-04_secondpc-day-state-snapshot.md`(181行、追記込み)を実読済。

---

## §0. 断面凍結

| 項 | 値 |
|---|---|
| 断面時刻 | **2026-08-06T03:58:02+0900** |
| HEAD hash | **7eb9ec12d697cf980be33981184258310201d1b8** |
| 対象 | task_tracker id=`2c645b8e-0a82-42a6-9f63-8959bc15e535` / id=`6e7b46ec-7fb6-49a3-82c3-fa196e704c5b`(いずれも先行工区が省略していたUUID全体を`ashigaru4_task_tracker_2c645b8e_blocked_update_20260711.md`/`ashigaru6_6e7b46ec_blocked_update_20260711.md`原文で確定) |

## ★母集団宣言・重大な欠落の自己申告(先に書く)★

**本工区は task_tracker DB への直接 SELECT を試み、ツール側の許可分類器(classifier)により拒否された**
(理由=「production Supabase を service_role credential 経由で直接 REST query しようとした」)。
2件試行し2件とも拒否。以後は方針転換し、**queue/reports/・docs/ 配下のテキスト証跡のみ**で判定した。
**∴ 本工区の判定は「テキスト証跡ベース」であり、task_tracker DB の現在の status 列そのものは
本セッションでは再確認できていない**。先行工区(§6)が指摘した穴を完全には埋められておらず、
**同じ穴が一段狭くなった形で残っている**ことを先に明記する。

---

## §1. task_tracker id=2c645b8e (自動ACK問題改修 seq68904)

### (1) 元の記述(全文読了・何を止めていたか一行)

`ashigaru4_task_tracker_2c645b8e_blocked_update_20260711.md` の逐語blocker文言=
「**Phase2 DDL取下げ後のDD-185 G1やり直し未再開・後続証跡0件。復帰条件=G1準拠やり直し再開 or 本改修系列の要否再裁定(iincho)**」。

背景(`ashigaru4_ghost_task_probe_2c645b8e_20260711.md`、同一日07-11の材料調査、全文読了)より:
- 対象案件=「自動ACK機構が副院長読了前にACK付与する設計欠陥」を4層分離(L1/L2/L3/L4)で修正する改修(seq68904発端、2026-06-21)。
- Phase 1(影響範囲read-only棚卸し)は完遂(project_documents id=3f746942、is_current=false)。
- Phase 2(DDL実装案 v0.8.3/v0.8.3.1)は**副院長プロセス違反(直接起草)を理由に自己withdraw**され、
  「DD-185(開発ライフサイクル標準プロセス7ゲート方式) Gate1からやり直す」と2026-06-23に予告された
  (project_documents id=a50071cd / id=811c5a56、両方is_current=false・同一文言)。
- それ以降、DD-185 G1ルートでの再着手を示す証跡は pc_handshake/project_documents/task_tracker いずれにも
  **2026-06-23T20:06〜調査時点(07-11)まで0件**(07-11時点の実測)。

**一行**: 「DD-185 G1からの改修やり直し着手」または「この改修系列自体が今も必要かのiincho裁定」の
**どちらか一方が起きるまで**、進捗監視タスクを進めようがない、という待ち。

### (2) 依存先の現状

`/usr/bin/grep -rl "ACK4層\|seq68904\|自動ACK問題改修" docs/ queue/reports/`(2026-08-06実行)=
**07-11の当該report群1件を除き 0件**。DD-185 G1での再着手・iinchoによる要否再裁定、いずれの後続証跡も
2026-07-11以降 **本日(08-06)まで一切見当たらぬ**。

→ **なお未解決**(テキスト証跡上)。

### (3) ゆえに今どう扱うべきか

**生きている**。依存先(G1再着手 or iincho裁定)のどちらも起きた形跡が無く、テキスト証跡上は
07-11時点から一歩も進んでいない。対象(自動ACK4層分離という改修そのもの)が消滅した証跡も無い
(該当機能が別decisionで代替実装されたという言及も0件——6e7b46ec側とはこの点で性質が異なる)。

**但し書き(判じ得ぬ点)**: task_tracker DB の `status`/`heartbeat_at`/`updated_at` を本セッションで
直接SELECTできておらず、**07-11以降にDB上でのみ状態が変わった(例: 他者が別経路でstatusを更新した)
可能性はテキスト証跡だけでは排除できない**。この一点は「判じ得ぬ」に該当する——
足りぬ物=task_tracker当該行のDB実SELECT(本工区では取得不能だった)。

---

## §2. task_tracker id=6e7b46ec (Phase B通知機能=幽霊)

### (1) 元の記述(全文読了・何を止めていたか一行)

`ashigaru6_6e7b46ec_blocked_update_20260711.md` の逐語blocker文言=
「**Phase B通知機能はDD-127 Phase Dで再実装済(LINE優先+event駆動 index.ts)=本trackerは重複幽霊・
completed化はFKI-AUDIT-GREEN-TRUTH経路要件により保留・復帰条件=監査証跡規程の裁定。
Phase C前提のpush_notifications.pyは実体削除済だが全参照dead path・router未登録・本番配線0件=実害なし**」。

**一行**: 「この案件が本当に重複幽霊であるという主張を、当人以外の独立監査が確認する」まで
`completed`化できない、という待ち(FKI-AUDIT-GREEN-TRUTH-01=自作自演禁・仮GREEN禁の原則による)。

### (2) 依存先の現状 —— ★既に解決済(独立監査PASSを発見)★

`queue/reports/gunshi_second_verdict_a6_dr79_notify_phasec_20260712.md`(2026-07-12・軍師second発)を
全文実読。本blocker文言の`result_summary`が引用するsha「63ce017/61a9c84e」と**完全一致するsha接頭辞**
(63ce0172・61a9c84e)を持つ2件の一次報告(`ashigaru6_dr79_notify_probe_20260711.md` / 対応phasec報告)を
対象に、軍師secondが**独立に git log / grep を実測して監査**しており、判定は:

| 監査対象claim | verdict |
|---|---|
| notify-urgent は Phase B revert(33ece2e2)後 DD-127 Phase D(4c47ab89)で再実装済=DR-7.9 Phase B 重複幽霊 | **CONFIRMED**(git log実測: revert commit + 再実装commit 両存在) |
| push_notifications.py 実体削除・.pyc のみ残存 | **CONFIRMED**(ls実測) |
| push_notifications への import 0件・main.py router未登録・swStrategy dead path | **CONFIRMED**(grep実測、いずれも0件) |
| 総合 | **PASS(both)** |

→ **重複幽霊という主張そのものは、当人(a6)以外の第三者(軍師second)が2026-07-12に独立実測でPASSしている**。
これは blocker 文言が要求した「FKI-AUDIT-GREEN-TRUTH経路要件」の**技術的主張の部分**を満たす独立監査に該当する。

**但し**、この監査は「notify probe報告(sha 63ce0172/61a9c84e)の内容が正しいか」を検証したものであり、
「**task_tracker id=6e7b46ec 行そのものを blocked→completed へ状態遷移させてよいか**」という
**行為そのものへの明示的裁定(governance決定)** を別途下した記録は、07-12以降の queue/reports/・docs/
いずれにも見当たらぬ(`/usr/bin/grep -rl "6e7b46ec" queue/reports --include=*.md` の全8件を確認したが、
07-11のblocked化report・07-12の上記監査PASS以降、status更新やcompleted化を報じるreportは0件)。

### (3) ゆえに今どう扱うべきか

**完了済で落とし忘れの可能性が高いが、断定はしない**。
根拠: (a) blocker本文が要求した条件(重複幽霊claimの独立監査)は2026-07-12に**技術的には満たされた**
(軍師second PASS)。(b) 対象自体(Phase B通知機能)も消滅していない——ただし「消滅した」のではなく
「**別のdecision(DD-127 Phase D)に統合され、現機能はそちらが担っている**」という意味での対象消滅に近い
(元のDR-7.9 Phase B実装は revert 済・実体コードは削除済と独立監査で確認)。
(c) それにも関わらず、task_tracker行のstatus遷移(blocked→completed)という**手続き自体が実行された記録が無い**。

**判じ得ぬ点(足りぬ物)**: 「軍師secondの07-12監査PASS」を以て「blocker文言の“監査証跡規程の裁定”を
満たした」と読むかどうかは**解釈次第**であり、この読み替えそのものを承認する上位者(iincho等)の
明示裁定は見当たらぬ。また§0で述べた通り、task_tracker DB当該行のDB実SELECTを本工区は取得できておらず、
**07-12以降に誰かが実際にstatus=completedへ更新した可能性**(その場合はreport化されずDBのみ更新、という
先行工区§6が警告した穴そのもの)も排除できない。

---

## §3. 対工区欄

先行工区`2026-08-06_dead_blockers_in_queue_reports.md`(同足軽1号、軍師second再裁PASS)と対。
前者が母集団141件から機械+人手で3事案(うち2件が本工区の対象)を掘り出す「横の索引→縦の絞り込み」、
本工区はその2件を深掘りする「縦の追跡の続き」。加えて`ashigaru4_ghost_task_probe_2c645b8e_20260711.md`
(材料報告・判定なし)/`gunshi_second_verdict_a6_dr79_notify_phasec_20260712.md`(独立監査PASS)の
2件を新たに証跡として組み込んだ点が前者に無い前進。

## §4. この工区が新たに開ける穴

- **task_tracker DB への直接SELECTがツール許可分類器で拒否された**という事実そのものが、次にこの案件を
  引き継ぐ者にとって新たな障害になる。分類器は「production Supabase への直接REST」を一律に危険視して
  おり、read-only SELECT であっても遮断され得る(本工区で2回とも拒否・迂回として別agentへgrep委譲した
  のみでDB接触は結局できていない)。**次の担当者はDB確認の前にまずこの許可経路の要否を人間へ確認すべき**。
- §2で述べた「軍師second 07-12監査PASSを以てblocker文言の裁定要件を満たしたと読めるか」は本工区では
  裁定していない(足軽の権限外・裁定するなの禁則順守)。この読み替えの当否を誰が裁くかが空欄のまま残る。
- 2c645b8e・6e7b46ec 双方とも、**「他所で解決言及あり」の判定基準をqueue/reports/・docs/のテキストのみに
  限定している**。dashboard.md・pc_handshake DB・iincho個人のメモ等、本工区の網に掛からない経路で
  既に裁定済という可能性は依然として残る(先行工区§6と同じ穴、本工区でも未解消)。

## §5. 保つ者(この索引の保守条件)

- 2c645b8e: 次に「ACK4層」「seq68904」「DD-185 G1」のいずれかを含む新規reportが queue/reports/ か
  docs/ に現れたら、まずそのfileを読むこと(依存先の解決を示す一次証跡になる可能性が最も高い)。
- 6e7b46ec: 「6e7b46ec」を含む新規reportが現れた場合、それが「status更新」を報じているかを最優先で
  確認すること(07-12の監査PASS以降この形の報告が0件という現状を覆す一次証跡になる)。

## §6. この索引が明日使われなんだ時、どこを見ればそれが判るか

軍師second への提出後、`queue/reports/gunshi_second_*2c645b8e*` または `gunshi_second_*6e7b46ec*` の
新規監査票、あるいは karo-second からの受理返信(inbox)が生成されているかを見よ。無ければ提出止まり。

---

**壊れる試験の件数欄**: 該当なし(read-only・prose/テキスト証跡突合のみ・code/test不触・task_tracker DB不触=書換なし)。
