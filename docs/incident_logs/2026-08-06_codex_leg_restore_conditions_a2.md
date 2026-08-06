# Codex leg 復帰条件 実測 (足軽2号、2026-08-06)

- 発令: karo-second → 足軽2号 (msg_20260806_093057_9a1d4622・2026-08-06T09:30:57)
- 提出先: karo-second + 軍師second
- 測時 (`date -Iseconds` 実行結果): 2026-08-06T09:37:18+0900
- HEAD (`git rev-parse HEAD` 実行結果): `62b0b5a9b06fac0f2e9245cd7b073e294e9deaef`

---

## 境・限界・未測 (冒頭)

- **読取のみ**。`audit_codex.sh` / `audit_meta_codex.sh` は一切走らせていない (実行=grep/read/ls/cat/git log/git show/sha256sum/date/wc のみ)。
- 守本体 (`scripts/checks/codex_exec_sandbox_guard.sh`)・`.claude/settings.json`・`.gitignore` は一切編んでいない。
- **GO_RECORD file は作成していない** (`/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record` — 実在有無を `ls` で見ただけ)。
- hakudokai-dev へは一字も書いていない。
- grep は `/usr/bin/grep` (全件) を使用。判定は終了コード (`git check-ignore -q` の exit 等) で行い、`-v` の出力有無では判じていない ([[tool-output-is-not-tool-verdict]])。
- 本測定は **当PC (second_pc) 上のファイルシステム/repo に限る**。main_pc/third_pc 側の状態は当職の権限・接続範囲外であり未測。

---

## 母集団宣言 (全文読了 or 限定読解の別を明記)

| # | path | 読解 | 行数/sha256 |
|---|---|---|---|
| 1 | `scripts/checks/codex_exec_sandbox_guard.sh` | 全文 | 59行 / `a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c` |
| 2 | `skills/codex-exec-sandbox-guard/SKILL.md` | 全文 | — |
| 3 | `docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md` | 全文 | 60行 / `a4d687d85947c69f957266ae6dfc3b945b6b730112dd8b24f4b403b8ad5d5fd0` |
| 4 | `tests/checks/codex_exec_sandbox_guard/smoke_test.sh` | 全文 | 163行 / `6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89` |
| 5 | `docs/incident_logs/2026-08-06_codex_guard_reject_side_negtest_a3.md` | 全文 | — |
| 6 | `docs/incident_logs/2026-08-06_codex_guard_wiring_adversarial_review_a1.md` | 全文 | — |
| 7 | `docs/incident_logs/2026-08-06_codex_guard_wiring_design_v3_a6.md` | 全文 | 91行 / `2722d51b6c4248693130e546a22ed7f902d8e0d835977950cd0304fd70d29c6b` |
| 8 | `scripts/audit_codex.sh` (呼び手①) | grep + 先頭60行 | — |
| 9 | `.claude/settings.json` hooks 節 | 全文 (hooks キー3件) | — |
| 10 | `git log`/`git show` (e411b0d, 32135cc, 16d18b9, 62b0b5a, 25e6ec9) | commit message + stat | — |

加えて `docs/incident_logs/2026-08-04_SECONDPC_BACKLOG.md` の B-83 行 (将軍second 自己申告=解除条件を知らぬまま裁定した例) を裏取りに参照 (限定読解)。

---

## 前提の再検証 (下命⒜「守本体の10-16行目に逐語が在る」を検めた)

karo-second 便は「守本体の 10-16行目に逐語が在り申す (当職一次実測)」と記していたが、**当職が独立に全文を読んだ所、10-16行目は逐語の条文ではない**。

```
10	#
11	# 使い方: bash scripts/checks/codex_exec_sandbox_guard.sh [intended_cwd]
12	# exit: 0=安全 (sandbox確認済で起動可) / 1=停止 (halt or live-repo-cwd or sandbox未確立) / 2=判定不能
13	# stderr に警告を出す。timeout 5 秒相当 (重い処理はしない)。
14	
15	set -uo pipefail
16	
```

