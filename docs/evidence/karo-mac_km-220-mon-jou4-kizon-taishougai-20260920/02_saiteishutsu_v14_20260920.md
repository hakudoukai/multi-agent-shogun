# km-220 再提出 v1.4 ―― 雛形 v1.3 ①〜⑦（軍師mac 判 seq343521 REVISE の療法）

## 判の逐語（seq343521 ―― 之より広くも狭くも直さぬ）

> 「REVISE ③raw2/97_mon_kessai3.argv。同fileのcwd/argvはfixed commit/treeを明示せず、同一run束縛が不成立です。
> 40桁commit/treeをrawへ明記して再走し、rc・正負対照・cleanと同一束で提出してください。固定証跡のみ。DB/CI/配備/GOなし。」

**∴ 判の指す疵は「紙に commit が書いて在るか」ではなく「★raw 自身が己の走つた commit を持たぬ★」である。**
當職が測つた所 ―― `raw2/97_mon_kessai3.argv`（3746B・rc=0）の中に **40桁 hex は一つも無い**（器で数へて 0）。
∴ 判は事実に基づく。當職の器 `utsuwa/hashiru.sh`（v1）は 札/cwd/刻/env/argc/argv[i]/rc しか焼かず、
**commit/tree を一字も焼かぬ**設計であつた ―― 之が根である。

## ★本紙は 00_shodan.md も 01_saiteishutsu_v13 も書き替へぬ★

提出済の紙は彫らぬ（裁: 提出済の束は彫らず）。訂は本紙に書く。

## ★臺帳 manifest.txt を建て直さぬ ―― 其の理由を宣す★

臺帳は commit `21bac4df` で凍つて居り、`path=` 行は **84 本**（sha256 `bade27e09db3a0263742552238b3ed3cea02515f7bf2e8e8c5369ace8df45ebf`）。
本再走で新たに起こした紙（`utsuwa/hashiru2.sh`・`raw3/*`・新 fixture・本紙）は
**雛形 v1.3 第4項「臺帳が建つた後に内容が決まる紙は全て臺帳の外」**に当たる。
加へて ―― **臺帳を建て直せば條①の母數が 84 から動き、raw2 の走り（母數 84）と比べられなく成る。**
判は「**同一 run 束縛**」を求めて居る ∴ 比較可能性を壊す建て直しは判に背く。
**∴ 臺帳は一行も触れぬ。本節が其の宣言である。**

---

## ① 対象 tuple

```
ref        = karo-mac/km-220-mon-jou4-kizon-wo-taishougai-20260920
commit40   = 21bac4df79af0d928afb4cb970edd7f4b37d03f0
tree40     = 2efba8da26cf97e9241db9497d6a79485b1ece0c
門 blob40  = 484e7a36aa8145925cf8f86942e29357d249db53
門 disk sha256 = 5c46ef7b5fbc8d4f0f13e394a93e3a4d9bef6c8a4f14f045480c490c8b9421e1
樹         = /Users/momizimac/wt/km-220-jou4-kizon-taishougai
```

**★此の五つは悉く raw3 の全 .argv に焼かれて居る★**（判の求める「同一 run 束縛」の本体）。
紙が主張するのではなく、**走りが己で名乗る形**に据ゑた。

## ② 成果物（path / sha256 / bytes / lines）

### 本紙の為に新たに据ゑた器（一本）

| path | sha256 | bytes | lines |
|---|---|---|---|
| `utsuwa/hashiru2.sh` | `44be0965f5466dc406a85c5a80fa09ea660481303d1f3179758430b12876dbc3` | 3386 | 52 |

v1 との差 = **焼く項を足しただけ**（rc の取り方・空 stream の註は v1 と同形）。足した項:

```
git_ref / git_commit40 / git_tree40 / mon_blob40 / mon_disk_sha256
yogore_zensu（porcelain -uall の行数）/ yogore_zen:（同・逐行）
```

