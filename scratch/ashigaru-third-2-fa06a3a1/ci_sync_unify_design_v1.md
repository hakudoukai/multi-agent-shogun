# CI sync を v3 の器へ一本化する案 (讀取と案文・製品 file へ 0 字)

as_of 2026-09-08T04:41+09:00 / 席 ashigaru-third-2 / 令 order73 (総監督 裁 288068・owner=当席)
前紙 (再刷して同値を確かめた): order72 `119702752981c5e8` 59行 / order71 `4f3e0a728903d109` 62行 —— 不触
底本: v3 `scripts/sync_source_cache.py` 709行 / CI `.github/workflows/sync-source-cache.yml` 200行 / hook `scripts/git-hooks/pre-push` 70行
数の断り: 1 = 特記なき限り ★file 1 本★ か ★行 1 行★。path の数は ★git の追跡簿 (ls-files) の 1 行★ を 1 と数へた。
規 (数へた器): `scratch/ashigaru-third-2-fa06a3a1/o73_eye_count.py` 48行 sha16 `971bc646c306ce07` (讀取のみ・DB へ触れぬ)

## §1 一本化の差分案 (触れる file と行・逐語)

触れる file = ★2 本★。振舞ひを変へる行は ★workflow 側のみ★。

| # | file | 行 | 現 | 案 |
|---|---|---|---|---|
| 1 | .github/workflows/sync-source-cache.yml | L34-35 `fetch-depth: 2` | 浅い clone | ★案では触れぬ★ (理由 §3-①: 深くしても prev_commit は label 形ゆゑ解けぬ) |
| 2 | 同 | L42-43 `run: pip install requests` | requests のみ | `pip install httpx python-dotenv` (v3 の import は L20-21 `httpx` `dotenv`・requests 不使用) |
| 3 | 同 | L46-48 env | `SUPABASE_SERVICE_ROLE_KEY` | ★`SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}` へ名を移す★ (v3 L45 が讀む名。秘の中身は動かさぬ) |
| 4 | 同 | L49-199 `run: \|` heredoc python ★151 行★ | CI 独自の POST/DELETE | ★`python3 scripts/sync_source_cache.py --changed-only --no-stale` の 1 行★ |
| 5 | scripts/sync_source_cache.py | INCLUDE/EXCLUDE の近傍 | 註が薄い | ★註のみ追記 (§2 の文案)・振舞ひを変へる行 0★ |

和: 削る ★151 行★ (heredoc python)・置く ★1〜8 行★ (見込み)・註 ★数行★。★独自 POST は消え upsert は v3 L200-222 の 1 箇所に集まる (`on_conflict=file_path` 明示・L121/L209)★。

## §2 目と EXCLUDE の差を v3 側に書く理由の文案 (各一行)

★四条②の断り★: 家老下命の「3/2」は ★数の差★ である。記号の差は別で、次の三つは数へ方が違ふ。
- INCLUDE: v3 一意 ★31★ / CI ★28★ —— 数の差 3・★記号の差も 3★ (CI−v3 = 0 本 ∴ CI ⊂ v3)
- EXCLUDE: v3 ★5★ / CI ★7★ —— 数の差 2 なれど ★記号の差は 4★ (CI にのみ 3・v3 にのみ 1)
- EXCLUDE_DIRS: v3 ★8★ / CI ★6★ —— 数の差 2・★記号の差 4★ (v3 にのみ 3・CI にのみ 1)

文案 (v3 の註へ置く・逐語案):
1. `.cache/audit_redo/**/*.md` `.cache/audit_redo/**/*.txt` `docs/audits/**/*.log` の 3 本 —— 「副医院長 453ca4a4 命令 (理事長直接命令) で監査永続化の対象を広げた分。CI の目は其の令より前の形ゆゑ 3 本を欠く。v3 を正とする。」
2. v3 が `**/*.test.*` `**/*.spec.*` `**/test_*` を ★除かぬ★ 事 —— 「試験 code も監査で読む写しに要る。cache は『動く物』ではなく『読める写し』ゆゑ試験を落とさぬ。」
3. v3 が `**/.git/**` を ★除く★ 事 —— 「入口が追跡簿 (collect_files L157) ゆゑ本来入らぬが、glob 経路へ戻つた時の帯として残す (二重の止め)。」
4. EXCLUDE_DIRS の `.venv` `.venv-linux` `venv` `.codex_audit` —— 「2026-07-19 の 1 走行で 15,288 行が `backend/**/*.py` × 作業樹 glob で入つた事故の帯 (v3 L96-101 に既述)。」
5. CI にのみ在る `.pytest_cache` —— 「追跡簿基準では入らぬが帯として v3 へ足しても害が無い ∴ 揃へるなら v3 側へ 1 語足す (本弾では足さぬ・裁を仰ぐ)。」

