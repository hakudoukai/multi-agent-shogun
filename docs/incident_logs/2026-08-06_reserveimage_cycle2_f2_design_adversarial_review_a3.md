# F2 現行patch直接回帰test 設計 — 反証役レビュー (足軽3号)

下命=家老second msg_20260806_104108_5b52ea68 (2026-08-06T10:41:08)。
対象=`docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md`
(261行 sha256=3b0e8754ab10112e845ec2eae50516e306451e36c205609a8613ae9eee3c0fd6・下命本文の値と当職手元sha一致を確認)。

**冒頭・姿勢**: 下命どおり「同意を探すな。反証を探せ」を実行した。走らせず・DB接触せず・
hakodoukai-dev/newbuildへ一字も書かず、参照先 (`/tmp/resimg-cycle2-impl-20260806`、
HEAD=`7d463edae84c704edabbd9da5465078dc62e55b1`・a2申告値と一致確認済) を読取のみで検めた。
結論を先に言えば——**§3の核心担保 (コード構造による決定性) は当職の独立読取でも成る。
然れど §2-2/§6 の具体的な仕込み・pseudocodeには、a2が自ら挙げた4穴に含まれぬ★誤り★が
少なくとも3点在る**。裁定 (何を以て収めるか) は当職の権限外ゆえ、家老second殿へ委ねる。

---

## ⒜ dangling FK 仕込みは「この形で」現に仕込め申すか

| 小問 | 判定 | 根拠 |
|---|---|---|
| INSERT自体が通るか | ①成る | `appointment_history` の NOT NULL列は `appointment_id`/`action`/`changed_by` の3つのみ (`appointment_tables.py:118-129` 読取確認)。a2のINSERT文はこの3列を悉く埋めており、`action='created'` はCHECK制約の許容値に含まれる。列不足によるINSERT失敗は無い。 |
| 999が将来実在し得ぬか | ①成る | 本testは`appointments`へ1行 (id=1) のみ挿入する使い捨てDB。AUTOINCREMENTは1から始まり本test内で999まで到達する経路が無い。 |
| OFFの射程は当該接続のみか | ①成る | SQLiteの`PRAGMA foreign_keys`は接続単位の設定であり、他接続・DBファイル自体には影響しない。a2の主張どおり。 |
| **違反件数が「必ず1件」に固定されるか (a2 §2-2手順4の明示claim)** | **②誤りが在る** | 下記詳述。 |

### ★発見1: 「違反件数=必ず1件」は a2 自身の pseudocode 前提と矛盾する★

a2 §2-2手順4は明記する:「他のFK参照table (`appointment_reminders`/`prediction_log`) へは行を入れない…
仕込む dangling 行は悉皆1件のみとし、`PRAGMA foreign_key_check` の返す違反件数を『必ず1件』に固定する」。

然れど `appointments` テーブル自体が既に FK を持つ: `unit_id INTEGER NOT NULL REFERENCES units(unit_id)`
(`appointment_tables.py:81` 実読確認)。a2 §6 pseudocodeは `_create_all_appointment_tables(conn)`
(=「APPOINTMENT_TABLESをloop適用」の意) で `units` テーブルを**スキーマとしては作るが、
`units` へ行を1件も挿入していない**。その状態で `appointments(unit_id=1, ...)` をINSERTすれば、
`unit_id=1` は `units` テーブルに存在せぬ参照 = **もう1件のFK違反**。

∴ `PRAGMA foreign_key_check` の返す違反は **999行 (appointment_history) + unit_id=1孤児 (appointments)
の計2件**であり、a2の明記した「必ず1件」は当職の独立検算で**成立しない**。

**★但し書き (公平性のため明記)★**: §6 pseudocodeの実際のassertは
`pytest.raises(RuntimeError, match="foreign_key_check failed")` という**部分一致**のみで、
件数を検めていない。∴ このtest自体はRED (期待どおり例外送出) には成る——**「必ずRED」という
§3の結論そのものは揺るがぬ**。誤っているのは「件数を1件に固定できる」という**a2自身が
明記した設計上の主張**であり、その主張の裏付け (`units`行の未投入) が pseudocode内に
存在しないという点。実装者がこの誤りに気付かず「件数=1」を前提にした将来のassertを足せば、
その時初めて表面化する種の欠陥である。

**是正案 (紙上)**: `units(unit_id=1, clinic_id=1, name=...)` をINSERTに加えれば、
a2の「必ず1件」claimは成立する。対象file (`test_booking_concurrency_root_migration.py`) の
既存 `_schema()` ヘルパ (28行) は現に `units` へ1行INSERTしている——後述⒞で詳述するが、
a2は§6でこの既存ヘルパを使わず別の (存在しない) ヘルパ名を充てた。

---

## ⒝ 「必ずRED」の担保はコード構造で成るか

**当職の独立行番号再々算出 (a2の§1採番を写さず、`grep -n` で自ら再抽出)**:

