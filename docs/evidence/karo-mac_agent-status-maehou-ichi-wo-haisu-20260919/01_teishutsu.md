# 判定提出の束 ―― 裁337507⑶疵②「前方一致で生きた席を掴む形」の是正

提出席: 家老mac ／ 親裁: seq337507⑶疵②（★最優先★）・seq337509（⒜本体をcommitし固定tupleを作れ）
雛形: JUDGE-SUBMISSION-BUNDLE-TEMPLATE v1.1（①〜⑦。★本紙は雛形に無い欄を足して居らぬ★）

---

## ■① 対象 tuple（一組のみ）

```
ref名   = refs/heads/karo-mac/km-agent-status-maehou-ichi-wo-haisu-20260919
commit  = ★本紙には書けぬ（自己言及）★ ―― 本紙は此の tuple の中に在る故、
tree    = ★同★                          己を含む commit/tree の40桁を己の中へ書く事は出来ぬ。
```

**∴ 40桁は★便（seq）に記した物が正★である。** 引き方は二つ、いづれも席で検算できる:

```
git rev-parse refs/heads/karo-mac/km-agent-status-maehou-ichi-wo-haisu-20260919   # → commit 40桁
git rev-parse refs/heads/karo-mac/km-agent-status-maehou-ichi-wo-haisu-20260919^{tree}  # → tree 40桁
```

★検算★ `git rev-parse <ref>` == commit（祖先を出さず先端を出す）。
★不動★ 本紙の提出後、此の tuple は動かさぬ。直す時は新しい提出として出し直す。

### ★親の取り方 ―― 掟からの逸脱を申告する★

裁334442/334443 は「★1弾1枝★（origin/main から切る）」である。本件は **★origin/main から切つて居らぬ★**。

| | 40桁 | 此の枝から見た位置 |
|---|---|---|
| origin/main | `6bde7170ce574090a6139ba2dfe3aa4cb6db8634` | 祖父 |
| 前弾 tuple（無言 fallback 是正・裁337425 ★受理済★） | `776ce71f76e228e8a94ff89e7bb13ba99686db53` | ★親★ |

**逸脱の理由（測つた事）**: 前弾 776ce71f の `scripts/agent_status.sh` blob
`3b08ae5ee4c082cee3cdd91329c8521daad82a34` の sha256 は
`4ff08530e5ea70106c04c5de1b54a49dcdadfc5a6f3468ac4b809364717faac5` ―― **★本件の前像と一字も違はず一致する★**。
∴ 親を前弾に取れば差分が★丁度一弾★に成り、origin/main に取れば★二弾分★に成る。

| 差分の取り方 | 実測 |
|---|---|
| `git diff 776ce71f76e2 <commit> -- scripts/agent_status.sh` | **110挿入 / 18削除（追107・削18）＝★本件のみ★** |
| `git diff 6bde7170 <commit> -- scripts/agent_status.sh` | 227挿入 / 39削除 ＝ 二弾分（受理済の前弾を含む） |

**∴ 判定席が「此の弾だけ」を見る差分は ★前者★ である。** 掟の字面（origin/main から切る）と
掟の目的（1提出=1弾）が此処では別を指した故、目的を採り、逸脱を本紙に明記して★裁を請ふ★。
「origin/main から切り直せ」と裁されれば刷り直す（rebase ではなく plumbing で作り直す）。

---

## ■② 成果物（artifact）

### 本体（是正した器）

| repo-relative path | sha256 | bytes / lines | mode |
|---|---|---|---|
| `scripts/agent_status.sh` | `55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31` | 21898 / 467 | 100644 |

前像 `4ff08530e5ea70106c04c5de1b54a49dcdadfc5a6f3468ac4b809364717faac5`（375行/16339byte）。
mode は disk・origin/main・HEAD・本 tuple の四所で悉く `100644`（★意図せぬ mode 変更は無し★）。

### 束（docs/evidence/karo-mac_agent-status-maehou-ichi-wo-haisu-20260919/）

