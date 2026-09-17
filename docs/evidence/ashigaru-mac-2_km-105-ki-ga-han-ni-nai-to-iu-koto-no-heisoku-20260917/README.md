# km-105 ―― ★器が幹に無いといふ事★ の閉包(專任2 第47弾・臺帳外の紙)

的(札 逐語): 「★此の機が一つ失せた時、臺帳は建ち、門は鳴るか★」

## ★答(一行)★

★臺帳は建たぬ。門は鳴る ―― 然し鳴らす物が無い。且つ幹の照合器は、通る筈の束に鳴る。★

## ⑴ 閉包の定義(★測る前に宣つた★ ―― `_inst/00_heihou.py` の docstring が原本)

> 「★一つの束の臺帳を建て、出す前門を通し、其の出目を検めるまでに、實際に process として
> 起動される器★」。起点は二本のみ ―― `karo_mac_manifest_append.py` と
> `karo_mac_dasumae_gate.sh`。此の二本から ★呼出の連鎖を辿つて★ 閉ぢる。

★宣の外(測らぬと明記した物)★: ⑴便の器(inbox_write.sh 等 ―― 臺帳も門も呼ばぬ) ⑵束ごとの私器
⑶番人(hook)類 ―― ★但し `context_usage_warn.sh` は家老が「中身異」と名指した ∴ ★丁★ として
表には載せ、甲乙丙の判じからは外す。「外した」は「無い」の意に非ず★ ⑷python 標準ライブラリ
⑸`/bin/sh`・git・grep 等の系の器。

### 閉包 = ★3本★ / 辺 = ★3本★

| 器 | 如何にして閉包へ入つたか |
|---|---|
| `scripts/checks/karo_mac_dasumae_gate.sh` | 起点 |
| `scripts/checks/karo_mac_manifest_append.py` | 起点 |
| `scripts/checks/karo_mac_manifest_verify.py` | `gate.sh:209,213` が `$(dirname "$0")/` で呼ぶ／`append.py:142 _yomite()` が `importlib.util.spec_from_file_location` で ★path 直読み★ |

★裏取り(`_inst/01_uraura.py`)★: 別の規(字面の basename を悉く拾ふ)で 3本 ―― ★表 ⊆ 裏 = 是★。
陽性対照 `_fixture/09_taisho.sh` = 4形を植ゑて ★4件 拾ひ・註の中の1件は拾はず★。

## ⑵ 五面(`_inst/10_gomen.py` / 刻 2026-09-17T16:39:25+0900)

| 器 | 面1 disk | 面2 index | 面3 object | 面4 origin/main | 面5 幹PR#20 `0bb92e2b800c` |
|---|---|---|---|---|---|
| `karo_mac_dasumae_gate.sh` | 在 16261byte `054c442eaee3886b2283f98f7c3a1ab8cb813b68` | 在 `9cd550fc2cf963ca0475b3448bb33483b9aede6b` ★相違★ | ★在★ rc=0 | ★path 無★ | ★在★ `9cd550fc2cf963ca0475b3448bb33483b9aede6b` ★中身異★ |
| `karo_mac_manifest_verify.py` | 在 10965byte `ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579` | 在 `b19ec9ea259653d9e65d052459128c635a44e93f` ★相違★ | ★在★ rc=0 | 在 `b19ec9ea259653d9e65d052459128c635a44e93f` ★中身異★ | 在 同左 ★中身異★ |
| `karo_mac_manifest_append.py` | 在 10959byte `b56d6576c82212c155980968d4ec1e0a8c5c7427` | ★外★ | ★在★ rc=0 | ★path 無★ | ★path 無★ |
| ★丁★ `context_usage_warn.sh` | 在 6709byte `3212039429ae27aab4cdbd41c3f5e146a10f4ea8` | 在 `ce712f785c8fb34e13d19ccb9ff2166412930481` ★相違★ | ★在★ rc=0 | 在 `ce712f785c8fb34e13d19ccb9ff2166412930481` ★中身異★ | 在 同左 ★中身異★ |

面3 は ★中身から blob sha1 を組み `cat-file -e`★(`hash-object` は ★書く★ 故 用ゐぬ ―― 禁は読取のみ)。
面4面5 の `ls-tree` は悉く `git -C <根>` + `--full-tree`、且つ ★出目への対照★
(`pane_identity.sh` が cat-file rc=0 で在り、★同じ ls-tree の出目にも在る★ 事を検め、無ければ止まる)。

## ⑶ 甲乙丙丁

- ★甲(幹が運ぶ)= 2本★ `karo_mac_dasumae_gate.sh` / `karo_mac_manifest_verify.py`。
  ★但し「運ぶ」は「同じ物を運ぶ」の意に非ず★ ―― 二本とも幹の版は古い(下の⑸)。
