# 候補 1,649 の内「其外 900」の由来 三分 と 逆向き 44
as_of 2026-09-07T18:57:56+09:00 / 前紙 option_c_execution_packet_v1.md **sha16 ee9e19ec2a63b4dd**(70 行・着手時に再測し一致)・order50 紙 306816953dc056f5
用ゐた材: order61 の csv/json(局所)と ★git 讀取動詞のみ★。DB 讀取 0・DB 書込 0・fetch 0・走行 0・DDL 0。數へ方: 1 = path 1 本。

## 冒頭 ―― order50 ㋩ の併記訂正
- ★元の文(取消さず併記)★: order50 は ㋩「CI #2 が v3 の外を書く」を ★現に無い★(CI 集合 3,301 ⊂ v3 集合 4,185・CI only = 0)と測つた。
- ★本測(order61 S3)★: 候補 1,649 の内 ★317 本が CI #2 の集合に当たる★(其の内「其外 900」に属する分 147)。
- 何が違ふか: order50 は ★其の時の作業樹★ の追跡簿同士を比べた。本測は ★表に現に在る行★ を CI の pattern に当てた ―― 母集合が違ふ ∴ 二つは矛盾せぬが、★「CI は v3 の外を書かぬ」と読むには足りぬ★。CI が現に走つて居るかは測つて居らぬ。

## §1 「其外 900」の三分 (和 = 900)

| 分 | 定義 | 件数 | 頭 dir (件数のみ) |
|---|---|---|---|
| ㋥ | 履歴の rename の ★旧側★ に在る (`-M --diff-filter=R`・記録 170・旧 168/新 168) | **9** | tools 5・setup 3・scripts 1 |
| ㋭ | ★履歴に一度も現れぬ★ (全 249 ref の全 commit の name 集合 20,305 に無い) | **335** | backend 77・frontend 74・docs 61・`hakudokai-shogun-r1` 45・頭が空 27・queue 9・scripts 9・`shinshoku-gosai` 9 |
| ㋬ | 履歴には現れるが rename 旧側でなく、ref の tip にも現 main にも無い | **556** | `.agents` 150・docs 136・backend 72・frontend 68・outputs 25・`mockup_v26_left_files` 22・tools 6・tests 6 |

- ★path 正規化の差は 現に無い★: ㋭ 335 の内 大小違ひで履歴に在る **0**・NFC/NFD 違ひで履歴に在る **0**。900 全体で逆斜線 `\` を含む **0**。
- ★頭が空 27★ = 先頭が `/` の絶対 path 様。git の追跡簿は相対 path のみゆゑ ★履歴側に相手が無いのは道理★。書いた器は測つて居らぬ。
- ㋬ が ㋺(order61 の 24)に入らなかつた理由は ★測つて居らぬ★。㋺ は現行 INCLUDE regex を通した `--diff-filter=D` の集合(母数 402)ゆゑ、pattern が当時と違へば落ちる ―― 之は ★道理の説明であり測定ではない★。

## §2 逆向き 44 (S2 集合に在り表に無い = 未同期)

- 頭 dir: frontend **27**・backend **17** (和 44)。拡張子: `.py` 17・`.tsx` 17・`.ts` 10。
- 中身: `cat-file --batch` で 44 本すべて size > 0・strip 後も空でない **0 本が空** ∴ ★L592-595 の SKIP(empty) には当たらぬ★。
- main へ追加された日: **2026-09-06 が 38 本・2026-09-07 が 6 本**(`log --diff-filter=A -1 --format=%cs`)。∴ ★悉く直近 2 日の新入り★。

v3 定常走で入るか (三値・blob `0754d928…` の行番号):

| 走り方 | 判定 | 行番号と理由 |
|---|---|---|
| 全同期 (引数無し) | ★入る★ | L550 `sync_files = collect_files(repo_root)` → L577 の輪 → L603-610 で batch へ → L612/L620 `upsert_with_isolation` → L200-214 `upsert_batch`(L209 `on_conflict=file_path`)。落とす関門は L579(不在)・L592(空)のみで、44 は何れにも当たらぬ |
| `--changed-only` | ★入らぬ★(条件付) | L533-547: `git diff --name-only origin/main...HEAD` の集合と積を取る (L547) ∴ ★HEAD が origin/main と同じなら空★。44 は既に origin/main に在るゆゑ差分に現れぬ |
| 現に走るか | ★測定不能★ | pre-push hook は L54-61 の止血で既定 `exit 0`(order60 で実見)・かつ hook は L64 で `--changed-only` を渡す。CI #2 が現に走るかは測つて居らぬ |

## §3 用ゐた command (悉く讀取・timeout 付き)
`git -C /mnt/c/DentalBI log --all --name-only --format= -z`(20,305 名)／`… log --all -M --diff-filter=R --name-status -z --format=`(記録 170)／`… cat-file --batch-check=%(objectsize)` と `… cat-file --batch`(44 本)／`… log --diff-filter=A -1 --format=%cs <sha> -- <path>`(44 回)／`… cat-file -p 0754d928…`(行番号の讀み)。

## 境界
- 三分は ★局所 249 ref の履歴★ に対する物。遠隔にのみ在る枝(order59 の 17 本)は含まぬ ∴ ㋭「履歴に一度も無い」は ★上限★ である(fetch すれば減り得る)。
- ㋥ の rename 検出は `-M`(既定の相似度)に依る ∴ ★閾値次第で増減する★。`-M50%` 等を変へた測りはして居らぬ。
- 「其外 900」の書いた器は測つて居らぬ ―― ㋭ の 335 も ㋬ の 556 も、誰が/いつ表へ入れたかは表の `commit_hash`/`updated_at` を讀まねば分らぬ (本 order は DB 讀取 0)。
- 44 が「入る」と書いたのは ★符號を辿つた結果★ であり、走らせて確かめては居らぬ (走行 0)。
- DELETE の打手は総監督殿。当席は打たぬ。推す語は書かぬ。
