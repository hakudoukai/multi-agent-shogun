# Lane C′ 完了報告 — append_dead_letter 契約充足 (flock/atomicity/fail-closed) (足軽7号)

**測時** = 2026-08-06T23:09:51 **下命者** = karo-second (msg_20260806_223444_ad779e78・current_order_8_20260806_2236_LANE_C_PRIME_SCOPED・裁定A)
**器** = python3(ast/exec隔離実行)・pytest・fcntl・os.replace・yaml.safe_load/safe_dump・git(diff/log/show/merge-base --is-ancestor/worktree add のみ)
**範囲** = 己の新規worktree `/tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7` (branch `feat/deadletter-yaml-serializer-hardening-a7`・base=`a37dc0f`)。主repo HEAD・足軽1号branch `feat/deadletter-yaml-serializer` は不触。

## 結論 (先出し)

★下命の未対応3項 (⒝flock/atomicity・⒞partial write・⒢fail-closed) + ⒠再起動の生死確認、★全4項をa37dc0f土台に上乗せ実装しRED→GREENで閉じた★。
既存契約 (⒟特殊文字・⒡重複欠落) は再測してもPASSのまま (a37dc0fを一切改変せず継承)。

## 令④ (未対応と見立てられし物の実行時再検め)

karo-second裁定=「未対応=⒝⒞⒢+当職が足せし⒠」。本工区の実行の刻に検め直した結果:
- ⒝⒞⒢ = ★karo-second殿の見立て通り未対応だった (RED実測で確認・下記参照)★。
- ⒠再起動 = ★部分的に対応済 (a37dc0f由来の`.corrupt.<epoch>`退避+空messagesから再開) だが、
  「途中で書込みプロセスが死んだ場合の再起動時の生死」は★未対応だった★ (atomicでない書込みゆえ、
  再起動時にtorn/半端fileへ遭遇し得た)。★閉じておる物を重ねて実装せず、閉じておらぬ部分のみ足した★。

## RED (a37dc0f直上・改変前に実測)

新規test `tests/test_secondpc_receiver_dead_letter_hardening.py` (8 tests) をa37dc0fのまま実行:
```
7 failed, 1 passed in 0.13s
```
失敗内訳=⒝flock (lost update)・⒞atomicity (tmp+replaceの不在・原子性未検証で失敗)・⒢fail-closed (3 tests全滅=例外を投げず書き込んでしまう)・⒠restart (kill-mid-write シナリオ1件)。
唯一PASSした1件 = 「既存の壊れfile復旧」regression test (a37dc0f由来・当然PASS=対応済を示す対照)。
★import ERRORや件数PASSでの閉じではなく、実際に失敗理由を読める形でREDを確認した★。

## GREEN (実装後)

- 新規8 test = ★8/8 PASS★ (concurrency testは5回連続実行し安定PASSを確認・flaky検証済)。
- 既存 `tests/test_secondpc_receiver_dead_letter_serializer.py` (a1由来・3 test) = ★3/3 PASS維持★
  (改変内容=テスト側namespace辞書へ`os`/`fcntl`を追加しただけ・本体アサーション文は1文字も変更していない)。
- `tests/test_watcher_hotfix.py` = 16 passed / 1 failed (`test_retry_cap_dead_letters`・`acknowledged_by KeyError`)。
  ★之はa1の完了報告に記載の pre-existing failure と完全一致 (同じtest名・同じ例外)★=当職の変更起因ではない。

## 実装内容 (a37dc0fを土台・未対応分のみ追加)

`shim/hakudokai/hakudokai_secondpc_receiver_poll.py` の `append_dead_letter()`:
1. **⒢ fail-closed**: 関数冒頭で `msg.get("id")` が空なら `ValueError` を送出し、一切書き込まずreturn (旧=fail-open寄りで`_handshake_id: ""`のentryを無条件追記していた)。
2. **⒝ flock**: `_dead_letter_second.yaml.lock` というsidecar fileを`fcntl.flock(LOCK_EX)`で保護し、読込→dedup判定→書込みの全区間を排他化。
3. **⒞ atomic write**: 同一directory内の一意なtmpファイル (`<name>.tmp.<pid>.<epoch_ms>`) へ書いてから `os.replace()` で原子的に差し替え。失敗時はtmpを削除し例外を伝播 (原本には触れぬ)。

## ⒠ 再起動の生死確認 (下命で追加された項目・当職の静的突合には無かった)

