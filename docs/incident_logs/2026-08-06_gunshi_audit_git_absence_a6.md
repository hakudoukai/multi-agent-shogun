# 軍師second監査票がgitに残らぬ件・実測+設計案 (足軽6号、2026-08-06・家老second下命)

★★読取のみ(git status/git grep/du/ls実施のみ)。.gitignoreは編集していない(案のみ提示)。
commit不触。測時=2026-08-06T00:34:40+0900(date -Iseconds実行結果)。★★

## ⒜ 監査票252件の総bytes・期間 (実測・命令+出力そのまま)

$ ls queue/reports/gunshi_second_*.md | wc -l
252

$ git status --porcelain --ignored=matching queue/reports/gunshi_second_*.md | awk '{print $1}' | sort | uniq -c
    252 !!

$ du -cb queue/reports/gunshi_second_*.md | tail -1
883918	total

最古= queue/reports/gunshi_second_context_saturation_recovery_20260706.md (2026-07-06 10:10:15)
最新= queue/reports/gunshi_second_w_canon_application_procedure_audit_20260805.md (2026-08-06 00:31:13)

$ git ls-files queue/
queue/inbox/_archive/README.md
queue/pane_registry.yaml

**∴ queue/配下でgit tracked(commit可能)なのは上記2件のみ。252件の監査票は全て`!!`(完全に無視)。
家老second殿の実測と一致。**

## ⒝ git外で参照されている正本の有無 (実測・命令+出力)

$ git log --all --format="%H %s" | grep -c "queue/reports\|queue/orders\|queue/tasks"
1

$ git log --all --format="%H %s" | grep "queue/reports\|queue/orders\|queue/tasks"
f24ca2fb608c34e614ea36b5cb56360fb647cc35 fix(cmd_014): cure Phase 6 false-positive on queue/reports/*.yaml (Option C dual defense)

$ git grep -l "queue/reports/\|queue/orders/\|queue/tasks/" -- '*.md' | wc -l
97

**∴ git追跡下の.md file(CLAUDE.md/README.md/docs/audit-framework.md等)97件が、git外の
`queue/reports|orders|tasks/`配下を参照している。clean cloneした者は、これら97file中の
参照path文字列は読めるが、★参照先の実物(監査票本体)には一切到達できない★。commit message側も
1件(f24ca2f)が`queue/reports/*.yaml`を名指ししているが実体は既にgit外。**

★これは既存memory `claudemd-index-phantom-canon-paths.md`(CLAUDE.md Index+起動時必読の
docs/*正本10/11が実在せず)と★同型★——「正本のように参照されるが、参照先自体がgit外」という
構図が、CLAUDE.md本体からqueue/reports/へも及んでいる。

## ⒞ 方策案 (提示のみ・実装せず)

1. **`.gitignore`へ`!queue/reports/gunshi_second_*.md`等の否定規則を追加**——最も直接的だが、
   本日の教訓(`!docs/incident_logs/*.md`の否定規則を`-v`で誤読した事例)を踏まえ、追加後は
   必ず`git status --porcelain --ignored=matching`で実証すべき。252件+今後増える分すべてを
   救う事になり、リポジトリ容量への影響(現状883918 bytes=約863KB、監査票のみなら軽微)を要検討。
2. **監査票を`docs/incident_logs/`(既に否定規則で救われている既存dir)へ移設**——新規否定規則を
   増やさず、既存の"二重管理"回避(本日B-138周辺で確立した「行き先は既存の生きた場所へ」原則)に
   沿う。ただし`queue/reports/`という現行の参照習慣・スクリプト連携があれば移設コストが要る。
3. **監査票の要旨のみ既存の`docs/incident_logs/2026-08-04_SECONDPC_BACKLOG.md`型の集約ledgerへ
   都度追記**——本日確立した「行き先を持つ条」の方式を監査票にも適用。ただし監査票は個票として
   全文参照される用途があり、要旨化で情報が痩せる恐れ(台帳自身の§2既知の弱点)。

★当職はいずれも実装しない(委員長殿殿裁定またはkaro-second殿判断待ち)。★

## ★母集団漏れの自己申告★

1. `queue/reports/`配下の非gunshi_second系file(karo-second-*.md等、計665-252=413件)は
   同様にgit外か否かを個別確認していない(推定=同じ`.gitignore:7`の`*`規則で同様に無視される
   はずだが、実測していない)。
2. commit message検索は`git log --all --format`のgrep一致のみで、squash/rebase等で消えた
   履歴は追えていない。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、監査票git外問題への応答。飽和のまま小口で完結。
