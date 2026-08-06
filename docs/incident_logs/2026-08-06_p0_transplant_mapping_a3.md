# P0 根治済み差分「そのまま持てる形」抽出 (足軽3号)

**下命**: karo-second msg_20260806_101557_a038a13d (10:15:57)「当repo 側の 根治済み差分を『そのまま持てる形』に 抽出」
**測開始**: 2026-08-06T10:18:19+09:00 (`date -Is`)・**測終** 2026-08-06T10:21:49+09:00
**当repo HEAD (測終時点)**: `f3bbecb926f0596adbd249a9682920e8302203fc` (作業中に karo-second 側 commit が進み HEAD が動いた可能性あり。本file の実測は各コマンド直前に取り直しており、行番号・sha は個々の実測時点のものを正とする)
**newbuild HEAD (参考・読取のみ)**: `a54c6f00212b3d030aabde63112353549f41a2e0`

**禁の遵守申告**: ★newbuildへ一文字も書いていない(読取・diff生成のみ・diff出力は本repo scratchpad → 本file にのみ収めた)。走らせていない(scriptを実行せず、静的読取とgrep/diffのみ)。hakudokai-dev・姉妹clone(2件)には触れていない。★

**監査体制**: 二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 で停止中)。

---

## §0 対象file 断面 (再測・一致確認)

| file | 行数 | sha256 | 一致 |
|---|---|---|---|
| 当repo `scripts/watchdogs/enter_restart_common_watchdog.sh` | 382行 | `ba89766923fdf4ea9354e8afdccb85536ca4f833f81161fc22fad45da36be378` | ★addendum3 (07:48測) と完全一致★ |
| newbuild `.../enter_restart_common_watchdog.sh` | 330行 | `ce56c722570f7b2636230d1ca6c3adf737d47b23d7a310f9e78318d0a5d27a7f` | ★addendum3 と完全一致★ |

∴ 両fileとも addendum3 作成 (07:48) から本測 (10:18) まで **無変更**。以下の実測は addendum3 と同一断面に対するものであり、断面ずれの懸念は無い。

---

## §1 heredoc 開始行 4箇所 — 再測 (完全一致)

`/usr/bin/grep -n "PYEOF" scripts/watchdogs/enter_restart_common_watchdog.sh` (当repo) 実測:

| Step | 当repo heredoc開始行 (引用形) | addendum3 の記載 | 一致 |
|---|---|---|---|
| 0 (fire cap halt) | L102 `<<'PYEOF' \|\| true` | L102 | ★一致★ |
| 2 (pc_handshake取得) | L150 `<<'PYEOF'` | L150 | ★一致★ |
| 7 (shireiko_audit_log INSERT) | L315 `<<'PYEOF' \|\| true` | L315 | ★一致★ |
| 8 (heartbeat) | L355 `<<'PYEOF' \|\| true` | L355 | ★一致★ |

∴ **委員長殿の御指摘行 (L102/150/315/355) は 4/4 で実測一致**。ここは addendum3 の記載どおりで誤りなし。

---

## §2 直前 export 行 — 再測 (★addendum3 の行番号記載 3/4 に誤差あり・変数リストは正★)

`/usr/bin/grep -n "_PY=" scripts/watchdogs/enter_restart_common_watchdog.sh` (当repo) 実測:

| Step | 実測 export 行範囲 | addendum3 記載 | 一致 | 備考 |
|---|---|---|---|---|
| 0 | **L96-100** (5行) | L95-99 | ★不一致 (+1行ずれ)★ | addendum3のL95はコメント行(`# (= homework#1...)`)であり export行ではない。実 export は L96-100。変数名5件 (ER_EVENT_TYPE_PY/ER_RECENT_FIRES_PY/ER_FIRE_CAP_COUNT_PY/ER_FIRE_CAP_WINDOW_MIN_PY/ER_TARGET_PC_PY) は addendum3 と完全一致 |
| 2 | **L149** (1行) | L149 | ★一致★ | `LAST_INFO=$(ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" doppler run ...` — 単一行に統合 |
| 7 | **L306-313** (8行) | L308-314 | ★不一致 (-2行ずれ)★ | addendum3のL314は`doppler run --project openhands --config dev -- \`行でありexport行ではない。実 export は L306-313。変数名8件は addendum3 と完全一致 |
| 8 | **L345-353** (9行) | L347-354 | ★不一致 (-2行ずれ)★ | addendum3のL354は`doppler run --project openhands --config dev -- \`行でありexport行ではない。実 export は L345-353。変数名9件は addendum3 と完全一致 |

**判定**: 変数の中身・個数は 4/4 一致 (移植先で使う情報として実害なし)。★行番号の引用のみ 3/4 で ±1〜2 のずれ★。原因は未測 (追い番の目視誤差の可能性・断面ずれではない事は §0 で確認済)。∴ 本file 以降の移植当てはめ (§6) では ★本節の再測値 (L96-100 / L149 / L306-313 / L345-353) を正として用いる★。

---

## §3 newbuild 側 対応行 — 実測 + 対応表

`/usr/bin/grep -n "PYEOF\|resolved_at\|enter_restart_log\|shireiko_audit_log\|HEARTBEAT_MODE\|^if .. \|^else$\|^fi$"` (newbuild・読取のみ) 実測より:

| Step | newbuild heredoc開始行 (無引用) | newbuild 側の周辺特徴 |
|---|---|---|
| 0 | **L100** `<< PYEOF \|\| true` | url=`enter_restart_log` (L104)・`resolved_at` field (L114) |
| 2 | **L136** `<< PYEOF`| 特記なし (URL文字列直接展開のみ) |
| 7 | **L282** `<< PYEOF \|\| true` | url=`enter_restart_log` (L286)・`resolved_at` field (L296) |
| 8 | **L311** `<< PYEOF \|\| true` | ★外側 if/else (L307-327) に包まれる★ (下記§4-③) |

### 当repo行 ↔ newbuild行 対応表 (行番号は本file §2/§3 の実測値)

| Step | 当repo (根治済) | newbuild (未根治) | 対応の型 |
|---|---|---|---|
| 0 | export L96-100 / heredoc開始 L102 | heredoc開始 L100 (直前に export 無し) | 挿入型 (exportをheredoc直前に新設) |
| 2 | export L149 (1行統合) / heredoc開始 L150 | heredoc開始 L136 (env prefix無し・`LAST_INFO=$(doppler run ...`) | 統合型 (env prefixをdoppler呼出直前に同一行で付与) |
| 7 | export L306-313 / heredoc開始 L315 | heredoc開始 L282 (直前に export 無し) | 挿入型 |
| 8 | export L345-353 / heredoc開始 L355 | heredoc開始 L311 (直前に export 無し・★外側if/elseの内側★) | 挿入型 (if/elseの内側のみ・外枠は不変) |

---

## §4 newbuild固有3構造 — 三値判定 (①②③ 全て ㈠特定済)

軍師second/将軍second が指摘した「newbuild固有3構造」を、本職の実測 (newbuild grep・読取のみ) で再特定した。

| # | 構造 | 判定 | newbuild 実測行 | 当repo に有無 |
|---|---|---|---|---|
| ① | HEARTBEAT_MODE 検証ブロック (`always\|events_only` 妥当性 case文) | **㈠特定できた** | L73-82 (`HEARTBEAT_MODE=...` L73 / `case` L76 〜 `esac` L82) | ★当repoに存在せず (0件・grep実測)★ |
| ② | `resolved_at` field + `enter_restart_log` テーブル repoint (Step0/Step7) | **㈠特定できた** | Step0: url L104・resolved_at L114 / Step7: url L286・resolved_at L296 | ★当repoは両Stepとも `shireiko_audit_log` のまま・resolved_at 無し (grep実測=0件)★ |
| ③ | Step8 外側 `if [ HEARTBEAT_MODE=events_only ] && [ RESULT=skipped ]` 分岐 | **㈠特定できた** | if L307 / else L309 / (heredoc L311-326) / fi L327 | ★当repoのStep8は無条件実行 (if/else無し・grep実測=0件)★ |

**当repoに ① が無い事の意味**: `HEARTBEAT_MODE` という変数自体が当repoのソース中に登場しない (`/usr/bin/grep -c HEARTBEAT_MODE scripts/watchdogs/enter_restart_common_watchdog.sh` = 0)。∴ ①③ は対になっており、当repoは「常時 heartbeat 送信」という旧い (newbuildより前の) 挙動のまま。

---

## §5 「そのまま持てるか」の判定 — ★Step0/Step7は そのままでは持てぬ★

`diff -u newbuild版 当repo根治版` (207行・addendum3の同数と一致・§0の断面一致で再現性確認済) を実測した結果:

| Step | そのまま持てるか | 理由 |
|---|---|---|
| **0** | **㈡ そのままは不可・部分適用が要る** | 当repoの diff をそのまま当てると、newbuild固有②(`url=enter_restart_log`・`resolved_at`)が **削られ `shireiko_audit_log` へ退行する**。実際に diff 中で確認: `-url = os.environ['SUPABASE_URL'] + '/rest/v1/enter_restart_log'` / `+url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'`、および `-    "resolved_at": datetime.datetime.now(...)...,` が削除側に出ている |
| **2** | **㈠そのまま持てる** | newbuild固有構造なし (§4に該当なし)。diffはURL構築ロジックの変更のみで退行要素なし |
| **7** | **㈡ そのままは不可・部分適用が要る** | Step0と同型。同じ diff hunk 内に `enter_restart_log→shireiko_audit_log` 退行と `resolved_at` 削除が現れる |
| **8** | **㈡ そのままは不可・外枠保持が要る** | 当repoの diff をそのまま当てると外側 `if/else` (③) ごと消え、`events_only` 時の抑制機能が失われる (diff中の `-if [ "$HEARTBEAT_MODE" = "events_only" ]...` `-else` `-fi` が削除側に出ている事で確認) |

**∴ 結論**: 「当repoの diff を丸ごと当てる」は **4箇所中3箇所 (Step0/7/8) で機能退行を起こす**。★これは addendum3 §2 が既に文章で警告していた内容だが、本file は「どの行が退行を起こすか」を diff の実物行で特定した点が新規★。「そのまま持てる」と呼べるのは Step2 のみ。

---

## §6 移植当てはめ表 (★案のみ・newbuildへは一切適用せず★)

以下は「裁が立った刹那、適用のみで終わる形」の下書き。★本file はscratchpadでなく docs/incident_logs/ の記録であり、当てるのは委員長殿裁可後の実施者★。

### Step 0 (newbuild L88-124相当・fire cap halt)

- newbuild L100 `<< PYEOF` → `<<'PYEOF'` (引用化)
- 直前 (newbuild L99 `doppler run ...` の前) に、当repo L96-100 と同型の5 export行を挿入:
  `ER_EVENT_TYPE_PY="$EVENT_TYPE" \` / `ER_RECENT_FIRES_PY="$RECENT_FIRES" \` / `ER_FIRE_CAP_COUNT_PY="$FIRE_CAP_COUNT" \` / `ER_FIRE_CAP_WINDOW_MIN_PY="$FIRE_CAP_WINDOW_MIN" \` / `ER_TARGET_PC_PY="$ER_TARGET_PC" \`
- python本体: `import os, json, urllib.request, datetime` (newbuildの `datetime` importは★維持★・当repoは `resolved_at` が無いため `datetime` 不要で削られているが、newbuildでは要る)
- `url = ...` 行は **newbuild の `enter_restart_log` を維持** (当repoの `shireiko_audit_log` へ書き換えない)
- 直前のコメント行 `# Phase-2 S6 差し戻し対応...` も **維持**
- `event_type`/`recent_fires`/`fire_cap_count`/`fire_cap_window_min`/`target_pc` の5変数を `os.environ.get('ER_*_PY', '')` で受けるよう書き換え (当repo同型)
- `payload` 内 `"resolved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),` は **維持** (当repoには無いが newbuild固有②ゆえ削らない)

### Step 2 (newbuild L134-155相当・pc_handshake取得)

- newbuild L136 `<< PYEOF` → `<<'PYEOF'`
- `LAST_INFO=$(doppler run ...` の `doppler` 直前に `ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" ` を1行内で付与 (当repo L149と同型・分離不可という当repoの教訓を継承)
- python本体: `import urllib.parse` 追加、`from_pc_filter = os.environ.get('ER_FROM_PC_FILTER_PY', '')`、`urllib.parse.urlencode(...)` でquery構築 (当repo L151-162と同型・そのまま持てる・newbuild固有要素なし)

### Step 7 (newbuild L273-302相当・shireiko_audit_log/enter_restart_log INSERT)

- newbuild L282 `<< PYEOF` → `<<'PYEOF'`
- 直前に当repo L306-313相当の8 export行を挿入 (`ER_EVENT_TYPE_PY`/`ER_ROLE_NAME_PY`/`ER_ELAPSED_MIN_PY`/`ER_THRESHOLD_MIN_PY`/`ER_DETAIL_EXTRA_PY`/`ER_ACTION_PY`/`ER_SHIREIKO_RESULT_PY`/`ER_TARGET_PC_PY`)
- `url = ...` は **newbuild の `enter_restart_log` を維持**・直前コメント `# Phase-2 S6 差し戻し対応...` も維持
- `payload` 内 `"resolved_at": ...` は **維持**
- `print(f"enter_restart_log INSERT rc=...")` の文言は **newbuild側のまま維持** (当repoは `shireiko_audit_log INSERT` に変わっているが、これはテーブル名repointに追随しただけの表示文言であり newbuild側の方が実態に正確)

### Step 8 (newbuild L304-327相当・heartbeat)

- **外側 `if [ "$HEARTBEAT_MODE" = "events_only" ] && [ "$RESULT" = "skipped" ]; then ... else ... fi` は丸ごと維持** (③・削ってはならない)
- `else` ブロックの内側 (newbuild L311 heredoc) のみ、当repo L345-353相当の9 export行を挿入し `<< PYEOF` → `<<'PYEOF'` に変更
- python本体は当repo L356-379と同型 (os.environ.get 化) — この部分は newbuild固有構造なし・そのまま持てる

---

## §7 零に理由 / 判じ難き

- ★零★=当repoの `HEARTBEAT_MODE` 出現数=0件 (`/usr/bin/grep -c HEARTBEAT_MODE scripts/watchdogs/enter_restart_common_watchdog.sh` 実測)。理由=①③の機構自体が当repoに未実装のため。
- ★零★=当repo・newbuild両fileの heredoc周辺における `second_pc` 等PC名ハードコード=0件 (`/usr/bin/grep -n "second_pc\|main_pc\|third_pc"` 実測・両file共にコメント文中とL68のデフォルト値のみで完全一致、ハードコード分岐は無し)。addendum3 §0⒝の裏取りとして再確認。
- ★判じ難き★=§2で見つかった addendum3 の行番号ずれ (3/4) の発生原因。当職は自分の引用を鵜呑みにせず実測したが、★addendum3側の誤差の発生経緯 (手動カウント誤りか、参照した断面が違ったか) までは本工区の対象外につき未測★。実害面 (移植内容) には影響しない事のみ確認済。

---

## §8 【本工区で己が直した誤り】

無し。(本工区の性質は「addendum3を鵜呑みにせず実測で裏取り」であり、その過程で addendum3 側の行番号誤差3件を発見・訂正した — これは他者の成果物の誤りであって、己の誤りではない。§2に明記の通り区別した)

## §9 【この工区と対に成る他工区】

無し (探索範囲=`docs/incident_logs/2026-08-0[56]*.md` 中の「移植」grep 全件・`queue/tasks/*.yaml` 中の「transplant」「newbuild.*mapping」grep。ヒットは本file の上流artifact (`2026-08-06_p0_ishoku_heredoc_fix_plan_a2*.md`、下命書内で明示された参照元) のみで、並行する別工区は確認できず)。

---

## §10 監査提出

成果物: 本file (`docs/incident_logs/2026-08-06_p0_transplant_mapping_a3.md`)。
ETA: 即時 (提出済)。
提出先: karo-second + 軍師second。
監査体制: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 で停止中)★。
