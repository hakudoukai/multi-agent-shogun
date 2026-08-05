# ⒝ 差配者通知束ね — 既定 disable の決着 (足軽3号)

- **lane**: `delivery-route-stabilization`
- **下命**: karo-second `msg_20260806_002057_77c916e6` (待機解除・次工区)
- **報告先**: karo-second → 提出=軍師second 直 (下命本文どおり)
- **base_commit**: `502cbfe` 系 (未 commit・write_authorization 継続中の作業樹。本 doc 執筆時点で
  `scripts/inbox_write.sh` は他レグ (SHADOW-FAILCLOSED leg C・inbox_watcher.sh 等) の未commit差分と
  同一作業樹上に同居しておるが、本工区が触れたのは `_notify_pc_dispatcher_of_unroutable()` 直上の
  コメント全面差替と既定値の1点のみ)。

## 1. 下命の要旨と決定

karo-second 下命= 「点検日 (出口の門が軍師PASSを得た時 もしくは 2026-08-08 の早い方) は
既に到達済 (PASSは既に出ており申す) ∴ 出口の門へ統合するか、既定を0へ倒すか、決めて そこまで進めよ」。

**決定 = ★既定を 0 (有効) へ倒す★。「出口の門への統合」は選ばぬ。**

## 2. 決定理由 (三点・断じるからには根拠を書く)

1. **出口の門は★設計のみ★で実装が一切開始していない。**
   `docs/incident_logs/2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md` §4-7 に
   当職 (足軽3号) 自身が明記した通り「現時点で止まっている状態: 本書は設計のみであり、
   ★何も稼働を開始していない★」であり、かつ実装開始の GO は★委員長殿の専権★とされている。
   ∴ 「統合」しようにも統合先の実装が存在せず、当職が先回りしてそれを作ることは委員長殿の
   専権を侵す。統合待ちを続けても収束の見込みが無い。

2. **§4-4 の核心禁則と本機構の書込先は、同一問題ではない。**
   §4-4「alt-signal の記録先を inbox.yaml 自身にするな」は、★出口の門が監視する対象箱★
   (staleness を検知される側) への書込みを禁じる規律である。一方、本機構
   (`_notify_pc_dispatcher_of_unroutable`) が書く先 (`queue/inbox/shogun-second.yaml`) は
   委員長裁定 (FROM不明の墓場落ちを差配者へ必ず1行報せる) の★宛先★であり、出口の門の
   監視対象ではない。懸念の実体 (cap 圧迫) 自体は本機構が独自に測定・軽減済み
   (`docs/incident_logs/2026-08-05_dispatch_notice_bundle_impl_a2.md` §2:
   「9.3%流入増 → 周期37分→約34分」・軍師second PASS
   `queue/reports/gunshi_second_dispatch_notice_bundle_impl_audit_20260805.md`)。

3. **委員長殿の原下命が、存在せぬ統合先を理由に無期限へ流れるべきではない。**
   「FROM不明の墓場落ちを差配者へ必ず1行報せる」は委員長裁定であり、当職の権限で
   無期限に不履行のままにしてよい性質のものではない。

## 3. 実装 (母集団=1関数のコメント全面差替+既定値1点)

- **path (絶対)**: `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`
- **対象**: `_notify_pc_dispatcher_of_unroutable()` 直上のコメントブロック (旧 288-309行付近) と
  関数内 disable 判定行 (旧318行)。
- **変更点**:
  - `INBOX_WRITE_DISPATCH_NOTICE_DISABLE:-1` → `INBOX_WRITE_DISPATCH_NOTICE_DISABLE:-0`
    (既定=無効→既定=有効)。
  - 上記コメントを、旧「決着待ち」の記述から「決着済 (本 doc が決着の記録)」へ全面差替。
  - 明示 `1` 指定での無効化経路は★変更なし★ (安全側の逃げ道は誰でも即時利用可能なまま)。
- **現行ファイル**: 709行 / sha256
  `71dba0d2973bae36011b552bfd7c38d194999b5bfb46fd1610bccda7ba29d11a`
  (断面 2026-08-06T00:41:24+0900・`sha256sum` 実行・64桁を数えてから転記=委員長殿具体化指示遵守)。

## 4. 実証 (sandbox・足軽2号の既存 harness 技法を流用・新規発明なし=Anti-Duplication)

止血命令 (他 bats はなお禁・`agent_selfwatch.bats` のみ解除) の対象は「実 `scripts/inbox_write.sh`
を直呼びする bats」。本検証は★bats を一切使わず★、実関数のみを `sed -n` で機械抽出し
scratchpad へ source、`_write_message` を no-op stub に差し替えて実行した (実 `queue/inbox/*.yaml`・
実 `queue/dead_letter/` へは一切書込まぬ)。

harness:
`/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/e70d9a47-0ca9-4e56-a9e7-54407be9c42c/scratchpad/notice_default_flip/test_default_flip.sh`
(実行者=当職・本 turn。関数本体は現行 sha256 `71dba0d2...` から `grep`/`awk`/`sed -n` で機械抽出
— 手で書き写していない)。★scratchpad は当職セッション限りの ephemeral dir ゆえ、監査者が
再実行する場合は本 doc の手順 (grep/awk抽出+stub化) を同じ技法で再現されたし — 断言の根拠は
下記実測出力であり、scratchpad 自体の永続性ではない。★

実行時の生出力 (第2回・自己是正後の版):

