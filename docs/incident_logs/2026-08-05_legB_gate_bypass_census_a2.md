# leg B 附帯 — queue/inbox/*.yaml「触り得る script」全数台帳・門迂回の実効分母 (足軽2号)

- **下命**: karo-second (msg_20260805_152832_5fa9ef27, 2026-08-05T15:28:32)。
  「門は `inbox_write.sh` の中にのみ在り (canon参照4箇所)、然れど `queue/inbox/*.yaml` を触り得る script は当職の勘定で11本 (scripts/のみの grep 実測・記憶に非ず)。
  母集団は scripts/ のみゆえ shim/ tests/ も足して数え直せ」との指示。
- **境**: 読取のみ・実装なし / bats 禁 (実行はしておらぬ・全て静的解析) / .gitignore 不触 / commit は軍師 PASS 後。
- **断面凍結**: 2026-08-05T15:38:53+0900 / base_commit=`7b14b8d` (`7b14b8df710a84d2ce23290817c47cb20fa16956`)。

---

## §0 この帳は何を以て閉じるか

閉じる条件 = (1) 母集団 (scripts/+shim/+tests/) を悉皆で列挙し、(2) 各件を 読取専用/門経由書込/門直接迂回 の三値+第四値(判定不能)で分け、
(3) 「11本」との差分を報告し、(4) 実効の迂回経路数 (real path へ現に届き得る非経由書込) を出し、(5) karo-second の受理を得た時点。
**閉じないもの** = 迂回経路の是正実装 (本帳は監査のみ・実装は別工区)。

**次回検知法**: `/usr/bin/grep -rl "queue/inbox" --include="*.sh" --include="*.py" --include="*.bats" scripts/ shim/ tests/` を再実行し、
件数が30と一致するか見よ。不一致なら本帳は陳腐化。

---

## §1 母集団の定義・断面凍結 (先に宣言)

**抽出コマンド (独立実行)**:
```
/usr/bin/grep -rl "queue/inbox" --include="*.sh" --include="*.py" --include="*.bats" scripts/ shim/ tests/
```
`/usr/bin/grep` を用いた理由 = `git grep`/wrapped `grep` は `.gitignore` 対象を無警告 skip する既知欠陥
(memory `grep-git-grep-silently-skip-gitignored`)。実際 scripts/ 配下だけで **3件が gitignored/untracked** と判明 (§3 参照)。

**母集団 = 30件** (scripts/=15・shim/=2・tests/=13)。うち **1件は false positive** (§3-D、実際には file I/O を一切行わぬ)。

### karo-second の「11」との差分 (先に報告・咎めぬ)

- 当職が `/usr/bin/grep -rl` (filesystem 直読・gitignore 無視) で scripts/ のみを数えると **15件** (12 git-tracked + 3 gitignored)。
- `git grep` (tracked のみ) で数え直すと **12件**。
- karo-second の「11」は「記憶に非ず grep 実測」と明記されているが、当職の12/15いずれとも一致せず。
  **原因は判定不能 (第四値)** — 使用した grep の実装・include パターン・除外条件が不明ゆえ。
  ★これは咎めではない★ — 母集団の抽出条件が一行違うだけで数は動く、という本日一貫の型そのものである。
- ∴ 本帳では **当職が独立に導いた 30件 (scripts/15 + shim/2 + tests/13)** を正とし、以後この数で進める。

---

## §2 判定基準

| 軸 | 値 |
|---|---|
| ⑴ I/O | 書込あり / 読取のみ / **I/O無し (false positive)** |
| ⑵ 書込経路 | `inbox_write.sh` 経由 (門の内) / 直接書込 (門の外=迂回) |
| ⑶ 稼働状況 | 稼働中 (daemon/timer/hook等で現に呼ばれる) / 手動 (人・agent が明示実行) / 死蔵疑い (呼び手不明) |
| ⑷ 対象 path | 実 PROJECT_ROOT (real) / sandbox (mktemp 隔離・退避先が queue/inbox の外) |
| ⑸ 迂回時の被害半径 | 任意内容の書込可 / 既存メッセージの `read` flag のみ変更可 / 空 skeleton 作成のみ (存在しない時に限る) |

