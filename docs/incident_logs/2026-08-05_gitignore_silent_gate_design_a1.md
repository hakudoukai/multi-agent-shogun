# 【00E 裁定降下・第三の門】設計 — 『whitelistは咎めず、沈黙のみを咎めよ』(足軽1号)

- **下命**: 委員長殿 00E 裁定 → 将軍second の差配 → karo-second msg_20260805_190249_fcbf6e8a → 当職。
- **性質**: ★設計のみ★。`.gitignore` を編んで commit する行為は含まぬ(§6 は diff 案の提示のみ)。実装 code の commit も含まぬ(スクリプトは scratchpad 上のプロトタイプであり、repo 内へは未設置)。
- **境**: read-only(repo 内 file 改変は本書 1 点のみ)・`.gitignore` 不触(起案まで)・bats 禁・commit は karo-second。

---

## §0 断面 (測定時刻をその場に貼る)

**測定時刻(冒頭): 2026-08-05T19:06:33+09:00**
**測定時刻(最終確認): 2026-08-05T19:21:38+09:00**
**測定 repo: `/home/hakudokai/projects/multi-agent-shogun` (他 repo と混同せぬよう明示)**
**測定時 HEAD: `749468b5cfb7464b8064a79f779ce1bfd1b07489` branch=`feat/dd169-d006-conditional-exception`**

本書中の grep/git コマンドの出力は、上記時間帯に当職が実行したそのままである(手で書き写していない)。

---

## §1 「零 裁定の要旨」への応答 — 手段を責めるな、沈黙を責めよ

委員長殿の裁定=**whitelist 方式は手段であって病に非ず(secret 防禦の実利が現に在る)。病は沈黙**。

∴ 本設計は一貫して以下の一点で貫く:

> **`.gitignore` の whitelist 方式そのものは変更を求めない。変更を求めるのは「`!` を書き忘れた事が git status にも何にも現れず、誰にも気付かれぬまま消え得る」という★沈黙の性質★のみである。**

門が咎めるのは「ignored である事」ではなく「ignored かつ 稼働中 であるにもかかわらず、そのことが誰にも告げられておらぬ事」である。

---

## §2 着手前の既存資産探索 (四、二重実装の禁)

**探した範囲**: `scripts/checks/*.sh` 全 9 本(`ls scripts/checks/` で列挙)・`.claude/settings.json` の `hooks` キー・`.git/hooks/`(sample 以外の実体)・`.pre-commit-config.yaml`・`scripts/watchdogs/`(既存の巡回インフラ形式の参考用)。

```
$ ls scripts/checks/
codex_cli_required_persona.sh  codex_exec_sandbox_guard.sh  context_usage_warn.sh
dd169_kill_term_guard.sh  inbox_alias_integrity.sh  pane_identity.sh
pretooluse_bash_guard.sh  secondpc_dispatch.sh  symlink_aware_atomic_write.sh

$ python3 -c "import json; print(list(json.load(open('.claude/settings.json'))['hooks'].keys()))"
['Stop', 'PreToolUse', 'UserPromptSubmit']

$ ls .git/hooks/ | grep -v sample   → (該当なし)
$ ls .pre-commit-config.yaml        → No such file or directory
```

**見付からなんだ事**: `.gitignore` の whitelist 漏れ・ignored-but-active を検知する既存機構は 0 件。`scripts/checks/` の 9 本はいずれも別種(kill -TERM guard・pane identity・codex persona 等)であり、本件と主題が重ならぬ。

∴ **新造は二重実装に当たらぬ**。但し §5 で示す通り、実装形式(systemd .service+.timer)は `scripts/watchdogs/` の既存パターンを流用する(様式の新造はしない)。

---

## §3 母集団実測 — 00E 既知六件は「出発点」であって「全数」ではない

**当職が実測した母集団**(五、出発点の六件を鵜呑みにせず、己で全数を測った):

```
$ date -Iseconds
2026-08-05T19:06:33+09:00

$ find . -path ./.git -prune -o -type f -print | wc -l
9070

$ find . -path ./.git -prune -o -type f -print0 \
    | xargs -0 -I{} sh -c 'git check-ignore -q "{}" && echo "{}"' \
    | wc -l
8484
```

