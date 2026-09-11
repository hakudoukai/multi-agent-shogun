## §的 ★当 repo の作業樹に在る未 commit の差の全体像を符のみで測る（一字も直さず・stage も checkout も stash も clean も 0）★
## §A 頭書
- 席 ashigaru-third-3・板 12e9d4bd・令307（全文 scratch/k3_orders/order307_a3.txt 12 行(wc) sha256頭16 b0182a1cf326759c・己が実読）
- 何時 as_of 2026-09-11T17:57:54+0900／何を 当 repo の作業樹全体／幾つ 讀取 5 打（12 の枠内）
- 測時の HEAD 1ad4edfbadc69191183a42113e9979c3f91b7dbf（不動）・樹 /home/hakudoukai/multi-agent-shogun（作業樹・LF）
- 母の定め ―― 「差」とは git status --porcelain が返す一行を一つと数へた物。file 名は㋓の代表 5 本を除き列挙せぬ
## §B ㋐ porcelain の行数と符の内訳
- 全 ★170 行★
- ?? 未追跡 ＝ ★99 件★
- 右欄 M（作業樹のみ変更）＝ ★66 件★
- 右欄 D（作業樹で消えて居る）＝ ★5 件★（内訳 tests/unit 4・tests/test_helper 1）
- ★左欄（index の欄）に符の立つ行は 0 件 ∴ stage 済の差は現に無い★
## §C ㋑ numstat の和
- git diff --numstat の和 ―― file ★71★・追 ★4500★・削 ★1904★（git diff --shortstat も同じ三数を返す）
- git diff --cached --numstat の和 ―― file 0・追 0・削 0
- 食ひ違ひの意 ―― 71 ＝ M 66 ＋ D 5 であり ??（未追跡）は git diff の母に入らぬ。cached の 0 は㋐の左欄 0 件を別の器で見た同じ事である
## §D ㋒ dir 別の畳み（母は M の 66 件）
- scripts 23／shim 19／tests 10／lib 3／docs 3／root 直下 3／config 2／agents 1／.github 1／.claude 1
- 和 ＝ 23+19+10+3+3+3+2+1+1+1 ＝ ★66★ ∴ ㋐の M の数と合ふ
- shim の 19 件は悉く shim/hakudokai の下に在る（19 分の 19）
## §E ㋓ 代表 5 本の最終符（選び方＝各 dir の M を sort した先頭一本。中身の逐語は写さず 題は前半のみを引いた）
- scripts/agent_health_check.sh ―― 4f1f82b｜ashigaru-third-3｜2026-06-07｜題 feat(p1): fukuincho stage3 全自動ループ実装適用
- shim/hakudokai/_section18_roles.py ―― 94833a6｜hakudoukai｜2026-05-08｜題 feat(roles): Phase 15 takenaka 持ち場準備
- tests/agent_selfwatch.bats ―― 9102fa0｜hika019｜2026-02-15｜題 feat: macOS サポート追加
- lib/_section18_roles.sh ―― 94833a6｜hakudoukai｜2026-05-08｜題 feat(roles): Phase 15 takenaka 持ち場準備
- docs/08-ops/ack-retry-omni-engine-design.md ―― 2d0a1e4｜Commander Third｜2026-06-07｜題 fix(ack-omni cycle6): Codex cycle5 RED 5件是正
- ★作者は四人に分かれ 日付は 2026-02-15 から 2026-06-07 まで散る。但し之は ★最終符の作者★ であり ★未 commit の差を書いた手★ ではない★
## §F ㋔ 三値 ―― ★断じ得ぬ★
- ③器による生成物の再生成 を支へぬ根 ⑴ 直近の「生成物再生成」を名乗る符 6e221cd が触れた 17 本と 今の M 66 本の共通は ★0 件★
- ③を支へぬ根 ⑵ 一本あたりの形が一様でない ―― 追の多い順 3 本は 追519削66／追492削445／追382削190、少ない順 3 本は 追0削108／追0削143／追0削145
- ②複数の手が混じる へ傾く根 ―― ㋓の最終符の作者が四人・日付が四箇月に跨る。★但し最終符は差の手を証さぬ ∴ 之だけでは断じ得ぬ★
- 何を見れば足るか ―― 各 file の差の頭に器の名や生成の刻が入るかを讀めば ③ が判り、枝の一覧と reflog で此の樹を開いた窓を見れば ①②が判る
## §G ㋕ 締め
- ㋐の和 170（?? 99・M 66・D 5）／㋒の和 66（㋐の M と一致）／㋓で挙げた本数 5
## §H 床の守り ―― 讀取 5/12・焚 0・走 0・当て 0・★作業樹へ書込 0・stage 0・checkout 0・stash 0・clean 0・restore 0・git add -A 0★・DB 0・一時 file 0・本紙 35 行(wc)／36 片・枝は席が押す
