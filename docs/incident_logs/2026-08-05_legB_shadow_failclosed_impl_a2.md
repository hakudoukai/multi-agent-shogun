# leg B — 影の箱 fail-closed 実装 (足軽2号)

- **工区**: `subtask_shadow_failclosed_legB_a2_20260805`
- **発令書**: `docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md` (sha256 先頭16 `fb446d5b78a60fe7` — 己で `sha256sum` を打ち一致確認済)
- **base_commit**: `502cbfe`
- **報告先**: karo-second
- **blocked_by**: leg C (`subtask_shadow_failclosed_legC_a3_20260805`・完了済・当職が独立に受入契約として使用)

## 1. 成果物

- **path (絶対)**: `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`
- **行数**: 450 (旧 321 行から +271/-141 行差分)
- **sha256**: `61b893f699e86aefc86283ee97d775f0c77287112bc994d27604e97923e2a001`
- 既存 file の書換 (leg B の性質上、共有 script 本体の修正が必達。W25 当時の「新規 file のみ」制約は本工区には非適用 — 発令書 §2 の禁止事項5点にも「既存 file 書換禁」は含まれず)。

## 2. ★moving target 事案 (発生・検知・対応を記す)★

着手時に読んだ受入契約 `tests/test_shadow_mailbox_failclosed.bats` は leg C 成果物報告記載の
sha256 `ae93b8cda8a50abbaf5ab44488d69ef378e4a2a51affc6c75c6afbb893bc390a` (168行) で、
己の `sha256sum` 実測でも一致確認して着手した。

実装完了後の実行確認時、**同一 path が 227 行・sha `758ab789961705625c0f6a276ab2bc1f85416c4f2d89d6a628980edc6e71a2db`
へ変わっており申した** (`SMFC-SCHEMA1`/`SMFC-SCHEMA2` の2件が追加)。新設テストのコメントに
「軍師second 監査 FAIL 是正 (2026-08-05)」とあり、当職の着手後・完了前に第三者 (推定 a3 または
karo-second) が是正を加えたものと判ず。

**己の対応**: 契約を写して実装を合わせるのではなく、★新設2件が何を要求するかを読んで検証★=
`SMFC-SCHEMA1` は「実 registry と形が近いが違う物 (`pane_registry:` の一段が無い flat `panes:`)」
を canon 判定源として誤って通してしまわぬ事を要求。当職の初版実装 (`find_panes()` で
dict を再帰的に探索し `panes` キーを持つ最初の物を拾う設計) は★この形も誤って受理してしまう
欠陥を持っていた★ (実測: 実行して `not ok 7` を確認)。

## 3. 【本工区で 己が直した誤り】

**有り、1件**: 上記 moving target で検出された自身の実装欠陥。

- **誤り**: canon 出所の探索を `pane_registry.panes[].agent_id` という★厳密な一段★ではなく、
  dict を再帰的に降りて `panes` という名のキーを持つ任意の階層を拾う★寛容な探索★にしていた。
  結果、トップレベル直下に `panes:` を置いた「形は近いが違う」registry も canon 判定源として
  誤って受理してしまう (fail-closed の趣旨に反し、canon 判定が「何を読んでいるか」を機械的に
  保証していなかった)。
- **直し方**: `data.get('pane_registry')` が dict かつ `.get('panes')` が list である事を
  明示的に検査する、厳密な一段のみを canon 出所として受理する形へ変更 (`scripts/inbox_write.sh`
  内 `_canon_lookup()`)。
- **直した後の実測**: `SMFC-SCHEMA1`/`SMFC-SCHEMA2` を含む全8件を実行し `ok` を確認 (下記§4)。
- **『道具の出力は道具の判定にあらず』の適用**: bats の `ok`/`not ok` を鵜呑みにせず、
  修正前後で同一コマンドを2度実行し (`not ok 7` → 修正 → `ok 7`)、差分が★己の変更のみに
  起因する事★を確認した (registry 内容・test 本体は修正前後で不変)。

## 4. 実行して確かめた記録 (「緑の筈」は証に非ずを踏まえ)

