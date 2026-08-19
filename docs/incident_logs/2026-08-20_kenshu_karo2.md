# 第2段 ― 配下の版揃・doppler統一 検収台帳（家老second / 委員長令 seq200097 受）

- as of: 2026-08-20T02:09:30 JST
- host: second_pc / repo: /home/hakudokai/projects/multi-agent-shogun
- 親令: pc_handshake **seq200097**（iincho → karo-second, 2026-08-20T01:02:10 JST）
  「★貴殿の持ち分＝配下の版上げ検収。doppler統一(8体)の検収も★」
- 執行体の台帳（読取のみ・sha 独立検算にて一致）:
  - `docs/incident_logs/2026-08-20_stage2_restart_execution_shogun-second_200226.md`
    sha256 `70bf1d2a4c17944b12e7a9f20ef0b2e14695b683bd8c283f8bbbc2da8eb6532e`
  - `docs/incident_logs/2026-08-20_stage2_post_verify_protocol_shogun-second_200174.md`
    sha256 `d651768ebc0e49fcf193f08b03f99bde1ea886076473f7cb5f59bd08106e0549`
- 本紙の性格: **読取のみ**。restart 0 ／ kill 0 ／ send-keys 0 ／ capture-pane 0 ／ install・npm 一指 0 ／ Hermes 不触。
- **★測りの順★**: 執行体の紙を**読む前に**己の器で測り、後に突合した（相手の値に引かれぬ為）。

---

## 一 検収の述語（三点＋一点）

| # | 問 | 器 | 合格 |
|---|---|---|---|
| ㊀ | 実行体が入れ替はったか | `readlink /proc/<PID>/exe` | `(deleted)` が**消ゆ** |
| ㊁ | 同一性 | `stat -L -c %s` ＋ ディスク実体の sha256 | 330,946,864 B ／ `bfcf0ae2…d5d5` |
| ㊂ | 旧実体を掴み居らぬか | `/proc/<PID>/maps` の `(deleted)` 行数 | **0** |
| ㊃ | doppler 統一 | 祖先遡り（`/proc/<PID>/stat` の ppid 連鎖） | 祖先に doppler 有 |

**同定は `--resume <UUID>`** にて行ふ（`tmux` を一切用ゐず）。UUID→役職 の対は seq200174 の紙（sha 検算済）に拠る。

---

## 二 実測（2026-08-20T02:09:30 JST）

| @agent_id | 新 PID | 起動 | ㊀exe | ㊁size | ㊂deleted_maps | ㊃doppler |
|---|---|---|---|---|---|---|
| ashigaru-second-1 | 3661563 | 2026-08-20T02:00:56 JST | npm-global 実体（deleted 無） | 330,946,864 | 0 | **False** |
| ashigaru-second-2 | 3660796 | 2026-08-20T02:00:45 JST | 同上 | 330,946,864 | 0 | **False** |
| ashigaru-second-3 | 3660072 | 2026-08-20T02:00:28 JST | 同上 | 330,946,864 | 0 | **False** |
| ashigaru-second-4 | 3658974 | 2026-08-20T02:00:13 JST | 同上 | 330,946,864 | 0 | **False** |
| ashigaru-second-5 | 3657843 | 2026-08-20T01:59:58 JST | 同上 | 330,946,864 | 0 | **False** |
| ashigaru-second-6 | 3655376 | 2026-08-20T01:59:16 JST | 同上 | 330,946,864 | 0 | **False** |
| karo-second（当職） | 3662641 | 2026-08-20T02:01:16 JST | 同上 | 330,946,864 | 0 | **False** |
| shogun-second | 1663046 | 2026-08-10T18:41:48 JST | `.claude-code-wTkEzMFd/bin/claude.exe` **(deleted)** | 297,831,432 | **5** | **False** |

exe 実体 ＝ `/home/hakudokai/.npm-global/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`
ディスク実体を独立に測る: 330,946,864 B ／ sha256 `bfcf0ae2dbf94b2b6a106074aabf3938b9a10889c3b678e4cb5a00c03274d5d5`（**執行体の申告と一致**）／ 同 path の `--version` ＝ **`2.1.235 (Claude Code)`**。

祖先は 8 体悉く `-bash > tmux > systemd`。

---

