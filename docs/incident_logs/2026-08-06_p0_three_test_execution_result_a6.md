# P0 三種テスト 実走結果 (足軽6号、2026-08-06・段取り書 sha256=7abead49… に基づき実施)

## 境・限界・未測 (冒頭)

**newbuildへは一字も書いていない。** 抽出・compile・実行は悉く`/tmp`配下(scratchpad)のみで実施(karo-second裁定
2026-08-06T10:46:53の一条件を順守)。稼働pid・timerへ手出し・停止・再起動一切せず。rcはpipe越しに読んでいない。
`/usr/bin/grep -r`使用。hakudokai-devへ一字も書いていない。

測時=2026-08-06T12:30:47+09:00(date -Iseconds実行結果)。当repo git rev-parse HEAD=148ac247303cf58ce0cbc96920cc5296ef308558。
newbuild HEAD=1a7ea76e21938ff94b2d8a14a64b41323943c8c6(独立実測、karo-second報告と一致)。

**★途中Bash toolがclassifier不能で断続的に失敗した(newbuild非依存の一般コマンドでも発生する回もあった)★——
推して進まず、都度リトライまたはワークアラウンド(小分けコマンド化)で対応、失敗が続いた時点はkaro-secondへ
都度報告した。**

**★自己訂正★**: 段0報告で「newbuild該当file=382行」と報じたが、これはReadツールの表示由来の誤りで、
`wc -l`/`git show`いずれも実測=★381行★(sha256は既報値と一致=122a66c22d1e0537ebf4290389a902f0cd837298cc33fd78d198ceada7f0c418、
内容には影響なし)。

## ⒜ 前提確認 (段0、独立再測・karo-second報告と全項目一致)

| 項目 | 実測値 | karo-second報告との一致 |
|---|---|---|
| newbuild HEAD | 1a7ea76e21938ff94b2d8a14a64b41323943c8c6 | 一致 |
| commit逐語 | fix(P0): watchdog Python heredoc injection 根治(部分移植・newbuild固有3構造は維持) | 一致 |
| working tree (watchdog file) | 清浄 | 一致 |
| sha256(全桁) | 122a66c22d1e0537ebf4290389a902f0cd837298cc33fd78d198ceada7f0c418 | 一致(先頭24桁報告値と一致) |
| 行数 | 381行 | ★karo-second報告に無し・当職の382行報告は誤りにつき自己訂正★ |
| bash -n | exit_code=0 (PASS) | 一致 |
| timer 3本 | auto-git-sync/enter_restart_shogun_second/shogun_auto_claim 悉くenabled+active | 一致 |

4箇所(Step0/2/7/8)いずれも`<<'PYEOF'`引用化・env-prefix export挿入・`resolved_at`/`enter_restart_log`維持・
HEARTBEAT_MODE if/else維持をReadツールで視認確認(段取り書⒝の一次判定通り)。

## ⒝ 抽出gate (段2、git show経由・newbuild読取専用・書込0)

`git show <commit>:scripts/watchdogs/enter_restart_common_watchdog.sh`でold(親commit `8018688`)・new(`1a7ea76`)
双方を`/tmp`scratchpadへ出力(newbuildの作業木には一切触れず)。

| | 行数 | sha256 | a2記録値との一致 |
|---|---|---|---|
| old(旧・親commit) | 330行 | ce56c722570f7b2636230d1ca6c3adf737d47b23d7a310f9e78318d0a5d27a7f | ★完全一致★ |
| new(新・patch後) | 381行 | 122a66c22d1e0537ebf4290389a902f0cd837298cc33fd78d198ceada7f0c418 | (a2に旧値のみ記録・new値は本工区初出だが⒜の独立sha256実測と完全一致) |

PYEOF終端カウント=新旧とも★4件★(`grep -c '^PYEOF$'`)。4箇所×新旧=8本のheredoc本体を個別抽出、
全て1件ずつの锚(env-prefix行+PYEOF終端)でペア対応が明確であることを確認(母集団取り零しなし)。

## ⒞ 陽性対照(実物・old) — 段3

**実行方法**: 抽出したold heredoc本体を、実際のbash unquoted heredoc構文(`<< PYEOF`)へ物理的に埋め込んだ
wrapper scriptを`/tmp`上で構成し、a2§2と同型の悪性値(`MAL='second_pc"; import os,sys; sys.stderr.write("INJECTED\n"); x="'`)
を該当bash変数へ設定した上で実行、bashの実際の変数展開結果(置換後のpythonソース)を捕獲した。

