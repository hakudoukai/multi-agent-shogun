# order88: git が pre-push hook を呼ぶ時の `$0` を隔離 repo で實測した (走 1・本物 hook 不触)

as_of 2026-09-08 07:2x JST / 席 ashigaru-third-2 / 令 order88 (家老 `msg_20260908_072438_fb84d642`)
令 逐語:「★走 1 本 許す=order88(隔離 repo で $0 の basename を実測=C の前提)★。因=★前提を測らぬ案文は出す方が害★。本物の hook は一指も触れるな。」
前紙 o87 `4a43a3285d416605`(148 行) §5-1「確かめて居らぬ」を承ける。★前紙は書き換へず本紙で補ふ★。
規 = `scratch/ashigaru-third-2-fa06a3a1/o88_dollar0_probe.py` (115 行・sha16 `6f350d62bd98eb76`)。生の値 = `o88_lab/o88_result.json`。
1 = 走 1 回 / file 1 本。走行 ★1 回★・elapsed ★0.1 秒★ (己に課した上限 180 秒)。

## §1 場の作り (何を 隔離したか)

- 場 = `scratch/ashigaru-third-2-fa06a3a1/o88_lab/` に `origin.git`(bare) と `work` を建てた。remote は ★local path★ ∴ network 0。
- 本物 `/mnt/c/DentalBI/.git/hooks/` は ★讀んだのみ★ (`pre-push.bak-loadshed-20260907` の byte を讀み、写しを隔離 repo で使つた)。
  讀んだ時の sha16 = ★`6284d288f4f4e21d`★ (o87 §1 と同値 = 走の前・走の了り いづれでも本物は動いて居らぬ)。
- 隔離 repo の user.email/user.name は ★其の repo の local config のみ★ に置いた (全域 config 不触)。

## §2 測つた 5 項と出た値 (逐語)

| # | 測つた事 | 出た値 (逐語) | 読み |
|---|---|---|---|
| ① | `$0` の生値 | `PROBE_DOLLAR0=[.git/hooks/pre-push]` | git は ★repo root からの相対 path★ で呼ぶ |
| ② | `basename "$0"` | `PROBE_BASENAME=[pre-push]` | ★案文 C の前提は成り立つ★ |
| ①' | hook の cwd | `PROBE_PWD=[…/o88_lab/work]` | ★repo root★ で走る |
| ③ | 門付きの写しを `pre-push` の名で置き push | `rc=1` / `[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。` + 戻し方の 1 行 / git の `error: failed to push some refs` | ★門が鳴り push が止まつた★ |
| ③' | 同じ門付きの写しを `.bak-…` の名で置き push | `rc=0` / 出力 ★0 行★ | ★鳴らぬ★ (名が違へば `$0` も違ふ) |
| ④ | probe を `.bak-…` の名だけで置き push | `rc=0` / 出力 ★0 行★ | ★git は `pre-push` といふ名の file しか呼ばぬ★ |
| ⑤ | `install.sh` を走らせた後の `.git/hooks/` | 退避 file は ★在る儘★・sha16 ★不変★ (`26a7ad641d1a6534` 前後同値) / `pre-push` が ★新たに作られ★ sha16 = src の値と一致 | ★install は退避を触らず・正規版で `pre-push` を作る★ |

- ③ で使つた門付きの写し = 本物 bak (61 行) の shebang 直後に門 10 行を挿した物・71 行・sha16 `26a7ad641d1a6534`。
- ⑤ の `install.sh` は ★本物 `scripts/git-hooks/install.sh` の写し★ を隔離 repo で走らせた (本物 repo では走らせて居らぬ)。
  出力逐語 `[hooks] installed: pre-push`。

## §3 ∴ 何が定まつたか

