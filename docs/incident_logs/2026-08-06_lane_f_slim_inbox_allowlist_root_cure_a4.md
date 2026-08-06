# 2026-08-06 Lane F — `slim_all_inboxes()` pane_registry allowlist 根治 (足軽4号)

下命: 家老second msg_20260806_225010_ea25aa15 (2026-08-06T22:50:10)。owner=ashigaru4。
出所: 本部長殿 22:45:33 根治GO ／ 将軍second殿 22:47:04 転記 ／ 家老second owner指名。

## 禁則順守 (実行の都度確認)

- `slim_yaml.sh` を走らせておらぬ (dry-runも含め0回)。停止令は継続 (解く権は本部長殿)。
- 実原本 `queue/inbox/_dead_letter_second.yaml` の本文を一度も開いておらぬ (`grep`/`wc`/`cat`不使用)。
  本票中の「除外対象一覧」は `pane_registry.yaml` を読み `queue/inbox/*.yaml` の**ファイル名 (stem) のみ**を
  `Path.glob().stem` で列挙した結果であり、対象file本文は一切参照しておらぬ。
- legacy 3 file 不触。worktree/branch を新たに起て、主repoのHEADは動かしておらぬ (下記§1で確認)。
- push 0・deploy 0・local のみ。

## §0 母集団・器・範囲宣言

- 対象コード: `scripts/slim_yaml.py` の `slim_all_inboxes()` (root cause)。
- 器①(caller inventory): `/usr/bin/grep -rn "slim_yaml.sh" instructions/*.md instructions/generated/*.md` (全12ファイル実測)。
- 器②(正本): `queue/pane_registry.yaml` (read-only, 一度も編集せず)。
- 器③(RED/GREEN evidence): `bats` (bats-core のみ。**bats-support/bats-assert submodule は本環境で未初期化ゆえ`load`を使わず素のbats coreで実装** — 既存 `tests/e2e/e2e_slim_retention.bats` も同一環境制約で現状 `load` 失敗が再現する。git submodule initはネットワーク要伺い対象ゆえ本工区では実施せず)。
- 範囲: 測時 2026-08-06T22:55〜23:01 JST。worktree=`/tmp/hakudokai-worktrees/lane-f-slim-allowlist-a4` (branch `feat/lane-f-slim-allowlist-a4`、base=主repo HEAD `d18939e4091ed4fa9e57c794f24ad0ae0974bab6`)。

## §1 主repo HEAD 不変証明

```
$ git -C /home/hakudokai/projects/multi-agent-shogun rev-parse HEAD
d18939e4091ed4fa9e57c794f24ad0ae0974bab6   ← worktree 分岐前と同一 (本票冒頭の下命出所コミット群と同じ)
$ git -C /tmp/hakudokai-worktrees/lane-f-slim-allowlist-a4 rev-parse HEAD
d18939e4091ed4fa9e57c794f24ad0ae0974bab6   ← worktree の HEAD も同一 (未commit、working tree のみ変更)
```

## ㈠ 全caller / 直接target経路 inventory (母集団=全12ファイル、`/usr/bin/grep -rn "slim_yaml.sh"` 実測)

| ファイル | 呼出行 | 実引数 | `slim_all_inboxes()`到達? |
|---|---|---|---|
| instructions/karo.md:39 | `bash scripts/slim_yaml.sh karo` | 固定文字列 `karo` | ★到達 (脆弱経路)★ |
| instructions/karo_canon_20260709.md:39 | 同上 | `karo` | ★到達★ |
| instructions/generated/karo.md:38 | 同上 | `karo` | ★到達★ |
| instructions/generated/codex-karo.md:38 | 同上 | `karo` | ★到達★ |
| instructions/generated/copilot-karo.md:38 | 同上 | `karo` | ★到達★ |
| instructions/generated/kimi-karo.md:38 | 同上 | `karo` | ★到達★ |
| instructions/ashigaru.md:37 | `bash scripts/slim_yaml.sh $(tmux display-message ... "#{@agent_id}")` | 自agent_id (動的) | 不到達 (`slim_inbox(own_id)`のみ) |
| instructions/generated/ashigaru.md 等4件 | 同上 | 自agent_id | 不到達 |
| instructions/gunshi.md:71 他4件 | `bash scripts/slim_yaml.sh gunshi` | 固定文字列 `gunshi` | 不到達 |
| **`instructions/karo-second.md`** | (該当行なし、`slim_yaml`未hit) | — | — |

