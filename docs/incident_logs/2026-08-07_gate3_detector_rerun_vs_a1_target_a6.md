# Gate3 detector 再走 — a1 target 14cad3a 対（足軽6号）

下命=karo-second msg_20260807_002256_044691ff（key=current_order_9_20260807_001900_GATE3_DETECTOR_RERUN、本部長殿00:02:30令）。
役=★足軽4号 detector(独立設計・実装済)の再走のみ★。detector自体の新設・改変・実装fixは一切行わず。

測時=2026-08-07T00:36:08+09:00。主repo HEAD=5da21919d74b780df14683d276a81faa6305e476（着手前後不動）。

## 禁則順守

- ㈣修正0＝a1 target(`/tmp/resimg-cycle2-f123-clean-20260806`)・a4 detector元(`/tmp/resimg-verify4-cycle2-20260806`)ともに★一字も書込せず★（下記「境」節で実測裏付け）。
- commit0・push0・merge0（当職の作業は全て`/tmp/resimg-gate3-rerun-a6-20260806`という★新規scratch dir★内のみ）。
- 既存resimg freeze 32件＝不触（新規scratch dirは freeze対象32件の内でも外でもない、当職が本工区の為に新設した物であり既存資産に含まれず）。

## サンドボックス構築（試行錯誤を隠さず記す）

### 初回試行の欠陥（自己発見・訂正）

初回はa1 targetの`backend/`直下エントリをsymlinkするだけの浅いsandboxを作ったが、実行結果が「scanned 3 files」（本来458件前後の筈）と異常値を示した。
`python3 -c "from pathlib import Path; print(sum(1 for _ in Path('backend').rglob('*.py')))"`で単体検証した所、★`Path.rglob`はsymlinkされた**サブディレクトリ**の中へは再帰せぬ★事を実測で確認（symlink先ディレクトリの直下は数えるが、その中は辿らぬ）。
∴ ★「scanned 3」は誤測定であり、a1の実コードを実質何も走査していなかった★。この値は使わず、破棄した。

### 訂正後の構築

`cp -r`でa1 targetの`backend/`をscratch dir(`/tmp/resimg-gate3-rerun-a6-20260806/backend`)へ★複製★（a1 target自体は読取のみ、書込0）。
複製後、`tests/`ディレクトリのみ空にして、足軽4号原本のdetector script（`/tmp/resimg-verify4-cycle2-20260806/backend/tests/detect_undelegated_occupancy_mutation_a4.py`、sha256=e13185b7e7e4a091a4399805dd562ce897dafeb031d03412b5debaa4dbf1bcff・264行）を★一字も変えず★複製し設置。
複製先のsha256を再測し、原本と★一致★を確認（下記「己の手」節）。
`diff -rq`でscratch dir内の`services/`・`api/`両ディレクトリがa1 targetの同ディレクトリと★完全一致★である事を確認。
複製後の`.py`到達数=463（`tests/`除外前・除外後の差は detector自身のEXCLUDE_DIR_NAMESが担う）。

## 実行結果（scratch dir、a1 target 14cad3aの実コード）

```
$ cd /tmp/resimg-gate3-rerun-a6-20260806 && python3 backend/tests/detect_undelegated_occupancy_mutation_a4.py
[gate3-detector] scanned 458 files under backend, excluding delegated modules ['backend/db/migrations/booking_concurrency_root.py', 'backend/services/appointment_lifecycle.py']
[gate3-detector] UNDELEGATED occupancy-relevant mutation sites (function calls NO delegation callable): 1
  - backend/api/email_parser.py:108 [_create_appointment_from_parsed] INSERT appointments touches ['clinic_id', 'duration_minutes', 'end_time', 'start_time']
[gate3-detector] RESIDUAL raw SQL (function ALSO calls a delegation callable -- co-existing old+new path): 7
  - backend/api/appointment_detail.py:116 [api_update_detail] UPDATE appointments touches ['duration_minutes', 'start_time', 'unit_id']
  - backend/api/appointment_grid.py:768 [move_appointment] UPDATE appointments touches ['end_time', 'start_time', 'unit_id']
  - backend/api/booking_manage.py:278 [change_booking] UPDATE appointments touches ['end_time', 'start_time']
  - backend/routers/next_appointment.py:69 [book_next_appointment] INSERT appointments touches ['clinic_id', 'duration_minutes', 'end_time', 'start_time', 'unit_id']
  - backend/services/diagonal_service.py:276 [update_linked_appointment] UPDATE appointments touches ['end_time', 'start_time']
  - backend/services/diagonal_service.py:300 [update_linked_appointment] UPDATE appointments touches ['end_time', 'start_time']
  - backend/services/web_reservation/booking_service.py:408 [update_booking] UPDATE appointments touches ['clinic_id']
[gate3-detector] RESULT: RED (未委譲の到達可能 mutation site != 0)
EXIT=1
```

