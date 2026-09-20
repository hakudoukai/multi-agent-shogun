# km-220 再提出 ―― 雛形 v1.3 ①〜⑦（軍師mac 判 seq342967 REVISE の療法）

## 判の逐語（seq342967 ―― 之より広くも狭くも直さぬ）

```
REVISE ②bundle_evidence。branch/tip/baseのみで、固定tree、artifact path/full SHA/bytes/lines、
同一run raw argv/rc、正負復元/cleanが未提出です。①〜⑥を一括束で提出してください。mutation=0。
```

## ★本紙は 00_shodan.md を書き替へぬ★

初提出の紙（`00_shodan.md`）は**既に納めた證**である。∴ **一字も直さぬ。**
古びた記述・誤つた記述は**本紙で名指しして訂す**（下の「★00_shodan.md の訂★」節）。

---

## ① 対象 tuple

```
ref名   = karo-mac/km-220-mon-jou4-kizon-wo-taishougai-20260920
起点    = 6bde7170ce574090a6139ba2dfe3aa4cb6db8634
origin/main(測つた刻の値) = eab623bc017c01cfd4da1e2dce9119f9090ebfc7
commit40 = ★納便で宣す★（本紙を含む commit ゆゑ本紙には書き得ぬ・自己言及）
tree40   = ★納便で宣す★（同上）
```

**根拠**：雛形 v1.3 L138 逐語「★①の commit/tree は「納便」で宣してよい★」。
**受け手の検算の手**：`git rev-parse <ref名>` と `git rev-parse <ref名>^{tree}` が
納便の40桁と一致する事を己の器で測れる。

## ② 成果物（artifact ―― path / sha256 / bytes / lines）

### 本弾の器（判定の対象そのもの）

```
path   = scripts/checks/karo_mac_dasumae_gate.sh
sha256 = 5c46ef7b5fbc8d4f0f13e394a93e3a4d9bef6c8a4f14f045480c490c8b9421e1
bytes  = 23477   lines = 400
blob   = 484e7a36aa8145925cf8f86942e29357d249db53（枝の版）
改修前 = 3b8b7182566cc8c4e81533d27d2f6c5d98a9b56429d2d7205dfca9d3a9295bac / 339行 / 19268 B
bash -n = rc=0
★main/origin/main の現版は「改修前」と★同一物★である★
  blob   = 04672e15b1edf4a02b7cea1f4f32cfb9a64e34d5
  sha256 = 3b8b7182566cc8c4e81533d27d2f6c5d98a9b56429d2d7205dfca9d3a9295bac / 19268 B
  ―― git show 04672e15… を砂箱へ取り出して測り、改修前の sha256 と★一字一句一致★した(rc=0)。
  ★∴ 枝は main から切られ、差は當職の改修分のみである事が sha で示された。★
  ★當職は本紙の初稿で此の二つを別物の如く並べた ―― 測れば同一であつた。之は本紙の疵であり訂した。★
```

### 本紙の為に新たに据ゑた器（argv を焼く為・二本）

```
path   = docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/utsuwa/hashiru.sh
sha256 = 626522b9949c02b50a8e2db93947cc422cf9ab400c1783c9547d29ca9007ee0b
bytes  = 2101    lines = 39     sh -n = rc=0

path   = docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/utsuwa/genbutsu.sh
sha256 = bccc573328eca2312cd37941d4d83914b3e6edbae55df3e4d91573dad7d078c4
bytes  = 1371    lines = 18     bash -n = rc=0
```

### 本紙の為に新たに彫つた對照紙（一本）

```
path   = docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/fixtures/saitei_taishou_20260920.txt
sha256 = dab36064c546640565edb4d129bde78598c575d2a41f0a86390098b3ac5ab383
bytes  = 91      lines = 0（★EOF 改行を意図して持たぬ★ ―― 直すな）
```

### 残りの紙（初提出の紙32本＋raw2 の48本）は ★臺帳が担ふ★

**之を一行で宣す** ―― `manifest.txt` が束内の全紙の `path= sha256= bytes= lines=` を持つ。
**臺帳自身の sha256/bytes/lines と、本紙の sha256/bytes/lines は ★納便で宣す★**
（紙は己を含む臺帳の數を書けぬ・臺帳は本紙の sha を載せる ∴ 互ひに追ふ形に成る）。

