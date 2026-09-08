# rows=20,903 を file_path PK の下で説明する（order29 產・讀取のみ）

as_of: 2026-09-07 10:3x JST / 席: ashigaru-third-2 / 令: karo-third order29（origin=order28 紙 §5）
測り方: git 讀取と作業樹の讀取のみ。DB 書込 0・DB 讀取 0（rows=20,903 は総監督 seq283366 の値であり
★当席は測つて居らぬ★）。三択語=測つた／測つて居らぬ／測れぬ。

## §1 まづ数を並べる（1 = 各行に明記）

| 物 | 数 | 1 の数へ方 | 出所 |
|---|---|---|---|
| 表の行 | 20,903 | 行 1 本 | 総監督 seq283366（当席 未測） |
| 現作業樹で script が見る file | 4,149 | file 1 本 | 当席が glob で測つた（追跡外 37 を含む） |
| git 追跡 file（scope 前） | 13,951 | path 1 本 | `git ls-files \| wc -l` |
| 履歴に一度でも現れた path | 18,994 | path 1 本 | `git log --all --pretty=format: --name-only` |
| 同・A のみ | 18,826 | path 1 本 | 同上 `--diff-filter=A` |
| ↑のうち現行 include 型に当たる | 5,629 | path 1 本 | 当席が glob 同義の正規表現で選つた |
| ↑のうち今 作業樹に在る／無い | 4,129 ／ 1,500 | path 1 本 | 同上 |
| 歴代 include 型の和に当たる履歴 path | 5,632 | path 1 本 | script を触つた 29 commit の型を集めた |
| 大文字小文字だけ違ふ追跡 path の組 | 0 | 組 1 つ | `ls-files \| tr A-Z a-z \| uniq -d` |

★核★: 最も広く採つても、git から説明できる path は ★5,632★ に留まる。20,903 との差 ★15,271★ は
git の履歴では説明できぬ（測つた）。∴ PK が file_path である事と 20,903 は矛盾せぬが、
★行の大半は「git に載つた事の無い path」である★ と考へざるを得ぬ（仮説・未検証）。

## §2 形の列挙（PK の下で行が増える道）

a. ★削除・改名の残骸★: 現行 scope で「履歴に在り今 無い」= ★1,500★（測つた）。
   旧道の全表 pagination でしか消えぬゆゑ溜まる。上限として 1,500 は説明に足りぬ。
b. ★大文字小文字・区切りの違ひ★: PK は text ゆゑ `A.ts` と `a.ts` は別行。追跡 path の
   大小違ひは ★0 組★（測つた）。CI も local も `str(rel).replace("\\","/")` で `/` に正規化して居る
   （逐語・CI L114）。∴ この道は ★小さい★（仮説）。
c. ★git に載らぬ file（本命）★: script は git ではなく ★作業樹を glob で舐める★。今この刻、
   scope 内の追跡外 file は ★37 本★（frontend 27 / backend 9 / scripts 1・測つた）。
   走行の度に其の時在つた一時 file・生成物が行になり、消えても行は残る。
   ★過去の各走行で幾つ在つたかは測れぬ★（作業樹の過去は git に無い）。
d. ★別 root・別 checkout★: order28 で測つた通り `repo_root = Path(__file__).parent.parent` ゆゑ、
   script の写しを別の樹で走らせれば ★別の樹の path★ が同じ表へ入る。何度在つたかは測れぬ。
e. ★include 型の変遷★: 歴代の和 32 型（現行 35 を包含・和固有は 1 本
   `frontend/src/layout/ekarte-v6-default.json`）で数へても 5,632 で、現行 5,629 と ★+3★ のみ。
   ∴ ★型の変遷では説明できぬ★（測つた・仮説の否定側）。
f. ★CI は scope が狭い★: CI inline の型は 28 本で script 35 本の部分集合（測つた）。
   ∴ CI が余分な path を増やす道ではない。但し CI は DELETE を「その push で消えた file」だけ行ふ。

