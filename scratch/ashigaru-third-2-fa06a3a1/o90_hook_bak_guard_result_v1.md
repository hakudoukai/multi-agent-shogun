# order90 後半: 門を当て・repo へ置き・鳴りを実測した（前紙 o90_..._v1 は不触）

as_of 2026-09-08 07:5x JST / 席 ashigaru-third-2 / 令 order90（総監督 GO・案文 C 可）
前紙 `o90_hook_bak_guard_v1.md`（87 行・`5998b25176652092`）は ★一字も書き換へて居らぬ★（本紙で続ける）
樹 `/home/hakudoukai/a2/wt-hook-guard`（枝 `a2/hook-bak-guard-20260908`・`1fd60d4f9994` 起点・家老が張つた）
数: 1 = file 1 本／行 1 本。走 = ★1 回★（§4 の鳴り実測）。push = ★1 回★。

## §1 当てた（本物の退避 hook）
`/mnt/c/DentalBI/.git/hooks/pre-push.bak-loadshed-20260907`

| 項 | 当てる前 | 当てた後 |
|---|---|---|
| byte | 2744 | ★3384★ |
| 行 | 61 | ★71★（+10・削除 0） |
| CRLF | 0 | ★0★ |
| sha16 | ★`6284d288f4f4e21d`★ | ★`42306954c91b822b`★ |
| mode | 0o777 | ★0o777（保存した）★ |

★現用 `/mnt/c/DentalBI/.git/hooks/pre-push` は 当てる前も後も `e4a47593600691e3`（3399 byte・70 行）＝★一指も触れて居らぬ★★。

## §2 ★可逆の実証（GO の条件）★
`git show 4b1f7d293:scripts/git-hooks/pre-push` を byte で数へた:
★2744 byte・61 行・sha16 `6284d288f4f4e21d`★ ―― ★§1 の「当てる前」と完全に同値★。

★∴ 戻す道は現に在り、戻した先が元と同じ物である事を 数で言へる。★

## §3 repo へ置いた（令の 2 条目）
| 項 | 値 |
|---|---|
| path | `scripts/git-hooks/pre-push.bak-guard` |
| commit | ★`c36b9556f`★（`71 insertions(+)`・`1 file changed`・★製品 code の変更 0★） |
| push | `origin/a2/hook-bak-guard-20260908` = ★`c36b9556f0b4138160c91406d9485c66cb446927`★（rc=0・force 無し） |
| 中身 | 樹側で数へて 3384 byte・71 行・CRLF 0・sha16 `42306954c91b822b`（★当てた物と同値★） |

★前紙 v1 §4-2 の未測が埋まつた★: 樹で `git check-attr text eol` を打つと
`scripts/git-hooks/pre-push.bak-guard: text: set` / `eol: lf` ―― ★`.gitattributes` :7 が現に当たつて居る★。

## §4 ★鳴りの実測（令の 4 条目）★ ―― ★現用に触れぬ道を採つた（開示）★
家老より「★『現用 pre-push に触れる』許しは家老の一存では出せぬ ∴ 総監督へ請ふ・許し無き間は当てるのみ★」を受けた。
∴ ★現用を退避して戻す形は 打たなんだ★。代りに ★当てた退避 hook の中身 其の物★ を二つの名で写し、走らせた。
写しの sha16 は両名とも `42306954c91b822b`（★当てた物と 1 byte も違はぬ★）。cwd = `/home/hakudoukai/multi-agent-shogun`。

| 走らせた名 | rc | 出た物（器の言葉・逐語） |
|---|---|---|
| ★`pre-push`★ | ★1★ | `[pre-push] BLOCKED: 之は止血前の退避版である（総監督 2026-09-07・dev_qa#822）。`<br>`[pre-push]   正規の hook を戻すには: bash scripts/git-hooks/install.sh` |
| `pre-push.bak-loadshed-20260907` | 0 | `[pre-push] sync script not found: /home/hakudoukai/multi-agent-shogun/scripts/sync_source_cache.py` |

★陽性＝門は現に鳴り、rc=1 で止める。陰性＝名が違へば門を素通りする。★

