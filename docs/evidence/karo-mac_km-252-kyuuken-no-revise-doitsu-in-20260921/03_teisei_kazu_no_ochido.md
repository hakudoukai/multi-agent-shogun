# 03 ―― 數の訂（家老mac の落度 ㊿+13）

## 何を誤つたか

初めの commit message（b0b9105865…・**本 amend で置き換へた**）に逐語こう書いた:

> 束 disk 27 = 臺帳path 24 + 臺帳1 + 門の札2(宣した除外)

**★之は誤りである★**。正は:

```
束 disk 33 = 臺帳path 24 + 臺帳 1 + 門の札 8
```

門の札 8 枚の名（逐語）:
`90_manifest_append.out` `90_manifest_append.err`
`91_dasumae_gate.out` `91_dasumae_gate.err` `92_dasumae_gate.rc`
`93_dasumae_gate_base.out` `93_dasumae_gate_base.err` `94_dasumae_gate_base.rc`

## 機序（何故誤つたか）

「束 disk 全 file = 27」を測つた刻は**臺帳を建てた直後**であり、**門は未走であつた**。
其の後に門を二度走らせ（基点無し=對照／基点=. の本走）、札 6 枚が生れて 33 に成つた。
**當職は臺帳建て直しの刻に測つた數を、commit の刻の數として書いた。**

## 條に照らして

- **「A census with no 刻 becomes a lie」**（己の memory 条）――
  當職は 27 に刻を付けずに commit message へ焼いた。刻を付けて居れば誤りに成らなかつた。
- **門の札は走らせる度に増える** ∴ 「門の札 = N 枚」を固定値として書くな。
  **commit の刻に `git ls-tree -r --name-only HEAD` で測つた數を書け**（本 amend では之を用ゐる）。

## 捕へた器

```
git ls-tree -r --name-only HEAD -- <束> | sort   ＞ commit 側
find <束> -type f | sort                          ＞ disk 側
comm -23 / comm -13                               ＞ 双方向の差
```
出目 = **commit 33 / disk 33 / 双方向の差 0**。
∴ commit と disk は一致して居り、**誤つて居たのは「27」という宣だけ**であつた。

## 臺帳との関係

本紙 03 は**臺帳を建て直してから**門を走らせる ∴ 臺帳 path 行は **24 → 25** に成る。
（臺帳は本紙を含み、門の札は含まぬ ―― 02 で宣した除外の儘）
