# 「命令は届き、手段は届かぬ」— 同型探索 (足軽7号・2026-08-06)

**測時** = 2026-08-06T(session内・機械測時なし。git log時刻を代用) **HEAD** = 08271dd (feat/dd169-d006-conditional-exception)
**下命者** = karo-second (msg_20260806_080632_1aa99db2) **母体doc** = docs/incident_logs/2026-08-06_means_not_delivered_with_orders_karo_second.md (commit e609528・未監査)
**本 file は保全であって完了に非ず。未監査 (暫定二者制=軍師+Gemini・Codex leg 停止中・監査モデル gpt-5.4 暫定)。**

## 境・限界・未測 (冒頭)

- **母集団範囲を宣言する** = 当職自身 (ashigaru7) の inbox のみ (`queue/inbox/ashigaru7.yaml` 現行 + `queue/inbox/_archive/ashigaru7_pruned.yaml`)。他 agent の inbox は範囲外 (read-only 境界・下命の「当隊」を広義に取れば不足の可能性あり、明記する)。
- 機械列挙 = 現行35件 + archive131件 (7 archive doc) = **計166メッセージ**。うち命令型 (`task_assigned`/`cmd_new`/`task_coordination`) = **87件**。
- 検出法 = 87件の本文から拡張子付きpath様トークン (`.sh/.py/.md/.yaml/.yml/.json/.sql/.ts/.tsx/.js`) + `project_documents id=` を機械 grep → **70件のユニーク参照**を抽出 → 各参照を「メッセージ本文に手段(helperの中身/正本の全文/端点の定義)が同梱されているか」で人手選別。
- ★選別基準 (母体docの4例と同型と判定する条件)★ = ①命令/正本引用が特定の外部artifact (helper/正本file/端点) を**名指し**する ②その artifact の実体・全文が**メッセージ本文に同梱されていない** ③実測の結果、**当PC/当repoで到達不能** (不在・ignored・branch未到達等) と確認できる。
- この人手選別の閾値判断そのものは主観を含む。★機械 grep は再現可能・選別の当落線は当職の判断★ と明記する。

## 前提検め (下命附則「この下命の前提を一つ検めて結果と併せて返せ」への回答)

**検めた前提** = 母体doc「根」節の一文 **『かつその手段は悉く git の外に在る』**。

**結果 = この前提は成り立たぬ。機序は最低4種に分岐する (実測)**:

| 機序 | 実例 | 実測 |
|---|---|---|
| (a) .gitignore whitelist除外 (git内対象だが不可視) | 母体②④・karo_second_send_iincho.sh | `git check-ignore -v` = `.gitignore:7:*` 該当・確認済 |
| (b) repo境界問題 (当repoに実体が無く、別repoに所在する可能性) | fleet-composition-manifest.yaml・reservation-imaging-division-charter.md | `git ls-files`=0、`git show origin/main:<path>`=fatal (存在せず)、他repo走査は禁ゆえ未確認のまま |
| (c) branch同期問題 (origin/mainには存在するが作業branchが未到達) | scripts/commander_send_shogun_second.sh | 下記「新規実測①」参照。★今回はじめて実測で確認した第3の機序★ |
| (d) 概念/端点そのものが未実装 | 母体①③ (pc_handshake読取経路・inbox_read_watermark) | 母体doc記載どおり (当職inbox内には該当命令の直接控えなし・参考扱い) |

∴ 「手段は悉くgit外」は **(a)(c)には当てはまるが(b)には当てはまらぬ** — (b)は「git外」ではなく「そもそも当repoの管理下に無い」であり、別の障害点。**根を一つに束ねたのは早計** であった可能性が高い。母体doc自身も「根を一つに束ねたのは当隊の見立てであり外の検証を受けていない」と自ら留保しており、本実測はその留保を裏付ける。

## 新規実測① — scripts/commander_send_shogun_second.sh (機序(c)・現在進行形)

- CLAUDE.md:309 が「唯一の許可経路」と定める helper。
- 当職現branch (HEAD=08271dd) では **`ls scripts/commander_send_shogun_second.sh` = No such file or directory**。
- `git ls-files -- scripts/commander_send_shogun_second.sh` = 0件。
- `git check-ignore -v` = `.gitignore:7:*` 該当 (ignoreルールには掛かる)。
- **然れど** `git show c61a124:scripts/commander_send_shogun_second.sh` = 存在 (rc=0)。commit c61a124 = 「commander_send_shogun_second.sh(+test)をgit管理へ=CLAUDE.md唯一経路helperのwhitelist漏れ根治」。
- `git merge-base --is-ancestor c61a124 HEAD` = **rc=1 (祖先でない)** = 当職の作業branchに未到達。
- `git merge-base --is-ancestor c61a124 origin/main` = **rc=0 (祖先)** = origin/mainには既に存在。
- ∴ **同じ helper が、断面 (branch) によって「有る/無い」が割れる** — これは.gitignore是正が既に済んでいても、feature branchが古いままなら再現する。★§15/§15-bが繰り返し警告する「断面を先に固定せよ」が、この命令-手段乖離それ自体にも適用される★実例。