| Step | 悪性値注入先 | 結果 | 判定 |
|---|---|---|---|
| 0 | EVENT_TYPE | `ast.parse`→SyntaxError (invalid syntax, line 6) | ★PASS(欠陥実証)★ |
| 2 | FROM_PC_FILTER | `ast.parse`→★PARSE_OK(構文的に妥当なPython)★ | ★PASS(欠陥実証・但し性質が異なる=下記★重要知見★参照)★ |
| 7 | EVENT_TYPE | `ast.parse`→SyntaxError (invalid syntax, line 6) | ★PASS(欠陥実証)★ |
| 8 | HEARTBEAT_FROM_PC | `ast.parse`→SyntaxError (invalid syntax, line 6) | ★PASS(欠陥実証)★ |

### ★重要知見★ — Step2の脆弱性はSyntaxErrorで顕在化せず、サイレントなコード実行を許す

a2§3末尾(169行時点)は「Step2のような文字列連結箇所では、悪性値次第でSyntaxErrorにならず構文的に妥当な
注入コードが成立し得る余地がある(今回は実証していない・想定される最悪形として明記する)」と★留保付きの
理論的懸念★として記していた。本工区は★実物のold heredocバイトに対して実際にbash展開を行い★、この懸念を
実証した:

```
url = os.environ['SUPABASE_URL'] + "/rest/v1/pc_handshake?from_pc=eq.second_pc"; import os,sys; sys.stderr.write("INJECTED\n"); x="&select=created_at,topic&order=created_at.desc&limit=1"
```

この文字列は★SyntaxErrorを起こさず★、以下のように解釈される有効なPython文の連なりである:
1. `url = os.environ['SUPABASE_URL'] + "/rest/v1/pc_handshake?from_pc=eq.second_pc"` (有効な代入)
2. `import os,sys` (実行される)
3. `sys.stderr.write("INJECTED\n")` (実行される — 実証用に無害な文を選んだが、任意のPython文に置換可能)
4. `x="&select=created_at,topic&order=created_at.desc&limit=1"` (有効な代入、無害)

**∴ Step0/7/8はSyntaxErrorという「大声で壊れる」形の脆弱性であるのに対し、Step2は「構文的に妥当なまま
任意コードが実行される」という★より発見しにくい形の脆弱性★であった。** これは根治の必要性がStep0/7/8と
少なくとも同等以上である事の実証的裏付けであり、a2/a3/a4いずれも理論上の懸念として留保していた点を
実物バイトで確定させた(本工区独自の新知見)。

## ⒟ 負テスト(実物・new) — 段4

| Step | 悪性値注入先 | 良性値との比較 | 判定 |
|---|---|---|---|
| 0 | ER_EVENT_TYPE_PY | heredoc本体 diff=0 (sha256完全一致) | PASS |
| 2 | ER_FROM_PC_FILTER_PY | heredoc本体 diff=0 (sha256完全一致・urlencode経由で安全) | PASS |
| 7 | ER_EVENT_TYPE_PY | heredoc本体 diff=0 (sha256完全一致) | PASS |
| 8 | ER_HEARTBEAT_FROM_PC_PY | heredoc本体 diff=0 (sha256完全一致) | PASS |

4箇所悉く、悪性値の有無に関わらずheredoc本体は完全に不変(`<<'PYEOF'`の引用化 + env経由受取りの効能が
実物バイトで確認された)。

## ⒠ 機能テスト(4箇所全て) — 段5

ローカルloopback(127.0.0.1、ephemeral port)にPython製の最小HTTPサーバを都度1回限り(`handle_request()`)
起動し、良性sentinel値を実際にPythonへ流し込み、★受け口が捕獲した実POST body/実request path★(scriptの
print出力ではなく)を根拠として値到達を確認した。

