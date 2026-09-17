# 第52弾 納め ―― ★閾20箇所6file の母數を確定せよ★

★基点(臺帳の根)= 本束 `docs/evidence/km-52-shikii-no-bosuu-wo-kakutei-seyo-20260917/` の ★束内相対★(新法・總監督裁 seq322699)。臺帳の行は `path=ki/…` の形である。★
席=專任3(足軽mac3号) ／ 下知=家老mac 第52弾(msg_20260917_085508_70e3a903・2026-09-17T08:55:08)
凍結点 = ★commit 6dbe09e67c045da1a86c59cd023460bb125d461e★(一手目に固定・nama/00_kotei.txt)

---

## 冠 ―― 一枚で言ふと

| 問 | 家老の宣 | ★當席の實測★ | 差 |
|---|---|---|---|
| file 數 | 6 | ★6(凍結点)★ / ★7(今の disk)★ | 凍結点は ★再現する★。disk は +1 file |
| 箇所 數 | 20 | ★22(fix_threshold の宣言)★ ／ ★21(内 比較器へ渡る物)★ | ★+2 ／ +1★ |

★20箇所は再現せぬ。6file は凍結点でのみ再現する。★ 差の一本一本は ㋐② に file:行 で挙げた。

---

## ㋐① ★「閾を読む箇所」の判定条件 ―― 逐語★

器の冠に同じ字で書いて在る(ki/32_kessai3.py / ki/23_bosuu4.py)。逐語:

```
甲 file は 凍結点の樹(又は git ls-files)に在り、docs/evidence/ の下に無い。
乙 其の file 内に ★`fix_threshold <名> <既定> <受皿>` の呼★ が在る。
   呼の引数が `"$_n" "$_d" "$_n"` の形(loop 呼)である時は、
   直前の `for _t in NAME:DEF …` の一覧を展開して ★名の一本一本★ を数へる。
   ―― 之が「閾を読む箇所」の ★guard 側★ の定義である。單位=(file, 環境変数名)。
丙 其の名か其の受皿が、同 file 内で ★数値比較器の項★ に立つか否かを別欄で刷る。
   数値比較器 = `項 -eq|-ne|-lt|-le|-gt|-ge 項`(test/[/[[) 及び `(( … ))` / `$(( … ))` の中。
   ★丙は母數を削らぬ★ ―― 「読む箇所」と「比較へ渡る箇所」は別の數であり、両方刷る。
   ★一跳びの別名を辿る★(純粋な写しの代入のみ・二跳び以上は辿らぬ)。
```

★單位は「行」ではなく (file, 環境変数名) の組である。★ 同じ名が十行に出ても一箇所。行數は別欄に刷る。

★素で比べる側(guard を通らぬ箇所)の定義★ は ki/23_bosuu4.py の冠に別途 逐語で在り、
`${NAME:-d}` / `${NAME-d}` / `${NAME:=d}` / `fix_threshold` / 代入の無い裸の `$NAME` の何れかで現れ、
且つ其の名か受皿が数値比較器の項に立つ物 ―― と宣して在る。

---

## ㋐② ★6file / 20箇所 は再現するか ―― 否。差を一本づつ★

### 再現する物
★6 file は凍結点で完全に再現する。★ 加へて其の六本は ★凍結点と disk で byte 同一★ である
(sha16: inbox_watcher=15ac9f97f473245d / agent_health_check=7d11ba9f852ac759 /
 enter_restart_common_watchdog=f92cd54e09736a4e / context_usage_warn=3010defd413a3479 /
 karo_mac_gate4=95b027ea5e4f0fc5 / karo_mac_dasumae_gate=e11f0d0142549086)。
∴ ★此の六本に関する限り、數は版に依らぬ。★

### 再現せぬ物 ―― 差は四本
★差① 母數が 22 で在る(家老の 20 に対し +2)。★
  凍結点の宣言を悉く挙げると 22 本(内訳 = inbox_watcher 10 / agent_health_check 3 /
  enter_restart_common_watchdog 3 / context_usage_warn 2 / karo_mac_gate4 2 / karo_mac_dasumae_gate 2)。
  全 22 本の file:行 と 既定・受皿・比較行 は ★nama/32_kessai3.raw★ に一覧で在る。