これは使い方・exit code の説明であり、SAFETY 裁定の逐語ではない。**逐語が実在するのは 8-9行目 (概要) と 19-40行目 (詳細)**。∴ karo-second の行番号は誤りと判定する (咎めではなく、下命⒠の「検めよ」に忠実に応えた結果)。

---

## ⒜ 停止の出所 — 逐語 + path/id

**逐語 (`scripts/checks/codex_exec_sandbox_guard.sh` L8-9・L19-40、一字も違えず)**:

```
# 目的: audit_codex.sh / npx @openai/codex exec を「監査/read-only」目的で起動する前に呼び、
#       live repo cwd + sandbox 未確立なら停止 (fail-closed)。信長 SAFETY 裁定 (2026-07-21) =
#       検証済 sandbox 確立まで当PC の Codex exec 全面停止。
...
# --- (0) halt フラグ: 信長 SAFETY 裁定による全面停止 ---
# 検証済 sandbox 機構が確立し halt 解除されるまで、既定で停止する (fail-closed)。
#
# ★重要 (§19検分finding是正・信長 msg_20260721_223309)★:
# halt 解除は ★env 変数単独で成立させない★。env 1行での解除は、lane A v7 で撤去した
# CODEX_BYPASS_APPROVALS_SANDBOX opt-in と同型の「自己供給 bypass (改竄痕跡なし)」であり、
# F-LA-1 非拡大 fail-closed 原則に反する。∴解除は ★改竄痕跡の残る理事長GO記録file★ の
# 実在+内容検証で成立させる。
# ★GO記録file は理事長GO発令後に上位のみが配置する。agent 自己配置/自己設定 = D-lane違反★
# (推奨=root所有・agent書込不可の固定path。lane A の人間鍵配備要件と同思想)。
```

**path/id**:
- 守本体: `scripts/checks/codex_exec_sandbox_guard.sh` (L8-9・L19-40)
- 一次記録: `docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md` L34-35 「(3) 信長へ SAFETY 即上申 → 信長 SAFETY 裁定 = Codex leg documented 扱い + 検証済 sandbox 確立まで当PC の Codex exec 実行を全面停止」
- id: **seq132707** / **id=035e283b** (同ファイル L35, L57「信長 SAFETY 裁定 (Codex exec 全面停止) / 全艦隊上申 seq132707/id=035e283b」)
- 信長 msg 参照 (guard L22 に逐語引用元として明記): `msg_20260721_223309` — **本 msg 自体の実体は当職の探索範囲 (repo 内 grep) には見当たらず** (`/usr/bin/grep -rn "msg_20260721_223309"` は guard コメント自身の1件のみヒット)。∴ 「guard コメントが引用元として名指す msg」と「その msg 本体」は別工程であり、本工区では **後者は零・理由=repo内に msg 本体を保存する仕組みが無い (口頭/DB系伝達だった可能性、判じ得ぬ)**。

---

## ⒝ 解除の要件 — 条ごとの列挙 (karo-second の①②③を検めた)

**結論: 守本体のコードが明示的に検査する解除条件は ★1つだけ★** である。karo-second の「①guard結線 ②負テストPASS ③委員長殿のGO」は、**本工区の探索範囲 (guard本体・skill・原incident log・CLAUDE.md) のどこにも「解除の3条件」として明文化されている出所を見つけられなかった** — karo-second 自身の作業仮説(再構成)と判断する。

