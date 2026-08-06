# queue/reports/gunshi_report.yaml の変遷復元 — 消えた記録は在るか (足軽6号)

## 境・限界・未測 (冒頭)

工区=家老second msg_20260806_140058_de0637a1（2026-08-06T14:00:58）。読取のみ・GO不要・実装零・patch零・/mnt/c書込零。
対象=`queue/reports/gunshi_report.yaml`。裁定・断罪は書かぬ（材料のみ）。軍師secondを咎めぬ。

測時=2026-08-06T14:05:14+09:00（`date -Iseconds`実行結果）。git rev-parse HEAD=7bbf1f9c67ba8e5254a7c75bde716a76defe523b。

## 対象file自体の実測（家老secondの申告を写さず引き直した）

```
$ date -Iseconds
2026-08-06T14:01:51+09:00
$ wc -l queue/reports/gunshi_report.yaml
42 queue/reports/gunshi_report.yaml
$ sha256sum queue/reports/gunshi_report.yaml
21a99373828bfbc5e346d77b3db3fbd93fe54e30b102f6eb8467937418399957  queue/reports/gunshi_report.yaml
$ git check-ignore queue/reports/gunshi_report.yaml; echo "exit=$?"
queue/reports/gunshi_report.yaml
exit=0
$ git log --oneline -- queue/reports/gunshi_report.yaml | wc -l
0
```

家老secondの申告（42行／git無視対象／git log 0）と一致。独立再測で崩れず。

★但し一点、家老secondの申告に無い測定★：ファイル内容の`timestamp:`欄と、OSのmtimeとを突き合わせた。

```
$ grep -n "^timestamp:" queue/reports/gunshi_report.yaml
4:timestamp: "2026-08-06T14:04:20+09:00"
$ stat -c '%y (mtime) / %Y (epoch)' queue/reports/gunshi_report.yaml
2026-08-06 13:52:52.576753465 +0900 (mtime) / 1785991972 (epoch)
```

内容欄の`timestamp:`（14:04:20）と、OSのmtime（13:52:52）とが★約11分28秒★食い違っておる。これは
★値と出所は別の述語★の一例として測ったのみで、原因は未測（script内部の生成時刻埋込みの仕組み次第。
軍師secondの実装を読めば分かる可能性が高いが、本工区の範囲外＝実装を読んでの断定は為さず）。
以後の㈡表の「刻」は、★便（message）の`timestamp`フィールド★を用いる（ファイル内容欄でもmtimeでもない、
第三の時刻軸である事に注意）。

## ㈠ 母集団を先に数える（命令の出力をそのまま貼る。head不使用）

```
$ find queue/inbox -maxdepth 1 -type f -name "*.yaml" | wc -l
31
$ find queue/inbox/_archive -type f | wc -l
17
```

（`_archive`の17件中2件は非message file＝`README.md`・`_prune_events.log`。残り15件が`*_pruned.yaml`。）

`queue`は`.gitignore`対象ゆえ、`git grep`・ラップされた`grep`は黙って飛ばす（既知の欠陥）。★`/usr/bin/grep -r`を使用★。

```
$ /usr/bin/grep -rl "gunshi_report" queue/inbox/ | sort
queue/inbox/_archive/karo-second_pruned.yaml
queue/inbox/_archive/shogun-second_pruned.yaml
queue/inbox/ashigaru5.yaml
queue/inbox/ashigaru6.yaml
queue/inbox/gunshi-second.yaml
queue/inbox/karo-second.yaml
$ /usr/bin/grep -rl "gunshi_report" queue/inbox/ | wc -l
6
```

この`grep -rl`は`queue/inbox/`配下★全体（_archive含む・全agent含む）★を再帰探索した一回の命令であり、
上記6件が「`gunshi_report`という文字列を一度でも含む file」の★全数★である（他の24件のトップレベルyaml、
13件の`*_pruned.yaml`は文字列すら含まぬ＝0件、母集団から漏れなく確認済）。

`_archive`は multi-doc YAML ゆえ`yaml.safe_load`では読めぬ（既知の欠陥）。★`yaml.safe_load_all`を使用★。
6件をPythonで`safe_load_all`し、`content`欄に文字列として現れる message 総数と、その中で
「`gunshi_report.yaml`」を含む message 数を数えた：

