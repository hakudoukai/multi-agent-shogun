# 母数食い違い (81 / 38+2) 切り分け — venv 導入前後の収集件数変化「実測し得るか」調査 足軽4号

**測時**: 2026-08-06T02:19:09+0900 (`date` 実行)
**下命**: karo-second msg_20260806_021159_02e0d616 (次⑵「母数の食い違いの切り分け＝venv導入前後で収集件数がどう変わるかを実測し得るかを調べよ。実行して環境を壊すな・調べ得ぬなら未測と書け」)
**本工区に効く条**: 「実行するな。調べ得るか否かを調べよ」
**境**: 本便は ★実測 (pytest 実行等) は一切行わず★、`ls`/`find`/`grep`/`git log`/`git show`/`git status` の読取専用コマンドのみで調査。環境への書込・状態変更は0件 (下記実行ログ全件が読取専用である事を明示)。

---

## §0 母数の出所を先ず特定

「81」の出所を確認 (己が上げた数の裏取り、憶測で答えぬ)。

```
$ cd /tmp/resimg-stage1-runtime-20260806 && git log -1 --format="%B" 7d463ed
```
→ 自 commit メッセージに「backend/tests/web_reservation/ + backend/api/web_reservation/: 79 PASS + 2 pre-existing FAIL」と記載 (79+2=81)。

**★己が直した誤り①★**: 上記 commit message の書き方は不正確であった。実測 (下記) の通り `backend/api/web_reservation/` は **test file を1件も含まぬソースdir** (router.py/auth.py/booking.py 等・`def test_` 0件) であり、「+」で並記したのは誤解を招く書き方であった。81件は **`backend/tests/web_reservation/` 単独 (6 file)** に由来する。

```
$ /usr/bin/grep -rc "def test_" backend/tests/web_reservation/*.py
test_phase2_1.py:10 / test_phase2_2_api.py:15 / test_phase2_2_auth.py:24 /
test_phase2_2_booking.py:25 / test_twilio_sender.py:7 / __init__.py:0
合計 = 81 (10+15+24+25+7)

$ /usr/bin/grep -rc "def test_" backend/api/web_reservation/*.py
全 file 0件 (router.py/auth.py/booking.py/health.py/dependencies.py/__init__.py)
```

**∴ 81 は grep による静的関数定義数であり、venv の有無に一切依存せぬ** (grep は python を実行せず、file を文字列として読むのみ)。

---

## §1 venv 導入前後の「収集」を実測し得るか — 二層に分けて調ぶ

問いを分解: 「収集」が①**静的 (grep等)** か②**動的 (pytest --collect-only 等の python 実行)** かで答えが異なる。

### 1-1. 静的収集 (grep) — venv 非依存・既に実測済 (本便§0)

grep は python interpreter を呼ばぬゆえ、venv の有無・version に一切影響されぬ。**この意味では「導入前後で変わるか」の問い自体が成立せぬ (変わり得ぬ、が構造的に確定)**。

### 1-2. 動的収集 (pytest --collect-only 相当) — venv 前後で差が「生じ得る」構造的根拠を実測 (実行はせず)

**venv 側 (`/tmp/resimg-stage1-runtime-venv`) の主要 package バージョン**:
```
$ ls /tmp/resimg-stage1-runtime-venv/lib/python3.12/site-packages | grep -iE "dist-info$" | grep -iE "fastapi|pytest-|pydantic-|httpx"
fastapi-0.141.1.dist-info / httpx-0.28.1.dist-info / pydantic-2.13.4.dist-info / pytest-9.1.1.dist-info
```

**system (venv 不使用時に到達し得る `~/.local`) 側の同 package バージョン**:
```
$ ls $HOME/.local/lib/python3.12/site-packages | grep -iE "dist-info$" | grep -iE "fastapi|pytest-|pydantic-|httpx"
fastapi-0.136.1.dist-info / httpx-0.28.1.dist-info / pydantic-2.13.4.dist-info / pytest-9.0.3.dist-info
```

| package | venv | system (~/.local) | 一致? |
|---|---|---|---|
| fastapi | 0.141.1 | 0.136.1 | ★不一致★ |
| pytest | 9.1.1 | 9.0.3 | ★不一致★ |
| httpx | 0.28.1 | 0.28.1 | 一致 |
| pydantic | 2.13.4 | 2.13.4 | 一致 |

