# 台帳大掃除 分類表 v1 — task_tracker未完了125件 + design_decisions非final 53件

- 発令: seq130897(委員長、理事長指示2026-07-20)。work_started=seq130898。
- 実施: 将軍main 2026-07-20。**読み取り専用**(task_tracker/design_decisionsへのUPDATE・completed化は一切なし)。
- 分類定義: **A**=生きている(振興管理へ) / **B**=現行レーンへ吸収(吸収先明記) / **C**=廃止候補(理由) / **D**=既に実質完了(証拠)。
- 判定原則: AI正直5箇条準拠。D判定は行内証跡または当職の一次証跡がある場合のみ。証跡が「green待ちのみ」の行はD候補として裁定表へ(AUDIT-GREEN-TRUTHトリガ考慮)。C確定・D確定の反映は理事長裁定後の一括作業とし本書では分類のみ。

## 0. 集計

| 分類 | task_tracker | design_decisions | 計 |
|---|---|---|---|
| A 生きている | 43 | 27 | 70 |
| B 吸収 | 12 | 3 | 15 |
| C 廃止候補 | 50 | 5 | 55 |
| D 実質完了 | 20 | 18 | 38 |
| 計 | 125 | 53 | 178 |

現行主力6親レーン(008df0d0/1f583fa6/fb66b73b/aa2e84b3/bfbde76c/56379a3f)は全てA。未完了125件の約56%(C+D)が4-5月旧体制の残骸で、台帳ノイズの主因。

## 1. task_tracker 分類表(125件)

### 1.1 abandoned 11件 → 全てC(正式廃止の裁定を求める)
| id | 件名(短縮) | 分類 | 理由 |
|---|---|---|---|
| 50949c50 | DD-070 Phase2 DB層E2E | C | DD-070健全化構想は4月体制で停止。後継なし |
| c40b90f7 | ekarte-v3 code-audit初回試運転 | C | ekarte-v3は旧世代(現正史=V6 EkarteV6Layout)。試運転目的も達成済 |
| 14f7bd36 | DR-7.10 v1.1再監査 | C | 旧監査体制(コーちゃん宛handshake)。監査標準はCodex+Hermesへ改定済(正本85b541b5§8) |
| 7068dfa8 | Stop Hook一時退避復元 | C | Phase5 override前提の一時タスク。現行hook体制で意味喪失 |
| ebfe81f9 | DD-134 v1.2修正案 | C | DD-134系は旧ekarte-v3前提。§1.3参照(designing 3件と一括廃止裁定) |
| 36bd5f11 | OpenClaw実態調査Stage1 | C | 調査目的はDD-142(OpenClaw統合)起草時点で消化。レセコン停止lane付随 |
| d20f535c | さくら本物監査72hタイマー | C | 監督タイマー期限到過・旧愛称体制(DD-162で上書き) |
| fd10db2d | fukuincho_desktop_poke完成 | C | 副院長desktop自動poke構想。現行はwatcher/dispatcher+pane直伝体制で代替 |
| fc419890 | 同 段階3実装適用 | C | 同上 |
| 3e4046cf | fukuincho自動ループGAP-2 | C | 同上 |
| ed5b6137 | 着火台帳+期限超過自動催促 | C | 同構想族。趣旨はALL-INBOX-SWEEP/ALL-BLOCKED-MUST-ESCALATE規則(07-19理事長令)が規範側で吸収 |

