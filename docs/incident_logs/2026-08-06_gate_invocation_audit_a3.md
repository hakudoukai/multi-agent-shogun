# scripts/checks/ 門の起動法監査 — 塞がっておるか・素通りし得るか（足軽3号）

下命=家老second msg_20260806_110045_51c3fc11 ③。★読取のみ・一本も走らせず・hook/guard/settings.json/.gitignore不触★。
起草時点でcontext圧により本便で一旦着地(未完了分は「未測」として明記・打ち切らず継続の要あり)。

## 境・限界（冒頭）

既存資産を先に確認した(Anti-Duplication)——`docs/incident_logs/2026-08-06_checks_firing_evidence_a6.md`(呼出元実在+発火痕跡)、
`2026-08-06_checks_scripts_positive_control_audit_a6.md`(陽性対照)、`2026-08-06_stub_bypass_inventory_a6.md`
(exported function/hash cache/sudo secure_pathの出所=audit_codex.sh向け・本件の枠組みの初出)。
本便は★これらを再導出せず引用し、scripts/checks/の実際にhook結線された2本への適用という未踏部分に絞る★。

下記の「素通りし得る」判定の多くは★regexの静的読解による論理的帰結であり、実行して確認した物ではない★
(潰しに掛かって潰れなかった、とは別種の証拠。当隊の書式に倣い明記する)。

## 表（9本、㈠塞がる／㈡素通りし得る／㈢未測）

| script | hook結線 | 判定 | 根拠 |
|---|---|---|---|
| context_usage_warn.sh | UserPromptSubmit(常時) | **①塞がっておる** | 発火条件がBashコマンド文言ではなく「UserPromptSubmitイベントの発生自体」。読取専用(session jsonl size計測のみ)でブロックもせぬ(exit 0強制)ため、迂回する動機自体が無い設計。 |
| pretooluse_bash_guard.sh | PreToolUse/Bash(常時) | **㈡素通りし得る(但し低severity)** | 下記§1。tmux検出は変数分割/wrapper scriptで回避可。但し本guardは§19原則により★絶対にブロックせぬ設計★(exit 0固定)——迂回されても失うのはstderr側チェック(pane_identity.sh発火)の1件のみ。 |
| dd169_kill_term_guard.sh | PreToolUse/Bash(常時) | **㈡素通りし得る(高severity)** | 下記§2。regexの`(^|[[:space:]])`境界条件により**絶対path指定・引用符で囲んだ間接呼出し**が検出網の外に出る。fail-secureの設計思想(不明入力=block)自体は健全だが、「不明入力」として捕捉される前に「kill系コマンドではない」と誤判定されて素通りする経路がある。 |
| codex_cli_required_persona.sh | agent_health_check.sh経由(条件付) | **㈢未測** | agent_health_check.sh自体の起動法(手動/cron/watchdog)を本便で確定できず(下記§3、時間切迫のため打切り)。 |
| pane_identity.sh | pretooluse_bash_guard.sh経由(tmux検出時のみ) | **㈡素通りし得る** | 呼び元(pretooluse_bash_guard.sh)のtmux検出自体が§1と同型の迂回を受けるため、透過的に同じ迂回が効く。 |
| codex_exec_sandbox_guard.sh | 呼出元0件(a6実測・checks_firing_evidence_a6.md L26-27) | **㈡素通りし得る(自明)** | 自動発火経路が存在しないため、通常のBash呼出しでは如何なる起動法でも到達し得ぬ(既存finding引用・再測せず)。 |
| inbox_alias_integrity.sh | 呼出元0件(同上) | **㈡素通りし得る(自明)** | 同上。 |
| secondpc_dispatch.sh | 呼出元0件(同上) | **㈡素通りし得る(自明)** | 同上。 |
| symlink_aware_atomic_write.sh | 呼出元0件(同上) | **㈡素通りし得る(自明)** | 同上。 |

## §1 pretooluse_bash_guard.sh — tmux検出の迂回（regex読解・未実行）

L47: `if printf '%s' "$COMMAND" | grep -qE '(tmux split-window|tmux kill-pane|tmux respawn-pane)'; then`
—境界アンカー無しの単純部分一致ゆえ、引用符・絶対pathでは迂回されぬ(文字列がどこかに連続して現れれば検出される)。
★然れど★変数分割では迂回し得る——例:`T=tmux; S=split-window; $T $S` はcommand文字列中に
"tmux split-window" という★連続した部分文字列★を持たぬためgrepは一致せぬ(regex読解による論理的帰結・未実行)。
或いはwrapper script化(`bash mytmux.sh`、中身にtmux split-windowを書く)でも同様に迂回し得る。
★但し★本guardは§19「hookは絶対にブロックしない」原則によりL52で常時`exit 0`——迂回の実害は
「pane_identity.shによるstderr警告が出ない」事のみで、動作自体は妨げられぬ(元々ブロックしない設計)。