## 三 判定

- **㊀㊁㊂ 版揃 ＝ PASS 7/7**（足軽second 1〜6 ＋ 当職）。基線（8/8 deleted・297,831,432 B）より入れ替はった事、**二つの独立な徴**（exe から deleted が消えた／maps の deleted 写像が 5→0）にて確かむ。
- **shogun-second ＝ 未了（1/8）** ―― 執行体自身が「次は当職自身が落ちて戻る」と申し置き、**予定通り**。瑕に非ず。
- **★㊃ doppler 統一 ＝ FAIL 0/8★** ―― 委員長ご下命の「doppler統一(8体)」は**果たされて居らぬ**。

### doppler ―― 二つの器で測り、同じ答
1. 祖先遡り ＝ **0/8 True**
2. `/proc/<PID>/environ` の `DOPPLER_` 変数**個数のみ**を数ふ（**値は一切読まず・出力もせず**） ＝ **8 体悉く 0 本**

執行体の台帳 五の二節に**自ら「一体も包んで居らぬ」と記載**在り。理由 ⑴seq200226 の四条に doppler 無し ⑵doppler は env に secret を注ぐゆゑ `ANTHROPIC_API_KEY` 混入なれば §18／DD-164 の禁ずる直課金経路へ倒れ得る・secret 値を読めぬ以上 安全を確かめ得ぬ。
**⇒ 当職の測りと執行体の申告は一致。隠蔽・誤報の類に非ず。** 残るは「**doppler で包むは安全か**」の一問であり、**之は当職の枷の外**（secret 読取・§18 経路の裁は上位の専権）。

---

## 四 ★併せて見付けたる罠（現に害無し・後に効く）★

`claude` は **二本** 在り、PATH の順にて勝敗が決まる。

| path | 実体 | version | size | 更新 |
|---|---|---|---|---|
| `~/.npm-global/bin/claude`（PATH 先） | `~/.npm-global/lib/.../claude.exe` | **2.1.235** | 330,946,864 | 2026-08-20T01:52 JST |
| `~/.local/bin/claude`（PATH 後） | `~/.local/lib/.../claude.exe` | **2.1.187** | 234,874,664 | 2026-06-24T12:57 JST |

- 今回の 7 体は**先の一本**を掴み居る（exe path にて実証）ゆゑ **現に害は無い**。
- 然れど **path を名指しにて起こす者が `~/.local/bin/claude` を指せば 2.1.187 へ退行する**。当職も本 turn の初手で此の旧き方を名指しして「ディスク＝2.1.187」と誤つ所を得た。
- **当職は直さず**（機構是正 0）。**罠として札すのみ**。処置の可否は上位の裁。

---

## 五 UNMEASURED（隠さず札す）

- **走行体の version 文字列** ―― 実行体は packed ゆゑ逐語掃き 0 件。㊁の同一性（size ＋ sha ＋ 同 path の `--version`）**より推す**。★直の測りに非ず★。
- **会話継続（`--resume` が効いた事）** ―― 当職自身に就いては**当職の自申**（＝他体より弱い証）。足軽 6 体に就いては **pane 実視 0**（capture-pane を用ゐぬ条を守る）ゆゑ **UNMEASURED**。ただし 6 体とも `--resume <UUID>` を引数に持ち、UUID は再起動前の対応表と**悉く一致**する。
- **足軽second 7** ―― Claude Code に非ず Hermes ゆゑ**本件の外・不触**。

---

## 六 変ぜぬ物

restart 0 ／ kill 0 ／ tmux 一指 0（list-panes すら用ゐず） ／ send-keys 0 ／ capture-pane 0 ／ pane 入力 0 ／ script 改変 0・実行 0 ／ install・npm 一指 0 ／ watcher 一指 0 ／ config 0 ／ **secret 値 読取 0**（`DOPPLER_` は個数のみ・値は読まず） ／ Hermes 一指 0 ／ 他 PC へ SSH 0 ／ DB mutation 0（本件の報のみ） ／ git add 0・commit 0・push 0 ／ queue/tasks 書込 0 ／ 新規 task 起票 0 ／ 他者の箱 札 0 ／ 軍師直送 0 ／ dashboard 不触 ／ 広域走査 0 ／ 空焚き 0 件。
