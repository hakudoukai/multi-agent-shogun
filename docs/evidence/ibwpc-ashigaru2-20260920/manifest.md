# IBW_PC 検め ―― 足軽second二号の証 ★凍結★ (2026-09-20)

裁: 総監督(iincho) `pc_handshake` seq339912 (2026-09-20T01:54:22)
  ―― 「『書込零』は共有樹への禁であり、自枝 commit は 339598 で解禁済。∴ 足軽二号の証
     (raw2本・IBW_PC 実体の写し)を自枝 docs/evidence/ へ commit し fixed commit/tree を
     付けて軍師secondへ再提出せよ（数の規律22=freeze して渡す）。」
前提: 軍師second REVISE 二度目 ―― 「①fixed commit/tree は repo 外未 commit のまま、
     raw2本も untracked で同一 revision へ束縛不能。fixed tuple を権限者が付与後、
     同一 tree へ raw2本を収載して一括再提出せよ。」
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

写しは `cp -p` にて取り、源の mtime を保つ。git は mtime を蔵さぬゆゑ、上表の「源の刻」が
其の唯一の記録である。

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
- 控2 の mtime は 00:20:39。生の捕獲（`raw/ibwpc_restore_raw_…`）に載る実行は `cp -v` ―― ★`-p` 無し★。

★推（家老second の推、字より導く）★
`cp` に `-p` 無くば写しの mtime は ★写した刻★ となり、★源の刻★ とはならぬ。
∴ 控2 の 00:20:39 は「源が其の刻に書かれた」の謂ひに非ず、「其の刻に写した」の謂ひである。
中身の符が 00:19 の live と完全一致する事が、控2 が 00:16:15 世代の忠実なる凍結である事を示す。
其の後 00:20:56 に live は再び書かれ `d703708d…`／16430B／271行 となり、以後 02:00:56 迄不動。

∴ ★mtime 差は齟齬に非ず、`cp -p` を用ひざる事の当然の帰結である。★
   束縛の軸は mtime ではなく ★内容の符★ であり、其の符は三本とも合ふ。

## 五. 本 commit の限界（★これを越えて読むな★）

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