★差② 22 の内 一本は「比較器の項に立たぬ」―― 之を除けば 21。★
  逐語で名指す:
  `scripts/checks/karo_mac_dasumae_gate.sh:77` `fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO`
  ―― 受皿 `SAFE_SIZE_TMO` は `scripts/checks/karo_mac_dasumae_gate.sh:96` で
  `"$TIMEOUT_BIN" "$SAFE_SIZE_TMO" stat -f %z -- "$r"` の ★引数★ に立つのみで、
  ★数値比較器の項には一度も立たぬ★。
  ∴ 「閾を読む箇所」ではあるが「閾を ★比較へ渡す★ 箇所」ではない。22 → 21。

★差③ 21 と 20 の差 一本 ―― 之が最後の一本である。★
  `scripts/inbox_watcher.sh:177` `ASW_PHASE`(既定 2・比較 `scripts/inbox_watcher.sh:216` と `:217`)
  逐語 L216: `ASW_DISABLE_NORMAL_NUDGE=${ASW_DISABLE_NORMAL_NUDGE:-$([ "${ASW_PHASE}" -ge 2 ] && echo 1 || echo 0)}`
  ―― 之は「限度(閾)」ではなく ★段の番号(phase 1/2/3)★ である。
  ★之を除けば 20箇所/6file で家老の宣と完全に一致する。★
  但し當席の定義(㋐①)では ★env 由来の値を `-ge` へ渡して居る★ 以上 21 が當席の數である。
  ★何れを採るかは家老の裁を仰ぐ ―― 當席は丸めぬ。★

★差④ 母數の外 ―― 今の disk には ★7本目の file★ が在る。★
  `scripts/redundancy/shogun_report_watcher.sh:78`
  `fix_threshold SHOGUN_REPORT_WATCHER_COOLDOWN 60 COOLDOWN_SEC`(比較 `:73` と `:328`)
  ―― 凍結点 6dbe09e6 の同 file には fix_threshold が ★一つも無い★
  (sha16 凍結点=0f3a5b39da990d90 / disk=a82e877eced423ad ―― ★七本中 此の一本だけが動いて居る★)。
  ∴ ★「6file」は凍結点でのみ真であり、今の disk では 7file / 23箇所(比較へ渡る物 22)である。★

---

## ㋐③ ★既に guard を通る箇所 / 未だ素で比べる箇所★

| 側 | 箇所 | file | 實測の出所 |
|---|---|---|---|
| ★甲 guard を通る★(裁322952 甲乙) | ★22★(比較へ渡る物 21) | 6 | nama/32_kessai3.raw |
| ★乙 未だ素で比べる★ | ★52★(式を取れた物・全体は 91−22=69) | 21 | nama/42_hatan2.raw |

★甲の實測結論 ―― guard は効いて居る。★
毒六形(未設定/空文字/空白のみ/全角数字/2^63超/先頭空白)を ★22本 悉くに当てた★ 結果、
★閾が非数の儘 残つた本数 = 0★。空文字・空白のみ・全角数字・2^63超 では悉く既定へ倒れ、
且つ ★倒した旨を刷つて居る(鳴=1)★。未設定は context_usage_warn の意匠(裁 seq323895㋐)通り ★黙つて★ 既定へ倒れる。
先頭空白 `' 120'` は ★倒れず素通りする★ ―― 之は疵ではない。test(1) は先頭空白を整数の項として受ける
(當席の第一走は之を Python の `str.isdigit` で「非数」と誤判した ―― 疵J・下記)。

★乙の實測結論 ―― 52本中 ★49本★ が實際に fail-open する。★
毒別の内訳(rc=2 に成つた本数): 空白のみ 49 / 全角数字 49 / 2^63超 49 / 未設定 34 / 空文字 34 / 先頭空白 2。
★rc=2 は「偽」ではない ―― if も elif も偽に成り、★黙つて else へ落ちる★。之が fail-open の機構である。★

---

## ㋐④ ★重い順 ―― 家老が当てる順★

重さ = ⑴呼ばれる回数 ⑵落ちた時の害 の積で並べた。

