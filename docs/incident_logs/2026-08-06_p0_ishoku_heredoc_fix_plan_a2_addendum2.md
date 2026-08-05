# 追補2 — 新工区の前提検証 + 差分のみ (足軽2号)

**対象**: `docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2.md` (以下「本体」) + `..._addendum1.md`
**下命**: karo-second msg_20260806_073239_381fae66 (07:32:39)「新工区【P0 移植の★事前調査★——読取のみ・書込一切なし】」
**測時**: 2026-08-06T07:36:11+09:00 (`date -Is`)
**当repo HEAD**: `32135ccbf790ee700ed361a00fe0a2f512e61dd1`
**監査体制**: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 で停止中)★。「三者PASS」と書かぬこと。

**禁の遵守申告**: ★newbuild=読取のみ (書込・実行せず)。hakudokai-dev (=姉妹clone) には一切触れず、読取もせず★。下記の負テスト/機能テストは当職 scratchpad 上の再現用最小サンプルで検証したものであり、newbuild の実 script は一度も起動しておらぬ。

---

## 0. ★本命令の前提を一つ検めよ★ (下命末尾の指示への回答)

**検めた前提**: 「本工区は新規の調査である」という前提。

**結果**: ★この前提は誤り (部分的)★。本工区の (a)(b)(c) の大半は、当職が既に本日 03:17〜03:34 に作成し ★軍師second PASS 済★ (commit `7ad0071`) の下記2文書と実質的に重複する:
- `docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2.md` (225行・sha256=`6e226ae4...`)
- `..._addendum1.md` (47行・sha256=`ca55e906...`)

対応表:

| 新工区の要求 | 本体の該当箇所 | 充足度 |
|---|---|---|
| ⒜ 正 (当repo) の P0 差分を逐語で.mdへ・値の渡し方 (os.environ か argv か) | 本体§1 (パターン記述のみ・commit の生 diff 引用は無し) | ★部分★→本追補§1で補完 |
| ⒝ newbuild 現物と突き合わせ・移植差分を行単位で確定 | 本体§0 (対象file実測・4箇所 heredoc・newbuild固有差分の保存指定) | ★充足済★ (本追補§2で再測・断面据置を確認) |
| ⒞-1 負テスト | 本体§2 | ★充足済★ |
| ⒞-2 陽性対照 (旧版が RED) | 本体§3 | ★充足済★ |
| ⒞-3 機能テスト (EVENT_TYPE/RECENT_FIRES/FIRE_CAP_*/ER_TARGET_PC が現に Python へ届く実出力) | ★本体に無し★ (負テストの一部で ER_TARGET_PC 単体のみ触れているが、四値全部を対象にした専用の正常系テストではない) | ★未充足★→本追補§3で新規に埋める |

★∴ 本追補は 本体を書き直さず (二重実装回避・追補1と同じ作法)、上表「未充足」「部分」の2点のみを埋める。★

---

## §1 ⒜ 補完 — 当repo P0 差分の逐語引用 + 値の渡し方の明示

**出所**: `git show 0eb6798 -- scripts/watchdogs/enter_restart_common_watchdog.sh` (Step0/Step7/Step8 の quote化+env化本体) + `git show 0c3f371 -- scripts/watchdogs/enter_restart_common_watchdog.sh` (Step2 の env prefix 位置修正)。★2 commit に分かれている★ (cycle1 で quote化+env化、cycle2 で Step2 のみ env 伝播順序の別バグを追加是正)。本節はこの2 commit を分けずに逐語転記する (本追補は方針立案ではなく引用の充足が目的ゆえ)。

**値の渡し方 (問いへの直接回答)**: ★os.environ 経由。argv は使っていない★。旧版も新版も python 起動は `"$ER_PYTHON3_BIN" -` (標準入力から heredoc を読ませる形) であり、python への argv 引数は渡されていない。旧版は heredoc 内リテラル文字列へ bash 展開で直接埋め込み (unquoted `<< PYEOF`)、新版は heredoc を `<<'PYEOF'` で quote した上で、bash 側の `VARNAME_PY="$VARNAME" doppler run ...` という env prefix で環境変数として渡し、python 側は `os.environ.get('VARNAME_PY', '')` で取得する。

