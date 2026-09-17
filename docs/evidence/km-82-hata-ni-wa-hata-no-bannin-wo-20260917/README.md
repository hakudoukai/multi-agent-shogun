# 第82弾 ―― ★旗には旗の番人を★ (`scripts/inbox_watcher.sh` の `ASW_PROCESS_TIMEOUT` を宣どほり守らせる)

- 席: 家老mac (係長格・`multiagent-mac` %68)
- 件名: `km-82-hata-ni-wa-hata-no-bannin-wo-20260917`
- 據: 委員長裁 **seq324588** の順 **⑵**「`inbox_watcher.sh` の `ASW_PROCESS_TIMEOUT` を宣どおり守らせる」
- 則: 1弾=1file ／ 負テスト両対照 ／ 自枝 commit → push は代行を請ふ
- 枝: `karo-mac/km-82-hata-ni-wa-hata-no-bannin-wo-20260917`

## 一 ―― 裁の指す⑵ は何であつたか

器の中に ★宣★ が書かれて在る(控 L220-224 逐語):

```sh
# Optional safety toggles:
# - ASW_DISABLE_ESCALATION=1: disable phase2/phase3 escalation actions
# - ASW_PROCESS_TIMEOUT=0: do not process unread on timeout ticks (event-only)
ASW_DISABLE_ESCALATION=${ASW_DISABLE_ESCALATION:-0}
ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}
```

∴ 宣は二値である ―― **`0` ならば timeout tick で unread を処理せぬ(event-only)／既定 `1` ならば処理する**。
下流の比較器は **字面比較** で之を読む(今 L1633 逐語):

```sh
        if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then
```

★此処に穴が在る。★ `0|1` の外の値 ―― `2`・`01`・`+1`・`abc`・空白 ―― は字面比較で偽と成り、
**`0` と同じ枝(event-only)へ落ちる**。而も rc は 0、stderr は 0行 ∴ ★沈黙の縮退★ である。
未読は次の event が来る迄 待たされる。

## 二 ―― 前後の姿

| | 行 | sha16 | `bash -n` |
|---|---:|---|---|
| 控(`_before/inbox_watcher.sh.snapshot`) | 1666 | `15ac9f97f473245d` | (据ゑ前の写し) |
| 今(`scripts/inbox_watcher.sh`) | 1700 | `494c8c788d50d724` | rc=0 |

- 控⇔今: 相違 **36行**(右35/左1・純増34) ―― `raw/05_hikae_vs_ima.diff`
- main⇔控: 相違 **130行**(右121/左9・純増112) ―― `raw/06_main_vs_hikae.diff`

### 二之補 ―― ★commit を二本に分けた(断り)★

★「据ゑた」は「commit した」ではない。★ 前回 round(2026-09-16) の直しが作業樹に未commitで残つて居た。
前弾(km-81)では之を **文で断つた** が、文は器で測れぬ。**本弾は形で分けた**:

| commit | 何を運ぶか | 数 |
|---|---|---|
| **A** `1b9304262c6a98c433398b4da0d67c03a8466559` | ★本弾ではない★ 前round の未commit分(裁322952 甲乙・323062⑷ 横展開・323980⑵ 行注入の封じ・守る表10名) | 1 file・121+/9− |
| **B** (本 commit) | ★本弾(km-82)の分のみ★ `fix_flag` の新設と受ける口の差し替へ、及び本束 | 下記 |

之を器で検めた ―― `raw/71_oya_ga_hikae_ka.sh`(★本弾の commit の親の blob が控と一致するか★):

```
親(1b9304262c6a98c433398b4da0d67c03a8466559) blob=428bd79fa78e
控          blob=428bd79fa78e
今          blob=73cdfbc4a8df
親⇔控 の相違行=0 / 控⇔今 の相違行=36
★断り不要★ 親の blob = 控 ∴ 本弾の commit は ★本弾の分のみ★ を運ぶ
```

※ 前弾から持つて来た `raw/70_zen_commit_kenme.sh` は **main を基点に測る器**ゆゑ、
  commit を二本に割つた形は測れぬ(鳴り続ける)。∴ `71` を一本足した。

## 三 ―― 現形の穴(十二形・毒の実測)

