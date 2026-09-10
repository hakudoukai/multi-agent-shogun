## §的 ★的一行★

★third_pc の空き計は 既存三器の何れとも重ならぬ列（D:・kind・一日一行 TSV）を持たぬ ―― ゆゑに 新器を立てず、`~/bin/cdrive_autoguard.sh` へ ★測るだけの `gauge_daily()` を 63 行 足す patch★ を鋳り、当てずに `apply --check` rc=0 まで持つた。★

---

## §零 帳の頭（何時・何を・幾つ讀んだか）

| 欄 | 値 |
|---|---|
| as_of | 2026-09-10T17:11:55+0900 |
| 席 | ashigaru-third-3（板 12e9d4bd・third_pc momizi-dx・TMUX_PANE %6） |
| 令 | 第二百七十一令（常設器 GO・詳細 `scratch/k3_orders/order271_a3.txt`・8 行 / 2,807 B / sha16 `a9018a64f4841738`） |
| 樹 | `/home/hakudoukai/multi-agent-shogun`（作業樹・LF） |
| HEAD | `1ad4edfbadc69191183a42113e9979c3f91b7dbf`（不動） |
| porcelain | 170 行（本弾で不変） |
| 讀んだ物 | systemd user unit 5 枚・器 3 本（ps1 / autoguard.sh / tripwire.sh）・`/mnt/c` の紙 3 本（boot-auto-resume.md・fleet-composition-manifest.yaml・persist-org-changes.md）・己の紙 order262 の §五 ＝ ★計 12 物★ |
| 走 | ★6 / 6★（下表） |
| 焚 | ★1 / 2★（`order271_gauge.rule.py` rc=0） |
| 母 | 本紙を書く前に測つた ＝ 113 枚 / 23359 行・N=268（幅 169〜484） |

### 走の帳（外の世界を測つた command のみ ―― 令264 ■〇-2）

| 走 | 何を測つたか |
|---|---|
| 1 | systemd user unit dir の一覧 ＋ unit 5 枚 ＋ 器 3 本 の悉皆讀み（出力 29.5 KB が置き物へ落ちた） |
| 2 | 其の置き物から unit と器の本文を取り出した |
| 3 | `/mnt/c` の紙 2 本の頭 ＋ manifest の persist-org-changes 周辺 ＋ order262 の一覧 |
| 4 | `/mnt/c/DentalBI/.claude/rules/persist-org-changes.md` 全文（157 wc / 11,197 B / sha16 `ea6fca1a905eef60`） |
| 5 | order262 §五 ＋ `df -B1` 三点 ＋ glob 三本 |
| 6 | `~/bin/cdrive_autoguard.sh` の頭 34 行 ＋ manifest L528-534 ＋ 両者の CR 数 |

★数へ方の申告（條 四百三十六）★ ―― 己の樹の `git ls-files` / `rev-parse` / `status` / `apply --check` と、己の箱の既読化・紙の io は ★走に数へて居らぬ★（令264 ■〇-2「己の紙・器・枝・箱・帳の頭は走に数へぬ」に依る）。令271 四 の括弧を ★悉くの command★ と讀むなら 本弾は 10 走であり上限を超える。★何れの讀みを採つたかを家老の裁に委ねる★。

★harness の置き物（床に依り記す・消して居らぬ）★ ―― `/home/hakudoukai/.claude/projects/-home-hakudoukai-multi-agent-shogun/f1588e31-d0a6-45ba-8e96-192df867cd08/tool-results/bak7913pg.txt`・刻 2026-09-10T15:14:36・30,216 B・sha16 `43e762a3ba27d99d`。

---

## §一 令の逐語（写した）