```
$ bats tests/test_shadow_mailbox_failclosed.bats
1..8
ok 1 SMFC-B: valid canon target (ashigaru1) is delivered unchanged (positive control)
ok 2 SMFC-A1: shadow target (ashigaru-second-1) is rejected, not silently written
ok 3 SMFC-A2: shadow target rejection is returned to a resolvable FROM's own inbox
ok 4 SMFC-C: unroutable target AND unresolvable FROM is escalated, not silently dropped
ok 5 SMFC-D1: healthy zero-violation accept leaves an explicit canon-check-ran marker
ok 6 SMFC-D2: canon registry unreadable → fail-closed reject with a detector-dead marker (not a silent allow)
ok 7 SMFC-SCHEMA1: wrongly-shaped registry (flat top-level panes:, no pane_registry: wrapper) is NOT accepted as canon source
ok 8 SMFC-SCHEMA2: canon set is driven by the actual overridden registry content, not a hardcoded/fallback list
```

exit code = 0。**8/8 GREEN**、(a)(c)(d)(SCHEMA1)(SCHEMA2) が赤→緑に転じ、**(b) 陽性対照は緑のまま** (発令書 §5 必達を充足)。

## 5. 実装の要旨 (契約4条との対応)

1. **canon 出所** = `INBOX_WRITE_CANON_REGISTRY` (env、既定 `$SCRIPT_DIR/queue/pane_registry.yaml`) の
   `pane_registry.panes[].agent_id` の★厳密な一段のみ★ (§3 の是正後)。
2. TARGET が canon 外 → exit 非0・`queue/inbox/<TARGET>.yaml` は書かれない。
   - FROM が canon 内 → FROM 自身の inbox へ `type=delivery_failed` の返送便 (「宛先不明」
     「<TARGET>」「有効な宛先の一例 (ashigaru1)」を含む)。実装は既存の書込ロジックを
     `_write_message()` 関数へ切り出し、TARGET 用にもこの返送便用にも共用 (二重実装を避けた)。
   - FROM も canon 外 → `queue/dead_letter/_unroutable/` 配下に新規記録 (TARGET/FROM 双方を含む)。
     既存の宛先 inbox には触れない (「存在せぬ送り主の inbox を勝手に作る」= 新たな影を生む、
     という leg C の廃案理由をそのまま踏襲)。
3. registry が読めぬ/形が違う時は fail-closed (allow ではなく reject)、stderr に
   `DETECTOR_UNAVAILABLE` を出す (§3 の是正含む)。
4. canon 内 TARGET を通す時は stderr に `canon_check` と `OK` を残す。

## 6. 壊れた試験の件数 (★是正の代価・隠さず全数列挙★)

**前提**: 既存の regression 3 suite (`tests/test_inbox_write.bats` / `tests/test_inbox_expiry_supersession.bats`
/ `tests/agent_selfwatch.bats`) は、`scripts/inbox_write.sh` を sandbox 化する際
(`SCRIPT_DIR` を tmp へ retarget) に**独自の `queue/pane_registry.yaml` を配置していない**
(leg C の `test_shadow_mailbox_failclosed.bats` だけが実 registry を sandbox へ複製する設計)。
∴ fail-closed 導入後、これらの sandbox は★registry 不在=detector dead★を実際に踏み、
新規に赤へ転ずる。★これは是正の代価であり、当職の実装欠陥ではない★ (根拠: 下記の
「己の変更を stash して baseline と比較」実測で、原因が 100% 「sandbox に registry が無い事」
に帰着する事を確認済み)。

### 6-1. `tests/test_inbox_write.bats` — 14件中 **10件が新規に赤**

実行して確認 (修正前後で `git stash` により己の diff のみ on/off し baseline と比較):

- **新規に赤 (10件、原因=同一・sandbox に `queue/pane_registry.yaml` 不在)**:
  T-002c (self-send REJECTED 文言未達) / T-003 (新規書込) / T-004 (追記) / T-005 (ID一意性) /
  T-007 (custom type/from) / T-008 (overflow 50件) / T-009 (overflow unread保護) /
  T-010 (flock 並行書込) / T-011 (特殊文字) / T-012 (ディレクトリ自動作成)