`raw/12_run12.py` が 12形 × 2器形 = **24走**。器は束の中の写し(`raw/13_harness_{genkei,naoshi}.sh`)であり、
`process_unread` は `printf BRANCH=%s` の stub、rc は `inotifywait` の timeout を模して 2。

### 現形(控の受ける口)

| 形 | 値(可視印) | rc | BRANCH | 器の報せ行 | 外の声行 | 報せの頭 |
|---|---|---:|---|---:|---:|---|
| ①未設定 | (未設定) | 0 | timeout | 0 | 0 |  |
| ②空文字 | (空文字) | 0 | timeout | 0 | 0 |  |
| ③空白半 |   | 0 | ★無★ | 0 | 0 |  |
| ④空白全 | ␠全 | 0 | ★無★ | 0 | 0 |  |
| ⑤非数 | abc | 0 | ★無★ | 0 | 0 |  |
| ⑥20桁 | 99999999999999999999 | 0 | ★無★ | 0 | 0 |  |
| ⑦域外2 | 2 | 0 | ★無★ | 0 | 0 |  |
| ⑧域外01 | 01 | 0 | ★無★ | 0 | 0 |  |
| ⑨域外+1 | +1 | 0 | ★無★ | 0 | 0 |  |
| ⑩先頭改行 | ␊1 | 0 | ★無★ | 0 | 0 |  |
| ⑪正常1(宣) | 1 | 0 | timeout | 0 | 0 |  |
| ⑫正常0(宣) | 0 | 0 | ★無★ | 0 | 0 |  |

- **BRANCH 無 = 9形**(③④⑤⑥⑦⑧⑨⑩⑫)。其の内 **⑫ `0` は宣どほり** ∴ ★毒による黙りは 8形★。
- ★器の報せ 0行 / 外の声 0行 / rc は 12走悉く 0★ ―― 何処にも警めが出ぬ。
- ①②が timeout 枝へ行くのは、比較器自身の `${…:-1}` が既定へ倒すゆゑ(穴ではない)。

### 直し形(`fix_flag` を通した後)

