# ★型で出し直す★ ―― 軍師third REVISE 四件への是正（走 0・調べる走行のみ）

as_of 2026-09-08 19:4x JST ／ 席 ashigaru-third-2 ／ 令 `msg_20260908_194320_*` + `msg_20260908_194322_4548e9bc`
★本紙は走 0 である★（`sha256sum` `wc -l` `hostname` `id -un` `pwd` `git ls-files` は ★調べる走行★ ゆゑ走に数へぬ ―― 本 lot 通しの定義）。
★digest の種＝`sha256`。以後 ★64 桁の完全値★ で書く（短 SHA は本紙では使はぬ）。★

---

## §0 ★先に一つ ―― 型では直らぬ物が在る（之が REVISE の根である公算）★

軍師の指摘①は「★短 SHA・板 `b44649cf` は正本 repo で解決不能★」。当席は之を ★己の側でも当たつた★:

```
$ git ls-files --error-unmatch scripts/sweeps/audit_disk_pressure.sh
error: pathspec '...' did not match any file(s) known to git
$ git status --porcelain scratch
?? scratch/
```

★∴ 当席の器も紙も ★git に一つも入つて居らぬ★（untracked）。★
★当席は commit 0・push 0 の床に在る★（本 lot 通し・境界に明記して来た）。
∴ ★repo 相対 path を幾ら正確に書いても 軍師の正本樹では `git show` も `cat` も当たらぬ★
 ―― ★file が其処に無いのだから★。

★之は型の疵ではなく ★渡し方の疵★ である。★型を満たしても解決せぬ。★

★解ける道は三つ（当席は選べぬ ―― 裁を請ふ）★:
1. ★同一 host の絶対 path を渡す★ ―― 軍師third は ★当席と同じ third PC 在★ ゆゑ
   `momizi-dx:/home/hakudoukai/multi-agent-shogun/scratch/...` は ★同じ file を指す公算★。
   ★最も安い★。★但し「軍師が当席の作業樹を讀めるか」は 当席は確かめて居らぬ★（他席の樹は覗かぬ床）。
2. ★commit の許し★ ―― 床が変る。当席の一存では打てぬ。
3. ★本文へ全文を貼る★ ―― 紙 2,454 行・便 300 字の床では ★成り立たぬ★。

★∴ 以下 §1 では ①に ★host を添へた絶対 path★ を併記する（repo 相対だけでは足りぬ為）。★

---

## §1 ★四件の型★（①〜⑧）

★①repo 相対 path ／ ★host 付き絶対 path★（§0 の理）／ ②完全 SHA 64 桁 ★sha256★ ／ ⑥host/user/cwd★

共通の ⑥: `host=momizi-dx user=hakudoukai cwd=/home/hakudoukai/multi-agent-shogun`
★git blob の sha1 ではない★（o85 §14-1 で一度 取り違へた前科が在る ∴ ★種を必ず書く★）。

| # | ①repo 相対 path | 行 | ②sha256（完全 64 桁） |
|---|---|---|---|
| 1 | `scripts/sweeps/audit_disk_pressure.sh` | 211 | `fa0e3922b9d8534e6cc876df20e27ee067ebfb4e10807575cab68f610a1ac81e` |
| 2 | `scratch/ashigaru-third-2-fa06a3a1/after_delete_5668_gap_1483_readonly_v1.md` | 2454 | `7205ec2fbdc3878a4e499ad6c41d575d17bbbdc0b120b2a10f4d75f2d59eb11f` |
| 3 | `scratch/ashigaru-third-2-fa06a3a1/o97_handover_index_v1.md` | 422 | `377746993629e50f689c5248d1f8e83fcfa2689eb0b389a32df4c181e525971a` |
| 4 | `scratch/ashigaru-third-2-fa06a3a1/o130_magazine_v1.md` | 101 | `4ce6af5e257ae9b4ea90c7dec00af5b47c1a8c08bf81929a63a3aed3d7b50e28` |

★host 付き絶対 path★＝上の相対 path の前に `momizi-dx:/home/hakudoukai/multi-agent-shogun/` を付けた物（四件とも同形）。

★1 の mode＝0755・★repo へ書いた唯一の製品 code（令の名指し）★・★untracked★。★
★2〜4 は `scratch/` 配下＝★untracked★。★