★安全を二重に固めてから走らせた（讀取で先に確かめた）★:
1. 門が鳴れば L11 の `exit 1` で本体へ行かぬ。
2. 鳴らずとも、hook の L15-18 が `SYNC_SCRIPT` の不在で `exit 0` する。
   cwd の repo（multi-agent-shogun）に `scripts/sync_source_cache.py` は ★無い★ と讀取で確かめた。
★陰性の行に出た `sync script not found` は、其の 2 段目が現に効いた事の証である（DB へは行かなんだ）。★

走の前・走の了り いづれでも本物 2 file の sha16 を測つた: 退避 `42306954c91b822b` → ★不変★／現用 `e4a47593600691e3` → ★不変★。

## §5 ★依然 未測（伸ばして書かぬ）★
1. ★git が push の時に呼ぶ経路での鳴り★ ―― 本紙 §4 は ★当席が bash で直に走らせた★ 物であり、
   ★git が hook として呼んだ物では無い★。之を測るには現用 `pre-push` に触れる要が在り、★総監督の許し待ち★。
   （o88 の「本物での鳴りは未測」は ★中身と名に関しては埋まつたが、呼び手が git である経路は 未だ埋まつて居らぬ★。）
2. `install.sh` を走らせた後に `.git/hooks/pre-push.bak-guard` が現に増えるか ―― ★走らせて居らぬ★（前紙 v1 §3 は讀取からの見極め）。
3. 他 PC（main/second/mac）の退避 hook ―― ★触れて居らぬ・測つて居らぬ（令の禁）★。

## §6 器の言葉（当席の判定語では無い）
- pre-commit hook: `Supabase secret scan PASS: no tracked secret values detected.`
- pre-push hook（現用・止血版）: `[dup-check] PASS: 新規path 1件を検査、二重実装0件`
- 同上: `[pre-push] source_code_cache sync SKIPPED (DB負荷止血 2026-09-07・main は CI が同期・強制は SYNC_SOURCE_CACHE_FORCE=1)`
★三行とも hook が刷つた物であり、消さずに残す。三行目は ★止血が現に効いて居る★ 事を押した瞬間に示して居る。★

## §7 境界と開示
走 1 回（§4）／push 1 回（名指しの refspec `a2/hook-bak-guard-20260908`・★force 無し★）／commit 1 本（製品 0）／
★共有 `.git` への書込は 退避 hook 1 本のみ★（総監督 GO で解かれた一点。fetch/pull/clone/prune 0）／
★現用 `.git/hooks/pre-push` は一指も触れて居らぬ★／★main/second/mac 不触★／
DB 讀 0・書 0・SQL 0 本／CI 走行 0／製品 code 書込 0／
D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触／Commander の箱 0 打／他席 inbox 直接書込 0。

★家老の問ひへの答: `wt-guard-evidence` に当席の用は ★無い★。★
（汚れ 0＝`git status --porcelain` 出力 0 行／HEAD `d84ede4ee` が `origin/main` に含まれる＝merge 済／当席が触る物は残つて居らぬ。）

## §8 追補（order91・総監督の裁 2026-09-08 08:00 家老経由・★上の §5-1 は消さず 此処へ併記する★）

★本物での鳴り＝未測。隔離の同 sha `42306954c91b822b` が鳴る。★
（本紙 §4 の實測 ―― 名が `pre-push` の時 rc=1 で `BLOCKED` の行を刷り、
　名が `pre-push.bak-loadshed-20260907` の時 rc=0 で素通る。中身は現用の退避と 1 byte も違はぬ写しである。）

### §8-1 ★何故 本物で測らぬか（一語）★
★測り忘れでは無い。★ 現用 `pre-push` の在る樹は 総監督が ★毎分 push に使ふ樹★ である ∴
退避して戻す其の窓の間 ★他人の push が止まる★。★測れぬのでは無く、「測らぬ」と決めた。★

- 裁の逐語（家老経由）: 「★否は『駄目』でなく『此の道は他人の仕事を止める』の意★」。
- ∴ 本件は ★此処で閉ぢる★。閉ぢ方 ＝ ★隔離の同 sha の鳴り（§4）を以て代へる★。

