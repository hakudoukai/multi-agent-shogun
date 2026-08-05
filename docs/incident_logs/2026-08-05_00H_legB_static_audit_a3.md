# 00H『leg B (canon gate) が意味を失わせた試験』静的実査 (足軽3号)

断面: 2026-08-05T17:14 JST / 発令= 家老second msg_20260805_170507_60e8daa8 / base_commit=502cbfe (作業樹はこれより先行中の未commit差分を含む)
境界順守: **bats 実行 0件・実装 0件・.gitignore 不触・inbox_write.sh 不触・commit は軍師 PASS 後**。以下は全て `Read`/`grep`/`sed -n` によるコード読解のみで導出。

---

## ①既存を探した結果 (命令+出力)

```
$ grep -rn "DETECTOR_UNAVAILABLE" --include="*.sh" --include="*.bats" --include="*.py" . 2>/dev/null | grep -v "\.git/"
scripts/inbox_write.sh:17:#   stderr に DETECTOR_UNAVAILABLE を出す。env INBOX_WRITE_CANON_REGISTRY で registry
scripts/inbox_write.sh:476:    echo "[inbox_write] DETECTOR_UNAVAILABLE: canon registry check failed (registry=$CANON_REGISTRY, detail follows) — target=$TARGET write rejected fail-closed" >&2
tests/test_shadow_mailbox_failclosed.bats:72:#    stderr に検出器不能である旨の印 (例: `DETECTOR_UNAVAILABLE`) を出す。
tests/test_shadow_mailbox_failclosed.bats:356:    [[ "$output" =~ DETECTOR_UNAVAILABLE ]]

$ find tests -iname "*e2e_basic_flow*" -o -iname "*e2e_inbox_delivery*" -o -iname "*e2e_parallel_tasks*" -o -iname "*test_inbox_write*" -o -iname "*test_inbox_expiry_supersession*"
tests/test_inbox_expiry_supersession.bats
tests/test_inbox_write.bats
tests/e2e/e2e_basic_flow.bats
tests/e2e/e2e_parallel_tasks.bats
tests/e2e/e2e_inbox_delivery.bats

$ grep -n "set -e\|trap.*ERR" /home/hakudokai/.local/lib/node_modules/bats/libexec/bats-core/bats-exec-test
2:set -eET
116:  trap - ERR EXIT

$ python3 -c "import yaml; d=yaml.safe_load(open('queue/pane_registry.yaml')); print([p.get('agent_id') for p in d['pane_registry']['panes']])"
['shogun','karo','ashigaru1','ashigaru2','gunshi','ashigaru3','takenaka','honda','sanada',
 'shogun-second','karo-second','ashigaru1','ashigaru2','ashigaru3','ashigaru4','ashigaru5',
 'ashigaru6','ashigaru7','gunshi-second','honbucho']
```

`bats-exec-test:2` が `set -eET` である事を確認 — **@test 本文中の `run` で括られておらぬコマンドが非0で終われば、その行で即座にテストを打ち切る** (ERR trap 経由)。これが本件の RED/緑 判定の土台に成る (下記②)。

---

## ②解き方 (機序の実地確認 — 5件それぞれ)

### 前提: leg B の発火条件 (`scripts/inbox_write.sh:430-478`)

```
CANON_REGISTRY="${INBOX_WRITE_CANON_REGISTRY:-$SCRIPT_DIR/queue/pane_registry.yaml}"
_canon_lookup() { ... open(path) ... }   # path が無ければ例外 → sys.exit(2)
_CANON_RC=$?
if [ $_CANON_RC -ne 0 ]; then
    echo "... DETECTOR_UNAVAILABLE: ... write rejected fail-closed" >&2
    exit 1
fi
```
`SCRIPT_DIR` は sed で書き換えられた `inbox_write.sh` 自身の写しの位置 (= sandbox 直下) に解決される。∴ **sandbox 側が `queue/pane_registry.yaml` を複製せねば、この `open()` が `FileNotFoundError` を投げ、常に DETECTOR_UNAVAILABLE 分岐へ落ちる** (足軽2号の発見どおり実地で確認)。

### 五件の個別判定

