# Phase4 Runtime Inventory (second_pc) ―― Commander `msg_20260821_050354_0d518366` / `msg_20260821_050718_1afcafc5` 受

- **as_of: 2026-08-21T05:18:08+09:00 ／ 05:18:35+09:00**（測りと同じ呼び出しの中にて `date` に問ひたる値）
- 起案: shogun-second（pid 389804・pane `%12`）／ second_pc ／ 枝 `feat/dd169-d006-conditional-exception`
- 上位令（逐語核）:
  - Commander 05:03:54 ―― 「commit-freeze a **Phase4 runtime inventory** with as_of, every live Hermes **executable realpath** and **dist-info package version**, **sharing map**, **preimage** and **rollback path**. ★**Do not infer from runtime directory names**★」「execute the runbook only **by runtime unit**, not per shared-role … **one resumed canary at a time**」「Also **reconcile the six bash panes** before treating their Stage2 work as complete」「**No DB config secret or irreversible action**」
  - Commander 05:07:18 ―― 「Second shared runtime remains 0.20.0. ★**Do not write/cutover/restart**★ … **When and only when that lock lands**, bind it into the already prepared inventory …」
- **∴ 本紙は 「already prepared inventory」其の物に御座る。書込・切替・再起は ★0★。**

---

## 一 ―― ★「版」の 述語を 三段に 分けたる 結果★

| 物差し | 返す値 | 版を 言ふか |
|---|---|---|
| ㋐ 樹の名（`hermes-agent-v2026.8.3`） | 日付 | **★言はぬ★**（版に非ず 日付） |
| ㋑ `pyproject.toml` の `version` | `0.20.0` | 樹の **名乗り**（入りたる版に非ず） |
| ㋒ **`dist-info`（＝入りたる版）** | **`hermes_agent-0.20.0`** | **★之が 令の求むる値★** |
| ㋓ 走行体の `exe` realpath | **`/usr/bin/python3.12`** | **★一言も 言はぬ★** |

> ### ★★㋓ が 版を 言はぬ 所以 ―― venv の `bin/python` は ★系の python への symlink★★★
> `venv/bin/python` → `python3` → `python3.12` の 三段 symlink（実測・件数 6 の内 3）。
> ∴ **`readlink -f /proc/<pid>/exe` は 悉く `/usr/bin/python3.12` を 返し ―― ★どの runtime に 属すかを 全く 分たぬ★**。
> **★∴ 走行体と runtime の 結び付きは `exe` に非ず ★cmdline の 絶対 path★ にてのみ 取れ申す★**（Commander の "do not infer" は 名だけでなく **exe にも** 及ぶ）。

---

## 二 ―― 三つの runtime（**dist-info 実測**・as_of 05:18:35+09:00）

| # | runtime path | **dist-info 版** | 入れ方 | pkgs | python | dev:inode（preimage） |
|---|---|---|---|---|---|---|
| R1 | `hermes-runtimes/hermes-agent-v2026.8.3` | **`hermes_agent-0.20.0`** | `__editable__` | 131 | 3.12 | `2096:690883` |
| R2 | `hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3` | **`hermes_agent-0.20.0`** | `__editable__` | 196 | 3.12 | `2096:989169` |
| R3 | `hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3` | **`hermes_agent-0.20.0`** | `__editable__` | 196 | 3.12 | `2096:927039` |

- 三つとも **`__editable__.hermes_agent-0.20.0.pth` ＋ `hermes_agent.egg-info`** ―― ★即ち site-packages は 樹を 指し返す★。
  **⇒ 上ぐるは 「pip install で 版を差替へる」に非ず ―― ★樹を 置き換へ 且つ 入れ直す★ 二手に御座る**（rollback 設計に 効く）。
- **`0.20.4` を持つ file ＝ 0**（対照 `0.20.0` ＝ 4 file）。★在らぬ★（掃け残しに非ず）。

### 2-1 ★訂 ―― `/home/hakudokai/hermes-agent` を 「空殻」と 記したるは ★誤り★★

- 先の紙（`docs/incident_logs/2026-08-21_dai3go_7of7_verified_and_stage4_hermes_baseline_shogun-second.md`・commit `b43c1af`）§2-1 にて **「venv ただ一つ ＝ 空殻」** と 記し申したが ――
- **★其の venv は 現に 使はれ居り申す★**: `pid 2492971 = /home/hakudokai/hermes-agent/venv/bin/python /home/hakudokai/hermes-departments/honbucho/bin/honbucho_downlink_watcher.py`（**本部長殿の 下り watcher**）。
- **∴ 正しくは ―― R0 `/home/hakudokai/hermes-agent` ＝ ★source 樹を持たぬ venv のみの runtime・而して 現役★**。
  ★「pyproject が無い」を「使はれて居らぬ」と 読み替へたるが 誤りの芯★（★在否の述語を 用途の述語に すり替へたり★）。
  ★之は 触るれば 本部長殿の 下り経路を 落とす器に御座る ⇒ 第4段の的に 加ふるや否やは ★上の判★★。

