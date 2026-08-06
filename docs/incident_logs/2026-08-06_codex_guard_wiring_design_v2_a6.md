# codex_exec_sandbox_guard 結線・再設計 (足軽6号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭)

設計のみ・実装せず。guard本体・audit_codex.sh・audit_meta_codex.sh・hakudokai_audit_scheduler.sh・
.claude/settings.json・.gitignoreいずれも編んでいない。走らせず。newbuild・姉妹clone不触。

測時=2026-08-06T09:05:28+0900(date -Iseconds実行結果)。HEAD=6a561fdc669a5ed9c47eb8e0fb2f3487ee9bc97f
(git rev-parse HEAD実行結果)。★別file(v1設計・その追補への★さらなる追補★)。既commit本体は不触★。

## 誤りの因 (再確認)

v1設計は「渡す値(REPO_PATH)」を選んだが、これは★設定変数★であり★実行時の実cwd★ではない。
正しい設計は「渡す値」ではなく「測る場所」——★guardが自ら実行される瞬間のcwdを測る形★にすべき。

## ⒜ 正しき結線先の設計 (実cwdを測る形)

$ sed -n '255,263p' scripts/audit_meta_codex.sh / sed -n '118,126p','170,177p' shim/hakudokai/hakudokai_audit_scheduler.sh
**実測=4箇所いずれも、`npx @openai/codex exec`の行はsubshell(`$(...)`)に包まれていない
——直接その行が実行される時点のscript本体の実cwdが、そのままCodexの実行cwdに成る。**

**∴ 設計案=guardをbash子processとして呼べば、★子processは親の実cwdを自動継承する★
(明示的なcdを挟まぬ限り)。∴ guard自身が内部で`pwd`(引数無し)を実行し、その値をチェック
対象とすれば、★呼出し元がREPO_PATHのような変数を渡す必要が無くなる★。**

具体案=guard起動コマンドを`bash scripts/checks/codex_exec_sandbox_guard.sh`(引数無し)へ変更、
guard内部の該当箇所(現状はコメントより`[intended_cwd]`を引数として受ける設計)を
`intended_cwd="${1:-$(pwd)}"`のように★引数省略時は自身のpwdを使う★形へ改める(既存の
引数渡しの互換性も残しつつ、既定を「測る」側へ倒す)——これも設計案であり実装はしない。

## ⒝ 4箇所悉くへの結線 (一箇所で「済んだ」としない)

| # | file:line | 呼ぶ位置(案) |
|---|---|---|
| 1 | scripts/audit_codex.sh:93 | L92直前(v1設計を維持、当該箇所は変わらず正しい) |
| 2 | scripts/audit_meta_codex.sh:263 | L259直前(retry loop突入前、同じ理由でloop外側1回) |
| 3 | shim/hakudokai/hakudokai_audit_scheduler.sh:125 | L125直前(codex dispatch実行直前) |
| 4 | shim/hakudokai/hakudokai_audit_scheduler.sh:176 | L176直前(commit audit実行直前) |

いずれも「guard呼出しとexec呼出しの間にcdを挟まない」事が要件——挟めば実cwdの継承が破れる。

## ⒞ この修正が新たに開ける穴は何か

1. **guardの`pwd`測定自体が、呼出し元scriptの★呼ばれた文脈★に依存する**——例えば
   `hakudokai_audit_scheduler.sh`がsystemd timer経由で起動される場合、そのtimerの
   `WorkingDirectory`設定次第でpwdが変わり得る(本日別工区で確認済=systemd unitの
   `WorkingDirectory`は個別に設定され得る)。∴ guardが「安全なpwd」を測れても、
   ★systemd側のWorkingDirectory設定自体が誤っていれば、guardは誤った前提を「正しく」
   測ってしまう★——guard単体では防げぬ層が存在する。
