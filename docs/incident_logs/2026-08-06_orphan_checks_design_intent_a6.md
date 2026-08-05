# 呼出元見当たらぬ4本・設計意図の在否 (足軽6号、2026-08-06・家老second相談)

読取のみ。検査は走らせていない。newbuild・姉妹clone不触。
測時=2026-08-06T03:40:50+0900(date -Iseconds実行結果)。HEAD=7ad007162771d5157291eb423730cf8c3f3a377f
(git rev-parse HEAD実行結果)。

## 結論を先に

4本すべてに設計意図の記載が本体の冒頭コメントに在った。うち3本は「書かれた呼び手」が
実在しないことを確認した。残り1本は「人が手で叩く運用ツール」として書かれており、
自動呼び手そのものを持たない設計だが、手で叩いた記録は見当たらなかった。

## ①各scriptの冒頭コメント (命令+出力そのまま)

$ head -25 scripts/checks/codex_exec_sandbox_guard.sh
「Codex exec (agentic CLI) 起動前 sandbox 検証guard」「audit_codex.sh / npx @openai/codex exec を
起動する前に呼び、live repo cwd + sandbox 未確立なら停止」

$ head -25 scripts/checks/inbox_alias_integrity.sh
「IMPORTANT (CLAUDE.md §19.3 mandate): PreToolUse hook で呼ばれる場合、本scriptの非0 exitが
親tool操作をブロックしてはならない。呼出側で || true を必ず付ける」

$ head -25 scripts/checks/secondpc_dispatch.sh
「用途: 家老が SecondPC ashigaru5/6/7 に発令した直後の確認」

$ head -25 scripts/checks/symlink_aware_atomic_write.sh
「IMPORTANT (CLAUDE.md §19.3 mandate): PreToolUse hook で呼ばれる場合、」(inbox_alias_integrity.shと同文)

## ②書かれた呼び手が現に居るかの実測

$ grep -n "codex_exec_sandbox_guard" scripts/audit_codex.sh
(該当なし・0件) ∴ **「audit_codex.sh が呼ぶ」という設計意図は書かれているが、audit_codex.sh
自身は現に呼んでいない。**

$ grep -n "inbox_alias_integrity" .claude/settings.json
(該当なし・0件) ∴ **「PreToolUse hookで呼ばれる」という設計意図は書かれているが、
.claude/settings.jsonのhook一覧(4件=stop_hook_inbox.sh/pretooluse_bash_guard.sh/
dd169_kill_term_guard.sh/context_usage_warn.sh)に本scriptは含まれていない。**

$ grep -n "symlink_aware_atomic_write" .claude/settings.json
(該当なし・0件) ∴ inbox_alias_integrity.shと★全く同型の欠落★。

$ grep -rl "secondpc_dispatch.sh" scripts/ shim/
(scripts/checks/secondpc_dispatch.sh自身のみ・他からの呼出は0件) ∴ 本scriptは「家老second が
手で叩く」設計であり、そもそも自動の呼び手を持たない意図。∴ ここでの問いは「呼び手が居るか」
ではなく「手で叩かれた記録が在るか」。

$ grep -n "secondpc_dispatch" docs/incident_logs/2026-08-05_gitignore_silent_gate_design_a1.md docs/incident_logs/2026-08-05_legB_gate_bypass_census_a2.md
2件ヒットしたが、いずれも★scripts/checks/配下の一覧列挙内での言及のみ★であり、実際に
実行された痕跡(出力・exit code・当該scriptを叩いたと明記する文)ではなかった。

## 表 (4本、設計意図の記載有無/書かれた呼び手の実在)

| 検査 | 設計意図の記載 | 書かれた呼び手 | 実在するか |
|---|---|---|---|
| codex_exec_sandbox_guard.sh | 有(audit_codex.sh起動前) | audit_codex.sh | **居らず(0件)** |
| inbox_alias_integrity.sh | 有(PreToolUse hook) | .claude/settings.json | **登録されておらず(0件)** |
| symlink_aware_atomic_write.sh | 有(PreToolUse hook、同文) | .claude/settings.json | **登録されておらず(0件)** |
| secondpc_dispatch.sh | 有(家老second手動確認) | (自動呼び手は設計上不要) | 手動実行の痕跡=当職の検索範囲では未発見 |

