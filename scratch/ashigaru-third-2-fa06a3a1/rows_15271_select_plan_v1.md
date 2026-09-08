# 履歴 path 15,271 の切り分け SELECT 案 (order33 產・讀取のみ・実行 0)

as_of 2026-09-07 14:2x JST / 席=ashigaru-third-2 / 令=karo-third order33 (裁 ⓑ 先・ⓐ は裁 283660 待ち)
測り方: file の讀取のみ (cat/grep/sed -n)。DB 讀取 0・DB 書込 0・script 走行 0・新樹 0・push 0。
三択語=測つた/測つて居らぬ/測れぬ。註: `ON CONFLICT` `PRIMARY KEY` `TIMESTAMPTZ` 等は file の逐語で当席の
判定語ではない。SQL は ★案★ であり当席は 1 本も打つて居らぬ。

## §1 前提の数を出所付で再刷 (床(27)・1 = 各行に明記)
| 数 | 1 の数へ方 | 出所 | 当席は測つたか |
|---|---|---|---|
| 20,903 | 表の行 1 本 | 総監督 seq283366 | ★測つて居らぬ★ |
| 18,994 | 履歴に現れた path 1 本 | order29 §1 (`git log --all --name-only`) | 測つた(order29) |
| 5,629 | ↑のうち現行 include 型に当たる path 1 本 | order29 §1 | 測つた(order29) |
| 5,632 | 歴代 include 型の和に当たる履歴 path 1 本 | order29 §1 | 測つた(order29) |
| 4,149 | 現作業樹で script が見る file 1 本 | order29 §1 (glob) | 測つた(order29) |
| 15,271 | 行 1 本 | ★20,903 − 5,632★ の引き算 | 引き算は測つた |
| 16,754 | 行 1 本 | ★20,903 − 4,149★ の引き算 | 引き算は測つた |

## §2 列名の出所 (推測 0・全て file の逐語)
正本 `supabase/migrations/20260403020939_create_source_code_cache.sql`(本樹・測つた): `file_path TEXT
PRIMARY KEY` / `content TEXT NOT NULL` / `file_size INTEGER` / `line_count INTEGER` / `commit_hash TEXT`
/ `updated_at TIMESTAMPTZ DEFAULT now()` / `created_at TIMESTAMPTZ DEFAULT now()` / 索引
`idx_source_code_cache_updated ON source_code_cache(updated_at DESC)`。裏取り: #1 sync_source_cache.py
L393-398 の payload 6 鍵(created_at を送らぬ) / #2 CI inline L64-68 の 5 鍵(updated_at も送らぬ) / #3
secondpc L189 `INSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash,
updated_at)`。★content 列は本紙の SELECT で 1 度も選ばぬ★。

## §3 仮説 3 つ・各 1 本 (read-only・LIMIT 付・content 0)
### 仮説A 別 root・別 checkout の痕 (order29 §2-d / order30 §5-4 の続き)
#1 `repo_root = Path(__file__).parent.parent` に対し #2 CI は `repo = Path(".")`。写しを別樹で走らせれば
別根の相対 path が同表へ入る ⇒ 現行 include 型の頭に無い prefix が塊で出る筈 (仮説)。
```sql
SELECT split_part(file_path,'/',1) AS prefix, count(*) AS rows,
       min(created_at) AS first_seen, max(updated_at) AS last_touched,
       count(DISTINCT commit_hash) AS commits
FROM public.source_code_cache GROUP BY 1 ORDER BY 2 DESC LIMIT 40;
```
数の形: 上記 7 頭以外(frontend/backend/tests/tools/scripts/docs/shim 以外)が合計 ★1 万行台★ なら A 側・
上記 7 頭で 20,903 が概ね埋まるなら A は小さい。

### 仮説B 旧道の DELETE が届かず古い行が層を成す (order29 §2-a)
旧道は全表 pagination の差集合でしか行を除かぬ ⇒ 直近走行の commit_hash を持たぬ行が厚く、
其の created_at が古い日に山を作る筈 (仮説)。
```sql
SELECT date_trunc('day',created_at) AS born_day, count(*) AS rows,
       count(DISTINCT commit_hash) AS commits,
       min(updated_at) AS oldest_touch, max(updated_at) AS newest_touch
FROM public.source_code_cache GROUP BY 1 ORDER BY 1 DESC LIMIT 60;
```
数の形: born_day が数日に集中し其処だけで ★1 万行超★ なら B 側 (大量投入の痕)・日が散り各日 3 桁以下なら小。

### 仮説C git に載らぬ file (生成物・一時 file) が走行時に居た (order29 §2-c)
script は git ではなく作業樹を glob で舐める。今この刻の追跡外 file は 37 本 (order29 で測つた) だが
過去の各走行で幾つ在つたかは ★測れぬ★ ⇒ 拡張子分布が git 追跡と離れれば C 側 (仮説)。
```sql
SELECT lower(reverse(split_part(reverse(file_path),'.',1))) AS ext,
       count(*) AS rows, min(created_at) AS first_seen
FROM public.source_code_cache WHERE position('.' in file_path) > 0
GROUP BY 1 ORDER BY 2 DESC LIMIT 40;
```
数の形: 現行 include 35 型に無い拡張子が合計 ★4 桁★ なら C 側。3 桁以下なら小さい。
## §4 読み方の限り
A/B/C は排他ではない。3 本とも厚い塊を返す事は在り得る。帰属を 1 つに定めるには prefix × born_day の交叉が
要るが本紙は「1 仮説 1 本」の令ゆゑ書いて居らぬ。打つ順は A→B→C を当席の案とし、裁は家老に在る。

## §5 ★開示 (令の欠・当席の欠)★
1. ★令文の引き算が合はぬ★: order33 purpose は「18,994−5,629 と 20,903 の関係」と書くが 18,994 −
   5,629 = ★13,365★ で 15,271 ではない。15,271 は order29 §1 の通り ★20,903 − 5,632★ である
   (引き算は測つた)。本紙は後者を前提に置いた。裁を仰ぐ。
2. ★created_at を order29 は使つて居なかつた★: DDL に在るのに order29 §3 の 3 本は updated_at のみを
   視て居た ―― 当席の欠。行が ★何時生まれたか★ と ★何時触られたか★ を分けねば A と B は見分けられぬ。
3. 20,903・重複・prefix 分布は当席 ★測つて居らぬ★ (DB 0 の令)。本紙は打ち手への案に留まる。なほ C の
   `reverse(split_part(reverse(...)))` は素朴な形であり `.d.ts` 等は `ts` に丸まる (当席の限り)。
4. #4 の Edge Function `sync-source-cache-temp` の中身は本樹に無く ★讀めて居らぬ★ ゆゑ、
   其の書き手が created_at をどう置くかは ★測れぬ★。

## §6 先の紙の sha 再測 (床(27)・as_of 14:2x)
78534cba04087c34 100 行 rows_20903_under_pk_v1.md(o29) / 2ec2a8d7931b0df3 69 行 source_code_cache_
writers_v1.md(o30) / e783d38e30bacf3d 75 行 sync_source_cache_rewrite_v2.md(o31) / b99e75d8d356ec46
554 行 0002-sync_source_cache-v2-fold-tests-24.patch / eb60655c1f9d8822 37 行 order32_tree_...v1.md(o32)