| path（束内） | sha256 | bytes / lines |
|---|---|---|
| `00_nou.md` | `d77e8b9f219ad16355beb3f96051414223d27050000845ee11beeb40c92b889d` | 11800 / 158 |
| `01_teishutsu.md`（★本紙★） | ★未測（自己言及ゆゑ本紙には書けぬ ―― tuple の blob から引け）★ | ★同★ |
| `kiki/km_patch_kizu2.py` | `08ce3dd645fa3cad74173acc215349bd1575de32d4d6d8460299294a6277d8f9` | 7878 / 158 |
| `kiki/km_patch_kizu2b.py` | `49135a67b47f46bc9d8610fecc1658ca6ef96fea51df8d9c78c979f58597006a` | 3779 / 78 |
| `kiki/km_tmux_census.py` | `7c95152006a163cb28fded6c230c17059a534bfcfba7702fecf9d7afd13514d2` | 3994 / 101 |
| `kiki/km_tmux_census2.py` | `956c4669d99ba1b60bd707252f7d36ac726e5c1e3d8e05024d779f94cbf9a6a2` | 3504 / 67 |
| `kiki/km_tmux_census_jiko_nozoku.py` | `9ca49e367a5bcdf6c12391b9049378b74b6fe819c9ccac30974c726abff30e3c` | 5393 / 123 |
| `raw/10_before.txt` | `8ef089d09c3f8647eccd674aed3e4943439bb9c19b003ff72a388505fc657f86` | 2681 / 47 |
| `raw/20_after.txt` | `06a04219c247a57dcffa54e813ae89b57466cb0b7a4ccf0389a0209dd5b181ae` | 2635 / 40 |
| `raw/30_tmux_gohou.txt` | `51231dd005b8bba5e905446a9676c52bb0a93df7ee0a2604597632047f71e4d4` | 1459 / 42 |
| `raw/40_census_kou.txt` | `269b10e580b35057551190e4128b86c27e166dbeeaa61524beab02c3048ca11f` | 1574907 / 12158 |
| `raw/41_census_otsu_honntai.txt` | `03e28d5a6f20b3496cfc5109deb7a20125e3079b126a48b065c8f8f69d8ab41a` | 318993 / 2726 |
| `raw/42_census_hei_hashiru_kiki.txt` | `3ec052f91372d877070d74f19e8fed0b1c735a426114b06e00def16d105b06e0` | 19419 / 249 |

★席-local path（/Users/...）は一つも使つて居らぬ★（全て repo-relative）。

---

## ■③ 実走の raw（①と同一 tuple・同一 run）

```
cwd  = /Users/momizimac/multi-agent-shogun
```

| 何を | argv（打つた行そのまま） | rc | raw の repo path |
|---|---|---|---|
| 旧版 両対照（四路） | `bash scripts/.km_before_4ff08530.sh` 系 四射（詳細は raw 内に逐語） | 0/0/1/0 | `…/raw/10_before.txt` |
| 新版 両対照（五路） | `bash scripts/agent_status.sh` ／ `--session multiagent` ／ `--session zzzznosuch` ／ `--session multiagent-mac` ／ `--session multiagent-mac --panes 99` | 0/1/1/0/1 | `…/raw/20_after.txt` |
| tmux 語法 五事 | `tmux has-session -t '=multiagent'` 他（逐語は raw） | 1/0/0/0/1 | `…/raw/30_tmux_gohou.txt` |
| 横展開 甲（repo 全体） | `python3 -B …/kiki/km_tmux_census_jiko_nozoku.py .` | 1（★説明済★ 下記⑤） | `…/raw/40_census_kou.txt` |
| 横展開 乙（当repo 本体） | 同器 ＋ `KM_SKIP_PREFIXES=./.claude/worktrees,./queue` | 0 | `…/raw/41_census_otsu_honntai.txt` |
| 横展開 丙（★走る器★） | `python3 -B …/kiki/km_tmux_census2.py` | 0 | `…/raw/42_census_hei_hashiru_kiki.txt` |

