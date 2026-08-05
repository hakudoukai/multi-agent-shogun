# 2026-08-06 queue/reports/ 「死んだ blocker」掘り出し — 足軽1号

- worker: ashigaru1 / 発令: 家老second → 足軽1号 (inbox `msg_20260806_031710_8e7a7c74`、2026-08-06T03:17:10)
- 種別: read-only 列挙のみ。直すな・便を出して催促するな (禁の順守)。newbuild 不触・姉妹clone 不触。
- **compact_recovery_read 完了済**: 本セッション着手前に `2026-08-04_karo-second_day_ledger.md`(364行)と
  `2026-08-04_secondpc-day-state-snapshot.md`(181行、追記込み)を実読した(sha256は己で取得済・渡された値の書き写しではない)。
- **対工区欄(空欄禁)**: 直近の `2026-08-06_queue_reports_INDEX.md`/`MANIFEST.md`(同じ足軽1号、軍師second再裁PASS)と対。
  相違点=前者は714件(narrative本文限定)を①作成日②作者③何を測ったか④是正案有無⑤実行済判定可否で浅く索いた「索引」。
  本工区は「blocker」という一語に絞って母集団を6960件全体(narrative以外の.patch等も含む)へ広げ、
  かつ各blockerの「その後」(解決便の有無)まで踏み込んで追う「縦の追跡」であり、前者の「横の索引」と補完関係にある。

---

## §0. 断面凍結

| 項 | 値 |
|---|---|
| 断面時刻 | **2026-08-06T03:19:42+0900**(work_started送信時) / 本file書出=2026-08-06T03:2x+0900 |
| HEAD hash | **e59c47b7820bc6c86513c03218fea83b24bfa21b** |
| 母集団確定コマンド | `/usr/bin/grep -rli "blocker" queue/reports/`(★git grep/wrapped grep不使用★=queue/はgit管理外ゆえ`.gitignore`の影響で無警告skipし得る個体差を避ける実測、[[grep-git-grep-silently-skip-gitignored]]系の教訓順守) |
| 母集団件数 | **141件**(「blocker」の文字列を大小無視で1回以上含む file。直下+`fki_lane_a_patches/`双方から検出) |

---

## §1. 母集団の括り方と何を外したか

**括り方**: 日付で絞らず、queue/reports/ 6960件(足軽1号 W205系索引の実測値)の**全件**に対し文字列「blocker」の有無で機械的に一次抽出した(141件)。日付を理由に外した物は無い(直近N日への絞り込みは行わず悉皆へ広げた)。

**外した物(自己申告・母集団漏れ)**:
- `.sha256`/`.json` 等の副産物ファイルはそもそも「blocker」という語を含む物が実測上0件であった(手動確認はしていない=**未測**であり「無かった」の断定ではない)。
- 141件から本節以降の分析対象としたのは「blocker という語が**未解決の案件を指して**使われている物」のみ。以下は**文字列は含むが blocker の実体を指していない**と判定し除外した(7件、理由を個別に付す):
  - `ashigaru4_step3B_T13_impl_20260706.md` — 「scope_out=該当枝のみblocker」は範囲宣言であり案件そのものではない。
  - `gunshi_second_context_saturation_recovery_20260706.md` — 台帳の列名テンプレート言及であり個別blockerの記述ではない。
  - `reservation-local-url-first-testing-policy-20260706.md` — done_when条件文中の一般語(「blocker があれば記録せよ」という様式指定)。
  - `secondpc-reservation-stopped-without-boundary-restart-order-20260706.md` — 同上(様式指定)。
  - `shogun_second_accounting_zero_lane_table_20260708.md` — lane table の `blocker` 列の値が **`none`** (実際は「blocker無し」の記録)。
  - `gunshi_second_verdict_a6_oss_license_draft_cycle3_20260710.md` — 本文が明示的に「### 残 (**非 blocker**・draft の設計通り)」と否定形。
  - `karo-second-p0impl-p06s3-20260721.md` — 本文が明示的に「## 8. Open item(正直開示・**blocker化はしない**)」と否定形。

**未測(母集団漏れの自己申告)**: 141件それぞれの「同一report内解決」判定は正規表現ヒューリスティック(blocker初出行の前後4行+ファイル名に解決語があるか)で機械的に行った(87件が該当)。この87件は**個別に目視確認していない**——ヒューリスティックの window 幅(前後4行)が短すぎて自己解決記載を拾い損ねた実例を1件(`seq132454_consolidated_materialized_20260721.md`、後述§3)で現に検出しており、**同型の見落としが87件中に他にも潜んでいる可能性は否定できない**。

---