> ⑴ALL-SEARCH-BEFORE-CREATE=third 既存の dentalbi-cdrive-monitor.service / dentalbi-cdrive-autoguard / scripts/repo_copy_tripwire.sh を先に読み、同目的なら★拡張★（新器は作らぬ）⑵書込0（df -B1・固定深さ glob 2本 C:既定/D:WSL・kind 列 c_default/d_wsl/none・none を「無い」と読ませぬ註）⑶一日一行 TSV・4〜6走・timer は persist-org-changes の4欄で登録⑷vhdx 圧縮そのものは理事長の管理者 PowerShell 専管＝器は測るだけ・戻る量は幅で書く。owner=A3・判定=軍師third・紙の新條6本は dev_qa へ

> 四 上限＝走 6（df・glob・ls・讀み＝command 1 本＝1 走）・焚 2（拡張器の selftest のみ・timer は焚かぬ）・90 分。patch は当てず apply --check まで。

---

## §二 三器の一表（器／測る物／書くか／周期／§五 との重なり）

| 器 | 在処 | 測る物 | 書くか | 周期 | §五 との重なり |
|---|---|---|---|---|---|
| ㋐ `cdrive_free_monitor.ps1` | `/mnt/c/DentalBI/scripts`（163 wc / 8,162 B / sha16 `fba77e5e4be96b1f`）・Windows 側 | ★C: の空きのみ★（`Get-PSDrive C` の `Free`・GB へ丸め） | 書く（log / state / latest.json / capacity_epoch.json / lease） | 30 分（`OnUnitActiveSec=30min`・`OnBootSec=3min`） | ★一点のみ ＝「空きを測る」★。D: 0・kind 列 0・TSV 0・byte 精度 0（GB へ丸める） |
| ㋑ `cdrive_autoguard.sh` | `~/bin`（124 wc / 6,466 B / sha16 `d175e32a71aec0a8`）・WSL 側 | ★C: の空きのみ★（`df -BG /mnt/c` ＝ GB 丸め） | 書く（log ＋ ★掃除する★＝log 截り・bak 削除・journal vacuum・ccflare DB の白名簿 4 表削除） | 3600 秒（`OnUnitActiveSec=3600`・`OnBootSec=300`） | ★一点のみ ＝「空きを測る」★。D: 0・kind 列 0・TSV 0・byte 精度 0 |
| ㋒ `repo_copy_tripwire.sh` | `~/bin`（20 wc / 2,080 B / sha16 `79cfad60119712dd`） | ★空きではない★ ―― repo の複製（`.git` が -mmin -20 で 300MB 超）と `/tmp` 直下 1000MB 超 | 書く（`~/.local/state/repo-copy-tripwire` の log/seen/msg ＋ 委員長へ便） | ★測定不能★（本弾で当該 unit を名指して確かめて居らぬ ―― 自訴 3） | ★重なり 0★（測る物が違ふ） |

★∴ 同目的の器 ＝ ㋐ と ㋑ の二本。重なりは ★「空きを測る」一点のみ★ で、§五 の要る列（D:・root・kind・byte 精度・一日一行 TSV）は ★三器の何れにも現に無い★。★

---

## §三 実測（★書込 0★・as_of は §零 と同刻の走 5）

### 甲 `df -B1`（byte・丸め 0）

| 点 | size_b | used_b | avail_b |
|---|---|---|---|
| `/` (`/dev/sdd`) | 1,081,101,176,832 | 299,242,942,464 | 726,865,879,040 |
| `/mnt/c` | 510,294,749,184 | 240,851,673,088 | 269,443,076,096 |
| `/mnt/d` | 1,024,191,361,024 | 396,707,082,240 | 627,484,278,784 |

### 乙 固定深さ glob 二本と kind 列

| 網 | pattern | n | kind |
|---|---|---|---|
| C: 既定 | `/mnt/c/Users/*/AppData/Local/Packages/*/LocalState/*.vhdx` | 0 | ― |
| D: WSL | `/mnt/d/*/*/*.vhdx` | 1 ＝ `/mnt/d/WSL/Ubuntu-24.04/ext4.vhdx` | ★`d_wsl`★ |
| （深さ違ひの対照） | `/mnt/d/*/*.vhdx` | ★0★ | ― |

