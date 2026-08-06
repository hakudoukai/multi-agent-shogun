# 足軽4号 → 家老second/軍師second: 走行順9/10/12 (item⑦⑩⑬) 陽性対照 紙上設計（read-only）

断面: 2026-08-06T09:2x JST（当職 実測）。本便は read-only。apply/worktree新設/DB/実走 一切なし。
下命出所: `queue/inbox/ashigaru4.yaml` msg_20260806_091331_b85c202c（家老second→足軽4号）。
参照先固定: base=`7d463edae84c704edabbd9da5465078dc62e55b1`（実測=`git -C /tmp/resimg-cycle2-impl-20260806 rev-parse HEAD`・前回監査と不変）。
コード実読は既存worktree `/tmp/resimg-cycle2-impl-20260806`（前工区で他者が用意した物・当職が新設せず）への**読取のみ**。1文字も書き換えておらぬ。

## §0 母集団宣言・前提の再確認

- **13項matrix**＝出所 `reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md` §6。番号①〜⑬。
- **走行順**＝当職の前回成果物（`2026-08-06_reserveimage_cycle2_acceptance_matrix_a4.md` §4）が独自に付けた実行順序の通し番号1〜12（②③のSHA/隔離DB要件は走行順に乗らぬため除く）。
- **★番号の衝突に注意★**（W194型の再発防止）＝ 家老second 下命本文の「⑦」は**受入①〜⑨の⑦**（＝13項matrixの⑬と同根、当職が既に指摘済）であり、**13項matrixの⑦（T/space cross-channel）とは別物**。当職の前回報告 §4 の走行順9/10/12 は 13項matrix の ⑦/⑩/⑬ を指す。以下この対応で進める（誤読の芽を本節で断つ）。
- **危うき3件（F1/F2/F3）**: F1=staff経路idempotency未配線／F2=`apply_booking_concurrency_root`のfk_check失敗時already-committed・自己rollback無し／F3=idempotency_key未使用時のexisting簡易replay早期return。

## §1 9/10/12 と F1/F2/F3 の対応（強制せず・書けぬは書けぬと書く）

| 走行順 | item | 主対応 | 対応の性質 |
|---|---|---|---|
| 9 | ⑦T/space cross-channel | **F1（補完）** | F1そのものの検出ではなく、「F1が在ってもslot claim側が食い止めるか」の**代償機構**検証 |
| 10 | ⑩reschedule atomic rollback | **F2型の再発検査** | F2と同型（多段操作+rollback）のパターンが`update_booking`に**も**在るかの検査。結論=無い（§3で自己是正） |
| 12 | ⑬陽性対照RED維持 | **F2（直撃）+ F1/F3（各々試み・両者GREEN-only）** | F2のみ現時点でREDを構成可。F1/F3はRED化できず、理由を明記 |

## §2 走行順9 (item⑦ T/space cross-channel) 設計

### §2-1 実測（設計の土台）

`backend/db/migrations/booking_concurrency_root.py`:
- `slot_starts(start_time, end_time, ...)` は内部で `_parse()`→`_canonical()`（`value.replace("T"," ")`）を経てから `cursor.strftime("%Y-%m-%d %H:%M:%S")`（space形式固定）で`slot`文字列を作る。
- `claim_appointment_slots()` はこの正規化済`slot`を`appointment_slot_claims(clinic_id,unit_id,slot_start,appointment_id)`へINSERTする。PK=`(clinic_id,unit_id,slot_start)`。

`backend/services/appointment_service.py`（staff側）:
- `start_time = data["start_time"]`／`end_time = et.isoformat()` を**そのまま**`appointments`へINSERT（T区切りのまま生保存、実測=L207-213付近のinsert_vals）。
- **★staff側に`BEGIN IMMEDIATE`が無い★**（`grep -n "BEGIN" backend/services/appointment_service.py` → 0件、当職実測）。web側`booking_service.create_booking`は関数冒頭で`BEGIN IMMEDIATE`を取るが、staff側は無い。
- staff側の事前重複検査は`create_appointment`→`validate_booking`（`booking_validator.py`）→`_check_double_booking`（同file L355）で行われ、この読み取りは**writer lockより前**に走る。