---

## §2 ★③argv 逐語 ／ ④raw の完全 SHA と行数 ／ ⑤exit code★

### §2-1 order129（走 3・三台）

★③argv 逐語★（三本とも）:

```
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new mainpc   'bash -s -- --report'  < scripts/sweeps/audit_disk_pressure.sh
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new secondpc 'bash -s -- --report'  < scripts/sweeps/audit_disk_pressure.sh
bash scripts/sweeps/audit_disk_pressure.sh --report
```

★他 PC には file を置かぬ（stdin へ流し込む）★＝no-repo-copies。★他 PC への書込 0。★

★④raw★: `scratch/ashigaru-third-2-fa06a3a1/o129_run1_3pc_20260908_184527.txt`
 82 行 `3ed3e8bcc3afda83617194eda104a96bb52897351560f118ee12d9cabcf5dbaa`

★⑤exit code★: raw の各 PC 見出し行に ★逐語で載つて居る★ ―― `### PC=main rc=0` / `PC=second rc=0` / `PC=third rc=0`。★三本とも rc=0。★

★別名 vs 実値の確かめ★: `scratch/ashigaru-third-2-fa06a3a1/o129_alias_check.txt`
 5 行 `0e9d320cd946ba62d448c83c2c09dcf7c6281d93e4d77d3f5105645e486e8c59`（四通り 悉く rc=0・hostname 一致）。
★但し 之は ★走の後に取り直した★（家老の追補が 8 秒差で走に間に合はず）―― ★順の違背は数が合つた事で消えぬ★（紙 §35-5①・§35-10）。

### §2-2 order128（走 21・三之PC のみ）

★④raw 四本★（行数と完全 SHA）:

| raw | 走 | 行 | sha256（完全） |
|---|---|---|---|
| `o128_run1_raw.txt` | 3 | 60 | ★本紙では未取得★（短 `f0efab257a47ebc1` のみ紙に在り）―― ★軍師が要れば次便で完全値を出す★ |
| `o128_run2_raw.txt` | 6 | 62 | ★同上★（短 `c1af8c93096470e7`） |
| `o128_run3_raw.txt` | 6 | 59 | ★同上★（短 `7ba2b7c973270690`） |
| `o128_run4_raw.txt` ★判定に供する最終★ | 6 | 88 | `6f40e486dcd330149628d6f9ca91c2743e4639c3a93de900a49ab43dee3fd759` |

★正直に書く★: 上の三本は ★本紙を書く手番で完全値を取り直して居らぬ★ ∴ ★「確かめて居らぬ」を添へる★。
（判定に供するは run4 一本ゆゑ 之を先に完全値で出した。）

★③argv／⑤exit code★: ★raw の中に ★走ごとの見出しとして★ 逐語で在る★ ――
 run4 の例: `=== 走 既定 / rc=0 ===` `=== 走 abs=100 / rc=0 ===` `=== 走 abs=300 / rc=0 ===`
 `=== 走 abs=9000 pct=99 / rc=0 ===` `=== 走 pct=101（在り得ぬ閾） / rc=0 ===` `=== 走 --report / rc=0 ===`。
 ★rc の載る行数★: run1=3／run2=6／run3=8／run4=6。
★食ひ違ひを一つ開示★: run3 は ★走 6 と紙に書きながら rc 行が 8 在る★。
 ★因は当席の手元では判じ得ぬ（本紙は走 0 ゆゑ raw を讀んだのみ）★ ―― ★数の食ひ違ひとして そのまま出す★。
 ★どちらが正かを 今 断ずるは避ける★（走を許されれば raw の全文を突き合はせて解ける）。

---

## §3 ★⑦正負の対照★

同じ走の中で ★両方★ を述べる形にして在る（条⒁）。

| 何 | 出る所 | order129 三台の値 |
|---|---|---|
| ★陽性★ `SELFTEST` | stderr・毎走 | ★三台とも `STANDS`★（合成した満杯の床で ★鳴る★） |
| ★陽性（令の指定値）★ `SELFTEST_CANON leg=vhdx_225_99` | stderr・毎走 | ★三台とも `FIRES`★（★exit から外して 毎走 述べる★＝令①②の形） |
| ★陰性★ | stdout | ★閾を超えぬ床では ★1 行も出ぬ★（silent）★ |

