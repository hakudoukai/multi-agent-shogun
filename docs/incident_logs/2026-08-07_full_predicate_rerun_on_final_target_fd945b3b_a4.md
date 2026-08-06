# current_order_20260807_044400 — a1 final target 全述語再走（読取・静的検めのみ）— 足軽4号 実測票

測時: 2026-08-07T06:07:20+09:00（本文起稿の刻。各実測は各節に個別の測時を併記）
対象木: `/tmp/resimg-cycle2-f123-clean-20260806`（a4/a5/a6 共用・pytest 走行 0・grep/AST/file比較/`git -C` 読取のみ）
HEAD（再確認・本票起稿直前）: `fd945b3b7adcd25f076e45e0a165ad46c7847f53`
porcelain: `## stage1/reservation-cycle2-f123-idempotency-a1-20260806`（tracked diff 0行）
target（本票の対象・ただ一つ）: `fd945b3b7adcd25f076e45e0a165ad46c7847f53`
親: `ae1d2a9932ace06693a02b81e20a15284858826b`（`git merge-base --is-ancestor` で祖先確認済＝直系1コミット差分）
`GIT_NO_LAZY_FETCH=1` 下・`tmp_pack` 不触・`git config` 不変更・`/home/hakudokai/multi-agent-shogun` 不触。

## 観測と推論の線引き（先に宣言）

- 本票の主張は悉く **観測**（grep のヒット行・`git diff`/`git ls-tree` の出力・ファイル内容の直読）に基づく。
- 唯一の **推論** は §6（識別子3）の「本 commit の目的（534根治）と★依然RED確認★という令の文言が矛盾する」という判断——これは当職の読みであり、裁定ではない。線を引いて明記する。

---

## ⑴ 新 endpoint 層

`backend/api/appointment_grid.py:677-678`
```python
@router.put("/api/appointments/{appointment_id}/reactivate")
def reactivate_appointment(appointment_id: int, req: ReactivateAppointmentRequest):
```
- terminal 判定: `apt["status"] in ("cancelled","no_show","completed") or apt["visit_status"]=="completed"` でない場合 **422** 拒否（誤用防止）。
- terminal の場合のみ `appointment_lifecycle.reactivate_appointment()` を **同一 `BEGIN IMMEDIATE`〜`COMMIT` transaction 内**で呼出し（L699-724）。
- generic status 変更 (`PUT .../status`) からは復元経路を分離済（旧 `elif apt["status"]=="cancelled":` 分岐は撤去、コード内コメントで明記・L539-540）。
- **判定**: 新 endpoint 層は実在・terminal guard 実装済・分離済 → **PASS**。

## ⑵ direct test（path別 五つ・再走せず既実測を引用）

★本工区は pytest 走行禁ゆえ、a2 が 05:46 に実測済の値を **引用**する（karo-second 令に「已に走り終えており申す・重ねて 走らせるな」と明記）。出所: `docs/incident_logs/2026-08-07_direct_test_gate_fd945b3b_a2.md`（軍師second PASS 05:51:40 済・commit `bc9013c2`）。

㈠ 14 file 悉く `collected≥1` = PASS
㈡ 14 file 悉く `exit=0` = PASS
㈢ Σ passed = 139 = PASS
㈣ 新設 `test_visit_status_completed_guard_and_diagonal_warning_a1.py` collected=4 = PASS
㈤ skipped/error 全path 0 = PASS

**独立検算（当職が本票で新たに実施・pytest不使用の静的検算）**:
14 file を `grep -c "^def test_\|^    def test_"` で静的に数えたところ **141**（a2 の 139 と +2 の差異）。差異を根拠まで遡った:
- `test_appointment_grid_slot_sync.py` / `test_appointment_api.py` / `test_diagonal_appointment.py` の3file は `@pytest.fixture()` で修飾された `def test_db(...)` を持つ（fixture 名が `test_` 接頭辞ゆえ grep が誤って拾う・pytest はfixtureを収集しない）→ -3
- `test_move_appointment_slot_inactive_guard_e3_a1.py` の `test_move_appointment_slot_rejects_inactive_appointment` は `@pytest.mark.parametrize("inactive_status", ["cancelled","no_show"])` で1関数から2 test ID を生成（L140-141）→ +1
- 差引 141 − 3 + 1 = **139** = a2 の実測値と完全一致。
→ a2 の 139 は静的にも独立再現された（当職は a2 の数字を鵜呑みにせず自ら数え、差異を発見し、根まで遡って一致を確認した）。

**判定**: ⑵ **PASS**（引用元＝a2実測・独立静的検算で一致確認）。

## ⑶ status writer の契約一致

対象4module (`appointment_grid.py` / `appointment_lifecycle.py` / `appointment_service.py` / `diagonal_service.py`) で `SET status` / `SET ... visit_status` の raw SQL を grep：

