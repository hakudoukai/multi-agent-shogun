# 第66弾 ―― 載らぬ 336 を ★載せぬ(正)★ と ★載せられぬ(疵)★ と ★決められぬ★ に分けろ ―― 則を先に書いて(読取のみ・据ゑず・他席の臺帳 0 字)―― 答を先に(★數の出處 = raw/30_sanzan.txt + .tsv + _per_ledger.tsv(三山・一本ごと・臺帳ごと)/ raw/30_sanzan.first.*(2MB 閾を持つた一走目 = 343)/ raw/32_1byte.txt(相違 1 の決着)/ raw/33_onore.txt(己の本数)/ raw/00_start.txt(起・宣・★則の逐語★)★)

★答★: 則は ★測る前に★ raw/00_start.txt へ書いた(甲1→甲2→甲3→甲4→乙1→(乙5)→丙1→乙2→丙2→乙3→乙4・丙0 の順で ★最初に当たつた山★・順序も則の一部)。前弾 26 と同じ定義(40 本の臺帳の <紙>_evidence 配下・os.walk・lstat・S_ISREG・臺帳自身を除く・臺帳の一致項が指す realpath に無い file)で本弾の刻(02:47:04)に引き直し ★配下 1532 / 載らぬ 336(動かぬ)★。三山 = ★甲(載せぬのが正)285 本 489,924 B / 乙(載せるべきなのに落ちた)49 本 547,675 B / 丙(決められぬ)2 本 15,495 B・総和 336 差 0★。乙の何故(㋑)= 乙1 届かぬ 23(項は在るが dir を省き実体へ届かぬ)/ 乙5 讀めぬ行に載る 3(sha は臺帳の生の行に在るが余欄で讀み手が破れる)/ 乙3 門の後に生れた 6 / 乙4 器へ渡さなかつた 17 / 乙2 名が器を破る 0 / 追記器が拒んだ(rc=3)★実測 0★(追記器の生 09-17 01:40 より後の臺帳 0/40 ∴ 測れぬ)/ 不明 0。丙(㋒)= 同秒 2 → 「同分」へ締めて ★4★(零でない)。相違 1(㋓)= 1 byte は ★末尾の改行 LF★(22047 通り抜いて宣 sha に当たる位置 22045/22046 = LF LF の連)・臺帳が後(20:19:20 > 紙 20:19:01・紙の ctime は臺帳より前 ∴ 紙は其の後触られて居らぬ)。己(㋔)= 40 の内 己の舊紙 21 本は載らぬ 0・己の km-60〜65 の 6 束 589 本は「別所」の定義が外す(除いたのは己でなく定義)・本束は門の後に同じ則を掛け _after/33_onore_after.txt。一走目(02:45:45)は ★343★ と出た ―― 差 7 は己の器の 2MB 閾(丙0)が産んだ(disk は動かず・.first に残す)。

## 0. 断(先に)
1. **★「載らぬ 336」は一つの山ではない。285 は載せぬのが正、49 は疵、2 は決められぬ。★** 甲の 269 は門の出目(mon/・gate・.gatelog)で、凍結の後に走る物を臺帳に載せる法は無い。
2. **★乙 49 の内 23 は「載つて居る」。★** B2_30/B2_31/karo B0_10 の臺帳は同じ sha の項を持つが path から dir(raw/・kizai/)が落ちて実体へ届かぬ。載せ忘れでなく ★書き方★ の疵。
3. **★乙 17 の「渡さなかつた」は「誤つて渡さなかつた」を意味せぬ。★** km-sengen の S2/S3 は條②④を鳴らす fixture(載せれば門が落ちる)・km-36 の 94_argv は臺帳の 1 秒前 = 門の argv。則の順序が字面で決めた。§7 に書く。
4. **★相違 1 は「紙が後から直つた」ではない。★** 紙の birth/mtime/ctime は悉く臺帳より前。臺帳の器が disk と違ふ中身(末尾 LF が一つ少ない)を hash した。何を hash したかは決められぬ(§5 に「何が在れば決まるか」)。
5. **★一走目の 343 は誤測でなく則の差。★** 己が 00_start に「2MB 超は開かぬ → 丙0」と書いた則の下では 343 が正しい。26 と揃へる為に則を変へ、変へた事を 30 の docstring と本紙に書いた。
6. **★乙5 は一走目の後に足した山である。★** 「渡したが讀めぬ形」は札の ㋑「名が讀手を破る」に在るが、己の則には無かつた。後から足した山は「何とでも分けられる」の入口ゆゑ、足す前(乙4 20)と後(乙4 17 + 乙5 3)の両方を書く。