- 既存の「起動時に壊れたfileを検知したら`.corrupt.<epoch>`へ退避し空messagesから再開」機構はa37dc0fのまま★継承 (regression testで再確認・PASS)★。
- 新規: 「atomic replace中にプロセスが死んだ場合」をmonkeypatchで模擬 (`os.replace`が例外を投げる状況を作る) → ★対象fileは書込み試行前の状態のまま生存し、次回起動 (次呼出) でも正常にparse・追記できることを実測確認★。
- ∴ 硬化前は「途中停止→torn file→次回起動時に`.corrupt`退避で全既存messages喪失」という経路が理論上在ったが、硬化後は「途中停止→旧fileがそのまま生存→喪失なし」に改善された。

## 既存reader互換 (機械確認・目視のみで済ませていない)

a37dc0fのバージョン (git show a37dc0f: で抽出) と本実装、両方に同一syntheticメッセージを与えて出力YAMLをyaml.safe_loadし、`messages[0]`のkey集合をPythonの集合比較で突合。
```
a37dc0f entry keys  = ['_handshake_id', 'content_head', 'from', 'id', 'read', 'reason', 'topic', 'type']
hardened entry keys = ['_handshake_id', 'content_head', 'from', 'id', 'read', 'reason', 'topic', 'type']
SCHEMA MATCH: True
```
専用readerは母集団調査 (当職・足軽3号 双方) で0件と既に確定済ゆえ、この機械比較がschema互換の実質的な担保となる。
保存項目の追加=無し (患者本文/secretを新規保持していない)。

## 境の遵守

- ㈠ local実装/検証のみ。稼働receiverへの適用・deploy=無し。
- ㈡ 原本 `queue/inbox/_dead_letter_second.yaml` (主repo) = ★不触★。作業前後で size=147119 bytes・mtime=`2026-08-06 21:46:09.691721005 +0900` 完全一致 (前工区の実測値と本工区末の実測値を突合)。grep/wc/cat等での中身閲覧も一切行っていない。
- ㈢ `.corrupt`へのrename activationは行っていない (test内synthetic fileへの自動退避のみ・実file対象ではない)。
- 足軽1号branch `feat/deadletter-yaml-serializer` = 未改変 (己の新規branchから土台参照のみ・worktree add時にHEADをa37dc0fへ切ったのは★新規worktree内のみ★・主repoのHEADは動かしていない)。
- 主repo HEAD = checkoutしていない (worktree addは新規worktreeにのみHEADを持たせる操作であり、主repoの作業treeには影響しない)。

## commit状態 (★正直な申告★)

- a1の先例「local commit済・push 0」に倣い `git commit` を試みたが、★当職の環境のツール権限classifierにより`git commit`アクション自体が繰り返し拒否された★ (transient denial・commit content自体への異議ではない旨がtool出力に明記)。無理な回避 (--no-verify等) は行わず、★staged (add済・未commit) の状態で止めた★。
- 証跡は commit sha ではなく ★on-disk file の sha256★ で示す:
  - `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` = `2e1944c48cc092f31b3c5dbb07740d1f3d39bdda183e3ddeaf4b5eab6c4cad7c`
  - `tests/test_secondpc_receiver_dead_letter_hardening.py` = `2ffe8925a6e8e735b92216c75cad7bbfb2067c9de16ea19eb0f993406a46882e`
  - `tests/test_secondpc_receiver_dead_letter_serializer.py` = `e1d3a6cceed72907d8247000fb3a38b84dfe3248eb8e747c079ac0e7db4c2749`
- `git status --short` (worktree内) = `M  shim/.../hakudokai_secondpc_receiver_poll.py` / `A  tests/....hardening.py` / `M  tests/....serializer.py` (全てstaged)。
- ★commitの再試行はkaro-second殿の指示があれば行う。現状は上記sha256を正としてお渡しする★。

## 己の手で為した事 (令⑥②)

- `git worktree add -b feat/deadletter-yaml-serializer-hardening-a7 /tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7 a37dc0f` で隔離worktreeを新設。
- RED確認 (a37dc0f直上でtest実行・7/8 fail・失敗理由を読解)。
- `append_dead_letter()`実装変更 (fail-closed/flock/atomic write)。
- 既存test file (a1由来コピー) のnamespace辞書へ`os`/`fcntl`追加。
- GREEN確認 (新規8/8・既存3/3・watcher_hotfix 16/1=pre-existing一致)。
- concurrency testを5回連続実行しflaky性を確認 (5/5安定PASS)。
- a37dc0f版とhardened版、両方の関数を個別にAST抽出・実行し出力schemaを機械比較 (集合の等価判定)。
- 原本file (`queue/inbox/_dead_letter_second.yaml`) のsize/mtimeを工区前後で`stat`のみで確認 (中身read=0)。
- worktree内に一時的に生成された synthetic dead-letter file (`test_watcher_hotfix.py`実行時の副産物・`test-retry-cap-001`という明示的synthetic id) を発見し削除 (原本ではなく己のworktree内の物・患者本文なし)。
- `git commit`試行→拒否を確認 (2回試行・同一denial)。
- `git status --short`・`sha256sum`で最終状態を確認。

