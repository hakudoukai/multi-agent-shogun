# km-232 新束 ―― km-227b 束の 0byte 86本を ㋐現物／㋑器の疵／㋒採り漏れ へ切る（彫らず・測るのみ）

- 板: 6ac85357-750c-4281-95e3-cee7aaac58dc（km-232）／弾: queue/goals/ashigaru-mac-1.yaml（2026-09-25 07:27 発）
- 席: ashigaru-mac-1（專任1）／着手報 seq370513（karo-mac）
- 自席枝: ashigaru-mac-1/km-232-shinsoku-20260925（worktree /Users/momizimac/wt/a1-km232b）
- 親: b9573b2d376e9a0a372234b696a733677feb7919（origin/main・門 blob 04672e15 を持つ）
- 前束: commit 2ba9e671ca51848cd9fa1aa3f0c680ea16d23da1（2026-09-20・判は未見）。前束の欠けは
  ⑴條ごとの母數なし ⑵②の sha256 を「manifest参照」で空けた ⑶零の札が「母數・器・rc・刻」の形でない
  ⑷再走が main 版 absent の 2 場面のみ ⑸⑥が grep -v で濾した「空」 ⑹便で commit を 9桁で書いた。本束はこの6つを塞ぐ。
- 彫り 0（製品 code 不触）・push 0・前束／km-227b 束への書き込み 0。

## ① 対象 tuple

| 役 | ref | commit40 | tree40 |
|---|---|---|---|
| 測る物（km-227b 束） | ― (object で引く) | 6d8f28d53ff9bf055262350af370c7fdbf4aa4f6 | 9a451df69ad3f6d4f15ec050a1717d3e17c748e1 |
| 本束の親 | origin/main | b9573b2d376e9a0a372234b696a733677feb7919 | ― |
| 本束自身 | ashigaru-mac-1/km-232-shinsoku-20260925 | ★未確定（雛形 v1.3: 紙は己の commit を書けぬ）★ → `_hosoku/01_tuple.txt` と家老macへの便で宣す | 同左 |

測る物の path: `docs/evidence/ashigaru-mac-1_km-227b-fuzai-pane-goukan-ga-watcher-no-te-made-todoku-ka-20260920/`
（ls-tree 総数 239・うち size 0 が 86・86本悉く blob e69de29b＝git の空 blob ―― `bunrui/summary.txt`）

## ② 成果物（manifest の外の紙は `_hosoku/` に在る）

| path | sha256 | bytes | lines |
|---|---|---|---|
| bunrui/86hon.tsv（86本 1行1本・類と根） | f546ab8fb7cf69106237830f7c53a8743c1d21133da41103b938b34f766fa851 | 25005 | 87 |
| bunrui/summary.txt | d378e2774d7a7fb0b7177a2507ba6e10986aa5220bd6906b793a82e4d2e90c6e | 511 | 15 |
| bunrui/crosscheck.out（場面別 両向き） | 83c2810ec6677f6f8ebae42b26e94795e80a7f321a4cb6c7cb436d74a0198b57 | 1031 | 18 |
| raw/sizes.tsv（再走の全出目 209本の byte と sha256） | d8c57835df3e14485803f358b338efd59fceaa6b9f9a5e81d6b10411c840add3 | 22557 | 209 |
| raw/argv_all.txt（門 走1 の後に行末空白を剥いだ・直す前の値は _hosoku/11_before_fix.txt） | 61180e4f44c6b742629b6eea707b69f14291490235b06ae275b849b5640a4797 | 1686 | 14 |
| raw/sbx_inputs.sha256 | 309374cc315f2c98944e0581eefe7f7b1007666e897909f03299b1542b935fca | 1180 | 12 |
| harness/run_case.sh | 784967a25e74840e7174be4eff672216dc100a3aa0aecb8345220f55752f7177 | 1788 | 35 |
| harness/run_all.sh | e6539f600a2ce48c10886a73f9e7e0dc3d81216b24f18e87f6e1df679f96f3e3 | 3516 | 55 |
| harness/mutate.py | 08e2df50a453f3f443b6b306313c1d81c1f184779aacb38d633c1f79e12c9375 | 820 | 21 |
| harness/classify86.py | cf4fae91ca37de65b3f24bae64a0434650c54c38b8e885ad8702edfa9d67e325 | 3722 | 80 |
| harness/crosscheck.py | 95c181baefda42bcab2ddfc8cc96b33405f506165a40f0acbc4be381d1c48bdd | 1485 | 32 |
| （束に置かぬ）karo_carve.diff ＝ `git show 6d8f28d5:<測る物の path>/02_ver_diff/karo_carve.diff`（git blob 6c61d1ed4a35198faa3d3d9965c206dc1a9a0d66・走に使つた写しと byte 一致を實測） | 1746912b3ca99aba926466c0b509884c943a708228047ddb1a554909b8c83626 | 11870 | 206 |
| removed_empty.tsv | e5b8ae4adeb2f556e4daa1fd5da670829cd34b469d385bd881368eafcc482c74 | 867 | 16 |