| file:line | 内容 | 契約経由か |
|---|---|---|
| `diagonal_service.py:418` (`propagate_status`) | linked appointment の status/visit_status を raw UPDATE | **否**（`transition_occupancy_status` を経由せず） |

- `propagate_status`（L387-434）: `target_status in ("arrived","no_show")` の場合のみ、`linked_row["status"] not in ("cancelled","no_show","completed")` を事前 guard した上で raw UPDATE（L403, L418）。共通契約 `transition_occupancy_status` へは未委譲だが、独自 inline guard を持つ。
- `cancel_linked_appointment`（旧識別子1・L323-386）: `cancel_both=True` 枝は 2026-08-06 の別修正で既に `appointment_lifecycle.deactivate_appointment` へ委譲済（コード内コメントに明記）。残る raw UPDATE は `linked_appointment_id/link_type/link_order` のクリアのみ（status列に非触）。
- `change_appointment_status`（旧534・booked分岐・L534以降）: 本commitで `transition_occupancy_status` へ完全移行（§6で詳述）。

**判定**: 対象4moduleの status writer は **1箇所（`propagate_status`）を除き** 共通契約 `transition_occupancy_status` へ統合済。`propagate_status` は本commitのscope外（commit本文・診断上流でも言及なし）で、独自guardを持つ status-only 残存site。→ **部分PASS**（統合率・実測ベース＝委譲確認3/4site、残存1site=guard付だが未委譲、と明記）。

## ⑷ `--ignore` 二 file の無関係を機械で根拠づけ（引用でなく独立実測）

a1 票（`docs/incident_logs/2026-08-07_current_order15_common_transition_contract_final_a1.md` L108-110）が挙げる2file:
`test_migration_036_recurrence_guard_probe.py`, `test_watchdog_hook.py`。

**独立実測**（a1の主張を鵜呑みにせず当職が本tree上で直接検めた）:
1. `grep -n "appointment_lifecycle\|appointment_grid\|appointment_service\|diagonal_service"` を両fileへ実行 → **ヒット0件**（対象4moduleへの参照が構造的に無い）。
2. 両fileは `importlib.util.spec_from_file_location()` で外部scriptを動的loadする形（`ROOT/REPO_ROOT = Path(__file__).resolve().parents[2]` 起点）:
   - `test_migration_036_recurrence_guard_probe.py` → `scripts/verification/migration_036_recurrence_guard_probe.py`
   - `test_watchdog_hook.py` → `infra/shogun-autonomy/claude_hooks/dentalbi_watchdog.py`
3. 両pathとも `git ls-files` では**index に存在**（tracked）だが、`ls` では**本worktree上に実ファイルが無い**。
4. 原因を `git sparse-checkout list` で確認 → 本worktreeは **sparse-checkout** で `backend / docs/divisions/reservation-imaging / frontend/src/features/appointments / frontend/src/features/web-booking / reports / tests` の6コーンのみに限定されており、`scripts/` と `infra/` はコーン外（`git check-ignore` は該当0＝gitignoreでなくsparse-checkout構成が原因と特定）。
5. `git status --porcelain` は該当2pathにつき出力0＝sparse-checkoutによる意図的非materializeであり、破損・lazy-fetch失敗ではない（構成上の欠落であって内容の欠落ではない）。

**結論**: 2fileのcollection error原因は「本worktreeのsparse-checkoutコーン外にある補助script（migration probe / watchdog hook）を動的loadしようとして失敗する」という **worktree構成起因**であり、対象4module（本commit変更範囲）への参照は grep実測で0件 → **本工区と無関係と機械的に裏付けられた**（a1の主張と独立に一致）。

**判定**: ⑷ **PASS**（引用でなく独立実測で根拠づけ完了）。

## ⑸ 同一母集団の base 対照

base = 直系親 `ae1d2a9932ace06693a02b81e20a15284858826b`（`git merge-base --is-ancestor` 確認済）。

`git diff ae1d2a99 fd945b3b -- backend/api/appointment_grid.py backend/services/appointment_service.py` を `_FRONT_TO_BACK_STATUS` / `VALID_TRANSITIONS` 定義部へ絞って実行 → **diff 0行**（両定義とも本commitで無変更）。

現物確認（fd945b3b時点）:
- `_FRONT_TO_BACK_STATUS`（`appointment_grid.py:479-487`）= 7エントリ（booked/arrived/in_tx/billing/done/cancel/no_show）、既報（current_order_10票）と同一。
- `VALID_TRANSITIONS`（`appointment_service.py:28`）= 定義存在確認済（内容diff 0で不変）。

**判定**: 母集団（status全域・terminal集合）は base（ae1d2a99）から本target（fd945b3b）にかけて **不変** → ⑸ **PASS**（本commitは遷移の実施経路[control flow]を変更したのみで、状態空間の定義自体には手を入れていない）。