## 母集団の突合（baseline=足軽4号本票 base e88e7582 と 今回=base 14cad3a）

| 部位 | baseline(e88e7582) | 今回(14cad3a) | 遷移 |
|---|---|---|---|
| appointment_detail.py:106→116 [api_update_detail] | undelegated | residual | 委譲呼出が追加された(move_appointment_slot)、但し生UPDATE併存 |
| appointment_grid.py:761→768 [move_appointment] | residual | residual | 不変 |
| booking_manage.py:278 [change_booking] | undelegated | residual | 委譲呼出が追加された(move_appointment_slot)、生UPDATE併存 |
| email_parser.py:108 [_create_appointment_from_parsed] | undelegated | **undelegated(不変)** | ★手を付けられておらぬ★ |
| next_appointment.py:69 [book_next_appointment] | undelegated | residual | 委譲呼出が追加された(claim_appointment_slots)、生INSERT併存 |
| diagonal_service.py:116/145 [create_diagonal_appointment] | undelegated×2 | **検出0(消失)** | ★根治★——下記「実読での裏取り」参照 |
| diagonal_service.py:260/275→276/300 [update_linked_appointment] | undelegated×2 | residual×2 | 委譲呼出が追加された(move_appointment_slot)、生UPDATE併存 |
| web_reservation/booking_service.py:408 [update_booking] | residual | residual | 不変 |

## 実読での裏取り（detectorの出力を鵜呑みにせず、実coreを読んで検算）

- ★`diagonal_service.py:create_diagonal_appointment`が検出から消えた理由★を実読で確認——現在は`appointment_lifecycle.create_appointment_with_claim(..., insert_sql="""INSERT INTO appointments ...""")`という形で、INSERT文字列を委譲先primitiveへ★引数として渡す★形に変わっており（127行・163行）、生の`conn.execute(INSERT...)`が関数自身のbodyから消えている。∴ detectorが「関数自身の直接execute呼出」を対象とするAST走査の性質上、これは★検出漏れではなく真の根治★（実コード確認済、下記grep）。
- ★booking_manage.py:change_booking★・★next_appointment.py:book_next_appointment★の残り2件も実読——いずれも生SQL(`conn.execute`)行と委譲呼出(`move_appointment_slot`/`claim_appointment_slots`)行が★同一関数内に併存★している事を確認、detectorの"residual"分類と一致。
- ★email_parser.py:108★のINSERT列一覧を実読——`(clinic_id, patient_id, start_time, end_time, duration_minutes, category, treatment_content, status, source, memo, created_at, updated_at, version)`と、★`unit_id`が依然として列挙に含まれておらぬ★事を確認。足軽4号本票が指摘した「動的到達可能性は静的検出の射程外」の状態は、baseline時点から★一切変わっておらぬ★。

## ㈡ semantic predicate — 未委譲 = 0 か

**述語＝偽（未委譲 = 1 ≠ 0）**。
唯一の残存site（`email_parser.py:108`）は、baseline(足軽4号本票)が既に指摘していた★同一site★であり、今回の測定でも一字も変わっていない。
∴ 「未委譲=0」の受入条件は★未だ満たされておらぬ★。但しこのsiteは baseline時点で既に「unit_id欠落によりIntegrityErrorで動的に到達不能である蓋然性が高い」と指摘され、その動的裏取り自体は本detector(静的AST走査)の射程外である事も baseline・今回共通で明記されている——★真に0か1かは、本測定だけでは確定し得ぬ★（下記㈤参照）。

## ㈢ semantic predicate — residual = 0 か 非occupancy の根拠 か

**述語＝偽（residual = 7 ≠ 0、かつ7件悉く occupancy 関連であり非occupancyの根拠は成立せぬ）**。
7件は全て`OCCUPANCY_FIELDS`(clinic_id/unit_id/start_time/end_time/duration_minutes)のいずれかを実際に触れている事がdetector自身の出力(`touches [...]`)で個別に示されており、「occupancyに無関係だから残って良い」という逃げ道は★7件とも成立せぬ★。
残存の性質＝★raw SQLの削除ではなく、委譲呼出の追加による並存★（baseline比較の表参照）。これは足軽4号本票が既に「co-existing old+new path」と命名した形そのものであり、a1の対応方針は「置換」ではなく「横に足す」形だった事が、今回の再走で機械的に裏付けられた。

