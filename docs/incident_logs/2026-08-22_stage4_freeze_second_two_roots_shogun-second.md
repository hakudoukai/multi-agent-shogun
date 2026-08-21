# 第4段 freeze ―― ★実行 proc 直読による Second の現 root ★二本★★／★staging `0.20.4`（source `6a3d50c`）は ★現に 在り★★／**★★訂 ―― 己の前紙 `a91aaa7`「`0.20.4` の実体 `0` 件」は ★誤り★ に御座る★★**

- **役**: 将軍second（`shogun-second`・pane `%12`・pid `1924984`）
- **as_of**: 本紙の測りは 悉く **`2026-08-22T05:13:54`〜`05:16:06 +0900`**（★測りと同じ呼び出しの中で `date` に問ひ申した★）
- **枝**: `feat/dd169-d006-conditional-exception` / 直前 HEAD `a91aaa7f52695de1d18d406dc86445a3aae7c4f2`
- **上位令**: Commander `seq203838` ＋ **`seq203838` correction**（`05:05:03`）／本部長 `nonce=HB-20260822-0505-STAGE4`（`05:04:38`）／委員長 `seq203847`・`seq203853`
- **本紙の性格**: ★★便を出す ★前★ に freeze（新条の通り）★★・★測りは 悉く read-only★

---

## 〇 ―― ★★★★★訂 ―― 己の前紙が 誤り申した★★★★★

★己は `a91aaa7`（`2026-08-22_seq203847_dai3go_recheck_and_stage4_baseline_shogun-second.md` §二）にて 斯く 書き申した★

> ★「目標 `0.20.4` ―― ★当PCに 実体 `0` 件★」「述語 ＝ `grep -rl 'version = "0.20.4"' hermes-roles hermes-agent hermes-runtimes hermes-departments` ⇒ `0` file」「対照 `0.20.0` ⇒ `6` file ★∴ `0.20.4` の `0` は 「掃けなんだ」に非ず 「★在らぬ★」★」★

★★之は ★誤り★ に御座る★★

| | 実測（as_of `2026-08-22T05:14:25+0900`） |
|---|---|
| 述語 | `grep -rl 'version = "0.20.4"' /home/hakudokai --include=pyproject.toml` |
| **結果** | **★`/home/hakudokai/hermes-staging-0.20.4/hermes-agent/pyproject.toml` ―― `version = "0.20.4"`★** |

★★誤りの 因 ―― ★二重★★★

| # | 因 |
|---|---|
| **㊀** | ★★己の絞りが `hermes-roles hermes-agent hermes-runtimes hermes-departments` の ★四つに 閉ぢ居つた★★ ―― ★staging 樹は 其の外★ |
| **㊁** | **★★己が ★昨夜 己の手にて 作りたる樹★ を ―― ★数へ落とし申した★★★**（`PROVENANCE.txt` に **`extracted_by=shogun-second pid 1924984`** ＝ ★己★） |

★★∴ 之は ―― ★己の 第一の根（母集団を 先に 置かず）の ★五度目★★★
★而して ―― ★己は 「対照 `6` 件」を 添へて ★物差しの生存★ まで 示し ―― ★強く★ 書き申した★
⇒ ★★★己の條「★零には 絞りを添へよ★」は ―― ★絞りを 明記せよ★ の意にて ―― ★絞りを ★広げよ★ の意に あら申さなんだ★★★

> ## **★★★★★★條 ―― ★『在らぬ』と断ずる前に ―― ★絞りを 一段 広げて ★撃ち直せ★★。★対照が 生きて居る事は ―― ★窓が 足りて居る事★ を 意味し申さぬ★★★★★★★**

> ## **★★★★★條 ―― ★己が 為したる事も ―― ★記憶に非ず 紙より 引け★★。★『不可逆の型は 紙の逐語より引け』は ―― ★己の過去の手★ にも 及び申す★★★★★**

★★∴ 訂の宛先 ―― ★委員長殿（`seq203893` にて 誤つた数を 現に 手に持たれ申す）★ ―― ★便を以て 直ちに 出し申す★★

---

## 一 ―― ★★実行 proc 直読 ―― Second の 現 root ＝ ★二本★★★（as_of `2026-08-22T05:13:54`〜`05:16:06+0900`）

★述語 ―― `ps -eo pid,ppid,lstart,args` にて 列挙し ―― ★argv は `/proc/<pid>/cmdline` を `tr '\0' ' '` にて ★截らず★ 取り直し申した★（★己の條「★出力を截るな★」「★process 本数は 嘘をつく ⇒ ★列挙せよ★★」★）
★pane の割当は `tmux list-panes -a -F '... #{pane_id} pid=#{pane_pid}'` にて ★索引に非ず `pane_id` にて★ 取り申した★

### root ㋐ ―― **`/home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3`**

| 役 | pane | leader PID | 子 PID | 起動 | argv（逐語・截らず） |
|---|---|---|---|---|---|
| **本部長** | **`%38`**（`hermes-honbucho:0.0`） | **`86872`** | `86886` | `Sat Aug 22 04:44:32 2026` | `/usr/bin/doppler run --project openhands --config dev -- /home/hakudokai/.local/libexec/dentalbi/promote_supabase_rotation_key.sh /usr/bin/env -u ANTHROPIC_BASE_URL -u LLM_BASE_URL -u LLM_MODEL -u OPENAI_BASE_URL <root>/venv/bin/python <root>/hermes --continue` |
| **軍師second** | **`%24`**（`hermes-gunshi-second:0.0`） | **`836658`** | `836838`・`837082`(node)・`837090`(tui_gateway) | `Wed Aug 12 14:51:32 2026` | `/usr/bin/doppler run ... -- /usr/bin/env HOME=/home/hakudokai/hermes-roles/gunshi-second-hermes HERMES_HOME=<同> <root>/venv/bin/python <root>/hermes --tui --continue` |

★★∴ ★本部長 ＋ 軍師second ＝ ★同一の gunshi role-local root★★ ―― ★本部長殿の申告と 己の実測が ★一致★★★
★裏書きの取り方 ―― ★`pane_pid` にて `%38`→`86872`・`%24`→`836658` を 引き ―― ★argv の `HOME` 上書きの 有無★ に ★依らず★ 確と割り申した★（★`86872` は `HOME` を上書きせず ⇒ ★argv のみにては 決し得なんだ★）

### root ㋑ ―― **`/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3`**

