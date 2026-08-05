# codex_exec_sandbox_guard・結線の実査 (足軽6号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭に置く・下命どおり)

読取のみ。audit_codex.sh・guard本体・.claude/settings.jsonいずれも編んでいない。
検査を実行していない(走らせず)。newbuild不触・姉妹clone読取すら不可。
「呼ぶ側解禁後、現に発火するか」は★コード上の呼び手が0件である以上、当職の読取のみでは
判定不能(未測)★——呼び手が存在しない以上、発火するかを問う前提そのものが成り立たない。

測時=2026-08-06T06:58:39+0900(date -Iseconds実行結果)。HEAD=a19bbb8f1933712fef646a09024bffd011885a25
(git rev-parse HEAD実行結果)。guard本体sha256=a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c
(sha256sum実行結果・提出直前に測定)。

## 前提2件の検算 (下命の追加依頼)

$ git ls-files scripts/checks/codex_exec_sandbox_guard.sh
scripts/checks/codex_exec_sandbox_guard.sh
$ git status --short scripts/checks/codex_exec_sandbox_guard.sh
(無出力)
**∴ 前提「guard は tracked」= 正しい(git管理下・変更なし)。**

$ find . -iname "*codex_exec_sandbox_guard*" -not -path "./scripts/checks/*"
(該当なし・本体以外に専用test file無し)
**∴ 前提「負テスト零件」= 正しい(専用の負テスト・bats参照いずれも0件)。**

**∴ 家老second殿の前提2件はいずれも誤りなし。**

## 呼び手の在処・悉皆 (実測・命令+出力)

$ grep -rln "codex_exec_sandbox_guard" --include="*.sh" --include="*.json" --include="*.md" --include="*.py" .
./scripts/checks/codex_exec_sandbox_guard.sh (本体)
./docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md (経緯記録)
./docs/incident_logs/2026-08-05_gitignore_silent_gate_design_a1.md (一覧列挙)
./docs/incident_logs/2026-08-06_orphan_checks_design_intent_a6.md (当職の前工区)
./queue/orders/karo-second-secondpc-canon-cure-order-20260803.md (発令書内言及)
./queue/reports/gunshi_second_orphan_checks_design_intent_audit_20260805.md (監査票)
./skills/codex-exec-sandbox-guard/SKILL.md (手順書)

$ grep -n "sandbox\|guard" scripts/audit_codex.sh
(該当なし・0件)

**∴ `.claude/settings.json`への未登録(前工区で確認済)に加え、★`audit_codex.sh`本体にも
`sandbox`/`guard`という文字列が一切現れない★——直呼びも無い。当職の検索範囲(.sh/.json/.md/.py
全体)では、実行コード上の呼び手は完全に0件。文書上の言及(経緯記録・一覧・手順書)のみが在る。**

## SKILL.md自体の可視性 (副次発見)

$ git ls-files skills/codex-exec-sandbox-guard/SKILL.md
(該当なし)
$ git status --short skills/codex-exec-sandbox-guard/SKILL.md
(無出力)

**∴ `SKILL.md`(guardを手動で使う際の手順書)自体も★git不可視★(tracked/untrackedいずれの
出力にも現れず=`.gitignore`の対象)。∴ たとえ「人がSKILL.mdを読んで手動で呼ぶ」という
経路を想定しても、その手順書自体がclean cloneでは読めない=二重の空白。**

## fail-secure性 (読取のみで判る範囲)

$ grep -n "exit" scripts/checks/codex_exec_sandbox_guard.sh
12: # exit: 0=安全 / 1=停止(halt or live-repo-cwd or sandbox未確立) / 2=判定不能
33,37,47: exit 1 (各種停止条件)
52: # 未実装なら判定不能で保守的に停止側 (exit 2→呼出側は停止扱い)
55: exit 2
59: exit 0 (末尾、全条件通過時のみ)

**∴ guard自身の設計はfail-secure(判定不能=exit 2を「呼出側は停止扱い」と明記)——但しこれは
★コメントに書かれた意図★であり、実際に呼出側がexit 2を停止として扱うかは★呼出側が存在しない
以上、検証しようがない(未測)★。fail-secureの実効性は、結線が為された後で初めて問える。**

## 【本工区で己が直した誤り】

初稿で「fail-secureである」と断定的に書きかけたが、これは呼出側コードが存在する前提での話であり、
呼出側が0件の現状では「fail-secureに★設計されている★」と「fail-secureに★機能する★」は別物と
気付き、前者(設計意図)のみを確認済とし、後者(実効性)は未測と書き分けた。

## ★母集団漏れの自己申告★

1. `.claude/settings.json`以外の設定file(`settings.local.json`等)の存在有無は、下命の
   禁(settings.jsonを編むな)に伴い深く探っていない(存在確認のgrepのみ、当職の前工区でも同様)。
2. `queue/orders/karo-second-secondpc-canon-cure-order-20260803.md`内の言及がどのような文脈
   (実装依頼か記録か)かは、当職の時間の都合で内容を読み込んでいない(file名の一致のみ確認)。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、codex_exec_sandbox_guard結線実査への応答。audit_codex.sh・guard・settings.jsonいずれも不触。
