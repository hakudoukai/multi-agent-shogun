# canon が名指す手段の全件×実在判定 — CLAUDE.md + instructions/** + docs/** path 走査

下命=家老second msg_20260806_220233_3b6f8bae（2026-08-06T22:02:33）。読取のみ・裁定なし・是正なし。
対象file・canonへの書換は一切行っていない（新規1本 = 本票のみ）。lane（/tmp/resimg-*）不触。
remote通信（fetch/ls-remote/remote show/push）は実行していない——`origin/main`は既存の fetch 済 ref を読んだのみ（後述）。
`queue/inbox/_dead_letter_second.yaml`・`_archive/*_legacy_*` は一切触れていない（glob からも明示除外）。

測時=2026-08-06T22:07:06+09:00（`date -Iseconds`）。
git rev-parse HEAD=295f680c1c5d3b7fe94f5971cdb5f4f434a91ca3／branch=feat/dd169-d006-conditional-exception。
`git status --short --branch`実測=ahead 147・`M CLAUDE.md`（作業樹に未commitの変更が存在。本票はこの断面のCLAUDE.mdを読んだ）。
`origin/main`参照= `git for-each-ref refs/remotes/origin/main`で ★既存ローカルrefを読んだのみ★（通信なし）＝
`9b8c89b5722d6f06b985797eb619719cd16153b8`／`git log -1 --format=%cI origin/main`=2026-08-04T10:29:32+09:00
（★このrefは2日前断面であり最新のorigin/mainではない可能性がある。fetchして更新することは要伺いにつき行っていない★）。

## ⒜ 索いた鍵・母集団の作り方（例は一つも渡されなんだゆえ、当職が組んだ）

**抽出正規表現**（票に明記の義務）:
```
(?:scripts|shim|docs|skills|queue)/[A-Za-z0-9_\-./]+
```
（末尾の全角/半角句読点・引用符・★等の記号は剥がした。`{`・`*`・`」`等はこの正規表現に含めておらぬため、
テンプレ表記（例=`queue/tasks/ashigaru{N}.yaml`）はそこで途切れる——★これは当職の器の限界であり、後述⒡で自己申告する★）。

**母集団の一次走査**: `CLAUDE.md` + `instructions/**`（48file）+ `docs/**`（401file）= 450file、`find`で列挙し全文を該当正規表現で走査。
結果=総ヒット13,706／unique token 7,682。

**除外の判断（当職の裁量・射程を明記）**: このうち `docs/incident_logs/**`（11,750 hit）・`docs/codex_audits/**`（63）・
`docs/proposals/**`（11）・`docs/audit_reports/**`（4）の計11,828 hitを母集団から除外した。
理由=これらは★agentが書いた記録・監査ログ・提案書であり、canonが「使え」と命じる文ではない★
（下命⒟「言及があると命じられておるは別」に照らし、記録内でのpath引用は「命令」ではなく「引用」）。
★この除外自体が当職の判断であり、除外した1件たりとも中身までは読んでいない——次に読む者はここを覆せる★。

除外後の残母集団=1,878 hit／unique token 277（`CLAUDE.md`94・`instructions/**`1,003・`docs/`直下685・
`docs/08-ops/`63・`docs/codex_audits/`は既に除外・`docs/runbooks/`19・`docs/03-workflows/`12・`docs/proposals/`除外・
`docs/audit_reports/`除外・`docs/01-architecture/`2）。

**noise token の自己申告**=277 unique tokenのうち21件は、regexが `{`・末尾アンダースコア・glob途中で
途切れた抽出artifact（例=`docs/cmd_`／`docs/honda_`／`queue/tasks/ashigaru`〔本来`queue/tasks/ashigaru{N}.yaml`〕／
`scripts/lib_v3`〔bare dir、実ファイルは`scripts/lib_v3/inbox_path.py`等〕）であり、★単独のfile/dir名として実在判定を
下すべき対象ではない★と当職が判じた。これらは以下の集計から除外し、277−21=256を「real token」とした。

## ⒝ 実在判定（機械的・real token 256件 全件）

