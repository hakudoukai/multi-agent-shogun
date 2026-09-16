# 第74弾 ―― 行注入の印「乙(␊)」を ★共有器 四本★ へ据ゑる

- 席: 家老mac(karo-mac) / 刻: 2026-09-17 08:20〜08:29 / 束: `docs/evidence/km-74-otsu-wo-kyouyuuki-yonhon-he-sueru-20260917/`
- 裁 seq323980⑵ 逐語: 「行注入の印=乙(␊)を採る。甲(0xB6)はUTF-8不正ゆえ捨て。曖昧性は★入力に␊が既在なら拒否(fail-closed)★で消せ」
- 裁 seq323062⑷ 逐語: 「20箇所6fileは共有器=repo source が正。貴席が枝で甲乙を当てよ(重い順 inbox_watcher→watchdog→health→warn)・各1形負テスト・稼働中watcherは触らず次respawnで反映・4PC配布は監督lot」
- 裁 seq323687⑴ 逐語: 「專任2 行注入の直し紙は据えてよい(可逆・★自席の器★・負テスト1形)」 ∴ 共有器は ★家老の lot★ であり、專任2 が止まつたのは正しい振舞ひである(當職の下命㋑が自らの的と矛盾して居た ―― 當職の疵)。

## 一 何が疵であつたか

四器 悉く ★一箇所★、env 由来の閾値を其の儘 log へ刷る行が在つた(逐語同一)。

```
_th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
```

`${_ft_v}` は env の値ゆゑ ★改行を含み得る★。含めば log に ★偽の行が一本生れる★(=行注入)。
「fail-closed で倒す」事自体は正しいが、其の報せ方が log の行構造を壊す。

## 二 横展開の母數 ―― ★4 で閉じた★

`grep -rln '_ft_v' scripts/ ~/bin/` = ★4 file★(出目は下記の四本のみ)。各 file 内の当該行は ★1 本★。
∴ 裁 323062⑷ の「20箇所6file」より狭い。彼の數は ★閾の番人(甲/乙)全体★ の母數であり、
本弾が閉じたのは其の内の ★行注入の口★ のみである。★残りの母數は當職が閉じて居らぬ★(未了として上げる)。

## 三 当てた形(四本 逐語同一)

```bash
  case "$_ft_v" in
    *␊*|*␍*|*␉*) _th_say "★閾 ${_ft_n} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${_ft_d} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
  esac
  _ft_vp="${_ft_v//$'\n'/␊}"; _ft_vp="${_ft_vp//$'\r'/␍}"; _ft_vp="${_ft_vp//$'\t'/␉}"
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
```

- 甲(`tr` で 0xB6 へ)を採らぬ理由=裁の逐語「UTF-8不正ゆえ捨て」。加へて `tr` は fork を生む。
- ★印の曖昧性★=値が元から `␊` を含めば注入と区別が付かぬ ∴ 裁の定め通り ★刷らずに倒す★。
- `inbox_watcher.sh` のみ `unset` 行が在るゆゑ `_ft_vp` を其処へ足した(他三本は `unset` 行を持たぬ形)。

## 四 前後 sha16(重い順・裁の順)

| 器 | 前 sha16 | 前 行 | 後 sha16 | 後 行 | `bash -n` |
|---|---|---:|---|---:|---|
| `scripts/inbox_watcher.sh` | `cac867f8b94d5be4` | 1659 | `15ac9f97f473245d` | 1666 | rc=0 |
| `scripts/watchdogs/enter_restart_common_watchdog.sh` | `b224557e96e54c8c` | 422 | `f92cd54e09736a4e` | 429 | rc=0 |
| `scripts/agent_health_check.sh` | `6493c1d72a1e3a39` | 481 | `7d11ba9f852ac759` | 488 | rc=0 |
| `scripts/checks/context_usage_warn.sh` | `897412b069d0a620` | 90 | `3010defd413a3479` | 100 | rc=0 |

前の実体は `_before/*.before` に在る(束内・sha は上表と一致)。
`context_usage_warn.sh` は +10 行 ―― 内 7 行が本直し、3 行は ★古びた註の直し★(下記七)。

## 五 負テスト ―― ★16 形(四器 × 四形)★ 悉く期待通り

器=`raw/40_futatesuto.sh`(常駐 loop を起さぬ為、閾函数の塊のみ抜いて source。境は毎回 grep で測り、行番号は焼かぬ)。
出目=`raw/41_futatesuto.out` / `raw/41_futatesuto.err`(★捕つた時 0 行★ ―― 後に器が「空である旨の1行」を置いた、下記九)。`BASH_VERSION=3.2.57(1)-release`。