| 役 | pane | leader PID | 子 PID | 起動 | argv |
|---|---|---|---|---|---|
| **ashigaru-second-7** | ★pane 見えず（`tmux list-panes -a` に 出で申さず）★ | **`1156226`** | `1156252`・`1156384`(node)・`1156392`(tui_gateway) | `Wed Aug 12 16:47:22 2026` | `/usr/bin/doppler run ... -- /usr/bin/env HOME=/home/hakudokai/hermes-roles/ashigaru-second-7-hermes HERMES_HOME=<同> <root>/venv/bin/python <root>/hermes --tui` |
| （附）a7 watcher | ―― | **`1220779`** | ―― | `Wed Aug 12 17:11:06 2026` | `/usr/bin/python3 /home/hakudokai/hermes-roles/ashigaru-second-7-hermes/bin/ashigaru_second_7_hermes_watcher.py` ★★root の ★外★（`bin/` 直下）―― ★cutover の 対象外★★ |

★★∴ ★a7 root は a7 のみに 効き申す★★ ―― ★Commander correction の申さるる通り★

### ★★共有 `~/hermes-runtimes` を 参照する proc ―― ★`0`★★★

★★∴ ★Commander correction「`Do not claim ~/hermes-runtimes`」は ―― ★己の実測にて 裏書き★★★
★∴ ★己の前紙が 第4段の対象として 並べたる「共有runtime」の行は ―― ★参照者 `0` の樹★ ゆゑ ★対象に あら申さぬ★★（★之も 亦 ―― ★『樹に在る版』を 『役が 現に参照する版』として 書きたる★ 誤り★）

### ★（附）`/home/hakudokai/hermes-agent/venv` を 参照する proc ―― `2`★

| PID | argv |
|---|---|
| `2492958` / `2492971` | `... /home/hakudokai/hermes-agent/venv/bin/python /home/hakudokai/hermes-departments/honbucho/bin/honbucho_downlink_watcher.py` |

★★`/home/hakudokai/hermes-agent` は ★空殻★（`pyproject.toml` 無し・`venv` のみ）★ ⇒ ★版を持た申さぬ★ ⇒ ★第4段の対象外・而して ★存在を 申告 申す★★

---

## 二 ―― ★★現 root の 版（dist-info 実体にて）★★

| root | `pyproject.toml` | `sha256` | `site-packages` dist-info |
|---|---|---|---|
| gunshi role-local | `version = "0.20.0"` | `b83b6f40f05c8e4fab0d6d6d8a791d7216f712ae252787740057848ac704fe21` | **`hermes_agent-0.20.0.dist-info`** |
| a7 role-local | `version = "0.20.0"` | **`b83b6f40…`（★同一★）** | **`hermes_agent-0.20.0.dist-info`** |

★∴ ★二本の root の `pyproject.toml` は ★byte identical★★（★版は ★名★ にて判ぜず ★実体★ にて判ぜよ ―― ★dist-info まで 降り申した★）

---

## 三 ―― ★★staging `0.20.4` ―― ★現に 在り・provenance 済★★★

| 項 | 値 |
|---|---|
| 樹 | **`/home/hakudokai/hermes-staging-0.20.4`**（`mtime 2026-08-21 23:28:56`） |
| source | `pyproject.toml` ＝ **`version = "0.20.4"`** / `sha256 = 1f928b1560b0669291b3f7d562aa78c99ac4f927375939ca97fd3c3e7494cb91` |
| **dist（実体）** | **`/home/hakudokai/hermes-staging-0.20.4/venv/lib/python3.12/site-packages/hermes_agent-0.20.4.dist-info`** |
| install | `full_install.log` 末尾 ―― `Successfully installed ... hermes-agent-0.20.4` |
| **`PROVENANCE.txt`** | `sha256 = 17296faa010d208c0ebbfbe255c06c6ea5dd448ed84b508706661c45a5da052d` |

★★`PROVENANCE.txt` ―― ★逐語（全五行）★★★

```
source_repo=https://github.com/NousResearch/hermes-agent.git
source_commit=6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f
extracted_from=/home/hakudokai/hermes-runtimes/hermes-agent-v2026.8.3 (read-only, git archive, network 0)
extracted_by=shogun-second pid 1924984
as_of=2026-08-21T23:18:29+09:00
```

★★∴ ★本部長殿の申さるる `source=6a3d50c` は ―― ★`6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f` の 頭 七字★ にて 一致★★
★★∴ ★委員長 `seq200891` の ★provenance blocker★ は ―― ★`2026-08-21T23:18:29` に 己の手にて 解け居り申した★★（★`copy/rsync` に非ず ―― ★`git archive`・network `0`・read-only★）
★★∴ ★己は 己が 解きたる blocker を 忘れ 「実体 `0`」と 書き申した★★ ―― ★上 〇 の 訂の通り★

★（註）staging 樹は ★git 樹に非ず★（`git -C ... log` ⇒ `fatal: not a git repository`）―― ★`git archive` にて 抜きたるゆゑ★。★∴ 由来の證は ★`PROVENANCE.txt` ただ一枚★ に懸かり申す★

---

## 四 ―― ★★cutover の 型 ―― ★二本の root は 型が 異なり申す★★★

| root | 切替の口 | 可逆や |
|---|---|---|
| **a7 role-local** | **★`/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/run/active-hermes-runtime`★**（`81` B・平文 一行・`sha256 = 56be6edf44c9c93829b64b5d664f4c78758c6079116420f1aa1994949ea9d90b`）<br>現の中身 ＝ `/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/run/hermes-agent-v2026.8.3` | **★可逆 ―― 旧 path を 書き戻すのみ★** |
| **gunshi role-local** | ★同種の pointer ★無し★★（`run/` の中は `hermes-agent-v2026.8.3` と `install-home` の 二つのみ）<br>⇒ ★切替は ★launcher（`hermes-departments/honbucho/bin/hermes-honbucho` 等）★ に 依ると 推せらる★（★印・推論） | ★★己の枷「hermes系 file 改変禁」に 掛かり申す★★ |

★★∴ ★二本は ★同じ手順にて 切替へ得申さぬ★★★

### ★rollback root（保持）★

| root | rollback |
|---|---|
| a7 | ★現 `hermes-agent-v2026.8.3` を ★一指も触れず 残す★ ＋ `active-hermes-runtime` の 旧一行（上記 sha にて 凍結済） |
| gunshi | ★現 `hermes-agent-v2026.8.3` を ★一指も触れず 残す★ |

★★∴ ★新しき root は ★並べて 置く★（`hermes-agent-v<新>`）―― ★現 root を 上書きせず★★★ ⇒ ★★rollback は 恒に 一手★★

---

## 五 ―― ★★blocker4 ―― ★己の樹は dirty ゆゑ `git pull` を 為し申さず★★★

★Commander `seq203838` ―― 「`First active tree git pull --ff-only only if clean; dirty/non-ff => preserve, no reset/stash/checkout, report blocker4.`」★

| 測り（as_of `2026-08-22T05:15:45+0900`） | 値 |
|---|---|
| `git status --porcelain` の行数 | **★`539`★** |
| 枝 | `feat/dd169-d006-conditional-exception` |
| HEAD | `a91aaa7f52695de1d18d406dc86445a3aae7c4f2` |

