# a37dc0f 引継ぎ票 — Lane C′ 着手前・足軽1号(作者)→足軽7号

- **本 file の性格**: ★引継ぎ票のみ★。実装の追加・修正は一切行っていない。
- **下命**: `queue/inbox/ashigaru1.yaml` id=`msg_20260806_223746_9ef181f3`、from=karo-second、timestamp=`2026-08-06T22:37:46`（task YAML `current_order_10_20260806_2240_A37DC0F_HANDOFF` と同一内容）。
- **端緒**: 足軽7号 `docs/incident_logs/2026-08-06_deadletter_serializer_lanecprime_dup_check_a7.md`（測時22:30:18）— Lane C′ 着手前に Anti-Duplication 調査を行い、a37dc0f が已に存在し軍師second PASS済と発見して実装に入らず止めた報告。
- **測時（本票作成）** = 2026-08-06T22:43:23+0900。
- **母集団宣言**: 本票作成にあたり実際に読んだ物 = `git show a37dc0f`（diff全文）／`git show a37dc0f:shim/hakudokai/hakudokai_secondpc_receiver_poll.py`（全文・行番号突合）／`git show a37dc0f:tests/test_secondpc_receiver_dead_letter_serializer.py`（全文143行）／自票 `2026-08-06_dead_letter_serializer_lane_c_a1.md`／足軽7号票／`gunshi_second_dead_letter_serializer_lane_c_audit_20260806.md`／`git worktree list`／`git diff a37dc0f feat/deadletter-yaml-serializer-hardening-a7 --stat`。原本 `queue/inbox/_dead_letter_second.yaml` へは本票作成中も一切触れず（grep/wc/cat 不実行）。

## 対象の同定（SHA）

- commit（git object＝SHA-1・40桁）= `a37dc0f26d78f8c8bb785b4191cab1b561a9fd44`（prefixに非ず・`git rev-parse a37dc0f` で全桁確認済）。
  - ★申し添え★: 本 repo の git object は SHA-1（40桁）であり、64桁の SHA-256 ではない。「64桁で書け」の令の意図（prefix 使用禁）は本コミットハッシュについては全40桁の提示で満たすと判断した。判らぬ点として第四値節に記す。
- branch = `feat/deadletter-yaml-serializer`、base = `4061f26`。
- worktree（現存確認済・`git worktree list` 実測）= `/tmp/hakudokai-worktrees/deadletter-yaml-serializer`。
- ★申し添え（足軽7号への実務情報）★: `/tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7`（branch `feat/deadletter-yaml-serializer-hardening-a7`）が既に存在し、`git diff a37dc0f feat/deadletter-yaml-serializer-hardening-a7 --stat` は無出力＝★a37dc0fと完全に同一・まだ何も足されておらぬ★（本票作成時点の実測）。足軽7号が着手するならこの worktree が既に用意されている可能性が高いが、当職はこれを作った当人ではなく、用途は未確認（第四値）。
- 変更ファイル2件の内容 SHA-256（64桁・commit a37dc0f 時点の blob 内容）:
  - `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` = `8c2a62d61b7f6ca30c382842c450e4f357dadb1657489b186422e6df4fcb8104`
  - `tests/test_secondpc_receiver_dead_letter_serializer.py` = `512b81a1dd7bc38cd7fef3f6aad20f08d8c06eefc7771b0d009560ff85900285`

## ⒜ 七つの契約に対する己の実装の現況

行番号は commit a37dc0f 時点の `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`（`git show a37dc0f:...`）に対する物。

