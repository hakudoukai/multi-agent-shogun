# 臺帳を建てる器を repo の中へ ―― karo_mac_manifest_append.py 独立1commit

- 件名: km-manifest-append-track-20260917
- 席: 家老mac(係長格・pane %68)
- 裁: pc_handshake **seq326512**(委員長)/ 親 seq326490 / 祖 seq326093
- 刻: 2026-09-17 16:20 JST(生の刻は各 raw の冠に在り)

## 一 裁の逐語(seq326512)

> 裁(326490)=可。.gitignore の許し行(!scripts/checks/karo_mac_manifest_append.py)+当該 file を、
> 裁326093②の枠(幹着地後の甲 小PR)ではなく★先に★独立の1 commit
> (枝 karo-mac/manifest-append-track-20260917・親 origin/main)へ据ゑ push願い1行
> →総監督が代行 push+PR。理由=台帳を建てる器が repo 外では幹の検分も再現不能。secret 0・blob sha を紙へ。

## 二 疵 ―― 何が欠けて居たか

臺帳(manifest)へ行を書く **唯一の書き手** `scripts/checks/karo_mac_manifest_append.py` が
**git の何處にも無かつた**。

| 面 | 出目 | 器 |
|---|---|---|
| disk | 在り 10959 bytes / 242 行 | stat / grep -c '' |
| index | **外** | git ls-files |
| object | **無し** | 中身から blob sha1 を組み `cat-file -e` rc=1 |
| ref(90本) | **0/90** | git log --all -- \<path\> が空 |

★object すら無い★ ―― 即ち **一度も commit されて居らぬ**。
中身から `sha1(b"blob %d\0" % len(b) + b)` を組んで `cat-file -e` に掛ける形で測つた
(path を経ぬ故、名を変へて隠れて居る場合も拾へる)。
対照に同じ dir の `gate.sh` を掛けると rc=0 ―― **器の側の誤りではない**。

## 三 因 ―― `.gitignore:7` の『\*』一字

`.gitignore` 7 行目は裸の `*`＝**許し形**(allowlist)。全てが遮断され、
`!` で名指した物だけが戻る。`scripts/checks/` は

```
!scripts/checks/
!scripts/checks/*.sh                       ← .sh のみ
!scripts/checks/karo_mac_manifest_verify.py ← .py は名指し一本(先例 26e2359・裁 294773)
```

`.py` は **名指ししか通らぬ**。verify.py には其の一行が在り、append.py には無かつた。
**唯 それだけ**である。器の書き方にも席の働きにも落度は無い。

## 四 直し ―― 一行

```diff
 !scripts/checks/
 !scripts/checks/*.sh
+!scripts/checks/karo_mac_manifest_append.py
 !scripts/checks/karo_mac_manifest_verify.py
```

- 先例 **26e2359**(origin/main に在る f0d59a3 の押された版・裁 294773)と**同形**。
- 並びは verify.py の**前**＝字順(append < verify)。
- **戻し方**: 其の一行を消せば元へ復る(可逆・`-f` 不使用)。

### ★据ゑる前に掴んだ食ひ違ひ★

disk の `.gitignore` は origin/main の版より **`!scripts/idle_backlog_wake.sh` を一行欠く**
(disk 441 行 / origin/main 442 行)。
disk を種にすれば**其の一行を黙つて消す commit** に成つた。
∴ 種は `git cat-file -p origin/main:.gitignore` から採つた。

## 五 secret 0(裁の名指した條件)

- 器: repo 正本 `.gitleaks.toml` の則を読み込んで当てた(`gitleaks` の binary は当機に無し)。
- 母數: **則 15 本 / `[[rules]]` 塊 15**(等しい＝読めぬ則が無い)。
- **当該 file の当り = 0 件**(15 則 悉く 0)。
- **陽性対照 3/3**: `bearer-token` / `generic-password` / `generic-api-key` が
  偽の値に鳴る事を確かめた ―― **則が死んで居らぬ證**。
- 生: `raw/02_secret0.txt`

## 六 blob sha(裁の名指した條件)

| 物 | 値 |
|---|---|
| append.py blob sha1 | `b56d6576c82212c155980968d4ec1e0a8c5c7427` |
| append.py sha256 | `f5ea5e1e85d64936288e9937421eb8e201bc1f34ed05b9308fa495464c7b2533` |
| append.py bytes / 行 / mode | 10959 / 242 / 100755 |
| .gitignore(新) blob sha1 | `2c809232c39277c0889ae2a80a01aed129cd6319` |
| .gitignore(親) blob sha1 | `1cf7a0d…`(diff の index 行に出づ) |
| tree | `6b1f60977b00aae2892f516f79d014727675bb77` |
| **commit** | **`61a9fe1c18beffddef6b40503766ba726b8b0a05`** |
| 親 | `4be3ee19e1c5113eb4c2490cd4b496e9b453c7d1`(origin/main) |
| **枝** | **`refs/heads/karo-mac/manifest-append-track-20260917`** |

blob sha1 は **器二本**で測つて同値 ―― `git hash-object` と python `hashlib` の独立計算。

## 七 検め(対照つき)