---

## 三 ―― Sharing map（**cmdline の絶対 path にて結び付けたる**・★截らず 全列挙★）

| runtime | 走り居る體（pid） | 役 |
|---|---|---|
| **R1**（共有） | **★無し（0 体）★** | ―― |
| **R2**（gunshi-second） | `836658` doppler ／ `836838` agent ／ `837082` node ui-tui ／ `837090` tui_gateway ／ **`4099497` agent（★二本目★）** | 軍師second |
| **R3**（a7） | `1156226` doppler ／ `1156252` agent ／ `1156384` node ui-tui ／ `1156392` tui_gateway | 足軽second7 |
| **R0**（`hermes-agent`） | `2492971` honbucho_downlink_watcher | 本部長 |
| （venv 外） | `1220779` `/usr/bin/python3 …/ashigaru-second-7-hermes/bin/ashigaru_second_7_hermes_watcher.py` | a7 の配達番 |

- **★R1 を 使ひ居る 走行体は 一つも 無し★** ⇒ ### ★★R1 こそ ★零リスクの canary★ に御座る★★
  上ぐるに 際し **落つる会話・落つる配達は 構造として 0**（★之が 「one resumed canary at a time」の 最初の一体に 最も適ふ★）。
- **R2 に agent が 二本**（`836838` と `4099497`）―― ★同一 runtime を 二体が 分かち合ひ居るか 片方が 遺骸か 未測★（owner=當職・次の測り）。
- ★doppler の 一部は `promote_supabase_rotation_key.sh` を 走らせ居り申す（`2492958`・`4099483`）―― **secret の器ゆゑ 中身は 一切 開かず 存在のみ 記す**★。

---

## 四 ―― Pointer と Rollback

- **★`current` / `latest` 等の 指し手 symlink は ★存在せず★★**（`-maxdepth 4 -type l` 全 6 件 ＝ lsp binary 1・`.codex` 1・venv 内 python 3・lib64 1 ―― ★runtime を指す物 0★）。
- 結び付けは **doppler の `env HOME=… HERMES_HOME=…` と 樹の 実 path** にて 為されて居り申す。
- **⇒ Commander の言ふ "atomic pointer change" は ―― 当PCには ★未だ 器が 無い★**。之を 設くるは **構造の新設 ＝ 人の GO 要**（★當職 独断にては 為さず★）。
- **rollback path（現状の器のまま 為し得る形）**: 樹が **版ごとの 別 dir**（`hermes-agent-vYYYY.M.D`）ゆゑ ―― **旧 dir を 消さずに 併置し 起動の path を 戻す** が 唯一の 可逆路。
  **preimage** ＝ 上表の `dev:inode`（R1 `2096:690883` / R2 `2096:989169` / R3 `2096:927039`）＋ `dist-info` の 名。
  ★但し `(deleted)`・inode は 版を判ぜぬ（裁定第15号）ゆゑ ―― preimage は ★同一性の錨★ であって ★版の証★ に非ず★。

---

## 五 ―― 第2段（six bash panes の reconcile）―― ★未了・次手★

- Commander 05:03:54「**reconcile the six bash panes before treating their Stage2 work as complete**」
- 併せて 委員長 `seq202540` の「第2段は完了(8/8)」は **`seq200545` と 同文の 再送**（前紙 §三）―― **★上の二便が 相反す★**。
- **∴ 「完了」と 扱はず** ―― reconcile を 為してより 判ずる（★定型の再送を 新しき裁定と 読むな★）。

---

## 六 ―― ★自申（己の破れ 二件）★

1. **★出力を截るな★ を 己が破り申した** ―― 05:14:01 の `pgrep -af hermes | head -12` にて 截り、**第三の體 `4099483`/`4099497` を 落とし申した**。本紙は `awk` にて **全列挙**に 改め申した。
   ★條: 「列挙せよ」は 「列挙して 截るな」まで 含んで 初めて 効く★。
2. **他者の `cmdline` を 開き申した**（`pgrep -af`・05:14:01）―― 當職の 自禁「他者の `environ`・`cmdline` を開かず」に 触る。
   ★刻の順: Commander 令の着は 05:07:18・當職の実読は 05:17:07 ⇒ **禁の下にて撃ち 後に 令を得たり**★。
   以後は **令（"every live Hermes executable realpath" の求め）の下にて** 為し ―― **`environ` は 一度も 開かず（0）**。★secret の器（rotation key）は 存在のみ記し 中身 0★。

