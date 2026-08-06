# F2 現行patch直接回帰test 設計 (足軽2号)

下命=家老second msg_20260806_102449_d21f447a (2026-08-06T10:24:49・出所=本部長殿裁定便
msg_20260806_102049_e6c63cd2・将軍second経由で家老second受領)。

**冒頭・別枠宣言 (⒟)**: ★本工区は項13の既存2 detector
(`test_true_two_connection_same_slot_only_one_active_row` /
`test_exact_request_replay_returns_same_appointment_id`。旧code陽性対照・已に定義済・修正前RED実測済) とは
**別枠**である。項13の2件=「旧codeに当てて陽性対照RED維持を再検定する仕組み」。本工区(F2)=
「現行patch (booking_concurrency_root.py) 自体が持つ欠陥への直接回帰test」。★両者を混ぜれば
「已に在る物」と「新たに要る物」が見分け得なくなる (下命(1)原文)。本書は後者のみを扱う★。

**冒頭・F2単独発火の事実**: F1/F2/F3のうち、現構造で紙上RED化が可能なのは★F2のみ★
(足軽4号 実測・`2026-08-06_reserveimage_f1f3_greenonly_causal_analysis_a4.md` §3-2=
「RED化に要る物: 入力データの用意のみ〈dangling FKを仕込んだconn〉— 呼出しは1回・単一スレッド・並行性は不要」)。
F1/F3は㈡構造上不能 (同書§1-3/§2-3)。本書はF2の「入力データの用意」部分——
足軽4号が前回成果物 (`_gap_test_design_9_10_12_a4.md` §4-1末尾) で
「fk_checkを人為的に失敗させる具体的な仕込み方は未設計」と明記した箇所——を埋める。

## §0 境界・禁則遵守の申告

- ★設計のみ。書いておらぬ・走らせておらぬ★。`hakodoukai-dev`(`/tmp/resimg-*`系統含む) へは一字も書いていない。
  apply・patch適用・worktree新設・DB接触・実走 (pytest等)、いずれも行っていない。
- 参照は `git show` / `sed -n` / `grep -n` (悉く `/usr/bin/grep`、pipe未使用・単発実行) による読取のみ。
- ★newbuild へも一字も書いていない★ (本工区のscope外・存在にも触れていない)。
- 本書自体が新規作成する file はこれ1本 (docs/incident_logs/ 配下)。既存 file は一字も書き換えていない。
- 参照先固定: base_commit (hakodoukai-dev側, 読取のみ) = `7d463edae84c704edabbd9da5465078dc62e55b1`
  (実測: `git -C /tmp/resimg-cycle2-impl-20260806 rev-parse HEAD`。前工区群と不変であることも確認)。
  worktree自体は前工区で他者が用意した物 (当職は新設していない)。
- 本repo base_commit = `89685bf202cedef63f30638010116f817ab9ea5d` (§末尾に断面として再掲)。

## §1 実測の独立再確認 (己の手で行末まで数え直した)

パッチ本体 (`/home/hakudokai/hermes-departments/honbucho/reports/reserveimage-cycle2-gate2-4-handoff-20260806.patch`、
`booking_concurrency_root.py` は diff 456行目〜763行目、`@@ -0,0 +1,301 @@` = 新規301行) を対象に、
新規fileの行番号 (diffの `+` を剥いた実ファイル行) を己で数え直した (先行agentの申告値を写さず独立算出):

```
217: def apply_booking_concurrency_root(conn, slot_minutes=SLOT_MINUTES) -> dict[str, Any]:
...
229:     conn.commit()                              # 準備段commit(本工区の対象外)
231:     conn.execute("PRAGMA foreign_keys=OFF")
233:         conn.execute("BEGIN IMMEDIATE")
235:         conn.execute("ALTER TABLE appointments RENAME TO _appointments_pre_root")
...(appointments再作成・INSERT...SELECT・DROP _appointments_pre_root・idx再作成)...
...(booking_idempotency / appointment_slot_claims 新規CREATE TABLE)...
284:         conn.commit()                          # ★スキーマ変更のcommit — try節内★
285:     except Exception:
287:             conn.rollback()
289:     finally:
291:         conn.execute("PRAGMA foreign_keys=ON")
293:     fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
295:         raise RuntimeError(f"foreign_key_check failed: {len(fk_errors)}")
```

