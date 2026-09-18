# km-167 ―― main の CI 赤 4 job の根治(build-check / shellcheck / unit-tests×2)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-167-main-ci-aka-yon-job-no-konchi-20260918`(裁 seq331141・板 94c61e26・家老mac 据ゑ 12:28)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T12:58 / 着手 12:30:06(自己識別)/ 着手便 12:48:26(遅い・疵として記す)
- 基底 = origin/main `6bde7170ce574090a6139ba2dfe3aa4cb6db8634`(赤の run 35289072580・push 2026-09-17T23:57Z)。己の樹 = `~/wt/a1-km167-ci`(枝 `ashigaru-mac-1/km-167-ci-20260918`)。共用樹の HEAD/index/作業紙は不触。
- 母數 = job 4 / 生成物 19 file / .sh 71 本 / bats 紙 21 本(tests 6 + tests/unit 15)/ bats 走 = root 58・selfwatch 19(+skip 1)・unit 338 = 415 試験 × 環境 3 態
- ★測りの限界(先に書く)★: CI の log は `gh api .../jobs/<id>/logs` が **HTTP 403(Must have admin rights)** で読めぬ(raw/10_cilog_*.err 4 本)。∴ 本紙の数は ★悉く此の Mac の出目★ であり、Linux CI と同一であるとは断じ得ぬ。CI と同じ器を手元に置いて近づけたが、同一ではない。

## ㋐ 結語

★赤 4 job の真因は、家老の見立て 3 項(生成物 19 本・冠一行・GNU 字面 6 類)の内 2 項が当たり、1 項(GNU 字面)は外れ、見立ての外に 6 件在つた。★

| job | 落ちた step(raw/11_run_view.txt) | 真因(手元実測) | 本弾の直し | 手元の後 |
|---|---|---|---|---|
| Build Instructions Check | Check for uncommitted changes | ⑴ 生成物 19 本が元紙より古い(差は実体) ⑵ ★元紙 instructions/shogun.md が CRLF(CR 行 413)ゆゑ build の awk `/^---$/` が閉ぢ `---` を拾はず、将軍系 4 紙の front matter が★黙つて消える★(raw/63_frontmatter_before_fix_shogun.txt: 4 紙とも 0 行) | 19 本 再生成 + build script の awk に `sub(/\r$/,"")` 一語(raw/64_build_script.patch) | 冪等(run1=run2・raw/65_idempotent.txt)・4 紙の front matter が元紙と同一(raw/67: FM_IDENTICAL ×4) |
| Shell Script Linting | Run shellcheck on scripts/ | SC2148 ★一件のみ★ = scripts/checks/karo_mac_gate7.sh の冠無し(raw/30_shellcheck_scripts.out 7 行・lib は 0 件 rc0) | 一行目に `#!/usr/bin/env bash` | `-S error` rc0・既定 level でも 0 件(raw/60_gate7_shellcheck_all.out 0 行) |
| Unit Tests (ubuntu / macos) | Run root-level tests(両 OS 同じ step) | ★GNU 字面ではない★(ubuntu にも落ちる・bats 紙に date/stat/base64 は 0)。真因 = 古い test 5 類(LB-07 / stop hook fixture / get_agent_model 既定 / T-CRESET-003 / md5sum)+ 裁の要る 3 類(§18 役名 lib・撤回済 MDV2 試作の test・裁が許した skip) | test 5 紙を現行の契約へ(下表 ㋔)。md5sum→shasum | root 8→**7** 落・unit 12→**7** 落・selfwatch 0 落(skip 1)。★残る 14 落 + skip 1 は裁の要る物(㋕)ゆゑ unit-tests は本 PR だけでは青に成らぬ★ |

∴ 本 PR(一本・押さず)で ★build-check と shellcheck は青に成る見込み★(Mac の出目)。unit-tests は ㋕ の裁が下りるまで赤の儘。e2e / integration は unit-tests に依存ゆゑ手元では測れず(inotifywait が此の Mac に無い)。

## ㋑ 測り方(器と環境)