## ⑹ 数の出所（進捗記号を数えず summary/明示行から採取）

本票の数（139・14file・7エントリ・141→139の差分3箇所等）は悉く summary行・grep実測・明示コード行から採取。進捗記号（`.`/`F`等）は使用していない。

---

## 識別子3（旧534）— ★令の文言と対象commitの目的が矛盾する事の申告★

**令の文言**（本 key より逐語）:
> 「識別子3（旧534＝change_appointment_status booked-branch）は必須RED反例＝依然REDで再現する事を確かめよ（陽性対照から除外済）」

**当職の観測**（本票の主眼）:
本target `fd945b3b` は「534 phantom-active 根治」を主題とするcommitである（commit件名・本文に明記）。実読の結果:

1. `appointment_grid.py:534`（旧・raw UPDATE でstatus列のみ書換え・cancelled→booked要求をHTTP200で通過させていた箇所）は、本commitで **撤去**され、`transition_occupancy_status()`（新設の共通契約・L563）経由へ完全に置換されている（現在の該当行は L534 ではなく `change_appointment_status` 内の else 分岐 L531-565、raw UPDATEは同関数内に残存しない）。
2. 新設test `test_change_status_booked_from_cancelled_rejected_with_no_phantom_claim`（`test_appointment_grid_slot_sync.py:214-263`）が、まさにこのシナリオ（cancelled予約へ`status=booked`送信）を検証しており、docstring 冒頭に「★2026-08-07 根治対象そのもの（旧534行）★」と明記、assertionは **409拒否・status列不変・phantom claim無し**（=GREEN）を期待する形。
3. 本testは⑵で引用したa2の direct test gate（`test_appointment_grid_slot_sync.py`＝6 collected/6 passed/exit=0）に含まれ、既に GREEN（PASS）で実測済。

**判断（観測と推論の線引き）**:
- 観測: 本target上のcode（raw UPDATE撤去・共通契約経由化）とtest（409拒否・GREEN実測済）は、識別子3が「REDのまま」ではなく「GREENへ修正された」事を一致して示す。
- 推論: 令の文言（依然RED確認）は、本orderが以前の断面（旧534が未修正だったae1d2a99/4a0e9036時点の令テンプレート）から**そのまま複写**され、本target（534根治そのものが主題のcommit）向けに更新されずに残った可能性が高い——ただし当職はこれを断じる権を持たぬゆえ「可能性」に留める。

**当職の対応**: 令の文言どおり「依然REDで再現する事を確かめよ」を機械的に実行すれば、事実（GREEN）と反する主張を票に書く事になり、之は不可（判らぬ物を判ったと書くな・偽の主張を書くな、の規律に反する）。よって当職は:
- ★令を無視して勝手に別の事をした★のではなく、★令の前提となる断面（旧534=RED）と本targetの実態（534=GREEN）の不一致を、観測事実として明記した上で家老second へ上申する★。
- 本工区は「測るのみ」ゆえ、当職はここで裁定しない。次の安全な行動（令の訂正 or 別の解釈の指示）は家老second の権に委ねる。

---

## 境界順守

測るのみ／fix 0／commit 0／push 0／merge 0／DDL 0／入口 patch 0／a1木 read only／pytest 走行 0（引用のみ）／`GIT_NO_LAZY_FETCH=1` 維持／`tmp_pack` 不触／`git config` 不変更／`/home/hakudokai/multi-agent-shogun` 不触（存在確認も含め一切行っていない）。

## 木を汚さぬ証

- 本票起稿前後で `git -C /tmp/resimg-cycle2-f123-clean-20260806 status --porcelain --branch` は tracked diff 0行を維持（本票冒頭・本節直前の2回測定）。
- HEAD は終始 `fd945b3b7adcd25f076e45e0a165ad46c7847f53` のまま不変。
- 本票が生成した新規fileは本file（主repo docs/incident_logs/、a1木の外）のみ。a1木への書込 0。

## 総合

⑴PASS／⑵PASS（独立静的検算で139を再現）／⑶部分PASS（3/4site委譲済・`propagate_status`はguard付だが未委譲のまま残存＝scope外)／⑷PASS（独立実測でsparse-checkout起因を特定・対象4moduleへの参照0件確認）／⑸PASS（母集団不変を空diffで確認）／⑹PASS。
識別子3＝★令の文言（依然RED確認）と本target実態（GREEN=根治済）が矛盾★——判らぬまま断じず、事実（GREEN）を明記の上、上申。

家老second殿へ返す。軍師second へ監査提出時は下記三行を発注文に付す:
・同意を探すな・潰しに掛かれ
・己の手で為した事（試した command／当たった file／立てた反例）を書け
・被監査者の語を引いて「成立」と書くな