一致=先行2件 (足軽4号2件) の申告値と己の独立再算出が完全一致 (284/285-291/293-295)。★写しではなく
己で数え直した上での一致★であることをここに明記する。

## §2 ⒜ dangling FK をどう用意するか (紙上の手順・DB未接触)

### §2-1 前提となる事実 (base repo `appointment_tables.py` を読取確認)

`git -C /tmp/resimg-cycle2-impl-20260806 show HEAD:backend/db/migrations/appointment_tables.py` で読取確認
(1325行、当該worktreeでは本fileは非改変=working treeの `M`/`??` 一覧に含まれず、HEAD版=worktree版が一致):

| table | FK | 行 |
|---|---|---|
| `appointment_history` | `appointment_id INTEGER NOT NULL REFERENCES appointments(appointment_id)` | 123 |
| `appointment_reminders` | 同上 | 191 |
| `prediction_log` | 同上 | 231 |

`appointments` テーブルのPK列名 = `appointment_id INTEGER PRIMARY KEY AUTOINCREMENT` (75-78行、
上記3件の参照先と一致することを確認)。

これら3 tableは `apply_booking_concurrency_root` が触れる対象 (`appointments` 本体・
`booking_idempotency`・`appointment_slot_claims`) の★外側★にある——同関数は
`appointments` のrename/再作成 と 新規2 tableの作成のみを行い、`appointment_history` 等の
中身には一切触れない (§1の行番号内に該当操作が存在しない事は実測済)。

### §2-2 仕込み手順 (紙上・4段)

1. **schema構築**: 既存test流儀 (`sqlite_init.TABLES`型のloop。他工区が既に使う fixture 相当) で
   `APPOINTMENT_TABLES` 全体を空DBへ適用し、`appointments` + `appointment_history` を含む
   全既存tableを用意する (この段階では `booking_idempotency`/`appointment_slot_claims` はまだ無い
   ——これらは `apply_booking_concurrency_root` 自身が作る新規table)。
2. **正常行を1件だけ用意**: `appointments` へ active な1行 (`appointment_id=1`、15分grid整合の
   `start_time`/`end_time`) をINSERT。これは `scan_active_overlaps`/`scan_slot_granularity` を
   クリーンに通す為の最小構成 (F2の検出対象外の経路を先に塞ぎ、fk_check失敗のみを単一原因にする)。
3. **★dangling行を1件だけ仕込む★**: `appointment_history` へ
   `(appointment_id=999, action='created', changed_by='test')` をINSERT。`999` は手順2で作った
   `appointments` のどの行番号とも一致しない値を選ぶ (=当初から存在しない参照先)。
   ★sqlite3は`PRAGMA foreign_keys`の既定値がOFF★ (base repo の別migration関数
   `migrate_appointments_drop_patient_hash`が明示的に `cur.execute("PRAGMA foreign_keys = OFF")`
   →作業→`= ON` と往復させている実例が同fileに存在=1240/1257行、当職読取確認)。
   ∴ この手順単体では接続の既定設定に依存させず、**INSERT直前に明示 `conn.execute("PRAGMA
   foreign_keys=OFF")` を打ってから999行を挿む**設計とする (下記§4「新たに開ける穴」1点目の対策と直結)。
4. **1件のみに絞る**: 他のFK参照table (`appointment_reminders`/`prediction_log`) へは行を入れない。
   ★仕込む dangling 行は悉皆1件のみ★とし、`PRAGMA foreign_key_check` の返す違反件数を
   「必ず1件」に固定する (複数件仕込むと件数assertが曖昧になる=下記§4で明記)。

以上いずれも★紙上の手順として記述したのみであり、当職はこれをDB上で実行していない★
(下命の禁=「実走するな」に従う)。

## §3 ⒝ 「欠陥が在れば必ずRED」を何で担保するか

