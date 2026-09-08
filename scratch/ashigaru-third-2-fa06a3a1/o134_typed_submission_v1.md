# o134 型の提出（八項）― order132「heads の印無し 15 本の生年」走 1・讀取のみ

## ① host 付き絶対 path ／ ② sha256(64) ／ 行数
| 何 | path | sha256 | 行 |
|---|---|---|---|
| 器 | `momizi-dx:/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o134_birthmark_absence_probe.py` | `225789cd63a8b4073f546646fdc30df0c92c60db761121ab34bea1c39747310a` | 204 |
| 生出力 | `momizi-dx:/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o134_run1_20260909_042907.txt` | `d0eb6b011dfac93b3325c6fad632a6048b5cdec1ffab012b424fdb1a0e2be305` | 35 |
| 一覧 | `momizi-dx:/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o134_birthmark_absence_20260909_042910.txt` | `488374693c1555b44b30dc63c5f0fc8162109d00a50f28d3db964518f2b48f8b` | 129 |
| 紙 | `momizi-dx:/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/after_delete_5668_gap_1483_readonly_v1.md` | `950cb37b63f28938fec88b0439d06e7abc5a59eec3b8656f82d9a65ad24846ce` | 2629 |

## ③ argv 逐語
```
/usr/bin/python3 scratch/ashigaru-third-2-fa06a3a1/o134_birthmark_absence_probe.py
```
（生出力 file の 1 行目に同文を持つ。★器は `/mnt/c/DentalBI/.git` を ★讀むだけ★・git を一度も実行せぬ・書込は `scratch/` のみ★）

## ④ 令の問と其の答
- **『印無し』の定めを紙の頭に（何を以て印と呼ぶか）** → 紙 §37-0。
  材＝`logs/<refname>`／**印有り**＝最古 entry の action が `branch: Created from` `checkout: moving from` `clone:` の何れかで始まる／
  讀めた別 action（空 message 含む）＝**印無し**／開けぬ・零 byte・解せぬ＝**讀めず**／帳が無い＝**別値**。
- **★其の定めで数が 15 に成るか（借り物にせぬ）★** → **成つた**。己の器で母数丙（o112 の heads **120** 本）を通し
  印有り 59 ／ **印無し 15** ／ 讀めず 46。**定めも数も食ひ違はず**。
  但し **母を変へれば 19**（甲∪乙 128 本）―― ★15 は「定め×母数」の数であり 母を書かぬ 15 は意味を成さぬ★。
- **① 何時出来たか** → §37-3 の表（15 本 悉く刻を書いた・JST）。早い 1 本＝2026-08-08T10:47:02、
  他 14 本＝2026-09-06〜09-08 の 3 日に集まる。
- **② 印が無い因を三択語で** → `器が付けぬ` **14** ／ `付けた後に消えた` **1** ／ `元より対象外` **0**（★0 も明記★）。
  分けた物差し＝最古 entry の **old_sha が 40 個の 0 か否か**（0＝此の帳の中で生まれた／非零＝帳の頭より前に在つた）。
- **③ 生年が測れぬ本は別値（0 と書かぬ）** → 測れた **14** ／ **別値(上限のみ) 1**（`wp-a1-a3-3-20260723`・n=2129）。
  **別値を 0 と書かず 母にも足さぬ**。

## ⑤ rc
`rc=0`（対照が外れれば `exit 3` で数を出さぬ機構。当走は 5/5 立つた）。

## ⑥ 走らせた場
`host=momizi-dx user=hakudoukai cwd=/home/hakudoukai/multi-agent-shogun`

## ⑦ 対照（同じ走・条 十四）
陽性 2（`branch: Created from` / `clone:` → 印有り）・陰性 3（空 message → 印無し/器が付けぬ、
old≠0 → 印無し/付けた後に消えた、零 byte → 讀めず）。**5/5 立つ**。合成の帳は `scratch/…/o134_control/` に置いた（`.git` に一指も触れぬ）。

## ⑧ 母数を足さぬ
- 母数甲 128（帳の在る heads）／母数乙 128（今 生きて居る heads・packed 127 行）／母数丙 120（o112 の heads）。
  **甲∪乙 = 128・丙 ⊂ 甲**。★三つを足すな★。
- 15 の内訳 14+1+0 = 15（三択語）／14+1 = 15（生年の質）。**讀めず 46・印有り 59 は別の帯であり 15 に足さぬ**。
- 讀めず 46 本の理由は悉く `zero-byte`（46/46）＝**印を論ずる材が無い ∴ 別値**。

## ⑨ 此の数が言はぬ事（紙 §37-4 と同じ）
- `old_sha=0` は「**此の帳の中での創生**」しか言はぬ ―― 枝を消せば帳も消える ∴ 同名で作り直しても 0 に成る。
  **★作り直しの有無は当弾で測つて居らぬ（確かめて居らぬ）★**。
- `付けた後に消えた` は「誰かが消した」の意ではない。**最古より前が現存せぬ**事のみ。**下手人は測つて居らぬ**。
- 刻は帳の epoch を JST へ直した物＝**器の時計が正しい前提**（時計は検めて居らぬ）。