★不利の証★: 既定閾（`DP_ABS_MAX_GIB=80`）では ★三台とも `/` が當たる★（244/155/91 GiB）
 ∴ ★『静かな時は黙る』は 此の床では現に見えて居らぬ★。★之は圧が高い事の証ではなく 閾の据ゑ方の帰結★。
 ★閾は当席が動かさぬ★ ―― ★軍師の裁定を待つ★（軍師指摘④と同趣旨）。

---

## §4 ★⑧母数と『測れなかつた数』を別値★

★足さぬ★。三つの母数が在り ★立つ所が違へば別の数★ である（家老が「本日の隊で最も効く註」と採つた件）。

| 母数 | 値 | 註 |
|---|---|---|
| ★PC★ | ★measured 3 ／ unmeasured 1★ | 3=main/second/third・1=Mac（★正本三先に無く 経路不明・令『探すな』★）。★0 と書かぬ・三台で足りたと書かぬ★ |
| ★mount（各 PC 内）★ | main 15 ／ second 14 ／ third 17 | ★足さぬ★（PC の母数 4 とも足さぬ） |
| ★器の行 `pc_measured=1`★ | 各 PC で 1 | ★各 PC から見た値★ ―― 隊の 3/1 は ★三本を突き合はせて初めて出る★ |

★軍師指摘⑥『Mac UNMEASURED は明記済だが 母集団完了ではない』は ★当席も同じ読み★。★
 ∴ 弾倉 §1 順 3 に ★Mac の圧＝席の外（経路が要る）★ として立てて在る
 （`o130_magazine_v1.md` 101 行 `4ce6af5e257ae9b4ea90c7dec00af5b47c1a8c08bf81929a63a3aed3d7b50e28`）。

---

## §5 ★軍師の六指摘に一つづつ★

| # | 指摘 | 当席の答 |
|---|---|---|
| ① | 短 SHA・板 `b44649cf` は正本 repo で解決不能 | ★受ける★。而して ★型では直らぬ★＝当席の file は ★git 未追跡★（§0 の実測）。★渡し方の裁を請ふ★（三つの道を §0 に並べた） |
| ② | 21 走の argv/raw/exit 未提出 | ★出した（§2-2）★。raw 四本の行数と走の別・rc 行数を併記。★run1〜3 の完全 SHA は本手番で取り直して居らぬ＝確かめて居らぬ★ |
| ③ | 陽性・陰性対照 | ★出した（§3）★。★毎走 stderr に述べる形★（exit から外した＝令①②） |
| ④ | 閾値は裁定を固定してから判ず | ★同意・当席は動かさぬ★。80/100/200/300 を並べて渡し済（弾倉 §1 順 2＝★走 0・選べば即決まる★） |
| ⑤ | 3PC 値は主張のみ・host/user/path・raw が要る | ★出した（§1・§2-1）★。★raw の中に host 名が逐語で入つて居る★（`USER-0T4SR8MIQA` / `USER-O6AK917NTU` / `momizi-dx`）∴ ★主張ではなく 器の出力である★ |
| ⑥ | Mac UNMEASURED は母集団完了ではない | ★受ける（§4）★。★弾倉に『撃てる弾・席の外』として立てて在る★ |

---

## §6 ★型を定めなんだは家老の疵、と裁かれた ―― 而して当席が見た物は消さぬ★

家老は「★型を定めなんだは家老の疵★」と書いた。★之は受ける★。
★併し★ ―― ★短 SHA で出したのは当席である★。★型が無くとも 完全値を出す事は出来た★。
∴ ★裁（咎は家老）と 己が見た物（当席も出せた筈）を 二つ並べて残す★
 ―― ★隊の作法（家老の条 百九十八）に従ふ★: ★咎が上に在ると裁かれても 己が己の違背と見た事は消さぬ。★

---

## §7 境界（本弾）

