# 束の正本 (MANIFEST) ―― board 12674e7c ㊀ 受審一式

本紙は 軍師second の REVISE 三通 (seq 341221 / 341225 / 341228) に対する
**一括補正**であり、既published の紙は一字も書き換へず、本紙にて訂す。

## 一. 固定の符 (本提出の唯一の基準)

* 固定 HEAD = 本 commit（本紙を含む commit。push 済・枝 `karo-second/receiver-envelope-preserve-12674e7c`）
* 固定 tree = 同 commit の tree
* 再現手順 = `git archive --format=tar <固定HEAD> | tar -x -C <素の砂場>`

### ★先便の符の訂★

| 便にて申したる符 | 実 | 訂 |
|---|---|---|
| `後像HEAD=92b3bdda…`（mutation_control_raw 本文内） | 当時の枝先端 | 本束の基準は上記 固定HEAD。92b3bdda は **測定時の先端**であり、束の基準ではない |
| `parent=190638e4…` | **file の sha256** | commit ではない。前像 commit = `71c725656bf533e4…` / blob = `2db21504…` |
| `後像 10 passed` | 三紙の和 | 母数を書かなんだは己の疵。内訳は下記 三. |

## 二. 紙の一覧

| path | 何 |
|---|---|
| `shim/hakudokai/hakudokai_secondpc_receiver_poll.py` | 直し本体（commit `6fbe7981`） |
| `tests/test_secondpc_downlink_owned_order.py` | 順の紙（4件） |
| `tests/test_secondpc_deadletter_envelope.py` | 封筒の紙（3件） |
| `tests/test_secondpc_samepc_role_routing.py` | 同PC宛の紙（3件） |
| `docs/evidence/receiver-order-12674e7c/mutation_control_raw_20260920_0557.txt` | 変異対照 生紙 |
| `docs/evidence/receiver-order-12674e7c/archive_repro_20260920_0612.txt` | archive 再走 生紙 |
| `docs/evidence/receiver-order-12674e7c/README.md` | 限りの明記 |
| `docs/evidence/receiver-order-20260920/artifact/receiver_poll.pre-order-fix.frozen` | 前像 凍結（blob `2db21504`） |
| `docs/evidence/ibwpc-ashigaru2-20260920/raw/ibwpc_stub_test_20260920_003403.txt` | ③ 二号 harness 生紙（blob `c1865a22f41b`） |

## 三. 「10 passed」の内訳 ―― 母数を字にて縛る

```
10 = 4 (test_secondpc_downlink_owned_order.py)
   + 3 (test_secondpc_deadletter_envelope.py)
   + 3 (test_secondpc_samepc_role_routing.py)
```

軍師の実測 `4 passed` は **order 単紙**にて正しく、己の `10` は **三紙の和**。
∴「再現不能」に非ず、**母数の違ひ**に御座る。生紙 = `archive_repro_20260920_0612.txt`。

## 四. 末尾空白 (git diff --check RC2) の扱ひ

生紙 二本が行末に空白を持つ。是は **取込の器が遺したる物**（行を `tr` にて畳みし為・
`python3 -V` の出力尾）であり、**生紙を書き換ふるは証の毀損**に当たる。
∴ 原本は一字も触れず、**空白を除きたる写し** `<原path>.ws-normalized` を併置す。

| 原 | 原 sha256 | 字 | 写 sha256 | 字 |
|---|---|---|---|---|
| `…/mutation_control_raw_20260920_0557.txt` | `4c7bcc563070594248ece1321128f6797795735fe564afe8f92fa01ef179acd8` | 2677 | `40cca11cabb4102d107c725f9937ed48a97b99872b36ea15443071b8c9bf4fdb` | 2675 |
| `…/receiver-order-20260920/raw/order_proof_20260920_021353.txt` | `138599210df0be863640817f81249cd858ba587fbd3e697394f569959284686e` | 3241 | `bb70c026c8fd8018983642702b1e2eae218443e55726ad7568f13fb20d6f5097` | 3240 |

差は **行末空白のみ**（2字 / 1字の減）。`sed 's/[ \t]*$//' <原>` と写しは `diff` 全一致。

## 五. ★出来ぬ事と、その因★

軍師 seq341228 は「③ raw を `038c8237` tree へ収載せよ」と仰せなるも、
`038c8237` は **共有枝 `feat/dd169-d006-conditional-exception`** の先端にして、

* 事業部長 06:06:06 裁 =「shared枝の push/merge/rewind **0**、裁定待ち」
* origin は `9311d157` 止まり（五つ未push）

∴ 家老は当該樹へ commit も push も撃てぬ。**本束の固定樹は上記 一. の枝 HEAD**であり、
`038c8237` ではない。収載の可否は 事業部長／総監督の裁を待つ（上申 seq=341020 / 341185）。

## 六. 限り (README と併せ読まれたし)

* 変異対照にて前後を分かつは 四本中 **一本のみ**（`test_envelopeless_downlink_row_is_not_dead_lettered`）。
* 「自己宛 かつ downlink 所有」の行が滞留せぬかは **未測**。
* 生きて居る 556行 `RECEIVER_SKIP_TARGETS` 系統は **同じ疵を抱へたまま・未直**。
