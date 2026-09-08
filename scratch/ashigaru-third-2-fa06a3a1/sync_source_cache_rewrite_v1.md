# sync_source_cache.py 抜本策 v1（order28 產）

as_of: 2026-09-07 10:2x JST（測定は同日 09:56〜10:2x に実施）
席: ashigaru-third-2 / 令: karo-third order28（総監督 seq283366 ⑶）
枝: a2-fa06a3a1-sync-rewrite / commit 1de681b15 / 樹: /home/hakudoukai/a2/wt-order28-sync-rewrite
base: 8daf47adb2ec31cb3ffc2591276cc3c20082c904（樹を切つた刻の共有 HEAD・当席が rev-parse で測つた）

## §0 三択語の約束
本紙の各数は「測つた／測つて居らぬ／測れぬ」を明示する。推量は「仮説（未検証）」と書く。
語の註: 本紙に現れる `STALE_CLEANUP_FAILED` `COUNT_CHECK_FAILED` は script が吐く印字子の逐語、
`Supabase secret scan PASS: ...`（§7-4）は commit 時に hook が吐いた逐語である。
いづれも ★当席の判定語ではない★。当席は判定の語を用ゐぬ。

## §1 產物（1 = file 1 本を 1 と数へた）

| 物 | path | sha16 | 行数 |
|---|---|---|---|
| patch | scratch/ashigaru-third-2-fa06a3a1/0001-sync_source_cache-stale-git-upsert-pytest-15.patch | ce2df0f39d0acc93 | 565 |
| 本体 | <樹>/scripts/sync_source_cache.py | 3211f34abad9eb7b | 667（base 464） |
| 試験 | <樹>/scripts/tests/test_sync_source_cache.py | 78a7603218737587 | 237（新設） |

patch 統計（git show --stat 逐語）: `2 files changed, 450 insertions(+), 10 deletions(-)`。
1 = 行 1 本を 1 と数へた。patch の byte 数 23,907（測つた）。

## §2 改めた中身

### ⓐ stale 検査を git 差分へ
- 前回 sync commit を ①DB（commit_hash を updated_at 降順 limit=1）→ ②state file
  `sync_last_commit.txt` の順で読む。
- `git diff --name-status --diff-filter=DR prev..HEAD` の D（削除）と R の旧 path のみを
  DELETE 対象とする。M/A は対象にせぬ。
- prev が無い・`git cat-file -e <rev>^{commit}` で引けぬ・`--full-stale-scan` 指定の三つの時のみ
  従来の全件 pagination へ落ち、`-- STALE_FALLBACK_FULL_SCAN: reason=...` を stderr へ出す
  （黙つて落ちぬ）。git が非零で返れば RuntimeError を上げ、order26 の
  `STALE_CLEANUP_FAILED`（stale_source 付き）へ流す。

### ⓑ 重複行を作らぬ
- upsert に `on_conflict=file_path` を明示（`UPSERT_CONFLICT_KEY`）。
- 根拠: 移行 `supabase/migrations/20260403020939_create_source_code_cache.sql` に
  `file_path TEXT PRIMARY KEY`。全移行を grep した限り PK を変へた文は無かつた（測つた）。
  ただし ★稼働 schema そのものは測つて居らぬ★（DB 讀取が令で 0 ゆゑ）。
- 走行末尾の「全件を再び頁繰りして数へる」二周目を除き、`Prefer: count=exact` +
  `Range: 0-0` の content-range 1 本に替へた（`-- Cache total: N rows`／失敗時
  `-- COUNT_CHECK_FAILED`）。

### ⓒ batch50 据置・pytest
- `BATCH_SIZE == 50` を試験で釘付け。50 行 = 呼出 1 回を試験で示した。

## §3 pytest（1 = 試験函数 1 本を 1 と数へた）

逐語: `15 passed in 1.57s`。skip 行は出て居らぬ = ★skip 0★（測つた）。
網は塞いだ: `monkeypatch.setattr(mod.httpx, "get"/"post"/"request", boom)`。
tmp git repo を実際に作り D/M/A/R を置いて確かめた。

## §4 --dry-run 新旧比較（raw・同一 cwd=樹）

raw: scratch/ashigaru-third-2-fa06a3a1/order28_dryrun_compare.json

| | 旧 (HEAD:scripts/sync_source_cache.py) | 新 (a2-fa06a3a1-sync-rewrite) |
|---|---|---|
| stdout byte | 181,281,492 | 181,281,492 |
| stdout sha256 | 7cfa1cdd2258…a7f3 | 7cfa1cdd2258…a7f3 |
| INSERT 文（1 = 文 1 本） | 4,090 | 4,090 |
| stderr | `-- Full sync mode: 4113 files detected` / `-- Dry-run complete: 4113 files` | 同左 |
| rc | 0 | 0 |
| 秒 | 2.6 | 3.3 |

∴ ★--dry-run の吐き出しは新旧で byte 一致★（測つた）。stale/count の道は --dry-run では
走らぬゆゑ、本紙の一致は「INSERT 側を壊して居らぬ」ことのみを示す。stale/count 側の
確かめは §3 の試験に依る。