## 1. 則(00_start 逐語は raw/00_start.txt・要約)
| 山 | 則 | 順 |
|---|---|---|
| 甲1 門の出目 | 相對 path が `(^\|/)mon/`・basename に `gate\|gatelog\|_mon\d`・`mon\d*[_.].*\.(out\|err\|rc)$` | 1 |
| 甲2 臺帳の器の出目 | basename に `manifest\|daichou` | 2 |
| 甲3 __pycache__ | path に `/__pycache__/` | 3 |
| 甲4 宣で員外 | 臺帳の非項行 or 紙の行に `員外\|ingai\|門の後\|載せぬ\|門控` が在り ★同じ行★ に (a) 相對 path 逐語 or (b) 親 dir + '/' | 4 |
| 乙1 届かぬ | 臺帳に ★同じ sha256★ の項が在る(path が届かぬ) | 5 |
| 乙5 讀めぬ行に載る | sha256 が臺帳の ★生の文字列★ に在る(項として讀めぬ行)―― ★一走目の後に足した★ | 6 |
| 丙1 同名別 sha | 臺帳に同じ basename の項・sha 違ふ | 7 |
| 乙2 名が器を破る | 相對 path に `"` `'` 改行 復帰(append.py togame = rc 3 相当) | 8 |
| 丙2 同秒 | file mtime(秒)= 臺帳 mtime(秒)(締めれば同分) | 9 |
| 乙3 門の後に生れた | file mtime > 臺帳 mtime | 10 |
| 乙4 器へ渡さなかつた | 上の何れにも当たらぬ(臺帳より前・名清く・sha も名も無い) | 11 |
| 丙0 測れぬ | 臺帳 mtime 無 / 開けぬ(一走目のみ「2MB 超」も此処) | − |