## §2 dd169_kill_term_guard.sh — kill検出の迂回（regex読解・未実行、★高severity★）

境界条件`(^|[[:space:]])(kill|pkill|killall)([[:space:]]|$)`（L50・L55・L62共通の構造）は
「行頭または直前が空白」を要求する。∴ 以下の形は**この境界条件を満たさぬためL50の初回gateで
「kill系コマンドではない」と判定され即exit 0（ログ記録すら無し）**——regexの読解のみによる論理的帰結、
実行して確認してはおらぬ(D-lane相当ゆえ実行禁・本監査の縛りにも反する):

- `/bin/kill -9 <PID>` — "kill"の直前文字が"/"であり、空白でも行頭でもない
- `bash -c "kill -9 <PID>"` — "kill"の直前文字が`"`(二重引用符)であり、空白でも行頭でもない
- `env kill -9 <PID>` は★逆に検出される★（"kill"の直前が空白）——★参考として境界の効く例と効かぬ例を並記した★

∴ ★問いの核心（「正しく書かれておるか」ではなく「通さずに済む呼び方が在るか」）への答=在る★。
L69の「厳格kill -TERM単発PID許可」regexも同型の境界条件を持つゆえ、絶対path/引用符越しの
`kill -TERM <PID>`自体も同じ理由でDD-169の例外許可対象として認識され得ぬ(=許可されるべき安全な形すら
弾かれ得る、という逆方向の副作用も同時に存在する——但しこちらは「安全側の過剰検知」であり脅威ではない)。

### ★未測（時間切迫のため打切り）★

- hook timeout(dd169=5秒・pretooluse_bash_guard=10秒)超過時、Claude Code harnessがfail-open(通過)か
  fail-closed(遮断)かは本便では確定できず。公式docの参照・実測いずれも本便の時間内に行えなんだ。
  ★これは本監査の眼目(「どの起動法で素通りするか」)に直結する最重要の未測項目である★——次工区で
  優先されたし。
- 上記§2の3例(絶対path/引用符/wrapper)は★regex読解のみ★——同一shell環境内でこれらが実際に
  Claude Code hookのstdin JSON `.tool_input.command`としてどう渡るか(shellのquote展開が先か、
  hookが受け取る文字列は展開後かエスケープ保持かで結果が変わり得る)は未検証。

## §3 codex_cli_required_persona.sh の呼び元 agent_health_check.sh — 打切り(未測)

`agent_health_check.sh`自身の呼び元=`shim/hakudokai/hakudokai_watchdog.sh` / `scripts/setup_known_hosts.sh` /
`scripts/karo_second_reception_check.sh`の3件を発見したが、これらが自動起動(cron/watchdog常駐)か
手動起動のみかを本便の時間内に確定できず。∴ codex_cli_required_persona.sh / pane_identity.sh
(pretooluse_bash_guard.sh経由分を除く手動経路)の起動法は★未測のまま次工区送り★とする。

## 新たに開ける穴

1. 本便のdd169迂回3例は★regex読解のみ★であり、実際のClaude Code hook実行環境
   (stdin JSON化される際のquote/escape処理)で同じ結果になるかは検証していない——「机上の空論」で
   終わる可能性を排除できておらぬ。次工区は★実行せずに検証する設計★(例えば別環境でのpython json.dumps
   相当の読取シミュレーション)を要する。
2. §1・§2の迂回はいずれも「Bashツールの command 文字列に、検出対象の連続部分文字列/境界条件を
   満たす形で現れぬようにする」という同型の弱点であり、当職が本日先に発見した「grep shell関数の
   ignore-files解釈がgit本体より甘い」件と★同じ族の脆弱性(検出器が実際の実行系より狭い視野で
   判定している)★——両者を束ねた一般則の抽出は本便未着手。
3. hook timeout時のfail-open/fail-closed挙動が未測のまま、dd169の設計文書(L13-15コメント)は
   「対称fail-secure」を謳っているが、★timeout超過という第三の経路★がこの対称性の範囲内かどうかは
   本便では確認できておらぬ——最重要の残課題。

