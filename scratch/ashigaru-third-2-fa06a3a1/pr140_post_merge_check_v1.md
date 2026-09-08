# PR#140 merge 後の検算 —— 減=0 を測る SELECT 2 本・期待値表・規 (案文のみ・DB 0)

as_of 2026-09-08T04:59+09:00 / 席 ashigaru-third-2 / 令 order74 (家老 裁=弾A)
前紙: 設計 `ci_sync_unify_design_v1.md` 80行 sha16 `3c3329b0010f273f` / 併記 `o73_paper_vs_deed_addendum_v1.md` 28行 sha16 `d976795618ab3872` —— ★何れも不触★
写し (総監督 裁288144): `source_code_cache` **4,249 行**・distinct 4,249・csv sha256 先頭 `a98d3b07f289c7de` (4,250 行=header 込)
★SELECT は案文のみ・打つは上官★。当席は DB へ 0 打。

## §1 「減」の判じ方 (一行・四条②)
★減 = 写し(pre) に在つた file_path のうち、CI 走行後(post) の表に無い本数。1 = file_path 1 本。★
★行数の差ではない★ —— CI は書き足すゆゑ、増が減を覆ひ隠す (四条③: 意味の違ふ数を足し引きせぬ)。
∴ `count(*)` の前後比較だけでは ★減=0 を測れぬ★。§2 の ② が本命、① は早見に過ぎぬ。

## §2 SELECT 2 本 (実行 0)

★① 早見 (安くて粗い)★
```sql
select count(*) as rows, count(distinct file_path) as paths, max(updated_at) as latest
from source_code_cache;
```
期待列 rows / paths / latest ・期待行数 1

★② 本命 (減を測る唯一の形)★
```sql
select file_path from source_code_cache order by file_path;
```
期待列 file_path ただ 1 列・期待行数 4,249 以上 (見込み)。
出力を csv (先頭行に列名 `file_path`) で保存し §3 の規へ渡す。
註: REST 経由は既定で 1,000 行上限ゆゑ、`limit`/`offset` の頁繰り (または psql の \copy) で ★全行★ を採る事。頁を落とせば ★落とした分が「減」に化ける★。

## §3 突き合はせ表 (出た値 → 読み)
| 出た値 | 読み |
|---|---|
| ② の 減 = 0 本 | `--no-stale` が効き CI は消して居らぬ (令の狙ひ通り) |
| ② の 減 ≥ 1 本 | 消えた ―― 旗が効いて居らぬか、他の経路 (手打ち・別 workflow) が消した。★戻すか否かの判断は上官★ |
| ② の 増 = 0 本 | CI が書けて居らぬ疑ひ (upsert の失敗・差分 0・secret 名の不一致 いづれか) |
| ② の 増 ≒ 637 本 | CI にのみ在つた 3 除外が外れて目が広がつた分 (見込み・o73 紙 §2 の数) |
| ① の paths ≠ rows | 鍵が壊れて居る (本来 file_path は一意・v3 L121 `UPSERT_CONFLICT_KEY`) |
| ① の rows < 4,249 | 早見の段で既に減つて居る ⇒ ② を待たず上官へ |
| ① の latest が CI 走行時刻より前 | CI が表へ届いて居らぬ (走つたか否かは Actions の log で) |

## §4 規 (五条: script で残す)
`scratch/ashigaru-third-2-fa06a3a1/o74_no_decrease_check.py` **61 行**・★sha256 先頭 16 = `2009dc96e8fd995d`★
(★sha の種★: git blob hash に非ず・file の sha256 の先頭 16 桁。写しの `a98d3b07f289c7de` も同じ種)
- 打ち方: `python3 o74_no_decrease_check.py <pre.csv> <post.csv> [--expect-pre 4249]`
- 出す数: pre/post の 行数・一意数・sha256_16、★減★ の本数、★増★ の本数、減つた path を先頭 20 本
- 戻り値: 減 0 なら 0 / 減 1 本以上なら 1 / csv が読めねば 2 —— ★DB へ触れぬ (csv 2 本を讀むのみ)★
- 自己試験 (当席が走らせた・scratch の作り物 3 本): 減 1 本の形で rc=1 と `減=1 本`、
  ★行数が 3→4 と増えても減 0 の形では rc=0★ (増が減を隠さぬ事を此処で確かめた)

## §5 手順 (上官の打つ順)
1. merge 前に写しが在る事を確かめる (4,249 行・`a98d3b07f289c7de`)
2. merge → 初回 CI 走行 → Actions の log で sync step の成否を見る
3. ① を打つ (早見)。rows < 4,249 なら此処で止める
4. ② を打ち post.csv を採る (★全行★・頁落ち無し)
5. §4 の規へ pre.csv と post.csv を渡し、★減=0★ を見る

## §6 境界
DB 讀 0・書 0・SQL 実行 0 本 (案文 2 本を書いたのみ) / 走行 0 (走らせたは §4 の自己試験のみ・作り物 csv) /
fetch・pull・clone・push・prune 0 / PR#140 へ手を入れて 0 / 製品 file へ 0 字 / shell `>` `>>` `tee` 0 (書込は python `open()`) /
secret の値 0 (名のみ) / 患者本文 0 / 他席の inbox へ書込 0 / Commander の箱 0 打 / 旧樹 wt-964a06d0 不触。
4,249・637 は ★当席が数へた数に非ず★ (前者=総監督の實測・後者=o73 紙の見込み)。
