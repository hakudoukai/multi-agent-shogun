# 自主束(第70弾 便5 の未測を埋める)―― 門の基点の口が ★空文字 ""★ の時、札は「引数 明示」を刷りながら出目は cwd で反転する ―― 二器(verify 直・門 main)× 基点四態(unset/明示/空文字/空白)× cwd 二所(repo 根・km-70 束の根)= 16 走・外れ 0・讀取のみ(共有器へ 0 byte・km-70 束へ 0 byte)―― 答を先に(★數の出處 = raw/10_kuumoji.{txt,tsv} + raw/10_*_*.{out,err,rc,argv} / raw/05_seikyu*.txt(起・便)/ _after/60_gate_rcs.txt(門・紙の後に生れる故 紙は其の數を書けぬ)★)

★臺帳の基点(一行)★: 本束の臺帳 `ashigaru-mac-1_a1-jishu-kuumoji-kiten-20260917_manifest.txt` の path は ★束の根 `/Users/momizimac/multi-agent-shogun/docs/evidence/a1-jishu-kuumoji-kiten-20260917/` からの相對(束内相対・裁 322699)★ ―― append.py を cwd = 束の根で呼ぶ故。照合は門に `KM_GATE_MANIFEST_BASE=<束の根>` を渡すか verify.py の第二引数に束の根を渡せ。既定基点(repo 根)で当てれば悉く実体無と出る(基点の違ひ)。★空文字 "" は渡すな ―― 本紙の題其の物(cwd 相対に成る)★。

## 0. 断(先に)
1. **★空文字の基点は「明示」の札の儘 cwd 相対である。★** 門 `KM_GATE_MANIFEST_BASE=""`: cwd=repo 根 → 條① 実体無 139 / rc 1「出すな」、cwd=km-70 束の根 → 一致 139 / rc 0「出してよい」。★両走とも stderr は同じ札 `條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)` を刷る★。verify.py 直(argv[2]="")も同じ形(札 `基点 引数(明示)`)。
2. **他の三態は cwd に依らぬ。** unset → 既定(repo 根)で実体無 139 / rc 1(両 cwd)。明示(束の根の絶対 path)→ 一致 139 / rc 0(両 cwd)。空白 " " → 実体無 139 / rc 1(両 cwd・`os.path.join(" ", p)` = " /…" ゆゑ偶々 fail-closed)。
3. **讀んだ逐語が予想を与へ、16 走が悉く其の通りであつた(外れ 0)。** 門 L197 `[ -n "${KM_GATE_MANIFEST_BASE+set}" ]` は空文字でも set を返し、L194 の註は「空文字も『cwd 相対』の明示として通る」と★自認★して居る。verify.py L97 `if argv[2:]` は `[""]` を真とし base_src=「引数(明示)」、L146 `os.path.join(b, p) if b else p` が b="" で cwd 相対に落とす。
4. **門の乙(env_state・L40〜46: unset/empty/blank/value を分けて名指す)は ★閾(fix_threshold)にのみ★ 当たり、基点には当たつて居らぬ。** ∴ 9/12 止血(L185〜188 逐語「旧版は基点に ★明示の ""★ を渡して居た。"" は cwd 相対 ―― ∴ 門は ★立つ場所で出目が変つた★」)が閉ぢた形は、呼ぶ側が "" を渡せば再び開く ―― 而も札は「明示」で、既定へ倒した事は刷られぬ。
5. **共有器へ 0 byte・km-70 束へ 0 byte。** 禁域と km-70 束 前⇔後: 門 e11f0d0142549086→e11f0d0142549086 同 / 照合器 a507c998c7bd6485→a507c998c7bd6485 同 / km-70 印 ('c063d827d172f2ad', 197)→('c063d827d172f2ad', 197) 同。