**★束の紙の総数と臺帳の行数の一致は當職が己で数へて納便に書く★**（門に代らせぬ）。

## ③ 実走の raw ―― ★argv 其の儘★（本節が判 seq342967 の核心である）

```
cwd  = /Users/momizimac/wt/km-220-jou4-kizon-taishougai
器   = docs/evidence/…/utsuwa/hashiru.sh（走り手・argv を .argv へ焼く）
産   = raw2/<札>.argv / .out / .err / .rc  ―― ★四つ組で一走り★
.argv が持つ物 = 札 / cwd / 刻(UTC) / env DASUMAE_JOU4_SCOPE / env KM_GATE_MANIFEST_BASE
                 / argc / argv[1..argc] を★一行ずつ★ / rc
```

| 札 | 何の對照か | argc | 鳴り | 條④對象外 | rc |
|---|---|---|---|---|---|
| `C01_yousei_mitsuiseki` | **陽性①** repo 内・未追跡の紙 | 4 | 1 | 0 | **1** |
| `C02_insei_kizon` | **陰性** 同じ紙を彫つた後（追跡済・差無し＝既存） | 4 | 0 | 1 | **0** |
| `C03_kagyaku_scope_all` | **可逆** 同じ紙へ `DASUMAE_JOU4_SCOPE=all` | 4 | 1 | 0 | **1** |
| `C04_tsuiseki_zumi_sa_ari` | **差有り** 追跡済だが HEAD と差有り | 4 | 1 | 0 | **1** |
| `C05_yousei_git_no_soto` | **陽性②** git の外の紙 | 4 | 1 | 0 | **1** |
| `C06_genbutsu_km209` | **現物** 席1 km-209 束（68本） | 71 | 0 | 29 | **0** |
| `C06b_genbutsu_km209_evidence_zentai` | **現物** 同席 `docs/evidence` 全体（87本） | 90 | 0 | 29 | **0** |
| `C07_genbutsu_km213` | **現物** 席1 km-213 束（37本） | 40 | 0 | 5 | **0** |
| `C07b_genbutsu_km213_evidence_zentai` | **現物** 同席 `docs/evidence` 全体（56本） | 59 | 0 | 5 | **0** |
| `C08_km209_scope_all` | **意味負** 同じ68本へ `SCOPE=all` | 71 | 29 | 0 | **1** |
| `C09_km213_scope_all` | **意味負** 同じ37本へ `SCOPE=all` | 40 | 5 | 0 | **1** |
| `C10_selftest` | 器自身の自己検め | 3 | 1 | 0 | **0** |

**★argc は argv の全数であり file の本数ではない★** ―― `argv[1]=/bin/bash` `argv[2]=<門>`
`argv[3]=--` の三つが先に立つ ∴ **file の本数 = argc − 3**（C10 は `--selftest` ゆゑ argc=3）。
**鳴りの数へ方**：`.err` の `^★` 行の全数から結語の一行（`^★出す前`）を引いた数。
**★C10 の鳴り 1 は器の内部の陽性対照が鳴つた行であり、疵ではない★**
（`.err` 末尾逐語「★自己検め通 ―― 陽性対照は鳴り・負対照は鳴らず。器として使へる。★」）。

### ★一本の對照紙が四状態を通る形に据ゑた★

`fixtures/saitei_taishou_20260920.txt` 一本が
⑴彫る前＝未追跡→**鳴る**(C01) ⑵彫つた後＝追跡済・差無し→**對象外**(C02)
⑶`SCOPE=all`→**旧挙動で鳴る**(C03) ⑷一字足して差有り→**當てる**(C04) を通る。
**C04 の後に `git checkout --` で戻し、`git diff --quiet HEAD` rc=0・bytes=91 を検めた。**

### ★他席の樹は讀取のみ★

`genbutsu.sh` は `find <樹>/<束> -type f -print0 | sort -z` で母數を作り、
其の path を**當職の門へ argv で渡した**のみ。**他席の HEAD / index / 作業樹は不動。**

```
wt/a1-km209 : HEAD 7be60c734f76fd7187c9abd2e5bd5b6e7cd0e4f9
wt/a1-km213 : HEAD 66741317019a7388be7a2747dfb7ee12316523e0
```

