# o136 型（八項）― order134 母の減り方 as_of 2026-09-09 05:05 JST

## ① host 付き絶対 path
- host=momizi-dx user=hakudoukai cwd=/home/hakudoukai/multi-agent-shogun
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_shrink_probe.py（200 行）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_run1_20260909_045557.txt（17 行）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_run2_20260909_045711.txt（25 行）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_run3_20260909_050311.txt（29 行・★rc=3 ABORT★）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_run4_20260909_050531.txt（32 行）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o136_shrink_20260909_050516.txt（346 行・名の一覧）
- /home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/after_delete_5668_gap_1483_readonly_v1.md（2751 行・§39）

## ② sha256（64 桁・digest の種を書く）
- 98aad2f39963bdf017c4df162eacabe9e71de54cbf2e16e940fdbe47a87324f0  o136_shrink_probe.py
- 2186f06e68f53ce944654e72e3f80d642ce9bb81ee520e486128332835c74a14  o136_run1_20260909_045557.txt
- 8e2e8062dba70ac2eabeb5b216112d001b9ef80c6cbfc190ba81a516300c63fe  o136_run2_20260909_045711.txt
- a654f06de16d742e0c6efa0a128644944548928e6f510441abd16c2deecc1db3  o136_run3_20260909_050311.txt
- c41f1d5cbf8fb48199b4565d3bfa44705c74678e0d53b27dd6718f546160c146  o136_run4_20260909_050531.txt
- 099567ea47bf180942fa325f28e175d62c4fe9a532ca4f34698de3460dc669b7  o136_shrink_20260909_050516.txt
- 822b0f0099add01e73dcdc84c34da8ae87493801cf3c9e108beafdbe5b8c34bb  after_delete_5668_gap_1483_readonly_v1.md

## ③ argv 逐語 と 走が四本に成つた因
- 悉く `/usr/bin/python3 scratch/ashigaru-third-2-fa06a3a1/o136_shrink_probe.py`
- 走 1 rc=0（04:55:57）＝三つ止まりの初出。
- 走 2 rc=0（04:57:11）★因＝範を狭める二手（o116 の packed 順・帳の親 dir mtime）を足した★。申告 msg_20260909_045644_8fb5dd12 → 許諾 msg_20260909_045708_4f9a7210。
- 走 3 rc=★3★（05:03:11）★因＝手 2 の前提を検める対照③ を足した★。申告 msg_20260909_050227_f1d558b9 → 許諾 msg_20260909_050306_a0ea0757。★陽性 立たず ∴ 数を出さず ABORT★。
- 走 4 rc=0（05:05:31）★因＝走 3 の陽性が立たなんだのは ★己の対照設計★（makedirs 直後と足した直後が同一 tick）∴ 各段に 1.1 秒措き m0/m1/m2 を刷る★。申告 msg_20260909_050440_a9784538 → 許諾 msg_20260909_050512_4dc10033。

## ④ 令の問と 答
- 問「①幾つ減つた」⇒ 答: 帳(logs)が無い ★2 本★ ／ ref(loose|packed)が無い ★2 本★ ／ 両方無い 2 本（母 345）。名＝`refs/remotes/origin/pr-71-review` ／ `refs/remotes/origin/pr69`。
- 問「②どの層（空/保つ/別刻）から」⇒ 答: ★「保つ」から 2★・空 0・別刻 0。何処からは両方 `refs/remotes/origin`。
- 問「③何時より後か」⇒ 答: 範 ★2026-09-08 12:49:39 〜 2026-09-09 05:05:29（幅 16.26 時間）★。狭めて ref は ≤ ★21:04:05★（packed-refs の最後の書き）・帳は ≤ ★19:20:00★（親 dir の最後の書き）⇒ 帳は ★12:49:39〜19:20:00（幅 6.5h）★。
- 問「★三つ止まり★」⇒ 答: 其れ以上は出して居らぬ（点・下手人・回数は ⑨ に「言はぬ」と明記）。
- 「帳」と「ref」は ★別語★ として両方 別々に数へた（令の通り）。

## ⑤ rc
- 走 1 rc=0 ／ 走 2 rc=0 ／ ★走 3 rc=3（対照③ 陽性 立たず ∴ 数を出さぬ門が働いた）★ ／ 走 4 rc=0

## ⑥ 座
- host=momizi-dx user=hakudoukai cwd=/home/hakudoukai/multi-agent-shogun ／ 席=ashigaru-third-2 ／ 上官=karo-third
- ★讀取のみ★=/mnt/c/DentalBI/.git は python の file 讀のみ・git を一度も実行せぬ・書込は scratch のみ・★消す動詞 0★。

## ⑦ 対照
| 対照 | 中身 | 望み | 実測 | 判 |
|---|---|---|---|---|
| 陽性①（ref 在り） | home 樹の実在 20 本 | 20 本とも ref 在り | 20 | ★立つ★ |
| 陰性①（ref 無し） | 贋の名 `refs/heads/zzz-o136-nonexistent-NN` 20 本 | 20 本とも ref 無し | 20 | ★立つ★ |
| 陽性②（走 3） | 贋 dir に entry を足す | dir mtime 動く | ★動かず★（同一 tick） | ★立たず→ABORT★ |
| 陽性②（走 4） | 同上・1.1 秒措く | dir mtime 動く | 差 104,353,382,267 ns | ★立つ★ |
| 陰性②（走 4） | 中身だけ書換 | dir mtime 動かず | 差 0 ns | ★立つ★ |

## ⑧ 母を足さぬ（別の母を混ぜぬ）
- 母＝o112 の一覧 ★345 本★（保つ 88 ／ 別刻 145 ／ 空 112）。o116/o135 の ★帯 200／198★ とは ★別の母★ ∴ 足し比べるな。
- 母 345 自体が 09-08 の測り ∴ ★其れ以前に減つた本は此の母に入らぬ★。

## ⑨ 此の数が言はぬ事
1. ★点★（何秒に消えたか）―― 出ぬ。出したのは ★範★ のみ。狭めた範を 点と誤るな（両刻は「最後の書き」）。
2. ★誰が消したか★ ―― 出ぬ。当席は下手人を測らず。
3. ★一度に消えたか 二度に分けてか★ ―― 出ぬ。
4. 対照② を鳴らしたのは ★ext4（己の scratch）★・測つた樹は ★drvfs★ ⇒ ★測つた樹では鳴らして居らぬ★。
5. 対照② で鳴らしたのは ★足す★ であり ★消す★ ではない ―― ★同じ事象ではない★。
6. 当ての検め＝★半ば★（偏り origin は当たり・「2 本では止まらぬ」は ★外れた★）。
