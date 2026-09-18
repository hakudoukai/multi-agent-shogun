# km-198 ―― 刻無き測りの census ―― 動く物を測る器は、いくつ刻を刷るか(紙のみ・器は書換へず)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_198_20260918T2123`(task_id km-198・家老mac 発・板外・8 桁は着地時に家老が焼く)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T21:29:47+0900 / 着手便 21:25(宣ETA 22:10)/ 測り 21:25〜21:28
- 枝 = `ashigaru-mac-1/km-198-toki-wo-surazu-hakaru-utsuwa-no-census-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km198)。押さず。
- 出所 = 家老が 21:19 頃の検分「km-196 tip 一致 = yes(20e1b255)」に刻を刷らず、枝は 21:16:43 に 5bf4397c へ動いて居た。出目が正しいか古びたかを後から誰も判じ得ぬ形。

## ㋐ 結語

1. ★三母數(㋐・file 単位・rc 0・刻 21:27)★: ⑴ scripts/checks/*.sh(己の樹 origin/main・深さ 8・冠問はず)= ★16 file★ ⑵ ~/bin の実行可 file(深さ 1)= ★74★(find -perm 73 と walk 74・差 1 は実行可の判の差=名指す)⑶ 己の束(ashigaru-mac-1_* と km-1*)の raw/*.txt = ★146 file / 15 束★(origin/main 由来の km-manifest-append-track の raw は 14 樹に写るゆゑ除いた=除いた数 14・己の器 01_walk 自身は名で除いた)。
2. ★動く物を測る器(㋑)★ = checks ★8★ / bin ★12★ / raw ★11★(検出子 = git rev-parse|rev-list|for-each-ref|ls-remote|reflog・date・stat・wc・du・sb read・tmux capture-pane の字面・註行は見ぬ)。検出子無し(動かぬ物のみ)= checks 8・bin 62・raw 135。測れぬ(binary)= 0。
3. ★三値(㋒・和 = ㋑ の母數)★: checks 甲 1 / 乙 3 / 丙 ★4★(和 8)・bin 甲 3 / 乙 5 / 丙 ★4★(和 12)・raw 甲 1 / 乙 7 / 丙 ★3★(和 11)。丙(刻無しで動く物を測る)= checks: context_usage_warn.sh・ephemeral_worktree_hygiene.sh・karo_mac_dasumae_gate.sh・tests/karo_mac_dasumae_gate_negative_test.sh / bin: dept_visual_sweep.sh・hermes_idle_flag_sync.sh・km_inbox_read_mark.sh・sb / raw(己): km-182 raw/12・km-187 raw/14・km-188 raw/15。
4. ★固定(㋓)★: ref 名を 2 度以上使ふ器で「一度 40 桁へ解いて以後其れを使ふ」形は ★0★・「毎度 ref 名で引き直す」= checks 2(ephemeral_worktree_hygiene.sh・pane_identity.sh)・bin 1(dept_visual_sweep.sh)・raw 2(己の km-196 raw/20・raw/30 = origin/main…refs/heads/… を二度以上名で引いた)。★二度の間に動き得る形 = 5★。
5. ★家老の本日の検分の置き場(命)★: 陽性対照の種(raw/seed_ctrl/positive_control_karo_form.sh = 刻を刷らず ref 名を二度引き「tip 一致= yes」と出す形)は器で ★丙(刻無し)★・固定無し。∴ 家老の km-195/km-196 の検分は ★丙★ ―― 出目が古びたか否かを後から判じ得ぬ形であつた。陰性対照(negative_control_static.sh = 引数 file を grep するのみ)は「検出子無し」で ㋑ に入らぬ。

## ㋑ 器と判の法(raw/01・10)

- 器 = raw/01_walk_toki_naki_hakari.py(己・python・歩き根は argv・己の名を除く)。file 単位で: 検出子の行(註を除く)が 1 本以上 → 「動く物を測る器」。刻の字面 = `date +|-I|"+`・strftime・koku=|刻=|as_of|timestamp|%Y-%m|isoformat|now()。甲 = 検出子の行 ★悉く★ 同じ行に刻 / 乙 = file の別の行に刻(一部同行を含む・註す)/ 丙 = file に刻の字面が無い。
- 固定 = ref 名(HEAD・origin/main・refs/heads/…・main)の行が 2 本以上在る file で、`=$(git rev-parse …)` の受けが在れば「固定」・無ければ「毎度 ref 名で引き直す」。
- 排他: 各 file は 甲/乙/丙/検出子無し/測れぬ の丁度一つ。和は各母數に一致(raw/10 末尾)。
- 疵(round1・round2 の控): 初版は root 欄を label のみ・path を root 相対で刷り、14 樹に写る同名 file が同じ行に見えた(362 行・unique 232)→ 実 path へ。二版は origin/main 由来の tracked 束を 14 度数へた → 己の束名で絞つた(除いた数 14 を書く)。