## ④ 依存の境界（lockfile）

```
lockfile = ★該当無し（N/A）★ ―― 理由: 本弾の成果物は POSIX shell script 三本のみであり、
           package.json / requirements.txt / Gemfile / Cargo.toml の何れも持たぬ。
           ∴ 固定すべき依存の版が存在せぬ。
外部 node_modules / 外部 symlink = 無し
呼ぶ器（悉く repo 内） = scripts/checks/karo_mac_fukashiji.py（判じ手）
                        scripts/checks/karo_mac_manifest_verify.py（條①）
実行系 = /bin/bash 3.2（macOS 既定・`declare -A` 使へず・本弾は用ゐず）/ /usr/bin/python3
```

## ⑤ 件数

```
正     = 34/34 ―― C06(29) + C07(5) の全 file が「既存」と判ぜられ對象外・鳴り 0・rc=0
意味負 = 34/34 ―― 同じ二束へ SCOPE=all を渡すと C08(29) + C09(5) が悉く鳴り rc=1
         ★∴ 新條④は「常に對象外にする」恒真ではない★
陽性対照 = ★二形★ C01 repo内・未追跡(rc=1) / C05 git の外(rc=1)
           ―― 二因が重なる紙一本では「どちらで鳴つたか」を判じられぬゆゑ分けた
陰性対照 = C02 rc=0 ―― 逐語「★條④は 1/1 本を既存として對象外にした★」
差有り対照 = C04 rc=1 ―― ★fail-open の向きへ倒れて居らぬ證★
自己検め = C10 rc=0
```

**★同じ 29 と 5 が二つの歩き根で出る事の意味★** ―― C06(68本)と C06b(87本)で
對象外は共に 29。∴ **對象外の 29 本は km-209 束の中に在り、もう一つの束
（`km-manifest-append-track-20260917`・差 19 本）には條④に鳴る紙が無い。**
**之は「母數を広げても數が動かぬ」事の實測であり、數の名を取り違へぬ為に要る。**

## ⑥ 復元（clean ―― ★porcelain を二形で測つた★）

```
cmd = git status --porcelain -uall      → rc=0 / ★1行★
  ' M docs/runbooks/ERR-EKARTE-001.md'
cmd = git status --porcelain --ignored  → rc=0 / ★3行★
  ' M docs/runbooks/ERR-EKARTE-001.md'
  '!! docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/raw2/'
  '!! docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/utsuwa/'
```

**★`-uall` だけでは本紙の raw2/ と utsuwa/ が一行も見えぬ★** ―― `.gitignore` の7行目が
**裸の `*`**（全除外の allowlist 形）ゆゑ、新造の dir は `!!`（ignored）に落ちる。
∴ **彫るには `git add -f` が必須**であり、**`-uall` を「未追跡が無い證」と讀めば偽の青に成る。**
**之が「-uall と --ignored の両方を書け」という雛形の条の實地の意味である。**

### ★` M docs/runbooks/ERR-EKARTE-001.md` の因を測つた（當職の物でない一行・第一条）★

```
當職の樹の index : git ls-files docs/runbooks/ → ★ERR-EKARTE-001.md（大文字）が在る★
                   かつ err-ekarte-001.md（小文字）も在る = ★双子★
席2 の樹(eab623bc=origin/main) の index : ★大文字は無い★（11本）
席2 の樹の porcelain -uall = rc=0 / ★0行★
```

**∴ 因は「case-insensitive な file 系で双子が一つの実体を指す」事であり、
母數（base commit）が違へば行数も違ふ。** 當職の枝の起点 `6bde7170` には大文字が index に在り、
`origin/main` `eab623bc` は**大文字を index から外す commit を既に載せて居る**。
**∴ 當職の1行と席2の0行は★両方正しい★**（同じ述語を違ふ母數へ当てた）。
**本弾では一指も触れぬ** ―― 双子の直しの裁は未だ下りて居らぬ（別弾）。

### 復元の手（受け手が己の手で踏める形）

