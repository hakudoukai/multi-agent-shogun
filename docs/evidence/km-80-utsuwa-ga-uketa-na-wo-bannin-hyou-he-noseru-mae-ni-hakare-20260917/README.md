# 第76弾 ―― 器が受けた名を、番人表へ載せる前に測れ: inbox_watcher.sh の ASW_PROCESS_TIMEOUT は「受ける口」に在つて「守る表」に無い。毒六形を写し器へ当て、直し形は紙にのみ書く

- 弾: km-80(家老便 msg_20260917_095405_64ec967a・札 sha16 cc538102168bd323 48行)/ 束 docs/evidence/km-80-utsuwa-ga-uketa-na-wo-bannin-hyou-he-noseru-mae-ni-hakare-20260917 / 書手 ashigaru-mac-1 / 宛 karo-mac(監査 gunshi-mac へ pc_handshake)
- 裁: seq324588(親 324585)⑵「inbox_watcher.sh の ASW_PROCESS_TIMEOUT を宣どおり守らせる」の ★当てる前の測り★。1弾=1file・負テスト両対照・repo の器へ 0 字(束の中に建てた)・稼働中 watcher 不觸(裁 323062⑷)。
- 刻: 紙を書いた刻 2026-09-17T10:04 / 着手便 msg_20260917_100022_ae3cd5d4(10:00:22・宣ETA 12 分・起点= 着手便 timestamp・端点= 納め最終便 timestamp)/ 凍結点 HEAD 6ba8fcb2 ―― 但し ★的の file は disk と HEAD で違ふ(`00`: disk sha16 15ac9f97f473245d 80724B ⇔ HEAD blob 00cd905d6eeb 77285B)★ ゆゑ ★主= disk・副= HEAD★ を表に併記する。
- 器: 讀むのみ。scripts/ ~/bin/ へ 0 字・箱へは家老便 1 通の既讀印と着手便 1 通のみ・watcher へ信号 0・send-keys 0。生は `raw/`(以下 `NN`)。臺帳= MANIFEST.txt・門控= _gate/(員外・名は走ごとに一意)・_after/ は臺帳の後。
- 家老札の行番号(L224/L1599/L173-175)は ★信ぜず己の器で引き直した★(`10`)。結果: 受 L224・比 L1599 は一致、守る表は ★L173-178★(札の L173-175 は `for` の頭三行のみ・`done` は L178)。HEAD では L212/L1540/L161-166。

## ㊀ 結語を先に

1. ★㋐ ASW_PROCESS_TIMEOUT は disk/HEAD とも「受ける口」1 行(L224/L212)+「比較器」1 行(L1599/L1540)+ 註 1 行(L222/L210)の 3 行に現れ、「守る表」(L173-178 の 10 名)には ★無い★(陽性対照 ESCALATE_PHASE1 は在る・陰性対照 ZZ_KM80_NEG は無い)。★
2. ★㋑ 其の名が立つ比較器は `[ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]` ―― 演算子 `=` の ★字面比較★ ゆゑ「數比較器が rc2 で if も elif も偽に落ちる」形の疵には ★非ず★。然し毒は別の道で効く: 0/1 の旗を守る番人が無いゆゑ、★空白/非数/巨大/先頭改行/域外の十進(2・01・+1)は悉く rc0・刷り 0 行で event-only(timeout 掃き無し)へ黙つて落ちる★(`30` H1・9/12 形)。★
3. ★㋒ 陽性対照(ESCALATE_PHASE1 へ fix_threshold)は 6 形の内 5 形を「倒した旨を刷つて」既定 120 へ倒し、陰性対照(正しい十進)は黙つて通る ―― 器は器として使へる。但し ★先頭改行付き十進「␊1」を fix_threshold が黙つて通す穴★ が新たに出た(H2・FT_RC 0・stderr 0 行)。★
4. ★㋓ 直し形は fix_threshold の呼出一行では ★足らぬ★。理由= 此の名は閾ではなく 0/1 の旗であり、fix_threshold は「-ge 0 で扱へる整数」を悉く通す ∴ 2・01・+1 は番人を黙つて抜け、比較器 `= "1"` で黙つて event-only に落ちる(H3 で實測)。要るのは ★旗の番人(0|1 以外は刷つて既定 1 へ倒す)★ の case 一段(㊄に紙で書く・据ゑて居らぬ)。★
5. ★㋔ 稼働中の watcher 3 本(pid 9826/9838/9859・起動 2026-09-10 20:07:54)が開く inode は 20564860/74274B で、disk の 22062559/80724B とも HEAD 系譜の何れの blob 寸法とも ★一致せぬ★。fix_threshold が的へ入つた commit ab2a1f1 は 09-17 05:57 ゆゑ、★稼働 3 本には守る表其の物が無い(0/10 名)★ と推せる ―― 之は起動刻と寸法からの推定であり、稼働 process の逐語は讀めぬ(`45`)。★

