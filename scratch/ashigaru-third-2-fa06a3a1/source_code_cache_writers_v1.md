# source_code_cache の書き手 棚卸し (order30)

as_of: 2026-09-07 10:28 JST / 席=ashigaru-third-2 / 令=order30
測り方: 讀取のみ (grep・git 読取動詞・sed -n)。走行 0・DB 0・新樹 0・push 0。
樹: /mnt/c/DentalBI (本樹・書込 0)。行番は as_of 時点の作業樹の実測。
三択語: 測つた / 測つて居らぬ / 測れぬ。

## §0 語の註
本紙に現れる `resolution=merge-duplicates` `ON CONFLICT` `--diff-filter` 等は
file の逐語 (機械の語) であり、当席の判定語ではない。

## §1 表名を含む file の数 (測つた)
- 作業樹の全 file を grep: **119 本** (1 本 = 表名 source_code_cache を含む file 1 個・追跡外を含む)
- `git grep -l ... HEAD`: **107 本** (1 本 = HEAD に載る file 1 個)
- 差 12 本 = 追跡外 (生成物・scratch 等)。内訳は本紙の令外ゆゑ写して居らぬ。
うち「表へ実際に書く」器は下表の 7 系統。他は讀取・文書・試験である。

## §2 書き手表 (file・行・契機・path の組み方・key)
| # | 書き手 (file) | 要点行 | 走る契機 | file_path の組み方 | upsert key | commit_hash |
|---|---|---|---|---|---|---|
| 1 | scripts/sync_source_cache.py | L110 collect_files / L128 rev-parse / L143 upsert_batch / L266 delete_stale / L309 repo_root | 人手・pre-push (既定 skip)・ps1 経由 | L309 `repo_root = Path(__file__).parent.parent` を起点に glob → 相対化 → "/" | 旧=無指定 / 当席 patch 後=`on_conflict=file_path` + merge-duplicates | `git rev-parse --short HEAD` (L128) |
| 2 | .github/workflows/sync-source-cache.yml (CI inline python) | L3-7 on.push / L60 Prefer / L114 rel / L119 repo / L127,134 diff-filter / L169 post / L185 delete | push to `main` と `feature/**` (paths 限定: frontend/src, backend, tests, tools) | L119 `repo = Path(".")` = runner の workspace。L114 `rel = str(path.relative_to(root)).replace("\\","/")` | L60 `Prefer: resolution=merge-duplicates` (on_conflict 無指定) | L121 rev-parse --short HEAD |
| 3 | scripts/sync_source_cache_secondpc.py | L23 REPO_ROOT / L24 OUT_DIR / L189 INSERT / L197 ON CONFLICT | 人手 (REST を打たず batch SQL を生成するだけ) | L23 `Path(__file__).resolve().parent.parent` 起点の相対 | L197 `ON CONFLICT (file_path) DO UPDATE SET` | 生成時の変数 |
| 4 | scripts/call_sync_temp.py | L19 REPO_ROOT / L20 Edge Function / L34-37 manifest / L76 httpx.post | 人手 | manifest.json の file_path をそのまま送る (自前で組まぬ) | POST 先は Edge Function `sync-source-cache-temp` ゆゑ key は関数側 (讀めて居らぬ) | L36 manifest.commit_hash |
| 5 | docs/audits/source_code_cache_sync/batch_001..011.sql | 各 L2 付近 | 人が psql 等で打つ (打たれたか測つて居らぬ) | #3 が生成した時点の相対 path が埋込 | 埋込 `ON CONFLICT (file_path)` | 埋込 (manifest commit=69a9be10) |
| 6 | scripts/push_and_sync.ps1 | L17 git push / L27 Join-Path / L37 python 呼出 | 人手 (Windows 側) | #1 を呼ぶだけ | #1 に従ふ | #1 に従ふ |
| 7 | scripts/git-hooks/pre-push (正本) → .git/hooks へ配備 | L58-60 既定 skip / L64 --changed-only | git push | #1 を `--changed-only` で呼ぶ | #1 に従ふ | #1 に従ふ |