担保は**確率ではなく§1のコード構造そのもの**による (足軽4号の実測=§1参照先と同一構造を、
本工区でも§1で独立に再確認済):

1. `PRAGMA foreign_keys=OFF` (231行) が `try` 突入前に敷かれ、`finally` (289-291行) で
   `ON` に戻るまでの全区間、FK制約は一度も評価されない。§2で仕込んだ999行は
   この区間を無傷で通過する (`appointment_history` は同関数が一切書き換えない table であり、
   通過を妨げる操作が存在しない事は§1の行番号列挙で確認済=消極的事実ではなく積極的な「不在の実測」)。
2. `conn.commit()` (284行) が `try` 節の**内側**にあり、`except`/`finally` のいずれよりも
   ★コード上先に★ 実行される。この commit は §2で仕込んだ999行を含む DB 全体の未commit分
   (renameされた `appointments`・新規2 table・999行いずれも) を確定させる。
3. `PRAGMA foreign_key_check` (293行) は `try`/`except`/`finally` の**外**にあり、
   `finally` で `foreign_keys=ON` に戻った★後★に実行される。sqlite3の `foreign_key_check`
   は現在のDB内容を無条件に走査する (pragma状態に関わらず既存データを検定する、
   `PRAGMA foreign_keys`は将来のDML/DDLに対する強制のON/OFFであり、`foreign_key_check`自体は
   別系統の一括検定コマンドである)。999行は`appointments`のどの行番号とも一致しないままなので、
   この走査は★必ず★ 1件以上の違反を返す。
4. 293-295行の条件分岐に「0件なら何もしない・1件以上ならraise」以外の分岐は存在しない
   (§1の行番号列挙どおり)。∴ 999行が存在する限り、この関数呼び出しは
   ★必ず★ `RuntimeError("foreign_key_check failed: 1")` を送出する。

**∴「必ずRED」の担保は、(i) 999行がtry区間を通過できる (FK評価が丸ごとOFF)、
(ii) 通過した999行を含めてtry内でcommitが確定する、(iii) commit確定後にのみfk_checkが走る、
の3点が★コード上の固定順序★であり、並行性・タイミング・乱数のいずれにも依存しない**
(足軽4号 §3-2「決定的・何度呼んでも同じ結果」と同結論・当職は独立に構造を再確認した上でこれに同意する)。

## §4 ⒞ この設計が新たに開ける穴

1. **fixtureのpath固定リスク**: §2の手順は「使い捨てDB」を前提とする。もし将来この
   仕込み手順が `tmp_path` 等のpytest標準の一時fixtureではなく固定pathへ書かれた場合、
   ★dangling FKを意図的に持つ壊れたDBファイルが残存/再利用され得る★。
   対策として明記する=本設計は★pytestの`tmp_path`(またはそれに準ずる、testごとに使い捨てられる
   一時fixture)専用とし、固定pathを一切使わない事★をtest実装者への要件として本書に残す。
2. **既定pragma依存の隠れた脆さ**: §2-2手順3で「sqlite3のFK既定値はOFF」を利用する設計とした。
   もし将来、DB接続を開くヘルパ (`_open_file_db`等) 自体が「安全側に倒す」改修で
   `PRAGMA foreign_keys=ON` を既定化した場合、★999行の仕込み自体がINSERT時点で
   `sqlite3.IntegrityError` を起こし、本testの前提 (仕込みが成功する事) が壊れる★。
   ∴ §2-2手順3で明示した「INSERT直前に `PRAGMA foreign_keys=OFF` を自testが打つ」設計は
   この将来変更に対する予防線として必須であり、接続ヘルパ側の既定値に依存しない事を
   本工区の必須要件として明記する (=「壊れたDB状態を作る手続き」自体を一般ユーティリティ化せず、
   本negative-test専用の局所処理として閉じ込める。汎用fixtureへ格上げしない)。