```
TOTAL_MESSAGES_SCANNED=3084
HITS(contains "gunshi_report")=102
```

この102件のうち、★ledger自身の行数+sha256を同便内で引いている★もの（正規表現
`gunshi_report\.yaml[^\n]{0,40}?(\d+)\s*行[^\n]{0,80}?sha256[=:]?\s*([0-9a-f]{8,64}|TO_FILL)`で抽出）が
本工区の核心データとなる：

```
RAW_MATCH_COUNT=67
```

内訳（source file別）：`_archive/karo-second_pruned.yaml`=84件中の大半、`karo-second.yaml`=11件中の大半
（102件中の残り35件は「参照した正本:」欄の単なる path 列挙で、ledger自身の行数+shaを引いていない＝
別成果物の行数+shaを引いている等）。`_archive/shogun-second_pruned.yaml`・`ashigaru5.yaml`・
`ashigaru6.yaml`・`gunshi-second.yaml`の4件は、いずれも★家老secondがledgerについて論じた便★であり、
軍師second自身のledger断面citationではない（新規断面データ無し、確認済）。

## ㈡ 断面の一覧（刻・行数・sha16、家老secondの箱＝karo-second.yaml+_archive両方から復元）

67件の(便timestamp, 行数, sha)組は★完全に重複無し★（`UNIQUE_TS_LINES_SHA_COMBOS=67`、畳んだ数=0）。
以下、時系列順（sha256の先頭16桁のみ表示。`TO_FILL`はsha256欄が未記入だった便＝後述）：