| 母數 | file | 動く物を測る器 | 甲 | 乙 | 丙 | 検出子無し | 毎度引き直す |
|---|---|---|---|---|---|---|---|
| checks(scripts/checks/*.sh) | 16 | 8 | 1(dd169_kill_term_guard.sh) | 3(karo_mac_gate4.sh・pane_identity.sh・secondpc_dispatch.sh) | 4 | 8 | 2 |
| bin(~/bin 実行可) | 74 | 12 | 3 | 5(compact_drain_inject.sh・idle_backlog_wake.sh の bak 3・karo_mac_bundle5.sh) | 4 | 62 | 1 |
| raw(己の束 15) | 146 | 11 | 1(km-184 raw/31 round1) | 7 | 3 | 135 | 2 |
| seed(対照) | 2 | 1 | 0 | 0 | 1(陽性=家老の形) | 1(陰性) | 0 |

## ㋒ 判じの註

- 家老の器 ~/bin/sb(丙)は「sb read」の入口ゆゑ動く物(DB)を読むが刻を刷らぬ ―― 読み手が刻を添へる約束が要る。karo_mac_dasumae_gate.sh(丙)は stat/wc で disk を測るが刻を刷らぬ(門の出目に「いつの disk か」が無い・當席は門の控を別名で焼き刻を file 名と koku 行で補つて来た = 乙の形を紙の側で作つて居る)。
- 己の raw の丙 3 は census の中間出目(要約 txt)で、koku 行を持つ隣の raw に刻が在る = 「別 file に刻」= 乙に近いが器は file 単位で判ずるゆゑ丙。★己の疵として数へる★。
- 固定 0 は「40 桁へ解いてから測る」形が此の三母數の何処にも無い事を言ふ。當席の km-196 raw/30 も `origin/main...refs/heads/…` を二度名で引いた(二度同値と出たが、其れは動かなかつた證であつて動かぬ證ではない)。

## ㋓ 案(★紙のみ・器は書換へず★)

- 動く物を測る出目の行に `koku=<date +%Y-%m-%dT%H:%M:%S%z>` を同じ息で刷る(甲の形)。門(karo_mac_dasumae_gate.sh)は結語の行に刻を添へる一行。
- ref 名を二度使ふ器は最初に `SHA=$(git rev-parse --verify <ref>)` で固定し、以後は `$SHA` で測る(km-196 raw/30 の己の形もこの直しの対象)。

## ㋔ 測れぬ物

- 検出子は字面。`git log`・`ls`・`cat` の様な読みは動く物を測る事も在るが網の外(除いた事を書く)。
- ~/bin の binary(0 本・悉く text)。走らせねば判らぬ刻(実行時に log へ書く器)は静的網では拾へぬ。
- 「甲 = 同じ行」は行の単位。`{ echo koku; cmd; } | tee` の様に同じ出目 file に刻が入る形は乙に落ちる(器の粗)。

## ㋕ 疵

⑴ 着手便 300 字超 1 度(369)⑵ 走査器の初版(label のみ)と二版(tracked 束の重複 14)の粗 → 控を残し三版で数へた ⑶ zsh の語分割無しで根の引数が一つに潰れ 1 度落ちた(bash -c で走らせ直し)⑷ 紙の初版を unquoted heredoc で書き `$(…)` が shell に食はれて紙が出来なかつた(quoted heredoc で書き直し)。

## 宣⇔實

宣ETA 22:10。實 = 納め便の刻(紙の外・21:3x 見込み)。