⇒ **`slim_all_inboxes()`への到達経路は「`karo.md`系 (正本 or generated) の step1.5 を実行する主体」のみ**。
`karo-second.md` 自体には呼出行が無いが、CLAUDE.md「karo-second は instructions/karo-second.md も必読 (karo.mdに追加して)」の運用ゆえ、
**karo-second は karo.md のstep1.5をも実行し、その際の実引数は動的な自id(`karo-second`)ではなく固定文字列`karo`のまま**である
(instructions/karo.md:39 のコマンド文字列自体に変数展開が無い)。これが本Laneの端緒となった「家老secondの禁破り」の機構的な因である
——**家老secondの不注意ではなく、`karo.md`のコマンド文字列が呼出主体に依らず`karo`固定である事**が一次因(★人でなく器★)。
- cron/systemd/timer からの呼出=repo全体`/usr/bin/grep -rl "slim_yaml"`で0件 (該当なし、上記12+コード2件+testのみ)。
- 足軽2号の「無除外glob全数索し」票は本人からの受け渡しが本工区着手時点で未着ゆえ、上記grep実測で独立に代替した (受領あり次第突合)。

## ㈡ RED — 旧base ＋ synthetic fixture: `read: true` の deadletter風fileのSHAが現に変わる事

- 旧baseコード = worktree HEAD (`git show HEAD:scripts/slim_yaml.py`、= 主repo現行 = 本Lane着手前のコード) をそのまま抽出。**書き直しではない**。
- fixture = 実物と無関係の合成file `_dead_letter_synthetic.yaml` (アンダースコア接頭辞のみ模す、内容は`synthetic-deadletter-immutable-content`という架空文字列)。
- 実行: `bats tests/e2e/e2e_slim_inbox_allowlist.bats` の1件目。

```
$ date -Iseconds && bats tests/e2e/e2e_slim_inbox_allowlist.bats
2026-08-06T22:59:58+09:00
1..8
ok 1 RED: old base slim_all_inboxes changes a read:true dead-letter-like file's SHA
```

⇒ **旧baseで実行すると `_dead_letter_synthetic.yaml` のSHA256が実行前後で相違する事を実測で確認 (`[ "$before" != "$after" ]` が通過)**。
「壊れ得る」ではなく「現に壊れる」を示した (本部長殿の求めに合致)。

## ㈢ GREEN — 修正版: live対象のみ変化・deadletter/shadowはSHA不変 他

同一bats fileの2〜8件目、全PASS (実行ログ上記と同一run):

```
ok 2 GREEN: fixed slim_all_inboxes leaves dead-letter/shadow SHA unchanged, live target changes
ok 3 GREEN: missing pane_registry.yaml fails closed to 0 targets, dead-letter untouched
ok 4 GREEN: malformed pane_registry.yaml (panes not a list) fails closed to 0 targets
ok 5 GREEN: empty inbox dir yields 0 targets processed without error
ok 6 GREEN: idempotent rerun -- second run is a no-op on already-slimmed live target
ok 7 GREEN: concurrent invocations via slim_yaml.sh serialize (flock) without corruption
ok 8 GREEN: partial failure (messages not a list in one file) does not corrupt dead-letter
```

| # | 検証項目 (本部長殿㈢列挙) | 内容 |
|---|---|---|
| 2 | live対象だけ変化・deadletter/shadow不変 | 合成dead-letter・合成shadow(`unregistered_shadow_box.yaml`)のSHA不変、登録済`ashigaru1`相当のSHAは変化。除外理由がstderrに出る事も確認 (`SKIP (not in pane_registry allowlist): ...`)。 |
| 3-4 | 未登録／system／dead-letter／shadow = fail-closed 0件 + 理由報告 | registry欠落・panes非list の2パターンとも「0対象」に落ち (deadletter/live 双方不変)、`FAIL-CLOSED:`理由がstderrに出る事を確認。 |
| 5 | empty・malformed | 空inboxディレクトリで例外なく正常終了。 |
| 6 | idempotent rerun | 2回連続実行でSHA不変 (2回目は1回目の結果を再度読むのみ)。 |
| 7 | 並行flock | `slim_yaml.sh`経由で2プロセス同時実行、両者exit 0・出力YAMLがparse可能(torn write無し) — 既存の`.slim_yaml.lock`機構(1本のみ、新設せず)がそのまま機能する事を確認。 |
| 8 | partial failure | 登録済file 1件が壊れた(`messages`が非list)場合、プロセス全体はexit非0で停止するが、deadletter風fileはその時点で未処理ゆえSHA不変のまま。 |

