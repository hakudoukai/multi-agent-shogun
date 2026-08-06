# Lane B — D案 installer local実装 + sandbox検証 (足軽3号)

owner: ashigaru3 / report_to: karo-second
task key: `current_order_13_20260807_011400_D_INSTALLER_LOCAL_SANDBOX`
発令経路: 本部長殿 01:05:58 → karo-second msg_20260807_011455_34104565、追補 msg_20260807_012156_fc8ea882
測時: 2026-08-07T01:21〜01:35 JST (器=`bats`/`git`/`sha256sum`・date -Iseconds実値)
主repo HEAD: `5da21919d74b780df14683d276a81faa6305e476` (branch `feat/dd169-d006-conditional-exception`・本工区で無変更)
worktree: `/tmp/hakudokai-worktrees/morning-digest-reader-sender` HEAD=`879334a37a6d4e9f3bd90549f53132e0ade0a644` (branch `feat/morning-digest-reader-sender`・★本工区で local commit 1件★)

★HARD_STOP 確認★= 実host apply／systemctl／runtime dir／unit dir／send＝悉く0のまま。local実装・build・test・local commitのみ本票の範囲(令の射程内=karo-second msg_20260807_012156_fc8ea882 ㈠で確定済)。

---

## ㈠ installer local実装

新規: `scripts/watchdogs/morning_digest_send_install_dplan.sh`（250行/sha256=713b7e7b5bc6894e61d459edffd55da6546507283ca278dcfccb7d02b674c39f）

既存 `morning_digest_send_install.sh`（copy-only・ExecStartはcheckout pathのまま）を土台に、以下を追加/変更:
- script blobを `$HOME/.openclaw/morning_digest_runtime/` へ copy → 生成unitのExecStartをinstalled blobへ向ける
- 生成unitへ ExecStartPre を追加し、依存 `scripts/inbox_write.sh`（main repo絶対path参照・copy 0継続）の full SHA を**毎起動時に**検証、drift/missingでfail-closed（karo-second msg_20260807_011455 ㈢「毎回検証」の実装。旧設計にはこの検証が存在せず、之が本部長殿ご指摘「無検証のまま依存」の穴であった）
- apply時にも同依存のpreflight検証を追加（インストール前に既に壊れている場合は据え付けさせない）
- source/installed byte一致のfail-closed（不一致ならinstalled側を削除しrefuse、旧installerには無かった経路）
- `--rollback` はruntime script + unit + timerを除去（旧installerはunit/timerのみ、runtime dirへ何も書かないため之で足りていた。D案はruntime scriptを新たに書くため必須拡張）
- manifest (JSON) へ installed_script_sha256／rendered_service_sha256／timer_sha256／approval_ref等を記録

overridable env（既存installerの `MDS_INSTALL_UNIT_DIR`/`MDS_INSTALL_SYSTEMCTL` パターンを踏襲・拡張）:
`MDS_INSTALL_UNIT_DIR` / `MDS_INSTALL_RUNTIME_DIR` / `MDS_INSTALL_SYSTEMCTL` / `MDS_INSTALL_LOG` / `MDS_INSTALL_MANIFEST` / `MDS_INSTALL_INBOX_WRITE_REF`

approval-ref gate構造は既存installerと同一のまま維持（`seq152416/id616c43a9-aef2-4a63-a706-d47ad7d7357a`・一字も違えず）。

---

## ㈡ sandbox検証（実installer scriptを対象・bats helper関数の代用ではない）

新規: `tests/e2e/test_morning_digest_dplan_installer_local_sandbox.bats`（276行/sha256=b51be6e012ff4dadcb2f93621022f265da366483ec3a564b24dd915f06d11ea3）

current_order_12票（`test_morning_digest_dplan_installer_synthetic_e2e.bats`）との違い= あちらはD案の経路をbats内helper関数（`dplan_copy_step`等）で再現し経路そのものの妥当性を先に示した票。本票は**実行可能なinstaller script自体**を対象にする（Anti-Duplication抵触なし・対象が異なる・drift fail-closed検証は本票が初出）。

### 実走結果（2回独立実走・同一commit `aafd8ec3a5e4f1c8285061118c219714f217887b`＝本工区の主対象コードは無変更、テストのみ追加）

```
cd /tmp/hakudokai-worktrees/morning-digest-reader-sender
bats tests/e2e/test_morning_digest_dplan_installer_local_sandbox.bats
```

1回目・2回目とも同一結果 = **15/15 GREEN**:

```
1..15
ok 1 RED: old installer (copy-only, ExecStart -> %h/projects/multi-agent-shogun checkout, unmodified) is dangling RIGHT NOW against the real main repo (read-only check, no host mutation)
ok 2 GREEN: D installer apply -- installed script, rendered service, timer, manifest all present with correct SHAs
ok 3 GREEN: apply preflight refuses when inbox_write dependency already drifted before install
ok 4 GREEN: apply preflight refuses when inbox_write dependency missing before install
ok 5 GREEN: post-install ExecStartPre drift check fails-closed when dependency drifts AFTER apply (per-start, not just install-time)
ok 6 GREEN: post-install ExecStartPre drift check fails-closed when dependency goes missing AFTER apply
ok 7 GREEN: post-install ExecStartPre drift check PASSES when dependency untouched (no false positive)
ok 8 GREEN: production-mode content assertion -- default INBOX_WRITE_REF renders literal %h path (string-asserted only, never executed against real main repo)
ok 9 GREEN: rollback removes installed script, unit, and timer
ok 10 GREEN: rollback is idempotent -- second rollback run does not error
ok 11 GREEN: rollback leaves unrelated files byte-invariant
ok 12 GREEN: apply without approval-ref refused (fail-closed, unchanged from old installer's discipline)
ok 13 GREEN: apply with wrong approval-ref refused
ok 14 GREEN: end-to-end send via the D installer's actual installed blob (direct service entry, correct dependency)
ok 15 GREEN: 装着0 across whole suite -- systemctl canary + real host paths untouched
```

### RED/GREEN の実際の意味（令④・混同防止のため明記）

- **RED-1**（テスト名「old installer ... dangling RIGHT NOW」）= ★令が名指した本来のRED★。既存(旧)installerの生成ExecStartが指す `%h/projects/multi-agent-shogun/scripts/morning_digest_send.sh` を、実際に `%h`→実`$HOME`展開して確かめたところ、★シミュレーションではなく現実に★ 存在しない（本feature branchは未mergeゆえ）ことを read-only で実測。current_order_10 censusの「dangling ExecStart」findingそのものを、D案installerが要る理由として再現した。
- **GREEN-2〜15** = D案installerが実際に採る手順（apply/drift fail-closed/rollback/idempotent/byte-invariant/end-to-end send/装着0）を実走し、期待通り通ることを確認。

### ㈢ drift fail-closed契約（本工区の主眼・前回karo-second指摘の穴を実装で塞いだ）

- **install前（preflight）**: `--apply` 実行時、`MDS_INSTALL_INBOX_WRITE_REF` の実SHAが期待値 `6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d` と不一致／不在なら `REFUSED` で即終了、runtime script/unit一切書かず（test 3,4で実測）。
- **install後・毎起動前（ExecStartPre）**: 生成unitに埋め込まれた `ExecStartPre=/bin/bash -c 'sha256sum "<ref>" 2>/dev/null | cut -d" " -f1 | grep -qx "<expected>"'` を、install後に依存ファイルへ改変/削除を加えた上で直接実行し、非0終了することを実測（test 5,6）。改変しない場合は0終了（test 7・false positive無し確認）。
- これにより先便で「現状は無し」と申告した drift fail-closed 契約が、本工区で実装として存在するようになった。

### ㈣ rendered service／unit SHA と installed script SHA（manifest実測）

test 2 にて `MDS_INSTALL_MANIFEST` を実際に読み、`installed_script_sha256` が source（`scripts/morning_digest_send.sh` @ worktree HEAD `aafd8ec`）と一致=`4dc46677276e78aecdf8ba100d3ffba61addaba08573eb93fd18c781e4275800`であることをJSON経由で実測。`rendered_service_sha256`／`timer_sha256`も同manifestへ記録される構造をtest内で確認済（値そのものはsandbox実行毎にunit_dir絶対pathを含むため実行環境依存・固定値ではない——本票では「記録される」ことをmanifest構造として検証し、値の同一性は installed_script_sha256（source依存の値）のみ固定値比較した）。

### ㈤ rollback（実installerの`--rollback`モードを実走・sandbox drillに非ず）

test 9,10,11 にて: apply後にrollbackすると installed script/unit/timer が3件とも消える(test 9)／2回目のrollback実行もerrorしない(test 10・idempotent)／rollback前後で installer script自身・source script・unit template のSHAが不変(test 11)、を実測。

---

## ㈥ 依存 inbox_write.sh の absolute path + full SHA（先便からの変更なし・再掲）

absolute path = `%h/projects/multi-agent-shogun/scripts/inbox_write.sh`（%h展開後の実値 = `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`）
full SHA = `6060e9c1e8d358255e4809f25b6ac65f7455bf05d684f88d83ffc0d430df280d`
test 8 にてこの2値が生成unit内に文字列として正しく現れることを実測（実行はせず、read-onlyのsha256sumのみ）。

## 装着0の確認