```
1. git fetch && git checkout karo-mac/km-220-mon-jou4-kizon-wo-taishougai-20260920
2. shasum -a 256 scripts/checks/karo_mac_dasumae_gate.sh
   → 5c46ef7b5fbc8d4f0f13e394a93e3a4d9bef6c8a4f14f045480c490c8b9421e1
3. bash -n scripts/checks/karo_mac_dasumae_gate.sh                 → rc=0
4. bash scripts/checks/karo_mac_dasumae_gate.sh --selftest          → rc=0
5. 陰性: bash …gate.sh -- docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/fixtures/saitei_taishou_20260920.txt
        → rc=0・「條④は 1/1 本を既存として對象外」
6. 可逆: DASUMAE_JOU4_SCOPE=all bash …gate.sh -- <同じ紙>          → rc=1
7. 現物: bash docs/evidence/…/utsuwa/genbutsu.sh <札> <他席の樹> docs/evidence <門>
        → 母數と rc が raw2/<札>.argv / .rc と一致する
```

**★再正は「見做し」ではなく測定で示す★** ―― 上の 2〜7 が `raw2/` の `.rc` と
同じ値を返す事を受け手が己の器で確かめられる形に置いた（`.argv` に argv 其の儘が在る）。

## ⑦ 法令根拠

```
N/A ―― 理由: 本弾は開発器（出す前門）の射程の直しであり、
       患者情報・保険請求・電子カルテ三原則の何れにも触れぬ。
```

---

## ★00_shodan.md の訂（書き替へずに此処へ書く）★

### 訂① ★紙と raw が別の走りであつた★（判 seq342967 の指す実害）

`00_shodan.md` ③ の表は `40_genbutsu_km209` の argv を `run_gate -- <87本>`・rc=0・
「對象外29/87」と書いた。**當職は本日、其の raw の中を数へた。**

```
raw/40_genbutsu_km209.err の結語（逐語）
  條②末尾不可視字 / 條③CR混入 = 全file(★29本★)通 ―― ★條④は 29/29 本を…★
raw/41_genbutsu_km213.err の結語（逐語）
  … = 全file(★5本★)通 ―― ★條④は 5/5 本を…★
```

**∴ raw に残つて居るのは「29本」「5本」の走りであり、紙が書いた「87本」「56本」ではない。**
本日 C06b で 87本を渡し直すと結語は「全file(87本)通・29/87」と出て**紙と逐語一致した**。
**∴ 紙の数は誤りではない ―― 誤りは「紙の数を出した走りの raw を置かなかつた」事である。**
**★argv を焼かなかつた故に、當職自身が半日後に己の走りを再現できなかつた★**
（`grep -rl argv raw/` = 0本）。**之が雛形 ③「同一 run の raw」の条が守る物である。**
**療法**：`hashiru.sh` が argv を焼く形へ据ゑ、12走りの四つ組を `raw2/` に置いた。

### 訂② 臺帳の数が古びた

`00_shodan.md` は「臺帳 = manifest.txt 34行(冠2 + 紙32行) / 4213B」と書く。
**本弾で臺帳を建て直した故、此の数は初提出の刻の値として古びた。**
**新しい値は納便で宣す**（紙は己を含む臺帳の數を書けぬ）。

### 訂③ 門の走りは二版で取る

`00_shodan.md` は本束へ当てた門を一走りしか書かぬ（枝の版）。
**本弾では枝の版と main の現版の★両方★を走らせ、`raw2/mon_*` に置いた。**
**main の現版では fixtures が鳴つて rc≠0 に成るのが★正しい出目★である**
（條④を「既存は對象外」へ直すのが本弾の目的ゆゑ、直す前の版は鳴つて当然）。
**∴ 「出す前に main 版の門を通せ」は本弾に限り「rc を測つて宣せ」と讀む。**
**之を黙つて枝の版だけで通すのは、門を己に有利な版で選ぶ事に当たる ∴ 両方置く。**

## ★當職の落度（本日新たに測つた分・己の分を先に書く）★

### 落度⑦ 紙の数と raw の数を突き合はせずに納めた

初提出の時、當職は紙へ「87本」と書き、raw には「29本」の走りを置いた。
**両方を己で数へれば其の場で判つた。** 數の規律は「母數を宣せ」と言ふが、
**本件は其の前段 ―― 紙と raw が同じ走りかを検めなかつた事である。**

### 落度⑧ argv を焼かぬ器で 26本の raw を作つた

`raw/` の26本は out/err/rc を持つが argv を持たぬ。
**∴ 後の者も當職も「何を渡したか」を raw から取れぬ。**
**療法**：走り手が argv を焼く形へ据ゑた（`utsuwa/hashiru.sh`）。