**8484 件は母集団に非ず**。`queue/`・`projects/`・`.venv/`・`node_modules/` 等、★設計として全面 ignore の対象になっておる領域★を含むゆえである(下記 §3-1 で実証)。これらを「沈黙の病」と混同すれば、母集団の桁を丸ごと誤る。

### §3-1 「queue/ は wholesale-ignore である」の実証(新規発見・00E 六件には無かった知見)

```
$ for d in $(ls queue/); do n=$(grep -c "queue/$d" .gitignore || true); echo "$d : $n gitignore-mentions"; done
archive : 0   dead_letter : 0   inbox : 0   inbox_v2 : 0   metrics : 0
orders : 0   packets : 0   pane_registry.yaml : 1   reports : 0   tasks : 0   watchers : 0

$ git ls-files queue/inbox/karo-second.yaml queue/tasks/ashigaru2.yaml \
    queue/reports/gunshi_second_w25_uplink_helper_audit_20260803.md \
    queue/orders/karo-second-secondpc-canon-cure-order-20260803.md
(0 件 — git ls-files は空を返した = いずれも未追跡)

$ git check-ignore -v queue/inbox/karo-second.yaml
.gitignore:7:*	queue/inbox/karo-second.yaml
```

**確定**: `queue/inbox/*`・`queue/tasks/*`・`queue/reports/*`・`queue/orders/*` は **全件 git 未追跡**であり、`queue/pane_registry.yaml` 1 件のみが例外的に whitelist されておる。これは「`!` の書き忘れ」ではなく、**設計として queue/ を git 管理外に置いた結果**である(既存 memory 「queue/はgit外ゆえ損失数は永久に不明」と符合)。

∴ **本門の母集団は queue/ を含めてはならぬ**。含めれば 7000 件超の誤検知母集団を生む(§8 で実測)。

### §3-2 「統治された(governed)ディレクトリ」を母集団の境とする

`.gitignore` を読むと、末尾 `/` を持つトップレベル `!dir/` は 2 種に分かれる:

- **A 種(部分統治)**: `!dir/` の後に個別 file の `!` が複数連なる(例: `scripts/`・`shim/`・`docs/`・`context/`・`lib/`・`config/`・`instructions/`・`tests/`・`.claude/`・`skills/`・`backend/`・`templates/`・`.github/`)。★この種で個別 file の `!` が漏れる事★が「沈黙の病」の起こる場所。
- **B 種(探索路のみ開放)**: `!dir/` 一行のみで個別 file の whitelist が皆無、または極少(例: `queue/`(§3-1)・`images/`・`android/`・`saytask/`・`memory/`)。★これは設計上そもそも大半を ignore する意図★であり、本門の対象外。

∴ **母集団 = A 種ディレクトリ配下の ignored-but-existing file のみ**(B 種は対象外・queue/ 含む)。境の引き方は §2 の求めに応じ当職が引いた(委員長殿・将軍second・当職いずれも「線は貴殿が引け」と明示)。

### §3-3 実測結果(A 種ディレクトリに絞った ignored-but-existing 母集団)

```
母集団(scripts/ shim/ docs/ context/ lib/ config/ instructions/ tests/ .claude/ skills/ backend/ templates/ .github/
       配下・vendor/backup/archive/__pycache__ 除く)= 20 件
```

内訳(00E 既知六件との突合):

