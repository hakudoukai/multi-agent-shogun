# 「命令は届き、手段は届かぬ」— 11 file 突合 (足軽7号・2026-08-06)

**測時** = 2026-08-06T21:59:06 **HEAD** = 7c69508 (feat/dd169-d006-conditional-exception)
**下命者** = karo-second (msg_20260806_215732_9d66f8b9)。前工区 = 同型探索本体 (`docs/incident_logs/2026-08-06_means_not_delivered_samepattern_search_a7.md`・軍師second PASS 21:51:34・karo-second 収載済 21:56)。
**器** = `GIT_OPTIONAL_LOCKS=0 git -c gc.auto=0 diff --name-status HEAD origin/main --diff-filter=A`（読みのみ・fetch/push無し）
**範囲** = 当repo現branch (`feat/dd169-d006-conditional-exception`) × `origin/main`

## ★件数の数え直し (下命附則「実行の刻に数え直し、食い違えば数え直した方を採り報せよ」への回答)★

- **11件の総数** = 当職の実測でも **11件・一致**（karo-second申告と同数）。
- **然れど ⒞ 節「disk 在・当branch 無」の副数に食い違い有り**: karo-second申告 = **4件**。当職実測 = **5件**（下記詳述）。★数え直した当職の値=5を採り報せる★（下命の原則通り）。

## 各file実測 (disk存否／git tracked／gitignore実効判定)

| # | file | disk | git ls-files (当branch) | check-ignore -q rc (0=無視/1=非無視) | 機序 |
|---|---|---|---|---|---|
| 1 | docs/08-ops/enforcement-phase2-inventory-20260721.md | 無 | 0件 | 1 (非無視・`!docs/08-ops/*.md`whitelist該当) | (c)単独 |
| 2 | instructions/archive/gunshi_canon_20260709.md | 無 | 0件 | 0 (`.gitignore:7:*`) | (a)+(c) |
| 3 | instructions/archive/karo_canon_20260709.md | 無 | 0件 | 0 (`.gitignore:7:*`) | (a)+(c) |
| 4 | instructions/archive/shogun_canon_20260709.md | 無 | 0件 | 0 (`.gitignore:7:*`) | (a)+(c) |
| 5 | instructions/gunshi-second.md | **在** | 0件 | 0 (`.gitignore:7:*`) | (a)単独 |
| 6 | instructions/karo-second.md | **在** | 0件 | 0 (`.gitignore:7:*`) | (a)単独 |
| 7 | instructions/shogun_charter_v1.md | **在** | 0件 | 0 (`.gitignore:7:*`) | (a)単独 |
| 8 | scripts/commander_send_shogun_second.sh | 無 | 0件 | 0 (`.gitignore:7:*`) | (a)+(c) |
| 9 | scripts/karo_second_send_iincho.sh | **在** | 0件 | 0 (`.gitignore:7:*`) | (a)単独 |
| 10 | skills/codex-exec-sandbox-guard/SKILL.md | **在** | 0件 | 0 (`.gitignore:7:*`) | (a)単独 |
| 11 | tests/test_commander_send_shogun_second.py | 無 | 0件 | 1 (非無視・`!tests/*.py`whitelist該当) | (c)単独 |

**check-ignore実効判定の注記**: #1・#11は`.gitignore`にwhitelist再包含規則 (`!docs/08-ops/*.md`・`!tests/*.py`) が効き、**実際には無視されていない** (`-q`のrc=1で確証)。`git check-ignore -v`の出力だけを見て「マッチした行がある=無視されている」と読むと誤る (whitelistのnegationパターンも表示されるため)。当職は`-q`のrcで実効判定した。

## ⒜ 4機序分類 (母体4機序=(a)gitignore除外/(b)repo境界/(c)branch同期/(d)概念未実装)

- **(a)単独** (disk在・gitignore実効=有・branch未到達だが実害無し=既に手元で読める) = 5件: #5 #6 #7 #9 #10
- **(a)+(c)複合** (disk無・gitignore実効=有・branch未到達=消えたら復せぬ上に、復す経路も塞がっている) = 4件: #2 #3 #4 #8
- **(c)単独** (disk無・gitignoreは実は非該当・branch未到達のみが障壁=origin/mainからの取り込みでそのまま復する) = 2件: #1 #11
- **(b)該当なし**: 11件すべて`origin/main`という同一repo内に実体が確認できる (`--diff-filter=A`の定義上、origin/mainには存在が保証される)。他repo所在の疑いを持たせる事例は今回の11件中には無い。
- **(d)該当なし**: 11件すべて「file」という具体的artifactであり、「概念/端点が未実装」型ではない。

## ⒝ 既発見との重複／新規

- **既知(重複)** = **1件**: #8 `scripts/commander_send_shogun_second.sh` — 当職の前工区 (`2026-08-06_means_not_delivered_samepattern_search_a7.md` 新規実測①) に既出。機序(c)判定・「CLAUDE.md:309が唯一の許可経路と定めるhelperがbranchによって有無が割れる」旨も前工区と一致。二重計上せず。
- **新規** = **10件**: #1〜#7・#9〜#11（前工区の`fleet-composition-manifest.yaml`とは別file、重複なし）。

