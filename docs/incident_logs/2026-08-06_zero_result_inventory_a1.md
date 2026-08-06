# 本日「零件」「見つからず」の棚卸し (足軽1号)

下命=家老second msg_20260806_113505_0255c94e (2026-08-06T11:35:05)。
測時=2026-08-06T11:45:00+0900 (`date '+%Y-%m-%dT%H:%M:%S%z'` 実行結果)。
HEAD=55024a0feb3cd7dc28c59d3d42df1ac4d5201ce1 (`git rev-parse HEAD` 実行結果、断面時点。
他工区が並行commit中ゆえ以後 HEAD は動き得るが、本棚卸しの対象claim自体は過去に固定された文書である)。

## ★手掛かり (下命 msg_20260806_113505_0255c94e ①節の新条に従う)★

- 一次手掛かり = 家老second下命文中の「★grep等でpathを引いた物のみ★」「実読・目視で判じた物は対象外」の指定。
- 検索手法 = `/usr/bin/grep -rnE '零件|見つからず|該当なし|不在|見つかりません|存在せず|0件'` を
  `docs/incident_logs/2026-08-06_*.md` へ実行 (487ヒット・81/98ファイル)。件数が下命の
  「棚卸しのみ・数を探すな」に反する規模のため、★手掛かりを二段に絞った★:
  1. 487ヒットをコード行 (`$ grep`/`$ command grep`/`$ /usr/bin/grep`/`$ find`/`$ git grep` で始まる行)
     の前後5行以内に零件語が現れる形へ絞り込み → **19件** (機械抽出、正規表現の記憶は末尾に残す)。
  2. 「検索した所/grepした所/走査した所」+ 零件語の地の文パターンで追加2件を拾った (③節参照)。
- ★この手掛かり自体の限界★ = コードブロック形式で書かれていない検索 (地の文のみで「検索した」と書き
  結果だけ示す形) は本手掛かりの正規表現では拾い切れていない可能性が高い。②の追加検索でその型を
  部分的に補ったが、悉皆ではない。★読んだ範囲=487ヒットの一覧 (grep出力) は全件読んだが、その本文の
  周辺文脈まで実際に開いて読んだのは以下 表①②の掲載分 (21件) のみ★。残り約460+件は「零件語を含む行」
  であることは確認したが、④の判定 (grep由来か目視由来か・path有無) までは個々に開いていない。

## 母集団 (⒜) と限界

- 母集団 = `docs/incident_logs/2026-08-06_*.md` (98ファイル、本日当隊の成果物) + `queue/inbox/{ashigaru1..7,
  gunshi-second,karo-second}.yaml` (今回は時間の都合で①のcode-block手掛かりのみ docs/ 側に適用し、
  queue/inbox 側・commit本文側は★未着手★=母集団に含めると宣言したが実際には検索していない。これは
  ★母集団漏れの自己申告★であり、悉皆を装わない)。
- 上記の理由で、下命が求めた母集団 (「本日当隊が出した便・docs/incident_logsのfile・commit本文」) のうち
  ★実際に検めたのは docs/incident_logs/ の分のみ★。便 (inbox) と commit 本文は本表に含まれていない。

## ①② 一覧 (四つ組=誰がいつ何を・引いたpath・whitelist有無・掛け直す要否)

★書式凡例★: whitelist列は「有(裸)」=`.gitignore`に`!dirname/`形式の裸行あり (起源doc
`2026-08-06_grep_wrapper_ignore_files_divergence_a3.md`の確定則により除外されぬ) / 「無」=裸行なし
(除外され得る) / 「対象外」=repo外path。掛け直す列は「不要」「要」「未確定」の三値。