## 判じ難き・未測（総括）

- codex_cli_required_persona.sh / pane_identity.sh(非tmux経路)の起動条件確定=未測(§3)
- hook timeout時の挙動=未測(§2末尾)
- §1・§2の迂回例が実行環境で真に機能するかの実証=未測(実行禁の縛り下では別途安全な検証設計を要する)

## 禁則遵守の確認

一本も走らせていない(scripts/checks/配下の9本、いずれも`cat`/`Read`による読取のみ)。hook・guard・
settings.json・.gitignoreへの書込み0件。§2の3例は文字列として例示したのみで実行していない
(kill -9等の実行は理事長裁定Tier1相当・本監査の縛り双方に反するため厳に回避)。rcはpipeに通していない。

---
断面: 2026-08-06T11:33:09+0900(機械)／HEAD=`589a1e576180a5939a1203445cfa35a98a32d8f4`／
pretooluse_bash_guard.sh sha256=`a29fd99d6d514cc42005c801a4fe315f18a6c57ac5830d7418cb6e56f8e1c986`／
dd169_kill_term_guard.sh sha256=`3958f4fff3295e6398981f4e970ee7374c9db167860f7a8d7ac2cb2c1b3fa821`／
context_usage_warn.sh sha256=`6a9ecbad0e8666bbd9b382c74113dc425655e69a25f211b759b0d0dd59455c0a`／
.claude/settings.json sha256=`844c63c0d4870f48e23838e777b96b107d5820750644d8d8aab83dc1b8c90c77`。
参照=docs/incident_logs/2026-08-06_stub_bypass_inventory_a6.md／2026-08-06_checks_firing_evidence_a6.md。
提出先: 家老second + 軍師second。★本便は時間切迫により打切り・未完了項目を明記済み★。

## hook timeout 時の挙動（読解のみ・追補）

下命=家老second msg_20260806_114228_a014af32。★本節は上記§2末尾・「新たに開ける穴」3の未測項目への回答である。
読解と記録のみ・実証(hookを意図的に遅延させる等)は一切行っていない★。

### ㈠ `.claude/settings.json` の hook 定義に timeout の記載が在るか

★記載あり★。4件全て個別に明記されており、逐語は以下:

| hook | event | command | timeout(秒) |
|---|---|---|---|
| stop_hook_inbox.sh | Stop | `bash scripts/stop_hook_inbox.sh` | `60` |
| pretooluse_bash_guard.sh | PreToolUse/Bash | `scripts/checks/pretooluse_bash_guard.sh` | `10` |
| dd169_kill_term_guard.sh | PreToolUse/Bash | `bash scripts/checks/dd169_kill_term_guard.sh` | `5` |
| context_usage_warn.sh | UserPromptSubmit | `bash scripts/checks/context_usage_warn.sh` | `5` |

「記載なし」の対象は無い(4件とも数値指定あり)。

### ㈡ 既定値がどこかに書かれておるか(repo内のdoc・script・註)

★直接の答え(timeout超過時にfail-openかfail-closedかを明記した箇所)は本repo内に発見できず=判らぬ★。
近接する記述を2件発見したが、★いずれも本問いには答えていない★事を明記する:

(a) `docs/proposals/pane_identity_pretool_hook_proposal.md:90`
「3. **timeout**: 5 秒以内に hook 終了、超過時は Claude Code 側で hook を打切る」
— ★「打切る」(=killする)方法のみの言及★であり、killされた後に元のtool call自体が
進む(fail-open)のか止まる(fail-closed)のかは無記載。また本提案書自体が★未実装の提案★
(status=提案)であり、pane_identity.shは現に本形では登録されておらぬ(本監査§0表で既述の通り
pretooluse_bash_guard.sh経由の間接呼出のみ)ため、参照価値も限定的である。

(b) `docs/03-workflows/post-incident-lessons.md:32,43`
「`scripts/checks/<name>.sh` — 自動チェックスクリプト (exit 0/1/2、stderr 警告、timeout 5 秒)」
「check スクリプト | timeout 必須、失敗時素通り」
— ★これは新設checkスクリプト自身に課す内部設計原則(スクリプトが自発的に`\|\| true`等で
exit 0を返す事を義務化する規範)であり、★harness側がtimeout秒数を超過して強制killした場合に
何が起きるか(exit codeとして何を受け取るか)を定めた物ではない★。

