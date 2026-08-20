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

---

## 十 ―― 第2段 reconcile（Commander「six bash panes を reconcile してより Stage2 完了と扱へ」への答）

- **as_of: 2026-08-21T05:33:35 ／ 05:38:40 ／ 05:39:23 +09:00**（測りと同じ呼び出しの中の `date`）
- 上位令: **Commander `msg_20260821_050354_0d518366`** ―― *"Also reconcile the six bash panes before treating their Stage2 work as complete."*

### 10-1 ★物差しを 二度 作り直し申した★

| 版 | 述語 | 結果 |
|---|---|---|
| v1 | `pgrep -f 'cli\.js\|claude-code'` | **掬へたるは 當職自身の bash 一本のみ**（★物差しが 己の綴りを 数へ申した ―― 三度目★） |
| v2 | `stat` on `…/claude-code/cli.js` | **無音** ―― ★`cli.js` は 存在せず★（樹の実形は `bin/claude.exe` ＋ `node_modules/@anthropic-ai/claude-code-linux-x64/claude`） |
| **v3（採用）** | `pgrep -x claude` ＋ `pgrep -x node`・己の pid を 明示に除く | **claude 走行体 8 体を 悉く 掬ひ申した** |

> ### ★★綴りで 族を 括れば ―― 0 を返さず ★少なき数★ を 返し申す★★
> 且つ ★族を数ふる時は 己を除く一手を 常に置け★（本夜 三度 破れ申した）。

### 10-2 pid ↔ pane ↔ 役職（`tmux list-panes` 読取のみ・★index に非ず `pane_id` にて取る★）

| pane_id | agent_id | pane_pid | claude pid | 生誕（lstart） |
|---|---|---|---|---|
| `%20` | `ashigaru-second-1` | 1834805 | **1834813** | 2026-08-20 16:00:07 |
| `%19` | `ashigaru-second-2` | 3257012 | **3257021** | 2026-08-20 23:50:17 |
| `%18` | `ashigaru-second-3` | 1490451 | **1490460** | 2026-08-20 14:05:19 |
| `%17` | `ashigaru-second-4` | 1539218 | **1539228** | 2026-08-20 14:21:40 |
| `%16` | `ashigaru-second-5` | 1591161 | **1591170** | 2026-08-20 14:38:22 |
| `%15` | `ashigaru-second-6` | 1767393 | **1767402** | 2026-08-20 15:37:18 |
| `%13` | `karo-second` | 1659821 | **63955** | 2026-08-20 05:36:15 |
| `%12` | `shogun-second`（★當職★） | 1658558 | **389804** | 2026-08-20 07:28:37 |
| `%26` | `ashigaru-second-7` | 1156226 | ―― | ★claude に非ず Hermes 体★（node・R3 樹） |
| `%24` | `gunshi-second` | 836658 | ―― | ★Hermes 体★（R2 樹） |
| `%35` | （`@agent_id` **空**） | 4099483 | ―― | ★本部長殿の Hermes 体（R2 樹）―― 名簿札 無し★ |

- ⇒ **令の言ふ「six bash panes」＝ `%20 %19 %18 %17 %16 %15`（`ashigaru-second-1`〜`-6`）と 確定**。
  ★`ashigaru-second-7` は claude 体を持たず ―― 第2段（Claude Code 版上げ）の 母集団に 構造として 入り申さぬ★。

### 10-3 ★片道の述語★ ―― OLD は証せる・NEW は証せぬ

- 述語 ＝ `/proc/<pid>/maps` に **`(deleted)`** の mapping が有るか。
- **8 体 悉く `deleted` = 5 件**、且つ **悉く 同一の path**:
  `…/@anthropic-ai/.claude-code-wTkEzMFd/bin/claude.exe (deleted)`
  ―― ★`.claude-code-XXXXXXXX` は npm install の 一時 staging 樹★。∴ 8 体は **同一の 或る過去の install 世代**より 起ち、其の樹は **既に 消えて居る**。
- ⇒ **★8/8 悉く OLD 確★**（走り居る実体が disk に 非在 ＝ 現 disk 版と 別物）。
- ★但し 版番号までは 判ぜられ申さぬ★ ―― **裁定第15号「(deleted)/inode は 版を判ぜぬ」** が 現に効く。
  言へるは **「現 disk 版に非ず」＝ OLD** のみにて、**「2.1.236 である」とは 一言も 言へ申さぬ**。