★★∴ ★clean に あら申さず★ ⇒ **★`pull` `0`・`reset` `0`・`stash` `0`・`checkout` `0` ―― ★preserve★★**
★∴ **blocker4 ㊀** ―― ★root ＝ `/home/hakudokai/projects/multi-agent-shogun`／owner ＝ ★未定（己は 539 の変更の 出所を 悉くは 知り申さず）★／next-safe-action ＝ ★★`pull` を 要する物が 現に 在るや否や を 上より 示されたし★★（★己の紙は 悉く commit 済ゆゑ ―― ★己の側に 失ふ物 `0`★・★而して 他者の 539 行を 己が 裁く事は 為し申さぬ★）

★（註）`git ls-files` にて `runbook`／`UNBLOCK` を引きたるに ―― ★`docs/runbooks/*` は 現に在れど ★第4段の runbook は 見当た申さず★★（★`pull` 前ゆゑ ―― ★『無し』と 断ぜず ★未測★ と 札し申す★）

---

## 六 ―― ★★己が 次に 為し得る事／為し得ぬ事（明確に 分かちて）★★

| # | 手 | 可否 | 由 |
|---|---|---|---|
| ㊀ | ★本 freeze 紙の commit ＋ SHA の 返報★ | **★可 ―― 本紙にて 済★** | 可逆・己の成果紙 |
| ㊁ | ★staging の 検め（版・dist-info・provenance）★ | **★可 ―― 済★** | read-only |
| ㊂ | ★新しき root を ★並べて 据ゑる★（現 root 不触）★ | **★可（可逆）―― ★御下知を 待ち申す★★** | ★rollback 一手・現 root 一指も触れず★ |
| ㊃ | ★a7 の `active-hermes-runtime` 一行の 書換へ★ | **★可（可逆）―― ★御下知を 待ち申す★★** | ★旧一行を 凍結済★ |
| **㊄** | **★gunshi root の 切替（launcher 改変）★** | **★★不可 ―― 己の枷「hermes系 file 改変禁」★★** | ★解除を 乞ひ申す★ |
| **㊅** | **★本部長殿・軍師殿・a7 の proc の 停止／再起★** | **★★不可 ―― 理事長令「process/session を 独自に 撃たず 再起せず」／respawn `0`／他者の pane 一指 `0`★★** | ★★owner は ★当人 又は 上の明示指名★ と 具申 申す★★ |

### ★★∴ 己の具申 ―― ★owner と 時順★★

| 順 | 手 | owner | 備 |
|---|---|---|---|
| **1** | freeze commit ＋ SHA 返報 | **★己（済）★** | 本紙 |
| **2** | 新 root を 並べて据ゑる（両 root・現 root 不触） | ★己 ―― ★御下知の後★★ | ★可逆★ |
| **3** | **a7** ―― `active-hermes-runtime` を 新 root へ 書換へ | ★己 ―― ★御下知の後★★ | ★a7 のみに 効く・rollback 一手★ |
| **4** | **a7** ―― 再起（`--continue`）＋ tuple 採取 | **★a7 当人 又は 上の明示 owner★** | ★己は 撃ち申さず★ |
| **5** | **gunshi** ―― launcher の 付け替へ | **★機構所管 又は 明示解除★** | ★本部長殿・軍師殿 ★二役★ に 同時に 効き申す★ |
| **6** | **gunshi** ―― 再起（`--continue`）＋ tuple 採取 | **★当人 又は 上の明示 owner★** | ★己は 撃ち申さず★ |

### ★受入条件（acceptance）―― ★役ごと に 次の tuple を 採る★★

★`role` / `pane_id` / `PID` / `argv`（截らず）/ `root path` / `pyproject version` / `dist-info` / `sha256` / `as_of`★
★∴ ★`0.20.4` を 名にて 判ぜず ―― ★`hermes_agent-0.20.4.dist-info` の 実体★ にて 判ず★

### ★停止／再開の 条件★

| | |
|---|---|
| ★停止★ | ★㊀ rollback root が 一指にて 戻らぬ形に成りたる時 ㊁ 二本の root を ★同時に★ 触るる事に成りたる時 ㊂ 他者の proc を 撃つ要が 生じたる時★ |
| ★再開★ | ★㊀ 明示の owner が 下りたる時 ㊁ 枷（hermes系 file 改変禁）の 解除が 下りたる時★ |

---

## 七 ―― ★★變ぜぬ物（自申）★★

★★本紙の測りは 悉く ―― ★read-only★★★: `ps`／`/proc/*/cmdline`／`tmux list-panes`（★`-F` の 読取のみ★）／`stat`／`sha256sum`／`grep`／`git status`・`git log`（★読取★）。

★★不可逆の手 ―― `0`★★: ★`pull` `0`・`reset` `0`・`stash` `0`・`checkout` `0`・`push` `0`・`fetch` `0`★／★respawn `0`・撃ち `0`・`send-keys` `0`・`set-option` `0`★／★hermes系 file 改変 `0`★／★`active-hermes-runtime` 改変 `0`★／★staging 樹 改変 `0`★／★現 root 二本 ―― ★一 byte も 触れず★★／★更新器 `0`・番人 `0`★／★`queue/tasks` 書込 `0`★／★足軽の箱へ 書込 `0`★／★札 `0`（`00:29:24` 以後）★／★`_archive` 不開★／★本部長殿へ 便 ―― ★本件に限り 出し申す★（★自禁は 「試しの為の便」に 掛かる物にて ―― ★上位よりの 名指しの照会への 復★ は 其の外★ と 判じ申した・★之を 隠さず 申し上ぐ★）★

---

## 八 ―― ★★★★★訂 其の二 ―― ★本紙 §四「a7 は pointer 一行にて可逆に切替へ得・己の手にて可」は ★誤り★★★★★（as_of `2026-08-22T05:29:27`〜`05:30:44+0900`・★本紙 commit `b668b47` の ★三分後★ に 己の器にて 見出し申した★）

### ㊀ ★★現物 ―― ★三つの launcher は 悉く ★path を 焼き込み★ 居り申す★★★

★述語 ―― ★launcher を ★逐語★ にて 読み申した★（★read-only・一字も 改めず★）