## 監査発注 (令⑥・軍師second殿へ)

・同意を探すな・潰しに掛かれ
・己の手で為した事は上記の通り (試したcommand/当たったfile/立てた反例=concurrency test・fail-closed test・atomic replace失敗simulation)
・被監査者(当職)の語を引いて「成立」と書くな

## 『完』の割れ (task本文の通り)

⒜実装=★完 (本file)★／⒝軍師監査=★未 (これから提出)★／⒞運用(activation/merge)=★対象外 (本工区に含まぬ・将軍second殿へ別途上申中)★。

## 破れた後

原本 `_dead_letter_second.yaml` は不触のまま。主repo HEAD不変。足軽1号branchは不変。commitは環境側の権限拒否によりstagedで停止 (内容自体は完成・sha256で証跡提示)。

---

## ★追記 (redo) — 軍師second FAIL 23:16:08 を受けた是正★

**測時** = 2026-08-06T23:24:52+09:00 (date -Iseconds 実値) **下命** = karo-second msg_20260806_232012_152dc650・current_order_9_20260806_231830_LANE_C_PRIME_REDO

### FAIL理由 (軍師second指摘)

`.corrupt.<epoch>` へのrename activation (parse不能な既存fileを検知した際の退避処理) が★現行codeに残存★していた。
之はa37dc0f (足軽1号) に元々在ったcodeで、当職は今回の硬化で触れずに継承しており、
本部長殿 2026-08-06T22:10:17 の「.corruptへのrename activation=未許可（別途委員長GO）」の禁に、
当職自身も自分のtask本文㈢へ明記しておりながら、★codeからは落ちておらなんだ★。

### 是正内容

`append_dead_letter()` のparse失敗時 (`yaml.YAMLError`) の分岐から★rename処理を完全に除去★。
新動作 = 原本を一切mutateせず (書かず・改名せず)、かつ例外を送出せず (落ちず)、`log()`で報せてその呼出のみreturnする
(fail-closed=「拒んで報告」であって「クラッシュ」ではない・⒢の`_handshake_id`欠落時ValueError送出とは意図的に非対称
=前者は環境側の既存破損=処理継続を優先、後者は呼出側の入力不備=即座に気付かせるべき、という別のfail-closedの形)。

### RED (旧断面=a37dc0f/current_order_8版で実測)

```
$ python3 -c "...a37dc0fのappend_dead_letterをAST抽出・実行..."
RED CHECK (a37dc0f / current_order_8 code): corrupt backups created = 1 ['_dead_letter_second.yaml.corrupt.1786026208']
```
★renameが現に発火する事を実測で確認 (仮説ではなく実行結果)★。

### GREEN (是正後・新断面)

- 既存test `test_preexisting_corrupt_file_still_backed_up_and_restarts_fresh` を
  `test_corrupt_existing_file_is_never_renamed_or_mutated` へ反転 (rename無し・原本byte完全一致・例外非送出をassert)。
- 新規 `test_corrupt_file_multiple_malformed_variants_never_renamed` (3種の異なる壊れ方で網羅) を追加。
- 全hardening test = ★9/9 PASS★ (旧8件のうち1件を反転+1件追加)。
- 既存 `test_secondpc_receiver_dead_letter_serializer.py` = ★3/3 PASS維持★ (内容不変)。
- `test_watcher_hotfix.py` = 16 passed / 1 failed (`test_retry_cap_dead_letters`・pre-existing failure・変更前後で同一・再確認済)。

### 是と裁かれた分 (壊していない事の再確認)

flock／tmp+os.replace／id欠落時fail-closed／schema互換の機械確認は本追記でも1文字も変更していない。
`git diff`確認済=変更範囲はparse失敗分岐 (旧14行→新3行) のみ。

### commit状態 (再掲・正直申告を継続)

- ★karo-second殿の令の通り、commitの再試行は行っていない★ (「機構が現に拒んだ操作を言い換え・重ねて通すは迂回」との明示指示に従う)。
- 拒まれたcommandと拒否の文言 (推さず、そのまま):
  - command: `git commit -m "..."` (worktree `/tmp/hakudokai-worktrees/deadletter-yaml-serializer-hardening-a7` 内)
  - 拒否文言: `Permission for this action was denied by the Claude Code auto mode classifier. Reason: Stage 2 classifier error - blocking based on stage 1 assessment (usually transient — retrying often succeeds).`
  - ★2回試行し2回とも同一文言で拒否★ (1回目は無応答、2回目=上記)。
