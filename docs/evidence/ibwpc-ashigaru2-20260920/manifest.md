# IBW_PC 検め ―― 足軽second二号の証 ★凍結★ (2026-09-20)

裁: 総監督(iincho) `pc_handshake` seq339912 (2026-09-20T01:54:22)
  ―― 「『書込零』は共有樹への禁であり、自枝 commit は 339598 で解禁済。∴ 足軽二号の証
     (raw2本・IBW_PC 実体の写し)を自枝 docs/evidence/ へ commit し fixed commit/tree を
     付けて軍師secondへ再提出せよ（数の規律22=freeze して渡す）。」
前提: 軍師second REVISE 二度目 ―― 「①fixed commit/tree は repo 外未 commit のまま、
     raw2本も untracked で同一 revision へ束縛不能。fixed tuple を権限者が付与後、
     同一 tree へ raw2本を収載して一括再提出せよ。」
本補完の由来: 軍師second REVISE維持 (2026-09-20T02:10:27・逐語)
  ―― 「REVISE維持。fixed/origin・五本SHA/blob・正RC0/負RC3・復元一致は確認。ただし
     ①manifest L24=`cp -p`とraw=`cp -v`が矛盾 ②manifest EOF空行でdiff-check失敗 ③cwd
     ④lockfile/外部依存 ⑤独立正負対照N（各1）が未充足。同一fixed treeで一括補完してください。」
  本版は ①=§一末尾（三つの行ひへ裂く）＋§四（支への差し替へ） ②=末尾空行を除く
  ③=§五 ④=§六 ⑤=§七 にて答ふ。★先の版を撤せず、其の上への継ぎである★
  （先の版 sha256 = `a04da2e641d150ea6b2c95d5dfcc46f57ff5eb4a56895a1532470c837f86a3b1`・
   commit `6fbe798199d03eba47643009b4aed0aba38c49b7` に在り）。
凍結せし者: 家老second (karo-second)
凍結の刻  : 写し始 2026-09-20T02:00:56.779064800+09:00 / 写し終 同 02:00:56.787352339+09:00
        （源と写しの sha256 を ★同一呼出内★ にて突合し 五本とも一致を実視）

## 一. 凍結せし物（五本）

| # | 凍結後の path | 丈B | 行 | sha256 | 源 path | 源の刻(mtime) |
|---|---|---|---|---|---|---|
| 1 | `raw/ibwpc_stub_test_20260920_003403.txt` | 1330 | 20 | `8052242b995e76da0f7a47d63a81508fa938aa319387065b5339653506bec72b` | `/home/hakudokai/projects/multi-agent-shogun/docs/audit_reports/ibwpc_ashigaru2_stub_test_20260920_0033.txt` | 2026-09-20 00:34:03.717980417 +0900 |
| 2 | `raw/ibwpc_restore_raw_20260920_003807.txt` | 2606 | 29 | `08296c5110e136759ac07f81b1a0dbff82179c315f3b6723551aaafc82f4fdce` | `/home/hakudokai/projects/multi-agent-shogun/docs/audit_reports/ibwpc_ashigaru2_restore_raw_20260920_0033.txt` | 2026-09-20 00:38:07.091222914 +0900 |
| 3 | `artifact/idle_backlog_wake.sh.live-20260920T002056.frozen` | 16430 | 271 | `d703708db068d6787a52c7c6590297aeffdb6c93752aafe235ce895df9c3e46b` | `/home/hakudokai/bin/idle_backlog_wake.sh` | 2026-09-20 00:20:56.373875339 +0900 |
| 4 | `artifact/idle_backlog_wake.sh.bak-ibwpc-20260920-0016.frozen` | 13935 | 222 | `0ddf1725b60c9926b266284bf93456e964faba5c68448c0563c05c115ec6b2a9` | `/home/hakudokai/bin/idle_backlog_wake.sh.bak-ibwpc-20260920-0016` | 2026-09-20 00:16:03.864344244 +0900 |
| 5 | `artifact/idle_backlog_wake.sh.bak-ibwpc2-20260920-002039.frozen` | 14994 | 250 | `a77f8d901cf15217abddc72fe815fbaf1f306a17025b117ad901b426e531498f` | `/home/hakudokai/bin/idle_backlog_wake.sh.bak-ibwpc2-20260920-002039` | 2026-09-20 00:20:39.109767917 +0900 |

### ★写しの行ひは 三つ在り。флаг を一つに畳むな★（軍師second REVISE維持 ①への答）

先の版は此処に「写しは `cp -p` にて取り、源の mtime を保つ」と ★主語を欠いたる儘★ 記した。
表の直下に置かれたるゆゑ、五本悉くに掛かると読め、生の捕獲に載る `cp -v`（`-p` 無し）と
矛盾して見ゆる。★軍師second 殿の指摘は正しい。★ 正すに、行ひを三つに裂いて記す。

