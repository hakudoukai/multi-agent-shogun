# 第4段 ― Hermes 全12体 0.20.4 化 / 検収の**基線**（家老second / 委員長令 seq200550 受）

- **as_of: 2026-08-20T05:23:23 JST**（本紙の全数値は此の一断面）
- host: second_pc / repo: `/home/hakudokai/projects/multi-agent-shogun`
- 親令: pc_handshake **seq200550**（iincho → karo-second, 2026-08-20T05:01:01 JST・当職 `sb read seq 200550` にて直読）
  「★貴殿の持ち分★: 第4段の検収。第2段は完了(OLD=0)。裁定第9号のcopy実行を配下へ配られたい」
- 本紙の性格: **読取のみ**。restart 0 ／ kill 0 ／ install・pip・npm 一指 0 ／ tmux 一指 0（capture すら 0）／ pane 入力 0 ／ Hermes 体への**書込 0**。
- **新条の適用**（seq200550 逐語「検証させる物は先にcommit(freeze)しas_ofを併記せよ」）⇒ **本紙は復命より先に commit して凍らす**。

---

## 一 検収の述語

| # | 問 | 器 | 合格 |
|---|---|---|---|
| ㊀ | runtime の版 | `run/<runtime>/pyproject.toml` の `version =` | **0.20.4** |
| ㊁ | 走行体が其の runtime を掴み居るか | `/proc/<PID>/cmdline` の path | 版を測った path と**同一** |
| ㊂ | 入替の刻 | `pyproject.toml` の mtime | 第4段の執行後の刻 |

**注**: `hermes-agent-v2026.8.3` は**ディレクトリ名**にて版に非ず。**版は `pyproject.toml` の `version`**。ディレクトリ名で版を判ずれば**偽の緑**と成る。

---

## 二 実測（as_of 2026-08-20T05:23:23 JST）

| 体 | runtime path | ㊀version | pyproject mtime | ㊁走行 PID |
|---|---|---|---|---|
| `ashigaru-second-7-hermes` | `~/hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3` | **0.20.0** | 2026-08-07T10:04:22 JST | 1156252 |
| `gunshi-second-hermes` | `~/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3` | **0.20.0** | 2026-08-07T10:04:22 JST | 836838 ／ 4178443 |

- 走行 PID の掴む path は**測った path と一致**（㊁PASS）。
- **PID 4178443 は 2026-08-20T05:09:32 JST 起動**（第4段の窓の内）。**然れど掴む runtime は同じ 0.20.0** ⇒ **版は上がり居らぬ**。★process が新しき事を「版が上がった」と読むな★。

### 判定
- **second_pc 分 ＝ 0/2 PASS**（目標 0.20.4 に対し 両体 0.20.0）⇒ **第4段 未了**。
- 之は**瑕の申告に非ず**。05:00 JST 再開直後の**基線**にて、執行前の断面に御座る。

---

## 三 UNMEASURED（隠さず札す）

- **`hermes-honbucho`**（PID 1519165 / `~/hermes-departments/honbucho/bin/hermes-honbucho`）― `find -maxdepth 3` にて `pyproject.toml` **見当らず** ⇒ **版 UNMEASURED**。深掘りは**機構owner（本部長殿）の領分**ゆゑ**踏み込まず**。
- **全12体の同定** ― 当職の器より見ゆるは **second_pc の 2体（＋本部長体1）**のみ。**残りは他 PC** に在り、当職の測りの外 ⇒ **UNMEASURED**。「12体」の名簿は**上位より賜りたし**。
- `/home/hakudokai/hermes-agent/` は **venv のみ**（pyproject 無）― 本部長 downlink watcher（PID 2492971）が掴む python の出所にて、**役の runtime に非ず**と見ゆ。★推★ と札す。

---

## 四 併せて為したる事（seq200550 の他の持ち分）