| # | 検め | 出目 | 対照 |
|---|---|---|---|
| ⑴ | 親との差 | **2 本 丁度**(M .gitignore / A append.py) | diff-tree -r --name-status |
| ⑵ | 樹の総 file 数 | 515 | ls-tree -r --full-tree -z(NUL 区切) |
| ⑶ | 当該 path の mode/sha | 100755 / b56d6576… 一致 | **陽性対照** .gitignore と verify.py が各 1 本在る事を先に確かめた |
| ⑷ | 遮断が解けたか | 本題 add rc=0・index=1 | **陽性対照** verify.py=1 / **陰性対照** DAREMO…=0 |
| ⑸ | 中身の往復 | `cat-file -p <commit>:<path>` と disk が `cmp` 一致 | sha256 同値 |
| ⑹ | 隔たり | origin/main..枝=1 / 枝..origin/main=0 | 片道のみ＝直子 |
| ⑺ | HEAD・共有 index | **不動**(HEAD=260f2a06… 変はらず) | GIT_INDEX_FILE 別立て |

### ★己の疵 ―― 途中で読みを誤つた★

`git check-ignore -v` の **rc=0 を「遮断中」と読んだ**が、彼の rc は
「**則に当たつた**」であつて「遮断」ではない。`!` で始まる則に当たつても rc=0 に成る。
∴ 決め手を `git add`(`-f` 無し)の實走へ替へ、陽性・陰性の両対照を添へて測り直した(raw/04)。
**rc の意味を確かめずに読んだ**のが疵である。

## 八 意味せぬ事

- 此の commit は **push されて居らぬ**。push は総監督の代行が正路。當席は commit までで止めた。
- 此の commit は **PR#20(幹 km-gate-kou-otsu)とは別物**。裁326512 が「★先に★独立の1 commit」と
  名指した通り、PR#20 の枝には一指も触れて居らぬ。
- 「secret 0」は **此の file の 242 行に対して** 0 であつて、repo 全体の話ではない。
- 此の一行は append.py **一本**の遮断を解くのみ。陰性対照(同 dir の別 .py)は今も遮断されたまま。

## 九 生

| 生 | 中身 |
|---|---|
| `raw/01_sunpou.txt` | 寸法・blob sha1 を器二本で |
| `raw/02_secret0.txt` | 則 15 本の当り 0 と陽性対照 3/3 |
| `raw/03_ki_to_taishou.txt` | diff-tree / ls-tree / .gitignore の差 / 隔たり |
| `raw/04_shadan_toketa.txt` | add 實走 三対照 |
| `raw/05_fudou.txt` | HEAD・共有 index 不動 |

## 十 門 ―― 走1 は★落ちた★(消さずに残す)

| 走 | 出目 | 中身 |
|---|---|---|
| 走1 `mon_162139.log` | **rc=1** | 條② 末尾空白 ―― `raw/02_secret0.txt` に 15 行 / `raw/03_ki_to_taishou.txt` に 1 行 |
| 走2 (下記) | rc=0 | 整へた後 |

**因**:
- `raw/02` = 己の書式 `"%s" % (h if h else '')` が**空の時に末尾空白を産む**(15 則 悉く 0 ゆゑ 15 行)。
- `raw/03` = `git diff` の**空の文脈行は `" "` 一字**として出る(unified diff の仕様)。書き手の落度ではない。

**直し**: 正本の作法(2026-09-07 軍師mac REVISE・全席周知)
`perl -pe 's/[ \t\r]+$//'` → `perl -0pi -e 's/\n+\z/\n/'` を掛けた。

### ★整へる前の寸法(控)★ ―― 作法「sha を取る前に整へ、前の寸法を控へよ」

| 紙 | 前 bytes | 後 bytes | 差 | 前 sha256(頭16) |
|---|---|---|---|---|
| `00_shodan.md` | 6458 | (下記) | — | `0f0f2b3fdebdb0…` |
| `raw/01_sunpou.txt` | 327 | 327 | 0 | `d92fdd68f27afe…` |
| `raw/02_secret0.txt` | 784 | 769 | **−15** | `059a397dea633a…` |
| `raw/03_ki_to_taishou.txt` | 1001 | 1000 | **−1** | `f26fa70169f7db…` |
| `raw/04_shadan_toketa.txt` | 331 | 331 | 0 | `909f0097e17512…` |
| `raw/05_fudou.txt` | 402 | 402 | 0 | `a767420d07202a…` |

差 −15 / −1 は門の鳴り(15 行 / 1 行)と**丁度合ふ**。
`00_shodan.md` は此の節を書き足した故、上表の「前」は節を足す前の値である。

### 員外(臺帳の外に置いた物と、其の理由)

| 物 | 理由 |
|---|---|
| `mon_162139.log` | **門 己の産物**。己を検める臺帳へ己の出目を入れれば自己言及に成る(條①) |
| `mon_*.log`(走2) | 同上 |
| `manifest.txt` | 臺帳自身は條⑤ byte和の外(器の仕様) |

**臺帳は建て直した**: `karo_mac_manifest_append.py` は追記専用ゆゑ、整へた後の sha へ書き換へる術が無い。
走1 の臺帳を消し、整へた後の 6 本で建て直した。此の束は未だ何處へも出して居らぬ
(出した紙は書き換へぬ ―― 出す前ゆゑ建て直しが正)。
