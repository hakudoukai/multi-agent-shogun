# ★型で出す★ ―― order131「圧の増え方（GiB/日）」提出紙（走 2）

as_of 2026-09-09 04:0x JST ／ 席 ashigaru-third-2 ／ 令 `msg_20260909_040202_8f84cfa8`（始業・order131）
★digest の種＝`sha256`★（git blob の sha1 ではない ―― 種を書かねば同じ file が二つの数を持つ）。
★本紙は走 0★（`sha256sum` `wc -l` `hostname` `id -un` `pwd` は調べる走行ゆゑ走に数へぬ・本 lot 通しの定義）。

---

## ⑥ host / user / cwd（共通）

```
host=momizi-dx  user=hakudoukai  cwd=/home/hakudoukai/multi-agent-shogun
```

## ① path（repo 相対 ＋ ★host 付き絶対★）／ ② sha256 完全 64 桁 ／ 行数 ／ 追跡の別

★host 付き絶対★＝下の相対 path の前に `momizi-dx:/home/hakudoukai/multi-agent-shogun/` を付けた物（全件同形）。

| # | repo 相対 path | 行 | sha256（完全 64 桁） | 追跡 |
|---|---|---|---|---|
| 1 | `scripts/sweeps/audit_disk_pressure.sh` ★器・mode 0755★ | 402 | `94fe338d2e1beafdcbd33faaa3e27cc90e451c2c5b243c4c857609b3e8071955` | ★untracked（作業樹）★ |
| 2 | `scratch/ashigaru-third-2-fa06a3a1/o133_run1_sample_20260909_040745.txt` ★生・走1★ | 27 | `583975388f5917573e46cee412bb04b8dd4fb5a936bdfb4f2810e8b96663fbbc` | ★untracked★ |
| 3 | `scratch/ashigaru-third-2-fa06a3a1/o133_run2_growth_20260909_040757.txt` ★生・走2★ | 27 | `5c1bf05a38bd643cefe195cd7584b6c197f5283f5eda7623221381bd1aabfee3` | ★untracked★ |
| 4 | `scratch/ashigaru-third-2-fa06a3a1/after_delete_5668_gap_1483_readonly_v1.md` ★紙・§36 を併記★ | 2540 | ★commit 後に本紙 §末へ記す★ | ★untracked★ |

★「untracked」は 本紙を書いた刻の状態である★ ―― 本弾は此の後 ★commit で凍らせる★（押しは家老）。
★凍らせた後は `git show <枝>:<path>` で 軍師third の樹からも当たれる★（o131 §0 で「渡し方の疵」と書いた件の手当）。
★但し 押して居らぬ間は ★third PC の当席の樹にしか無い★★ ―― 之を隠さず書く。

## ③ argv 逐語 ／ ⑤ exit code

```
走1: bash scripts/sweeps/audit_disk_pressure.sh --sample
     rc=0
走2: bash scripts/sweeps/audit_disk_pressure.sh --growth \
       scratch/ashigaru-third-2-fa06a3a1/o128_run1_raw.txt \
       scratch/ashigaru-third-2-fa06a3a1/o128_run2_raw.txt \
       scratch/ashigaru-third-2-fa06a3a1/o128_run3_raw.txt \
       scratch/ashigaru-third-2-fa06a3a1/o128_run4_raw.txt \
       scratch/ashigaru-third-2-fa06a3a1/o129_run1_3pc_20260908_184527.txt \
       scratch/ashigaru-third-2-fa06a3a1/o133_run1_sample_20260909_040745.txt
     rc=0
```
★argv と rc は 生 file の 1〜2 行目に ★逐語で載せて在る★★（後の者が本紙を信ぜずとも生から読める）。
★材料 6 本は讀取のみ★・★器は file を一つも作らぬ★（吐くのは標準出力のみ・落としたのは当席の python）。

## ④ 令の問ふ三つ

### ①二点以上の刻
| 何 | 刻 | used | 粒 |
|---|---|---|---|
| ★古い方（採つた点）★ | 2026-09-08T18:16:06+09:00 | `prior_used_b=261993005056`（244 GiB） | ★gib_rounded★ |
| ★今★ | 2026-09-09T04:07:57+09:00 | `cur_used_b=265937563648` | byte |
| 隔たり | `span_s=35511` ＝ ★9 時間 51 分 51 秒★ | `delta_b=3944558592` | ― |
`n_points=15`（材料 6 本から momizi-dx `/` について拾へた点の数）。★最も古い点を採つた★＝隔たりを最大に採り 丸めの疵を小さくする為。

### ②増え方（GiB/日）★器の言葉・逐語★
```
DISKGROWTH host=momizi-dx target=/ gib_per_day=8.936 gib_per_day_milli=8936 span_s=35511
 n_points=15 granularity=gib_rounded prior_used_b=261993005056 cur_used_b=265937563648
 delta_b=3944558592 exceeded=yes growth_max_gib_per_day=5 resolution_gib_per_day=2.433
```
★8.936 GiB/日・閾 5 を超えた（exceeded=yes）★。
★★数の意味せぬ事を併記する★★:
- ★此の数は ±2.433 GiB/日 の幅を持つ★ ―― 過去の点が ★GiB 丸め★ ゆゑ ±1 GiB が `86400/span` 倍に化ける。
  器は其れを ★同じ行に `resolution_gib_per_day` として吐く★（数だけ抜いて誤らぬ様に）。