★第一 `scripts/karo_overload_monitor.sh` ―― 12箇所 悉く素・悉く fail-open★
  名附の閾 7本 = KARO_UNREAD_THRESHOLD(:438) / KARO_LATENCY_THRESHOLD_SEC(:439) /
  DISPATCH_LATENCY_THRESHOLD_SEC(:440) / PARALLEL_CMD_NEW_THRESHOLD(:441) /
  UNSTARTED_SUBPHASE_THRESHOLD(:442) / COOLDOWN_SEC(:472) / ALERT_CAP_PER_HOUR(:481)。
  加へて左項 m1〜m5(:438-442)も素。★12/12 が毒五形で rc=2★。
  害 = 家老の過負荷警報が ★鳴らなく成る★(else へ落ちる = 警報を出さぬ側へ倒れる)。
  ★之が最も重い ―― 「黙る」方向の fail-open だからである。★

★第二 `scripts/inbox_watcher.sh` の素の側 ―― 9箇所★
  FIRST_UNREAD_SEEN(:243) / LAST_NUDGE_TS(:305) / NEW_CONTEXT_SENT(:637) /
  LAST_APPROVAL_ALERT_TS(:898) / LAST_CLEAR_TS(:917) / STARTUP_PROMPT_SENT(:1435) /
  _token_int(:1622) / _th_unset_told(:148) / _ft_v(:156)。
  呼ばれる回数は艦隊で最多(inbox 事象毎・timeout tick 毎)。
  害 = 段の判定が狂ふ。★但し名附の閾10本は既に guard 済★ ―― 残るは状態変数側である。
  ★_ft_v と _th_unset_told は guard 自身の内部であり、env からは来ぬ(疵M・下記)。★

★第三 `scripts/agent_health_check.sh` の素の側 ―― 5箇所★
  INSERT_COUNT(:231) / n(:253) / max_tokens(:378) / _th_unset_told(:109) / _ft_v(:117)。
  `[ "${n:-0}" -gt 10 ]`(:253) は ★裸の 10 と比べる閾★ で、n が SSH 越しの数へである。

★第四 `scripts/watchdogs/enter_restart_common_watchdog.sh` ―― 2箇所(guard 内部のみ)★

★第五以下(各1〜2箇所)★ scripts/ratelimit_check.sh / scripts/inbox_write.sh /
  scripts/agent_periodic_push.sh / scripts/audit_meta_codex.sh /
  scripts/checks/ephemeral_worktree_hygiene.sh / shim/hakudokai/hakudokai_activity_monitor.sh。