### 落度⑨ `-uall` を clean の証に使ひかけた

`.gitignore` の裸の `*` ゆゑ新造 dir は `-uall` に出ぬ。
**∴ `-uall` 1行を「未追跡無し」と讀めば偽の青である。** `--ignored` を併せて初めて見える。

---

## ★臺帳を建てた器の自己検めが落ちて居る（rc=1）―― 隠さず宣す★

本弾の臺帳は `scripts/checks/karo_mac_manifest_append.py`（★行を足す唯一の器★・裁321856）で
建て直した。**建てた直後に其の器の `--selftest` を走らせたら rc=1 で落ちた。** 出目:

```
甲 陽性(空白無)      rc=0 書=1 括=無  一致=True   ―― 期待通
乙 往復(空白有)      rc=0 書=1 括つた 一致=True   ―― 期待通
丙 括らぬ空白名を讀ませる → ['a b.txt'] ★切り落す(期待 'a b.txt' でない)★ 切落=False ―― ★落ちた★
丁 陰性(二重引用符)  rc=3 書=0 臺帳不変=True     ―― 期待通
戊 陰性(一重引用符)  rc=3 書=0 臺帳不変=True     ―― 期待通
己 全か無か          rc=3 書=0 臺帳不変=True     ―― 期待通
庚 既存旧形は残る    rc=0 書=1 残存=True         ―― 期待通
★selftest 落★
```

**∴ 落ちたのは丙★一つだけ★であり、丙は「★讀み手★が括らぬ空白名を切り落す」事を期待する対照である。**
**書き手の六対照（甲乙丁戊己庚）は悉く期待通り ―― ★行を足す機能そのものは健全★。**

### 丙が落ちる因（★推定であり、本弾では測り切つて居らぬ★）

`karo_mac_manifest_verify.py`（讀み手）を三所で測つた:

```
己の樹 disk = 9e831137f1d33f41b6ba88414b26d44dfb93ebc9c544d263f7c0c1d1234e4d8f
己の樹 HEAD = 9e831137f1d33f41b6ba88414b26d44dfb93ebc9c544d263f7c0c1d1234e4d8f
origin/main = 9e831137f1d33f41b6ba88414b26d44dfb93ebc9c544d263f7c0c1d1234e4d8f
★共有樹 disk = a507c998c7bd648543a8dcb8643ba1188254800b039cdad76f4953ef34d5fa41（★別版・未彫★）★
```

**∴ 己の樹で走らせた讀み手は main 版である。其の main 版が空白名を★切り落さなかつた★（丙 切落=False）。**
**∴ 丙 の期待「切り落す」は、讀み手が直つた事に★対照が追随して居らぬ★形と見える ―― 即ち★偽の赤★。**
**★但し之は推定である★**：丙 の期待が何故書かれたかの由来を本弾では辿つて居らぬ。
**∴ 別弾として起こす**（器の自己検めを赤の儘据ゑるのは静かな失敗に近い）。

### 本弾の臺帳の正当性に及ぶか ―― ★及ばぬ。測つた★

```
束の中に空白を含む名が在るか = ★0件★
  rc=0 / 歩き根=docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920
  刻(UTC)=2026-09-20T02:57:20Z / 深さ=無制限 / type=f
建立の出目 = 「書いた=84 行 / 母數=84 / ★括つた(空白名ゆゑ必須)=0★ / 臺帳=manifest.txt(新たに建てた)」
```

**∴ 丙 が問ふ「括らぬ空白名」は本束に一本も無い ∴ 本弾の 84 行は丙の射程外である。**

### ★共有樹 disk の讀み手が main と違ふ事も宣す（第一条・調べる・消さぬ・咎めぬ）★

共有樹 `/Users/momizimac/multi-agent-shogun` の disk 版 `a507c998…` は main に無い。
**本弾では讀取で sha256 を測つたのみ ―― 一指も触れて居らぬ。** 中身の差は未測。
**∴ 別弾**（出所不明の物は調べる・消すな・戻すな・咎めるな）。

## 臺帳と本紙の値