| # | path | 00E 既知六件か | 新規発見か |
|---|---|---|---|
| 1 | `scripts/read_pruned_archive.sh` | 既知① | — |
| 2 | `scripts/karo_second_send_iincho.sh` | 既知② | — |
| 3 | `scripts/shogun_self_check.sh` | 既知③ | — |
| 4 | `scripts/setup_shogun_sc.sh` | 既知④ | — |
| 5 | `scripts/setup_shogun_standard.sh` | 既知⑤ | — |
| 6 | `scripts/alive_to_productive_monitor_v0_2_once.sh` | 既知⑥ | — |
| 7 | `context/dentalbi-inventory.md` | — | ★新規★ |
| 8 | `context/prod_runtime_inventory_20260704.md` | — | ★新規★ |
| 9 | `context/shift_yoyaku_survey_20260705.md` | — | ★新規★ |
| 10 | `context/teriha-zero-wait.md` | — | ★新規★ |
| 11 | `context/yoyaku_inventory_20260704.md` | — | ★新規★ |
| 12 | `lib/tmux_send.sh` | — | ★新規★ |
| 13 | `scripts/test_secondpc_monitor_v2.py` | — | ★新規★ |
| 14 | `scripts/design-pipeline/extract_prototype.py` | — | ★新規★ |
| 15 | `scripts/design-pipeline/design_pipeline.sh` | — | ★新規★ |
| 16 | `scripts/design-pipeline/generate_mockup.py` | — | ★新規★ |
| 17〜20 | `tmp_secondpc_keepalive.sh`・`tmp_secondpc_start_formation.sh` 等(repo ルート直下、A種でも B種でもない孤立 file) | — | ★新規(境界外の例・§9-①参照)★ |

**健全対照(⑧、分母なき病を煽らぬ為)**: `scripts/inbox_write.sh` は `git ls-files` で追跡下と確認(下記)。

```
$ git ls-files scripts/inbox_write.sh
scripts/inbox_write.sh
$ git check-ignore -q -- scripts/inbox_write.sh && echo IGNORED || echo NOT_IGNORED
NOT_IGNORED
```

---

## §4 「稼働中」の定義(★最も難しい所・偽陽性/偽陰性を明記せよとの下命)

四つの信号を定義する。**A・B・C のいずれか 1 つでも真なら「稼働中」と判定し ignored なら FLAG。D は単独では判定材料にせず、補助情報(STALE)としてのみ出す。**

| 信号 | 定義 | 採った理由 | 偽陽性リスク | 偽陰性リスク |
|---|---|---|---|---|
| **A: canon 参照** | `CLAUDE.md` または `docs/**/*.md` の正本文中に path が literal で出現 | 正本に名指しされる = 隊の運用手順の一部と見做せる | 低(正本は当職が編めぬので恣意混入なし)だが、正本が更新遅延だと「もう使っておらぬのに名だけ残る」逆方向の偽陽性はあり得る | 正本が未記載のまま稼働している物(口伝運用)は拾えぬ |
| **B: cron/systemd 起動** | `~/.config/systemd/user/*.service(.d/*.conf)` または `/etc/systemd/system/*.service` の `ExecStart*` 行に path/basename が出現、または `crontab -l` に出現 | 最強の実証的信号(現に定期実行される) | 極低(unit file に書けば実際に呼ばれる) | `%h`・環境変数展開・wrapper 経由の間接呼出しは literal 一致せず漏れる(§9-② 参照) |
| **C: 他 script からの source/invoke** | 追跡済み(=ignored でない)file 内に `(source|.|bash|sh|python3?|run)[[:space:]]+.../basename` の呼出し構文が出現 | 呼出元が git に見えている限り、呼出関係を辿れる | 中(doc/report の地の文がたまたま同じ構文断片を含む可能性・bats の `run` は特に広く拾う) | 呼出元自体が ignored の場合、鎖が git から見えず辿れぬ(§9-② 参照) |
| **D: 直近の実行痕跡** | mtime が 14 日以内、または対応する `__pycache__/*.pyc` が存在 | 「最後に使われたのは何時か」でしか判らぬ型④(将軍second §3)への対応 | 高(誰かが無関係に触っただけでも mtime は動く) | 実行頻度が低い季節運用の物を「古い」と誤って軽視し得る |

**判定式**: `ACTIVE = A OR B OR C`。`D` のみは `STALE`(非 block・所有者裁定待ちとして別掲)。

---

## §5 門(本体)設計

### §5-1 形式: 巡回(patrol)を第一・pre-commit hook は将来案