- ★乙(小PR一本で運べる・repo 内)= 1本★ `karo_mac_manifest_append.py`。
  因は `.gitignore:7` の裸の `*`(許し形)。★許し行を一行足せば足る★(`_raw/30_tsugi.md`)。
  ★家老mac が既に同じ形で書いて居る★ = `61a9fe1c18beffddef6b40503766ba726b8b0a05`
  (枝 `refs/heads/karo-mac/manifest-append-track-20260917` / 16:18:13 / ★遠隔追跡枝 0本 = 未押★)。
- ★丙(repo 外ゆゑ PR では治らぬ)= 器は 0本★。閉包3本は悉く repo の下に在る。
  ★然れど「器」ではなく「★器が踏む地面★」に 4種 在る★(`_inst/23_hei.py`):
  `stat -f %z`(BSD書式・gate.sh:107,109) / `tr -d '[:space:]'`(U+3000 の讀みが系で分かれる・4箇所) /
  `xxd`(coreutils に非ず・gate.sh:155,163) / `timeout`(stock macOS に無し・`$TIMEOUT_BIN` 経由)。
- ★丁(宣の外・表にのみ載せる)= 1本★ `context_usage_warn.sh`(幹は運ぶ・版は +48 -3 古い)。

## ⑷ 乙の最小 patch → `_raw/30_tsugi.md`(★紙のみ・据ゑず・commit せず・戻し方一行付★)

## ⑸ ★丙に就き「では何が起きるか」(一行づつ)★

- `stat -f %z` ―― GNU 系では ★illegal option★ ∴ 寸法が取れず ★條⑤(byte和)が倒れる★。
- `tr -d '[:space:]'` ―― 本機(BSD)は U+3000 を空白と讀む(實測 残0byte)が GNU は讀まぬ
  ∴ ★同じ値が blank と value に分かれ、閾の判じが系で変る★。
- `xxd` ―― 無い系では `2>/dev/null` に呑まれ ★條④(EOF改行)が無言で空を返す★。
- `timeout` ―― stock macOS に無く、倒した先の振舞ひは系で変る。
- ★之等は repo の中に版が無い ∴ PR では治らぬ。治せると書かぬ。★
  ★治る道が在るとすれば「PR」ではなく「系を揃へる」か「器の中で方言を検めて倒す」かの二つである。★

## ★的への答(實測・`_inst/20_kotae.py` `_inst/21_shizuka.py`)★

幹PR#20 の版だけを己の束へ取り出し、試料の束で ★實際に走らせた★。

1. ★臺帳は建たぬ★ ―― 幹に `append.py` が無い(`git show` rc=128)。
   零の四札: 陽性対照=手許の append.py は同じ路で rc=0・393byte の臺帳を建てた／
   根=`0bb92e2b800c` 深さ=1／rc=128／刻=2026-09-17T16:43:06+0900。
2. ★門は鳴る★ ―― 幹の gate.sh は rc=0「★出す前 門 通。出してよい。★」。
   ★但し臺帳は手許の append.py で建てた物を食はせた★。幹だけの世界では ★食はせる物が無い★。
3. ★より静かな欠★ ―― 同じ臺帳・同じ file を二つの verify.py に食はせると
   ★rc が反転する★:

   | 試料 | 幹 127行 | 手許 198行 |
   |---|---|---|
   | 引用符で括つた既存行 `path="e.txt"` | ★rc=1★ 実体無1 | ★rc=0★ 一致1・旧形1行「★拒んで居らぬ★」 |
   | 空白を含む path `path=c d.txt` | rc=1 実体無1 | rc=1 実体無1(★両版とも落ちる★) |

   裁 seq321353⑴ は「引用符禁は ★新規に書く行★ にのみ適用＝既存行は拒否せず」と定める。
   ★幹の版は其の裁より古く、通る筈の束に鳴る。★
   被害半径(`_inst/22_hankei.py`)= `docs/evidence/*/MANIFEST.txt` 37本中 ★1本★
   (`docs/evidence/km-83-shikii-de-wa-mamorenu-tane-wo-mitsuke-yo-20260917` 2行)。

## ★家老の測りへの照らし(疑つて良い・覆したら手柄)★

| 家老の値 | 專任2 の再測 | 判じ |
|---|---|---|
| scripts/checks の .py/.sh disk 16本 | 16本 | ★一致★ |
| index 15本 / index 外は append.py 1本のみ | 15本 / 同 | ★一致★ |
| origin/main と食ひ違ふ 5本(path無3・中身異2) | 5本(path無3・中身異2)・sha も悉く一致 | ★一致★ |
| 親裁「append.py は ★object すら無し★(cat-file -e rc=1)」 | ★今は rc=0★ | ★覆る★ |