> ### ★★物差しは 誤りを「測れず」の側へ 倒せ ―― ★片道の述語★★★
> 本述語は **OLD を証し得て NEW を証し得ぬ**。★今回は 母集団 全員が OLD 側に 倒れたるゆゑ 判が立ち申した★。
> 若し `deleted` が 0 の體が 有らば ―― 其れは NEW に非ず **UNMEASURED** と 札すが 筋に御座る。

### 10-4 ★測りの最中に 器が 動き申した★（本節 最重要）

| 刻 | disk の版 | 出所 |
|---|---|---|
| 2026-08-21T05:33:35 | **`2.1.237`** | `package.json` |
| **2026-08-21T05:38:25** | **★`2.1.238`★** | `package.json` mtime ＝ 05:38:25.456 ／ binary mtime ＝ 05:38:28.824 |

- binary: `…/claude-code-linux-x64/claude`・`size=338,860,336`・`dev:inode=2096:708762`・**`sha256(16)=0933b286cf94e1b2`**（★算法を名指す ―― 裁定第15号★）。
- **★入替の主は 當職に非ず★** ―― 當職は本夜 `npm` を **一度も** 走らせ居り申さぬ（撃ち 0）。**他者の手が 現に進行中**に御座る。
- ⇒ ★當職の断面が「古い」のではなく ―― ★母集団の側が 測りの窓の中で 変じ申した★★。

> ### ★★己の測りの窓の中で 母集団が 変じたる時 ―― ★数★ ではなく ★窓★ を 報ぜよ★★
> 「8/8 OLD」は **`05:33:35`〜`05:39:23` の窓の内にてのみ 真**に御座る。
> 且つ ★入替が 現に走り居る★ 事を 併記せねば、受け手は 之を「将軍が 古き断面を 見て居る」と 読み申す ―― ★同じ数が 逆の意味に 化ける★。

### 10-5 ★∴ `seq202540` の「第2段は完了(8/8 NEW・OLD=0)」は ―― 実測にて 覆り申した★

| 項 | 令の申す所 | **當職の実測** |
|---|---|---|
| NEW | **8** | **★0★** |
| OLD | **0** | **★8★** |

- 昨夜 當職は 之を **「`seq200545` と同文の再送 ⇒ 継承の疑ひ」** と ★推論★ にて 記し申した（本紙 §五・`b43c1af` 三）。
- **本節にて 其の推論は ★実測の證★ に 昇り申した** ―― ★疑ひ★ ではなく ★確★ に御座る。

> ### ★★定型の status 行は 古びたる偽を そのままの顔で 運ぶ ―― ★而して 之を 覆すは 論に非ず 測りに御座る★★★

### 10-6 次の安全な一手（★當職は 撃ち申さぬ★）

- 8 体を NEW（`2.1.238`）に するには **各 pane の claude を 落として 起ち上げ直す** 外に 道 無し。
- ★之は ★理事長令「process/session を独自 kill/restart せず・★未送信 composer を破壊しない★」★ に 直に 触る★。
  且つ ★死んだ／古びたる CLI の 蘇生主は ★委員長殿★★（当PCの 定め）。
- ⇒ **當職の為し得るは 本紙の freeze と 上申のみ**。**blocker 4 点**:
  - root_cause ＝ 走行体が 起動時の binary を 抱き居り、**入替は 再起動を 経ねば 効か申さぬ**（`deleted` mapping が 其の證）。
  - owner ＝ **委員長殿**（蘇生の主）／入替を 現に走らせ居る 手（★誰かは UNMEASURED・owner＝委員長殿★）。
  - next_safe_action ＝ 本紙 freeze ＋ Commander・委員長殿へ 一便ずつ。
  - human_GO_required ＝ **要**（8 体の 停止再起 ―― 内 1 体は ★當職自身★・1 体は ★家老second★）。
- ★且つ 入替が 現に 05:38 に 走りたる以上 ―― ★次の再起動を 待てば 自づと 238 に 成り申す★★。**★急ぎ撃つ理由が 無い★**。

### 10-7 ★己の破れ 二件（自申）★

- ㋐ `pgrep -x node` にて **他者の cmdline を 広く 開き申した** ―― 當職の自禁は 「cmdline は Commander 令の下にて ★名指し 4 pid のみ★」に御座った。
  本件は Commander の reconcile 令の下ゆゑ 令には 適ふが、**★範を 広げたる事 其の物を 記し置く★**（`environ` は 一度も 開かず **0**／secret 不開）。
  ★己の枷を 己で 黙って 広げるは 破れに御座る ―― 広げたるならば 其の刻に 上へ 申告せよ★。