### 1-A. commit `0eb6798` (Step0/Step2/Step7/Step8 の quote化+env化・cycle1)

```diff
diff --git a/scripts/watchdogs/enter_restart_common_watchdog.sh b/scripts/watchdogs/enter_restart_common_watchdog.sh
index ebb8033..877b9f9 100755
--- a/scripts/watchdogs/enter_restart_common_watchdog.sh
+++ b/scripts/watchdogs/enter_restart_common_watchdog.sh
@@ -87,19 +87,35 @@ fi
 log "fire cap check: recent_fires_in_${FIRE_CAP_WINDOW_MIN}min=${RECENT_FIRES} cap=${FIRE_CAP_COUNT}"
 if [ "$RECENT_FIRES" -ge "$FIRE_CAP_COUNT" ]; then
     log "★HALT★ fire cap exceeded (${RECENT_FIRES} >= ${FIRE_CAP_COUNT}) in last ${FIRE_CAP_WINDOW_MIN}min — skip cycle"
+    # ★副院長令 b0bdfa67 (P0): S1 high (Codex implementation-scope audit 15ff8ff0) 根治★
+    # 旧版は heredoc unquoted で ${EVENT_TYPE} 等を bash 展開して Python ソースに混入
+    # → wrapper envvar override 経路から Python コード注入の余地。
+    # 構造修正: heredoc <<'PYEOF' (quoted = bash expansion 無効) + 環境変数経由 (os.environ)
+    # + json.dumps (string→Python literal は json で安全) で literal interpolation を断つ。
+    # (= homework#1 audit_gemini.sh と同型根治、FKI-DEV-ROOT-CURE-FIRST 順守)
+    ER_EVENT_TYPE_PY="$EVENT_TYPE" \
+    ER_RECENT_FIRES_PY="$RECENT_FIRES" \
+    ER_FIRE_CAP_COUNT_PY="$FIRE_CAP_COUNT" \
+    ER_FIRE_CAP_WINDOW_MIN_PY="$FIRE_CAP_WINDOW_MIN" \
+    ER_TARGET_PC_PY="$ER_TARGET_PC" \
     doppler run --project openhands --config dev -- \
-      "$ER_PYTHON3_BIN" - << PYEOF || true
+      "$ER_PYTHON3_BIN" - <<'PYEOF' || true
 import os, json, urllib.request
 key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
 url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
+event_type = os.environ.get('ER_EVENT_TYPE_PY', '')
+recent_fires = os.environ.get('ER_RECENT_FIRES_PY', '')
+fire_cap_count = os.environ.get('ER_FIRE_CAP_COUNT_PY', '')
+fire_cap_window_min = os.environ.get('ER_FIRE_CAP_WINDOW_MIN_PY', '')
+target_pc = os.environ.get('ER_TARGET_PC_PY', '')
 payload = {
-    "event_type": "${EVENT_TYPE}",
-    "detail": "Fire cap exceeded (${RECENT_FIRES} >= ${FIRE_CAP_COUNT}) in last ${FIRE_CAP_WINDOW_MIN}min. Skipping cycle.",
+    "event_type": event_type,
+    "detail": f"Fire cap exceeded ({recent_fires} >= {fire_cap_count}) in last {fire_cap_window_min}min. Skipping cycle.",
     "judgment_level": 2,
     "action_taken": "halted",
     "result": "escalated",
     "engine": "enter_restart",
-    "target_pc": "${ER_TARGET_PC}",
+    "target_pc": target_pc,
 }
 req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
     headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
@@ -120,12 +136,24 @@ fi
 
 # Step 2: Supabase で最終投函取得 (idle 判定)
+# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Codex fix_suggestion 準拠)★
+# 旧版は ${FROM_PC_FILTER} を URL 文字列に直接展開 → URL injection の余地。
+# urllib.parse.urlencode で query 構築 + os.environ 経由値取得。
+ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" \
 LAST_INFO=$(doppler run --project openhands --config dev -- \
-  "$ER_PYTHON3_BIN" - << PYEOF
-import os, json, urllib.request
+  "$ER_PYTHON3_BIN" - <<'PYEOF'
+import os, json, urllib.request, urllib.parse
 from datetime import datetime, timezone
 key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
-url = os.environ['SUPABASE_URL'] + "/rest/v1/pc_handshake?from_pc=eq.${FROM_PC_FILTER}&select=created_at,topic&order=created_at.desc&limit=1"
+base = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
+from_pc_filter = os.environ.get('ER_FROM_PC_FILTER_PY', '')
+query = urllib.parse.urlencode({
+    'from_pc': f'eq.{from_pc_filter}',
+    'select': 'created_at,topic',
+    'order': 'created_at.desc',
+    'limit': '1',
+})
+url = base + '?' + query
 req = urllib.request.Request(url, headers={'apikey':key,'Authorization':f'Bearer {key}'})
 try:
     with urllib.request.urlopen(req, timeout=15) as r:
@@ -266,19 +294,38 @@ case "$RESULT" in
     halted)   SHIREIKO_RESULT="escalated" ;;
     *)        SHIREIKO_RESULT="detected_only" ;;
 esac
+# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Step 7 shireiko_audit_log INSERT)★
+# heredoc <<'PYEOF' quoted + 環境変数経由で全 bash 値を Python へ渡す。
+# 全文字列は json.dumps で安全に literal 化、Python source injection 不能。
+ER_EVENT_TYPE_PY="$EVENT_TYPE" \
+ER_ROLE_NAME_PY="$ROLE_NAME" \
+ER_ELAPSED_MIN_PY="$ELAPSED_MIN" \
+ER_THRESHOLD_MIN_PY="$THRESHOLD_MIN" \
+ER_DETAIL_EXTRA_PY="$DETAIL_EXTRA" \
+ER_ACTION_PY="$ACTION" \
+ER_SHIREIKO_RESULT_PY="$SHIREIKO_RESULT" \
+ER_TARGET_PC_PY="$ER_TARGET_PC" \
 doppler run --project openhands --config dev -- \
-  "$ER_PYTHON3_BIN" - << PYEOF || true
+  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
 import os, json, urllib.request
 key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
 url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
+event_type = os.environ.get('ER_EVENT_TYPE_PY', '')
+role_name = os.environ.get('ER_ROLE_NAME_PY', '')
+elapsed_min = os.environ.get('ER_ELAPSED_MIN_PY', '')
+threshold_min = os.environ.get('ER_THRESHOLD_MIN_PY', '')
+detail_extra = os.environ.get('ER_DETAIL_EXTRA_PY', '')
+action = os.environ.get('ER_ACTION_PY', '')
+shireiko_result = os.environ.get('ER_SHIREIKO_RESULT_PY', '')
+target_pc = os.environ.get('ER_TARGET_PC_PY', '')
 payload = {
-    "event_type": "${EVENT_TYPE}",
-    "detail": "${ROLE_NAME} last handshake ${ELAPSED_MIN}min ago (threshold ${THRESHOLD_MIN}min). ${DETAIL_EXTRA}",
+    "event_type": event_type,
+    "detail": f"{role_name} last handshake {elapsed_min}min ago (threshold {threshold_min}min). {detail_extra}",
     "judgment_level": 2,
-    "action_taken": "${ACTION}",
-    "result": "${SHIREIKO_RESULT}",
+    "action_taken": action,
+    "result": shireiko_result,
     "engine": "enter_restart",
-    "target_pc": "${ER_TARGET_PC}",
+    "target_pc": target_pc,
 }
 req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
     headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
@@ -287,22 +334,42 @@ with urllib.request.urlopen(req, timeout=10) as r:
 PYEOF
 
 # Step 8: heartbeat 投函
+# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Step 8 heartbeat INSERT)★
+# heredoc <<'PYEOF' quoted + 環境変数経由で全 bash 値を Python へ渡す。
+ER_HEARTBEAT_FROM_PC_PY="$HEARTBEAT_FROM_PC" \
+ER_HEARTBEAT_TOPIC_PREFIX_PY="$HEARTBEAT_TOPIC_PREFIX" \
+ER_ROLE_NAME_PY="$ROLE_NAME" \
+ER_ELAPSED_MIN_PY="$ELAPSED_MIN" \
+ER_TARGET_PC_PY="$ER_TARGET_PC" \
+ER_THRESHOLD_MIN_PY="$THRESHOLD_MIN" \
+ER_RESULT_PY="$RESULT" \
+ER_ACTION_PY="$ACTION" \
+ER_CYCLE_LOG_PREFIX_PY="$CYCLE_LOG_PREFIX" \
 doppler run --project openhands --config dev -- \
-  "$ER_PYTHON3_BIN" - << PYEOF || true
+  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
 import os, json, urllib.request, uuid
 key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
 url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
+heartbeat_from_pc = os.environ.get('ER_HEARTBEAT_FROM_PC_PY', '')
+heartbeat_topic_prefix = os.environ.get('ER_HEARTBEAT_TOPIC_PREFIX_PY', '')
+role_name = os.environ.get('ER_ROLE_NAME_PY', '')
+elapsed_min = os.environ.get('ER_ELAPSED_MIN_PY', '')
+target_pc = os.environ.get('ER_TARGET_PC_PY', '')
+threshold_min = os.environ.get('ER_THRESHOLD_MIN_PY', '')
+result = os.environ.get('ER_RESULT_PY', '')
+action = os.environ.get('ER_ACTION_PY', '')
+cycle_log_prefix = os.environ.get('ER_CYCLE_LOG_PREFIX_PY', '')
 payload = {
     "id": str(uuid.uuid4()),
-    "from_pc": "${HEARTBEAT_FROM_PC}", "to_pc": "fukuincho",
-    "topic": "${HEARTBEAT_TOPIC_PREFIX}: last_${ROLE_NAME}=${ELAPSED_MIN}min ago",
-    "content": "${ER_TARGET_PC} enter_restart heartbeat (5min cycle, engine=enter_restart, role=${ROLE_NAME}). last=${ELAPSED_MIN}min, threshold=${THRESHOLD_MIN}min, result=${RESULT}, action=${ACTION}",
+    "from_pc": heartbeat_from_pc, "to_pc": "fukuincho",
+    "topic": f"{heartbeat_topic_prefix}: last_{role_name}={elapsed_min}min ago",
+    "content": f"{target_pc} enter_restart heartbeat (5min cycle, engine=enter_restart, role={role_name}). last={elapsed_min}min, threshold={threshold_min}min, result={result}, action={action}",
     "priority": "low", "message_type": "status_update"
 }
 req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
     headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
 with urllib.request.urlopen(req, timeout=10) as r:
-    print(f"${CYCLE_LOG_PREFIX} heartbeat rc={r.status}")
+    print(f"{cycle_log_prefix} heartbeat rc={r.status}")
 PYEOF
 
 log "=== ${CYCLE_LOG_PREFIX} cycle complete (result=${RESULT} action=${ACTION}) ==="
```