★覆りの中身★: blob `b56d6576c82212c155980968d4ec1e0a8c5c7427` は今 ★在る★。
且つ ★ref から到達する★ ―― 家老mac 自身の枝 `61a9fe1c…`(16:18:13)が運んで居る。
∴ 「object すら無し」は ★km-104 の刻には真であり、今は偽★ である。
★因は本紙では断ぜぬ★(測つたのは在り処と刻のみ)。
陰性対照: `for-each-ref --contains 0000…(40)` = 出目0本 ★rc=129★(rc≠0 の零は「0本」に非ず)。

## ★己の疵(三件・隠さず)★

1. `_inst/11_arika.py` ―― 「因は当てぬ。此処で言へるは『在る』と『到達せぬ』の二つのみ」を
   ★条件分岐の外に固定文として★ 刷つた。實測は「到達する」。★判じの前に結語を書いた★。
   `_raw/11_arika.txt` は其の儘残し、`_inst/12_dochira.py` で名指した。
2. `_inst/22_hankei.py` ―― 緩い規が ★和文の散文★ を拾つた(「裸の file 名」の `file` 等)、且つ
   print の中の助言 `shasum -a 256` を「走る器」と数へ、且つ `xxd`/`tail`/`timeout` を網から落した。
   ★偽陽性と偽陰性は同時に起きる★。`_inst/23_hei.py` で治し、拾つた行を悉く逐語で刷つた。
   (治した後も docstring 本文中の `file` は残る ―― `#` で始まらぬ故。★網はまだ完全では無い★。)
3. `_inst/00_heihou.py` ―― `importlib.util.spec_from_file_location` による path 直読みを
   ★辺として拾へなんだ★。顔触れ(3本)は変らぬが ★辺は2本でなく3本★。

## 禁の順守

読取のみ。据ゑず・commit せず・push せず。器は悉く本束の中(`_inst/`)。
`hash-object` は ★用ゐて居らぬ★(書く器ゆゑ)。他席の pane は覗かず、枝は一本も消さず、
`.gitignore:7` の裸の `*` は書換へず。幹の版の取り出しは `git show` の ★読取★ のみ。

## 臺帳と門(本束自身・臺帳外の記録)

- 臺帳 `MANIFEST.txt` = 頭註2行 + ★29行★。★束内相対★(裁 seq322699)ゆゑ `cd <束>` して
  `karo_mac_manifest_append.py` で建てた。臺帳外 = `MANIFEST.txt` 自身 / `README.md`(本紙) / `_after/`。
  空白を含む `_fixture/s_A/c d.txt` は ★形②(括り)★ で 1 行。門は之を
  「★旧形★ ―― ★拒んで居らぬ★(裁 seq321353⑴)」と刷り、rc を赤にせぬ(手許の 198行版)。
- 門 `KM_GATE_MANIFEST_BASE=. bash karo_mac_dasumae_gate.sh MANIFEST.txt <29本>`
  → ★rc=0「出す前 門 通。出してよい。」★(刻 2026-09-17T16:54:06+0900 / `_after/72_gate_165405.*`)
  條①一致 / 條②③④ 29本通 / 條⑤ byte和 87883。
- ★陽性対照★(門が今も鳴るかを同じ路で検む): 末尾空白+EOF改行複数を植ゑた 1 本を argv に足す
  → ★rc=1★・條②と條④が名指しで鳴つた(`_after/73_taisho.*`)。∴ 上の rc=0 は ★黙りでは無い★。

## ★疵 その四 ―― 門が一度落ちた(隠さず)★

初回の門は ★rc=1★ であつた(`_after/70_gate_165316.*`)。因 = `_raw/21_shizuka.txt` の
★尾に改行が二つ★(條④ EOF改行丁度1 に触れた)。器が `print` で書いた末尾に更に改行を足して居た。
★法★: 紙を書いた其の場で尾を検めよ(門に見付けさせるな)。
治め: `rstrip(b'\n')+b'\n'` で 1944→1943 byte。臺帳は sha を抱く故 ★建て直した★ ――
落ちた方の臺帳は消さず `_after/71_manifest_ochita.txt` に残し、差は ★21_shizuka.txt の1行のみ★
(`bytes=1944 lines=32 sha256=63e6af52…` → `bytes=1943 lines=31 sha256=62bb1790…`)である事を
`diff` で確かめた。★他の28行は一字も動いて居らぬ。★