| Step | sentinel値 | 実捕獲結果(受け口実file) | 判定 |
|---|---|---|---|
| 0 | event_type=halt/recent_fires=7/fire_cap_count=5/window=10/target_pc=second_pc | `{"event_type": "halt", "detail": "Fire cap exceeded (7 >= 5) in last 10min. Skipping cycle.", ..., "target_pc": "second_pc", "resolved_at": "..."}` (rc=201) | PASS(5値悉く到達) |
| 2 | from_pc_filter=shogun_second | request path=`/rest/v1/pc_handshake?from_pc=eq.shogun_second&select=created_at%2Ctopic&order=created_at.desc&limit=1`、応答body経由で`sentinel_topic_value`が正しく戻る | PASS(1値到達・urlencode正常) |
| 7 | event_type/role_name/elapsed_min/threshold_min/detail_extra/action/shireiko_result/target_pc (8値) | `{"event_type": "halt", "detail": "shogun_second last handshake 12.3min ago (threshold 15min). alive", "action_taken": "none", "result": "detected_only", "target_pc": "second_pc", ...}` (rc=201) | PASS(8値悉く到達) |
| 8 | heartbeat_from_pc/topic_prefix/role_name/elapsed_min/target_pc/threshold_min/result/action/cycle_log_prefix (9値) | `{"from_pc": "second_pc", "topic": "hb: last_shogun_second=12.3min ago", "content": "second_pc enter_restart heartbeat (...) last=12.3min, threshold=15min, result=skipped, action=none", ...}` (rc=201) | PASS(9値悉く到達) |

## ⒡ systemd健全性 — 段6

| timer | 段0(pre) | 段6(post) | 変化 |
|---|---|---|---|
| auto-git-sync.timer | enabled/active | enabled/active | 無し |
| enter_restart_shogun_second.timer | enabled/active | enabled/active | 無し |
| shogun_auto_claim.timer | enabled/active | enabled/active | 無し |

★稼働中watchdogへの影響=0件★(全テストが`/tmp`内で完結し、稼働中processへは一切触れていない為、当然の結果
ではあるが、段取り書の中止条件⒞に従い実測で裏を取った)。

## newbuild境界の確認 (karo-second裁定の一条件、実測)

- `git -C newbuild status --porcelain -- scripts/watchdogs/` = ★該当なし(清浄)★。
- `find newbuild -iname "__pycache__"` = 複数ヒットするが、いずれも★`scripts/`直下・`tests/`・`.venv/`
  site-packages等の既存物であり、`scripts/watchdogs/`配下には★1件も無い★(本工区がpy_compileを実行したのは
  `/tmp`上の抽出物のみである事の裏付け)。
- newbuildの`git status --porcelain`全体には`queue/reports/naomasa_secondpc_report.yaml`・
  `scripts/stop_hook_inbox.sh`・`docs/karo_moushi_v0_1_review.md`の変更が見えるが、これらは
  ★本工区が触れていないfile★(watchdogとは無関係・他工区の並行作業由来と見受ける)。

## 12マス集計 (四値・PASS/FAIL/ERROR/UNMEASURED)

| Step | 陽性対照(old) | 負テスト(new) | 機能テスト(new) |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 2 | PASS(★性質が異なる=SyntaxErrorでなく妥当構文でのコード実行★) | PASS | PASS |
| 7 | PASS | PASS | PASS |
| 8 | PASS | PASS | PASS |

**12/12 PASS。ERROR/UNMEASUREDは0件。** ∴ 段取り書⒠の規則(1マスでもFAIL/ERRORがあれば個別報告)は
発動条件に該当しない——但しStep2の性質差(⒞参照)は「概ね良好」に丸めず本文に明記した(段取り書⒠の
「省略の偏り防止」の趣旨をここでも適用)。

## 証跡manifest

`/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e25d7399-058a-4bef-bc33-81d5d6a89eed/scratchpad/p0_test/manifest.txt`
(45行、当該scratchpad配下の全証跡fileのpath+行数+sha256を列挙。実POST捕獲body=`step{0,7,8}_captured.json`、
実request path=`step2_captured_path.txt`、陽性対照/負テストの置換後ソース・diff対象file悉く含む)。

## この工区で確かめた事・確かめておらぬ事

- 確かめた=4箇所悉くの陽性対照・負テスト・機能テストが実物バイトで実行可能であり、悉くPASS。Step2の
  脆弱性がa2の理論的懸念(未実証)を実物で確定させ、SyntaxErrorという「大声」ではなく「構文的に妥当な
  サイレント注入」という質的に異なる形である事。
- 確かめておらぬ=`enter_restart_shogun_second.timer`の実際の次回発火(5分周期)による本番watchdog起動後の
  実挙動(段取り書§4手順8相当・実行は「誰が・いつ」を要する別工程であり本工区の範囲外、段取り書自身も
  「実行は本工区の範囲外」と明記済)。

## 監査体制

暫定二者制(軍師second+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、P0三種テスト実走結果への応答。newbuildへは一字も書いていない・稼働pidへ手出ししていない。