sha256 は②の表に在る（同じ file ゆゑ二度書かぬ）。★件数の申告だけでは出して居らぬ ―― raw を置いて path で指した★。

---

## ■④ 依存の境界（repository-local）

```
lockfile = requirements.txt  sha256=46ab49a3e33f78c3f3313886a94834884a636df9589516bba066ae6122c46844  bytes=13
外部 node_modules 参照 = ★無し★
外部 symlink 参照     = ★無し★（scripts/ と本束を find -type l で歩いて 0本）
```

★本件の器は repo 外の pkg を一つも要せぬ★。走るに要るのは機の物のみ:
`/opt/homebrew/bin/tmux`（3.7b）／`/bin/bash` 3.2.57(1)-release arm64-apple-darwin25。
∴ lockfile は本件の再現に関与せぬが、欄を空にせぬ為に repo 根の物を名指して置く。

---

## ■⑤ 件数

### 正 ＝ 5/5（両対照・新版の五路が悉く宣の通り）

| 路 | 宣 | 実 | 判 |
|---|---|---|---|
| MainPC 既定（該当 session 無し） | rc=0・十一席★悉く不在★・母數行に `寫像不能(session無)=6` | 同 | ○ |
| `--session multiagent`（★当機に無い名★） | **rc=1**「完全一致で存在せぬ」・表の冠も出さぬ | 同 | ○ |
| `--session zzzznosuch` | rc=1・誤りは★一行のみ★ | 同 | ○ |
| `--session multiagent-mac`（★当たる路★） | rc=0・四席・★字面まで従来通り★ | 同 | ○ |
| `--session multiagent-mac --panes 99` | rc=1「該当する pane が無い」 | 同 | ○ |

### ★意味負★ ＝ 6/6（恒真でない事の證 ―― 旧版は此の六つで★偽を刷つて居た★）

| 旧版が刷つた席 | 実際に掴んだ物 |
|---|---|
| hideyoshi | **%68 ＝家老mac 自身** |
| ashigaru1 | **%72 ＝專任1** |
| ashigaru2 | **%7 ＝專任2** |
| ashigaru3 | **%125 ＝專任3** |
| ieyasu | index 4 が無く **%7（專任2）へ黙つて倒れた** |
| takenaka | index 5 が無く **同上** |

∴ 旧版の「通」は★恒真ではなく偽★であつた。新版は同じ六つを悉く不在と申す。

### 陽性対照（1行）

`--session multiagent-mac` ＝ ★当たる路★ → rc=0・四席・字面まで従来通り
（∴ 門を立てた事で「当たる路まで殺して居らぬ」事の證）。

### 陰性対照（1行）

`--session zzzznosuch` ＝ ★在り得ぬ名★ → rc=1・出は誤り一行のみ
（∴ 旧版は同じ入力で `PANE_TARGETS[@]: unbound variable` と死に、★表の冠は既に刷つて居た★）。

### 横展開 三母數（★並べて読むな・各々別の物を數へる★）

| 母數 | 定義 | 全file | 的 | risk | `-t %N` | `-t =名` |
|---|---|---|---|---|---|---|
| 甲 | repo 全体（`queue/` 13G・`.claude/worktrees/` を含む） | 52809（読めた 51368） | 9005 | **3501** | 69 | 2 |
| 乙 | 当repo 本体（`KM_SKIP_PREFIXES=./.claude/worktrees,./queue`） | 17141（読めた 16733） | 5380 | 1881 | 3 | 2 |
| 丙 | ★走る器★（`.sh/.py/.bats/.zsh/.bash`・器 2435本） | 35288 | ― | 甲99件/7本 → ★生きた器 5本/53件★ ／ 乙16件/11本 → ★生きた器 9本/11件★ | 0件/0本 | **2件/1本** |