**★v1 `utsuwa/hashiru.sh` は一指も触れぬ★**（提出済ゆゑ）。v2 を別名で立てた。

### 本紙の為に彫つた對照紙（一本）

| path | sha256 | bytes | lines |
|---|---|---|---|
| `fixtures/taishou_r3_eof_nashi.txt` | `da4fda5bb84d4ed3716a39a26317bc1c4f311562061424eb2aca33a8571621c2` | 67 | 1 |

胴の逐語 = 「再走の陽性対照 ―― 此の紙は EOF 改行を持たぬ。」（末尾 `e380 82`＝「。」・改行なし）

### raw3（本再走の raw ―― 5 走り分）

| path | sha256 | bytes | lines |
|---|---|---|---|
| `raw3/R00_clean.txt` | `8021427a6bec5a05d7fd891fc1a790598dbe23e9918a955ba98e84f9b859fdf9` | 2378 | 32 |
| `raw3/R01_kessai_saisou.argv` | `f03f85f478374cf17d1b10dce5ddf3969a455f6e7fc1b08ff30ccce52f30ade3` | 4251 | 105 |
| `raw3/R01_kessai_saisou.out` | `8b86f81bdb2726557fcb98fb0cb14065b85accd9f93635abcd1b07e37bf37e7c` | 332 | 5 |
| `raw3/R01_kessai_saisou.err` | `951159a475d9e12c24ee51c1fe2fa59ab81eeb457705edadfcd4845d9e5d2cd5` | 1467 | 12 |
| `raw3/R01_kessai_saisou.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 | 1 |
| `raw3/R02_yousei_mitsuiseki.argv` | `115465636965fb10307a2e3ec994e65b9d90812aaa8f172cc9134c7e51c43ee6` | 891 | 21 |
| `raw3/R02_yousei_mitsuiseki.out` | `00a69db22fb590cca93ef6da97c0a6b8843475c78a6a15fe8b7e71f7e82ad025` | 262 | 1 |
| `raw3/R02_yousei_mitsuiseki.err` | `336707ca5b1ce8ab8a55a9bcd182a33524e513c03f84fc3c8f936e057a216465` | 943 | 8 |
| `raw3/R02_yousei_mitsuiseki.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | 2 | 1 |
| `raw3/R02b_yousei_scope_all.argv` | `6c2a6b52e42c91da02fc84163d1ad9dd793b31eb3e91e0aa1d6e7733d50348af` | 879 | 21 |
| `raw3/R02b_yousei_scope_all.out` | `8592bae15b3cf1c3c4460512dfafe196466be19923fae5a90bec0df8b87d5ae1` | 262 | 1 |
| `raw3/R02b_yousei_scope_all.err` | `ea9b448613306f053649506ee2b14c0a84cc6cd42811f01cec80e3dcf5c11e12` | 609 | 8 |
| `raw3/R02b_yousei_scope_all.rc` | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | 2 | 1 |
| `raw3/R02c_yousei_mitsuiseki_shin.argv` | `3b917bcd5375e8f1dff56ef91af952ba0fae4b1807ff3e2bba30fd539dcc8262` | 894 | 21 |
| `raw3/R02c_yousei_mitsuiseki_shin.out` | `6e7c2406a2d47cebf5959740d0f3b6387b16e03709f6d4e7d6c381880ec5bb52` | 268 | 1 |
| `raw3/R02c_yousei_mitsuiseki_shin.err` | `2fd50c33a8a73a20d2a16726fa4d176738a7375af4bad24a59f7e8ad017848ec` | 618 | 8 |
| `raw3/R02c_yousei_mitsuiseki_shin.rc` | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | 2 | 1 |

初提出の紙 32 本＋raw2 の 48 本は**臺帳（84行）が担ふ** ―― 本紙は其れを数へ直さぬ。

---

## ③ 実走の raw ―― ★40桁 commit/tree を raw 自身が持つ★（本節が判 seq343521 の核心）

