# 足軽2号 → 家老second・軍師second: 信長SAFETY裁定(seq132707)の逐語 — 何を禁じたか

断面: 2026-08-06T10:08:38+09:00（`date -Iseconds` 実測）。HEAD=`e1bd5d7c81491e1cb25e5ca46ba4d5349fe99e31`（branch=`feat/dd169-d006-conditional-exception`）。
read-only。audit_codex.sh / audit_meta_codex.sh は一切走らせず（実行=grep/read/wc/sha256sum/date/git rev-parse/sqlite3(python3読取専用SELECTのみ・書込0)）。守本体・settings.json・.gitignoreは一切編まず。GO_RECORD未作成。hakudokai-dev不触。rcはpipeに通さず。全grepは`/usr/bin/grep`。

## 冒頭回答（結論を先に）

**問い**: 信長SAFETY裁定（2026-07-21・seq132707）が禁じたは ㈠Codex exec のみ／㈡audit_codex.sh の実行／㈢両方／㈣その他 のいずれか。

**回答**: ★事案発生当日 (2026-07-21) の一次記録★（4件・後述§1）は**悉く** ㈠**「Codex exec」を対象に明記**している（"Codex exec 全面停止"／"当PCのCodex exec実行を全面停止"）。「audit_codex.sh の実行」という語そのものを裁定の対象として明記した当日記録は**見当たらぬ**。
★但し★ 別途、後日 (2026-08-05) の1通（§2）に「audit_codex.sh は全面停止」という**異なる文言**が見つかり、これが将軍second・karo-second が引く「記録の文言」の出所と一致する。∴ **一次記録と後日の一通で文言が食い違っており申す** — 当職はこれを㈠と断じ切らず、**両方を逐語で提示し、判断は家老second・軍師second へ委ねる**（下命⒝「推すな」に従う）。

## §1 事案発生当日 (2026-07-21) の一次記録 — 4件・悉く「Codex exec」

| # | 出所 (file:line) | 逐語 | 行数/sha256 |
|---|---|---|---|
| 1 | `docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md:34-35` | 「信長へ SAFETY 即上申 → 信長 SAFETY 裁定 = Codex leg documented 扱い + ★検証済 sandbox 確立まで当PC の **Codex exec 実行**を全面停止★。」 | 60行/`a4d687d85947c69f957266ae6dfc3b945b6b730112dd8b24f4b403b8ad5d5fd0` |
| 2 | 同file `:57` | 「信長 SAFETY 裁定 (**Codex exec** 全面停止) / 全艦隊上申 seq132707/id=035e283b。」 | 同上 |
| 3 | `scripts/checks/codex_exec_sandbox_guard.sh:8-9` | 「信長 SAFETY 裁定 (2026-07-21) = 検証済 sandbox 確立まで当PC の **Codex exec** 全面停止。」 | 59行/`a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c` |
| 4 | `queue/reports/karo-second-fki-lane-a-close-setsumei-20260721.md:30` | 「信長裁定 (SAFETY): (a)承認=Codex leg documented扱い + 機構是正(検証済sandbox)確立まで当PCの**Codex exec全面停止** (a6含む新規監査も同様)」 | 62行/`f2edbcbbba391cef5e314b21da3f7447fd5ec8ebe3e924b6573961337986d9c9` |
| 5 (参考) | `skills/codex-exec-sandbox-guard/SKILL.md:40` | 「全艦隊 SAFETY 上申: seq132707/id=035e283b」（本文には対象語なし、id併記のみ） | 40行/`0a7d6ac56e32a601e024a40f905a56e0e6443b7baad36278312ac25b835e4605` |

★4件とも同日 (2026-07-21・karo-second作成)・同一事案 (Codex監査がlive repoへapply_patch書込試行) を出所とし、悉く対象語を「Codex exec」と明記。「audit_codex.sh」の語自体は#4に1回登場するが「audit_codex.sh是正(codex exec cwd+sandbox強制)」という**改修対象**としての言及であり、**禁止対象**としての用法ではない。

## §2 後日 (2026-08-05) の1通 — 「audit_codex.sh は全面停止」

- **出所**: `queue/inbox/_archive/shogun-second_pruned.yaml` id=`msg_20260805_112935_53ca2c1c` (L9947)、from=`third_pc`（本文冒頭「[委員長→将軍second]」= 原発信者は委員長、third_pc中継）、timestamp=`2026-08-05T11:29:35`、宛先=shogun-second。
  ★本fileは `queue/inbox/_archive/` = **git非追跡 (gitignore対象、working-tree限定)**。repo+branchの通常引用に当たらぬ点を明記 ([[gitignore-whitelist-silent-drop]] 型の母集団注意)。
- **逐語** (L9882、T9ゲート close の裁可文脈): 「26日で前提（Codex経路）が崩れた。理事長SAFETY裁定 seq132707 で `audit_codex.sh` は全面停止（codex exec が invoker の cwd で agentic に live repo を書換え試行する、が因）。」
- ★注意★: この一文は**2026-07-21の当日記録ではなく、9日後・別文脈 (T9三者ゲートclose裁可)** における委員長の要約引用であり、逐語部分に続けて「理由」を付す文構造 (「audit_codex.shは全面停止（codex execが〜するが因）」)。∴ 「audit_codex.sh」が主語だが、その理由として「codex exec」の挙動を挙げており、**書き手が両者を一体として述べている**とも読める。★これが㈠なのか㈢(両方が一体として禁じられた、の意)なのかは、当職の探索範囲では判じ切れぬ（㈢潰さず残す）★。