- ㋑ `grep -c … || echo 0` が **二重に 0 を刷り申した** ―― `grep -c` は 0 件にて `rc=1` を返すゆゑ **既定枝が 発火**。
  ★`&&`＋`||` の 既定枝は ―― 「走らなんだ」時のみならず 「走って 0 を得た」時にも 発火し申す★。

### 10-8 變ぜぬ物（本節の分）

撃ち **0**（`npm` 一度も 走らせず）・respawn **0**・kill **0**・`tmux` **変更 0**（`list-panes` 読取のみ・`capture-pane` **0**・`send-keys` **0**・pane 入力 **0**）／
hermes 系 file 改変 **0**／`~/.npm-global` 配下 **読取のみ**（`stat`・`grep`・`sha256sum` のみ・書込 **0**）／
他者の `environ` **0**・secret 不開／`queue/tasks` 書込 **0**・他者の箱 読取のみ・札 **0**／push **0**・fetch **0**・pull **0**。

---

## 十一 ―― ★第4段の 母集団の 訂★ ―― R0 は **`0.19.0`** に御座り 且つ **其れを import する者が 一人も 居らぬ**（Commander 令「source/destination Python compatibility」への 前倒しの答・as_of 2026-08-21T05:56:28 / 05:56:52 / 05:57:27 +09:00）

### 11-1 ★baseline は 一様に非ず★

| runtime | **dist-info 版** | 入れ方 | python | pkgs | 樹 dev:inode |
|---|---|---|---|---|---|
| R1 共有 | `hermes_agent-0.20.0` | `__editable__` | 3.12 | 131 | `2096:690883` |
| R2 軍師second | `hermes_agent-0.20.0` | `__editable__` | 3.12 | 196 | `2096:989169` |
| R3 a7 | `hermes_agent-0.20.0` | `__editable__` | 3.12 | 196 | `2096:927039` |
| **R0 `hermes-agent`** | **★`hermes_agent-0.19.0`★** | **★editable の印 掬へず ⇒ 素の install と見ゆ★** | 3.12 | **179** | `2096:417300`（venv `2096:417374`） |

- 述語: `find $R0/venv/lib -maxdepth 3 -name 'hermes*dist-info' -o -name '__editable__*hermes*'` ⇒ ★dist-info 一件のみ・editable の印 **0 件**★。
- **★Commander 令の前提「Second shared runtime remains 0.20.0」は ―― R1/R2/R3 にて 真・★R0 にて 偽★★**。
- **python は R0〜R3 悉く `3.12`**（`venv/lib/python3.12` の dir 名＋`readlink -f venv/bin/python` ⇒ `/usr/bin/python3.12`・★実行せず 樹の形にて測る★）。
  ⇒ ★Commander 令の source/destination Python 適合は ―― python の軸にては 四つとも 同一ゆゑ 障り無し★。★障るは 版と 入れ方の軸★。

### 11-2 ★入り居る版は 走り居る版に非ず★（本節の芯）

- R0 の 走行体は ただ一つ ―― `2492971`・`etime 13-05:57`・`Fri Aug 7 23:59:48 2026` 起（本部長殿の 下り watcher）。
- **其の script（`…/honbucho/bin/honbucho_downlink_watcher.py`・290 行 13,070 B）の import は 悉く 之のみ**（`:23-25` 逐語）:
  `hashlib, json, os, pathlib, subprocess, time, traceback` ／ `requests` ／ `psycopg2, psycopg2.extras`
- **★`hermes_agent` を 一行も import せ申さぬ★**（`grep -n -i hermes` の当たりは `ROLE` path・`TARGET` tmux 名・`HERMES_RO_*` の env 名・註のみ ―― ★import に非ず★）。
- ⇒ **★R0 の `0.19.0` は 「入り居る」が 「走り居らぬ」★**。R0 の venv が 現に果たし居る役は ―― ★python 3.12 ＋ `requests` ＋ `psycopg2` の 供給者★ に過ぎ申さぬ。

> ### ★★入り居る版は 走り居る版に非ず ―― ★dist-info を数へず import を引け★★★
> `dist-info` は **配られたる事** を言ひ、**使はれ居る事** を 一言も 言ひ申さぬ。
> （★之は 已に本紙 §一 の「realpath は版を言はぬ」と 同じ形の 破れに御座る ―― ★同じ罠が 軸を替へて 三度目★★）

### 11-3 ★∴ 第4段の 的から R0 を 外すべし（案・判は 上）★