**★丁（`-t =名`）が 0 から 2 へ増えたのは、本件の是正そのもの★**
（`scripts/agent_status.sh:106` と `:418` ―― 門を `has-session -t '=名'` で立てた故）。

#### ★器の疵を自ら申告する（母數を膨らませて居る）★

1. 器⑵ の `.bak` 除外は **`-bak-` を見ぬ** ∴ `shutsujin_departure.sh.karo-mac-bak-20260820T000340`（44件）が
   ★走る器★の母數へ入つた。
2. 器⑵ は「代入の先で門に守られて居る」事を見ぬ ∴ **是正済の `scripts/agent_status.sh:416` は乙で★偽陽性★**。
3. 甲の rc=1 は★説明済★ ―― 歩けなかつた1本は
   `queue/reports/ashigaru-mac-3_…/shiryou/tomari24/p10_reg_noread` の PermissionError(13)、
   ★專任3が意図して置いた読めぬ仕掛★である（器が名指しで刷る）。
4. **★未突合★**: 今朝の狭い根での乙は 12件/10本（test 4本）、本日の根 `.` での乙は 11件/9本（test 3本）。
   test 1本の去就が合はぬ。因は未測。

---

## ■⑥ 復元

```
復元後の sha256 = 55c9acd9a9f1215625d4e47afad03aed562fdeceed89b79ed415612500514e31
   （検算: git cat-file blob <commit>:scripts/agent_status.sh | shasum -a 256 == disk の sha256。★一致★）
束12本も悉く一致 = 12/12（食違 0）
再正 = 5/5（②の器を tuple から出して五路を再射しても同じ ―― ③の raw と同一）
```

### ★clean 確認 ＝ 未測（理由を測つて書く）★

雛形は `git status --porcelain -uall` が空である事を求める。**本機では席が原理的に満たせぬ。実測:**

| 器 | 行数 |
|---|---|
| `git status --porcelain -uall` | **1043行** |
| `git status --porcelain -uall --ignored` | **51087行** |
| 内 本束を指す行 | 12（悉く `!!` ＝ ignored） |
| 内 `scripts/agent_status.sh` | 1（` M`） |

**因は二つ、いづれも★席の手の外★である:**

1. **本体が ` M` に成るのは、此の worktree の HEAD が★他席の枝★だから** ――
   HEAD = `a02391d8deca9b176644ea0a1f188a91dd09e38c`
   （`ashigaru-mac-3/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917`）。
   porcelain は★HEAD と比べる★ゆゑ、当方の tuple に正しく入つて居ても ` M` と出る。
   **HEAD を当方の枝へ動かせば消えるが、其れは★專任3の作業樹を奪ふ事★ゆゑ★せぬ★。**
2. **束が `!!` に成るのは `.gitignore:7` が★裸の `*`★（allowlist 式）だから** ――
   tuple には blob として悉く入つて居る（12/12 一致を上に示した）。
   裁337509 が自ら「⒝束は git add -f が要る／之は當職の雛形の疵」と申された所と★同根★である。

∴ 雛形条3 の趣旨（★席が自力で満たせる線を受入線とせよ★）に照らし、
**clean 欄は「★未測（共有樹の HEAD が他席の枝／裸の `*`）★」と記して出す。**
代はりに★席が自力で満たせる形★で復元を證した ―― **tuple の blob と disk の sha256 の一致 13/13**。

### ★共有樹を動かして居らぬ事の證★

```
plumbing で作つた（GIT_INDEX_FILE=/tmp/km_idx_<刻> git read-tree → hash-object -w
  → update-index --add --cacheinfo → write-tree → commit-tree → update-ref）
HEAD        = a02391d8deca9b176644ea0a1f188a91dd09e38c（前後で不動・專任3の枝の儘）
共有 .git/index sha256 = 5f070053c5213936fd4bd78ce5421259e795b0d9deb6c4a44d237d1a35ff99ae（前後で不動）
worktree    = 一つも触れて居らぬ（checkout/reset/add を一度も打つて居らぬ）
```