★深さを一つ外すと同じ物が 0 に見える★ ―― `/mnt/d/*/*.vhdx` は 0、`/mnt/d/*/*/*.vhdx` は 1。∴ 0 は「無い」ではなく「其の深さに無い」である（新條 四百九十一）。

★戻る量は幅で書く（令 一 ⑷）★ ―― 本弾は圧縮の器を一度も走らせて居らぬ ∴ ★戻る量は 測定不能★。上限の目安だけは書ける ―― vhdx の実寸（別弾 order262 の実測 393,514,844,160 B）と `/` の avail から「上限は vhdx 実寸を超えぬ」と言へるのみ。

---

## §四 拡張か新器か ―― ★拡張★

| 問 | 答 | 因 |
|---|---|---|
| 新しい `.sh` / `.ps1` を作つたか | ★作つて居らぬ★ | 令 一 ⑴「同目的なら拡張（新器は作らぬ）」 |
| 新しい unit（service / timer）を作つたか | ★作つて居らぬ（増分 0 本）★ | 既存 `dentalbi-cdrive-autoguard.timer`（3600 秒）へ相乗りし、一日一度だけ書く事は器の中の刻の比べで為す |
| 何処へ足したか | `~/bin/cdrive_autoguard.sh`（㋑） | ㋑ は ★WSL 側・bash・既に `df` を持ち・既に timer を持つ★ ―― 四つとも §五 と同じ土俵。㋐ は Windows 側 PowerShell ゆゑ D: の glob と TSV を足すには器の言葉ごと変る |
| 掃除部に触れたか | ★一字も触れて居らぬ★ | 挿入は `free_gb()` の直後・`BEFORE=$(free_gb)` の直前の一箇所のみ。白名簿 4 表・件数不変の検算・vacuum の条件は ★不変★ |
| 本弾で作つた `.rule.py` は新器か | ★常設器ではない★ | 一回限りの ★検算器★（patch の 甲 hunk を取り出して合成値で焚くだけ）。常設に残さぬ。新條 四百九十四 |

---

## §五 patch の中身と数

| 欄 | 値 |
|---|---|
| path | `scratch/ashigaru-third-3-12e9d4bd/order271_extend.patch` |
| 大きさ | 5143 B |
| 行数 | ★86 wc / 87 片★（床(32) 併記） |
| sha16 | `85f010d0cf9538e0` |
| hunk | 2 本 ―― 甲 `home/hakudoukai/bin/cdrive_autoguard.sh` ＋63 行 ／ 乙 `mnt/c/DentalBI/docs/rules/fleet-composition-manifest.yaml` ＋8 行 |
| 挿入 合計 | ★71 行★（削除 0） |
| 当てたか | ★当てて居らぬ★ |
| 検 | `git -C / apply --check -p1 --unsafe-paths <patch>` ＝ ★rc=0★（根 `/`・剥がし -p1 ―― 新條 四百九十三） |

### 甲 hunk が足す物（§五 の設計に一対一で当てた）

| §五 の要り物 | patch の何処 |
|---|---|
| `df -B1`（`-h` でなく） | `gauge_df3()` ＝ `df -B1 "$1" ... awk NF>=4` |
| 固定深さ glob 二本 | `GAUGE_GLOB_C` ＝ C: 既定 ／ `GAUGE_GLOB_D` ＝ `/mnt/d/*/*/*.vhdx` |
| kind 列 | `gauge_probe()` ＝ `c_default` → `d_wsl` → `none` の順に当て、当たつた網の名と byte を返す |
| none を「無い」と読ませぬ註 | 器の頭 4 行目 ＋ TSV の頭 2 行目 の ★二箇所★ |
| 一日一行 TSV | `gauge_daily()` ＝ TSV に `<TAB>今日T` が在れば何も書かず戻る |
| 列 | 14 欄 ＝ mode / pc / as_of / root 3 / c 3 / d 3 / vhdx_kind / vhdx_bytes |
| 書込 | ★当該 TSV の一行のみ★（`/mnt/c` へは一字も書かぬ） |
| 一日あたりの走 | 6 ＝ `df` 3 ＋ glob 2 ＋ `stat` 1（`find` は使はぬ） |

