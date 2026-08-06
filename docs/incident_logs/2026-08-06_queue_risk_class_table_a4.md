[足軽4号→家老second] queue/** risk級表 提出(本文・値・path・token・患者情報は一字も引かず、schema/key名/型/自由文可否のみで判定)

■0 母集団・除外
測時=2026-08-06T21:41:21+09:00／器=find(-type f 再帰)+python3(yaml.safe_load/json.load,key名のみ抽出・値は不出力)+wc -w+grep -c "^#"／範囲=queue/{inbox,tasks,reports,dead_letter,metrics,watchers,orders,packets,archive} 配下全ファイル／HEAD=08271dd(前後不変)。
除外(禁則により未openのまま)=queue/inbox/_dead_letter_second.yaml(glob明示除外)、queue/inbox/_archive内の legacy 3件(*_legacy_*、glob明示除外)。
参考=queue/inbox_v2 は存在するが今回の9分類の対象外・0ファイルにつき分析せず(隠さず記す)。

■1 subtree別 判定(全て型のみ・値未参照)
inbox(queue/inbox/*.yaml、除外2件): schema=messages[]配列、要素はcontent/from/id/read/timestamp/type/supersedes/expires_at。自由文欄=有(content)。患者/secret混入可能性=型では排除不可→高。機械数値のみ=否。保存期間候補=一言なら「短命(rotation運用)」寄りと言い得る根拠あり=cap到達で既読分を自動退避する挙動を本セッション中に自inboxで実観測(機構由来・値でなく挙動の観測)。但し決めるのは院長殿の権ゆえ「候補」に留める。

tasks(queue/tasks/*.yaml): schema=task直下にkey毎object、status/owner/report_to等の定型項目に加え複数のblock scalar自由記述欄(作業内容・禁則・理由等)を持つ。自由文欄=有(定型項目より多い)。患者/secret混入可能性=型では排除不可→高。機械数値のみ=否。保存期間候補=型のみでは一言で言えず(保留)。

reports(queue/reports/**、拡張子混在=sha256/json/md/yaml/log/diff/patched_reference/sh): 型が一様でないため型別に判定。
 - sha256: ハッシュ値+ファイル名の定型行のみ→自由文=無→機械生成の固定形式のみ→低。保存期間候補=監査証跡(ハッシュチェーン)の性質上「長」と型から言い得る。
 - json: 定義済keyが主だが自由記述key(例=状況説明用の欄)を持つ個体を確認→自由文=有→高。
 - yaml: 自由記述block(結果・報告等)を持つ→自由文=有→高。
 - md: マークダウン文書=型自体が自由記述用途→自由文=有→高。
 - log: 行単位の自由形式テキスト→自由文=有→高。
 - diff/patched_reference: コード差分の自由形式テキスト。型上は任意文字列を含み得るため排除不可→中〜高。
 - sh: シェルスクリプト本文(自由形式テキスト、型のみ確認・実行せず)→自由文=有→高。
 上記 sha256 以外は保存期間候補=一言では言えず(保留)。

dead_letter: queue/dead_letter/ 直下は現状0ファイル→型を観測できず=判らぬまま(第四値)。
 - _unroutable/: schema=content/from/reason/target/type/evidence等。自由文欄=有(content/reason/evidence)→高。
 - _pending_notice/: 現状0ファイル→型を観測できず=判らぬまま(第四値)。
 保存期間候補=いずれも一言では言えず(保留)。

metrics(queue/metrics/*.yaml): schema=agent_id/timestamp/unread_latency_sec/read_count/bytes_read/estimated_tokens。自由文欄=観測範囲内で無し。患者/secret混入可能性=数値・識別子欄のみで自由記述欄を持たぬため低い。機械数値のみ=概ね該当。保存期間候補=一言では言えず(保留)。

watchers(queue/watchers/*.health): schema=schema_version/agent_id/watcher_pid/version/alive/started_at/uptime_sec/last_action/last_seen_at/tui_capture_state/ready_for_clear/ready_for_dispatch/restart_count_24h。大半は真偽値・数値・時刻の定型欄。ただし last_action 1欄のみ、値を見ておらぬため自由文か定型短ラベルか型だけでは断定できず=判らぬまま(第四値)。それ以外は自由文なし→総合=低(ただしlast_action 1欄は未確定と明記)。保存期間候補=一言では言えず(保留)。

orders(queue/orders/*.md): マークダウン文書(発令書)=型自体が自由記述用途→自由文=有→高。患者/secret混入可能性=型では排除不可→高。保存期間候補=一言では言えず(保留)。

packets(queue/packets/*.md、現状1ファイルのみ=母集団が小さい事を明記): orders同型のマークダウン文書→自由文=有→高。保存期間候補=一言では言えず(保留)。

archive: 二箇所存在。⑴queue/archive/直下のyaml=messages[]配列、要素schemaはinboxと同一(content等の自由記述欄を含む)→自由文=有→高。⑵queue/inbox/_archive/配下のyaml(rotation退避先)=multi-doc(count/messages/pruned_at)、messages要素はinboxと同一schema→自由文=有→高。⑵のうち*_legacy_*3件は禁則により未openのまま=型未確認・判らぬまま(第四値、隠さず記す)。保存期間候補=一言では言えず(保留)。

■2 己の手で為した事
find -type fでsubtree別ファイル数を数えた／find+sed+uniqで拡張子内訳を得た／python3+yaml.safe_load・json.loadで代表fileのtop-level key名のみ抽出(printしたのはkeyリストのみ、値は変数に読んだが出力・保存せず)／.mdはwc -wで語数のみ、grep -c "^#"で見出し数のみ確認し本文は読まず／queue/inbox/_dead_letter_second.yamlとqueue/inbox/_archive内legacy3件はglobで明示除外し一度もopenせず／己の箱(queue/inbox/ashigaru4.yaml)の既読化はflock+id明示(msg_20260806_213633_e19adc1c/msg_20260806_213633_cap_rotated/msg_20260806_213831_851d0f99の3件個別指定、read:falseの一括潰しはせず)。

■3 判らぬまま(第四値)一覧(隠さず列挙)
dead_letter直下(0ファイル)／dead_letter/_pending_notice(0ファイル)／watchers.health の last_action欄の自由文可否／queue/inbox/_archive内legacy 3件の型。

以上。