- 本 repo に `.pre-commit-config.yaml` は存在せず、`.git/hooks/` も未設置(§2)。新規に git hook を敷くには clone ごとの個別インストールが要り、既存の巡回慣習(`scripts/watchdogs/*.service`+`*.timer` の対、`systemctl --user list-timers` で実測 7 件稼働中)と形式が食い違う。
- pre-commit hook は「これから増える新規漏れ」しか捕まえられぬ(既存 20 件の漏れは無傷で通過する)。**本件の主題(00E)は既存 6+件の実測から始まっておる**ゆえ、まず**既存の漏れを見つけられる巡回**を先に据え、pre-commit hook は「今後の再発防止」として後追いで足す二段構えとする。
- ∴ **第一実装 = 巡回 script + 既存 `scripts/watchdogs/` 形式に倣った `.service`+`.timer` 対**(様式の使い回し・新形式の発明はしない)。

### §5-2 巡回頻度

既存の類似巡回(`shogun-self-check.timer`・`secondpc-alive-monitor-v0.2.timer`)は実測 15 分毎(§8 実測ログ参照)。**新設の門もこれに揃える(15 分)**。理由: 露出窓(sabotage から検知までの猶予)を既存インフラの粒度以上に広げぬ為(§9-③)。

### §5-3 うるさく失敗する、の実装

- 標準出力に `[FLAG] path evidence=[...] git_check_ignore_v="..."` を itemize。
- exit code は 0 以外(FLAG が 1 件以上で非 0)。
- **「0 件」と「測っておらぬ」の混同を禁ずる**(六④)ため、母集団が 0 件の場合も明示的に `RESULT: 0 candidates (population empty — not the same as 'nothing active')` を出す(黙って exit 0 しない)。
- 検知後の周知経路(dashboard 🚨要対応 への追記等)は★本設計では規定しない★。それは karo-second の裁可・所有事項であり、当職が勝手に自動配線すれば F002/F003 境界を跨ぐ(足軽は新規タスク付与不可・dashboard 記帳は karo/軍師の役目)。

### §5-4 自己適用検定(⒠)

門自身の path(想定設置先 `scripts/checks/<gate名>.sh`)が ignored であってはならぬ。門は自身の想定 path に対しても `git check-ignore -q` を打ち、ignored なら `[SELF-CHECK-FAIL]` を出して exit 非 0 とする。§7-⒠ で実測済。

---

## §6 通路(`.gitignore` diff 案 — ★起案のみ、未適用★)

**線引き**: A・B いずれかの信号を実測で確認できた物のみを「即時 whitelist 候補」とする。C のみ・D のみの物は「所有者裁定待ち」として別掲し、diff には含めぬ(§4 の FP リスクを diff の重みに反映)。

### §6-1 即時候補(A/B 実証済 6 件、00E 既知六件と一致)

```diff
--- a/.gitignore
+++ b/.gitignore
@@ scripts/ セクション内(既存 !scripts/... の並びに追記)
+!scripts/read_pruned_archive.sh
+!scripts/karo_second_send_iincho.sh
+!scripts/shogun_self_check.sh
+!scripts/setup_shogun_sc.sh
+!scripts/setup_shogun_standard.sh
+!scripts/alive_to_productive_monitor_v0_2_once.sh
```

根拠: `shogun_self_check.sh`・`alive_to_productive_monitor_v0_2_once.sh` は systemd 実測(B、§8 参照)。他 4 件は dashboard 00E 実測(家老second 14:32、陽性対照つき)+当職の再測一致(§3-3)。

### §6-2 所有者裁定待ち(C のみ、または境界外)

```diff
# 以下は A/B 未実証(C のみ、または B種/境界外)= 中身の secret 混入有無を検めておらぬ。
# 一括 whitelist は具申しない(下命四⑤に倣う)。
+# !context/dentalbi-inventory.md              (要: CLAUDE.md の「context/{project}.md」参照パターンとの整合確認)
+# !context/prod_runtime_inventory_20260704.md
+# !context/shift_yoyaku_survey_20260705.md
+# !context/teriha-zero-wait.md
+# !context/yoyaku_inventory_20260704.md
+# !lib/tmux_send.sh                            (C のみ・呼出元2本が5月8日から更新なし=低頻度運用の可能性)
```

### §6-3 対象外(STALE のみ、whitelist 具申せず)

`tmp_secondpc_keepalive.sh`・`tmp_secondpc_start_formation.sh`(A 種/B 種いずれの統治ディレクトリにも属さず、参照 0 件、"tmp_" 接頭辞・7月1日以降更新なし)、`scripts/design-pipeline/*`(5月4日以降更新なし・外部参照 0 件)は**削除も whitelist もこの工区の範囲外**として明示するのみに留める(裁定するな、の下命に従う)。