判定軸=①disk実在（`os.path.exists`）②当branch git追跡（`git ls-files`）③`origin/main`ツリー内
（`git ls-tree -r --name-only origin/main`・★通信なし、既存refのみ★）。

```
real_token=256
absent_all3（①②③すべて偽）=114
```

bucket別内訳（source fileの由来で分類。1 tokenが複数bucketに跨る場合は両方に計上）:
```
claude_md（CLAUDE.md自身）              : absent 5
instructions（instructions/**）          : absent 23
docs_operational_canon（01-architecture/03-workflows/05-charter/08-ops/runbooks/rules/infra配下） : absent 7
docs_proposal_or_historical（ファイル名に_design_/_draft/cmd_phase/honda_等を含む2026-05-08前後の設計提案書群） : absent 81
docs_other_toplevel（上記いずれにも属さぬdocs/直下等）: absent 21
```

## ⒟ 「命じられておる」と「言及がある」の切り分け（下命⒟直結・最重要）

`docs_proposal_or_historical`の81件は、当職が個別に文脈を確認した限り（サンプル抽出、全81件の逐語読了はしていない）、
いずれも**「〜を新設する」「〜スクリプトを作る」型の提案書・草案（`_design_2026-05-08.md`／`cmd_phase*_draft.md`／
`honda_*.md`）内の記述**であり、★現在それを使えと命じている文ではない★（例=`docs/message_delivery_v2_design_2026-05-08.md`
の`scripts/message_delivery_v2/watcher.sh`＝設計上の未来のfile名であって現存canonの呼出し先ではない）。
∴ **この81件は「commanded but absent」の主張から除外する**——命令ではなく提案の言及ゆえ。
★ただし全81件を当職が逐語で確認した訳ではない（サンプル判定）——この分類自体、次に読む者が覆し得る★。

∴ **★真に「commanded but absent」と当職が判ずる残り＝claude_md 5 + instructions 23 + docs_operational_canon 7
+ docs_other_toplevel（個別確認済み分のみ）＝下記の具体的一覧★**。

## ⒞ 具体的発見（個別に一次情報へ当たった上位案件）

### ① CLAUDE.md 自身の `files:` SSoT ブロック（CLAUDE.md:16-27・★最上位canon★）

CLAUDE.md冒頭の `files:` ブロックが宣言する11項目のうち、当職が個別実在確認した11件中★4件が disk 不在★:
```
ABSENT: queue/shogun_to_karo.yaml      (cmd_queue: 将軍→家老 commands の宣言先)
ABSENT: queue/tasks/pending.yaml       (pending_tasks: 家老管理の保留タスク の宣言先)
ABSENT: queue/ntfy_inbox.yaml          (ntfy_inbox: 副院長窓口経由 の宣言先)
ABSENT: config/projects.yaml           (config: Project list summary の宣言先)
EXISTS: queue/tasks/gunshi.yaml
EXISTS: queue/reports/gunshi_report.yaml
EXISTS: dashboard.md
（queue/tasks/ashigaru{N}.yaml / queue/reports/ashigaru{N}_report.yaml はテンプレ表記ゆえ個別解決=
  queue/tasks/ashigaru2.yaml 等は実在確認済〔本セッション内で既読〕）
```
★これは本工区の端緒（`scripts/commander_send_shogun_second.sh`不在）と★同型★で、しかも★CLAUDE.md本文
そのものの冒頭ブロック★という点で射程が広い。この4項目が実際に運用されているか（他の経路に切り替わって
いるだけで実害なしか、それとも参照時にエラーになる死んだ宣言か）は★当職には判定できぬ★——直すな指せ、ゆえここで止める。

### ② `docs/audit-framework.md`（CLAUDE.md直リンクの Third-Party Audit 正本）§15.3