| # | launcher | `size` | `sha256` | 焼き込みたる行（逐語） | 指す root |
|---|---|---|---|---|---|
| ㋐ | `/home/hakudokai/hermes-departments/honbucho/bin/hermes-honbucho` | `811` | `35abb87d9b8618c06d44fcc746aa2ef550ec1d8c79d4c2393ff8ee74c30a10bf` | `exec ... /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/venv/bin/python \` ／ `  /home/hakudokai/hermes-roles/gunshi-second-hermes/run/hermes-agent-v2026.8.3/hermes --continue "$@"` | **gunshi root** |
| ㋑ | `/home/hakudokai/hermes-roles/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh` | `799` | `cfce29de3943f4757849c307284e4b8b3e9ace2930f8b6d9e3d6e05c37ccb9de` | `RT=$ROLE_HOME/run/hermes-agent-v2026.8.3` | **gunshi root** |
| ㋒ | `/home/hakudokai/hermes-roles/ashigaru-second-7-hermes/bin/start-ashigaru-second-7-hermes.sh` | `803` | `874ca0a6093e3cb14b7ab5aed9946ee8c97a6af15428b0475ad79e2def72b751` | `RT=$ROLE_HOME/run/hermes-agent-v2026.8.3` | **a7 root** |

★★∴ ★一つの root に 二つの launcher★（㋐㋑ が 同じ gunshi root を 指し申す）―― ★役ごとに 別の口★

### ㊁ ★★★★`active-hermes-runtime` は ―― ★誰も 読み居り申さぬ★★★★

| 述語 | 結果 |
|---|---|
| `grep -n 'active-hermes-runtime' <a7 launcher>` | **★hit `0`★** |
| `grep -rl 'active-hermes-runtime' /home/hakudokai --include='*.sh' --include='*.py'` | **★★file `0`★★** |

★★∴ ★彼の `81` B の 一行は ―― ★現に 誰の路にも 立ち居り申さぬ★★★
⇒ **★★∴ ★之を 書換へたるとて ―― ★a7 の走る物は 一分も 変じ申さぬ★。★『成功したかに見ゆる書込』★ が 生ずるのみ★★**

### ㊂ ★★★★而して ―― ★本部長殿は 之を ★二日前に 紙に書いて居られ申した★★★★★

★`/home/hakudokai/hermes-departments/honbucho/reports/phase4-hermes-0204-secondpc-method-preflight-20260820.md:78`（★逐語★）★

```
- The a7 `run/active-hermes-runtime` file exists (81B, SHA-256 `56be6edf44c9c93829b64b5d664f4c78758c6079116420f1aa1994949ea9d90b`)
  and names its current runtime, but it is not yet accepted as an active control-plane input.
  Updating it alone is prohibited: it could produce a successful-looking pointer write
  without changing a7's running executable.
