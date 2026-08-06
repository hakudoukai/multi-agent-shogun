# `_dead_letter_second.yaml` の「もう一人の書き手」探索 (足軽3号)

- 測時: 2026-08-06T22:12:07+09:00
- 器: `/usr/bin/grep -rn` (直接呼出・git grep 不使用) + `Read` tool による該当箇所の実読
- 範囲: `shim/**` `scripts/**` `tests/**` (指示範囲通り)
- 発注: 家老second msg_20260806_220710_1c6b20ba (22:07:10)
- ★禁則順守★: 原本 `queue/inbox/_dead_letter_second.yaml` は一度も開いていない (grep/wc/cat 不使用・glob には明示除外なしだが対象 glob 自体を使わず file 単位で個別 grep/Read のみ実施)。copy も作成・借用していない。

## 結論 (要旨)

**unconfirmed**。「もう一人の書き手」を scope 内で確定する直接証拠は見付からなかった。
ただし、構造的に一致し得る候補パターンを1つ発見した (下記②)。推測で断定はしない。

## ⒜ `_dead_letter_second` を書く/作る code 全件 (読むだけの物と分離)

`/usr/bin/grep -rn "_dead_letter_second" --include="*.py" --include="*.sh" shim scripts tests` の結果は **1件のみ**:

```
shim/hakudokai/hakudokai_secondpc_receiver_poll.py:234
```

該当関数 `append_dead_letter(msg, reason)` (同ファイル L232-254)。実読内容:

- L234: `path = pathlib.Path(script_dir) / "queue" / "inbox" / "_dead_letter_second.yaml"`
- L237: `existing = path.read_text(...) if path.exists() else "messages:\n"` — **file が無ければ block 形式 (`messages:\n`) で種を作る**。flow 形式 (`messages: []`) の種は作らぬ。
- L242-251: 追記 entry は生文字列連結 (`f"  - id: ..."` 等) の block-sequence 形式。**yaml ライブラリを一切使わず、既存内容をそのまま前提に文字列を継ぎ足すのみ**。
- ∴ この関数 **単体では** line1 が flow 形式になり得ない。かつ既存内容が既に flow 形式であっても、それを検めず・変換せずそのまま前へ残し、後ろへ block を継ぎ足す構造になっている (これは②の下地として重要)。

**読むだけの箇所 (書込ではない)**: 本工区の grep 範囲では `_dead_letter_second` を読む専用の code は見付からず (append_dead_letter が読み書き両方を兼ねる)。

**同関数の bak 4版との突合** (`*.bak-honbucho-20260803-171604` / `*.bak-fulltext-20260803-225108` / `*.bak-prefixfix-20260803-172711` / `*.bak.seq132067.v4`): `diff` で該当関数部分を突合し、**実質差分なし** (前後の別関数の有無のみ)。∴ append_dead_letter は本日まで一貫して block-only writer。

## ⒝ `yaml.safe_dump({"messages": []})` 等 flow 産出し得る書き方が他に無いか

scope 内で `yaml.safe_dump(` / `yaml.dump(` を呼ぶ箇所は2件のみ:

- `scripts/slim_yaml.py:39` — `yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)`
- `scripts/seo_qc.py:561` — `yaml.dump(report, f, ..., default_flow_style=False, sort_keys=False)`

**両方とも `default_flow_style=False` を明示** — flow を産み得ぬ。∴ この2件は除外できる。

## ⒞ 生文字列 flow seed (`messages: []`) を書く箇所 — 発見した候補パターン

grep `'messages: \[\]'` (scope 全体、拡張子問わず) で **flow 形式を1行で書く箇所が多数見付かった**:

| file | 行 | 備考 |
|---|---|---|
| `scripts/inbox_watcher.sh` | 46 | 現行・`$INBOX` (=`queue/inbox/${AGENT_ID}.yaml`) が無い時の初期化 |
| `scripts/inbox_write.sh` | 143 | 現行・`_write_message()` 内、`$inbox` (=`queue/inbox/${target}.yaml`) が無い時の初期化 |
| `shim/hakudokai/hakudokai_secondpc_setup.sh` | 330 | 現行・`$INBOX_DIR/${AGENT_ID}.yaml` 初期化ループ内 |
| `scripts/watcher_supervisor.sh` | 26 | 現行・`ensure_inbox_file()`、`queue/inbox/${agent}.yaml` |
| `scripts/watcher_supervisor_third.sh` | 24 | 現行・同上 third_pc 版 |
| `scripts/archive/message_delivery_v2_full_20260508/watcher.sh` | 252 | ★archive★ (旧設計・非稼働と見受けられる) |
| `scripts/test_secondpc_monitor_v2.py` | 30 | test 用 |
| `tests/*.bats` 各種 | 複数 | test fixture 用 |
| `scripts/inbox_watcher.sh.bak-*` / `inbox_write.sh.bak-*` 各種 | — | bak (非稼働) |

**共通点**: いずれも `queue/inbox/<識別子>.yaml` という **`_dead_letter_second.yaml` と同一ディレクトリ・同一命名の型** を、`<識別子>` (agent_id / target 変数) が指す file が **未存在の時に限り** flow 形式1行で新規作成する。

**確認した事 (これが未確定の核心)**: 上記いずれの呼出元も、`<識別子>` に文字列 `_dead_letter_second` を渡している箇所は scope 内に見付からなかった。具体的に検めた範囲:

- `hakudokai_secondpc_setup.sh` の対象は `AGENT1_ID="ashigaru2"` / `AGENT2_ID="ashigaru8"` の2件のみ (L29, L33, L328 ループ)。`_dead_letter_second` は含まれず。
- `watcher_supervisor.sh` / `watcher_supervisor_third.sh` は MainPC / ThirdPC の固定 agent 一覧を対象とし (script 冒頭コメント参照)、SecondPC は対象外と明記。`_dead_letter_second` を渡す呼出は見付からず。
- `inbox_write.sh` の `_write_message()` は `target="$1"` を呼出元から受け取る形。scope 内の grep (`_dead_letter_second`) では `inbox_write.sh` を `_dead_letter_second` という target で呼ぶ箇所は見付からず。
- `inbox_write.sh` には canon fail-closed gate (§先頭コメント L11-17、`subtask_shadow_failclosed_legB_a2_20260805` 発の是正、2026-08-05 付) が在り、TARGET が `queue/pane_registry.yaml` の canon 集合に無ければ `queue/inbox/<TARGET>.yaml` を書かない設計になっている (`_dead_letter_second` は agent pane ではないため通常は canon 外と見受けられる)。**但しこの gate の導入時期 (2026-08-05) が対象 file の実際の作成時刻より後か前かは、原本を読まぬ本工区の禁則下では確認できず、unconfirmed のまま残す**。
- `inbox_watcher.sh` の初期化 (L44-46) には canon gate は無く、`bash inbox_watcher.sh <agent_id> <pane_target>` の起動引数 `<agent_id>` がそのまま使われる。この script を `_dead_letter_second` という agent_id で起動する呼出元は scope 内で見付からず。

∴ **候補パターンは特定できたが、それを `_dead_letter_second` という識別子で実際に発火させた呼出箇所は scope 内で確認できなかった** — 機序としては「もし何らかの経路でこの汎用初期化群のいずれかが `_dead_letter_second` を対象に呼ばれれば、flow seed が生まれ、その後 append_dead_letter() が既存内容を検めず block を継ぎ足すことで、まさに足軽1号が実測した『line1 flow / line2以降 block』の矛盾が再現される」という **構造的な説明可能性** はある。これは仮説であり、証拠ではない。

## ⒟ 見付からなかった事の明示

- `_dead_letter_second` を明示引数・識別子として渡す呼出は scope 内 (`shim/**` `scripts/**` `tests/**`) に **0件**。
- flow 形式を生む yaml ライブラリ呼出 (`default_flow_style` 未指定または `True`) は scope 内に **0件** (見付かった2件は両方 `False` 明示)。
- test/fixture が `_dead_letter_second` という名で空 file を作る箇所は **0件** (tests/ 配下を `_dead_letter_second` で個別 grep、該当なし)。

## ⒠ 己の手で為した事

1. `/usr/bin/grep -rn "_dead_letter_second" --include="*.py" --include="*.sh" shim scripts tests` を実行 (1件)
2. `/usr/bin/grep -rln "_dead_letter_second" shim scripts tests` (拡張子なし) を実行 (bak 4件 + pyc 1件 + 本体1件)
3. `Read` tool で `hakudokai_secondpc_receiver_poll.py` L180-299 を実読
4. bak 4版全てで `dead_letter` 行を grep し、`diff` で該当関数を突合
5. `/usr/bin/grep -rln "dead_letter" shim scripts tests --include="*.py" --include="*.sh"` で広域候補を洗い出し、各 file を個別 grep で実読 (9 file)
6. `/usr/bin/grep -rn "yaml.safe_dump\|yaml.dump" shim scripts tests --include="*.py"` で全 yaml dump 呼出を洗い出し (2件)、両方を実読し `default_flow_style` を確認
7. `/usr/bin/grep -rn 'messages: \[\]'` を scope 全体 (拡張子指定なし) で実行し、flow seed 箇所を列挙 (14件、bak/archive/test 含む)
8. `hakudokai_secondpc_setup.sh` の `AGENT1_ID`/`AGENT2_ID` 定義を grep で確認
9. `watcher_supervisor.sh` / `watcher_supervisor_third.sh` を `Read` tool で冒頭〜35行実読 (対象 agent 範囲の確認)
10. `inbox_write.sh` L100-160 を `Read` tool で実読 (`_write_message()` の初期化・canon gate コメント確認)
11. `inbox_watcher.sh` L1-60 を `Read` tool で実読 (起動引数の扱い確認)

## 何を索いたか (見付からなかった部分について)

- 語彙: `_dead_letter_second` (完全一致文字列)、`dead_letter` (部分一致)、`messages: []` (flow seed 文字列)、`yaml.safe_dump`/`yaml.dump` (シリアライズ呼出)
- 範囲: `shim/**` `scripts/**` `tests/**` (拡張子 `.py`/`.sh` 限定検索と拡張子無指定検索の両方を実施)
- 器: `/usr/bin/grep -rn` / `-rln` (git grep は使用せず、queue/ 等の gitignore による無警告 skip を避けた)

以上。

## この工区と対に成る他工区

★足軽1号の実測 (line1 flow / line2以降 block の構造矛盾を発見・軍師second PASS済) が本工区の端緒★。
本工区はその「もう一人の書き手」の code-only 探索であり、足軽1号票と対を成す。

## 『完』の三状態

- ⒜ 実装: 該当なし (本工区は調査のみ・実装物なし)
- ⒝ 監査: pending (本報告を軍師second へ提出予定)
- ⒞ 運用: 該当なし (調査報告のみゆえ運用状態を持たぬ)