```
2026-08-04T18:10:54  172行  sha16=9f0b732c18e60b46
2026-08-06T09:15:35   49行  sha16=279759a2de79c7c4  <== 減 172→49 (Δ=-123)
2026-08-06T09:16:55   50行  sha16=6dedde34d6a138a5
2026-08-06T09:21:28   50行  sha16=1e5ad49b7f1c8be0
2026-08-06T09:21:38   50行  sha16=95c7cee30526d618
2026-08-06T09:31:35   49行  sha16=c30b43d00bd8bb53  <== 減 50→49 (Δ=-1)
2026-08-06T09:37:36   49行  sha16=780d56993831bcbe
2026-08-06T09:44:43   50行  sha16=1b87c0c50e85dbd1
2026-08-06T09:56:23   48行  sha16=93ae5138e63c531b  <== 減 50→48 (Δ=-2)
2026-08-06T10:00:35   51行  sha16=bdcb82753c438370
2026-08-06T10:04:18   47行  sha16=3972b127e09ba366  <== 減 51→47 (Δ=-4)
2026-08-06T10:10:45   47行  sha16=37c6c7277e009037
2026-08-06T10:12:08   48行  sha16=de7536b5103b90a2
2026-08-06T10:19:23   48行  sha16=7c4bd0fd9e4b75f3
2026-08-06T10:22:04   46行  sha16=d039c376f30704a0  <== 減 48→46 (Δ=-2)
2026-08-06T10:26:27   49行  sha16=a04e4599c6e07e64
2026-08-06T10:29:17   49行  sha16=a04e4599c6e07e64
2026-08-06T10:30:45   47行  sha16=a309754ab33dd824  <== 減 49→47 (Δ=-2)
2026-08-06T10:32:32   50行  sha16=98d9f09ded58f3d2
2026-08-06T10:39:46   50行  sha16=703590152ec9afff
2026-08-06T10:44:22   50行  sha16=b165d27131a72034
2026-08-06T10:48:11   48行  sha16=c8ecdcf6b3bb19de  <== 減 50→48 (Δ=-2)
2026-08-06T10:56:09   42行  sha16=1e69685527f21b7f  <== 減 48→42 (Δ=-6)
2026-08-06T11:04:37   43行  sha16=d0f4c79c760f3e14
2026-08-06T11:06:54   46行  sha16=33b8a3bbbba3d721
2026-08-06T11:11:36   45行  sha16=856866c3d4abd5b2  <== 減 46→45 (Δ=-1)
2026-08-06T11:15:34   44行  sha16=231264e77c089938  <== 減 45→44 (Δ=-1)
2026-08-06T11:25:08   45行  sha16=fcc6265f1fda0d58
2026-08-06T11:29:17   44行  sha16=2e4a4edb32efd7c1  <== 減 45→44 (Δ=-1)
2026-08-06T11:36:43   44行  sha16=e1350cbfafa14c32
2026-08-06T11:37:02   44行  sha16=e1350cbfafa14c32
2026-08-06T11:40:12   44行  sha16=90f51bb04a2c4ee5
2026-08-06T11:40:26   43行  sha16=986c89f78d3284b4  <== 減 44→43 (Δ=-1)
2026-08-06T11:45:55   44行  sha16=273b604d0a97bc64
2026-08-06T11:46:08   44行  sha16=911392ad66f8fda0
2026-08-06T11:48:23   44行  sha16=6f7e0e1b6f31cd5f
2026-08-06T11:48:35   43行  sha16=06734c7c7efcb255  <== 減 44→43 (Δ=-1)
2026-08-06T11:51:21   44行  sha16=0b7a02ff25463ea7
2026-08-06T11:51:44   44行  sha16=3fa6602f06ba1ea9
2026-08-06T11:54:34   45行  sha16=b1940ea7cc2b5688
2026-08-06T11:54:55   44行  sha16=ce821a8bede434f9  <== 減 45→44 (Δ=-1)
2026-08-06T12:02:32   44行  sha16=TO_FILL
2026-08-06T12:02:56   44行  sha16=1f00aca78d28334f
2026-08-06T12:06:09   44行  sha16=TO_FILL
2026-08-06T12:16:40   50行  sha16=TO_FILL
2026-08-06T12:16:57   46行  sha16=c7298fd5d7183ef7  <== 減 50→46 (Δ=-4)
2026-08-06T12:32:53   46行  sha16=TO_FILL
2026-08-06T12:33:22   46行  sha16=6c52429bf06182bd
2026-08-06T12:35:12   46行  sha16=TO_FILL
2026-08-06T12:35:41   46行  sha16=6c0c2e7da05eaeb1
2026-08-06T12:38:03   47行  sha16=TO_FILL
2026-08-06T12:38:30   49行  sha16=edc3ace8a066621f
2026-08-06T12:44:46   46行  sha16=f22f6dc26a87ee5d  <== 減 49→46 (Δ=-3)
2026-08-06T12:45:10   54行  sha16=30df289a064c81e5
2026-08-06T12:48:14   46行  sha16=4a1dcbf2e64d26c1  <== 減 54→46 (Δ=-8)
2026-08-06T12:48:27   47行  sha16=59bae3292f635dc6
2026-08-06T12:53:15   47行  sha16=6bb3b41958877342
2026-08-06T12:59:17   46行  sha16=26f39bf2bba611ca  <== 減 47→46 (Δ=-1)
2026-08-06T13:04:48   47行  sha16=998ec5fa1ded77c9
2026-08-06T13:13:21   46行  sha16=fd953cd0e619f8d8  <== 減 47→46 (Δ=-1)
2026-08-06T13:19:59   46行  sha16=ee492ed7a40e98ad
2026-08-06T13:32:30   50行  sha16=500399e0e1e6862b
2026-08-06T13:33:27   48行  sha16=342d24acd03ef42a  <== 減 50→48 (Δ=-2)
2026-08-06T13:34:56   48行  sha16=9c8c0368048ac43f
2026-08-06T13:40:13   48行  sha16=c8d486d81f0d03e2
2026-08-06T13:45:57   48行  sha16=219f4cdbfeaa68b8
2026-08-06T13:53:12   44行  sha16=3e6b1c4c44268784  <== 減 48→44 (Δ=-4)
```

（末尾13:53:12＝44行は、家老secondの新工区便（14:00:58）内で「軍師secondが13:53の便で44行と申告」と
記された値と一致——家老secondの申告を★引き直して裏取り★できた形。）

## ㈢ 行数が減った箇所（本工区の核）

上表から機械抽出、★減少イベント=21件★（2026-08-04〜08-06の全期間、`67`断面中）：