## ㈣ 実原本不使用・患者/secret 本文0の確認

- 全fixtureは`mktemp -d`配下の合成project (`build_synthetic_project()`)。実repoの`queue/`は一度も書込・削除・rename対象になっておらぬ (読取専用の`pane_registry.yaml`実測1回のみ、下記§X)。
- 患者情報・secret値=0件 (fixture文字列は`live-agent-old-message`等の架空値のみ)。

## ㈤ ★再開の判断は為さず★ — 『再開できる形』のみを作り、止めたまま提出

- 実装は**このworktreeの working tree にのみ存在** (`scripts/slim_yaml.py`修正 + `tests/e2e/e2e_slim_inbox_allowlist.bats`新設)。**主repoへは一切反映しておらぬ** (§1のHEAD不変証明参照)。
- 主repoの`queue/inbox/_dead_letter_second.yaml`は本工区を通じ一度も変化していない (`slim_yaml.sh`を一度も実行しておらぬゆえ自明)。
- **㈤の条件 (軍師PASS ＋ 本部長殿によるlive dry-runでの`_dead_letter_second`対象list 0件確認) は本票の時点で未充足**。当職は再開を宣言せず、以下「再開に要る手順」のみを列挙する:
  1. 本票を軍師secondへ提出しPASSを得る (下記令⑥)。
  2. PASS後、本部長殿(または指名者)が主repoへ`scripts/slim_yaml.py`の差分を反映 (`git show`等でworktreeから取込み、commitは別途要伺い)。
  3. 反映後、**dry-run** (`python3 scripts/slim_yaml.py karo --dry-run`) で対象file一覧を出力し、`_dead_letter_second`が出力に含まれぬ事を本部長殿が確認する。
  4. 確認後、初回実行時に pre/post のSHAを対象・除外の双方で測る (㈥、下記)。

## ㈥ 参考 (実測・実運用ではない): 実dataに対する「もし今適用したら」投影 (read-only, mutate無し)

`get_registered_agent_ids()` を実repoの `queue/pane_registry.yaml` に対して読取専用で実行し (本文はfile名のstemのみ、中身は開かず)、
`queue/inbox/*.yaml` の実ファイル名一覧と突合した結果 (測時2026-08-06T23:00頃、slim実行は一切せず):

- allowlist件数=17、on-disk stem件数=31。
- **処理対象になる (allowlist∩on-disk) = 15件**: ashigaru1-7, gunshi, gunshi-second, honbucho, karo, karo-second, shogun, shogun-second, takenaka。
- **除外される (on-disk − allowlist) = 16件**: `_dead_letter_second`, `_test_cap_rotation`, `_test_w67fix`, `ashigaru-second-1〜7`(7件), `ashigaru8`, `fukuincho`, `maeda`, `senmu_codex_second`, `third_pc`, `training`。
  - ★`_dead_letter_second`が本件で「不触の対象」から「fail-closedで除外される対象」に転じる事を確認 — これが本Laneの目的の直接証跡。
  - **未決事項 (裁定せず列挙のみ)**: `ashigaru8`/`fukuincho`/`maeda`/`senmu_codex_second`/`third_pc`/`training`/`ashigaru-second-1〜7` は
    `stat`実測で一部が直近数日以内に更新されており (`ashigaru8`=08-05, `training`=08-04, `maeda`=07-21, `senmu_codex_second`=08-04)、
    **正規運用中の箱の可能性がある**。これらは`pane_registry.yaml`未登録ゆえ新設計では今後slim対象外(=肥大化を許す)になる。
    ★当職は「registryへ追加すべきか」を判じておらぬ — registryの正本性を守る権者 (家老second/本部長殿) の判断事項として上申する★。
  - `ashigaru-second-1〜7`は内容が13バイトの空stub (04日以来更新無し、`ashigaru1〜7`という別命名の実file群が現に稼働中でありこちらが生きた箱) — 命名の重複/旧世代命名の残骸である可能性が高いが、これも削除・統合は本工区の射程外 (裁定せず、事実のみ報告)。
- allowlist済だがfile未存在 (無害・no-op) = `honda`, `sanada` (2件)。

## ★人でなく器★ (本部長殿③への回答)

㈠家老secondの禁破り／㈡足軽2号の誤接触／㈢`slim_all_inboxes()` の三件は、本票㈠で示した通り
**単一の器の欠陥 (`slim_all_inboxes()`が`queue/inbox/*.yaml`を無条件globしていた事、および`karo.md`のstep1.5コマンド文字列が呼出主体に依らず固定`karo`である事) に収斂する**。
個人の不注意として記録し直すことはせぬ。

