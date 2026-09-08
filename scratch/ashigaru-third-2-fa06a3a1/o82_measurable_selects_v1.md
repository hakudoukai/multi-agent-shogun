# order82 ―― 「測れぬ」を測れる形にする SELECT 集 (走 0 回・DB へ 0 回)

as_of 2026-09-08 06:2x JST / 席 ashigaru-third-2 / 令 order82
前紙 `c24ae7c7451f1c7b`(o81) 不触。★本紙の SQL は 1 本も走らせて居らぬ★ ―― 家老が其の儘写せる形で置くのみ。

## §0 結び (先に置く)
- 問① 其の行が現に在るか = ★DB で測れる★ (§3 の 3 本)。
- 問② 其の commit が現樹で解けるか = ★DB では測れぬ★ ―― 器も git に訊いて居る (§4)。
- 問③ 消える DB 行は何本か = ★SQL 単独では「上限」までしか出ぬ★。因 = 器は ★二段の網★ を使ひ、
  二段目 (fnmatch) は SQL の like と一対一に写せる物と写せぬ物が混ざる (§5-c)。

## §1 底本 (行番号は ★二系統★ 在る・混ぜぬ)
| 底本 | sha256_16 | 行数 | 何処で走る |
|---|---|---|---|
| `origin/main:scripts/sync_source_cache.py` | 16e2db65f8cb48fa | 766 | ★CI が現に走らせる版★ |
| 作業樹 `scripts/sync_source_cache.py` (枝 wp-a1-a3-3-20260723 / HEAD 4a7e1891e) | 5779563bdd21819e | 709 | 手打ち・hook が拾ふ版 |
| `origin/main:.github/workflows/sync-source-cache.yml` | 6332d822b108cc0b | 63 | ★CI 本体★ |
| 作業樹 `.github/workflows/sync-source-cache.yml` | f2a94fa4e67faa65 | 199 | 枝にのみ在る |
| `supabase/migrations/20260403020939_create_source_code_cache.sql` | 986af6e77aa2630d | 20 | 表定義 (両樹で同 sha) |
| `supabase/migrations/20260516103359_add_source_code_cache_manifest_rpc.sql` | ecd02deff5f2c3cc | 6 | 既存 RPC |