```
217: def apply_booking_concurrency_root(...)
229:     conn.commit()
230:     conn.execute("PRAGMA foreign_keys=OFF")
233:         conn.execute("BEGIN IMMEDIATE")
284:         conn.commit()          # try節内
285:     except Exception:
287:             conn.rollback()
289:     finally:
291:         conn.execute("PRAGMA foreign_keys=ON")
293:     fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
295:         raise RuntimeError(f"foreign_key_check failed: {len(fk_errors)}")
```

**a2の§1申告値 (217/229/231/233/235/284/285/287/289/291/293/295) と完全一致**。
足軽4号→a2→当職の**三者が独立に同じ行へ収束**した。①**成る**。

`appointment_history` に対する操作は217〜301行の全域に一切存在しない (探して不在=積極的実測)。
∴ FK OFF区間 (230〜291) を999行が無傷で通過する点、commit (284) がtry内側で
except/finallyより先にコード上実行される点、`foreign_key_check` (293) がfinallyの外側かつ
`foreign_keys=ON`復帰後に無条件で全DBを走査する点——いずれも当職の独立読取で確認でき、
①**成る**。並行性・タイミング依存の要素は見当たらぬ。

**軽微な言い回しの不正確さ (実害なし)**: a2 §3-2は「この commit は§2で仕込んだ999行を含む
DB全体の**未commit分**を確定させる」と書くが、pseudocode上は`_seed_dangling_fk_for_negative_test_only`
自身が末尾で `conn.commit()` している (999行は既にこの時点で確定済)。∴ 229/284行のcommitが
「999行を(初めて)確定させる」わけではない——999行は**それより前に既に確定済**であり、
229/284のcommitは主にスキーマ変更分を確定させるのみ。結論 (999行が最終的にDBへ残る) は
変わらぬが、a2の説明文の「未commit分」という言い回しは厳密には不正確。

---

## ⒞ a2の挙げた新穴4点は足りておるか / 挙げられておらぬ穴

a2自身の4点 (fixture path固定 / pragma既定値依存 / 汎用fixture化伝播 / GREEN化後の手動書換え) は
いずれも妥当な指摘であり、当職の再検討でも反証は見当たらなんだ。**然れど以下2点、
a2の穴一覧にも§6「未確定」注記にも現れておらぬ欠落を発見した**。

### ★発見2: `_open_file_db` は「既存fixture流儀の流用」ではなく、同一未commit patchの新規コード★

a2 §6 pseudocodeは `_open_file_db(tmp_path / "f2_regression.db")` を呼び、コメントで
「既存fixture流儀を流用 (新規発明なし)」と明記する。然れど当職が `git diff --stat` /
`git show HEAD:...` で実測したところ:

```
git diff backend/tests/web_reservation/test_phase2_2_booking.py --stat
 → 1 file changed, 121 insertions(+)   (0 deletions=全行が新規追加)
git show HEAD:backend/tests/web_reservation/test_phase2_2_booking.py | grep _open_file_db
 → 該当なし (HEAD版=commit済版には存在せぬ)
```

`_open_file_db` は **本patch自身が新規に書いた関数** (working tree の `M` 差分121行の内)。
かつ定義箇所は `backend/tests/web_reservation/test_phase2_2_booking.py`——a2が本書冒頭で
「別枠」と明記した**項13の2 detector (旧code陽性対照) 用の同一file**である。a2は§0で
「両者を混ぜれば『已に在る物』と『新たに要る物』が見分け得なくなる」と自ら釘を刺しながら、
§6ではその項13専用fileの (アンダースコア始まり=モジュール private 命名慣習の) ヘルパを
別file (`test_booking_concurrency_root_migration.py`) へ跨いで呼ぶ設計を書いている。
pseudocode をそのまま配置先案のfileへ貼れば `NameError` (未import) で即死する。

### ★発見3: `_create_all_appointment_tables` はrepo全体を探しても実在しない★

```
grep -rn "_create_all_appointment_tables" --include=*.py .   → 0件 (repo全体)
```

a2 §6コメント「# APPOINTMENT_TABLES を loop 適用」は**意図の説明**としては正しい
(この loop パターン自体は `test_booking_rules.py`/`test_booking_validator.py` 等
10ファイル前後で現に使われている実在の慣習)。然れど `_create_all_appointment_tables`
という**関数名そのもの**は当職の全repo検索で1件もヒットせず、既存の慣習パターンを
指す変数名でも既存関数の別名でもない——**未定義の呼び出し**である。a2の§6末尾
「未確定」注記はINSERT文の省略カラム (`...`) 一点のみに触れ、この呼び出し自体が
未定義である事には触れていない。