---

## §六 timer 登録 ＝ persist-org-changes の ★4 欄★（紙に書くのみ・unit は打つて居らぬ）

欄の名は `/mnt/c/DentalBI/.claude/rules/persist-org-changes.md` L98-101 から ★写した★（逐語）:

> PERSISTENCE:      なし | LaunchAgent(<plist path>) | systemd --user(<unit>) | タスクスケジューラ(<name>)
> LINGER/RUNATLOAD: 有 | 無（Linuxで loginctl enable-linger 未実施なら「無」＝未完）
> REBOOT_PROOF:     未実施 | 実施(<時刻>・自動復旧した構成を実視)
> MANIFEST_UPDATED: 未 | 済(<path>)

本件の 4 欄（★4 行★）:

```
PERSISTENCE:      systemd --user(dentalbi-cdrive-autoguard.service + .timer) ―― 既存 unit への相乗り。新 unit 0 本
LINGER/RUNATLOAD: 有（既存 unit が現に 3600 秒周期で走つて居る事から推す）―― ★己は loginctl を打つて確かめて居らぬ★
REBOOT_PROOF:     未実施 ―― 席は systemd の live 操作（enable/start/daemon-reload）を持たぬ。実視は総監督の手
MANIFEST_UPDATED: 未 ―― 行は patch の 乙 hunk に鋳た（当てては居らぬ）。当て先 /mnt/c/DentalBI/docs/rules/fleet-composition-manifest.yaml
```

---

## §七 manifest へ足す行（`delivery_routes:` の 7 欄）

欄の名も同じ紙 L58 から写した ―― 逐語「欄は `path / host / direction / what / why / proof / gap`。★`gap` を空にしない★」。
patch 乙 hunk が足すのは ★8 行★（鍵 1 行 ＋ 7 欄）。鍵 ＝ `cdrive_gauge_daily_tsv_20260910`。挿す所 ＝ `delivery_routes:`（L531）の直後。

---

## §八 陽性対照（★合成値・実測ではない★）

器 `scratch/ashigaru-third-3-12e9d4bd/order271_gauge.rule.py`（73 wc / 74 片 / 2900 B / sha16 `a3ccda2d76d06aaf`・焚 1・rc=0）が立てた門 五つ:

| 門 | 何を証したか | 出 |
|---|---|---|
| 一 | 禁の command が器に無い（Optimize-VHD / diskpart / wsl の停止 / rm の再帰 / Compact-VHD の 5 語） | 悉く 0 |
| 二 | 三つの註（none・実測ではない・kind）が器に在る | 現に在る |
| 三 | 合成値の selftest が走る（`bash -s -- --gauge-selftest` へ pipe 直流・一時 file 0） | rc=0・2 行 |
| 四 | ★実測の TSV へ一字も書いて居らぬ★（`~/.local/share/dentalbi/cdrive_gauge.tsv` の不在） | ★現に無い★ |
| 五 | 頭の欄名の数と合成行の列数が ★共に 14★ | 14 ＝ 14 |

出た合成行（`<TAB>` は器が刷つた置き換へ・★実測ではない★）:

```
# selftest: 以下の行は 合成値 であり 実測ではない
gousei<TAB>gousei-pc<TAB>2000-01-01T00:00:00+0900<TAB>1<TAB>2<TAB>3<TAB>4<TAB>5<TAB>6<TAB>7<TAB>8<TAB>9<TAB>none<TAB>
```

★`mode` 列を第一列に置いたゆゑ、TSV を後で讀む者は 合成行と実測行を ★列で★ 分けられる。★