## 1. 走り(10)―― 表は raw/10_kuumoji.txt の逐語
- 臺帳 = km-70 の凍結済(束内相対・項 139・sha16 d444a828b6fc4bcd)。門 sha16 e11f0d0142549086 / 照合器 sha16 a507c998c7bd6485。門 main の argv = [臺帳, 紙, 臺帳](km-70 の 60 と同じ形)。基点は門には環境変数、verify 直には argv[2] で同じ値を渡す(unset は argv[2] 無し)。
| 器 | 基点 | cwd | rc | 母數 | 一致 | 相違 | 実体無 | 読めぬ | 基点の札 | cwd依存 | 期待通り |
|---|---|---|---|---|---|---|---|---|---|---|---|
| verify | unset | repo | 1 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根 /Users/mom | 不依存 | True |
| verify | unset | taba | 1 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根 /Users/mom | 不依存 | True |
| verify | meiji | repo | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | 不依存 | True |
| verify | meiji | taba | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | 不依存 | True |
| verify | kuu | repo | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | cwd依存★ | True |
| verify | kuu | taba | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | cwd依存★ | True |
| verify | kuuhaku | repo | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | 不依存 | True |
| verify | kuuhaku | taba | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | 不依存 | True |
| gate | unset | repo | 1 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根 /Users/mom | 不依存 | True |
| gate | unset | taba | 1 | 139 | 0 | 0 | 139 | 0 | 既定(器の在處から導いた repo 根 /Users/mom | 不依存 | True |
| gate | meiji | repo | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | 不依存 | True |
| gate | meiji | taba | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | 不依存 | True |
| gate | kuu | repo | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | cwd依存★ | True |
| gate | kuu | taba | 0 | 139 | 139 | 0 | 0 | 0 | 引数(明示) | cwd依存★ | True |
| gate | kuuhaku | repo | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | 不依存 | True |
| gate | kuuhaku | taba | 1 | 139 | 0 | 0 | 139 | 0 | 引数(明示) | 不依存 | True |
- 外れ 0 行 / 母數 16 走。cwd 依存 = 同じ器・同じ基点で cwd を変へたら (rc, 四数) が変はるか ―― ★kuu のみ依存★(二器とも)。
- 門 kuu の結語 逐語: 門 kuu cwd=repo: 條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE) / ★出す前 門が落ちた。出すな。★ / 門 kuu cwd=taba: 條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE) / ★出す前 門 通。出してよい。★

## 2. 提案(★之は提案であつて器の改めではない ―― 門へは一字も入れて居らぬ★)
- 基点の口にも乙(env_state)を当てる: `empty`/`blank` は ★拒む(rc≠0・「基点が空 ―― cwd 相対は許さぬ」を刷る)★ か、既定(repo 根)へ倒して ★倒した事を刷る★。何れも「札が明示と言ひながら cwd 相対」を無くす。verify.py 側は L97 を `if any(argv[2:])` 等で空を既定へ倒し、base_src に ★渡された値★(空なら「空文字」)を刷る。
- 戻し方(提案が採られた時の可逆): 門は if の一行、verify は L97 の一行 ―― 控へ戻せば旧挙動。裁は家老・上の物。

## 3. 便と宣⇔實(05・62)
- 起 = おめざめくん便 06:32:20 → 05 弾を請ふ便 2026-09-17T06:34:55+0900(字数 296・rc 0)。一走目は 301 字で己の門(300 字)に鳴つた → .first に残し一字削つた。
- ★宣 ETA は出さなんだ(疵)★ ―― 自主の弾ゆゑ端点を宣せずに入つた。實は 63_sent.txt の刻(納め便 1 本目の直前)−05 の刻。次弾の材料: 本弾の器は 10/15/50/59/60/62/70 の 7 本。

## 4. 本紙が意味せぬ事
1. 「空文字は疵」とは言はぬ ―― 門 L194 の註は之を★設計として自認★して居る。本紙の的は「札が空文字と絶対 path を見分けぬ」事であつて、動作が仕様外である事ではない。
2. 外れ 0 は ★km-70 の臺帳一本(束内相対)★ に対してのみ。repo 根相対の旧形臺帳なら kuu@repo は一致に成り得る(未測)。
3. cwd 依存は ★二所(repo 根・束の根)★ でのみ測つた。第三の cwd(例 fixtures 配下)は未測。
4. 札「引数(明示)」が偽だとは言はぬ ―― 引数は確かに明示された(空文字として)。刷られて居らぬのは「何を明示したか」である。
5. 乙が基点に当たらぬのは L197 の設計(閾のみ)であり、「当てよ」は提案であつて裁ではない。共有器へは 0 byte。
6. 空白 " " が両 cwd で落ちたのは os.path.join の偶然(" /…" が実在せぬ)であつて守りではない ―― " " が実在する dir 名なら通る。
7. 数は門 e11f0d0142549086 / 照合器 a507c998c7bd6485 の版に対する物。版が変はれば数も変はる。
8. 己の門の数(main/all/nobase の rc・條⑤ byte和)は紙の後に生れる故 本紙には無い ―― _after/60_gate_rcs.txt を見よ。

## 5. 數の出處
- raw/10_kuumoji.py(器)/ raw/10_kuumoji.{txt,tsv}(表)/ raw/10_{verify,gate}_{unset,meiji,kuu,kuuhaku}_{repo,taba}.{out,err,rc,argv}(16 走 × 4)/ raw/15_normalize.txt(shell 直取り三本を kaki へ)/ raw/05_seikyu*.txt(便)/ raw/05_measure*.txt(契約 0・板 owner 0・DB 送信器 無)。