★以下の file:行 は断りが無ければ ★origin/main 版★ を指す★ (CI の話ゆゑ)。作業樹版は行が 57 行ずれる。
★併せて測つた事★: origin/main の CI yml には REST 直打ちが ★無い★ (`grep 'rest/v1'` が 0 行)。
同 file `:48` に逐語で「同じ表 source_code_cache へ書く器が 2 つ在り」と在る ∴ 器 2 系は ★当作業樹の枝にのみ★ 生きて居り、
main では v3 ただ 1 系である。o50 の紙 (`§2` で CI #2 を DB へ書く経路に数へた) は ★枝の話★ であつた ―― 前紙は書き換へず此処に併記する。

## §2 表定義 (逐語・migration 986af6e77aa2630d:3-11)
```
CREATE TABLE IF NOT EXISTS source_code_cache (
  file_path    TEXT PRIMARY KEY,
  content      TEXT NOT NULL,
  file_size    INTEGER,
  line_count   INTEGER,
  commit_hash  TEXT,
  updated_at   TIMESTAMPTZ DEFAULT now(),
  created_at   TIMESTAMPTZ DEFAULT now()
);
```
索引 (同 file:20): `CREATE INDEX IF NOT EXISTS idx_source_code_cache_updated ON source_code_cache(updated_at DESC);`
★列名は此の 7 つのみ★。以下の SQL に出る名は悉く此処と §5-b の RPC から引いた。推し量りで足した名は無い。

## §3 問① ―― 器が讀む 1 行が現に在るか
器の逐語 (`v3:337,340`): `url = f"{SUPABASE_URL}/rest/v1/source_code_cache"` /
`params={"select": "commit_hash", "order": "updated_at.desc", "limit": "1"}` ∴ 下は其の SQL 写しである。

★①-a 器が現に取る 1 行★
```sql
select commit_hash, updated_at
from source_code_cache
order by updated_at desc
limit 1;
```
期待列 = commit_hash / updated_at ・期待行数 = 0 か 1。

| 出た値 | 読み |
|---|---|
| 0 行 | `get_last_sync_commit_from_db` が None を返す形 ∴ `v3:706` で state file へ落ち、o81 で示した通り state file は両樹に在らぬ ∴ `v3:713` の全表枝 |
| 1 行・commit_hash が非 null | 其の値が問② へ渡る |
| 1 行・commit_hash が null | `v3:338` は `data[0].get("commit_hash") or None` ∴ ★null は None と同じ扱ひ★ = 全表枝 |

★①-b 表が空か否か (①-a が 0 行の時の切り分け)★
```sql
select count(*) as rows_total from source_code_cache;
```
期待列 = rows_total ・期待行数 = 1。0 なら表が空、正なら並べ替へ側の話。

★①-c 先頭を奪ふ null が在るか★
```sql
select count(*) filter (where updated_at is null)  as updated_at_null,
       count(*) filter (where commit_hash is null) as commit_hash_null
from source_code_cache;
```
期待列 = updated_at_null / commit_hash_null ・期待行数 = 1。
読み = Postgres の `order by ... desc` は既定で NULLS FIRST ∴ ★updated_at が null の行が 1 本でも在れば其の行が先頭を奪ふ★。
其の行の commit_hash が null なら ①-a は「1 行返るのに全表枝へ落ちる」形になる。

## §4 問② ―― DB では測れぬ (器も git に訊いて居る)
器の逐語 (`v3:350,355`): `def commit_exists(repo_root: Path, rev: str) -> bool:` /
`["git", "cat-file", "-e", f"{rev}^{{commit}}"]`。
∴ ①-a が返した値を持つて ★git へ★ 訊く。讀取語のみ:
```
git cat-file -e <①-a の commit_hash>^{commit} && echo resolves || echo unresolved
```
`unresolved` の時に器が何を印字するかも逐語で在る (`v3:710-712`):
`-- STALE_FALLBACK_FULL_SCAN: reason=prev_commit_unresolvable prev=... source=...` ∴ ★声は上がる★ (o80 で扱つた depth の口とは別)。
★併記★: 是は「其の樹で解けるか」であり ★樹ごとに答が違ふ★。CI の shallow clone と手元の全 clone で別の答になる。

## §5 問③ ―― 消える DB 行は何本か
### §5-a 器が消す条件 (逐語 `v3:256,264-270`)
```
for cp in cached_paths:
    if cp in all_local_paths: continue
    for pattern in INCLUDE_PATTERNS:
        if fnmatch.fnmatch(cp, pattern): stale.add(cp); break
```
∴ ★二段の網★: 一段目 = 現樹に在らぬ / 二段目 = INCLUDE_PATTERNS に fnmatch で当たる。

★上限を出す 1 本 (一段目のみ)★
```sql
select count(*) as would_delete_upper
from source_code_cache c
where not exists (
  select 1 from unnest(string_to_array($1, E'\n')) as t(p) where t.p = c.file_path
);
```
`$1` = ★v3 の `collect_files` が返した path を改行で連ねた 1 個の text★ (作り方は §5-d)。
期待列 = would_delete_upper ・期待行数 = 1。
★読み★: 是は ★上限★ である ―― 二段目で落ちる分だけ実数は之より小さい。等号になるのは
「DB の行が悉く INCLUDE に当たる」時のみで、其れは ★測つて居らぬ★。

★何処が消えるかの内訳 (同じ上限の分解)★
```sql
select split_part(c.file_path,'/',1) as top1, count(*) as n
from source_code_cache c
where not exists (
  select 1 from unnest(string_to_array($1, E'\n')) as t(p) where t.p = c.file_path
)
group by 1 order by 2 desc;
```
期待列 = top1 / n ・期待行数 = 5〜20。読み = `frontend` が大半なら o50 の㋑ (他の枝にのみ在る path) と同じ像。

### §5-b 既存資産 (新たに作らぬ)
migration `ecd02deff5f2c3cc:1-6` に逐語で在る:
`CREATE OR REPLACE FUNCTION public.get_source_code_manifest() RETURNS TABLE(file_path text, content_md5 text, file_size integer) LANGUAGE sql STABLE`。
∴ `$1` を渡さずに一覧だけ取りたい時は `select file_path from public.get_source_code_manifest();` で足る (讀取・STABLE)。
返る行数は表の行数と同じ ∴ 大きい。5,668 前後を手元へ引く事になる (総監督殿 實測 seq285143 の数・★当席は確かめて居らぬ★)。

### §5-c 二段目を SQL で書きたい時の作り方 (等価と非等価が混ざる)
`fnmatch` は `/` を特別扱ひせぬ ∴ pattern → like は機械的に写せる: `**` → `%` / `*` → `%`。
但し ★pattern 中の `/` は literal で残る★ ゆゑ `frontend/src/**/*.ts` は `like 'frontend/src/%/%.ts'` であり、
★`frontend/src/x.ts` (直下) には当たらぬ★。此処を `%` 1 個で書くと ★器より広い網★ になり数が膨らむ。
∴ 二段目を足す時は pattern を 1 本づつ写し、写した本数を紙に書く事 (当席は本紙で ★写して居らぬ★ = 上限のみ置いた)。
INCLUDE_PATTERNS の在処 = `v3:48` 以降 (当席が目で数へた範囲で 22 本以上・★終端まで数へて居らぬ★)。

### §5-d `$1` の作り方 (走 1 回・DB へは当たらぬ)
`v3:166 def collect_files(repo_root: Path) -> list[str]:` を ★単体で★ 呼び、返つた list を改行で連ねる。
`main()` は呼ばぬ ∴ upsert も delete も走らぬ。当席は本紙で ★呼んで居らぬ★ (走 0 回)。

## §6 元素を揃へる (o81 の続き)
- §5 の `would_delete_upper` が数へるのは ★DB の行★ である。
- o78 の proxy ★1,722 / 1,724★ は ★git の path★ を元素にした数 ∴ 此処へ代入してはならぬ
  (DB に無い path は消えず、DB にしか無い path は proxy に出ぬ ―― 上限にも下限にもならぬ)。
- o81 の見積 ★1,483★ = 残 5,668 (総監督殿 實測) − 現樹 4,185 (当席 git 数へ) は
  「現樹が悉く DB に在る」時のみ成り立つ近似であり、§5 の SQL は ★其の仮定を要らなくする★ ―― 是が本令の値である。

## §7 測れぬ物 (測れぬと書く)
- DB が現に何を返すか ―― 当席は 0 回も当たつて居らぬ。
- `$1` を作らぬ限り §5 の数は出ぬ (作り方だけ置いた)。
- RLS・鍵の別で見える行が変はり得るか ―― 表定義 20 行に RLS の語は無かつたが、別 migration に在るかは ★探して居らぬ★。
- 他 PC の樹で `collect_files` が何を返すか ―― 手が届かぬ。
- INCLUDE_PATTERNS の総本数 ―― 22 本まで目で数へ、終端まで数へて居らぬ。

## §8 境界
SQL 走行 0 本・DB 讀 0 書 0・走 0 回 (通算 3/5)・push 0・製品 file 書換 0・fetch/pull/prune 0・`main()` 不走・
D 樹 `a2/wt-964a06d0-d3adf65b` 不触・Commander の箱 0 打。
数の 1 = ★行 1 行 / path 1 本 / file 1 本 / pattern 1 本★ (混ぜて居らぬ)。
