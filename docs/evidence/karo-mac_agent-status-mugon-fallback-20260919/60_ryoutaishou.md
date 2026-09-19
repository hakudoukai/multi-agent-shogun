# 両対照 ―― 裁337393 ⑴⑵⑶（家老mac）

刻 = 00_koku.txt ／ 器 = /bin/bash = GNU bash 3.2.57(1)-release arm64-apple-darwin25

## ⑴ `scripts/agent_status.sh` ―― 「意味が変はる fallback を無言で行ふな」

疵の逐語（原本 L222）: `task = data.get('task', data)`

**★両対照が当方の見込みを撃ち落した★**。当方は「頂に task 鍵が無ければ `task_id` が外れて
`--- ---`（弾無）を刷る」と見込んで居た。**実測は違ふ。**帳の頂には旧形の欄
（`task_id` / `status` / `priority` / `assigned_at`）が居坐つて居り、fallback は
**★其の古い一組を「今の弾」として刷つて居た★**。症は「読めぬ」ではなく **★尤もらしい偽値★**。

| 席 | 古い弾が刷つた物 | 実体（弾鍵を歩いた数） | 今の弾 |
|---|---|---|---|
| ashigaru-mac-1 | `km-116-…-20260917` / **done** | 弾鍵 89本・assigned **0**本 | `(multi:0/89) !` |
| ashigaru-mac-2 | `km-117-…-20260917` / **done** | 弾鍵 25本・assigned **3**本 | `(multi:3/25) !` |
| ashigaru-mac-3 | `km-113-…-20260917` / **done** | 弾鍵 29本・assigned **2**本 | `(multi:2/29) !` |
| ashigaru-mac-4 | `km-a4-mimi-…` / done | `task:` 鍵有（甲の形）ゆゑ路は変はらず | 同じ（変化無） |
| ashigaru-mac-7 | `km-P1-pr69-akashi4-kizoku` / assigned | 弾鍵 3本・assigned 2本 | `(multi:2/3) !` |
| gunshi-mac | `subtask_mac_gakushu_runtime_rebuild_001` / assigned | 弾鍵 0本（頂の鍵 47本） | `(multi:0/0) !` |

**★実害★**: 席2は「done・弾無し」と刷られて居たが、其の時 **assigned が 3 本走つて居た**。席3も同じ（2 本）。
**∴ 之は表示の綾ではなく、差配の判断を誤らせる偽値である。**

- 何れの弾を「今の弾」と選ぶかは **★政策★** ゆゑ器が選んではならぬ。器は **測つた数（assigned/弾鍵）** を出し、
  頂の旧形 `task_id`/`status` を **stderr へ逐語で吐いて「用ゐぬ」と宣する**。
- 顔は悉く ASCII（`printf %-42s` は和字を byte で数へ、表の桁組みを崩す ―― 原本の註に従ふ）。
- 結語へ `★多鍵形=%d★` を足し、`黙らぬ` の条件へも加へた（no-silent-failure §4）。

### 実走（argv 逐語）
```
bash scripts/agent_status.sh                      # 生の路
古い弾: rc=0 stdout=15行 stderr=1行   (10_*)
今の弾: rc=0 stdout=15行 stderr=1行   (32_*)   ★表は diff 0 行=一字も動かず★
```
生の名簿は **旧名**（hideyoshi / ashigaru1… ）ゆゑ帳が無く、生の路では新しい顔は **0 件**（`多鍵形=0`）。
∴ 疵を発火させる為に **★名簿を mac の席へ差し替へた写し★**を試験具として用ゐた（`# ★試験具★` 2 行・両写しに同一の差し替へ）。
```
sed -e 's|^MAINPC_AGENTS=(.*|MAINPC_AGENTS=(ashigaru-mac-1 … -4)  # ★試験具★|' \
    -e 's|^SECONDPC_AGENTS=(.*|SECONDPC_AGENTS=(ashigaru-mac-7 gunshi-mac)  # ★試験具★|'
古い弾: rc=0 stdout=10行 stderr=1行   (30_*)
今の弾: rc=0 stdout=10行 stderr=7行   (31_*)   ★鳴り5行+母數+黙らぬ★
```

## ⑵ `scripts/ratelimit_check.sh:64` ―― 甲と同じ病（bash 3.2）

```
古い弾: rc=2 ／ stdout ★0 行★ ／ stderr 2 行
  scripts/ratelimit_check.sh: line 64: declare: -A: invalid option
今の弾: rc=0 ／ stdout ★7 行★ ／ stderr 0 行（鍵無しの鳴り 0 件）
```
`set -euo pipefail` ゆゑ L64 で即死し、**器は初めから何も刷つて居らぬ**（甲が四器の口を塞いで居たのと同型・但し此れは自前の疵）。
連想配列 4 つ（AGENT_CLI / AGENT_MODEL / AGENT_PANE / CODEX_CONTEXT）を
**「鍵=値」の行を積んだ文字列 + `table_get`** へ書き直した（依存を増やさぬ・brew bash を入れぬ）。

**★意味を変へぬ為の一手★**: `table_get` は鍵が無い時 **空へ倒さず、stderr へ鳴つて rc=1 を返す**。
bash4+`set -u` で `${A[$k]}` が unbound で死ぬのと同じ扱ひを保つ為である
（黙つて既定値へ倒すと fail-open を作る ―― 当方の既往の疵）。
唯一の例外は群分けの `case "$(table_get … || true)"`：命令置換の rc は `case` の語では `set -e` を発火せぬ故、
**鳴りは出るが死なぬ**（其の時は `*)` = OTHER へ落ちる）。之は紙に宣して残す。

## ⑶ `scripts/switch_cli.sh` ―― ★引数を与へて測つた★（未測を残さぬ）

五路（50_）悉く **rc=1 で閉ぢる**。詳細と ★二つの疵★ は `62_kizu_switch_cli.md`。
**変異路（`--type` を正しく与へて実際に切替へる路）は ★測らぬ★** ―― 理由は 62_ に記す（未測の宣）。