| # | karo-second の記述 | 出所の有無 | 当職の実測 |
|---|---|---|---|
| ① | guard結線 | 出所なし (明文の「解除条件」としては) | guard自体には結線状態を検査するコードは無い。後述⒞参照 |
| ② | 負テストPASS | 出所なし (同上) | 同上、guardは負テストの実行結果を検査しない |
| ③ | 委員長殿のGO | **★出所と食い違う★** | guard本体・skill・原incident log は一貫して「**理事長**GO記録file」と記す (「委員長」の語は当該3ファイルに0件、`/usr/bin/grep -c "委員長" scripts/checks/codex_exec_sandbox_guard.sh skills/codex-exec-sandbox-guard/SKILL.md docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md` は3ファイルとも0件)。CLAUDE.md 上でも「理事長」と「委員長」は別役職として明確に区別されている (例: 本ファイル冒頭 index の「Security Phase 一旦凍結」節=理事長令、Commander憲章=委員長/副委員長への上申)。∴ **③は役職名の取り違えの可能性が高い** — 判じ得ぬ点は「karo-second が別途、口頭/DB経由で委員長委任の情報を得ていないか」であり、これは当職の探索範囲外 |

**guard がコードで検査するのは唯一これ**: `GO_RECORD` file (固定path) の実在 + 期待marker文字列の内容一致 (L29-38)。①②は、この GO_RECORD が発行されるに足る「安全機構が信頼に値する状態」を作るための**工学的な前提作業**と読める (guard/skill文中に理由付けの記述はあるが、「GO発令のための必須チェックリスト」として明文で列挙された箇所は見つからず)。

---

## ⒞ 各要件の現況 (三値・誰が判ずるかを併記)

| 要件 | 現況 (三値) | 根拠 | 誰が判ずるか |
|---|---|---|---|
| ① guard結線 (`audit_codex.sh` 等が実際に guard を呼ぶ) | **㈡満たしておらぬ** | `/usr/bin/grep -n "codex_exec_sandbox_guard" scripts/audit_codex.sh scripts/audit_meta_codex.sh shim/hakudokai/hakudokai_audit_scheduler.sh` → **0件**。一方、結線の**設計 v3** (`docs/incident_logs/2026-08-06_codex_guard_wiring_design_v3_a6.md`・91行・sha256=2722d51b…) は軍師second が PASS 判定済 (commit `62b0b5a`・裁定 09:31:35・「a6 v3 91行 …PASS」)。∴ **設計は承認済・実装は未着手**という分離した状態。加えて実装の権限自体が未解決 (`2026-07-21_codex-audit-live-repo-write.md` L36「audit_codex.sh是正…は艦隊共有infraゆえ独断改修禁→信長→Commander経由で全PC横断上申(発令は上位判断待ち)」) | 実装の是非=横断発令待ち (信長/Commander経由)。実装完了の確認=当職のような read-only 実測で可能 (今回の方法で足りる) |
| ② 負テストPASS | **㈠満たした (但し範囲限定)** | `tests/checks/codex_exec_sandbox_guard/smoke_test.sh` (163行・sha256=6a624c8d…) は `git ls-files` に現れ (`git check-ignore -q` exit=1=非ignore) — 当初の「着地閉塞 (git不可視ゆえFAIL)」は commit `e411b0d` (`.gitignore` whitelist 2行追加・理事長令施行第一号・軍師second裁可) で解消済。commit `32135cc` の題「codex guard 負テスト (FAIL→PASS・着地閉塞)」がこれを裏付ける。実行結果は7/7 PASS (a3報告・halt gate=段0のみ)。**但し段1(cwd判定)/段2(sandbox種別判定) の弾く側は、GO_RECORD自己配置がD-lane違反ゆえ実行検証不能=構造的に未測のまま** (a3・a1いずれも同一限界を自己申告) | PASS/FAILの認定=軍師second (認定済)。段1/2の検証可否=設計上の限界であり、これ以上の解消には理事長GO発令後のGO_RECORD配置を要する (鶏と卵) |
| ③ 委員長殿のGO (→ 実際は理事長GO記録file) | **㈡満たしておらぬ** | `/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record` は不在。親ディレクトリ `/home/hakudokai/.config/dentalbi/` 自体が不在 (`.config` は在るが `dentalbi` 配下は無い、`ls`実測)。理事長GOがCodex leg復帰の文脈で発令された記録も、当職の grep 範囲 (`docs/incident_logs/*.md` 全体) には見当たらず (別件=gitignore whitelistの「施行第一号」はヒットしたが、これはCodex leg復帰そのものではなく負テストの着地問題への個別裁可) | 理事長本人のみ (guard本体コメントL27が明記=「GO記録fileは理事長GO発令後に上位のみが配置する。agent自己配置=D-lane違反」) |