### 1-B. commit `0c3f371` (Step2 のみ・env prefix 位置の別バグ是正・cycle2)

★重要★: cycle1 (`0eb6798`) の Step2 修正には★もう一つ別の欠陥★が残っていた。`ER_FROM_PC_FILTER_PY="$VAR" \` と `LAST_INFO=$(...)` を別々の行に分けて書くと、bash の評価順序上「代入のみの simple command」が2つ並ぶ形になり、env prefix が subshell 内の `doppler` へ伝播しない (= python 側で空文字列を受け取り、本番で idle 判定が常に false になる実害が出た)。本工区の (0) 冒頭原則「引用する＋値を別経路で渡す、の対」は cycle1 で満たされたが、★env prefix の置き場所★という別軸の落とし穴が cycle2 で追加是正された。★newbuild へ移植する際は cycle1 の型だけでなく cycle2 の型 (env prefix を `$( )` の中、`doppler` の直前に置く) を採るべし★ (本体§1 の該当箇所は既にこの正しい形で書かれている — 本体作成時点でこの2 commit をまとめて反映済みだったことを、本追補で裏取りした)。

```diff
diff --git a/scripts/watchdogs/enter_restart_common_watchdog.sh b/scripts/watchdogs/enter_restart_common_watchdog.sh
index 877b9f9..a5f7a13 100755
--- a/scripts/watchdogs/enter_restart_common_watchdog.sh
+++ b/scripts/watchdogs/enter_restart_common_watchdog.sh
@@ -139,8 +139,14 @@ fi
 # ★副院長令 b0bdfa67 (P0): S1 high 根治 (Codex fix_suggestion 準拠)★
 # 旧版は ${FROM_PC_FILTER} を URL 文字列に直接展開 → URL injection の余地。
 # urllib.parse.urlencode で query 構築 + os.environ 経由値取得。
-ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" \
-LAST_INFO=$(doppler run --project openhands --config dev -- \
+#
+# ★Codex 再監査 (b0bdfa67 cycle2) B1/T1 high 根治: env propagation 順序修正★
+# 旧版 `ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" LAST_INFO=$(...)` は両方が
+# assignment-only simple command ゆえ bash 評価順で subshell の doppler に
+# env が伝播しない (= LAST_INFO は subshell の中で from_pc_filter='' となり
+# runtime breakage)。Step 0/7/8 と同形 (env prefix が doppler という command に
+# 直接付く形) になるよう、command substitution の括弧の中で env を渡す。
+LAST_INFO=$(ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" doppler run --project openhands --config dev -- \
   "$ER_PYTHON3_BIN" - <<'PYEOF'
 import os, json, urllib.request, urllib.parse
 from datetime import datetime, timezone
```

**照合**: 本体§1 の「Step 2」記述 (行78-111) は `LAST_INFO=$(ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" doppler run ...)` の形で既に書かれており、cycle2 の正しい型と一致することを確認した (差分無し)。

---

## §2 ⒝ 再確認 — newbuild 側の断面据置

- 対象file: `/home/hakudokai/projects/multi-agent-shogun-newbuild/scripts/watchdogs/enter_restart_common_watchdog.sh`
- 本追補時点 (07:36:11) の実測: 330行 / sha256=`ce56c722570f7b2636230d1ca6c3adf737d47b23d7a310f9e78318d0a5d27a7f` / mtime=`Jul 15 16:24` (変更無し)
- 本体§0 (03:17測定) の値と★完全一致★ → ★断面据置を確認 (差分なし)★。本体§0の4箇所 heredoc 位置・newbuild固有差分 (`resolved_at`/`enter_restart_log` repoint/`HEARTBEAT_MODE` 分岐) の記述は★再検証不要のまま有効★。
- 当repo側対象file (`scripts/watchdogs/enter_restart_common_watchdog.sh`) も本追補時点で sha256=`ba89766923fdf4ea9354e8afdccb85536ca4f833f81161fc22fad45da36be378` / 382行 → 本体§0 の記録済み値と★完全一致★ (git HEAD は `e59c47b7...`→`32135cc...`へ進んだが、当該fileへの変更commit無し=本体作成後に無関係commitが積まれただけ)。

---

## §3 ⒞-3 新規 — 機能テスト設計 + scratchpad 実測 (EVENT_TYPE/RECENT_FIRES/FIRE_CAP_*/ER_TARGET_PC が現に Python へ届くことの実証)

**目的**: 負テスト (悪性値でも壊れない) と陽性対照 (旧型は壊れる) だけでは「正常な値が★実際に★ Python 側の payload まで届くか」は示せていない。委員長殿の訂正「引用するだけでは値が渡らなくなる (=機能を殺す)」を裏から実証する為、★正常系の実出力★を独立に確認する。

**設計 (誰が・いつ・何を)**:
- 対象: Step0 の env→payload 構築部 (`ER_EVENT_TYPE_PY`/`ER_RECENT_FIRES_PY`/`ER_FIRE_CAP_COUNT_PY`/`ER_FIRE_CAP_WINDOW_MIN_PY`/`ER_TARGET_PC_PY` の5変数、下命が明示した「EVENT_TYPE/RECENT_FIRES/FIRE_CAP_*/ER_TARGET_PC」と一致)
- 手段: 本体§1と同一の env→python 部分のみを scratchpad 上で抽出し (実 POST/urlopen 部分は除外・secret 不要)、実在する5変数へ★実在の値★を与えて実行し、`payload` dict に正しく反映されるかを assert + 実出力で確認する。
- 実行者: 当職 (本工区・scratchpad限定・newbuildへは一切触れず)。
- 実行タイミング: 本追補作成時点 (07:36台) に実施済み (下記が実出力そのもの)。

**scratchpad 実行 (`/tmp/.../scratchpad/p0_functest/step0_fixed_payload_only.sh`)**:
```bash
EVENT_TYPE="halt" RECENT_FIRES="7" FIRE_CAP_COUNT="5" FIRE_CAP_WINDOW_MIN="10" ER_TARGET_PC="second_pc"
# → ER_*_PY として env 経由で python へ渡し、os.environ.get() で受け取り payload 構築
```

**実測結果 (逐語)**:
```
FUNCTEST_PAYLOAD={"event_type": "halt", "detail": "Fire cap exceeded (7 >= 5) in last 10min. Skipping cycle.", "judgment_level": 2, "action_taken": "halted", "result": "escalated", "engine": "enter_restart", "target_pc": "second_pc"}
FUNCTEST_ALL_FIVE_VARS_REACHED_PYTHON=true
```
5変数すべて (`event_type`/`recent_fires`/`fire_cap_count`/`fire_cap_window_min`/`target_pc`) が payload 内に★リテラルではなく実値として★出現していることを、script内 assert 4本 (event_type一致・target_pc一致・"7 >= 5"含有・"10min"含有) が例外を出さず通過したことと合わせて確認した。

**併せて実証 (委員長殿訂正の直接検証・`naive_quote_only_broken.sh`)**: 「quote するだけ」の片手落ち修正 (env化を伴わない) を同じ最小サンプルで試すと:
```
NAIVE_QUOTE_ONLY_PAYLOAD={"event_type": "${EVENT_TYPE}", "target_pc": "${ER_TARGET_PC}"}
NAIVE_QUOTE_ONLY_VALUE_LOST=true (期待値 halt が届かず、リテラル文字列のまま)
```
★委員長殿の訂正が指した危険が、当職の環境で実際に再現することを確認した★ (quote のみでは `${EVENT_TYPE}` が展開されず python 側にリテラル文字列 `"${EVENT_TYPE}"` としてそのまま渡り、値が失われる)。本体§1・本追補§1の是正案 (quote + env経由) はこの型を回避しており、これが「引用する＋値を別経路で渡す、の対」でなければならない理由の実物証拠である。

**結論**: 機能テストの3値状態は以下の通り (負テスト/陽性対照の型に倣う):
- ①是正案 (quote+env) → 5変数すべてが実値として payload に到達 (green)
- ②片手落ち (quoteのみ) → 値が失われリテラル文字列化 (red・委員長殿訂正が警告した通りの実害)
- ③無修正 (旧型・unquoted) → 本体§3 で既に実証済み (SyntaxError で cycle 全体が壊れる)

---

## §4 【本工区で己が直した誤り】

- 無し。ただし §0 で「本工区は新規調査である」という下命側の前提を検め、★大半が既存 (PASS済) 成果物と重複する★ことを検出し、二重実装せず差分のみを追補として作成する対応を取った (これは karo-second の"前提を一つ検めよ"要求への直接回答であり、"誤りを直した"には該当しないため本欄は「無し」とする)。

## §5 【この工区と対に成る他工区】

- ★本体そのもの★ (`docs/incident_holder... a2.md` + `_addendum1.md`) — 対工区というより★前身工区★。無断で本体を書き換えず追補で対応する作法は追補1と同型。
- 他に対になる同時進行工区は探索範囲 (`docs/incident_logs/2026-08-0[56]*.md` grep + `queue/tasks/*.yaml` grep) 内では見当たらず。

---

## §6 監査提出

成果物: 本file (`docs/incident_logs/2026-08-06_p0_ishoku_heredoc_fix_plan_a2_addendum2.md`)。
ETA: 即時 (本便提出時点で完了・追加作業なし)。
提出先: 軍師second (直接提出義務)。
監査体制: ★二者制 (軍師second + Gemini。Codex leg は SAFETY 裁定 seq132707 停止中)★。
