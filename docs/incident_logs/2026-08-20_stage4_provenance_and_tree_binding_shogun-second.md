# 第4段 ―― ★0.20.4 の source provenance は second_pc に已に在る★ ＋ 役↔樹の結び目は何処に在るか

- **as_of: 2026-08-20T09:02 JST**／起案 shogun-second (pid 389804)／second_pc／**read-only・変更 0・network 0・install 0**
- 契機: ㊀ 委員長 **seq200891**（08:57:21・parent 200884）「a7樹先→gunshi樹後 を★承認★。★但し★本部長200887 の★provenance blocker★(source commit/tag+lock 未到達)が解けるまで★実行するな★。ABI差(third=py3.11/second=py3.12)ゆゑ★copy/rsync不可★。★source探索は委員長が引き取る★」／㊁ 家老second `msg_20260820_085625_dca6b88f` ㊂「★将来 別の樹から起こされ得るか★は設計の紙も実体の紙も測って居らぬ」
- **本紙は実行に非ず。委員長が引き取られた探索へ、当職の器に在る物を差し出す物**。restart/cutover/install/fetch **悉く 0**。

---

## 一 ★provenance ―― 求むる物は second_pc の樹の中に已に在り申した★

**在処**: `/home/hakudokai/hermes-runtimes/hermes-agent-v2026.8.3/.git`（★第四の樹★。役は誰も走らせて居らぬ **install の元**）

| 求むる物 | 実測値 |
|---|---|
| source repo | `https://github.com/NousResearch/hermes-agent.git` |
| **source commit（0.20.4）** | **`6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f`** ＝ ローカルの `origin/main` ref |
| 其の commit の刻 | 2026-08-19T11:03:01-05:00 ／ subject `fix(tui): allow the ESC byte in the SGR param matcher` |
| **版（其の ref の `pyproject.toml`）** | **`version = "0.20.4"`** ★目標と一致★ |
| **lock** | **`uv.lock` 在り**（同 ref）。`name = "hermes-agent" / version = "0.20.4" / source = { editable = "." }` |
| tag | ★0 本★（`git tag` ＝ 0）⇒ **tag では指せぬ・commit で指せ** |
| `.python-version` | **3.11** ／ `requires-python = ">=3.11,<3.14"` |

**★network 0 の証★**: 先に `remote.origin.promisor` / `partialclonefilter` を引き**空**（＝ partial clone に非ず）と確かめてより読んだ。∴ `git log` / `show` / `ls-tree` は**悉くローカル object** を読んだのみ。**fetch は打って居らぬ**。

### 之が blocker に効く筋

- **「source commit+lock 未到達」は second_pc では ★到達済★**。三の PC から運ぶ必要が無い。
- **ABI 差は「運ぶな」の理由であって「second で作れぬ」の理由に非ず** ―― `requires-python = ">=3.11,<3.14"` ゆゑ **second の py3.12.3 は許容の内**（`.python-version` の 3.11 は repo の既定 pin であって上限に非ず）。⇒ **copy/rsync ではなく、second にて uv.lock 準拠で建てる**筋が立つ。

### ★併し 素直に checkout してはならぬ（当職が見た罠）★

当該樹の **HEAD は `0957277f2f468bac22bbfcfa7c43029858c9597e`（0.20.0）** にして、**`origin/main` に対し ahead 1 / behind 1**。
ahead の一つ ＝ **`refactor(skills): move polymarket to optional-skills/finance`（2026-08-06）** ―― ★origin に無い、此の PC 固有の commit★。
**素な checkout / reset は之を落とす。** 落として可か・積み直すかは **委員長／本部長の裁**であり、当職は測るのみ。

**猶 UNMEASURED**: ローカルの `origin/main` が GitHub の現在と一致するか ―― **fetch を要すゆゑ測らず（network 0 を守る）**。∴ 上の commit は「**此の PC が最後に取り込んだ origin/main**」であって「**GitHub の今**」ではない。

---

## 二 家老second ㊂ への答 ―― ★将来 別の樹から起こされ得るか★

**答: ★得る。而して其の結び目は「切替器」ではなく ★3 枚の launcher の本文★ に在る。**

| 測った物 | 実測 |
|---|---|
| `run/hermes-agent-v2026.8.3` は symlink か | **否。実体の dir**（両役とも）⇒ ★倒す「current」札が無い★ |
| launcher の pin の形 | `RT=$ROLE_HOME/run/hermes-agent-v2026.8.3` ―― **逐語の絶対 path**。env 上書き無し (`${RT:-}` 無し)・pointer file 不読 |
| 本部長 wrapper | `~/hermes-departments/honbucho/bin/hermes-honbucho` が **gunshi 樹の python と hermes を逐語 2 行で** 指す。加へて **行7 の註が巻戻し先 `~/hermes-agent/venv` を書き残す**（＝ 委員長裁② の 0.19.0 降格路） |
| 起動の別口 | systemd user `gunshi-second-hermes.service` は **start script を呼ぶだけ**（樹を二重に指さぬ）。a7 は hermes の unit **無し**（在るは inbox watcher unit のみ）⇒ a7 の起こし手は別経路 ＝ **UNMEASURED** |

⇒ **`HERMES_HOME`（身元）と runtime の樹（実体）は独立の二軸**。本部長が其の生き証（HOME=honbucho・実体=gunshi 樹）。**構造は「役↔樹 1:1」を一切保証して居らぬ** ―― 一行書き換ふれば何処へでも向く。∴ 入替の裁は **「樹を何本置くか」ではなく「此の 3 枚を誰が如何に書き換へるか」** で書かれるべし。

### ★死んだ札を一つ見付け申した★

`~/hermes-roles/ashigaru-second-7-hermes/run/active-hermes-runtime`（81 B）は樹の path を書き持つが、**之を読む者は居らぬ**（`bin` / `hermes-departments` / `hermes-roles/*/bin` / `.local/libexec` / systemd user unit を掃いて **参照 0**）。
⇒ ★**書かれたが読まれぬ物は札であって切替器に非ず**★。**入替の手順書が「active-hermes-runtime を書き換へよ」で終はって居たら、a7 は一歩も動かぬ。**
（併せて `start-…sh.bak-continue-fix-20260813` も同じ樹を pin して居る ―― 復旧と称して .bak を戻しても樹は変はらぬが、`--continue` の条件が変はる。）

---

## 三 為さぬ事

fetch / clone / checkout / reset / pip / uv / venv 作成 / install / restart / cutover / launcher 書換 / wrapper 書換 / `active-hermes-runtime` 書換 / pane 入力 / systemctl 一指（`is-active` すら打たず） ―― **悉く 0**。
着手は **委員長の provenance 解決 ＋ release scope 明示 GO** の後。順は承認どほり **a7 樹（1役）先 → gunshi 樹（2役）後**。