### §8-2 次の者へ（★「測り忘れ」と読ませぬ為の書き置き★）
1. §5-1 の「総監督の許し待ち」は ★08:00 の裁を以て 待ちでは無くなつた★。前の行は残して在る（当席は書き換へぬ）。
2. 再び測らうとする者は ★先づ「其の樹が 毎分 push に使はれて居るか」を確かめよ★ ―― 樹が変れば前提も変る。
3. 他人の push を止めずに測る道は在る（★当席は打つて居らぬ★）:
   毎分 push の掛からぬ ★別の樹★ に同じ二本を置き、其処で git に呼ばせる。
   ★但し §4 と同じく「本物の樹では無い」事は残る。★
4. ∴ 本紙で言へるのは ★「中身と名に依る鳴りは測つた」★ までであり、
   ★「本物の樹で git が呼ぶ経路」は 測つて居らぬ★ ―― 之は ★意図して残した空白★ である。

### §8-3 本追補の境界
走 0・DB 0・SQL 0・push 0・commit 0・fetch 0／★現用 `pre-push` 不触（触れぬ事が本追補の主題である）★／
★本紙 §1〜§7 の 79 行は 一字も書き換へて居らぬ（併記のみ）★／main/second/mac 不触。

## §9 追補其の二（order92・2026-09-08 08:1x・★§8-2⑶ を消さず 此処で訂正する★）

★結論 ＝ §8-2⑶ の「別の樹」が ★worktree★ を指すなら ★成り立たぬ★。★

### §9-1 測つた物（★讀取のみ・走 0★／`<共有>` ＝ 製品 repo の root）
| 訊いた事 | 出た値 |
|---|---|
| 樹の `.git` | ★file★（dir に非ず）・中身 `gitdir: <共有>/.git/worktrees/wt-hook-guard` |
| `git rev-parse --git-dir` | `<共有>/.git/worktrees/wt-hook-guard`（★樹ごとに別★） |
| `git rev-parse --git-common-dir` | `<共有>/.git`（★共通★） |
| ★`git rev-parse --git-path hooks`★ | ★`<共有>/.git/hooks`★ ―― ★樹の中から訊いても 共有を指す★ |
| `core.hooksPath` | ★未設定★ |
| per-worktree git-dir の直下 | ★hooks dir は 無い★（COMMIT_EDITMSG・HEAD・ORIG_HEAD・commondir・gitdir・index・locked・logs の ★8 名のみ★） |
| 樹から見える `pre-push` | 3,399 byte・70 行・sha16 `e4a47593600691e3` ＝ ★現用 其の物★ |
| 樹から見える退避 | 3,384 byte・71 行・sha16 `42306954c91b822b` ＝ ★当てた門付き版 其の物★ |

数: 1 ＝ file 1 本／8 名は `ls -la` の出力から `.`・`..` を除いた数。

### §9-2 ★何故 成り立たぬか（一語）★
★hooks は per-worktree では無く common dir に在る★ ∴ 樹を幾つ張つても ★見る hooks は同じ 1 つ★ である。
かつ git が呼ぶのは ★`pre-push` といふ名の file だけ★ ゆゑ、門を git に呼ばせるには ★名を変へる ＝ 現用を退避する★ 要が在り、
之は 08:00 の裁が ★否★ と定めた 其の道へ戻る。∴ ★worktree は迂回に成らぬ。★

★向きも書いて置く★: 当席は §8-2⑶ を「★他人の push を止めぬ道★」として書いた。
併し worktree で試せば ―― 止めぬ所か ★現用を退避する其の窓が 現に開く★。★前紙の見立ては 逆であつた。★

### §9-3 ★何処までなら成り立つか（3 段に分ける）★
1. ★別 clone ／ 別 repo★（common dir が別）＝ ★成り立つ筈★。
   根 ＝ hooks の在処は `--git-common-dir`/hooks（§9-1 の實測）∴ common dir が別なら hooks も別。
   ★但し 当席は clone を打つて居らぬ ∴ 之は 確かめて居らぬ。★