- **不変で緑 (4件)**: T-001 (無引数) / T-002 (content欠落) / T-002b (type/from欠落) / T-006 (type/from欠落・デフォルト値)
  — いずれも★引数検証段階で exit 1 する物★で canon チェックへ到達する前に落ちるゆえ影響なし。

### 6-2. `tests/test_inbox_expiry_supersession.bats` — **1件が新規に赤 (LB-09)**

- **新規に赤**: LB-09 (`inbox_write` integration・expires_at/supersedes round-trip) — 同一原因。
- **baseline から既に赤 (当職の変更と無関係、stash比較で確認済)**: LB-07 (`clear_command` 消費regression) —
  当該 file は git status 上★既に他エージェントにより dirty (M)★であり、当職は不触。
  stash 比較で「己の変更を外しても LB-07 は赤のまま」を実測、誤帰属を避けた。

### 6-3. `tests/agent_selfwatch.bats` — **1件が新規に赤 (TC-FR-014 + TC-NFR-002)**

- **新規に赤**: TC-FR-014 + TC-NFR-002 (`inbox_write` IF/schema backward compat) — 同一原因。
- **baseline から既に赤 (当職の変更と無関係)**: TC-FR-003 (`get_unread_info` routing) —
  同ファイルも git status 上★既に dirty (M)★、stash比較で当職の変更と無関係と確認済。

### 6-4. 合計

**新規に赤へ転じた試験 = 12件** (10 + 1 + 1)。**全12件が単一の同じ根本原因** (sandbox が
`queue/pane_registry.yaml` を持たぬ) に帰着する事を、stash による on/off 比較で実測済み
(推測で束ねていない)。**当職はこれら3 file を一字も編集していない** (うち2件は他エージェントの
作業中 file であり不触が適切、1件 (`test_inbox_write.bats`) は clean だが、fail-closed 導入は
これらの sandbox fixture 更新を要する不可分の帰結であり、その判断は当職の権限を超えると判じ
karo-second へ上げる)。

## 7. 影響範囲の限定 (leg C 陽性対照 + 実 repo 確認)

- `SMFC-B` (陽性対照) は緑のまま (§4)。
- 実 `queue/inbox/*.yaml` は一切書き換えていない (全試験は sandbox `$TEST_TMPDIR` 内で実行、
  実 `scripts/inbox_write.sh` 自体も bats の `sed` retarget コピー越しにのみ実行される)。
- 影 file (`ashigaru-second-1〜7.yaml`) の mtime/サイズ不変を実測済み (下記§9)。

## 8. 【この工区と対に成る他工区】

- **leg A** (ashigaru5・滞留便 `ashigaru-second-1.yaml` の `msg_20260804_163553_7fb42f79` 救出): 別 leg、当職は不触・進捗未確認 (探した範囲 = 本工区スコープ外につき `queue/tasks/ashigaru5.yaml` 等は未読)。
- **leg C** (ashigaru3・負テスト設計・`subtask_shadow_failclosed_legC_a3_20260805`): 本工区の受入契約そのもの。完了済 (§2 の moving-target 追補を含め当職が実行して確認)。

## 9. 禁止事項の遵守 (自己申告)

- **影 file 不触・不消去**: `git status --short queue/inbox/ashigaru-second-*.yaml` は無変更 (追跡外ゆえ出力なし)、`ls -la` で mtime 不変を実測 (`ashigaru-second-1.yaml` = Aug 4 16:35、`-2〜-7` = Aug 3 16:17、いずれも本工区着手前の値のまま)。
- `dd189-respawn-secondpc-claude-to-third8080.sh` 不触・不実行。
- process 不触 (kill/restart/tmux 操作なし)。
- **commit / push / stage なし**: `git diff --cached --stat` = 空出力で確認済み。
- **scope 拡大なし**: 新規作成 file はこの報告書のみ (leg A/C の precedent と同型)。既存 file 編集は契約で必達の `scripts/inbox_write.sh` 1本のみ。他の regression suite 3 file は§6の通り一字も編集していない。

