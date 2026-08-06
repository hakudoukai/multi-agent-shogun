# 「無除外 glob」全数索し — queue/ 配下を舐める箇所の census

- 測時: 2026-08-06T22:53:33+0900 (実行の刻)
- 器: `/usr/bin/grep -r` (git grep / wrapped grep は gitignore 対象を無言で飛ばすため不使用)。python は `.glob()`/`glob.glob()`/`os.listdir()`/`os.walk()`/`.iterdir()`、bash は `for … in …/*`／`find`／`ls` を対象語として索った。
- owner: ashigaru2 (家老second 発令・current_order_9_20260806_2245_GLOB_NO_EXCLUSION_CENSUS)
- **本件は索しのみ・直しておらぬ**。除外案は §6 に書くが実装はしておらぬ。

---

## ⒞ 索いた範囲（母集団）— 先に明示

| 対象 | 実在 | 備考 |
|---|---|---|
| `scripts/` (直下 + `checks/`・`lib/`・`redundancy/`・`watchdogs/`・`archive/` を含む) | 有 | `.py`・`.sh` を対象。`*.bak*` サフィックス file と `__pycache__/*.pyc` は **母集団から除外**（実行されぬコピー・バイナリのため） |
| `shim/hakudokai/` | 有 | `.py`・`.sh`。`*.bak*` は同様に除外 |
| `skills/` | 有 | `SKILL.md` + 配下 `scripts/` |
| `watchdogs/`（発注書の記載） | **top-level には無し** — `scripts/watchdogs/` として実在（12 file：`.sh`×6・`.service`×3・`.timer`×3） | 発注書の `watchdogs/` は `scripts/watchdogs/` を指すと解し、之を索った |
| `tests/` | 有 | `.bats`・`.sh`・`.py`・`tests/specs/*.md`・`tests/fixtures/*.yaml` を含む |

★上記以外（`docs/`・`config/`・`agents/`・`backend/` 等）は **本件の母集団外**（発注書の指定外ゆえ）。

---

## ⒜ file:line ＋ pattern ＋ 除外の有無（全件）

### 【言語＝Python — `.glob()` / `os.listdir()`】

| # | file:line | 関数 | pattern（実際のコード） | 対象 dir | 除外 |
|---|---|---|---|---|---|
| 1 | `scripts/slim_yaml.py:311` | `slim_all_inboxes()` | `inbox_dir.glob('*.yaml')` | `queue/inbox/` | **無し** |
| 2 | `scripts/slim_yaml.py:108` | `slim_tasks()` | `tasks_dir.glob('*.yaml')` | `queue/tasks/` | **無し**（`stem in CANONICAL_TASKS` は「アーカイブするか否か」の後段分岐であって glob 自体の除外ではない） |
| 3 | `scripts/slim_yaml.py:164` | `slim_reports()` | `reports_dir.glob('*.yaml')` | `queue/reports/` | **部分的**（`if filepath.stem in CANONICAL_REPORTS: continue` — 特定 canonical 名のみ skip。それ以外の非canonical file は全て処理対象＝実質無除外に近い） |
| 4 | `scripts/slim_yaml.py:330` | `migration()` | `legacy_archive_dir.glob('*.yaml')` | `queue/reports/archive/` | **無し**（但し §⒠ 参照＝現在到達不能） |
| 5 | `shim/hakudokai/hakudokai_audit_misconduct.py:137` | `scan_all_reports()` | `os.listdir(reports_dir)` （+ `.yaml`/`.yml` 拡張子 filter のみ） | `queue/reports/` | **無し**（拡張子 filter のみで file 名パターンによる除外なし） |

### 【言語＝Bash — glob 展開 / for ループ】

| # | file:line | pattern（実際のコード） | 対象 dir | 除外 |
|---|---|---|---|---|
| 6 | `scripts/karo_overload_monitor.sh:317` | `for f in "$TASKS_DIR"/ashigaru*.yaml; do` | `queue/tasks/` | **明示除外は無し**。但し pattern 自体が `ashigaru*.yaml` 前置限定ゆえ、非 ashigaru 名（`_dead_letter*` 等）は構造上掬われぬ（`--exclude` ではなく prefix 限定という別の型の絞り） |
| 7 | `tests/specs/agent_selfwatch_spec.md:199` | `for f in queue/inbox/*.yaml; do c=$(awk '/read: false/{n++} END{print n+0}' "$f"); …` | `queue/inbox/` | **無し**（E2E 手順書内のコマンド例＝人 or agent が手動実行する想定の文書。実行される code そのものではないが、実行されれば `_dead_letter_second.yaml` を awk で開く形になる） |

### 【`find` — queue/ を対象にした物】

★索った範囲内で **queue/ 配下を対象にした `find` は 0 件**。
（`scripts/archive/message_delivery_v2_full_20260508/dead_letter.sh:136` に `find "$dlq_dir" …` が在るが、`dlq_dir="${DLQ_BASE}/${agent}"` であり `queue/inbox` とは別の base。かつ本 file は `scripts/archive/`＝旧実装ゆえ非稼働系と見受けた。稼働可否は未確認＝第四値として §⒠ に記す）

