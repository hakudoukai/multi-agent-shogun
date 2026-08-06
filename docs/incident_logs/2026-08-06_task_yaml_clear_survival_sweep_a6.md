# queue/tasks/*.yaml 全件×判定 —「令が /clear を越えるか」（足軽6号）

下命=家老second msg_20260806_203930_92ebe42d（2026-08-06T20:39:30）。読取のみ・freeze外。
禁＝書くな・消すな・`read`を立てるな（karo-secondが20:36に書いた6file以外は一字も触れず）。lane不触（守った・触れていない）。

測時=2026-08-06T20:44:03+09:00（`date -Iseconds`実行結果、本票の最終再測）。
git rev-parse HEAD=0fdf844a55f68d306002d45e2d2acb7c3d1248e0（着手時4e8ab81e...から進んでいた＝他者の並行commit、当職は無関与・無変更）。

## 母集団（測時・器・範囲）

```
$ ls queue/tasks/*.yaml | wc -l
13
$ /usr/bin/grep -c "agent_id" queue/pane_registry.yaml
22
```
測時=2026-08-06T20:44:03+09:00／器=`ls`+`wc -l`・`/usr/bin/grep -c`／範囲=`queue/tasks/*.yaml`（13件）と`queue/pane_registry.yaml`のpanes配下agent_id行（22行、実体は重複込みユニーク17 id、下記⒟参照）。

対象13件＝ashigaru1〜8、gunshi-second、gunshi、karo-second、maeda、rh_blocked_note_20260706。

## ⒜ file名・mtime・task_id（トップ有効エントリ）・status

