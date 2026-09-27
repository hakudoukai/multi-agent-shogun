# 板 2e654902 km-227 再測 ―― .bak 三形の表 と 不在 pane の偽の待機

- 席: ashigaru-mac-1（専任1）／差配: karo-mac（goal 2026-09-28 07:16・便 msg_20260928_071702_8396ff59）
- 枝: `ashigaru-mac-1/b2e654902-km227-saisoku-20260928`（自席 worktree `/Users/momizimac/wt/a1-2e654902`）
- 基: origin/main `b9573b2d376e9a0a372234b696a733677feb7919`
- 前の束: km-227 `e4df8056150fe85417fac7d45428fd34e53b512d`、km-227b `1288610b…`（どちらも改変していない）。軍師mac の seq342642「固定commit/tree・artifact/raw・正負復元/clean を揃えて別親で判定」に答えるため、**今の main で撮り直した**。

## ① 版の組

| 名 | commit | inbox_watcher.sh blob | lib/agent_status.sh blob |
|---|---|---|---|
| main | origin/main `b9573b2d376e9a0a372234b696a733677feb7919` | `778d233445de00b0ac1df9b464dd135024046402` | `e99b4d3bc4bf104f8701e7e4d4adca35d8e165ed` |
| fix | `a764b314fb584a38438e0e8a6d25bcebf1b9f061`（枝 `ashigaru-mac-1/3859cda0-ko3-ko4-20260925`） | `2b509eb4323f7921ceb77f38328d965081f3db91` | `b637b672eff0319d21d52608fa42c98c712db4b9` |

`raw/00_versions.txt` の各行は「名・ref・git の blob 2本・sandbox に写した disk の hash-object 2本」で、disk と git は一致している。
fix は **main に入っていない**（`merge-base --is-ancestor a764b314 origin/main` rc=1、それを含む枝は上の1本だけ）。
commit と tree の 40 桁は、本束の commit 後に家老への便で示す（紙は自分を含む commit の sha を書けない）。

## ② 何を測ったか

### ㋑ 不在 pane の偽の待機（sandbox・mock tmux）

`harness/run_case.sh` が、sandbox（`.sbx/ver_{main,fix}`。scripts/ と lib/ を写しただけで本物の watcher・tmux・受信箱には触れない）の watcher を source し、未読1件の試料箱で `process_unread` を1回呼ぶ。PATH の先頭に置く mock tmux は3種類。

- `absent`: pane が不在。display-message は rc=0 で空を返し、capture-pane は rc=1。
- `negctrl`: 陰性対照。pane が居て作業中（`esc to interrupt` を返す）。
- `idle`: 陽性対照。pane が居て待機中（`❯` だけを返す）。本束で新しく足した。

`sendkeys` は mock が記録した send-keys の回数。`agent_is_busy_rc` は `agent_is_busy()` を直に呼んだ戻り値（0=busy、1=idle）。

最終の撮り（`raw/12_run_all.*`、rc=0、stderr 0 byte、18 場面、場面ごとの raw は `raw/run3_cases/<名>/`）:

| 場面 | main busy_rc | main sendkeys | fix busy_rc | fix sendkeys |
|---|---|---|---|---|
| claude absent | 1 | **3** | 0 | **0** |
| claude negctrl（陰性） | 0 | 0 | 0 | 0 |
| claude idle（陽性） | 1 | 3 | 1 | 3 |
| codex absent | 1 | 0 | 0 | 0 |
| codex negctrl（陰性） | 0 | 0 | 0 | 0 |
| codex idle（age≈0） | 1 | 0 | 1 | 0 |
| codex idle age150（陽性） | 1 | 5 | 1 | 5 |
| codex absent age150 | 1 | **5** | 0 | **0** |
| codex absent age250 | 1 | **5** | 0 | **0** |

読み方:
- main は不在 pane を「待機」と読み、居ない相手へ send-keys を撃つ（claude 3・codex の昇圧 5）。これが 9/20 の km-227b と同じ値で、今の main でも直っていない。
- fix は不在 pane を busy に倒し、撃たない（全て 0）。
- 同じ fix が idle の陽性対照では撃っている（claude 3・codex age150 5）。つまり fix の 0 は「何も送らなくなった」のではなく、不在の時だけ止まっている。
- codex の age≈0 で main・fix とも 0 なのは、codex 経路が age 120 秒前後まで nudge を控えるため。陽性対照を age150 で取ったのはそのため。

