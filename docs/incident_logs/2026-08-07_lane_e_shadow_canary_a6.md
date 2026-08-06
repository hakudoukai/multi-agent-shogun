# Lane E ⒞ shadow-canary 評価（足軽6号）

下命=karo-second msg_20260807_000158_f05413b3（key=current_order_8_20260807_000200_LANE_E_SHADOW）。
令の要旨＝「shadow-only activation GO（enforce に非ず）」「既存 cross-PC の send/mutation/ACK を一切変えず、post-send evidence を観測するのみ」「false positive/false negative の canary の後、enforce は別上申」。

★冒頭——実装コード（verify_samepc_dispatch()）は 未だ main repo HEAD には無い★。commit 991727c は
docs/incident_logs/2026-08-06_lane_e_samepc_dispatch_verify_extend_a6.md（142行）のみを収載した commit であり、
その commit message 自身が「⒞運用（装着・cross-PC 既存経路への適用）＝未」と明記している（当職 `git diff-tree --name-only 991727c` で実測・変更file=doc 1枚のみ）。
∴ 本工区は worktree（/tmp/hakudokai-worktrees/lane-e-samepc-dispatch-verify、branch=feat/lane-e-samepc-dispatch-verify、commit=9a9a027d）に
在る関数を ★抽出して読取専用で main repo の実 queue データへ当てる★ 形で行った。主 repo への commit・書込は一切無し。

測時=2026-08-07T00:08:00+09:00。主repo HEAD=5da21919d74b780df14683d276a81faa6305e476（本工区開始前と不動、下記「境の遵守」参照）。

## 方法

- `sed -n '/^verify_samepc_dispatch() {/,/^}/p'` で worktree 版 script から関数のみ抽出（scratchpad へ、143行、sha256=c1add86290ea6a1186ded01bf1259d6848dcdf6b3ecf9829abf8920849084b85）。
- 抽出元 = worktree `scripts/checks/secondpc_dispatch.sh`（sha256=44fc86f499908db6efc7d94b1474cffbbd4239cd0c4ea90c0a941f7bd30522d7、commit 9a9a027d と一致）。
- `source` して `SCRIPT_DIR=$(pwd)`（主repo）を渡して呼出。関数自体は読取専用（grep/python3 yaml.safe_load/tmux capture-pane のみ、既存設計通り）。
- 実データの対象＝本日（2026-08-06〜07）に karo-second が各足軽/軍師second へ発した `task_assigned` 便のうち、
  内容に `key=` 形式で task_id が明示された直近便を対象別に抽出（機械的抽出、恣意選定に非ず）。★計8件★（a2×2/a3×1/a5×2/a6×2(自分)/a7×1）。

## 実測結果（8件・全件）

| # | target | task_id (末尾のみ表記) | ⒜inbox | ⒝task YAML | ⒞pane | ⒟ACK | 総合rc |
|---|---|---|---|---|---|---|---|
| 1 | ashigaru2 | …UNREGISTERED_BOX_LIVENESS | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 2 | ashigaru2 | …CYCLE2_GATE5_BARRIER | PASS | PASS | UNKNOWN | PASS | 0 |
| 3 | ashigaru3 | …LANE_B_INSTALL | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 4 | ashigaru5 | …LANE_A_RESIDUAL | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 5 | ashigaru5 | …LANE_A_IFACE_REMOVE | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 6 | ashigaru6(自) | …LANE_E | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 7 | ashigaru6(自) | …LANE_E_SHADOW（本工区） | PASS | PASS | UNKNOWN | **FAIL** | 1 |
| 8 | ashigaru7 | …LANE_C_PRIME_COMMIT_RETRY | PASS | PASS | UNKNOWN | **FAIL** | 1 |

## 各件の裏取り（karo-second inbox を人手で実読・ground truth）