**∴ 新規観察（前回監査に無し・誤りではなく特性）**: staff経路は「idempotency無し(F1)」に加え「BEGIN IMMEDIATEも無し」という**二重に弱い**入口を持つ。二重防御(idempotency dedup + writer lock先取り)が web にはあるが staff には無く、**`appointment_slot_claims`のPK衝突のみ**が staff の最終防波堤である。走行順9はこの「最終防波堤が cross-channel かつ format差(T/space)を跨いでも機能するか」を検証する点で、**F1の帰結（代償機構の有効性）に対する陽性対照**として位置づけられる。

### §2-2 設計（紙上・pytest疑似コード）

```python
# 配置先案: backend/tests/test_reserveimage_cycle2_gap_positive_controls.py（新設・未作成）
def test_staff_web_cross_channel_same_slot_pk_collision(shared_file_db_path):
    """陽性対照: staffがT区切り・WebがSpace区切りで同一物理slotへ同時create。
    F1(staff idempotency無し)+staff BEGIN IMMEDIATE無しでも、
    slot_starts()のT→space正規化によりPK衝突で片方のみ成功するはず。"""
    barrier = threading.Barrier(2)
    results, errors = [], []

    def staff_worker():
        conn = _open_file_db(shared_file_db_path)
        try:
            barrier.wait(timeout=0.4)
            r = create_appointment(conn, {
                "clinic_id": 1, "unit_id": 1,
                "start_time": "2035-06-01T09:00:00",  # T区切り
                "duration_minutes": 30, "source": "staff",
            }, operator="staff-x")
            results.append(("staff", r))
        except Exception as exc:
            errors.append(("staff", exc))
        finally:
            conn.close()

    def web_worker():
        conn = _open_file_db(shared_file_db_path)
        try:
            barrier.wait(timeout=0.4)
            r = booking_service.create_booking(
                conn, 1, "000001", "menu_01_001", "2035-06-01 09:00",  # space区切り
            )
            results.append(("web", r))
        except Exception as exc:
            errors.append(("web", exc))
        finally:
            conn.close()

    t1, t2 = threading.Thread(target=staff_worker), threading.Thread(target=web_worker)
    t1.start(); t2.start(); t1.join(timeout=5); t2.join(timeout=5)

    verify = _open_file_db(shared_file_db_path)
    active = verify.execute(
        "SELECT COUNT(*) FROM appointments WHERE clinic_id=1 AND unit_id=1 "
        "AND replace(start_time,'T',' ')='2035-06-01 09:00:00' "
        "AND status NOT IN ('cancelled','no_show')"
    ).fetchone()[0]
    claims = verify.execute(
        "SELECT COUNT(*) FROM appointment_slot_claims WHERE clinic_id=1 AND unit_id=1 "
        "AND slot_start='2035-06-01 09:00:00'"
    ).fetchone()[0]

    assert len(results) == 1          # 片方のみ成功
    assert len(errors) == 1           # 片方のみ409/IntegrityError系
    assert active == 1                # 物理予約は1件のみ（T/space混在でも二重にならぬ）
    assert claims == 1                # claimsも1件（PKが両表記を同一視できている証）
```

**未確定（紙上ゆえ検めておらぬ）**: staff側fixtureは`sqlite_init.TABLES`+`seed_appointment_data`（`test_appointment_service.py`流儀）、web側fixtureは独自CREATE TABLE（`test_phase2_2_booking.py`流儀）であり、**両者を同一DBへ両立させるスキーマ統合が未検証**。加えて`claim_appointment_slots`は`root_tables_present(conn)`がFalseなら**何もせず`return`する**ため、本testの前提として`apply_booking_concurrency_root(conn)`（またはroot tables相当の手動CREATE）が事前に要る。

