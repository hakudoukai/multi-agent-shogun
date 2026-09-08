# order87 案①: 退避 hook が名を戻された時に止まる門 ―― 案文のみ (讀取のみ・hook 書換 0)

as_of 2026-09-08 07:2x JST / 席 ashigaru-third-2 / 令 order87 (家老 `msg_20260908_070139_ca92e97a`)
★縛り (令 逐語)★: 「退避 hook の名を戻すな・動かすな(★案文のみ・書換 0★)・出所は讀取で辿れる限り(辿れねば『辿れぬ』と書け)」
対象 = 共有樹 `/mnt/c/DentalBI/.git/hooks/`。前紙 o78 `..._mouths_census_v1.md` §5 危険① を承ける。前紙は書き換へず本紙で補ふ。
1 = file 1 本 / 行 1 本。

## §1 二版の實測 (讀取・sha256 の頭 16)

| 名 | bytes | 行 | sha16 | 止血の門 | sync の口 |
|---|---|---|---|---|---|
| `.git/hooks/pre-push` (現用) | 3,399 | 70 | `e4a47593600691e3` | ★有 (3 箇所)★ | 2 |
| `.git/hooks/pre-push.bak-loadshed-20260907` (退避) | 2,744 | 61 | `6284d288f4f4e21d` | ★無 (0)★ | 2 |
| `scripts/git-hooks/pre-push` (repo 正本・作業樹) | 3,399 | 70 | `e4a47593600691e3` | 有 | 2 |
| `.git/hooks/pre-commit` / `scripts/git-hooks/pre-commit` | 696 | 28 | 両者 `8030a506e0c127d7` | ― | 0 |

- ★現用 hook は repo 正本と逐語同一★ (`diff -u` の出力 0 行)。追跡簿 blob も `origin/main` `HEAD` 共に `911cbab96061` で一致。
- 二版の差 = ★止血 9 行の「追加のみ」・削除 0★ (`diff -u` 退避→現用 = `@@ -51,6 +51,15 @@` の 1 hunk のみ)。逐語:
  `if [ "${SYNC_SOURCE_CACHE_FORCE:-0}" != "1" ]; then` / `echo "[pre-push] source_code_cache sync SKIPPED …"` / `exit 0` / `fi`
- ∴ ★名を `pre-push` へ戻す = 止血の門だけを外す事に等しい★ (他は 1 byte も違はぬ)。
- CRLF 0 (両版とも `\r\n` = 0)。

## §2 出所 ―― 誰が・何時・何故 (★辿れた★)

| 問 | 答 | 出所 (讀取) |
|---|---|---|
| 誰が | ★iincho (委員長)★ | repo commit `94f078059` の author |
| 何時 | ★2026-09-07 08:03:35 +0900★ (repo) / disk mtime は `08:01:55` | `git log -1` / `ls -la` |
| 何故 | 「source_code_cache 同期を既定 skip(DB負荷止血 2026-09-07・main は CI が同期・SYNC_SOURCE_CACHE_FORCE=1 で強制)・dev_qa#822」 | 同 commit の題 (逐語) |
| 台帳に載るか | ★載る★。`docs/rules/fleet-composition-manifest.yaml:2300` に退避 file の名が逐語で在り | 同 file |
| 台帳の逐語 | 「third pre-push hook: source_code_cache sync 既定skip (.git/hooks/pre-push.bak-loadshed-20260907・repo scripts/git-hooks/pre-push 94f078059)」 | 同 |

- ★退避 file の中身は追跡簿に残つて居る★: commit `4b1f7d293` (2026-08-05 ashigaru-third-5「二重実装を push の瞬間に止める」) の
  `scripts/git-hooks/pre-push` = blob `6d4039bb1671`・2,744 byte・61 行・sha16 ★`6284d288f4f4e21d`★ ―― 退避 file と ★逐語同一 (byte 比較)★。
- ∴ ★退避 file が担ふ「止血前の姿を残す」役は、git が既に担つて居る★ (`git show 4b1f7d293:scripts/git-hooks/pre-push` で取れる)。
- 辿れなんだ物 = ★無し★ (令の「辿れねば『辿れぬ』と書け」に該当する項 0)。

## §3 危険① の形を精緻にする ―― 何が起これば発火するか

前紙 o78 §5 危険① は「名を `pre-push` へ戻すと push 毎に stale が走る」と書いた。本紙で発火の条件を細かく分ける。

- `core.hooksPath` = ★未設定★ ∴ git が見るのは `.git/hooks/` ただ一つ。worktree も此処を共有する
  (當席の a2 樹からの push で `[pre-push] source_code_cache sync SKIPPED` を現に見た = 止血は今 効いて居る)。
- 配る器 `scripts/git-hooks/install.sh` (626 byte・22 行・`e2b3b58c28b94baa`) の振舞ひ (逐語 L11-21):
  `for hook in "$HOOKS_SRC"/*` … `cp "$hook" "$HOOKS_DST/$name"` / `chmod +x "$HOOKS_DST/$name"`
  ∴ ★src (`scripts/git-hooks/`) に在る名だけを配る★。退避 file は src に無い ∴ ★install.sh は退避 file を消しも上書きもせぬ★。
  同時に ★install.sh を走らせれば `.git/hooks/pre-push` は止血版で上書きされる★ (止血は自ら回復する側)。