全件の sha256 は MANIFEST.txt（器 karo_mac_manifest_append.py が建てる・手書き行 0）。
`git ls-files` が本束 path で 1本以上を返す事は commit 後に `_hosoku/` へ刷る。

## ③ 実走 raw（cwd・argv・rc・刻）

| 段 | cwd | argv の紙 | rc の紙 | rc | 刻 |
|---|---|---|---|---|---|
| 再走（10場面＋陽性4場面） | /Users/momizimac/wt/a1-km232b（driver は砂箱内 `cd <sbx>`） | raw/argv_all.txt（14行） | raw/run_all.rc／raw/driver_rc_all.txt（14行） | 0／悉く 0 | raw/run_all.started_at.txt 07:33:32 → ended_at 07:33:57 (+0900) |
| karo 版の組立（patch） | 同上 | harness/run_all.sh L19-22 | raw/patch_karo.rc | karo 0・karo_mut 0 | 同上 |
| 変異体の組立 | 同上 | harness/run_all.sh L23-26 | raw/mutate.rc／raw/mutate.out（置換 6回・各 count=1） | main 0・karo 0 | 同上 |
| 分類 | 同上 | bunrui/classify.argv.txt | bunrui/classify.rc | 0 | 07:34 台 |
| 両向き照合 | 同上 | harness/crosscheck.py の argv は本表の下 | bunrui/crosscheck.rc | 0 | 07:34 台 |
| 門の對照 | `<sbx>/pos`・`<sbx>/neg` | control/gate/{pos,neg}.argv.txt | control/gate/{pos,neg}.gate.rc | 1／0 | 07:35 台 |

照合の argv: `python3 -B harness/crosscheck.py /Users/momizimac/multi-agent-shogun 6d8f28d53ff9bf055262350af370c7fdbf4aa4f6 <測る物の path> raw/sizes.tsv`

砂箱 `~/a1_sbx_km232b.EAwo` は走後に消した（raw/sbx_path.txt: `sbx_removed_rc=0 exists_after=0`）。
砂箱へ置いた入力は★悉く測る物の commit object から★ `git show 6d8f28d5:<path>` で取つた:
scripts/inbox_watcher.sh・lib/agent_status.sh・lib/cli_adapter.sh・mock tmux 二種（05_mock_tmux）・karo 版 diff（02_ver_diff）。
karo 版の watcher sha256 は 6653228694efb537…（raw/sbx_inputs.sha256）で、板3859cda0 の親 5bae2d5d の watcher と同値（別の束で既に實測した値）。

## ④ 依存