3. **「意図的に壊れたDBを作る」パターンの伝播リスク**: 本testは「dangling FKを持つDBを
   意図的に構築する」という、通常のtestでは避けるべき操作を正当に行う。この手続きが
   関数として外出しされ他testから再利用されると、★本来「守るべき制約が壊れている異常系」
   専用のはずの仕込みが、無自覚に他の正常系testへ混入する危険がある★。
   対策=本設計のヘルパ名は `_seed_dangling_fk_for_negative_test_only` のように
   ★用途を名前に刻み、他testからの流用を能動的に思い留まらせる命名とする事★を実装要件とする。
4. **「直った時にこのtestが自動的にGREEN化する」ことの意味**: 本testは★現行codeの欠陥を
   前提としたRED期待test★である。もし将来 `apply_booking_concurrency_root` の
   try節がfk_check後まで拡張される是正がなされれば、本testは自動的にGREENへ転じる
   (§4-1の設計時点で既に足軽4号が同旨を指摘済=`_gap_test_design_9_10_12_a4.md` §4-1末尾コメント)。
   ★これは「直った証拠」として正しく機能するが、そのままでは「意図的に壊れたDBを作って
   例外を期待する」という異常系専用のtestが正常系のsuiteに残り続ける★——是正後は
   本testの docstring/assert 意味 (「commit済のまま」→「rollbackされ、999行もそもそも
   到達しない」等) を★手動で書き換える追補作業が要る事★を、本工区の申し送りとして明記する
   (削除だけで済ませると「検出器が消えた事に誰も気付かない」= false-green型の再発)。

## §5 ⒟ 別枠である事の確認 (冒頭の宣言の再掲・形式要件)

本工区の成果物 (仕込み手順 + 疑似コード) は項13の2 detector
(`test_true_two_connection_same_slot_only_one_active_row`/`test_exact_request_replay_returns_same_appointment_id`)
と★file・対象・目的のいずれも共有しない★。項13の2件=旧code (base `7d463ed`)へ当てるRED維持再検定。
本工区=現行patchのbooking_concurrency_root.py単体への直接回帰test。混在させて1つのtest classへ
まとめる設計は本書では採らない (下命(1)の指示どおり、書面上も別枠として保つ)。

## §6 pytest疑似コード (紙上・未作成・未実行)

足軽4号の骨子 (`_gap_test_design_9_10_12_a4.md` §4-1) を土台とし、§2-2で埋めた仕込み手順を
`_seed_dangling_fk_for_negative_test_only` として明示した版。★当repo・hakodoukai-dev いずれにも
このfileは作成していない。以下はコードブロックとして紙上に記すのみ★:

```python
# 配置先案: backend/tests/test_booking_concurrency_root_migration.py
# (patch内に既存・diff 763行目〜。新規classとして追加する想定。当職は未作成・未実行)

def _seed_dangling_fk_for_negative_test_only(conn: sqlite3.Connection) -> None:
    """★negative-test専用。appointment_history へ appointment_id=999
    (どのappointments行にも一致しない値) の行を仕込み、意図的にFK違反を作る。
    他のtestから再利用しない事(§4-3)。"""
    conn.execute("PRAGMA foreign_keys=OFF")   # §4-2: 接続既定値に依存させない明示指定
    conn.execute(
        "INSERT INTO appointment_history(appointment_id, action, changed_by) "
        "VALUES(999, 'created', 'test')"
    )
    conn.commit()


def test_fk_check_failure_leaves_schema_committed_not_rolled_back(tmp_path):
    """回帰test(F2): fk_check失敗時、apply_booking_concurrency_root は
    スキーマ変更をcommit済のまま例外送出する(既存の欠陥・現行codeでは意図的にRED)。
    項13の2 detector(旧code陽性対照)とは別枠(本書§5)。
    tmp_path専用(§4-1、固定pathを使わない)。"""
    conn = _open_file_db(tmp_path / "f2_regression.db")   # 既存fixture流儀を流用(新規発明なし)
    _create_all_appointment_tables(conn)                    # APPOINTMENT_TABLES を loop 適用
    conn.execute(
        "INSERT INTO appointments(appointment_id, clinic_id, unit_id, start_time, end_time, "
        "duration_minutes, status, ...) VALUES(1, 1, 1, '2035-06-01 09:00:00', "
        "'2035-06-01 09:15:00', 15, 'confirmed', ...)"
    )
    conn.commit()
    _seed_dangling_fk_for_negative_test_only(conn)          # ★999行=dangling FK仕込み(§2-2)★

    with pytest.raises(RuntimeError, match="foreign_key_check failed"):
        apply_booking_concurrency_root(conn)

    # ★眼目(a4案を継承)★: commit済(=欠陥の実在)か否かを検める
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "_appointments_pre_root" not in tables      # rename後table消失=commit済の証
    assert "appointment_slot_claims" in tables          # 新tableも作成済のまま=commit済の証
    # ★本工区での追加(§3の担保を直接裏付ける)★: 999行がなお存在する事(=検出はしたが治せていない)
    dangling = conn.execute(
        "SELECT COUNT(*) FROM appointment_history WHERE appointment_id=999"
    ).fetchone()[0]
    assert dangling == 1                                # 仕込んだ1件のみ・除去されていない
```

