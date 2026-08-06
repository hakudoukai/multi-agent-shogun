# E-3 共通guard 限定再測（足軽6号）

下命=karo-second msg_20260807_015857_53b6a15c（本部長殿 01:56:12・exactly-once・current_order_10欄の trigger_arrived=2026-08-07T01:59として更新済）。
target=4a0e9036ed94022d79baa4a1e2cf88d5827eec12（immutable detached、足軽1号作、
"fix(appointment): E-3根治 — move_appointment_slotへcancelled/no_show guardを一元化 (current_order_13⒜⒝)"）。
scope=★共通guard一元化／呼び手無変更／old RED → target GREEN の限定再測のみ★。実装fix0・commit0・push0・merge0。a1の木は read のみ。

★記録の語＝「4a0e9036 の ⒜⒝ 断面 PASS／FAIL」★。★五述語全体PASSとは書かぬ★。②③④⑤（current_order_13の他部分）は本工区の射程外＝未達expectedであり欠陥数へ混ぜぬ。

## 先に実施（下命 ⒜⒝）

⒜ 外部handoff復元＝`/tmp/.../scratchpad/a6_compact_handoff_20260807T0101.md`（sha256=9d76b4c3fee9b7a7e94cb2b614c25366b849063de15dd46b5a20c1680d21c0e9、43行）を実読、保持task・禁則・直近3提出物を復元確認。
⒝ auto-clear保護の再確認＝現行 `scripts/inbox_watcher.sh` を実読（stale .bak不使用）。`is_no_auto_clear_agent()`（L797-806）に自分（ashigaru6）が現に含まれ、`send_context_reset()`（L856-858）・`clear_command`処理（L1340-1347）双方で抑止が生きている事を実測確認。保護は現行主線に生存。

## 対象（a1の木・読取専用）

- 場所=/tmp/resimg-verify4-cycle2-matrix2-20260807（既にHEAD=4a0e9036detached、work_started時点でも作業終了時点でも `git status --short` は当職起因の変更0——他agent由来の未追跡file2件（`detect_undelegated_occupancy_mutation_a4.py`／`verify_b2_status_only_a4_ephemeral.py`）は当職着手前より存在・不触）。
- target commitのblob sha256を実read直後に照合（改変無きを担保）：
  - `backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py` = 23e7fd3a5ec462e214b4ecf0d458f8c7304a2685d64781948851192848b804cb（作業tree一致）
  - `backend/tests/test_true_concurrency_barrier_a1.py` = 9971edd94b659766bda3b51f5649473e0d26088d0b8b309a58875503505044cd（作業tree一致）
  - `backend/services/appointment_lifecycle.py`（guard込み target版） = 2ade6cf52b250378fd9aae405529f5a3c1d256c228043ec2aaf682e1f18217d7（作業tree一致）

## 方法（a1の木を一切書かず、自前scratch複製2本で再測）

1. `/tmp/resimg-e3-guard-rerun-a6-20260807/{target,old}/backend` へ `cp -r` で物理複製2本作成（symlink不使用）。直後 `diff -rq` で複製元との完全一致を確認（差分0）。
2. `target/` = 複製そのまま（=guard込み4a0e9036状態）。
3. `old/` = `git -C <a1木> show 14cad3a...(親commit):backend/services/appointment_lifecycle.py` を複製先のみへ上書き（a1の木へは書込0・`git show`は読取のみ）。guard文言 `cannot move slot for inactive appointment` の grep件数=0（old）／1（target）で新旧の切替を機械確認。
4. venv=`/tmp/resimg-stage1-runtime-venv`（pytest 9.1.1／fastapi 0.141.1、既存資産・新規構築せず）。
5. pytest実行後、a1の木を再度 `git status --short`＋`git rev-parse HEAD` で確認（不動）。

## 実測結果

### ⒜ old RED → target GREEN（cancelled/no_show move guard）

`backend/tests/test_move_appointment_slot_inactive_guard_e3_a1.py` を old/target 両複製で実行：

- **old（guard文言0=旧構成再現）＝RED**：`3 failed, 1 passed`。失敗3件は悉く「DID NOT RAISE ValueError」（domain直呼2件＋実呼び手1件=booking_manage.change_booking経由）。通過1件は陽性対照（active予約は従来通り成功）——guard欠如時のみ失敗する構造を確認、偽陰性ではない。
- **target（guard文言1=4a0e9036そのまま）＝GREEN**：`4 passed, 0 failed`（同一4 test、warnings 2件のみ・fastapi/httpx非推奨警告と無関係）。

∴ ⒜ = **PASS**（old RED を自前複製で独立再現した上で target GREEN を確認。a1の報告の丸写しに非ず）。

### ⒝ old RED → target GREEN（move/reschedule 真並行 15分ずれ overlap）

`backend/tests/test_true_concurrency_barrier_a1.py -k "move_RED or move_GREEN"` を target で実行（本ペアはtarget commit内で apply_root=False/True を自己内包する双子testゆえ、旧木への checkout 無しで両方の断面を1回の実行で機械的に確認可能——⒜と異なり old-tree 再現を要さぬ設計）：

- `test_true_concurrency_move_RED_without_concurrency_root_double_books`（apply_root=False=旧構成相当）＝**PASSED**——「両thread成功・moved_count==2（二重move成立）」という★RED相当の不具合が現に再現する事★をassertし、その通り実測された（=旧構成は真にRED挙動を持つ事の裏付け）。
- `test_true_concurrency_move_GREEN_with_concurrency_root_prevents_double_booking`（apply_root=True=target現行構成）＝**PASSED**——「1thread成功・他1threadはIntegrityError・moved_count==1・claims==2」という★GREEN挙動★を実測。
- 計 `2 passed, 2 deselected in 8.97s`。

∴ ⒝ = **PASS**（old構成のRED挙動・target構成のGREEN挙動の双方を、target commit1点の実行のみで機械的に再現確認）。

## 断面（記録の語・下命の指定通り）

**4a0e9036 の ⒜⒝ 断面 ＝ PASS／PASS**（⒜=old RED→target GREEN 実測確認・⒝=old RED挙動／target GREEN挙動 双方実測確認）。

②③④⑤（current_order_13の他要素）＝本工区の射程外。未達expectedゆえ欠陥数へ混ぜず、本票では言及も評価もしない。

## 境の遵守

- 実装fix=0・commit=0・push=0・merge=0（主repo・a1木ともに）。
- a1の木（/tmp/resimg-verify4-cycle2-matrix2-20260807）＝終始 read のみ（`git show`のみ・checkout/reset/stash等の破壊系コマンドは一度も使わず）。work_started直後と全実行後の双方で `git status --short`＋HEAD不動（4a0e9036）を実測確認。
- 己の複製・改変は自前scratch（/tmp/resimg-e3-guard-rerun-a6-20260807）内のみに限定。
- 主repo HEAD不動（4a0e9036参照は誤読防止のため作業directory切替のみ・主repoへのcheckoutは実施せず、主repo上でのgit rev-parse HEADは本票作成時点のものであり別途確認）。

## 数の扱い

測時=2026-08-07T02:0x+09:00（JST）。器=`git show`（読取のみ）+`cp -r`+`diff -rq`+`sha256sum`+pytest 9.1.1（venv=/tmp/resimg-stage1-runtime-venv）。
範囲=target commit 4a0e9036が追加した2 test file中、⒜=新設4 test全数・⒝=新設2 test中「move_RED／move_GREEN」の2件（他2件はcreate経路の既存testゆえ本工区の限定再測=E-3move guard対象外、deselected扱い・除外理由明記）。
以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