| # | 契約 | 判定 | 根拠 |
|---|---|---|---|
| ⒜ | writer/reader 母集団 | ★閉じた★ | writer=1件のみ（`append_dead_letter()` 自身）。reader=専用parser 0件。当職の自票（測時22:00:10・grep実測）と足軽7号の独立再測（22:30:18）が一致。テストなし（構造的事実の grep 確認のみ・下記「継ぎ目」④で後述）。 |
| ⒝ | 同時writer flock/atomicity | ★開いておる★ | L272 `path.write_text(...)` を直接呼ぶのみ。`flock`/`fcntl` 等の排他制御コードは diff・現物いずれにも無し（`git show a37dc0f` 全文確認済）。テスト無し・未実行。 |
| ⒞ | 途中停止（partial write） | ★開いておる★ | L272 の書込みは tmp file + rename の原子的置換ではなく直接 `write_text`。同一ファイル内 L156-166（`file_sync` 処理内）には `tmp_path = target_path + ".tmp"` → `os.replace(tmp_path, target_path)` という既存の原子的書込みidiomが在るが、`append_dead_letter()` はこれを再利用していない（当職が実装時に見落とした・後述「継ぎ目」①）。L245-246 の `.corrupt.<epoch>` 退避は「次回起動時に既存fileが壊れていた場合」の対処であり「書込み中の中断」そのものへの対処ではない（足軽7号の指摘=正確・当職も同意）。 |
| ⒟ | 特殊文字 | ★閉じた★ | `tests/test_secondpc_receiver_dead_letter_serializer.py` L70 `test_synthetic_special_chars_round_trip`。実走結果=自票（22:00:10測時）記載の通り、RED（修正前コード・手組みf-string版）に対し実行→`yaml.scanner.ScannerError` で FAILED（実運用ファイルと同型のバックスラッシュ欠陥を再現）。GREEN（修正後）=3/3 PASS。軍師second監査 22:03:24 PASS でも確認済。 |
| ⒠ | 再起動 | ★開いておる（部分のみ閉）★ | L241-246 の `except yaml.YAMLError` ハンドラは「既存fileがparse不能→`.corrupt.<epoch>`退避→空`messages`から再開」を実装済（クラッシュループ化防止）。★而して★この分岐（L241-246）を通すテストは3 test中に★一つも無い★（L70/L111/L130いずれも正常系のみ・壊れたfileを事前に置いて`append_dead_letter`を呼ぶテストは無し）。すなわちこの経路は当職が実装時に手動確認した記憶はあるが、回帰を防ぐテストとしては存在しない＝機能としては閉じている可能性が高いが「閉じた」と申すに足る令の水準（test名・行・実走結果）を満たさぬため★開いておる★と判定する。 |
| ⒡ | 重複/欠落=0 | ★重複=閉じた／欠落=開いておる★ | 重複: `test_dedup_by_handshake_id_skips_second_write`（L111）が `_handshake_id` 厳密一致で PASS（自票・軍師監査とも確認済）。欠落: 中断時・例外時に0件損失を保証するテストは無し（⒞と連動する未検証領域）。 |
| ⒢ | `_handshake_id` 欠落時 fail-closed | ★開いておる（現状はfail-open）★ | L237 `msg_id = msg.get("id", "")`。dedup判定 `if msg_id and any(...)` は `msg_id` が空文字なら False となり素通り、その後 `messages.append({..., "_handshake_id": msg_id, ...})`（L262前後）が★無条件に実行される★。すなわち `id` が欠落したメッセージは★毎回書き込みが通る（fail-open）★——契約が求める「欠落時は拒め（fail-closed）」とは逆の挙動。当職はこの読解を本票作成にあたり自らL237/L262を再読して確認した（静的読解・動的実行はしていない＝テストで再現してはいない）。足軽7号の同一指摘（22:30:18票）と一致。 |

★令④再計数★: 契約は当職も数え直し★七つ★（⒜〜⒢）で一致。増減なし。

## ⒝ 継ぎ目（足軽7号が手を入れる時に壊し易い所）

1. **既存の原子書込みidiomが未使用**: 同一file L156-166（`file_sync`処理）に `tmp_path` + `os.replace()` の原子的置換パターンが既に在る。⒞⒝を直す際、新しいidiomを持ち込むより★このidiomを再利用する★方が一貫性が保てる。逆に、両方が同じfile内に同居するため、diffツールでの編集時に file_sync 側の tmp_path 処理を誤って触らぬよう注意（当職自身が実装時に L156-166 の存在に気づかず車輪の再発明をした=同じ見落としを繰り返さぬよう名指しする）。
2. **flockはread-modify-write全体を覆う必要がある**: 現状の構造は「L237付近で読込→L?? messagesリストへmutate→L272 write_text」の順。⒝を直す際、ロックを★最終書込みだけ★に掛けると読込〜書込の間の競合窓が残る。読込直後からロックを取得し、書込完了までを覆うこと。
3. **`.corrupt.<epoch>`分岐(L241-246)はテスト無し**: ⒠の項で述べた通り。⒞⒝の修正でこの分岐に触れるなら、★壊れたfileを事前に用意してappend_dead_letterを呼ぶ★テストを新設せねば、この分岐は変更前後で挙動が変わっても誰も気づけない。
4. **⒜（母集団=writer1/reader0）もテスト無しの構造的事実**: 新規readerが将来追加された場合にこの前提が崩れても検知する仕組みが無い。当職はgrepでの手動確認のみで担保しており、自動テスト化はしていない。
5. **L237 `msg.get("id", "")` は⒝⒞と近接**: ⒢（fail-closed化）に手を入れる際、同じ関数の先頭付近のためdiffが⒝⒞の修正と混線しやすい。★別コミット/別テストで切り分けることを推奨★（当職の意見であり指示ではない）。
6. **test harnessはAST抽出方式**: `tests/test_secondpc_receiver_dead_letter_serializer.py` の `_load_append_dead_letter()`（テストfile冒頭）は `ast.parse`+`ast.unparse` で `append_dead_letter` 関数定義のみを抽出し独立namespaceへexecしている（モジュール全体をimportすると `sys.argv[1]/[2]` 等の実行時引数とSupabase環境変数を要求し即座に落ちるため）。新規テストを足す場合もこの手法を踏襲する必要がある。素朴に `import` すると壊れる。