- ★之は「一日測つた」数ではない★ ―― ★9.86 時間の二点を 日へ延ばした★数である。
- ★何が増えたかは言つて居らぬ★（どの dir かは本弾の器では測つて居らぬ）。
- （★己の引き算・器の出しに非ず★: 下端 8.936−2.433＝6.503 で尚 5 を上回る。★器の数は上の一行のみ★。）

### ③測れなかつたは別値の儘（★0 に足さぬ★）
| 型 | 本数（★出力 1 行を 1 と数へた★） | 意 |
|---|---|---|
| `DISKGROWTH` | ★1★ | 率を出せた |
| `DISKGROWTH_WITHHELD` | ★1★ | ★短い ∴ 出さぬ★ |
| `DISKGROWTH_UNMEASURED` | ★15★ | 過去の点が無い（`why=no_prior_point`） |

★出さなんだ 1 行（逐語）★:
```
DISKGROWTH_WITHHELD host=momizi-dx target=/init status=span_short span_s=12 delta_b=0
 n_points=2 granularity=byte min_span_s=3600
```
`/init` は ★走 1 と走 2 の間 12 秒★ しか隔たりが無い ∴ ★率を出さぬ★。
令の逐語「★二点の差が短ければ『短い』と書け（推し量つた増え方を出すな）★」を
★人の筆でなく 機構で★ 守らせ ―― ★其の機構自体に陽性対照を置いた★（下の ㋒）。
★測れなかつた 15 件★＝`/mnt/c` `/mnt/d` `/run/*` `/mnt/wsl*` 等。★0 と書かず・母数にも足さぬ★。

## ⑦ 正負の対照（★同じ走の中に★・条 十四）

`SELFTEST_GROWTH result=STANDS legs=positive_rate,negative_zero,short_withhold,span_zero growth_max_gib_per_day=5 min_span_s=3600`

| 脚 | 組み方（★閾から組む★） | 期する | 出た |
|---|---|---|---|
| ㋐ ★陽性★ positive_rate | 閾+1 GiB を ★丁度一日★ | rate==(閾+1)*1000 | ★合ふ★ |
| ㋑ ★陰性★ negative_zero | 同じ used を 一日 | ok かつ rate=0 | ★合ふ★ |
| ㋒ ★「出さぬ」の陽性★ short_withhold | `DP_MIN_SPAN_S/2` に 1000 GiB | ★span_short・率 "-"★ | ★合ふ★ |
| ㋓ ★同上★ span_zero | 隔たり 0 | ★span_zero・率 "-"★ | ★合ふ★ |

★合成値であり実測に非ず★（器が自ら其の註を吐く）。
外れれば `ABORT reason=selftest_growth_did_not_stand` ★率を一つも出さず exit 3★。
`DP_MIN_SPAN_S -lt 2` なら ★対照を組めぬ ∴ FAILED_TO_STAND★（黙つて通さぬ）。
★前の走（`SELFTEST` / `SELFTEST_CANON leg=vhdx_225_99 FIRES`）も同じ走で鳴つて居る★（走 1・走 2 とも）。

## ⑧ 母数と「測れなかつた数」を別値（★足さぬ★）

| 母数 | 値 | 註 |
|---|---|---|
| ★本弾の PC★ | ★measured 1★（third＝momizi-dx） | ★他 2 台は本弾で ★測つて居らぬ★（走らせて居らぬ）★。Mac は ★探さぬ★ |
| ★mount（third 内）★ | 率 1 ／ 短い 1 ／ 過去の点無し 15 | ★足さぬ★（17 と書けば「17 を測つた」と読まれる） |
| ★材料の生 file★ | 6 本（讀取のみ） | 内 5 本は前弾の凍結生・1 本は本弾の走 1 |

## ★食ひ違ひの開示（隠さぬ）★

走 1 `used_b=265936404480` と 走 2 `cur_used_b=265937563648` は ★12 秒で 1,159,168 byte 違ふ★。
★走 2 は己で今を測り直して居る★（走 1 の値を持ち回つて居らぬ）∴ ★二つの走の「今」は別の今★ である。

## ★二重実装を避けた証（先に数で立てた）★

`grep -rl 'growth|per_day|増え方' scripts/ shim/ lib/` ⇒ ★3 本★。中を読んで用途を分けると
`hermes2_deaddrop_stale_detector.sh`＝未読 ID の増え方／`hakudokai_fukuincho_reverse_poll.py`＝別用途
∴ ★ディスク使用量の増え方を出す器は 0 本★ ―― 故に ★新器を作らず 己の器 1 本を 211→402 行へ延ばした★。
（★何を 1 と数へたか★＝grep が名を挙げた file 1 本を 1。用途を分けたのは己の目である。）

## ★動かさぬ物★

push 0（★押しは家老★）・DB 0・SQL 0・消す/移す/圧す 0・hook 不触・D 樹不触・
他 PC 0・Commander の箱 0 打・Mac は探さぬ・/tmp 0・共有 `.git` 書込 0。
