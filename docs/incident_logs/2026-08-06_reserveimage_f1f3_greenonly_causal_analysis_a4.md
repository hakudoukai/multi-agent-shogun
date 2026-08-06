# 足軽4号 → 家老second/軍師second: F1/F3 GREEN-only 因の逐語分析（read-only）

断面: 2026-08-06T09:54:52+0900（当職 実測、`date` コマンド）。本便は read-only。apply/worktree新設/DB/実走 一切なし。rc はpipeへ通しておらぬ。
下命出所: `queue/inbox/ashigaru4.yaml` msg_20260806_095028_d66483f9（家老second→足軽4号、09:50:28）。
参照先固定: base=`7d463edae84c704edabbd9da5465078dc62e55b1`（実測=`git -C /tmp/resimg-cycle2-impl-20260806 rev-parse HEAD`・前回監査と不変）。
コード実読は既存worktree `/tmp/resimg-cycle2-impl-20260806`（前工区で他者が用意した物・当職が新設せず）への**読取のみ**。1文字も書き換えておらぬ。

## §0 冒頭の結論（「難しい」は書かぬ）

**F1・F3 とも、不能の因は各々 ★一つ★ に絞れる。かつ ★F1 は 前回報告の分類そのものが不正確であった★（下記§0-1で自己是正）。**

- **F1**: 不能の因＝**㈡構造上不能**。今回 呼出し元（backend `appointments.py` + frontend `useAppointmentForm.ts`）を実読した結果、実在するcaller には retry機構が一切無く、かつ同一slotへの重複再送は idempotency とは別の機構（`appointment_slot_claims` PK）が先に捕捉するため、F1単体を検出するREDが構成できぬ。
- **F3**: 不能の因＝**㈡構造上不能**。`create_booking` 冒頭の `BEGIN IMMEDIATE`（writer lock先取り）が該当コード全体を直列化しており、2接続が early-return分岐の内側で競合する窓が構造的に存在せぬ。

### §0-1 自己是正（前回報告の分類誤り）

前回成果物（`2026-08-06_reserveimage_cycle2_gap_test_design_9_10_12_a4.md` §4-2）で当職は F1 の不能理由を「staff側retry呼出し元(`appointments.py`等)は**patch対象外・当職未読**」と書いた——これは**㈠情報が足りぬ**（読めば解ける）の体裁であった。
**今回 実際に `backend/api/appointments.py` と `frontend/.../useAppointmentForm.ts` を読了した結果、情報は既に読める状態にあり（patch対象外という前提自体が誤り）、読んだ上で判った事実は「retry機構が存在しない」という★構造上の事実★であった。**
∴ **前回の㈠判定は誤りであり、正しくは㈡である**。原因＝前回は「読んでおらぬ」事実のみを申告し、「読めば何が判るか」まで踏み込まなんだ（求めた検証を己で先送りした落度）。

---

## §1 F1（staff経路idempotency未配線）の逐語分析

### §1-1 実測（呼出し元 全経路）

**backend側 (`backend/api/appointments.py` L30-98)**:
- `CreateAppointmentRequest`（Pydanticモデル、L30-56）に **`idempotency_key` フィールドが存在せぬ**（実測: `grep -n "idempotency_key" backend/api/appointments.py` → 0件）。
- `api_create_appointment`（L85-98）は `create_appointment(conn, req.model_dump(), req.source)` を**単発呼出し**するのみ。retry・再送検知ロジックは無い。`sqlite3.IntegrityError` を409へ変換するのみ（呼出し元へ返すだけで、自ら再試行はせぬ）。

**frontend側 (`frontend/src/features/appointments/hooks/useAppointmentForm.ts` L441-555)**:
- staff予約作成フォームの唯一の送信経路。`setLoading(true)` → 単発 `fetch(POST /api/appointments)` → 失敗時は `{success:false, error}` を呼出し元(UI)へ返して**終わり**（自動retryのループ・指数バックオフ・再送コードは0件、`grep -n "retry" useAppointmentForm.ts` → 0件）。
- 二重送信ガード: `AppointmentForm.tsx` の submitボタンは `disabled={loading}`（L845/1141/1158/1195実測）。`setLoading(true)` は非同期関数冒頭・最初の`await`より前に同期実行される。
  - **残る隙間（F1とは別種の一般的UIリスクとして申告・混同せぬ）**: React の再描画は次tickゆえ、`disabled`属性の反映までクリック→再描画の1フレーム未満の窓が理論上ある。これは**任意のReactフォームに共通する既知の一般論**であり、idempotency_key不在(F1)固有の欠陥ではない。本分析ではF1の因として数えぬ（型を混ぜぬ）。

