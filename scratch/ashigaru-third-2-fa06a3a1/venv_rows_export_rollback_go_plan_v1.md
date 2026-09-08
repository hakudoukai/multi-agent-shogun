# .venv 行の export→rollback→GO 手順 と v2 の追跡外 guard 検分 (order35 產・実行 0)

as_of 2026-09-07 14:3x JST / 席=ashigaru-third-2 / 令=karo-third order35。測り方=file 讀取と git 讀取動詞
(ls-files/check-ignore/status) のみ。DB0・SQL 実行0・script 走行0・push0・commit0・新樹0・D 樹不触。
三択語=測つた/測つて居らぬ/測れぬ。SQL は ★案★ であり当席は 1 本も打つて居らぬ。註 `LIKE` `ON CONFLICT`
`EXCLUDE_DIRS` 等は file と SQL の逐語で当席の判定語ではない。1 = 表の行 1 本。
前提 (当席 未測・家老便 14:23 の総監督実測 0032ec458): `.venv` ★12,527★ + `.venv-linux` ★2,761★ = ★15,288★・A≈400・B 山なし。
## §1 ① v2 は追跡外 file を止めるか ―― ★止めぬ★
### 1-1 列挙は git ではなく作業樹 glob (現 HEAD `59ef7ecd0` L110-122 の逐語)
```
def collect_files(repo_root: Path) -> list[str]:
    for pattern in INCLUDE_PATTERNS:
        for path in repo_root.glob(pattern):        # ← ★git を一切見ぬ★
            if any(part in EXCLUDE_DIRS for part in path.parts): continue
```
L96 `EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git"}` ―― ★`.venv` 無し★ (測つた)。
L87-93 `EXCLUDE_PATTERNS` は `**/__pycache__/**` `**/node_modules/**` `**/dist/**` `**/.git/**`
`frontend/src/vite-env.d.ts` の 5 本 ―― ★`.venv` 無し★ (測つた)。L50 `"backend/**/*.py"` が `backend/.venv/lib/pythonX/site-packages/**/*.py` に当たる。
∴ ★経路 = INCLUDE `backend/**/*.py` × `repo_root.glob` × EXCLUDE 2 表に `.venv` 不在★。
### 1-2 .gitignore は効かぬ (二重に素通り・測つた)
`git check-ignore -v backend/.venv/x.py` → 逐語 `.gitignore:35:.venv/	backend/.venv/x.py` rc=0。
同 `backend/.venv-linux/x.py` → ★出力 0 行★ = ignore されて居らぬ。
∴ `.venv` は git が無視するが collect_files は git を見ぬゆゑ拾ふ／`.venv-linux` は git すら無視せぬ。
### 1-3 patch v2 は此の 3 行を 1 文字も触れて居らぬ (patch の逐語)
v2 の当該 hunk 頭 `@@ -98,6 +99,20 @@ EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git"}`
―― EXCLUDE_DIRS 行は ★hunk header の context★ で `+`/`-` が付かぬ。v2 の新関数
(`stale_paths_from_git` `deleted_paths_since` `matches_include_patterns`) は ★除く側★ の経路で git 差分
D/R を入口にするゆゑ追跡外は其処から入らぬ。然し ★投入側★ は v2 でも `collect_files` の儘 (現 HEAD
L335/L339/L429/L447 の 4 呼出・測つた)。∴ ★v2 を当てても .venv は再び入る★。今 作業樹に `.venv`/`.venv-linux`/`.codex_audit` は無い (`ls` 不在・測つた) が、venv を作り直した次の走行で同じ事が起きる。
## §2 ① 直す案 = patch v3 の差分案 (★適用 0★・commit 0・`--check` も打つて居らぬ)
### 案1 git ls-files 基準 (当席が本命として書く案)
v2 が已に持つ `matches_include_patterns` を再利用でき、投入側と除く側で matcher が 1 本に揃ふ。
```diff
 def collect_files(repo_root: Path) -> list[str]:
-    for pattern in INCLUDE_PATTERNS:
-        for path in repo_root.glob(pattern):
-            if not path.is_file(): continue
+    out = subprocess.run(["git","-C",str(repo_root),"ls-files","-z"],
+                         capture_output=True, text=True, check=True).stdout
+    for rel in filter(None, out.split("\0")):
+        path = repo_root / rel
+        if not path.is_file() or not matches_include_patterns(rel): continue
             if any(part in EXCLUDE_DIRS for part in path.parts): continue
-            rel = str(path.relative_to(repo_root)).replace("\\","/")
             if not should_exclude(rel): files.add(rel)
```
副作用 (仮説・測つて居らぬ): ★追跡外だが同期したい file★ が在れば落ちる。order29 で測つた追跡外は 37 本
(frontend 27/backend 9/scripts 1)・今 再測すると backend の追跡外 .py だけで 21 本 (`git status --untracked-files=all`・測つた)。落ちて困る物が在るかは ★測つて居らぬ★。
### 案2 EXCLUDE に足すだけ (最小・不完全)
```diff
-EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git"}
+EXCLUDE_DIRS = {"node_modules", "__pycache__", "dist", ".git",
+                ".venv", ".venv-linux", "venv", "site-packages", ".codex_audit"}
```
名を知つた物しか止められぬ (次の名が来れば同じ事が起きる)。案1 と併用も出来る。
★孰れを採るかの裁は家老・総監督に在る。当席は適用も commit も行つて居らぬ。★
## §3 ② export 案 (実行は総監督の器・当席 0)
```sql
-- (a) 件数と大きさ。期待 15,288。実行は総監督 GO 後
SELECT count(*) FILTER (WHERE file_path LIKE 'backend/.venv/%')       AS venv_rows,
       count(*) FILTER (WHERE file_path LIKE 'backend/.venv-linux/%') AS venv_linux_rows,
       count(*) AS both_rows, sum(file_size) AS bytes_content,
       min(created_at) AS first_seen, max(updated_at) AS last_touched
FROM public.source_code_cache
WHERE file_path LIKE 'backend/.venv/%' OR file_path LIKE 'backend/.venv-linux/%';
-- (b) export 本体 (7 列全部・content を含む)。出力先は総監督の器。実行は総監督 GO 後
SELECT file_path, content, file_size, line_count, commit_hash, updated_at, created_at
FROM public.source_code_cache
WHERE file_path LIKE 'backend/.venv/%' OR file_path LIKE 'backend/.venv-linux/%'
ORDER BY file_path;   -- psql なら \copy (…) TO 'venv_rows_20260907.csv' CSV HEADER
```
大きさの見積: ★測れぬ★。`.venv` は今 作業樹に無く file を讀めぬゆゑ 1 byte も測れて居らぬ。∴ (a) の
`sum(file_size)` を ★先に★ 打ち、其の値で export 先の空きを判じて頂きたい (外挿は仮説ゆゑ数を書かぬ)。
## §4 ③ rollback 案 (export file から同 PK で戻す)
```sql
-- 実行は総監督 GO 後
CREATE TEMP TABLE venv_restore (LIKE public.source_code_cache INCLUDING DEFAULTS);
\copy venv_restore FROM 'venv_rows_20260907.csv' CSV HEADER
INSERT INTO public.source_code_cache
       (file_path, content, file_size, line_count, commit_hash, updated_at, created_at)
SELECT  file_path, content, file_size, line_count, commit_hash, updated_at, created_at
FROM venv_restore
ON CONFLICT (file_path) DO UPDATE SET content = EXCLUDED.content,
  file_size = EXCLUDED.file_size, line_count = EXCLUDED.line_count,
  commit_hash = EXCLUDED.commit_hash, updated_at = EXCLUDED.updated_at;
```
件数照合 (3 つとも成り立つ事): ⑴`count(venv_restore) = 15,288` ⑵`DELETE 前 − 後 = 15,288`
⑶`rollback 後 count(*) = DELETE 前 count(*)`。
## §5 ④ GO checklist (総監督が押す前の 8 項・当席は 1 つも押して居らぬ)
1. §3(a) の `venv_rows + venv_linux_rows` が ★15,288★ と一致するか (ずれたら止まる)
2. §3(a) の `sum(file_size)` を測り、export 先に其れ以上の空きが在るか
3. export file の行数が 15,288 + header 1 行か・sha256 を控へ、別媒体 (別 disk か別 host) へ 1 本 置いたか
4. (3 と併せて) 控へた sha256 と置いた先の path を紙に残したか
5. rollback の乾走: TEMP 表へ `\copy` し `count(*)=15,288` まで測つたか (本表へ INSERT せず)
6. patch v3 が現 HEAD で `git apply --check` rc=0 か ―― ★未作成★ ゆゑ当席は ★測つて居らぬ★
7. DELETE の WHERE が §6 の 2 条件のみか (`LIKE 'backend/.venv%'` の 1 本書きにして居らぬか)
8. DELETE を打つ器・打つ人・時刻を控へたか (打つのは総監督・当席は打たぬ)
## §6 ⑤ DELETE 文 (各行に「実行は総監督 GO 後」・当席は実行 0)
```sql
BEGIN;                                                --  実行は総監督 GO 後
DELETE FROM public.source_code_cache                  --  実行は総監督 GO 後
WHERE file_path LIKE 'backend/.venv/%'                --  実行は総監督 GO 後
   OR file_path LIKE 'backend/.venv-linux/%';         --  実行は総監督 GO 後
-- 此処で count(*) を測り DELETE 前 − 後 = 15,288 を確かめる  -- 実行は総監督 GO 後
COMMIT;  -- 合はねば ROLLBACK;                        --  実行は総監督 GO 後
```
★1 本書き `LIKE 'backend/.venv%'` を避けた理由★: 其の型は `backend/.venvXYZ` の様な別 path も拾ふ。
2 条件に分ければ範囲が `/` で閉ぢる (測つた性質ではなく LIKE の定義から言へる)。
## §7 ★開示★
1. ★数が 17 合はぬ★: 総監督実測 15,288 に対し order33 の 15,271 (=20,903−5,632) は ★17 少ない★。∴ git で
   説明できる筈の 5,632 のうち ★17 path は表に無い★ (引き算は測つた・因は未測)。§5-1 で 15,288 と
   15,271 の孰れを採るかは裁が要る。当席は 15,288 を前提に書いた。
2. `.codex_audit` は今 作業樹に無く現 INCLUDE 型で拾はれる道も見付けて居らぬ。令に名が在つたゆゑ案2 の
   除外表には入れたが ★拾はれた証跡は測つて居らぬ★。
3. patch v3 は ★作つて居らぬ★ (紙の差分案のみ)。∴ `git apply --check` も ★打つて居らぬ★。作れとの令が在れば枝 `-v3` で作る (commit は自席枝のみ・push 0 の床は不変)。
4. §3〜§6 の SQL は当席が ★1 本も打つて居らぬ★。DB の器は当席に 0 本の儘である。
## §8 先の紙の sha 再測 (床(27)・as_of 14:3x)
393e15d70eb2a148 50 行 o34 紙 / ea20e81d75e95ade 80 行 o33 紙 / b99e75d8d356ec46 554 行 patch v2 /
2ec2a8d7931b0df3 69 行 o30 紙
