# senmu_desktop_route_watcher.py 型④(在るが誰も使わぬ)是正 (足軽2号、2026-08-06・家老second下命 msg_20260806_002057_340822ac)

測時=2026-08-06T00:32:46+0900 (`date -Iseconds`実行結果)。対象file sha256=`21e712c958ce89c99a75fbb2c560b9218f9475b4c0c668b4a7c13ac7e0c86eb7`(126行、本是正適用後)。

## 母集団・探索範囲(明記)

対象=`shim/hakudokai/senmu_desktop_route_watcher.py` 1file。検査=`/usr/bin/grep -rn`で
`box_held`/`return_to_sender_required`/`return_reason`/`return_event_key`/`preflight_blocks`/
`terminal_reason`/`database_ack_written`の7語を`.py`/`.sh`/`.md`/`.yaml`/`.yml`全体(git ignore無視の
filesystem grep、`grep-git-grep-silently-skip-gitignored`教訓に倣う)で実測。

## ①受命範囲=4field・実測では6field (件数の食い違い・訂正)

家老second下命は「box_held / return_to_sender_required / return_reason / return_event_key」の4field。
実測すると同じ`record.update`ブロック内に**もう2件**、同型(定義1箇所・消費0箇所)の書込専用fieldが
在った:
- `preflight_blocks` (L87相当・カウンタ)
- `terminal_reason` (L89相当・`status=='terminal_isolated'`の時のみ)

∴ 母集団を4→6へ訂正して報告する(下命の数をそのまま信じず実測で数え直した)。

## ②消費者0件の実測根拠

上記7語のうち`database_ack_written`のみ**定義箇所1(record組立)+送出箇所1(旧print文)**で、
他6語は**定義箇所1のみ**(旧コード時点)。repo全体grep(shim/hakudokai全47file・scripts全36file・
queue/inbox含む)で読出側=0件。健全対照として`status`/`next_retry_epoch`/`attempts`はL74-77で
実際に消費されている事を確認済(型④ではない)。

## ③★live 実測=仮説ではなく現に起きている★ (最重要)

ローカル state file (`~/.cache/dentalbi_senmu_desktop_route/inbound.json`)を実読した所、
**box_held=True の行が現に10件**存在した(測時 2026-08-06T00:30:xx時点、pid=853260の稼働プロセスが
書いた実データ):

| seq | status | attempts | preflight_blocks | updated_at |
|---|---|---|---|---|
| 139593 | queued_unrung | 0 | **571** | 2026-08-05T09:45:12+0900 |
| 140219 | terminal_isolated | 3 | 3 | 2026-08-05T12:13:33+0900 |
| 140298 | queued_unrung | 1 | 1 | 2026-08-05T12:25:48+0900 |
| 140989 | terminal_isolated | 3 | 3 | 2026-08-05T14:05:07+0900 |
| 141727 | terminal_isolated | 3 | 3 | 2026-08-05T16:00:29+0900 |
| 141800 | terminal_isolated | 3 | 3 | 2026-08-05T16:11:43+0900 |
| 141914 | terminal_isolated | 3 | 3 | 2026-08-05T16:29:06+0900 |
| 142272 | terminal_isolated | 3 | 3 | 2026-08-05T17:15:43+0900 |
| 142761 | terminal_isolated | 3 | 3 | 2026-08-05T18:07:43+0900 |
| 142900 | terminal_isolated | 3 | 3 | 2026-08-05T18:18:09+0900 |

**seq=139593の`preflight_blocks=571`は、`queue/inbox/honbucho.yaml`(委員長→本部長、2026-08-05T10:27:19)が
言及する「★571回の再発だけは絶対に許されぬ★」の571と一致**(数値の一致のみ実測・因果は断定せず)。
∴ 本file (`senmu_desktop_route_watcher.py`)は、委員長・本部長間で協議されていた対象と**同一と見て
矛盾しない**(既存diffに`EXPECTED_TITLE_SHA256`等、当該協議で言及された修正が既に含まれている事も
傍証)。断定はせず「矛盾しない」に留める(第四値の扱い)。

**未解決の継続**: process (`last_poll_status=ok`・測時直近poll=2026-08-06T00:30:41+0900)は生存・正常
poll中だが、上記10件は**測時点でなお`box_held=True`のまま**。最新のheld更新(142900)から測時まで
**約6時間**新規blockが記録されていない(新規到着0件か、既存10件が全て`terminal_isolated`/
`queued_unrung`のスキップ条件でre-processingされていないかは本工区の範囲外・未検証)。

## ④決定=「送り返す機構を実際に作る」か「書込を落とす」か

**下命は二択、当職は★第三の道★を選んだ。理由を以下に記す(Critical Thinking Rule・代替案提示)。**

**選ばなかった理由**:
- **(A) 実際にDB書込で送り返す機構を作る**=`pc_handshake`への新規INSERTが要る。しかし
  ①本fileの docstring 自身が明記=「No database ACK is written here; visible proof remains the
  completion gate」— DB ACKを書かぬ設計を明示的に選んでおり、新規INSERTは自己矛盾する。
  ②新規送信経路は本セッションの先例(W25=`karo_second_send_iincho.sh`)が示す通り、
  ★canonical envelope固定 + sb_auth.sh source + live POST許可の別途上申★ が要る重い工程であり、
  本下命はそこまでの権限委任を明示していない。③委員長↔本部長の協議(§③)は本file(または極めて
  近い設計)を対象に**既に進行中**と見られ、当職が独自にDB書込機構を作れば**二重実装**の危険がある
  (Anti-Duplication)。