## ㊁ ㋐ 受ける口と守る表 ―― 別の二表(`10` / 10_ukeru.tsv・10_uke_mamoru.txt)

### 表A 受ける口(語 ASW_PROCESS_TIMEOUT を含む行 悉く)

| 版 | 行 | 分類 | 逐語 |
|---|---|---|---|
| disk | 222 | 註 | `# - ASW_PROCESS_TIMEOUT=0: do not process unread on timeout ticks (event-only)` |
| disk | ★224★ | 受(NAME=${NAME:-既定}) | `ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}` |
| disk | ★1599★ | 比較器([ ] の中) | `if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then` |
| HEAD | 210 / 212 / 1540 | 同上三形 | 逐語同一(行番号のみ −12 / −12 / −59) |

零の札: 陽性= 語 disk 3 行・HEAD 3 行 / 陰性= 語 ZZ_KM80_NEG 0 行 / 根= 的 file 一本(全行)/ 刻= `10` の頭。

### 表B 守る表(disk L173-178・逐語)

```
L173: for _t in ESCALATE_PHASE1:120 ESCALATE_PHASE2:240 ESCALATE_COOLDOWN:300 \
L174:           NUDGE_COOLDOWN_SEC:60 NUDGE_COOLDOWN_SEC_CODEX:300 NUDGE_COOLDOWN_SEC_CLAUDE:60 \
L175:           ASW_PHASE:2 APPROVAL_ALERT_COOLDOWN:300 MAX_TYPING_SKIP:5 INOTIFY_TIMEOUT:30; do
L176:   _n="${_t%%:*}"; _d="${_t##*:}"
L177:   fix_threshold "$_n" "$_d" "$_n"
L178: done
```

名 10 本(ESCALATE_PHASE1/2・ESCALATE_COOLDOWN・NUDGE_COOLDOWN_SEC/_CODEX/_CLAUDE・ASW_PHASE・APPROVAL_ALERT_COOLDOWN・MAX_TYPING_SKIP・INOTIFY_TIMEOUT)。★ASW_PROCESS_TIMEOUT 無し★・隣人 ASW_NO_IDLE_FULL_READ(L219・同形 `${:-1}`・km-77 ㋒B)も無し。HEAD は L161-166 で逐語同一。

- 補(disk): `NAME=${NAME:-既定}` の受口は 22 名、内 守る表に無い名 19(ASW_DISABLE_ESCALATION・ASW_NO_IDLE_FULL_READ・ASW_PROCESS_TIMEOUT・LAST_*_TS・READ_COUNT 等)。★其の大半は状態変数(既定 0・process 内で更新)であつて閾でも旗でもない★ ―― 「19 が守られて居らぬ」と読むな。旗(0/1・比較器に立つ)は ASW_PROCESS_TIMEOUT と ASW_NO_IDLE_FULL_READ の 2 名(km-77 の B と一致)。

## ㊂ ㋑ 其の名は比較器に立つか(`10` / 10_hikakuki.tsv)

| 版 | 行 | 左項 | 演算子 | 右項 | 種 |
|---|---|---|---|---|---|
| disk | 1599 | `"${ASW_PROCESS_TIMEOUT:-1}"` | `=` | `"1"` | ★字面比較★ |
| HEAD | 1540 | 同 | `=` | 同 | 字面比較 |