**「この testは 欠陥(F1)が在れば必ずREDか」**: **書けぬ**。理由=このtestが検証するのは「F1が在ってもslot claim側の代償機構が効くか」であり、代償機構が効けば**GREENのまま**でF1は依然として存在し続ける（=このtestはF1自体を検出する設計になっておらぬ）。F1そのものを直接RED化する陽性対照は、staff側が受け取れないidempotency_key相当の**再送検知**を要求する形になるが、staff側の実際の再送経路（呼出し元=`appointments.py`等）は**patch対象外・当職未読**につき設計できぬ（前回監査§0で既に明記した未測と同一根）。

## §3 走行順10 (item⑩ reschedule atomic rollback) 設計 —— ★前回finding の自己是正を含む★

### §3-1 実測（`update_booking`全体を今回あらためて行末まで実読）

```
389 def update_booking(...):
...
(new_start_time and root_tables_present(conn) の分岐内)
    release_appointment_slots(conn, appointment_id)
    try:
        claim_appointment_slots(conn, appointment_id, clinic_id, row["unit_id"], ...)
    except sqlite3.IntegrityError as exc:
        conn.rollback()          # ★ここ★
        raise BookingConflictError(...) from exc
...
    conn.execute(f"UPDATE appointments SET ...")
    ...
    conn.commit()                # 452行付近（相対78行目）
```

`grep -n "commit\|BEGIN\|rollback" `で関数全体(389-472行)を実測した結果、**`BEGIN IMMEDIATE`は無く、commit/rollbackはこの2箇所のみ**。Pythonの`sqlite3`標準動作（`isolation_level=""`既定）では、`release_appointment_slots`（DELETE）が本関数内で最初の書込となり、そこで暗黙にtransactionが開始される。`claim_appointment_slots`（INSERT）が同一transaction内で失敗した場合、`conn.rollback()`は**releaseのDELETEも含めて丸ごと取り消す**。

### §3-2 ★自己是正★（前回報告 `2026-08-06_reserveimage_cycle2_patch_readonly_audit_a4.md` §4 item10 行の訂正）

前回、当職は同item10の設計欄に「**release→claim失敗時に旧claimは既に消えている**」を★新規finding★と記した。**今回あらためて`conn.rollback()`の存在とその作用範囲（暗黙transaction全体）を突き合わせた結果、この主張は誤りであった公算が高い**——`rollback()`が`release_appointment_slots`のDELETEも同時に取り消すため、例外時に旧claimは復元される設計に読める。
**原因（当職の落度）**: 前回は「releaseが先・claimが後」という**順序**のみに着目し、両者が**同一の未commit transaction内にある**か（＝rollbackで両方消えるか）を突き合わせておらなんだ。「求めた証拠を己が先に渡す」の逆で、**己の前回結論を今回検め直さず運べば同じ落度**になるところであった。
**確度**: sourceの実測に基づく高い確度だが、**紙上設計であり実走で確認しておらぬ**。特に「暗黙transactionの境界」はsqlite3ドライバのisolation_level設定（本モジュール冒頭・接続生成箇所は未確認）に依存し得るため、下記§3-3の陽性対照は**この是正自体を検証する目的も兼ねる**。

### §3-3 設計（F2型パターンの再発検査として）

```python
def test_reschedule_claim_failure_restores_old_claim_atomically(file_db_path):
    """陽性対照: 新slotのclaimが失敗した場合、release済みの旧slot claimが
    rollbackで復元されるか（F2と同型=多段操作+部分commitの再発チェック）。
    是正(§3-2)通りなら GREEN。前回finding通りなら RED（旧claim消失）。"""
    conn = _open_file_db(file_db_path)
    apply_booking_concurrency_root(conn)
    r1 = booking_service.create_booking(conn, 1, "000001", "menu_01_001", "2035-07-01 09:00")
    r2 = booking_service.create_booking(conn, 1, "000002", "menu_01_001", "2035-07-01 10:00")

    old_claims_before = conn.execute(
        "SELECT slot_start FROM appointment_slot_claims WHERE appointment_id=?",
        (r1["appointment_id"],),
    ).fetchall()

    with pytest.raises(BookingConflictError):
        # r1を r2 の枠(10:00)へ動かそうとして衝突させる
        booking_service.update_booking(
            conn, 1, "000001", r1["appointment_id"], new_start_time="2035-07-01 10:00"
        )

    old_claims_after = conn.execute(
        "SELECT slot_start FROM appointment_slot_claims WHERE appointment_id=?",
        (r1["appointment_id"],),
    ).fetchall()
    appt_row = conn.execute(
        "SELECT start_time FROM appointments WHERE appointment_id=?", (r1["appointment_id"],)
    ).fetchone()

    assert old_claims_after == old_claims_before   # 旧claim保持（是正の主張）
    assert appt_row["start_time"] == "2035-07-01 09:00:00"  # appointments行も未変更
```

