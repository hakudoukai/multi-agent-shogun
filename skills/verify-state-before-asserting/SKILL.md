---
name: verify-state-before-asserting
description: 「読んだ物の形」「枝の頭」「remote の実体」「母數」を ★断ずる前に 一 行 で確かめる★。2026-09-08 に家老mac が同型の誤りを 6 度 犯した(manifest の形式 3 度・枝の頭・stale ref・母數)。相手の紙を疑ふ前に 己の読み方を疑ふ為の手順。
---

# 断ずる前 に 状態 を確かめる

## いつ使う (= mandatory)

★次 の何れか を 人 へ言ふ 前★:
1. ★「其 の紙 の数 は合はぬ」「file が無い」「hash が違ふ」★ と言ふ前
2. ★「此 の枝/commit を押した」「merge されて 居る」★ と言ふ前
3. ★「origin は …」「remote には 無い」★ と言ふ前
4. ★「N 件 の内 M 件 が…」★ と ★割合 や 母數★ を言ふ前

## 使わない

- 己 が今 作つた 物 に就いて 言ふ 時(己 の出力 は己 が知る)
- 既 に同じ turn で 確かめた 事 を 繰り返し 言ふ 時
- 相手 が ★出典 と器 を添へて★ 出した 数 を そのまま 転記 する 時(転記 と明記 するなら 可)

## 必須チェック手順(★一 行 づつ★)

### ⑴ 紙 の数 が合はぬ と言ふ前
```bash
head -5 <manifest>          # ★形式 を見る★(path= 付か/生 の 64 桁か/12 桁 の頭か)
grep -in "正規化\|normali" <manifest> | head -2   # ★正規化後 の sha か★
```
★2026-09-08 に 三 度 落ちた★: ⑴r6 が 12 桁 の頭 なのに 64 桁 で grep ⑵manifest が
「正規化後」と書いて 居るのに 生 byte で hash ⑶母數 を 6 値 と思ひ 15 値 の答 と較べた。

### ⑵ 押した と言ふ前
```bash
git rev-parse <branch>                        # ★枝 の頭★
git merge-base --is-ancestor <asked-sha> <branch> && echo OK || echo "★頭 に無い★"
```
★commit を検めても 枝 の頭 を検めねば 意味 が無い★(2026-09-08 dr-m M2)。

### ⑶ remote に就いて 言ふ前
```bash
git fetch -q origin && git rev-parse --short origin/main
```
★局所 の ref は 黙つて 古びる★。「origin は 08-04 で止まる」は ★己 の ref が古かつた だけ★ で あつた。

### ⑷ 割合 を言ふ前
```
母數 は 幾つか / 相手 の母數 と ★同じ か★ / 己 は何 を数へたか
```
★相手 と母數 が違へば 答 も違ふ ―― 相手 が誤つて 居るのでは無い★。

## 過去事例

- 2026-09-08 家老mac が ★同型 の誤り を 6 度★(門書 6 通 に自記)。
  詳細: docs/incident_logs/2026-09-08_mac_disk_full_worktree_sprawl.md(併記)
  教訓: ★相手 の紙 を疑ふ 前 に 己 の読み方 を疑へ★。
  ★己 の器 の落ち を 門書 に書く 事 は 恥 では無く 器 の校正 で ある★。