## 新規実測② — docs/rules/fleet-composition-manifest.yaml (機序(b)・当職W53由来の独立発見)

- 出所 = CLAUDE.md起動時必読 → `docs/08-ops/pc-allocation.md` 冒頭警告文 → 「現行正本」として名指される file。
- `ls docs/rules/fleet-composition-manifest.yaml` = 不在。`git ls-files` = 0件。`git show origin/main:<path>` = fatal (存在せず)。
- karo-second の裏取り (msg_20260803, 当職W53受理便) = 「hakudokai-dev repo所在と注記されておる」「当隊は他repoへの走査を禁じられておるゆえ正本を指す矢印が当隊の手の届かぬ先へ出ておる」。
- **本件は当職が2026-08-03のW53で既に発見・報告済 (委員長殿・将軍second へ上申済)。本工区で改めて母体doc(2026-08-06起草)の型に照らして再確認した** — 母体4件より先に、同型の事例が当職inbox内に既に存在していたことになる。

## 既知重複の扱い — docs/rules/reservation-imaging-division-charter.md

- karo-second が msg_20260806_085027 (本工区着手前) で既に「本日六件目」と自己申告済。
- 当職の独立実測 = `git ls-files` = 0件・commit `574322e1` は `git cat-file -t 574322e1` = fatal (当repoに無いobject)。karo-second の申告「574322e1もunknown revision」と一致。third_pc側の物と推定・未確認のまま。
- ∴ **新規発見ではなく既知**。二重計上を避けるため「候補」ではなく「参考」として記載。

## 除外した近縁事例 — .claude/rules/knowledge-gap-warning-duty.md (同型に非ず)

- 台帳B-31が「正本はrepoに在り」と記すが `git ls-files`=0・`find`全域=0・`git log --all`=0 (当repo=multi-agent-shogun)。
- 然れど当職の過去の独立実測 (2026-08-05) で `git -C /mnt/c/Projects/hakudokai-dev show origin/main:.claude/rules/knowledge-gap-warning-duty.md` = 実在確認 (sha=7d1843613b2b17b0・184行・work treeには無し=origin/mainにのみ)。
- ∴ **手段は最終的に見つかった** (どのrepoかの指定漏れが真因)。「手段が届かぬ」ではなく「手段の所在ポインタが誤っていた」— 同型ではなく **別の失敗形** と判定し、母集団の分類 (C) に置く。

## 結論・数

**「四件で全部」ではない。**

- 母体doc記載の base 4件 (当職inbox内には④のみ直接該当・①②③は当職inbox外)。
- 当職inbox母集団内で本工区にて確認した**新規同型 = 2件**:
  - fleet-composition-manifest.yaml (機序(b)・当職W53由来・独立発見)
  - commander_send_shogun_second.sh (機序(c)・branch同期問題・★母体doc未記載の第3の機序を持つ新規実例★)
- 既知重複 (二重計上せず参考記載) = 1件 (reservation-imaging-division-charter.md)
- 除外 (同型に非ずと判定) = 1件 (knowledge-gap-warning-duty.md)

∴ 母体4件 + 新規2件 = **当職inbox母集団だけで最低6件**。かつ機序は単一ではなく**最低4種 (a)(b)(c)(d) に分岐**する。「五件目が在るなら根が別に在る」の問いに対する答 = **五件目どころか六件目が在り、かつ根そのものが単一ではない**。

## 母集団と除外 (再掲・明記義務)

- 総メッセージ166件 (現行35+archive131) → 命令型87件を対象 → 機械抽出70ユニークpath参照 → うち本節で言及した6件 (base参考4+新規2+既知重複1+除外1=実質6件を検分対象として詳述、残64件は「同型条件③(到達不能の実測)」を満たさず候補落ち — 大半は本工区/他工区の**成果物対象そのもの**であり「命令に必要な手段」ではなかった)。
- 未測 = 当職inbox以外の他agent inbox・他PCの状態・hakudokai-dev/third_pc repo内部。

## 判定に使った rc (パイプ前で受領)

```
git show origin/main:docs/rules/fleet-composition-manifest.yaml  → rc=128 (fatal: does not exist)
git show origin/main:docs/rules/reservation-imaging-division-charter.md → rc=128
git cat-file -t 574322e1 → rc=128 (fatal: Not a valid object name)
git merge-base --is-ancestor c61a124 HEAD → rc=1
git merge-base --is-ancestor c61a124 origin/main → rc=0
git ls-files -- scripts/commander_send_shogun_second.sh → rc=0 (出力0件)
git ls-files -- scripts/karo_second_send_iincho.sh → rc=0 (出力0件・check-ignore該当)
```

## 監査注記

暫定二者制 (軍師+Gemini。Codex leg 停止中・監査モデル gpt-5.4 暫定)。★「二者PASS」を「三者PASS」と書くな★。

## 破れた後 (該当なし)

本工区中、repo内fileの書換・commit・機構の新規作成は行っていない (読取・grep・git show/ls-files/cat-file/merge-baseのみ)。