`scripts/audit_verify.sh` は §15.3・§16.3 に具体的呼出し例（`bash scripts/audit_verify.sh <gunshi_report_path>`他
計4箇所）を伴って記載され、同fileの改訂履歴表（742行目）には「2026-05-05 実装済みスクリプト3本
（audit_codex.sh / audit_gemini.sh / audit_verify.sh）」と★実装済みと明記★されている。
実測=`scripts/audit_codex.sh`（存在・git追跡済）／`scripts/audit_gemini.sh`（存在・git追跡済）／
`scripts/audit_verify.sh`（★disk・当branch・origin/main いずれにも不在★）。
★CLAUDE.md自身が直接命じるのは`audit_codex.sh`と`audit_gemini.sh`のみ（348行目「標準呼出しは
scripts/audit_codex.sh / scripts/audit_gemini.sh 経由」）——`audit_verify.sh`はCLAUDE.md本文には現れず、
`docs/audit-framework.md`という一段下の正本のみが命じている★。∴ この1件は「CLAUDE.md直下」ではなく
「CLAUDE.md→正本docs/audit-framework.md→更に先」という★二段目の欠落★である。

### ③ `docs/clinic-expansion-design.md`（CLAUDE.md §17 直リンク）

同fileが命令調（「〜を自動実行」「導入完了確認スクリプト」等）で名指す6件、当職が個別実測した限り★全件 disk 不在★:
```
ABSENT: scripts/hq_remote_diagnose.sh   (211,362行=自動診断・runbookテスト対象として明記)
ABSENT: scripts/hq_audit_log.sh          (212行=全保守ログ集計)
ABSENT: scripts/setup_new_clinic.sh      (381行=Day1自動セットアップ)
ABSENT: docs/clinics/template/            (382行=各医院ディレクトリの雛形)
ABSENT: scripts/health_check_clinic.sh   (384,430行=導入完了確認)
ABSENT: docs/onboarding_checklist.md     (385行=チェックリスト実行可能版)
```
CLAUDE.mdの§17は「他院展開・リモートメンテナンス」＝★将来複数医院展開時に使う設計★であり、
現に他院展開が進行中か否かは当職の権限外・情報範囲外（判ずる権＝理事長または委員長）。
★∴ここも「命じられておるに不在」だが、「今使うべき物が壊れておる」のか「まだ使われる段階に至って
おらぬ提案」なのかは、当職の検索範囲だけでは切り分けられぬ★（③は下記⒟のdocs_proposal_or_historical
判定基準と紙一重——`clinic-expansion-design.md`自体はCLAUDE.mdから直リンクされる★現行正本★であり
`_design_2026-05-08.md`のような日付付き草案とは扱いが異なるため、当職はこちらを「commanded」側に置いた
が、この線引きの当否は次に読む者が検めよ）。

### ④ `docs/observability_coverage.md`（instructions/karo.md〔現行〕997行目 ★かつ★ 旧版karo_canon_20260709.md 1000行目、両方に存在）

現行の `instructions/karo.md`（当職確認=`git ls-files`で存在・現行家老正本、本日read-first手順で参照される file）
自身が997行目で「既存コード Boy Scout 整備…観察可能性 coverage 向上 (`docs/observability_coverage.md`)」と参照するが、
当該fileは★disk不在★。旧版`instructions/karo_canon_20260709.md`（2026-07-09付、CLAUDE.md/instructions/karo.mdの
いずれからも「読め」と参照されている形跡は当職の検索範囲内では見つからず＝★旧版残存の型②の疑いあり★）にも
同一文言が残る。★どちらが先で写されたのかは当職には不明（判らぬまま残す）★。

### ⑤ 既に自己申告済み・新規発見ではない2件（参考として併記）

- `docs/03-workflows/anti-duplication.md` 5・14行目=同file自身が「`skills/pre-build-check/SKILL.md`は
  2026-06-04時点でthird_pc上に実体不在（Commander実機検証済）」と★自ら明記★している。当職の走査でも
  当branch/disk/origin-mainいずれにも不在を確認したが、★これは新規発見ではなく、正本が既に自白済の件★。
- `docs/08-ops/pc-allocation.md` 1行目=同file自身が「編成記述は陳腐化しており作業根拠にしてはならない」と
  ★一部廃止済と自ら警告★している（`docs/rules/fleet-composition-manifest.yaml`不在を含む文脈）。同じく既知。

## ⒠ 己の手で為した事