∴ `update-index --add` が **`git add -f` の代はりを果たし**、裸の `*` の下でも束が tuple に入つた。

---

## ■⑦ 法令根拠

**★該当せず★** ―― 本件は agent 監視器の的の解き方であり、算定・記載要件に触れぬ。

---

## 附 ―― ★裁の処方の一半が実測で撃ち落された事★（報告義務ゆゑ本紙に残す）

裁337507⑶疵② の処方「**-t は =名 か %N へ**」の内、**`=名` は tmux 3.7b では★器に依つて効かぬ★**。
五事の実測（`raw/30_tmux_gohou.txt` 逐語）:

| # | 打つた行 | 出 | 判 |
|---|---|---|---|
| ⑴ | `has-session -t '=multiagent'` | rc=1「can't find session: multiagent」 | ★効く★ |
| ⑵ | `list-panes -s -t '=multiagent'` | **rc=0 で multiagent-mac の四席（%68 %72 %7 %125）** | ★効かぬ★ |
| ⑶ | `display-message -t '=zzzz:agents.0'` ／ `-t '%99999'` | **共に rc=0・出は空** | ★rc で不在を判じ得ぬ★ |
| ⑷ | `display-message -t 'multiagent:agents.4'` | **rc=0 → `%7 ashigaru-mac-2`** | ★index 溢れが現用 pane へ黙つて倒れる★ |
| ⑸ | `capture-pane -t 'multiagent:agents.4'` ／ `-t '%99999'` | rc=1「can't find pane」 | ★鳴るのは此れのみ★ |

⑵の因: 誤りの字面が "can't find **window**" ゆゑ **window 的**と解され、**session 部へ `=` が掛からぬ**。

**∴ 据ゑた形は三段である:**
1. **@agent_id 完全一致**（`list-panes -a` 悉皆列挙）で `%N` を得る ―― **n>1 は★当てず rc=3（曖昧）★**
2. 当たらねば **`has-session -t '=名'` を門**とし、閉ぢて居れば★寫像せず不在★（fail-closed）
3. standalone 路も同じ門を立て、的は `%N`・該当0本なら**空配列を触る前に rc=1**
   （★bash 3.2 は空配列の `"${arr[@]}"` を `set -u` で殺す★ ―― 旧版の死が此れ）

裁337482 にて「★名でなく識別子で当てる★は当方の指示より良い」と既に採られた形の、**standalone 路への横展開**である。

---

## 附 ―― ★別弾として出す物（本提出に混ぜぬ）★

1. **`lib/agent_status.sh` の `agent_is_busy_check`** ―― 存在確認を
   `if ! tmux display-message -t "$pane_target" -p '#{pane_id}' &>/dev/null; then return 2` で行つて居る。
   display-message は**常に rc=0** ゆゑ **`return 2` は★死んで居る★** → capture が空 → `return 1` ＝ **★偽の待機中★**。
   **lib は触れて居らぬ** ―― `scripts/inbox_watcher.sh:71`/`:1673` が source する★稼働中 watcher★ゆゑ。
   消費側 7本（`tests/unit/test_send_wakeup.bats:556/557`・`tests/e2e/e2e_bloom_routing.bats:31`・
   `scripts/ratelimit_check.sh:28`・`scripts/agent_status.sh:47`・`scripts/inbox_watcher.sh:71/1673`・
   `lib/cli_adapter.sh:1070`）を数へた上で、**呼手側で fail-closed にする形**を別弾で出す。
2. **裁337507⑶疵①** ―― `--lang/--session/--panes` の値無しで `$2: unbound variable` の死を usage へ。
   ★rc を分ける（使ひ方の誤=1 / 器の死=2）★。
3. **裁337507⑵** ―― 箱の器の母數行へ「messages鍵無=N」を常設する。
4. **横展開の是正弾** ―― 甲 生きた器 5本/53件・乙 生きた器 9本/11件（⑤に名指し）。
5. **器⑵ の `.bak` 除外が `-bak-` を見ぬ疵**。
