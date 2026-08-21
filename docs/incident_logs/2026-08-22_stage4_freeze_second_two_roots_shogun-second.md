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