## 10. 監査体制

**二者制** (Codex leg は SAFETY 裁定 seq132707 により停止中)。三者と書かない。
本報告は監査提出前段階 (karo-second 受理 → 将軍second review → 委員長殿 commit、発令書
completion_definition 準拠)。

---

## 11. 追補 — 契約拡張 (是正三点目・resolvable FROM) への対応 (2026-08-05 11:0x)

**契機**: karo-second 便 `msg_20260805_110248_a13f9b69` (2026-08-05T11:02:48・未読で着信)。
将軍second 具申 (karo-second 実測裏付け) を踏まえ、受入契約が「FROM が canon 帰属のみ」
から「FROM が canon ★かつ★ 読む者が居る証拠 (inbox file mtime 鮮度)」へ拡張された。
受入契約 = `tests/test_shadow_mailbox_failclosed.bats` **314行 / sha256先頭16=`11f82cb7e34aeb38`**
(己の `sha256sum` 実測で一致確認済)。karo-second 自身の実行報告 (8緑+2赤=SMFC-C2/SMFC-C3)
を、着手前に己でも再実行し同一結果を確認した上で着手した。

### 11-1. 何を実装したか

`scripts/inbox_write.sh` に `_from_resolvable()` を新設 (既存 `_canon_lookup` の
FROM_OK/FROM_BAD = 純粋な canon 集合帰属は変更せず、別軸として追加):

- 戻り値 0 = resolvable (FROM の inbox file が存在し mtime が閾値内)
- 戻り値 1 = unresolvable — 箱が一度も作られておらぬ (file 不在。honda/sanada 実測を模す)
- 戻り値 2 = unresolvable — 箱は在るが mtime が閾値超 (長期停滞。shogun/gunshi/karo 実測を模す)

`TARGET_BAD` 分岐を「FROM_OK なら常に返送」から「FROM_OK **かつ** resolvable のみ返送、
それ以外 (FROM_BAD、または FROM_OK だが unresolvable) は dead-letter escalate」へ変更。
dead-letter の `reason` フィールドを3値に分岐 (`unroutable_target_and_unresolvable_from` /
`target_non_canon_from_canon_but_inbox_never_created` /
`target_non_canon_from_canon_but_inbox_stale`) し、escalate の**機序**を後から読む者が
区別できるようにした (本サイクル規律 5「似た物を並べる時は同種と見た根拠を書け」の適用—
「どちらも escalate された」は結果、機序は3通り別)。

閾値既定値 = **86400秒 (24h)**、`INBOX_WRITE_STALE_READER_SECONDS` で上書き可 (契約通り)。
**この既定値は当職の判断であり一意の正解ではない** (発令書の但し書きに倣う) — 根拠は
台帳実測 (`karo-second_day_ledger.md` 記載の空箱停滞が 07-02/05-09 起点＝月単位) が
「日」を明確に超えており、24h は「今日活動した箱」と「長期停滞箱」を分ける保守的な線と
判じた。より正確な指標がある場合は karo-second へ差分提案の上で置換可 (契約文言どおり)。

**★追記 (2026-08-05 11:1x・karo-second 便 `msg_20260805_111105_58ed631b` 受・軍師second FAIL 反映)★**:
上記 mtime 方式は **軍師second が FAIL** と判じ、karo-second が実測で裏を取った (当職の
11:08:19 報告と軍師の 11:05:03 FAIL は交差=当職に咎なし・契約が後から覆った)。
- **mtime を採った理由**: 「箱への直近の触れ」を安価に得られる既存の filesystem 属性であり、
  「読む者が居るか」の実測代理指標として最短距離に見えたゆえ (§11-1 本文)。
- **軍師が否認した理由**: **mtime は WRITE で進み READ では進まぬ**。かつ **fail-closed の
  返送便それ自体が対象 file の mtime を新しくし得る** ため、「書かれた事」を「読まれた事」と
  取り違える★循環★が生じる (本サイクル一日の主題「書かれるが読み返されぬ」の型そのもの)。
  ∴ 86400秒という**閾値の長さの当否ではなく、測っている物自体が違う**という指摘。