**未確定 (紙上ゆえ検めていない、次点課題として明記)**: `appointments`の全カラム構成
(`INSERT`文の省略部分`...`) は当職が今回列挙していない (base repoのDDL全カラムを1つずつ
突き合わせる作業は本工区の時間内に未実施)。既存test (`test_booking_concurrency_root_migration.py`
diff763行目〜) の既存fixtureヘルパを流用すれば省略できる可能性が高いが、★当職はそのヘルパの
中身を読み切っていない★——「読めば埋まる」類の未測であり、書けぬ物ではない事だけを申告する。

## §7 対に成る他工区

- `docs/incident_logs/2026-08-06_reserveimage_cycle2_gap_test_design_9_10_12_a4.md`
  (足軽4号・219行) §4-1——本工区が埋めた「未設計」の出所そのもの。
- `docs/incident_logs/2026-08-06_reserveimage_f1f3_greenonly_causal_analysis_a4.md`
  (足軽4号・144行) §3——F2のみ構成可能である事の論拠。本書冒頭で引用。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_red_positive_control_design_a3.md`
  (足軽3号) §2-4/§3-2——項13の2 detectorの正体、およびF2を「旧code陽性対照とは別枠の
  現行patch直接回帰test」と初めて明確化した工区 (本書はこの区分を継承・実装レベルへ具体化)。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_defect_handoff_a5.md` (足軽5号)——
  F1/F2/F3三値の一枚渡し。本書のF2の症状記述の一次出所。

## §8 本工区で己が直した誤り

無し (新規実測は§1〈独立再算出・先行値と一致〉と§2-1〈appointment_tables.py 読取〉のみで、
いずれも先行agentの申告と矛盾しなかった。訂正すべき誤りは生じていない)。

## §9 監査体制

暫定★二者制★ (軍師second + Gemini。監査モデル gpt-5.4 暫定)。Codex leg は SAFETY裁定 seq132707
により停止中。★「二者PASS」を「三者PASS」と書かない★ (委員長殿裁定・下命形式要件どおり)。

## 禁則遵守の確認 (再掲)

設計のみ。test fileの新規作成・書込みは一切なし (本file自体が設計文書であり、pytest実装ではない)。
`hakodoukai-dev`・`/tmp/resimg-*`系統への書込み・apply・worktree新設・DB接触・実走 (pytest実行)
いずれも未実施。`newbuild`へも一字も書いていない。`/usr/bin/grep -r`の使用は本工区の調査範囲では
不要だった (単発`grep -n`/`git show`/`sed -n`で足りた)。rcはpipeへ通していない。commitは
karo-second殿がPASS後に行う。

---
断面: 2026-08-06T10:30:37+0900 (機械・提出直前再測)／本repo base_commit (測定時HEAD)=
`89685bf202cedef63f30638010116f817ab9ea5d`／hakodoukai-dev側参照base=
`7d463edae84c704edabbd9da5465078dc62e55b1` (読取のみ・不変)。
提出先: 家老second + 軍師second。