- **裁定第9号（seq200280・2026-08-20T02:22:33 JST）の copy 実行 ―― 配下へ配布済**。
  足軽second 1〜6 の箱へ 2026-08-20T05:22:20〜21 JST 着荷・**6/6**・各 1,137字・本文 sha256先頭 **`4ea43dcb1aea`** 悉く一致（**相手の器を parse して実証**・rc に拠らず）。
  併せて**新条（commit freeze ＋ as_of 併記）も同便にて逐語配布**。
- **正本紙 `reports/IINCHO-RULING-9-patient-word-durable-copy-20260820.md`（sha16 `2348ad3d6aadd804`）は当PCの樹に無し**（`find` 0件・2026-08-20T05:21:03 JST 実測）⇒ **当職の sha 検算 0・UNMEASURED**。逐語は DB seq200280 本文より直に引き申した。
- **第2段「OLD=0」** ― 当職の独立検収（`2026-08-20_kenshu_karo2.md`・sha256先頭 `a2c5b692490a`）の **PASS 7/7** と**齟齬無し**。

---

## 五 ★併せて実測 ―― 「第2段 完了(OLD=0)」は**既に腐り居る**★（as_of 2026-08-20T05:28:57 JST）

seq200550 に「第2段は完了(OLD=0)」と賜り、当職の 02:09 断面の検収（PASS 7/7）とも齟齬無し。**然れど其の後に事が起き申した**。

| 断面 | ディスク実体 | 走行体の掴む物 | OLD |
|---|---|---|---|
| 2026-08-20T02:10 JST | 330,946,864 B ／ **2.1.235** | 同左（deleted 消ゆ） | **0/8** |
| 2026-08-20T05:28:57 JST | **334,645,552 B ／ 2.1.236**（mtime **2026-08-20T05:10:19 JST**・sha256先頭 `6c8818fa22187aa5`） | 330,946,864 B ／ **`(deleted)`** | **★8/8★** |

**当職の器にて 8 体悉く実測**（`readlink /proc/<PID>/exe` ＋ `maps` の deleted 行数 ＝ 各 5）:
3655376／3657843／3658974／3660072／3660796／3661563／**3662641（当職自身）**／**3686358（将軍second・2026-08-20T02:10:09 JST 起動＝申し置き通り自ら落ちて戻り申した体）**。

- **⇒ 02:10 JST 断面の「8/8 NEW」は真に御座った**。将軍second も予告通り戻り、**其の刻は確かに OLD=0**。
- **⇒ 而して 2026-08-20T05:10:19 JST に 2.1.236 が入り、走行 8 体の実体を悉く orphan と致し申した**。**新版導入が再起動を追ひ越した**形。
- **之は誰の瑕にも非ず。「合格線が動いた」のみ**に御座る。

### ★当職の測り得ぬ一問（上位の裁を乞ふ）★
**第2段の合格線は 2.1.235 か、2.1.236 か。**
- **2.1.235 が線** ⇒ 第2段は**完了のまま**。本節は「次に版が上がる迄の間、走行体は一世代古い」旨の**記録**に留まる。
- **2.1.236 が線** ⇒ **第2段は未了へ戻り、8 体の再起動が要る**（当職自身を含む）。
★当職は restart 権を持たず・自ら判ぜず★。**執行は将軍secondレーンの職掌**にて、当職は**測りて札すのみ**（restart 0 ／ kill 0 ／ install 0 は下記の通り堅持）。

---

## 六 変ぜぬ物

restart 0 ／ kill 0 ／ tmux 一指 0 ／ send-keys 0 ／ capture-pane 0 ／ install・pip・npm 一指 0 ／ Hermes 体への書込 0 ／ a7 pane 不触 ／ 本部長 pane 不触 ／ 軍師second 直送 0 ／ secret 値 読取 0（env は開かず）／ 他 PC へ SSH 0 ／ DB mutation は本件の復命のみ ／ queue/tasks 書込 0 ／ 新規task起票 0 ／ 他者の箱 札 0 ／ 広域走査 0（DB は**単一 seq 名指し**のみ）／ push 0。
