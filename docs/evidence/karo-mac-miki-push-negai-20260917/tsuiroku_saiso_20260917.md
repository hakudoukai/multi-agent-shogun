# 追録 ―― 固定頭 68b6e07b での再走(裁 seq326349)

★此の紙は README.md を書き換へぬ★。提出済の紙は一指も触れず、改めは別紙に置く。

    README.md            sha256=866154237959606bf7783563cbca9fcba0985f707e1a61b8f25ddeffa5da1cb2
    MANIFEST.txt(追記前) sha256=010f201bf31620a1f19a60698bf26190aaf6e05af71002155efb5ab066278d43

## 一 何を求められたか(軍師mac 326273 → 総監督 326349 の逐語)

「提出 raw が親 363d5fb0 の --mae 走行で、固定 head 68b6e07b での再走 raw・生成3本の
manifest・PR ref の到達が無い。同枝で head 再走(候補差分/門/対照)の raw と manifest を
commit し push 願いを寄越せ。註: CI は請求起因で全 job 未起動(dev_qa#1099)ゆえ CI 緑は
要件から外す(軍師mac へも伝える)」

## 二 何を走らせたか ―― ★器を増やさず、同じ器へ頭を渡した★

| 求め | 器 | 出目 |
|---|---|---|
| 候補差分・対照 | driver/40_atarashii_atama.py **68b6e07b** | raw/50_atama_head68b6e07b.txt |
| PR ref の到達 | driver/50_ref_toutatsu.py **68b6e07b**(新) | raw/51_toutatsu.txt |
| 門 | scripts/checks/karo_mac_dasumae_gate.sh | gate_dasumae_*.log(本走) |
| 臺帳 | karo_mac_manifest_append.py(唯一の書き手) | MANIFEST.txt へ★追記のみ★ |

40 は元より頭を引数に取る形ゆゑ、新しい器は建てて居らぬ(二重実装を避く)。
raw/40_atama.txt(--mae 走)は上書せず、走らせた後に commit から戻して★sha 不動★を確かめた
(前=937c2faedacf7a72 / 後=937c2faedacf7a72 / 臺帳の宣=937c2faedacf7a72)。

## 三 數 ―― --mae 走 と 68b6e07b 走 の差

| 欄 | --mae(親 363d5fb0) | ★68b6e07b★ | 差 |
|---|---|---|---|
| 乙 足した行 | 15144 | 15758 | +614 |
| 乙 触れた file | 464 | 476 | ★+12 ＝ 束の12本そのもの★ |
| 陽性対照 | 2/2 鳴 | 2/2 鳴 | ― |
| 乙 当り | 0 | 0 | ― |
| 束 当り | 0(本 11) | 0(本 14) | ― |

∴ ★最初の REVISE の因(紙が commit の外に在り固定検証できぬ)は消えた★ ――
束の12本は今や頭の側の「足した行」の中に在り、其の上で当り 0 である。

## 四 到達(raw/51_toutatsu.txt)

- 甲 紙の到達 = ★12/12★(頭の tree に在り、中身も disk と異 0)
- 乙 ref の到達 = 手許 1 本(refs/heads/karo-mac/km-gate-kou-otsu-20260917)・遠隔 ★0 本★。
  遠隔 0 は★未 push★を意味するのみ。push は総監督の代行が正路ゆゑ當席は commit で止める。
- 前の PR 頭 363d5fb0 は 68b6e07b の★祖先★(rc=0)＝同枝を前へ進めた形であり、書換では無い。

## 五 ★己の器に見付けた疵(隠さず書く)★

50_ref_toutatsu.py の初走は「到達 0 本 / 不到達 13 本」と出した ―― ★偽である★。
因: git ls-tree の pathspec は ★cwd 相対★ で、束の中から走らせた故に空を返した。
陽性対照は git cat-file -e の <rev>:<path>(★根相対★)を通したゆゑ鳴らず、
即ち ★對照が、數を出した器とは別の約束を検めて居た★。
治し: 悉くの git 呼出へ -C <根> を噛ませ、--full-tree を足し、
★ls-tree の出目自身にも對照★(MANIFEST.txt が出目に在るか)を置き、無ければ止める(rc=5)。

## 六 ★此の數が意味せぬ事★

- 「当り 0」は「repo の歴史に secret が無い」の証に非ず。測つたのは
  origin/main...68b6e07b の★足した行★と★束の全byte★のみ。基に既に在る物は母數の外。
- 基に既に在る緩形 6 行(SECURITY.md:47 / tests/test_karo_second_send_iincho.bats:123,138,162,231 /
  tests/unit/test_ntfy_auth.bats:50)は★本 PR の可否とは別件★として理事長筋へ上申する(README 六-4 と同じ)。
- 本走の後に生れる紙(此の追録・raw/50・raw/51・臺帳・門の控)は束の母數の外に残る。
  之は再走の度に一つ後ろへ動く影であり、頭を固定した本走で消せる物では無い。名は raw/51 に悉く列べた
  (不到達 4 本 = driver/50_ref_toutatsu.py・raw/50_atama_head68b6e07b.txt・raw/51_toutatsu.txt・本紙)。
- CI は dev_qa#1099(請求起因で全 job 未起動)により★緑を要件から外す★裁が出て居る。
