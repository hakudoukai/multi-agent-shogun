# 板 5f9f18d3 ― 15分 alive monitor が旧名で critical を出し過ぎる件の調べ（読み取りのみ）

- 担当: ashigaru-second-1 ／ 実測: 2026-09-26 21:00 JST 前後 ／ host: USER-O6AK917NTU（SecondPC）
- 変更・配備・timer・設定・push は**一切していない**（script も unit も触れず、写しのみ）。

## 1. 対象版（固定）

| 物 | path | sha256 |
|---|---|---|
| live 実体 | `/home/hakudokai/projects/multi-agent-shogun/scripts/alive_to_productive_monitor_v0_2_once.sh`（**git 未追跡**） | `e8bce96573bbbac5be899c60ea8455d0a6503165c72704f98c8b095e9970ca5d` |
| 写し | `target_script_e8bce965.sh.txt` | 同上（一致） |
| 呼ぶ unit | `secondpc-alive-monitor-v0.2.service`（ExecStart=`/bin/bash <上の実体>`）／timer 15分毎 | `live_measure_20260926.txt` |

## 2. 二時点の raw（別時点として比べる）

| 時点 | 写し | sha256 | alert_decision |
|---|---|---|---|
| baseline 2026-09-25T00:31:20Z | `baseline_raw_20260925_093119.json` | `7c8ae02c160a5eaa3e7d1944a3adf2d37ab123ec83e3f171354fae296d047659`（sidecar と一致） | critical |
| 現行 2026-09-26T11:50:44Z | `current_raw_20260926_205042.json` | `b51985a70cfacc3c8091495c95b01f7ead2da335d1ce71b454b8701c0547a2d8` | critical |

両時点とも6行は同じ形: shogun-second／karo-second／ashigaru5／ashigaru6／ashigaru7 が `active_expected・watcher_process_count=0 → delivery_path_broken__watcher_absent・critical`、ashigaru8 が `standby_not_expected・silent`。**二時点の差は無い＝一時の揺れではなく、恒常の誤り。**

## 3. critical の根拠（script の該当行）

- L15 `agents = ["shogun-second", "karo-second", "ashigaru5", "ashigaru6", "ashigaru7", "ashigaru8"]`
- L16 `expected = {"shogun-second", "karo-second", "ashigaru5", "ashigaru6", "ashigaru7"}`
- L193-196 watcher は `ps` の中の `scripts/inbox_watcher.sh {agent} ` で数える。
- L249-252 `expected` に居て watcher が0なら `critical`。L350 一つでも critical なら全体が critical。

∴ 母集団がこの script に**固定の字で書かれ**、2026-09-06 の体制替え（将軍職と足軽4〜7の廃止）に追随していない。

## 4. 現行 roster と実 watcher（2026-09-26 実測）

| 席 | 種 | pane | inbox_watcher | 備考 |
|---|---|---|---|---|
| ashigaru-second-1 | Claude Code | multiagent-second:0.0 %4 | PID 3543（起動 16:11:23・cwd=repo・log=`/tmp/iw_ashigaru-second-1.log`） | 生 |
| ashigaru-second-2 | Claude Code | multiagent-second:0.1 %5 | PID 3535（同） | 生 |
| ashigaru-second-3 | Claude Code | multiagent-second:0.2 %6 | PID 3529（同） | 生 |
| karo-second | Hermes | hermes-karo-second:0.0 %3 | 無し | 家老は DB 便で受ける（CLAUDE.md 現体制）＝局所 watcher を要さぬ |
| gunshi-second | Hermes | hermes-gunshi-second:0.0 %7 | 無し | 同 |
| shogun-second・ashigaru5〜8 | ― | 無し | 無し | 2026-09-06 廃止 |

## 5. 分類

| 類 | 該当 | 中身 |
|---|---|---|
| **旧名** | shogun-second・ashigaru5・ashigaru6・ashigaru7（critical 4件）、ashigaru8（silent） | 廃止席を `expected` に持つ。誤 critical の主因 |
| **対象母集団（種の誤り）** | karo-second（critical 1件） | Hermes 席で DB 便受け。`inbox_watcher.sh` の有無で生死を測る述語が当たらぬ。pane は在る（pane_present=True） |
| **対象母集団（漏れ）** | ashigaru-second-1〜3 | 実 watcher 3席が `agents` に無い＝**本当の断を見る目が今は無い**（誤 critical の裏に、見落としの穴） |
| **時刻差** | baseline と現行 | 二時点とも同形ゆえ、時刻差による誤りは見えぬ。付記: 9月の raw 2088件のうち critical 1759・warning 329、最後の warning は `..._20260907_031727`（廃止 09-06・WSL crash 09-07 の直後）以後は全て critical |
| **（副）log の旧名** | 全席 | L198 は `/tmp/inbox_watcher_{agent}.log` を読むが、実 log は `/tmp/iw_{agent}.log`（`/tmp/inbox_watcher_*.log` は0件）。log 由来の欄（log_age・last_wakeup 等）は常に空 |

## 6. 解除条件の案（task_tracker 記載用・変更は承認経路の後）

1. 対象版 = 上の e8bce965（git 未追跡ゆえ、直すならまず追跡に入れて版を持たせる）。
2. 誤 critical の原因 = L15-16 の固定母集団が旧名（§5）。
3. 現行の許容 role = Claude Code 足軽 `ashigaru-second-1〜3` を watcher 述語で `expected`。Hermes 席（karo-second・gunshi-second）は watcher 述語の外（pane の有無か DB 便の側で別に測る）。廃止席は外す。
4. 依存 = `queue/pane_registry.yaml`（旧名の行が残る）、log の path（`/tmp/iw_*`）、unit の ExecStart（repo の実体を直に呼ぶ＝file を変えれば次の15分で効く＝**配備と同義**ゆえ承認要）。
5. 受入の目安 = 直した後の1回の raw で、足軽3席が watcher=1・critical 0、廃止席の行が無いこと。

## 7. 測っていないもの

- 板の current_step の行そのもの（DB の板は本 worktree から読んでいない）。
- 「62578306 の配備」が何の commit・何の配備かは未照合。
- 事業部長の readback（上位の仕事）。