★最低(当てるな、と當席は言ふ)★ tests/e2e/*(4箇所) / scripts/archive/*(3箇所) /
  first_setup.sh(1・BASH_VERSINFO で fail-open せぬ) /
  queue/reports/…km-39…evidence/ki/15〜17_hi_suu_no_shikii*.sh(6箇所) ―― ★後者は當席自身の旧束の器である★。

---

## ㋑ ★fail-open に成る入力 ―― ★当てて★ 数へた★

「当てずに数へるな」に従ひ、★数へた箇所の一つ残らずに毒を實際に当てた★。器 = ki/42_hatan2.py。
guard の寫し = ki/41_guard_utsushi.sh(凍結点 context_usage_warn.sh L32-L75 の ★逐語の寫し★)。
★生器は一行も走らせて居らぬ ―― 比較式のみを取り出して別 shell で走らせた(作法⑴ 讀取のみ)。★

毒六形 = ①未設定 ②空文字 `''` ③空白のみ `' '` ④全角数字 `１２０` ⑤2^63超 `99999999999999999999` ⑥先頭空白 `' 120'`

代表の名指し(全数は nama/42_hatan2.raw):

| 箇所 | 当てた毒 | 出目 |
|---|---|---|
| karo_overload_monitor.sh:438 KARO_UNREAD_THRESHOLD | `99999999999999999999` | ★rc=2 ―― 警報を出さぬ側へ黙つて落ちる★ |
| karo_overload_monitor.sh:472 COOLDOWN_SEC | `''`(空文字) | ★rc=2★ |
| karo_overload_monitor.sh:481 ALERT_CAP_PER_HOUR | `１２０`(全角) | ★rc=2★ |
| inbox_watcher.sh:243 FIRST_UNREAD_SEEN | 未設定 | ★rc=2★ |
| inbox_watcher.sh:1435 STARTUP_PROMPT_SENT | `''` | ★rc=2★ |
| agent_health_check.sh:253 n | `' '`(空白のみ) | ★rc=2★ |
| agent_health_check.sh:378 max_tokens | `99999999999999999999` | ★rc=2★ |
| ★inbox_watcher.sh:177 ESCALATE_PHASE1(guard 済)★ | `99999999999999999999` | ★閾=120 へ倒れ、★倒した旨を刷る★(鳴=1)★ |
| ★karo_mac_dasumae_gate.sh:81 DASUMAE_MAX_BYTES(guard 済)★ | `１２０` | ★閾=10485760 へ倒れ、鳴=1★ |

★fail-open に成らなんだ 3本(乙側)★:
  `first_setup.sh:359` BASH_VERSINFO(shell 自身が入れる値・env から入らぬ)
  `scripts/inbox_watcher.sh:1614` LAST_TOKEN_WARN_TS ―― ★式の取出しが壊れて居る(疵L)★
  `shim/hakudokai/hakudokai_activity_monitor.sh:200` AUDIT_CHECK_INTERVAL ―― 同上
  ★∴ 「fail-open せぬ」と断ずるな。3本の内 2本は ★測れて居らぬ★ である。★

---

## ★己の疵 ―― 名指して先に置く★

★疵0(便の條)★ ★着手便が 361字 ―― 一便 300字の條を 61字 超えた。★
  加へて ★字数を送信と同じ一行で測つた★ 故、測りが破れを止められなんだ。
  ―― memory「Measure letter length before writing the sender」の實例を、其れを持ちながら踏んだ。
  ★本紙の納め便は、送信の ★前★ に別途測る。★

器の疵(全て本弾の中で當席が見附け、直した ―― 倒れた走は消さず `.first` に残して在る):
  ★疵A★ 代理の伝播が path 組立の代入まで拾ひ、數を膨らませた(576→94)。
  ★疵B★ `;` で区切つた行の ★最初の代入しか見なんだ★。
  ★疵C★ 「比較行に名が在る」を「比較器の項に立つ」と混同した。
  ★疵D★ 区切子が `{` `}` で割れ、`${MAX_TYPING_SKIP:-5}` を三片に砕き
        ―― ★inbox_watcher の guard 済 10本の内 5本を黙つて落とした★。
  ★疵E★ 受皿(WARN_BYTES 等)を別箇所として二重に数へた(代理落し 11本)。
  ★疵F★ `(( … ))` の中では変数が `$` 無しで書かれる故、ESCALATE_COOLDOWN が母數へ入らなんだ。
  ★疵G★ `git ls-tree` は binary file も出す ―― text=True の subprocess が UnicodeDecodeError で倒れた。
  ★疵H★ 丙が ★一跳びの別名★ を追はず、偽陰性 4本(NUDGE_COOLDOWN_SEC/_CODEX/_CLAUDE/MAX_TYPING_SKIP)。
  ★疵I★ guard の寫しを `num_same_op` から切つた故 ★`_th_say` を落とし★、
        鳴の欄が悉く `command not found` に成つた ―― ★「鳴つた」ではなく「壊れた」を測つて居た。★
  ★疵J★ 「閾が非数か」を Python の `str.isdigit` で判じ、`' 120'` を非数と誤判した
        ―― ★判ずるのは bash 自身でなければならぬ。★
  ★疵K(未直・殘つて居る)★ ki/23_bosuu4.py の stderr の冠が ★「母數(第三走)」の儘★ である(第四走なのに)。
  ★疵L(未直)★ 比較式の取出しが `$(( … ))` を跨ぐと壊れる(上記 2本)。
  ★疵M(未直)★ `eval` で代入される変数(`_ft_v`)を「代入無し=env 由来」と看做す
        ―― ∴ 乙の 52本には guard 自身の内部 7本(`_ft_v`×4・`_th_unset_told`×3)が混じつて居る。

---

## ★本弾が意味せぬ事★

⑴ ★「閾を読む箇所を悉く数へた」ではない。★ 數へたのは shell file のみである。python・yaml・plist の中の閾は歩いて居らぬ。
⑵ ★「guard が効いて居る」は寫しで測つた。★ 生器其の物は一行も走らせて居らぬ(作法⑴)。
   本番の `fix_threshold` が寫しと同一である事は sha で示したが、★実行時の env まで同じとは言つて居らぬ。★
⑶ ★「52本が素である」は式を取れた物の數である。★ 取れなんだ物(69−52=17)は ★測れて居らぬ★ であつて「素でない」ではない。
⑷ ★「呼ばれる回数」は測つて居らぬ。★ ㋐④ の重さは ★file の役目からの見立て★ であり、實測の呼数ではない。
⑸ ★disk の 7本目は凍結点の外である。★ 家老の 20/6 は凍結点で採る限り正しい向きであり、當席の +1 は ASW_PHASE 一本の読みに帰する。
⑹ ★毒は六形しか当てて居らぬ。★ 負数・小数・`0x10`・改行混じり・8byte 境界丁度 は当てて居らぬ。

---

## 宣⇔實

起点 = 着手便自身の timestamp `2026-09-17T08:58:26` ／ 宣 ★85分★ ／ 端点 = 本納め便自身の timestamp。
差は納め便に符號付きで書く。

---

## ★門 と 臺帳後の産物★

★本紙は門に掛ける ★前★ に閉ぢる。★ ∴ 本節は「門をどう当てたか」であり、
★本紙自身を含む最終走の rc は本紙には書けぬ★(書けば己を含む數を己で書く事に成る)。
最終走の rc は ★納め便★ と `nama/5x_mon_*.err` に在る。

⑴ ★出す前 門(karo_mac_dasumae_gate.sh)★
   第一走 = ★rc=1・條④(EOF改行丁度1)が 6本で鳴つた★ ―― `nama/50_mon_dasumae.first.err`。
   鳴つた 6本 = nama/20_bosuu.first.raw / 21_bosuu2.raw / 22_bosuu3.raw / 23_bosuu4.raw /
                31_kessai2.json / 32_kessai3.json。
   因 = ★生の `>` 捕獲が ki/10_kaki.py を通つて居らなんだ★(memory「Raw > capture bypasses normalization」)。
   正し = 中身は一字も書き換へず kaki へ通しただけ ―― ★6本悉く +1 byte(EOF改行 1本)のみ★。
   前後の sha16 と bytes は `nama/51_seisu.txt` に全件。★倒れた走は消して居らぬ(作法⑺)。★
   第二走 = ★rc=0(36本 通・條① 一致36/相違0/実体無0)★ ―― `nama/52_mon_dasumae.err`。
   ★基点の口★ = `KM_GATE_MANIFEST_BASE=.` ―― 束内相対の臺帳は之無しでは條①が悉く落ちる。

⑵ ★押す前 門(karo_mac_gate4.sh)★ ―― ★rc=1 の儘である。「通」と読むな。★
   落ちて居るのは ★條①(遠に枝 origin/ashigaru-mac-3/km-51-… が無い)一本のみ★。
   條④(diff --check)=0 ／ 條⑤(寸法)=通 ／ staged=40 file。
   ★之は「押し先」の話であり、押すのは家老である(作法⑼)。當席は staged に載せる所迄しか行かぬ。★
   `nama/53_mon_gate4.err`(staged 0 の走) / `nama/55_mon_gate4b.err`(staged 40 の走)。

⑶ ★門 v7(karo_mac_gate7.sh)★ ―― 本紙に当てて ★rc=0★(`nama/54_mon_gate7.err`)。

⑷ ★臺帳の外に在る産物 ―― 名指す★
   `nama/52_mon_dasumae.err` / `nama/53_mon_gate4.err` / `nama/54_mon_gate7.err` /
   `nama/55_mon_gate4b.err` および ★本節を足した後の最終走の log★。
   ―― 之等は ★臺帳を建てた後に門自身が産む物★ であり、臺帳へ入れれば
   ★門が己の log を照合する自己言及★ に成る(memory「The gate-log burner breaks 條① by self-reference」)。
   ∴ ★除いたのではなく、臺帳より後に生まれた★。staged には載る(40 = 臺帳37 + 門の log 3)。

⑸ ★疵N(本節で名指す)★ ―― 6本を正す第一走で `for f in $BAD` と書き、
   ★zsh は語分割せぬ故 一本も当たらなんだ★(memory「zsh の parse 罠」)。
   file の無傷を確かめてから配列で引き直した。★rc は 0 で無かつたが、之も「通つた様に見える」形であつた。★