判定不能に何が出れば動くか = 呼び手 (cron/systemd/人) の実在を `systemctl`/`crontab` 等 **一次情報で確認できた時**。
本帳は当PCで確認できた範囲 (systemd --user) のみを実測とし、それ以外は「コード上は可能・稼働主体は未検証」と明記する。

---

## §3 全30件 台帳

### A. 実 path へ直接書込 = 門の迂回 (5件・被害半径つき)

| # | file:line | 稼働状況 | 被害半径 |
|---|---|---|---|
| 1 | `scripts/inbox_watcher.sh:387,507,562` (`yaml.safe_dump`) | **稼働中** — 常駐 watcher daemon。git status M (本 turn の直前まで編集中)。 | **大** — read-mark更新・rotation・archive退避で file 全体を書き換え可。任意内容を書ける経路 (自 agent の受信処理ロジックとして)。 |
| 2 | `scripts/bulk_ack.sh:118` (`yaml.safe_dump`) | 手動 — usage文 `bash scripts/bulk_ack.sh <agent_id>` (2026-05-07 制定・自己増殖ループ事故の恒久対応ツール)。cron/systemd 未確認。 | **中** — 既存message群の `read` flag のみ変更可。新規内容の捏造は不可。 |
| 3 | `scripts/watcher_supervisor.sh:26` (`ensure_inbox_file`) | **稼働中** — MainPC watcher 監視 loop (常駐想定、`set -euo pipefail` の永続 script と明記)。 | **小** — file が存在しない時に `messages: []` の空 skeleton を作るのみ。既存 file には触れぬ。 |
| 4 | `scripts/watcher_supervisor_third.sh:24` (同上) | **稼働中** — third_pc 版・同一パターン。 | **小** — 同上。 |
| 5 | `shim/hakudokai/hakudokai_secondpc_setup.sh:328` (`echo "messages: []" >`) | 手動 — Phase 4 (inbox準備)、PC 初期セットアップ時の一回限り実行。 | **小** — 同上 (存在しない時のみ)。 |

### B. 門経由だが real path に現に副作用あり (2件・うち1件は事故確定)

| # | file | 経路 | 所見 |
|---|---|---|---|
| 6 | `tests/agent_selfwatch.bats:258` (`TC-FR-014`) | `run bash "$INBOX_WRITE_SCRIPT" test_agent ...` — `INBOX_WRITE_SCRIPT="$PROJECT_ROOT/scripts/inbox_write.sh"` = **実スクリプトを sed retarget なしで直呼び** | ★★事故の根治源を特定★★ — target=`test_agent` は canon 外ゆえ leg B の fail-closed が発火、FROM=`karo` (canon 内) の**実 `queue/inbox/karo.yaml`** へ delivery_failed 通知を書く。teardown (L276) は `queue/inbox/test_agent.yaml` の掃除のみで、karo.yaml への副作用は掃除対象外。**止血命令が指す4通の delivery_failed の発生機序と file:line が一致**。leg B 以前は同じ呼出しが「宛先不明チェック無しで `queue/inbox/test_agent.yaml` を実 path に生成する」型 (静かなゴミ file) だった可能性が高く、leg B は**症状を「静かなゴミ」から「karoへの誤配」に変えた** (=karo-second が言う「leg B が新たに開けた穴」の実体)。 |
| 7 | `scripts/shogun_self_check.sh` | `bash "$SCRIPT_DIR/scripts/inbox_write.sh" "$TARGET" ...` (gate経由・正しい使い方) | **untracked/gitignored** (`git status --porcelain --ignored=matching` で `!!`) にも関わらず、`systemctl --user list-unit-files` 実測で **`shogun-self-check.timer` = enabled/enabled** と確認 — ★git に見えぬ file が現に systemd で定期稼働している★ (memory `gitignore-whitelist-silent-drop` の実例追加)。書込自体は門経由で健全だが、**この script の存在・改変履歴が git に残らぬ**点は別種のリスクとして注記。 |

