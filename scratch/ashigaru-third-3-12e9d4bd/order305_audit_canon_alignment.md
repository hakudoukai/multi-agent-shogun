## §的 ★冠 CLAUDE.md と詳細 docs/audit-framework.md の監査の定めが揃ふかを符のみで測る（直さず・書込 0）★
## §A 頭書
- 席 ashigaru-third-3・板 12e9d4bd・令305（全文 scratch/k3_orders/order305_a3.txt 11 行(wc) sha256頭16 a85db2e79513d9c1・己が実読）
- 何時 as_of 2026-09-11T17:43:12+0900／何を 二本の .md／幾つ 讀取 4 打（12 の枠内）
- 測時の HEAD 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）・樹を二つに分ける ―― 作業樹 /home/hakudoukai/multi-agent-shogun（LF）と HEAD の blob
- 本紙は前紙を書き換へず新たに鋳た。sha16 は種を明記する（作業樹＝sha256 頭16／git の id＝sha1 頭16）
## §B ㋐ 全行数と sha（樹を欄で分ける）
- CLAUDE.md ―― 作業樹 621 行(wc)／622 片(split)・52842 B・sha256頭16 142a8eea82866214
- CLAUDE.md ―― HEAD の blob 621 行(wc)・blob の sha1 頭16 5792ab40bca162e9・git status は当該 path を 0 行で返す ∴ 作業樹と blob は同じ
- docs/audit-framework.md ―― 作業樹 826 行(wc)／827 片(split)・41950 B・sha256頭16 c5dc50055b607a2b
- docs/audit-framework.md ―― HEAD の blob 802 行(wc)・blob 内容の sha256頭16 cd7b052cb95dae5e・blob の sha1 頭16 ab15f783775042fb
- ★同じ path で 作業樹 826 対 blob 802 ＝ 24 行の差。git status は当該 path を M と出す ∴ 未だ符に入つて居らぬ直しが作業樹に在る★
- 家老の先測「docs は 826 行・c5dc50055b607a2b」は ★作業樹の側と一致★する（blob の側とは一致せぬ）
## §C ㋑ 「Gemini」の当たり（大小の軸を同じ行に名指す）
- 大小を区別する当たり（grep 既定）―― CLAUDE.md 1 件 rc=0（行 463）／docs 作業樹 4 件 rc=0（行 240 245 716 744）
- 大小を無視する当たり（grep -i）―― CLAUDE.md 2 件（行 463 465）／docs 作業樹 10 件（行 240 245 304 602 716 744 745 747 750 813）
- HEAD の blob の側 ―― CLAUDE.md 大小無視 2 件／docs 大小無視 10 件（作業樹と同数）
- ★家老の先測「冠 2・docs 10」は ★大小を無視した軸★ の数と一致する。大小を区別すれば 冠 1・docs 4 であり別の数である★
- 差の出所 ―― 冠の 465 行と docs の 304/602/745/747/750/813 行は 小文字の script 名（audit の器）であり 大文字の固有名ではない
## §D ㋒ 外した／置き換へた旨の記述
- ★現に在る★。docs 作業樹に三箇所。逐語（3 行以内）:
- > 240:Geminiは全面decommission済（DD-192）。以降の第三者監査二本目は相談役(Hermes)が担う。
- > 744:★open blocker（finding 002・decommission未強制）★: 本ドキュメントは Gemini を三者監査の
- > 747:"scripts/audit_codex.sh" / "scripts/audit_gemini.sh" 経由」と両者を並記している。
## §E ㋓ 三値 ―― ★食ひ違ふ★
- 根 ⑴ 冠 L463 は三者の並びに Gemini を現役として置く。逐語:
- > 463:原則: 第三者監査 (軍師/Codex/Gemini) 三者全員 PASS まで完了不可。自作自演禁止、軽微修正でも省略不可。
- 根 ⑵ 冠 L465 は標準の呼出しとして audit の器 二本を並記し、其の一方が gemini の器である
- 根 ⑶ docs L240 は decommission 済・二本目は相談役と書く ∴ 同じ事柄に二つの定めが同時に立つ
- 根 ⑷ ★docs 自身が L744-747 で「冠が両者を並記して居る」事を open blocker として名指して居る★ ―― 己の測りと docs の自己申告は同じ所を指す
- ★令に従ひ 一字も直して居らぬ。冠にも docs にも書込 0★
## §F ㋔ 対照
- 陽性 ―― 語「監査」 CLAUDE.md 11 件 rc=0／docs 作業樹 64 件 rc=0 ∴ 器は盲ひて居らぬ
- 陰性 ―― 語 ZZNoSuchNameZZ CLAUDE.md 0 件 rc=1／docs 作業樹 0 件 rc=1
## §G 床の守り ―― 讀取 4/12・焚 0・走 0・当て 0・冠と docs へ書込 0・製品樹書込 0・DB 0・一時 file 0・本紙 35 行(wc)／36 片・枝は席が押す