## §3 総監督に打つて頂きたい SELECT 3 本（値の埋込 0・讀取のみ）

```sql
-- ⑴ 直近走行で書かれた行と、さうでない行（= 現樹に無い path の上限）
WITH latest AS (
  SELECT commit_hash FROM public.source_code_cache ORDER BY updated_at DESC LIMIT 1
)
SELECT (SELECT commit_hash FROM latest)                                        AS latest_commit,
       count(*) FILTER (WHERE commit_hash =  (SELECT commit_hash FROM latest)) AS rows_from_latest_run,
       count(*) FILTER (WHERE commit_hash <> (SELECT commit_hash FROM latest)) AS rows_from_older_runs,
       count(*)                                                                AS rows_total
FROM public.source_code_cache;

-- ⑵ prefix 別の行数（§1 の prefix 表と突き合はせる為）
SELECT split_part(file_path, '/', 1) AS prefix,
       count(*)                      AS rows,
       min(updated_at)               AS oldest,
       max(updated_at)               AS newest
FROM public.source_code_cache
GROUP BY 1 ORDER BY 2 DESC LIMIT 30;

-- ⑶ updated_at の分布（何時の走行が行を積んだか）
SELECT date_trunc('day', updated_at) AS day, count(*) AS rows
FROM public.source_code_cache
GROUP BY 1 ORDER BY 1 DESC LIMIT 30;
```

読み方: ⑴の `rows_from_older_runs` が 15,000 前後なら §2-c/d が主因側、数百なら §2-a が主因側
（打つてから言へる事であり ★今は言へぬ★）。⑵ に現樹に無い頭（別 root の痕）が出るか、⑶ が山を作るかを見る。

## §4 旧道と新道の DELETE 対象の差（見積・仮説）

| 道 | 1 走行あたりの DELETE 対象 | 数へ方 |
|---|---|---|
| 旧道（全表 LIMIT/OFFSET → 差集合） | 20,903 − 4,149 = ★16,754 行★（仮説: 全行が cached） | 行 1 本 |
| 新道（git 差分 D/R のみ） | 直近 100 commit の D/R path 異なり ★1,130★（scope 前）÷ 75 commit ≒ ★15 path/commit★ | path 1 本 |

∴ 新道は 1 走行の DELETE を三桁下げるが、★既に溜まつた 16,754 相当は消さぬ★。
其の為に `--full-stale-scan` を残して在る（order28 patch）。掃除は ★1 度打てば足りる★ 形であり、
毎走行の常道に戻す必要は無い（仮説・打つ判断は上に仰ぐ）。

## §5 patch と現 HEAD の差（⑤）

- `git diff --stat 8daf47adb2ec31cb..HEAD -- scripts/sync_source_cache.py scripts/tests/` = ★出力 0 行★
  （測つた）。∴ order28 の patch は現 HEAD へも素直に当たる見込み（apply --check は
  新樹 0 の令ゆゑ打つて居らぬ = ★測つて居らぬ★）。
- 本樹 HEAD は測る度に動いて居る: 令 `030e15684` → 樹を切つた刻 `8daf47adb2ec31cb` →
  order28 紙の刻 `d4e693633e6d14c0` → 本紙の刻 `b1fecb6dde77d846`（いづれも測つた）。

## §6 限界と、当席の過ち

- 20,903・重複の有無・prefix 分布は ★測つて居らぬ★（DB 讀取 0 の令）。§3 は其の為の文である。
- script を触つた 29 commit のうち ★3 本は型を取れなんだ★（構文解析に失敗・古い版）。
  但し現行 35 型は全て和に含まれて居た（測つた）ゆゑ §2-e の結論は揺るがぬ。
- 令の karo_note は「自席樹 wt-order28-sync-rewrite のまま（新樹 0）」と書くが、当席は
  order28 の床「作業後 remove」に従ひ ★既に除いて在る★。本紙の git 讀取は全て本樹
  /mnt/c/DentalBI に対して行ひ、新樹は作つて居らぬ（測つた）。裁を仰ぐ。