---

## ⒟ GO_RECORD file — path と現在の有無

- path (固定): `/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record`
- 期待marker: `CODEX_EXEC_SANDBOX_GO: APPROVED`
- **現在の有無 (当PC=second_pc): ★不在★**。実測:
  ```
  $ ls -la /home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record
  ls: cannot access '...': No such file or directory
  $ ls -la /home/hakudokai/.config/dentalbi/
  ls: cannot access '...': No such file or directory
  ```
  親ディレクトリごと不在。
- guard自身のコード (L31-38) の通り、この file が無い限り halt は解除されない。

---

## ⒠ 零に理由 (「見つからなかった」と「無い」を分ける)

- **GO_RECORD file の不在**: これは「探索範囲外で見つからなかった」ではなく、**固定path・親ディレクトリごと `ls` で直接確認した実在チェックであり「(当PC上に)無い」と言い切れる**。但し「当PC(second_pc)上に無い」であって「全PCで無い」ではない — main_pc/third_pc 上の同一固定pathの状態は当職の接続範囲外であり判じ得ぬ (★仮定を避け、範囲を明記した★)。
- **guard結線の未実装**: 呼び手3ファイル全てを `/usr/bin/grep` で全文相手に検査し0件 — これは「見つからなかった」ではなく「無い」と言える (探索対象を a1/a2 の反証が確定した4呼び手全てに揃えた上での0件)。
- **「解除3条件」を明文化した出所**: これは「無い」と断定しきれない。当職の探索範囲 (guard本体・skill・原incident log・CLAUDE.md・本日のincident_logs大量ファイル) には見当たらなかったが、口頭下命・DB (design_decisions/session_minutes 等) 経由で存在する可能性は排除できず、**当職はDBアクセス権を持たぬため判じ得ぬ**。

---

## 【本工区で己が直した誤り】

- 当初、karo-second の「守本体10-16行目」をそのまま引用しかけたが、実際に該当行を `cat -n` で確認した所、使い方コメントであって逐語のSAFETY裁定ではなかった。正しい行番号 (8-9, 19-40) に訂正した上で報告した。

---

## 【この工区と対に成る他工区】

- `docs/incident_logs/2026-08-06_codex_guard_wiring_design_v3_a6.md` (足軽6号) — 条件①(guard結線)の設計側進捗そのもの。軍師second PASS済・実装未着手という当職の判定と直接対応。
- `docs/incident_logs/2026-08-06_codex_guard_wiring_adversarial_review_a1.md` (足軽1号) — 条件①の設計に対する反証。当職の「呼び手は現4箇所、結線先は監査済だが実装は0件」という結論の裏付けとして利用した。
- `docs/incident_logs/2026-08-06_codex_guard_reject_side_negtest_a3.md` (足軽3号) — 条件②(負テストPASS)そのものの実測。当職はこれを一次情報として引用した (自分では再実行していない=読取のみ下命を厳守)。
- 上記3件は「守を良くする」工区であり、当職の本工区「③GOの主体を含め、解除条件そのものの正体を測る」は**それらとは別の問い**である (探した範囲=自inbox46件・docs/incident_logs全体grep、他に同一問いの重複工区は見当たらず)。

---

## 監査体制

暫定二者制 (軍師second + Gemini。Codex leg は本工区が扱う対象そのものであり停止中・SAFETY裁定 seq132707)。三者PASSとは書かない。

---

以上、Codex leg 復帰条件の read-only 実測。裁定・実装・commit はいずれも行っていない。