- **代替材料 (karo-second 実測・足軽3号が四巡目契約で正式化予定)**: `read:true` 遷移を用いる
  — read:true を書くのは読み手自身であり (mtime と異なり「読んだ」を直接意味する)、かつ
  fail-closed の返送便自体は `read:false` で入るため自己の signal を汚さぬ (循環が断たれる)。
- **当職の対応**: 書いた `_from_resolvable()` の枠組み (canon∧resolvable でのみ返送、
  それ以外は dead-letter escalate という分岐構造・戻り値3値の設計) は**捨てない**。
  内部の判定材料 (mtime 鮮度 → read:true 遷移) のみを、足軽3号の是正版契約を待って
  差し替える。**現時点では実装を変更していない** (指図⑵に従い contract 待ち)。
- **裁可の逐語 (2026-08-05T11:21:24・karo-second 便 `msg_20260805_112124_f1ab4574` 中継・
  委員長殿裁定)**: 「★『(c)は「黙って捨てず ★上げる★」と定めた。★上げる先を file と
  限定していない★。∴ non-zero exit + stderr で 呼び手へ返すのは ★字義どおりの「上げる」★
  である。★凍結を一切 動かさない★』★」— これにより「戻り値終端 (non-zero exit + stderr
  UNROUTABLE_ESCALATED) を主契約とする」設計が★scope 拡大ではなく字義内★と確定した
  (下記 §12 で実装・下記 §12-4 の通り終端自体は未検証のまま残る)。

### 11-2. 【本工区で 己が直した誤り】(追補分)

**無し** — 今回は契約拡張への新規対応であり、既存実装 (§3 記載分) への追加誤り修正は無い。
契約拡張前の実装 (§1-§10) は当該拡張前の契約に対して 8/8 緑であり、拡張後の契約が
新たに要求する `_from_resolvable()` を素直に追加した (既存の TARGET_OK 経路・
FROM_BAD×TARGET_BAD 経路・D1/D2/SCHEMA1/SCHEMA2 経路には触れていない)。

### 11-3. 実行して確かめた記録 (拡張後・全10件)

```
$ bats tests/test_shadow_mailbox_failclosed.bats
1..10
ok 1 SMFC-B: valid canon target (ashigaru1) is delivered unchanged (positive control)
ok 2 SMFC-A1: shadow target (ashigaru-second-1) is rejected, not silently written
ok 3 SMFC-A2: shadow target rejection is returned to a resolvable (canon + actively-read) FROM's own inbox
ok 4 SMFC-C: unroutable target AND unresolvable FROM is escalated, not silently dropped
ok 5 SMFC-C2: canon FROM whose inbox file has never been created (no reader ever) is treated as unresolvable, escalated
ok 6 SMFC-C3: canon FROM whose inbox is stale (mtime beyond threshold, no recent reader activity) is treated as unresolvable, escalated
ok 7 SMFC-D1: healthy zero-violation accept leaves an explicit canon-check-ran marker
ok 8 SMFC-D2: canon registry unreadable → fail-closed reject with a detector-dead marker (not a silent allow)
ok 9 SMFC-SCHEMA1: wrongly-shaped registry (flat top-level panes:, no pane_registry: wrapper) is NOT accepted as canon source
ok 10 SMFC-SCHEMA2: canon set is driven by the actual overridden registry content, not a hardcoded/fallback list
```

exit code = 0。**10/10 GREEN**。SMFC-B (陽性対照) は緑のまま (§4 との比較で不変)。

### 11-4. 壊れた試験の件数 (拡張後・再実測)

同じ3 regression suite を再実行し、§6 記載の12件と**完全一致**することを確認した
(増減なし・新規に壊れた試験なし):

- `tests/test_inbox_write.bats`: 同じ10件が赤 (T-002c/T-003/T-004/T-005/T-007/T-008/T-009/T-010/T-011/T-012)
- `tests/test_inbox_expiry_supersession.bats`: 同じ1件 (LB-09) が新規に赤・LB-07 は§6同様 baseline 赤 (他エージェント dirty file・不触)
- `tests/agent_selfwatch.bats`: 同じ1件 (TC-FR-014+TC-NFR-002) が新規に赤・TC-FR-003 は§6同様 baseline 赤 (不触)