**sqlalchemy**: venv・system 両方とも site-packages 直下に見当たらず (`ls | grep -i sqlalchemy` 両者 0件・DB 層の実装方式は本調査の範囲外ゆえ未確認)。

**∴ venv と system で fastapi/pytest の version が現に異なる (静的事実・実行不要で確認済)。これは「動的収集 (import を伴う pytest collection) が環境により異なり得る」構造的根拠であるが、★実際に収集件数が変わるか否かは pytest --collect-only を両環境で走らせて初めて判る★ — 本工区はこれを禁じておる (「実行するな」)。**

---

## §2 「38+2」との対応関係 — 推測の域を出ぬ点を明示 (裁定はせぬ)

81 (10+15+24+25+7) の部分和で 38 に一致する組合せは file 単位では確認できず (試算: 24+10+... 等いずれも非整合)。**∴ 「本部長殿の38+2が具体的にどの file/どの環境実行に由来するか」は本調査からは特定し得申さぬ (未測)**。これは裁定に踏み込む領域ゆえ、本工区の範囲外として扱う。

---

## §3 「実測し得るか」への回答 (下命への直答)

| 収集の種別 | 実測し得るか | 根拠 |
|---|---|---|
| 静的 (grep による `def test_` 数) | **可・既に実測済 (§0)** | venv 非依存が構造的に確定。81 は再現可能な事実。 |
| 動的 (pytest --collect-only 等の実行による収集件数) | **方法としては存在 (読取専用・DB書込等を伴わぬ)。ただし本工区では実行禁ゆえ未実施＝未測** | venv/system 間で fastapi・pytest の version 差 (§1-2) を実測済であり、動的収集が環境により変わり得る構造的根拠は在る。実際の差分値は次段で明示 GO あれば即実測可能な状態まで環境調査済 (venv path / system site-packages path / 対象 file 群 悉く特定済)。 |
| venv 導入「前」の履歴収集記録 | **無し (未測)** | venv (`/tmp/resimg-stage1-runtime-venv`) は 01:01 作成・当職の着手 (01:14:35) より前に既に存在。本 clone 内に venv 導入前の pytest 実行記録は残っておらぬ (git log 3 commit のみ・いずれも venv 作成後)。 |

**結論**: 「調べ得るか否か」への答=★条件付きで可★。静的収集は既に実測済 (venv非依存と確定)。動的収集は「実行すれば測れる」ところまで環境面の下調べ (venv/system の package version 差) を完了したが、★本工区の境界 (実行するな) により実測そのものは行っておらぬ★。venv 導入「前」の履歴比較は記録が存在せず不可能 (未測)。

---

## §4 己が直した誤り (欄・空欄不可)

**誤り①**: §0 に記載。commit message で「backend/tests/web_reservation/ + backend/api/web_reservation/」と2 dir 並記したが、後者は test を含まぬソース dir であり、81 は前者単独の数であった。次任が同 commit message を「2 dir 合算値」と誤読せぬよう本便で訂正。

---

## §5 境界・実行記録の総括 (「環境を壊しておらぬ」ことの証)

本工区中に実行したコマンドは悉く読取専用: `date` / `cd` / `git log` / `git show --stat` / `git status --short` / `ls` / `find` / `/usr/bin/grep`。**pip/pytest/python -c import 等、python interpreter を起動するコマンドは一切実行せず** (§1-2 の package version 確認も `ls` による dist-info dir 名の読取のみで達成)。DB (`dentalbi_local.db`) への接続・書込は0件。

---

## §6 完了規準 (self-check)

- [x] 実行するな (python/pytest/pip 系コマンド 0件・全て読取専用)
- [x] 調べ得るか否かの回答 (§3 表・可否を分けて明示)
- [x] 未測は「未測」と明記 (§2 / §3 最終行)
- [x] 咎めるな・裁定せぬ (§2 で明示的に裁定を回避)
- [x] 丸めた数と誤った数を分けて記載 (§1 は「実測」・§2 は「未測・推測の域を出ぬ」と明記)
- [x] 己が数に添えた語を検め (「実測」= 本便中で己が打ったコマンドの結果のみに使用。§2 は「未測」と明記し「実測」を僭称せず)
- [x] 己が直した誤り欄 (§4・空欄不可)

---
report path: docs/incident_logs/2026-08-06_venv_collection_count_feasibility_a4.md
