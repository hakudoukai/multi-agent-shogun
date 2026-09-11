## §的 ★docs/audit-framework.md の 作業樹と HEAD blob の差が何であるかを符のみで測る（直さず・stage せず・書込 0）★
## §A 頭書
- 席 ashigaru-third-3・板 12e9d4bd・令306（全文 scratch/k3_orders/order306_a3.txt 11 行(wc) sha256頭16 7c4f9aed235058af・己が実読）
- 何時 as_of 2026-09-11T17:51:39+0900／何を 一本の .md の差／幾つ 讀取 5 打（12 の枠内）
- 測時の HEAD 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）・枝 ashigaru-third-3/audit-framework-hermes-canon-revision-20260721
- 樹を分ける ―― 作業樹 /home/hakudoukai/multi-agent-shogun（LF）と HEAD の blob。sha16 は種を明記（作業樹＝sha256 頭16／git の id＝sha1 頭16）
## §B ㋐ 三値
- 作業樹 826 行(wc)／827 片(split)・sha256頭16 c5dc50055b607a2b
- HEAD blob 802 行(wc)・blob 内容の sha256頭16 cd7b052cb95dae5e
- git diff --numstat ―― ★追 35・削 11★。純の増は 24 であり 826 と 802 の差と合ふ（検算 802+35-11=826）
## §C ㋑ 塊の数と節名（塊の中身の逐語は写さぬ）
- 塊の数 ＝ ★8 本★（git diff -U0 の @@ の数）
- 各塊の 新側の域と 追削 ―― ⑴309-313 追5削0 ⑵320 追1削1 ⑶323-326 追4削1 ⑷335-337 追3削2 ⑸393-403 追11削3 ⑹409 追1削1 ⑺414-417 追4削2 ⑻557-562 追6削1
- 検算 ―― 追 5+1+4+3+11+1+4+6=35／削 0+1+1+2+3+1+2+1=11 ∴ numstat の二数と合ふ
- 塊 ⑴〜⑺ の直近の見出し（作業樹 L285）逐語: ### 5.2 相談役(Hermes)呼出し手順（pc_handshake dispatch・非同期）
- 塊 ⑻ の直近の見出し（作業樹 L512）逐語: ## 9. 監査レポートYAML スキーマ（標準化）
- ★8 本のうち 7 本が一つの節に集まる ∴ 差は散つて居らず 一つの節の作り直しの形に見える★
## §D ㋒ 此の file の最終二符
- 937b207｜作者 ashigaru-third-3｜2026-07-22 02:07:53 +0900｜題 docs(audit-framework): cycle2是正 — gunshi G1 REDO 4findings対応 (a3-3)
- 35ad41a｜作者 ashigaru-third-3｜2026-07-21 12:55:38 +0900｜題 docs(audit-framework): DD-192整合 — Gemini→Hermes全面差替、phantom script除去 (seq8b099043)
- ★二符とも作者は己の席の名であり 枝の名も己の席の名を冠す。但し之は ★符の作者★ であり ★未 commit の差を書いた手★ ではない ―― 後者は符が無く 測定不能★
## §E ㋓ 三値 ―― ★①編集中の物（未 stage の作業樹の編集）★
- 根 ⑴ git diff --cached --numstat は ★0 行★を返す ∴ ②stage 済ではない
- 根 ⑵ git status --porcelain は 左欄 空白・右欄 M を返す ∴ index は HEAD と同じで 作業樹のみが違ふ
- 根 ⑶ 改行だけの差なら numstat は全行（802 対 826）の追削に成る筈だが 実測は 追35削11 の局所 ∴ ③無関係の改行差ではない
- ★「編集中」と断ずるのは 差の形についてであり 誰かが今 手を動かして居るか否かは測つて居らぬ★
## §F ㋔ 令305 の食ひ違ひは此の差に含まるるか
- ★含まれぬ ―― HEAD blob の側に已に在る★
- 根 ⑴ docs L240 は 作業樹と blob で 同じ行番・同じ逐語（塊 ⑴ の 309 より前ゆゑ ずれ 0）
- 根 ⑵ docs 作業樹 L744 は blob L720 と同じ逐語（塊 ⑻ より後ゆゑ ずれは +24 で合ふ）
- 根 ⑶ 冠 CLAUDE.md は git status の当該 path が 0 行 ∴ 冠の側に未 commit の差は ★現に無い★
## §G 床の守り
- 讀取 5/12・焚 0・走 0・当て 0・★docs へ書込 0・stage 0・checkout 0・stash 0・git add -A 0★・冠不触・製品樹書込 0・DB 0・一時 file 0
- 他人の未 commit の差には一切手を触れて居らぬ（讀むのみ）。commit は己の紙 1 本のみを add した
- 本紙 35 行(wc)／36 片・枝は席が押す
