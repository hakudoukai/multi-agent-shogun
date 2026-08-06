# 旧code RED維持test（陽性対照）設計 — 固め (足軽3号)

下命=家老second msg_20260806_095125_581f005c（09:51:25・宛先=当職＋軍師second）。
★冒頭——設計のみ。書いておらぬ・走らせておらぬ★。`hakodoukai-dev`へは一文字も書かず、apply・worktree新設・
DB接触・実走・いずれも行っていない。参照は`git show`（読取のみ）に限る。

---

## §0 base取得法（⒟・確認済）

```
git -C /tmp/resimg-stage1-runtime-20260806 show 7d463edae84c704edabbd9da5465078dc62e55b1:<path>
```
で読取のみ取得できることを実測で確認した（当該worktreeは`stage1/reservation-cycle2-concurrency-idempotency`
branchを保持しており、baseへの到達は`git show`一発で足り、checkout等の書込操作を要さぬ）。

## §1 陽性対照の定義（⒜）

下命の定義をそのまま採る：**旧code（patch適用前・base `7d463ed`）に新testを当て、REDに成る事を以て
「試験が現に欠陥を捉える」証と為す形**。

---

## §2 ★最重要の発見★ — 受入⑦/item13の原文は F1/F2/F3 を指していない（⒞）

### §2-1 原文を特定した

`受入⑦（migration後、旧code+新testで陽性対照2件RED維持）`の出所を遡ると、a4/a5の両成果物とも
`13項matrix`の`⑬`と同根と記すのみで、**⑬自体の原文を引用していなかった**。当職が実測で遡った所、
原文は以下に在った：

> `/home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md`
> （256行・sha256=`0d8a20f6292932d1878f576266170cef11de89c598f27c79cd2706c54cb55b26`）
> **L225**（§6「migration適用前の必須RED/GREEN」項13）：
> 「13. migration適用後も、既知の欠陥service snapshotへ同じ陽性対照を当てればRED（active 2件／replay不安定）
> のままであること。修正済みtargetのGREENだけでなく、検出器が既知の欠陥を引き続き検出することを再検定する。」

### §2-2 「陽性対照2件」の正体

同file §2「陽性対照: 修正前FAIL」に、既に固有名で2件が定義・実行・証跡化されている：

| # | 名称 | test | 修正前実測 | 証跡 |
|---|---|---|---|---|
| 2.1 | 真の2接続・同一枠 | `test_true_two_connection_same_slot_only_one_active_row` | `CONCURRENT_ACTIVE_ROWS=2 SUCCESSES=2 ERRORS=0`（FAIL・期待はactive1件） | `resimg-cycle2-baseline-concurrency.txt` sha256=`141b59d9f7a15aefe793367e82cfcdc436fc3f51479ec3a49a7f3cef24dd30da` |
| 2.2 | 同一要求の別接続再送 | `test_exact_request_replay_returns_same_appointment_id` | 2回目が`BookingConflictError`・同一ID安定応答を返せずFAIL | `resimg-cycle2-baseline-replay.txt` sha256=`02f0b934bc27ee3fde219ba283919b07111e317fc3fcae807b718780edde2099` |

**∴「陽性対照2件」＝この2.1／2.2であり、F1/F2/F3ではない。** a5の成果物（`_reserveimage_cycle2_defect_handoff_a5.md`
L62）は「⑦(陽性対照2件RED維持)…**F3と同根**(idempotency_key未使用時の早期return経路が陽性対照で検出される
保証が無い)」と記すが、★この対応付けはitem13の原文には無い当職未確認の推測であった★——原文L225は
「既知の欠陥service snapshot」「active 2件／replay不安定」とのみ記し、F1/F2/F3という名称・症状は
一切登場しない。当職はこれを咎めとしては書かぬ（a4/a5はF1/F2/F3側の監査であり item13 原文へ遡る事は
本工区で初めて課された事ゆえ）が、**下命⒞への答としては「読み取れた」——判じ難しではなく、原文はF1/F2/F3の
話ではないと明確に読める**、と申告する。