**⑴ `tests/e2e/e2e_basic_flow.bats`** — sandbox 構築部 `tests/e2e/helpers/setup.bash` (`setup_e2e_session`) を実読。`scripts/` `lib/` `config/` `.venv` はコピー/symlinkするが **`queue/pane_registry.yaml` を複製する行は0件** (grep 済・該当無し)。
  - `E2E-001-A` (L52-82): L58-59 `bash "$E2E_QUEUE/scripts/inbox_write.sh" ...` が **`run` で括られておらぬ** → DETECTOR_UNAVAILABLE (exit 1) が `set -eET` の ERR trap を即座に発火 → **L58 で赤** (L61 の nudge 送信〜L81 の report 検証は一度も実行されぬ)。
  - `E2E-001-B` (L88-114): L94-95 同型 → **L94 で赤**。
  - `E2E-001-C` (L120-156): L130-131 同型 → **L130 で赤**。
  - **判定: 3件とも 赤 (機構が即打ち切る)。「karo→ashigaru1 decompose→実行→report」という本題の検証は 0% 実行される**。

**⑵ `tests/e2e/e2e_inbox_delivery.bats`** — sandbox は同じ `setup.bash` 経由 (登録なし、同条件)。
  - `E2E-002-A` (L49-65): L51-52 は `run` で括られ、L53 `assert_success` (bats-assert) で判定 → **L53 で赤** (L56 以降の YAML 構造検証は未実行)。
  - `E2E-002-B` (L71-96): L77-78 **`run` 無し** → **L77 で赤** (unread件数/nudge/task完了検証 L81-95 は未実行)。
  - `E2E-002-C` (L102-126): L104,106,108 **いずれも `run` 無し** → **L104 で赤** (最初の1本目で即打ち切り。2本目3本目は実行されぬ)。
  - `E2E-002-D` (L132-148): L134,136 **`run` 無し** → **L134 で赤**。
  - `E2E-002-E` (L154-177): L160-161 **`run` 無し** → **L160 で赤**。
  - **判定: 5件とも 赤**。

**⑶ `tests/e2e/e2e_parallel_tasks.bats`** — 同じ sandbox 条件。
  - `E2E-006-A` (L48-84): L56-59 **`run` 無し** (2本連続呼出) → **L56 で赤**。
  - `E2E-006-B` (L90-129): L97-100 **`run` 無し** → **L97 で赤**。
  - **判定: 2件とも 赤**。

**⑷ `tests/test_inbox_write.bats`** — `setup()` (L29-50) を実読。`TEST_SCRIPT_DIR` へ `sed` retarget した写しを作り `.venv` を symlink するが、**`pane_registry.yaml` の複製も `INBOX_WRITE_CANON_REGISTRY` の上書きも0件** (`grep -ni registry tests/test_inbox_write.bats` → 該当無し)。14件の `@test` を全数実読、TARGET/FROM と `run`/直呼びの別を突合:

  | test | TARGET/FROM | canon gate 到達前に打切りか | 結果 |
  |---|---|---|---|
  | T-001 (L61) | (無し・引数検証のみ) | 検証は canon gate (L430) より前の必須引数チェック (L35 付近) で完結 | **無関係・健全** |
  | T-002 (L71) | 同上 | 同上 | **無関係・健全** |
  | T-002b (L81) | 同上 | 同上 | **無関係・健全** |
  | T-002c (L91-95) | target=karo/from=karo | canon gate が **self-send guard (L527) より先** に走る (`registry` 不在で karo の canon 該非を判定する前に例外) → `status=1` は一致するが出力は `DETECTOR_UNAVAILABLE...write rejected fail-closed` (小文字 `rejected`) であり `[[ "$output" =~ "REJECTED" ]]` (大文字・L94) と**大小文字不一致で不一致** | **赤 (L94 の第二assertionで失敗・誤診断)** |
  | T-003 (L101-103) | target=test_agent | `run` 有 → L103 `[ status -eq 0 ]` で失敗 | **赤** |
  | T-004 (L141-147) | target=test_agent | L143 **`run` 無し** (1本目) → L143 で即打切り (L146 の `run` 行に到達せぬ) | **赤 (L143)** |
  | T-005 (L170-176) | target=test_agent | L172-173 **`run` 無し** (2本とも) → L172 で即打切り | **赤 (L172)** |
  | T-006 (L197-200) | (引数不足) | 必須引数チェックで完結 | **無関係・健全** |
  | T-007 (L207-209) | target=test_agent | `run` 有 → L209 で失敗 | **赤** |
  | T-008 (L231-255) | target=test_agent | `run` 有 → L255 で失敗 | **赤** |
  | T-009 (L278-315) | target=test_agent | `run` 有 → L315 付近で失敗 | **赤** |
  | T-010 (L341-374) | target=test_agent (8並行) | L354 は **`&` でバックグラウンド化**・L358 `wait` は終了ステータス未チェック ∴ `set -eET` は**発火せぬ** (バックグラウンドjobの非0はERR trapを起こさぬ) → 8本とも黙って失敗 (書込ファイル自体が作られぬ) → L361-374 の python heredoc が `open()` で `FileNotFoundError` を投げ、heredoc 自体が非0終了 → ここで初めて打切り | **赤 (L361 の heredocで失敗・意図した「重複ID検査」ではなく「ファイル不在」で落ちる=最も誤診断の度合いが大きい一例)** |
  | T-011 (L381-389) | target=test_agent | `run` 有 → 失敗 | **赤** |
  | T-012 (L417-425) | target=test_agent | `run` 有 → 失敗 | **赤** |

  **判定: 14件中 10件が赤 (T-002c,003,004,005,007,008,009,010,011,012)。4件 (T-001,002,002b,006) は無関係・健全のまま (canon gate に触れる前に完結する引数検証のみを見ている)**。