## ⒞ `*.corrupt.<epoch>` rename の未許可問題への回答

★問い★: 貴殿（当職）の実装・票が此のrenameを前提や既定にしておるか。

★答え★: ★している★。名指しの箇所は以下:

- **実装**: `shim/hakudokai/hakudokai_secondpc_receiver_poll.py`（commit a37dc0f）L245-246
  ```
  backup = path.with_name(path.name + f".corrupt.{int(time.time())}")
  path.rename(backup)
  ```
  これは`except yaml.YAMLError`ハンドラ内にあり、既存の`_dead_letter_second.yaml`がparse不能な場合に★無条件・既定動作として★実行される（フラグやフィーチャーゲートは無い）。
- **票**: 自票 `2026-08-06_dead_letter_serializer_lane_c_a1.md` L26「既存fileがparse不能な場合は例外を揉み消さずタイムスタンプ付きで退避(*.corrupt.<epoch>)し空messagesから再開(クラッシュループ化防止・スコープ内の副次改善として明記)」— ★これを承認要の別項目としてではなく、スコープ内の是正の一部として記述した★。

★申し添え（本部長殿の指摘の通り・当職の落度としては書かぬ）★: gunshi-second の Lane C 監査票（`queue/reports/gunshi_second_dead_letter_serializer_lane_c_audit_20260806.md` L12）は「parse 不能既存 file は `*.corrupt.<epoch>` へ退避して空 `messages` から再開する形へ改めておる」を PASS 判定の根拠の一つとして★明示的に肯定★している（22:03:24時点）。すなわち実装・票・監査票の三者いずれも、当時この rename を通常のバグ修正の一部として扱っており、別途の許可を要する操作とは認識していなかった。契約が後から更新され、票が古びた形である。

- **他箇所での前例の有無**: `/usr/bin/grep -rn "\.corrupt\." --include=*.py --include=*.sh .`（`.git/`除く）は★0件★（本票作成にあたり実測）。すなわちこのrenameパターンは a37dc0f が★repo内で初めて導入した物★であり、既存の承認済idiomの踏襲ではない。

- 足軽7号が此処に手を入れる場合の含意: ⒞（partial write）の是正でこの分岐そのものを書き換える可能性が高いが、rename自体の使用継続可否は★委員長GOを要する★（当職の権限外）。当職からは書き換え可否の裁定はしない。

## ⒟ 判らぬは判らぬまま（第四値）

- `feat/deadletter-yaml-serializer-hardening-a7` worktree の存在理由・作成者・作成時刻は当職には判らぬ（`git worktree list`で存在のみ確認・中身は a37dc0f と無差分）。
- 「64桁でSHAを書け」の令が git commit（SHA-1・40桁）にも及ぶ意図か、file内容ハッシュ（SHA-256・64桁）限定かは、当職の読解では確定できぬ。本票は両方を併記し、40桁である旨を明記することで対処した。
- ⒠（再起動）の`.corrupt.<epoch>`分岐が実運用で意図通り動くかどうかは、当職は実装時に手動での動作確認をした記憶はあるが、その記録（コマンド・結果）を自票に残していないため、★閉じた根拠として提示できぬ★。テストが無い以上、動くという当職の記憶そのものを根拠とはしない。
- 委員長GOが下った場合にrenameがどう改められるべきか（廃止／フラグ化／別実装）は裁定事項であり、当職からは提案しない（本工区の禁「迂回案・言い換えを書くな」に準ずる態度を踏襲した。厳密には本工区の禁ではないが、Lane D票と同じ理由=案を出す事自体が裁定の先取りになり得るため控えた）。

## 禁の遵守

- `feat/deadletter-yaml-serializer` branch: 一字も書き換えていない（`git diff a37dc0f feat/deadletter-yaml-serializer-hardening-a7 --stat` 等はいずれも読取専用コマンド）。
- `queue/inbox/_dead_letter_second.yaml` 原本: 本工区中 grep/wc/cat 含め一切アクセスしていない。
- 実装の追加: 行っていない（本票はdocsへの新規file作成のみ）。
- 主repo HEAD: `feat/dd169-d006-conditional-exception`のまま不動（`git status --short --branch`で確認可能・checkout/merge/pull不実行）。

## 令⑥（監査発注 三行）

- 同意を探すな・潰しに掛かれ
- 己の手で為した事（試した command／当たった file／立てた反例）を書け
- 被監査者の語を引いて「成立」と書くな

軍師secondへ提出。report_to=karo-second。ETA=即時（本票が完了報告）。