| 問 | 答 |
|---|---|
| R0 を `0.20.4` へ 上げて 得る物は | **★無し★** ―― 其の venv にて `hermes_agent` を import する者が 現に 0 |
| R0 を 触りて 失ふ虞れある物は | **★本部長殿の 13 日 走り続けたる 下り配達★**（`requests`・`psycopg2` は 其の venv に在り） |
| ⇒ 案 | **★R0 ＝ 第4段の 母集団の 外・不触★**（★判は 上に属す ―― 當職は 案のみ★） |

> ### ★★母集団を「入り居る物」にて 括れば ―― 使はれ居らぬ物まで 掃き込み ★現役の配管を 巻き添へに す★★★
> 「12 体を 0.20.4 へ」は **体（役）の数** にて括られ居り申すが、
> ★版上げが 現に効くは ★`hermes_agent` を import する体★ のみ★。
> ★∴ 的は 「入り居る runtime」に非ず ―― ★「import する体」★ にて 括るべし★。

### 11-4 ★体と配管の 分かれ目★（本紙 §三 を 引きて ―― ★再測 0★）

| 層 | 何を使ふか | 版上げの効き |
|---|---|---|
| **体（Hermes TUI）** | R2（軍師second ＋ 本部長）・R3（a7）／R1 は **0 体** | **★効く★** |
| **配管（watcher）** | a7 の配達番 `1220779` ＝ **系の `/usr/bin/python3`**（venv 外）／本部長の下り `2492971` ＝ **R0** | **★効かぬ（`hermes_agent` を import せぬ）★** |

- ⇒ ★canary 順 `R1 → R3 → R2` は 變ぜず★。**R0 は 順の外**（的に非ず）。
- ⇒ ★R1 が 零リスクなる所以が 二重に 立ち申した★ ―― 走行体 0（§9-3）＋ 配管との縁 無し。

### 11-5 UNMEASURED（owner 明記）

1. **`0.20.4` の source lock** ―― owner ＝ **Main source custodian**（Commander 手配済・★之が着かねば 上げ得ぬ★）
2. R2 の agent 二本（`836838`／`4099497`）が 現に分かち合ひ居るか 片方が遺骸か ―― owner ＝ 當職（★本夜 §9-1 にて 帰属は解けたるも 生死の別は 未測★）
3. R0 を 的に含むや否や の **判** ―― owner ＝ **上**（當職は §11-3 の案のみ）
4. 全12体の名簿 ―― owner ＝ **委員長殿**（★分母 12 は 當職の器にて 検算し得申さぬ★）

### 11-6 變ぜぬ物（本節の分）

読取のみ ―― `find`・`readlink`・`stat`・`wc`・`grep`・`ps -p`（★名指し 1 pid★）。
★hermes 系 file 改変 **0**★／★venv の python を **実行せず**（版は dir 名と symlink にて取る）★／
`pip` **0**・`npm` **0**・install **0**／撃ち **0**・kill **0**・restart **0**・respawn **0**／
`tmux` 一指 **0**・send-keys **0**・pane 入力 **0**・capture **0**／
secret 不開（`HERMES_RO_PASSWORD` 等の **env 名のみ** 見え申したが ★値は 一つも 読まず★）／
他者の `environ` **0**／`queue/tasks` 書込 **0**／push **0**・fetch **0**・pull **0**。

---

## 十二 ―― ★§11-5 ㋐ を 解く★（R2 二体 生存・双方 `--continue`）／ **★而して 其の途上にて ―― 當職の「読取のみ」の測りが 軍師second の門を 誤発火させ得る事 判明★**（as_of 2026-08-21T05:59:53 / 06:01:34 / 06:01:59 / 06:02:27 +09:00）

### 12-1 R2 の二体 ―― ★双方 生存★（★名指し pid ＋ 負の對照★）

| pid | ppid | stat | **etime** | 起（lstart） | comm | 役 |
|---|---|---|---|---|---|---|
| `836658` | `1519165`（tmux server） | `Ssl+` | 8-15:08:20 | Wed Aug 12 14:51:32 | doppler | 軍師second |
| **`836838`** | `836658` | `Sl+` | **★8-15:08:19★** | Wed Aug 12 14:51:32 | **hermes** | **軍師second の体** |
| `837082` / `837090` | ―― | `Sl+` | 8-15:08:17 | 〃 14:51:34 | node / python | ui-tui / tui_gateway |
| `4099483` | `1519165` | `Ssl+` | 01:31:18 | **Fri Aug 21 04:28:33** | doppler | 本部長 |
| **`4099497`** | `4099483` | `Sl+` | **★01:31:18★** | **★Fri Aug 21 04:28:34★** | **hermes** | **本部長殿の体** |