- CI の定義 = `.github/workflows/test.yml`(origin/main)。unit-tests は ubuntu + macos の matrix、macos は `brew install bash coreutils` + gnubin を PATH 先頭へ(L33-37)。∴ ★CI では両 OS とも bash 5 + GNU coreutils★。
- 此の Mac の素 = bash 3.2.57 / BSD 器 / shellcheck 無 / bats 無 / .venv 無。∴ 同一環境を ★~/wt/tools★ に置いた(PATH・brew・system に一指も触れず・戻し = `rm -rf ~/wt/tools`): bats-core 1.14.0 + bats-support + bats-assert(git clone)/ shellcheck 0.10.0(静的 binary・darwin.aarch64)/ bash 5.2.0(source build・prefix ~/wt/tools/bash52)。己の樹に `.venv`(pyyaml 6.0.3・gitignore 済)と `tests/test_helper/{bats-support,bats-assert}`(CI と同じ clone・gitlink 160000 の空 dir を満たした・commit せぬ)。
- 環境 三態: (甲) bash 3.2 + BSD = 此の Mac の素 / (乙) bash 5.2 + BSD / (丙) bash 5.2 + gnubin + .venv ≈ CI。数を書く時は環境名を併せ書く。
- 刻: raw/40〜44・80〜94 の `*_koku.txt`。rc は `$?` を pipe 無しで取り `*.rc` に刷つた。

## ㋒ build-check(生成物)

1. 差 = 19 file(raw/20_build_changed_files.txt・20_build_diffstat.txt: 20 files +1111 −872 は ERR-EKARTE を含む git の数)。sha16 の前後 = raw/21_sha_before_after.txt。中身は persona 名の purge(家康→軍師main 等 16 行)+ role/common/cli_specific の parts の更新。
2. ★front matter 消失★: 元紙 4 本の一行目 = shogun `2d2d2d0d0a`(CRLF)/ karo・ashigaru・gunshi `2d2d2d0a`(LF)。mac awk で `/^---$/` を数へると shogun 0 行・karo 191・ashigaru 138・gunshi 137。CRLF は commit 9a3ca573 の親でも 402 行 ゆゑ 07-10 以前から。origin/main の生成物 shogun.md には front matter が在る(05-08 c384a564 に生成)= ★其の後に元紙が CRLF に成り、以来 build を走らせれば消える状態であつた★。家老の ⑴「差は実体」は正しいが、此の欠けは含まれて居らぬ。
3. 直し(scripts/build_instructions.sh sha16 dfd91a92 → a1aea23e・raw/64_build_script.patch +2 −1):
   `awk '{sub(/\r$/,"")} /^---$/{...}'` ―― pipe を使はぬ。★初版は `tr -d '\r' < f | awk` で、awk が `exit` した後 tr が SIGPIPE を受け `set -euo pipefail` に殺され 6 紙目で止まつた(raw/62_rebuild_run1.rc: rc=141)。★捨てて v2 にした。★ shellcheck -S error rc0。