補: #5 の manifest は included=40・batches=11 (1 = SQL file 1 本)。#4 も同じ manifest を讀む。

## §3 prefix 別結果との対応表 (★仮説★・未検証)
order29 §3 ⑵ の `split_part(file_path,'/',1)` を受けた時の当て方。いづれも仮説である。
| prefix の見え方 | 当席の当て (仮説) | 見分けの根拠 (仮説) |
|---|---|---|
| frontend / backend / tests / tools のみが厚い塊 | #2 (CI) | CI の paths 限定が此の 4 つに一致する |
| scripts / docs / shim 等も含め広く薄い | #1 (script) | #1 は paths 限定を持たず INCLUDE 35 型を全域 glob する |
| manifest の 40 本と一致する塊 | #4 | 送る path が manifest そのもの |
| #3 が生成した時点の 40 本と一致 | #3 → #5 | #4 と同じ manifest ゆゑ ★#3/#4/#5 は prefix では見分けられぬ★ |
| 現行の型に無い拡張子 (歴代の型) | #1 の旧版 | order29 で歴代和 +3 と測つた (小さい) |
★prefix だけでは #1 と #2 を見分けられぬ★ ―― 両者とも repo 相対 + "/" で同形になる。
見分けるなら commit_hash (#2 は CI の runner の HEAD) と updated_at の時刻分布を併せて視るほか無い。
∴ order29 の 15,271 の差の帰属は、本紙の讀取だけでは **測れぬ**。

## §4 ⑥ 当席 patch が触れる書き手
当席 order28 の patch (ce2df0f39d0acc93 / 565 行・as_of 再測) が触れるのは **#1 のみ**。
#2 CI inline python・#3・#4・#5・#6・#7 の本文は 1 行も触れて居らぬ (patch の対象 file は 2 本)。
∴ #1 に `on_conflict=file_path` を入れても、#2 の無指定 upsert は元のまま残る。

## §5 ★開示 (令の欠・当席の過ち を含む)★
1. ★二重の試験★: 既存 `tests/test_sync_source_cache.py` (245 行・試験 10 本・相談役 seq129633 監査由来) が
   在るのに、当席 order28 は同主題の試験群を別に足した。Anti-Duplication に触れる疑ひが在る。
   既存の在処を order28 の時点で測つて居らぬ ―― 当席の過ちである。
2. ★既存 10 本を patch 後の #1 に対して走らせて居らぬ★ = 測つて居らぬ。
   新樹 0・走行 0 の令ゆゑ今は **測れぬ**。走行の GO を仰ぐ。
   読みだけの見立て (仮説): 既存 `test_main_calls_cleanup_with_full_collect_files` は
   DB 讀取が失敗すると full scan へ落ちる道が残るゆゑ壊れぬ見込み。★測つて居らぬ★。
3. module 名衝突: `tests/__init__.py` 在り・`scripts/tests/__init__.py` 無し・`scripts/__init__.py` 無し・
   `pytest.ini` は `[pytest]` のみ ⇒ 名が異なるゆゑ import 衝突は起きぬ見込み (仮説)。
   `scripts/tests/` に sync 関連の試験は **0 本** (測つた)。
4. ★書き手が 7 系統在る事自体が令の前提に無かつた★。order29 の紙は #1 だけを念頭に書いた。
   #2 の `repo = Path(".")` は runner の workspace であり、#1 の `__file__.parent.parent` と
   別の根に成り得る ―― order29 で残した「別 root」説に此処が繋がる (仮説)。
5. #4 は REST を直に打たず Edge Function を叩く。関数の中身は本樹に無く **讀めて居らぬ**。
6. #5 の batch SQL 11 本が実際に打たれたか否かは DB 讀取が要る ⇒ **測れぬ** (DB 0 の令)。

## §6 先の紙の sha 再測 (床(27))
- sync_source_cache_rewrite_v1.md sha16=ac838d986f8c20ca 131 行 (order28 產)
- 0001-...pytest-15.patch sha16=ce2df0f39d0acc93 565 行
- rows_20903_under_pk_v1.md sha16=78534cba04087c34 100 行 (order29 產)
