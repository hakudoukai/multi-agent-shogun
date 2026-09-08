# order89: install.sh の `sed -i 's/\r$//'` が作業樹を汚すか（隔離 2 repo・陽性/陰性 対）

as_of 2026-09-08 07:4x JST / 席 ashigaru-third-2 / 令 order89（案②・走 1 許可）
規 `scratch/ashigaru-third-2-fa06a3a1/o89_sed_dirty_probe.py`（88 行・sha16 `102dcdffbe2f97b9`）
生値 `scratch/ashigaru-third-2-fa06a3a1/o89_lab/o89_result.json`
前紙 o87 §5-3・o88 §4 は ★書き換へて居らぬ★（本紙で補ふ）
数: 1 = file 1 本／行 1 本。走 = 規の走行 1 回（★1 回で了へた★）。

## §0 令の受入条件と本紙の当たり
| 令の条件 | 本紙の何処 |
|---|---|
| 汚すか否かを ★陽性/陰性 対で★ | §2（表）・§3（三層に分けた） |
| ★隔離の結論に留まる事を紙に明記★ | §7（明記・§3 の三層も隔離での値） |

## §1 場の作り
本物 `/mnt/c/DentalBI` は ★讀取のみ★（`scripts/git-hooks/install.sh` を讀んで写した・626 byte・sha16 `e2b3b58c28b94baa`）。
隔離 repo を 2 つ建て、いづれも `core.autocrlf=input`（★本物と同値★）を置いた。

| 場 | `.gitattributes` | 狙ひ |
|---|---|---|
| A `o89_lab/noattr` | ★置かぬ★ | 属性の助け無しで sed が何をするか |
| B `o89_lab/withattr` | `scripts/git-hooks/* text eol=lf`（★本物の :7 行と逐語同じ★） | 属性が防壁に成るか |

両場とも `scripts/git-hooks/` に 3 本を置き ★追跡簿に載せて commit した★
（o88 の隔離では `scripts/` が追跡簿の外＝`?? scripts/` ゆゑ測れなんだ。★今回は其の穴を塞いだ★）。
- `lf_hook` 32 byte・CRLF 0 …… ★陰性の検体★
- `crlf_hook` 37 byte・CRLF 3 … ★陽性の検体★
- `install.sh` 本物の写し

## §2 實測（陽性/陰性 対）
`bash scripts/git-hooks/install.sh` を走らせた前後。install.sh の rc は両場とも 0。

| 場 | 検体 | 走前 byte / CRLF / sha16 | 走後 byte / CRLF / sha16 | 判 |
|---|---|---|---|---|
| A | `lf_hook`（陰性） | 32 / 0 / `b0194f232d71c4fc` | 32 / 0 / `b0194f232d71c4fc` | ★不変★ |
| A | `crlf_hook`（陽性） | 37 / 3 / `0df048f405fccc6b` | 34 / 0 / `6b8cbe609572ed3e` | ★変つた★ |
| B | `lf_hook`（陰性） | 32 / 0 / `b0194f232d71c4fc` | 32 / 0 / `b0194f232d71c4fc` | ★不変★ |
| B | `crlf_hook`（陽性） | 37 / 3 / `0df048f405fccc6b` | 34 / 0 / `6b8cbe609572ed3e` | ★変つた★ |

`git status --porcelain`: 両場とも 走前 = ★0 行★ → 走後 = ★` M scripts/git-hooks/crlf_hook` の 1 行★。

## §3 ★核 ―― 「汚す」は一語で答へられぬ（三層に分けた）★
数の作法 四条②「何の数かを一語」に従ひ、「汚す」を ★三つの別の物★ として測り直した。

| 層 | 問ひ | 實測 | 答 |
|---|---|---|---|
| ① file の byte | sed は file を書き換へるか | CRLF 検体 37→34 byte・sha16 が変つた | ★現に書き換へる★ |
| ② git の内容差 | 追跡簿から見て中身が違ふか | 作業樹 `hash-object` = `178d6b209d6672d858128b83a8b3a4738e4b51c2`／index の sha = ★同値★／`--no-filters` でも ★同値★／`git diff` 空・`diff --numstat` 空 | ★差 0★ |
| ③ `git status` の見え | 一覧に行が立つか | ` M scripts/git-hooks/crlf_hook` が立つ（2 度走らせても・`update-index --refresh` の後も消えぬ） | ★立つ★ |

★① と ② が食ひ違ふ因★: `core.autocrlf=input` が作業樹→追跡簿の向きで CRLF を LF へ均す。
∴ sed が消す前から index の blob は ★LF の 34 byte★（両場とも `git cat-file -p` を `od -c` で見て LF を確かめた）。
∴ sed は ★file の byte だけを★ 追跡簿の姿へ近づけた ―― ★中身の差は元から 0 で、其の後も 0★。

★∴ 「汚す」を ③ だけで答へると「汚す」・② だけで答へると「汚さぬ」。★
★一語で答へず、何を 1 と数へたかを併記せねば ならぬ形である。★

