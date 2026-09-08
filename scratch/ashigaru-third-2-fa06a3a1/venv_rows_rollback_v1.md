# venv 行 rollback 手順書 v1 + GO checklist (order37 產・★実行 0・DB 接続 0★)

as_of 2026-09-07 15:0x JST / 席=ashigaru-third-2 / 令=karo-third order37。本紙は order35 §4・§5 を
独立させた ★打手用の手順書★。★打手 = 総監督★・当席は 1 本も打つて居らぬ。対に成る紙 =
`venv_rows_export_v1.md` (sha16 120f4fe5968c98cf・78 行)。三択語=測つた/測つて居らぬ/測れぬ。1 = 表の行 1 本。

## §1 何を戻すか
export file `venv_rows_20260907.csv` (7 列・15,288 行 + header 1) を ★同じ主鍵で★ 表へ戻す。
主鍵 = `file_path TEXT PRIMARY KEY` (DDL `20260403020939_create_source_code_cache.sql`・測つた)。
∴ ★衝突鍵 = `file_path` 一本★。同 path は表に 1 行しか持てぬゆゑ、戻しても行は増えぬ。

## §2 戻す前に export file を検める (讀取のみ)
1. `sha256sum venv_rows_20260907.csv` ―― export 紙 §6-3 で控へた値と ★一致するか★
2. `wc -l venv_rows_20260907.csv` = ★15,289★ (= 15,288 + header 1)
3. header の列順が `file_path,content,file_size,line_count,commit_hash,updated_at,created_at` か
★1 つでも合はねば戻さぬ★ (違ふ file を戻すのが最も危い)。

## §3 乾走 ―― ★transaction の中で戻して ROLLBACK する★
```sql
BEGIN;
CREATE TEMP TABLE venv_restore (LIKE public.source_code_cache INCLUDING DEFAULTS);
\copy venv_restore FROM 'venv_rows_20260907.csv' WITH (FORMAT csv, HEADER true)
SELECT count(*) AS loaded FROM venv_restore;          -- ★15,288★ を見る
INSERT INTO public.source_code_cache
       (file_path, content, file_size, line_count, commit_hash, updated_at, created_at)
SELECT  file_path, content, file_size, line_count, commit_hash, updated_at, created_at
FROM venv_restore
ON CONFLICT (file_path) DO UPDATE SET content = EXCLUDED.content,
  file_size = EXCLUDED.file_size, line_count = EXCLUDED.line_count,
  commit_hash = EXCLUDED.commit_hash, updated_at = EXCLUDED.updated_at;
SELECT count(*) AS after_rows FROM public.source_code_cache;
ROLLBACK;   -- ★乾走ゆゑ必ず戻す★ (COMMIT せぬ)
```
乾走で見るもの: ⑴`loaded` = 15,288 ⑵`\copy` が符号や引用で転ばぬ事 ⑶`after_rows` が
「戻す前 + 15,288」に成る事 (DELETE 済みの状態で打つた場合)。

## §4 本番の再投入
§3 と ★同じ SQL★ を用ゐ、末尾の `ROLLBACK;` を `COMMIT;` に替へるのみ。他は 1 字も変へぬ。
照合 (§5) が 1 つでも合はねば `COMMIT;` の代りに `ROLLBACK;` を打つ。

## §5 照合 3 式 (3 つとも成り立つ事)
1. `count(venv_restore)` = ★15,288★
2. `DELETE 前 count(*) − DELETE 後 count(*)` = ★15,288★ (削つた数と戻す数が同じ)
3. `rollback 後 count(*)` = ★DELETE 前 count(*)★ (元の総数に戻つた)
★3 つとも合はねば COMMIT せぬ。★

## §6 止まる条件 (下記のいづれかで手を止め、総監督へ上げる)
- export file の sha256 か行数が §2 と合はぬ
- `\copy` が符号・引用・NUL で失敗する (1 行でも落ちたら止まる)
- `loaded` が 15,288 でない
- 照合 3 式のいづれかが合はぬ
- DELETE 前の総数を控へて居らぬ (照合 2・3 が立たぬゆゑ先へ進めぬ)

## §7 GO checklist (総監督が押す前の 8 項・★当席は 1 つも押して居らぬ★)
1. export 紙 §6 の照合 3 式が揃つたか (行数 15,289・both_rows 15,288・sha256 控へ)
2. §2(a) の `both_rows` が ★15,288★ か。ずれたら止まる (17 の食ひ違ひは未詰・§8-2)
3. export file の sha256 を控へ、★別媒体 (別 disk か別 host)★ へ 1 本 置いたか
4. §3 の乾走 (TEMP 表へ `\copy` → `count` → transaction 内 `ROLLBACK`) まで済んだか
5. patch v3 の軍師 third-2 の検分の結果が ★着いて居るか★ (枝 a2-fa06a3a1-sync-rewrite-v3 /
   commit 3155e8dc0 / patch sha16 c05138103db14f7b)
6. v3 が実際の同期経路へ入つて居るか ―― 入る前に消すと ★次の走行で再び入る★
7. DELETE の WHERE が ★prefix 2 本 + 生れた日★ のみか (`backend/.venv%` の 1 本書きでないか)
8. 打つ器・打つ人・時刻を控へたか (打つのは総監督・当席は打たぬ)

## §8 ★開示★
1. 令の逐語は「v3 PASS 済の項を足す」だが、当席は判定語を書かぬ定めゆゑ ★7-5 を「検分の結果が
   着いて居るか」の事実の形★ に改めて書いた。判定そのものは軍師 third-2 と家老の物である。
2. 15,288 (総監督実測) と 15,271 (order33 の引き算) の ★17 の食ひ違ひ★ は未だ詰まつて居らぬ。
   本紙は 15,288 を期待値に採つた。
3. DELETE 文は本紙に ★書いて居らぬ★ (令の定め)。要る時は order35 §6 を見られたい。
4. 当席は SQL を ★1 本も打つて居らぬ★。DB の器は当席に 0 本・commit 0・push 0 の儘である。
