---
name: ephemeral-worktree-hygiene
description: 一時 worktree を切る 器(dino:check:clean 等)を作る/直す/走らせる 前 に、後始末・上限・名 の限り を検める。2026-09-08 Mac disk 満杯(worktrees 237GB・残 760Mi)の再発防止。証跡 を PR tip へ載せる 時 の「指す 物 と 指 の乖離」も併せて検める。
---

# 一時 worktree と 証跡 の衛生

## いつ使う (= mandatory)

★次 の何れか に当たる 時★:
1. ★一時 worktree を切る 器 を 書く/直す★(`git worktree add` を含む script)。
2. ★同じ 器 を 3 回 以上 走らせる 段取り★ に入る 時(門 の代走・比較 の走 等)。
3. ★証跡(manifest・raw)を PR の枝 へ載せる★ 時。

## 使わない

- 樹 を 1 回 だけ 切つて 直ちに 消す 手作業(= 積む 余地 が無い)。
- 常設 の worktree(`DentalBI-*` 等・使ひ捨て では無い)の話。
- disk が逼迫 して 居らぬ 事 を確かめた 上 で の ★読取 のみ★ の作業。

## 必須チェック手順

### A. 器 を書く/直す 時
```bash
# ⑴ 後始末 が在るか(走了 と ★失敗 の走★ の両方)
grep -n "worktree remove\|finish()" <script>
# ⑵ 上限 が在るか
grep -n "KEEP\|上限\|tail -n +" <script>
# ⑶ 掃く 対象 が ★名 で限られて 居るか★(席 の樹 を巻き込まぬ)
grep -n "tmp-dino-clean-\*\|case .* in" <script>
```
★三 つ とも 無ければ 足す★。★負テスト 3 形★(連続 2 走 で樹 が増えぬ/失敗 の走 でも掃かれる/
他人 の樹 が残る)を ★実撃 して raw に残す★。

### B. 走らせる 前
```bash
df -h /System/Volumes/Data | awk 'NR==2{print $4" free "$5}'
ls -d <repo>/.claude/worktrees/tmp-* 2>/dev/null | wc -l
```
★free < 20Gi または 一時樹 > 10 なら 先 に掃く★(lsof で使用中 0 を確かめてから)。

### C. 証跡 を PR の枝 へ載せる 時
```bash
# ⑴ manifest が指す 原物 が ★tip に在るか★ ―― 手元 では無く tip で走らせる
cd <worktree-at-tip>/<evidence-dir> && shasum -a 256 -c _manifest.txt
# ⑵ 其 の弾 は docs のみ か・★製品 を変へるか★
git show --stat <tip> | grep -E "\.tsx?$|\.ts$|src/"
```
★⑵ が非空 なら「正本 N/A」は ★使へぬ★★ ―― 正本 の節 を名指す。


## ★器 の在り処(2026-09-08 追記)★

★紙 が名指す 器 は 紙 の読み手 が手 を伸ばせる 所 に在らねば ならぬ★。
本日 の実測(家老mac と 專任1 の掃き):

| 在り処 | 何 が起きたか |
|---|---|
| ★`/tmp`★ | 專任1 の紙 15 枚 が指す 器 ★8 本★ ―― 写 有 3・★写 無 4★・★既 に死 1★。 |
| ★`~/bin`★ | ★`karo_mac_gate7.sh` は 67 の紙 が名指す のに ★どの repo にも無い★★。 |
| 証跡 dir | ★死んでも 事 が済んだ★ ―― 死んだ 器 の代りに 写し が在つた(実害 0)。 |

★`/tmp` は「消える」と知られて 居る 分 まだ よい★。
★`~/bin` は「在るのが当り前」と思はれる 分 ★誰 も見ぬ★★ ―― ★重い のは 此方★。

### 走らせる 前 / 紙 を出す 前 の一 行
```bash
# 己 の紙 が名指す 器 が 何処 に在るか を数へる
grep -rhoE '(~|/tmp)/[A-Za-z0-9_/.-]+\.(sh|py|ts)' <papers> | sort | uniq -c | sort -rn
```
★写し を採る 時 は ★byte 同一 を cmp で測り 陽性対照 を添へよ★★
(★名 が同じ だけ で 中身 が違ふ 写し は 写し では無い★)。
★凍つた 紙 の証跡 dir へは 足すな★ ―― ★完全ID(manifest)が壊れる★。★新しい dir へ★。

## 過去事例

- 2026-09-08 Mac disk 満杯(460Gi 中 残 760Mi)。因= `dino:check:clean` が commit 毎 に樹 を切り
  ★消さぬ★ 設計(頭書 逐語「worktree は消さない(存置・次回再利用)」)。67 樹 が積み 237GB。
  詳細: docs/incident_logs/2026-09-08_mac_disk_full_worktree_sprawl.md
  教訓: ★「使ひ捨て」と名 に書いた 物 は 器 が己 で捨てねば ならぬ★。
- 2026-09-08 証跡 の二 疵(同日・同 じ人)。manifest だけ を tip へ写し 原物 を写さず(rc=128)/
  製品 を変へる 枝 に「正本 N/A」。
  教訓: ★己 の手元 で正しい 事 は 受け手 で正しい 事 を意味 せぬ★。

## 追記 2026-09-08 ―― ★台 の力(CPU)も 掃除 の内★

★掟 の穴 が出た★: 家老 は「席 が捕り/門 を走らせて 居る 間 は ★共有樹 で git を走らせぬ★」を
己 に課して 居た が、★之 は git の話 で あり 台 の力 の話 では 無かつた★。
2026-09-08 14:5x、專任1 が 15 捕り を走らせて 居る 最中 に 家老 が 8 段(playwright ★4 worker★・
chrome が %CPU 48〜50 を 4 つ)を同じ 台 で回し、★專任1 の 1 走 が 900 秒 の timeout で落ちた★。
(★因 は未測★ ―― 時 の重なり は 因 の証 に非ず。專任1 も 家老 も 断じて 居らぬ)

### 走らせる 前 の一 行(B に足す)
```bash
ps -eo pid,pcpu,command | grep -E "playwright|chrome|dino-kit" | grep -v grep | head
```
★席 の捕り が動いて 居たら 8 段 は待つ★。急ぐ なら ★先 に席 へ告げ 席 の都合 を訊く★。
★捕り は 刻 を測る 仕事 で あり 台 の力 を奪はれると 落ちる★。