| 札 | 何の對照か | cwd | argc | 40桁 commit/tree | rc |
|---|---|---|---|---|---|
| `R01_kessai_saisou` | 決裁走の再現（raw2/97 と**逐語同一 argv**） | 束 | 88 | **在り**（commit40/tree40/blob40/disk sha256） | 0 |
| `R02_yousei_mitsuiseki` | C01 と**逐語同一 argv**の再走 | 樹の根 | 4 | **在り** | **0**（★C01 は 1★ ―― 下記） |
| `R02b_yousei_scope_all` | 陽性対照・射程 all | 樹の根 | 4 | **在り** | **1** |
| `R02c_yousei_mitsuiseki_shin` | 陽性対照・未追跡の新紙 | 樹の根 | 4 | **在り** | **1** |
| `R00_clean` | 復元（porcelain 二形＋rev-parse） | 樹の根 | ― | **在り** | 0 |

### R01 ―― 逐語同一で 86 args を渡した（當職が一度撃ち損じた）

`raw2/97_mon_kessai3.argv` の `argv[3..88]` を機械で抜いて渡した（argc=88＝`/bin/bash` + 門 + manifest引数1 + file 85）。
**★一度目の撃ちは 85 で走つた ―― 當職の疵である★**: 抽出器が `b"\0".join(...)` で**終端 NUL を書かず**、
`read -r -d ""` が末尾一本（`utsuwa/hashiru.sh`）を落とした。終端 NUL を足して撃ち直し、
`渡す数=86`・`argc=88` を目で検めた。**落ちた走りは raw に残さぬのではなく、本節に因を書いた。**

R01 の err の末尾逐語:

```
條②末尾不可視字(類 Zs/Zl/Zp/Cc/Cf) / 條③CR混入 = 全file(85本)通 ―― ★條④は 4/85 本を既存として對象外にした(裁 seq339959)★。★對象外は「EOF改行が在つた」の意に非ず★
條⑤ 寸法 = byte和 184745(閾 10485760未満)
★出す前 門 通。出してよい。★
```

### ★本再走が掴んだ新しい事実 ―― 對照の極は commit に縛られる★

`R02` は **C01（02:42・rc=1）と逐語同一の argv・同一の fixture** で走らせたのに **rc=0** に成つた。
當職は初め「fixture が変はつたか」を疑ひ、disk と HEAD の byte を両方測つた ―― **共に 91B・末尾 `e380 82`（改行なし）で同一**。
∴ 因は file ではない。差の逐語（`diff C01.err R02.err`）:

```
< ★EOF改行が無い(0) ―― …/fixtures/saitei_taishou_20260920.txt★
> 條④ 對象外 ―― …/fixtures/saitei_taishou_20260920.txt は既存(追跡済・HEADと差無し)・札=1(裁 seq339959。悉く当てるには DASUMAE_JOU4_SCOPE=all)
< ★出す前 門が落ちた。出すな。★
> ★出す前 門 通。出してよい。★
```

**∴ 因は條④の射程である。** C01 の刻には fixture が**未追跡**であつた ∴ 條④の對象に成り門が落ちた。
今は同 fixture が**追跡済で HEAD と差が無い** ∴ 條④が「既存＝對象外」に倒して門が通つた。

> **★學び（判の求める「同一 run 束縛」が何故要るかの實証）★**
> **rc は argv だけでは決まらぬ。commit（＝file の追跡状態）が rc を決める。**
> ∴ **commit を持たぬ raw は rc の意味を持たぬ。** 判 seq343521 は正しい ―― 且つ本再走は
> **同一 argv が commit 違ひで rc 0/1 に分かれる事を実物で示した**。之が判の根拠の裏付けである。

### 陽性対照を★二本★据ゑ直した（一本では極が commit に流されるゆゑ）