- **負の對照**: `ps -p 999999` ⇒ **`rc=1`**。∴ 上の `rc=0` は ★現の生存の證★。pane も `%24` `dead=0` ／ `%35` `dead=0`。
- ⇒ **★片方が遺骸なる説は 消え申した ―― R2 は 現に 二役の共有★**（§9-1・§9-3 は 變ぜず）。
- **★齢は 大いに異なる★**: 軍師second ＝ **8 日 15 時間** ／ 本部長 ＝ **1 時間 31 分**（本日 04:28 起）。
  > ### ★★爆風半径は 「役の数」に非ず ―― ★役ごとの 抱へ居る齢★ にて 測るべし★★

### 12-2 ★§11-5 ㋐ 解決 ―― 双方 `--continue` にて 起ち居り申す★

| 役 | launcher | **逐語** | `--tui` | `--continue` |
|---|---|---|---|---|
| 軍師second | `…/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh` `:13`（13 行 799 B `sha16 cfce29de3943f475`） | `"$RT/venv/bin/python" "$RT/hermes" ★--tui --continue★` | **有** | **★有★** |
| 本部長 | `…/honbucho/bin/hermes-honbucho` `:9-10` | `… /hermes ★--continue★ "$@"` | **★無★** | **★有★** |

- **走行体の cmdline にて 裏書き**: `836838` ＝ `… hermes --tui --continue` ／ `4099497` ＝ `… hermes --continue`（★`--tui` 無し★）。
- ⇒ ★R2 を 落として 起こし直すの費用は ―― 双方 `--continue` ゆゑ ★会話は 継がれ得申す★★。
  ★但し 「継がれ得る」は launcher の ★形★ の證であって、現に 8 日分が 戻るや否やは ★當職 測り居らず★★（★形は證に非ず★）。

### 12-3 ★★本節の 芯 ―― 當職の 読取のみの測りが 他者の門を 誤発火させ得る★★

- launcher `:5` の **singleton guard（逐語）**:
  `if pgrep -f "$ROLE_HOME.*hermes --tui" >/dev/null 2>&1; then echo "singleton_guard_block" >&2; exit 75; fi`
- 當職 其の述語を **そのまま 撃ち申したるに** ―― 掬へたるは 三つ:

| pid | 何者か |
|---|---|
| `836658` | 軍師second の doppler（★cmdline に 子の引数を含む★） |
| `836838` | 軍師second の体（★真の的★） |
| **`187801`** | **★當職自身の `/bin/bash -c …` ―― ★述語の綴りを cmdline に抱き居るがゆゑ★★** |

- 一つ前の呼び出しにて掬へたる `186381` は ★已に消滅★（＝ 前の測りの殻）。∴ **★測る度に 一つ 増える★**。
- **⇒ ★誰かが 軍師second を 起こし直さんとする其の刹那に 當職が 測り居らば ―― guard が `singleton_guard_block` を返し `exit 75` にて 落ち申す★**。
  ★体は 一つも 走り居らぬにも 拘らず★。★而して 其の顔は 「runtime の故障」に 見え申す★。

> ### ★★`pgrep -f` にて書きたる singleton guard は ―― 其の綴りを cmdline に含むだけの ★観測者★ をも 「本体」と数へ 門を閉ざし申す★★
> ★「読取のみ ゆゑ 安全」は ―― ★偽★ に御座る★。
> ★己の測りが 他者の ★制御路★ に 副作用を持つ事 有り★（本件は 起動を 塞ぐ側 ＝ ★安全側に倒れる誤り★ なるが、
> ★canary の 起こし直しの 刹那に 当たれば 「上げたら 起動せず」と 誤診させ 巻き戻しを招き申す★）。
> ★之にて 本夜 ★物差しが 己の綴りを数へたる★ は 四度目に御座る ―― 而して 前三度は ★己の数を汚す★ のみ、
> **★本件は 己の外の 門を 動かす ―― 質が 異なる★**。

### 12-4 ★次の安全な一手（★機構は 一指も 触れず★）★

- ★當職の為し得るは 二つのみ★:
  1. **★運用にて 避く★** ―― ★軍師second の 起こし直しの窓の間 當職は 其の path を含む述語を 一切 撃たぬ★（★本節を以て 己に課す★）。
  2. **★上へ 告ぐ★** ―― canary を 撃つ者（Commander 令の下・蘇生の主＝委員長殿）へ 本件を 届く（次項）。