```
[harness] extracted function lines 321-382 from /home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh
=== test 1: env未設定 (新既定) → 有効のはず: cap=5 束ねで1回flush ===
[inbox_write] DISPATCH_NOTICE_FLUSHED: 5 pending unroutable notice(s) sent to 'sandbox_dispatcher'
flush count (期待=1): 1
CALLED dispatcher=sandbox_dispatcher type=unroutable_notice_bundle from=inbox_write body_lines=5
=== test 2: 明示 DISABLE=1 → なお無効化できる (安全側の逃げ道が生きている事) ===
(DISPATCH_NOTICE_DISABLED ログ5件・略)
flush count with explicit DISABLE=1 (期待=0): 0
buffer dir exists (期待=作られぬ): no
=== test 3: 明示 DISABLE=0 (旧来の明示指定書式もなお動く事・後方互換) ===
[inbox_write] DISPATCH_NOTICE_FLUSHED: 5 pending unroutable notice(s) sent to 'sandbox_dispatcher'
flush count with explicit DISABLE=0 (期待=1): 1
=== 判定 ===
VERDICT: PASS (既定=有効・明示1で無効化可・明示0も動作=三値とも仮説どおり)
```

三値判定:
1. **env 未設定 (新既定) → 有効**: 実測どおり (仮説どおり)。cap=5 束ねで1回 flush。
2. **明示 `DISABLE=1` → 無効化できる (安全弁は生存)**: 実測どおり。flush 0件・buffer dir すら作られぬ。
3. **明示 `DISABLE=0` (旧来の明示指定書式) → なお有効に動く (後方互換)**: 実測どおり。

age=300s (時間経過) 側は本工区の対象外 (旧来からの既知の未実測領域・
`2026-08-05_dispatch_notice_bundle_impl_a2.md` §3 末尾で足軽2号が既に「判定不能」と明記済 — 本工区は
既定値の1点のみを変更しており、cap/interval 判定ロジック自体には触れていないため、当該未実測領域は
不変のまま継承する。★新たに未実測を作ってはいない★)。

## 5. 【本工区で 己が直した誤り】(欄・必須)

**有り**。本検証 harness の自作コードに誤りが1件あった: `grep -c CALLED "$WRITE_LOG" || echo 0` は
`grep -c` が0件時に★既に"0"を標準出力へ書いた上で exit 1する★ため、`|| echo 0` が更に"0"を追加し
出力が二重化する (`0\n0`)。初回実行 (2026-08-06T00:4x) で `COUNT2` がこの二重化を含んだ状態のまま
数値比較に使われ `VERDICT: FAIL` を誤って出力した。当職はこれを実行結果を読んで直後に検出し、
`|| echo 0` → `|| true` (grep 自身の"0"出力のみを活かし、`||` 節は追加出力をしない形) へ修正、
再実行して `VERDICT: PASS` を確認した (§4 の出力は修正後の第2回実行分)。
★『赤の筈』も『緑の筈』も証に非ず — 実行して確かめる、を自分の検証コードにも適用した一例★。

## 6. 【この修正が新たに開ける穴】(受入条件⑴・空欄不可)

1. **委員長裁定の原下命 (差配者への確実な通知) が、既定有効化により実際に発火し始める。**
   これまで既定無効ゆえ★発火していなかった★ shogun-second.yaml への束ね書込みが、以後は
   実際に起き得る。§2-2 で引用した測定 (周期37分→約34分・9.3%増) は足軽2号による事前測定であり、
   当職はこれを追加で再実測していない (既存測定を引用するのみ・Anti-Duplication)。
2. **「出口の門」実装が将来 GO された場合、本機構との統合設計を改めて要する。**
   本決定は「統合先が存在しない現時点での」決着であり、出口の門が将来実装されれば、
   本機構の書込先 (shogun-second.yaml 直書き) と出口の門の別state設計 (§4-4) が
   再び同じ論点に戻る可能性がある。★本決定はこの再検討を不要にするものではない★。
3. **age=300s (interval flush) 側は依然未実測のまま**引き継がれる (§4末尾)。既定有効化により
   この未実測経路も実際に発火し得る状態になる。

## 7. 境界遵守声明

- 実 `queue/inbox/*.yaml`・実 `queue/dead_letter/*` — 検証時も一切書込んでいない (stub化・scratchpad限定)。
  `git status --short queue/` および `ls queue/dead_letter/_pending_notice/` (存在せず) で確認。
- bats 実行なし (他 bats 止血継続中・`agent_selfwatch.bats` 以外は今回も未実行)。
- commit・push・stage なし (Third-Party Audit Rule により軍師 PASS が前提・本 doc 提出後に判断を仰ぐ)。
- 影 file・dd189・process・患者/secret 不触。
- 出口の門設計 doc 本体 (`2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md`) は
  ★不改変★ (参照のみ)。
- 暫定二者制 (軍師second + Gemini)。Codex leg は SAFETY 裁定 seq132707 により停止中
  (「二者PASS」を「三者PASS」とは書かぬ)。

## 8. 【対に成る他工区】

- 足軽2号 = ⒝ 差配者通知束ね実装 (`2026-08-05_dispatch_notice_bundle_impl_a2.md`) — 本 doc は
  その §7 が明記した「既定無効・有効化は権限外」を、権限を持つ側 (karo-second 下命) から決着させたもの。
- 当職 (足軽3号) 自身 = 【第五】出口の門 設計 (`2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md`) —
  §4-7 に基づき「統合ではなく既定反転」を選んだ理由が、その doc 自身の記述と直接対応する。

## 9. 監査体制の併記

★三者監査は二者制 (Codex leg は SAFETY 裁定 seq132707 で停止中)★ — 軍師second + Gemini の二者。
本 doc は karo-second への報告と併せ、軍師second へ直接提出する (下命本文どおり)。
