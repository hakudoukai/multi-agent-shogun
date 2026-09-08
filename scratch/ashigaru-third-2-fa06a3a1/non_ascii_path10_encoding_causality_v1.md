# 非 ASCII path 10 本 と 「+10」の因果 ―― git 表記 対 REST 符号化 (order58・讀取のみ)
as_of 2026-09-07T18:29:14+09:00 / 席=ashigaru-third-2 / 對象 repo=/mnt/c/DentalBI
前紙: gap41_5627_vs_5668_source_candidates_v1.md sha16=e662da0c4d34468a (53行) §2-5・§4
前紙: option_c_full_stale_scan_predicate_v1.md sha16=34f11cfac4d55b42 (58行) L486-492 の件
※ 兩紙は開いて讀んだのみ・書き換へて居らぬ。

## §1 git 側の表記 (件數のみ・path 値 0)
`git config --get` の現値: **core.quotepath = 未設定**(∴ git の既定 true) / **core.precomposeunicode = 未設定** / **core.autocrlf = input**。

| 動詞 | 件數 | 行頭が `"` | 生の非 ASCII を含む |
|---|---|---|---|
| `git ls-files` (行指向) | 13,975 | 1,014 | 0 |
| `git -c core.quotepath=false ls-files` | 13,975 | 0 | 1,014 |
| `git ls-files -z` | 13,975 | 0 | 1,014 |
| `git ls-tree -r --name-only HEAD` | 13,975 | 1,014 | 0 |
| `git ls-tree -r --name-only -z HEAD` | 13,975 | 0 | 1,014 |

- ∴ **quotepath 既定 true は「行指向出力」だけに掛かり、`-z` には掛からぬ**。escape の形は `"…\ooo…"` (八進) であり、1,014 行がそれに當たる。
- 1,014 は追跡簿全體の數。INCLUDE を通した後の非 ASCII は **10** (前紙 §2-5 と同數・本紙で測り直して一致)。
- 正規形: 10 本は悉く **NFC** と一致。NFD と一致するのは 9 本 ∴ **NFC/NFD で表記が分かれ得るのは 1 本のみ**。

## §2 v3 script (blob 0754d928…) が file_path を DB へ渡す三經路と符號化
- **入口**: L140-146 `git ls-files -z` (L142)。L138 の docstring 逐語「-z ゆゑ path は生 (非 ASCII の quote 無し)・區切は NUL」。∴ **§1 の escape は v3 に屆かぬ**。
- **關門**: L167-178 collect_files。**L169 `if not path.is_file(): continue`**・L173 EXCLUDE_DIRS・L175 matches_include_patterns・L177 should_exclude。
- **經路① INSERT/upsert**: L207-212。**L210 `content=json.dumps(rows, ensure_ascii=False)`** + L196 `Content-Type: application/json`。file_path は **body の JSON 內**ゆゑ URL 符號化を通らぬ。生 UTF-8 のまま。
- **經路② SELECT**: L459-463。**L461 params は `select`/`offset`/`limit` のみで file_path を渡さぬ** ∴ path は URL に載らぬ。返りは L465 `resp.json()` → L469 `all_paths.add(row["file_path"])` ∴ 生 UTF-8。
- **經路③ DELETE (v3)**: L488-491。**L490 params に `file_path: in.(…)` を渡す** ―― params 渡しゆゑ client が query 値を percent-encode する。**L487 は各 path を `"` で括る**・L486 の逐語は「パスにカンマが含まれることはないので安全」。
- **經路③' DELETE (CI #2 `.github/workflows/sync-source-cache.yml`)**: **L185-186 は URL を f-string で組み `?file_path=eq.` の後ろに path を直に挿す** ―― params ではない。v3 の L490 と作りが異なる。
- 併記 (CI #2 の INSERT): L169-174 は `json=payload` (L172) ∴ body 側・URL 符號化を通らぬ。

## §3 三值の結び
| 問 | 三值 | 根據行・數 |
|---|---|---|
| 同じ path が 2 通りの表記で **2 行に成る** | **現に無い**(讀取の範圍で) | 入口 L142 は `-z` の一本道・經路①②は body/返り json ゆゑ表記の分岐點が無い。NFD 差の在る 1 本も、v3 が NFD を作る箇所は無い |
| 10 本が **1 行も成らぬ** | **現に無い** | L169 の關門 `os.path.isfile` は 10 本すべて **真**(偽=0)。INCLUDE 全體 4,113 本でも偽=0 |
| **影響無し** | **現に在る** | 上二つの否定の歸結 |
| 表記の分岐が **DB 側に既に在るか** | **測定不能** | DB 0 の床。§4 が之を分かつ |

- ∴ **「非 ASCII 10 本」と「+10」の數の一致を支へる根據は、讀取で 1 つも出なかつた** ―― 偶然の側に倒れる。**否定し切つたのではない**(DB を讀めぬ ∴ 表側の實態は言へぬ)。
- 併記 (URL 分離子): 合併 INCLUDE 5,678 本のうち `&` `#` `+` `%` `?` `=` 空白 `"` `,` 逆斜線 を含む path は **悉く 0**。∴ 經路③' の直挿しが現に壞す path は今の集合に無い。
- 推しは置かぬ。

## §4 SELECT 案文 (2 本・件數のみ・path 値 0・當席 0 打・打つは總監督殿)
- S58-1 (表記の分岐が在るか): `select count(*) as non_ascii, count(distinct normalize(file_path, NFC)) as nfc_distinct from source_code_cache where file_path ~ '[^\x20-\x7e]';`
- S58-2 (escape 形の混入が在るか): `select count(*) from source_code_cache where file_path like '"%' or file_path like '%!%' escape '!';`

## §5 境界
- §1 の 1,014・13,975 は **現 HEAD の追跡簿**の數であり、合併 248 ref の數ではない。
- §3 の `os.path.isfile` は **10 本と INCLUDE 4,113 本に對してのみ** stat した (作業樹の walk はして居らぬ・内容は讀んで居らぬ)。
- 經路①②③ は **blob の行を讀んだだけ**であり、走らせて返りを見て居らぬ (走行 0)。httpx/requests が實際にどう符號化するかは版に依る ∴ **當席は符號の知識として書いた**。
- 經路③' の CI #2 が現に走つて居るか否かは本紙では測つて居らぬ。
- 前紙 2 本の sha16 は着手時に測り直し、e662da0c4d34468a(53行)・34f11cfac4d55b42(58行) で一致した。