### §1-2 「F1が在ればREDになる」形を試みた結果

`create_appointment` を同一slot・同一paramsで2回連続呼出す形（sequential replay想定）を紙上で構成すると:
1. 1回目: `appointments` へINSERT成功 → `claim_appointment_slots` が `appointment_slot_claims(clinic_id,unit_id,slot_start)` PKへINSERT成功 → commit。
2. 2回目（同一params）: `appointments` へは再度INSERT可能（`appointments`側に一意制約は無い）だが、`claim_appointment_slots` が同一PKへ二度目のINSERTを試み **`sqlite3.IntegrityError`** → `api_create_appointment` L95-96で409へ変換 → **2件目は成立せぬ**。

**∴ F1（idempotency不在）そのものは実在するが、実際に重複行を作る所まで到達する前に、別機構（slot claims PK）が先に食い止める。この食い止めは idempotency ではなく「物理slotの一意性制約」であり、F1の代償にはなるが F1 の不在を検出する陽性対照にはならぬ**（検出したいのは「idempotencyが無い事」であって「slot衝突が起きる事」ではない）。

### §1-3 不能の因（三値判定）

| 値 | 該当性 |
|---|---|
| ㈠情報が足りぬ | **該当せず**（§0-1の通り、今回読了済。読んだ結果が下記㈡） |
| ㈡構造上不能 | **★該当★** — 実在する唯一のcaller（frontend単発fetch）にretry機構が無く、かつ同一slotへの再送は別機構(PK)が先に捕捉するため、「F1単体の不在」を選択的に検出するREDを構成する入力が存在せぬ。REDを作るには「retryするが微妙に異なるslotを計算する」という**実在せぬcaller挙動**を仮定する必要があり、それは測っておらぬ物を測ったと書く事に当たる |
| ㈢権が無い | **該当せず**（読取・実行いずれも当職の権限内。frontend/backendとも当職のread scope内） |

---

## §2 F3（idempotency_key未使用時のexisting簡易replay早期return）の逐語分析

### §2-1 実測（`booking_service.create_booking` L198-316）

```
214:    conn.execute("BEGIN IMMEDIATE")          # ★writer lock 先取り・関数の最初の書込★
...
249:    if root_enabled and idempotency_key:      # idempotency_key使用時の分岐（先）
...
260:    existing = conn.execute(...)              # ★F3対象: 簡易replay判定 SELECT★
270:    if existing and not (root_enabled and idempotency_key):  # ★早期return分岐★
271:        conn.commit()
272:        return {...}
280:    _check_conflict(conn, clinic_id, start_dt, end_dt)
```

`BEGIN IMMEDIATE` は関数冒頭・全ロジックの前で writer lock を取得する。SQLiteの `BEGIN IMMEDIATE` は「他のwriter接続がこのlockを取得するまでブロックする」動作であり、**後続の `create_booking` 呼出し（別接続）は260-278行の実行中、必ず214行でブロックされ待機する**。∴ 2接続が同時に260行の `existing` SELECTへ到達する事は構造上起こり得ぬ（片方が必ず先にcommitまたはrollbackし、lockを解放してから他方が進む）。

### §2-2 「F3が在ればREDになる」形を試みた結果

F3が問題化し得るのは「`existing` が古い/不正確な状態を読み、後続の書込と食い違う」場合だが、`BEGIN IMMEDIATE` により:
- 先行トランザクションが commit済みなら、後続の `existing` SELECT は先行の結果を**必ず**見る（lock解放後に開始するゆえ）。
- 先行トランザクションが rollback済みなら、後続は先行の変更を一切見ない（無かった事になる）。
- **「先行の変更を一部だけ見る」中間状態は SQLite の write-lock直列化により発生し得ぬ**。

∴ F3の早期return分岐は「同一内容の予約が既に存在するなら、新規作成せず既存IDを返す」という**意図した直列化replay一致**として一貫して動作し、これを「競合状態」として検出するREDを構成する入力（2接続が矛盾した状態を同時に見る具体的シナリオ）が存在せぬ。

### §2-3 不能の因（三値判定）

| 値 | 該当性 |
|---|---|
| ㈠情報が足りぬ | **該当せず**（`create_booking`全文・`BEGIN IMMEDIATE`の位置とも今回・前回とも実読済） |
| ㈡構造上不能 | **★該当★** — `BEGIN IMMEDIATE`によるwriter lock直列化が、early-return分岐を「複数接続が矛盾した状態を同時に見る」形にする経路を構造的に排除している。RED化には SQLite の直列化保証そのものを破る入力が要るが、それは「バグの再現」ではなく「SQLiteの提供する保証を無視した仮定」になる |
| ㈢権が無い | **該当せず** |

