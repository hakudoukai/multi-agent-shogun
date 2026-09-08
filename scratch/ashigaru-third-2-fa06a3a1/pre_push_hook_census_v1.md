# pre-push hook 讀取 census v1 ── 総監督が「残す/外す/条件付」を裁ける材
as_of: 2026-09-07T06:22:43+09:00
席: ashigaru-third-2 / 令: subtask_thirdpc_a2_pre_push_hook_readonly_census_for_disclosure_001 (order_in_seat 20)
出所: order19 の副作用開示(push が hook を発火させ外部 table へ書いた)
本令で当席が打つた動詞: stat / sha256sum / wc / cat / grep / git ls-files / git status(path 限定) のみ。hook 実行 0・REST 0 叩き・編集 0・chmod 0・push 0。

## 節一 hook 本體
- path: /mnt/c/DentalBI/.git/hooks/pre-push (git の追跡外・.git 配下ゆゑ commit 履歴は 現に無い)
- sha256: 6284d288f4f4e21de5ea3d4c6e56f24c75a450e8b0c0ad7858915670a01a7d49
- bytes=2744 / 61 行 / mode=-rwxrwxrwx / mtime=2026-08-05 11:19:23 +0900
- 「何時誰が置いた」の材は mtime と本文の註記のみ(1 = 註記 1 行):
  - 逐語 L2-4: `pre-push hook: source_code_cache自動同期` / `同期失敗してもpushは中断しない（ただし結果は正直に表示する）。`
  - 逐語 L6: `2026-07-18 委員長修理 (整合性調査で発覚した2欠陥の根治):`
  - 逐語 L8 中: `（7/9設置以来）` ⇒ 初置は 2026-07-09 と本文が言ふ(当席の実測に非ず)
  - 逐語 L34: `── 二重実装の門（理事長令 2026-08-05）──`
- ∴ 置いた主体は 註記の字面では 委員長(7/18 修理)・理事長令(8/5 門)。file 系の裏取りは 測れぬ(.git 配下に履歴無し)。

## 節二 hook が呼ぶ物(1 = file 1 本)
- scripts/sync_source_cache.py sha256=0d5a2258ef1adccb4c4093b82568d575d1a566e1a67eb03254d9b367e00f47a3 bytes=16892 455 行 mtime=2026-09-05 02:16:39
- scripts/check_duplicate_implementation.py sha256=0899f5d1748a60c57cb8126f1ee440eb2eec70baf166ad9dea4cc059c4aaa4bf bytes=6894 159 行 mtime=2026-08-05 11:18:36
- docs/rules/completed-features-registry.yaml sha256=99d1d683e34e92f7f9a2c3ff59a690cc6c5d0ac74eb655c3416b4416ff3fcf81 bytes=4979 107 行(門の逃し先として hook L47 が名指す)
- interpreter は `python3 python py` の順で `-c "import sys"` が通つた最初(逐語 L22-27)

## 節三 門の挙動(push を止め得る唯一の枝)
- 逐語 L41-48: `"$PY" "$DUP_CHECK" --range "${BASE}...HEAD"` → `DUP_RC` が 0 以外なら `exit 1`
- 逐語 L44: `# 1=二重実装の疑い / 2=検査できていない。★どちらも push を止める★`
- BASE は `origin/main`、無ければ `main`(逐語 L39-40)
- DUP_CHECK が無い時は止めず `NOT_CHECKED` を出すのみ(逐語 L51)
- 同期側は止めぬ: 逐語 L58 `FAILED: source_code_cache sync error (push continues; ...)` ・末尾 `exit 0`(L61)

## 節四 書込先(host 種別と table 名のみ・URL の host は伏字)
- host 種別: Supabase の PostgREST(`{SUPABASE_URL}/rest/v1/...`)。host 実体は伏す。
- table = 1 つ: `source_code_cache`(他 table の字面 0 件)
- 動詞 3 つ: POST(upsert・`on_conflict=file_path`・`Prefer: return=minimal,resolution=merge-duplicates`) / GET(`select=file_path` を offset+limit=1000 で全掃) / DELETE(`delete_stale`・`file_path=in.(...)`)
- ∴ 此の hook は push の度に外部 table へ ★書き・消し得る★(DELETE の枝が現に在る)

## 節五 env(名のみ・値 0 字)
- 名 2 本: `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`
- 読む先: 逐語 L39-41 `backend/.env` を `load_dotenv` で読む(path のみ・中身 0 字)
- ∴ push の度に service 権の鍵が使はれる事は 現に在る。鍵の値・host は当紙に 0 字。

## 節六 retry / timeout の逐語(150 字内)
- `MAX_UPSERT_TRIES = 3  # 初回+リトライ2回 (backoff 1s→2s)`(L163)
- `-- TRANSIENT ({type(e).__name__}): retry {attempt}/{MAX_UPSERT_TRIES - 1} in {delay:.0f}s`(L183)
- timeout: upsert=60.0(L154) / GET 全掃=30.0(L252) / DELETE=30.0(L281)
- transient 判定は `httpx.TimeoutException, httpx.TransportError` と `HTTPStatusError`(L168-170)

## 節七 `--no-verify` の字面
- hook 0 件 / sync_source_cache.py 0 件 / check_duplicate_implementation.py 0 件
- 迂回が実際に効くか否かは 測つて居らぬ(本令は hook 実行 0 ゆゑ試して居らぬ)

## 節八 order19 の実走で何が起きたか(既取得 raw の読み直し・新たな実行 0)
- 500 が出たのは `?select=file_path&offset=14000&limit=1000` ⇒ 節四の GET 全掃の途中 ⇒ `delete_stale` へは 到達して居らぬ(削除 0)
- `-- Upserted: 4, Skipped: 0, Errors: 0` ⇒ 外部 table への書込は 4 行
- ★追ひの開示★: 同 script は repo 内の追跡 file も書く。逐語 L437-440 `scripts/sync_file_list.txt` を更新。
  実測: 当該 file mtime=2026-09-07 06:15:11(当席の push の最中)・`git ls-files` で追跡下・`git status --porcelain` は ` M scripts/sync_file_list.txt` 1 行。
  ∴ 当席の push は共有作業樹の追跡 file を 1 本 変へた ── 当席の手に依る編輯では無く hook の物であるが、当席の push を経て起きた。当席は之を戻して居らぬ(戻すは令の外)。

## 節九 三択語の結び
- hook と 2 script の sha・大きさ・時 = 測つた
- 書込先 table 名・動詞・env 名・retry/timeout = 測つた
- 「誰が置いたか」の file 系裏取り = 測れぬ(.git 配下に履歴無し・註記の字面のみ)
- `--no-verify` の実効 = 測つて居らぬ(実行 0)
- 外部 table の現在行数・鍵の権限範囲 = 測れぬ(REST を叩かぬ令)