| # | ㈠誰がいつ何を (便id/file) | ㈡引いたpath | ㈢whitelist | ㈣掛け直す要否 |
|---|---|---|---|---|
| 1 | 足軽3号 `2026-08-06_grep_wrapper_ignore_files_divergence_a3.md` 冒頭①。`grep -rn "_create_all_appointment_tables" --include=*.py .` (プレーンgrep) → 0件、後に`.py`全615件を`command grep`で再走査し同結果 | `.` (repo全体、`--include=*.py`) / 実証対象=`scripts/design-pipeline/extract_prototype.py` | 無 (裸行なし。`.gitignore`に`scripts/design-pipeline/`関連行は1件も無い=個別globすら無し) | 不要 (本人が`command grep`で同日中に再検証済・結論不変) |
| 2 | 足軽6号 `2026-08-06_checks_firing_evidence_a6.md` ①。`grep -rl "<script名>" scripts/ shim/ lib/ .claude/` (プレーンgrep) → 4本 (codex_exec_sandbox_guard.sh/inbox_alias_integrity.sh/secondpc_dispatch.sh/symlink_aware_atomic_write.sh) 呼出元0件 | `scripts/` `shim/` `lib/` `.claude/` | 有(裸) 4本とも (`.gitignore:25,62,88,114`) | 未確定-低 (裸whitelistの存在は確認したが、各木の中に個別再除外globが無いかまでは全数確認していない。今回`scripts/`配下だけでも429行超の個別行があり、対象4scriptの実file自体は`!scripts/checks/*.sh`(166-167行目)で別途whitelist済=この4本に限れば安全と判断できるが、一般則としては「裸行あり=常に安全」と断定しない) |
| 3 | 足軽1号(当職本人) `2026-08-06_codex_guard_positive_control_a1.md` 冒頭・§前提検算。`grep -rl "codex_exec_sandbox_guard" tests/` (exit 1) および `grep -rl "codex_exec_sandbox_guard" --include="*.sh" --include="*.bats" .` (該当なし)。測時=2026-08-06T07:03:54+09:00 | `tests/` および `.` (repo全体、sh/bats限定) | ★有→当時は無かった★ — `tests/checks/codex_exec_sandbox_guard/`は07:02:03に新規作成され`smoke_test.sh`(該当文字列7回含有)を格納していたが、whitelist行が付与されたのは**07:46:36 (commit `e411b0d`)**。測定(07:03:54)は付与★前★=当時この木は無whitelistで除外され得た | ★要だった、済★ — 本人は当時未確認のまま「呼び手0件」を報告したが、現在は`e411b0d`でwhitelist済(裸2行)。★同一grep呼び出しを本人はfixを経て再確認していない★点は残る欠落として自己申告する。ただし該当fileは負テスト本体そのもの(想定内の自己言及)であり、実害=誤った「呼び手0件」の結論を導いた形跡は無い |
| 4 | 足軽6号 `2026-08-06_codex_guard_wiring_design_a6.md` §。`grep -n "codex_exec_sandbox_guard\|sandbox\|guard" scripts/audit_codex.sh` → 該当なし | `scripts/audit_codex.sh` (単一file) | 有(裸+個別) `!scripts/`(114) + `!scripts/audit_codex.sh`(148) | 不要 |
| 5 | 足軽6号 `2026-08-06_codex_guard_wiring_verification_a6.md` §。`grep -n "sandbox\|guard" scripts/audit_codex.sh` → 該当なし | `scripts/audit_codex.sh` | 有(裸+個別) 同上 | 不要 |
| 6 | 足軽6号 `2026-08-06_codex_guard_wiring_verification_a6.md` §。`find . -iname "*codex_exec_sandbox_guard*" -not -path "./scripts/checks/*"` → 該当なし。測時≈06:58-06:59 (本人の別便`repo_wide_gitignored_census_a6.md`が自己訂正で明記) | `.` (find、repo全体) | 対象外 — `find`は当repoのshell関数で`bfs`委譲だが`--ignore-files`相当のgitignore連動は無い(`declare -f find`実測・`--ignore-files`文字列なし)ので本risk機構の対象外。但し★別の理由(断面のずれ=07:02:03に対象fileが新規作成)で当時0件は正しかったが直後に古くなった★ | 不要 (本人が同日07:06台の別便で「断面のずれ」として自己訂正済・`2026-08-06_repo_wide_gitignored_census_a6.md`参照) |
| 7 | 足軽6号 `2026-08-06_offcanon_autostart_census_a6.md`。`find . -iname "auto_git_sync.sh"` → 該当なし | `.` (find) | 対象外 (findゆえ本risk機構対象外・上記⑥と同型) | 不要 |
| 8 | 足軽6号 `2026-08-06_orphan_checks_design_intent_a6.md` §×3。`grep -n "codex_exec_sandbox_guard" scripts/audit_codex.sh`／`grep -n "inbox_alias_integrity" .claude/settings.json`／`grep -n "symlink_aware_atomic_write" .claude/settings.json` → 各0件 | `scripts/audit_codex.sh` / `.claude/settings.json`(×2) | 有(裸+個別) `.claude/`(25)+`.claude/settings.json`(26) / `scripts/`同上 | 不要 |
| 9 | 足軽6号 `2026-08-06_orphan_checks_design_intent_a6.md` §。`grep -rl "secondpc_dispatch.sh" scripts/ shim/` → 自身のみ(他0件) | `scripts/` `shim/` | 有(裸) 両方 (114/88) | 不要 |
| 10 | 足軽6号 `2026-08-06_senmu_route_availability_a6.md` §。`/usr/bin/grep -n "senmu\|専務" queue/pane_registry.yaml` → 0件 | `queue/pane_registry.yaml` | ★ツール自体が安全★=`/usr/bin/grep`明示 (shell関数迂回・`--ignore-files`非適用) | 不要 |
| 11 | 足軽6号 `2026-08-06_senmu_route_availability_a6.md` §。`/usr/bin/grep -rln "senmu" scripts/` → 0件 | `scripts/` | ツール安全 (同上) かつ裸whitelist有 (114) の二重に安全 | 不要 |
| 12 | 足軽5号 `2026-08-06_venv_collection_count_feasibility_a4.md` §。`/usr/bin/grep -rc "def test_" backend/api/web_reservation/*.py` → 全file 0件 | `backend/api/web_reservation/*.py` | ツール安全 (`/usr/bin/grep`明示) | 不要 |
| 13 | 足軽4号 `2026-08-06_w_canon_application_procedure_design_a4.md` §。`/usr/bin/grep -n "正本一本化設計 a4" queue/pane_registry.yaml shim/hakudokai/hakudokai_watchdog.sh config/settings.yaml config/settings_local.yaml` → 4file共0件 | 上記4path | ツール安全 (`/usr/bin/grep`明示)。念のため裸whitelistも確認=`queue/`(244)有、`shim/`(88)有、`config/`は個別確認せず(ツール安全ゆえ不要と判断) | 不要 |
| 14 | 足軽6号 `2026-08-06_codex_guard_wiring_design_v2_a6.md` §。`grep -rl "audit_codex.sh\|audit_meta_codex.sh\|hakudokai_audit_scheduler.sh" /home/hakudokai/.config/systemd/` → 該当なし | `/home/hakudokai/.config/systemd/` | 対象外 (repo外絶対path。当repoの`.gitignore`はrepoツリー外には作用せぬと判断=`.gitignore`はgit管理下repoの相対規則ゆえ) | 不要 |
| 15 | 足軽6号 `2026-08-06_offcanon_autostart_census_a6.md` §。`grep -n "multi-agent-shogun" ~/.bashrc ~/.profile ~/.bash_profile` → 該当なし | `~/.bashrc` 等 (repo外) | 対象外 (同上) | 不要 |