**「この testは 欠陥(F2型再発)が在れば必ずREDか」**: **概ね書ける**——もし`release_appointment_slots`と`claim_appointment_slots`の間に将来の改修で`conn.commit()`が誤って挿入されれば（＝F2と同じ「途中commit」パターンの再発）、`rollback()`は既commit分を取り消せず`old_claims_after`が空になり本testは確実にREDへ落ちる。ただし**「暗黙transactionがsqlite3接続設定に依存する」点は紙上で断定できぬ**ため、「必ず」は接続生成コード（本testが使う`_open_file_db`のisolation_level）を含めて実走確認して初めて言い切れる、と留保を明記する。

## §4 走行順12 (item⑬ 既知欠陥への陽性対照RED維持) 設計 —— ★本工区の眼目★

受入⑦（＝13項matrix⑬・同根）を埋める。F1/F2/F3それぞれに陽性対照を試み、**結果は不揃い**（咎めではなく零は零と書く）。

### §4-1 F2 向け陽性対照（★唯一、現時点でRED を構成できる★）

```python
def test_fk_check_failure_leaves_schema_committed_not_rolled_back(tmp_path):
    """陽性対照: fk_check失敗を誘発し、apply_booking_concurrency_rootが
    スキーマ変更をcommit済のまま例外送出する(F2)ことを確認する。
    ★現行コードでは意図的にRED（欠陥の実在を示す）★。"""
    conn = _make_conn_with_dangling_fk(tmp_path)  # appointment_historyに存在せぬappointment_idを仕込む等、
                                                    # fk_check失敗を人工的に誘発する仕込みが要る(詳細未設計=次点)
    with pytest.raises(RuntimeError, match="foreign_key_check failed"):
        apply_booking_concurrency_root(conn)

    # ★本行が眼目★: commit済みか(=F2の主張どおりか)を検める
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "_appointments_pre_root" not in tables      # rename後table消失=commit済の証
    assert "appointment_slot_claims" in tables          # 新tableも作成済のまま=commit済の証
    # ↑ この2つのassertが「commit済のまま」を裏付ければ意図通りRED相当(欠陥の実在確認)。
    #   もし将来是正でtry/exceptの範囲がfk_check後まで広がれば、この2assertはFAILし
    #   （＝ロールバックが効いた＝GREENへ転じた）、それ自体が「直った」の検出器になる。
```

**「fk_checkを人為的に失敗させる具体的な仕込み方」は未設計**（`appointment_history.appointment_id REFERENCES appointments(appointment_id)`という単一FKに対し、rename→再作成の狭い窓でどう不整合行を混入させるかは、`_appointments_ddl_without_broken_unique()`の内部順序に依存し紙上では確定できぬ。次点課題として明記する）。

**「この testは 欠陥(F2)が在れば必ずREDか」**: **書ける**——§3-5実読（前回監査済・今回`apply_booking_concurrency_root`全文を再読し不変を確認）の通り、`conn.commit()`はtry節内・`PRAGMA foreign_key_check`はtry/except/finallyの**外側**にあり、fk_check失敗時にrollbackへ到達する経路がコード構造上**存在しない**。この構造が変わらぬ限り、fk_check失敗を誘発できさえすれば本testは確実にRED（＝rename済tableが残り、旧table名が消えている）になる。

