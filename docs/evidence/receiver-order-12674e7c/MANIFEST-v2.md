# 束の正本 補 (MANIFEST-v2) ―― board 12674e7c ㊀ 受審一式

本紙は `MANIFEST.md`(blob `bec97209d3895dc983fbbd0347e42d16767d503d`) の **疵を訂す新紙**である。
既published の紙は一字も書き換へず（家老條・紙は新紙にて訂す）。

## 〇. ★己の疵 ―― 二つ、認む★

| # | 疵 | 実 |
|---|---|---|
| ㊀ | 旧 MANIFEST 第8–9行「固定 HEAD = **本 commit**」「固定 tree = **同 commit の tree**」 | ★自己言及★にて、外の検め手には何も縛らぬ。軍師second の REVISE は正しい |
| ㊁ | 旧束の実行生紙 `archive_repro_20260920_0612.txt` が縛る HEAD は `8452033d…` | ★固定HEAD と別の commit★。且つ pytest を要し、pytest 無き席では再現し得ぬ |

㊁ の註: `8452033d` は `3da2076d` の★祖先★にて、四紙(受信器・三試験紙)の blob は★両 commit で同一★。
∴ 測りの中身は生きて居るが、**縛りの符が別物**であった。本紙にて固定HEADの符へ改める。

## 一. ★全字の縛り★ (前置符を用ゐず・四十字/六十四字を悉く記す)

固定 HEAD = `3da2076d25f624458f06402f331a97b0990246eb`
固定 tree = `b6349da119f9f500ac48676cabe497e35e0e7340`
枝        = `karo-second/receiver-envelope-preserve-12674e7c`
再現手順  = `git archive --format=tar 3da2076d25f624458f06402f331a97b0990246eb | tar -x -C <素の砂場>` (砂場 570紙)

| path | git blob (40字) | sha256 (64字) |
|---|---|---|
| `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` | `c014232ce75de23633c3a16c827f98dd8e233013` | `02801104367daef538f592812e2bc3ff32329c09b4c1c36b4bf461f882f6e5d0` |
| `tests/test_secondpc_downlink_owned_order.py` | `fe5c8bbf764ede104babfc59695ea13b093b25eb` | `1514bcb6f10c59f7f46369b989317ed48f34b55407deaf00b0cb4d296062bd07` |
| `tests/test_secondpc_deadletter_envelope.py` | `82e7a9c4e398511ec0990b66cd34da9c04b6f2ea` | `81105e5b621ddccf769a1a46213bedd331b897d4f3b85b62866b621f472dbf4c` |
| `tests/test_secondpc_samepc_role_routing.py` | `a1bfe1730c4e29920c9645cbc064754a47efc9fa` | `fa4ccffa872dd3c90f8ab88164c26d9bc23e8259aea3c824b36fe436c5e604a7` |
| `docs/evidence/receiver-order-12674e7c/mutation_control_raw_20260920_0557.txt` | `885d3d4161eb63fb0ae188906acf0780ff23d402` | `4c7bcc563070594248ece1321128f6797795735fe564afe8f92fa01ef179acd8` |
| `docs/evidence/receiver-order-12674e7c/mutation_control_raw_20260920_0557.txt.ws-normalized` | `eabc19977ce8ebe65ebb6663f54d73843f3aea46` | `40cca11cabb4102d107c725f9937ed48a97b99872b36ea15443071b8c9bf4fdb` |
| `docs/evidence/receiver-order-12674e7c/archive_repro_20260920_0612.txt` | `9864a73341d4ea56894c1d438ce44ab8d9c0b880` | `919b1da1d034571ab2fe977f450db12b1044efc975ade98eaa67f71f83d14ddf` |
| `docs/evidence/receiver-order-12674e7c/README.md` | `7d4922ce1adac2f1c64a9cdf1e52ee59e82aa9da` | `1e6093d9fcfea7cc8d2b7366eb33d1c569930adc14032de6358337273fe4f3c9` |
| `docs/evidence/receiver-order-12674e7c/MANIFEST.md` | `bec97209d3895dc983fbbd0347e42d16767d503d` | `5eb62234268c396a7aa72a709e547d9511f2befb7e024b4f5216048790429204` |

本紙と共に収める新紙 (本 commit にて加はる故、固定HEADには未だ無し):

| path | sha256 (64字) |
|---|---|
| `docs/evidence/receiver-order-12674e7c/run_nopytest.py` | `ac40c0bd5388fc527eef337c223d7d29b5f71efe393c884471139ec5bd1dc838` |
| `docs/evidence/receiver-order-12674e7c/portable_repro_raw_20260920_0707.txt` | `7e76c0464b1c90d3d9f781dc887f4222389513c356791e052cf43bb3a5829038` |

## 二. ★可搬なる実行生紙★ ―― pytest 無き席でも再現し得る

旧束の実行証は pytest に依り、軍師second・事業部長の両席にて★再現不能★であった。
本紙は之を替へる。借る pytest 機構は組込 fixture `tmp_path` ★ただ一つ★にて、
`run_nopytest.py` が tempfile にて自前で与ふ（標準庫のみ・外部依存零）。

```
㊀ 正対照 後像 blob c014232ce75de23633c3a16c827f98dd8e233013 → ok=10 fail=0 rc=0
㊁ 負対照 前像 blob 2db21504ebba6568185cfe7d0190be4e8eacd242 → ok= 9 fail=1 rc=1
   前後を分かつ紙 = test_envelopeless_downlink_row_is_not_dead_lettered (四本中一本)
   条件 PYTHONNOUSERSITE=1 ―― 利用者site を無効にして尚 通る事を示す
```

生紙 = `portable_repro_raw_20260920_0707.txt`（上表に sha256）。

### 母数の註 ―― 数の食ひ違ひに非ず

軍師second 06:57:34 の「order 3 pass / 1 fail RC1」は ★order 単紙 4件★ が母数、
本紙の「9 pass / 1 fail」は ★三紙 10件★ が母数。分かつ紙は両者同一の一本。
（旧 MANIFEST 三. の「10 = 4+3+3」と同じ筋の食ひ違ひである）

## 三. 旧 MANIFEST の生きて居る節

旧紙の 三.(10=4+3+3) / 四.(末尾空白の写し) / 六.(限り) は★そのまま生く★。
本紙が替へるは 一.(符) と、実行証の器 のみ。

## 四. 限り (旧紙 六. と併せ読まれたし)

* 変異対照にて前後を分かつは四本中★一本のみ★。
* 「自己宛 かつ downlink 所有」の行が滞留せぬかは★未測★。
* 生きて居る 556行 `RECEIVER_SKIP_TARGETS` 系統は★同じ疵を抱へたまま・未直★。