**⑸ `tests/test_inbox_expiry_supersession.bats`** — `setup()` (L38-75) を実読。`TEST_WRITE_DIR/inbox_write.sh` へ sed retarget した写しを作るが、**ここでも `pane_registry.yaml` の複製/上書きは0件**。ただし本ファイルの `@test` 9件のうち **`$TEST_INBOX_WRITE` (= inbox_write.sh) を実際に呼ぶのは LB-09 のみ** (grep 済・他8件は `get_unread_count_fast`/`get_unread_info` を `harness.sh` 経由で直接 source し、手で用意した YAML を読ませるだけで inbox_write.sh を一切呼ばぬ)。
  - LB-01, LB-02, LB-03, LB-04, LB-05, LB-06, LB-07, LB-07b, LB-08 — **inbox_write.sh 不使用ゆえ leg B と無関係。健全のまま**。
  - LB-09 (L372-392): L373 `run bash "$TEST_INBOX_WRITE" "test_agent" "no expiry" "task_assigned" "karo"` → `run` 有 → L374 `[ status -eq 0 ]` で失敗。**L377 の2本目 (env 付き) は未到達**。
  - **判定: 9件中 1件のみ赤 (LB-09)。8件は無関係・健全** — 本ファイルは 5件のうち唯一「大半が無傷」であり、一律に汚染されていると見るのは誤り (下記④で強調)。

---

## ③約の検め — 『赤に成る』か『緑のまま何も検めぬ』か (肝の問い)

**5件・全 33 `@test` を通覧した結論: leg B が絡む 21件は 悉く「赤」であり、「緑のまま黙って通る」事例は 1件も見付からなんだ。**

根拠は二重: (i) `bash-exec-test` が `set -eET` である以上、`run` に括られておらぬ非0終了は即座にテストを打ち切る (ERR trap)。(ii) `run` に括られている場合も、末尾で必ず `[ "$status" -eq 0 ]` 等の明示チェックが在り、DETECTOR_UNAVAILABLE の `exit 1` を拾って落ちる。**∴ 発令書の懸念 (緑のまま気付かれぬ) に対する答えは「本件五ファイルの範囲では該当なし」** — 但しこれは「安全」ではなく「別の危険」を意味する (④参照)。

**然れど 赤の中身は一様ではない**。三段に分かれる:

- **(甲) 正しい理由で赤** — 該当0件。5件のうち「意図通りの assertion」で落ちた例は無い。
- **(乙) 早すぎる打切りで赤** — E2E系13件全部・T-004・T-005。本来の検証コード (nudge/report 突合・overflow・特殊文字) に**一行も到達せぬ**まま落ちる。「何が壊れているか」を出力から読み取るには `inbox_write.sh` の DETECTOR_UNAVAILABLE 行を読み解く必要があり、テスト名 (例: "E2E-001-A: ashigaru1 processes assigned task") からは全く分からぬ。
- **(丙) 誤った理由で赤 (最も危うい)** — T-002c (self-send のテストのはずが「REJECTED」の大小文字不一致で落ちる=self-send guard 自体が生きているか死んでいるかを本試験は一切証していない)、T-010 (flock/重複ID検査のはずが「ファイル不在」の `FileNotFoundError` で落ちる=並行書込み8本が実際に競合したかは一切不明)、LB-09 (expiry/supersedes の round-trip および injection 安全性 = `"$(whoami)"` がリテラルとして残るかの検証が一度も走らぬ)。この三者は **「テストは赤い」→「じゃあ既存の理解通り直っていない」という誤読を誘発しやすい** — 実際には「壊れているかどうか自体が不明」。

---

## ④是正の形 (設計のみ・実装は為さず)

### 健全例 (足軽2号 W211/`tests/test_shadow_mailbox_failclosed.bats`) の実地確認

```
$ grep -n "pane_registry\|HOME=" tests/test_shadow_mailbox_failclosed.bats | head
82:    export REAL_PANE_REGISTRY="$PROJECT_ROOT/queue/pane_registry.yaml"
108:    cp "$REAL_PANE_REGISTRY" "$TEST_TMPDIR/queue/pane_registry.yaml"
112:    export HOME="$TEST_TMPDIR/fake_home"
352:    INBOX_WRITE_CANON_REGISTRY="$TEST_TMPDIR/queue/does_not_exist.yaml" \
388-401: (custom_registry.yaml を INBOX_WRITE_CANON_REGISTRY で差し替える技法・SMFC-SCHEMA1/正しい形の別名テスト)
```

この健全例は **二つの技法** を使い分けている: (a) 実 registry をコピーして本物の canon 名 (`ashigaru1`, `shogun-second` 等) を TARGET/FROM に使う (SMFC-B 陽性対照)、(b) `INBOX_WRITE_CANON_REGISTRY` を env で丸ごと差し替え、テスト専用の合成 registry を使う (SMFC-SCHEMA1 系)。**いずれも registry を「無い」状態にはしていない** — これが5件の欠陥ファイルとの唯一かつ決定的な差。

### 是正の二段構成 (設計のみ)

1. **registry を sandbox に存在させる**: 上記 (a) または (b) のどちらか。
2. **(b) の方が本件5ファイルには適合的と見る** — 理由: 5ファイルの TARGET/FROM は `test_agent`/`other_sender`/`custom_sender`/`sender1`/`sender2`/`writer_N`/`system` 等、**実 registry に一件も存在せぬ架空名**である (`queue/pane_registry.yaml` の agent_id 全20件を実地列挙済・下記⑤で再掲)。もし (a) (実 registry を単純コピー) だけを当てれば、DETECTOR_UNAVAILABLE (registry 不在) は消えるが、**代わりに TARGET_BAD (`REJECTED: target 'test_agent' is not a canon agent_id`) に化けるだけ** — 赤は赤のまま・診断名だけが変わる。∴ (b) 合成 registry に `test_agent`/`karo`/`shogun`/`other_sender`/`custom_sender`/`sender1`/`sender2`/`writer_1..8`/`system` 等、各テストが実際に使う名を **列挙して収録** する形が要る (SMFC-SCHEMA1 と同技法)。
3. e2e 側は `tests/e2e/helpers/setup.bash` の `setup_e2e_session()` に「合成 registry を書き出し `$E2E_QUEUE/queue/pane_registry.yaml` に置く」一手を足す形(該当箇所は本報告 L不参照・setup.bash 内 `mkdir -p "$E2E_QUEUE"/queue/{inbox,tasks,reports,metrics}` の直後が自然な挿入点)。

---

## 条⑿ (二問)

**問1: この是正が、また同じ穴を開けぬか**