2. ★`core.hooksPath` を per-worktree config へ置く★ ＝ ★形は在る★。
   根 ＝ `extensions.worktreeConfig` が現に `true`（實測）。★但し 当席の樹に `config.worktree` は 無い★。
   ★かつ 之を置くには 共有 `.git/worktrees/…/config.worktree` へ ★書く★ 要が在り、
   当席の床（共有 `.git` への書込は 退避 hook 1 本の GO のみ）に触れる ∴ ★打たぬ。★
3. ★同じ樹で名を変へる★ ＝ ★禁じられた道 其の物★（§9-2）。

### §9-4 ★§8-2⑶ の訂正（元の行は消して居らぬ）★
§8-2⑶ 逐語: 「毎分 push の掛からぬ ★別の樹★ に同じ二本を置き、其処で git に呼ばせる。」
★訂正★: 「別の樹」を ★worktree の意で読むな★ ―― 本 lot で当席は「樹を張つた」を ★worktree の意で★ 使つて来た
∴ ★後の者は worktree と読む★（之が §8 を書いた時の当席の落ちである）。
成り立つのは ★別 clone ／ 別 repo★ の時のみであり、其れすら ★当席は確かめて居らぬ★（§9-3-1）。

### §9-5 境界
走 0・push 0・commit 0・DB 0・SQL 0・fetch/clone 0／★共有 `.git` への書込 0★／
★本物 hook 不触（讀取のみ）★ ―― 08:1x の sha16 は 現用 `e4a47593600691e3`・退避 `42306954c91b822b` ＝ lot 終りの當て直しと同値／
main/second/mac 不触／★§1〜§8 の 105 行は 一字も書き換へて居らぬ（併記のみ）★。

## §10 追補其の三（order93・2026-09-08 08:2x・★§9-3-1 の「確かめて居らぬ」の札を外す★）

★答 ＝ 別 clone なら hooks も別。★ ∴ ★§9-3-1 の札は 外せる（但し §10-4 の限りで）。★

### §10-1 場（★隔離のみ・network 0・本物不触★）
規 `o93_clone_hooks_probe.py`（3,541 byte・74 行・sha16 `fcadd0f67873d242`）。
`git init --bare` で remote 役を作り local path から clone する ∴ ★network を通らぬ★。
- `bare.git` ＝ remote 役
- `X` ＝ 作業 clone。★X の `.git/hooks/pre-push` に門を置く★（中身 ＝ `echo "X-GATE fired"; exit 1`）
- `W` ＝ X から張つた ★worktree★（＝陰性対照・共有する筈の側）
- `Y` ＝ bare から取つた ★別 clone★（＝陽性・別である筈の側）

★語の定め★: 「陽性」＝ ★hooks が別である事が現れる★ 側（Y）／「陰性対照」＝ ★共有ゆゑ X の門が鳴る★ 側（W）。

### §10-2 對の實測
| 訊いた事 | worktree W（陰性対照） | 別 clone Y（陽性） |
|---|---|---|
| `git push` の rc | ★1★ | ★0★ |
| X の門の行 `X-GATE fired` | ★出た★ | ★出ぬ★ |
| 己の `.git/hooks/pre-push` | （共有ゆゑ X の物を見る） | ★無い★ |
| hooks dir の中身 | （X と同じ 1 つ） | ★`.sample` が 14 本のみ★ |
| hooks の realpath | ★X と同一★ | ★X と別★ |

数: 14 ＝ `Y/.git/hooks` 直下の file 数（`.sample` ばかりで ★門は 0 本★）。1 ＝ file 1 本。

∴ ★別 clone は 門を引き継がぬ★ ―― clone は ★履歴を写すが hooks を写さぬ★（Y の hooks は template から作られ `.sample` のみ）。

### §10-3 ★己の規の落ち（開示）★
初手の規は `--git-path hooks` の出力を ★其の儘 文字列で比べた★。
併し `--git-path` は ★cwd 相対で返す事が在る★ ―― X も Y も 己の root に居るゆゑ ★双方 `.git/hooks` と返した★。
∴ 初手の値は ★`hooks_same_X_W=False`・`hooks_same_X_Y=True`★ ―― ★真逆★ であつた。
直し ＝ `--path-format=absolute` と `realpath` の ★二法で★ 取り直し、★X==W が True・X==Y が False★ を得た。