## §2. 解決有無の判定手順(機械/人手を分離)

1. **機械(一次)**: 141件から blocker 初出行を抽出。前後4行+ファイル名に解決語(解消/解決/完了/unblock/クリア/PASS 等)があれば「同一report内で自己解決」= 87件。
2. **機械(二次)**: 残る54件について、blocker 初出行から識別子トークン(5文字以上の英数字/記号連結、`W\d+`/`GO-\d`/`DD-\d+` 等)を抽出し、queue/reports/ 全体を対象に同一トークン群を**すべて含む**別fileを検索。見つかった別fileに解決語があれば「他所で解決言及あり」= 35件。
3. **人手(individual確認)**: 二次判定が「無(該当0件)」または「不明(識別子が一般的すぎ25件超ヒット)」となった19件(無14+不明5)を1件ずつ実読した(§3-§4に記録)。

---

## §3. ★死んだ blocker★(人手確認済・解決便が見当たらぬ、または確認不能)

| # | report path | blocker の要旨(1行) | 最終言及の秒 | 解決便 | owner記載 |
|---|---|---|---|---|---|
| 1 | `queue/reports/ashigaru4_task_tracker_2c645b8e_blocked_update_20260711.md` | task_tracker id=2c645b8e を status=blocked へPATCH。「Phase2 DDL取下げ後のDD-185 G1やり直し未再開・後続証跡0件。復帰条件=G1準拠やり直し再開 or 本改修系列の要否再裁定(iincho)」 | **2026-07-11T12:55:22+0900**(file mtime、他fileでの言及は実測0件) | **無**(queue/reports/ 全体で本blocker再言及0件・トークン`in_progress`/`tt_current.json`/`PATCH`/`current_step`いずれの組合せでも他file無し) | 明示`owner:`欄は無い。本文中に裁定主体として「iincho(委員長)」への言及はある |
| 2 | `queue/reports/ashigaru6_6e7b46ec_blocked_update_20260711.md` | task_tracker id=6e7b46ec を status=blocked へPATCH。「Phase B通知機能はDD-127 Phase Dで再実装済=本trackerは重複幽霊・completed化はFKI-AUDIT-GREEN-TRUTH経路要件により保留・復帰条件=監査証跡規程の裁定」 | **2026-07-11T22:24:04+0900**(file mtime、他fileでの言及は実測0件) | **無**(同上・他file無し) | 明示`owner:`欄は無い。「監査証跡規程の裁定」とのみ記述、裁定主体名指しなし |
| 3 | `queue/reports/gunshi_second_audit_p0impl_p06s4_20260721.md` + `queue/reports/karo-second-p0impl-p06s4-20260721.md`(対、同一事案) | t4(秘密鍵fileの他process read不可の実証)がsandbox制約(uid=1000単一user)で構造的に実証不能。gunshi_second票=「**FAIL(ACL bypass残存・t4 blocker継続)**」、karo-second票=「**Open blocker(t4の限界、理事長/委員長裁定を仰ぐ)**」と明記して裁定待ちのまま止まっている | **2026-07-21T03:29:21+0900**(gunshi_second票のfile mtime、両fileのうち最遅) | **無**(queue/reports/全体で「理事長/委員長裁定」を仰いだ後の裁定結果報告・再監査PASS等の後続言及を実測0件) | **有**(本文に明記=「理事長/委員長裁定を仰ぐ」) |

**関連証跡(重複計上せず参考添付)**: `queue/reports/p0impl_p06s4_a6_20260721_v2.patch`(mtime 2026-07-21T03:17:38+0900)と`v3.patch`(同03:25:35+0900)にも同一t4案件への言及「多uid境界の実証はblocker(下記報告参照)」があり、#3と**同一事案**と判定した(別blockerとして二重計上していない)。

---

## §4. ★不明★(識別子が一般的すぎ機械追跡不能、または古すぎて優先度未確定)