**∴ 4本すべてで「意図は記録されている」事を確認した。將軍second殿の見立て
(「4本が不要とは限らぬ」)は正しかった——不要なのではなく、★意図はあるのに配線されていない
(codex_exec_sandbox_guard/inbox_alias_integrity/symlink_aware_atomic_write)★か、
★手動運用ツールとして書かれたが実際に手で叩かれた記録がない(secondpc_dispatch)★のいずれかで、
「捨ててよい」根拠はどこにも見当たらない。**

## 【本工区で己が直した誤り】

初稿でsecondpc_dispatch.shも他の3本と同列に「呼び手が0件=配線漏れ」と書きかけたが、
冒頭コメントを読み直した所これは元より自動呼出を想定しない手動確認ツールである事に気付き、
問いを「呼び手が居るか」から「手で叩かれた記録が在るか」へ書き直した(4本を機械的に同一の
物差しで測ろうとしていた誤りの是正)。

## ★母集団漏れの自己申告★

1. secondpc_dispatch.shが実際に手で叩かれたかは、karo-second殿ご本人の記憶・手元の実行履歴
   (shell history等)でしか確認できない可能性が高く、当職の検索範囲(docs/incident_logs・
   scripts/・shim/)では確認できなかった。
2. .claude/settings.local.json等、settings.json以外のhook設定fileが存在するかは確認していない。

## 追補 (2026-08-06T03:50:32+0900・将軍second殿の訂正を受けて)

家老second殿のcommit 137f26cが4本を一括して「意図は在り結線が無い」と括ったのは言い過ぎであった
(家老second殿の落度として明記・当職の票自体は正確であったと家老second殿より確認済)。三分する。

【SUPERSEDED・以下は三分類版・下記四分類版に改訂済(将軍second裁・secondpc_dispatchを⒞と
「同様」と括った点が誤りであった為)】
~~- 真に結線を欠く(2本)=`inbox_alias_integrity.sh`・`symlink_aware_atomic_write.sh`。
  「0件」の意味=呼ぶ側(PreToolUse hook登録)自体が存在しない。
- 呼ぶ側が凍結ゆえ発火せぬ(1本)=`codex_exec_sandbox_guard.sh`。
- 手動運用で未実行(1本)=`secondpc_dispatch.sh`。「0件」の意味=家老second殿ご自身の道具で
  あり、家老second殿が一度も手で叩いていない事による——結線の欠落ではなく運用の欠落。~~

### 四分類版(現在有効・各分類に処方を一行添える)

- **⒜ 不要**=要らぬ物が在る。**該当なし(0本)**——分類を立てて空である事も情報として明記する。
- **⒝ 結線漏れ(2本)**=`inbox_alias_integrity.sh`・`symlink_aware_atomic_write.sh`。機構が呼ぶ
  設計なのに登録が無い(`.claude/settings.json`のPreToolUse hook一覧に不在)。
  **処方=結線せよ(hookへの登録を検討する余地あり、実装は上位裁を要す)。**
- **⒞ 凍結(1本)**=`codex_exec_sandbox_guard.sh`。呼ぶ側(`audit_codex.sh`)自体が信長SAFETY裁定
  (2026-07-21・当職も独立確認済=memory `codex-audit-live-repo-write-risk`)で禁じられている。
  門は正常・発火せぬのが正しい状態。**処方=放っておいてよい(呼ぶ側が解禁されれば自然に発火する)。**
- **⒟ 未使用(1本)**=`secondpc_dispatch.sh`。呼び手は人(家老second殿)で、その人が呼んでいない。
  結線は要らぬ(手動ツールゆえ)。**処方=決めねばならぬ(使うか廃するかを家老second殿ご自身が
  決める必要あり)。放っておけば「在るが誰も使わぬ物」として残り続ける。**

∴ ⒞と⒟は「0件」という外形は同じだが、処方が正反対(⒞=放置でよい・⒟=決定を要す)。
これを「同様」と一括すれば、⒟へ「結線せよ」という誤った処方が出かねない——本日確立した
「同型は検証を省かせる語」の実例が、この追補作成の過程そのものに現れた。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、呼出元見当たらぬ4本・設計意図の在否への応答(追補込み)。検査は一切実行していない。