### 【`scripts/watchdogs/`・`skills/`】

★`scripts/watchdogs/` 全 12 file 索った結果、queue/ への言及 **0 件**。
★`skills/` 全体で `find`／`glob` は screenshot path のみ（`skills/shogun-screenshot/`）、queue/ への言及 **0 件**。

---

## 除外「有り」と判じて本表から除いた物（除外機構の型が違うため参考記載）

census の対象は「queue/ を舐める」箇所ゆえ、以下は **ディレクトリの全件列挙をしておらぬ** ため ⒜ の主表から除いた。除外の有無の判定基準を誤解なきよう併記する。

| file:line | 型 | なぜ「舐める」に該当せぬか |
|---|---|---|
| `scripts/alive_to_productive_monitor_v0_2_once.sh:61,93` | `report_dir.iterdir()` | agent 別 alias の `startswith` whitelist filter (`is_productive_artifact_for`) が掛かっており、**inclusion 側**の絞りで無条件通過ではない |
| `scripts/bulk_ack.sh` | 固定 agent 名リスト (`AGENTS="shogun karo gunshi ashigaru1 …"`) | directory glob を一切用いず、静的 whitelist の for ループ |
| `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:118` | docstring の "Allowed paths: queue/tasks/*.yaml" | 実装は `ALLOWED_PREFIXES` の `startswith` whitelist（`os.listdir` 等の列挙なし。個別 path を JSON payload から受け取り検査するのみ） |
| `tests/e2e/helpers/setup.bash:113,116` | `rm -f "$E2E_QUEUE"/queue/tasks/*.yaml` 等 | `$E2E_QUEUE` は `mktemp -d` の隔離 dir。実 repo の `queue/` ではない |
| `tests/checks/test_karo_overload_monitor.bats` の `find` | `$FAKE_TASKS_DIR`／`$BATS_TMPDIR_TEST` | 同上、隔離 fixture |
| `tests/fixtures/bloom_task_corpus.yaml:30` | `"output matches ls queue/inbox/"` | test corpus 内の**文字列データ**であり実行される command ではない |
| `scripts/checks/inbox_alias_integrity.sh`・`scripts/checks/secondpc_dispatch.sh` | 固定 path（`queue/inbox/shogun.yaml` 等の alias pair／`${TARGET}.yaml`） | directory 列挙をしておらぬ（個別 file 名を直接指す） |

---

## ⒝ 除外が無い物について — 現に掬われる file 名（file 名のみ・中身は読んでおらぬ）

★`_dead_letter_second.yaml`・legacy 3 file の中身は禁に従い読んでおらぬ。`ls` で file 名のみ列挙した。

### queue/inbox/*.yaml（表 #1・#7 が対象）— 測時 2026-08-06T22:53、全 30 件

```
_dead_letter_second.yaml   ← ★除外なしゆえ掬われる（既知3件の1つ）
_test_cap_rotation.yaml    ← ★除外なしゆえ掬われる（既知3件の1つ）
_test_w67fix.yaml          ← ★除外なしゆえ掬われる（既知3件の1つ）
ashigaru-second-1.yaml 〜 ashigaru-second-7.yaml（7件）
ashigaru1.yaml 〜 ashigaru8.yaml（8件）
fukuincho.yaml / gunshi-second.yaml / gunshi.yaml / honbucho.yaml /
karo-second.yaml / karo.yaml / maeda.yaml / senmu_codex_second.yaml /
shogun-second.yaml / shogun.yaml / takenaka.yaml / third_pc.yaml / training.yaml
```
→ 家老second 実測（`_dead_letter_second.yaml`／`_test_cap_rotation.yaml`／`_test_w67fix.yaml` の三つ）と **一致**。`_archive` は dir ゆえ `*.yaml` glob に掛からず、`*.lock` は拡張子違いゆえ同様に掛からぬ（家老second の既知記載どおり）。

### queue/tasks/*.yaml（表 #2 が対象）— 全 13 件

```
ashigaru1.yaml 〜 ashigaru8.yaml（8件）
gunshi-second.yaml / gunshi.yaml / karo-second.yaml / maeda.yaml /
rh_blocked_note_20260706.yaml
```
→ `_dead_letter` 相当・`_test_` 相当の file は **現状 0 件**（測時同上）。★但し glob 自体には除外機構が無い＝将来 同種 file が置かれれば無条件で掬われる構造ではある。

### queue/tasks/ashigaru*.yaml（表 #6 が対象・prefix 限定）— 全 8 件

```
ashigaru1.yaml 〜 ashigaru8.yaml
```
→ 上記13件から prefix 限定により絞られた結果と一致。`_dead_letter`等が仮に将来 `ashigaru_` 前置で作られれば掬われ得る（限定は "非ashigaru名を防ぐ" だけであり万能ではない）。