---

## §九 新條（★四百九十 から★・六本）

- ★四百九十★ ＝ 「同目的か」は ★器の名では決まらぬ★ ―― 三器は悉く名に「cdrive」を持つが、★測る物／書くか／周期★ の三欄を並べて初めて 重なりが「空きを測る」一点に絞れ、㋒ は重なり 0 と出た。器を比べる時は ★名ではなく欄で★ 比べよ。
- ★四百九十一★ ＝ ★固定深さの glob は 深さを一つ外すと 同じ物を 0 と返す★ ―― `/mnt/d/*/*.vhdx` は 0、`/mnt/d/*/*/*.vhdx` は 1。0 を「現に無い」と讀むな。★何れの深さで当てたか★ を同じ行に書け（條 百七十七 の深さ版）。
- ★四百九十二★ ＝ ★常設器を立てる事と timer を立てる事は別★ ―― 既存 unit へ相乗りすれば 新 unit 0 本・enable/start 0 で済む。「常設器を入れた」と書く時は ★unit が何本増えたか★ を同じ行に書け。
- ★四百九十三★ ＝ ★patch の当て先が repo の外に在る時、`apply --check` の ★根（走らせる dir）と 剥がし数（-p）★ を同じ行に書け★ ―― 本弾は 根 `/`・`-p1`・`--unsafe-paths`。根を書かねば「通つた」は再現できぬ。
- ★四百九十四★ ＝ ★検算器は常設器ではない★ ―― 「新器を作るな」の禁は ★常設器★ に掛かる。一回限りの検算器を鋳た時は 其の別を紙に明記し、★常設に残さぬ事★ を同じ行に書け。
- ★四百九十五★ ＝ ★合成値の陽性対照は 二つを同時に証さねばならぬ★ ―― ㋐列の数が合ふ事 ㋑★実測の置き場へ一字も書いて居らぬ事★。列だけ見る対照は「書いてしまつた」を見逃す。

★母の伸び（家老 条(r)）★ ―― 本紙を書く前の母 ＝ 113 枚 / N=268。★本紙が更に 6 本鋳る ∴ 274★。己の紙が己の母に入り、書いた分だけ未着手が増える ―― 268 からの現行犯を重ねて居る。

---

## §十 三択語で結ぶ（十問）

| 問 | 結び |
|---|---|
| ⑴ 同目的の器は現に在るか | ★現に在る★ ＝ ㋐ `cdrive_free_monitor.ps1` と ㋑ `cdrive_autoguard.sh` の二本（重なりは「空きを測る」一点） |
| ⑵ ㋒ `repo_copy_tripwire.sh` は同目的か | ★現に無い★（測る物 ＝ repo の複製であり 空きではない） |
| ⑶ 三器の何れかが D: を測るか | ★現に無い★ |
| ⑷ 三器の何れかが 一日一行 TSV を書くか | ★現に無い★ |
| ⑸ 三器の何れかが kind 列を持つか | ★現に無い★ |
| ⑹ C: 既定の網に vhdx は在るか | ★現に無い★（n=0） |
| ⑺ third_pc の vhdx は現に在るか | ★現に在る★ ＝ `/mnt/d/WSL/Ubuntu-24.04/ext4.vhdx`（kind=`d_wsl`） |
| ⑻ patch は当たるか | ★現に在る★ ＝ `apply --check` rc=0（★当てては居らぬ★） |
| ⑼ 圧縮で戻る量 | ★測定不能★（圧縮の器を一度も走らせて居らぬ ―― 上限の目安のみ書ける） |
| ⑽ ㋒ の周期 | ★測定不能★（当該 unit を名指して確かめて居らぬ ―― 自訴 3） |

---

## §十一 自訴（七項）