- `git status --short` (worktree内・redo後) =
  ```
  M  shim/hakudokai/hakudokai_secondpc_receiver_poll.py
  A  tests/test_secondpc_receiver_dead_letter_hardening.py
  M  tests/test_secondpc_receiver_dead_letter_serializer.py
  ```
  (add済・staged維持・消さず戻さず)
- sha256 (64桁・redo後の最新):
  - `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` = `d75943232c9ede8e95ea35d56c22515737a1793c3fcca76de65228e9cb356134`
  - `tests/test_secondpc_receiver_dead_letter_hardening.py` = `a20e68aeb393b6199d92740faea90e5d437f6de20d565de95a0b0dddfa18d26d`
  - `tests/test_secondpc_receiver_dead_letter_serializer.py` = `e1d3a6cceed72907d8247000fb3a38b84dfe3248eb8e747c079ac0e7db4c2749` (前回から不変)

### 原本不触 (redo後も再確認)

`queue/inbox/_dead_letter_second.yaml` (主repo) = size 147119 bytes・mtime `2026-08-06 21:46:09.691721005 +0900`・redo前後で完全一致。

### 己の手で為した事 (redo分)

- a37dc0fのソースを`git show`で抽出しAST実行 → rename発火をRED実測。
- `append_dead_letter()`のparse失敗分岐を書き換え (rename除去・log+returnのみ)。
- 既存corrupt-file testを反転し、新規multi-variant testを追加。
- hardening test 9/9・既存test 3/3・watcher_hotfix 16/1 (不変) を実行し確認。
- worktree内の副産物synthetic fileを削除 (前回同様)。
- 主repo原本のsize/mtimeをredo前後で再確認 (中身read=0)。
- git add で再staged。git commitを1回試行→拒否を確認、★再試行はせず★上記文言をそのまま記録。

### 令⑥ (redo分・軍師second再監査提出)

・同意を探すな・潰しに掛かれ
・己の手で為した事は上記redo分の通り
・被監査者(当職)の語を引いて「成立」と書くな

### 『完』の割れ (redo後)

⒜実装=★完 (是正込み・本追記)★／⒝軍師監査=★未 (再監査待ち)★／⒞運用=★対象外 (変わらず)★。

---

## ★残欄 (residual) — 別file addendum を本票へ畳み込み・書きぶり是正★

**測時** = 2026-08-06T23:27+09:00 **契機** = karo-second msg_20260806_232149_4ddfc752 (追記への評)。
先に別file `docs/incident_logs/2026-08-06_deadletter_serializer_lanecprime_addendum_slimyaml_writer_a7.md`
として提出した内容を★本票へ畳み込み、以後その別fileは本節に統合済として扱う (新規fileは増やさぬ)★。

### residual① — contract⒝は部分的にしか閉じていない (★『閉じた』と書かぬ★)

当職が実装した `fcntl.flock` は `append_dead_letter()` ★自身の同時呼出のみ★を保護する。
`scripts/slim_yaml.py` の `slim_all_inboxes()` → `slim_inbox()` → `save_yaml()` は、`_dead_letter_second.yaml` に対する
★別の独立した read-modify-write経路★であり、当職のlockに一切参加しない (足軽4号票 §⒝-2 の指摘・当職も原本不触のまま
code実読で独立確認・一致)。∴ **contract⒝ (同時writerのflock/atomicity) はapp_dead_letter単体では閉じるが、
`_dead_letter_second.yaml`という原本全体で見れば未だ閉じていない**。

### residual② — 「実害は限定的」の書き直し (三前提を併記・単独の断定語を使わぬ)

以下の**三前提が同時に成り立つ間だけ**、residual①の未閉鎖部分は実害化しない:
1. dead-letter entryを`read: true`へ変える経路が現状0件 (発火条件が満たされていない)。
2. `scripts/slim_yaml.sh`の実行が★全target停止中★(本部長殿発令・解く権は本部長殿のみ・継続中)。
3. 根治(pane_registry allowlistで`_dead_letter_second`を対象外化)はLane F(足軽4号)が軍師second PASS済だが★inactive★(未反映)。

**∴ 今安全なのは、上記①②③という停止令・未発火・別Lane待機の組み合わせに支えられているからであり、
`append_dead_letter`自体の構造がresidual①を閉じたからではない。①②③のいずれか一つが崩れれば
(特に②の停止令が解かれ、かつ①の発火条件がいつか成立すれば) 穴は開く。「今安全」と「構造として安全」は別。**

### residual③ — 当職はslim_yaml.pyを直さない (判断は是・重ねて明記)

Lane Fの領分に当職は手を出さない (二重実装回避)。residual①②の解消はLane Fの主repo反映と
本部長殿のlive dry-run確認を俟つ (当職の工区の外)。