**合計 12件で不変**。本追補で新たに壊した試験は **0件**。

### 11-5. 成果物 (更新後の断面)

- **path (絶対)**: `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`
- **行数**: 498 (§1 時点 450 行から +48/-0 行付近の差分。実差分は `_write_dead_letter` の
  reason 引数化 + `_from_resolvable()` 新設 + `TARGET_BAD` 分岐の拡張)
- **sha256**: `d57314f76b4ccbe8ba2dc3cbf324330a112a554c29d90207f8423412fc5c5157`
- HEAD (`83bdb61`) からの累積差分 (§1 分含む): `git diff --stat` = 460 insertions(+), 141 deletions(-)

### 11-6. 禁止事項の遵守 (追補分・再確認)

- **影 file 不触・不消去**: `ls -la queue/inbox/ashigaru-second-*.yaml` mtime 再実測 — §9 記載値
  (`ashigaru-second-1`=Aug 4 16:35、`-2〜-7`=Aug 3 16:17) から**不変**を確認。
- **実 queue/inbox 不触**: `git status --short queue/inbox/` = 空出力 (追跡外・変化なし)。
- `queue/dead_letter/_unroutable/` は**実 repo には作られていない** (`ls` = No such file or
  directory — 全試験は sandbox `$TEST_TMPDIR` 内で実行される事の確認)。
- **commit / push / stage なし**: `git diff --cached --stat` = 空出力。
- **scope 拡大なし**: 新規 file 作成は本追補では 0件 (既存の報告書 1本へ追記のみ)。

### 11-7. 【この工区と対に成る他工区】(追補分)

- **leg A** (ashigaru5): §8 と不変・当職不触・進捗未確認。
- **leg C** (ashigaru3): 是正三点目の契約拡張元。本追補はその契約を満たす実装対応であり、
  対をなす関係が§8時点よりさらに直接的になった (契約 v2 ⇄ 実装 v2)。

### 11-8. 次工程

karo-second 受理側疑義 → 将軍second review → 委員長殿 commit (発令書 completion_definition
準拠、不変)。本追補をもって leg B の受入契約 (是正版・10件) への対応は完了と判ずるが、
**裁定は当職の権限を超える** — karo-second の受理判断を仰ぐ。

---

## 12. 追補2 — read:true 遷移への差し替え + 委員長裁可 (2026-08-05T11:2x)

**契機**: karo-second 便 `msg_20260805_112124_f1ab4574`。受入契約 (最終版) =
`tests/test_shadow_mailbox_failclosed.bats` **405行 / sha256先頭16=`9bf59617d1672d6b`**
(己の `sha256sum` 実測で一致確認済)。karo-second 自身の実行報告 (7緑+4赤=C・C2・C3・C4)
を着手前に己でも再実行し同一結果を確認した上で着手した。完了条件=赤4件を緑に転じ、7緑を
緑のまま保つ事。

### 12-1. 何を実装したか

`_from_resolvable()` の判定材料を **mtime → `read:true` 遷移** へ差し替えた
(枠組み=canon∧resolvable でのみ返送・それ以外は dead-letter escalate、という §11-1 の
分岐構造・戻り値3値は不変):

- 戻り値 0 = resolvable — FROM の inbox に `read: true` の便が1件以上あり、
  その中の最新 `timestamp` が閾値 (`INBOX_WRITE_STALE_READER_SECONDS`、既定86400秒) 以内
- 戻り値 1 = unresolvable — 箱が一度も作られておらぬ／messages が空／`read:true` が一件も無い
  (C4 の「新着だが未読のみ」もここに含まれる — 未読がいくら積もっても resolvable にならぬ)
- 戻り値 2 = unresolvable — `read:true` 履歴は在るが最新 timestamp が閾値超 (長期停滞)