### queue/reports/*.yaml（表 #3・#5 が対象）— CANONICAL_REPORTS 除く全件

```
ashigaru-second-3_db560a15_task_a_cycle4_implementation_report.yaml
ashigaru1_report.yaml 〜 ashigaru8_report.yaml（7件・ashigaru3を除く note: ashigaru3のみ見当たらず）
gunshi_report.yaml
hermes_gazo_p0_onesha_771a1174_exact_sha_audit_relay_20260721.yaml
karo-second_report.yaml
karo_second_d1_spy_20260702.yaml
karo_second_inventory_20260702_1501.yaml
karo_second_r0_r1_20260702.yaml 〜 karo_second_r9_5_addendum_final_20260702.yaml（10件前後）
karo_second_stage0_20260702.yaml / karo_second_stage1_gunshi_20260702.yaml / karo_second_stageW_20260702.yaml
maeda_report.yaml
settings_local_before_commander_mapping_20260702074650.yaml
```
（`CANONICAL_REPORTS` の中身は本 census の scope 外ゆえ差引の当否は未検証＝第四値）
→ `_dead_letter` 相当・`_test_` 相当の file は **現状 0 件**。

### queue/reports/archive/*.yaml（表 #4 が対象）

★`legacy_archive_dir`（= `queue/reports/archive/`）自体が **disk 上に現存せず**。`migration()` は `exists()` check で早期 return し、本 glob は現在 **到達不能**。掬われる file 名は「0（対象dirが無いゆえ）」。

---

## ⒟ 言語別内訳

| 言語 / 機構 | 件数 | 該当 # |
|---|---|---|
| Python `.glob()` (pathlib) | 4 | #1〜#4（すべて `scripts/slim_yaml.py`） |
| Python `os.listdir()` | 1 | #5（`hakudokai_audit_misconduct.py`） |
| Bash for-loop glob 展開 (`.../*.yaml`) | 2 | #6（`karo_overload_monitor.sh`）・#7（`agent_selfwatch_spec.md` 記載の手順コマンド） |
| Bash `find` (queue/ 対象) | 0 | — |
| `scripts/watchdogs/` | 0 | — |
| `skills/` | 0 | — |

**合計＝無除外（または部分的除外に留まる）箇所 7 件**（器の数）。うち queue/inbox 直撃＝2件（#1・#7）、queue/tasks 直撃＝2件（#2・#6、うち#6は prefix限定）、queue/reports 直撃＝2件（#3・#5）、queue/reports/archive＝1件（#4・現在到達不能）。

---

## ⒠ 判らぬは判らぬまま（第四値）

1. `queue/reports/archive/`（legacy_archive_dir）が将来 復活した場合に何が掬われるかは **未検証**（現在 disk 上に存在せぬため中身を確認できず）。
2. `scripts/archive/message_delivery_v2_full_20260508/dead_letter.sh` の `find "$dlq_dir" …` が **本当に非稼働か**（どの process からも呼ばれておらぬか）は、本 census の scope（静的 grep）では確認できておらぬ。呼出元の実配線調査は別工区の要。
3. `.bak*` サフィックスの file 群（`scripts/*.bak*`・`shim/hakudokai/*.bak*`、多数）は「実行されぬコピー」と見做して母集団から除外したが、★何らかの経路（誤 chmod／誤 symlink／誤 include）で実行され得るかは **未検証**。もし実行経路が在れば本 census は不完全となる。
4. `queue/reports/*.yaml` の `CANONICAL_REPORTS` 定数の中身（`scripts/slim_yaml.py` 内で参照される list の実体）は本工区で開いておらぬ（コードを直すなの禁に従い最小限の読取に留めた）。差引後の正確な「掬われる file 名」は本表より少ない可能性がある。

---

## 【本工区で己が直した誤り】
無し（★上げ物ゆえ code は一行も直しておらぬ・禁則順守）。

## 【この工区と対に成る他工区】
`scripts/checks/` 配下に「glob 除外」を機械検査する構造は見当たらず（本 census 自体が初出）。対を成す既存工区は無い（探した範囲＝`scripts/checks/*.sh` 全件）。

## 除外案（★書いてよいが実装はしておらぬ★）
- `inbox_dir.glob('*.yaml')`（#1）に対しては `if p.stem.startswith('_'): continue` 等の prefix 除外が最小手当てとして考えられる（`_dead_letter_second`・`_test_*` は悉く `_` 前置ゆえ）。ただし `_archive` は dir ゆえ元々掛からず、既存の非 `_` 前置 canonical file には影響せぬはず——★裁定・実装は家老second の権限★。

---

## 監査発注（三行）
1. 同意を探すな・潰しに掛かれ
2. 己の手で為した事（試した command／当たった file／立てた反例）を書け
3. 被監査者の語を引いて「成立」と書くな
