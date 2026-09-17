# 第82弾 ―― ★main の乖離を一本づつ名指しで測れ★: local main 363d5fb0 と origin main 4be3ee19 は分岐点 6e9d4060(= karo-mac/skills-tools-20260908b の tip)から両向きに乖離。母數三つ= rev-list 16/21(origin 側 merge 11)・非merge 16/10・patch-id 一意化 16/10 → 相手に無い patch-id ★14/8★(家老の「14/8」は此の第三の數)。local 16 本の判= 甲 2(f2bfa26a・f0d59a3b ≡ origin af0dacfc・26e23590= PR #15 で作り直された同 patch)/ 乙 14 / 丙 0。origin 21 本は悉く手元に object 在り(2026-09-17 04:19:56 の fetch 痕)・手元の枝 0 本が含む・「誰が押したか」は測れぬ。9 枝の「9 vs 1」の食ひ違ひは ★枝の中身でなく main の乖離 14 本が写つた物★(9 tip は悉く local main の祖先)。乙 14 本は origin に枝 karo-mac/km-gate-kou-otsu-20260917(=363d5fb0)他 46 本として在り main に無い。推す道= 乙(其の枝を PR で origin main へ)。.gitignore は file 3-way で衝突 0。

- 弾: km-95(家老便 msg_20260917_134006_c8836a16(clear_command・「第82弾」)・札 queue/tasks/ashigaru-mac-1.yaml sha16 e54b5b23542ef48b 64 行 4747B)/ 束 docs/evidence/km-95-main-no-kairi-wo-hitotsu-zutsu-nazashi-de-hakare-20260917 / 書手 ashigaru-mac-1(專任1)/ 宛 karo-mac(監査 gunshi-mac へ sb・PASS は待たぬ= 裁 seq324831)/ 親裁 無し(家老 seq325507 が生んだ穴・的= 家老の紙 karo-mac-origin-eda-kenbun-20260917/README.md 2620B sha256 585eea9f…= 札の宣と一致)
- 刻: 起 2026-09-17T13:43:08+0900 / 着手便 msg_20260917_134340_dd56d11f(13:43:40・宣ETA 60〜150 分(幅)・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 紙 2026-09-17T13:51:46+0900 / 作業樹の枝 ashigaru-mac-3/km-51-…(共有・不觸)・HEAD 0039e1321654
- ★禁の守り★: git は読取の口のみ(raw/gitro.py が白表で縛る= rev-parse/ls-remote/for-each-ref/merge-base/rev-list/log/cherry/diff-tree/patch-id/cat-file/diff/reflog show/branch --contains)。fetch・pull・merge・rebase・reset・cherry-pick・push・update-ref・branch -f・remote set-url は ★0 回★。★束の commit も打たぬ★(札「refs を書き換へる命令を一つも」を字義で読んだ ―― git commit も ref を動かす。家老が据ゑるなら束 path と sha16 は ㊇)。生器へ 0 字・watcher 不觸・/tmp 不使用・行番を焼かぬ(逐語で指す)。origin の今の値は ls-remote(00・10)で引き、手元の refs/remotes/origin/main と ★一致★(食ひ違ひ無し)。
- 母數の宣: ㋐= rev-list(O..L / L..O)の commit 数 → 非merge の数(= git cherry の母數)→ patch-id(--stable)一意化の数、の三つを ★数の前に★ 宣す(㊁)。㋑= local 16 本。㋒= origin 21 本。㋓= 家老の紙から regex で抽いた 9 枝(手写し 0)。origin の枝 snapshot= ls-remote --heads 239 本(家老の宣 239 / karo-mac 41 / ashigaru-mac 18 と一致・raw/10_ls_remote_heads.txt)。
- 條① の宣(受④): 臺帳の項= README.md 1 + raw/ の通常 file 30 + raw/50_build_manifest.py 1 = ★32★(非通常 file 0)。條① 一致は ★32/32★ を期待し、實は _gate/ の門控(main 走)に焼く。員外は _after/61_ingai.txt に ★自ら数へて名指し★(㊇)。

## ㊀ 結語を先に

1. ★㋐ 分岐点★(10): merge-base --all = ★1 本★ 6e9d40600a801aa713ac238e2e62bbae06c9e683(2026-09-08T20:53:06+09:00・MomiziMac・「docs(skill): ⑻『語 を数へたら 文脈 を読め』」)= karo-mac/skills-tools-20260908b の tip 其の物。origin/main は其れを PR #8(49f843c1)で取り込んで先へ進み、local main は其の上へ直に 16 本を積んだ(reflog に merge/pull は 2026-08-07 の ff 一件のみ・㊃)。
2. ★㋐ 三つの母數★(10): local 側(O..L)= rev-list ★16★(merge 0)/ 非merge ★16★ / patch-id 一意 ★16★ → 相手に無い ★14★・cherry +14 −2。origin 側(L..O)= rev-list ★21★(merge ★11★)/ 非merge ★10★ / patch-id 一意 ★10★ → 相手に無い ★8★・cherry +8 −2。∴ 家老の「14/8」は ★第三の數(非merge patch-id)★ であつて commit の數(16/21)ではない。--stable と --unstable の patch-id が食ひ違ふ commit= local 11 / origin 7 だが、判(甲/乙)は両者で同じ(cherry の +/− と 16/16・10/10 一致= 二器)。
3. ★㋑ local 16 本の判★(20): ★甲 2★= f2bfa26a163d(fix 台帳照合の器・読めぬ行)≡ origin af0dacfcbc88 / f0d59a3b6315(feat 台帳照合の器 一本化)≡ origin 26e23590f4e4 ―― 共に origin 側 PR #15(mac/karo-manifest-verify-20260910・committer iincho)で ★同じ patch が別 sha で作り直され★ 入つた。★乙 14★= 707df791(gate4)・dafb2402(第五條 寸法)・e8470d8c(註)・2320dbbb(dasumae gate)・f626f200・561dd8ff(死箱の門 rc68)・c771fbfc・2187e25f・b82b98c9・99ea2984・2992eeca・d4849b0e・43808f83・363d5fb0(門 甲乙)。丙 0。甲+乙+丙= 16 = 母數。乙 14 本が変へた path の内 origin tip で同 blob の物= 0(中身は別経路でも届いて居らぬ)。
4. ★㋒ origin 21 本★(30): 悉く ★object 手元に在り★(cat-file -e 21/21)= refs/remotes/origin/main 経由で fetch 済(reflog: 2026-09-17 04:19:56 fetch → 4be3ee1)。★手元の refs/heads/* が含む物 0 / refs/remotes/* からのみ届く 21★。非merge 10 の内 patch-id が local と一致 2(上の甲の相手)・不一致 8(中身も届いて居らぬ= hakudoukai / ashigaru-third-3 / iincho の receiver・watcher・bats の直し)。merge 11 は悉く committer GitHub <noreply@github.com>(PR #4〜#17 の web merge)。★測れぬ★: 誰が・何処の PC から押したか／local main へ取り込まぬ「判断」の有無 ―― clone からは読めぬ(推量は書かぬ)。測れた「理由」= ★local main が 2026-08-07 以来 一度も origin/main を取り込んで居らぬ★(reflog 40 行の内 merge 1= 2026-08-07 ff・reset 2= 2026-09-08 HEAD~1 ×2・他は commit)。
5. ★㋓ 9 枝★(40): 紙の sha は ls-remote の今と ★9/9 一致★。手元に ref が在る枝 3(a3-r39-fix / km-50-47 / km-gate-kou-otsu)・無い枝 6(object は 9/9 在り)。cherry 基点=local: ★+0 が 9/9★(家老の宣 9 と一致)。cherry 基点=origin: +0 は ★skills-tools-20260908b の 1 本のみ★(家老の宣 1 と一致)、他 8 枝は +1〜+14(+ に立つ sha は悉く local 側 16 本の中= 表)。祖先= 9 tip 悉く local main の祖先(○)・origin main の祖先は skills-tools のみ(○)。★食ひ違ひの出所(一行)★: 9 tip は悉く local main の祖先ゆゑ基点=local では寄与 0 だが、tip が含む乙 14 本は origin/main に無い ∴ 基点=origin では其れらが + に立つ ―― 差は「枝の中身」でなく「main の乖離 14 本」其の物が写つて居る。km-gate-kou-otsu の tip = local main 其の物(363d5fb0)ゆゑ 14 本悉くが +。
6. ★㋔ 三案★(45・46): 甲= local を origin へ寄せる(直る: main が一つに / 直らぬ: 乙 14 本が main から落ち 9 枝を消せば ★両側から失せる★)。★乙= origin へ未到達分を出す★(直る: 14 本が origin/main へ・9 枝が両基点で 0 に / 直らぬ: 甲 2 本の二重 sha は残る(diff 空・害無し)・真の merge の出目は走らせねば測れぬ・後に local main を合はせる一手が要る)。丙= 別物と扱ひ基点だけ改める(直る: 「9 vs 1」の説明 / 直らぬ: 乖離其の物・14 本は永久に届かぬ)。★推す= 乙★(捨てた理由: 甲は中身を失ふ側へ倒す・丙は解かぬ)。乙の足場= ★乙 14 本は origin に既に在る★: 手元に object の在る origin 枝 82 本の内 ★46 本★ が 363d5fb0 を含む(karo-mac/km-gate-kou-otsu-20260917 = 363d5fb0 其の物)∴ 此の席からの push は要らぬ。両側が変へた path の重なり= ★2★(.gitignore・karo_mac_manifest_verify.py)、後者は両 tip で同 blob、前者は ★file 単位 3-way(git merge-file・ref 不觸)で衝突 0★(local +1 行 / origin +2 行・重なり無し)。
7. ★裁へ出す一文★(45・python len ★299★ 字 = wc -m 299・條 300 通): 「裁へ: local main 363d5fb0 と origin main 4be3ee19 は分岐点 6e9d4060 から両向きに乖離(patch-id で local 14・origin 8、内 2 本は同 patch 別 sha)。local の 14 本は origin に枝 karo-mac/km-gate-kou-otsu-20260917(=363d5fb0)に在り main に無い。推す道=乙: 其の枝を PR で origin main へ入れ、後に local main を合はせる。9 枝は其の後 両基点で寄与 0 と成つてから消す。今消せば 14 本が両側から失せる。」
8. ★疵 7(㊉)・便= 着手 1 + 納め 4(_after/62)+ 監査 1(_after/64)。★

## ㊁ ㋐ 分岐点と三つの母數(raw/10_bunki.txt・10_local.tsv・10_origin.tsv・10_ls_remote_heads.txt)

| 側 | (a) rev-list commit | 内 merge | (b) 非merge= cherry 母數 | (c) patch-id 一意 | 相手に無い patch-id | cherry + / − | stable≠unstable |
|---|---|---|---|---|---|---|---|
| local(O..L) | 16 | 0 | 16 | 16 | ★14★ | 14 / 2 | 11 |
| origin(L..O) | 21 | 11 | 10 | 10 | ★8★ | 8 / 2 | 7 |

- 全列(full sha・subject・author 日・cherry)は raw/10_bunki.txt の二表(local 16・origin 21)に逐語。TSV に author/committer の名と mail・commit 日・両 patch-id。
- origin の枝 snapshot(ls-remote --heads)= 239 本 / karo-mac 41 / ashigaru-mac-* 18。手元の refs/remotes/origin/* は ★7 本★のみ(HEAD・main・ashigaru-mac-1 km-72・ashigaru-mac-2 km-53・ashigaru-mac-3 km-49・karo-mac lot48235904・karo-third disk-pressure)∴ origin の枝の殆どは手元に ref が無い(object は在り得る・45② で 82 本在り/157 本無し)。

## ㊂ ㋑ local 16 本の判(raw/20_local_side.txt・.tsv)

| 判 | 本数 | sha(12) | 根拠 |
|---|---|---|---|
| 甲 | 2 | f2bfa26a163d / f0d59a3b6315 | patch-id(--stable)が origin af0dacfcbc88 / 26e23590f4e4 と一致 ∧ cherry − |
| 乙 | 14 | 707df7914723 dafb24026c77 e8470d8c4536 2320dbbb871e f626f2002255 561dd8ff4e1e c771fbfcc3db 2187e25fba27 b82b98c91222 99ea2984f2a4 2992eecab19d d4849b0e6987 43808f8363e9 363d5fb06084 | origin 側 10 本の何れとも不一致 ∧ cherry + |
| 丙 | 0 | ― | (二器が食ひ違へば丙へ落とす則・落ちた物無し) |

- 則: 甲= patch-id 一致先が在る ∧ cherry が −。乙= 一致先無し ∧ cherry +。二器が食ひ違へば丙(理由付き)。merge・空 diff も丙。
- 「O の tip で blob 同じ」列: 乙 14 本 悉く 0 ―― 中身は別経路でも origin/main に届いて居らぬ。甲 f2bfa26a は 1/1(同 patch が入つた故 当然)。

## ㊃ ㋒ origin 21 本(raw/30_origin_side.txt・.tsv・30_reflog_*.txt)

| 測り | 出目(母數 21) |
|---|---|
| object 手元 | 在 21 / 無 0 |
| 届く手元の ref | refs/heads/* 0 / refs/remotes/origin/{HEAD,main} のみ 21 |
| patch-id 一致(非merge 10) | 一致 2(af0dacfc→f2bfa26a・26e23590→f0d59a3b)/ 不一致 8 |
| merge 11 の committer | 悉く GitHub <noreply@github.com>(PR #4 #5 #6 #7 #8 #9 #10 #11 #15 #16 #17) |
| merge の第二親 | #4〜#8 の第二親は手元の heads 55 本が含む(分岐点以前)/ #9〜#17 の第二親は手元の heads に無し |
| fetch の痕(reflog origin/main) | 8 行・最新 2026-09-17 04:19:56 fetch origin --quiet: ff → 4be3ee1(其の前 09-10 14:56 / 09-09 05:27 / 09-09 01:58 / 09-08 ×3 / 08-07) |
| local main の痕(reflog main) | 40 行・merge 1(2026-08-07 02:00:57 merge origin/main: Fast-forward)・reset 2(2026-09-08 HEAD~1 ×2)・他 commit |

- ★測れた理由★: local main は 2026-08-07 の ff 以来 origin/main を一度も取り込まず、origin/main は其の後 PR 11 本で進んだ。fetch は 8 回届いて居る(object は在る)が merge が無い。
- ★測れぬ事(推量を書かぬ)★: 各 commit を誰が・何処の PC から押したか／local main へ取り込まぬ判断が在つたか否か／PR を誰が押したか(committer GitHub は web merge の徴に過ぎぬ)。

## ㊄ ㋓ 9 枝(raw/40_eda9.txt・.tsv)

| 枝 | 紙 sha(12) | ls-remote 今 | 手元 ref | 基点=local +/− | 基点=origin +/− | 祖先 L/O |
|---|---|---|---|---|---|---|
| karo-mac/a3-r39-fix-20260917 | 2992eecab19d | 一致 | heads | +0 −0 | +11 −2 | ○/× |
| karo-mac/gate4-20260909 | 707df7914723 | 一致 | 無 | +0 −0 | +1 −0 | ○/× |
| karo-mac/gate5-20260909 | e8470d8c4536 | 一致 | 無 | +0 −0 | +3 −0 | ○/× |
| karo-mac/gate5-note-20260909 | e8470d8c4536 | 一致 | 無 | +0 −0 | +3 −0 | ○/× |
| karo-mac/km-50-47-20260917 | 43808f8363e9 | 一致 | heads | +0 −0 | +13 −2 | ○/× |
| karo-mac/km-dead-inbox-gate-20260917 | b82b98c91222 | 一致 | 無 | +0 −0 | +9 −2 | ○/× |
| karo-mac/km-gate-kou-otsu-20260917 | 363d5fb06084 | 一致 | heads | +0 −0 | +14 −2 | ○/× |
| karo-mac/manifest-verify-20260909 | f0d59a3b6315 | 一致 | 無 | +0 −0 | +3 −1 | ○/× |
| karo-mac/skills-tools-20260908b | 6e9d40600a80 | 一致 | 無 | +0 −0 | +0 −0 | ○/○ |

- + に立つ sha は表(40)に名指し・悉く local 側 16 本の中(内 local 16 本の中= 11/1/3/3/13/9/14/3/0)。manifest-verify の −1 = f0d59a3b(甲・origin に同 patch)。
- ★一行★: 差は「枝の中身」でなく「main の乖離 14 本」が写つた物 ―― 基点=local では tip が祖先ゆゑ 0、基点=origin では tip が含む乙 14 本の分だけ + に立つ。

## ㊅ ㋔ 三案と推す案(raw/45_an3.txt・46_gitignore_3way.txt)

| 案 | 直る物 | 直らぬ物 |
|---|---|---|
| 甲 local→origin へ寄せる | main が一つに・9 枝の判が基点に依らず | 乙 14 本が main から落ちる・origin main には届かず・9 枝を消せば両側から失せる |
| ★乙 origin へ未到達分を出す★ | 14 本が origin/main へ・9 枝が両基点で 0 に成つてから消せる | 甲 2 本の二重 sha(diff 空)・真の merge の出目は走らせねば測れぬ・後に local main を合はせる一手 |
| 丙 別物と扱ひ基点のみ改める | 「9 vs 1」の説明・消せるのは skills-tools 1 本と読める | 乖離 14/8 其の物・14 本は永久に届かぬ・以後 毎回 基点を宣す羽目 |

- 捨てた理由: 甲は中身を失ふ側へ倒す道(測りの目的= 枝を消せるか、に対し逆)。丙は数の食ひ違ひを説明で済ませ乖離を解かぬ(札の的は「乖離を解く道」)。乙は origin に既に在る 363d5fb0(46 枝が含む)を main へ入れるだけで push 不要・PR は閉ぢられる(可逆)。
- 乙の足場の測り: 重なり path 2(.gitignore・karo_mac_manifest_verify.py)/ 後者 同 blob / 前者 merge-file 3-way rc 0(local `!scripts/checks/karo_mac_manifest_verify.py` +1 行・origin 同行 +1 と `!scripts/idle_backlog_wake.sh` +1)。此の測りが意味せぬ事: file 単位であり真の merge(rename/mode/他 path)は走らせねば分からぬ。
- 裁へ出す一文= ㊀7(python len 299 字)。

## ㊆ 数が何を意味せぬか

- 「14/8」は非merge patch-id の数。commit の数(16/21)でも、枝の数でも、file の数でもない。merge 11 本は cherry の母數の外。
- 「46 枝が 363d5fb0 を含む」は ★下限★: origin の枝 239 本の内 157 本は object が手元に無く測れぬ(fetch 禁)。
- 「衝突 0」は .gitignore の file 単位 3-way の値。merge 全体の出目ではない。
- 「測れぬ」= clone に痕が無い事であり、「誰も押して居らぬ」の意ではない。
- 手元の refs/remotes/origin/main と ls-remote は本弾の刻で一致した。刻が違へば違ひ得る(00・10 に刻)。

## ㊇ 束・臺帳・門・員外

- 束= docs/evidence/km-95-main-no-kairi-wo-hitotsu-zutsu-nazashi-de-hakare-20260917/ = README.md + raw/(器 .py と出目 .txt/.tsv・46_gitignore/ の写し四本・gitro.py・kaki.py)+ MANIFEST.txt + _gate/ + _after/。
- 臺帳= raw/50_build_manifest.py が ★cd 束の根★ で karo_mac_manifest_append.py を呼ぶ(束内相対・裁 seq322699・手書き 0)。載せる= README.md + raw/ の通常 file(50 の .py 其の物を含む・50 の出目三つを除く)= 宣 32 項。
- 門= _after/60_gate_run.py が selftest / main(KM_GATE_MANIFEST_BASE=.・cwd 束の根)/ nobase(基点無し・落ちて正)の三走、門控は _gate/mon_km95_<刻>_{selftest,main,nobase}.log(走毎に一本)+ 纏め一本。
- 員外(臺帳に載らぬ)= MANIFEST.txt 其の物 / raw/50_build_manifest.out .err / raw/50_sengen.txt / _gate/* / _after/*。★_after/61_ingai.py が disk を歩いて数へ、名指しで列べる(己の出目 61_ingai.txt を自産と宣す)★。
- ★commit は打たぬ★(札の禁を字義で)。束の sha16 は納め便に(README・MANIFEST・門控)。家老が据ゑるなら `git hash-object` + temp index の温 recipe(km-92 _after/66 逐語)で worktree に触れず載せられる。

## ㊈ 器と読みの則

- raw/gitro.py: git の白表(読取の口のみ)。白表外は assert で落ちる。branch は --contains のみ・reflog は show のみ。
- kaki.py は km-86/km-92 逐語(行末空白落とし・LF・末尾改行一つ・空は一行の印)。
- 家老の紙の 9 枝は regex `^  - (karo-mac/\S+)  ([0-9a-f]{40})$` で抽く(9/9・手写し 0)。
- 数は悉く器の出目(raw/*.txt)から本紙へ写した。本紙の数と raw の数が食ひ違へば raw が正。

## ㊉ 疵(隠さぬ)

- ★疵 1★ 着手便の胴を測らずに書き、門が二度鳴つた(321 字 → 306 字 → 297 字で通)。器が止めたゆゑ超過の便は送られて居らぬが、鳴つた二胴の写しは raw/01_letter.txt が上書きされて残らぬ(数は此処にのみ)。
- ★疵 2★ 45① で「衝突し得る」と先に書き、46 で測つてから 45 を書き直した ―― 45_an3.txt の刻は 46 より後(順が逆)。断じてから測つた形。
- ★疵 3★ 30 の「測れぬ」は 21 本 同文。一本づつの差は object/届く ref/patch-id/committer/第二親 の列にしか無い(「理由」を一本づつ別の言葉で言へた訳ではない)。
- ★疵 4★ 45② の「46 枝が 363d5fb0 を含む」は下限 ―― origin 239 枝の内 157 本は object が手元に無く測れぬ(fetch 禁)。
- ★疵 5★ 束を commit せぬ(札の禁を字義で読んだ)ゆゑ、束の sha16 は disk の物で版が動き得る。raw/ は 60 で 0444/0555 の錠を掛けるが _after/ は掛けぬ。
- ★疵 6★ 本紙の数は raw から手で写した。70_kami_awase.py が主な数を raw に当てて照合するが、照合するのは列べた組だけ(全数ではない)。
- ★疵 7★ 「乙を推す」は席の判である。merge の真の出目・PR を誰が押すかは此の席では測れぬ(裁へ出す)。