```
臺帳  = docs/evidence/…/manifest.txt   ★納便で宣す★（冠2 + path行 N ―― 紙は己を含む臺帳の數を書けぬ）
本紙  = docs/evidence/…/01_saiteishutsu_v13_20260920.md  ★納便で宣す★（臺帳が本紙の sha を載せる）
束の disk 全本数・臺帳の path 行数・其の一致 = ★納便で宣し、當職が己で数へた事を明記する★
```

## 門の走り（★臺帳が建つた後ゆゑ臺帳の外★・雛形 v1.3 第4項）

```
raw2/90_mon_edaban.{argv,out,err,rc}   己の枝の版 blob 484e7a36aa8145925cf8f86942e29357d249db53
raw2/91_mon_mainban.{argv,out,err,rc}  main の現版 blob 04672e15b1edf4a02b7cea1f4f32cfb9a64e34d5
rc = ★納便で宣す★（本紙を彫つた後に走るゆゑ本紙には書き得ぬ）
★main 版は fixtures で鳴つて rc≠0 に成る筈である ―― 之が本弾の因そのものゆゑ隠さず測る★
```

---

## ★門を二版で通した ―― 本弾の因と療法が一枚で測れた★

同じ **85本**（臺帳 `manifest.txt` 自身 + 84紙）を、**同じ臺帳**・**同じ基点**で二版に通した。

| 札 | 門の版 | 條① | 條②③ | 條④ | 鳴り | rc |
|---|---|---|---|---|---|---|
| `92_mon_edaban_daichou_ari` | 枝 `5c46ef7b…` | 一致 | 85本通 | **對象外 4/85** | **0** | **0 = 通** |
| `93_mon_mainban_daichou_ari` | main `3b8b7182…`(blob `04672e15…`) | 一致 | ―（條④で落ちた） | **對象外 0** | **4** | **1 = 落** |

**★差は條④の一箇所のみである★**（條①は両版で「一致(manifest_verify.py rc=0)」・條⑤は両版で byte和 174419）。

### 鳴つた4本と對象外にした4本は★逐語で同一集合★（`diff` rc=0 で照合した）

```
fixtures/saitei_taishou_20260920.txt
fixtures/taishou_eof_kaigyou_nashi.txt
fixtures/taishou_repo_nai_mitsuiseki.txt
fixtures/taishou_tsuiseki_zumi_sa_ari.txt
```

main 版の逐語: `★EOF改行が無い(0) ―― fixtures/saitei_taishou_20260920.txt★`（他3本も同形）
枝  版の逐語: `條④ 對象外 ―― fixtures/saitei_taishou_20260920.txt は既存(追跡済・HEADと差無し)・札=1(裁 seq339959。悉く当てるには DASUMAE_JOU4_SCOPE=all)`

**∴ 本弾の直しは「追跡済・HEAD と差無しの既存 file を條④の射程から外す」一点であり、
其の効きは★4本／85本★という形で測れた。副作用として他の 81 本の判定は一字も変はつて居らぬ
（條②③は両版で全 85本を歩き、條⑤の byte和も同一）。**

### ★出す前に main 版の門は落ちる ―― 之を隠さず宣す★

**main 版で rc=1 に成るのは正しい出目である。** 本弾は其の条を直す弾であり、
**直す前の版が對照紙で鳴らねば「直す物が無かつた」事に成る。**
∴ 「出す前に門を通せ」の條は、本弾に限り **「両版で測り、差を宣せ」** と読む。
**枝の版では鳴り0・rc=0 で通つて居る（`92_…`）。**

## ★當職の落度（門を走らせる段で二つ踏んだ・測りを二度作り直した）★

### 落度⑩ 門の第一引数に `--` を渡し、★條①を己で飛ばした★

門の usage 逐語: `bash scripts/checks/karo_mac_dasumae_gate.sh <manifest|--> <file...>`
（註の逐語: `manifest = 台帳path(照合する台帳が無ければ "--" を渡す→條①はskip扱ひで表示)`）

**當職は最初の走り（`90_mon_edaban` / `91_mon_mainban`）で `--` を渡した。**
結果の逐語は `條① 台帳とdiskの差 = スキップ(台帳未指定)` ―― **臺帳照合が一度も走らなかつた。**
`KM_GATE_MANIFEST_BASE=.` は環境に立てて居た（`.argv` に `env KM_GATE_MANIFEST_BASE=.` と焼かれて居る）
が、**基点だけ渡して臺帳そのものを渡さねば條①は動かぬ。**

