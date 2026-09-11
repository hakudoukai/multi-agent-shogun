# order278 ―― 令271 拡張 patch の当たり直し（★当てては居らぬ★）

## §的 ★的一行★
令271 の拡張 patch は 鋳つた時と同じ形で ★今も当たる★ ―― 的 甲 `~/bin/cdrive_autoguard.sh` の sha16 は基線 `d175e32a71aec0a8` と ★一字も違はず一致★ し、`git -C / apply --check -p1 --unsafe-paths` は ★rc=0★ を返した。而して 乙 の的 manifest は ★基線 sha を令271 の紙に記して居らぬ★ ∴ 乙の「鋳つた時から変はつたか」は ★測定不能★ であり、rc=0 は「今の乙にも当たる」を言ふのみである。
## §A 頭
| 項 | 値 |
|---|---|
| as_of ／ 令 | 2026-09-10T18:39:50+0900 ／ `scratch/k3_orders/order278_a3.txt`（7 行 / 1,723 B / sha16 `53bd779c51d6c981`） |
| 何を幾つ讀んだか | 令の紙 1・令271 の紙 1（234 行）・patch 1（86 行）・的 file 2（甲 乙）＝ ★計 5 物★ |
| HEAD ／ 樹 | `1ad4edf`（不動）／ 此 repo ＝ `/home/hakudoukai/multi-agent-shogun`（作業樹・LF）。★甲 乙 は repo の外の樹に在り git blob に非ず★（床⑵） |
| 走 ／ 焚 | 走 ＝ `apply --check` ★1★（上限 1・使ひ切り）／ 焚 ＝ ★0★。的の頭を取る wc/sha256sum は走に数へぬ（令264 ■〇-2 の裁）― ★之は己の解であり家老の裁を仰ぐ★ |

## §B 基線と今の比較（樹を併記・條 五百三）
| 的 | 樹の根 | 令271 の紙が記す基線 | 今の実測 | 別 |
|---|---|---|---|---|
| 甲 `home/hakudoukai/bin/cdrive_autoguard.sh` | `/`（WSL 作業樹・git 管理外） | 124 wc / 6,466 B / `d175e32a71aec0a8`（紙 L52） | 124 wc / 125 片 / 6,466 B / `d175e32a71aec0a8`・mtime Aug 13 08:10 | ★一致★ |
| 乙 `mnt/c/DentalBI/docs/rules/fleet-composition-manifest.yaml` | `/`（/mnt/c 作業樹・git 管理外） | ★sha を記して居らぬ★（紙 L31 は「manifest L528-534 を讀んだ」とのみ） | 2,492 wc / 2,493 片 / 363,080 B / `36d70d34f4274231` | ★測定不能★ |
| patch 本体 | 此 repo（作業樹・LF） | 5,143 B / `85f010d0cf9538e0`（紙 L102） | 86 wc / 87 片 / 5,143 B / `85f010d0cf9538e0` | ★一致★ |
- `--numstat` は ★打つて居らぬ★ ―― 甲は sha 一致ゆゑ行域の差は 0・乙は比べる相手が紙に現に無い。且つ ★甲乙とも git 管理外ゆゑ numstat の的に成らぬ★（床⑵）。

## §C `apply --check` の rc と raw
| 項 | 値 |
|---|---|
| argv | `git -C / apply --check -p1 --unsafe-paths <patch の絶対 path>` ―― 根 `/`・剥がし `-p1`（條 四百九十三） |
| rc ／ 吐いた物 | ★rc=0★ ／ stdout 0 B・stderr 0 B（何も吐かず） |
| raw | `scratch/ashigaru-third-3-12e9d4bd/order278_raw_v1.txt`（12 wc / 13 片 / 341 B / sha16 `a11e56f63cc5e0e9`）＝ argv と rc を逐語で収めた |
| hunk | 2 本 ―― 甲 `@@ -26,4 +26,67 @@`（+63 行）／ 乙 `@@ -530,3 +530,11 @@`（+8 行）。rc=0 は ★2 本とも当たる★ の意 |
- ★当たらぬ時の手（本弾では起きて居らぬ）★ ＝ 割れた行番を stderr の逐語で写し、★patch は直さず・v2 patch も鋳らず★ 家老へ上げる（令 ■二③）。

## §D GO 後の手順（★席の見込み・一手も打つて居らぬ★）
| 順 | 手 | 何を見れば「成つた」と言へるか |
|---|---|---|
| ① | 再度 `apply --check` を 1 走（GO の刻の的で取り直す） | rc が 0 で在る事。0 でなければ ★当てずに家老へ上げる★ |
| ② | `git -C / apply -p1 --unsafe-paths <patch>`（★当てる★・GO の後のみ） | rc が 0 で在る事 |
| ③ | 甲の当たりを検む | 甲の wc が 124 → ★187★（+63）に成る事・`gauge_daily` の定義行が 1 本現に在る事 |
| ④ | 乙の当たりを検む | 乙の wc が 2,492 → ★2,500★（+8）に成る事・鍵 `cdrive_gauge_daily_tsv_20260910` が 1 本現に在る事 |
| ⑤ | 器を手で 1 回走らせ TSV の一行を見る | TSV が一行 増える事・kind 列が `d_wsl` か `none` の何れかで在る事（★`none` は「二本の網の何れにも当たらず」の意であり「vhdx が現に無い」の意ではない★＝條 百七十七） |
| ⑥ | enable ／ start ／ daemon-reload | ★席は打たぬ（0）★ ―― timer は既設 `dentalbi-cdrive-autoguard.timer`（3600s）に相乗り ∴ 新 timer 0。live 操作と REBOOT_PROOF の実視は ★総監督の手★（令271 紙 L137） |

## §E 実測と見込みの別・完全 SHA256
- ★実測★ ＝ 甲乙 patch の wc/片/B/sha16（本弾で当たつた）／`apply --check` の rc=0（走 1・raw に argv と rc を残した）／甲と patch は基線と一致。
- ★見込み★ ＝ §D の ①〜⑥ は ★未だ一手も打つて居らぬ★ 案である。③④の +63 / +8 は patch の hunk 頭から引いた算であり ★当てて数へた数ではない★。新條は令に無きゆゑ ★足さぬ★。
- ★rc=0 が意味せぬ事★ ＝ ⑴「当てた」を意味せぬ（`--check` は当てぬ）⑵「器が動く」を意味せぬ（走らせて居らぬ）⑶「乙が鋳つた時と同じ物である」を意味せぬ（乙の基線 sha は紙に現に無い＝測定不能）。
- 完全 SHA256 ⑴ raw `a11e56f63cc5e0e96ff4feff289cfd4667e59570a5c7eb7780d75b61ca321529` ⑵ patch `85f010d0cf9538e094d3a556084c37e1d09bc25dcc4c422d9bc1dce90050d40d`
- 完全 SHA256 ⑶ 甲 `d175e32a71aec0a8f2f4f4f7ed32173dd38ee8f8c5080a5021ccc0bb2706cb92` ⑷ 乙 `36d70d34f4274231ef157af9b9207c63d9fd6e7d98e10e4a2507b88d5d1617b4`