★走 0★（`sha256sum`/`wc -l`/`hostname`/`id -un`/`pwd`/`git ls-files`/`git status` の ★調べる走行のみ★）／
★git は ★讀取二本★（`ls-files --error-unmatch` と `status --porcelain`）―― ★書く動詞 0・commit 0・push 0★★／
★repo 触れず（器は改訂 0）★／他 PC への経路 0／消す・移す・圧す 0／hook 不触／D 樹不触／
Commander の箱 0 打／書込は ★本紙と索引のみ★。


---

## §8 ★家老の裁を受けて ―― ★絶対 path＋sha256(64)＋行数★ の一覧（軍師が己の手で当たれる形）★

裁の逐語（`msg_20260908_194604_38b03345`）: 「★軍師third は ★同じ床(third PC)に居る★ ゆゑ ―― ★repo 相対でなく ★絶対 path＋sha256(64)＋wc★ を渡せば ★軍師が己の手で当たれる★★（★未追跡の作業樹 file である旨を明記★ せよ）。★併せて『commit/push が要るか』の裁は家老が上へ請ふ★＝其の答が来る迄 ★上の道で出せ★。」

★∴ §0 の道 1 が採られた。以下 其の形で出す。★

★★悉く `host=momizi-dx` の ★untracked（git 未追跡）作業樹 file★ である ―― `git ls-files` に一件も無い。★★
★∴ 軍師の正本樹では当たらぬ。★下の絶対 path を ★third PC 上で★ 開かれたい。★

| # | ★絶対 path（host=momizi-dx）★ | 行 | ★sha256（完全 64 桁）★ |
|---|---|---|---|
| 1 | `/home/hakudoukai/multi-agent-shogun/scripts/sweeps/audit_disk_pressure.sh` | 211 | `fa0e3922b9d8534e6cc876df20e27ee067ebfb4e10807575cab68f610a1ac81e` |
| 2 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/after_delete_5668_gap_1483_readonly_v1.md` | 2454 | `7205ec2fbdc3878a4e499ad6c41d575d17bbbdc0b120b2a10f4d75f2d59eb11f` |
| 3 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o97_handover_index_v1.md` | 422 | `377746993629e50f689c5248d1f8e83fcfa2689eb0b389a32df4c181e525971a` |
| 4 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o130_magazine_v1.md` | 101 | `4ce6af5e257ae9b4ea90c7dec00af5b47c1a8c08bf81929a63a3aed3d7b50e28` |
| 5 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o129_run1_3pc_20260908_184527.txt` | 82 | `3ed3e8bcc3afda83617194eda104a96bb52897351560f118ee12d9cabcf5dbaa` |
| 6 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o129_alias_check.txt` | 5 | `0e9d320cd946ba62d448c83c2c09dcf7c6281d93e4d77d3f5105645e486e8c59` |
| 7 | `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o128_run4_raw.txt` | 88 | `6f40e486dcd330149628d6f9ca91c2743e4639c3a93de900a49ab43dee3fd759` |
| 8 | ★本紙★ `/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-2-fa06a3a1/o131_typed_submission_v1.md` | ★§9 に記す★ | ★§9 に記す★ |

★当たり方（軍師が己の手で確かめる形）★:
```
sha256sum <絶対 path>      # ②と突き合はせる
wc -l      <絶対 path>      # 行数と突き合はせる
```
★digest の種＝`sha256`（★git blob の `sha1` ではない★）。★

★なほ ★『軍師が当席の作業樹を讀めるか』は 当席は確かめて居らぬ★★（他席の樹は覗かぬ床・当席から軍師へは直に書かぬ床）
 ―― ★読めぬ時は 其れ自体を報せられたい★。★当席は次の道（commit の許し）を ★己では選べぬ★（裁は家老が上へ請ふ由）。★


## §9 ★本紙自身の digest は 本紙に書けぬ★（§8 の 8 行目の答）

★書けば其の瞬間に変る★ ―― file の digest を其の file の中に書く事は ★原理として出来ぬ★。
∴ ★本紙の行数と sha256 は ★便に載せる★（便は本紙の外に在る）。★
★之は「測れぬ」の四つ目の形（原理として測れぬ）である★ ―― 弾に数へぬ。

★軍師へ★: 本紙を当たる時は ★便に載つた値★ と `sha256sum` を突き合はせられたい。
★便の値と本紙の実測が食ひ違へば ―― 便を出した後に誰かが本紙を触つた事に成る。★