- **(B) 書込を落とす(削除する)**=§③の通り、この6fieldは**単なる死んだ変数ではなく、
  委員長が「静かに捨てぬ形になっている」と★名指しで評価した設計要素と一致する可能性が高い★
  (571の数値一致)。削除は、上位の裁定が固まる前に評価済み設計を消す事になり、不可逆的に近い
  (git履歴には残るが、次に読む者が「削除された」を「不要と判断された」と誤読する危険)。

**選んだ道 (C)**: 6fieldの★書込は変えず★、本file自身が定める「visible proof=完了ゲート」の経路
(=標準出力・現に`/tmp/senmu_desktop_inbound_watcher.log`へredirectされ稼働中)へ、この6fieldを
**新たに合流**させた。従来の print 文はこれらを一切含んでおらず、たとえ人間が`tail -f`しても
`box_held`状態は見えなかった(state fileにしか無かった)。∴ これは「消費者を作る」の**最小・
可逆・無認可で完結する**部分実装であり、★真の意味での「送り主(from_pc)へ通知する」機構ではない★
(それは(A)の射程であり、本工区の権限外)。

## ⑤実装内容 (file差分)

`inbound_once()`内、`record`組立と旧print文を統合=`hold_fields`という中間dictへ切り出し、
`record`(local state永続化用)と`log_line`(stdout=完了ゲート用)の両方へ同じ内容を反映。
status='queued_unrung'/'terminal_isolated'以外(通常成功=`pending_visual`等)ではhold_fieldsは
空のままゆえ、print出力は従来通り変化なし(regression無き事を後述の負テストで確認)。

## ⑥負テスト (3形・3/3 PASS・実行済)

`python3 -m py_compile`構文確認PASS。加えて`fetch`/`trigger`をmonkeypatchしたsandbox実行
(scratchpad、repoへ未追加・live Supabase接続なし)で3形実測:
- CASE_A: actuator_status=`blocked_task_title`→status=`queued_unrung`。print出力に
  `box_held`/`return_to_sender_required`/`return_reason`/`return_event_key`/`preflight_blocks`
  全5field ★出現確認★。
- CASE_B: 事前attempts=MAX_ATTEMPTS-1で同actuator_status→status=`terminal_isolated`。上記5field+
  `terminal_reason` ★出現確認★。
- CASE_C(健全回帰対照)=actuator_status=`fired`→status=`pending_visual`。上記6field
  ★全て非出現を確認★(従来の成功系print出力を壊しておらぬ事の実証)。
3/3 PASS。★live環境のprocess(pid=853260)には未適用★(commit/再起動は当職の権限外・下記参照)。

## 【本工区で己が直した誤り】

無し(実装は加算のみ・既存分岐条件/戻り値/state書込は無変更。CASE_Cで非破壊を実測確認)。

## 【この工区と対に成る他工区】

- `docs/incident_logs/2026-08-06_type4_dead_field_sweep_a6.md` (足軽6号、同日・
  `scripts/inbox_write.sh`等3fileの型④棚卸し。★shim/hakudokai/配下は明示的に未探索★と自己申告済
  ゆえ本工区と母集団が重複せず、対になる)。
- `queue/inbox/honbucho.yaml` idx23 (委員長→本部長、2026-08-05T10:27:19)= 本fileと同一設計を
  指すと見られる協議(§③の571一致)。★当職はこの協議の当事者ではなく、内容の裁定はしない★。

## KNOWLEDGE_GAP(判定不能・断定せず)

1. §③の委員長↔本部長協議が本file(または同一系統の別role file)そのものを指すか=**判定不能**
   (571の数値一致のみを根拠に「矛盾しない」と書いたが、同一の証明ではない)。
2. 10件のheld行のうち特にseq=139593(preflight_blocks=571・attempts=0)が、なぜ`attempts=0`のまま
   571回blockされ得たか=**未検証**(旧コード世代の残存data・別カウント経路の可能性等、複数の
   仮説が有り得るが本工区の範囲外につき断定せず)。
3. 6件の held 行が測時点でなお未解決だが、これを誰が・いつ解消すべきかの手順=**設計として不在**
   (真の「送り主へ返す」機構=(A)が実装されるまでは、box_heldは人間がstate file/logを直接見ない
   限り気付けない)。

## 【下命への回答=残数の明記】

★下命4field→実測6field。6件とも★書込は維持・削除0件★。★真の意味での「送り主へ返す」機構は
未実装のまま残る(0→0、進捗なし・意図的)★。★変わったのは「完了ゲート(stdout log)に6fieldが
初めて現れるようになった」の1点のみ★。

## 監査体制

★暫定二者制(軍師second + Gemini)。Codex leg 停止中(SAFETY裁定 seq132707)★。

## commit/push/live適用について

★本工区はfile編集のみ・commit/push/live process再起動は行っていない★(禁則の理解に基づく・
稼働中process pid=853230/853260/3759956/3760024への反映は再起動が要り、それは当職の権限外)。
稼働反映の要否・timingは家老second/委員長殿の判断を仰ぐ。

以上、型④是正 (box_held等6field) への応答。軍師secondへ直接提出する。
