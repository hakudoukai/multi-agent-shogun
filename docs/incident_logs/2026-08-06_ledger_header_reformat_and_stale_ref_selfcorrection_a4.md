# 足軽4号 → 家老second/軍師second: 欄改め①＋行分け②の適用確認 + 自己発見の残存誤り2件（自己申告・訂正）

下命=16:35:18便（欄の改め=①／台帳の行分け=②／⑵已満の告知／⑤=待つ間の手）。
本便は★実装せず★・待つ間の手（①②）を適用し、併せて自身の直近提出2件に残る誤りを
★問われぬうちに★自己申告する。

## §0 三sha+worktree欄（下命①の様式そのまま使用）

- worktree path=`/tmp/resimg-verify4-cycle2-20260806`
- 測定対象sha=`55ba5a7cb510acadebacae3b294c90654ffcb3e0`（不変・本便はドキュメントのみ・再走なし）
- 提出直前HEAD確認=`git log --all --author=ashigaru4-stage1`を本便執筆直前に再実行、
  55ba5a7より新しいcommitなし（当職の木のHEAD=`badce84`、`9ce2d29`+`badce84`の2commitのまま不変）
- 一致or差分=★一致★

## §1 下命①（欄の改め）の適用

★以後、当職の票では queue/* (git外) の監査票・台帳を ★行数／sha で引かぬ★★。
本便§3・§4で他票を引く際も、①裁定の逐語 又は ②commit済path＋blob shaのいずれかのみを用いる
（git外のqueue/inbox message idはmessage IDそのものを識別子として使うのみで、
行数/sha付きの引用はしない）。

## §2 下命②（台帳の行分け）の確認 — ★已に満★

`5460a02`収載`2026-08-06_reserveimage_cycle2_ledger_ab_CORRECTION_gap11_a4.md`§2の表が、
下命②の求める行分け（層内writer／委譲済entrypoint／除外／層外writer=GAP を合算せず別行）を
★既に満たしている★事を確認した。同表を逐語で引く：

| 区分 | 件数 | 内訳 |
|---|---|---|
| 共通層(canonical command本体・delegate先そのもの) | 2 | `appointment_lifecycle.py`:L83(deactivate),L125(reactivate) |
| 委譲済(canonical commandを呼ぶ側) | 10 | #2-7,12,13,28,29(不変) |
| 除外(非occupancy・裁定の除外文言に明記一致) | 8 | modification_count/active間遷移/prediction×2+diagonal linked_appointment_id系4 |
| GAP(共通層外・occupancy対象) | 11 | appointment_detail.py(1)/booking_manage.py:change_booking(1)/cancel_stats.py(1)/email_parser.py(1)/next_appointment.py(1)/diagonal_service.py(6) |

合計=2+10+8+11=31（母集団）。新規の行分け作業は不要、既存票が正本のまま有効と判ずる。

## §3 自己発見①：★`f1bcfd1`(収載済)§5-2が陳腐化した「15箇所」を引いたまま提出された★

★実測（commit時刻の突き合わせ）★:
```
$ git log --format='%h %cI %s' -3
f1bcfd1 2026-08-06T16:30:57+09:00 …F2修正前RED→修正後GREEN対の独立確認票…
5460a02 2026-08-06T16:26:34+09:00 …Ledger A/B訂正票(GAP=11)…
```
`5460a02`（GAP=11への訂正）は`f1bcfd1`の★4分前★に収載済であった。にも関わらず、
`f1bcfd1`が収載した`2026-08-06_reserveimage_cycle2_f2_red_to_green_confirmed_55ba5a7_a4.md`
§5-2は「Ledger B層外gap=6file/★15箇所★」と記しており、★訂正後の11箇所を反映していない★。

★原因（当職の落度）★: 当該票は訂正便(5460a02の元原稿)と並行して執筆しており、
提出直前に「測定対象sha」の再確認は行ったが、★自票が引用する他票の最新値までは
再確認していなかった★（下命①以前の作法=sha欄の一致のみを見て、引用内容の陳腐化は見ていなかった）。

★訂正★: 現在の正本値は★6file/11箇所★（`5460a02`§2・§3）。`f1bcfd1`収載票は上書きせず、
本便を訂正便として提出する（当隊の条=同idの上書き禁）。

## §4 自己発見②：★`5460a02`のsupersedes欄がpath/sha取り違え★

`5460a02`収載票`…CORRECTION_gap11_a4.md`冒頭は以下のように記す:
```
supersedes= docs/incident_logs/2026-08-06_reserveimage_cycle2_ledger_ab_full_population_verdict_a4.md
（commit`79b13be`収載・sha256=475f689bc770a1407124e6bfb9f2d5c0d927742dfaba34ab7f89bf0edb04a5d5）
```
★実測で path と sha256 の対応を検めた★:
```
$ git show 79b13be --stat | grep staged
staged=docs/incident_logs/2026-08-06_reserveimage_cycle2_ledger_ab_final_verify_596c87e_a4.md
  158行 sha256=475f689bc770a1407124e6bfb9f2d5c0d927742dfaba34ab7f89bf0edb04a5d5

$ sha256sum docs/incident_logs/2026-08-06_reserveimage_cycle2_ledger_ab_full_population_verdict_a4.md \
             docs/incident_logs/2026-08-06_reserveimage_cycle2_ledger_ab_final_verify_596c87e_a4.md
41d803f068e3c1ea694e29df303b84bf13e6217b203e071d208102bf61f24439  …_full_population_verdict_a4.md
475f689bc770a1407124e6bfb9f2d5c0d927742dfaba34ab7f89bf0edb04a5d5  …_final_verify_596c87e_a4.md
```
★sha256=475f689b…は`…_final_verify_596c87e_a4.md`の物であり、`…_full_population_verdict_a4.md`
の物ではない（後者のsha256は41d803f0…）★。`5460a02`のsupersedes欄はpathとshaを取り違えている。

★併せて判明した事実★: `…_full_population_verdict_a4.md`（当職が16:14に書いた15箇所版の草稿）は
★一度もcommitされていない★（現在も`??`のuntrackedのまま working tree に存在）。
∴ 正しいsupersedes連鎖は:
```
…_final_verify_596c87e_a4.md（79b13be収載・sha256=475f689b…）
  → superseded by → …_CORRECTION_gap11_a4.md（5460a02収載）
```
であり、`…_full_population_verdict_a4.md`は★別系統の未収載草稿★（内容は最終的に
CORRECTION票と同じ結論=11箇所側へ収斂したが、supersedes関係としては一度も正式に鎖へ入っていない）。
当職はこの草稿ファイルを削除する権限を持たぬ役割（read-onlyでなく本件は当職の成果物だが、
untracked fileの取り扱いは家老second殿の裁定を仰ぐ）ため、本便での指摘に留める。

★これは下命①が求める「path+blob shaでの引用」の実践においても、★機械の出力でpathとshaの
対応そのものを検めねば取り違えが起き得る★事の実例であり、当職は以後 supersedes欄を書く際
`git show <sha>:<path>`または`git show <commit> --stat`で★対応を機械に出させてから★記す。

## §5 ⑵の状況確認

`f1bcfd1`（軍師second PASS 16:27:48・根=test_41同一oracle RED→GREEN独立再測）により
★⑵は已に満★と承知。当職からの追加作業なし。

## §6 現状（下命⑤・待機はblockedに非ず）

- a1殿の47b根治（audit log欠落・同transaction化またはoutbox化）を待機中。当職は実装に手を付けず。
- RED oracle（test_47b）は当職の木で★其のまま保持★（§0確認どおり55ba5a7断面から不変）。
- a1殿の修正完了後、最終統合HEADで独立再走する（順序厳守=下命④の作法を継続）。
- 本待機は blocked に非ず（karo-second殿の板書どおり）。

## §7 禁則遵守

読取＋自票執筆のみ・実装ファイル一字も変更せず。git show / sha256sum / grep の読取コマンドのみ実行。
push/PR/main/本番=一切なし。queue/*の行数/sha引用なし（下命①順守）。

★札★
```
$ date -Iseconds
2026-08-06T16:39:23+09:00
```