```
R02b = 門自身が err に示した逃がしで撃つ ―― env DASUMAE_JOU4_SCOPE=all
       → rc=1・err L5「★EOF改行が無い(0) ―― …/fixtures/saitei_taishou_20260920.txt★」
       ∴ 條④は「常に對象外にする」恒真ではない（射程を all へ倒せば既存も当たる）
R02c = 真に未追跡の新紙を置いて既定射程で撃つ ―― fixtures/taishou_r3_eof_nashi.txt
       → rc=1・err L5「★EOF改行が無い(0) ―― …/fixtures/taishou_r3_eof_nashi.txt★」
       ∴ 既定射程でも★新しい紙には現に当たる★（門は死んで居らぬ）
```

**陰性対照 = R01（rc=0・85本通）**。∴ 正負の両極が**同一 commit・同一 blob の門**で取れて居る。

### ★新 fixture が porcelain -uall に出ぬ事も測つた★

`.gitignore:7` が裸の `*` ゆゑ、新 fixture は **ignored** であり `porcelain -uall` に出ぬ。
器で検めた: `porcelain -uall` = 1 行（既知の一行のみ）／`--ignored -uall` に当該 path = 1 行／
`check-ignore -v` = `.gitignore:7:*`。**∴ 「-uall に出ぬ」は「無い」の意に非ず** ―― R00_clean は二形を両方焼く。

---

## ④ 依存の境界（lockfile）

```
lockfile = ★該当無し（N/A）★
理由: 本弾の成果物は POSIX shell script 二本（utsuwa/hashiru.sh・hashiru2.sh）と
      text の raw / fixture のみ。外部 package を一つも引かぬ ∴ 固定すべき依存の表が無い。
用ゐた器は悉く OS 同梱の絶対 path で名指した:
  /bin/sh /bin/bash /bin/cat /bin/ls /bin/date
  /usr/bin/git /usr/bin/shasum /usr/bin/awk /usr/bin/sed /usr/bin/grep /usr/bin/head /usr/bin/tail
  /usr/bin/stat /usr/bin/printf /usr/bin/python3
★「N/A」を空欄で済ませぬ ―― 何故 N/A かを書くのが雛形 v1.3 ④の求めである。★
```

---

## ⑤ 件数 ―― ★母數を條ごとに分けて書く★

```
條① の母數 = ★臺帳 manifest.txt の path= 行数 = 84★
              （器 = /usr/bin/grep -c '^path=' manifest.txt・rc=0・刻=本再走時）
條②③ の「N本通」= ★門へ渡した file 数 = 85★
              （器 = raw3/R01_kessai_saisou.argv の argc=88 から算ず:
                argc 88 − /bin/bash 1 − 門 1 − manifest 引数 1 = 85）
條④ 對象外 = ★4/85 本★（悉く fixtures/ の紙・逐語は R01.err L6-L9）
條⑤ 寸法   = byte 和 184745（閾 10485760 未満）

★此の二つの母數(84 と 85)を一語に混ぜるな★ ―― 當職は本日 km-220 の初提出で混ぜた(落度⑱)。
差の 1 本は utsuwa/hashiru.sh ―― 臺帳が建つた後に彫つた紙ゆゑ臺帳の外に在り、
然し門へは渡した ∴ ★正しく 84 と 85 は違ふ★。
```

### 正負対照の表（悉く commit 21bac4df・門 blob 484e7a36 で取つた）

| 走り | 期す極 | rc | 決めた條 |
|---|---|---|---|
| R01（85本） | 負（通る） | 0 | 條①〜⑤ 悉く通 |
| R02b（射程 all） | 正（落ちる） | 1 | 條④ → EOF改行が無い(0) |
| R02c（未追跡の新紙） | 正（落ちる） | 1 | 條④ → EOF改行が無い(0) |
| R02（C01 と同 argv） | ―（**意味負**） | 0 | 條④ 對象外（★極が commit に流された實証★） |

**★意味負の宣★**: R02 の rc=0 は「門が壊れた」の意に非ず・「fixture が直つた」の意にも非ず。
**「條④ の既定射程 existing_exempt が、追跡済に成つた紙を對象外にした」**の意である。
**∴ R02 は陽性対照として★使へぬ★** ―― 使へぬ事を測つて宣し、R02b/R02c へ据ゑ直した。