**開ける。実測で示す**: `queue/pane_registry.yaml` の agent_id 全20件を実地列挙した結果、`test_agent` はおろか `other_sender`/`custom_sender`/`sender1`/`sender2`/`writer_N`/`system` の**いずれも一件も含まれておらぬ**。∴「健全例をそのまま横展開 (registry を丸ごとコピーするだけ)」という最も安直な適用は、**DETECTOR_UNAVAILABLE を REJECTED (TARGET_BAD) に置き換えるだけで、テストは赤のまま直らぬ**。これは③で述べた「(丙) 誤った理由で赤」を「別の誤った理由で赤」へすり替えるに過ぎず、本件と同型の第二の穴である。是正を実装する者は、**合成 registry に各テストの架空名を明示的に列挙する事**を、単なる registry コピーと取り違えぬよう、設計段階で名指ししておく要がある (④で先回り済)。

**問2: 己ならこの実査をどう誤らせるか**

三点、実際に踏みかけた/踏みやすい所を申告する:
- **一律汚染の決めつけ**: 最初「5ファイル=leg B で一律に壊れている」と早合点しかけた。実際は `test_inbox_expiry_supersession.bats` の8/9件・`test_inbox_write.bats` の4/14件は **inbox_write.sh を呼ばぬ、または canon gate に達する前に完結する**ため無関係・健全である。ここを見ずに「5ファイル全滅」と書けば、既に機能している検証範囲を過大に切り捨てる虚偽の棚卸しになっていた。
- **『赤=正しく検出』の即断**: 「テストが赤くなる」事を確認した時点で「じゃあ気付かれるから大丈夫」と結論しかけた。しかし T-002c/T-010/LB-09 は**赤の中身が意図と無関係**であり、「赤である」ことは「その試験が本来の契約を守っているか」について**何も保証せぬ** (`acknowledged_at` と同型の「印はあるが意味を持たぬ」の一族=台帳§2の④⑥に相当)。
- **健全例の丸写し**: 足軽2号の是正パターンを見た瞬間「これをコピーすれば直る」と早合点しかけたが、実際は TARGET/FROM の名前集合が一致しておらず、単純コピーでは新しい赤 (TARGET_BAD) を生むだけだった (問1で実証済)。

---

## ⑤触る path (本工区で実際に触れた/読んだ全 path)

- `scripts/inbox_write.sh` (読取のみ・L1-60, L425-560 精読)
- `tests/e2e/e2e_basic_flow.bats` (全文)
- `tests/e2e/e2e_inbox_delivery.bats` (全文)
- `tests/e2e/e2e_parallel_tasks.bats` (全文)
- `tests/e2e/helpers/setup.bash` (全文)
- `tests/test_inbox_write.bats` (全文)
- `tests/test_inbox_expiry_supersession.bats` (setup 部・LB-09・grep による全 `@test`/`TEST_INBOX_WRITE` 出現箇所)
- `tests/test_shadow_mailbox_failclosed.bats` (L1-204・健全例確認用)
- `queue/pane_registry.yaml` (agent_id 全件列挙用)
- `/home/hakudokai/.local/lib/node_modules/bats/libexec/bats-core/bats-exec-test` (L1-3, L110-120・`set -eET` 確認用)
- 本報告書自体 (新規作成・repo 内 `docs/incident_logs/`)

**編集・書換は0件** (境界厳守)。`inbox_write.sh` は不触。`.gitignore` 不触。bats 実行は0件 (`grep`/`sed -n`/`Read` のみ)。

---

## 【本工区で己が直した誤り】

無し (静的実査のみ・実装/修正は本工区の対象外)。

## 【この工区と対に成る他工区】

- **足軽7号**: 条の誤用の数え上げ (本工区とは別軸・「試験の実査」と「条の誤用」は別物、家老second 本人が下命文中で明示済)。
- **足軽2号**: 本工区の機序発見者 (`sandbox が queue/pane_registry.yaml を複製せぬ`) および健全例 (`tests/test_shadow_mailbox_failclosed.bats`) の作者。本工区は彼の発見を5ファイルへ**実地に当てて検証**した続き。
- **足軽5号**: 実ユーザー回答待ち (無関係だが同時並走中と申し送り済)。

## 【監査体制の明記】

三者監査は **二者制** (Codex leg は SAFETY 裁定 seq132707 により停止中)。本報告は軍師second + Gemini の PASS を得るまで commit しない (家老second 下命 §追補5〜7 一巡ルールに合わせ、本件も一巡後の提出と心得る)。

## ETA

本便投函をもって完了 (家老second への work_started 相当は本報告自体で兼ねる)。追加確認・redo が要らば即応可。
