# 差 17 を切り分ける SELECT 案 v1 (order39 產・★実行 0・DB 接続 0★)
as_of 2026-09-07 15:1x JST / 席=ashigaru-third-2 / 令=karo-third order39 / 打手=総監督。列は migration
`20260403020939_create_source_code_cache.sql` から写した (file_path/content/file_size/line_count/commit_hash/updated_at/created_at)。★`content` 列は 1 度も選ばぬ★ (PII 列 0)。1 = 行 1 本。
## §1 前提の再刷 (数と出所)
| 数 | 何を数へた 1 | 出所 (紙 sha16 / 便) | 当席は |
|---|---|---|---|
| 20,903 | 表の行 | 総監督 seq283366 | 測つて居らぬ |
| 5,632 | 履歴 path (歴代 include 型の和) | rows_20903_under_pk_v1.md 78534cba04087c34 §1 | 測つた |
| 15,271 | 20,903 − 5,632 の引き算 | 同 §1 核 / rows_15271_select_plan_v1.md ea20e81d75e95ade | 測つた(引算) |
| 15,288 | 表の行 = 12,527 (`backend/.venv%`) + 2,761 (`.venv-linux%`) | 総監督 SELECT 実測 便 0032ec458 | 測つて居らぬ |
| 27 | 総監督紙の言ふ root 直下 | 同便 | 測つて居らぬ (§4-1) |
差 = 15,288 − 15,271 = ★17★。総監督紙は「同じ日の他 prefix 分と相殺の範囲」と記す。以下は其れを確かめる形。
## §2 仮説ⓐ ―― 07-19 の同じ走行で、2 prefix の外にも行が入つた
```sql
SELECT split_part(file_path, '/', 1) AS top_seg, count(*) AS rows
FROM public.source_code_cache
WHERE created_at >= DATE '2026-07-19' AND created_at <  DATE '2026-07-20'
  AND file_path NOT LIKE 'backend/.venv%'
  AND file_path NOT LIKE '.venv-linux%'
GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
```
★数の形★: `rows` の合計が ★17★ なら仮説ⓐ。0 なら ⓐ は消える。17 でも 0 でもない時は §4-2 へ。
## §3 仮説ⓑ ―― 5,632 の側に venv 由来の path が混ざつて居る
```sql
SELECT file_path, created_at
FROM public.source_code_cache
WHERE (file_path LIKE '%/.venv/%' OR file_path LIKE '%/venv/%' OR file_path LIKE '%site-packages%')
  AND file_path NOT LIKE 'backend/.venv%'
  AND file_path NOT LIKE '.venv-linux%'
ORDER BY created_at LIMIT 20;
```
★数の形★: 出た行が ★17★ なら仮説ⓑ (2 prefix の外に venv 由来が 17 本在り、5,632 に数へ込まれて居た
事に成る)。LIMIT 20 ゆゑ 20 行出たら「17 より多い」= ⓑ では説明が付かぬ。
## §4 ★開示★
1. 当席の測りに在る 27 は ★frontend 配下の追跡外 file 27 本★ (rows_20903_under_pk_v1.md §2-c) であり、
   令の言ふ「root 直下 27」と ★同じ物か判じて居らぬ★。同一と決めて書かなんだ。
2. ⓐⓑ は排他でない。両方 0 なら差 17 は「日の境界の取り方」か「刻の違ひ」に因る ―― 20,903 と 15,288 は
   ★別の刻の別の測り★ (seq283366 と 0032ec458) ゆゑ、其の時は 2 つを同じ刻で採り直す SELECT が要る。
   本紙は其処までは書いて居らぬ (令の仮説 ≤2 に従つた)。
3. 当席は SQL を ★1 本も打つて居らぬ★。DB 接続 0・commit 0・push 0。