---

## ⑥ 復元（clean ―― ★porcelain を二形で測つた★）

raw = `raw3/R00_clean.txt`（32行・sha256 `8021427a6bec5a05d7fd891fc1a790598dbe23e9918a955ba98e84f9b859fdf9`）

```
git status --porcelain -uall   → ★1 行のみ★ = ` M docs/runbooks/ERR-EKARTE-001.md`
git status --porcelain --ignored -uall → 上記＋ignored（新 fixture・raw3 等を含む）
rev-parse → ref / commit40 21bac4df… / tree40 2efba8da…
```

`ERR-EKARTE-001.md` の一行は**當職の物ではない** ―― docs/runbooks の大小二形（case collision）に由る
**偽の modified** であり、既に別件として記録済（裁未了ゆゑ本弾では触れぬ・第一条「消すな・戻すな・咎めるな」）。

### 復元の手（受け手が己の手で踏める形）

```sh
git -C <樹> rev-parse HEAD            # → 21bac4df79af0d928afb4cb970edd7f4b37d03f0
cd <束>
export KM_GATE_MANIFEST_BASE=.
# R01 の再現（86 args ―― raw3/R01_kessai_saisou.argv の argv[3..88] を終端 NUL 付きで渡す）
# R02b の再現
cd <樹> && DASUMAE_JOU4_SCOPE=all /bin/bash scripts/checks/karo_mac_dasumae_gate.sh \
  -- docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/fixtures/saitei_taishou_20260920.txt
  # → rc=1・「★EOF改行が無い(0)★」
# R02c の再現
cd <樹> && /bin/bash scripts/checks/karo_mac_dasumae_gate.sh \
  -- docs/evidence/karo-mac_km-220-mon-jou4-kizon-taishougai-20260920/fixtures/taishou_r3_eof_nashi.txt
  # → rc=1・「★EOF改行が無い(0)★」
```

---

## ⑦ 法令根拠

| 条 | 本紙での履行 |
|---|---|
| 判 seq343521（軍師mac） | 40桁 commit/tree を raw へ焼いて再走・rc・正負対照・clean を同一束で提出 |
| 裁 seq339959 | 條④の射程 existing_exempt／`DASUMAE_JOU4_SCOPE=all` の逃がし ―― 逐語で引いた |
| 裁 seq322699 | 臺帳の根は束内相対 ―― `KM_GATE_MANIFEST_BASE=.` で束から走らせた |
| 裁 seq321856 | 臺帳へ行を足すのは `karo_mac_manifest_append.py` のみ ―― **本紙は臺帳へ一行も足さぬ** |
| 裁 seq310228⑶ | 空 stream は註一行（器 v1/v2 共に同形） |
| 雛形 v1.3 第4項 | 臺帳が建つた後に内容が決まる紙は臺帳の外 ―― 本紙・raw3・hashiru2.sh・新 fixture が其れ |
| 數の規律1〜3 | 「數が何を意味せぬか」を併記（R02 の意味負・對象外は EOF改行在りの意に非ず・-uall に出ぬは無いの意に非ず） |
| no-silent-failure | 撃ち損じた 85 args の走りを隠さず③に因を書いた |
| 第一条 | 他席の樹・提出済の束・門自身・臺帳の器は**一指も触れず**、讀取のみで測つた |

## ★當職の落度（本再走で己が踏んだ物）★

1. **抽出器が終端 NUL を書かず、86 の args を 85 で走らせた** ―― 逐語同一を名乗れぬ走りを一度作つた。療法＝終端 NUL を足し、`渡す数` を刷つて目で検める形にした。
2. **陽性対照を「前に落ちたから今も落ちる」と当て込んだ** ―― C01 の rc=1 を再現と称する前に測らなかつた。療法＝**對照は commit ごとに極を測り直す**（本紙③の學び）。
