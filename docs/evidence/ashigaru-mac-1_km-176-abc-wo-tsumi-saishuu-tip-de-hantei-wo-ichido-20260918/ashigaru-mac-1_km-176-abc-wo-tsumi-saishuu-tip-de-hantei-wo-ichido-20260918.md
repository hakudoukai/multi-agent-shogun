# km-176 ―― km-167 の ⓐⓑⓒ を枝の上へ積み、最終 tip で判定を一度取る

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-176-abc-wo-tsumi-saishuu-tip-de-hantei-wo-ichido-20260918`(裁 seq332367 ⓐⓑⓒ 可・裁 seq332511 最終 tip で PASS 一回・板 94c61e26・家老mac 据ゑ 17:40)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T18:00:44+0900 / 着手便 17:55(宣ETA 19:30)/ 前の測り 17:55:52 / 後の測り 17:57〜17:59
- 枝 = `ashigaru-mac-1/km-167-ci-20260918`(己の樹 ~/wt/a1-km167-ci)。積む前の tip = `d168a6af46245af2342a9235cce7a85cd90c99d6`(tree f4a3e1a0db1d89f46b8eca1ff44ae5421ad7a4ed・委員長代行 push 済・PR#31 head)。★積んだ後の tip/tree は commit の後に納め便へ書く(紙は己の commit sha を書けぬ)。押さず。★
- 環境 = km-167 (丙) と同じ: bash 5.2 + gnubin + bats-core 1.14 + shellcheck 0.10(~/wt/tools)+ 己の .venv(pyyaml)。本弾で .venv に ★pytest 9.1.1 を足した★(raw/03・己の worktree 内・gitignore 済・戻し = rm -rf .venv)。
- 「前」の全走は同 tree f4a3e1a0 の km-167 raw/90(root 51/7・selfwatch 19/0 skip1・unit 331/7)を引く。ⓐⓑⓒ 各々の的を絞つた前は本束 raw/10〜31 で今日測り直した。

## ㋐ 結語

★三手とも据ゑ、CI 四 job の手元模走は悉く rc0 に成つた(Mac の出目)。★

| 手 | 前(件数・rc) | 後(件数・rc) | raw |
|---|---|---|---|
| ⓐ §18 lib 役名化+逆 alias | tests/test_section18_roles.bats ok12/**not ok 7** rc1・tests/unit/test_switch_cli.bats ok19/**not ok 3** rc1・実行時 `section18_mainpc_pane_index karo` rc1 | ok19/0 rc0・ok22/0 rc0・karo→0 gunshi→4 rc0(hideyoshi/ieyasu は rc1 に転じ alias は karo/gunshi を返す) | 10・11・40・41・43 |
| ⓑ MDV2 試作 test 4 紙 退避 | bats 4 紙 = setup_file failed ×4 rc1(tests/unit に在り CI が走らせる) | tests/unit に無し(ls rc2)・CI の glob `tests/*.bats tests/unit/*.bats` に archive 0 件・退避先で走らせれば今も 4 落(★消して居らぬ★) | 20・44・45 |
| ⓒ 除外語 SUPERSEDED | selfwatch skip1・CI 網(`CI environment` のみ)で数へると **1**(job 落) | 網 `CI environment\|SUPERSEDED` で **0**・TC-NFR-008 は残り(grep 1)・skip 行は不変 | 30・31・46・47 |
| 全走(後) | root 51/7・selfwatch 19/0 s1・unit 331/7(km-167 raw/90) | ★root 58/0 rc0・selfwatch 19/0 skip1 rc0・unit 334/0 rc0★・CI の SKIP 検め(新網)= 0・build-check rc0(生成物差 0)・shellcheck lib/scripts rc0 | 50〜56 |

unit の母數 338→334 は ⓑ で setup_file 4 件が tests/unit の外へ出たゆゑ(落ちが 7→0 の内 4 は此れ、3 は ⓐ の switch_cli)。root の 7→0 は悉く ⓐ。

## ㋑ ⓐ の中身(lib/_section18_roles.sh・sha256 7efbaa51… → 後は臺帳)

- 配列: MAINPC_PANE_ORDER = hideyoshi/a1/a2/a3/ieyasu/takenaka(6)→ ★karo/a1/a2/a3/gunshi(5)★。SECONDPC_PANE_ORDER = maeda/a5/a6/a7/a8(5)→ ★a5/a6/a7/a8(4)★。ALL_ROLES = 12 → ★10★(T-004 の断言と一致・Python SoT tests/test_section18_migration.py L40-41 と一致)。
- alias(★逆向き★): 旧 [karo]=hideyoshi/[gunshi]=ieyasu/[shogun]=nobunaga → 新 ★[hideyoshi]=karo/[ieyasu]=gunshi/[nobunaga]=shogun★。役名は identity。maeda/takenaka は配置表に役名が無いゆゑ identity で残す(消さぬ)。
- ★可逆★: 変へたのは配列 2 本と alias map の向きのみ・関数の本体は不変・pane 構成(tmux)は不触。戻し = 此の commit を revert する。★raw/60_a_lib.patch・61_c_test_yml.patch は写しであり、門(條②③)の為に行末の空白と CR を剥いだゆゑ逐語では当たらぬ(unified diff の空 context 行は末尾空白・test.yml は CRLF)。逐語は commit の `git show`。★
- ★消費者の検め★: scripts/checks/pane_identity.sh は actual/expected の両側を `section18_resolve_alias` で正規化して比べる(L22)ゆゑ向きが変はつても同値。bats(tests/checks/test_pane_identity.bats)は fixture fake_tmux.sh に -x が無く前後とも setup_file 落(raw/12・42 = 本弾と無関係の既存疵)。∴ +x の写しを mktemp に置き pane_identity.sh を直に走らせた: ★前 rc0 DRIFT 0 / 後 rc0 DRIFT 0★(raw/14_*)。switch_cli.sh(L104)・agent_status.sh(L168)・ratelimit_check.sh(L51)は配列を役名として使ふ ∴ 役名化で正しく解ける(switch_cli の resolve_pane 3 落が青に成つた事が證)。
- ★残る疵(裁の外・本弾で触らず)★: Python 版 shim/hakudokai/_section18_roles.py は今も persona 名(nobunaga/hideyoshi/ieyasu/takenaka/maeda)。pytest の ShellHelper 3 件は前 ★落→後 通★、SoT drift 6 件は前 4 落→後 ★6 落★(shell が役名に成り Python が persona の儘ゆゑ差が広がつた・raw/13・49)。pytest は CI(test.yml)に無い(grep 0)ゆゑ CI の色には響かぬが、Python 版も役名へ揃へるかは裁(変更統制 ⑷・lib 冠の註「Python 版と同時更新」に反して居る)。

## ㋒ ⓑ の中身

- `git mv` で tests/unit/{test_codex_guard,test_dead_letter,test_dedup,test_safe_nudge}.bats → tests/archive/(履歴保つ・R 4 本)。README.md 1 行「撤回済・的は archive」(裁の字面)。
- tests/test_helper/mock_tmux_pane.bash L117 の MDV2 節と tests/unit/test_safe_nudge_doppler.bats・test_watcher_rc6_integration.bats の MDV2 参照は ★触れて居らぬ★(後の unit 334/0 ゆゑ落ちて居らぬ)。

## ㋓ ⓒ の中身

- .github/workflows/test.yml L94-97: `grep -cv "CI environment"` → `grep -cEv "CI environment|SUPERSEDED"`(+註 2 行)。★元紙は CRLF ゆゑ bytes で当て CR を保つた(300 行 CRLF 不変)★。yaml.safe_load 通。
- TC-NFR-008(skip が丁度 1 で文言 SUPERSEDED by TC-FR-003b)は残す。∴ 裁 seq293394 の skip と SKIP=FAIL は両立する。

## ㋔ 意味せぬ事・測れぬ物

- 「rc0」は Mac(bash 5.2.0・gnubin・bats 1.14.0)の出目。Linux runner・macos-latest の brew 版での実走は無い。CI log は 403 で読めぬ(km-167 と同じ)。
- e2e / integration job は測つて居らぬ(inotifywait 無し)。
- PR#31 の本文へ事後報を書く手(gh)は當席に無い(token 無効・gh 不触)。∴ 本文へ足す文を ★letters/pr31_body_addendum.md★ に置き、起票者(委員長)へ貼付を請ふ。

## ㋕ 疵

⑴ 着手便が 300 字を三度超え(331/310/304)四度目で 300 丁度 ⑵ test.yml の初回 patch を LF 前提で書き CRLF の assert で止まつた(紙は無傷・bytes で当て直し)⑶ zsh で `echo ===` が `=` 展開に食はれ後の pytest が走らず、走らせ直した ⑷ pytest を .venv へ足した(己の scratch・宣す)⑸ 門の前の正規化で patch 写し 2 本の CR/末尾空白を剥いだ(㋑ に記す・逐語は git show)。臺帳と門の一巡目は `_manifest.round1.txt`・`_gate.round1.*` に残す。

## 宣⇔實

宣ETA 19:30。實 = 納め便の刻(紙の外・18:1x 見込み = 宣の下)。