---

## §3 F2（fk_check失敗時already-committed）が構成可能であった理由

### §3-1 実測（`apply_booking_concurrency_root` 構造・行番号は前回監査と不変）

```
217: def apply_booking_concurrency_root(conn, ...):
229:     conn.commit()          # 準備段のcommit（本節と別）
232:     try:
...(rename/DDL)...
284:         conn.commit()      # ★スキーマ変更のcommit（try節内）★
285:     except Exception:
...(rollbackあり)...
289:     finally:
...
293:     fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()   # ★try/exceptの外★
295:         raise RuntimeError(f"foreign_key_check failed: {len(fk_errors)}")
```

`conn.commit()`（284行）は try節**内**で実行され、`PRAGMA foreign_key_check`（293行）は try/except/finally**の外**にある。∴ fk_check失敗時にraiseされる例外へ到達するルートは、そもそも try/exceptのrollback機構の対象外——**284行のcommitは必ず先に確定済**。

### §3-2 F1/F3との対比（不能の因の違いを際立たせる）

| 項目 | F2 | F1 | F3 |
|---|---|---|---|
| 欠陥の所在 | 単一関数の**直列コード構造**（try/exceptの範囲外にfk_check） | 実在しないcaller挙動（仮定のretry） | SQLiteのwriter lock直列化が防ぐ競合窓 |
| RED化に要る物 | **入力データの用意のみ**（dangling FKを仕込んだconn） — 呼出しは1回・単一スレッド・並行性は不要 | 実在せぬ「異なるslotを計算するretry」というcaller挙動の**発明** | SQLiteの直列化保証を**破る**入力（構造的に用意不能） |
| 並行性・タイミング依存 | **無し**（決定的・何度呼んでも同じ結果） | 有り（だが実在せぬ挙動が前提） | 有り（だがlockが窓を閉じている） |
| ∴ 構成可能性 | **可能**（単発呼出し＋データ仕込みで再現） | 不能（caller不在） | 不能（lockが窓を閉じる） |

**要点**: F2は「関数内の条件分岐（try/exceptの範囲）」という**当職が制御できる入力（DB状態）のみ**で決定的に再現できる欠陥である。F1/F3は、再現のために「当職が制御できぬ物」（実在せぬcaller挙動／SQLiteの排他制御そのもの）を要求するため、紙上設計の射程を超える。

---

## §4 家老second下命への直接回答（(1)〜(4)まとめ）

- **(a) F1**: 何が在ればREDになるか＝実在せぬ「slotを僅かに変えて再送するcaller」の発明。**成らぬ因＝実在するcallerに retry機構自体が無く、同一slot再送はPKが先に捕捉するため（㈡構造上不能）**。
- **(b) F3**: 不能の因＝`BEGIN IMMEDIATE`によるwriter lock直列化が、early-return分岐を矛盾状態で通過させる経路を構造的に排除している（㈡構造上不能）。
- **(c) 三値**: F1・F3とも ㈡構造上不能。㈠（前回のF1分類）は今回の実読により**誤りと判明**（§0-1）。㈢は両者とも非該当。
- **(d) F2が構成可能であった理由**: 欠陥がtry/except範囲外という**単一関数内の決定的コード構造**にあり、並行性・実在せぬcaller挙動のいずれにも依存せず、入力（dangling FK）の用意のみで確実に再現できるため。

## §5 己が本工区で直した誤り

- **前回報告のF1不能理由の分類（㈠情報不足）を、今回の実読により㈡構造上不能へ訂正した**（§0-1）。前回「patch対象外・当職未読」と書いた前提自体が誤りであり、実際は読める状態にあった。

## §6 禁則順守の確認

hakudokai-dev（`/tmp/resimg-*`系統含む）への書込み・apply・worktree新設・DB接続・実走（pytest等）——**悉く行っておらぬ**（本便は読取専用コマンドのみ: `git rev-parse`/`grep`/`date`）。rcはpipeへ通しておらぬ。

**`/usr/bin/grep`使用の確認（実測）**: 本便の全grep呼出しは`/usr/bin/grep`を明示指定済（`which grep`実測でも`/usr/bin/grep`のみ・alias/wrapper無し、本便作成中に確認）。当初この節に「未確認ゆえ疑わしきは申告」と書いたが、**実測せず書いた申告であった**ため、実測後の本文へ差し替えた（憶測での自己申告は、実測を経ぬ限り確定情報として書かぬ）。

---
生成: ashigaru4 / 2026-08-06T09:54:52+0900 / read-only・紙上分析のみ・apply/worktree/DB/実走 一切なし。
提出先: karo-second + gunshi-second。commit は karo-second（PASSの後）。
