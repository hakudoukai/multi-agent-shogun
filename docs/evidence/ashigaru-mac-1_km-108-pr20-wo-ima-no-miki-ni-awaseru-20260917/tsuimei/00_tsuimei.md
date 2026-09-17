# km-108 追命(裁 seq326961) ★合流 4c99ff7c の検め★ ―― 專任1(ashigaru-mac-1) 子束

札=km-108-pr20-wo-ima-no-miki-ni-awaseru-20260917 / tsuimei_20260917_1735 ／ 據=委員長裁 pc_handshake seq326961(2026-09-17T17:15:54+09:00)+家老mac 追命(inbox msg_20260917_172216_ec5ebe86)
着手 刻=raw/00_chaku_toki.txt(2026-09-17T17:23:56+0900) ／ 宣ETA=18:30 ／ ★讀取のみ★(幹枝 karo-mac/km-gate-kou-otsu-20260917・4c99ff7c・他席 worktree・git add/commit/push 悉く不觸)
★此の子束は既成の親束(../manifest.txt・74行)を固定した儘、別臺帳(./manifest.txt・束内相対・cd 此處)で建てる★(記憶札: 既成の束は舊形の儘固定)。

## 一 結語(先に)

| 問 | 出目 |
|---|---|
| ㋐ 衝突印 | ★零★ ―― 根=/Users/momizimac/km108t_wt_47405(4c99ff7c を detach で出した己の捨て worktree)・深さ 11・regular file 1010 本(内 1 本は worktree の `.git` 指し file)・rc=0・刻=2026-09-17T17:25:03+0900。行頭 `<<<<<<< `=0／行全体 `=======`=0／行頭 `>>>>>>> `=0(raw/20)。第二の器 `git grep -E '^(<<<<<<< |>>>>>>> )'`=0 件 rc=1(raw/22)。陽性対照(印を入れた fixture・raw/21)は同じ器で 1/1/1・順に揃つた file 1・rc=1(二) |
| ㋐ 讀み手の blob | 4c99ff7c:scripts/checks/karo_mac_manifest_verify.py = ★ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579 / 198 行★ = main(4f591fc0)の blob と★同一★(raw/40) |
| ㋐ .gitignore | L169 `!scripts/checks/karo_mac_manifest_append.py`・L170 `!scripts/checks/karo_mac_manifest_verify.py` ★共に在り★(raw/41)。blob=2c809232 = ★main の blob と同一★(PR#20 が足した 1 行は main が既に持つ ∴「両側の和」= main 側そのもの・raw/43) |
| ㋑ 127 に在つて 198 に無い行 | ★5 本★(diff の `-` 行=5・集合 comm=5 の二器一致・raw/51・raw/52)。★家老の數 5 と合ふ★。198 にしか無い行=76(numstat 76/5・raw/50) |
| ㋒ bases | 198 行側 L97–105: argv 無 → `[repo根/, repo根/queue/reports/, dino-story-engine/]`・★`""` 無し★(raw/60)。㋒-1 束で argv 無 → ★rc=1・一致 0／実体無 77★(基点=器の在處=★捨て worktree の根★)／㋒-2 argv `.` → ★rc=0・一致 77★／補 cwd=repo根 argv 無 → rc=1(raw/70〜72)。★回帰ではない★(四) |
| ㋓ 大小二形 | index に `ERR-EKARTE-001.md`(e6de627b・79行・LF)と `err-ekarte-001.md`(de00cbd9・67行・★全行 CRLF★)の二項・disk は一本(core.ignorecase=true)。己の worktree の `git status` = `modified:   docs/runbooks/ERR-EKARTE-001.md`(porcelain ` M`)。★己の cwd(本 repo・他席の枝)では逆に ` M docs/runbooks/err-ekarte-001.md`★ ―― checkout 毎に片方が「変更有り」(raw/31・raw/39_main_checkout)。害と塞ぎ三案は(五) |
| ㋔ 門 9cd550fc(4c99ff7c の版)を束内相対の臺帳へ | BASE=. 有 → `條① 基点=★引数 明示★`・一致 77/77(條① は通る)／無 → `條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ)`・★條① 落ちた★(mon_172805/172808)。初走の gate_rc は両方 1 ―― 有の 1 は★條②③(己の raw 5 本の末尾空白/CR)★であつて條①ではない(六) |

## 二 ㋐ 解きの検め

- 合流 commit=4c99ff7c2a8466487d13a1494ed8f4fa9ca053f7・親①=0bb92e2b800c1b434c8a660d38f6feea7d450124(幹枝)・親②=4f591fc021947b9f477b676c96e36a1dc4437500(main)・合流点=6e9d40600a801aa713ac238e2e62bbae06c9e683(raw/11)。origin/main は 4c99ff7c の祖先(rc=0)。★家老の宣と全て一致★。
- `git diff-tree -c 4c99ff7c` は path を一本も出さぬ(raw/42) ―― 合流の結果は★全 path が両親のどちらかと同一★(手で書き足した行は無い)。
- 衝突印走査(driver/20_marker_scan.py・os.walk・S_ISREG のみ・.git dir 除外):

```
root=/Users/momizimac/km108t_wt_47405
files_walked=1010 maxdepth=11 skipped_nonregular=0
lines_lt(行頭'<<<<<<< ')=0  files=0
lines_eq(行全体'=======')=0  files=0
lines_gt(行頭'>>>>>>> ')=0  files=0
files_with_ordered_triplet=0
koku=2026-09-17T17:25:03+0900     rc=0
```

- 員數の突合(raw/23・36・37): `git ls-files`=1012 ＝ regular 1009 ＋ gitlink 2(tests/test_helper/bats-assert・bats-support・mode 160000)＋ 大小重複 1(ERR-EKARTE-001.md)。disk=1010 ＝ regular 1009 ＋ worktree の `.git` 指し file 1。★走査は index の regular file を全て歩いた★。
- 陽性対照(raw/21): 同じ器を、`<<<<<<< HEAD/=======/>>>>>>> other` を書いた fixture の根へ → 1/1/1・ORDERED 1・rc=1。★零は器が黙つて居る零ではない★。
- 讀み手 blob(raw/40): `git rev-parse 4c99ff7c:…verify.py`=ebfc4c0ecc080c0fcac0cb49b8e83c284a61e579・`cat-file -p | wc -l`=198。同 path の 4f591fc0 blob も ebfc4c0e(同一)。0bb92e2b 側は b19ec9ea/127(捨てられた側)。
- .gitignore(raw/41・43): 4c99ff7c の blob 2c809232 = main の blob。main が base から足した 3 行(`!scripts/idle_backlog_wake.sh`・append.py・verify.py)と PR#20 が足した 1 行(verify.py)。PR#20 の 1 行は main の 3 行に含まれる ∴ 和 = main。`git diff 4f591fc0 4c99ff7c -- .gitignore` は空(raw/41_gitignore_diff_vs_main.txt)。

## 三 ㋑ 127/198 の差を己で数へ直す

二器で数へた:

| 器 | 127 に在つて 198 に無い | 198 に在つて 127 に無い | 控 |
|---|---|---|---|
| `git diff --numstat b19ec9ea ebfc4c0e` | 5(削除) | 76(追加) | raw/50 |
| `sort` → `comm -23 / -13`(行の集合) | 5 | 76 | raw/52 |

5 本の逐語(raw/51):

```
-    """1 行から path 候補を取り出す。順に試す。"""
-    m = re.search(r"(?:^|\s)path=(\S+)", line)
-        out.append(m.group(1))
-    bases = argv[2:] or ["", "queue/reports/",
-                         "/Users/momizimac/DentalBI/.claude/worktrees/dino-story-engine/"]
```

★家老の數 5 と合ふ★。5 本は「一行 docstring・`path=(\S+)` 一本の regex・其の append・既定 bases の二行」で、其の意味は 198 側の +76(三段 regex・_dequote・\r 剥ぎ・repo 根導出・base_src)に置き換へられて居る(親束 四の一と同じ)。★撥ねる物無し★。

## 四 ㋒ bases から `""`(cwd)が消えた事の實測

198 行側 L97–105(raw/60_bases_198_verbatim.txt):

```
    if argv[2:]:
        bases = argv[2:]
        base_src = "引数(明示)"
    else:
        _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bases = [_root + os.sep,
                 os.path.join(_root, "queue", "reports") + os.sep,
                 "/Users/momizimac/DentalBI/.claude/worktrees/dino-story-engine/"]
        base_src = "既定(器の在處から導いた repo 根 %s ―― ★cwd に依らぬ★)" % _root
```

127 行側 L62–63: `bases = argv[2:] or ["", "queue/reports/", "/Users/momizimac/DentalBI/.claude/worktrees/dino-story-engine/"]`(★`""`=cwd 相対が第一★)。

實測(讀み手を直に・臺帳=manifest_jou1.txt 77 本・cwd=此の子束・器=捨て worktree 4c99ff7c の verify.py・raw/69):

| 札 | cwd | argv base | 基点(讀み手が刷つた) | 一致/相違/実体無/読めぬ | rc | 控 |
|---|---|---|---|---|---|---|
| ㋒-1 | 子束 | ★無★ | 既定(器の在處から導いた repo 根 ★/Users/momizimac/km108t_wt_47405★ ―― cwd に依らぬ) | 0/0/★77★/0 | ★1★ | raw/70 |
| ㋒-2 | 子束 | `.` | 引数(明示) | ★77★/0/0/0 | ★0★ | raw/71 |
| 補 | repo 根 | 無(臺帳は絶對 path) | 同 ㋒-1 | 0/0/77/0 | 1 | raw/72 |

- ★家老の申し送りは實測で正★: 束内相対の臺帳を `cd <束>` して素で照合すると★解けぬ★(実体無 77)。`.` を渡せば解ける。
- ★見付けた事(家老の申し送りの一段先)★: 「器の在處から導いた repo 根」は★呼び手の repo ではなく、其の verify.py が置かれた repo★である。捨て worktree の器で走らせた ㋒-1 の基点は /Users/momizimac/km108t_wt_47405 で、本 repo(/Users/momizimac/multi-agent-shogun)にある束は、cwd を何處にしても既定では★決して★見付からぬ。∴ 他の樹の器で束を照合する者は BASE を明示せねば必ず落ちる(門は「倒した事を刷る」で此れを報せる)。
- ㋒-3 ★回帰か否か★: ★回帰ではない★。根拠: ⑴ 4f591fc0(main)の blob が ebfc4c0e で 4c99ff7c と同一(raw/40) ⑵ main の履歴 26e23590(97行)→af0dacfc(127行・`""` 有)→★0bb82bfb(198行・`""` 無・2026-09-17 16:48:18 PR#22)★(raw/62) ∴ `""` を落としたのは PR#22 であつて本合流ではない ⑶ 198 側の註釈が「cwd に依らぬ」を★意図★として書き、門(裁322952 乙)が既定へ倒した時に其れを刷る ―― 意図した変更であり、本札 ㋖ の條「門は KM_GATE_MANIFEST_BASE=.」が既に其れを前提にして居る。★怖れは實在するが疵ではなく作法である★(BASE 無しの門は條① で落ちて止まる=fail-closed・親束 四の二の pure_nobase(127 側)が cwd 次第で通つた fail-open の逆)。

## 五 ㋓ 大小二形 docs/runbooks/ERR-EKARTE-001.md ／ err-ekarte-001.md

### 五の一 再現(己の worktree・raw/30〜39)

- `git ls-files -s docs/runbooks/` に★二項★: `100644 e6de627b… ERR-EKARTE-001.md`・`100644 de00cbd9… err-ekarte-001.md`。`git ls-files | tr A-Z a-z | sort | uniq -d` → ★1 本★(docs/runbooks/err-ekarte-001.md・樹全体で此の一組だけ・raw/35)。
- `git config core.ignorecase` = true。disk(`ls -la`)は ★err-ekarte-001.md 一本(3471 bytes)★・大文字名は無い。disk の内容 hash-object=★de00cbd9★(=小文字名の blob・checkout が後に書いた方が勝つた)。
- `git status`(逐語・raw/31_status.out):

```
Not currently on any branch.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   docs/runbooks/ERR-EKARTE-001.md

no changes added to commit (use "git add" and/or "git commit -a")
```

- ★同じ樹の別 checkout(己の cwd=本 repo・他席の枝が出て居る)では逆★: `git status --porcelain -- docs/runbooks/` → ` M docs/runbooks/err-ekarte-001.md`(raw/39_main_checkout_status_runbooks.txt)。どちらの名が「変更有り」に見えるかは checkout の書き順で決まる。
- 二 blob は別物(raw/39): e6de627b=79 行・LF・頭 `---`/`error_code: ERR-EKARTE-001`(front-matter 形)／de00cbd9=67 行・★67 行全て CRLF★・頭 `# Runbook: ERR-EKARTE-001 (カルテ visit 作成失敗)`。diffstat 67(+)/79(−)。
- 由来: 大文字名は 911eb135(2026-05-05)・小文字名は 04e7d0f9(2026-05-29)で入り、合流点 6e9d4060・main 4f591fc0・PR#20 0bb92e2b の三つ全てに二項在り(raw/34)=★元からの疵・本合流は作つて居らぬ★。CLAUDE.md は小文字名を 2 箇所で引く(L81・L424)。大文字名を引く参照は docs/evidence 外に 0(raw/39_refs_*)。

### 五の二 害 ―― `git add -A` を打つた者が何を commit して了ふか

1. 己の worktree では index の `ERR-EKARTE-001.md`(e6de627b・79行 LF)が「変更有り」に見え、`git add -A` は★disk の一本(de00cbd9 の中身)を大文字名の項へ★詰める。commit すると二項が★共に de00cbd9★になり、front-matter 形の 79 行版は★誰も消すと言はぬまま消える★(diff は raw/38: −79 +67・146 行動く)。
2. 逆順の checkout(己の cwd の出目)では小文字名が「変更有り」に見え、`git add -A` は小文字名へ e6de627b を詰める ―― CLAUDE.md が引く runbook の中身が★front-matter 形へ★入れ替はり、CRLF 版が消える。
3. 二台の Mac が交互に `add -A` すれば★二 blob が往復(ping-pong)★し、runbook の履歴が意味の無い差分で埋まる。commit message は runbook に一言も触れぬ(作業者は己の変更だけを見て居る)。
4. 副作用: 全席の「worktree 不触の證」(`git status` が空か)が★常に偽鳴り★する。親束 99_katazuke の「repo working tree untouched?」も此の 1 行を除いて讀まねばならぬ。★「不動」の判定が使へぬ★(記憶札: porcelain の不動は不触の證に成らぬ、の実例)。
5. Linux(第一・第二 PC)では二本が別 file として素直に出るので★Mac でしか見えぬ★ ―― Mac の席だけが誤 commit の当事者になる。

### 五の三 塞ぎ方の案(据ゑるな・提案のみ)

- 案一 ★一本化★: CLAUDE.md が引く小文字名 `err-ekarte-001.md` を正とし、大文字名の front-matter(error_code/severity …)で要る行を小文字名へ移した上で `git rm --cached docs/runbooks/ERR-EKARTE-001.md`(★tracked file の削除=変更統制の許可案件・委員長裁の後★)。CRLF は `.gitattributes`(`*.md text eol=lf`)で LF へ揃へる(別疵・同時に直すか否かは裁)。
- 案二 ★門に條を足す★: 出す前門 or pre-commit hook に「`git ls-files | tr A-Z a-z | sort | uniq -d` が非空なら落とす」を置き、Mac 席が大小重複を含む樹を出せぬ様にする(讀取のみの檢出・既存の疵は案一で先に除く)。
- 案三 ★運用★(案一が裁される迄の暫定): Mac 席は `git add -A` / `git commit -a` を打たず、path を名指して add する(記憶札「Shared worktree: git commit --only」の延長)。効き目は人の手に依る故、案二を伴はねば塞ぎにならぬ。

## 六 ㋔ 門を 4c99ff7c の版(9cd550fc・310 行)で BASE 有/無

器: gate=/Users/momizimac/km108t_wt_47405/scripts/checks/karo_mac_dasumae_gate.sh(sha256 e11f0d01…・0bb92e2b と同 blob・main には★無い★ file)・隣の讀み手=a507c998…(=ebfc4c0e/198)。臺帳=manifest_jou1.txt(77 本・束内相対)・cwd=子束。

| 札 | BASE | 條① の出目(逐語) | 條①以外 | gate_rc | 控 |
|---|---|---|---|---|---|
| m4c99_base | `.` 有 | `條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)` → `台帳とdiskの差 = 一致(manifest_verify.py rc=0)`・一致 ★77★/0/0/0 | ★條② 末尾空白 3 本・條③ CR 2 本★(己の raw・git diff/cat-file の写しが CRLF の runbook を含んだ故) | 1 | mon_172805_m4c99_base |
| m4c99_nobase | 無 | `條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★` → `★條① 台帳とdiskの差が落ちた★` | 同上 | 1 | mon_172808_m4c99_nobase |

- ★BASE を解する證は出目★: 有=條① 通る(一致 77)・無=條① 落ちる。門の報せ行は★言ふ通りに cwd に依らず★落ちた(親束の pure_nobase が cwd 次第で通つた fail-open は、198 の讀み手では★起きぬ★)。
- 初走の rc=1 の内訳は★條①ではなく條②③★(記憶札: rc を條で割つてから信じよ)。鳴つた 5 本は driver/K.py(seikei)を通し讀む爲の写しにした(raw/80_seikei_before/after: CR 67→0・3→0、末尾空白 3/1/5→0)。最終臺帳(./manifest.txt)への最終二走の出目は★臺帳外の控 mon_<HHMMSS>_final_*・99_katazuke.txt★に置く(紙は己を含む臺帳の數を書けぬ)。

## 七 數が意味せぬ事

- 「衝突印 零」は「合流が正しい」の意ではない。印が残らなかつた事だけを言ふ。解きの正しさは ㋐ の blob 同一(ebfc4c0e=main)と .gitignore blob 同一(2c809232=main)が別に言ふ。
- 「5 本」は「5 つの機能が失はれた」の意ではない。5 行は 198 側の +76 に意味を移した旧行で、失はれた挙動は `""`(cwd 相対)の★一つ★だけであり、其れは意図して落とされた(四)。
- 「実体無 77」は「臺帳が壊れて居る」の意ではない。同じ臺帳が argv `.` で 77 一致した。77 は基点の誤りの數であつて中身の誤りの數ではない。
- 「gate_rc=1(BASE 有)」は「4c99ff7c の門が落ちる」の意ではない。落ちたのは己の raw に混ぜた CR/末尾空白(條②③)で、條① は通つて居る。
- 「大小重複 1 本」は「1 file の疵」の意ではない。Mac の全 checkout・全席の `git status` に効く 1 本であり、Linux では 0 本に見える。
- 「1010 ≠ 1012」は走査漏れの意ではない。差 2 = gitlink 2 − `.git` file 1 + 大小重複 1(二)。

## 八 臺帳・門・片付け

- 臺帳=./manifest.txt(★此の子束内相対★・`cd <子束>` → `scripts/checks/karo_mac_manifest_append.py` のみ)。門=`KM_GATE_MANIFEST_BASE=. bash <4c99ff7c の門> manifest.txt <path 列>`。控=mon_<HHMMSS>_<札>.{log,err,rc}(走る毎に別名・臺帳へ入れぬ)。
- 生成 3 本(裁326273)は最終臺帳に對して行ひ、cmp の出目は 99_katazuke.txt(臺帳外)。
- 己が作つた worktree 一つ(raw/10_wt_path.txt=/Users/momizimac/km108t_wt_47405)は最終の門の後に `git worktree remove --force` で片付ける(控は 99)。★家老の worktree /Users/momizimac/karo_mac_pr20_merge_36939・幹枝・4c99ff7c・/private/tmp/gunshi-km49.*・.claude/worktrees/karo-mac-a1 には一指も触れて居らぬ★。
- 己の測り誤り(記す): `$c:scripts/…` を zsh の `:s` 修飾に食はれ raw/62_main_verify_blobs.txt を一度誤つた(親束と同じ罠・`"${c}:…"` で取り直した)。