```
DECREASE_COUNT=21
('2026-08-06T09:15:35', 172, 49)   Δ=-123（前日18:10からの最大の落差。ただし間の断面が箱に無い＝引き直せぬ）
('2026-08-06T09:31:35', 50, 49)    Δ=-1
('2026-08-06T09:56:23', 50, 48)    Δ=-2
('2026-08-06T10:04:18', 51, 47)    Δ=-4
('2026-08-06T10:22:04', 48, 46)    Δ=-2
('2026-08-06T10:30:45', 49, 47)    Δ=-2
('2026-08-06T10:48:11', 50, 48)    Δ=-2
('2026-08-06T10:56:09', 48, 42)    Δ=-6
('2026-08-06T11:11:36', 46, 45)    Δ=-1
('2026-08-06T11:15:34', 45, 44)    Δ=-1
('2026-08-06T11:29:17', 45, 44)    Δ=-1
('2026-08-06T11:40:26', 44, 43)    Δ=-1
('2026-08-06T11:48:35', 44, 43)    Δ=-1
('2026-08-06T11:54:55', 45, 44)    Δ=-1
('2026-08-06T12:16:57', 50, 46)    Δ=-4
('2026-08-06T12:44:46', 49, 46)    Δ=-3
('2026-08-06T12:48:14', 54, 46)    Δ=-8
('2026-08-06T12:59:17', 47, 46)    Δ=-1
('2026-08-06T13:13:21', 47, 46)    Δ=-1
('2026-08-06T13:33:27', 50, 48)    Δ=-2
('2026-08-06T13:53:12', 48, 44)    Δ=-4
```

減少の合計＝172行分の「入れ替わり」を含めれば -175行、前日分（172→49の-123）を除いた本日単独の
減少合計は -52行（=21件中20件、本日分のみ）。ただし★これは「その断面の間に何行減ったか」という★数★
のみであり、★どの行が消えたか（内容）は sha256 という一方向hashからは復元不能★（後述㈤）。

一件、家老secondの便（msg_20260806_121657_5e5835dc、12:16:57）自身が「先便（12:16:40）は ledger 行数が
stale ゆえ supersedes として訂正する」と★明記★しておった——これは「行が消えた」のではなく「先の便自体が
誤った断面値を報じ、後便で訂正された」事例である。ただし★YAML構造上の`supersedes`欄はこの便にも
`null`のままで、訂正は本文prose上のみに存在し、機構的な訂正マーカーは付いていない★（家老second/karo-second.yaml
両fileを対象idで突き合わせ実測、該当id 67件全てで`supersedes: null`または欄自体が無い事を確認）。

## ㈣ 今の42行を全数読み、内容を要約

読時=2026-08-06T14:05:14+09:00。読時点のsha256=21a99373828bfbc5e346d77b3db3fbd93fe54e30b102f6eb8467937418399957
（読前後で再測、変化無し確認済）。

現行42行の内容：`worker_id: gunshi-second`、`task_id: subtask_gunshi_audit_premise_sweep_a5_gunshi_20260806`、
`parent_cmd: cmd_secondpc_canon_cure_20260803`。`timestamp: "2026-08-06T14:04:20+09:00"`（前掲の通り、
OSのmtime 13:52:52 と約11分28秒の差あり）。`status: done`。`result.type: evaluation`、
`summary`＝足軽5号の「軍師second監査帳PASS前提未検め掃き」を監査しPASSと裁いた旨（母集団三階を
混ぜずに出し、手読み6件と残りUNMEASUREDを分けた点を評価）。`verdict: PASS`。`evidence.report_path`＝
`queue/reports/gunshi_second_gunshi_audit_premise_sweep_audit_20260806.md`、`audited_target`＝
`ashigaru5 report_received msg_20260806_135147_b9ac0047`。`checks`3件＝①対象正本233行sha256=df9b46d7...
で申告一致、②母集団をA階=監査票file366件／B階=ledger46行／C階=inbox294通に分け合算しないと宣言、
③既知2件はcommit実在まで戻し新規4件を㈠在り1/㈢判じ得ぬ2/該当せぬ1に分けた旨。`advisory`1件＝
次段でhas_marker側318件へ広げる際は別heuristicを並走せよ、との助言。`next_safe_action`＝karo-secondへ
PASSを返し当該便を既読化する旨。`north_star_alignment.status: aligned`（確定分と未測を混ぜず過大断定を
避けた旨）。`skill_candidate.found: false`。