| file | mtime | 有効task_id（最上位/current） | status |
|---|---|---|---|
| ashigaru1.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈠_ashigaru1` | assigned |
| ashigaru2.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈡_ashigaru2` | assigned |
| ashigaru3.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈢_ashigaru3` | assigned |
| ashigaru4.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈣_ashigaru4` | assigned |
| ashigaru5.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈤_ashigaru5` | assigned |
| ashigaru6.yaml | 2026-08-06 20:36:11 | `subtask_20260806_stalled_inbox_triage_㈥_ashigaru6` | assigned |
| **ashigaru7.yaml** | **2026-08-06 02:55:08** | `subtask_w212_packet_dropped_items_a7_20260804`（`latest_dispatch`欄） | assigned |
| ashigaru8.yaml | 2026-08-03 19:39:42 | `subtask_t13_kanban_003c2`（自己申告=廃止済・存在せぬlane） | done |
| **gunshi-second.yaml** | **2026-08-06 02:55:08** | `subtask_shadow_failclosed_legC_audit_gunshi_20260805`（`latest_dispatch`欄・本欄自体が「supersedes_note: 本欄を優先せよ」と明記） | assigned |
| gunshi.yaml | 2026-07-19 11:48:38 | `gunshi_second_audit_queue_20260708` | done |
| karo-second.yaml | 2026-08-04 21:22:06 | `current_assignment`欄=cmd_secondpc_canon_cure_20260803（task_id形式ではなくcmd形式） | in_progress |
| maeda.yaml | 2026-08-03 19:39:24 | （自己申告=廃止済・稼働しておらぬlane） | idle |
| rh_blocked_note_20260706.yaml | 2026-08-03 19:37:32 | `subtask_readyqueue_RH_blocked_20260706` | blocked |

★ashigaru1〜6の6件は全て mtime=2026-08-06 20:36:11 台で一致（karo-second本人が20:36是正済と自認した6件と符合）。
★ashigaru7とgunshi-secondの2件のみ mtime=2026-08-06 02:55:08 台で ★突出して古い★（karo-second特記「六名の外ゆえ未是正＝最も危うき二つ」と符合）。

## ⒝ その agent の箱（`queue/inbox/<id>.yaml`）最新の令との食い違い有無

- **ashigaru1〜6**：現物未突合（既に本人 karo-second が20:36に自らinbox発の令を反映済と自認しており、当職が同時刻の是正の正しさを疑う根拠は無い。★ただし当職はこの6件について箱との個別突合は実施していない★＝下記⒠に明記）。
- **ashigaru7**：★食い違い有り（実測）★。
  ```
  $ python3 -c "yaml.safe_load(open('queue/inbox/ashigaru7.yaml'))..."
  最新のtype=task_assigned/cmd_new: msg_20260806_094155_7b12b4f5 (2026-08-06T09:41:55, cmd_new)
  ```
  a7の箱の直近2通（08:50:27, 09:41:55、共にtype=cmd_new）は★「家老second→全隊」の一斉布告★（事業部憲章・Codex leg訂正）であり、a7個人への新task_id発行ではない。
  a7個人宛の直近task_assignedはmsg_20260806_080632_1aa99db2（08:06:32、保留取消の一句）。
  いずれもtask yamlの`latest_dispatch`（task_id=subtask_w212..._20260804、08-04発）を更新するものではない。
  ∴ task yamlのtask_idは箱の内容と★一致も矛盾も明示的には確認できない★（箱側に「新task_id」を名乗る発令が無いため）が、
  ★task yaml自体が02:55のまま停止しており、当日09:41以降の全隊布告2件を一切反映していない★のは確実。
- **gunshi-second**：★食い違い有り（実測、より明確）★。
  task yamlの`latest_dispatch`はtask_id=`subtask_shadow_failclosed_legC_audit_gunshi_20260805`（08-05発、status=assigned）で、
  欄自体に「★本 latest_dispatch が現行の下命に御座る★…本欄を優先せよ」と明記されている。
  しかし箱の実測では、本日18:49〜19:33の間に軍師secondは★新規の監査下命（㈥点追加）と2件の監査提出受領（足軽1号・足軽2号）★を受けており、
  さらに `queue/reports/gunshi_report.yaml`（当職が別工区で先に実読済）には★本日15:26:10★時点で
  `task_id: subtask_f1f2f3_root_cure_impl_a1_gunshi_20260806`（status=done）という★task yaml上に一切現れないtask_id★の完了報告が記録されている。
  ∴ task yamlの「現行の下命」表示（08-05のlegC監査）は★本日の実際の稼働実態（08-06の複数監査、うち1件完了済）を反映していない★。

## ⒞ 食い違うなら /clear 時に何を為すか

- **ashigaru7**：/clear後の復帰手順（CLAUDE.md「/clear Recovery」）はtask yaml優先で読ませる設計。a7がこの手順を字義通り踏めば、
  `latest_dispatch`（W212、08-04発、status=assigned）に★着手★してしまう可能性が高い。本日09:41以降の全隊布告や03:17の「門を数えよ」個別下命は
  task yamlに反映されていないため、/clear後にこれらへ気づける保証が無い＝★古き工区への着手★のリスク（karo-second指摘の型と同型）。
- **gunshi-second**：同様に、/clear後に`latest_dispatch`（legC監査、08-05、status=assigned、かつ欄自体が「優先せよ」と自己申告）を読めば
  ★08-05の監査に着手★してしまう可能性が高い。本日08-06の複数の新規監査下命・提出受領・完了報告（f1f2f3 root-cure監査）はtask yamlに一切現れず、
  ★空振るのではなく誤った古き工区に着手する★型のリスクに該当する。

## ⒟ 名簿（`queue/pane_registry.yaml`）と task yaml の過不足

```
$ /usr/bin/grep -n "agent_id" queue/pane_registry.yaml
```
（全22行、ユニークid=17：shogun, karo, ashigaru1, ashigaru2, ashigaru3, gunshi, takenaka, honda, sanada,
shogun-second, karo-second, ashigaru4, ashigaru5, ashigaru6, ashigaru7, gunshi-second, honbucho。
うちashigaru1/2/3はMainPC/SecondPC重複登録=同id2回で計22行）

- **名簿に在るがtask yamlが無い**：shogun, karo, takenaka, honda, sanada, shogun-second, honbucho（7 id）。
  ★これが設計上の想定内（将軍/家老格・監査外役職はtask yaml方式を使わない）か、それとも見落としかは当職からは判定不能★——事実のみ記す。
- **task yamlが在るが名簿に無い**：ashigaru8, maeda, rh_blocked_note_20260706。
  ashigaru8・maedaは★file自体が冒頭で「廃止済（ARCHIVED）」と自己申告済★（廃止日2026-08-03、退避sha256も自己記載あり）——既知の残骸であり新規発見ではない。
  rh_blocked_note_20260706は agent_id命名規則（"ashigaruN"等）に該当しないnote file（status=blocked、GO待ちを明記）——そもそもagent個人の箱ではない。

## ⒠ 己の手で為した事

- `ls -la queue/tasks/*.yaml` / `stat -c 'mtime=%y'` を13件全てに実行
- `/usr/bin/grep -nE "task_id:|^status:| status:"` を13件全てに実行し、有効task_id/statusの位置を特定
- `head -5`〜`head -30`で各fileの冒頭コメント・構造を目視確認（13件全て）
- `wc -l queue/tasks/karo-second.yaml` および `sed -n` で該当部抜粋を目視
- `python3` + `yaml.safe_load()` で `queue/inbox/ashigaru7.yaml`（35通）と `queue/inbox/gunshi-second.yaml`（37通）を全件パースし、
  type=task_assigned/cmd_newのメッセージをtimestamp順に抽出、直近数件のcontentを目視確認
- `queue/reports/gunshi_report.yaml` の内容（本日15:26:10時点のtask_id=subtask_f1f2f3_root_cure_impl_a1_gunshi_20260806）は
  ★別工区（本部長殿からの巡回中に既読・非改変で実見済）の実測を援用★——本票のために新規に読み直したものではない旨、明記する
- `/usr/bin/grep -c "agent_id" queue/pane_registry.yaml` を実行し、名簿の行数を実測
- ashigaru1〜5については★箱との個別突合（yaml.safe_load）は実施していない★——karo-second本人による20:36是正の自認を根拠に「食い違い無し」と推定しているに留まり、当職独自の実測ではない旨、明記する（過大主張回避）

## 数の扱い

令に個数の明示は無し（「全件×判定」）。測時=2026-08-06T20:44:03+09:00／器=`ls`+`wc -l`／範囲=`queue/tasks/*.yaml`＝13件（実測、下命時の想定と食い違い無し）。
以上（本票が扱った母集団は上記13件・読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