∴ 「字面比較ゆゑ(數比較器の)疵に非ず」―― `[ "abc" = "1" ]` は rc1 で正しく偽・rc2 は出ぬ(H1 の TEST_RC 列は悉く 0 か 1)。★然し「疵に非ず」は「毒が効かぬ」ではない★: 旗の域(0|1)を検める番人が無いゆゑ、域外は悉く黙つて「0 の枝」(event-only)へ落ちる。之は暴発でも氾濫でもなく ★沈黙の縮退★ ―― 未讀が次 event まで滞る(timeout tick で process_unread を呼ばぬ)。裁の語で言へば「宣どおり守らせる」の宣= 註 L222「0 なら event-only・既定 1」であり、★宣に無い値が宣の 0 と同じ枝を黙つて踏む★ のが本口の疵。

## ㊃ ㋒ 毒六形を實際に当てた(`30` / 30_doku.tsv・写し器= /bin/bash 3.2.57・的の逐語を錨で切り出し)

切り出し(行番号は器が引いた): 受 L224・比 L1599・_th_say L125・num_same_op L130・env_state L133-139・fix_threshold L144-166。的の `set` 行= L28 `set -euo pipefail`(函数内)・L1582 `set -e`。

### H1 現形(受 → 比較器) ―― 悉く rc0・stderr 0 行

| 形 | 値 | rc | BRANCH | TEST_RC | 倒れ先 |
|---|---|---|---|---|---|
| 未設定 | `<unset>` | 0 | timeout_process | 0 | 宣どおり(既定 1)・刷り無し |
| 空文字 | `<empty>` | 0 | timeout_process | 0 | 宣どおり(`${:-1}` が空を既定へ)・刷り無し |
| 空白(半角) | `<SP>` | 0 | event_only | 1 | ★黙つて縮退★ |
| 空白(全角 U+3000) | `<U+3000>` | 0 | event_only | 1 | ★黙つて縮退★ |
| 非数 | `abc` | 0 | event_only | 1 | ★黙つて縮退★ |
| 2^63超の十進 | `99999999999999999999` | 0 | event_only | 1 | ★黙つて縮退★ |
| 先頭に改行 | `␊1` | 0 | event_only | 1 | ★黙つて縮退★ |
| 陰性対照 1(既定) | `1` | 0 | timeout_process | 0 | 宣どおり |
| 陰性対照 0(註の off) | `0` | 0 | event_only | 1 | 宣どおり(off は正) |
| 域外 2 / 01 / +1 | | 0 | event_only | 1 | ★黙つて縮退★(3 形) |

出先: stdout= 写し器の BRANCH/TEST_RC/VALUE のみ・stderr= 0 行(12/12)。★rc は 12 形とも 0★ ―― 何方へ倒れたかは rc でも stderr でも見えず、枝の挙動でしか見えぬ。

### H2 陽性対照 ―― 守る表に在る名 ESCALATE_PHASE1 へ同じ毒(fix_threshold・既定 120)

| 形 | FT_RC | stderr | VALUE | 倒れ先 |
|---|---|---|---|---|
| 未設定 | 0 | 1 行「★閾 未設定 ―― 既定へ倒す(ESCALATE_PHASE1=120)／本 process の未設定の報せは★此の一度のみ★…」 | 120 | ★刷つて倒す★ |
| 空文字 / 空白(半角) / 空白(全角) | 0 | 1 行「が空文字／が空白のみ ―― 既定 120 へ倒す(fail-closed)」 | 120 | ★刷つて倒す★(3 形) |
| 非数 / 2^63超 | 0 | 1 行「を比較器が扱へぬ(「abc」／「9999…」) ―― 既定 120 へ倒す(fail-closed)」 | 120 | ★刷つて倒す★(2 形) |
| ★先頭に改行★ | 0 | ★0 行★ | `␊1` | ★黙つて通る(穴)★ |
| 陰性対照 1 / 0 / 2 / 01 / +1 | 0 | 0 行 | 其の儘 | 黙つて通る(數ゆゑ正) |