**★且つ之は當職が專任2へ出した命の不備でもある★** ―― `queue/tasks/ashigaru-mac-2.yaml` に當職は
「`KM_GATE_MANIFEST_BASE=.` で束の中から呼び」と書き、**第一引数の `<manifest>` を書かなかつた**。
**∴ 專任2 が同じ穴を踏み得る。當職の落度として名指しし、別便で訂す。**

### 落度⑪ main 版の門を★判じ手から離れた砂箱★へ置いて走らせ、rc=1 を誤読しかけた

門は判じ手を `$(dirname "$0")/karo_mac_fukashiji.py` で探す（逐語）。
砂箱に置いた門は判じ手を見つけられず、85本すべてで
`★條②④ 測れぬ(不可視字の判じ手 rc=2・出目「… No such file or directory」)★ ★測れぬは通さぬ(default-deny)★`
と鳴り、**鳴り85／rc=1** に成つた（`91_mon_mainban`）。

**★之を「main 版が條④で落ちた」と読めば偽の結論だつた★** ―― 落ちた因は判じ手の不在である。
**療法**：main 版を判じ手の隣（己の樹の `scripts/checks/` 配下）へ別名で写し、走らせ、**走り終へて退けた**
（控は砂箱に在る・束の中にも commit にも入れて居らぬ）。取り直した札が `93_…` である。

**★門が default-deny で落ちた事自体は器の正しい振舞ひである★**（測れぬは通さぬ）。
**誤つたのは當職の置き場であり、器ではない。**

### ★誤つた二走り（`90_` / `91_`）を消さずに束へ残す★

**測り損ねた走りも證である。** 消せば「當職が一度で正しく測つた」様に見え、之は偽りに成る。
∴ `raw2/90_mon_edaban.*` と `raw2/91_mon_mainban.*` は**誤つた走りとして束に残す**。
**判ずる側は `92_` / `93_` を本測として読み、`90_` / `91_` は當職の落度の證として読まれたい。**
（四札 16 file は悉く**臺帳の外** ―― 臺帳が建つた後に内容が決まる紙ゆゑ・雛形 v1.3 第4項）

---

## ★⑥ の値は刻で動く ―― 上に書いた 1行/3行 は「raw2 を取り終へた刻」の値である★

上の ⑥ 節の `-uall` 1行 / `--ignored` 3行 は、**`raw2/` の12走りを取り終へ、
本紙と臺帳を未だ作つて居なかつた刻**の測りである。**其の後に本紙を書き、臺帳を建て直し、
門を五札走らせた故、同じ命は違ふ數を返す。** 彫る直前に測り直した:

```
刻(UTC)=彫る直前 ／ 歩き根=/Users/momizimac/wt/km-220-jou4-kizon-taishougai
cmd = git status --porcelain -uall      → rc=0 / ★2行★
  ' M docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/manifest.txt'
  ' M docs/runbooks/ERR-EKARTE-001.md'
cmd = git status --porcelain --ignored  → rc=0 / ★5行★
  上の2行 ＋
  '!! docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/01_saiteishutsu_v13_20260920.md'
  '!! docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/raw2/'
  '!! docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/utsuwa/'
束の disk 全本数(彫る直前) = ★107本★（臺帳に載る84 + 臺帳自身1 + raw/80_* 2 + 門の五札 20 = 107）
彫る前の先端 = f955803d9286498952ae3d4f392a545e6a3fe826
```

**★彫つた後の `-uall` / `--ignored` の行数は「納便」で宣す★** ―― 復元(clean)の条は
「彫つた後に樹が清いか」を問ふ條であり、**彫る前の紙に書ける値ではない。**
**残る筈の一行は ` M docs/runbooks/ERR-EKARTE-001.md` のみ**であり、之は當職の物でない
（雙子の直しの裁は未だ下りて居らぬ ∴ 一指も触れぬ）。**其の一行が残る事も納便で宣す。**

**★之も當職の落度である★** ―― ⑥ を「一度測れば済む値」として紙の中段へ書いた。
**復元は最後に測る條であり、紙の途中に置けば必ず古びる。** 次弾では ⑥ を納便専用の節にする。