1. ★案文 C の前提は成り立つ★ ―― `basename "$0"` は `pre-push` に成る (①②)。o87 §5-1 の「確かめて居らぬ」は ★是で埋まつた★。
2. ★門は「名を戻した時だけ」鳴る★ ―― `.bak-…` の名の儘なら鳴らぬ (③')。退避 file を退避のまま置く限り、門は無音である。
3. ★git は名で選ぶ★ ―― `pre-push` といふ名の file だけを呼ぶ (④)。∴ 退避 file が今 走つて居らぬのは名に依る (o78 §2 #3 の読みが實測で裏付いた)。
4. ★install.sh は退避を触らず、正規版で `pre-push` を作る★ (⑤) ―― o87 §3 の読み (讀取のみで立てた) が ★走らせて裏付いた★。
5. ∴ ★案文 C は「置けば効き・置いても普段は無音」★ である。効くのは人が名を戻した其の時のみ。

## §4 ★今回も確かめられて居らぬ事★ (六条)

- ★`install.sh` の `sed -i 's/\r$//'` が現に作業樹を汚すか★: 隔離 repo では `scripts/` が追跡簿に無く (`git status --porcelain` = `?? scripts/`)
  ∴ ★変更として立たぬ★ = 測れて居らぬ。o87 §5-3 は ★埋まつて居らぬ★。埋めるには「追跡簿に載つた CRLF の file」を持つ場が要る。
- ★本物の repo で門が鳴るか★: 本物の hook は一指も触れて居らぬ ∴ ★隔離での再現であつて本番の實測では無い★。
  隔離と本物の違ひ = 本物には worktree が繋がり `SYNC_SCRIPT` も `DUP_CHECK` も在る。但し門は shebang 直後ゆゑ ★其れらの前に鳴る★ 形である。
- ★`core.hooksPath` を設定した場合★: 測つて居らぬ。本物の repo では ★未設定★ を o87 §3 で實測済だが、他 PC は測つて居らぬ。
- ★他 PC (main/second/mac) の hook★: 手が届かぬ ∴ 測つて居らぬ (o78 §5・o87 §6 と同じ)。

## §5 案文 C の最終形 (★案文であり、本物へは当てて居らぬ★)

挿す位置 = 退避 file の shebang (L1) の直後。隔離 repo で ★現に鳴る事を確かめた形★ が下記である。

```bash
# ── 戻し防止の門（案文・未適用）──────────────────────────────
# 此の版は 2026-09-07 の DB負荷止血より前の姿である（止血の門を持たぬ）。
# 名を pre-push へ戻すと push 毎に source_code_cache の同期と stale 検査が走る。
# 止血前の姿は git に残る: git show 4b1f7d293:scripts/git-hooks/pre-push
if [ "$(basename "$0")" = "pre-push" ]; then
  echo "[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。"
  echo "[pre-push]   正規の hook を戻すには: bash scripts/git-hooks/install.sh"
  exit 1
fi
```

- 門を挿した退避 file = 71 行・sha16 `26a7ad641d1a6534` (隔離での値)。
- ★当てれば blob `6d4039bb1671` との逐語同一は崩れる★ (o87 §2)。止血前の姿は git 側に残る ∴ 失ふ物は ★無い★ が、
  「disk の退避 file を blob と突き合はせて確かめる」道は ★使へなく成る★ ―― 之が当てる代償である。

## §6 境界と開示

走行 ★1 回★ (隔離 repo の構築と push 4 回を 1 本の規で行つた・elapsed 0.1 秒)。
★本物の hook は讀んだのみ = 書換 0・名を戻さず 0・移さず 0・消さず 0★。本物 repo で `install.sh` を走らせて居らぬ。
DB 讀 0・書 0・SQL 0 本・本物 CI 走行 0・本物 repo への push 0・fetch/pull/prune 0・network 0 (local path)。
共有樹 `.git` へ ★書込動詞 0★。D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触。Commander の箱 0 打。
★数の断り (四条③)★: 「push 4 回」は ★隔離 repo の bare origin へ★ の回数であり、本物の remote への push とは ★元素が別★ ∴ 足すな。