### C. 読取専用 (14件・迂回リスクなし)

`agent_status.sh` / `checks/inbox_alias_integrity.sh` / `checks/secondpc_dispatch.sh` / `karo_overload_monitor.sh` / `stop_hook_inbox.sh` / `read_pruned_archive.sh`(untracked) /
`agent_health_check.sh`(★注1★) / `lib/inbox_path.sh`(path文字列を返すのみ・I/O自体なし) /
`tests/checks/test_agent_health_check.bats`(`TEST_MODE=1`で書込stub化済) / `tests/unit/test_stop_hook.bats`(mock) / `tests/unit/test_idle_flag.bats`(mock) /
`tests/unit/test_dead_letter.bats`(sandbox内stub) / `tests/unit/test_send_wakeup.bats`(`$TEST_TMPDIR`内・gate呼出なし) / `tests/e2e/mock_cli.sh`(★注2★)

★注1★ `agent_health_check.sh` は読取(unread count)に加え、3箇所で `bash .../inbox_write.sh shogun ...` を呼ぶが、これは対象固定 (`shogun`固定・canon内) の**意図された門経由の書込**であり迂回ではない。分類上「読取+正規門利用」。
★注2★ `mock_cli.sh` は `$MOCK_PROJECT_ROOT/queue/inbox/...` を参照。e2e harness からは `MOCK_PROJECT_ROOT=$E2E_QUEUE` (sandbox) で渡され安全。ただし **default値が `.`** (L30) ゆえ、e2e harness を介さず単独で cwd=repo root から手動実行すれば実 path に触れ得る (現状そのような呼び手は確認できず=判定不能)。

### D. 母集団への false positive (1件)

`shim/hakudokai/hakudokai_init_agents.sh` — grep が拾った行はエージェント起動 prompt 文字列中の `"queue/inbox/${agent}.yaml"` という**文言**であり、この script 自体は file I/O を一切行わぬ (別 agent への指示文の一部)。母集団に含めた上で「該当なし」と明記する (§本節冒頭の「零を述べるなら対照同梱」原則)。

### E. 健全例=対照 (門を正しく sandbox 化できている書込テスト・4件+1件)

- `tests/test_inbox_write.bats` / `tests/test_inbox_expiry_supersession.bats` / `tests/test_shadow_mailbox_failclosed.bats` —
  **`sed` で `SCRIPT_DIR=` 行を `$TEST_TMPDIR` へ retarget した実スクリプトの写しを作り、写しの方を呼ぶ**技法。
  `inbox_write.sh` の全 path (inbox / dead_letter / canon registry) は `$SCRIPT_DIR` 起点で一貫しているため、この技法は registry chk まで含め正しく隔離できる (独立に sed 出力を検証済・§1 抽出コマンド実行と同じ turn で確認)。
- `tests/e2e/{e2e_basic_flow,e2e_inbox_delivery,e2e_parallel_tasks}.bats` — `tests/e2e/helpers/setup.bash` が `cp` で実スクリプトを `$E2E_QUEUE/scripts/` へ複製、SCRIPT_DIR 自動解決で隔離。real path への漏出は無い。
- `scripts/test_secondpc_monitor_v2.py` (untracked) — `tempfile.TemporaryDirectory()` で完全隔離、そもそも `inbox_write.sh` を呼ばず file を直接生成するだけ。**real path 接触ゼロの正例 (対照)**。

**★§3-E に付随する隣接発見 (別工区候補・本工区の対象外)★**: `tests/e2e/helpers/setup.bash` の `queue/` 初期化 (L60-62) は
`queue/inbox,tasks,reports,metrics` は作るが **`queue/pane_registry.yaml` を複製していない**。leg B の canon gate 導入後、
E2E sandbox 内で `CANON_REGISTRY="$SCRIPT_DIR/queue/pane_registry.yaml"` が読めず `DETECTOR_UNAVAILABLE` fail-closed reject が
全 target (`ashigaru1`等、本来 canon 内) に対しても発火する可能性が高い (未実行で確認・bats 禁のため断定はしない → **第四値**)。
real path への漏出はないため safety 問題ではないが、E2E テスト群の **機能的レグレッション** の疑いとして記録する。