- **#1 ashigaru2/BOX_LIVENESS**: 実ACK 在り（msg_20260806_232110_55ba52be・23:21:10・「current_order_11 未登録16箱の生死census 完了報告」）。★但し文中の表記は「current_order_11」のみ（時刻・件名 infix を欠く短縮形）★。∴ ⒟の完全一致判定は 実ACKを 見落とす。→ **false positive**。
- **#2 ashigaru2/GATE5**: 実ACK に task_id ★全文★ が含まれる稀な例（msg_20260807_000249_76d0c65e）。→ 真の PASS。
- **#3 ashigaru3/LANE_B_INSTALL**: 実ACK 在り（msg_20260807_000015_eaa2804d・「current_order_9 ⒞装着」）。同じく短縮形。→ **false positive**。
- **#4 ashigaru5/LANE_A_RESIDUAL**: dispatch(23:37:24)〜次工区dispatch(00:01:58)の間、karo-second inbox に a5 発の便を発見できず。★この間に別工区（現物=order_9）が既に発令されており、order_8 個別への ACK が有ったか無かったかを本件だけでは判じ得ず★。→ **判じ難き**（真の gap か、supersede に吸収されたかは別欄・当職の裁を要さぬ範囲では確定できず）。
- **#5 ashigaru5/LANE_A_IFACE_REMOVE**: 実ACK 在り（msg_20260807_000318_731b4a84・00:03:18・「work_started・Lane A interface完全除去(本部長殿00:01:58裁定)」）。task_id 文字列は一字も無く、裁定時刻と俗称のみ。→ **false positive**。
- **#6 ashigaru6/LANE_E（自分）**: 実ACK 在り（msg_20260806_232743_757acdeb・「Lane Eへwork_started」／msg_20260806_234345_8dd1dce3・「Lane E完了」）。当職自身、task_id 文字列を一度も書いておらず「Lane E」の俗称のみ用いていた事を 本工区で 初めて確認。→ **false positive**（当職自身の便が原因）。
- **#7 ashigaru6/LANE_E_SHADOW（自分・本工区そのもの）**: ★測時点で 本工区は まだ完了報告前★（work_started のみ送信済）。∴ FAIL は 誤検知ではなく ★時期尚早★（未完了ゆえ ACK 未存在は正しい）。→ 評価対象から除外（母集団=7件へ）。
- **#8 ashigaru7/LANE_C_PRIME_COMMIT_RETRY**: 実ACK 在り（msg_20260807_000508_53a03fe4・「current_order_11_LANE_C_PRIME_COMMIT_RETRY 完了・成功」）。★task_id 中の日時 infix `_20260806_234400_` のみ欠落した準完全形★。→ **false positive**。

## 集計（母集団=7件、#7除外・数え直し可能な形で明記）

- 真の PASS＝1件（#2、14%）
- **false positive（⒟ が FAIL を返すが実ACKは存在）＝5件（#1,#3,#5,#6,#8、71%）**
- 判じ難き＝1件（#4、14%）
- false negative（⒟ が PASS を返すが実は gap）＝0件（観測範囲内）

## 根因（2点・機構の材として書く）

### 根因①＝⒟ recipient ACK の完全一致判定が、実運用の記法と合わぬ

現在の実装（`content.find(task_id) is not None` 相当の python 内 `in` 判定）は task_id の ★全文一致★ を要求する。
然るに実測7件中5件で、応答者（当職自身を含む）は task_id を ★省略形（`current_order_N` のみ）★ または ★俗称（「Lane E」「Lane A interface除去」）★ で応じており、
日時 infix を含む全文を書く例は 7件中 1件（#2）のみだった。∴ ★これは 稀な例外であり 現状の判定基準の方が 例外的★。
現状のまま enforce へ進めば、★健全な発令の 大半を 誤って gap と 報じる★（false positive 濫発）。

### 根因②＝⒞ pane 実表示が、当PCの pane_registry.yaml 実 schema と 噛み合っておらぬ