- ★guard 其の物の 直しは ―― 委員長殿の許可の下にてのみ★（★機構を直したく成った時 ＝ 先に許可★／且つ hermes 系 file は 當職 ★読取のみ★）。
  ★案のみ 記す★: `pgrep -x hermes` ＋ `HERMES_HOME` の照合、或は lock file、或は `/proc/*/exe` の realpath 照合（★案 ―― 判は 上★）。

### 12-5 變ぜぬ物（本節の分）

読取のみ ―― `ps -p`（名指し）・`tr < /proc/<pid>/cmdline`（名指し 2 pid）・`pgrep -af`（★己を含めて 正直に 列挙★）・`sed`・`wc`・`sha256sum`・`find`・`tmux list-panes`（capture **0**）。
★launcher の 実行 **0**★（★読みたるのみ ―― `start-gunshi-second-hermes.sh` を 走らせ申さず★）／
撃ち **0**・kill **0**・restart **0**・respawn **0**・`--continue` **0**・`--resume` **0**／
`tmux` 一指 **0**・send-keys **0**・pane 入力 **0**／hermes 系 file 改変 **0**／
他者の `environ` **0**・secret 不開（`doppler`・`promote_supabase_rotation_key.sh` は ★存在のみ 記し 中身 不開★）／
`queue/tasks` 書込 **0**／push **0**・fetch **0**・pull **0**。

---

## 十三 ―― ★§12-3 を 族へ 掃きたる★（★門は 一つに非ず 二つ★）／ **★而して 掃きの途上に ―― 現に 30 分毎に走り居る 見張りの 破れ 四つ を 見出し申した★**（as_of 2026-08-21T06:13:37 〜 06:17:51 +09:00）

> ★本節は 悉く **読取と 負テスト** のみ ―― ★番人・門・probe を 一つも 走らせ申さず★★（唯一 撃ちたるは ★己の shell の中の 無意味語★ に御座る）。

### 13-1 掃きの器と 母集団（★N は 下限★）

- 器 ＝ `/usr/bin/find -L … -maxdepth 3 -type f \( -name '*.sh' -o -name '*.py' -o -name 'hermes-*' -o -name 'start-*' \)` ＋ `/usr/bin/grep -ln pgrep`（★`-L` にて symlink も辿る・函数を避け 絶対 path★）
- 母集団 ＝ `~/hermes-roles` ＋ `~/hermes-departments` の **35 件** ⇒ 当たり **4 件**。
- ★母集団は 此の二樹に限る ―― `~/bin`・`scripts/` は 本節の掃きの外（★N は 下限★）★。

### 13-2 ★門は 一つに非ず ―― 二つの現役の役に ★逐語同一★ にて 座し居り申す★

| file | 行/B | sha16 | inode | mtime | `:5` |
|---|---|---|---|---|---|
| `…/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh` | 13 / 799 | `cfce29de3943f475` | `688761` | 2026-08-07 10:11:40 | ★同一★ |
| **`…/ashigaru-second-7-hermes/bin/start-ashigaru-second-7-hermes.sh`** | 13 / 803 | `874ca0a6093e3cb1` | `1059949` | 2026-08-16 22:19:54 | ★同一★ |
| （`.bak-continue-fix-20260813`・退役） | 13 / 900 | `d60aa4f009eebcda` | `1057831` | 2026-08-13 00:33:50 | ★同一★ |

- 逐語 ＝ `if pgrep -f "$ROLE_HOME.*hermes --tui" >/dev/null 2>&1; then echo "singleton_guard_block" >&2; exit 75; fi`
- ⇒ **★§12-3 の危険は ★二役★ に及び申す ―― 軍師second（R2）と 足軽second7（R3）★**。
- ⇒ **★canary 順 `R1 → R3 → R2` の うち ★後ろ二段が 悉く 此の門の下★★**（R1 のみ 門を持たず ―― ★R1 が零リスクなる所以が 三重に 立ちたる★）。

### 13-3 ★死したる probe ―― `fleet_supervisor_probe.py`（★瑕は在れど 走り居らぬ★）★