2. **4箇所同時結線は、4箇所同時に停止し得る事も意味する**——一箇所の結線ミス(例えば
   引数の渡し忘れ)が、意図せず他の3箇所の挙動には影響しないよう、★各呼出し箇所は
   独立したbash子processとして完全に分離すべき★(共有state・共有変数を持たせない)。
3. **既存のretry loop(audit_codex.sh・audit_meta_codex.sh)とguardの相互作用**——v1設計の
   自己申告どおり、既存retryロジックとguard由来の停止がどう共存するかは本設計でも未解決
   のまま(v1の限界を引き継ぐ)。

## 【本工区で己が直した誤り】

初稿で4箇所の呼ぶ位置を「script冒頭一括」とまとめて書きかけたが、audit_meta_codex.shが
retry loopを持つ事(v1のaudit_codex.shと同型)に気付き、loop外側1回のみへ個別に書き直した
(4箇所を機械的に同一パターンで済ませず、各scriptの実際の構造を読んでから設計し直した)。

## ★母集団漏れの自己申告★

1. `hakudokai_audit_scheduler.sh`がsystemd timer経由で起動される際の実際のWorkingDirectory
   設定値は、本工区では確認していない(⒞の穴として指摘したのみ、実測はしていない)。
2. 4箇所の呼出し前後で、既存のerror handling(exit code取得・ログ出力等)がguard導入により
   どう変わるべきかの詳細設計は、実装時に別途要する(本設計は「どこで・何を測るか」に留めた)。

## 追補 (2026-08-06T09:12:40+0900・新穴①の実測)

読取のみ(systemctl list-unit-files/list-timers・crontab -l・grep実施のみ)。再起動・停止・
編集いずれも行っていない。HEAD=6a561fdc669a5ed9c47eb8e0fb2f3487ee9bc97f(不変)。

$ systemctl --user list-unit-files --type=service --no-pager | grep -iE "audit|codex"
codex-healthcheck.service static -
(★別script=codex_state_healthcheck.shを指す物であり、audit_codex.sh/audit_meta_codex.sh/
hakudokai_audit_scheduler.shとは無関係★)

$ grep -rl "audit_codex.sh\|audit_meta_codex.sh\|hakudokai_audit_scheduler.sh" /home/hakudokai/.config/systemd/
(該当なし・0件)

$ crontab -l
no crontab for hakudokai

**∴ 当PC(SecondPC)には、4箇所の呼び手を起動するsystemd unit・crontabエントリはいずれも
存在しない。∴ 新穴①(WorkingDirectory依存)は★当PC上では現時点で発現しない★
(発現の前提となるsystemd/cron経由の起動自体が無い為)。★但し★=これは「穴が無い」の
証明ではなく「当PC上のsystemd/crontabという限られた探索範囲では見つからなかった」
に留まる——手動起動・他PC経由の起動・未発見の起動経路の可能性は排除できない。**

## 【SUPERSEDED 2026-08-06T09:25:13+0900】本file冒頭「誤りの因」節およびⒶ節の中心命題は誤り

足軽2号の反証(docs/incident_logs/2026-08-06_codex_guard_wiring_v2_adversarial_review_a2.md)により
判明=guard本体`scripts/checks/codex_exec_sandbox_guard.sh:17`に、当file自身が「新たに導入すべき」
とした挙動(`INTENDED_CWD="${1:-$PWD}"`、引数省略時は自身の$PWDを既定とする)が★既に存在していた★。
かつ、これは足軽1号のv1反証(msg内で当職が既読・応答済)が既に逐語引用していた事実であり、
「読んだが使わなんだ」に該当する。★本fileの守本体編集案は不要であり撤回する★。詳細・訂正版=
docs/incident_logs/2026-08-06_codex_guard_wiring_design_v3_a6.md参照。旧文言は削除せず保存する。

## 監査体制

暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)。

以上、codex_exec_sandbox_guard結線・再設計への応答(追補込み)。実装・再起動・停止いずれも行っていない。