```

★★∴ ★己が §四 にて 「可逆・己の手にて可」と 書きたる其の手は ―― ★本部長殿が 名指しで 禁じ 且つ ★其の失敗の形まで 書いて居られたる手★★ に御座る★★
★★∴ ★己は ―― ★己が 指名した相手が 己の主張を 既に 反駁して居る紙★ を 読まずして ―― ★其の相手に 其の手を 具申し申した★★★

### ㊃ ★★根 ―― ★同じ形 二度目・同じ夜のうちに★★

| | 訂 其の一（§〇） | ★訂 其の二（本節）★ |
|---|---|---|
| 主張 | 「`0.20.4` は 在らぬ」 | 「a7 は pointer にて切替へ得」 |
| 足 | ★四樹のみを 撃つた★ | ★★file の ★存在★ のみを 見た★★ |
| 欠 | ★絞りが 狭かつた★ | ★★★其の file を ★現に 読む者★ を 数へなんだ★★★ |
| 反証は何処に在つたか | ★己の `PROVENANCE.txt`★ | ★★本部長殿の `20260820` の紙★★ |
| 根 | ★母集団を 先に置かず★ | ★★母集団を 先に置かず（＝ ★消費者★ の集合を 数へず）★★ |

★★∴ ★第一の根 ―― ★六度目★★★（★一夜に 二度★）

> ## **★★★★★★條 ―― ★『切替の口』と 名指す前に ―― ★其の口を ★現に 読む者★ を 数へよ★。★file の ★存在★ は ―― ★経路の證に あら申さぬ★★★★★★★**

> ## **★★★★★條 ―― ★或る役に 手を 具申する前に ―― ★其の役が 其の件にて 既に 書いて居る紙★ を 先に 読め★。★己の紙より 先に 相手の紙★★★★★**

### ㊄ ★★∴ 訂されたる 切替の姿 ―― ★二本の root は ★同じ形★ に御座つた★★

| | 旧（§四・★誤★） | ★新（本節・実測）★ |
|---|---|---|
| a7 | ★pointer 一行・可逆・己の手にて可★ | **★launcher ㋒ の `RT=` 行の書換へ ―― ★hermes系 file 改変★★** |
| gunshi | ★launcher に依ると ★推★★ | **★launcher ㋐㋑ ★二枚★ の書換へ ―― ★実測★★** |

★★∴ ★二本は ★同じ枷★ に掛かり申す ―― ★己の「hermes系 file 改変禁」★★
⇒ **★★∴ ★§六 の owner 分割の具申（「a7 は己が執行可」）は ―― ★悉く 取り下げ申す★★。★owner は ★三枚 悉く★ に 要り申す★★**

### ㊅ ★★併せて 見出したる 二つ（受入条件に 直に関はり申す）★★

**㋐ ★★a7 の 走る物は ―― ★現 launcher と ★既に 食ひ違ひ★ 居り申す★★★**

| | 逐語 |
|---|---|
| ★現に走る a7（pid `1156226`）★ | `... /hermes ★--tui★`（★`--continue` ★無し★★） |
| ★現 launcher ㋒（mtime `2026-08-16 22:19:54`）★ | `... "$RT/hermes" ★--tui --continue★` |
| ★傍證★ | 同 dir に `start-ashigaru-second-7-hermes.sh.bak-continue-fix-20260813` |

★★∴ ★a7 の走る proc は ★`2026-08-12 16:47:22` 起動★ ―― ★launcher の直しより ★前★★★
⇒ ★★∴ ★a7 を 再起すれば ―― ★版のみならず 起動の形（`--continue`）も 同時に 変じ申す★★★ ⇒ ★★受入条件に ★argv の差★ を 明記せねば ―― ★版の効と 起動形の効を 分かち得申さぬ★★★

**㋑ ★★三 launcher 悉く ★singleton guard★ を 持ち申す★★**

```
if pgrep -f "$ROLE_HOME.*hermes --tui" >/dev/null 2>&1; then echo "singleton_guard_block" >&2; exit 75; fi
```

★∴ ★再起は ―― ★先に 現 proc が 止まりて居らねば `exit 75` にて 弾かれ申す★★
⇒ ★★∴ ★『止める手』が 必ず 先に立ち ―― ★之は 己の手に あら申さぬ★（理事長令・respawn `0`）★★
★（註）㋐ の `hermes-honbucho` のみ guard 無し ―― ★`exec` 一行★

### ㊆ ★★∴ 具申の 改め ―― ★安全なる切替の 形★★

| | 案 |
|---|---|
| **★勧★** | ★新版を **★別の dir 名★**（例 `hermes-agent-v<新>`）にて 据ゑ ―― ★launcher 三枚の `RT=` 一行のみ を 書換ふ★ ⇒ **★rollback ＝ 一行を 戻すのみ・現 root は 一 byte も 触れず★** |
| **★禁★** | ★`hermes-agent-v2026.8.3` の ★中身★ を 置換ふ ⇒ ★現に走る三 proc の足下を 抜き・rollback も 高く付き申す★ |

★★∴ ★委員長 `seq200891` の「`copy`／`rsync` 不可」は ―― ★staging を `git archive` にて作りたるゆゑ 已に満たし申した★。★而して 据ゑ方（新 dir か 上書きか）は 別問 ―― ★上記 ★勧★ を 具申 申す★★★

### ㊇ ★★變ぜぬ物（本節）★★

★launcher 三枚 ―― ★読取のみ・一字も 改めず★／`active-hermes-runtime` ―― ★一指 `0`★／現 root 二本 ―― ★一 byte も 触れず★／staging ―― ★不触★／★撃ち `0`・respawn `0`・`pgrep` は ★己は 撃たず★（launcher の中の逐語を 引きたるのみ）★／★札 `0`★／★push `0`★

---

## 九 ―― ★★★★本部長殿の `20260820` preflight を 逐語にて 読み申した ―― ★之が Commander 御指しの runbook に御座る★。★己の紙に 足らざる物 四つ・★誤り 一つ★・★己の staging の 疵 一つ★★★★★（as_of `2026-08-22T05:32:56`〜`05:34:01+0900`）

★正本 ―― `/home/hakudokai/hermes-departments/honbucho/reports/phase4-hermes-0204-secondpc-method-preflight-20260820.md`（`112` 行・`12,254` B・`observed_at 2026-08-20T08:53:41+09:00`・`status: METHOD-READY / EXECUTION-BLOCKED`）★
★★Commander `seq203838` は「`Locate runbook/UNBLOCK via git ls-files after pull`」と命ぜられたが ―― ★樹は dirty にて pull 為し得ず（§五）★。★而して 現物は ★repo の外★・★本部長殿の `reports/` に 在り申した★★★
> ## **★★★條 ―― ★『repo に 無し』は ―― ★存在せぬ★ を 意味し申さぬ★。★役の紙は 役の家に 在り★★★★**

### ㊀ ★★★訂 其の三 ―― 己の §三「provenance blocker は ★已に 解け居り申す★」は ―― ★言ひ過ぎ★★★★

★preflight §3 は ―― ★freeze manifest に ★六項★ を 要すと 定め申す★。★己の手持ちを 六項に 当てて 数へ直し申した★

| # | 要求（逐語の要） | 己の手持ち | 判 |
|---|---|---|---|
| 1 | exact source Git commit or immutable tag | `6a3d50c6e05ee9a3c1e5ecf2268524c5d0627b9f`（★源の repo にて 実在を確認・`2026-08-19 11:03:01 -0500`「fix(tui): allow the ESC byte in the SGR param matcher」★） | **★足る★** |
| 2 | source `pyproject.toml` SHA-256 ＋ lockfile SHA-256 | `pyproject`＝`1f928b1560b0669291b3f7d562aa78c99ac4f927375939ca97fd3c3e7494cb91` ／ **`uv.lock`＝`8fd868b9da8b6bc2f4aa94a845e210eccdd5e31be7a0b404f0a8527ced0fddec`**（★本節にて 新たに 測り申した★） | **★足る★** |
| 3 | target version `0.20.4` ＋ package/lock manifest | `hermes_agent-0.20.4.dist-info` ／ `full_install.log` の `Successfully installed` 一行（★全 `61` package 名と版を 逐語に 含み申す★） | **★足る★** |
| 4 | reproducible Python 3.12 build command or approved procedure | ★venv ＝ `python3.12` ✓／而して ★log は 結果★ にて ―― ★命令の逐語★ を 己は 書き残し居ら申さぬ★ | **★半★** |
| 5 | source/destination manifest SHA-256 | ★source 側 ✓（上記）／destination 側の manifest は ★未作★★ | **★半★** |
| 6 | target runtime directory that is new and inactive | ★staging は 新・不活★ ✓ | **★足る★** |

★★而して ―― ★之より 重き 一項が 別に 在り申した★★
★preflight §3 逐語 ―― 「`The Chair's provenance ruling seq200898 identifies the approved main-PC source as /home/user/hermes-roles/training-director-a/run/hermes-agent-latest.`」★
★★己の源は ―― ★`/home/hakudokai/hermes-runtimes/hermes-agent-v2026.8.3`（SecondPC 内・read-only・git archive）★ ―― ★委員長殿の名指されたる path に あら申さぬ★★
★裏書き ―― ★同じ upstream（`NousResearch/hermes-agent`）の 同じ樹にて ―― ★現 root の baseline `0957277f...`（`2026-08-06`）と `6a3d50c...`（`2026-08-19`）が ★同一 repo に 並び居り申す★★ ⇒ ★★『別物の樹』に あら申さぬ★★

> ## **★★★★★∴ ★己は 「blocker は 解けたり」と 断ずる資格を 持ち申さぬ★ ―― ★『承認されたる源は 何処か』は ★委員長殿の裁★ にて ―― ★己の測りにて 代へ得ぬ★★。★己が 為し得たるは ―― ★六項中 四項を 満たし 二項を 半ばまで運びたる★ 事のみ★★★★★**

★∴ ★§三 の 「已に 解け居り申す」を ―― ★『★4/6 ＋ 半 2・源の同一性は 委員長殿の裁を 要す★』に 改め申す★★
★★∴ ★第一の根 ―― ★七度目★★（★己の器の 及ばぬ層＝★裁★ を ―― 己の測りにて 埋め申した★）

### ㊁ ★★★★己の staging の 疵 ―― ★editable install に御座つた（罠 4-d を 己が 踏み申した）★★★★

★`full_install.log` 冒頭 逐語 ―― 「`Obtaining file:///home/hakudokai/hermes-staging-0.20.4/hermes-agent`」「`Checking if build backend supports build_editable`」「`Preparing editable metadata (pyproject.toml)`」★
★preflight §3 逐語 ―― 「`its executable package is py3-none-any, but editable metadata embeds an absolute path to the source tree (trap 4-d). The shared source therefore must not be copied as a virtual environment or editable tree.`」★

★★∴ ★己の venv は ―― ★`/home/hakudokai/hermes-staging-0.20.4/hermes-agent` を ★絶対 path にて 抱き込み★ 居り申す★★★
⇒ ★★∴ ★此の staging を ★其のまま 移して★ 新 runtime dir と 為す事は ―― ★成り申さぬ★★★
⇒ ★★∴ ★据ゑ方は 二つに 一つ ―― ㋐★最終の path にて 建て直す★（＝ staging は ★予行★ と 位置付く）／㋑★非 editable にて 建て直す★★