## ㈤ 本測りが覆っていない層（同じ行に・足軽2号の二層の件に鑑み）

- ★DB層の強制（UNIQUE index/制約）は本detectorの射程外★——本detectorはPython AST静的解析のみでapp層のソースコードしか見ておらず、DB schema制約の有無・射程は足軽2号のcurrent_order_13(UNIQUE indexの射程確定)の管轄であり、本票は一切測っておらぬ。
- ★動的到達可能性（実行して確かめる事）は射程外★——email_parser.py:108が実際にIntegrityErrorで止まるか否かは、本detector(静的走査のみ)では判じ得ず、baseline同様★未検証のまま★である。
- ★residual 7件における実行順序・trサンザクション意味論は射程外★——本detectorは「同一関数内に委譲呼出が存在するか」のみを見ており、生SQLと委譲呼出の★実行順序★（生SQLが先に効いてしまい委譲呼出の保証を実質無効化していないか）は判定していない。「併存している」事実のみが検出対象であり、「併存が安全か」は別問題。
- ★documents.py等 別ドメインの扱いは対象外★——本detector(gate3)はdocuments.pyを走査対象に含めておらぬ(DELEGATED_MODULES/EXCLUDE_DIR_NAMESに未収載だが、本来gate4b相当の別detector話であり、gate3自体は元々appointments tableのみを対象とする設計、baseline文書にも明記なし=当職が今回追加で確認した限定である事を明記)。

## 境の遵守（実測で裏付け）

- a1 target(`/tmp/resimg-cycle2-f123-clean-20260806`)＝`git status --short`で出力なし(dirty=0)・`git rev-parse HEAD`=14cad3a42c20c34ac1f93e4f334da5c85f195dd5(令の値と一致、当職の操作で不動)。
- a4 detector元(`/tmp/resimg-verify4-cycle2-20260806`)＝HEAD=63ce0a78a48abe380b13be5cd848e7119d0a7317(不動)。`?? docs/incident_logs/`の未追跡表示は当職の操作に非ず(当職はこのworktreeから★読取のみ★・書込は一度も行っておらぬ)。
- 主repo HEAD＝着手前後で5da21919d74b780df14683d276a81faa6305e476のまま不動。
- push0・merge0・commit0(scratch dir自体もgit管理下に置いていない)。
- 実装fix0(detector script・a1コードとも一字も改変せず)。
- 既存resimg freeze 32件＝不触(scratch dir `/tmp/resimg-gate3-rerun-a6-20260806`は当職が本工区の為に新設した物で、既存32件のいずれでもない)。

## 己の手で為した事

- `git cat-file -t 14cad3a...`で当該commitが主repoのobject storeに無い事を確認(別worktreeの独立repoである事の裏付け)。
- `git worktree list`・`ls`・`git -C <path> rev-parse HEAD`/`status --short`/`log --oneline -3`でa1 target・a4 detector元双方の現況を実測。
- 初回sandbox(symlink方式)を構築・実行し、`scanned 3 files`という異常値を検知、`python3 -c "..."`で単体切り分けし`Path.rglob`がsymlinkディレクトリを辿らぬ事を実測で特定、破棄。
- `cp -r`で訂正後sandboxを構築、`sha256sum`でdetector複製の一致を確認、`diff -rq`でservices/api両ディレクトリの複製忠実性を確認。
- detectorを実行、標準出力を本票へ逐語転記。
- baseline票(`docs/incident_logs/2026-08-06_cycle2_independent_detector_gates345b_a4.md`)を全文実読し、8件の未委譲+2件のresidualそれぞれの`file:line`を突合。
- `diagonal_service.py`・`booking_manage.py`・`next_appointment.py`・`email_parser.py`をgrep・実読し、detector出力の分類(残存/residual化/消失)を実コードで個別に裏取り。
- 上記いずれも書込・commit・send を伴わず(inbox_write.shのみ別途、本票path自体はEditツールで新規作成)。

## 数の扱い

測時=2026-08-07T00:36:08+09:00／器=`python3`(AST・detector本体)+`git`+`diff`+`sha256sum`+`grep`。
範囲=`backend/**/*.py`(458ファイル、detector自身の走査範囲・EXCLUDE_DIR_NAMES={__pycache__,_archive,tests,node_modules,.git}適用後)。
未委譲=1件(baseline比 -7)・residual=7件(baseline比 +5)・完全消失(根治確認)=2件・不変(residual→residual)=2件・不変(undelegated→undelegated)=1件。
以上（読めぬfileは無かった）。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。
