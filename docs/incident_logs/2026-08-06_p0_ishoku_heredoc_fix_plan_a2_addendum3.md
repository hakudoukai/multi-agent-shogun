# 追補3 — 委員長殿実測 (3点) への対応・行単位差分 + second_pc分岐検め + 判定根拠の明記 (足軽2号)

**対象**: 本体 (`a2.md`) + `addendum1.md` + `addendum2.md`
**下命**: karo-second msg_20260806_073800_442d16f8 (07:38:00)「委員長殿の実測が届き申した——三点 織り込まれたし」
**測時**: 2026-08-06T07:48:00+09:00 (`date -Is` 実行時刻・下記コマンド群の実測はこの前後)
**当repo対象file (根治済)**: `scripts/watchdogs/enter_restart_common_watchdog.sh` — 382行 / sha256=`ba89766923fdf4ea9354e8afdccb85536ca4f833f81161fc22fad45da36be378` (§0/§2既測と不変)
**newbuild対象file (未根治)**: 330行 / sha256=`ce56c722570f7b2636230d1ca6c3adf737d47b23d7a310f9e78318d0a5d27a7f` (§0/§2既測と不変)
**監査体制**: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 で停止中)★。

**禁の遵守申告**: ★newbuild=読取のみ (書込・実行せず)。hakudokai-dev (姉妹clone) には一切触れず★。当てるは委員長殿御自身、当職は「渡す物」を作るのみ。

---

## 0. 委員長殿の三点への回答

### ⒜ 「引用」と「環境変数経由」の対 — ★確認済・一致★

