# ⑶ switch_cli.sh を ★引数を与へて★ 測つた（裁337393⑶「未測を残すな」）

## 測つた五路（raw = 50_switch_cli_jissoku.txt）

| 路 | argv | rc | 出目 |
|---|---|---|---|
| ㋐ | （引数無し） | 1 | usage 7 行（stdout） |
| ㋑ | `ashigaru-mac-99` | 1 | WARN(動的検索不発)→`ERROR: Unknown agent_id`（stderr 2 行） |
| ㋒ | `ashigaru-mac-3 --type nonesuch` | 1 | `ERROR: Invalid CLI type`（stderr 1 行） |
| ㋓ | `ashigaru-mac-3 --type`（値無し） | 1 | **`line 340: $2: unbound variable`**（stderr 1 行） |
| ㋔ | `ashigaru-mac-3 --nonesuch` | 1 | `Unknown option` + usage |

**★甲の直しの効き★**: 五路の何れにも `declare: -A: invalid option` は出て居らぬ。
（本器は `lib/_section18_roles.sh` を source する。甲を直す前は此処で鳴つて居た。）

## ★疵 その一★ ―― ㋓ は「拒絶」ではなく ★set -u の生の死★

L339-341 逐語:
```sh
        --type)
            NEW_TYPE="$2"
```
`--type` に値が無い時、usage を出して閉ぢるのではなく `$2: unbound variable` で落ちる。
rc=1 は **偶然 usage と同値**であり、受け手は「使ひ方の誤り」と「器の死」を区別できぬ。
`--model` も同型（L342-344）。**★直しは別弾（本弾では叫ばせた儘 上げる）★**。

## ★疵 その二（重い）★ ―― `-t multiagent` の前方一致が ★当機の生きた席★ を掴む

裁337394 が「canon 第26実例の ★session 版★」と名付けた形の、**pane_identity に続く三つ目の実物**。

読取のみで測つた（51_）:
```
tmux list-panes -t multiagent:agents    → multiagent-mac:0.0 %68 / 0.1 %72 / 0.2 %7 / 0.3 %125
tmux list-panes -t =multiagent:agents   → can't find session: multiagent
```
∴ **MainPC の session は当機に無く**、`multiagent` は **`multiagent-mac` へ前方一致する**。

本器の pane 解決は、動的検索（`@agent_id` 突合）が外れると **固定写像**へ落ちる（L102-108 逐語）:
```sh
    if mainpc_idx=$(section18_mainpc_pane_index "$agent_id" 2>/dev/null); then
        echo "multiagent:agents.$((pane_base + mainpc_idx))"
```
`@agent_id` の実体は `karo-mac / ashigaru-mac-1 / -2 / -3` のみ（51_ ㋕）ゆゑ、**旧名を渡すと必ず固定写像へ落ちる**。
∴ 当機で `bash scripts/switch_cli.sh ashigaru1 --type codex` を打つと
`multiagent:agents.1` → 前方一致 → **`%72`（★專任1 の生きた pane★）** へ
`C-c` / `/exit` / `Enter` / 新 CLI 起動の `send-keys` が **悉く着弾する**（L239-262・L406-408）。

**★本器自身の註が、正に此の事故を防ぐ為に書かれて居る★**（L84-90 逐語）:
「動的検索失敗時に send-keys で送信先を誤ると … 別 agent に届く事故になる」。
**其の守りが、session 名の前方一致で ★破られて居る★。**

## ★未測の宣★ ―― 変異路は測らぬ（理由）

`--type` を正しく与へて実際に切替へる路は **測らぬ**。理由は三つ、何れも規律である:
1. 本器は `tmux send-keys` と `Enter` を席の pane へ押す。**家老は押鍵を禁じられて居る**（nudge の Enter が承認ダイアログを押し得る）。
2. 掴む先は **走つて居る席**（%72 專任1 / %125 專任3）であり、`C-c` と `/exit` は **其の場の仕事を殺す**。
3. 変更統制 ―― 席の CLI・model の変更は環境の変更である。

∴ 本弾の ⑶ は **「引数検めの五路は実測（悉く rc=1）／変異路は ★未測（理由=押鍵禁・稼働席の破壊・変更統制）★」** と宣して閉ぢる。
**測れる所は悉く測つた。測らぬ所は理由と共に名指した。**

## 請裁（本弾では直さず上げる）

㋐ 疵その一（`$2` unbound）を usage へ倒す直しを当てて良いか。
㋑ 疵その二（前方一致）は **`-t` を `=multiagent:agents` か pane_id へ改める**のが筋だが、
   其れは **「当機に MainPC の session は無い」ゆゑ即 fail** となり、**Mac で本器は使へぬ**と明示する形になる。
   之が正しい姿と判ずるが、器の意味が変はる故 ★裁を請ふ★。