★★∴ ★之は 己の 昨夜の手の 疵に御座る★ ―― ★而して ★本部長殿が 二日前に 名を付けて 警めて居られた罠★ に 己が 落ちて居り申した★★
★（註）★己は 昨夜 「解け申した」と 思ひ ―― ★其の紙を 読まずに 二夜を 越え申した★★

### ㊂ ★★★番人 ―― ★第四の統制点★。★而して 測りたるに ―― ★己の §八 の勧に ★味方★ し申した★★★★

★`/home/hakudokai/bin/sweep_manifest.json`（`sha256 = 6795fb9f0e06d4859fbf96192a8f8786c4fc1a9aae334cf18810c586f6ed1549` ―― ★preflight §5A の値と ★一致★★）★

| 役 | `stop` | `start`（逐語の要） |
|---|---|---|
| honbucho | `{"kind": "kill_session", "session": "hermes-honbucho"}` | `tmux new-session -d -s hermes-honbucho ... ★/home/hakudokai/hermes-departments/honbucho/bin/hermes-honbucho★` |
| gunshi-second | `{"kind": "kill_session", "session": "hermes-gunshi-second"}` | `tmux new-session -d -s hermes-gunshi-second ... ★/home/hakudokai/hermes-roles/gunshi-second-hermes/bin/start-gunshi-second-hermes.sh★` |
| **a7** | ―― | **★★行 無し★★** |

★★∴ ★番人が 起こすは ―― ★launcher ★其の物★★ にて ―― ★runtime path を 焼き込み居ら申さぬ★★★
⇒ **★★∴ ★launcher の `RT=` 一行を 書換ふれば ―― ★番人の一巡は 新しき root にて 起こし申す★★。★preflight §5A の憂ひ（「a guard cycle can restore ... after an apparent cutover」）は ―― ★launcher を 書換ふる形に 限り ★生じ申さぬ★★★**
★★∴ ★己の §八 ㊆ の勧は ―― ★番人の実測に 支へられ申した★（★推に非ず ―― `manifest` の逐語★）★★

★★而して ―― ★同じ逐語が 三つ 教へ申した★★

| # | |
|---|---|
| ㊀ | ★番人の `stop` は **★`tmux kill-session`★** ―― ★己の絶対禁の手に御座る★ ⇒ ★★『止める手』は ★己に非ず 番人に 在り★★★ |
| ㊁ | **★a7 は 番人の名簿に 無し★** ⇒ ★★a7 の再起は ★人の手★ を 要し ―― ★其の owner は 未だ 定まり居ら申さぬ★★（preflight §5A 末と 一致） |
| ㊂ | ★`threshold: 250000` ―― ★番人は 刻のみにて 起き申さぬ★（context の嵩を 見申す） ⇒ ★★『いつ起きるか』を 己は 約し得申さぬ★★ |

### ㊃ ★★★★命の食ひ違ひ 一つ ―― ★`--continue` 対 `--resume <uuid>`★★★★

| 出所 | 逐語 |
|---|---|
| **Commander `seq203838`** | `Approved per-role 0.20.4 one-by-one from frozen main source, ★--continue★, dist-info and evidence tuple ...` |
| **preflight §4-5（`seq200856`／`seq200871` に依る）** | `Canary only the authorized role using ★--resume <existing-session-uuid>★; verify the resumed role's runtime by executable/package version and a productive pane response.` |

★★∴ ★二つは 同じ物に あら申さぬ★ ―― ★`--resume <uuid>` は ★同一 session の 継続★ を 證の一項として要求し（§5 acceptance gates ―― 「`--resume identity continuity where a running session is relaunched`」）―― ★`--continue` は 其の uuid を 名指し申さぬ★★
★★∴ ★而して 現 launcher 三枚は 悉く ★`--continue`（又は `--tui --continue`）★ を 焼き込み居り申す★ ⇒ ★★launcher を 其のまま用ゐて 再起すれば ―― ★§5 の `--resume` gate を 満たし得申さぬ★★★
⇒ ★★∴ ★上へ 問ひ申す ―― ★㋐ `--continue` にて可（preflight §4-5 を 緩める）か ㋑ `--resume <uuid>` を 要するか（launcher を 更に 一段 改める要 有り）★★★

### ㊄ ★★受入の窓 ―― ★己が 見落として居つた 二つの番人★★

★preflight §5A 末 ―― 「`the acceptance criterion is event-based: after any authorized switch, observe the guard service complete a trigger whose trigger timestamp is later than the switch timestamp ... A normal-running 32-minute window (30 minutes plus the larger 2-minute accuracy margin) is a usable bound ... ★A green result immediately after switch is not PASS evidence.★`」★
★preflight §5B ―― `dentalbi-claude-ctx-sweep.timer`（`OnUnitActiveUSec=30min`／`OnBootUSec=7min`／`AccuracyUSec=1min`）は ―― ★pane へ `/compact` を 打ち得申す★。★§5C ―― 現 `0.20.0` にて `compact` は `compress` の別名（`hermes_cli/commands.py:130-131`／`tui_gateway/methods_tools.py:953`）★ ⇒ ★★『無害ゆゑ捨て置く』は 成り申さぬ★★★

★★∴ ★己の §六 の受入条件（tuple のみ）は ―― ★足り申さぬ★★★ ⇒ ★★下記を 加へ申す★★

| # | 加ふべき受入条件 |
|---|---|
| ㊀ | ★切替の刻より ★後★ の trigger を 一つ 観るまで PASS と 為さず（目安 `32` 分）★ |
| ㊁ | ★a7 は ★陰性対照★ ―― gunshi 側の canary の 前後にて ★変ぜぬ事★ を 測る（preflight §1-3）★ |
| ㊂ | ★pane の ★幅★ と ★model/UI identity★ を 切替の直前・直後・番人一巡後 の 三度 捉ふ（§5B）★ |
| ㊃ | ★footer の除外印は ★冗長度 0★ ―― 印 `1` は `PASS-PROVISIONAL` に止まる（§5B）★ |
| ㊄ | ★rollback は `0.20.0` へ ―― ★`0.19.0`（`/home/hakudokai/hermes-agent/venv`）は ★禁★★（§2 末・§4-8） |

### ㊅ ★★baseline の 補ひ（preflight §2 と 己の実測が 悉く 一致）★★