★併し 鳴りの實測（W で鳴り Y で鳴らぬ）は 初手から正しかつた。★ ∴
★物差しが二つ食ひ違つた時、当たつて居たのは ★現に走らせた方★ であり、外れたのは ★文字列を比べた方★ である。★
（前紙 §9-1 の `--git-path hooks` の値は ★樹の中で取つた物ゆゑ 元から絶対 path で返つて居り★、此の落ちに当たつて居らぬ。）

### §10-4 ★札の始末（何処まで外せるか）★
§9-3-1 の「★但し 当席は clone を打つて居らぬ ∴ 之は 確かめて居らぬ。★」は 本節を以て ★外す★。
★但し 外せるのは 隔離での話に限る。★ ―― 本物の repo で別 clone を作つては居らぬ（床 ＝ clone 0・network 0）。
∴ 言へるのは ★「別 clone なら hooks は別」を 隔離で確かめた★ までであり、
★本物で其の道を敷いた訳では無い★（敷けば 製品 repo の写しが 1 つ増える ―― 之は当席の裁量の外）。

### §10-5 境界
走 ★1★（§10-1 の規・隔離のみ）／追測 ★1★（§10-3 の取り直し・場は作り直して居らぬ・`git rev-parse` 3 回）／
network 0（local path のみ）・DB 0・SQL 0・push は ★隔離の bare へ 3 回のみ★（本物の remote 0）／
★本物 repo 不触・共有 `.git` 書込 0・本物 hook 不触★／main/second/mac 不触／
★§1〜§9 の 152 行は 一字も書き換へて居らぬ（併記のみ）★。

---

## §11 order94 ―― `update-index --refresh` が ` M` を消さぬ因（走 2・隔離のみ・本物不触）

as_of 2026-09-08 08:3x JST / 令 `msg_20260908_082711_c752b922`（B を採る・走 1 を許す）
規 = `scratch/ashigaru-third-2-fa06a3a1/o94_refresh_probe.py`（4,830 byte・114 行・sha16 `ef2515027f5c0af3`）
場 = `scratch/ashigaru-third-2-fa06a3a1/o94_lab/`（`git init` の空 repo 3 つ・remote 無・network 0）
數: ★1 = repo 1 つ★／★1 = ケース 1 つ★／組 = repo×ケース = ★9★。byte は file の byte・index size は `git ls-files --debug` の `size:` 行。

### §11-1 剥がした元素と、その對（令の「一つづつ」）

| 元素 | 剥がし方 | 出た値 |
|---|---|---|
| **属性** | P=`autocrlf=input`+`* text eol=lf` / Q=`input`+属性無 | ★P と Q は全数同値★ ∴ `.gitattributes` の有無は因では無い |
| **autocrlf** | Q=`input` / R=`false` | ★分かれた★（下 §11-3） |
| **size** | 作業樹 41→37 byte に変へた（`sed -i 's/\r$//'`） | index size は ★41 の儘★（refresh の後も 41） |
| **mtime だけ** | `os.utime(f,(0,0))`（中身不変） | status は ★空★（` M` が立たぬ）∴ mtime 単独では M に成らぬ |
| **真の内容差** | `echo two` → `echo TWO` | index size 37→★0★・hash が別値 `a291c80915f3` ∴ 別の因 |

### §11-2 ★因の名指し★（追測 1・P と Q の同じ場で）

| 打つた器 | rc | 出力 | 後の status | 後の index size |
|---|---|---|---|---|
| `git update-index --refresh` | ★1★ | `crlf.sh: needs update` | ` M crlf.sh` | 41 |
| `git update-index --really-refresh` | ★1★ | `crlf.sh: needs update` | ` M crlf.sh` | 41 |
| `git status --porcelain` ×2 | 0 | ` M crlf.sh`（2 回とも） | ` M crlf.sh` | 41 |
| **`git diff --quiet crlf.sh`** | ★0★ | （無） | ―― | 41 |
| **`git add crlf.sh`** | 0 | （無） | ★空★ | ★37★ |