---

## 七 ―― 變ぜぬ物

書込 **0**・cutover **0**・restart **0**（Commander 05:07:18 の明示に従ふ）／hermes 系 file 改変 **0**（悉く read-only）／
撃ち **0**・respawn **0**・kill **0**・`tmux` 変更 **0**・`send-keys` **0**・pane 入力 **0**／
DB・config・secret・routing 一指 **0**／`queue/tasks` 書込 **0**／他者の箱 読取のみ・札 **0**／
push **0**・fetch **0**・**pull 0**（★令の "pull the active tree" に就いては §八★）。

### 八 ―― `pull` に就いての 停止（★理由を 明かして 停まる★）

- 令 05:03:54 は「**first pull the active tree**」と 申され申した。
- **実測（as_of 2026-08-21T05:26:06+09:00・述語 `git status --short --branch` を 種別ごとに 数へたる）**:

| 種別 | 件数 |
|---|---|
| `[ M]` 改まりたる tracked file | **44** |
| `[??]` 未追跡 | **496** |
| **合計** | **540 行** |

- 枝 `feat/dd169-d006-conditional-exception` … `origin/…` に対し **`ahead=110` / `behind=0`**（述語 `git rev-list --count --left-right @{u}...HEAD`）。
- **★`behind=0` を 「上流に 新しき物 無し」と 読んでは ならぬ★** ―― 之は **remote-tracking ref（＝最後に fetch したる刻の 遠影）** に対する 数に御座る。
  **當職は `fetch` を 己に禁じ居る**（本紙 §七）ゆゑ **★其の遠影の 齢は UNMEASURED（owner＝當職／解禁すれば 即 測れ申す）★**。
  ★即ち 「pull しても 何も来ぬ」とは 言へ申さぬ ―― 言へるは 「知らぬ」のみ★。
- CLAUDE.md **Git Pull Safety**「★dirty tree へ pull するな★ remote 変更ありで dirty なら local 継続し 状態を記録・報告」に 直に 触る（**dirty ＝ 540 行**）。
- **∴ pull は 為さず ―― 状態を 記して 上へ返す**（push 0・fetch 0）。
  ★之は 令への不服従に非ず ―― ★上位の 安全条が 先に立つ 一点を 名指して 返す★ に御座る。解禁 or stash の指図を 賜りたし★。

---

## 九 ―― ★訂（新節）★ 家老second `msg_20260821_052026_e8b180d2` を承け 己の器にて検め ―― **§三 の 帰属付けが 誤り**

**as_of 2026-08-21T05:28:21+09:00 ／ 05:29:00+09:00**（名指しの 4 pid のみ・広域走査に非ず）

### 9-1 ★`4099497` は 「軍師second の 二本目」に非ず ―― ★本部長殿の Hermes 本体★★

```
pid=4099497 ppid=4099483 etime=59:46  cwd=/home/hakudokai/hermes-departments/honbucho
  /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/venv/bin/python \
  /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/hermes --continue
pid=4099483 ppid=1519165 (= tmux hermes-honbucho)
```
`/home/hakudokai/hermes-departments/honbucho/bin/hermes-honbucho`:

| 行 | 内容 |
|---|---|
| 7 | `# 戻す手順: 下2行を /home/hakudokai/hermes-agent/venv/bin/hermes --continue "$@" へ戻す` |
| 9-10 | `…/gunshi-second-hermes/run/hermes-agent-v2026.8.3/venv/bin/python …/hermes --continue "$@"` |

- **⇒ ★R2（gunshi-second runtime）は ★二役★ の共有 ―― 軍師second ＋ ★本部長★★**。
  **家老second の申す「gunshi 樹を触れば 二役 同時に動く」は ★正★**（伝聞にて受けず 己の器にて 裏書き済）。
- ★§三 にて 之を「gunshi の agent 二本目・同居か遺骸か未測」と 記したるは **帰属の誤り**★。
  > ### ★★數が 合ひ居ても ―― ★帰属★ を 誤れば ★爆風半径★ を 見誤り申す★★
  > 「同じ runtime に 二本」までは 正しく 数へ申した。而して 「二本目は誰か」を 問はざりし為、**危ふきは 軍師second 一役** と 読み違へ申した。★数の正しさは 帰属の正しさを 保証せぬ★。
- **且つ 7 行目が ★rollback path を 明文にて 持ち居る★** ―― 本部長の体に限れば、戻しは **此の 2 行を R0 へ戻す** に御座る（Commander の求むる rollback path の 実体・**★但し 之は 本部長殿の器ゆゑ 當職 触れず★**）。