| 行ひ | 誰が | 何を → 何処へ | flag | 其の帰結 |
|---|---|---|---|---|
| ㋐ 控を作る | ★足軽second二号★ | `bin/idle_backlog_wake.sh` → `bin/…bak-ibwpc*` | `cp`（`-p` ★無★） | 控の mtime は ★写した刻★ と成る（＝上表4・5行目「源の刻」の正体） |
| ㋑ 復元を試す | ★足軽second二号★ | `bin/…bak-ibwpc*` → ★己の scratchpad★ | `cp -v`（`-p` ★無★） | 生の捕獲 `raw/ibwpc_restore_raw_…` L8・L20 に載るは ★此の㋑★ |
| ㋒ 凍らせる | ★家老second★ | 上表「源 path」→ 本 tree `docs/evidence/` | `cp -p` | 源の mtime を保つ。∴ 上表「源の刻」欄が読める |

∴ `cp -p` は ★㋒のみ★ に掛かる。`cp -v` は ★㋑★ の行ひであり、源も宛ても㋒と異なる
（㋑の宛ては `/tmp/claude-1000/…/15cc9b47-…/scratchpad/` ―― ★足軽second二号の scratchpad★ であつて
本 tree では無い）。∴ 二つは ★同じ物を指して居らぬ★ ゆゑ矛盾せず。先の版の疵は
★事実の偽に非ず、一文が己の掛かる範囲を言はざりし事★ である。§二・§四 は初めより㋐㋑を
正しく書き分けて居り（§二 L30「`cp`（`-p` 無し）にて取りたる控」）、疵は此の一文に限る。

git は mtime を蔵さぬゆゑ、上表の「源の刻」が其の唯一の記録である。
而して ★束縛の軸は mtime に非ず、内容の符★ である（§四・§七に同じ）。

## 二. 作りたる者と 写したる者（★混ずな★）

- `raw/` 二本 ―― ★足軽second二号★ が 00:34:03 / 00:38:07 に自らの器にて産みたる生の捕獲。
- `artifact/` の `bak-…` 二本 ―― ★足軽second二号★ が `cp`（`-p` 無し）にて取りたる控。
- `artifact/…live-20260920T002056.frozen` ―― 実配 `/home/hakudokai/bin/idle_backlog_wake.sh`
  の 2026-09-20T02:00:56 時点の写し。
- ★家老second は「写して凍らせたる者」であり、「産みたる者」ではない。★
  産みの行ひそのものを家老は実視して居らぬ。家老が保証し得るは
  「02:00:56 の時点で此の五本が此の符を持ちたる」の一事のみである。

## 三. 軍師second の 00:34 測りとの突合（★三本とも一致★）

| 軍師が 00:34 に記したる値 | 本 tree の凍結値 | 判 |
|---|---|---|
| live = `d703708d…` | `d703708db068d678…f9c3e46b` | ★一致★ |
| bak ibwpc = `0ddf…` | `0ddf1725b60c9926…5ec6b2a9` | ★一致★ |
| bak ibwpc2 = `a77f…` | `a77f8d901cf15217…e531498f` | ★一致★ |

∴ 00:34 から 02:00:56 迄 三本とも一字も動いて居らぬ。

## 四. 軍師second が「未解決」と記したる mtime 齟齬 ―― 解ける

軍師の字: 「当方は00:19の direct stat/sha256sum で live=14994B/00:16:15.384404681/a77f… を取得。
現00:34の live=16430B/00:20:56.373875339/d703708d…、backup ibwpc=0ddf…/00:16:03、
ibwpc2=a77f…/00:20:39。live と backup の mtime 差は未解決で、いずれも固定根拠にしない。」

★字（測り）★
- 控2 の中身は `a77f…`／14994B／250行。
- 軍師が 00:19 に測りたる live も `a77f…`／14994B。
- 控2 の mtime は 00:20:39。之を持つ源の世代（live `a77f…`）の mtime は ★00:16:15★ である。

★★先の版の支への 差し替へ（家老second 自らの正し）★★
先の版は此処に「生の捕獲に載る実行は `cp -v` ―― `-p` 無し」を支へとして挙げた。
★之は支へとして不適であつた。★ 生の捕獲に載る `cp -v` は §一㋑（控 → 足軽の scratchpad）の
行ひであり、今 説かんとする ㋐（実配 → 控の作成）の行ひではない。★別の行ひの flag を以て
此の行ひを説いたのである。★ 軍師second 殿の ①指摘は、此の混同をも正しく射て居る。
∴ 支へを ★より強き、同じ行ひに属する物★ へ差し替ふ ―― 下の一行である。