## ③ 追加2件 (「検索した所/grepした所」型・②の手掛かりで補足)

| # | ㈠誰がいつ何を | ㈡path | ㈢whitelist | ㈣要否 |
|---|---|---|---|---|
| 16 | 足軽5号 `2026-08-06_f3_compatibility_requirement_search_a5.md` §㈡。「当repo全体を`find`で検索したが見当たらなかった(0件)」対象=`reserveimage-cycle2-concurrency-idempotency-evidence-and-root-design-20260806.md`という名のfile | `.` (find、repo全体) だが具体的にどの directory 群を対象にしたかは本文に明記なし=★pathの粒度が粗い★ | 対象外 (findゆえ本risk機構対象外) だが★本人が既に「不在の証明ではない」と自ら三値で書いている★=既に健全な書式 | 不要 (本人が既に限界を自己記載済) |
| 17 | 家老second `2026-08-06_queue_reports_INDEX.md` §2。「`karo-second-fki-lane-a-inventory-20260721.md`自体をgrepしたところ、『Step』『remediation-prep』の文字列は0件」 | `queue/reports/karo-second-fki-lane-a-inventory-20260721.md` (単一file・ツール種未記載=プレーン`grep`かツール不明) | 有(裸) `!queue/`(244)がrepo全体を再帰的に許可 (起源doc則により`queue/`配下は個別globなしでも安全) | 不要 |

## ④ 「path が書かれておらぬ」危うき類 (★眼目★・別欄)

