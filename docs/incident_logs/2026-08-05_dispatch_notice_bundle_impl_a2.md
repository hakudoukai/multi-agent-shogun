# ⒝ FROM不明・墓場落ち — 差配者通知 束ね実装 (足軽2号)

- **lane**: `delivery-route-stabilization`
- **下命**: karo-second msg_20260805_140505_f11b5a2f 系列 (第一の門・⒝)〜危険訂正 msg_20260805_141246_06125769〜
  受理 msg_20260805_143615_551f7830 (★保留解除・然れど commit 前に軍師監査を要すと明記★)
- **報告先**: karo-second → 本件は Third-Party Audit Rule により ★軍師second 監査提出が commit の前提★
- **base_commit**: `83bdb61` (未 commit・write_authorization 継続中の作業樹)

## 1. 何を実装したか (母集団=1関数+2呼出箇所)

- **path (絶対)**: `/home/hakudokai/projects/multi-agent-shogun/scripts/inbox_write.sh`
- **対象関数**: `_notify_pc_dispatcher_of_unroutable()` (L310–371)
- **呼出箇所 2 件**: L514 (FROM/TARGET 双方 canon 外の墓場落ち経路)・L610 (cross-PC bridge 経由の墓場落ち経路)
- **現行ファイル全体**: 698 行 / sha256 `d926aa1774dd8222273a4ea7053aa954dc111da6804b0e1aec7d47594592046b`
  (leg B 実装 (leg B 監査対象・別 doc `2026-08-05_legB_shadow_failclosed_impl_a2.md`) と同一ファイル内の追加分。
  ⒝ は leg B の上に載る後続工区であり、leg B 部分は本 doc の監査対象に★含まぬ★)

**何をするか**: 委員長殿裁定「FROM が解けない墓場落ちは、そのPCの差配者(shogun-second)の箱へ必ず1行報せる」を、
差配者の実箱 (`queue/inbox/shogun-second.yaml`) を溢れさせずに実装する。単発都度書きではなく、
`queue/dead_letter/_pending_notice/<dispatcher>.log` へ一旦バッファし、**cap=5件** または **age=300秒(5分)**
のいずれかに達した時点でのみ1便へ束ねて `_write_message()` を呼ぶ。

## 2. 束ねの数字を選んだ理由 (受入条件済み・数で決着)

karo-second との往復 (msg_20260805_142600_fb264487 / 143615_551f7830) で受理済みの実測:

- **flush 1回あたり箱に増える便数 = 常に1件** (束ねる件数によらず `_write_message` 呼出は1回。cap/interval のいずれで
  flush されても、buffer 全体を1つの `notice_msg` へ結合してから1回だけ呼ぶ設計ゆえ)。
- **60分窓で3回flush観測** = 本部長 registry 未登録起因の burst であり非定常。定常真値は判定不能
  (★二値に倒さず「判定不能」のまま残す★)。worst-case=72回/日 と明記 (楽観的な外挿はしない)。
- **9.3%流入増 → 周期37分→約34分** = 「圧縮であって根絶ではない」実測 (shogun-second.yaml は本機構と
  無関係な既存トラフィックのみで既に平均約37分周期で cap(50件)到達・退避を繰り返しており、追加書込みは
  退避頻度をわずかに早める。害の主因は本機構ではなくshogun-second.yaml自体の既存トラフィック)。
- cap=5 の根拠 (コード内コメント L282–286): 束ね無しなら9件の canon外 dead-letter (本日実測) が実便9通を
  消費する所、5件毎の束ねなら最大2通に圧縮できる。
- interval=300s の根拠: 既存 codebase の cooldown 慣例 (activity_monitor 監査間隔=120s 等) と同系統の桁。
  単発イベントが長時間未束ねのまま孤立するのを5分で打ち切る。

## 3. 陽性対照・陰性対照 (★sandbox化・実 queue/inbox 不触★)

止血命令 (karo-second msg_20260805_121348_364ebac2、本日12:13 発令・15:xx 断面でなお継続 —
`msg_20260805_140505_f11b5a2f` 系にも「bats実行はなお禁 (止血継続)」と明記) の対象は
「実 PROJECT_ROOT の `scripts/inbox_write.sh` を直に呼ぶ bats」。∴ 本検証は **bats を一切使わず**、
実関数のみを scratchpad へ抽出し、`_write_message` を no-op stub に差し替えて実行した
(実 `queue/inbox/*.yaml` ・実 `queue/dead_letter/` へは一切書込まぬ設計)。

harness: `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/de24e6d3-5826-480c-b068-faec7cab59b7/scratchpad/notice_sandbox/test_notice_bundle.sh`
(実行者=当職・本 turn・関数本体は現行 sha256 `d926aa1774dd8222273a4ea7053aa954dc111da6804b0e1aec7d47594592046b` の
L310–371 から `sed -n` で機械的に抽出 — 手で書き写していない)。

```
=== positive control 1: cap=5 束ね (5件投入で1回 flush) ===
[inbox_write] DISPATCH_NOTICE_FLUSHED: 5 pending unroutable notice(s) sent to 'sandbox_dispatcher'
flush count after 5 events: 1
CALLED dispatcher=sandbox_dispatcher type=unroutable_notice_bundle from=inbox_write body_lines=5

=== positive control 2: interval=300s 束ね (3件のみ→未flush) ===
flush count after 3 events (cap未到達): 0
buffer file exists with 3 pending line(s) (期待=3、未flush)

=== negative control (default): DISABLE=1 (既定) では _write_message が一度も呼ばれぬ事 ===
flush count with default DISABLE=1: 0 (期待=0)
buffer dir exists (期待=作られぬ): no
```