- ★穴(新規・本弾の外・別口)★: `[ "$v" -ge 0 ]` は先頭の空白類(改行含む)を読み飛ばすゆゑ、num_same_op が「␊1」を數と呼び、値は ★改行付きの儘★ 受け皿へ入る。數比較の道では 1 として働く(fail-open に非ず)が、其の値を log 行へ挟む器へは改行が渡る ―― 裁 seq323980⑵ の行注入の封じは「扱へぬ値」の枝(L157-165)にしか無い。同じ函数は共有器四本(裁 323062⑷)に写されて居るゆゑ穴も四本に在ると推せる(本弾では的一本しか測つて居らぬ)。

### H3 直し形の演示 ―― `fix_threshold ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT` を挟んでから比較器へ

| 形 | FT_RC | stderr | BRANCH | 倒れ先 |
|---|---|---|---|---|
| 未設定 / 空文字 / 空白×2 / 非数 / 2^63超 | 0 | 1 行(刷る) | timeout_process | ★刷つて既定 1 へ倒す= 宣どおり★(6 形) |
| 先頭に改行 | 0 | 0 行 | event_only | ★黙つて縮退★(番人を抜け比較器で落ちる) |
| 陰性対照 1 / 0 | 0 | 0 行 | timeout / event_only | 宣どおり |
| ★域外 2 / 01 / +1★ | 0 | ★0 行★ | event_only | ★黙つて縮退★(番人は「數」と呼び通す) |

∴ 一行で閉ぢるのは 12 形の内 6 形。★4 形(␊1・2・01・+1)は fix_threshold を黙つて抜ける★ ―― 閾の番人は旗の番人ではない。

## ㊄ ㋓ 守らせる直し形 ―― 紙にのみ書く(★据ゑて居らぬ★・repo へ 0 字)

兄弟器 scripts/redundancy/shogun_report_watcher.sh L63-69 の正本形は「fix_threshold の呼出一行」であるが、上の H3 のとほり ★此の名には足らぬ★。要るのは二段:

```bash
# ⑴ 守る表へ載せる(L175 の末尾へ一語・未設定/空/空白/非数/巨大を刷つて 1 へ倒す)
          ASW_PHASE:2 APPROVAL_ALERT_COOLDOWN:300 MAX_TYPING_SKIP:5 INOTIFY_TIMEOUT:30 ASW_PROCESS_TIMEOUT:1; do
# ⑵ 旗の番人(loop の直後・L178 の次)―― 0|1 の外は名指して刷り、既定 1 へ倒す(fail-closed)
case "$ASW_PROCESS_TIMEOUT" in 0|1) ;; *)
  _th_say "★旗 ASW_PROCESS_TIMEOUT が 0/1 の外(「${ASW_PROCESS_TIMEOUT//$'\n'/␊}」) ―― 既定 1 へ倒す(fail-closed)★"; ASW_PROCESS_TIMEOUT=1 ;;
esac
```

- ⑵だけでも 12 形悉く閉ぢる(case は字面ゆゑ ␊1・2・01・+1・空白・非数・巨大を皆 `*` で受ける)。⑴を併せる理由= 未設定/空文字を「異常の三形」と同じ道で名指して刷る(裁 322952 乙)為。⑴のみでは 4 形が抜ける(H3)。
- L224 `ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}` は ⑴⑵の後では ★重複★(値は既に定まる)。残しても害は無いが、乙(未設定/空文字を分ける)を先に倒してはならぬ(L172 註)ゆゑ ★L224 を ⑴⑵より先に置くな★ ―― 現に L224 は loop(L173-178)の ★後★ に在るので順は保たれる。
- L1599 の `${ASW_PROCESS_TIMEOUT:-1}` も同じく重複に成る(触らずとも可)。
- 隣人 ASW_NO_IDLE_FULL_READ(L219)は同形の旗ゆゑ同じ二段で閉ぢる(別弾)。
- ★負テスト両対照(据ゑる時)★: 陽性= 上の 12 形を H3 の写し器へ当て「刷り 1 行 ∧ BRANCH=timeout_process」を 10 形(0 を除く 11 形の内 ␊1・2・01・+1 を含む)で見る / 陰性= 1・0 で刷り 0 行。本束の `30_doku.py` の H3 に case 一段を足せば其の儘負テストに成る(束の中で当てた・repo へは書いて居らぬ)。
- 据ゑるのは裁の後・自枝 commit→push は代行を請ふ・稼働 3 本へは次 respawn で反映(裁 323062⑷)。