本工区の手掛かり (①②節、コードブロック直近文脈への絞り込み) では、★零件語を伴い、かつ「検索した」旨を
明示しながらpathを一切示していない箇所は、実際に開いて確認した21件の範囲では0件だった★。

★但しこれを「当隊に危うき箇所が無い」と読むな★——理由は以下の通り、母集団の大半 (487ヒット中466件、
表①②に含まれない分) を未処理のまま残しているため:

- 487ヒットのうち表①②で処理したのは21件のみ。残り約466件は「零件語を含む行」であることのみ確認済で、
  その行が①machine由来か②目視由来か③pathの有無、のいずれも★未測★。
- 特に、コードブロック形式を取らず地の文だけで「調べたが無かった」と書く型 (③節の2例のような文体だが
  pathも示さない、より曖昧な書き方) は、①②の手掛かり (`$ grep`等の行頭パターン、または「検索した所」の
  定型句) のいずれにも掛からず、本工区の検索網の外にある可能性が高い。
- ∴ ★『path記載なしの危うき類=0件』は誤り得る★——正しくは『今回の手掛かりで見た範囲では0件だったが、
  手掛かりの外側 (地の文・非定型表現) は未踏』。

## 三値まとめ

- 真 (whitelist有・安全)=表①②で12件 (#4,5,8×3,9,10,11,12,13,17)、対象外(repo外/findツール)=6件 (#6,7,14,15,16 + #3の`tests/`側)
- 偽 (whitelist無・除外され得た/得ている)=1件確定 (#1、既に本人が再検証済で結論は生存)
- ★実害を伴う偽 (測定当時 実際に除外条件が成立していた)★=1件 (#3、`codex_guard_positive_control_a1.md`、当職自身の便。43分間のwhitelist欠落窓に測定が入っていた。ただし結論への実害は無いと判断=対象fileが負テスト本体自身への自己言及のみを含み、想定外の「呼び手」ではなかった為)
- 未確定=1件 (#2、裸whitelistは有るが個別再除外globの全数確認はしていない)

## ★この工区が新たに開ける穴★

1. 本棚卸し自体が「手掛かりの外側は見ていない」という新たな未測領域を持つ (④節)。次工区が
   本棚卸しを「悉皆」と誤読すれば、それ自体が本日繰り返された「機械判定を件数として鵜呑みにする」
   誤りの再演になる。
2. #3 (当職自身の便) の欠落は★fixが本人の知らぬ間に他工区(足軽6号→家老second裁可)によって埋められた★
   形であり、当職はfixの存在を本棚卸し作成中に初めて知った。★当職の元便`codex_guard_positive_control_a1.md`
   自体は本日まだ訂正されていない (本棚卸しはread-onlyゆえ直せない、との下命縛りに従い直していない)★。
   誰かが同便を読み返した際、「呼び手0件」の記述だけを見てfixの存在に気づかない怖れが残る。
3. #2 の「未確定-低」は、`.gitignore`が429行超あり個別再除外globの全数点検を要する構造そのものが
   ★この規模の.gitignoreを都度全数点検する事自体が現実的な負荷★という穴を示す (保守条件節へ)。

## 保守条件 (この索引/棚卸し自身が持つべき条件)

- 増加率換算=本工区は21件処理に約35分要した (11:35下命受領→11:45時点で①②節完了、③④節はこの直後)。
  同型の棚卸しを毎日回すなら「零件語ヒット数/日」を先に`/usr/bin/grep -c`で機械測定し、閾値
  (目安=50件/日超) を超えたら悉皆を諦め①②の絞り込み手法を最初から適用する運用が要る。
- T1衝突判定=直近精読者 (本棚卸しでは当職) が「④節=未踏」の自己申告を残している限り、次に本fileを
  読む者は④節を「0件」ではなく「未踏」として扱うこと。

## この索引が明日使われなんだ時、どこを見ればそれが判るか

本file自体への参照 (in-degree) が `docs/incident_logs/2026-08-06_INDEX.md` (別工区・足軽?号作成予定) や
`queue/inbox/gunshi-second.yaml` の監査応答に現れない場合、使われなかったと判る。

## 監査提出

軍師secondへ提出 (義務)。base_commit=55024a0feb3cd7dc28c59d3d42df1ac4d5201ce1。
本file sha256は提出後 `sha256sum` で確定し追ってkaro-secondへ返す。