撮りは3回あった。捨てていないので raw に残している。
- `raw/10_run_all.*` と `raw/run1_cases_no_idle_ctrl/`: 陽性対照を足す前の 12 場面。
- `raw/11_run_all.*` と `raw/run2_cases/`: claude/codex idle を足した 16 場面。codex idle が age≈0 で 0 になり、陽性対照になっていなかった。
- `raw/12_run_all.*` と `raw/run3_cases/`: codex idle age150 を足した最終。

3回の間で同じ場面の値は全て一致している。`harness/run_all.sh` は最終の版で、1・2回目との違いは出力 dir 名と場面の一覧だけ。

### ㋐ .bak 三形の表（読取）

器 `harness/km_bak_sankei_hyou.py` は e4df8056 の束の器を写したもの（blob `eb436639a4d93f2ea630ccf8d54c6616f5b9899e`、写した disk も同じ。`raw/20_instrument_blob.txt`）。

| 樹 | HEAD | rc | 当たった file | old_excluded | new_excluded | changed |
|---|---|---|---|---|---|---|
| 共有樹 `/Users/momizimac/multi-agent-shogun` | `10000ff8…` | 0 | 24 | 23 | 24 | 1 |
| 自席 worktree（=origin/main） | `b9573b2d…` | 0 | 0 | 0 | 0 | 0 |

- changed の1本は 9/20 と同じ `./shutsujin_departure.sh.karo-mac-bak-20260820T000340`。form3（`-bak-`）だけに当たる形で、旧器は除けず新器は除く。
- 9/20（22本）との差は、その後に置かれた2本だけ（`raw/22_paths_diff.txt`）。どちらも form1/form2 に当たるので changed は増えない。
  - `./scripts/inbox_write.sh.bak-karohermes-20260924`
  - `./scripts/watcher_supervisor_mac.sh.bak-dedupe-20260926`
- 24本は全て git に追跡されていない（`git ls-files` で 0 本）。main の worktree で 0 本なのはそのため。

## ③ raw

`raw/` の各撮りに timestamp・argv・cwd・rc・stdout・stderr がある。rc は管を通さずに file へ書いた。

## ④ lockfile

該当しない（依存の導入なし）。

## ⑤ 数字が意味しないこと

- **fix は main に入っていない。** 今動いている watcher（版 778d2334）は不在 pane へ撃つ。本束は直った版の振舞いを sandbox で示しただけで、本番を直したわけではない。merge と push は本弾の外（総監督の代行）。
- mock tmux の上での振舞いであって、本物の tmux や本物の watcher 過程では測っていない。不在 pane で display-message が rc=0・空を返すことは、9/20 の束で本物の tmux を使って測ってある（本束では撮り直していない）。
- `agent_is_busy_rc` は関数を直に呼んだ値で、watcher が rc=2 をどう読むかは `sendkeys` の方で見る。fix の direct rc が 0 なのは、fix 版の `agent_is_busy` が内部で rc=2 を busy に倒しているため。
- .bak の表は「watcher の census 器がどの file を器として数えるか」の表であり、.bak の file を消すべきかどうかは言っていない。消すかどうかは本弾の外。
- 共有樹の 24 は測った時刻の値で、共有樹は他の席も書くので増えることがある（`raw/21_bak_shared.timestamp`）。

## ⑥ 復元と clean

- 共有樹へは読むだけ（器を cwd `.` で走らせた）。書いていない。
- sandbox（`.sbx/`）は自席 worktree の中にあり、.gitignore の `*` で無視される。commit には入れない。
- commit 前の自席 worktree: `git status --porcelain -uall` は 0 行、`--ignored` は 2 行（`!! .sbx/` と `!! <本束>/`）。`raw/90_before_commit_*`。
- commit 後の行数は、この紙を含む commit の後にしか測れないので、家老への便に書く。
- `/tmp` に `testagent` の名の file は 0 本（harness は watcher の fingerprint を場面ごとの出力 dir へ向けている）。

## ⑦ 法令の根拠

該当しない。

## 束の file

`SHA256SUMS`（自分自身は含まない）に全ての file の sha256 がある。