★目を v3 へ揃へた時の増分 (見込み)★: 追跡簿 13,990 本のうち v3 の目に当たるは ★3,531 本★、
うち ★CI にのみ在る 3 除外で落ちて居た path = 637 本★ (frontend 333・backend 242・scripts 49・tests 12・supabase 1)。
∴ ★一本化で新たに書かれ得る path は 637 本 (見込み)★。
★断り★: 此の 3,531 は当席が ★fnmatch★ で数へた数で、v3 本体は L377 `_glob_pattern_to_regex` の別意味で当てる (order50 では 4,185 本)。∴ 637 も ★見込みの数★ であり、実数は走らせねば測れぬ。

## §3 危険 (何が壊れ得るか)

| # | 危険 | 根 (逐語の在処) | 重さ |
|---|---|---|---|
| ① | ★表の大量 DELETE★: CI は shallow ゆゑ `commit_exists` 偽 → `STALE_FALLBACK_FULL_SCAN` → `get_cached_paths()` 全表 → runner の作業樹に無い INCLUDE path を悉く `delete_stale` | v3 L648-661 / L476-495 | ★最重★ (order50 の枝のみ path ★1,442 本 (見込み)★ が消え得る) |
| ①' | 深くしても消えぬ | DB の最新 commit_hash は ★label 形★ (order72 §3: `live_20260608_f9139ee1` 等 5 種) ∴ `git cat-file -e` で解けず全表走査へ落ちる | ★最重★ |
| ② | DB 負荷が CI へ移る | hook L55-58 が「全表 LIMIT/OFFSET 走査で Micro が crash」と書いて hook を既定 skip にした当の負荷 | 重 |
| ③ | 秘の名の食ひ違ひ | v3 L45 は `SUPABASE_SERVICE_KEY`・CI L48 は `SUPABASE_SERVICE_ROLE_KEY` ∴ 移さねば v3 L527-530 で exit 1 | 中 (赤で気付く) |
| ④ | 依存不足 | v3 は `httpx`・`dotenv` を import・CI は `requests` のみ入れる | 中 (赤で気付く) |
| ⑤ | 増分 637 本 (見込み) が新たに表へ | §2 | 中 |
| ⑥ | `tmp/sync_file_list.txt` `tmp/sync_last_commit.txt` を書く | v3 L682-687 / L315-320 | 軽 (runner は揮発・追跡外) |
| ⑦ | 窓 `origin/main...HEAD` が shallow で失敗し `HEAD~1..HEAD` へ落つ | v3 L536-545 | 軽 (現 CI と同窓) |

★∴ ①①' を切らぬ限り 一本化は打てぬ★ —— 消えた行は revert では戻らぬ (§4)。

## §4 戻し方 と 三案

戻し方: ⑴ workflow は file 1 本ゆゑ ★当該 commit を revert すれば元の heredoc へ戻る★。
⑵ ★DELETE された行は revert で戻らぬ★ ∴ 走らせる前に ★表の file_path 一覧の写しを採る★ (打手は総監督殿・当席は DB へ触れぬ)。
⑶ 枝は `a2/sync-cache-unify-ci-20260908` の 1 refspec のみ・force 無し・main 直 push 無し。

| 案 | 形 | 危険① | v3 の書換 |
|---|---|---|---|
| A | workflow から v3 を呼ぶだけ | ★残る (最重)★ | 無し |
| B | v3 へ `--no-stale` を足し (既定は現行の儘)・CI は `--changed-only --no-stale` | ★切れる★ | ★有り (足す・既定不変)★ |
| C | `fetch-depth: 0` にして git 差分 stale へ | ★残る (①' ゆゑ label は解けぬ)★ | 無し |

★当席の見立て (見込み)★: ★案 B★。理 = ①①' を切る道が他に無く、既定を変へぬゆゑ hook と手打ちの振舞ひは動かぬ。
但し ★v3 へ 1 語足す事は「workflow の書換」より広い★ ∴ 家老殿・総監督殿の裁を仰ぐ (本紙では足さぬ)。

## §5 三値
| 問 | 三値 |
|---|---|
| CI の独自 POST を v3 呼出へ畳めるか | ★現に在る★ (v3 は CLI で `--changed-only` を持つ・hook L66 が同形で呼ぶ先例) |
| 一本化のみで危険①が消えるか | ★現に無い★ (v3 の stale は main() で常に走る・止める旗が無い) |
| 増分 637 本・削除候補 1,442 本の実数 | ★測定不能★ (走らせるか DB を讀まねば測れぬ・当席は何れも打たぬ) |

## §6 境界
DB 讀 0・書 0 / SQL 0 本 / 走行 0 / fetch・pull・clone・push・prune 0 / 製品 file と workflow へ ★0 字★ (本紙は案文のみ) / shell `>` `>>` `tee` 0 (書込は python `open()`・捕獲は subprocess) / secret の値 0 (名のみ) / 患者本文 0 / 他席の inbox へ書込 0 / Commander の箱 0 打。