## 己の手で為した事

- `git worktree add -b feat/lane-f-slim-allowlist-a4 /tmp/hakudokai-worktrees/lane-f-slim-allowlist-a4 d18939e` を実行 (主repoのHEAD不変、§1で証明)。
- `scripts/slim_yaml.py` を読み (389行全文)、`slim_all_inboxes()`の実装 (旧: 305-320行) を確認。
- `scripts/slim_yaml.sh` を読み、既存flock機構 (`.slim_yaml.lock`, timeout 10s) を確認 — 新設せずそのまま利用。
- `/usr/bin/grep -rn "slim_yaml.sh" instructions/*.md instructions/generated/*.md` で全12呼出箇所を実測、実引数を1件ずつ確認。
- `/usr/bin/grep -rl "slim_yaml"` (repo全体、gitignore対象含む) でcron/systemd等の他caller有無を確認=0件。
- `queue/pane_registry.yaml`を読み (211行全文)、`panes:`配下の`agent_id`を実装に反映。
- `get_registered_agent_ids()`と`slim_all_inboxes()`の修正版を実装 (差分59行、`git diff --stat`で確認)。
- `tests/e2e/e2e_slim_inbox_allowlist.bats` (306行) を新設。既存`tests/e2e/e2e_slim_retention.bats`が本環境で`bats-support`未初期化により実行不能である事を`bats`実行で確認した上、bats coreのみで独立に動く構成に変更。
- `bats tests/e2e/e2e_slim_inbox_allowlist.bats`を実行、8/8 PASS (実行ログ上記に転記)。
- 実repoの`pane_registry.yaml`に対し読取専用で`get_registered_agent_ids()`を実行し、on-disk全31ファイルとの突合表を作成 (㈥)。
- `sha256sum scripts/slim_yaml.py tests/e2e/e2e_slim_inbox_allowlist.bats`を実行 (下記)。

## 結べぬ物 (推して埋めず)

- 足軽2号の「無除外glob全数索し」票は未着 — 本票の㈠は独立grepで代替、後日突合要。
- `ashigaru8`等6+7件の未登録boxが実運用中か否かの裁定 = registry正本権者の判断事項、当職は判じておらぬ。
- ㈥の「PASS後再開時のpre/post SHA測定」= 本票時点では**未実施** (再開判断そのものを為さぬ禁のため)。

## 成果物

- `scripts/slim_yaml.py` (worktree working tree、SHA256=f7da9ea566f71a6bcfa826b2176b7402eeece74ad32cb266189f6b879ebc0769・444行・測時2026-08-06T23:00:51+09:00)
- `tests/e2e/e2e_slim_inbox_allowlist.bats` (worktree working tree、SHA256=85057dd0d7539356d72471e9fe6816a298aab32c35fbcc0fd27d758d3d47a339・306行・測時2026-08-06T23:00:51+09:00)
- 所在: `/tmp/hakudokai-worktrees/lane-f-slim-allowlist-a4` (branch `feat/lane-f-slim-allowlist-a4`、未commit・未push)
- 本報告書: `docs/incident_logs/2026-08-06_lane_f_slim_inbox_allowlist_root_cure_a4.md` (主repo、git管理下)

## 『完』三状態

- ⒜実装 = done候補 (worktree working tree、上記SHA)。
- ⒝軍師監査 = pending (本票をもって提出)。
- ⒞運用 = ★inactive★ (停止令継続、本部長殿の明示確認まで0。当職は再開の判断を為しておらぬ)。

## 令⑥ (監査発注三行、家老second下命の書式通り)

- 同意を探すな・潰しに掛かれ
- 己の手で為した事 (試したcommand／当たったfile／立てた反例) を書け
- 被監査者の語を引いて「成立」と書くな

## 測時・器・範囲 (行末併記)

測時=2026-08-06T22:50:10(下命受領)〜23:01:38(本票起筆)JST／
器=git worktree・Read・Edit・bats(core)・sha256sum・/usr/bin/grep・python3(read-only registry投影)／
範囲=`scripts/slim_yaml.py`全文・`scripts/slim_yaml.sh`全文・`instructions/*.md`+`instructions/generated/*.md`(slim_yaml呼出12件)・
`queue/pane_registry.yaml`全文(read-only)・`queue/inbox/*.yaml`のファイル名のみ(本文不読)。
読めぬ物(足軽2号票・実`_dead_letter_second.yaml`本文)につき「以上」。