`git add` の前後で index blob は `780901177b82` → `780901177b82` ＝ ★不変★。

> ★因 ―― `git update-index --refresh` は index の stat が作業樹と食ひ違ふ事を ★報せる★ 器であり、
> 内容が同じ事を確かめて stat を ★書き直す★ 器ではない。`--really-refresh` でも同じであつた。★
>
> 其の場で `git diff --quiet` が ★rc=0★（内容差 0）を返し、`git add` が blob を ★変へずに★ index size を
> 41→37 に書き直して ` M` を消した ―― ∴ ★書き直す器は `git add` である★。

∴ ` M` の正体は「★内容の差★」では無く「★index に載つた stat（size 41）が作業樹（37）と合はぬ★」事であつた。
そして `status` は其の stat 差を ` M` と刷り、`refresh` は其れを ★報せるだけ★ ゆゑ、何度打つても消えぬ。

### §11-3 ★同じ ` M` に二種在る★（R が分けた）

| repo | index blob | `hash-object`（filter 有） | 読み |
|---|---|---|---|
| P・Q（`autocrlf=input`） | `780901177b82` | `780901177b82` ＝★一致★ | ★stat だけの差★（内容は同じ）―― `git add` で blob 不変の儘 消える |
| R（`autocrlf=false`） | `6a8b2bfa8a99` | `780901177b82` ＝★食ひ違ふ★ | ★真に内容が違ふ★ ―― CRLF が index に載つて居る |

∴ ` M` を見た者は ★先づ index blob と `hash-object` を突き合はせよ★。
同じ見た目でも、前者は `git add` で消え（履歴に差は入らぬ）、後者は `git add` すれば ★履歴に差が入る★。

### §11-4 ★己の規の落ち（開示・二件）★

⑴ ★`ls-files --debug` の `ino` を全ケースで `None` としか取れて居らぬ★ ―― 当席の parse が `ino:` 行を拾へて居らぬ。
   ∴ 本 §11 で ★inode を根拠にした断りは一つも書いて居らぬ★（size と rc と blob だけで組んだ）。
⑵ ★同じ repo を 3 ケースで使ひ回した★ ∴ ケース②③ の refresh 出力に、ケース① で汚した `crlf.sh: needs update` が
   混ざつて居る（追測 1 でも `real.sh: needs update` が併記されて出た）。
   ―― 出力の ★行の混入★ であり、各ケースの status・index size・blob は file ごとに取つて居るゆゑ ★値は分かれて居る★。
   併し「refresh の出力行数」を数へる用には ★此の場は使へぬ★。次に測る者は ★ケース毎に repo を作れ★。

### §11-5 ★o89 §6 の「言へぬ」の札 ―― ★外せる★★

o89 §6 に当席は「`update-index --refresh` を打つても ` M` が消えぬ因は ★言へぬ★」と書いた。
本走で ★外せる★。答＝ ★`--refresh` は報せる器であり、書き直す器では無い。書き直すのは `git add`。★

★但し 外せるのは 隔離での話に限る。★ 本物の `/mnt/c/DentalBI` で同じ形が起きて居るか否かは ★確かめて居らぬ★
（本物の作業樹は CRLF・index は LF といふ既知の形が在る ∴ ★R の側（真の内容差）である見込み★ ―― 見込みであつて實測では無い）。

### §11-6 境界

走 2（o94 規 1・追測 1）／全て `scratch/…/o94_lab/` の `git init` 空 repo・★network 0★・remote 0・push 0。
現用 `/mnt/c/DentalBI/.git/hooks/pre-push` = `e4a47593600691e3` ★不触★（走の前後で讀取のみ）。
共有 `.git` 書込 0／main・second・mac 不触／DB 讀 0 書 0・SQL 0／本物 CI 0／製品 code 書込 0／D 樹不触。
禁語走査（網 = `PASS|合格|充足|解消|緑` / `推奨|良い` / `後で|次サイクル|明日|一旦|一区切り`・範囲 = 本 §11 の行のみ）= ★0★。