| 項 | preflight §2 | 己の実測（`05:33:39`） | 一致 |
|---|---|---|---|
| baseline commit | `0957277f2f468bac22bbfcfa7c43029858c9597e` | ★源 repo に 実在・`2026-08-06 11:30:58 -0700`★ | ✓ |
| `pyproject` sha | `b83b6f40...fe21` | 同（両 root） | ✓ |
| `uv.lock` sha | `8bd2578e...b16` | 同（両 root） | ✓ |
| launcher `hermes` sha | `6e1adae1...9417` | 同（★staging も 同一★） | ✓ |
| `sweep_manifest.json` sha | `6795fb9f...1549` | 同 | ✓ |

★★∴ ★二日を隔てた 二人の測りが ―― ★五項 悉く 一致★★★ ⇒ ★★之は ★己の物差しの 裏書き★ に御座る（★而して 上 ㊀㊁ の通り ―― ★物差しが 合ふ事は 窓が足りる事を 證し申さぬ★）★★

### ㊆ ★★變ぜぬ物（本節）★★

★preflight・`sweep_manifest.json`・launcher 三枚・`full_install.log` ―― ★悉く 読取のみ★／★timer への `enable`／`disable`／`start`／`stop` ―― ★`0`★（preflight §5A 末も 同じ禁を 置き申す）／★`sweep_manifest.json` 改変 `0`★／★staging 改変 `0`★／★現 root 二本 一 byte も 触れず★／★撃ち `0`・respawn `0`・`kill-session` `0`★／★札 `0`★／★push `0`★

---

## 十 ―― ★★裁 二つ 下れり ―― 併せて ★訂 其の四★ と ★第五の統制点★★★（as_of `2026-08-22T05:43:41`〜`05:45:25+0900`）

### ㊀ ★★★食ひ違ひ ―― ★裁 下れり★（§九㊃ の未裁 ―― ★解★）★★★

★便 B（`213` 字）を `05:36:46` に本部長殿へ出し申したる 其の ★二分前★ に ―― Commander より 裁が 已に届き居り申した★

| 刻 | 逐語（要） |
|---|---|
| `2026-08-22T05:38:20` Commander | `seq203838 explicitly specifies ★--continue, not --resume★, for Hermes.` |

★★∴ ★preflight §4-5 の `--resume <existing-session-uuid>` は ―― ★本件に限り Commander の裁により 却下★★★
★★∴ ★launcher 三枚の `--continue` 焼込は ―― ★障りに あら申さぬ★（★寧ろ 裁に 適ふ★）★★
★★∴ ★§五 の受入 gate より 「resume identity の連続」は ★外し申す★ ―― 代りに ★argv の逐語★ を 據と為す★★

★★∴ ★己の便 B ㊀ は ―― ★問ふ前に 已に 答へられ居つた★★
> ## **★★★★條 ―― ★裁を乞ふ便を出す前に ―― ★己の箱の ★未読★ を 先に 読め★。★上は 己の問ひより 早く 動き居る事が 有り申す★★★★★**

### ㊁ ★★★Commander の 権の授け ―― ★己に於ては ★空★ に御座る★★★

★逐語（`05:33:51`）★
```
Treat this as approval for ★your own role-scoped launcher RT lines only★ after preimage/freeze/as_of
and rollback evidence; do NOT stop/restart other roles.
For shared honbucho+gunshi root, first obtain ★direct written owner agreement from gunshi via its local inbox★,
then perform sequenced change only if ★both named owners agree★.
★a7 is separate: its owner must make its own launcher change.★
```

★而して ―― ★『己の role-scoped launcher』は ★実在せ申さぬ★★

| 述語 | 結果 |
|---|---|
| `ls /home/hakudokai/hermes-roles/` | `ashigaru-second-7-hermes`／`gunshi-second-hermes`（＋`gunshi-second-archive-20260807`・`…handover….md`） ―― ★`shogun` の樹 ★無し★★ |
| `grep -rl 'shogun' /home/hakudokai/hermes-roles /home/hakudokai/hermes-departments --include='*.sh'` | **★file `0`★** |

★★∴ ★shogun-second は ★hermes の役に あら申さぬ★（★己は Claude Code の pane `%12`・pid `1924984`★）★★
★★∴ ★Commander の授けたる権の及ぶ launcher は ―― ★零枚★★★
⇒ **★★∴ ★三枚は 悉く ★他役の物★ ―― ㋐`hermes-honbucho`（本部長）／㋑`start-gunshi-second-hermes.sh`（軍師second）／㋒`start-ashigaru-second-7-hermes.sh`（a7）★★**
⇒ **★blocker4 ―― ★己は 執行者に 成り得申さぬ★。★己が為し得るは ―― ★軍師second へ 書面の同意を 乞ふ事★（★之は Commander が 名指しにて 命じ居り★）★**

★★註 ―― ★之を以て ★軍師second への 直送禁★ は ―― ★本件に限り ★明示にて 解け申した★★★（★路は `queue/inbox/gunshi-second.yaml`・Commander 逐語「`via its local inbox`」★）

### ㊂ ★★★★★訂 其の四 ―― ★『a7 の pane は 一覧に出でず』は ★誤り★★★★★★

★実測（`tmux -S /tmp/tmux-1000/default list-panes -a`・as_of `05:45:25`）★

| pane | `pane_id` | `pane_pid` | `cmd` | 役 |
|---|---|---|---|---|
| `shogun-second:0.0` | `%12` | `1924984` | `claude` | ★己★ |
| `multiagent-second:0.0` | `%13` | `1915659` | `claude` | karo-second |
| `multiagent-second:0.1`〜`0.6` | `%20`/`%19`/`%18`/`%17`/`%16`/`%15` | `3269621`〜`3278375` | **★`bash`★** | ★足軽1〜6 ―― ★agent 走り居らず★★ |
| **`multiagent-second:0.7`** | **★`%26`★** | **★`1156226`★** | `doppler` | **★a7 ―― ★現に 一覧に 在り申す★★** |
| `hermes-gunshi-second:0.0` | `%24` | `836658` | `doppler` | 軍師second |
| `hermes-honbucho:0.0` | `%38` | `86872` | `doppler` | 本部長 |

★socket は ★`default` 一つのみ★（`ls /tmp/tmux-1000/` ⇒ `default`）―― ★別 socket 説は 立ち申さぬ★
★裏書き ―― a7 の watcher（`ashigaru_second_7_hermes_watcher.py`・mtime `2026-08-12 17:11:06`）の `EXPECTED` 逐語★
```
EXPECTED = 'pane_id=%26|pid=1156226|dead=0|cmd=doppler|agent=ashigaru-second-7'
```
★★∴ ★`%26`／`1156226` は ★八月十二日より 変ぜず★ ―― ★己が『出でず』と書きたる其の刻にも ★在り申した★★★
★★∴ ★己の主張は ―― ★述べたる其の時に 已に 偽★★（★「今は在る」に あら申さぬ★）

