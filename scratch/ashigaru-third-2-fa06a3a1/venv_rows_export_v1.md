# venv 行 export 手順書 v1 (order37 產・★実行 0・DB 接続 0★)

as_of 2026-09-07 15:0x JST / 席=ashigaru-third-2 / 令=karo-third order37 (lot 順序=総監督 seq284563)。
本紙は order35 §3 を独立させた ★打手用の手順書★ である。★打手 = 総監督★・当席は 1 本も打つて居らぬ。
三択語=測つた/測つて居らぬ/測れぬ。1 = 表の行 1 本。SQL 中の `LIKE` `\copy` 等は SQL の逐語。

## §1 対象の定め (prefix 2 本 + 生れた日)
- prefix ⑴ `backend/.venv/%` ⑵ `backend/.venv-linux/%` ―― ★2 本に分ける★。`backend/.venv%` の 1 本書きは
  `backend/.venvXYZ` の様な別 path も拾ふゆゑ用ゐぬ (LIKE の定義から言へる・測つた性質ではない)。
- 生れた日 = ★2026-07-19★ (総監督 SELECT 実測 0032ec458 を家老が 14:23 便で伝へた値。★当席は未測★)。
- 列 `created_at` は DDL `20260403020939_create_source_code_cache.sql` に在る
  (`created_at TIMESTAMPTZ DEFAULT now()`・測つた)。∴ 生れた日で切れる。

## §2 (a) 乾走 ―― 数と大きさを ★先に★ 測る (LIMIT 付・讀取のみ)
```sql
SELECT count(*) FILTER (WHERE file_path LIKE 'backend/.venv/%')       AS venv_rows,
       count(*) FILTER (WHERE file_path LIKE 'backend/.venv-linux/%') AS venv_linux_rows,
       count(*)          AS both_rows,
       sum(file_size)    AS bytes_content,
       min(created_at)   AS first_seen,
       max(updated_at)   AS last_touched
FROM public.source_code_cache
WHERE (file_path LIKE 'backend/.venv/%' OR file_path LIKE 'backend/.venv-linux/%')
  AND created_at >= DATE '2026-07-19' AND created_at < DATE '2026-07-20';
```
```sql
-- 中身の目視 (10 行だけ・content は頭 80 字のみ = 画面を潰さぬ)
SELECT file_path, line_count, file_size, created_at, left(content, 80) AS head80
FROM public.source_code_cache
WHERE (file_path LIKE 'backend/.venv/%' OR file_path LIKE 'backend/.venv-linux/%')
  AND created_at >= DATE '2026-07-19' AND created_at < DATE '2026-07-20'
ORDER BY file_path LIMIT 10;
```
期待の形: `venv_rows` ≒ 12,527 / `venv_linux_rows` ≒ 2,761 / `both_rows` = ★15,288★。
★日で切らぬ版★ (order35 §3(a)) と数が食ひ違つたら、日の条件で落ちた行が在る事になる。其の時は
★止まる★ ―― 日を外した版の数を採るか否かは総監督の裁 (当席は決めぬ)。

## §3 (b) export 本体 (LIMIT 無し・7 列全部)
```sql
SELECT file_path, content, file_size, line_count, commit_hash, updated_at, created_at
FROM public.source_code_cache
WHERE (file_path LIKE 'backend/.venv/%' OR file_path LIKE 'backend/.venv-linux/%')
  AND created_at >= DATE '2026-07-19' AND created_at < DATE '2026-07-20'
ORDER BY file_path;
```
psql から file へ落とす形 (打手=総監督):
```
\copy (…上の SELECT 全文… ) TO 'venv_rows_20260907.csv' WITH (FORMAT csv, HEADER true)
```

## §4 出力 file の定め
- 名 = `venv_rows_20260907.csv` (日付は打つた日。作り直す時は `_2` 等を足し ★上書きせぬ★)。
- 形式 = ★CSV (HEADER 有)★。理由 = §5 rollback 紙の `\copy … FROM … CSV HEADER` と対に成り、
  同じ 7 列を同じ順で往復できる。content に改行・引用符が入るが CSV の引用で括られる。
  jsonl も往復は出来るが、戻す側で `\copy` が使へず 1 行づつの INSERT に成るゆゑ採らぬ。
- 行数の期待 = ★15,288 + header 1 行 = 15,289 行★。
- 文字符号 = UTF-8。`content` に NUL が在る行は本来 sync 側で除かれて居る (script の
  `SANITIZE (NUL bytes removed)` 経路)。CSV へ落ちぬ行が出たら ★止まる★。

## §5 大きさの見積 ―― ★測れぬ★
`.venv` は今 作業樹に無く (`ls` 不在・測つた)、当席の器では 1 byte も測れて居らぬ。
∴ ★§2(a) の `sum(file_size)` を先に打ち★、其の値を元に export 先の空きを判じられたい。
目安の立て方 (数は書かぬ・式のみ): 必要な空き ≒ `bytes_content` + `file_path` 等の他列分
+ CSV の引用と改行の増分。★安全側に 2 倍を見る★ のが実務の常だが、之は当席の勘であり測りではない。

## §6 照合式 (export の後に必ず 3 つとも見る)
1. `wc -l venv_rows_20260907.csv` = ★15,289★ (= 15,288 + header 1)
2. §2(a) の `both_rows` = ★15,288★ (file の行数 − 1 と一致する事)
3. `sha256sum venv_rows_20260907.csv` を控へる (rollback 紙 §2 で同じ値を再測して突き合はせる)
★3 つとも合はねば先へ進まぬ★。合はぬまま DELETE へ移ると戻せぬ (削除は不可逆・総監督裁)。

## §7 ★開示★
- 生れた日 2026-07-19 は ★家老便が伝へた総監督の実測値★ であり ★当席は未測★。日が違へば §2〜§3 の
  `DATE '2026-07-19'` / `'2026-07-20'` を差し替へられたい (2 箇所 × 3 文 = 計 6 箇所)。
- 15,288 (総監督実測) と 15,271 (order33 の引き算) の ★17 の食ひ違ひ★ は未だ詰まつて居らぬ。
  本紙は ★15,288 を期待値に採つた★。
- DELETE 文は本紙に ★書いて居らぬ★ (令の定め・要る時は order35 §6 を見られたい)。
- 当席は SQL を ★1 本も打つて居らぬ★。DB の器は当席に 0 本の儘である。