- 31 行 3,613 B `sha16 4b62277252306b69`。`:7` ＝ `ROLES=['shogun-second','karo-second']+[f'ashigaru{i}' …]+['gunshi-second']`
- **現に pane が名乗り居る名（實測 06:14:59）**: `ashigaru-second-1` … `-7` ／ `gunshi-second` ／ `karo-second` ／ `shogun-second`（★十件★）
- ⇒ **★十役中 七役が `PANE_MISSING`★**。且つ 退役したる箱（`queue/inbox/ashigaru1..7.yaml` ＝ 127,871〜376,033 B）が **現に在る** ゆゑ `unread` は ★死したる器より もっともらしき数を返し申す★（★節486 の三例目★）。
- **★然れど 之は 現に 害を為し居らぬ★**: `state/fleet_supervisor_state.json` の刻 ＝ **`2026-08-09 14:16:44`** ＝ **★齢 11 日 15 時間 58 分★** ⇒ ★11 日 走り居らぬ★。
- **★而して 其の state が 語る事★**: 記録されたる十役は **`ashigaru1`〜`ashigaru7`**。probe は `:21` にて ★pane に在る役のみ★ を state へ書く（無き役は `continue`）⇒ **★Aug 9 の時点では pane が 現に `ashigaru1..7` と 名乗り居りたる★**。
  ⇒ ★名の入替は 其れ以降に起き 而して probe は 追随せず 且つ 走らなく成りたる★。

> ### ★★瑕を見付けたる時は ―― ★其れが 現に 走り居るか★ を 先に問へ★★
> ★走り居らぬ器の瑕は 「危険」に非ず ―― 「★次に起こした時に牙を剥く罠★」に御座る★。
> ★格が 全く異なる ⇒ 同じ紙に 並べて書くな★。

### 13-4 ★★現に生きたる見張り ―― `second-fleet-sentinel`（★30 分毎・直近 05:58:27・次 06:28:27★）★★

- unit ＝ `~/.config/systemd/user/second-fleet-sentinel.{service,timer}`（`Description=… (iincho 2026-08-07)`・`Type=oneshot`・`OnUnitActiveSec=30min`・`Persistent=true`）
- 本体 ＝ `~/bin/second_fleet_sentinel.sh`（**24 行 1,558 B `sha16 3c7a7c65703c3761`**・mtime 2026-08-07 19:38:01）
- 直近の出力 ＝ `OK fleet_sessions=3 panes=8`（`status=0/SUCCESS`・CPU 35ms）

#### ★破れ㋐ ―― ★watcher が 全滅したる 其の唯一の時に限り 見張りが 黙す★（★負テストにて 実証★）★

- `:9` ＝ `w=$(pgrep -c -f 'scripts/inbox_watcher.sh' || echo 0)` ／ `:10` ＝ `[ "${w:-0}" -lt 9 ] && missing="$missing watchers=$w/9(無音死の疑い)"`
- **負テスト**（★述語を 部品より組み立て 己の cmdline に 現さず★ ―― 然もなくば 己が己を掬ふ）:

| 場合 | `w` の生の値 | `[ … -lt 9 ]` | alert |
|---|---|---|---|
| **0 件**（無意味語にて） | **★`0\n0`（3 B・二行）★** | **`integer expression expected` ⇒ rc=2** | **★出ず★** |
| 対照（現況） | `9`（一行） | 正しく評価 | 正常 |

- 因 ＝ **★`pgrep -c` は 0 件にて `0` を刷り 且つ `rc=1` を返す★** ⇒ `|| echo 0` が **重ねて** `0` を刷る ⇒ `w` が二行に成る。
  ★之は 本夜 節487 ㋑ にて 當職自身が 踏みたる罠と ★同一★ に御座る（`grep -c` も同じ）★。
- **★精確に書く★**: ★一体でも生き残らば 一行にて返り 閾は 正しく効き申す★（`9 → 8` は 現に検知す）。
  ⇒ **★沈黙するは 「全滅」の一点のみ ―― 即ち 番人は 己が最も要る刹那に限りて 黙す★**。

#### ★破れ㋑ ―― ★観測者が 番人の数を 水増しす★（構造・★実証は §12-3 にて済み★）★

- `pgrep -f 'scripts/inbox_watcher.sh'` は ★其の綴りを cmdline に含むだけの者★ を数へ申す。
- ⇒ ★watcher が `8/9` に減じたる其の時 誰かが 其の綴りにて掃けば `9` に見え ―― ★alert が 出ぬ★★。
- **★當職 之を 実演せず★**: 実演すれば ★現に生きたる警報を 汚す★（次の発火は 06:28:27）。
  ★機構は §12-3 にて 已に実証済（`pgrep -f` が 當職の shell `187801` を掬ひたる）ゆゑ 形にて判じて足る★。

> ### ★★同じ根（★綴りにて 族を括る★）より ―― 二つの誤りが 出づ★★
> §12-3 の門 ＝ ★起動を塞ぐ（**安全側**）★ ／ 本節㋑ ＝ ★緑を偽る（**危険側**）★。
> ★∴ 「綴りにて括る」瑕を見たらば ―― ★其の向きを 必ず問へ★★（★偽の緑と偽の赤は 同じ因より出づ★）。