/bin/bash 3.2.57・/opt/homebrew/bin/python3 3.14.6・git 2.55.0・patch 2.0-12u11-Apple・shasum。
mock tmux を PATH の先頭に置き、本物の tmux server には一度も触れて居らぬ（raw/out/*/env_check.txt の which_tmux＝砂箱の bin）。
lockfile なし。

## ⑤ 受入（弾の current_step の句ごと）

### 86本の三分類（母數 86）

| 類 | 数/母數 | 定義（classify86.py の判じ方） |
|---|---|---|
| ㋐現物（真に空） | **86/86** | 同じ版・同じ cli・同じ mock・同じ age で再走して 0byte、かつ原の同段 rc が在る、かつ同じ流れの陽性對照が >0 |
| ㋑器の疵 | **0/86** | 再走に同名 file が無い／原の同段 rc が欠ける／陽性對照でも 0（捕へる器が壊れて居る） |
| ㋒採り漏れ | **0/86** | 再走で >0（出る物が在るのに原が採らなかつた） |

basename 別: source.stdout 16・source.stderr 16・process_unread.stdout 16・agent_is_busy_direct.stdout 16・agent_is_busy_direct.stderr 16・flags/shogun_idle_testagent 6（計 86）。
flag は流れではなく touch で立つ旗ゆゑ、判じ方が別: claude 場面でのみ 0byte で在り、codex 場面では一件も立たぬ事で判じた。

### 両向き照合（bunrui/crosscheck.out・rc=0）

16場面（03_contaminated 6＋04_authoritative 10）悉く「原の 0byte 集合＝再走の 0byte 集合」。原のみ 0 も再走のみ 0 も 0件。
03 の 6場面は同じ条件の 04 場面の再走と照らした（03 は fingerprint 汚染の差のみで、流れを採る器は同じ）。

### 零の四札（㋑=0・㋒=0 の各に）

| 零 | 母數 | 器 | rc | 刻 |
|---|---|---|---|---|
| ㋑=0 | 86（ls-tree size 0） | harness/classify86.py（sha256 cf4fae91…）＋再走 raw/sizes.tsv | classify 0・run_all 0・driver 14/14 が 0 | 07:33:32〜07:33:57 再走・07:34 台 分類 |
| ㋒=0 | 86 | 同上 | 同上 | 同上 |
| 原のみ0／再走のみ0 = 0 | 16場面・原 0byte 86 | harness/crosscheck.py（sha256 95c181ba…） | 0（不一致なら 1 を返す器） | 07:34 台 |

### 陽性・陰性の對照

| 對照 | 何を確かめる | 結果 | 紙 |
|---|---|---|---|
| 陽性A（捕へる器） | 流れに字を書けば、同じ redirect が捕へるか | 変異体 4場面で 5種の流れが悉く >0（source.stdout/err 20・agent_is_busy_direct.stdout/err 20・process_unread.stdout 59/39） | raw/sizes.tsv の pos_* 行・raw/out/pos_* |
| 陰性A（再現） | 原版は同じ所を 0 にするか | 10場面で原と同じ 0byte 集合（上の両向き照合） | bunrui/crosscheck.out |
| 陽性B（分類器 ㋒） | 再走 1件を 5byte に偽れば ㋒ と出るか | ㋒=2/86（同条件の 03 と 04 の 2本・狙つた file のみ） | control/pos_uchimore.* |
| 陽性C（分類器 ㋑・流れ） | 陽性對照 1件を 0 に偽れば ㋑ と出るか | ㋑=6/86（main codex 6場面の process_unread.stdout のみ） | control/pos_utsuwa.* |
| 陽性D（分類器 ㋑・旗） | codex 場面に旗を偽れば ㋑ と出るか | ㋑=4/86（main claude の旗 4本のみ） | control/pos_flag.* |
| 陰性B（分類器） | 同じ入力で再び走らせ同じ表を出すか | cmp rc=0（bunrui/86hon.tsv と byte 一致） | control/neg_same.* |
| 門 陽性／陰性 | 門が 0byte を撥ね、非空を通すか | rc=1／rc=0（門 blob 04672e15） | control/gate/* |

process_unread.stdout の 59/39 は、process_unread の中で agent_is_busy が呼ばれ、其の probe も同じ stdout へ流れた為（raw/out/pos_main_claude_absent/process_unread.stdout で 3行・codex で 2行を實見）。

### 條ごとの母數

條①（臺帳の path 行）と 條②③（門へ渡した file 数）は、★本紙を含む臺帳の数ゆゑ本紙には書けぬ★。
臺帳を建てて門を通した後、`_hosoku/02_bogen.txt` に器の出力のまま刷る（臺帳の外）。

### 再走の 0byte 83本の内訳（raw/not_copied_empty.txt）

原版10場面の 0byte 53（＝86本のうち 04 の 10場面の分・crosscheck.out の 04 行の和）＋陽性 claude 2場面の旗 2＋driver の stdout/stderr 14場面×2＝28。計 83。
0byte は門の條④に掛かるゆゑ束へ写して居らぬ。在つた事と大きさは raw/sizes.tsv（0byte も含む 209本）が證す。

## ⑥ 復元

- 着手時: worktree 作成直後の `git status --porcelain -uall --ignored` は 0行（画面で實見・紙へは刷らず ―― 宣）。
- 本束の器が 0byte で吐いた 15本は束の外（~/a1_letters/km232b_discard/empty/）へ退けた。名・rc・刻は removed_empty.tsv。
- 一度目の再走（main 版 absent の 4場面のみ）は 10場面版に置き換へた。二度目は `$5: unbound variable` で落ちた（rc=1）ゆゑ、其の raw と砂箱は束の外（~/a1_letters/km232b_discard/）へ退けて三度目を採つた。採つた三度目の値のみが本束に在る。
- 門 走1 は rc=1 で落ちた（因三つ: 基点を束の path で渡した／karo_carve.diff の空 context 行 7／argv_all.txt の行末空白 10 ―― age 無し場面の `${5:-}` が空で末尾に空白を一字残した）。
  直し: 基点を `.` に／diff は束から退けて（測る物の object に同じ blob が在る）再走の手順を下に書いた／argv_all.txt は正規化の約束事（2026-09-07）の pipeline で剥いだ。
  走1 の出目は _hosoku/10_gate_run1.*、直す前の値は _hosoku/11_before_fix.txt。
- 再走の手順: 束の harness/ へ `git show 6d8f28d53ff9bf055262350af370c7fdbf4aa4f6:docs/evidence/ashigaru-mac-1_km-227b-fuzai-pane-goukan-ga-watcher-no-te-made-todoku-ka-20260920/02_ver_diff/karo_carve.diff > harness/karo_carve.diff` で置いてから `bash harness/run_all.sh <束の絶対path> <repo>`（raw/ を空にして）。
- commit 後の porcelain（空である事）と `git ls-files` の数は `_hosoku/03_after_commit.txt` に刷る。

## ⑦ 法令

該当なし（課金・法定様式に関はらぬ内部の測り）。

## 宣

1. 本束は km-227b 束にも前束 2ba9e671 にも一字も書いて居らぬ。前束の値は使はず、測る物を commit object から測り直した。
2. 再走の場面は 04 の 10場面と同じ条件（版・cli・mock・age）で、03 の 6場面には別の再走を当てて居らぬ（上の両向き照合の註）。
3. E2E（本物の pane への配送）は本席の範囲外。
