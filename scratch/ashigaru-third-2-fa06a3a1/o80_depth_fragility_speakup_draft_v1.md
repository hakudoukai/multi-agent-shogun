# order80 案文: fetch-depth の脆さに ★声を上げさせる★ 二案 (書換 0・GO 未請)

as_of 2026-09-08T06:0x JST / 席 ashigaru-third-2 / 令 order80 (msg_20260908_055903_49873aa0)
前紙 o79 `3f1f8c2f45e55e1f` (64 行) を土台とし 書換へず。本紙は ★案文であり 実装は 1 行も行つて居らぬ★。
底本 v3 = origin/main 抽出 766 行 `16e2db65f8cb48fa` / 底本 CI = blob `3d2dbae7ae84` (63 行)

## §0 何を直すのか (静かな失敗の形)
o79 §5 の實測: `fetch-depth` を 1 へ縮めると `HEAD^1` が shallow の外へ出て
`git diff HEAD^1 HEAD` が rc≠0 → v3:573 の門を通らず `:576 return set()` → ★0 本★。
而して v3 は ★何も言はず★ 0 本を返し、job は正常に終る。外からは「変更が無かつた」と見分けが付かぬ。
∴ ★之は静かな失敗である★ (no-silent-failure の条に触れる形)。

## §1 判別式 ―― 「shallow ゆゑの 0 本」と「root commit の正当な 0 本」を分ける
`HEAD^1` が解けぬ因は 二つ在り、混ぜて止めると root commit の repo を巻き込む。
★判別式★: `HEAD^1` が解けぬ ★且つ★ `git cat-file -p HEAD` の本文に `parent ` 行が在る → ★shallow が因★。
(shallow は親の ★指し★ を commit 本文に残したまま ★物★ だけを持たぬ ∴ 之で分かれる)

實測 (規 o80_shallow_vs_root_probe.py 56 行・走 3 回目):
| 形 | shallow file | HEAD^1 rc | 本文に parent 行 | 判別式 = 声を上げる |
|---|---|---|---|---|
| 甲 tip depth1 (shallow ゆゑ HEAD^1 無し) | True | 1 | True | ★True★ |
| 乙 tip depth2 (正常形) | True | 0 | True | False |
| 丙 root commit depth1 | True | 1 | False | False |
| 丁 root commit depth2 | False | 1 | False | False |
∴ ★声が上がるのは 甲 のみ★。正常形も root も黙る。

## §2 両論併記 ―― 何処へ声を置くか
### 甲案: ★器側 (v3 `changed_paths_from_git` の中)★
- 形: `:573 if first_parent.returncode == 0:` の ★else 側★ に §1 の判別式を置き、shallow が因と判れば声を上げる。
- 利: 器を呼ぶ ★全ての口★ で同じ声が出る (o78 で数へた口 = CI 1・hook 1(条件付)・手打ち 4 箇所)。CI だけを守るのではない。
- 利: 直しが効いて居る限り ★決して起きぬ★ (§1 乙) ∴ 平時の費用は 0。
- 害: 器 1 本に条件が増える。試験を 1 本足さねば据わらぬ。
### 乙案: ★CI 側 (yml の checkout 直後に番人 step)★
- 形: `git rev-parse --verify -q HEAD^1` を検め、解けねば step を落とす (`:35 fetch-depth` の番人)。
- 利: 器を触らぬ。yml 1 本で済み、戻すも 1 本。
- 害: ★CI しか守らぬ★。hook (`SYNC_SOURCE_CACHE_FORCE=1` の時) と手打ち 4 箇所は素通り。
- 害: 判別式を持たぬ素の検めは root commit を巻き込む (§1 丙丁)。

## §3 選ぶ ―― ★甲案 (器側) × 止まる★
理由 ★一語★: ★赤は人を呼ぶ★。
- 「警告のみ」を採らぬ因: 警告は CI log の中に沈む。o79 が示した通り ★0 本は正常終了と同じ顔で通る★ ∴ 声を上げても誰も讀まねば 静かな失敗のままである。
- 「止まる」の代償が小さい因: CI は push の ★後★ に走る ∴ 止めても push は既に済んで居り、開発の手は止まらぬ。落ちるのは同期の job のみ。
- hook から呼ばれた時は `pre-push:64` が `if ... ; then / else` で受け ★表示のみで push を続ける★ (`:70 exit 0`) ∴ 器で非 0 を返しても push を塞がぬ。
- 平時に鳴らぬ事は §1 乙 で實測済 ∴ ★狼少年にならぬ★。

## §4 陰性対照の作り方 (案を当てる時に併せて据ゑる形)
o79 走 2 の型を其の儘用ゐる。作り物 repo を席の scratch 内に建て、bare も同 dir 内に置く (本物 remote へ 0)。
- ★陽性対照 (声が上がるべき)★: tip × `fetch-depth=1` → 声 1・返す本数 0
- ★陰性対照 (黙るべき) 三つ★: ⑴tip × depth2 → 声 0・返す本数 2 ⑵root × depth1 → 声 0 ⑶root × depth2 → 声 0
- ★据ゑ置く陽性★: merge/squash × depth2 × 直し在り → 2 本 (o79 §4 の値を動かさぬ事を確かめる)
- 判じ方: 声 = stderr に印字した符号の在否で数へる (o79 で `CHANGED_ONLY_FIRST_PARENT` を数へたのと同じ形)。

## §5 境界・確かめて居らぬ
★本紙は案文であり 製品 file の書換 0★・DB 讀 0 書 0・SQL 0・push 0 (作り物 bare へ 1 回のみ)・本物 CI 走行 0・fetch/pull/prune 0・Commander の箱 0 打。走 = ★3 回★ (上限 5)。
★確かめて居らぬ★: shallow の commit 本文に `parent ` 行が残る事は 当席の作り物での實測であり、本物の GitHub runner での fetch でも同じかは 現物を讀んで居らぬ。
★確かめて居らぬ★: 甲案を当てた時に他の呼手 (hook・手打ち 4 箇所) が現に何を表示するかは 走らせて居らぬ。
★GO は請うて居らぬ★ (家老が請ふ旨 令に在り)。