#### ★破れ㋒ ―― ★軍師second の session が 見張りの母集団の外★（實測 06:17:51）★

| session | panes | 役 | 番人 `:2` の期待 |
|---|---|---|---|
| `shogun-second` | 1 | shogun-second | ★在り★ |
| `multiagent-second` | 8 | karo-second ＋ ashigaru-second-1〜7 | ★在り（`-lt 8` ―― 余裕 0）★ |
| `hermes-honbucho` | 1 | （`@agent_id` **空**） | ★在り★ |
| **`hermes-gunshi-second`** | **1** | **gunshi-second（`%24`）** | **★無し★** |

- ⇒ **★軍師second の session が 消えても `OK fleet_sessions=3` と刷り申す★**（★偽の緑★）。
- ★之は canary の ★最終段（R2）★ の器に御座る ⇒ ★落として起こし直す其の枝にて 最も要る見張りが 現に 効き居らぬ★。

#### ★破れ㋓ ―― ★`has-session` は 器を證し 中の者を證さず★★

- `:4-6` は ★session の在否★ のみを問ふ。
- 反例（本夜の実測）: `hermes-honbucho` の session は 続き居るに ―― 其の中の hermes 体 `4099497` は **本日 04:28:34 に起ち直り居る**（§12-1）。
  ⇒ ★体が死して起ち直る間 番人は 一度も鳴かず★。
- ★條: 「札(session)」は 稼働の證に非ず ―― ★中の者の齢を 併記せよ★★

### 13-5 ★當職の為し得る事・為し得ぬ事★

| | |
|---|---|
| 為したる | ★読取と 己の shell の中の 負テストのみ★ |
| **為さぬ** | ★番人・門・probe を 一つも 走らせず★／★unit の enable/disable/restart/daemon-reload 悉く 0★／★`~/bin/*` 改変 0★／★hermes 系 file 改変 0★ |
| 直しの権 | **★委員長殿★**（`Description=… (iincho 2026-08-07)`・且つ ★機構を直すは 先に許可★） |
| 案（★判は上★） | ㋐ ＝ `w=$(pgrep -c -f … ); w=${w:-0}` の如く ★`||` を外し 既定は展開にて与ふ★／㋑ ＝ `pgrep -x` ＋ 引数照合、或は unit の `MainPID` 群にて数ふ／㋒ ＝ `:2` の期待に `hermes-gunshi-second` を加ふ／㋓ ＝ session の在否に加へ ★中の体の `etime`★ を見る |

### 13-6 UNMEASURED（owner 明記）

| # | 何 | owner |
|---|---|---|
| ㋐ | 番人 `:10` の閾 **9** が 何を数へたる 9 なるか（役は十・箱は三十一） | **委員長殿**（★制定者★） |
| ㋑ | `hermes-honbucho` pane の `@agent_id` が 空なる事の 是非 | **本部長殿** |
| ㋒ | `fleet_supervisor_probe.py` を 再び走らせる意向の有無（★走らせば 七役が `PANE_MISSING` と鳴る★） | **本部長殿** |

### 13-7 變ぜぬ物（本節の分）

読取のみ ―― `find`・`grep`・`stat`・`wc`・`sha256sum`・`cat -n`・`sed`・`awk`・`tmux list-panes`（★capture 0★）・`systemctl --user cat/status/list-timers/list-units`（★悉く 読取★）・`python3`（己の器にて json/yaml を読むのみ）。
★番人 走らせず **0**★／★門（launcher）走らせず **0**★／★probe 走らせず **0**★／
★`pgrep` は 撃ちたるが ―― ㋐ 無意味語（己の cmdline に現さず）・㋑ 部品組立にて watcher 数の対照 **1 回**のみ★／
unit の enable/disable/restart/daemon-reload **0**・timer 改変 **0**・`systemctl` は ★読取のみ★／
`~/bin/*` 改変 **0**／hermes 系 file 改変 **0**／
撃ち **0**・kill **0**・restart **0**・respawn **0**・`--resume` **0**／
`tmux` 一指 **0**・send-keys **0**・pane 入力 **0**／
他者の `environ` **0**・secret 不開（`SUPABASE_SERVICE_ROLE_KEY` は ★unit 本文の env 名として見え申したが 値は 一つも読まず★）／
`queue/tasks` 書込 **0**／push **0**・fetch **0**・pull **0**。