当repo実測: `grep -n "PYEOF" scripts/watchdogs/enter_restart_common_watchdog.sh` の結果:
```
102:      "$ER_PYTHON3_BIN" - <<'PYEOF' || true
124:PYEOF
150:  "$ER_PYTHON3_BIN" - <<'PYEOF'
177:PYEOF
315:  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
340:PYEOF
355:  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
379:PYEOF
```
★委員長殿の御指摘の行番号 (L102/150/315/355) と★完全一致★を実測確認した。いずれも直前に `ER_*_PY="$VAR" \` の export 行 (複数行) が並び、python 側は `os.environ.get(...)` で受ける対構造。本追補§1で行単位に整理する。

### ⒝ 丸ごとコピー不可・second_pc固有分岐の検め — ★実測実施・該当無しを確認 (以下、根拠を示す)★

`diff -u newbuild版 当repo根治版` の全文 (207行、本追補作成のため新規取得) を検めた。結論から述べる: ★4箇所のheredoc周辺 (env export + quote化対象の範囲) に second_pc 固有のハードコード分岐は見当たらなかった★。ただし★newbuild固有で当repoに無い構造が3種★見つかっており、これらは「second_pc固有」ではなく「newbuild固有 (multi-PC横展開機能)」である。詳細は本追補§2。

★見当たらなかった、を断定にしない理由★: 本diffは対象file1本のみの比較であり、wrapper file (`enter_restart_shogun_second.sh` 等、ER_TARGET_PC=second_pc を渡す側) は対象外 (禁=他PC読取・姉妹clone読取に抵触しないよう当repo側wrapperのみ確認可能だが、本工区は対象file限定の下命ゆえ広げていない)。∴ ★「本fileの範囲では見当たらず」と書く (悉皆断定はしない)★。

L68 (`ER_TARGET_PC="${ER_TARGET_PC:-third_pc}"`) は当repo・newbuild★両方で完全一致★ (委員長殿の御指摘は「根治版はL68でthird_pc既定」という事実確認であり、newbuild側がそこで分岐しているという主張ではないと解した — 実測でも分岐は無し)。

### ⒞ 判定根拠=heredocの引用の有無 (os.environ有無を根拠にせぬ) — ★実測で裏書き★

```
$ grep -n "os.environ" newbuild版  → 8箇所 (全て SUPABASE_SERVICE_ROLE_KEY / SUPABASE_URL の既存鍵取得。ER_*_PY は0件)
$ grep -n "_PY" newbuild版         → 0箇所 (env経由パターンが一切存在しない)
$ grep -n "PYEOF" newbuild版       → 4箇所とも "<< PYEOF" (★無引用★、quoted形が1箇所も無い)
```
★os.environ が8箇所在るにもかかわらず、heredocは4箇所とも無引用のまま★であることを実測確認した。これは委員長殿の御指摘 (「os.environ在る＝直っておる、と読むな。見るはheredocの引用の有無」) と完全に符合する実物証拠である。∴ ★当職が本追補以降に書く判定は、常に「該当heredocの開始行が `<<'PYEOF'` (引用付き) か `<< PYEOF` (無引用) か」を根拠とし、os.environ の存在有無を根拠にしない★。

---

## §1 行単位 移植差分表 (★どの行が引用か・どの行がexportか、を対で★)

| Step | newbuild開始行 (無引用・現況) | 当repo対応開始行 (引用済) | 直前export行 (当repo側・行数) | 変換 |
|---|---|---|---|---|
| 0 (fire cap halt) | L100 `<< PYEOF` | L102 `<<'PYEOF'` | L95-99 (5行: ER_EVENT_TYPE_PY/ER_RECENT_FIRES_PY/ER_FIRE_CAP_COUNT_PY/ER_FIRE_CAP_WINDOW_MIN_PY/ER_TARGET_PC_PY) | `<< PYEOF`→`<<'PYEOF'` (引用) ＋ 直前に5 export行を挿入 (対) |
| 2 (pc_handshake取得) | L136 `<< PYEOF` | L150 `<<'PYEOF'` | L149 (`LAST_INFO=$(ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" doppler run ...` — ★1行内でexportとdoppler呼出が同時★、cycle2の教訓により分離禁) | `<< PYEOF`→`<<'PYEOF'` (引用) ＋ env prefixを`$( )`の中・doppler直前に配置 (対・分離不可) |
| 7 (enter_restart_log/shireiko_audit_log INSERT) | L282 `<< PYEOF` | L315 `<<'PYEOF'` | L308-314 (8行: ER_EVENT_TYPE_PY/ER_ROLE_NAME_PY/ER_ELAPSED_MIN_PY/ER_THRESHOLD_MIN_PY/ER_DETAIL_EXTRA_PY/ER_ACTION_PY/ER_SHIREIKO_RESULT_PY/ER_TARGET_PC_PY) | `<< PYEOF`→`<<'PYEOF'` (引用) ＋ 直前に8 export行を挿入 (対) |
| 8 (pc_handshake heartbeat) | L311 `<< PYEOF` | L355 `<<'PYEOF'` | L347-354 (9行: ER_HEARTBEAT_FROM_PC_PY/ER_HEARTBEAT_TOPIC_PREFIX_PY/ER_ROLE_NAME_PY/ER_ELAPSED_MIN_PY/ER_TARGET_PC_PY/ER_THRESHOLD_MIN_PY/ER_RESULT_PY/ER_ACTION_PY/ER_CYCLE_LOG_PREFIX_PY) | `<< PYEOF`→`<<'PYEOF'` (引用) ＋ 直前に9 export行を挿入 (対) ★但しnewbuildは外側にHEARTBEAT_MODE分岐if/elseが在り、この構造は維持 (下記§2-③)★ |

★4箇所とも「引用のみを当てて export を当てぬ」「export のみを当てて引用を当てぬ」の片方だけの移植は禁 (§0-⒞・addendum2§3で実機確認済の通り、片方だけでは値が失われるか注入余地が残る)。★

---

## §2 newbuild固有構造 (当repoに無い・移植時★削るな★) — 全文diffで再確認

本体§0で既に指摘済の3点を、本追補作成時点の新規全文diff (`diff -u newbuild → 当repo`) で★再確認★した。★new findingは無い (既存指摘の裏取りのみ)★:

① **HEARTBEAT_MODE 検証ブロック (newbuild L73-80相当・当repoには存在しない)**:
```bash
HEARTBEAT_MODE="${ER_HEARTBEAT_MODE:-always}"
case "$HEARTBEAT_MODE" in
    always|events_only) ;;
    *)
        printf 'ERROR: invalid ER_HEARTBEAT_MODE=%s (expected always|events_only)\n' "$HEARTBEAT_MODE" >&2
        exit 2
        ;;
esac
```
これは PC名に依存しない汎用機能 (どのPCでも `ER_HEARTBEAT_MODE=events_only` を渡せば同じ挙動)。★second_pc固有ではない★。

② **Step0/Step7の `resolved_at` フィールド + `enter_restart_log` テーブル repoint (S5/Phase-2 S6副院長令)**: 当repoは `shireiko_audit_log` のまま・`resolved_at` 無し。newbuildはテーブル名repoint済 + INSERT時刻埋め込み。★これもPC非依存の機能差 (テーブルスキーマ差)、second_pc固有ではない★。

③ **Step8の外側if/else分岐 (`HEARTBEAT_MODE=events_only` かつ `RESULT=skipped` の場合はheredoc自体をskipしlocal logのみ)**: ①のHEARTBEAT_MODE機能と対になる分岐。当repoには丸ごと存在しない (heredocが無条件実行)。★heredoc本体の引用化はこのif/elseの★内側★のみに適用し、外側の分岐構造自体は変更しない★ (本体§1で既に明記済・本追補で再確認)。

★∴ 委員長殿の「second_pc固有の分岐が混じっておる公算」への回答★: 4箇所のheredoc本体そのもの (引用化+env化の対象範囲) には該当なし。ただし①②③という★newbuild固有 (multi-PC横展開機能) の周辺構造★が存在し、これらを誤って削ると「移植」ではなく「退行」になる。★見分け方★: ①②③はPC名 (second_pc/third_pc等) を直接ハードコードしていない・envvarまたはテーブル名という抽象化された差分であり、「second_pc固有分岐」というよりは「newbuildのみが持つ機能拡張」である。

---

## §3 三種テスト設計 — 既提出 (addendum2§3・本体§2-§3) で充足済、再掲なし

- 負テスト: 本体§2
- 陽性対照 (旧版でRED): 本体§3
- 機能テスト (EVENT_TYPE/RECENT_FIRES/FIRE_CAP_*/ER_TARGET_PCが現に届く実出力): addendum2§3 (scratchpad実測・green確認 + 委員長殿訂正の反例実証)

★委員長殿の三点指示に「三種テスト設計」も含まれていたが、これは新規要求ではなく既提出物の再確認要求と解した (下命文言「必ず入れる物」列挙の最後に三種テストが並記されているのみで、新たな追加観点の指定は無い)。∴ 本節は参照のみとし、重複作成しない (Anti-Duplication)。★

---

## §4 【本工区で己が直した誤り】

無し。

## §5 【この工区と対に成る他工区】

無し (探索範囲=`docs/incident_logs/2026-08-0[56]*.md` grep + `queue/tasks/*.yaml` grep、本体・addendum1・addendum2と同一探索範囲を再実行し変化なしを確認)。

---

## §6 監査提出

成果物: 本file (`docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2_addendum3.md`)。
ETA: 即時。
提出先: 軍師second。
監査体制: ★二者制 (軍師second + Gemini。Codex leg 停止中)★。