4. 後: run1 rc0・run2 rc0・20 file の sha256 同一(raw/65_idempotent.txt: IDEMPOTENT_20)。front matter = 4 紙とも 68/191/138/137 行で、元紙の CR を剥いだ front matter と `diff` 一致(raw/67_frontmatter_identity.txt: FM_IDENTICAL ×4)。origin/main の生成物 shogun.md の閉ぢ `---` も 68 行目 ゆゑ形は不変。
5. ★元紙の CRLF は直して居らぬ★(instructions/*.md は正本・変更統制)。CR を持つ元紙 = instructions/shogun.md(413)+ roles 4 本 + common 2 本 + cli_specific 4 本(raw/… 本紙 ㋖ に列挙)。生成物の胴は CRLF の儘(origin/main の生成物も 433 行 CR・同じ)。LF へ揃へるかは裁。
6. ★Linux 同一は断じ得ぬ★: awk の `sub(/\r$/,"")` は gawk / mawk / onetrue-awk いづれも通る字面だが、実走は此の Mac(awk 20200816)のみ。

## ㋓ shellcheck

- 母數 = `find scripts lib -name '*.sh' -type f` = 71 本。冠の無い紙 = 1 本(karo_mac_gate7.sh)= 家老の数と一致。
- CI と同じ命令(`find lib … -exec shellcheck -x -S error {} +` / `find scripts …`): lib rc0(0 行)/ scripts rc1(7 行 = SC2148 一件)。raw/30_*。
- 冠 `#!/usr/bin/env bash` を一行目に足す(sha16 41e44eba → 3a849873・21→22 行)。後 `-S error` rc0、既定 level でも 0 件 ゆゑ「冠を足すと他が鳴く」は起きなかつた(raw/60_*)。
- ★~/bin/karo_mac_gate7.sh(家老の配布写し)は origin/main と同一(diff rc0)で冠無しの儘★ ―― 家老の物ゆゑ触らぬ。repo の紙と写しが一行違ふ事を記す。

## ㋔ unit-tests(bats)

### 環境×紙×出目(before = origin/main の儘 / after = 本弾の当て後)

| 環境 | root(5 紙) | selfwatch | unit(15 紙) | raw |
|---|---|---|---|---|
| (甲) bash3.2+BSD・venv 無 before | ok16 / **not ok 21**(setup_file 2 = venv 無・§18 19 = `declare -A` が bash3.2 で落ちる) | ― | ― | 40 |
| (丙) bash5+gnubin+venv before | ok50 / **not ok 8** | ok19 / not ok 0 / skip 1 | ok326 / **not ok 12** | 42・43 |
| (乙) bash5+BSD+venv before | ok50 / not ok 8(同じ集合) | ― | ok323 / not ok 15(+T-WRC6 ×3 = timeout 無し・338/358 で中断) | 44 |
| (丙) after(★最終★) | ok51 / **not ok 7** | ok19 / not ok 0 / skip 1 | ok331 / **not ok 7** | 90・94 |

(甲) の 21 は環境の差(bash 3.2・venv 無)であり CI の因ではない。(乙)⇔(丙) の root は同集合 ゆゑ ★root の落ちは GNU 器の有無に依らぬ★。

### 直した test 5 紙(理由と根)

| 紙 | 落ち | 根(何時・何が変はつたか) | 当て | 後 |
|---|---|---|---|---|
| tests/test_inbox_expiry_supersession.bats LB-07 | 二度目の get_unread_info に clear_command が残る | W201 根治(scripts/inbox_watcher.sh 23d09034・2026-08-06): 抽出時に specials を read にせず、送れた後 `mark_message_processed` で印す契約へ | 一度目と二度目の間に `mark_message_processed msg_clear` を置く(契約の実の commit 点で「一度だけ消費」を検める) | ok |
| tests/unit/test_stop_hook.bats T-HOOK-008/010(009 は fixture のみ) | block JSON が出ぬ | 06-04 f724fe9c: hook の未読 grep を `^  read: false$`(2 字下げ)に錨止め(phantom block loop 根治)。fixture は 4 字下げ(`  - id:`)= inbox_write.sh(yaml.dump indent=2)の実の形と違ふ(実箱 karo-mac.yaml: 2 字 25 / 4 字 0) | fixture 3 塊を実の形(`- id:` 0 字・鍵 2 字)へ | ok |
| tests/unit/test_cli_adapter.bats get_agent_model ×2 | shogun→opus / karo→sonnet を期待 | lib/cli_adapter.sh 25e6ec99(2026-08-03): 既定 shogun→fable / karo→opus / gunshi→opus | 期待を lib の現行既定へ(model の既定そのものは触らぬ) | ok |
| tests/unit/test_send_wakeup.bats T-CRESET-003 | rc≠0 | ⑴ RC-1 cure(fc3a5b0b・06-07): busy なら defer rc1 ―― harness は test_agent の idle 旗しか作らず ashigaru3 は busy 扱ひ ⑵ 送つた後の cooldown(LAST_CLEAR_TS・T-BUSY-005)で post-reset nudge が skip され rc2(L923 の契約: 0=送つて nudge / 2=送つたが busy) | ashigaru3 の idle 旗を置く + `status` を 0 又は 2 に(送つた證は MOCK_LOG の `send-keys.*/clear` で見る・不変) | ok |
| tests/unit/test_build_system.bats L281/286 | (CI は落ちぬ)md5sum は GNU | 可搬化(家老 ⑶) | `shasum -a 256`(BSD/GNU 両方に在る) | ok |

### GNU 字面の表(家老 ⑶)―― raw/55_gnu_literals_table.md(20 行)・raw/50_gnu_literals.tsv

- 21 紙を `timeout / date -Is|-d / stat -c / base64 -w / md5sum / sha*sum / readlink -f / sed -i / grep -P / mapfile / declare -A / seq / realpath …` の網で歩いた(器 = raw/50 を作つた grep -nE・raw/50_bats_files.txt 21 本)。
- 出た類 = **timeout 14 行 / 6 紙**(内 stub 定義 `timeout() { shift; "$@"; }` + `export -f` が 6 行・実呼びが 8 行)/ **md5sum 2 行 / 1 紙**(★直した★)/ seq 2 行(BSD にも在る)。
- ★家老の `date -Is`=3 / `stat -c`=2 / `date -d`=1 / `base64 -w`=1 は bats 21 紙では **0**★(`grep -nE 'date -Is|stat -c|date -d|base64 -w' tests/*.bats tests/unit/*.bats` = 0 行)。同じ字面は scripts/ lib/ の .sh に 28 file 在る(raw に刷らず・本紙の数)。家老が bats でなく scripts を数へたか、表の写し違ひか ―― 家老の器を見て居らぬゆゑ断じぬ。
- timeout の実呼び 8 行(test_karo_second_send_iincho 139/232・test_ntfy_ack 107・test_send_wakeup 502/525・test_watcher_rc6_integration 74 等)は ★CI では両 OS に在る★(ubuntu 既設・macos は test.yml L33-37 の coreutils)ゆゑ CI 赤の因ではない。(乙) bash5+BSD では T-WRC6 ×3 が落ち bats が 338/358 で中断する(raw/44)。可搬化するなら shim(`command -v timeout || timeout(){ …perl/python… }`)が要るが、CI の赤とは別件 ゆゑ本弾では直さず記す。

## ㋕ 裁の要る残り(★blocker 4 点セット★)―― 本 PR では直して居らぬ

### ⓐ §18 役名 lib(root 7 + unit 3 = 10 test)

- root_cause: `lib/_section18_roles.sh` の配列は `hideyoshi / ashigaru1-3 / ieyasu / takenaka`(6)・`maeda / ashigaru5-8`(5)= 05-08 5be193c3/94833a61 の persona 内部 id。test(05-07 0edef778)・Python SoT(tests/test_section18_migration.py L40-41: karo/gunshi…)・呼び手(scripts/switch_cli.sh L104 が `$agent_id` = 役名を渡す)は ★役名★。07-20 18c95fcf の purge は註だけ替へ識別子を残した。★実行時にも `section18_mainpc_pane_index karo` は rc1、hideyoshi は 0★(raw/51_section18_runtime_probe.txt)―― 05-08 以来 main は此処で赤。
- owner: 委員長(役職・pane 構成 = 変更統制 ⑷)。persona id は live code 20 file に及ぶ(raw/52_persona_id_blast_radius.txt: config/settings.yaml 5・pane_identity.sh 6・inbox_alias_integrity.sh 3 …)。
- next_safe_action: 案 A = lib の識別子を役名へ改め alias を逆向き(hideyoshi→karo)に(DD-157/162 の向き・呼び手と SoT に合ふ・raw/52 の 20 file を併せ検める)。案 B = test を lib に合はせる(persona id を test が断言する=canon に逆行)。當席は A を薦めるが据ゑぬ。
- human_GO_required: yes。

### ⓑ 撤回済 MDV2 試作の test(unit 4 紙: test_codex_guard / test_dead_letter / test_dedup / test_safe_nudge)

- root_cause: 的 `scripts/message_delivery_v2/*.sh` は 05-08 94f15e18「archive 移動撤回 — 元の安定基盤復元 + v2 試作 archive 保管」で `scripts/archive/message_delivery_v2_full_20260508/` へ。test と helper(tests/test_helper/mock_tmux_pane.bash L117 も同 path を cp)は旧 path の儘。★archive へ向けて試した★: setup は通るが helper が別 path を写して T-CG ×6 / T-SN が落ち、test_dead_letter T-008 は挙動差で落ちる(raw/80: 13 落)ゆゑ★戻した★(git checkout・差 0)。
- owner: 家老mac → 委員長(test の削除/退避は範囲の裁)。
- next_safe_action: 4 紙 + helper の MDV2 節を tests/archive へ退避(CI の `bats tests/unit/` の外へ)。撤回された試作を live test で守る意味は無い。
- human_GO_required: yes。

### ⓒ 裁が許した skip と CI の SKIP=FAIL の衝突(selfwatch skip 1)

- root_cause: tests/agent_selfwatch.bats TC-FR-003 は総監督裁 seq293394 で「TC-FR-003b に取つて代はられた」として skip 指定、L360-364 の守り test が ★其の skip が丁度一つ在る事★ を断言する。test.yml の「Verify zero unexpected SKIPs」は `CI environment` を含む skip しか除かぬ ゆゑ此の skip で job が落ちる。★當席は一度 TC-FR-003 を消して走らせ(raw/83・92: 守り test が落ちた)、裁に背くと判じて戻した(raw/94: 19 ok / skip 1)。★
- owner: 総監督(seq293394 の裁)/ 委員長(test.yml = CI 構成)。
- next_safe_action: 案 A = test.yml の除外語に `SUPERSEDED by` を足す(CI 構成の改め)。案 B = 裁を改め TC-FR-003 と守り test を共に消す。案 C = skip 文言に `CI environment` を足す = 検めを欺く ゆゑ ★薦めぬ★。
- human_GO_required: yes。

## ㋖ 触れなかつた物・別の疵(家老 ⑷ を含む)

- `docs/runbooks/ERR-EKARTE-001.md`: 家老 ⑷ の通り worktree が起点で ` M`。git には大文字 `ERR-EKARTE-001.md`(blob e6de627b)と小文字 `err-ekarte-001.md`(blob de00cbd9)の ★二本★ が在り、disk は小文字一本(raw/70)。★commit に混ぜて居らぬ★(`git add -f` の名指し)。
- 元紙の CRLF(instructions/shogun.md 413 / roles: ashigaru 105・gunshi 206・karo 292・shogun 168 / common: forbidden_actions 44・protocol 129 / cli_specific: claude 92・codex 231・copilot 176・kimi 392 行)。.gitattributes は `*.sh` のみ LF 指定。正本 ゆゑ不触・裁。
- `~/bin/karo_mac_gate7.sh` の冠無し(家老の写し)。
- `.gitignore:7` の `*` allowlist ゆゑ commit は `git add -f` で名指し。tests/test_helper の clone 2 dir・.venv・~/wt/tools は commit せぬ。
- 監査提出(km-164/165)は本弾の中で己の手で送出した(㋓ の器): seq 331857/331858/331860/331861/331863/331864(gunshi-mac・parent_seq 330706・各 3 通・276〜300 字・raw は letters/)。★送つた胴の読み返し(第八の番人)は `sb read seq` が karo-mac の入口(~/bin/sb)ゆゑ當席の器では出来ず、送出器の echo(seq)と dry-run の封筒(letters/*.dryrun.txt)で代へた。★

## ㋗ 意味せぬ事

- 「build-check と shellcheck は青に成る見込み」は Mac の出目であり、Linux での実走は無い(CI log も読めぬ)。
- 「root 7・unit 7」は (丙) 環境の数であり、macos-latest の brew bash / coreutils の版が此の Mac の 5.2.0 / gnubin と同じである事は測つて居らぬ。
- 直した test 5 紙は「現行の実装の契約」に合はせた。★実装が正しいかは検めて居らぬ★(get_agent_model の既定 fable/opus・W201・cooldown の契約)。
- GNU 字面表は grep の網の内側だけを写す。網に無い GNU 字面(例: `sort -V` は網に在るが `ls --color` の類)は数へて居らぬ。
- e2e / integration job は測つて居らぬ(inotifywait 無し)。unit が青に成つても其処で落ちる可能性は残る。

## 宣⇔實

- 宣ETA = 14:00(着手便 12:48:26 で宣)。實 = 納め便の刻(紙の外)。
- 疵: ⑴ 着手便が着手(12:30)から 18 分遅れた(測りを先に走らせ便を後にした)。⑵ build の直し初版が SIGPIPE で script を殺した(rc141)。⑶ test 紙の python 当てを text mode で書き、CRLF の紙(test_build_system.bats)を丸ごと LF に変へた(578 行差)―― 戻して bytes で当て直した。⑷ cli_adapter の錨が二箇所に当たり止まつた(書く前に止まつたゆゑ紙は無傷)。⑸ MDV2 を archive へ向けて試し戻した。⑹ TC-FR-003 を消して守り test を落とし戻した。⑺ zsh の語分割無しで bats の引数が一語に成り 0 走で死んだ(bash -c へ)。