- `find`でCLAUDE.md+instructions/**(48file)+docs/**(401file)=450fileを列挙し、python3で正規表現走査
  （抽出script・生ヒットjson・unique tokenのjsonを scratchpad へ保存、本票はその集計）。
- `docs/incident_logs/**`等4ディレクトリ11,828 hitを除外する判断を下し、残1,878 hit/277 unique tokenを確定。
- 277 unique tokenの全件に対し `os.path.exists`（disk）・`git ls-files`（当branch追跡）・
  `git ls-tree -r --name-only origin/main`（★通信なし、既存ローカルref読取のみ★）の3判定をpythonで実行、
  結果jsonをscratchpadへ保存。
- 21件をregex抽出artifact（noise）と判じ除外、根拠を個別に`grep -n`で確認（例=CLAUDE.md 18-26行目の
  `files:`ブロックで`{N}`テンプレ箇所が途切れる実物を目視）。
- `docs_proposal_or_historical`81件のsource fileの命名規則（`_design_`/`_draft`/`cmd_phase`/`honda_`等）で
  提案書と判じたが、★全81件を逐語で読んではいない（サンプル抽出による分類）★。
- 上位5案件（①CLAUDE.md files:ブロック／②audit-framework.md／③clinic-expansion-design.md／
  ④observability_coverage.md／⑤anti-duplication.md・pc-allocation.md自白分）は`grep -n`で該当行を
  個別に実読し、`ls -la`・`git ls-files`で実在有無を1件ずつ確認した。
- `sha256sum`で本票が参照した主要7fileの断面を固定
  （CLAUDE.md=5cffbfca…c53a2f57aa／docs/audit-framework.md=705209af…8173601c4／
  docs/clinic-expansion-design.md=71704a4b…1aa46b8a363／instructions/karo.md=007553dd…886f7e5a24f／
  instructions/karo_canon_20260709.md=21e256ee…d820c879e9b73a／docs/03-workflows/anti-duplication.md=
  f013fbd4…5b3244509714e8e8df8e／docs/08-ops/pc-allocation.md=6ac63721…13d5472fdf3ef）。
- `queue/inbox/ashigaru2.yaml`の本下命1件のみ、`fcntl.flock`（Editツールではなく）で`read: true`に更新した
  （id=msg_20260806_220233_3b6f8bae・更新後もmessages総数40・未読0を確認、他39件の`read`値は不変）。

## 数の扱い（先出し）

令に数の明記は無かった（母集団は当職が作れとの指示）。実行の刻（2026-08-06T22:07:06〜22:13台）に
数え直した結果を上記に記載。測時・器・範囲は各節に併記済。読めぬ物（`docs_proposal_or_historical`81件の
全文・`docs_other_toplevel`21件中②③④⑤以外の16件・`origin/main`の最新化有無）は「以上」と書かず
「未確認」と明記する（等号は用いない）。

## この工区が新たに開ける穴

1. CLAUDE.md `files:`ブロックの4件不在（①）が★実害を持つか★（他経路に切替済で無害か、それとも
   参照時に落ちる死んだ宣言か）は当職には判定できない。次に読む者が実際の呼出し元コード
   （もしあれば）を検めよ。
2. `docs_proposal_or_historical`81件は全81件を逐語で確認していない——サンプル判定に基づく分類であり、
   中に本当は「命令」文脈のものが紛れている可能性を排除できない。
3. `docs_other_toplevel`21件中、当職が個別に一次情報へ当たったのは②③④⑤(実質4件)のみで、
   残り約16-17件は未個別確認のまま「absent_real」計上にとどまる。
4. `origin/main`のローカルrefは2026-08-04T10:29:32断面であり、fetchしていないため★現在のorigin/mainより
   古い可能性がある★（要伺いにつき当職からは更新していない）。
5. `docs_proposal_or_historical`と`docs_operational_canon`の境界線（③`clinic-expansion-design.md`の扱い）は
   当職の裁量で引いたものであり、次に読む者が覆し得る。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本票（母集団=CLAUDE.md+instructions/**+docs/**のうち記録系4ディレクトリを除いた1,878 hit/277 unique
token、うち21 noise除去後256 real token、absent_all3=114）。新規判定は上記⒞の5案件個別確認分に限り、
それ以外は機械的存否判定と自己申告済みの限界表示にとどめた。是正・持ち込みは行っていない（直すな・指せ、順守）。
