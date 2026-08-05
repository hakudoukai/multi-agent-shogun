# scripts/checks/ 9本・「当の欠陥を検出し得るか」棚卸し (足軽6号、2026-08-06・家老second下命)

★★読取のみ(grep実施のみ)。検査は一切実行していない(走らせず・列挙のみ)。★★
測時=2026-08-06T03:22:52+0900(date -Iseconds実行結果)。HEAD=e59c47b7820bc6c86513c03218fea83b24bfa21b
(git rev-parse HEAD実行結果)。

## 母集団 (前工区の見落とし=「本日変わらぬ物は検されぬ」の是正)

$ ls scripts/checks/*.sh
codex_cli_required_persona.sh / codex_exec_sandbox_guard.sh / context_usage_warn.sh /
dd169_kill_term_guard.sh / inbox_alias_integrity.sh / pane_identity.sh /
pretooluse_bash_guard.sh / secondpc_dispatch.sh / symlink_aware_atomic_write.sh
(計9本、前回除外した物★全数を本工区の母集団とした★)

## 検索方法・限界(明記)

各script名を`docs/incident_logs/*.md`+`tests/*.bats`全文でgrep一致させ、一致fileの中に
「陽性対照」「positive control」「わざと壊す」等の語が★同一scriptの文脈で★現れるかを確認した。

## 結果 (実測・命令+出力)

$ grep -rl "<script名>" docs/incident_logs/*.md tests/*.bats | wc -l (script毎)
codex_cli_required_persona.sh=1件 / codex_exec_sandbox_guard.sh=2件 / context_usage_warn.sh=1件 /
dd169_kill_term_guard.sh=5件 / inbox_alias_integrity.sh=4件 / pane_identity.sh=8件 /
pretooluse_bash_guard.sh=4件 / secondpc_dispatch.sh=2件 / symlink_aware_atomic_write.sh=2件

**参照回数の多い4本(dd169/inbox_alias/pane_identity/pretooluse)を個別に開いた所、
「陽性対照」等の語が出現する箇所は★悉く別主題(watcher_supervisor.shのpkill調査・
dashboard 00E測定等)の中で★偶々scriptの名が併記されていただけ★であり、
★当該script自身が「欠陥のある版へ当てるとFAILする」事を実行して示した記録は
当職の検索範囲では1件も見つからなかった★。**

## 表 (9本全て)

| 検査 | grep一致件数 | 陽性対照(実行によるFAIL実証) | 根拠 |
|---|---|---|---|
| codex_cli_required_persona.sh | 1 | 不明(未発見) | 該当file1件は名の言及のみ |
| codex_exec_sandbox_guard.sh | 2 | 不明(未発見) | 既存memory`codex-audit-live-repo-write-risk`に運用停止の記載はあるが、guard自体のFAIL実証は無し |
| context_usage_warn.sh | 1 | 不明(未発見) | 言及のみ |
| dd169_kill_term_guard.sh | 5 | 不明(未発見・偶々の併記) | 5件とも他主題(watcher pkill調査)内の名前併記 |
| inbox_alias_integrity.sh | 4 | 不明(未発見・偶々の併記) | 同上 |
| pane_identity.sh | 8 | 不明(未発見・偶々の併記) | 同上(dashboard 00E測定文脈) |
| pretooluse_bash_guard.sh | 4 | 不明(未発見・偶々の併記) | 同上 |
| secondpc_dispatch.sh | 2 | 不明(未発見) | 言及のみ |
| symlink_aware_atomic_write.sh | 2 | 不明(未発見) | 言及のみ |

**∴ 9本全てが「不明」——本工区の検索範囲(grep一致のみ)では、いずれの guard も
「欠陥のある版へ当てるとFAILする」事を★実行して示した記録★を発見できなかった。
これは「陽性対照が存在しない」事の証明ではなく、★当職の検索方法(既存doc内のgrep一致)
では見つけられなかった★事の記録である(下命⑽=判定不能には何が出れば動くかを併記=
「当該scriptを対象に、既知の欠陥入力を用いた実行ログまたは負テストコードが見つかれば
動く」)。**

## 【本工区で己が直した誤り】

初稿でdd169_kill_term_guard.sh等の参照件数(4-8件)を見て「陽性対照文書化済」と早合点しかけたが、
実際に該当箇所を開いて読んだ所、いずれも別主題(watcher調査等)での偶然の名前併記に過ぎない事に
気付き、「有」から「不明」へ訂正した(grep一致件数を中身の証拠と誤認しかけた=本日確立の
「道具の出力は道具の判定に非ず」の実演)。

## ★母集団漏れの自己申告★

1. `git log -p`によるscript本体の変更履歴(過去のcommit時に負テストが同時に書かれたか)は
   確認していない——grep一致のみに依った検索であり、より遡った履歴調査は行っていない。
2. これらscriptを呼び出すhook設定(`.claude/settings.json`等)側にテスト記述がある可能性は
   検討していない。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、scripts/checks/9本・陽性対照棚卸しへの応答。検査は一切実行していない。