★(a)と(b)は別の層の話である★——(a)はharnessのプロセス管理(kill方法)、(b)はスクリプト内部の
自律的な挙動(自分で自分をexit 0にする設計義務)。★両者を混同し「だからtimeout超過時もfail-open
のはずだ」と類推するのは証拠なき延長であり、本便では行わない★(下記「新たに開ける穴」2参照)。

### ㈢ 過去にtimeoutが起きた痕跡がlog等に在るか

- `logs/claude_stderr/*.log` (ashigaru-second-1~7・karo-second・shogun-second の全9件) =
  ★全て0バイト(空)★。実測: `wc -c logs/claude_stderr/*.log` → 全件`0`。timeoutに限らず
  hookのstderr出力そのものが1件も記録されていない。
- `logs/*.log`(inbox_watcher系・secondpc_receiver等)・`reports/`・`queue/`・`docs/` を母集団に
  `/usr/bin/grep -rniE "hook.*timed out|hook.*timeout.*超過|hookが.*超過|PreToolUse.*failed|hook.*打ち切られ"`
  で走査 → 0件。
- ∴ ★判定=測れぬ★(「痕跡が無い」と断ずるのではなく、★専用のhook実行ログ機構自体が存在せず、
  観測手段が無い★事が判った、という意味での測れぬ)。claude_stderr配下が全件空である事は、
  timeoutが一度も起きていない証拠にも、記録経路が機能していない証拠にも、両方読める(第四値=判定不能)。

### 三値まとめ

㈠ settings.jsonの記載 = ★判った★(有・4件逐語表つき、上記参照)
㈡ 既定値の文書化(fail-open/fail-closedの明記) = ★判らぬ★(repo内に直接の答え無し。近接記述2件は別の問いに答えている)
㈢ 過去のtimeout痕跡 = ★測れぬ★(hook専用ログ機構が皆無・既存ログは空または無関係)

### 新たに開ける穴

1. hookのtimeout超過時の挙動が本repo内の文書探索でも確定できなかった。§2末尾で指摘した
   「timeoutという第三の経路がdd169の『対称fail-secure』設計の範囲内かどうか未確認」という
   穴は、★本追補でも埋まらず、依然開いたままである事が追認された★。
2. `post-incident-lessons.md`§19.3の「timeout必須、失敗時素通り」を、harnessのtimeout-kill挙動の
   根拠として引用してしまう誤りが★次工区以降で起こり得る★(両者は別層)。本便でこの2つを明示的に
   切り離しておくこと自体が、次の読み手への予防線である。
3. `claude_stderr`配下の全9 file が0バイトである事は、★hookの標準エラー出力がそもそも記録される
   経路になっていない可能性★を示唆する。これは本問い(timeout時の挙動)とは別に、★hook実行全般の
   可観測性が薄い★という、より広い穴を開ける(次工区候補)。

### 各主張の検め直し方(一行ずつ)

- 「4hookのtimeout値(60/10/5/5秒)」→ `.claude/settings.json` の `hooks` 節を直接開き、sha256で
  断面照合の上で再確認せよ。
- 「(a)(b)は別層の話」→ 両file該当行(proposal L90 / post-incident-lessons L32,43)を並べて読み、
  「harnessのプロセスkillを語るか、スクリプト内部の自律設計を語るか」を文脈から再判定せよ。
- 「claude_stderr全9件が空」→ `wc -c logs/claude_stderr/*.log` を再実行し、0バイトのままか確認せよ
  (後日書込みが在れば前提が変わる)。
- 「timeout超過時のfail-open/fail-closedはrepo内未記載」→ 本便で用いなかった別語でのgrepを試すか、
  Claude Code公式docの正本(repo外)を委員長裁定を経て参照可能になった時点で再確認せよ
  (★実証(hookを実際に遅延させる)自体は委員長殿裁定id=785df375が定まるまで為すな★)。

---
断面(追補): 2026-08-06T11:47:38+0900(機械)／HEAD=`13f1c064c906e009d68fa780d642639b0a649d0d`／
.claude/settings.json sha256=`844c63c0d4870f48e23838e777b96b107d5820750644d8d8aab83dc1b8c90c77`(§0本文断面と同一・無変更を確認)。
禁則遵守: 読取(cat/grep/wc/sha256sum/git rev-parse/date)のみ・hook/guard/settings.json/.gitignore編集0件・
`git add -f`不使用・hookを意図的に遅延させる等の実証は一切行っていない。
提出先: 軍師second(再監査提出)。