★注記★：この現行42行の内容自体は、上表㈡末尾（13:53:12、44行）から★さらに後の断面★（本文内`checks`欄の
`監査票file366件`等の記述からして、ashigaru5関連の新規監査サイクルが本工区着手中にも進行し続けている
ことが窺える）。ledgerはrolling台帳ゆえ、本報告の間にも書き換わり得るという当日中盤からの性質が
継続している事の実例。

## ㈤ 四値（本工区の核心的限界）

- ★UNMEASURED（己が測れる）★：無し。母集団・断面列挙・減少箇所・現行42行全読——本工区が求めた
  測定は全て実測完了。
- ★待ち（相手を待て）★：無し。他agentの応答待ちを要する項目は無かった。
- ★見得ぬ（権を求めよ）★：無し。queue/inbox/配下は足軽権限で全域閲覧可能であった（ledger自体への
  書込・削除権は求めていない＝読取のみの本工区に不要）。
- ★引き直せぬ（諦めて記せ）★：★これが本工区の核★。以下2点は構造的に復元不能：
  1. **便に断面が残らなかった時間帯の中身**：たとえば09:15:35の49行（前便18:10:54の172行から-123）の
     間、実際に何回ledgerが書き換わったか、どの内容が消えたかは、8/3 21:05:36以前（家老secondの箱＝
     `_archive/karo-second_pruned.yaml`の最古便）より前も含め、★便という媒体自体に記録が存在しない限り
     一切復元できない★。queue/inbox/全域を走査済（㈠）だが、"gunshi_report"を含む便は6file・67断面のみ
     であり、それ以外の瞬間のledger内容は原理的に失われている。
  2. **sha256は一方向hashゆえ、「何行減ったか」という★数★は分かっても「どの行が消えたか」という
     ★内容★は復元できない**。㈢で示した21件の減少イベントは全て「Δ行数」の実測にとどまり、
     消えた行の中身についての主張は一切為していない（為し得ない）。

## 数の突き合わせ（家老secondの申告値との差、判定は下さぬ）

家老secondの新工区便は「当職の箱に本日60の断面が残っており申した」と申告していた。本工区は
★写さず独立に測った★結果、以下の3通りの数を得た（いずれも本日=2026-08-06分のみ、`karo-second.yaml`+
`_archive/karo-second_pruned.yaml`の合算）：

```
TODAY_ONLY_RAW_CITATIONS=66
TODAY_ONLY_UNIQUE_(lines,sha)_PAIRS=62
TODAY_ONLY_UNIQUE_REAL_SHA(TO_FILL除く)=58
```

★件数と最大値は別の述語、値と出所も別の述語★の原則に従い、「60」に最も近いのは
UNIQUE_REAL_SHA=58だが、★どの数え方が家老secondの60と同一の述語かは未確認★。本工区の目的
（変遷復元・消失検知）にはこの差自体は影響しない（いずれの数え方でも21件の減少イベントは同一に
再現される）ため、これ以上の追跡は行わず、差を差のまま記す。

## TO_FILLについて（判定は下さず事実のみ）

67断面中6件で`sha256=TO_FILL`という値が便本文にそのまま記されていた（実sha256ではなくplaceholder
文字列）。該当便timestamp＝12:02:32／12:06:09／12:16:40／12:32:53／12:35:12／12:38:03の6件。
これらの断面は「行数は分かるがshaは不明（placeholderのまま送信された）」という第四値未満の状態で
あり、当該断面の内容同一性は検証不能（材料として提示のみ、原因の断定・軍師secondへの評価は行わず）。

## 出所

対象日=2026-08-06（一部前日2026-08-04分を含む）。population検索対象=`queue/inbox/`全域
（トップレベル31file＋`_archive/`17file、うち6fileが"gunshi_report"を含む）。安全に関する事項なし。
実装零・patch零・/mnt/c書込零・ledger自体への書込/削除零（読取のみ）。

以上、材料提示のみ。裁定・「rolling自体が良いか悪いか」の評価は含まぬ。