### §2-3 「RED維持」の意（⒞・回答）

原文L225を字義通り読めば：**「migration適用後もREDのままである事」**（下命の選択肢の後者）。
より精確には——2.1/2.2は既に修正前FAIL（RED）・修正後PASS（GREEN）が実測済（§4）であり、item13が
要求しているのは★これとは別の第3の検定★＝「(将来の)migration適用後も、**既知の欠陥を持つservice
snapshotへ**同じ2.1/2.2のtestを当てれば、なお正しくRED**であり続ける**事」——検出器（test）自体が
将来の変更で無効化(false green化)していないかを再検定する趣旨であり、**「修正前に一度REDだった」だけでは
足りぬ**。この点で、当職の実測は**下命の二択いずれでもなく、両方の要素を含む第3の読み**を導いた
（migration前提の再検定である点は「migration後」、対象が「既知の欠陥snapshot」である点は「旧code的」）。
∴ ★未測ではなく、原文の読みを提示する★。

### §2-4 6path中0件という指摘との整合

a4/a5は「検証testが6path中0件」と記す。当職が`gate2-4-handoff-20260806.patch`を実測した所、
`test_true_two_connection_same_slot_only_one_active_row`と`test_exact_request_replay_returns_same_appointment_id`
は★該当patch内`backend/tests/web_reservation/test_phase2_2_booking.py`のdiffに現に存在する★
（patch行354・407、`/usr/bin/grep -n`で確認）。∴ ★2.1/2.2そのもの（現在codeに対するGREEN確認用）は
6pathに含まれている★。a4/a5が「0件」と見たのは、**item13が要求する「migration後の再検定（旧snapshotへ
再度当てる仕組み）」に該当する物が0件**という意味であれば正しい——2.1/2.2は「今のcodeがPASSする事」しか
検証しておらず、「将来の変更後も旧snapshotがREDのままである事を機械的に再検定する」仕組み（例：旧snapshotの
固定コピーを保持し、CIで定期的に同じtestを当てる等）は、当職が読んだ範囲のpatch・test file には
見当たらなかった。★∴ 0件の指摘自体は妥当と判じるが、根拠として引かれるべきはF3ではなくitem13の
「再検定の仕組みが無い」事である★。

---

## §3 F1/F2/F3 三値判定（⒝・己で検めた）

### §3-1 F1（staff経路idempotency未配線）

**判定＝㈠書ける（★a4の「GREEN-only」判定に当職は同意せぬ★・理由下記）**

- base確認：`git show 7d463ed:backend/services/appointment_service.py`（740行、存在確認済）の
  `create_appointment`実装（L195-229相当）は、単純`INSERT`→`commit`→履歴`INSERT`→`commit`のみで、
  `claim_appointment_slots`呼出・`BEGIN IMMEDIATE`・idempotency判定のいずれも★存在しない★。
- ★重要★：a4の§4-2は「slot claims PKが最終防波堤として効くため、同一slotへの再送は409で弾かれ
  重複行を作れない」ゆえF1をRED化できぬとするが、**この`claim_appointment_slots`（PK制約による衝突検出）
  自体が今回patchの新規追加**（`booking_concurrency_root.py`は`new file mode 100644`、baseには不在と
  当職が実測確認済）である。∴ a4の§4-2は**patch適用後（現行）codeの挙動**を記述しており、
  **旧code（base）の挙動ではない**。旧codeには一切の重複防止機構（idempotency・PK制約）が無い。
- 陽性対照設計（紙上・pytest疑似コード）：

```python
# 旧code (base 7d463ed) に対して当てる想定。当repoには未作成・未実行。
def test_staff_exact_retry_creates_duplicate_on_old_code(file_db_path):
    """陽性対照(F1): staffが同一payloadを2回送信した時、
    旧codeには防御機構が無いため active row が2件できるはず(RED=欠陥の実在)。"""
    payload = {"clinic_id": 1, "unit_id": 1, "start_time": "2035-06-01T09:00:00",
               "duration_minutes": 30, "source": "staff"}
    r1 = create_appointment(_open_file_db(file_db_path), payload, operator="staff-x")
    r2 = create_appointment(_open_file_db(file_db_path), payload, operator="staff-x")  # 単純retry
    active = _count_active_rows(file_db_path, clinic_id=1, unit_id=1, start="2035-06-01 09:00:00")
    assert active == 1   # 旧codeではこのassertがFAILする(=2件できる)と当職は予測=RED
```

