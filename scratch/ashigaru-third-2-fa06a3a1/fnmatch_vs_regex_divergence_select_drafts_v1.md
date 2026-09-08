# 入口 regex (L409-415) 対 出口 fnmatch (L258-260) の食ひ違ひ と SELECT 案文

- 前紙: order52 option_c_full_stale_scan_predicate_v1.md `34f11cfac4d55b42` (着手時 再測 一致)・order51 `ae4210d3fc811b36`・order50 `306816953dc056f5`
- 器: v3 main blob `0754d9284` (行番号は皆 此の blob)。as_of 2026-09-07 17:05 JST / 席 ashigaru-third-2 / 令 order53
- ★真偽の出し方★: 下表の真偽は ★合成した形★ (`A/**/*.e`・`A/x.e` 等の作り物) に `fnmatch` と L390-391 の写し取りを当てて得た値である。
  ★v3 script は走らせて居らぬ (--dry-run も打たず)・DB へは触れて居らぬ・実 path 値は 1 つも写して居らぬ★。当席の推しは書かぬ。

## §1 INCLUDE_PATTERNS (L48-84) の型 3 つ

| 型 | 形 | 該当 pattern (L48-84) |
|---|---|---|
| A | `<dir>/**/*.<ext>` | frontend/src・backend・tests・tools・scripts(py/ps1/sh)・infra(tf/ps1/md)・supabase/functions・docs/audits(md/txt/patch/log)・docs/codex_audits・docs/gemini_audits・.claude/skills・.cache/audit_redo |
| B | `<dir>/*.<ext>` | supabase/migrations・supabase/seed・supabase/policies・.claude/rules・.claude/agents・.claude/commands |
| C | `<dir>/<dir>/*` | scripts/git-hooks/* |
| D | 直書き | CLAUDE.md |

## §2 型 × path の形 の真偽表 (★= 入口と出口が食ひ違ふ枡)

| 型 | path の形 | 入口 regex L409 | 出口 fnmatch L258 | 枡 |
|---|---|---|---|---|
| A | 直下 (`A/x.e`) | 真 | 偽 | ★ 表へ入るが (b) は消さぬ ⇒ ㋒ を打つても ★残る★ |
| A | 階層 ≥1 (`A/b/x.e`) | 真 | 真 | 一致 (消える側) |
| A | 深い (`A/b/c/x.e`) | 真 | 真 | 一致 (消える側) |
| B | 直下 (`A/x.e`) | 真 | 真 | 一致 |
| B | 階層 ≥1 (`A/b/x.e`) | 偽 | 真 | ★ 入口は入れぬが (b) は消す側に数へる ⇒ 別経路で入つた古い行に効く |
| C | 直下 (`A/B/x`) | 真 | 真 | 一致 |
| C | 深い (`A/B/c/x`) | 偽 | 真 | ★ 同上 |
| D | 直書き / 別 dir 下 | 真 / 偽 | 真 / 偽 | 一致 |
| 全型 | 拡張子の大小違ひ (`A/X.E` 対 `*.e`) | 偽 | Linux=偽・★Windows=真★ | ★ OS で枡が変はる (§4) |

- 因: `fnmatch` の `*` は `/` を跨ぐが、L390-391 の写しは `**/`→`(?:[^/]+/)*`・`*`→`[^/]*` で ★階層を跨がぬ★。L379-385 の註と同旨。
- 食ひ違ひの向きは 2 つ ―― A 型は「消えぬ側」へ、B/C 型は「消える側」へ倒れる。★同じ 1 走で 両向きが同時に起きる★。

## §3 SELECT 案文 3 本 (讀取のみ・件数のみ・打つは総監督殿)

- S3-1 (A 型 直下 = ㋒ で残る側の候補):
  `SELECT p.prefix, count(*) FROM unnest(ARRAY['frontend/src/','backend/','tests/','tools/','scripts/','infra/','supabase/functions/','docs/audits/','docs/codex_audits/','docs/gemini_audits/','.claude/skills/','.cache/audit_redo/']) AS p(prefix) JOIN public.source_code_cache c ON c.file_path LIKE p.prefix || '%' WHERE strpos(substr(c.file_path, length(p.prefix)+1), '/') = 0 GROUP BY 1 ORDER BY 2 DESC;`
  読み: 結果の和 X ⇒ ㋒ を打つても消えぬ行は ★X の内 作業樹に無い分★。DB だけでは作業樹の有無を分けられぬゆゑ、Y の確定は 測定不能 (X は上限)。
- S3-2 (B/C 型 の深い行 = ㋒ で消える側の候補):
  `SELECT p.prefix, count(*) FROM unnest(ARRAY['supabase/migrations/','supabase/seed/','supabase/policies/','.claude/rules/','.claude/agents/','.claude/commands/','scripts/git-hooks/']) AS p(prefix) JOIN public.source_code_cache c ON c.file_path LIKE p.prefix || '%' WHERE strpos(substr(c.file_path, length(p.prefix)+1), '/') > 0 GROUP BY 1 ORDER BY 2 DESC;`
  読み: 結果 X ⇒ 入口では入らぬ形ゆゑ ★別経路で入つた行★ の数。㋒ を打てば X は消える側に入る (作業樹に在れば残る)。
- S3-3 (大小文字の枡・OS 依存):
  `SELECT count(*) FILTER (WHERE file_path ~ '\.(TSX|TS|PY|SQL|MD|SH|PS1)$') AS upper_ext, count(*) AS total FROM public.source_code_cache;`
  読み: upper_ext = X ⇒ Linux で打てば入口も出口も偽 (消えぬ)。Windows で打てば出口のみ真 ⇒ ★X が消える側へ足される★。
- 3 本とも件数のみを返し、行本文・content は選ばぬ。order50 §4 の 2 本とは重ならぬ (階層別 count / commit_hash 別 count は其方)。

## §4 Linux で打つ時と Windows で打つ時で変はる行

- 変はる: L127 `should_exclude` の `fnmatch.fnmatch`・L258-260 `compute_stale_paths` の `fnmatch.fnmatch` (いづれも `os.path.normcase` 依存 ⇒ Windows で大小を無視)。
- 変はらぬ: L390-391 の写し・L409-415 `matches_include_patterns` (正規表現ゆゑ常に大小を区別)・L169 `is_file()` の有無判定。
- ∴ ★同じ表・同じ引数でも、打つ OS で ㋒ の消す集合が変はる★。どちらで打つかは当席の測る所に非ず。

## §5 境界

- 走行 0 (v3 script・--dry-run とも)・DB 書込 0 讀取 0・DDL 0・fetch 0・本番 code 書込 0・前紙 4 本 不触・推し 0。
- §2 の真偽は合成形に対する値であり、實 path・實 表の行に当てた値ではない。實数は S3-1〜3 を打たねば 測定不能。
- symlink・除外 dir の扱ひは order52 §2 の通りで、matcher の食ひ違ひとは別の筋 (此処では重ねて論じて居らぬ)。
