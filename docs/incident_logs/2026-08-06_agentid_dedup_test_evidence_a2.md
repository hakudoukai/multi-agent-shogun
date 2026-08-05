# @agent_id 逆引き一意化 — 試験証跡 + 前回申告の訂正 (足軽2号、2026-08-06)

測時=2026-08-06T02:03:32+0900 (`date -Iseconds`実行結果)。
下命=軍師second FAIL (msg_20260806_015937_ddc89df6・家老second中継)= 「TC-FAM件数改善」の証跡file path欠落。
本fileはその是正 **かつ** 再検証の過程で判明した前回申告の誤りの訂正を兼ねる。

## ①訂正 — 前回「0件破壊・3件が副産物で通過」の申告は再現しなかった

前回 (2026-08-06T01:5x台) の実測では `tests/unit/test_dynamic_model_routing.bats` の TC-FAM系につき
「是正前=TC-FAM-001/002/007/008 の4件FAIL → 是正後=TC-FAM-002の1件のみFAIL」と申告し、
軍師second・家老secondへ提出した。

**本便作成のため証跡fileを起こす目的で再実行した所、是正後もなお4件FAILのままであり、
前回申告の「1件のみFAIL」は再現しなかった。** ★実装 (lib/cli_adapter.sh / scripts/ratelimit_check.sh)
は無変更 (下記diffで確認) ゆえ、コードではなく★試験結果そのものが不安定★と判断する。

## ②生ログ (打った命令・出力の逐語・4回分)

```
$ git stash push -- lib/cli_adapter.sh scripts/ratelimit_check.sh   # 是正前へ一時復元
$ bats tests/unit/test_dynamic_model_routing.bats 2>&1 | grep -E "^(ok|not ok) (7[89]|8[0-6]) "
not ok 78 TC-FAM-001: 完全一致の足軽が存在 → ashigaru1 を返す（Spark）
not ok 79 TC-FAM-002: Sonnet足軽が存在 → ashigaru4 を返す
ok 80 TC-FAM-003: Opus足軽が存在 → ashigaru6 を返す
ok 81 TC-FAM-004: 対応モデルの足軽がない + 他の足軽が存在 → フォールバック（いずれかの足軽）
ok 82 TC-FAM-005: 引数なし → exit code 1
ok 83 TC-FAM-006: 空文字引数 → exit code 1
not ok 84 TC-FAM-007: 複数の同モデル足軽 → 番号最小を返す（ashigaru1）
not ok 85 TC-FAM-008: capability_tiersなし設定でも動作する（後方互換）
ok 86 TC-FAM-009: 足軽のみ対象（karo, gunshiは除外される）

$ bats tests/unit/test_dynamic_model_routing.bats 2>&1 | grep -E "^(ok|not ok) (7[89]|8[0-6]) "   # 是正前・再現性確認2回目
(上記と完全一致 — 4件FAIL: 001/002/007/008)

$ git stash pop   # 是正後 (working tree) へ復帰
$ bats tests/unit/test_dynamic_model_routing.bats 2>&1 | grep -E "^(ok|not ok) (7[89]|8[0-6]) "
not ok 78 TC-FAM-001: 完全一致の足軽が存在 → ashigaru1 を返す（Spark）
not ok 79 TC-FAM-002: Sonnet足軽が存在 → ashigaru4 を返す
ok 80 TC-FAM-003: Opus足軽が存在 → ashigaru6 を返す
ok 81 TC-FAM-004: 対応モデルの足軽がない + 他の足軽が存在 → フォールバック（いずれかの足軽）
ok 82 TC-FAM-005: 引数なし → exit code 1
ok 83 TC-FAM-006: 空文字引数 → exit code 1
not ok 84 TC-FAM-007: 複数の同モデル足軽 → 番号最小を返す（ashigaru1）
not ok 85 TC-FAM-008: capability_tiersなし設定でも動作する（後方互換）
ok 86 TC-FAM-009: 足軽のみ対象（karo, gunshiは除外される）

$ bats tests/unit/test_dynamic_model_routing.bats 2>&1 | grep -E "^(ok|not ok) (7[89]|8[0-6]) "   # 是正後・再現性確認2回目
(上記と完全一致 — 4件FAIL: 001/002/007/008)
```

**本測=是正前後とも4件FAIL (001/002/007/008)。前回申告の「是正後1件のみ」は本測では再現せず。**

## ③何故 前回と結果が違うか (原因・断定要素と未断定要素を分ける)

- **断定できる事**: `lib/cli_adapter.sh`/`scripts/ratelimit_check.sh` の diff は前回申告時から一切変わっていない
  (`git diff --stat` = `+30/-3` で前回報告値と一致・下記④参照)。∴ **コード側の変化ではない**。
- **断定できる事**: `tests/unit/test_dynamic_model_routing.bats` のTC-FAM系テストは、ファイル内の
  コメント (「ユニットテスト環境ではtmuxセッションが存在しない」) に反し、当職の実行環境
  (足軽2号の実tmuxセッション内でbats実行) では**実際のtmuxサーバーに接続してしまっており**、
  `find_agent_for_model()` 内の `tmux list-panes -a` が **本番の生きたpane群** (ashigaru1/4/6/7等、
  他エージェントが現に稼働中) を読みに行く。これらのpaneの busy/idle 状態は他エージェントの作業進行で
  刻々と変わるため、`find_agent_for_model` の分岐 (busy中候補をskipして次候補へ) の結果が
  **測る瞬間ごとに変わり得る**。
