# 令286 fa06a3a1 ―― 第三の道（名の定義を戻す道）の探索 v1

## §的 ★的一行★
的の側から叩いても ―― 函 250 本の名・`documentation` の悉皆 10 行・test が期待する table の悉皆 0 行 ―― ★探す名に合ふ函は `backend/api/treatment_validation.py` に 現に無い★。近い綴りの 20 本は悉く ★別の table・別の鍵★ を扱ふ物であり、rename の跡ではない ∴ ★第三の道は 此の file の中には 無★（拵へて居らぬ）。

## §A 頭
- as_of 2026-09-11T08:14:47+0900。的の樹 `/mnt/c/DentalBI`（HEAD `53412b7bcda2f8aec4c5f5cdd157e819e8e91c02`）。當 repo の HEAD `1ad4edf` 不動。
- 己の compact 境界 ―― 本窓は一度 compact を経て居り、令283 以前の測りは ★要約から引いた物★ である。本紙の数は悉く ★本令で己が当たり直した★。
- ★打数 = 通算 19／上限 20（git 讀取 10／上限 15・grep 7・awk 2）★。★境界に当たつたゆゑ 之より先は測らず止めた★。走 0・当て 0・押し 0・install 0・DB 0・find 0・/mnt/c 書込 0・rm 0。

## §B ㋐ 的の file に現に在る函（名のみ・数を添へる）
- 数 ―― 頂の `def` ★227 本★／深さを問はぬ `def` ★250 本★（差 23 は 函の中の函・class の中の物）。★何を一つと数へたかは「`def` の行 1 本を 1 函」である（床(30)）★。
- 綴りの近い物（`resolve`／`documentation`／`comment`／`field_id` の何れかを名に含む）★20 本★ ―― `is_standalone_image_guidance_comment`・`_resolve_shinryo_points_for_date`・`_resolve_preview_point`・`_resolve_touyaku_shinryo_point`・`_resolve_touyaku_safety_evidence`・`_resolve_cr_dynamic_points_backend`・`_resolve_periodontal_exam_validation_plan`・`_resolve_srp_validation_item`・`_resolve_receipt_drug_components`・`_resolve_receipt_drug_component_sum_validation_item`・`_resolve_master_component_sum_validation_item`・`_resolve_dental_full_mouth_components`・`_resolve_core_build_up_validation_item`・`_resolve_root_canal_validation_item`・`_resolve_dental_xray_pair_validation_item`・`_resolve_dental_full_mouth_validation_item`・`_resolve_item_quantity`・`_resolve_point_multiplier`・`_select_comment_template_key`・`resolve_visit_point`。
- `documentation` の語は file 全体で ★10 行★ のみ ―― 内訳は `required_documentation_fields`（別 table・5 行）・`spt_start_documentation_*`（別の鍵・2 行）・`normalize_r4_p_exam_documentation`（別の旗・3 行）。★探す名の綴りは 一つも無い★。

## §C ㋑ test が其の名に何を期待して居るか
- 引数 ―― ★2 形★ で呼ばれる。第一は client、第二は set の符、第三は field の名（`None` 可・既定が在る形）。逐語:
> resolved_id_1 = _resolve_comment_documentation_field_id(fake_client, "TS_P_KENSA")
- 戻り ―― ★id を一つ★。`str()` を掛けた物が `treatment_set_documentation` の `is_active` な行の `id` と等しくなる事を試験が當てて居る。且つ 2 形の戻りが互ひに等しい事も當てて居る。
- ∴ 求められて居る函は ★`treatment_set_documentation` を引いて active な行の id を一つに解く物★ である。

## §D ㋐ と ㋑ が合ふ函の在無
- ★無★。近い綴りの 20 本は 点数・薬・歯式・処置の項を扱ふ物であり、★`treatment_set_documentation` を引く物は一つも無い★。
- 加へて ―― `treatment_set_documentation` の語は 的の file 全体で ★0 行★（悉皆で当たつた）∴ 期待する table に触れる code 其の物が此の file に無い。

## §E 第三の道は在るか
- ★此の file の中には 無★。定義を戻す台（同じ働きの函）も、抽出して名を付け直す台（同じ table を引く行）も、★何れも 0 件★ である。拵へて居らぬ。
- 別の module に其の働きが在るか否かは ★本令の的の外＝測つて居らぬ★（令は的を `treatment_validation.py` と test の二本に絞つた）。之を次に測るなら 樹の悉皆で `treatment_set_documentation` を引く形に成る。
- ∴ 三度叩いた末の判じ ―― ①移植（283）②③-㋐ の patch（284・285）③定義を戻す（286）の何れも、★今 台が在るのは ② のみ★ であり、其の ② も 285 で ★止まる所が移るのみ★ と出て居る。

## §F 三別
- ★実測★ = 函の数 227／250・近い綴り 20 本の名・`documentation` 10 行・`treatment_set_documentation` 0 行・test の呼び 2 形と當ての 2 本。悉く己で当たつた。
- ★見込み★ = 20 本が「rename の跡ではない」との判じ（名と扱ふ物からの推し量りであり、中身を一本ずつ讀んで確かめては居らぬ）。
- ★確かめて居らぬ★ = 別 module の在無・板 fa06a3a1 の逐語・總監督裁 280975 の中身（家老の便からの写し）。
- harness の /tmp 置き物 ―― 285 の走で置かれた `bnx8ctzg3.output`（149 B・sha16 `e500440ac69b980f`）が在る。★消して居らぬ★。本令では新たに置かれて居らぬ。