- **「必ずREDか」の留保**：当職は`appointments`テーブルのDDL（`CREATE TABLE`文そのもの）を本工区の
  時間内には読んでいない——`(clinic_id, unit_id, start_time)`相当のUNIQUE制約が旧schemaに別途存在すれば
  このtestはGREENになり得る。∴ **㈠書ける、ただし確度は「テーブルDDLのUNIQUE制約有無」の未確認1点に
  懸かる（未測1件を自己申告）**。この1点を除けば、旧codeのpython実装だけを見る限りRED以外の結果は
  考えにくい。

### §3-2 F2（fk_check失敗時already-committed・自己rollback無し）

**判定＝㈡在り方が異なる・「旧codeへのRED test」という枠組み自体が不成立（a4の㈠在るとは別軸の答）**

- base確認：`git show 7d463ed:backend/db/migrations/booking_concurrency_root.py`→
  `fatal: path ... does not exist in '7d463ed'`（当職実測・パス自体は下命/a5文書と完全一致）。
  patch側も`diff --git a/backend/db/migrations/booking_concurrency_root.py ...`＋`new file mode 100644`
  ＋`index 0000000..d378a28`（当職実測、`/usr/bin/grep -n "^new file mode" <patch>`で確認）で
  ★新規fileである事が二重に裏付く★。
- ∴ `apply_booking_concurrency_root`関数そのものが旧codeに存在しない。**「旧codeにF2の新testを当てて
  REDにする」は成立し得ない**——importが失敗する（`ModuleNotFoundError`）のみであり、これは
  「F2の欠陥（fk_check失敗時の非rollback）を旧codeが再現してRED」ではなく、単に「対象関数が無いので
  実行不能」という★別種のRED（collection error）★に過ぎぬ。下命⒜の定義（旧codeに当てて欠陥固有の
  挙動でREDになる事）には適合しない。
- a4の§4-1設計（現行codeへ`fk_check`失敗を誘発しcommit済のままである事を確認するtest）は、
  **「現行patchのF2欠陥を直接検出するtest」としては妥当**（当職も`apply_booking_concurrency_root`の
  try/except/finally構造をbase確認と合わせて再読し、commitがtry節内・fk_checkがtry/except/finallyの
  外側にある事は否定していない＝a4のこの部分の実測に当職は異論を持たぬ）。ただし★これは「旧code陽性対照」
  ではなく「新patchの欠陥を直接示す回帰test」という別カテゴリである★事を明示すべきと判じる。

### §3-3 F3（existing簡易replay早期return）

**判定＝F2と同型・「旧codeへのRED test」という枠組み自体が不成立**

- base確認：`git show 7d463ed:backend/services/web_reservation/booking_service.py`（411行・存在確認済。
  ★当職は初回試行でpath誤り(`backend/services/booking_service.py`)により「存在せず」と誤読した——
  下記【本工区で己が直した誤り】参照★）。
- patchのdiff（`sed -n '60,311p' <patch>`で当職実測）を読むと、`create_booking`内の`existing = conn.execute(...)`
  による早期return（`if existing and not (root_enabled and idempotency_key): conn.commit(); return {...}`）は
  ★patchによる新規追加コード★であり、base側の`create_booking`（L188-215相当、当職実測）は
  `_check_conflict`を無条件に一度だけ呼ぶのみで、この種の早期returnは一切存在しない。