---

## §4 実効の分母 (門を現に迂回し得る経路)

**11 (karo-second起点・scripts/のみ) → 30 (悉皆・scripts/+shim/+tests/) のうち、real pathへ迂回して書込み得るのは 7件**:

- **直接迂回 (門を通らず real path へ書込)** = 5件 (§3-A)。うち被害半径「大」は `inbox_watcher.sh` の1件のみ、
  残り4件は「file不在時のみ空skeleton作成」で既存内容を上書きできぬ狭い経路。
- **門経由だが real path へ誤配し得る/した** = 2件 (§3-B)。うち1件 (`agent_selfwatch.bats` TC-FR-014) は
  **本日の delivery_failed 4通と機序一致=事実上「起きた」**。もう1件 (`shogun_self_check.sh`) は健全利用だが git 不可視。

**∴ 30分の7 (23%) が real path 接触の実効経路。うち即応急を要するのは `agent_selfwatch.bats:258` の1件**
(唯一「非canon宛先を意図的に使い、かつ sandbox化されていない」組み合わせ=事故と直結)。

---

## §5 【本工区で己が直した誤り】

- 当初 `git grep` の出力のみで母集団を確定しかけたが、`/usr/bin/grep -r` と突き合わせて **gitignored 3件 (scripts/) の抜け** に気付き、
  全域を filesystem 直読に切り替えた (memory `grep-git-grep-silently-skip-gitignored` を実地で再確認)。
- `scripts/watcher_supervisor.sh` の直接書込を最初「危険な迂回」と一括りにしかけたが、`ensure_inbox_file` の中身を読み込み
  「存在しない時のみ空skeleton」という**狭い経路**と判明 → §3-A の「被害半径」列を追加し、5件を同列に並べない扱いに改めた。

## §6 【この工区と対に成る他工区】

- `docs/incident_logs/2026-08-05_legC_17site_ledger_a1.md` (足軽1号) — **母集団が異なる**: あちらは「`inbox_write.sh` を呼ぶ17箇所の呼び手が exit code を見ているか」(門の外からの**呼び方**の質)。
  本帳は「門を通らず real path へ書ける script が何本あるか」(門**自体の迂回**)。重なりは無い (相互参照のみ)。
- `docs/incident_logs/2026-08-05_legC_exitcode_caller_survey_a3.md` / `_unattended_caller_survey_a3.md` (足軽3号) — 同じく17箇所呼び手側の調査、本帳とは非重複。
- 未対工区候補 = §3-E 末尾の E2E sandbox `pane_registry.yaml` 欠落問題 — **本工区の scope外 (境=実装なし・調査のみ)**、別途起票候補として記す。

## §7 監査体制の明記

★PASS記載は現状 **二者制 (軍師 + Gemini。Codex leg は理事長 SAFETY 裁定 seq132707 により停止中)** ★。三者PASSとは書かぬ。

## §8 未了・引き継ぎ

1. 直接迂回5件 (§3-A) の是正 (実装) は本帳の対象外・別工区。
2. `agent_selfwatch.bats:258` の real-path汚染は既発生 (delivery_failed 4通・止血命令の対象母集団と一致) — 止血命令の解除条件 (sandbox化) にこの1件が該当することを karo-second へ明記して返す。
3. E2E sandbox の `pane_registry.yaml` 欠落疑い (§3-E末尾) — 未実行検証ゆえ第四値のまま。裁定・実行は上へ。
4. `shogun_self_check.sh` の git 不可視×稼働中 (systemd timer enabled) — 別種のリスクとして上申候補 (本帳は事実の記録のみ・裁定せず)。
