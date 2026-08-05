# git不可視・母集団を全域へ (足軽6号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭に置く)

読取のみ。.gitignore・guard・settings.jsonいずれも編んでいない。newbuild不触・姉妹clone読取すら不可。
母集団=repo全域から`queue/`・`node_modules/`・`.venv/`を除外した範囲(理由=queue/は本日別工区で
既に6953+件を測定済でありここに含めると新規signal が埋もれる為、node_modules/.venv/はOSS依存物で
当隊のcanon管理対象外の為、両方を除外し明記する)。

測時=2026-08-06T07:06:15+0900(date -Iseconds実行結果)。HEAD=61228c477791064c6ed1d2c6594f41e9aa46d5c2
(git rev-parse HEAD実行結果)。

## ★★緊急差込★★ 本工区の途中で、直前工区の前提が実行中に覆った

$ find . -iname "*codex_exec_sandbox_guard*" -not -path "./scripts/checks/*"
./tests/checks/codex_exec_sandbox_guard

$ stat -c '%y %n' tests/checks/codex_exec_sandbox_guard/
2026-08-06 07:02:03 tests/checks/codex_exec_sandbox_guard/
$ stat -c '%y %n' docs/incident_logs/2026-08-06_codex_guard_wiring_verification_a6.md
2026-08-06 06:59:12 (当職の前工区提出物のmtime)

**∴ このdirectory(+中の`smoke_test.sh`、163行)は★07:02:03に新規作成★された物であり、当職の
前工区(06:58:39測定・「負テスト零件」を確認済と報告)の★後★に現れた。当職の前回申告は
★申告時点では正確だった★(同一コマンドを今実行し直しても、この新規fileが無ければ0件のまま出る
事を確認済)——然れど★申告した直後に世界が動いた★。当職はこれを「見落とし」ではなく
「断面のずれ」として報ずる。この新規smoke_test.sh自体も`!!`(gitignore対象)である事も確認した。**

## 全域棚卸し (実測・命令+出力)

$ git status --porcelain --ignored=matching -- . | grep '^!!' | grep -v "^!! queue/" | grep -v "node_modules" | grep -v "\.venv/" | wc -l
242

### 拡張子別内訳 (実測)

| 種別 | 件数 |
|---|---|
| 実行される物(.sh/.py) | 15 |
| 手順書・設計(.md) | 35 |
| 設定(.json/.yaml/.yml) | 3 |
| その他(.log/.txt/.meta/.headers/.err/.pyc/.body/.bak*等) | 189 |

### 実行される物(.sh/.py、15件・全件列挙)

lib/tmux_send.sh / scripts/alive_to_productive_monitor_v0_2_once.sh /
scripts/design-pipeline/design_pipeline.sh / scripts/design-pipeline/extract_prototype.py /
scripts/design-pipeline/generate_mockup.py / scripts/karo_second_reception_check.sh /
scripts/karo_second_send_iincho.sh / scripts/read_pruned_archive.sh /
scripts/setup_shogun_sc.sh / scripts/setup_shogun_standard.sh / scripts/shogun_self_check.sh /
scripts/test_secondpc_monitor_v2.py / **tests/checks/codex_exec_sandbox_guard/smoke_test.sh**
(★緊急差込参照★) / tmp_secondpc_keepalive.sh / tmp_secondpc_start_formation.sh

### 手順書・設計(.md、35件・特に重いもの)

- ★`dashboard.md`★ ——艦隊中枢の運用台帳そのものが git 不可視。
- ★`instructions/karo-second.md` / `instructions/gunshi-second.md` / `instructions/karo_canon_20260709.md` /
  `instructions/gunshi_canon_20260709.md` / `instructions/shogun_canon_20260709.md` /
  `instructions/shogun_charter_v1.md`★ ——CLAUDE.md Session Startが「必読」と定める役職別
  instructions本体が git 不可視(clean cloneでは家老・軍師・将軍いずれの人格・職務憲章も読めない)。
- `skills/codex-exec-sandbox-guard/SKILL.md`(前工区の発見、本表に再掲)。
- `context/*.md`(5件)・`docs/secondpc_*.md`(7件)・`docs/audit_reports/*.md`(2件)・
  `docs/proposals/*.md`(1件)・`reports/*.md`(5件)・`shared-orders/*.md`(3件)等、多数。

### 設定(.json/.yaml、3件・全件列挙)

`.claude/settings.local.json` / `.codex/hooks.json` / `config/settings_local.yaml`
——いずれも「local」を名乗るローカル上書き設定であり、意図的にgit外である可能性が高いが、
本工区は「意図か事故か」を判じない(下命の趣旨=数を揃えるのみ)。

## a3起案(scripts/配下限定・12件)との重なりと差

a3起案の母集団(`git status --porcelain --ignored=matching -- scripts/`)は当職の実測11件
(karo_second_reception_check.shは②として本統合案から除外との明記あり、実質10件+除外1件)。
当職の全域実行される物15件のうち、a3起案の対象(scripts/配下)と重なるのは11件、
★a3起案の外(scripts/以外)にあるのは4件★=`lib/tmux_send.sh`・
`tests/checks/codex_exec_sandbox_guard/smoke_test.sh`(新規)・`tmp_secondpc_keepalive.sh`・
`tmp_secondpc_start_formation.sh`(後二者はrepo root直下)。

## 前提2件の検算 (下命の追加依頼)

$ grep -n "母集団" docs/incident_logs/2026-08-06_w_gitignore_silent_drop_consolidated_a3.md
「母集団 (足軽2号申告の再現・独立検算)」の直下コマンドが `-- scripts/` に限定
**∴ 前提「a3起案はscripts/配下のみ」= 正しい。**

$ git ls-files skills/codex-exec-sandbox-guard/
(該当なし・0件)
$ ls skills/codex-exec-sandbox-guard/
SKILL.md のみ(他fileなし)
**∴ 前提「SKILL.mdのみIGNORED」=当該skillフォルダ内では唯一のfileがSKILL.mdであり、
それが唯一ignoredである、という意味で正しい。**

## 【本工区で己が直した誤り】

上記「緊急差込」節に記載の通り、実行中に前工区の前提が時間経過で変化した事に気付き、
「見落とし」と「断面のずれ」を区別して報じた(本日確立の「食い違いは母集団の切り方/時の差の
いずれかを先に問え」を己に適用)。

## ★母集団漏れの自己申告★

1. `.pytest_cache/README.md`のような、ツールが自動生成するcache由来のfileは、意図的除外の
   候補たり得るが当職は仕分けていない(本工区は数を揃えるのみとの下命に従い、全て列挙した)。
2. `.bak*`拡張子の6件超(実際の拡張子名がタイムスタンプ付きの非標準形)は個別に開いていない。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、git不可視・全域棚卸しへの応答。.gitignore不触・実行なし。