★推（家老second の推、字より導く）★
控2 は中身が `a77f…` ゆゑ、其の源は ★mtime 00:16:15 の世代★ に他ならぬ。
然るに控2 自身の mtime は 00:20:39 ―― ★源の刻を継いで居らぬ★。
之 一事を以て、㋐ が源の刻を保たざる写しであつた事は ★控2 自身の二つの数のみ★ から出る
（他の行ひの flag を借りるに及ばず）。
∴ 控2 の 00:20:39 は「源が其の刻に書かれた」の謂ひに非ず、「其の刻に写した」の謂ひである。
中身の符が 00:19 の live と完全一致する事が、控2 が 00:16:15 世代の忠実なる凍結である事を示す。
其の後 00:20:56 に live は再び書かれ `d703708d…`／16430B／271行 となり、以後 02:00:56 迄不動。

∴ ★mtime 差は齟齬に非ず、㋐ が源の刻を保たざる写しであつた事の当然の帰結である。★
   束縛の軸は mtime ではなく ★内容の符★ であり、其の符は三本とも合ふ（§七 正対照 N=5 にて再検め）。

## 五. ③ cwd・argv・rc ―― 補完の生の捕獲

path : `raw/suppl_controls_20260920_022259.txt`
sha256: `8a5cbbafb98f7f2e58938d21246fd6f567d625693f7e23a8c2c3215155b7e55e`
丈/行 : 7910B / 112行

載る物（悉く器が吐きたる儘、物語りに非ず）:
- ★cwd★ = `/home/hakudokai/karo/wt-12674e7c`（`pwd` と `$PWD` の両方を刷る）
- host = `USER-O6AK917NTU` / user = `hakudokai` (uid=1000) / uname = `Linux 6.6.87.2-microsoft-standard-WSL2 x86_64`
- branch / HEAD / tree / worktree の四つ
- 各撃ちの ★`++ argv:` と `++ rc=` を対にして★ 刷る
- 道具の版（bash 5.2.21 / coreutils 9.4 / git 2.43.0 / python 3.12.3 / diffutils 3.10）

★此の捕獲を撃ちたる刻の HEAD は親 commit `6fbe7981…` である。★
本補完 commit が触るは `manifest.md` と本 raw の ★二本のみ★ であり、
上表五本は一 byte も動かぬ。検めらるるには
`git diff --name-only 6fbe7981 <本commit>` を撃ち給へ ―― ★二 path のみ★ 出づる筈。

## 六. ④ lockfile と 外部依存

★lockfile★
- 本 repo に依存固定 lockfile（`package-lock.json`/`yarn.lock`/`pnpm-lock.yaml`/`poetry.lock`/
  `Pipfile.lock`/`uv.lock`/`Cargo.lock`）は ★一本も無し★（`find` rc=0・出力空）。
  `requirements.txt`（13B）のみ在るが、本証の検証経路（`sha256sum`/`git`/`cp`/`diff`）は之を用ひず。
- 凍結せし三本自身の 排他語彙（`flock|lock|noclobber|pidfile|.pid|mutex|semaphore`）= ★三本とも 0★。

★外部依存（凍結せし主体が呼ぶ器）★

| 凍結物 | python3 | curl | tmux | STALL_WAKE_LIB |
|---|---|---|---|---|
| `…bak-ibwpc-…0016.frozen` | 7 | 3 | 7 | 4 |
| `…bak-ibwpc2-…002039.frozen` | 8 | 3 | 7 | 4 |
| `…live-20260920T002056.frozen` | 9 | 3 | 7 | 4 |

- L18 `STALL_WAKE_LIB="${STALL_WAKE_LIB:-$HOME/bin/stall_wake_lib.sh}"` / L163 `. "$STALL_WAKE_LIB"`。
- ★其の器は当機(second_pc)に在らず★（`/home/hakudokai/bin/stall_wake_lib.sh` 無・
  `/home/hakudoukai/bin/stall_wake_lib.sh` 無 ―― 二綴りとも測りて無）。
- 然れど L161 の枷 `[ "${IBW_PC:-third}" = third ] && [ -r "$STALL_WAKE_LIB" ]` に依り、
  当機では此の枝を通らぬ。∴ ★器の不在は本証の妨げに非ず。但し third にて走らす時は要る。★
- ★之は測りのみ。直しの案は出さぬ（Phase B 凍結）。★

★未測（他席の持ち物）★ ―― 足軽second二号の harness（`ibwpc_case.sh`/`funcs.sh`/`loopbody_raw.sh`）は
彼の scratchpad に在り本 tree の外ゆゑ、其の lockfile/外部依存は ★家老の手にて測り居らぬ★。
owner = ashigaru-second-2。

## 七. ⑤ 独立の 正・零・負 対照（N を各一より増やす）

