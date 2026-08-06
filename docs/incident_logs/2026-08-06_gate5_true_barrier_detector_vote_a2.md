# Gate⑸ true barrier detector — 最終票（ashigaru2 収載）

## 来歴（収載時 必須節・current_order_14_20260807_003300_GATE5_VOTE_PROVENANCE ㈡）

- ⒜ **正本の所在**: 本票の正本は **repo file ではなく inbox 転記本文** である。一次の全文は `queue/inbox/karo-second.yaml` の `msg_20260807_000249_76d0c65e`（2026-08-07T00:02:49・ashigaru2→karo-second）。同内容が監査提出用に再転記された先は `queue/inbox/gunshi-second.yaml` の `msg_20260807_000349_f406db1c`（2026-08-07T00:03:49・ashigaru2→gunshi-second）。
- ⒝ **軍師secondの監査の性質**: 監査票 `queue/reports/gunshi_second_gate5_true_barrier_detector_audit_20260806.md` は `scope: material` と明記され、`target` 欄に `queue/inbox/gunshi-second.yaml 内 msg_20260807_000349_f406db1c 転記本文` と `/tmp/resimg-verify2-cycle2-barrier-20260806/backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py` の両方が挙げられている。すなわち **inbox転記本文と実 test file を照合した material 監査** であり、repo内のこの票そのものを対象にした監査ではない（本票は当該監査の後に収載された）。verdict = `PASS`。
- ⒞ **repo内に原本が無かった事**: 上記監査票は自ら残の第5項に「repo 配下の incident log 正本 path は便内で明示されず、当方は inbox 転記本文を source として裁いた」と記す。当職（ashigaru2）も本収載作業時に `docs/incident_logs/` 配下を検めたが、本票と同内容の file は **収載直前まで存在しなかった**（`grep -rl "Gate⑸ true barrier detector" docs/` = 0件、実測）。∴ **PASS判定時点で本票の repo file は存在せず、監査は inbox 転記本文のみを material として為された**。

★事後に綺麗に見せるな（current_order_14 ㈢）★ — 上記は「無かった」を無かったまま書いたものであり、収載により遡って「最初から repo に在った」ことにはならない。

---

## 以下、転記（inbox 一次全文・一字一句そのまま・誤字脱字も含め訂正なし）

出所: `queue/inbox/karo-second.yaml` `msg_20260807_000249_76d0c65e`（2026-08-07T00:02:49・ashigaru2→karo-second・type=report_received）

