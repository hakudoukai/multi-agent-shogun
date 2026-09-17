# km-108 ★PR#20 を今の幹に合はせる★ ―― 專任1(ashigaru-mac-1) 初段

札=km-108-pr20-wo-ima-no-miki-ni-awaseru-20260917 ／ 據=委員長裁 seq326873(PR#22 merge 済・PR#20 の再走を専任へ)+裁 seq326273(固定head 再走・生成3本・PR ref)
着手 刻=raw/00_chaku_toki.txt(2026-09-17T17:10:41+0900) ／ 宣ETA=18:10 ／ ★讀取のみ★(PR merge・PR push・refs 書換・他席 worktree・git add/commit/push 悉く不觸)

## 一 結語(先に)

| 問 | 出目 |
|---|---|
| PR#20 幹をそのまま今の幹へ当てると | ★merge rc=1・衝突 2 本★(甲 .gitignore content 1 hunk／乙 karo_mac_manifest_verify.py ★add/add★ 8 hunk)。己の捨て worktree で再現(二) |
| 解 | ★二本とも HEAD(=main)側を採る★。甲=PR#20 側は其の位置に行が無い(空)・乙=PR#20 の讀み手 b19ec9ea は ★main が 0bb82bfb で置き換へる前に持つて居た blob と同一★ ∴ 失ふ物が無い(三) |
| 127行 と 198行 の差 | ★198 = 127 + commit 0bb82bfb の治し(+76/−5) そのもの★。PR#20 側に main に無い行は ★0★(raw/33・raw/31) |
| 門 9cd550fc(PR#20 幹の版)を己の束へ | BASE=. 有 → ★條① 一致 59/59・rc=0★／無 → ★讀み手の版で出目が割れる★: 純 PR#20(讀み手 127行)は cwd=束 で rc=0・cwd=repo根 で rc=1(実体無 59)／解いた樹(讀み手 198行)は rc=1(実体無 59・基点=器の在處)(四) |
| ★門の報せ行が偽★ | 純 PR#20 幹の門は BASE 無で「基点=既定(器の在處から導いた repo 根・cwd に依らぬ)」と刷るが、其の隣の讀み手(127行)の既定は ★""(cwd 相対)★ ―― 出目が cwd で割れた事が證(四の二) |
| 生成 3 本 | ★byte 一致★(sha256 553ac4cf…・7368 bytes・cmp rc=0 三對・陽性対照 rc=1)(五) |

## 二 ㋐ 固定の宣

```
main      = 4f591fc021947b9f477b676c96e36a1dc4437500   (git fetch origin main → git rev-parse origin/main)
PR#20 幹  = 0bb92e2b800c1b434c8a660d38f6feea7d450124   (git fetch origin 'refs/pull/20/head:refs/ashigaru-mac-1/km-108/pr20-head' → 己の名前空間へ)
merge-base= 6e9d40600a801aa713ac238e2e62bbae06c9e683   (git merge-base main PR#20幹)
```

- 裁326273 の固定 head 68b6e07ba6ef9c765c29a95f8d42ad6cbedb7328 は PR#20 幹の★祖★(`git merge-base --is-ancestor` rc=0)。幹は其處から 1 commit 進んで居る(0bb92e2b)。★古い head は回して居らぬ★。
- base からの進み: PR#20 幹 18 commit／main 25 commit(raw/25_*_ahead.txt)。
- GitHub の合成 ref refs/pull/20/merge = bf7806a8839d9a4790e9e9b1b24218d855063990(raw/26)は ★見て居らぬ・使つて居らぬ★(家老の言ふ通り親が古い 4be3ee19 ゆゑ、今の幹の絵ではない)。

## 三 ㋑ 衝突の再現(己の手)

捨て worktree(raw/10_wt_path.txt=/Users/momizimac/km108_wt_13337)を `git worktree add --detach <path> 4f591fc0…`(rc=0・raw/10)で出し、`git merge --no-commit --no-ff 0bb92e2b…` を当てた。

| 欄 | 出目 | 控 |
|---|---|---|
| merge rc | ★1★ | raw/12_merge.rc |
| stdout | `CONFLICT (content): Merge conflict in .gitignore` ／ `CONFLICT (add/add): Merge conflict in scripts/checks/karo_mac_manifest_verify.py` ／ `Automatic merge failed` | raw/12_merge.out |
| 衝突 file(全名) | `.gitignore`(UU)／`scripts/checks/karo_mac_manifest_verify.py`(AA) の ★2 本★ | raw/13_unmerged_names.txt・raw/13_status_porcelain.txt |
| index の段 | .gitignore: 1=bf689df1(base) 2=2c809232(HEAD) 3=3f066ffd(PR#20)／verify.py: 2=ebfc4c0e(HEAD) 3=b19ec9ea(PR#20)・★段1 無し=add/add★ | raw/13_ls_files_u.txt |
| hunk 數 | .gitignore ★1★／verify.py ★8★(`<<<<<<<`=`=======`=`>>>>>>>` の三數が各 file で一致・raw/15) | raw/14_conflict_*.txt |
| 衝突せず staged に乗つた物 | A 478(gate.sh・gate4.sh・queue/reports km-39 束・docs/evidence km-46 束 等)／M 1(scripts/inbox_write.sh)／U 2 | raw/44 |

### 三の一 甲 .gitignore ―― hunk 1(衝突 file の 169〜172 行・raw/16)

```
169	<<<<<<< HEAD
170	!scripts/checks/karo_mac_manifest_append.py
171	=======
172	>>>>>>> 0bb92e2b800c1b434c8a660d38f6feea7d450124
```
HEAD 側=1 行(`!scripts/checks/karo_mac_manifest_append.py`)／PR#20 側=★0 行(空)★。前後の文脈(共通): 上に `!scripts/checks/*.sh`、下に `!scripts/checks/karo_mac_manifest_verify.py`(★両側が同じ行を足した故 自動で合はさつた★・raw/30 の三 diff)。
base→main は 2 箇所(+`!scripts/idle_backlog_wake.sh`・+append.py・+verify.py)、base→PR#20 は 1 箇所(+verify.py のみ)。衝突は「同じ verify.py 行の直上に main だけが append.py 行を足した」事で起きた。

### 三の二 乙 karo_mac_manifest_verify.py ―― 8 hunk(逐語は raw/17_verify_hunks.txt・行番号は衝突 file 上)

| hunk | 位置 | HEAD 側 | PR#20 側 |
|---|---|---|---|
| 1 | L15–24 | 7 行(docstring: 書き手への條・裁321127/321257/321353) | ★0 行★ |
| 2 | L52–84 | 25 行(paths_of の r-docstring・`_dequote`・`\r` 剥ぎ・三段 regex ①②③) | 5 行(一行 docstring・`path=(\S+)` 一本・`out.append(m.group(1))`) |
| 3 | L90–93 | 1 行(`t = _dequote(t)`) | ★0 行★ |
| 4 | L104–124 | 16 行(既定基点を ★器の在處から導いた repo 根★ へ・`base_src`) | 2 行(`bases = argv[2:] or ["", "queue/reports/", …]` = ★"" cwd 相対が第一★) |
| 5 | L130–134 | 2 行(`kyuukei = 0`・`kyuu_rows = []`) | ★0 行★ |
| 6 | L140–155 | 13 行(旧形=引用符行を數へて通す・裁321353⑴) | ★0 行★ |
| 7 | L189–206 | 13 行(`cwd`・`基点`・旧形の報せ) | 2 行(一致/相違/実体無/読めぬ行 の一行のみ) |
| 8 | L211–216 | 3 行(実体無の註) | ★0 行★ |

PR#20 側の全 9 行は、HEAD 側では ★置き換へられた旧行★(hunk 2・4・7)であり、HEAD に無い行は ★一つも無い★(raw/33 の diff: PR#20→main で −5 行=其の旧行・+76 行=治し)。

## 四 ㋒ 解の提案

| 本 | 採る側 | 根拠(一行) |
|---|---|---|
| 甲 .gitignore | ★HEAD(main)側★ = blob 2c809232 | PR#20 側は其の位置に行を持たぬ(空)ゆゑ、HEAD を採る=和集合。append.py 行は main の 61a9fe1c(append.py を repo 内へ)が要る行であり落とせぬ。PR#20 が足す gate.sh/gate4.sh は共通の `!scripts/checks/*.sh` で既に通る |
| 乙 verify.py | ★HEAD(main)側★ = blob ebfc4c0e(198 行) | PR#20 の b19ec9ea(127 行)は main が af0dacfc→4be3ee19→61a9fe1c で持つて居た blob と ★同一★(raw/31)。0bb82bfb が之を ebfc4c0e に置き換へた。∴ 198 = 127 + 0bb82bfb の治し(+76/−5・raw/33)で、PR#20 側を採ると ★治しが消える★ |

### 四の一 127 と 198 の差 ―― 實測(raw/33_verify_pr20_to_main.diff・raw/34)

`git diff 0bb92e2b 4f591fc0 -- scripts/checks/karo_mac_manifest_verify.py` = ★1 file・+76/−5★。之は commit 0bb82bfb(「讀み手を直つた版へ揃へ」・軍師mac REVISE PR#22)が verify.py に加へた変更と同じ物(同 commit の stat も verify.py +81 行=76+5・raw/34)。中身:
- ⑴ 頭の docstring に書き手への條(7 行)
- ⑵ `paths_of`: `\r` 剥ぎ・引用符括りを剥ぐ `_dequote`・三段 regex(本形/非貪欲 空白名/従来形)―― ★空白名を切り落さぬ★
- ⑶ 既定基点を `""`(cwd 相対) から ★器の在處から導いた repo 根★ へ ―― ★cwd で出目が変る fail-open を塞ぐ★
- ⑷ 旧形(引用符行)を數へて通す(裁 seq321353⑴)
- ⑸ 報せに `cwd`・`基点`・旧形數・実体無の註
家老の見立て「198 は 127 の治り」は ★實測で一致★(blob の系譜 raw/31・patch-id raw/32: PR#20 の verify 系 2 commit f0d59a3/f2bfa26 は `git cherry` で `-`=既に main に在る)。

### 四の二 解いた後の絵(己の worktree で HEAD 側へ checkout --ours・★git add せず★・raw/45)
.gitignore=2c809232／verify.py=ebfc4c0e／gate.sh=9cd550fc(PR#20 から・衝突無し)。index の U は残る(add せぬ故・raw/45_status_after.txt)。★之は提案の絵であり、merge も commit もして居らぬ。★

## 五 ㋓ 門を PR#20 幹の版(9cd550fc・310 行)で走らせる

門の版: driver/karo_mac_dasumae_gate.pr20.sh = `git show 0bb92e2b:scripts/checks/karo_mac_dasumae_gate.sh` の写し(sha256 e11f0d01…・blob 9cd550fc・310 行・`KM_GATE_MANIFEST_BASE` の字面 4・raw/23・raw/24)。★走らせたのは写しではなく捨て worktree 内の本物★(`$(dirname "$0")/karo_mac_manifest_verify.py` で隣の讀み手を呼ぶ故・raw/40)。自己検め=通(raw/50・rc=0)。
臺帳=manifest_jou1.txt(束内相対・`cd <束>` → append.py・59 行・raw/59 が argv)。走らせ器=driver/60_gate_runs.sh。控=mon_<HHMMSS>_<札>.log/.err/.rc(★臺帳へ入れぬ★)。

| 札 | 門 | 隣の讀み手 | cwd | BASE | 條① の出目(逐語は 控) | gate rc |
|---|---|---|---|---|---|---|
| pure_base | 純 PR#20 幹(WT2) | b19ec9ea/127 | 束 | `.` 有 | `條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)` → 一致 ★59★/相違 0/実体無 0/読めぬ 0 | ★0★ |
| pure_nobase | 同 | 同 | 束 | 無 | `條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ)` と刷るが → 一致 59(★cwd 相対で当たつた故★) | 0 |
| pure_nobase_root | 同 | 同 | ★repo 根★ | 無 | 同じ報せ行 → 一致 ★0★/実体無 ★59★ | ★1★ |
| merged_base | 解いた樹(WT) | ebfc4c0e/198 | 束 | `.` 有 | `基点 引数(明示)` → 一致 ★59★/0/0/0・旧形 0 | ★0★ |
| merged_nobase | 同 | 同 | 束 | 無 | `基点 既定(器の在處から導いた repo 根 /Users/momizimac/km108_wt_13337 ―― cwd に依らぬ)` → 一致 0/実体無 ★59★ | ★1★ |

- ★BASE を解する事の證は出目★: 有=「基点=引数 明示」と刷り 一致 59・無=「既定」と刷る。grep の 4 は字面、之は挙動。
- ★四の二 門の報せ行が偽(純 PR#20 幹)★: 門(9cd550fc)は BASE 無の時「既定(器の在處から導いた repo 根・cwd に依らぬ)」と刷る(裁322952 乙で据ゑた行)。然し PR#20 幹の隣の讀み手は 127 行で、其の既定は `""`(cwd 相対)である(hunk 4 の PR#20 側)。∴ ★cwd=束 で通り(rc=0)・cwd=repo 根 で落ちた(rc=1)★ ―― 報せ行の言ふ「cwd に依らぬ」は ★成り立つて居らぬ★。門は治つた讀み手を前提に書かれ、PR#20 は治る前の讀み手を運んで居る。HEAD 側の讀み手(198)と組んだ merged_nobase では 基点=器の在處 と刷り ★言ふ通りに cwd に依らず★ 束内相対の臺帳が実体無 59 で落ちる(=束内相対の臺帳は BASE=. 無しでは落ちる・期待通り)。
- 純 PR#20 の nobase rc=0 は「通つた」ではなく ★fail-open の実演★(裁 307874⑴ が塞いだ物)。之が 乙 で HEAD 側を採る第二の根拠である。

## 六 ㋔ 生成 3 本(裁326273)

同じ argv(raw/59・59 本)で append.py を三度、gen3/manifest_gen{1,2,3}.txt へ生成(1 秒隔て・mtime 17:17:06/07/08)。

| 對 | cmp rc |
|---|---|
| gen1 ⇔ gen2 | 0 |
| gen2 ⇔ gen3 | 0 |
| gen1 ⇔ gen3 | 0 |
| gen1 ⇔ manifest_jou1.txt(門に掛けた臺帳) | 0 |
| 陽性対照(`x` ⇔ gen1) | ★1★(cmp は違ふ物には鳴る) |

三本とも sha256=553ac4cf460ee12e6600370d5bd558e321b5051ef049a7c900f8ed0a46010fd8・7368 bytes・61 行(gen3/70_cmp_result.txt)。★食ひ違ひ無し★。
註: 之は raw/+driver/ の 59 本に對する三本。本紙(00_shodan.md)と manifest_jou1・gen3/ を含む ★最終臺帳 manifest.txt★ は其の後に一度建て、其の三本 cmp は 99_katazuke.txt(臺帳外の控)に置く ―― ★紙は己を含む臺帳の數を書けぬ★。

## 七 ㋕ 數が意味せぬ事

- 「衝突 2 本」は「PR#20 が悪い」の意ではない。乙は ★両側が同じ path を各々 add した★ 事の帰結であり、PR#20 が先に着地して居れば add/add は ★同一 blob(b19ec9ea) の add/add★ で git が黙つて合はせ、次の PR#22 が modify として乗つた。★順序の帰結★である。
- 「一致 59/59」は「PR#20 の門が正しい」の意ではない。pure_nobase の 59 は cwd が偶々 束であつたから出た數で、cwd を repo 根へ移せば同じ門・同じ臺帳で 0 になる(四の二)。★數は cwd を伴はねば讀めぬ★。
- 「198 行 > 127 行」は「多い方が良い」の意ではない。良いのは行數ではなく、raw/33 の +76 が裁 307874⑴⑵・321353⑴ の治しである事(四の一)。
- 「+76/−5」は「PR#20 側の 5 行が失はれる」の意ではない。−5 は置き換へられた旧行で、其の意味は +76 の中に含まれる。
- 「生成 3 本 byte 一致」は「臺帳が正しい」の意ではない。書き手が決定的である事だけを言ふ(同じ入力→同じ出力)。中身の正しさは門の條①(disk との照合)が別に言ふ。
- 「捨て worktree で rc=1」は「GitHub でも merge 不可」の意と ★同じではない★ ―― GitHub の合成 ref は古い親(4be3ee19)の絵であり、今の幹へ当てた出目が本件の問ひである(家老の前提の通り)。

## 八 ㋖ 臺帳・門・片付け

- 臺帳=`manifest.txt`(束内相対・`cd <束>` → `scripts/checks/karo_mac_manifest_append.py` のみで建てる)。門=`KM_GATE_MANIFEST_BASE=. bash <門> manifest.txt <臺帳の path 列>` を ⑴repo 作業樹の門 ⑵純 PR#20 幹の門 の二つで走らせる。控=`mon_<HHMMSS>_<札>.log/.err/.rc`(走る毎に別名・臺帳へ入れぬ)。門の最終出目は ★控を見よ★。
- 己が作つた worktree 二つ(raw/10_wt_path.txt・raw/10_wt2_path.txt)は最終の門の後に `git worktree remove --force` で片付け、其の控を 99_katazuke.txt(臺帳外)へ置く。他席の worktree(/private/tmp/gunshi-km49.*・.claude/worktrees/karo-mac-a1)には ★一指も触れて居らぬ★(git worktree list の写しが 99 に在る)。
- 己の一時 ref `refs/ashigaru-mac-1/km-108/pr20-head` は ★残す★(再走の固定の爲・己の名前空間・他の ref は書換へて居らぬ)。
- 正規化: 0 byte の控 2 本(raw/12_merge.err・raw/50_…out)は條④の爲 一行にした。diff 4 本と raw/17 は driver/K.py(seikei)を通した爲、★unified diff の空白文脈行の一空白と、空行の末尾 tab が剥がれて居る★(`git apply` には使へぬ・讀む爲の写し)。git show の写し(raw/20・21・driver/…pr20.sh)は byte の儘。
- 己の測り誤り(記す): 最初の `git show $MAIN:scripts/…` は zsh の `:s` 修飾に食はれ 0 byte を出した(raw/23 を一度誤つた・`${MAIN}:` で取り直した)。cmp の對も `set -- $pair` が zsh で割れず一度空振りした(取り直して gen3/70)。