## ⒞ 「disk在・当branch無」= 消えれば当branchから復せぬ (別行で数える・当職実測=5件)

★karo-second申告=4件に対し当職実測=5件。差分の原因を特定した★:

- 一致した4件: #5 instructions/gunshi-second.md／#6 instructions/karo-second.md／#7 instructions/shogun_charter_v1.md／#9 scripts/karo_second_send_iincho.sh
- **karo-second申告に無く当職実測で追加した1件**: **#10 skills/codex-exec-sandbox-guard/SKILL.md**（`ls -la`で実在確認・8バイト超の通常file・disk在×git ls-files 0件×gitignore実効=有、他4件と同一条件）。karo-second原文では#10行に「★disk 在★／★除外★」の★disk在★注記が付いているにも関わらず、末尾の「4件」という数には算入されていない可能性が高い（原文の個別注記と合計数の不一致 = 記載時の数え違いと推定、当職からは断定不可）。
- ∴ **この5件は「今この瞬間は手元にあるが、`git`上は一度も存在しなかった扱い」= 当branchのgit履歴からは復元不能**。disk上のfileが誤って削除・上書きされた場合、当branch内には復旧手段が無い（origin/mainからの取り込みのみが復旧経路だが、それは現在「要伺い」対象＝実行禁止）。

## ⒟ canon参照の有無 (CLAUDE.md／instructions/ からの名指し。docs/incident_logsは他工区の言及に過ぎずcanonに非ずと判定し除外)

| file | CLAUDE.md/instructionsからの名指し | 危険度 |
|---|---|---|
| #6 instructions/karo-second.md | **有**（CLAUDE.md「Session Start」step4本文・instructions/gunshi-second.md・instructions/maeda.md） | disk在ゆえ当面実害無いが、canonが名指す=消えれば即座にSession Start手順が破綻 |
| #7 instructions/shogun_charter_v1.md | **有**（instructions/shogun.md・および同ファイルの.bak版） | 同上 |
| #8 scripts/commander_send_shogun_second.sh | **有**（CLAUDE.md:309「唯一の許可経路」） | ★最危険★=disk無×canon名指し×git到達不能の三重。前工区で既報 |
| #1 #2 #3 #4 #5 #9 #10 #11 | 無（CLAUDE.md/instructionsからの直接名指しは未検出） | 相対的に低（ただし#10はskillとして「file名指し」でなく「directory自動検出」で読み込まれる方式のため、canon名指しの有無という判定基準自体がこのfile種には馴染まない可能性あり=判定方法の限界として明記） |

**★最も危うい (canonが名指し・かつ現在到達不能) = #8のみ (前工区既知)。#6・#7は現在disk在ゆえ「名指されて不在」の状態には未到達だが、⒞節の5件同様の潜在リスクを負う**。

## ⒠ 己の手で為した事／判らぬは判らぬまま

- **為した**: `git diff --name-status`（再実行・読取）／`git ls-files`／`git check-ignore -q`および`-v`（全11件個別）／`ls -la`（disk実在確認）／`grep -rl`（CLAUDE.md・instructions・skills配下の名指し検索、読取のみ）。fetch/ls-remote/remote show/push/checkout/cherry-pickは一切行っていない。
- **判らぬ**: karo-second申告「4件」と当職実測「5件」の差の生成過程（karo-second側の原文注記と集計数のどちらが先に書かれ、どこで齟齬が生じたか）は当職からは特定不可能。#10がgitignore以外の要因（例:別の除外規則・当職とkaro-secondのgitignore実効の測定タイミング差）で本当に「無い」扱いだった可能性も排除できていない（当職は現HEAD=7c69508時点の一回の実測のみ）。
- **未測**: 他agent inbox・他PC状態・hakudokai-dev/third_pc repo内部（範囲外・前工区から継続）。

## 結論

- 11件総数=一致（11）。
- ⒜機序分類: (a)単独5・(a)+(c)複合4・(c)単独2・(b)(d)該当なし。
- ⒝ 重複1(commander_send_shogun_second.sh)・新規10。
- ⒞「disk在・branch無」= **当職実測5件**（karo-second申告4件との差分=#10 skills/codex-exec-sandbox-guard/SKILL.mdを追加特定・原因は記載時の数え違いと推定・断定不可）。
- ⒟ canon名指し×到達不能の最危険=#8のみ（既知）。#6・#7はcanon名指し×disk在＝将来リスク予備群。

## 監査注記

暫定二者制 (軍師+Gemini。Codex leg 停止中・監査モデル gpt-5.4 暫定)。「二者PASS」を「三者PASS」と書くな。

## 破れた後 (該当なし)

本工区中、repo内fileの書換・commit・機構の新規作成は行っていない (読取・grep・git diff/ls-files/check-ignore/ls -laのみ)。
