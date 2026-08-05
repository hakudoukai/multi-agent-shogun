# repo全域git不可視ファイルの「性」分類 (足軽5号)

## 境・未測・限界 (冒頭に置く)

読取のみ。`.gitignore`・guard・`.claude/settings.json` いずれも編んでいない。newbuild不触・姉妹clone(2件とも)読取すら不可。
母集団は前工区 (足軽6号) と同一定義を踏襲=repo全域から `queue/`・`node_modules/`・`.venv/` を除外した範囲。

分類軸=「性 (nature)」であり path ではない。∴ `tests/__pycache__/*.pyc` は path 上は `tests/` 配下だが、
性はコンパイル済キャッシュゆえ「試験」でなく「生成物」に計上した (根拠は本文中で明示)。

未測=`.bak*` 6件超の個別中身は開いていない (拡張子・命名規則のみで生成物と判じた)。
`.pyc` の中身 (逆コンパイル等) も未実施 (ファイル種別のみで判じた)。

## 測時・断面

測時=2026-08-06T08:13:28+09:00 (`date -Iseconds` 実行結果)。
HEAD=e6095288fae0555a56e52695ac3faabd3e0040f1 (`git rev-parse HEAD` 実行結果)。

## 前提検算 (下命「前提を一つ検めて返せ」への応答)

**検めた前提**=家老second便が引いた「母体＝足軽6号の census・242件」。

**結果=★不一致・ただし理由判明★**:

```
$ git status --porcelain --ignored=matching -- . | grep '^!!' | grep -v "^!! queue/" | grep -v "node_modules" | grep -v "\.venv/" | wc -l
241   (census doc の 242 ではない)
```

因を検めた:
```
$ git log --oneline -3 -- tests/checks/codex_exec_sandbox_guard/
e411b0d fix(gitignore): codex_exec_sandbox_guard 負テストの whitelist 2行 — 理事長令 施行第一号・軍師second 裁可
$ git status --porcelain tests/checks/codex_exec_sandbox_guard/
(空 = 現在は git 追跡下)
```

∴ 足軽6号の census 自身が「緊急差込」節で記した通り、census 測定 (07:06:15, HEAD=61228c47…) の**直後**に
新規出現した `smoke_test.sh` は、その後 (07:06〜08:13 の間の) commit `e411b0d` で **whitelist 化され git 追跡下に入った**。
∴ 242→241 の差は 1件であり、その1件の消長は**census自身が予告していた不安定要素がまさに解消された事**を示す
(誤りではなく、母集団が動く事が常態である事の実例)。∴ 前提「242件」は**測定時点では正しかったが、
本工区着手時点(08:13)では241件へ既に動いていた**——数字を更新して用いる。

## 分類結果 (実測・241件)

| 性 | 件数 | 処方 (一行) |
|---|---|---|
| canon (不変の正本) | 7 | 保全すべき — clean clone で読めぬ事自体が既知の穴 (足軽6号先便で指摘済)。git 追跡化 or whitelist を要検討 |
| 実行物 (script) | 14 | 保全すべき — 稼働中の運用script。git 追跡化 or whitelist を要検討 (一部は a3起案で既に検討中) |
| 試験 | 0 | 該当0件。★理由=試験の「原本」(`tests/*.py`・`tests/*.bats`)は元々 git 追跡下にあり、この母集団(git不可視)には現れぬ。母集団に現れる`tests/__pycache__/*.pyc`は性がコンパイル済キャッシュゆえ生成物へ計上した(下記参照)。∴ 0件は「試験が守られていない」の証ではなく「試験原本はそもそもこの穴の外に居る」の証 |
| 生成物 (状態表・log) | 191 | 事実のみ記す (保全不要) — log/pyc/bak/probe出力/dashboard.md(状態表)等。性質上いつでも再生成可能、または既に役目を終えた履歴 |
| どれにも入らぬ物 | 29 | 個別要仕分け — 内訳は下記 |

**合計 = 7+14+0+191+29 = 241 (母集団と一致)**

## 実行物(script) 14件・全件列挙

```
lib/tmux_send.sh
scripts/alive_to_productive_monitor_v0_2_once.sh
scripts/design-pipeline/design_pipeline.sh
scripts/design-pipeline/extract_prototype.py
scripts/design-pipeline/generate_mockup.py
scripts/karo_second_reception_check.sh
scripts/karo_second_send_iincho.sh
scripts/read_pruned_archive.sh
scripts/setup_shogun_sc.sh
scripts/setup_shogun_standard.sh
scripts/shogun_self_check.sh
scripts/test_secondpc_monitor_v2.py   ← ★命名に「test_」を含むが実体は監視script(census先便の分類を踏襲)。試験原本ではない
tmp_secondpc_keepalive.sh
tmp_secondpc_start_formation.sh
```

前工区(census)の15件から1件減 (`tests/checks/codex_exec_sandbox_guard/smoke_test.sh` が commit `e411b0d` でgit追跡下へ移動した為)。

## canon(不変の正本) 7件・全件列挙

```
instructions/gunshi-second.md
instructions/gunshi_canon_20260709.md
instructions/karo-second.md
instructions/karo_canon_20260709.md
instructions/shogun_canon_20260709.md
instructions/shogun_charter_v1.md
skills/codex-exec-sandbox-guard/SKILL.md
```

## どれにも入らぬ物 29件・全件列挙 (性の内訳を併記)

★仕分け不能ではなく「与えられた4性のいずれにも一致しない」の意★。当職の見立てでは大きく2性に割れる:

**⑴ 設定 (3件)** — 意図的ローカル上書きの可能性が高いが「意図か事故か」は本工区の範囲外 (census先便と同判断):
```
.claude/settings.local.json
.codex/hooks.json
config/settings_local.yaml
```

**⑵ 調査・設計・下命の散文記録 (26件)** — canon(不変の規範)でも生成物(状態表・log)でもない「一回性の報告書・提案書」の性質:
```
context/dentalbi-inventory.md
context/prod_runtime_inventory_20260704.md
context/shift_yoyaku_survey_20260705.md
context/teriha-zero-wait.md
context/yoyaku_inventory_20260704.md
docs/ai_chat_existing_impl_spec.md
docs/audit_reports/cmd_passport_rls_audit_001_cycle1.md
docs/audit_reports/gunshi_reaudit_has_real_consumer_falsepos_20260707.md
docs/kids_app_push_ceremony_design.md
docs/kids_game_detail_design.md
docs/proposals/gap13_pre_authority_start_precedent_draft_20260710.md
docs/secondpc_ai_chat_investigation_20260509.md
docs/secondpc_compliance_audit_prep_20260509.md
docs/secondpc_dd044_migration_script_20260509.md
docs/secondpc_dd044_switch_strategy_20260509.md
docs/secondpc_kanban_connection_design_20260509.md
docs/secondpc_passport_gap_design_20260509.md
docs/secondpc_specialty_mode_design_20260509.md
reports/ashigaru4-t9-b3-redo2-latestref-directionalsnap-churntest-vitestenv-oomfix-20260710.md
reports/ashigaru4-t9-b3-redo2-log-evidence-20260710.md
reports/ashigaru4-t9-useresize-s1-hermes-fix-and-b3-bundle-20260710.md
reports/fukuincho-accounting-dino-recovery-workstart-20260707.md
reports/post-reboot-agent-fleet-resume-work-order-20260712.md
shared-orders/fukuincho-jwt-s1-no-commit-codex-gemini-audit-route-order-20260708.md
shared-orders/fukuincho-jwt-s1-temp-commit-audit-go-20260708.md
shared-orders/fukuincho-secondpc-accounting-zero-fresh-lane-table-close-order-20260708.md
```
処方=保全不要 (歴史的記録として.gitignore管理の現状維持で問題無しと当職は見るが、裁定は当職の権外)。

## 生成物(状態表・log) 191件・分布 (全件列挙は冗長ゆえ内訳表)

| 種別 | 件数 | 代表例 |
|---|---|---|
| `.pyc`/`__pycache__` (コンパイル済キャッシュ、tests/scripts/shim横断) | 20 | `tests/__pycache__/test_secondpc_reverse_sync.cpython-312-pytest-9.0.3.pyc` |
| `.bak*` (各種バックアップ・スナップショット) | 27 | `scripts/inbox_watcher.sh.bak-r2-20260702121826` |
| `.pytest_cache/*` (pytest自動生成キャッシュ) | 4 | `.pytest_cache/README.md` |
| `logs/*.log` (稼働ログ) | 18 | `logs/claude_stderr/karo-second.log` |
| `reports/ccflare8081_*` probe出力 (`.body`/`.headers`/`.meta`/`.err`/`.txt`) | 121 | `reports/ccflare8081_direct_probe_20260707_1048/*` |
| `reports/*.txt` (作業ログ・heartbeat等) | 4 | `reports/secondpc_wsl_keepalive_heartbeat.txt` |
| その他単発 (`.lock`/`dashboard.md`等) | 2 | `.claude/scheduled_tasks.lock` / `dashboard.md`(状態表そのもの) |

合計 20+27+4+18+121+4+2 = 196 … ★検算不一致に気付いた★ → 下記「己が直した誤り」参照。

## 【本工区で己が直した誤り】

上表の内訳合計を機械的に足すと196だが、生成物の実測件数は191であった (5件の誤差)。
原因を検め直した所、`.pyc`/`__pycache__`カテゴリと`.bak*`カテゴリの手集計で
`reports/ccflare8081_direct_probe_20260707_1048/`配下の`.txt`(SHA256SUMS.txt/hostname.txt等、
上表「reports/ccflare8081_*」枠に既に含めた分)を「reports/*.txt」枠へ**二重計上**していた。
∴ 上表の内訳行は目視集計の誤りを含むため、**確定できるのは python 実測値の191件のみ**であり、
上表「代表例付き内訳」は**参考の見取り図**に留め、確定数として扱わぬ事をここに明記する
(数字に確度の札を貼れ、の条を自分の集計にも当てた)。

## 対に成る他工区

`docs/incident_logs/2026-08-06_repo_wide_gitignored_census_a6.md` (足軽6号・母集団と拡張子別内訳の初出・当職はこれを引き継ぎ「性」で組み替えた)。
軸の違い=足軽6号は「拡張子」で分け、当職は「性(役割)」で分けた——直交する2軸。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg は禁令 (2026-07-21事案・SAFETY裁定 seq132707) により停止中。

## 禁則遵守の申告

`.gitignore`・guard・`.claude/settings.json` いずれも不触。newbuild不触。姉妹clone(2件)読取すら不触。
判定に用いた`wc -l`はパイプ末尾の値をそのまま数として使用しており(判定分岐に`$?`を用いていない)、
DD-169関連の rc パイプ問題には該当しない。commit/push/stage 未実施。