### §11-7 ★§11-6 の「禁語 = 0」の訂正（前行は消さず併記）★

§11-6 の末尾に「禁語走査 … = ★0★」と書いた。★之は誤りである。★
書いた ★後に★ 現に打つたら ★3 件★ 当たつた。内訳（範囲 = §11 の行のみ・網は §11-6 と同一）:

| 当たつた行 | 語 | 読み |
|---|---|---|
| 「`git add` の前後で index blob は …」 | `後で` | ★偽陽性★ ―― 「★前後で★」＝ before/after であり先送りでは無い |
| 「現用 … `e4a47593600691e3` ★不触★（走の前後で讀取のみ）」 | `後で` | ★偽陽性★ ―― 同上 |
| §11-6 の網を書いた行その物 | 網の全語 | ★偽陽性★ ―― ★網の文字列を本文に書いた ゆゑ 己に当たつた★（自己言及） |

∴ ★真の禁語 = 0★・★網の当たり = 3★・★偽陽性 = 3★。數: 1 = 行 1 本。

★己の落ち（其の三・開示）★:
⑴ ★「0」を、走らせる前に書いた。★ 走らせたのは書いた後である ―― ∴ 其れは ★見込み★ であつたのに
   ★實測の顔で書いた★。四条④「見込みは見込みと書け」に反する。
   （o89・§10 で当席は「走らせた方が当たつて居た」と己で書いた ―― ★同じ穴に逆から落ちた★。）
⑵ ★網が粗い★: `後で` は「前後で」に当たる。`grep -E` に lookbehind は無い ∴ 次に測る者は
   ★網から `前後` を先に除いてから当てる★（例: `grep -v '前後' で濾してから当てる`）か、`grep -P` を使へ。
⑶ ★網を本文に書くと己に当たる★ ∴ ★網を書いた行を範囲から外す★ 事。

★物差しは動かして居らぬ★（網も範囲も §11-6 と同一）。変つたのは ★打つたか否か★ だけである。

---

## §12 order100（L）―― `install.sh` を隔離樹で走らせ、★己の見立て二つ★ を対で測る

as_of 2026-09-08 09:4x JST / 令 `msg_20260908_093812_0294f241`（走 1）＋ `msg_20260908_094139_…`（走 1 追加）
器 `o100_install_probe.py`（90 行・`bceec6eab33a49a5`・sha256:16）／隔離樹 `scratch/…/o100_tree_<epoch>_<pid>/{pos_guard_有,neg_guard_無}`
★本物の樹 `/mnt/c/DentalBI` は copy 元として讀んだのみ ―― 書込 0・現用 hook 不触。★
數: 1 ＝ file 1 本 / process 1 本。

### §12-0 ★走の数（開示）★

★走 2★。内訳 ―― ★走① ＝ 値 0★（byte literal に非 ASCII を入れて構文で落ちた。`4a0ab8f7813aa852`）／
★走② ＝ 値を得た★（直しは 2 箇所のみ・`bceec6eab33a49a5`・★対三組も判定も不変★）。
★値を得られぬ走も 1 と数へる★ ―― 09:04 に立てた物差しから ★二度目も同じ所で引いた★。
器の中の `git init` / `bash install.sh` の呼出は ★走に数へぬ★（`o98` と同じ数へ方）。

### §12-1 ★対① ―― 見立て①（src に置けば配られる）は ★当たつた★★

| 腕 | src に `pre-push.bak-guard` | `.git/hooks` に増えたか |
|---|---|---|
| 陽性 | ★有★ | ★増えた★（`pre-push.bak-guard`） |
| 陰性 | ★無★ | ★増えぬ★ |

∴ ★増えたのは install.sh に由る★（元から在つた物でも、樹を作つた事に由る物でもない）―― 対を置いたゆゑ言へる。
`install.sh` の stdout も其の儘: 陽性 `installed: lf-only-probe | pre-push | pre-push.bak-guard` / 陰性 `installed: lf-only-probe | pre-push`。
★mode★: 配られた三本は悉く `0o664 → 0o775`（`chmod +x` が現に当たつて居る）。