## §3 将軍second・karo-second が引く「記録の文言」の出所を辿る

- `queue/inbox/ashigaru6.yaml:1472`「将軍second の記録の文言は audit_codex.sh の実行を禁ず に御座る（codex execのみに非ず）」
- `queue/inbox/karo-second.yaml:745`「当職の記録の文言は『audit_codex.sh の実行を禁ず』に御座る（codex exec のみに非ず）」
- 両者とも**§2の同一便 (2026-08-05・委員長→将軍second経由third_pc)** を指しているとみられる（当職が探索範囲内で確認できた「audit_codex.sh は全面停止」の唯一の出所が§2の便であり、他に該当する便・fileは見当たらず＝探した範囲＝`docs/`全体・`skills/`全体・`queue/inbox/*.yaml`全体+`_archive/*.yaml`全体・`CLAUDE.md`）。
- ★重要★: **将軍second 自身が本便で「同じ記録の別の一語が正しい保証は御座らぬ・文言で決めてはなり申さぬ」と自己の記憶の信頼性に留保を付けている**（`queue/inbox/karo-second.yaml` 内、本下命と同便）。∴ §2は「一次記録」ではなく「後日の要約引用の記憶」に基づく可能性が高く、§1(当日4件)と同じ重みでは扱えない。

## §4 CLAUDE.md (守本体) — 未採用のまま

- `CLAUDE.md` に `Codex exec` / `信長SAFETY` / `seq132707` のいずれも**0件** (`/usr/bin/grep -n` 実測)。
- §1-#1の incident log 「生成物」節 (L53) が「CLAUDE.md 追記案」を DRAFT として提案しているが、**理事長GO前ゆえ未採用のまま**。∴ 守本体自体には裁定の逐語が現時点で存在しない。

## §5 ㈣ (その他/audit_gemini等への拡張) の有無

- §1の4件全てを`audit_gemini`で検索 → **0件** (`/usr/bin/grep -n "audit_gemini"` 実測)。∴ 対象がCodex以外 (Gemini leg等) に拡張された記述は見当たらず。㈣は探索範囲内では**見当たらず**。

## §6 未測 (母集団を広げた結果・㈢として残す)

- **design_decisions / project_documents (Supabase等の正本DB)**: 当職はこの系統への tool/MCP アクセスを持たぬ (ツール一覧に該当tool不在・確認済)。∴ 判じ得ぬ。karo-second・軍師second側でアクセス可能ならそちらで確認されたし。
- `/home/hakudokai/hermes-departments/honbucho/state.db` (sqlite3、read-only SELECTのみ実施) を試したが、`design_decisions`/`project_documents` に相当するtableは無く (`sessions`/`messages`等のみ)、本件とは別系統のDB (honbucho session log) と判じた。この一点のみDB接触した旨を明記する (SELECT限定・書込0・DDL0)。
- 信長本人の発言そのもの (2026-07-21当時の一次発話ログ・口頭記録) は、当職の探索範囲 (repo+当PC読める範囲) には見当たらず。§1の4件はいずれも**karo-second による記述** (5-Why報告・close報告) であり、信長本人の一人称verbatimではない。∴ §1も「信長の言葉を誰かが書き取った記録」という点では§2と同じ種類の資料であり、**唯一の違いは「当日・複数件・相互一致」対「9日後・単一件」という重みの差**であることを明記する。

## 【本工区で己が直した誤り】

無し（read-onlyゆえ直す手を持たぬ）。但し §3で将軍second/karo-second の「記録の文言」の出所を突き止め、それが§1の当日一次記録とは別種 (9日後の要約引用・将軍second自身が留保付き) である事を明らかにした。

## 【この工区と対に成る他工区】

- 本日の当職の前工区 `docs/incident_logs/2026-08-06_codex_leg_restore_conditions_a2.md` — 同じ守本体 (guard script) の逐語箇所を扱うが、問い(Codex leg復帰条件)は別。本工区はその副産物として見つけた§1の逐語を、今回の問い(禁止対象の文言)へ転用・再検証した。
- 他に同一問いの重複工区は探索範囲 (`queue/inbox/*.yaml`全体・`docs/incident_logs/`全体grep) では見当たらず。

---
生成: ashigaru2 / 2026-08-06 / read-only・逐語引用のみ・裁定・判断は行わず。
監査体制: 二者制 (軍師second + Gemini。Codex leg は本工区が扱う対象そのものであり停止中・SAFETY裁定 seq132707)。三者PASSとは書かない。

## 附記 (家老second下命による保全・scratchpad→docs移し)

写し前sha256(scratchpad)=680636673f39fa155f1a5e89e50462558545f1f652237e72a90bcea0264e6ab0（65行） / 写し後sha256(本file・移し直後・本附記追加前)=680636673f39fa155f1a5e89e50462558545f1f652237e72a90bcea0264e6ab0（同一・一致） / 移し元=`/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/441ffd60-518e-4d2d-80ec-b9f8636da2f9/scratchpad/w_ashigaru2_safety_ruling_verbatim_20260806.md`。
