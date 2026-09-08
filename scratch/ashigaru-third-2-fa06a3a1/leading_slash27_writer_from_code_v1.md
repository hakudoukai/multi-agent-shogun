# 先頭 `/` の 27 本の書き手を code 側から絞る (讀取のみ・DB 0・fetch 0・走行 0)

as_of 2026-09-08 04:27 JST / 席 ashigaru-third-2 / 令 order72 (弾A・家老の順の裁で B の次)
★床 (着手時 再測 差0)★: `4f3e0a728903d109` ci_hash2_eye_diff_and_on_conflict_v1.md 62行 / 前紙 `9268704f85a4f05a` plan123_ruling_and_window_correction_v1.md 64行 ―― ★何れも不触★
底本: v3 = blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9` / CI #2 = .github/workflows/sync-source-cache.yml / SP = scripts/sync_source_cache_secondpc.py / 静的 = docs/audits/source_code_cache_sync/batch_001〜011.sql / 27 本の形 = 局所写し o61_candidates_export.csv (讀取のみ)
★四条②★ 数には何の数かを添へる。★四条③★ 単位の違ふ数を足し引きせぬ (path 本数・行・値の種類・pattern 本数は別物)。★四条④★ 見込みは見込みと記す。
★path の値は写さぬ★ (先頭 3〜4 節の形のみ引く)。

## §1 27 本の形 (単位=path 本数・和 27)
| 先頭 3〜4 節 | path 本数 | 節の深さ |
|---|---|---|
| `/mnt/c/Users/...` | ★12★ | 10 |
| `/home/hakudoukai/.config/...` | ★5★ | 5〜6 |
| `/home/hakudoukai/multi-agent-shogun/...` | ★5★ | 4〜6 |
| `/home/hakudoukai/shogun_dispatcher/...` | ★3★ | 4〜6 |
| `/home/hakudoukai/scripts/...` | ★2★ | 4 |
- 和 = ★27 本★ (export 全 1,649 本の内)。★悉く DentalBI repo の外★ であり、2 つの樹 (WSL の home ・ Windows の Users) に跨る。

## §2 同表へ書く 4 経路の path 生成部 (逐語) と 三値 (各経路・和 4)
| 経路 | path 生成部の逐語 | 先頭 `/` を生み得るか |
|---|---|---|
| ① v3 本体 | L157 `def collect_files(repo_root: Path)` ―― 註に「★入口は git の追跡簿★ (作業樹 glob ではない)」/ L167 `for rel in list_tracked_files(repo_root):` / L604 `"file_path": file_path` | ★現に無い★ (git の追跡簿は repo 相対しか出さぬ) |
| ② CI #2 | L119 `repo = Path(".")` / L114 `rel = str(path.relative_to(root)).replace("\\", "/")` / L163 `"file_path": fp` | ★現に無い★ (`relative_to` を通す) |
| ③ SP (second PC SQL) | L23 `REPO_ROOT = Path(__file__).resolve().parent.parent` / L129〜130 `for rel in files:` `full = REPO_ROOT / rel` / L160 `"file_path": rel` | ★現に無い★ (書くは rel の側) |
| ④ 静的 batch SQL | ③ の産 (L189 近傍 `batch_path.open("w")` で `INSERT INTO source_code_cache (file_path, …)`) ・11 本を當たり先頭 `/` の値 ★0 本★ | ★現に無い★ (已測と差 0) |
- ∴ ★4 経路の悉くが「現に無い」★。已測 (静的 SQL 11 本 0 本・SP は rel 相対) と ★差 0★。
- 併せて ①③ は repo_root を `Path(__file__).parent.parent` から採るゆゑ、走らせる cwd が何処であれ ★repo の外の path は母集合に入らぬ★。

## §3 第二の指紋 ―― commit_hash の形 (単位を分けて数へる)
- 27 本が持つ commit_hash は ★値の種類 5★ (単位=値の種類):
  `live_20260608_f9139ee1` ★13 行★ / `windows_native_2026-05-26_t61` ★10 行★ / `windows_native_2026-05-26_t62_daishogun_pkg` ★2 行★ / `cycle4_a4a68a78_20260608` ★1 行★ / `ca47e70d` ★1 行★ (単位=行・和 27)
- 4 経路が commit_hash を作る所は悉く同じ形 (逐語): v3 L185 `["git", "rev-parse", "--short", "HEAD"]` (L188 `… else "unknown"`) / CI L121 同 / SP L97 同。∴ ★生まれる値は 短 sha か "unknown" の 2 形★ であり、`live_…` `windows_native_…` の如き ★label 形は生まぬ★。
- DentalBI の object store に commit として在るか (讀取 `cat-file -e <値>^{commit}`): ★在る 1 種 / 無い 4 種★ (在るは `ca47e70d` の 1 種・1 行のみ)。
- ∴ ★書き手は 4 経路の外の器★ ―― 自ら label を付ける手書きの器である。

## §4 刻 (単位=行)
- updated_at: 2026-05-26 が ★13 行★ (12:43 に 1・14:31 に 10・14:45 に 2) / 2026-06-08 が ★14 行★ (16:49 に 13・17:13 に 1)。和 27 行。
- created_at も同じ 2 日に落ちる (05-26 が 16 行・06-08 が 11 行) ―― 行ごとの差は本紙では數へて居らぬ。
- ∴ ★2 波★。何れも ㋒ の DELETE (2026-09-07 19:01:14) の 3 ヶ月以上前であり、㋒ で消えた 1,649 本の一部として落ちた。

## §5 三値
| 事 | 三値 |
|---|---|
| 4 経路の何れかが先頭 `/` を生む事 | ★現に無い★ (§2 の逐語 4 本) |
| 書き手が 4 経路の外の器である事 | ★現に在る★ (§3・commit_hash の形が 4 経路の生む 2 形と違ふ) |
| 其の器の名 | ★測定不能★ (表に書き手の列 0・唯一の路は order70 §4 の log 突合) |
| `ca47e70d` の 1 行が 4 経路の産である事 | ★現に無い★ (値の形は合ふが path が repo の外ゆゑ §2 の 4 経路では作れぬ) |
| 27 本が 2 波で入つた事 | ★現に在る★ (§4) |

## §6 前紙との突合
- order65 紙 (`a96fa3b10676202a`「5 器いづれも書き得ぬ」) と ★同じ結び★ へ、本紙は ★4 経路の path 生成部の逐語★ から至つた。
- 加へて本紙は ★commit_hash の形★ といふ第二の指紋を得た ―― order71 §3 の「目の差は書き手の指紋になり得る」と同じ器で、そこでは EXCLUDE の目、此処では commit_hash の形が指紋である。
- 併記: 「4 経路では書けぬ」は ★書き手を名指した事にはならぬ★ (§5)。名指しには log 突合が要り、其は当席の打つ物ではない。

## §境界
DB 讀 0・書 0・SQL 実行 0・fetch/pull/clone/push/prune 0・共有 `.git` へ書込動詞 0・走行 0・本番 code 書込 0・secret 0・患者本文 0。
打つた git = `cat-file -p` `cat-file -e` の 2 種 (讀取)。shell の `>` `>>` `tee` = ★0★ (python の subprocess で捕へた)。
csv は局所写し `/home/hakudoukai/o61_delete_20260907/o61_candidates_export.csv` を streaming で讀んだのみ (content 値は捨て file_path/commit_hash/刻のみ見た)。backup 樹は開いて居らぬ。
前紙 2 本は書き換へず。見込みと記した ETA 25 分に対し 実所要は本紙の刻の通り。