## ㊅ ㋔ 稼働中の watcher と repo の版(`45` / 45_inode.tsv・読取のみ・信号 0)

| pid | 起動 | fd | inode | bytes | pane |
|---|---|---|---|---|---|
| 9826 | 2026-09-10 20:07:54 | 255r | 20564860 | 74274 | ashigaru-mac-1 |
| 9838 | 同 | 255r | 20564860 | 74274 | ashigaru-mac-2 |
| 9859 | 同 | 255r | 20564860 | 74274 | ashigaru-mac-3 |

- disk: inode ★22062559★ / 80724B / mtime 09-17 08:25:48 / sha16 15ac9f97 ―― ★稼働と別 inode★(置換前の版を bash が fd 255 で読み続けて居る= 第74弾で踏んだ疵と同じ形)。
- HEAD 系譜(git log -- 的)の blob 寸法: ab2a1f1(09-17 05:57)77285 / 25e6ec9(08-03)73304 / 9a3ca57 70709 / …。★74274 に一致する blob は 0 本★ ∴ 稼働版は git 系譜の何れの commit とも一致せず、09-10 起動時の disk 状態(25e6ec9 の後・未 commit の手当を含む)と推せる。
- ∴ ★fix_threshold と守る表(ab2a1f1 で入つた)は稼働 3 本の中に無い★。「6file は閉ぢた」は disk の話であり、稼働 process では ★0/10 名★ が守られて居る。本弾の直し形も据ゑた後 respawn までは効かぬ。
- ps の語一致 4 行= 條(bash scripts/inbox_watcher.sh 起し)3 + 己の系譜 1(zsh -c … 逐語は `45`)。

## ㊆ 此の紙が意味せぬ事・疵

- 意味せぬ: 稼働 process の逐語(fd は他 process の物ゆゑ讀めず・寸法と起動刻からの推定)/ 共有器四本の H2 の穴(的一本のみ測つた)/ ASW_NO_IDLE_FULL_READ(数へたが毒は当てて居らぬ)/ 門の rc0 は形のみ。
- 疵①: 着手便の初稿 305 字 ―― 二器(len・wc -m)が一致して門が鳴り ★送らず★・詰めて 286 字で送出(`01_letter.txt.first`)。
- 疵②: `30` の初走は値 0(註の off)の event_only を「縮退」と札した ―― 宣どおりの off を疵に数へる誤り。札の語を直して再走(`.first` 三本を残す・數は一つも動いて居らぬ)。
- 疵③(束の外・手打ち): HEAD 系譜の blob 寸法を zsh の `$h:scripts/…` で引き ★`:s` 修飾に食はれた偽値(1943 等)★ を一度見た。python 経由(`45`)で引き直した。手打ちの命令行は session jsonl に残る。
- 疵④(束の外・手打ち): 前弾の束へ `cd` した儘の命令が二本 No such file で落ちた ―― 絶対 path で引き直した。
- ★疵⑤(門が捕へた)★: 50 の出目を `raw/50_run.stdout` `.err` へ shell の `>` で置いた ―― ★redirect は命令より先に 0byte を作る★ ゆゑ歩き器が之を臺帳へ載せ(bytes=0)、後から中身が入り、門 main が 條①(相違 1)+ 條④(0byte 1・EOF 複数 1)で落ちた(rc 1・門控 `_gate/mon_km80_20260917T100553.log`・倒れた走として残す・`_after/*.first`)。記憶に既に在る罠(「Redirect target exists before the command runs」)を己が踏んだ。処置= 50_run.* を `_after/` へ移し(員外)・臺帳を建て直し・門を再走。數は一つも動いて居らぬ。
- 宣⇔實: 納め便(`_after/62`)に書く(紙は門で凍る)。