timestamp は既存 message 書式と同じ naive local (`%Y-%m-%dT%H:%M:%S`)、`datetime.now()`
との比較も同じ naive local (契約の指定どおり、tz 変換していない)。`read:false` の便
(fail-closed の返送便自身を含む) は一切この判定に寄与しない — mtime 循環を断つ核心。

併せて escalate 分岐 (`TARGET_BAD` かつ FROM 非 resolvable) の stderr 文言を、契約の
主契約 (load-bearing) に合わせ `UNROUTABLE_ESCALATED: target=<TARGET> from=<FROM>
(reason=<reason>) dead_letter=<path>` の形へ変更 (非0 exit + stderr の明示印。
`queue/dead_letter/_unroutable/` への記録は補助的な法医学記録として維持するが、
それ単体が読み手を保証すると主張しない、契約 §(c) の格下げをそのまま反映)。

### 12-2. 【本工区で 己が直した誤り】(追補2分)

**無し** — 今回は契約の是正 (mtime→read:true) を素直に反映した差し替えであり、
新規の実装欠陥は検出していない (§3・§11-2 の枠組みは変更せず、判定材料と
escalate 時の stderr 文言の2箇所のみを差し替えた)。

### 12-3. 実行して確かめた記録 (差し替え後・全11件)

```
$ bats tests/test_shadow_mailbox_failclosed.bats
1..11
ok 1 SMFC-B: valid canon target (ashigaru1) is delivered unchanged (positive control)
ok 2 SMFC-A1: shadow target (ashigaru-second-1) is rejected, not silently written
ok 3 SMFC-A2: shadow target rejection is returned to a resolvable (canon + evidenced-read) FROM's own inbox
ok 4 SMFC-C: unroutable target AND unresolvable FROM is escalated, not silently dropped
ok 5 SMFC-C2: canon FROM whose inbox file has never been created (no reader ever) is treated as unresolvable, escalated
ok 6 SMFC-C3: canon FROM with read:true history but stale (latest read timestamp beyond threshold — 'was active, now stopped') is unresolvable, escalated
ok 7 SMFC-C4: fresh UNREAD traffic in FROM's inbox must NOT count as reader evidence (closes the mtime-style circularity at the message level)
ok 8 SMFC-D1: healthy zero-violation accept leaves an explicit canon-check-ran marker
ok 9 SMFC-D2: canon registry unreadable → fail-closed reject with a detector-dead marker (not a silent allow)
ok 10 SMFC-SCHEMA1: wrongly-shaped registry (flat top-level panes:, no pane_registry: wrapper) is NOT accepted as canon source
ok 11 SMFC-SCHEMA2: canon set is driven by the actual overridden registry content, not a hardcoded/fallback list
```

exit code = 0。**11/11 GREEN**。赤4件 (C/C2/C3/C4) が緑に転じ、既存7緑 (SMFC-B含む陽性対照) は
緑のまま (完了条件を充足)。

### 12-4. 壊れた試験の件数 (差し替え後・再実測 — かつ★己の変更の帰属を分離実測★)

同じ3 regression suite を再実行し、§6/§11-4 記載の**12件と完全一致**することを確認した
(増減なし・本差し替えで新規に壊した試験は0件)。

- `tests/test_inbox_write.bats`: 同じ10件が赤 (T-002c/T-003/T-004/T-005/T-007/T-008/T-009/T-010/T-011/T-012)
- `tests/test_inbox_expiry_supersession.bats`: 同じ1件 (LB-09) が赤・LB-07 は baseline 赤
  (他エージェント dirty file・不触)
- `tests/agent_selfwatch.bats`: 同じ1件 (TC-FR-014+TC-NFR-002) が赤・TC-FR-003 は baseline 赤 (不触)

**帰属の実測 (『壊れた試験』は道具の出力を鵜呑みにせず実測する、鉄則の適用)**:
本差し替え分の `_from_resolvable()` 差分だけを反実仮想的に戻した版 (mtime 版) を
一時ファイルへ再構成し同じ3 suite を実行 → 結果は差し替え前後で**一致**
(§6 の12件と1件も違わず)。∴ この12件は本追補2の変更に起因せず、§6 で既に
「原因=sandbox に `queue/pane_registry.yaml` 不在」と特定済みの★同一の既知欠落★に
帰着する (§11-4 からも不変)。