## §4 ★場B は当席の直前の見立てを削つた（開示）★
当席は本 lot の途中で「`.gitattributes` が `eol: lf` を強制し `core.autocrlf=input` ゆゑ ★CRLF が入り込む余地も薄い★」と書いた。
場B は其れを ★弱めた★:
- `.gitattributes` を置いても 場A と ★同じ結果★（① 変る・③ 立つ）。
- `check-attr` は 場B で `text: set` / `eol: lf` と現に効いて居る（場A は `unspecified`）。★属性は効いて居るのに結果が同じ★。
- 読み: `text eol=lf` は ★checkout の時に作業樹へ LF で展げる★ 規である。
  今回は file を ★手で作業樹へ置いてから add した★ ゆゑ checkout を経て居らぬ。∴ 作業樹の CRLF は残る。
- ∴ ★`.gitattributes` は「作業樹に CRLF が現れぬ」事の防壁には成らぬ★（checkout 経路でのみ効く）。
  手で置いた・別の器が書いた CRLF は ★属性が在つても残る★。
★己の見立てを實測が削つた ―― 前の言は書き換へず此処に開示する。★

## §5 本物 third の實測（讀取のみ）と ★己の規の落ちの開示★
| file | byte | 行(LF) | CRLF | sha16 |
|---|---|---|---|---|
| `scripts/git-hooks/install.sh` | 626 | 22 | ★0★ | `e2b3b58c28b94baa` |
| `scripts/git-hooks/pre-commit` | 696 | 28 | ★0★ | `8030a506e0c127d7` |
| `scripts/git-hooks/pre-push` | 3399 | 70 | ★0★ | `e4a47593600691e3` |
| `.git/hooks/pre-commit` | 696 | 28 | ★0★ | `8030a506e0c127d7` |
| `.git/hooks/pre-push` | 3399 | 70 | ★0★ | `e4a47593600691e3` |
| `.git/hooks/pre-push.bak-loadshed-20260907` | 2744 | 61 | ★0★ | `6284d288f4f4e21d` |

`core.autocrlf` = `input`／`core.eol` 未設定／`.gitattributes` :2 `*.sh text eol=lf`・:7 `scripts/git-hooks/* text eol=lf`。

★∴ 本物 third では CRLF が 0 ゆゑ、sed が変へる byte が ★無い★ ―― § 3 の ① すら起きぬ。★

★己の規の落ち（開示）★: 直前の手番で当席は同じ 3 本を「LF=0」と刷つた。
626 byte の bash に改行が 0 の筈は無く、★f-string の中で改行の escape を誤つた★ のが因である
（本 lot で ★二度目★ の同じ誤り。o87 §9 で一度開示して居る）。
上の表は ★escape を f-string の外で解いた形★ で数へ直した値である。
★CRLF=0 は誤つた規でも直した規でも同値であつたが、同じ誤りの下に在つた値ゆゑ、直した規で取り直した物を上に載せた。★

## §6 ★突き止めて居らぬ事★
1. ★`update-index --refresh` を打つても ③ の ` M` が消えぬ因★。内容は hash で完全一致（§3 ②）ゆゑ
   ★中身の差では無い★ 事までは言へるが、★何が refresh を素通りさせて居るかは 当席は言へぬ★。
2. `install.sh` は `sed -i` を ★src 側（`scripts/git-hooks/`）★ に打つ。
   ★写し先（`.git/hooks/`）は追跡簿の外★ ゆゑ、写し先の CRLF は ③ に一切現れぬ。本紙は src 側のみを測つた。
3. 本物で現に CRLF が ★入り込む道★（どの器が書けば CRLF に成るか）は ★測つて居らぬ★。
4. 他 PC（main/second/mac）の `scripts/git-hooks/` の CRLF は ★手が届かぬ・測つて居らぬ★。

## §7 ★隔離の結論に留まる（令の受入条件）★
★§2・§3 の値は いづれも 隔離 repo（`o89_lab/noattr`・`o89_lab/withattr`）で出た物である。★
★本物 `/mnt/c/DentalBI` で install.sh を走らせては居らぬ ―― 本物での ①②③ は 實測して居らぬ。★
本物について本紙が言へるのは §5 の ★讀取で出た「CRLF が 0」★ ただ一つであり、
「∴ 現に汚れぬ」は ★其の 0 から導いた筋★ であつて ★走らせて確かめた物では無い★。

## §8 境界と開示
走 1 回（規の走行・隔離のみ）／本物 hook 書換 0・名を戻さず・移さず・消さず／本物 repo への push 0・commit 0／
共有 `.git` へ書込動詞 0（`cat-file`・`ls-files`・`check-attr`・`config --get` は讀取）／
DB 讀 0・書 0・SQL 0 本／本物 CI 走行 0／network 0（隔離は local path のみ）／製品 code 書込 0／
D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触／Commander の箱 0 打／他席 inbox 直接書込 0。