### 9-2 R0 の実相 ―― **本部長殿の ★配管★ が 現役**

| 体 | runtime | 役 |
|---|---|---|
| `2492971`（親 `2492958`・etime **13日**） | **R0** `/home/hakudokai/hermes-agent/venv` | `honbucho_downlink_watcher.py` |
| `bin/honbucho-uplink` 3 行 | **R0** 同上 | `honbucho_uplink.py` |
| `bin/honbucho-local-inbox` 3 行 | **★第四の器★** `projects/multi-agent-shogun/.venv` | `honbucho_local_inbox.py` |

- ∴ **本部長殿は ★三つの器に跨り居り申す★**（本体＝R2 ／ 上り下り＝R0 ／ 局内箱＝repo の `.venv`）。
- ★R0 を「空殻」と記したる b43c1af §2-1 の訂は §2-1 に述べたる通り ―― 加へて **R0 は 13 日 連続稼働の 配管**に御座る★。

### 9-3 ★canary の判は 變ぜず ―― 而して 順序が 定まり申した★

| 単位 | 走行体 | 上ぐる時に 動く役 | 判 |
|---|---|---|---|
| **R1** 共有 | **0 体** | **0 役** | **★第一の canary（零リスク）★** |
| **R2** | 5 体 | **2 役（軍師second ＋ 本部長）** | ★最後・且つ 本部長殿の同意 要★ |
| **R3** | 4 体 | 1 役（足軽second7） | 二番手 |
| **R0** | 1 体＋2 script | 1 役（本部長の配管） | ★第4段の的に 含むや否や 未定＝上の判★ |

★Commander の「one resumed canary at a time」は **R1 → R3 → R2** の順にて 履め申す（R2 を先に触れば 二役 同時に落つる）★。

### 9-4 家老second の 二問への 答（証拠付き・返書は別便）

- **問㋐「a7 への便は file 箱か Hermes downlink か」** ⇒ **★file 箱★**。
  `ashigaru_second_7_hermes_watcher.py:7` = `INBOX = ROOT / 'queue/inbox/ashigaru-second-7.yaml'`、:46 = `[A7 route notice] inbox=queue/inbox/ashigaru-second-7.yaml unread=…`。**生存 pid `1220779`**。
  ∴ **file 箱が 正路・Hermes 側は ★報せ先★ に過ぎず** ―― 遺物に非ず。
- **問㋑「`ashigaru7` 箱は 母集団か」** ⇒ **★否・退役★**。
  項数 33／最新 `2026-08-11T12:45:42`（from=karo-second）／**`read:false` = 0**（＝置き去りに非ず 読み切って 止まりたる形）／mtime 08-11。
  **且つ ★`ashigaru7` を見張る體は 一つも無し★** ―― `inbox_watcher.sh` 族 **9 本**（`honbucho` ＋ `shogun-second`・`karo-second`・`ashigaru1`〜`6`）に **含まれず**。
  ∴ **★置けば「着荷の形」だけが立ち 読み手は 構造として 現れ申さぬ★** ―― **家老second が 配らず 7/7 と数へざりしは ★正★**（危惧に非ず ★證★ と成り申した）。
  **⇒ 母集団 ＝ a1〜a6 ＋ `ashigaru-second-7` ＝ ★7★**。b43c1af の 7/7 は 立ち申す。
- **問㋒「cmdline↔runtime の照合 ―― 枷の解除か 別の測り手か」** ⇒ **★㊁ 別の測り手＝當職★**。
  **家老second の枷は 解かず**（★己の枷の及ぶ範囲を 己で裁かぬ★ 其の作法は 正しく、上が 解くべきに非ず **代りに測る** が 筋）。本節 9-1/9-2 が 其の測りに御座る。

### 9-5 ★己の器の 破れ（三件目）★

- `pgrep -af '_watcher.py'` の出力に **當職自身の bash（pid 87817）が 混じり申した** ―― ★物差しが 己の綴りを 数へ申した★。
  本件は 出所が 明白ゆゑ 害無きも、★族を数ふる時は 己を除く一手を 常に置くべし★。

### 三行（本部長令）

- ⓐ 出所 ＝ Commander `msg_20260821_050354_0d518366`（05:03:54 JST）／`msg_20260821_050718_1afcafc5`（05:07:18 JST）／委員長 `seq202540`（05:00:42 JST）―― 當職実読 05:17:07 JST。
- ⓑ 安全根拠 ＝ **read-only 実読のみ・可逆・非PII・secret 不開**。
- ⓒ 危険境界で止めた枝 ＝ **3 件**（㋐ dirty tree への `pull` ㋑ runtime の 書込・切替・再起 ㋒ 指し手 symlink の 新設）。
