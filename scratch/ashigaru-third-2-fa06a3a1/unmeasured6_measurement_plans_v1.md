# 未測 6 件の測り方 手順書 v1 (order67 產・讀取のみ・★DB 0・SELECT 実行 0・fetch 0・走行 0★)

as_of 2026-09-07 21:40 JST / 席 ashigaru-third-2 / 前紙 (床) = `option_c_lot_handover_v1.md` `54fe3eb4b887c12c` 84行 ―― 本手番に再測し ★一致★・不触
6 件の並びは ★order67 節の①〜⑥に従ふ★。数: 1 = 案文 1 本 / ref 1 本 / 行 1 本。各項 5 欄 = 器 / 案文 / 前提 / 危険 / 権限。
★併記①★ 前紙 §6 は「総監督側 run.log・backup path は届いて居らぬ」と書いた。其の後 task YAML `order66.karo_note` に **backup = `Documents/DentalBI-local-backups/o61_20260907`** と在るを見た ∴ **backup は届いた・run.log は今も未受領**（前紙は書き換へて居らぬ）。
★併記②★ 前紙 §5 の未測 6 件と本節の 6 件は ⑤⑥ が別物である（前紙は「fnmatch 対 regex の実害」「CI #2 が現に走つて居るか」）。其の 2 件は §7 に器のみ置いた。

## ① C4 遠隔にのみ在る ref 17 本 (合併が幾ら増えるか)
- 器: `git fetch --prune --no-write-fetch-head origin` → `git ls-tree -r --name-only -z <tip>` → order59 §3 と同じ数へ方で 249+17 ref を合併し直す。
- 案文: `git -C /mnt/c/DentalBI fetch --prune --no-write-fetch-head origin`
- 前提: (a) fetch の GO (当席の令は fetch 0)・(b) 17 本の object が入る容量・(c) 作業樹に触れぬ形で足す事。
- 危険: fetch は ★遠隔追跡 ref と object を足すのみ★ で枝も作業樹も HEAD も動かさぬ ∴ 足した ref の削除で戻る。**pull / merge / rebase は別物** ―― 混ぜれば作業樹が動く。
- 権限: fetch の GO を持つ者 (総監督殿)。当席は禁ゆゑ 0 打。
- 読み: 合併が 5,678 より増えれば差の向きは「+10 過剰」から動かぬ (増える側にしか働かぬ・order59 §4 の算術)。増えねば 17 本は既知 path のみを持つ。

## ② ㋭335 (履歴に一度も名の無い path) の書き手の器
- 器: DB の SELECT (件数のみ) + repo 内 code の讀取 (当席が已に済・order63/65)。
- 案文 S67-1: `select length(commit_hash) as len, count(*) from source_code_cache group by 1 order by 2 desc;`
- 案文 S67-2: `select date_trunc('minute', updated_at) as m, count(*), count(distinct commit_hash) from source_code_cache group by 1 order by 2 desc limit 40;`
- 前提: DB 讀取の GO。表に ★branch/pc の列は無い★ (7 列・`20260403020939`) ∴ 器は commit_hash の形と時刻からしか当てられぬ。
- 危険: `select` のみ ∴ 表は動かぬ。count と長さのみ返す形に畳んで在り path 値・content は返らぬ。
- 権限: DB 讀取を持つ者 (総監督殿)。当席は 0 打。
- 読み: 40 字 hex 以外の長さが出れば「repo の commit を書かぬ器」が在る。1 分に数十本の束が並べば一括投入・散れば逐次。

## ③ 先頭 `/` の 27 本の書き手の器
- 器: DB の SELECT + `git cat-file -t <hash>` (当席が已に打ち 5 種中 4 種は repo 内に無しと出た) + Supabase 側の API log。
- 案文 S67-3: `select commit_hash, count(*), min(updated_at), max(updated_at) from source_code_cache where left(file_path,1) = '/' group by 1 order by 2 desc;`
- 案文 S67-4: `select count(*) from source_code_cache where left(file_path,1) = '/';`
- 前提: (a) DB 讀取の GO・(b) log を見るには Supabase の権 (当席は持たぬ)。repo 内で讀めた 5 器はいづれも `relative_to`/`ls-files`/`git diff` ゆゑ先頭 `/` を書き得ぬ (order65) ∴ **repo の外の器**を当てる話になる。
- 危険: `select` のみ ∴ 表は動かぬ。log 閲覧も表には触れぬ。
- 権限: DB 讀取 = 総監督殿 / log = Supabase の権を持つ者。当席は 0 打。
- 読み: S67-4 が 0 なら 27/27 は消えた側。S67-3 で 27 本以外に同じ hash が居れば、其の器は常に先頭 `/` を書く訳ではない。次の道は **05-26 14:31 / 06-08 16:49 の 2 分の PostgREST log**。