- ∴ ★発火は「人が手で `mv`/`cp` して名を `pre-push` に戻した時のみ」★。器が勝手に戻す道は ★見付からぬ★。
- 発火した時に起きる事 (前紙 o78 §2 #2' の逐語): `if "$PY" "$SYNC_SCRIPT" --changed-only; then` ―― ★`--no-stale` を持たぬ★
  ∴ 枝差分の upsert に加へ stale 検査が走る。之が総監督が 2026-09-07 に止めた其の物。
- ★併せて記す (install.sh 自身の副作用)★: L17 `sed -i 's/\r$//' "$hook"` は ★src 側 = 追跡簿の file を書き換へる★。
  走らせれば作業樹が汚れ得る (CRLF の樹では差分が立つ)。本弾では走らせて居らぬ ∴ ★現に汚れるかは確かめて居らぬ★。

## §4 案文 (五つ・★どれも当てて居らぬ★・hook file の書換 0)

★令が求めた「門を付ける」に直に当たるのは C★。他は比較のために並べる。効く範囲と欠けを対で書く。

### 案文 A ―― 退避 file に止血 9 行を移植する
- 効く範囲: 名を戻しても sync は走らぬ。
- 欠け: 移植後は現用と ★逐語同一★ に成る ∴ 退避 file の役 (止血前の姿) が消える。且つ其の役は git が既に担ふ (§2) ∴ ★得る物が「現用の写しが 2 本」以外に無い★。

### 案文 B ―― 実行 bit を落とす (`chmod -x`)
- 効く範囲: 名が `pre-push` でも git は走らせぬ。
- 欠け: `mv` は bit を保つ ∴ 名を戻す操作が `mv` なら ★bit も一緒に戻る = 効かぬ★。`cp -p` も同じ。人が `chmod +x` を打てば戻る。

### 案文 C ―― 退避 file の頭に「己の名を見て止まる門」を足す
- 案文 (★案文であり、当てて居らぬ★。挿す位置 = shebang L1 の直後):
```bash
# ── 戻し防止の門（案文・未適用）──────────────────────────────
# 此の版は 2026-09-07 の DB負荷止血より前の姿である（止血の門を持たぬ）。
# 名を pre-push へ戻すと push 毎に source_code_cache の同期と stale 検査が走る。
# 止血前の姿は git に残る: git show 4b1f7d293:scripts/git-hooks/pre-push
if [ "$(basename "$0")" = "pre-push" ]; then
  echo "[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。"
  echo "[pre-push]   正規の hook を戻すには: bash scripts/git-hooks/install.sh"
  exit 1
fi
```
- 効く範囲: install.sh は退避 file を触らぬ (§3) ∴ ★門は消えぬ★。exit 1 ゆゑ push が止まり ★人が気付く★ (黙つて通さぬ)。
  戻し方 (`install.sh`) を同じ画面で示す ∴ 気付いた人が次に打つ手を探さずに済む。
- 欠け: ★`$0` が hook 実行時に何に成るかを 当席は確かめて居らぬ★ (§5)。`basename` に依る ∴ git の呼び方次第で門が空振りし得る。
  また退避 file の中身が 1 hunk 増える ∴ blob `6d4039bb1671` との逐語同一が崩れる (§2 の「git が担ふ」証跡は git 側に残る)。

### 案文 D ―― 退避 file を消す
- 効く範囲: 危険の源そのものが無くなる。失ふ物 = ★0★ (§2 で blob `6d4039bb1671` と逐語同一を byte で實測)。
- 欠け: 第一条「出所不明の物は消すな」に触れる。出所は §2 で判つたが、★消す判は当席の外★ (作者=委員長・台帳に載る file)。
  且つ本弾の縛り「動かすな」に真向から当たる ∴ 案文としてのみ記す。

### 案文 E ―― `.git/hooks/` の外 (例: `docs/` 配下や別 dir) へ移す
- 効く範囲: `.git/hooks/` に居らぬ ∴ 名を変へるだけでは走らぬ。
- 欠け: 「動かすな」の縛りに当たる。且つ ★手間が一つ増えるだけで、戻す気の人は止められぬ★。

## §5 ★確かめて居らぬ事★ (六条)

1. ★`$0` の値★: git が pre-push hook を呼ぶ時 `$0` が `.git/hooks/pre-push` に成るか (∴ `basename` が `pre-push` に成るか) を
   ★走らせて確かめて居らぬ★。案文 C の効き目は此処に懸かる。確かめるには ★隔離した空 repo で hook を 1 本走らせる★ 要が在る
   (DB 0・製品 0・共有樹 0)。★走らせる前に家老へ申告する★ ―― 本紙は申告であり、未だ走らせて居らぬ。
2. ★他 PC (main/second/mac) の hook の姿★: 手が届かぬ ∴ 測つて居らぬ (前紙 o78 §5 境界と同じ)。§6 参照。
3. ★install.sh の `sed -i` が現に作業樹を汚すか★: 走らせて居らぬ (§3 末尾)。
4. ★退避 file を作つたのが誰の手か★: commit の author は委員長だが、`.git/hooks/` は追跡簿の外ゆゑ
   ★disk 上の退避 file を置いた手そのものは git に残らぬ★。mtime `Sep 7 08:01:55` と commit `08:03:35` の 100 秒差は
   「file を先に置き、其の後 repo へ commit した」と読めるが ★確かめて居らぬ★。

## §6 案文の外に在る、より大きい口 (令の外・報せるのみ)

`docs/rules/fleet-composition-manifest.yaml` の `db_load_shed_20260907_stage2.gap` に ★逐語★:
「main/second/mac の hook・polling は未是正(監督lot 283529/283584・edge_logs 実測で 5s watcher と停止役職 専務/常務向け watcher が主因)」

∴ 台帳が自ら「third 以外の hook は止血前の儘」と記して居る。是は ★退避 file 1 本より口が広い★ (現用名で走る hook が他 PC に在り得る)。
當席は其れらへ手が届かぬ ∴ ★測つて居らぬ★。本紙は「在ると台帳が書いて居る」事を写すに留める。

## §7 案文を当てた後、何を測れば効いたと言へるか

| 案文 | 測る物 | 期待する値 |
|---|---|---|
| C | 隔離 repo で退避 file を `pre-push` の名で置き push を試みる | 器が `BLOCKED: 之は止血前の退避版` を出し rc≠0 |
| C | 同じ隔離 repo で名を `pre-push.bak-…` の儘 push | 門は鳴らず (`$0` が違ふ) |
| C | `bash scripts/git-hooks/install.sh` の後の `.git/hooks/` | 退避 file が ★在る★ (install が触らぬ事の裏取り) かつ `pre-push` の sha16 = `e4a47593600691e3` |
| D | `.git/hooks/` の一覧 | 退避 file が ★無い★ / `git show 4b1f7d293:…` は取れる儘 |

## §8 境界と開示

讀取のみ。★hook file の書換 0・名を戻さず 0・移さず 0・消さず 0★。走らせた器 = 0 本 (本弾は讀取と `diff`・`git log`・`cat-file` のみ)。
DB 讀 0・書 0・SQL 0 本・本物 CI 走行 0・push 0・fetch/pull/prune 0。共有樹 `.git` へ ★書込動詞 0★ (`log`/`rev-parse`/`cat-file`/`config --get` は讀取)。
D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触。Commander の箱 0 打。
★己の落ち★: 前紙 o78 §5 危険① は「名を戻すと走る」とだけ書き、★install.sh が退避 file を触らぬ事・止血が自ら回復する事★ を測つて居なんだ。
本紙 §3 で補ふ。前紙は書き換へて居らぬ。

## §9 席の作法 九条目に従ふ ―― 渡し物を lot の終りに當て直した (家老 `msg_20260908_070808_420249e5`)

九条目 逐語:「★申し送り・渡し物は lot の終りに もう一度 當て直せ★」「★古びて居らぬ物も『當て直した・不変』と書け★」。

當て直した物 = order86 の渡し物 (証拠束 `docs/evidence/a2-sync-shallow-guard-20260908/`・樹 `wt-guard-evidence`)。

| 當てた点 | 今 (07:2x 實測) | 束の紙 (INDEX.md) の記載 | 判 |
|---|---|---|---|
| `INDEX.md` | `3cdee4e86b4c918f` | ― (己) | ★不変★ |
| `argv.txt` | `e7017ff341c8a50b` | ― | ★不変★ |
| `o84_shallow_guard_impl_v1.md` | `3a2ffff409f866ed` | `3a2ffff409f866ed` | ★一致・不変★ |
| `pytest-run1-tree.log` | `b8bb818ac8997a1b` | `b8bb818ac8997a1b` | ★一致・不変★ |
| `pytest-run2-mutation.log` | `23afb7b2c15ac7a2` | `23afb7b2c15ac7a2` | ★一致・不変★ |
| 樹の汚れ | `git status --porcelain` = ★0 行★ | ― | ★不変★ |
| 追補 (走 1 で録り直した節) が INDEX に載るか | §4 L44-51 に在り (`### ★其の後 走 1 本で録り直した★`) | ― | ★載る★ |
| 束の残る欠け (run2 の raw に argv 無し) が INDEX に書かれて居るか | §4 L50-51 に在り | ― | ★書かれて居る★ |

- ∴ ★古びて居らぬ = 當て直したが 不変★。order87 で新たに掴んだ事 (hook の話) は shallow guard の証跡と ★別の元素★ ゆゑ束へは混ぜて居らぬ。
- ★己の走査規の落ち★: 當て直しに使つた python の f-string で改行の escape を誤り `lines=0` と刷つた。
  ★行数は数として使つて居らぬ★ (sha16 のみで當てた)。誤つた出力は消さず此処に開示する。