### §4-2 F1 向け陽性対照（★試みたが RED化できず・GREEN-onlyと判定★）

「staff側で同一要求を意図的に再送し、idempotency不在ゆえ重複行ができる」形を試みたが、§2-1の通り**slot claims PKが最終防波堤として効くため、同一slotへの再送は209/IntegrityErrorで弾かれ重複行を作れない**。唯一考えられるRED化経路は「staff側retryが微妙に異なるstart_time（別slot）を計算してしまうケース」だが、**staffのretry呼出し元(`appointments.py`等)はpatch対象外・当職未読**（前回・本便§2-2で二重に明記）ゆえ、その挙動を紙上で仮定して設計するのは「測っておらぬ物を測ったと書く」に当たる。**∴ F1向け陽性対照は現時点で設計不能（書けぬ）と申告する**。

### §4-3 F3 向け陽性対照（★試みたが RED化できず・GREEN-onlyと判定★）

`create_booking`のコード順を再実読（本便§4-1と同じ実測範囲）した結果、`existing`早期return（`_check_conflict`未通過）が発火するのは**「patient_id・menu_id・start・end・treatment_contentが完全一致する、既にactiveな予約が存在する」場合のみ**——これは論理的に**新規の重複を作らず、既存行をそのまま返すだけ**であり、`_check_conflict`が防ぐべき「新規に重複を作る」ケースに該当せぬ。当職はこの経路が悪さをするパターン（例: 別スレッドが`existing`SELECTと`_check_conflict`の間に割り込む、等）を検討したが、`create_booking`全体が`BEGIN IMMEDIATE`配下にあり、同一transaction内では他コネクションの未commit書込は見えぬため、**この経路単体でRED化できる具体的シナリオを構築できなかった**。
**∴ F3は「危うき」として記録には値するが（`_check_conflict`を経由しない経路が存在する事実自体は本監査で確認済）、本工区の紙上設計では陽性対照をRED化できず、GREEN-onlyの位置づけと申告する**。§4-1(F2)との非対称は「零ならば零」の一例であり、F1/F2/F3を無理に同型へ揃えなかった。

## §5 足軽1号の三値判定との関係（争わせぬ・裁は家老second）

家老second下命(2)⒞の通り、足軽1号がF1/F2/F3を三値（有/無/不明相当）で独立に判定中と承知。本便の§4-2/§4-3（F1/F3のRED化不能=GREEN-only）は、**足軽1号が同じ2件を「無い」と判じた場合はそれと整合し得るし、「有る」と判じた場合は本便の設計力不足（staff retry経路未読等）が理由である可能性も残る**——当職はこの優劣を自ら裁定せぬ。§4-1(F2)は当職・前回監査ともに実コード構造で確認済のため、三値判定の結果如何によらず**実在するコード事実**として揺るがぬと考えるが、これも最終裁定は家老second へ委ねる。

## §6 己が本工区で直した誤り

- **前回成果物 `2026-08-06_reserveimage_cycle2_patch_readonly_audit_a4.md` §4 item10 行の「新規finding」（release→claim失敗時に旧claim消失）を、本便§3-2にて訂正**（`conn.rollback()`の作用範囲を今回あらためて突き合わせた結果、消失しない設計と読める）。**訂正の確度も紙上に留まる**旨を明記済（§3-3末尾）。
- 上記以外、repo内file・patch対象fileへの書換えは一切なし（read-onlyゆえ直す手を持たぬ）。

## §7 禁則順守の確認

apply／worktree新設（既存worktreeの読取のみ・新設せず）／DB書込／実走（pytest実行）／hakudokai-devへの書込み——**悉く行っておらぬ**。rcはpipeへ通しておらぬ（本便のBash実行は`grep`/`sed -n`/`git rev-parse`等の単発読取のみ）。

---
生成: ashigaru4 / 2026-08-06 / read-only・紙上設計のみ・apply/worktree/DB/実走 一切なし。
提出先: karo-second + gunshi-second。