三値判定:
1. **cap=5 到達 → 1回のflush・5件が1便へ束ねられる**: 実測どおり (仮説どおり)。
2. **cap未到達・interval未到達 → flushせず buffer に留め置かれる**: 実測どおり (3件のまま buffer に残存、
   実箱への書込みは起きぬ)。
3. **既定 (DISABLE=1) → 機構そのものが無発火**: 実測どおり (`_write_message` 呼出0件・buffer dir すら作られぬ
   = 「委員長裁定まで既定無効」の主張が★出力で★裏付けられた。文言だけの主張ではない)。

age=300s (時間経過) 側の flush 条件は、`date +%s` に依存するため sandbox 内で待機せず実演は省略した
(★判定不能として残す★—時計を早送りする代替検証はしていない。必要なら `now_epoch` 相当変数の直接注入で
検証可能だが、関数を書き換えずに検証する手段を当職はまだ持たぬ)。

## 4. 【この修正が新たに開ける穴】(受入条件⑴・空欄不可)

コード内コメント (L288–297) に明記済:

- **束ね判定は「dead-letter事象が起きた瞬間」にしか評価されない** (新規常駐processは増やさぬ設計ゆえ)。
  ∴ ある1件が★最後の★dead-letter事象のまま以後二度と起きなければ、その1件の通知はpending bufferに
  溜まったままflushされず、差配者へ★永久に届かぬ★ (cap/intervalのどちらの条件も、次のdead-letter事象が
  来て初めて再評価されるため)。
- これは「和名で名乗る者は不達を永久に知り得ない」を「差配者への通知そのものが同じ病に罹り得る」形で
  再生産する余地であり、**根絶していない** — 単発かつ稀な最終イベントについては残存する。
- 併せて (§3 末尾): age=300s 条件そのものを sandbox 内で時計を進めて実演していない (時間経過をシミュレート
  する手段を当職は使わなかった) — ∴ interval flush の実装が「意図通り動く」ことは cap flush ほど強く
  実証できていない (コードの読解による確信はあるが、実測による確信ではない)。

## 5. 【本工区で 己が直した誤り】

**無し**。本機能の実装過程で当職が自ら検出・是正した誤りは無い(sandbox検証は§3の実測どおり初回で
期待値と一致した)。
なお、本機構をめぐる誤りの訂正が2件あったが、いずれも★当職の誤りではない★ (誤って自分の手柄/失点に
書かぬ為、出所を明記する):
- 「無警告削除」という危険描写は karo-second 自身の誤りであり、karo-second 自身が
  `msg_20260805_141246_06125769` で訂正した (正しくは CAP_ROTATED による告知つき退避)。
- 専用file案(③)の当初検討〜却下も委員長裁定によるものであり、当職の実装誤りではない。

## 6. ⑼ 同じ穴がまた開くのを止めるか

**止めぬ**。次に誰かが新規の dead-letter 経路を足しても、本機構は自動適用されず、また報せ忘れる穴が
再発し得る (karo-second 受理済 `msg_20260805_143615_551f7830`、backlog 種として計上済)。

## 7. 既定値・有効化の扱い (commit後も不変)

- **既定 = `INBOX_WRITE_DISPATCH_NOTICE_DISABLE=1` (無効)** — 足軽3号【第五】出口の門設計
  (`docs/incident_logs/2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md` §4-4「alt-signal の
  記録先を inbox.yaml 自身にするな」)との統合が上申中のため、二つの門を別々に立てぬ目的で commit 後も
  既定=1を保つ (karo-second 指示・当職はこれに従う。有効化判断は当職の権限外)。
- 有効化は `INBOX_WRITE_DISPATCH_NOTICE_DISABLE=0` を明示指定した時のみ。

## 8. 境界遵守声明

- 実 `queue/inbox/*.yaml`・実 `queue/dead_letter/*` へは§3検証時も一切書込んでいない (stub化・scratchpad限定)。
- bats 実行なし (止血継続中)。
- commit・push・stage なし (Third-Party Audit Rule により軍師 PASS が前提)。
- 影 file・dd189・process・registry 本体・墓場 file の改変なし (読むのみ)。
- 暫定二者制 (軍師second + Gemini)。Codex leg は SAFETY 裁定 seq132707 により停止中。

## 9. 【対に成る他工区】

- 足軽3号 = 【第五】出口の門 設計 (`2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md`) —
  本機構との統合待ち・§4-4 禁則が本機構の flush 先(shogun-second.yaml)と正面衝突していた経緯を含む。
- 足軽7号 = `_archive` 可読化 (本機構の flush 先が cap 到達で退避された場合の受け皿)。
- 足軽4号 = registry scope 欄設計。
- 当職(足軽2号) 自身 = `2026-08-05_from_arg_canon_or_wamei_survey_a2.md` (17件台帳・karo-second 承認済・
  gunshi-second 監査提出済 msg_20260805_143034_a5720e37・PASS 未確認)。