### 4-1 4113 と 4148 の差（開示）
order27 で本樹 /mnt/c/DentalBI を数へた時は 4,148 file。本比較の樹では 4,113。
差 35 の因は ①worktree に追跡外 file が無い ②比較中だけ樹の scripts/ に旧版の写しを
1 本置いた（両走行に同じく在り・後に除いた）の二つ。①の内訳は ★測つて居らぬ★。

## §5 差 23（INSERT 106 対 席算 83）— 仮説・いづれも未検証

order27 で、総監督 seq283366 の INSERT 106 と当席の dry-run 由来 POST 83 が合はなんだ。
- ★重複行仮説は移行の記録と食ひ違ふ★: file_path が PK である以上、同 path で行は増えぬ。
  ただし稼働 schema は測つて居らぬゆゑ「否定した」とは書かぬ。
- 候補①（未検証）: `upsert_batch_with_retry` / `upsert_with_isolation` の再試行・分離送信で
  同一 batch が複数回 POST される。83 + 23 = 106 は数の上では合ふ。数が合ふ事は因の証にあらず。
- 候補②（未検証）: 計測時と当席の走行で対象 file 数が違つた。
- 候補③（未検証）: 打つた者が別（CI の inline python は 1 file = 1 POST・batch 無し）。
∴ 切り分けには DB 側の SELECT が要る。当席は DB 讀取 0 の令ゆゑ打つて居らぬ。

## §6 DB 書込 0 の証

- 走らせた形は `--dry-run` のみ（比較 harness は `[sys.executable, script, '--dry-run']` を逐語で渡す）と
  pytest のみ。それ以外の走行 0（測つた）。
- 試験 file に接続文字列は 0 行:
  `grep -nE 'https?://|SUPABASE|postgres|DATABASE_URL|service_role' scripts/tests/...` → 該当 0 行。
- ★併せて開示（都合の悪い測り）★: 当席 env には接続系の変数名が ★8 本★ 在る（1 = env 変数名 1 個を 1 と数へた）
  （DATABASE_URL / SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 等・名のみ列挙、値は 0 打）。
  ∴ 「DB を打たなんだ」は資格が無かつたからではなく ★走らせた形が --dry-run のみだつたから★ である。
  素で走らせれば本番へ届く。この芽は令の外ゆゑ当席は手を触れず、家老へ上げる。

## §7 令と実際の食ひ違ひ（黙つて迂回せず開示する）

1. ★base の指し違ひ★: 令の task 塊は `shared_head_at_assign: 030e15684` と書いて居たが、
   樹を切つた刻の実測は `8daf47adb2ec31cb`、本紙を書く刻の再測は `d4e693633e6d14c0`。
   本樹 HEAD は動き続けて居る（三値とも測つた）。patch の base は 8daf47ad である。
2. ★前の樹が残つて居る★: 家老は order27 受理便で「樹 remove 済 家老実測」と書かれたが、
   `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` は今も disk に在り、追跡外の log が 2 本在る
   （測つた）。当席の物ではない疑ひも有るゆゑ ★手は触れて居らぬ★。裁を仰ぐ。
3. ★commit は共有 .git へ object を書く★: 令は「本樹 書込 0・commit 0」と、
   「自席枝で format-patch せよ」を併せて命じて居る。worktree add の時点で既に枝 ref は
   共有 .git に書かれる。当席は後者を令の明示として commit したが、本樹の
   checkout / HEAD / 追跡枝には触れて居らぬ（測つた）。禁の広狭の裁を仰ぐ。
4. ★commit 時に hook が己の語を印字した★ 逐語:
   `Supabase secret scan PASS: no tracked secret values detected.`
   —— これは hook 自身の語であり、★当席の判定ではない★（当席は判定語を用ゐぬ）。
5. ★fnmatch と glob の食ひ違ひは旧道に残して在る★: `compute_stale_paths` は fnmatch ゆゑ
   `scripts/**/*.py` が `scripts/a.py` に当たらぬ。git 差分の道だけ glob と同義の正規表現に
   替へ、旧道は触れて居らぬ（落ちた時の DELETE 量を、測れぬまま広げぬ為）。
   両者の振舞を試験 2 本で釘付けにして在る。
6. ★頁繰り 12 の因★: 走行 1 回につき全件 pagination が ★2 周★ 在つた（order27 で測つた）。
   総監督の 12 頁は 2 × 6 頁と数が合ふ（仮説・未検証）。今日の 20,903 行なら 2 × 21 = 42 頁に
   なる筈で、本 patch は 2 周目を 1 本の count に替へた。1 周目（fallback 時のみ）は残る。

7. ★当席が床⑾を破つた（自己申告）★: 便の字数を測る折、`echo "$M" > scratch/.../.o28_msg.txt` と
   shell の `>` で file を 1 本作つた。床⑾は「file 書込は python open() で行へ・shell の
   `>`/`>>`/tee を使ふな」である。気付いて即座に python で除いた（除去を測つた: 除去後 False）。
   産物への影響は無い（当該 file は本紙にも patch にも入つて居らぬ）が、破つた事実を残す。

## §8 残る限界

- 稼働 schema・行数 20,903・差 23 の実体は ★測つて居らぬ★（DB 讀取 0 の令に依る）。
- 本 patch は push して居らぬ（GO 別）。CI の inline python（本 script を呼ばぬ第二の書き手）は
  本 patch の外に在り、手を触れて居らぬ。