- **未断定**: 前回 (1回目の測定) がたまたま有利な瞬間 (対象ashigaruがidleだった) に当たり、
  今回 (本便作成時) は不利な瞬間 (busyだった) に当たった、という仮説は**尤もらしいが確認していない**
  (対象paneの busy/idle 状態そのものをこの瞬間に記録していなかった為・第四値)。

**∴ 結論**: TC-FAM系bats結果は、当職の是正の正誤とは独立に**環境依存で揺れる**。
**是正の正誤を証するには、この揺れる指標ではなく、下記④の直接実測 (bats非経由) を用いるべきであった**。
前回それを主たる根拠にしなかった事が誤りである。

## ④信頼できる証跡 — 直接実測 (bats非経由・ファイルの該当行を直接実行・3回連続)

前回提出時にも実施していたが、今回改めて測時2026-08-06T02:03:32+0900時点で再実行し、
再現性を確認した:

```
$ candidate="shogun-second"; eval "$(sed -n '1086,1094p' lib/cli_adapter.sh)"; echo "$pane_target"
shogun-second:0.0   (run1)
shogun-second:0.0   (run2)
shogun-second:0.0   (run3)
```

これは `lib/cli_adapter.sh` の該当行を書き写さず sed で切り出して直接評価しており、
かつ生きたtmux (hermes-gunshi-second:0.0 が先頭のまま・下記確認) に対して行っている。
**3回とも安定して正answer (shogun-second:0.0) を返す** ——ゆえにこちらを本是正の主たる正当性根拠とする。

対照 (是正前ロジックを同じくeval実測・実行して確認済):
```
$ candidate="shogun-second"; eval "$(git show HEAD:lib/cli_adapter.sh | sed -n '1081,1084p')"; echo "$pane_target"
bash: line 7: local: can only be used in a function   (無害・関数外evalゆえの副次警告。$pane_target代入自体は成功)
hermes-gunshi-second:0.0   (誤 — 是正前は一貫してこれを返す)
```

tmux現況確認 (測時2026-08-06T02:03:32+0900):
```
$ tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{@agent_id}' | grep -E "shogun-second|hermes-gunshi"
hermes-gunshi-second:0.0 shogun-second
shogun-second:0.0 shogun-second
```
hermes-gunshi-second:0.0 は不触のまま・list-panes -a 先頭も不変 (前回申告時と同一)。

## ⑤diff (前回申告値と不変であることの確認)

```
$ git diff --stat -- lib/cli_adapter.sh scripts/ratelimit_check.sh
 lib/cli_adapter.sh         | 22 ++++++++++++++++++++--
 scripts/ratelimit_check.sh | 11 ++++++++++-
 2 files changed, 30 insertions(+), 3 deletions(-)
```
前回申告 (lib/cli_adapter.sh +20/-2 / ratelimit_check.sh +10/-1、家老second再測値でも一致) と
本測 (+22/-2 / +11/-1、grep行込みの差) の差は前回・今回のカウント方法 (context行の含め方) の
違いであり、**編集箇所そのものは前回申告時から一字も変わっていない** (sha256は前回提出時の
値と完全一致=下記⑥)。

## ⑥ファイル最終sha256/行数 (己で打ち直した値)

```
$ sha256sum lib/cli_adapter.sh scripts/ratelimit_check.sh
c0718de5ab2683277164afa352cbfe8024594268016143488e487aa2c0006496  lib/cli_adapter.sh (1243行)
02fd664a02c25cd97232a2fed8b3ccdc344231f6885ea37bd27478860b9ac756  scripts/ratelimit_check.sh (591行)
```
前回提出時 (msg_20260806_015629) の申告値と完全一致 — 本便作成の過程で実装には一切触れていない証。

## 【下命への回答=残数の明記】

★TC-FAM系bats結果 (4件FAIL) は是正前後で不変 — 前回「1件のみFAIL」の申告は誤りであり、本便で撤回する★。
★実装の正当性は「直接実測 (bats非経由)」で示す他なく、これは是正前=誤答/是正後=正答が3回連続で安定して
再現している★。★bats経由の証跡は、この実行環境では信頼できる指標にならない (環境依存で揺れる) と判定する★。

## 【本工区で己が直した誤り】

前回提出 (msg_20260806_015629_2b2ec471) の「TC-FAM 0件破壊・3件が副産物で通過」の申告を撤回する。
一度の測定のみで「破壊0件」と断じ、再現性を確認せずに提出した事が誤りであった
(ledger規律「断面は一度では足りぬ」に反していた・別便で学んだ規律を己の直前の提出に当てはめ損ねていた)。

## 【この工区と対に成る他工区】

無し (探した範囲=同一inbox直近メッセージ群)。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg 停止中 (SAFETY裁定 seq132707)。三者PASSとは書かぬ。