### 1.2 blocked 38件
| id | 件名(短縮) | 分類 | 理由/吸収先/証拠 |
|---|---|---|---|
| b0cef740 | DD-054 PhaseA ID体系統一 | A | DB整合性正史(patient_no統一)は現役課題。T10/T12と統合管理を提案 |
| 3b4b3b9b | DD-067 squashパターンX | C | 4月のmigration squash構想。以降の運用で前提陳腐化。裁定表 |
| eb645a15 | DD-091 Stage1 DDL本番適用 | C | 理事長保留(04-19)のまま3ヶ月。再上程なしなら廃止。裁定表 |
| 95a4370b | DD-091 72hモニタ | C | 上と連動(適用しないなら不要) |
| 92af0a72 | DD-091 kuroda指示改訂 | C | 同族+旧愛称体制 |
| 6e7b46ec | DR-7.9 PhaseB notify-urgent | **D** | blocker欄自認「DD-127 Phase Dで再実装済(LINE優先+event駆動)」 |
| 4b66c94e | T12 旧patient_id列最終整理 | A | 生きている(案+ローカル検証済・GO待ち)。裁定表(D-lane) |
| 7055f6b9 | T11 DD-087履歴トリガ | A | draft+local verify完了済(seq115376)。series-split要否の裁定待ち。裁定表 |
| 424f36a9 | T10 FK未付与30本 | A | DB整合性正史。D-lane DDL裁定待ち。裁定表 |
| c302ee9d | T14 Pediatricモード | **B** | 吸収先=**1f583fa6(患者アプリ統合改良)**。小児特化はP0-2/P1恐竜レーンが正史 |
| b2b21dcb | DD-066×StopHook役割分担 | C | 旧監査体制文書。draft止まり3ヶ月 |
| c0c7d72c | 副院長保留-4 claude.exe削除 | C | DD-138旧体制(段階3)従属。§1.2 DD-138群と一括裁定 |
| 29236fb2 | 副院長保留-3 source_code_cache同期 | **D** | 同期失敗の根治=f46d46a9(バッチ全滅欠陥修正、相談役PASS seq129664+PR#53 merge) |
| 1a41b982 | 副院長保留-5 Stage3残作業 | C | DD-138従属(Downloads削除+stash drop、旧環境前提) |
| 7ac7d0ba | 副院長保留-2 claude.exe削除案C | C | 同上 |
| 3e7cc47d | 副院長保留-1 Z26件削除GO | C | 同上+旧愛称体制 |
| ff259f8e | BI⇔Quartetto Stage2 | C(凍結) | レセコン停止指示(07-15理事長)対象lane。再開裁定に従属。裁定表 |
| ad3eaf92 | 同 Stage5 SaaS外販 | C(凍結) | 同上(Stage4+1年安定が前提の遠未来) |
| d27af58d | 同 Stage4 7医院展開 | C(凍結) | 同上 |
| 2a04506b | 同 Stage3 試験運用 | C(凍結) | 同上 |
| 0e8e1fb0 | 抜け11 議事録参照導線 | C | gunshi PASS済のdraft。onboarding組込は現行CLAUDE.mdスリム化(cb860c4d)が上位互換。裁定表 |
| 9fbeb5a4 | 抜け12 OSSライセンス担当 | A | コンプラ実義務(MIT/Apache表示)。担当者決定のみ残。小粒 |
| aa2798c3 | 抜け13 先行着手可明文化 | C | 規範側はALL-BLOCKED-MUST-ESCALATE等の新規則が実質カバー |
| bb31269c | スマホpermission承認 | A | 理事長「予定」発言あり。方式X/Y選定の裁定待ち。裁定表 |
| d476c1e1 | 不正積み上げDB段階3+4 | A | 残3項目=副医院長フック/過去ログ再分類/DD記録、各owner待ち(07-11棚卸し済) |
| 6423cea3 | 画像3者PDCA DB層 | **B** | 吸収先=**008df0d0(画像管理親)**。003_asset_fk_hardening適用はDD-179残15%と同梱 |
| 7460e8fd | P0 1症例UI土台(DD-173) | **B** | 吸収先=**56379a3f(見本カルテ11枚)**。W2 pivot+canon 444f97bf切替済(当職メモリ+行内記録一致) |
| ae83f22e | pane-state判定改修 | A | 監視層infra現役。947eb280監査後の順序待ち |
| 62bb8464 | gunshi-second Supabase復旧 | A | インフラ復旧現役(MCP config登録は完遂済・残=恒久確認) |
| d1065911 | compact自動発火 | A | third_pc側で進行中の現役infra |
| 75815b3a | ApoDent徹底分析 | **B** | 吸収先=**1f583fa6 P2(アプリ内予約動線)+予約担当部長担務**。理事長令の予約モジュール方針はweb-booking拡張へ確定済 |
| 30d0f370 | Apodent3解析残10件 | **B** | 同上(実機依存10件はU-3可否と共に予約レーンで処理) |
| bc7daeb5 | 確定ボタン%基準化 | A | 理事長裁定「一旦受入・いずれ修正」=V6レーンbacklogとして低優先で生存 |
| 55f99184 | Hermes独立検査seq68893 | **D** | 行内自認「実作業決着済(seq69103, 06-21)」。completed化のみaudit-green証跡要件で保留=裁定表(AUDIT-GREEN-TRUTH) |
| 2c645b8e | 自動ACK改修の監視 | C | Phase1完遂・Phase2 DDL取下げ後、G1やり直し放置1ヶ月。再開意思なければ廃止。裁定表 |
| 4db5b9ac | main Hermes監査環境復旧 | A | Dual Green第2leg欠は現役blocker(環境部長owner)。裁定表(ライセンス調達) |
| 48a90a8a | tmux copy-mode固着恒久対策 | A | 応急ガード稼働中・恒久策未了の現役infra |
| b5572878 | 経営BI open-decisions A/B | A | 理事長判断待ちの現役(aa2e84b3経営BI親と連動)。裁定表 |

### 1.3 designing 4件
| id | 件名 | 分類 | 理由 |
|---|---|---|---|
| 19f0fec8 | DD-134§6-1 JSONB DDL | C | DD-134系=ekarte-v3前提の旧世代。V6正史と不整合。裁定表(3件一括) |
| 4d0bf797 | DD-134§6-2 検知ルール | C | 同上 |
| 908d924a | DD-134§6-3〜5 features雛形 | C | 同上 |
| b13bf81f | image-p2ブランチ単独監査 | **B** | 吸収先=**008df0d0(画像管理親)**。指示書v1.3レーンの監査工程に統合 |

### 1.4 in_progress 25件
| id | 件名(短縮) | 分類 | 理由/吸収先/証拠 |
|---|---|---|---|
| 115d77eb | staff-auth+T15 RLS本番切替 | A | 認証・RLSは患者アプリP0-3上程と直結する現役。裁定表(DDL/RLS=GO必須) |
| f9fbf06d | baseline 39 TSエラー修復 | **D** | 行内自認「HEAD実測により1→0件に修復完了」 |
| 58d2e2ad | 申し送りaria-label | A(凍結注意) | 実作業=macレーン=stopped_by_user_order。裁定表(Mac停止laneの扱い) |
| 7a36ffb6 | Hermes T-A本番反映検証 | C | 06-20副院長desktop自動化族。現行体制(dispatcher+手動pane)で代替。裁定表(5件一括) |
| e841db83 | キルスイッチ3層+自動停止 | C | 同族 |
| a38a3564 | V6病名連動+定食+確定ボタン | A | V6現役レーン(RED要件訂正から再開) |
| 64ed6037 | Commander画像受領経路 | **D** | 行内自認「画像経路確定=案B」=設計目的達成。運用定着済 |
| e566b6db | T-A DB制約横展開監査 | C | 06-20族(三重ロック問題は把握済・体制側で解消) |
| 5ff0d3b9 | 上り送信割り込み防止 | C | 同族(fukuincho_desktop_poke系はabandoned 4件と同一構想) |
| 6d0af06f | V6グリッド開発タブ | A | V6現役(4037ec1fタブ配線工区と統合推奨) |
| 6bb4bba2 | 旧人格名→役職置換 | A | governance現役(gunshi REDO_REQUIREDから再開待ち) |
| 743088e1 | deferred放置一掃 | **B** | 吸収先=**本工区(seq130897台帳大掃除)**。目的同一 |
| 4e54f890 | mainテスト24件根治 | **D** | 行内自認「24件全件解消・PR#44/#45 merge済(相談役PASS)」 |
| ac046435 | PR-A 本流収容 | **D**候補 | merge完了・保全是正済。残=軍師green待ちのみ。裁定表(AUDIT-GREEN-TRUTH) |
| 75d04ac1 | .gitattributes導入 | **D** | 行内自認「監査PASS(seq124378)・PR#41 merge済」 |
| aa437254 | third skills links適用 | **D**候補 | 実装検証完了・軍師green待ちのみ。裁定表 |
| e4848816 | DD-191サーベイ実装 | A | 現役(v2実装済・進行中) |
| 5f274438 | 経営BI 28件PBIR修復 | A | 現役(研修課長レーン、M00再検収と連動) |
| 4cc72f25 | 管理者綱領repoミラー | A | 現役(PR#56作成済) |
| 008df0d0 | 【親】画像管理+患者送信 | A | 現行主力レーン(is_current指示書v1.3) |
| 1f583fa6 | 【親】患者アプリ統合改良 | A | 現行主力レーン(is_current v1.2。当職が設計6点提出済=seq130411) |
| fb66b73b | 【親】勤怠KOT×MF×BI | A | 現行主力レーン |
| aa2e84b3 | 【親】経営BI完成推進 | A | 現行主力レーン(M00再検収進行中) |
| bfbde76c | 【親】R7 113件逆引き検証 | A | 現行主力レーン(Phase1完了) |
| 56379a3f | 【親】見本カルテ11枚第1段階 | A | 現行主力レーン(計画書v1.0監査提出中) |

### 1.5 not_started 34件
| id | 件名(短縮) | 分類 | 理由/吸収先 |
|---|---|---|---|
| dceed06e | DD-054 PhaseB karteローダー | A | karte_visit_items(V6着地面)直結。V6正史下で再スコープ。裁定表 |
| 9f30de06 | T10 ZDR契約確認 | A | PIIコンプラ実義務(DD-061)。小粒・要担当指名 |
| a1506500 | T11 問診AI同意文言 | A | 同上 |
| 84f47aed | data_origin 5区分(10テーブルDDL) | C | 4月の大規模DDL構想。現行データ規律で代替。裁定表 |
| a9807a7f | DD-070 Phase3 | C | DD-070族(abandoned Phase2と一括) |
| cbc881d6 | DD-101 くろちゃん連携 | C | 旧愛称体制(DD-162で上書き) |
| ffb97d3b | PC間同期DD草案 | C | 趣旨はFKI-CACHE-AUTO-SYNC-01+CLAUDE.mdスリム化に吸収済み |
| 94dfb88c | DR-7.9 PhaseC PWA Push | **B** | 吸収先=**1f583fa6(患者アプリ)**。図鑑イベント/リコール通知動線と同一設計面 |
| b7a83e24 | backend/.env永続化 | C | 現環境で.env運用確立済(実害報告なし)。要最終確認のみ |
| 9c691c11 | StopHook Playwright到達性 | C | DD-134派生の旧前提 |
| 5c08337c | B案BE effort置換+pytest hook | C | DD-128 Phase6監査完走待ち前提が消滅(旧体制) |
| 09553c5c | effort置換網羅検証 | C | 同上従属 |
| 1a9bd24b | AutoMode導入時監査セット | C | AutoMode導入自体が立ち消え |
| fdca0fd8 | Python venv統一 | C | 4月infra hygiene。現運用(system python+doppler)で安定。裁定表(復活要否) |
| 0b1585a4 | DD-138 Stage5 | C | DD-138族一括(旧体制・監査基盤も旧) |
| c1dfeaec | DD-138 Stage6 | C | 同上 |
| 409c606a | DD-138 Stage3a | C | 同上(副院長保留5件の前提そのもの) |
| 5d86a358 | Claude Code Web/Desktop評価 | **B** | 吸収先=**6556d840(cloud Routines化検討)**。同一論点の新版 |
| 8b47a342 | DD-139自動進行統合4本柱 | C | 4月大構想。現行watcher/dispatcher体制が実装済の現実解。裁定表 |
| 47ea1b8a | n8n+MCP統合(B''-3) | C | B-dash構想族。前提のB''-2未着手のまま3ヶ月 |
| 946150af | n8n install(B''-2) | C | 同上 |
| 3af99f58 | DD-144 no-show予測AI | C | 前提(自動化基盤)消滅。ただし製品価値は将来ありうる→裁定表(将来棚へ移すか廃止か) |
| bdc3cfea | A2A protocol対応(B''-4) | C | SaaS化PhaseB前提の再評価項目 |
| 1cfc6da3 | Claude Dispatch Phase設計 | C | 副医院長Q6回答待ちのまま体制変更で立ち消え |
| ba913f37 | O-2 縮小再設計(検出器) | A | 理事長裁定(B)確定済(566f8f99)。既存fork実装の扱い質問(9cc171f9)未回答が唯一の栓。裁定表 |
| 463cc151 | O-1 shogun fork作成 | A | O-2と同族(fork基盤)。O-2裁定回答と同時に処理。裁定表 |
| bff83c77 | audit_gemini.sh根治 | C | **Gemini監査経路は廃止確定(正本85b541b5§8、新標準=Codex+Hermes)**。修理対象が消滅 |
| 0bc2cd14 | relay wrapper revert耐性 | A | O-2裁定(B)ファミリー(pri105)。O-2と一括裁定。裁定表 |
| ae8083dd | 着火ackリトライエンジン | **B** | 吸収先=**957414e7/d73cc946(watcher恒久化レーン)**。同一問題面 |
| 6556d840 | 週次巡回Routines化検討 | A | 現役(07-18起票の新infra検討) |
| cb860c4d | CLAUDE.mdスリム化 | A | 現役(起案納品済・検分待ち) |
| 4037ec1f | V6タブ配線工区 | A | 現役(次工区キュー済み・理事長裁可済) |
| bbcb5b27 | tooth_events 2系統統合調査 | A | 現役(07-20起票。第一歩=読み取り専用調査。統合実施は理事長裁定) |
| 0d1c3660 | frontend依存脆弱性8件 | A | 現役(07-20起票。security) |

### 1.6 reviewing 13件
| id | 件名(短縮) | 分類 | 理由/証拠 |
|---|---|---|---|
| ef9b4540 | 見本PDF11本物理確保 | **D**候補 | storage取込先確定済+見本カルテレーン(56379a3f)は本PDFを前提に計画進行中=前提物は確保済とみられる。裁定表(確証確認) |
| 529c52af | ssh_health復活 | **D**候補 | 稼働開始済・残=実着弾確証/軍師green待ち。裁定表(AUDIT-GREEN-TRUTH) |
| 8012f18c | 申し送りV5視認検証 | A | 現役P0(理事長優先)。blocker=sample table不在の差配待ち。裁定表 |
| 947eb280 | 是正案3案敵対監査 | **D**候補 | report完成・軍師提出済。verdict待ちのみ。裁定表 |
| f83dedaa | 3PC視覚環境統一 | **D**候補 | 軍師codex green row済(行内記録)。裁定表 |
| 7f98a1fa | 3PC視覚環境Tier1+2+3 | **D**候補 | 同上 |
| fd5a9958 | 申し送りWCAG contrast | A(凍結注意) | macレーン=stopped。裁定表(Mac停止laneの扱い、58d2e2ad/29ef43cbと一括) |
| 29ef43cb | 申し送りtruncation実バグ疑い | A(凍結注意) | 同上(実バグ疑いのため廃止不可) |
| fea6a167 | billing_items writer TRUE | A | P0理事長優先の現役(見本カルテ/カルテ正史直結) |
| 957414e7 | watcher auto-rebind | A | インフラ本丸の現役(3例実証済) |
| d73cc946 | watcher busy-flag構造穴 | A | 同上 |
| bdbcf340 | GO-2 Mac結線完成 | **D**候補 | 機能疎通verify成立・軍師green待ちのみ。裁定表(Mac停止lane注意) |
| f46d46a9 | sync_source_cacheバッチ全滅修正 | **D** | 相談役4往復監査PASS(seq129664)+PR#53 squash merge済 |

## 2. design_decisions 分類表(53件)

### 2.1 現行体制の根幹なのに非final — A(final化裁定を最優先で推奨) 13件
DD-160(AI劣化対策3条)/DD-161(建築四工程)/DD-162(組織序列正本)/DD-163(正本参照必須)/DD-164(API承認必須)/DD-165(副院長五条v1.4)/DD-166(Commander機構)/DD-169(kill例外)/DD-175(発信規律)/DD-176(F002範囲)/DD-177(Enter二層)/DD-178(堅実カデンス)/DD-180(検証ゲート統合原則)
— いずれも**日常運用で実効している統治正本**。pending/provisionalのままでは「正本を読まずに動くな」(DD-163)と自己矛盾。監査経路(旧Gemini併走前提)の再定義後、一括final化を裁定表へ。

### 2.2 名指し6件(発令文指定)の判定
| DD | 状態 | 分類 | 所見 |
|---|---|---|---|
| DD-167 司令庫v1.2 | pending, codex **failed**🟡 | C候補 | 監査fail(07-10)後の是正なし。死活監視の実需はwatcher恒久化(957414e7族)+ALL-BLOCKED-MUST-ESCALATE規則が実質代替。14重機構は過剰設計の疑い。**裁定=縮小再設計 or 廃止** |
| DD-179 画像残15% | pending | **B** | 吸収先=**008df0d0(画像管理親、指示書v1.3 is_current)**。残15%スコープはP0基盤穴工程と重複。DD自体はレーン完了時にsupersede |
| DD-183 hermes2→kankyo改名 | pending | A | 混同事故根治として有効。条件(SSH第2段階完了)の充足確認後に実施。小粒 |
| DD-185 7ゲート | provisional | A | 現に各レーンでG1等が引用される実効正本。final化裁定へ |
| DD-186 Mac 4PC編成 | pending | A(凍結注意) | Mac製品laneはstopped_by_user_order。編成正本化はMac再開裁定とセットで判断 |
| DD-188 指示モード | provisional | A | 進行中(PR#27 landed済・C1 bucket是正が残)。レーン完了時にfinal化 |

### 2.3 その他pending(4-5月系) 
| DD | 分類 | 所見 |
|---|---|---|
| DD-113 (DD-112補遺: handshake指示も監査対象) | A | 実効中の統治原則。final化一括へ |
| DD-115 T15 2軸設計 / DD-117 T19医院人格 | A | 患者アプリ発令(world_theme/年齢tier)の設計基盤として現役。provisional維持→レーンでfinal化 |
| DD-116 T17画像アセット基盤 | **B** | 吸収先=008df0d0。asset_master 5テーブルは画像レーン実装対象そのもの |
| DD-118 無曖昧性原則 | A | 実効(Completion Definition文化の源流)。final化一括へ |
| DD-120 指示文テンプレv2.2 | C候補 | v2.1完走前提が消滅。管理者共通綱領v1.0(129721)が上位互換。裁定表 |
| DD-127 認可基盤(RLS第一) / DD-128 全件是正 | A | **患者アプリP0-3認証上程の土台**。115d77eb(staff-auth/T15 RLS)と併せて振興管理へ |
| DD-129 暫定領収書(電子印鑑+メール) | A | DD-044完成まで暫定として有効か要確認。裁定表(小粒) |
| DD-135 VERBATIM物理ガードv2.3 | A | codex passed(yellow)。実効ルール。final化一括へ |
| DD-141 監査ウエイト再配分 | A | 現行の「文書軽量+実装厳格」運用の根拠。final化一括へ |
| DD-149 AHK×レセコン統合v4.0 | C(凍結) | レセコン停止指示対象。再開裁定に従属。裁定表 |
| DD-154/155 監査用投影体制(AGENTS.md/CODEMAP) | C候補 | 旧Codex/Gemini併走前提。新標準(Codex+Hermes)+source_code_cache体制で再定義要。裁定表 |
| DD-158 監査フォールバックチェーン | A | Hermes leg断(4db5b9ac)の現実に照らし実効価値あり。final化一括へ |
| DD-159 画像生成使い分け | A | 実効方針(gpt-image-2/nano banana)。final化一括へ |
| DD-168 死活監視の司令庫委譲 | C候補 | DD-167と運命共同。裁定表(167と一括) |
| DD-174 Gemini監査軸Phase化 | C候補 | Gemini監査経路廃止(85b541b5§8)により対象消滅。裁定表 |
| DD-181 視覚検査直列ゲート | A | 憲法級として実効(FKI-FRONTEND-VISUAL-CHECK-ALWAYS-01と一体)。final化一括へ |
| DD-182 pane入替send-keysズレ | A | 実効(pane identity規律の正本)。final化一括へ |
| DD-184 3拠点相互保守構想 | C(将来棚) | 第17章完了後の将来構想。台帳から将来棚へ隔離を提案 |
| DD-187 Context7 MCP | A | 導入判断未実施。小粒裁定(導入可否)へ |
| DD-189 ccflare 8080統一 | **D相当(final化即可)** | codex **passed🟢**+当職07-14実測(全10プロセス8080-only、8081/8082=0)で実態も一致。activate推奨 |
| DD-191 サーベイ | A | 実装進行中(e4848816)。レーン完了時final化 |
| DAISHOGUN-SPY-SENTINEL | A | provisional実効(誤宛先エスカレーション)。final化一括へ |
| DD-HERMES-CODEX-PIVOT-01 | **D相当** | pivot自体は実施済(gunshi=codex ChatGPT-authed運用が現実)。final化推奨 |

### 2.4 FKI-*系 provisional 8件 — 全てA(実効運用ルール、final化一括裁定へ)
FKI-CACHE-AUTO-SYNC-01 / FKI-DIFF-CANON-READ-01 / FKI-ETA-ALWAYS-01 / FKI-HERMES-AUTHJSON-MTIME-BASELINE-01 / FKI-HERMES-PCHS-PERMS-01 / FKI-HERMES-PCHS-PERMS-02 / FKI-HERMES-UPSTREAM-RELAY-01 / FKI-PCHS-SECRET-BASELINE-01
— いずれも運用中の実効規約。ただしHermes系5件はHermes監査leg復旧(4db5b9ac)と権限案A land状況の確認後にfinal化。

## 3. 理事長裁定表(裁定が必要な行のみ抜粋)

| # | 対象 | 裁定事項 | 当職推奨 |
|---|---|---|---|
| 1 | abandoned 11件(§1.1) | 正式廃止(台帳から除外) | 全件廃止 |
| 2 | DD-138族: 0b1585a4/c1dfeaec/409c606a+副院長保留4件(c0c7d72c/1a41b982/7ac7d0ba/3e7cc47d) | 旧体制残骸の一括廃止 | 廃止(29236fb2はD=f46d46a9で根治済) |
| 3 | DD-134族: ebfe81f9+designing 3件(19f0fec8/4d0bf797/908d924a) | ekarte-v3前提の一括廃止 | 廃止(V6正史と不整合) |
| 4 | DD-091族: eb645a15/95a4370b/92af0a72 | 04-19保留の失効宣言 or 再上程 | 失効宣言 |
| 5 | 06-20 desktop自動化族: 7a36ffb6/e841db83/e566b6db/5ff0d3b9+abandoned poke4件 | 一括廃止(現行dispatcher体制で代替) | 廃止 |
| 6 | B-dash族: 47ea1b8a/946150af/bdc3cfea/8b47a342/1cfc6da3 | 一括廃止 | 廃止 |
| 7 | 3af99f58 no-show予測AI | 廃止 or 将来棚(製品roadmap)へ隔離 | 将来棚(DD-184と同処遇) |
| 8 | レセコン凍結族: BI⇔Quartetto Stage2-5(4件)+DD-149+DD-186+Mac系3件(58d2e2ad/fd5a9958/29ef43cb)+bdbcf340 | 停止laneの台帳上の扱い(凍結棚新設か) | 「凍結棚」ステータス新設し振興管理から分離 |
| 9 | **D確定7件**: 6e7b46ec/29236fb2/f9fbf06d/4e54f890/75d04ac1/64ed6037/f46d46a9 | completed化の一括反映承認 | 承認(行内証跡+PR/監査PASS記録あり) |
| 10 | **D候補(green待ちのみ)9件**: 55f99184/ac046435/aa437254/ef9b4540/529c52af/947eb280/f83dedaa/7f98a1fa/bdbcf340 | AUDIT-GREEN-TRUTH下でのcompleted化条件(green証跡の回収手順) | 軍師/相談役verdict回収を一括バッチで実施→回収後completed化 |
| 11 | DB整合性族: b0cef740/4b66c94e/7055f6b9/424f36a9/dceed06e/84f47aed/bbcb5b27 | D-lane DDL適用の優先順位とGO(T10 FK/T11トリガ/T12旧列/tooth_events) | T10→T11→T12の順で個別GO。84f47aedは廃止 |
| 12 | O-2族: ba913f37/463cc151/0bc2cd14 | fork実装(1c31ecc+232commits)の扱い質問(9cc171f9)への回答 | 回答後にmain遊兵へ配分(裁定B確定済のため回答のみが栓) |
| 13 | DD-167/168 司令庫 | 縮小再設計 or 廃止 | 廃止し、実需はwatcher恒久化+新規則で吸収 |
| 14 | 統治正本final化バッチ: §2.1の13件+DD-113/118/135/141/158/159/181/182+FKI 8件+SPY-SENTINEL | 一括final化(監査要件の充足方法含む) | Codex単独監査で順次final化(Gemini廃止済のため) |
| 15 | DD-189 ccflare 8080統一 | 即時activate | 承認(codex🟢+07-14実測一致) |
| 16 | Gemini前提族: bff83c77+DD-174+DD-154/155+DD-120 | 廃止/再定義 | bff83c77・DD-174廃止、DD-154/155は新標準向けに再定義、DD-120廃止 |
| 17 | 4db5b9ac Hermes監査環境(main) | Copilot/gpt-4.1ライセンス調達 or main単独はCodex単独監査容認 | 環境部長へ調達指示、当面Codex単独容認 |
| 18 | bb31269c スマホ承認 / DD-187 Context7 / DD-129 暫定領収書 / 9f30de06+a1506500 DD-061コンプラ2件 | 小粒個別裁定(やる/やらない/担当) | 個別に5分裁定 |

## 4. 手法・制約遵守
- データ源: task_tracker 125行(status not in completed/done/cancelled、Content-Range実測125)+design_decisions 53行(pending+provisional_active)をSELECTのみで取得。生データ=scratchpad保管(tt_incomplete.json/dd_nonfinal.json)。
- D判定の証跡は行内記録(blocker/current_step/result_summary)と当職一次記録(seq/PR番号)に限定。推測でのD判定なし。
- **UPDATE/completed化/abandoned化は一切実行していない**(AUDIT-GREEN-TRUTHトリガ遵守)。反映は委員長検分→理事長裁定後の一括作業。
- 患者アプリ実装凍結は本工区と無関係に継続中。

記録者: 将軍main (shogun-main:0.0) 2026-07-20