> [足軽2号→家老second] ★Gate⑸ true barrier detector★ 完了報告（current_order_12_20260806_234100_CYCLE2_GATE5_BARRIER）
>
> ■ 返せ（別段）
> recipient ACK = 拝受・着手・完了（本便にて）
> pane = %5 multiagent-second:0.2
> base = e88e7582fa2c8d83e4617cec962a5724df8ad695（当職worktree HEAD・不変・下記実測）
> worktree = path=/tmp/resimg-verify2-cycle2-barrier-20260806 branch=ashigaru2-verify-cycle2-barrier-20260806（新規local isolated worktree・stage1-runtime repoの主worktree HEAD=7d463ed(branch stage1/reservation-cycle1-canonical-flow)不変を確認済）
> 最初のRED = test_offset_overlap_barrier_RED_on_pre_root_schema → PASSED（★厳密な実行時刻ログは取っておらぬ★＝worktree作成測時2026-08-06T23:47:00と本便測時2026-08-07T00:02:30の間・下記§2詳細）
>
> ■ §1 harness genuineness（禁㈠逐次2connection＝禁、の検め）
> backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py（base e88e7582時点で実在・424行・当職独自にsha256実測=e3d46d4857c4033e6974af6c3beac4723962dcb598312225e1c876eabb275163）を全文読了。
> ★真の並行と判定★＝_run_two_barrier_workers()（L128-149）が threading.Barrier(2) を生成し、2本の threading.Thread を start() で同時起動、各threadが★別々のsqlite3.connect()★（worker毎に独立connection）を持ち、precheck通過後〜claim/commit直前で barrier.wait() に到達した瞬間に同時解放される構造。逐次呼出し（2 connectionを順番に叩く形）ではない。
> ★注★：a4殿が§0で報告したsha(5d739167…)は990e5ad時点の値であり、当職が実測したe3d46d48…はe88e7582時点の値（990e5ad→51f644f→21f7a76→e1ace1c→e88e758の4commitでkaro-second殿指示によるrefactor/docstring追記が入っている）。★両者は別commitゆえsha不一致は正常・矛盾ではない★（写し間違いではなく別断面）。
>
> ■ §2 RED独立再現（同一unchanged harness・当職独自worktree・独自pytest実行）
> $ cd /tmp/resimg-verify2-cycle2-barrier-20260806 && /tmp/resimg-stage1-runtime-venv/bin/python -m pytest backend/tests/test_reserveimage_cycle2_barrier_concurrency_a4.py::test_offset_overlap_barrier_RED_on_pre_root_schema -v -s
> → F2BARRIER_OFFSET_RED_SUCCESS=2 ERRORS=[] / F2BARRIER_OFFSET_RED_ACTIVE=2 → PASSED
> ★旧欠陥（pre-root schema=apply_booking_concurrency_root未適用）下でoffset overlap（15分ずれ部分重複）が両者成功する事＝RED を、a4殿とは独立の worktree・独立のpytest実行で再現した。
>
> ■ §3 GREEN独立再現（同一unchanged harness・全5 test）
> 同worktreeで全5 testを実行、5件全PASS（web-vs-web / web-vs-web dual-guard exact-time / offset-overlap RED / web-vs-staff / offset-overlap GREEN）。
> ★flakiness検め★＝同コマンドを計5回連続実行、毎回5/5 PASS（合計25回の個別test実行で不安定なし・実行時間18.5〜22.1秒でばらつきは通常のI/O揺らぎの範囲）。barrierによる真の並行が運任せの偶然一致でない事を回数で確認。
>
> ■ §4 述語の検め（★本夜最も重き一条・数でなく述語★）
> 本部長殿の受入述語＝「未委譲reachable case＝0」「residual raw SQL＝0または非occupancy根拠」。
> 当職の実測結果＝★述語は満たされておらぬ（0ではない）★。
>
> 未委譲・reachableな raw SQL による appointments 直接INSERT を3箇所発見（claim_appointment_slots・_check_conflict のいずれも呼ばず、appointments tableへ直接書込む経路）:
>   ⒜ backend/services/diagonal_service.py L117・L146（INSERT INTO appointments ×2、斜め予約）
>      ガードは check_double_booking()（appointment_service.py L72-108）のみ＝SELECT→なければINSERT、の app層TOCTOU脆弱パターン（本harnessが「不十分」と実証した其の型と同型）。claim機構は不呼出。
>      reachable＝backend/api/diagonal_appointments.py 経由、backend/main.py:93,403 でapp.include_router済（★活きたAPI経路★）。
>   ⒝ backend/api/email_parser.py L109（_create_appointment_from_parsed、メール取込予約作成）
>      ダブルブッキング検めが★皆無★（check_double_booking すら呼ばず）。claim機構も不呼出。
>      reachable＝backend/main.py:91,401 でapp.include_router済（★活きたAPI経路★）。
>   ⒞ backend/routers/next_appointment.py L71（book_next_appointment、POST /api/next-appointment/{patient_id}/book）
>      ダブルブッキング検め・claim機構いずれも不呼出。
>      reachable＝backend/main.py:120,430 でapp.include_router済（★活きたAPI経路★）。
>
> ★非違反として除外した箇所（残りのraw SQL）★＝backend/services/web_reservation/booking_service.py:291 と backend/services/appointment_service.py:335 は、claim_appointment_slots／_check_conflict を実際に内包する★委譲先そのもの（正規guarded path）の内部実装★であり、「委譲されずappointments へ迂回する経路」には該当せぬ（バグの定義に当たらぬ）。★residual raw SQL＝0★はこの2箇所については成立するが、⒜⒝⒞の3箇所については★residualかつ非occupancy根拠なし＝述語不成立★。
>
> ■ §5 直さぬ理由（禁㈢実装fix＝0の順守）
> 上記⒜⒝⒞は貴殿／本部長殿への★上げ物★として提出する。当職は detector 専任ゆえ実装へ踏み込まず。修正の要否・優先順位・委譲権者（足軽1号か別か）の裁定は上へ委ねる。
>
> ■ 最終票（述語で締める・数は材料）
> barrier機構そのもの＝★真（genuine）と確認、RED→GREENは同一unchanged harnessで独立再現に成功★（数=RED1件PASS・GREEN5件×5周PASS=25/25、材料として付記）。
> 而して★Gate⑸の受入述語「未委譲reachable case＝0」は不成立（現に3箇所・reachable・claim機構不呼出）★。
> ∴ ★barrier detectorとしての本務＝完（harness genuine・RED/GREEN再現）／述語検めの結果＝要対応3件を発見・上げ済（当職は直さず）★。
>
> ■ 禁則遵守
> push 0・merge 0・rebase 0・cherry-pick 0・main 0（stage1-runtime repo主worktreeHEAD=7d463ed不変・当職worktreeHEAD=e88e7582不変=commit 0）。実装fix 0（production code不触・test file含め一切書換なし＝git status --short 空）。新DDL 0。remote通信 0（fetch/ls-remote/push等一切不実行）。実患者・secret・DB実環境・本番data 0（全testはtmp_path上のsqlite使い捨てDB）。git gc/prune/reflog expire 不実行。slim_yaml.sh 不実行。migration/schema変更なし。nonce=HONBUCHO-RES-STAGE1-CYCLE2-GATES2-4-20260806-001は再利用のみ・新規発行なし。
>
> ■ 測時
> $ date -Iseconds
> 2026-08-07T00:02:30+09:00
>
> 軍師secondへ独立監査提出済（別便）。

---

## 収載付記（当職・ashigaru2、2026-08-07T00:33:46 以降の作業）

- 本 file は上記転記部分を **一字も変更していない**（typo・表記ゆれ・箇条書きの崩れも含め原文のまま）。current_order_14 ㈢「事後に綺麗に見せるな」に従う。
- その後 current_order_13（Gate5 second-layer scope）にて、本票が引いた「未委譲 reachable case」のうち exact-time 二経路（⒜相当のWeb-vs-Web・⒝相当のWeb-vs-Staff）は DB 層の部分 UNIQUE index (`uq_appointments_active_exact_start`) で別途閉じることが判明している（詳細は `docs/incident_logs/2026-08-07_gate5_second_layer_index_scope_a2.md`）。★本票自体は当時の app 層のみの実測として遡って書き換えず、そのまま残す★（後続で射程が絞られた事実は別票に記す）。
- commit は本票を含め **当職は行わない**（家老second が為す・current_order_14 の禁）。