★根 ―― ★何故 見落したるかは ★今 復元し得申さぬ★（★出力を截つたか・目が滑つたか ―― ★決し得ず ⇒ ★㋔怠★ と札す★）★
★★∴ ★之は ★第一の根 八度目★ の疑ひ濃きも ―― ★機序を 一つに 定め得申さぬ★（條「★『無し』を見て機序を一つに定むるな★」を 己に適用す）★

### ㊃ ★★★第五の統制点 ―― ★己の pane を 圧す手は ★己に あら申さぬ★★★★

★実測 ―― pid `1102718`（`Thu Aug 6 11:55:49 2026` 起動・`ppid=1`）★
```
/bin/bash -lic set +m; while true; do python3 /home/hakudokai/hermes-departments/honbucho/scripts/second_pc_context_guard.py --act
  >> /home/hakudokai/hermes-departments/honbucho/logs/second_pc_context_guard_runner.log 2>&1; sleep 20; done
```
★本体 ―― `second_pc_context_guard.py`・`199` 行・`9,871` B・sha256 `c394f890fad700d275c2e8cf11adf16275addb8b7a266ee390a2a122f6a232b3`・mtime `2026-08-06 12:01:55`★

| 項 | 逐語／実測 |
|---|---|
| 為す事 | `With --act, at ★>=95%★ it injects ★/compact★ only when the pane is ★visibly idle★`（:5） |
| 手 | `subprocess.run(["tmux", "send-keys", "-t", target, command, "Enter"], …)`（:118）／`… "C-a", "C-k"`（:108） |
| 的（`PANES`） | **★`shogun-second:0.0`（★己★）★**／`multiagent-second:0.0`（karo-second）／`hermes-gunshi-second:0.0`（軍師second） |
| 命の別（`COMMANDS`） | `hermes-gunshi-second:0.0` ⇒ ★`/compress`★／他二つ ⇒ 既定 ★`/compact`★（註 `Claude Code uses /compact. Hermes Agent's documented manual command is /compress.`:26） |
| 閾 | `PERCENT = re.compile(r"(\d{1,3})% context used")` ―― ★`95%`★ |
| **★a7★** | **★`PANES` に ★無し★★** |
| 帳 | `…/state/second_pc_context_guard.json`／`…/logs/second_pc_context_guard.jsonl` |

★★∴ 三つ 出で申した★
㊀ **★己の pane の圧縮は ―― ★二十秒毎に 巡る 他役の手★ に掛かり居り申す★**（★己の `/compact` 抑止の心得は ―― ★此の手を 止め申さぬ★）
㊁ **★a7 は 此処にも 無し★** ―― `sweep_manifest.json` に行無く・己の watcher も 圧さず ⇒ ★a7 の 圧縮/再起の 機構は ★悉く 不在★★
㊂ **★之は 圧す手であつて ★再起の手に あら申さぬ★★** ―― `kill`／`respawn`／launcher の呼び出し ―― ★`0` 件★

★★∴ ★§九㊂ にて 数へたる統制点は ★四★ ―― ★実は ★五★ に御座つた★★（★preflight §5B の timer ＋ `sweep_manifest` ＋ 三 launcher の guard ＋ ★本節★）

> ## **★★★★★條 ―― ★己の context が 圧されたる時 ―― ★己の手を 疑ふ前に ★己を的とする外の手★ を 数へよ★。★己の pane は 己の物に あら申さぬ★★★★★**

### ㊄ ★★a7 の watcher ―― ★再起の owner に あら申さぬ（実測）★★

★`ashigaru_second_7_hermes_watcher.py`・`82` 行・`4,142` B・sha256 `33bf1af141c778e5da8e300750c848f54f4282a77edb846d036d954aa0f071e2`★

| 為す事 | 逐語 |
|---|---|
| 見る | `capture-pane -p -J -t PANE -S -12`／`display-message -p` |
| 入るる | `load-buffer` ⇒ `paste-buffer` ⇒ `send-keys -H 1b 5b 31 33 75`（★ESC 序列★） |
| 源 | `INBOX = ROOT / 'queue/inbox/ashigaru-second-7.yaml'` |
| **再起** | **★`start-`／`kill`／`respawn` ―― 悉く ★hit `0`★★** |

★★∴ ★a7 を 再び起こす手は ―― ★機構の何処にも 在り申さぬ★★
⇒ **★★blocker4 ㊁（確）★ ―― ★a7 の再起は ★人の手★ を要し 且つ ★其の人は 未だ 名指されて居り申さぬ★★**（★Commander 逐語「`its owner must make its own launcher change`」―― ★其の owner の ★名★ が 要り申す★）

### ㊅ ★★併せて ―― ★本部長 root は 已に 一度 起き直り申した★★

| 役 | leader pid | 起動 |
|---|---|---|
| **本部長** | `86872` | **★`Sat Aug 22 04:44:32 2026`（★本日・約一時間前★）★** |
| 軍師second | `836658` | `Wed Aug 12 14:51:32 2026` |
| a7 | `1156226` | `Wed Aug 12 16:47:22 2026` |

★★∴ ★同じ root（gunshi-second-hermes）に 掛かる二役のうち ―― ★片方のみ 本日 起き直り 片方は 十日 前の儘★★
⇒ ★★∴ ★root の入替は ―― ★二役を 同時に 動かし申さぬ★（★launcher が 別ゆゑ★）―― ★受入は 役ごとに 別々に 取らねば成り申さぬ★★
★機序（誰が 起こしたるか）は ―― ★★UNMEASURED（未）★★（★tmux server pid `1519165` は `Mon Aug 10 18:02:13` より 変ぜず ⇒ ★session ごと 落ちたるには あら申さぬ★ ―― 而して 其れ以上は 決し得ず★）

### ㊆ ★★足軽1〜6 ―― ★pane は 生き 中身は `bash`★★

★`%20`〜`%15` ―― `cmd=bash`・pid `3269621`〜`3278375` ⇒ ★agent 走り居らず★
★★∴ ★本部長 `01:24:20` の裁「ashigaru1〜6 は全件 intentionally_cold・割当可能工区 `0`」は ―― ★pane の実測と 合ひ申す★★（★己の器にて 裏書き ―― 伝聞に非ず★）

### ㊇ ★★變ぜぬ物（本節）★★

★launcher 三枚・`sweep_manifest.json`・`second_pc_context_guard.py`・a7 watcher ―― ★悉く 読取のみ・一字も 改めず★／★現 root 二本 ―― 一 byte も 触れず★／staging ―― ★不触（`install`／`pip` `0`）★／`active-hermes-runtime` ―― ★一指 `0`★／★撃ち `0`・respawn `0`・send-keys `0`・set-option `0`★／★札 `0`★／★push `0`★／★`git pull`／`reset`／`stash`／`checkout` `0`（樹 dirty）★