## 2. 三山(30・刻 02:47:04・母數 40 臺帳・配下 1532・非通常 4 除く)
| 山 | 本数 | byte 和 | 代表 |
|---|---|---|---|
| 甲1 門の出目 | 269 | 450,875 | a3 km-33 mon/*(209)・km-36 mon(14)・km-35(10)・km-43(9)… |
| 甲2 臺帳の器の出目 | 5 | 11,164 | soukantoku manifest.txt・km-38 kou/70_daichou_build.{out,err}・km-42 __pycache__/90_daichou…pyc・km-43 raw/91_daichou.stderr |
| 甲3 __pycache__ | 2 | 16,085 | km-35 ki/__pycache__/k01…pyc・km-42 ki/__pycache__/59_kaki…pyc |
| 甲4 宣で員外 | 9 | 11,800 | a(逐語)2 = km-38 kou/40_fudou.out・km-sengen ingai.txt / b(親 dir)7 = km-34 ki/92_soejou.py・km-38 jikken/build{,2,3,4,5}.err・km-38 kou/.!2271!42_fudou3.err |
| **甲 計** | **285** | **489,924** | |
| 乙1 届かぬ | 23 | 232,936 | B2_30 raw/* 10・B2_31 raw/* 9・karo B0_10 kizai/* 4 |
| 乙5 讀めぬ行に載る | 3 | 265,045 | B0_axis2 {desktop,phone,ipad}/walkthrough.webm |
| 乙2 名が器を破る | 0 | 0 | − |
| 乙3 門の後に生れた | 6 | 5,942 | km-34 sunaba/{ato_ids,mae_ids,chakudan_id}.txt・96_bin.{out,err}・97_yomikaeshi.out(+183〜+225 s) |
| 乙4 器へ渡さなかつた | 17 | 43,752 | B0_axis2 9(json/md)・soukantoku 3(log)・km-34 2(argv .lst)・km-36 1・km-sengen 2(fixture) |
| **乙 計** | **49** | **547,675** | |
| 丙1 同名別 sha | 0 | 0 | − |
| 丙2 同秒 | 2 | 15,495 | km-34 sunaba/argv34_182851.lst・km-sengen argv.txt |
| 丙0 測れぬ | 0 | 0 | (一走目は 7 = B12_16 raw/c_*.txt 6 + km-sengen 1 = 234,364,104 B・2MB 閾) |
| **丙 計** | **2** | **15,495** | 同分へ締めると 4(km-36 94_argv・km-34 argv34_182820 が乙4 から移る) |
| **総和** | **336** | **1,053,094** | = 載らぬ 336・差 0 |

### 2.1 臺帳ごと(載らぬ ≥1 の 15 本・30_sanzan_per_ledger.tsv)
| 紙 | 配下 | 載らぬ | 山 |
|---|---|---|---|
| ashigaru-mac-2_B0_axis2_20260908.md | 18 | 12 | 乙4 器へ渡さなかつた=9 乙5 讀めぬ行に載る(形が讀み手を破る)=3 |
| ashigaru-mac-2_B2_30_20260907.md | 10 | 10 | 乙1 届かぬ(同sha項あり)=10 |
| ashigaru-mac-2_B2_31_20260907.md | 9 | 9 | 乙1 届かぬ(同sha項あり)=9 |
| ashigaru-mac-2_km-43-lot48235904-no-gunshi-P | 38 | 1 | 甲1 門の出目=1 |
| ashigaru-mac-2_soukantoku291437_1_20260908.m | 6 | 6 | 乙4 器へ渡さなかつた=3 甲1 門の出目=2 甲2 臺帳の器の出目=1 |
| ashigaru-mac-3_km-33-hakarenu-wa-wa-no-dochi | 310 | 209 | 甲1 門の出目=209 |
| ashigaru-mac-3_km-34-touketsu-to-kotogotoku- | 67 | 18 | 丙2 同秒(門の前後 決められぬ)=1 乙3 門の後に生れた=6 乙4 器へ渡さなかつた=2 甲1 門の出目=8 甲4 宣で員外=1 |
| ashigaru-mac-3_km-35-atai-ga-kotogotoku-tada | 64 | 11 | 甲1 門の出目=10 甲3 __pycache__=1 |
| ashigaru-mac-3_km-36-mon-no-byte-wa-ga-fudou | 65 | 15 | 乙4 器へ渡さなかつた=1 甲1 門の出目=14 |
| ashigaru-mac-3_km-37-daichougai-wo-ingai-to- | 68 | 2 | 甲1 門の出目=2 |
| ashigaru-mac-3_km-38-kanou-to-itta-fudou-wo- | 205 | 15 | 甲1 門の出目=6 甲2 臺帳の器の出目=2 甲4 宣で員外=7 |
| ashigaru-mac-3_km-42-betsuwaku-54-hon-no-kiz | 65 | 8 | 甲1 門の出目=6 甲2 臺帳の器の出目=1 甲3 __pycache__=1 |
| ashigaru-mac-3_km-43-hanzezu-32-hon-wo-yomit | 125 | 10 | 甲1 門の出目=9 甲2 臺帳の器の出目=1 |
| ashigaru-mac-3_km-sengen-shita-hashira-wo-mo | 71 | 5 | 丙2 同秒(門の前後 決められぬ)=1 乙4 器へ渡さなかつた=2 甲1 門の出目=1 甲4 宣で員外=1 |
| karo_mac_B0_10_kizai_hozen_20260908.md | 5 | 5 | 乙1 届かぬ(同sha項あり)=4 甲1 門の出目=1 |

## 3. 乙(疵)一本ごと ―― 何故落ちたか(㋑・30_sanzan.tsv から器が引いた・49 本)
| 臺帳(紙) | 相對 path | bytes | mtime | 山 | 理由(器の出目・逐語) |
|---|---|---|---|---|---|
| ashigaru-mac-2_B0_axis2_20260908.md | desktop/pixel_diffs.json | 216 | 09-08T20:35:37 | 乙4 | file 09-08 20:35:37 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | desktop/walkthrough.webm | 87899 | 09-08T20:35:37 | 乙5 | 臺帳の生の行に sha 逐語 desktop/walkthrough.webm sha256=7a278da9bfa8386dff2f7c3b4d453d2958ec8d307d… |
| ashigaru-mac-2_B0_axis2_20260908.md | desktop/summary_table.md | 1297 | 09-08T20:35:37 | 乙4 | file 09-08 20:35:37 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | desktop/ready_timeouts.json | 3 | 09-08T20:35:37 | 乙4 | file 09-08 20:35:37 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | phone/pixel_diffs.json | 220 | 09-08T20:29:35 | 乙4 | file 09-08 20:29:35 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | phone/walkthrough.webm | 90065 | 09-08T20:29:35 | 乙5 | 臺帳の生の行に sha 逐語 phone/walkthrough.webm sha256=d694aed6bf9add7dbcb118f357399f4359eb46145aa2… |
| ashigaru-mac-2_B0_axis2_20260908.md | phone/summary_table.md | 1291 | 09-08T20:29:35 | 乙4 | file 09-08 20:29:35 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | phone/ready_timeouts.json | 3 | 09-08T20:29:35 | 乙4 | file 09-08 20:29:35 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | ipad/pixel_diffs.json | 221 | 09-08T20:30:58 | 乙4 | file 09-08 20:30:58 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | ipad/walkthrough.webm | 87081 | 09-08T20:30:58 | 乙5 | 臺帳の生の行に sha 逐語 ipad/walkthrough.webm sha256=1b0c14a6488009031d0ec6df18450bb25158aefa10133… |
| ashigaru-mac-2_B0_axis2_20260908.md | ipad/summary_table.md | 1288 | 09-08T20:30:58 | 乙4 | file 09-08 20:30:58 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B0_axis2_20260908.md | ipad/ready_timeouts.json | 3 | 09-08T20:30:58 | 乙4 | file 09-08 20:30:58 < 臺帳 09-08 20:39:30 名清く sha 無 |
| ashigaru-mac-2_B2_30_20260907.md | raw/09_stage2_e2eb83_GREEN_full.txt | 27266 | 09-07T23:24:37 | 乙1 | 臺帳の項 09_stage2_e2eb83_GREEN_full.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/01_propose_line_splits_idempotency_check.txt | 32045 | 09-07T23:24:37 | 乙1 | 臺帳の項 01_propose_line_splits_idempotency_check.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/02_const_fix_patch_saved_for_reapply.diff | 1928 | 09-07T23:24:37 | 乙1 | 臺帳の項 02_const_fix_patch_saved_for_reapply.diff |
| ashigaru-mac-2_B2_30_20260907.md | raw/00_worktree_baseline.txt | 1477 | 09-07T23:24:37 | 乙1 | 臺帳の項 00_worktree_baseline.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/04_stage6_roundtrip_RED.txt | 619 | 09-07T23:24:37 | 乙1 | 臺帳の項 04_stage6_roundtrip_RED.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/08_stage6_roundtrip_GREEN.txt | 631 | 09-07T23:24:37 | 乙1 | 臺帳の項 08_stage6_roundtrip_GREEN.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/05_stage2_e2eb83_RED_scoped_initial.txt | 5646 | 09-07T23:24:37 | 乙1 | 臺帳の項 05_stage2_e2eb83_RED_scoped_initial.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/06_stage2_e2eb83_RED_full.txt | 5187 | 09-07T23:24:37 | 乙1 | 臺帳の項 06_stage2_e2eb83_RED_full.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/03_stage1_vitest_RED.txt | 535 | 09-07T23:24:37 | 乙1 | 臺帳の項 03_stage1_vitest_RED.txt |
| ashigaru-mac-2_B2_30_20260907.md | raw/07_stage1_vitest_GREEN.txt | 476 | 09-07T23:24:37 | 乙1 | 臺帳の項 07_stage1_vitest_GREEN.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/04_vitest_RED_test_names.txt | 11899 | 09-07T23:56:35 | 乙1 | 臺帳の項 04_vitest_RED_test_names.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/05_e2e_b83_RED_test_names.txt | 51957 | 09-07T23:56:35 | 乙1 | 臺帳の項 05_e2e_b83_RED_test_names.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/08_dino_check_GREEN_final_15ep.txt | 1888 | 09-07T23:56:35 | 乙1 | 臺帳の項 08_dino_check_GREEN_final_15ep.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/01_apply_splits_script_log.txt | 3985 | 09-07T23:56:35 | 乙1 | 臺帳の項 01_apply_splits_script_log.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/00_propose_line_splits_full_before_apply.txt | 31755 | 09-07T23:56:35 | 乙1 | 臺帳の項 00_propose_line_splits_full_before_apply.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/03_dino_check_RED_baseline_15ep.txt | 2037 | 09-07T23:56:35 | 乙1 | 臺帳の項 03_dino_check_RED_baseline_15ep.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/06_dino_check_GREEN_attempt1_15ep.txt | 1866 | 09-07T23:56:35 | 乙1 | 臺帳の項 06_dino_check_GREEN_attempt1_15ep.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/02_propose_line_splits_idempotency_after_apply.… | 35286 | 09-07T23:56:35 | 乙1 | 臺帳の項 02_propose_line_splits_idempotency_after_apply.txt |
| ashigaru-mac-2_B2_31_20260907.md | raw/07_vitest_EXPECTED_diff.txt | 2909 | 09-07T23:56:35 | 乙1 | 臺帳の項 07_vitest_EXPECTED_diff.txt |
| ashigaru-mac-2_soukantoku291437_1_20260… | 12_vitest_baseline_after_relink.log | 9612 | 09-08T20:11:02 | 乙4 | file 09-08 20:11:02 < 臺帳 09-08 20:19:20 名清く sha 無 |
| ashigaru-mac-2_soukantoku291437_1_20260… | 13_dino_check_v2origin_relinked_port5182_ALLGREEN.l… | 1876 | 09-08T20:18:38 | 乙4 | file 09-08 20:18:38 < 臺帳 09-08 20:19:20 名清く sha 無 |
| ashigaru-mac-2_soukantoku291437_1_20260… | 11_vitest_v2origin_after_relink.log | 9620 | 09-08T20:11:02 | 乙4 | file 09-08 20:11:02 < 臺帳 09-08 20:19:20 名清く sha 無 |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/ato_ids.txt | 1102 | 09-13T18:32:12 | 乙3 | file 09-13 18:32:12 > 臺帳 09-13 18:28:51 (+201s) |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/mae_ids.txt | 1073 | 09-13T18:32:03 | 乙3 | file 09-13 18:32:03 > 臺帳 09-13 18:28:51 (+192s) |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/argv34_182547.lst | 5191 | 09-13T18:25:47 | 乙4 | file 09-13 18:25:47 < 臺帳 09-13 18:28:51 名清く sha 無 |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/97_yomikaeshi.out | 188 | 09-13T18:32:36 | 乙3 | file 09-13 18:32:36 > 臺帳 09-13 18:28:51 (+225s) |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/96_bin.out | 634 | 09-13T18:31:54 | 乙3 | file 09-13 18:31:54 > 臺帳 09-13 18:28:51 (+183s) |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/argv34_182820.lst | 5715 | 09-13T18:28:20 | 乙4 | file 09-13 18:28:20 < 臺帳 09-13 18:28:51 名清く sha 無 |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/chakudan_id.txt | 29 | 09-13T18:32:12 | 乙3 | file 09-13 18:32:12 > 臺帳 09-13 18:28:51 (+201s) |
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/96_bin.err | 2916 | 09-13T18:31:54 | 乙3 | file 09-13 18:31:54 > 臺帳 09-13 18:28:51 (+183s) |
| ashigaru-mac-3_km-36-mon-no-byte-wa-ga-… | 94_argv_all_200220.txt | 7146 | 09-13T20:02:20 | 乙4 | file 09-13 20:02:20 < 臺帳 09-13 20:02:21 名清く sha 無 |
| ashigaru-mac-3_km-sengen-shita-hashira-… | hei/shiryou/S3_eof_nashi.txt | 24 | 09-13T04:59:24 | 乙4 | file 09-13 04:59:24 < 臺帳 09-13 05:18:30 名清く sha 無 |
| ashigaru-mac-3_km-sengen-shita-hashira-… | hei/shiryou/S2_matsubi_kuhaku.txt | 26 | 09-13T04:59:24 | 乙4 | file 09-13 04:59:24 < 臺帳 09-13 05:18:30 名清く sha 無 |
| karo_mac_B0_10_kizai_hozen_20260908.md | kizai/karo_mac_bundle5.sh | 2563 | 09-08T15:53:55 | 乙1 | 臺帳の項 karo_mac_bundle5.sh |
| karo_mac_B0_10_kizai_hozen_20260908.md | kizai/karo_mac_mark.py | 1015 | 09-08T15:53:55 | 乙1 | 臺帳の項 karo_mac_mark.py |
| karo_mac_B0_10_kizai_hozen_20260908.md | kizai/karo_mac_unread.py | 445 | 09-08T15:53:55 | 乙1 | 臺帳の項 karo_mac_unread.py |
| karo_mac_B0_10_kizai_hozen_20260908.md | kizai/karo_mac_read.py | 9521 | 09-08T15:53:55 | 乙1 | 臺帳の項 karo_mac_read.py |
- ★rc=3(追記器が拒んだ)は 0 本 ―― 測れぬ。★ karo_mac_manifest_append.py の生(birthtime)は 2026-09-17 01:40:42 で、40 本の臺帳は悉く其れより前(0/40)。乙2 の 0 は「器なら拒む名(引用符・改行・復帰)が今の配下に無い」の意。空白を含む名は則から外した(括れば讀める故)―― 本数は数へて居らぬ。
- ★不明 = 0 本 ―― 乙4 が「上の何れにも当たらぬ」の受け皿ゆゑ、不明が零なのは則の形が産んだ零である(不明を隠したのではなく、不明が乙4 の名で出て居る)。∴ 乙4 17 の内 幾つが「誤り」で幾つが「意図して渡さず」かは §7 の通り決めて居らぬ。

## 4. 丙(決められぬ)―― 零でない(㋒)
| 臺帳(紙) | 相對 path | bytes | mtime | 山 | 理由 |
|---|---|---|---|---|---|
| ashigaru-mac-3_km-34-touketsu-to-kotogo… | sunaba/argv34_182851.lst | 6239 | 09-13T18:28:51 | 丙2 | file 18:28:51 臺帳 18:28:51 |
| ashigaru-mac-3_km-sengen-shita-hashira-… | argv.txt | 9256 | 09-13T05:18:30 | 丙2 | file 05:18:30 臺帳 05:18:30 |
- 同秒 2 → 同分へ締めると 4: km-36 `94_argv_all_200220.txt`(20:02:20・臺帳 20:02:21)と km-34 `sunaba/argv34_182820.lst`(18:28:20・臺帳 18:28:51)が乙4 から丙2 へ移る。★何れも門の argv の写しと見える(名に gate の語が無いゆゑ甲1 に当たらぬ)―― 「同分」で丙へ来る物は「門と同じ手続きの産物」の匂ひがする。之は則の緩さの證であり、丙が零でない事の證でもある。★
- 丙1(同名別 sha)0・丙0 0。二走目で丙0 が零になつたのは、2MB 閾を外して 234 MB を hash した故(一走目 7 本)。

## 5. 相違 1 の決着(㋓・raw/32_1byte.txt 逐語)
- 紙 `queue/reports/ashigaru-mac-2_soukantoku291437_1r_20260908.md` / 臺帳 `…_1_20260908_evidence/manifest_v2origin.txt` の行(逐語): `queue/reports/ashigaru-mac-2_soukantoku291437_1r_20260908.md sha256=5229…8330 bytes=22046 lines=354`。実 sha 24e7…0d6 bytes 22047・差 1 B。
- ★① 実の 22047 B から一 byte を抜いた 22047 通りの sha256 の内、宣 sha に当たる位置 = 2 箇所 = 22045 と 22046(0 起点)・byte は共に 0x0a(LF)★。紙の末尾は `…宣言)\n\n`(行 354 の末尾 LF + 空行の LF)で、★同じ byte の連ゆゑ「連の何れか」までしか決まらぬが、★1 byte の正体 = 改行 LF★ は決まる。∴ 宣 sha = 「末尾の LF が一つ少ない紙」の sha。字でも空白でもない。
- ★② 紙と臺帳の何れが後か★: 紙 birth 20:19:01.658234 / mtime 20:19:01.658385 / ctime 20:19:01.658618 ; 臺帳 birth 20:19:20.812753 / mtime 20:19:20.812864。★臺帳が 19 秒後★。★紙の ctime > 臺帳 mtime = False★ ―― cp -p は mtime を保つが ctime は保たぬ ∴ 紙は臺帳より後に inode を触られて居らぬ。∴「紙が後から直つた」は ★否★。
- ★③ 決められぬ物★: 臺帳の器が ★何を★ hash したか。disk の紙は臺帳より前から今の 22047 B の儘なのに、臺帳は 22046 B の中身を宣して居る ―― 器が disk でなく別の写し(末尾 LF を一つ落とした文字列・stdin・正規化後の text)を hash した、としか読めぬ。★決めるには★: a2 の臺帳の器(manifest_v2origin.txt を書いた script)か其の走りの log が要る。soukantoku の _evidence 配下 6 本に器は無い(log 4・manifest 2)。
- ④ git: 紙は untracked(rc 1)・実の中身の blob sha1 b68e2d2… は git に無い(cat-file -e rc 1)・同名の写しは queue/reports・docs/evidence に 0 本。∴ 宣 sha の 22046 B の原本は此の repo の何処にも無い(歩いた範囲で)。

## 6. 己(㋔・raw/33_onore.txt)
- 40 本の内 ★己(ashigaru-mac-1_)の舊紙 21 本★(B12_16〜27・B2_tanaoroshi・B3_rig・J1R/J1/J4/J5・KM_8c2d7119・km-0fc26f2f・km-29c7529f)は母數に ★入つて居り★、載らぬは悉く 0(甲 0/乙 0/丙 0)。
- 己の km-60〜65 の 6 束(配下計 589 本)は 40 の ★外★ ―― 兄弟 `_manifest.txt` 形(別所でない)ゆゑ、21 の定義が外した。★除いたのは己でなく定義である。本数を書く: 87+100+83+122+89+108 = 589。★
- 本弾の束(docs/evidence/km-66…)は 33 の刻(02:47:28・門の前)で 28 本 157,697 B。門の後に ★同じ則★(30 --one)を己の束(根 raw/・臺帳 = 本弾の臺帳)へ掛け、己の器・己の log が何の山へ入るかを `_after/33_onore_after.txt` に出す。★期待: 甲1(門の出目 = 60_/61_)のみ。乙3(門の後)が出れば追ひ便 7 の再犯である ―― 追ひ便 6 で告げる。★

## 7. 意味せぬ事(㋕・本弾の数が言はぬ事・9)
1. **甲 285 ≠ 其の臺帳の書き手が員外と宣した 285。** 甲1〜3(276)は ★名の形★ で当てた。宣を讀んで当てたのは甲4 の 9 のみで、内 7 は「親 dir + '/' が員外の語と同じ行に在る」の緩い一致(例: km-34 `ki/92_soejou.py` は `ki/10_ingai.py` を語る行で当たつた)。
2. **乙4 17 ≠ 誤つて渡さなかつた 17。** km-sengen `hei/shiryou/S2_matsubi_kuhaku.txt`/`S3_eof_nashi.txt` は條②④を鳴らす fixture(載せれば門が落ちる = 載せぬのが正)・km-36 `94_argv_all_200220.txt` は臺帳の 1 秒前 = 門の argv。則が字面(名・sha・mtime)で決めた故、意図は讀んで居らぬ。
3. **乙3 6 ≠ 疵 6。** 凍結の刻を ★臺帳の mtime★ と置いた(門控の刻ではない)。km-34 の `sunaba/` は砂場と名乗るが、行に 員外 の語が無ければ甲4 に当たらぬ。
4. **丙 2(4)≠ 決められぬ物の全数。** 丙2 は同秒/同分でしか測つて居らぬ。乙1 23 の「dir を省いた項」が意図(基点 = raw/ を宣した)か誤りかは臺帳の宣を讀まねば決まらぬ ―― 讀んで居らぬ。
5. **336 動かぬ ≠ 40 本の束の中身が動いて居らぬ。** 本数(1532/336)が同じでも sha・mtime の同一は比べて居らぬ。
6. **一走目 343 ≠ 誤測。** 2MB 閾は己が宣した則で、其の下では 343 が正しい。26 と揃へる為に則を変へた事を書いた(30 docstring ⑴)。
7. **rc=3 実測 0 ≠ 拒まれた名が無い。** 追記器が無い刻の臺帳ゆゑ測れぬ。乙2 0 は今の名に引用符・改行が無いの意。
8. **相違 1「臺帳が後」≠ 臺帳が誤り。** 器が別の写し(正規化後の text 等)を正しく hash した可能性は残る。誤りなのは「disk と違ふ物を disk の名で宣した」事であり、其れも器の宣を讀まねば断じ得ぬ。
9. **甲4 の一致 ≠ 員外の宣。** 「同じ行に語が在る」だけで当てた ―― 「員外でない」と書いた行も当たる(否定を讀まぬ)。

## 8. 己の疵(7)
1. 己の箱の auto-recovery 便(msg_auto_recovery_20260917_023817_df8c9e7f)を束の前(02:38)に ★手★ で read: true にした(65 は讀み返すのみ)。
2. 一走目に 2MB 閾を置き、26 と器を揃へずに 343 を出した → .first に残し則を直した(30 docstring ⑴)。
3. 乙5 は一走目の後に足した山(30 docstring ⑵)―― 「後から作れば何とでも分けられる」の入口。足す前と後の両方を書いた(§0 断 6)。
4. 00_start(則・宣)は器でなく手で書いた(kaki 経由・行末空白/CR/EOF は器の作法)。
5. 甲4b(親 dir)は緩い ―― `ki/` の三字で `92_soejou.py` を員外にした。則を先に書いた故其の儘数へ、緩さを §7-1 に書いた。
6. cwd が cd で二度動いた(worktree ↔ main 樹)―― 器は絶対 path で書いた故出目に影響は無い筈だが、其れを測つては居らぬ。
7. 62(便の器)の DRY が便1/3/4 を 314/335/341 字で捕へた ―― 門の前ゆゑ直した(字数の器は鎖の前・法の通り)。捕へた事自体は疵でなく、300 を超える便を初めに書いた事が疵。

## 9. 据ゑず・触れず
- 据ゑず(scripts/ ~/bin settings.json hook instructions/ 0 字・門・照合器・追記器は讀む/走らせるのみ・60 が前後の sha16 で示す)/ 他席の臺帳・紙・箱に 0 字 / DB 0(sb 0 回)/ git は rev-parse・ls-files・cat-file -e のみ(commit/push 0・add -f は納めの後に己の束のみ)/ tmux send-keys 0 / 非通常 file は S_ISREG で除き本数を宣した(配下 4)/ FIFO に触れず / rc は pipe 越しに取らず 10_run が直採 / 臺帳は append.py のみが書き 手書き 0。
- 在處: worktree `/Users/momizimac/multi-agent-shogun/.claude/worktrees/karo-mac-a1/docs/evidence/km-66-noranu-336-20260917/`(枝 karo-mac/a1-r56・HEAD 8c9fb3d)。項の path は main 樹の根からの相對 ―― worktree の根から引くなら頭の `.claude/worktrees/karo-mac-a1/` を落とす(50_sengen.txt に宣)。

## 10. 出處
raw/00_start.txt(起・宣 ETA・則逐語)/ 05_chakushu.txt(着手便)/ 30_sanzan.{txt,tsv,_per_ledger.tsv}(三山・二走目)/ 30_sanzan.first.*(一走目 343)/ 32_1byte.txt / 33_onore.txt / 50_sengen.txt(員外・門の後の名の宣)/ 50_build_manifest.out / 59_prescan.out / 60_gate_rcs.txt + 60_gate_top.r66.txt(門控)/ 65_kidoku.txt / _after/99_after_gate.txt・33_onore_after.txt・62_report_body.txt・63_sent.txt・96_after_send.txt・63b_sent.txt(門の後・根の外)。