器を ★二つ★ 用ふ ―― ①filesystem の `sha256sum` ②git object 蔵の `git cat-file blob`。
一方が誤つても他方が同じ誤りを犯す理由が無い。

| 対照 | N | 結 |
|---|---|---|
| ★正★ 作業樹の実体 = git blob の符 | ★5★ | 5/5 ★一致★（blob id も併記） |
| ★零★ 手を加へざる写し | 1 | 一致・`diff` rc=0（＝検出器は常に落ちるに非ず） |
| ★負★ 毀したる写し | ★3★ | 3/3 ★捕獲★・`diff` rc=1 |

負の三様（毀すは ★scratchpad の写しのみ★。源 `/home/hakudokai/bin/*` にも tree にも一字も触れず）:
1. 末に一字継ぐ ―― 14994B → 14995B
2. ★中の一字を差し替ふ ―― 14994B の儘★（∴ 丈のみを見る検出器では捕らへ得ぬ。符が之を捕へたる事が、
   検出器が丈に非ず ★内容★ を見て居る証である）
3. 末の一字を削る ―― 14994B → 14993B

★母集団より `manifest.md` を除きたり★ ―― 之は主張を為す器其の物であり、己を己の標本と為し得ぬ。
加之、本補完にて `manifest.md` は書き改まるゆゑ、其の符を此処に刷れば ★既に死したる頭★ を指す。

★猶 未充足（正直に記す）★ ―― 軍師second 殿が「各1」と指したる内、
足軽second二号の harness の 正RC0/負RC3 は ★今も各1のまま★ である。
之を増やすには彼の harness を再び撃たねばならず、器も証も彼の手に在る。
owner = ashigaru-second-2 / next_safe_action = 同 harness にて正負を各2以上へ / human_GO_required = NO。
★本 §七 が増やしたるは「凍結が忠実なるか」の軸であり、「wake 判定が正しきか」の軸では無い。★
二つの軸を混ずな。

## 八. 本 commit の限界（★これを越えて読むな★）

1. 本 tree が束縛するは ★上表五本の内容★ のみ。`idle_backlog_wake.sh` は可変であり、
   本 commit 以後の実配は別物たり得る。「此の commit の写し」と「今の実配」を同一視するな。
2. `idle_backlog_wake.timer` は無効・不活のまま。家老は触れて居らぬ。
3. 本件は ★稼働 receiver の系統割れ★（disk M が HEAD/main/自枝の何れにも当たらぬ件）とは
   別件である。彼は未決・総監督の裁定待ち。
4. ★本 dir の五本は .gitignore の白名に載らず、`git add -f` にて収載した。★
   （本 repo の `.gitignore` は 7行目 `*` の全遮断＋`!` の白名方式。`docs/evidence/` の
   白名は無い。既存の `docs/evidence/km-manifest-append-track-20260917/` 19本も
   同じく白名に載らぬまま追跡下に在る＝先例。）
   ∴ ★後の者へ：此の dir へ紙を置いても `git status` は黙る。`-f` を要する。★
   白名を足さざるは、共有の `.gitignore` を自枝で広げれば merge の折に他席の
   `docs/evidence/` 配下の私物まで一斉に可視化する虞あるゆゑ。
   ★本補完にて再び実視したり★ ―― 新たに置きたる `raw/suppl_controls_…txt` につき
   写しの直後に `git check-ignore -q` を撃てば ★無視さると答へ★、同時に撃ちたる
   `git status --porcelain` は ★一行も刷らざりき★。即ち「status が黙る」は言ひ伝へに非ず、
   本 commit の作業中に二度目の実視を得たる事実である。
5. ★己の欠（軍師殿に見付けらるる前に己で書く）★
   - 足軽second二号の harness の 正RC0/負RC3 は ★今も各1★。増やす器は彼の手に在る（§七末）。
   - 彼の harness の lockfile/外部依存は ★家老の手にて未測★（§六末）。
   - §七の対照は「凍結が忠実か」を測る。「wake の判定が正しきか」は ★測つて居らぬ★。
   - 凍結せし三本の ★実機実行は撃たず★。走らせずに読みたるのみ（`idle_backlog_wake.timer`
     不活のまま・実配に一字も触れず）。∴ 「読みて測りたる緑」であり「走らせたる緑」ではない。
   - §一㋐ の flag を家老は ★実視して居らぬ★。㋐が源の刻を保たざりし事は控2自身の
     二つの数（内容の符 と mtime）より導きたる ★推★ であり、㋐ の argv を見たるに非ず。
6. ★本補完 commit が触るは `manifest.md` と `raw/suppl_controls_…txt` の二本のみ。★
   上表五本は一 byte も動かず。検めは `git diff --name-only 6fbe7981 <本commit>` にて
   ★二 path のみ★ 出づる事を以てせよ。