| 形 | 値 | 期待 | 出目(四器 悉く) |
|---|---|---|---|
| 一 行注入 | `9x` + 改行 + `★閾 偽の行…★` | log 1 行・既定へ倒れる | ★刷つた log 行=1★・値=既定・rc=0 |
| 二 印既在 | `9x␊偽` | ★値を刷らず★ 既定へ | 「可視印(␊␍␉)を既に含む」1 行・値=既定・rc=0 |
| 三 陰性(正数) | `42` | ★黙る★・値は 42 | ★刷つた log 行=0★・値=42・rc=0 |
| 四 陰性(空文字) | `` | 「空文字」の1行(乙 322952 の既存枝) | 1 行・値=既定・rc=0 |

∴ ★12 形が 1 行・4 形が 0 行★。形三 が「直しが happy path を壊して居らぬ」証、形四 が「印の枝が既存の枝を食つて居らぬ」証である。

## 六 稼働中の器 ―― ★触つて居らぬ★(実測)

`raw/50_inode.txt`。置換は ★別 inode へ書いて `mv`★ で行つた(裁 323062⑷「稼働中watcherは触らず次respawnで反映」)。

- disk の `scripts/inbox_watcher.sh` = inode ★22062559★(置換後)
- 走つて居る三本(pid 9826/9838/9859 = 三席の watcher)は fd 255 で inode ★20564860★(74274B)を掴んだ儘
- ∴ ★走つて居る process は古い版を読み続けて居る★。新版は ★次の respawn★ で効く。

## 七 併せて直した事 ―― 古びた註

`context_usage_warn.sh` の註は「本器のみ据ゑ置き・★裁を請ふ★」と書いて在つたが、
裁 seq323895㋐ が既に「hook は黙る儘で据えよ」と下して居る。∴ 註を ★請ひ→定め★ へ改め、裁の逐語を置いた。

## 八 當職の疵(器の側) ―― 三件、控を残した

1. **`name==out` の時 sentinel が export を消した** ―― `fix_threshold "$_n" "$_d" "$_n"`(inbox_watcher の実形)では第1引数と第3引数が同名。
   當初の器は export の後に受け皿へ `未設定` を入れて居たゆゑ、★甲は注入値を一度も試して居らぬ★のに「通つた」と見えた。
   控=`raw/41_futatesuto_kizu.out`(甲が両形とも「未設定」を刷つて居る)。直し=sentinel を先、export を後。
2. **`=$n★` で行数が潰れた** ―― bash の変数名が隣の全角を吸ひ、`n★` を引いた。直し=`${n}`。
   此は memory に既載の疵(`reference_bash_var_name_absorbs_fullwidth_chars`)を ★再び踏んだ★ものである。
3. **系譜を測る器が ★二度 偽の零★ を出した** ―― 控=`raw/60_keiretsu.txt`。
   當初 `for r in $(git for-each-ref …)` と書き、zsh が語分割せぬ故 1 語で回つた(既載 `reference_zsh_parsing_traps` の再踏)。
   zsh 配列へ直しても尚 0 本ゆゑ、★陽性対照を添へて★三形で原因を引いた ―― 眞因は
   `"$r:scripts/inbox_watcher.sh"` の `:` を zsh が ★置換修飾★ と読み `:path` を食つて居た事であつた
   (∴ git は枝名のみを受け、commit を返した。`git rev-parse` が blob でなく commit sha を刷つたのが其の印)。
   直し=`"${r}:…"` と括る。直した器は ★当弾の前=1本(km-73 のみ)・陽性対照=6本★ を正しく引いた。
   ★教へ★: 0 本は ★器の疵の顔をして出る★ ∴ 零には必ず陽性対照を添へよ(既載 `feedback_a_zero_needs_four_tags_and_a_routed_control`)。

## 九 未了(次弾または上申)

- ★閾の番人の母數 20箇所6file★(裁 323062⑷)は閉じて居らぬ。本弾は ★行注入の口 4 箇所★ のみ。
- 4PC 配布は ★監督の lot★(裁 323062⑷)ゆゑ當席は commit までで止め、push は代行を請ふ。
- `raw/41_futatesuto*.err` は捕つた時 0byte であつた ∴ 器が「空である旨の1行」を置いた(裁 seq320669)。
- ★memory へ書くべき新知★: 「zsh は `"$var:..."` の `:` を置換修飾と読む ―― git の `<枝名:path>` を壊す」。
  当弾で二度踏んだ故、既載 `reference_zsh_parsing_traps` へ ★git を壊す形★ として一行加へる。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