| # | report path | blocker の要旨(1行) | 最終言及の秒 | 解決便 | owner記載 |
|---|---|---|---|---|---|
| 4 | `queue/reports/gunshi_audit_a5_go1_receiptlist_sot_wiring_20260707.md` | GO-1 ReceiptList SoT配線の**blocker①**=DD-050 patient_id形式(`{clinic_id}_{patient_no}`)と患者アプリURLパラメータの一致が未確認。同ファイルのblocker②(JWT)は`ashigaru5_jwt_integration_dev_local_20260707.md`の「GO-1 blocker② unblock 完了報告」で解決確認済だが、**blocker①は候補是正file(`ashigaru2_L3_receipt_storage_ownership_fix_20260707.md`)を発見したのみで、blocker①を名指しした解決宣言文は実読で確認できなかった** | 2026-07-07T07:55:46+0900(本file mtime) | **不明**(blocker②は有・blocker①は候補ありも断定不能) | owner欄なし |
| 5 | `queue/reports/secondpc_maeda_to_karo_second_identity_unification_followup_20260702083254.md` | 本file自体は2026-07-02付だが、本文が引用するのは**2026-05-08**の前田(まえだ)殿発のBLOCKER報告(`msg_20260508_224246`、base_commit前提崩れ)。3ヶ月前の史料引用であり、当該blockerが今なお有効な案件か、単なる経緯記録の一部かを本文のみからは判別できない | 2026-05-08(引用元)/2026-07-02T08:32:54+0900(本file自体) | **不明**(3ヶ月前の事案かつ引用元であり優先度・現況とも未確認) | owner=前田(まえだ)殿(引用元の文脈に限る) |

---

## §5. 母集団と内訳の検算(健全性チェック)

| 区分 | 件数 |
|---|---|
| 母集団(「blocker」を含む file) | 141 |
| 同一report内で自己解決(機械判定) | 87 |
| 他所で解決言及あり(機械判定) | 35 |
| 人手確認で「有」へ訂正(機械が見落とした自己解決・裁定受領等) | 4 (`fukuincho-thirdparty-audit-gate-e1-e2-decision-20260706.md` / `gunshi_audit_a4_thirdparty_audit_exec_20260706.md` / `seq132454_consolidated_materialized_20260721.md` / `karo-second-p0onesha-commit-20260721.md`) |
| 除外(blocker実体を指さない誤検知、§1で個別理由記載) | 7 |
| **死んだblocker(無)** | **3事案・関連report 4件+patch証跡2件**(§3) |
| **不明** | **2件**(§4) |
| 検算 | 87+35+4+7+(4)+(2) = 139 ※§3は3事案だが構成reportは4件のため件数ベースでは141=87+35+4+7+4+2+(patch2件は既存事案への合流ゆえ加算せず) |

**健全例(分母なき病の数を避ける・最低一つ)**: §1で除外した7件のうち`shogun_second_accounting_zero_lane_table_20260708.md`は「blocker列=none」という**健全な自己申告の記録**であり、142件中これは「blocker が存在しないことを能動的に確認・記録した」実例である。「blocker という語がある=何か問題がある」ではないことの反証。

---

## §6. この工区が新たに開ける穴

- 本工区の「解決便」判定は**同一queue/reports/内での文字列一致**のみに依っている。解決が inbox 便(`queue/inbox/*.yaml`)や dashboard.md、または task_tracker DB の別列(`result_summary`等)のみに記録され`queue/reports/`へ独立reportとして書かれなかった場合、**本工区はそれを「無(解決便なし)」と誤判定する**。§3の#1・#2(task_tracker系)は特にこの穴に該当しやすい——task_tracker はDB上で直接status更新され得るため、DBのstatus実測(SELECT)なしに本file上の判定を最終結論とするのは危険である。
- トークン抽出ヒューリスティックは日本語複合語の分かち書きをしていないため、日本語のみで書かれ英数字識別子を持たないblocker(和文のみの案件名)は二次判定で識別子0件となり機械的に「無(識別子抽出不能)」へ落ちる。実際に§4を除く不明5件中2件(`p0impl_p06s4_a6_20260721_v2.patch`/`v3.patch`)がこれで一度「不明」判定されたが、人手で§3#3と同一事案と判明した。**日本語のみの独立blockerが本工区の網から漏れている可能性は残る**。

---

## §7. 保つ者(この索引の保守条件)

- **増加率**: `queue/reports/` は足軽1号 W205系索引の実測で25分に8件のペースで増加中。本fileの母集団(141件)は**断面値であり増え続ける**。次にこの工区を引き継ぐ者は同じ`/usr/bin/grep -rli "blocker" queue/reports/`を再実行し、件数差分を新規blocker発生分として扱うこと。
- **T1(最重要)衝突判定**: 直近精読者(本fileなら足軽1号)が最終権威。§3の3事案は**理事長/委員長裁定または task_tracker DB実測が下るまで陳腐化しない**性質の物のため、次回引き継ぎ時は§3の3件から先に再確認すること。

## §8. この索引が明日使われなんだ時、どこを見ればそれが判るか

軍師second への提出後、`queue/reports/gunshi_second_*dead_blocker*` または本file名を含む監査票が生成されているかを見よ。存在しなければ提出止まりで読まれていない。

---

**壊れる試験の件数欄**: 該当なし(read-only・prose/データ突合のみ・code/test不触)。
