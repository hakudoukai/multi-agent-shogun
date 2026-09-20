# km-220 補ひ ―― ★一変数のみを動かした對照★（判 seq343521 の根拠の實証）

## 何を示す紙か

判 seq343521 は「raw が fixed commit/tree を明示せねば**同一 run 束縛が不成立**」と言ふ。
本紙は其の言の**根拠を実物で示す** ―― **argv を一字も変へず commit だけを動かすと rc が反る**事を、
當職の束の内で二走りに分けて測つた。

## 対照の形（一変数のみ）

| | R02c | R04 |
|---|---|---|
| 札 | `R02c_yousei_mitsuiseki_shin` | `R04_onaji_argv_commit_go` |
| commit40 | `21bac4df79af0d928afb4cb970edd7f4b37d03f0` | `f387315c33c26f3705e0bcd4d576b29c7eaee173` |
| tree40 | `2efba8da26cf97e9241db9497d6a79485b1ece0c` | `cf4a51576e12b7b387843417c2103531e7eebb67` |
| 門 blob40 | `484e7a36aa8145925cf8f86942e29357d249db53` | 同左（**門は一字も変はらず**） |
| cwd | 樹の根 | 同左 |
| argc | 4 | 4 |
| argv[i] | `-- docs/evidence/…/fixtures/taishou_r3_eof_nashi.txt` | **逐語同一** |
| env `DASUMAE_JOU4_SCOPE` | 未設定 | 未設定 |
| 對象 file の byte | 67B・末尾「。」改行なし | **同一 blob（`da4fda5b…`）** |
| **rc** | **1** | **0** |

`diff R02c.argv R04.argv` の出た行は **札 / 刻 / commit40 / tree40 / rc の五つだけ**である
（argv[i] の行は一行も差が出ぬ）。**∴ 動かした変数は commit 一つのみ。**

## 逐語の差（`diff R02c.err R04.err`）

```
< ★EOF改行が無い(0) ―― …/fixtures/taishou_r3_eof_nashi.txt★
---
> 條④ 對象外 ―― …/fixtures/taishou_r3_eof_nashi.txt は既存(追跡済・HEADと差無し)・札=1(裁 seq339959。悉く当てるには DASUMAE_JOU4_SCOPE=all)
> 條②末尾不可視字 / 條③CR混入 = 全file(1本)通 ―― ★條④は 1/1 本を既存として對象外にした★。★對象外は「EOF改行が在つた」の意に非ず★
< ★出す前 門が落ちた。出すな。★
---
> ★出す前 門 通。出してよい。★
```

## 断ずる所

1. **rc は argv だけでは決まらぬ。** 同じ門・同じ argv・同じ byte で、**commit が違へば rc が違ふ**。
   因は條④の既定射程 `existing_exempt`（裁 seq339959）―― file が追跡済に成つた刻に對象外へ倒れる。
2. **∴ commit を持たぬ raw は rc の意味を持たぬ。** 判 seq343521 は**正しい**。
   當職の v1 の器が commit を焼かなかつたのは設計の疵であり、判が之を捕へた。
3. **∴ 對照（陽性/陰性）は commit ごとに極を測り直さねばならぬ。**
   「前に落ちたから今も落ちる」は推量である ―― 當職は本再走で一度之を踏んだ（02紙の落度⑵）。

## 之が★意味せぬ★事（數の規律3）

- 門が壊れて居る事を意味せぬ ―― 未追跡の紙には現に当たる（R02c rc=1）。
- 條④が恒真に對象外へ倒す事を意味せぬ ―― 射程を `all` へ倒せば既存も当たる（R02b rc=1）。
- fixture が直つた事を意味せぬ ―― blob `da4fda5b…` は R02c と R04 で**同一**である。
- 「commit すれば門を通せる」の指南でもない ―― 條④の射程が斯う定まつて居る（裁 seq339959）事の**記述**である。

## 成果物

| path | sha256 | bytes | lines |
|---|---|---|---|
| `raw3/R04_onaji_argv_commit_go.argv` | ※本紙と同 commit にて焼く | | |
| `raw3/R04_onaji_argv_commit_go.out` | 〃 | | |
| `raw3/R04_onaji_argv_commit_go.err` | 〃 | | |
| `raw3/R04_onaji_argv_commit_go.rc` | 〃 | | |

**★本紙は己の commit の sha を書けぬ（紙が己を含む臺帳の數を書けぬのと同じ）★** ―― R04 の四本の
sha256 は本紙と同一 commit に在り、`git show <commit>:<path> | shasum -a 256` で受け手が直に取れる。
走りの commit = `f387315c`（R04 の argv に焼かれて居る）。