| 形 | 値(可視印) | rc | BRANCH | 器の報せ行 | 外の声行 | 報せの頭 |
|---|---|---:|---|---:|---:|---|
| ①未設定 | (未設定) | 0 | timeout | 1 | 0 | [watcher] ★旗/閾 未設定 ―― 既定へ倒す(ASW_PROCESS_TIMEOUT=1) ／ 本 proce |
| ②空文字 | (空文字) | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT が空文字 ―― 既定 1 へ倒す(fail-close |
| ③空白半 |   | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT が空白のみ ―― 既定 1 へ倒す(fail-clos |
| ④空白全 | ␠全 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT が空白のみ ―― 既定 1 へ倒す(fail-clos |
| ⑤非数 | abc | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「abc」) ―― 既定 1 へ倒す |
| ⑥20桁 | 99999999999999999999 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「99999999999999999 |
| ⑦域外2 | 2 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「2」) ―― 既定 1 へ倒す(f |
| ⑧域外01 | 01 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「01」) ―― 既定 1 へ倒す( |
| ⑨域外+1 | +1 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「+1」) ―― 既定 1 へ倒す( |
| ⑩先頭改行 | ␊1 | 0 | timeout | 1 | 0 | [watcher] ★旗 ASW_PROCESS_TIMEOUT は 0|1 の外(「␊1」) ―― 既定 1 へ倒す( |
| ⑪正常1(宣) | 1 | 0 | timeout | 0 | 0 |  |
| ⑫正常0(宣) | 0 | 0 | ★無★ | 0 | 0 |  |

- ★報せ 10形★(①〜⑩)・縮退 1形(⑫=宣どほり)・⑪は正値ゆゑ黙つて通る。
- 外の声(interpreter の悲鳴)は **24走 悉く 0行** ―― 直しは新たな悲鳴を生んで居らぬ。

## 四 ―― 稼働中の器と disk は別物である

```
disk	inode=22062559	bytes=83319	sha16=494c8c788d50d724
pid=9826	起動=Thu Sep 10 20:07:54 2026 	開いて居る=20564860//Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh
pid=9838	起動=Thu Sep 10 20:07:54 2026 	開いて居る=20564860//Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh
pid=9859	起動=Thu Sep 10 20:07:54 2026 	開いて居る=20564860//Users/momizimac/multi-agent-shogun/scripts/inbox_watcher.sh
稼働本数=3
```

∴ ★repo を直した事は、走つて居る器が直つた事ではない★(裁 seq323062⑷「稼働中watcherは触らず次respawnで反映」に沿ふ)。
本弾の `fix_flag` は ★稼働中の3本には入つて居らぬ★。

## 五 ―― 直し形(据ゑた物の逐語)

### ⑴ 番人を一本足す(今 L175-197)

```sh
fix_flag(){
  _fg_n="$1"; _fg_d="$2"; _fg_o="$3"; _fg_s="$(env_state "$_fg_n")"; eval "_fg_v=\"\${$_fg_n-}\""
  case "$_fg_s" in
    unset)
      if [ "${_th_unset_told:-0}" -eq 0 ]; then
        _th_say "★旗/閾 未設定 ―― 既定へ倒す(${_fg_n}=${_fg_d}) ／ 本 process の未設定の報せは★此の一度のみ★(裁 seq323687⑵)★"
        _th_unset_told=1
      fi
      eval "$_fg_o=\$_fg_d"; return 0 ;;
    empty) _th_say "★旗 ${_fg_n} が空文字 ―― 既定 ${_fg_d} へ倒す(fail-closed)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
    blank) _th_say "★旗 ${_fg_n} が空白のみ ―― 既定 ${_fg_d} へ倒す(fail-closed)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
  esac
  case "$_fg_v" in
    0|1) eval "$_fg_o=\$_fg_v"; return 0 ;;
  esac
  # ★行注入の封じ(乙・裁 seq323980⑵)★ 印が既在なら値を刷らず倒す(fail-closed)
  case "$_fg_v" in
    *␊*|*␍*|*␉*) _th_say "★旗 ${_fg_n} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${_fg_d} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
  esac
  _fg_vp="${_fg_v//$'\n'/␊}"; _fg_vp="${_fg_vp//$'\r'/␍}"; _fg_vp="${_fg_vp//$'\t'/␉}"
  _th_say "★旗 ${_fg_n} は 0|1 の外(「${_fg_vp}」) ―― 既定 ${_fg_d} へ倒す(fail-closed)★"
  eval "$_fg_o=\$_fg_d"
}
```

### ⑵ 受ける口を番人へ替へる(今 L255-258)

```sh
# ★受ける口を番人へ替へる(裁 seq324588⑵)★ ―― `${NAME:-1}` は ★空文字を番人の前で呑む★ ゆゑ
#   口の儘では「在るが空」を分けられぬ。fix_flag は env_state(${+set})で先に分ける。
#   下流の比較器(`[ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]`)は ★一字も変へて居らぬ★。
fix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT
```

★`${VAR:-N}` は空文字を番人の前で呑む★ ゆゑ、口を残して後から守る事は出来ぬ。
口そのものを `fix_flag` の呼出へ ★差し替へた★。`env_state` が `${+set}` で 未設定/空文字/空白 を先に分ける。

### ⑶ 下流は一字も触れて居らぬ

`raw/10_slice.py` が 番人・受口・比較器 の三片を控と今の双方から抜き、sha16 を並べた:

| 片 | 控 | 今 |
|---|---:|---:|
| 番人 | 43行 | 74行 |
| 受ける口 | 1行 | 4行 |
| ★比較器★ | 7行 `09a13b50f6d5fb98` | 7行 ★`09a13b50f6d5fb98`(同一)★ |

∴ 比較器は **同 sha** ―― 下流の意味は動いて居らぬ。

## 六 ―― 両対照(negative / positive)

```
対照	器形	値	rc	BRANCH	器の報せ行	外の声行
陰性A(値1・宣どほり)	genkei	1	0	timeout	0	0
陰性A(値1・宣どほり)	naoshi	1	0	timeout	0	0
陰性B(値0・宣どほり)	genkei	0	0	無	0	0
陰性B(値0・宣どほり)	naoshi	0	0	無	0	0
★陽性(値2・毒)★	genkei	2	0	無	0	0
★陽性(値2・毒)★	naoshi	2	0	timeout	1	0

○ 陰性A 両形とも BRANCH=timeout・報せ0
○ 陰性B 両形とも BRANCH=無・報せ0(宣=event-only)
○ ★陽性 現形= BRANCH無・報せ0(黙つて縮退=害)★
○ ★陽性 直し形= BRANCH=timeout・報せ1(刷つて倒す)★
○ 対照の証: 同じ器が BRANCH=timeout を出せる(陰性A) ⇒ 「無」は器の死に非ず

判=通(○=5/5)
```

★対照の証★: 同じ器が陰性Aで `BRANCH=timeout` を出せる ∴ 陽性の「無」は ★器の死ではなく、器の判断★ である。

## 七 ―― 可逆性

- 直しは **追加のみ**(番人1本 23行)と **一行の差し替へ**(受ける口 → 呼出)である。
- 戻すには: `fix_flag` の23行を消し、L258 を `ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}` に戻せば控に一致する。
- 控は `_before/inbox_watcher.sh.snapshot`(1666行 `15ac9f97f473245d`)に在り、**byte 一致で復せる**。

## 八 ―― 實器は走らせて居らぬ

- 測つたのは ★束の中の写し★ である。稼働中の `inbox_watcher.sh`(pid 9826/9838/9859)は ★止めず・触れず・走らせず★。
- 因: 實器を走らせれば tmux 送鍵と箱書込が起き、三席の走行を乱す。∴ 「直し形が實環境で効いた」ことは ★本弾では測れて居らぬ★。
- 效くのは ★次の respawn★ である。respawn は Mac事業部長の任(裁 seq299502/299680)。

## 九 ―― 疵(隠さぬ)

1. `raw/71_oya_ga_hikae_ka.sh` の初走は ★判が反転した★ ―― `git -C <repo> hash-object <相対path>` が
   path を ★repo 根から★ 解くゆゑ 控/今 の blob が空に成り、空文字との比較が「断り要」を出した。
   同じ出目の中に真の信号(「親⇔控 の相違行=0」)が在つたのに、判だけが逆を指した。
   直し=控/今 は `-C` を付けず cwd 起点で測る。
2. 本弾の `fix_flag` は `ASW_PROCESS_TIMEOUT` ★一口のみ★ に当てた。同器の `ASW_DISABLE_ESCALATION`(L254)・
   `ASW_NO_IDLE_FULL_READ`(L250)も **旗** であり、番人は未だ立つて居らぬ(残り=下記十)。
3. 可視印(␊␍␉)は ★値が既に印を含む時★ 刷らずに倒す(fail-closed)が、
   ★印を含む値と、印へ変換された値を、報せの上で区別する術は無い★(裁 seq323980⑵ の曖昧性は残る)。
4. `_th_unset_told` を `fix_threshold` と ★共有★ して居る ∴ 閾の未設定が先に報せれば、旗の未設定は黙る。
   高頻度器の氾濫を避ける為の意図的な選択(裁 seq323687⑵ 乙′)であるが、★一度きり★ の範囲は「process 毎・器全体」である。

5. 照合器 `raw/60_kami_awase.py` の初走は ★己の註を比較器と誤つた★ ―― 「`ASW_PROCESS_TIMEOUT` を含み `= "1"` を含む行」
   で探した故、L257 に置いた ★己の註(比較器を引用した一行)★ が先に当たり、比較器の行番を 1633 でなく 257 と出した。
   直し=註の行(`#` 起し)を除く。★器は己の引用を除けねば、己を測つてしまふ。★
6. 同じ初走で ★比較器片の sha16 が食ひ違つた★ ―― `60` が己の定義(比較器の行から7行)で切り直した故である。
   `10_slice.py` は別の錨(`if [ "$rc" -eq 2 ]; then`)から切る ∴ 同じ「7行」でも別の片であつた。
   直し=`60` は切り直さず、`10_slice.py` が出した `raw/slice_*_hikaku.sh` を ★讀む★。
   ∴ 照合の結果: **母數37 / ○37 / ×0**(`raw/61_kami_awase.tsv`)。

7. `raw/20_doku12.tsv` の **FINAL 欄は値の改行で切れて居る** ―― ⑩先頭改行 の現形の欄は `[` の一字のみである。
   値の欄(可視印 `␊1`)は正しいが、FINAL 欄には可視印を当てて居らぬ ★器の抜け★ である。
   ★判に使ふ欄(rc・BRANCH・報せ行・外の声行)は影響を受けて居らぬ★ が、欄として不完全である事を宣する。
8. 束の text を `raw/90_kaki.py --naose` で門の形(行末空白無し・EOF改行一本・LF のみ)へ揃へた。∴
   ㋐ `raw/06_main_vs_hikae.diff` の ★空行を表す `> ` の行末空白が削がれた★ ―― `diff` を再走させれば
     其の一行は `> `(空白付)で出る ∴ ★本束の diff は再走の出目と byte 一致せぬ★(行の中身は同じ)。
   ㋑ `raw/20_doku12.tsv` の ★末尾の空欄が落ちた★(9欄→8欄の行が在る)。讀む側は欄を埋めて讀む事。
   ㋒ `_before/` は ★控ゆゑ触れて居らぬ★(`90_kaki.py` が守る)。

9. 門の初走が落ちた(控 `_gate/mon_km82_20260917T104132.{out,err,rc}` ―― ★落ちた走も残す★)。
   出目は「★file が無い: README.md _before/… raw/slice_naoshi_uke.sh★」の ★一行★ であり、
   因は ★zsh は括らぬ変数を語に分けぬ★ 事である ―― `$FILES` が ★25本ではなく一本の argv★ として渡り、
   其の長い一名の file を探して無いと言つた。條① は臺帳側の器ゆゑ通り、條②③④⑤ だけが落ちた。
   直し=`files=("${(@f)$(find …)}")` で配列に取り `"${files[@]}"` で渡す。
   ★「25本を渡した」と思ひ込んで居たが、器は「一本」と讀んで居た。★

## 十 ―― 残り

- 同器の旗 2口(`ASW_DISABLE_ESCALATION`・`ASW_NO_IDLE_FULL_READ`)へ旗の番人。
- 裁 seq324588 順⑶ = ★番人無し4file★(`pane_enter_watcher_supervisor.sh`・`lib/detect_stale.sh`・
  `watchdogs/enter_restart_commander_watchdog.sh`。`stop_hook_inbox.sh` は弾⑴で閉ぢた)。
  之は第83弾(專任2)へ ★讀取のみ★ で測らせて居る(口21・三分類【閾/旗/名】)。
- ★名(文字列)の番人★ は未設計 ―― pane target や topic の毒は閾でも旗でも守れぬ。

### 十之補 ―― 門の控の讀み方

- 門の出目は ★悉く stderr★ に出る(判定も `verify.py` の★行も)。`_gate/` の `.out` が空でも落ちて居らぬ。
- 臺帳は ★束内相対★(裁 seq322699) ∴ 門は `cd <束>` の上で `KM_GATE_MANIFEST_BASE=.` を付けねば 條① が悉く落ちる。
- 門控の名は ★毎走変へて居る★ ∴ 同名の上書きは無い。★刻の最も遅い一本が本判★ である。
- 臺帳の項數は ★此の紙には書かぬ★ ―― 紙自身が臺帳の中に在り、書けば己を数へる循環に成る。臺帳を讀め。

## 十一 ―― 再現手順

```sh
cd docs/evidence/km-82-hata-ni-wa-hata-no-bannin-wo-20260917
python3 -B raw/10_slice.py            # 三片の抜き出しと sha16
python3 -B raw/12_run12.py            # 12形×2器形=24走 → raw/20_doku12.tsv
python3 -B raw/50_taishou.py          # 両対照 → raw/21_taishou.txt
bash     raw/45_kadou.sh              # 稼働 inode → raw/22_kadou.txt
bash     raw/71_oya_ga_hikae_ka.sh ../../.. scripts/inbox_watcher.sh \
         _before/inbox_watcher.sh.snapshot 1b9304262c6a98c433398b4da0d67c03a8466559
python3 -B raw/60_kami_awase.py       # 紙⇔測り の照合
```

## 十二 ―― 此の紙が意味せぬ事

1. ★「稼働中の器が直つた」を意味せぬ。★ 稼働3本の inode は disk と違ふ(四)。
2. ★「實環境で効いた」を意味せぬ。★ 測つたのは束内の写しである(八)。
3. ★「旗の口が全て守られた」を意味せぬ。★ 一口のみである(九-2)。
4. ★「fix_threshold が誤りである」を意味せぬ。★ 閾には正しく効く。旗に効かぬだけである。
5. ★「commit A が本弾である」を意味せぬ。★ A は前round の未commit分であり、本弾は B のみ(二之補)。
6. ★「門 rc=0 が紙の正しさを示す」を意味せぬ。★ 門は臺帳と byte の整合を測るのみ。