**合計 12件で不変。本追補2で新たに壊した試験は0件**。

### 12-5. ★終端は未だ検証されておらぬ (委員長殿御指摘・実装は進めてよいが「閉じた」と
     報ずるのは測定の後)★

karo-second 中継の委員長殿実測: `scripts/inbox_watcher.sh` **L1620-1621** に
`bash "$SCRIPT_DIR/scripts/inbox_write.sh" ... 2>/dev/null || true` という呼び出しが
実在する (己も該当行を読取専用で確認済・**不触**)。この呼び手は stderr を握り潰し
(`2>/dev/null`) かつ exit code も無視する (`|| true`) — ∴ 本工区が主契約とした
「non-zero exit + stderr の `UNROUTABLE_ESCALATED`」は、★この呼び手には一切届かぬ★。
`|| true` の直前コメント (L1611) 自体が「no-match grep の exit 1 を意図的に握り潰す」
目的で書かれた物であり、その `|| true` の射程が下流の `inbox_write.sh` 呼出しにまで
及んでしまっている (射程の意図せぬ漏れ)。

**∴ 本工区の実装 (§12-1) は完了しているが、「(c) は閉じた」という主張は★未だできぬ★**
— 足軽3号の「呼び手の全数列挙」(委員長殿がこの1件を先に見付けたのみで、他に同型の
呼び手が在るか未確認) が出るまで、終端の主張は保留する。この点は当職の実装欠陥ではなく
契約の射程 (呼び手側の網羅) が別工区であるゆえ、混同せず分けて記す。

### 12-6. 禁止事項の遵守 (追補2分・再確認)

- **影 file 不触・不消去**: `ls -la queue/inbox/ashigaru-second-*.yaml` mtime 再実測 — §9/§11-6
  記載値から不変。
- **実 queue/inbox 不触**: `git status --short queue/inbox/` = 空出力 (追跡外・変化なし)。
- `dd189` 不触・process 不触 (kill/restart/tmux操作なし)。
- **commit / push / stage なし**: `git diff --cached --stat` = 空出力。
- **scope 拡大なし**: 新規 file 作成は0件 (本報告書への追記のみ)。
  `scripts/inbox_watcher.sh` L1620-1621 は§12-5で読取専用に言及したのみで**一字も書換えていない**
  (git diff で確認可能 — 当職の変更範囲は `scripts/inbox_write.sh` のみ)。

### 12-7. 【この工区と対に成る他工区】(追補2分)

- **leg C** (ashigaru3・是正三点目の契約拡張元): §11-7 と不変。
- **足軽3号「呼び手の全数列挙」(委員長殿御指摘起点・工区IDは karo-second 側で採番予定)**:
  本工区の「戻り値終端」契約が★実際に呼び手へ届くか★を検証する対工区。§12-5 の保留は
  この工区の完了を待って解ける (本工区の実装そのものはこの工区をブロックせず先行できる、
  との karo-second 裁可済 — 「実装は進めてよい・『閉じた』と報ずるは測定の後」)。

### 12-8. 成果物 (最終断面)

- **path (絶対)**: `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`
- **行数**: 527
- **sha256**: `2e8c1d4a6eb50411f0e5419ed1a98d0de3e4632c4a0b3f8c970f6916f4f7c83f`
- HEAD (`502cbfe`) からの累積差分: `git diff --stat HEAD -- scripts/inbox_write.sh` =
  348 insertions(+), 141 deletions(-)

### 12-9. 次工程

karo-second 受理側疑義 → 将軍second review → 委員長殿 commit (発令書 completion_definition
準拠、不変)。本追補2をもって leg B の受入契約 (最終版・11件) への対応は完了と判ずるが、
**「(c) の終端が閉じたか」の裁定は§12-5の通り保留**、かつ受理そのものの裁定は当職の権限を
超える — karo-second の受理判断を仰ぐ。ETA 即返す。