### §12-2 ★対② ―― 見立て②（src に無い名は消えぬ）も ★当たつた★★

`.git/hooks` に先に二本置いてから走らせた。

| 先に置いた名 | src に在るか | install 後 | sha | mode |
|---|---|---|---|---|
| `pre-push` | ★在る★ | ★上書きされた★ | 変つた | `0o664 → 0o775` |
| `pre-push.bak-loadshed-20260907` | ★無い★ | ★残つた★ | ★不変★ | ★`0o664` の儘★ |

★両腕（陽性・陰性）とも同じ★。∴ ★当てた門は install.sh を走らせても消えぬ・書き換はらぬ・mode も触られぬ★。
（o90 §3 見立て② は「上書きされぬ・消されぬ」迄しか言つて居らなんだ ―― ★mode も触られぬ★ は本走で足した。）

### §12-3 ★対③ ―― `install.sh` L17 の `sed -i` は ★src を書き換へる★（CRLF が在る時のみ）★

| src | 中身 | install 後 sha |
|---|---|---|
| `pre-push.bak-guard`（CRLF を入れて置いた） | CRLF 有 | ★変つた★ `0b5df33787557e98 → 42306954c91b822b` |
| `lf-only-probe` | LF のみ | ★不変★ |
| `install.sh` 自身 | LF のみ | ★不変★（己は除外されるが `sed` の前に `continue` する形ゆゑ二重に不変） |
| `pre-push`（本物の copy） | LF のみ | ★不変★ `e4a47593600691e3`（＝現用 hook と同じ digest） |

★併せて出た事★: CRLF を除いた後の値 `42306954c91b822b` は ―― ★o90 §2 で当席が repo へ置いた門付き版の digest と同じ★ である。
∴ ★`sed -i` は CRLF 版を LF 版へ ★戻した★★（別物へ変へたのではない）。

★之が意味する事（害の形）★: `install.sh` は ★配る前に src を書き換へる★ ゆゑ、
★本物の樹で走らせれば 共有樹の `scripts/git-hooks/*` に手が入る★（CRLF が在る時）。
∴ ★本走を隔離樹で行つた事は 迂回ではなく 必要であつた★。
（★但し「本物で走らせたら何が起きるか」は ★測つて居らぬ★ ―― 令の禁ゆゑ。★三つの外★ に置く。）

### §12-4 ★見立ての当否（一覧）★

| # | 己の見立て（o90 §3・讀取から） | 実測 |
|---|---|---|
| ① | src に置けば `.git/hooks` へ配られ file が 1 本増える | ★当たつた★ |
| ①' | 害は無い（`.bak-guard` の名では git は呼ばぬ） | ★本走では測つて居らぬ★（o88 で「.bak 名は鳴らぬ」を隔離で実測済・本走は ★配られるか★ のみ）|
| ② | 当てた門（src に無い名）は上書きされぬ・消されぬ | ★当たつた★（＋mode も触られぬ） |
| ③ | ―― （讀取では立てて居らぬ・本走で新たに出た） | `sed -i` が ★src を書き換へる★（CRLF 時のみ・戻す向き） |

★∴ 讀取からの見立て 二つは 実測で覆らなんだ。★ ―― 併し ★三つ目は讀取の時に立てられて居なんだ★（L17 を「CRLF を直す」としか読まず、★書き換へる先が src である事★ を書かなんだ）。
★見立てが当たつた事より、★立て損ねた見立てが在つた事★ の方を記す。★

### §12-5 境界

★走 2★（値 0 が 1・値を得たが 1）。書いたのは ★scratch 下の隔離樹のみ★。
本物の樹 `/mnt/c/DentalBI` は ★讀取のみ（copy 元）★・現用 hook `e4a47593600691e3` 不触・main/second/mac 不触・
DB 讀 0 書 0・SQL 0・push 0・network 0・fetch 0・CI 0・製品 code 書込 0・共有 `.git` 書込 0・
D 樹不触・Commander の箱 0 打・`gunshi-third` 宛 0・逃げ道 env 0。