## ④ 其外 900 の書き手
- 器: ★export csv `o61_candidates_export.csv`★ (表側は ㋒ の DELETE で已に無い ∴ SELECT では戻らぬ)。`csv.DictReader` で 900 本を抜き updated_at の分・commit_hash・頭 dir で束ねる (order63 の数へ方を 900 全体へ広げる)。
- 案文 (python): 列を `file_path,updated_at,commit_hash` に絞つて讀み、束と種数のみ数へる。
- 前提: csv が scratch に在る事 (sha256 は前紙 §6)。**表からは測れぬ**。
- 危険: csv の讀取のみ ∴ 表も remote も動かぬ。ただし csv は content 列を含む 45.6MB ゆゑ、**path 値と content を紙へ写さぬ**事。
- 権限: ★当席が打てる★ (DB も網も要らぬ)。令が下れば即。
- 読み: ㋬556 は「D 動詞で消えた記録が無い」側 ∴ 作業樹に在つた儘 push されなかつた枝の疑ひが濃い。分けるには枝ごとの tree との突合が要る。

## ⑤ 総監督側 run.log・backup path の逐語 (受領要求)
- 器: 家老殿経由の便 (`scripts/inbox_write.sh` ・当席の唯一の出口)。
- 案文 (便の文面): 「㋒ lot (DELETE 19:01 COMMIT・seq286458) の **run.log の path** と **backup の作り方 (取得時刻・行数・sha256)** を逐語で賜りたし。backup path は `Documents/DentalBI-local-backups/o61_20260907` と YAML で拝見。v2 lot では `~/sync_v2_export/20260907/run.log` を賜つた。」
- 前提: 総監督殿が run.log を残して居られる事。無ければ「残つて居らぬ」も答である。
- 危険: 便を出すのみ ∴ 何も壊さぬ。ただし **path に secret が含まれ得る** ゆゑ、賜つた逐語を紙へ写す時は値の形を見てから置く。
- 権限: 当席が便を出せる (家老殿経由)。逐語を持つは総監督殿。
- 読み: run.log が在れば DELETE の実打件数 1,649 と backup の行数が突き合はせられる ∴ §2 の系譜の末端が閉ぢる。

## ⑥ cand_now 1,651 の内 2 行の由来
- 器: git の讀取のみ (当席が打てる)。已に hs_9d8570a9 で「#120/#121 で main に入つた file を v3 hook が書いた **正規行**・INCLUDE 基準 `dbf05a029` が古いだけ」と示されて居る ∴ 之を局所で裏取りする。
- 案文 (shell・当席が本手番に一部当てた): `git -C /mnt/c/DentalBI show --name-only -m --first-parent --format='' 8ca8e7ea1` / 同 `9bbdebdef` → 出た path を `dbf05a029` 時点の追跡簿 (`o61_include_set_main_dbf05a029.csv`) と突合し、**基準に無く現 main に在る** 2 本を名指す。
- 当席が已に見た事 (逐語): **#121 = `8ca8e7ea1` (2026-09-07 18:57:47)**・**#120 = `9bbdebdef` (同 18:57:36)**。触れた file はいづれも `frontend/src/features/ekarte/**` (前者 5 本・後者 6 本を頭から見た)。
- 前提: 局所 main が両 merge を含む事 (含んで居る)。DB は要らぬ。
- 危険: `show` / `log` は讀取動詞のみ ∴ 何も動かぬ。
- 権限: ★当席が打てる★。
- 読み: 2 本が基準 csv に無く現 main に在れば「正規行が古い基準ゆゑ候補に見えた」が閉ぢる。3 本以上出れば **消した 1,649 に正規行が混ざつた疑ひ**が立ち、其の時は backup (⑤) との突合が要る。

## §7 本節の 6 件に入らぬ 2 件 (前紙 §5 との差・器のみ)
- 入口 regex 対 出口 fnmatch の実害: 已に案文 10 本が 4 紙に書き上げて在り (S50-1/2・S53-1/2/3・S57-1/2/3・S58-1/2・S59-1/2)、**S59-2 は S57-1 と同文**ゆゑ実打は **9 本**で足りる。器 = DB 讀取・権限 = 総監督殿。母数は ㋒ 後の 4,159 に変はつて居る事を併記せねば数が独り歩きする。
- CI #2 が現に走つて居るか: 器 = `gh run list -R <owner/repo> --workflow sync-source-cache.yml --limit 30 --json status,conclusion,createdAt,headBranch` (讀取のみ・`gh workflow run` は発火器ゆゑ別物)。前提 = `gh` の認証。局所で已に讀めた発火条件 = `on: push` の `branches: [main, 'feature/**']` かつ `paths:` 16 件。

## §境界
- 本紙は案文を ★書いた★ のみで ★SELECT を 1 本も打つて居らぬ★。DB 讀取 0・書込 0・DELETE 0・DDL 0・fetch/pull/clone 0・gh 0・v3 走行 0・force push 0。⑥ で打つた git は `log` / `show` の讀取動詞のみ。
- 前紙 15 本 + 引き継ぎ紙 1 本を 1 字も書き換へて居らぬ。前紙への足しは冒頭に ★併記★ として置いた。
- 「測れる」と書いたのは ★器が在る★ の意であり打つた結果ではない。順位は付けて居らぬ (④⑥ が当席で打てる、は権限の別であり推しではない)。何を打つかの判は総監督殿・家老殿に在る。
