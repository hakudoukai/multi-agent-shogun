# 遠隔にのみ在る ref (C4) の測れる部分 ―― ls-remote 対 局所・fetch 0 (order59)
as_of 2026-09-07T18:33:45+09:00 / 席=ashigaru-third-2 / 對象 repo=/mnt/c/DentalBI / remote=origin (github.com/hakudoukai/hakudokai-dev.git)
前紙: non_ascii_path10_encoding_causality_v1.md sha16=725fa322a2478ae2 (52行)
前紙: gap41_5627_vs_5668_source_candidates_v1.md sha16=e662da0c4d34468a (53行) §1 C4・§5
※ 兩紙は開いて讀んだのみ・書き換へて居らぬ。

## §0 用ゐた動詞 (悉く讀取・timeout 付き)
`git remote -v` / `git ls-remote origin` / `git for-each-ref` / `git ls-tree -r --name-only -z` / `git cat-file -e <sha>^{commit}` / `git cat-file -p <blob>`。
**fetch 0・pull 0・clone 0・push 0・write 動詞 0・DB 0・script 走行 0**。ls-remote は ref 一覧を讀むのみで object を持つて來ぬ。

## §1 三分 (件數・ref 名は寫して可の令に依る)
遠隔 ref 總數 (peeled `^{}` を除く) = **277** ―― 内訳 HEAD 1 / heads **150** / pull **123** / tags **3**。
局所側の對應 = `refs/remotes/origin/*` 151 (HEAD 込) → 枝 **150** / `refs/pull/*` **3** / `refs/tags/*` **8**。

| 種 | 兩方に在る | 遠隔のみ | 局所のみ | 和 | 兩方で tip sha が異なる |
|---|---|---|---|---|---|
| 枝 (heads ↔ remotes/origin) | 148 | **2** | 2 | 152 | **2** |
| pull | 3 | **120** | 0 | 123 | 0 |
| tags | 3 | **0** | 5 | 8 | 0 |
| **計** | 154 | **122** | 7 | **283** | 2 |

- 遠隔のみの枝 2 本 = `karo-main/7703301f-lot35b-casenashi-kakeiA-unevaluable-on-lot33c` / `karo-main/7703301f-lot39-r7-defense-wiring-on-lot36`。
- 局所のみの枝 2 本 = `pr-71-review` / `pr69` (遠隔で既に無い remote-tracking ref)。其の tree は已に合併に入つて居る。
- 局所のみの tag 5 本も已に合併に入つて居る。

## §2 遠隔のみ ref の tip が局所 object store に在るか (`git cat-file -e`)
| 群 | 本數 | 局所に **在る** | 局所に **無い** |
|---|---|---|---|
| 遠隔のみ pull | 120 | **107** | 13 |
| 遠隔のみ 枝 | 2 | 0 | **2** |
| 兩方に在るが tip 差 (遠隔側 tip) | 2 | 0 | **2** |
| **計** | 124 | **107** | **17** |

## §3 在る分を足すと 5,678 は動くか
- 局所 248 ref の合併 INCLUDE = **5,678** (order57 §2-1 と同數・本紙で測り直して一致)。
- 之に §2 の **107 本の tip の tree** を足して同じ filter を掛けた合併 INCLUDE = **5,678**。
- **差 = 0** ―― 107 本の tip は **新たな INCLUDE path を 1 本も持ち込まなかつた**。
- 實測の殘 5,668 との差は **+10 のまま動かぬ**。

## §4 測れぬ分 (fetch 無しには測れぬ)
- **17 本**の tip (遠隔のみ枝 2・tip 差 2・遠隔のみ pull 13) は局所 object store に無い ∴ 其の tree は **測定不能**。
- 之を測るには fetch が要る ―― **當席は打たぬ** (令の禁)。打つ判は總監督殿。
- 17 本が仮に新たな path を持つとすれば合併は **増える側**にのみ動く ∴ **+10 の過剩を減らす向きには働かぬ**。之は算術上の向きの話であり、17 本の中身を見た結果ではない。

## §5 SELECT 案文 (2 本・件數のみ・path 値 0・當席 0 打・打つは總監督殿)
- S59-1 (遠隔のみ枝の commit が表に居るか): `select count(*) as n, count(distinct commit_hash) as h from source_code_cache where commit_hash is not null;`
- S59-2 (+10 の側を當てる): `select count(*) from source_code_cache;` ―― §3 の 5,678 と引き算する為の現行値 (S57-1 と同文ゆゑ、打つのは何れか 1 度で足りる)。

## §6 境界
- §1 の遠隔側は **ls-remote が返した ref 名と sha のみ**。遠隔の tree も content も讀んで居らぬ。
- §3 の「差 0」は **今 局所に在る 107 本**に對する結果であり、17 本を含めた答ではない。
- 5,668 は order50 時點の實測であり、本紙でも測り直して居らぬ (DB 0 の床)。
- pull ref は既定では fetch されぬ ∴ 局所 3 本と遠隔 123 本の開きは **設定どほり**であり、異常として書いて居らぬ。
- 途中で用ゐた一時 file (`.o59_present.json`) は本紙提出前に消した。前紙 2 本は不觸。