★発見2/3は独立ではなく同根★: 配置先file (`test_booking_concurrency_root_migration.py`、
164行・当職実読済) は**既に自前のfixtureヘルパ (`_schema`/`_add`) を持ち**、`_schema()`は
`units`/`appointments`/`appointment_history`の3tableを個別DDL適用した上で
`units(unit_id=1,...)` を明示INSERTしている——これは発見1で指摘した「units未投入」問題を
副作用的に解決し得る、**まさに目の前にある既存資産**である。然れどa2の§6は
この`_schema`/`_add`を使わず、①別fileの private ヘルパ (`_open_file_db`) と
②実在せぬ関数名 (`_create_all_appointment_tables`) を新たに持ち出している。
§6「未確定」注記が「そのヘルパの中身を読み切っていない」と書く**「そのヘルパ」が
`_schema`を指すのか`_open_file_db`を指すのか自体が曖昧**であり、いずれにせよ
pseudocodeへ落とし込む段で最寄りの既存資産 (`_schema`) が採用されていない。

### §4点2 (pragma既定値依存) の「将来リスク」framingは実態より弱く書かれている

a2 §4-2は「もし将来、`_open_file_db`等が『安全側に倒す』改修で`PRAGMA foreign_keys=ON`を
既定化した場合」を**仮定の将来リスク**として書く。然れど当職が repo 全体を
`grep -rn "PRAGMA foreign_keys"` で横断したところ:

- 本番の中枢接続ヘルパ `backend/db/sqlite_connection.py:32` は**現に**
  `conn.execute("PRAGMA foreign_keys=ON;")` を無条件発行 (`backend/main.py`/
  `backend/web_reservation_server.py` 等、多数のAPI moduleがこの`get_connection()`/`get_db()`経由)。
- 既存test群でも `PRAGMA foreign_keys=ON` を接続直後に明示する箇所が**50件超**
  (`grep -c` 実測、`tests/`・`backend/tests/` 横断)。

∴ 「FK既定OFFに依存しない」設計はa2の判断として正しいが、それが防ぐ対象は
**仮定の将来変更**ではなく、**この codebase で現に多数派の慣習**である。
a2自身の対策 (INSERT直前に明示OFF) は結果として正しい選択だが、リスクの重さを
「将来もし」で書くのは実態を過小に見せる。★この点は設計を壊さぬが、記述の正確さの誤り★
として指摘する。

---

## ⒟ 三値判定 (裁定はせず、根拠のみ提示)

| 対象 | 判定 |
|---|---|
| §3の核心担保 (コード構造による「必ずRED」) | **①成る** — 当職の独立行番号再算出・不在の実測で裏付け済 |
| §2-2手順4「違反件数=必ず1件」 | **②誤りが在る** — `units`未投入により実際は2件 (発見1)。ただしpytest.raisesのRED自体は影響を受けぬ |
| §6 pseudocode の fixtureヘルパ選定 (`_open_file_db`/`_create_all_appointment_tables`) | **②誤りが在る** — 前者は別file・同一未commit patchの新規codeを「既存流用」と誤記、後者はrepo全体で未定義 (発見2/3)。そのまま実装fileへ貼れば動かぬ |
| §4「新たに開ける穴」4点の網羅性 | **②誤りが在る (漏れ)** — 発見1〜3は a2 の4点にも§6「未確定」注記にも含まれず |
| INSERT列不足・999将来衝突・OFF射程 | **①成る** — 反証見当たらず |

---

## §対に成る他工区

- `docs/incident_logs/2026-08-06_reserveimage_cycle2_f2_direct_regression_test_design_a2.md` — 本レビューの対象そのもの。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_gap_test_design_9_10_12_a4.md` §4-1 — a2が埋めた「未設計」の出所。本レビューが指摘した`units`未投入は、遡ればこの出所文書にも記載なし (当職未確認・要別途照合)。
- `docs/incident_logs/2026-08-06_reserveimage_cycle2_red_positive_control_design_a3.md` (当職自身の前工区) — 項13detectorとF2の別枠区分。発見2は、この別枠区分をa2自身が§6で部分的に破っている点の指摘でもある。

## 本工区で己が直した誤り

無し (本工区は反証役であり、a2の成果物を書き換えていない。当職自身の過去成果物への訂正も本工区では生じていない)。

## 禁則遵守の確認

走らせず (pytest等の実行=0回)。DBに触れず (`.db`ファイルの生成・接続=0回、全て`.py`ソースの読取のみ)。
`hakodoukai-dev`・`/tmp/resimg-*`系統・`newbuild`への書込=0回 (`grep -n`/`sed -n`/`git show`/`git diff --stat`/
`wc -l`による読取のみ)。rcはpipeに通していない (各コマンド単発実行・`$?`個別確認はしていないが、
いずれもエラーなく標準出力を得ており、失敗を握り潰す構成ではない)。

---
断面: 2026-08-06T10:49:51+0900 (機械)／本repo (multi-agent-shogun) base_commit=`a19cf01aa13a30389dd472deeba531c742e19db4`／
対象repo参照base (`/tmp/resimg-cycle2-impl-20260806`、読取のみ)=`7d463edae84c704edabbd9da5465078dc62e55b1` (不変・確認済)／
対象a2文書 sha256=`3b0e8754ab10112e845ec2eae50516e306451e36c205609a8613ae9eee3c0fd6`。
提出先: 家老second + 軍師second。