1. ★走の数へ方は 己の讀みである★ ―― 己の樹の git 讀取（`ls-files`・`rev-parse`・`status`・`apply --check`）と 己の箱の既読化を走に数へて居らぬ。令271 四 の括弧を悉皆と讀めば 本弾は 10 走で上限超。§零 に隠さず書いた（條 四百三十六）。
2. ★`.rule.py` を一本鋳たのは 令五 の物の帳（紙・raw・patch の三つ）を ★己が広げた★ 事である★ ―― 広げた範 ＝ 検算器 1 本。触れて居らぬ禁 ＝ 常設器は増やして居らぬ・`/mnt/c` 書込 0・systemd 操作 0。焚の増分 ＝ 1（上限 2 の内）。裁は家老（條 四百三十三）。
3. ★㋒ の周期を確かめて居らぬ★ ―― `repo_copy_tripwire` の unit を名指して讀んで居らぬ。∴ §二 の周期欄は ★測定不能★ と書いた（推す事はできたが 推しを数に書かぬ）。
4. ★LINGER の「有」は 己が確かめた数ではない★ ―― `loginctl` を打つて居らぬ。既存 unit が現に走つて居る事からの ★推し★ である（作法 六条目）。
5. ★`gauge_daily` を毎時走行の頭へ置いたのは 己の判である★ ―― 令は挿す所を名指して居らぬ。因 ＝ 掃除部の前に測れば ★掃除の前の数★ が残る。掃除後の数を望むなら挿す所は変る ―― 家老の裁を仰ぐ。
6. ★`grep -q` の一日一行判は 刻の文字合はせである★ ―― `<TAB>YYYY-MM-DDT` を TSV 悉皆に当てる。行が増えれば当てる字数も増える（一日一行ゆゑ年 365 行 ―― 実害は見込まぬが ★見込みである★）。
7. ★`mkdir -p` は書込である★ ―― 令 一 ⑵「書込0」を ★`/mnt/c` への書込 0★ と讀んだ。TSV 一行と其の親 dir の作成は書込に当たる。讀み違ひなら patch の当該 2 行を落とせば済む（`~/.local/share/dentalbi` は既存 ―― ㋑ の log が現に在る）。

---

## §十二 物の帳

| 物 | path | 行数（wc / 片） | B | sha16 |
|---|---|---|---|---|
| 紙 | `scratch/ashigaru-third-3-12e9d4bd/order271_cdrive_gauge_extend_v1.md` | ????（完了便に記す） | ???? | ????（★書いた後に測る★＝総監督令 ⑴） |
| raw | `scratch/ashigaru-third-3-12e9d4bd/order271_raw_v1.txt` | 完了便に記す | ― | ― |
| patch | `scratch/ashigaru-third-3-12e9d4bd/order271_extend.patch` | 86 / 87 | 5143 | `85f010d0cf9538e0` |
| 検算器 | `scratch/ashigaru-third-3-12e9d4bd/order271_gauge.rule.py` | 73 / 74 | 2900 | `a3ccda2d76d06aaf` |

枝 ＝ `a3/order271-cdrive-gauge-20260910`（押しは席・非 force・新 ref・別 index → commit-tree → update-ref・HEAD 不動）。

---

## §十三 繰越

- 乙3 常設器 ＝ ★本弾で patch まで来た★（当てと enable/start は総監督の手）。
- 乙11 ＝ 家老の裁 15:14 逐語「kenshu_bucho の箱は書けるが読まれぬ（J2 通・J4 無）ゆゑ ★書かぬ・上げよ★」―― ★席は書かぬ★。監督（fukuincho）宛の家老便に乗る。
- 作法 ＝ 家老の裁 15:14「紙 order269 がローマ字綴り＝読めるが作法外・以後は日本語で（書き直しは不要・併記で可）」―― ★本紙から節の名を日本語に改めた★（order269 は書き換へぬ ＝ 前紙は書き換へるなの床）。
- 乙4 / 乙5 / 乙6 / 乙9 / 乙10 / 乙12 は不変（本弾で當て直した ―― ★古びて居らぬ★・作法 九条目）。