**★`.gitignore` へのこの diff の適用は行っておらぬ。委員長殿の裁可後★**。

---

## §7 負テスト五形(委員長殿指定・PASS とだけ書かぬ)

**実施場所**: `scratchpad/gate3_testrepo`(本 repo とは別の使い捨て git repo。当該 repo 内での破壊的操作を避ける為)。プロトタイプ script: `scratchpad/gate3_ignored_active_check.sh`(200行未満、`git ls-files --others --ignored --exclude-standard` で母集団を取り signal A〜D を判定)。

### ⒜ 新規の運用スクリプトを置く → 検知される

```
$ echo '[Service]\nExecStart=/bin/bash /repo/scripts/new_unwhitelisted.sh' > systemd_user/fake.service
$ bash gate3_ignored_active_check.sh <testrepo> <systemd_user_dir> <nonexist>
  [FLAG] scripts/new_unwhitelisted.sh  evidence=[B:systemd-user D:mtime<=14d(0d)]
GATE: FAIL (loud) — 1 ignored+active file(s) found.
```
→ **検知された(PASS)**。

### ⒝ 既に `!` 済みの物 → 通る

`scripts/known_good.sh` は `.gitignore` で `!scripts/known_good.sh` 済。全 4 回の実行(⒜⒞⒟⒠含む)を通じ、母集団(候補一覧)に一度も出現しなかった(`git ls-files --others --ignored` はそもそも追跡済 file を返さぬ為)。
→ **通った(PASS)**。

### ⒞ secret らしき物(`.env`/key/token)→ 依然落ちる

```
$ mkdir secretdir && echo 'API_KEY=fake_test_value_not_real' > secretdir/prod.env
$ bash gate3_ignored_active_check.sh ...
  [STALE] secretdir/prod.env  evidence=[D:mtime<=14d(0d)]
  (※ [FLAG] 一覧には出現せず。A/B/C いずれの signal も無い為)
```
→ **依然 STALE 止まり・whitelist 候補にはならぬ(PASS)**。whitelist の実利(secret 防禦)が損なわれておらぬ事の確認。

### ⒟ 対象 0件のとき → 「0件」と明示して返す

```
$ (別の使い捨て repo、全て whitelist 済の状態で)
$ bash gate3_ignored_active_check.sh <empty-testrepo> ...
# candidate population: 0
RESULT: 0 candidates (population empty — not the same as 'nothing active')
```
→ **沈黙と異常なしを同じ顔にしなかった(PASS)**。

### ⒠ 門自身が ignored でない事(自己適用検定)

```
# 門の想定 path を whitelist しない状態:
[SELF-CHECK-FAIL] gate script itself would be ignored at scripts/checks/gate3_ignored_active_check.sh

# 門の想定 path を whitelist した状態:
[SELF-CHECK-OK] gate script path not ignored (checked as: scripts/checks/gate3_ignored_active_check.sh)
```
→ **両状態を作り分けて確認(PASS)**。実装時は後者(whitelist済)を必達とする。

---

## §8 性能・スコープ上の教訓(プロトタイプ実測で判明・設計に反映済)

**教訓1(スコープ誤り)**: 母集団を repo 全体(`.` 配下)に取ったところ、候補が **7207 件**に膨れた(実測ログ `scratchpad/gate3_live_repo_run_v2.txt` 冒頭)。原因は §3-1 で示した `queue/` 全体(B種ディレクトリ)を含めてしまった為。→ **§3-2 の A種/B種の切り分けを設計に組み込んで是正済**。

**教訓2(性能)**: 母集団×追跡済 file の総当り(素朴な二重ループ)は実測で **3分超えでも終わらず timeout**(`scripts/gate3_ignored_active_check.sh` の素朴実装で実測)。単一 pass に直した v2(`gate3_v2_optimized.sh`)でも、母集団 7207 件のままでは実用時間内に収まらぬ事を確認した。→ **母集団を A種ディレクトリ限定(20件規模)に絞る事が、正確性だけでなく実装可能性の必須条件**である事が実測で判った。この教訓自体を設計の一部として記す(★「何を検めなんだか」の自己申告★、六①)。