- ∴ F2と同じ理由で、「旧codeにF3のtestを当ててREDにする」は成立し得ない——旧codeにはそもそも
  「`_check_conflict`を経由しない早期return経路」自体が存在しないため、そのtestを旧codeに当てても
  early-returnには一切到達せず、常に`_check_conflict`を通る通常経路が走るのみである
  （これは「欠陥が無いのでGREEN」ではなく「該当コードパス自体が無い」という意味で、F2と同じ
  category mismatch）。
- a4の§4-3（F3はRED化不能・GREEN-onlyと申告）と当職の結論は**現象として一致**するが、
  ★理由付けが異なる★——a4は「`existing`早期returnが悪さをする具体的シナリオを構築できなかった」
  （現行codeを対象に構築を試みて失敗）としているのに対し、当職は「旧codeにはそもそも当該コード自体が
  存在せず、旧code向けの陽性対照という設問が成立しない」という、より手前の理由を挙げる。

### §3-4 三値・まとめ（当職の実測）

| # | a4の判定 | 当職の判定 | 一致／不一致 |
|---|---|---|---|
| F1 | ㈡書けぬ（GREEN-only） | **㈠書ける**（旧codeは無防備。UNIQUE制約有無1点が未測） | ★不一致★ |
| F2 | ㈠書ける（現行codeへの直接test） | 現行codeへの直接testとしては同意。**旧code陽性対照としては枠組み不成立** | 部分一致（対象の性質の記述が異なる） |
| F3 | ㈡書けぬ（GREEN-only） | ㈡書けぬ（理由は異なる＝旧codeに該当コードパスが無い） | 現象一致・理由不一致 |

---

## §4 【本工区で己が直した誤り】

1. F3の対象file確認で、当初`backend/services/booking_service.py`（`web_reservation/`を欠く誤ったpath）を
   `git show`し「存在せず」という誤った中間結果を得た。patchのdiff冒頭（`diff --git a/backend/services/
   web_reservation/booking_service.py ...`）を読み直して正しいpathに気付き、再実測して411行の存在を確認した。
   ★誤った結果を最終報告に用いず、実測を継続した事をここに明記する★。
2. §3-1（F1）にて、a4の§4-2の結論をそのまま受けず、根拠（`claim_appointment_slots`の存在前提）が
   旧codeでは成立しない事を`git show`で確認する事によって発見した。これは下命⒝「己で検めよ。合わねば
   その旨」への直接の応答である。

## §5 対に成る他工区

- `docs/incident_logs/2026-08-06_reserveimage_cycle2_gap_test_design_9_10_12_a4.md`（足軽4号・219行・
  sha256=`9163e4971712f9e37d659750f334ceff99a15e222203999461c66a2f1328e76c`）——F1/F2/F3の三値判定の
  素材そのもの。§3で当職が異論を述べた対象。再掲せず参照のみ。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_defect_handoff_a5.md`（足軽5号・131行・
  sha256=`42229b78dc096b675a227fabd18d87903659a1d4bcdc2f3f436541a54d575256`）——⑦とF3の対応付けの出所。
  §2で当職が原文未確認の推測と指摘した対象。再掲せず参照のみ。
- `/home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-concurrency-idempotency-
  evidence-and-root-design-20260806.md`——item13原文の所在（本工区で当職が新規に遡って発見した一次資料）。

## 監査体制

暫定二者制（軍師second + Gemini）。Codex leg は禁令（2026-07-21事案・SAFETY裁定 seq132707）により停止中。

## 禁則遵守の申告

設計のみ。test fileの新規作成・書込みは一切なし（本file自体は設計文書であり、pytest実装ではない）。
`hakodoukai-dev`への書込み・apply・worktree新設・DB接触・実走（pytest実行）いずれも未実施。
`/usr/bin/grep -r`（および単発`git show`/`sed -n`）を用い、rcはpipeへ通さず単発コマンドの結果を
直接目視で判定した。commitは行っていない（karo-second殿がPASS後に行う旨、下命に明記済）。

---

断面: 2026-08-06T09:59:45+0900（機械・提出直前再測）／base_commit（測定時HEAD）=`292bcf264ec45ee57b8178d7eb0ab0afb0c95d22`
提出先: 家老second + 軍師second