test 15 にて: sandbox apply+rollback一式実行後、実 `$HOME/.openclaw/morning_digest_runtime` は不在のまま／実 `~/.config/systemd/user/` にmorning_digest関連unit該当0件、を測前・測後とも実測（2回独立実走とも）。実`systemctl`はPATH経由で一度も呼ばれず（installerは常に`$SYSTEMCTL`変数経由でsandbox stubを呼ぶ設計・default値は`--dry-run`/`--rollback-dry-run`モードでのみ使われずcatのみ）。

## commit

worktree local commit ＝ `879334a37a6d4e9f3bd90549f53132e0ade0a644`（`feat/morning-digest-reader-sender`branch・push/merge=0・主repo無変更）。
3 file追加（新installer + 新test 2件・current_order_12成果物のtest fileも本commitで併せて収載）。

## 【本工区で己が直した誤り】

初動でRED-1テストを「checkout gone」を人工的にsimulateする形（fakeな不在dirを用意）で書いたが、実際に `%h` を実`$HOME`へ展開して確かめたところ、main repo checkoutには`scripts/morning_digest_send.sh`が★現に★存在しない（本feature branchが未mergeのため）ことに気づき、simulationをやめて現実の不在を直接測る形へ書き直した。之によりRED-1はcurrent_order_10 censusの実際のfindingをそのまま再現する、より強い証拠になった。

また当初 test 14（end-to-end send）で `MDS_INSTALL_INBOX_WRITE_REF` に平置きcopyを使ったところ`inbox_write.sh`自身のSCRIPT_DIR解決（`$(dirname $0)/..`が repo rootを指す前提）が壊れ失敗した。原因を実読で特定し、既存base E2E suite（`test_morning_digest_send_synthetic_e2e.bats`）と同じ「worktree自身の在place inbox_write.shをそのまま使う」形へ直した——実行を要する箇所はflatなcopyでなく本来の相対構造を保つ必要がある、という区別を保てなかった初動の誤り。

## この工区と対に成る他工区

`current_order_11`（D案手順書・installerの手順を初めて文章化した票）・`current_order_12`（D案installer経路のsynthetic E2E・installer script自体ではなくbats helper関数で経路を先に実証した票・軍師second PASS済 01:22:18）。本票はその両方を実行可能なscriptへ落とし込み、かつ㈥で申告した設計gapを実装で塞いだ続き。

## 追補（2026-08-07T01:4x〜・本部長殿 01:26:02 裁定 msg_20260807_013141_d9266ff4 への応答）

本追補作成に伴い test file を20 test へ拡張（372行/sha256=e4f726570e070d0a9836590604a64b197cfbfeddb8167a76e9741441d9196484）。追加分含め **20/20 GREEN・2回独立実走**再確認済（装着0・real host不触も前後実測済、上記と同じ手順）。

### ① checksum gate ＝ 使用時検問として受入（本部長殿裁定・成立条件を実測で満たす）

成立条件（逐語）＝ oneshot 毎の ExecStartPre で inbox_write の missing／SHA drift を検出し、ExecStart を一度も起動せず nonzero ＋ journal／action log へ expected と actual を残す。

先便までの実測は「ExecStartPre行を単独で実行して非0を確認」に留まり、★systemd の実際のgating（ExecStartPreが1つでも失敗すればExecStartは一度も呼ばれぬ）を chain として実測してはいなかった★。本追補で `run_unit_like_systemd()` ヘルパー（rendered unit の全 `ExecStartPre=` 行を順に実行し、いずれかが非0なら即座に打ち切り ExecStart 相当のマーカー touch を行わない、systemd semantics通りの模倣）を追加し、以下を実測:

- test 8「GATE: ExecStart is NEVER invoked ... on drift」＝ drift時、chain が非0で止まり ExecStart 相当のmarkerが★一度も作られぬ★ことを実測（`[ ! -e "$MARKER" ]`）。
- test 9「... on missing dependency」＝ 同上、missing時も同様。
- test 11「GATE: ExecStart DOES run when ... passes」＝ 依存が正常な場合はmarkerが作られる（false-closed=無いことの確認）。
- test 10「records expected vs actual」＝ ExecStartPre のsha256sum失敗後、expected値とactual値の双方が stderr（実運用ではjournal相当）へ残る形を実測。

**★残る穴 ＝ 検知の遅れ（最大約24時間）のみ★**（timer の `OnCalendar=*-*-* 07:30:00` が唯一の発火点・oneshotゆえ常駐監視窓が無い）。実行の穴（drift状態で実際にsendされてしまう）はGATE test群で0と実測済。之は「実装せぬと決めた残余は票へ書いて初めて残余に成る」の令に従い、★本行にて明記する★:

> **常時alerting（drift発生から検知までの遅延を24時間未満に縮める仕組み）は本工区で実装せず。ExecStartPreによる使用時検問（次回timer発火時=最大24時間後に必ず検出しfail-closedする）のみが現状の防御線。連続稼働監視が要るか否かは本部長殿裁定事項（低順位・residual）。**

### ② unit SHA 正式採用（五点すべて実測で充足）

旧値 `1ef384b9564019236396f3b0bdfad6724ecf12d430f68b3713defcd20cda1f52` は証拠から除外済（再現command不明・以後引用せず）。
候補値 `a048d493e6372338bee312a73255930a040e883f6efd8d89af823e7a075f6622`（current_order_12時点でrenderer関数を直接呼出して得た値）も★正式採用しない★——本追補で原因を特定した: **current_order_12時点の設計にはまだ drift検査用 ExecStartPre 行が無く**、その後karo-second msg_20260807_011455 ㈢でこの行が追加されたため、**内容そのものが変わっていた**（diff で確認=当該1行のみの差分）。

**正式採用値** ＝ `a5f37a95e3868331c916f4debd79cfe60da6c6ab0e08aebad2160a4d8f07559a`（64桁・test 12で実測）。五点:

㈠ full 64桁SHA = 上記（python len()で64確認）
㈡ 生成command = `MDS_INSTALL_INBOX_WRITE_REF` を unset（=production既定値のまま）にして `bash scripts/watchdogs/morning_digest_send_install_dplan.sh --apply --approval-ref=seq152416/id616c43a9-aef2-4a63-a706-d47ad7d7357a` を実行（`MDS_INSTALL_UNIT_DIR` のみ sandbox先へ overrideし他は既定=production挙動を保つ）
㈢ rendered bytesのpath = installerが書いた `$MDS_INSTALL_UNIT_DIR/morning_digest_send.service`（renderer関数を直接呼んだ一時fileではなく★installerが実際に書いたfile★）
㈣ 同一入力で二回一致 = test 12 で unit_dir のみ異なる2回の独立apply実行を行い、生成されたservice fileのSHAが完全一致することを実測
㈤ installer sandbox applyで実際に書かれたservice のSHAと一致 = 定義上そのもの（本値自体が実際に書かれたfileのSHA）

### ③④ 軍師second への令（本追補で対応）

③「installed installer は要求せず」は本部長殿にて採用済（前便どおり・再掲省略）。
④「renderer直接呼出だけでは足りぬ・sandbox applyの出力を独立にhashせよ」＝ 本追補②が正にこれ（installerの実際の`--apply`出力をhashした。renderer関数を直接呼んで得た旧a048d493とは出自が異なることを明記した）。軍師second独立監査でも同じ区別（renderer直接呼出 vs installer実apply出力）を確認されたし、と発注文に添える。

## 判じ得ぬ点（推して埋めず・以上）

1. ★訂正（追補にて自己訂正）★= 本欄に元々「rendered_service_sha256は環境非依存の固定値になり得ない」と書いたが★誤りであった★。誤りの理由＝当時 `MDS_INSTALL_INBOX_WRITE_REF` を sandbox絶対pathへ override した状態で計測しており、その override値自体がunit内容に埋め込まれるため固定値化できないように見えた。だが production既定値（`%h/...`という★symbolicな placeholder のまま★・unit_dir自体は絶対pathを持つがそれはfileの「置き場所」であって「内容」には現れぬ）を使えば、生成unitの内容は環境非依存で固定値になる（追補②・test 12で二回一致を実測=`a5f37a95e3868331c916f4debd79cfe60da6c6ab0e08aebad2160a4d8f07559a`）。★測る条件（override値の有無）を書かずに一般化し過ぎたのが誤りの根★。
2. 実installerのapply/rollbackが「sandboxで動く」ことは本票で実測したが、実host（real systemctl・real unit dir）で実際にsystemd がこのExecStartPre構文を受理するか（bash -c構文のescapeがsystemd unit file syntax上正しいか）は`systemd-analyze verify`等での検証が本票の射程外——本部長殿ご確認プロセスでの検証が必要と当職は考える。

## 禁の遵守確認

実host apply=0／real systemctl呼出=0／real runtime dir・real unit dir 不触（前後実測）／push=0／merge=0／実患者・secret・DB・本番data=0。local commitのみ実施（isolated Lane B worktree・令の射程内）。

## 監査体制・提出

三者監査は暫定二者制（軍師second + Gemini。Codex leg停止中・SAFETY裁定 seq132707）。本票を軍師second へ提出。
発注三行=①同意を探すな・潰しに掛かれ ②己の手で為した事（試したcommand／当たったfile／立てた反例）を書け ③被監査者の語を引いて「成立」と書くな。