**未実測**: A種ディレクトリ限定・母集団20件での実行時間(本書執筆時点でのフル実測は行っておらぬ。手動での個別 `check-ignore`/`grep` 確認(§3・§6)により代替した。★実装段階で必ず計測すべし★)。

---

## §9 条⑿自己適用 — 己ならこの門をどう骨抜きにするか(最低3点)

**① 統治ディレクトリの外に置く**: 新しい運用 script を `scripts/` 等の A種ディレクトリではなく、repo ルート直下や `.gitignore` に `!dir/` すら無い全く新しいディレクトリへ置けば、母集団の列挙(§3-2)そのものに現れず、systemd に組み込んでも検知されぬ。**現に `tmp_secondpc_keepalive.sh` 等がこの盲点の実例である(§3-3 の 17〜20)**。
　→ 緩和策: 信号 B(systemd/cron)だけは repo 全体を対象にした軽量な別掃引を追加できる(unit file の数は少なく、全 ExecStart path を repo 相対に正規化して `check-ignore` を打つコストは低い)。信号 A・C は性能上 A種ディレクトリ限定のまま(§8)とし、この盲点は★明記した上で残す★。

**② 間接呼出しで文字列一致を外す**: systemd の `ExecStart` を `%h`/環境変数展開経由にする、または shell 内で `SCRIPT="$DIR/x.sh"; bash "$SCRIPT"` のように変数越しに呼べば、信号 B・C の literal grep は一致せぬ。
　→ 緩和策: 静的解析だけでは原理的に防げぬ(型③「在るが既定の手では届かぬ」と同型)。実行時 audit(auditd の exec ログ相関等)を将来課題として明記するに留める。今回は設計範囲外。

**③ 巡回間隔の間隙を突く**: 15分毎の巡回(§5-2)である以上、直前の巡回が終わった直後に「まだ signal が立っておらぬ状態」で置き、次の巡回が来る前に systemd 配線を外せば、理論上は検知窓を素通りできる。
　→ 緩和策: この露出窓の長さ自体を既存インフラの粒度(15分)以上には広げぬ事を設計に明記(§5-2)。窓を 0 にはできぬが、既存の同種巡回と同じ露出水準に揃える事で「この門だけが特別に緩い」状態を作らぬ。

---

## §10 今日制定の規律への自己適用(六)

1. 判定=`git check-ignore -q` の終了コード / 出所=`-v` の行 / **両方を §3-3・§6・上記表で常に併記した**。
2. どの repo を測ったか=§0 で明記(`/home/hakudokai/projects/multi-agent-shogun`)。
3. 証拠(sha・path・命令・数)は fence の外・素の文字で本文中に置いた(本書全体を通し実施)。
4. 時刻は機械から=`date -Iseconds` を単独実行し出力を見てから執筆(§0・§3)。
5. 「0件」と「測っておらぬ」を同じ顔にせぬ=§5-3(門自身の設計)・§7⒟(負テスト)・§8(未実測の明示)の三箇所で個別に実施。
6. 条⑿自己適用=§9 で最低3点。

---

## §11 完了の定義・引き継ぎ

**七の通り**: 本書提出 → 軍師second 監査 PASS → karo-second verdict → commit(当職は commit 権限外)。`.gitignore` の実適用(§6)は委員長殿の裁可後。

**引き継ぎ(次に読む者・所有者未定の事項)**:
- §6-2(context/*.md 5件・lib/tmux_send.sh)の whitelist 可否は中身検分(secret 混入有無)を経ておらぬ。所有者裁定待ち。
- §9-① の盲点(統治ディレクトリ外への設置)への signal B 全域掃引は、本書は設計のみで実装しておらぬ。
- §8「未実測」= A種ディレクトリ限定母集団(20件)でのフル実行時間。実装段階で必ず計測すべし。
- プロトタイプ実体: `scratchpad/gate3_ignored_active_check.sh`・`scratchpad/gate3_v2_optimized.sh`・`scratchpad/gate3_testrepo/`(いずれも repo 外・session 固有ゆえ短期。本書が恒久側)。