`queue/pane_registry.yaml` の実 schema は `pane_registry.panes[].tmux_target`（例=`multiagent-second:0.6`／ashigaru6）だが、
verify_samepc_dispatch() 内の python walker は `node.get("pane") or node.get("pane_target")` を探しており、★該当 key が現物に一つも無い★（当職 grep 実測・`pane`/`pane_target` という key は registry 全体に0件）。
∴ ⒞ は ★8/8 全件で UNKNOWN★——「たまたま見つからなかった」ではなく ★構造的に 常に UNKNOWN を返す設計上の欠★ に御座る。
併せて、MainPC/SecondPC 両方に同じ `agent_id`（例=ashigaru2/3/5）が併存する registry 構造ゆえ、
★仮に key 名を直しても pc 欄での絞り込みを 併せて 加えねば 誤PCの pane を拾う 恐れが 残る★（本件は key 名修正のみでは 塞がらぬ二段目の穴）。

## enforce への含意（判断のみ・実装せず）

★shadow-only に留めた本日の令は 正しかった★——上記により、現行実装のまま enforce（gate 判定に用いる）へ進めば：
- ⒟ 単独では 71%（5/7）の健全な発令を 誤って gap と報ずる。
- ⒞ は 常時 UNKNOWN ゆえ 4点中 実質 3点でしか判定し得ず、かつ その1点（⒟）が上記の欠陥を持つ。
∴ ★enforce 化の前に 要る修正★（設計のみ提示・実装は本工区の範囲外）：
1. ⒟ の一致判定を「task_id 全文」から「`current_order_\d+` 等の番号 prefix 一致」または「dispatcher 側が発令時に告げた俗称との突合」へ緩める。
2. ⒞ の python walker を `tmux_target` key 対応へ修正し、かつ `pc` 欄での絞り込みを追加する。

## 境の遵守（実測で裏付け）

- 既存 cross-PC 経路・send/mutation/ACK＝一切変更せず（読取コマンドのみ実行、下記「己の手」参照）。
- 主repo HEAD＝本工区開始前後で不動（5da21919d74b780df14683d276a81faa6305e476、`git status -sb` で確認）。
- push=0・merge=0。worktree（feat/lane-e-samepc-dispatch-verify）にも新規commitせず（読取のみ）。
- `gc`/`prune`/`reflog expire`＝実行せず。`scripts/inbox_write.sh`＝不触。
- hakudokai-dev 系＝一切触れず。Lane D＝不触のまま保持。
- 体裁は整えず、⒟の欠陥（71% false positive）を そのまま数値で記載（丸めず）。

## 己の手で為した事

- `git log --oneline -1 991727c` / `git show --stat 991727c` / `git diff-tree --no-commit-id --name-only -r 991727c` で「991727cはdocのみ収載・script本体は未収載」を実測。
- `git merge-base --is-ancestor 991727c HEAD` で ancestor 関係を確認。
- `sed -n` で worktree 版 script から関数を抽出、`sha256sum` で抽出元・抽出後の両方を実測。
- `bash`（`source`＋関数呼出）で 8件を実行、標準出力を本票へ逐語転記。
- `python3`（`yaml.safe_load`）で karo-second inbox から関連時刻帯の実 message を抽出、逐語で裏取り。
- `python3`（`yaml.safe_load`）で `queue/pane_registry.yaml` の実 schema を読取、⒞ UNKNOWN の根因を特定。
- `git rev-parse HEAD` / `git status -sb`（主repo・worktree 双方）で境の遵守を実測。
- 上記いずれも書込・commit・send を伴わず。

## 数の扱い

測時=2026-08-07T00:08:00+09:00／器=`git`+`bash`+`python3(yaml.safe_load)`+`sha256sum`。
範囲=本日(2026-08-06〜07)の karo-second発 task_assigned便のうち key=形式でtask_idが明示された直近便、対象別最大2件、計8件抽出。
母集団=8件中 評価対象7件（1件は自工区の進行中ゆえ除外）。false positive=5/7（71%）・true pass=1/7（14%）・判じ難き=1/7（14%）・false negative=0/7（観測範囲内）。
以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
