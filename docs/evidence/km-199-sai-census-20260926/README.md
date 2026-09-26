# km-199 再測 ―― 送った者が、己の送った便を取り戻す路の census（板 974529ef・2026-09-26・專任1 ashigaru-mac-1）

- 紙のみで、押していない（push 無し）。器は書き換えていない。板へ値を試していない。
- 本 census のための便は出していない。
  - raw/05 にある送出の記録は、別の弾（km-200）で本当に出した便を、出した時にそのまま写した物である。
  - 抽出子を確かめる親なしの行は、器の書式から組んだ試料で、便ではない（raw/41・raw/42）。
- 9/18 の旧束（`/Users/momizimac/wt/a1-km199/docs/evidence/km-199-onore-no-tayori-wo-kazoeru-michi-no-census-20260918/`）を今日の器で測り直した。
  - 読む器 karo_mac_read.py は 9/19 に変わっている。
  - 旧束の最短の路 sed に穴が見つかった（下の ㋓・㋔）。

## 器の版（15:14:25 に測った sha256 の頭16桁）

| 器 | sha16 | 役目 |
|---|---|---|
| ~/bin/sb | 2670b305a432e552 | `read` は karo_mac_read.py（ME=karo-mac）を呼び、`write` は agent_letter.py（役 karo-mac）を呼ぶ |
| ~/bin/karo_mac_read.py | 3564b65d44193493 | mtime は 9/19 で、9/18 の旧束より後 |
| ~/bin/agent_letter.py | 8118c84d07c9fdd5 | 送出行は L335-336 |
| ~/bin/km_send.sh | 51499c10445ce482 | `sb-karo-mac write letter` へ exec する |
| ~/bin/l1send | 6d25affb1f5065cd | ― |
| ~/bin/mac_send.py | 263b218718f60339 | ― |
| ~/bin/sb-ashigaru-mac-1 | 7c55ef880d099fda | ― |

## ㋐ 路の母數：7路

9/18 の6路に ⑦ pcid を足して7路とした。根拠は karo_mac_read.py の `read` の口を読んだこと：
- 便の胴を返す口は seq・seqs・sent・inbox・pcid の5つ。
- 残りの口（task_tracker・dev_qa 等）は便を返さない。
- 送った者の手元に残る物として、⑸ 送出器の stdout/stderr と ⑹ 箱 file を加えた。

| 番 | 路 | 呼び方 |
|---|---|---|
| ⑴ | seq | `~/bin/sb read seq <N>` |
| ⑵ | seqs | `~/bin/sb read seqs <lo-hi or a,b>` |
| ⑶ | sent | `~/bin/sb read sent <役>` |
| ⑷ | inbox | `~/bin/sb read inbox <N>` |
| ⑸ | 送出器の出目 | km_send.sh／agent_letter の stdout と stderr |
| ⑹ | 箱 file | `queue/inbox/<役>.yaml` の尾 |
| ⑦ | pcid | `~/bin/sb read pcid <id の頭8桁>`（9/18 には無かった路） |

実走の記録：
- raw/20_jissoku.py が ⑴⑵⑶⑷⑦ の17呼び出しを走らせた（15:15:35〜15:15:42）。17本とも rc=0。rc は subprocess から直に取り、管は通していない（`raw/20_calls/*.rc`）。
- ⑸ は raw/05_sender_out に写した実の送出記録で測った。
- ⑹ は raw/30_kazoe.py が箱を読んで測った。

## ㋑ 五欄の表（［実走］＝今日走らせて見た／［字面］＝器を読んだだけ／［未測］）

| 路 | ⒜ seq | ⒝ 胴が切れずに出るか | ⒞ context_data | ⒟ 並びと窓 | ⒠ 何で絞るか |
|---|---|---|---|---|---|
| ⑴ seq | 出る［実走］ | 出る。8/8 で宣した字数と返った字数の差は0［実走］ | 出る（parent_seq・sender・target 全部）［実走］ | 1件だけ［実走］ | seq 一つ |
| ⑵ seqs | 出る［実走］ | 出る。8/8 が一致し、content_len も一致［実走］ | 出ない。代わりに sender_agent と target_agent の欄を刷る［実走］ | asc・limit200［実走・字面 L224］ | 範囲か列挙 |
| ⑶ sent | 出る［実走］ | ★出ない★。111字で切られる（21/22・474/494・488/500）［実走］ | 出ない（刷るのは seq・created_at・requires_response・content だけ）［実走］ | ★asc・limit500★［実走］。iincho 宛は母數1589のうち1089が落ちた（9/18 は737）。★asc ゆえ落ちるのは新しい方★（尾が292455で止まる）［実走］ | sender=karo-mac かつ target=<役> かつ resolved_at が null［字面］ |
| ⑷ inbox | 出る［実走］ | 出る（0/200 が切られていない）［実走］ | 出ない［実走］ | desc。20 では2742のうち2722が落ち、200 では2542が落ちた［実走］ | topic か target が karo-mac［字面］。★karo-mac 宛の便しか出ない★（378725 は gunshi-mac 宛なので出なかった）［実走］ |
| ⑸ 送出器の出目 | 出る（`seq=N`）［実走］ | ★出ない★。stderr に字数（`胴=N字`）が出るだけ［実走］ | parent_seq だけ（親があるとき）［実走・字面 L335-336］ | 送った1件だけ | ― |
| ⑹ 箱 file | ★出ない★（`seq:` 欄が3箱とも0）［実走］ | 378724 の胴の頭40字は3箱とも0件［実走］ | 出ない［実走］ | append［memory の既知・今日は未測］ | ― |
| ⑦ pcid | 出る［実走］ | ★出ない★。121字で切られる（1/1・1/1）［実走］ | select には入っているが刷るのは target_agent だけ［実走・字面 L191］ | asc・limit20［字面 L191］ | id の頭8桁［実走］ |

## ㋒ F1〜F6 の胴の字数（宣＝家老の 9/18 の宣／返り＝今日の実走）

| seq | 宣 | ⑴seq | ⑵seqs（刷った字数/content_len） | ⑶sent | ⑷inbox200 | ⑦pcid |
|---|---|---|---|---|---|---|
| 334180 F1 | 230 | 230 | 230/230 | 無 | 無 | 未測 |
| 334181 F2 | 258 | 258 | 258/258 | 無 | 無 | 未測 |
| 334182 F3 | 122 | 122 | 122/122 | 無 | 無 | 未測 |
| 334183 F4 | 240 | 240 | 240/240 | 無 | 無 | 未測 |
| 334184 F5 | 237 | 237 | 237/237 | 無 | 無 | 未測 |
| 334185 F6 | 132 | 132 | 132/132 | 無 | 無 | 未測 |
| 378724（陽性対照・今日の己の便） | 283 | 283 | 283/283 | 在（111字で切れ） | 在（283） | 121/283 |
| 378725（同） | 248 | 248 | 248/248 | 在（111字で切れ） | 無 | 121/248 |

- 宣と返りの差：⑴ は 0/8、⑵ も 0/8 だった。
- F1〜F6 が ⑶ sent に無い理由は突き止めていない。考えられるのは次の2つで、どちらかは［未測］：
  - resolved_at が埋まって sent の絞り込みから外れた。
  - iincho 宛で、落ちた1089の中にある。
- 字数は行頭に錨を置いた regex で取った（`raw/30_kazoe.py` の RX）。「字数が一致する」は「中身が同じ」の証にはならない。胴そのものが正しいかは、⑴ で出した胴を読み返して確かめた（km200r6k.readback）。

## ★見つけた事（疑いと、その測り方）★

1. **km_send.sh で出した己の便は、DB に「karo-mac 発」と記録される**［実走］。
   - 378724 の context_data は `sender_agent: karo-mac` で、378725 も同じだった。
   - このため、己の便は ⑶ sent karo-mac／gunshi-mac と ⑷ inbox に★家老の便と区別できずに★混ざる。
   - 己の便だけを取り出す路は、seq の値を手に持っているときの ⑴⑵⑦ しか無い。
   - 器の身元の話であり、足軽の側では直さない（器を変えることになるので）。
2. **⑶ sent は asc・limit500 なので、在庫が500を超えると★新しい便から落ちる★**［実走］。
   - iincho 宛は1089が落ちた。gunshi-mac 宛は494/500 で、窓の縁に近い。
   - 9/18 に書いたとおり、sent 路は「今出した一通」を見る器ではない。
3. **疑い：9/18 の最短の路 sed（形C・全角「（」に錨を置く）は、親の無い送出行で空を返す**。→ ★確かめた［実走］★（下の ㋓）。

## ㋓ 抽出子の census（送出器の出目から seq を拾う形）

母數：
- glob は3つ：`/Users/momizimac/wt/*/docs/evidence/**/*.sent.txt`、`/Users/momizimac/multi-agent-shogun/docs/evidence/**/*.sent.txt`、`raw/05_sender_out/*.out`。
- 当たった file は316本。そのうち送出行（`★<役> へ送出した★ seq=`）を持つ物が★129本★、持たない物が187本だった（15:20:53・`raw/40_chuushutsu.out`）。
- 送出行を2行以上持つ file は0本。
- 129本の内訳は、親あり129・★親なし0★。つまり実物の中に親なしの行は1本も無い。
- そこで親なしの行は、器 L335-336 の f-string をそのまま使い、ctx に parent_seq を入れずに組んだ試料で測った（`raw/41`・`raw/42`）。試料は母數129に含めていない。

| 形 | 字面 | 親あり129本（正／parent を掴んだ／None） | 親なしの試料 |
|---|---|---|---|
| A | `grep -o 'seq=[0-9]*' \| tail -1` | 0／★129★／0 | 999001（正） |
| B | `(^\|[^_])seq=([0-9]+)` の最初 | 129／0／0 | 999001（正） |
| C（9/18 の最短の路） | `sed -n 's/.*へ送出した★ seq=\([0-9]*\)（.*/\1/p'` | 129／0／0 | ★空（None）★ |
| C2（新） | `sed -n 's/.*へ送出した★ seq=\([0-9][0-9]*\).*/\1/p'` | 129／0／0 | 999001（正） |
| D | 行頭が ★ の行の最初の `seq=` | 129／0／0 | 999001（正） |

- **排他性**（`raw/40_chuushutsu.out`）：
  - B・C・C2・D が正を掴む file の集合は、互いに全て重なる（どの組も ∩=129）。
  - A は129本の全てで parent_seq を掴み、正は0本。A と他の形の重なりは0。
- **陽性対照**（今日の実の便 raw/05 の km200s3・km200g）：
  - A は 378690（親）を返した。
  - B・C・C2・D は 378724 と 378725（正）を返した。
- **陰性対照**：送出行を持たない187本では、5形とも187本全てで None を返した。
- **BSD sed での実走**（`raw/42_sed_jissou.out`）：
  - 実の3行では、C も C2 も正を返した。
  - 親なしの行では、C は `[]`（空）で、C2 は `[999001]` だった。
- 親なしの便は出し得る：km_send.sh が `--parent-seq` を求めるのは、胴に seq を書いたときだけ（memory の既知・今日は未測）。このため C の穴は実害になり得る。
  - ただし実物129本には0本しか無い。「今まで落とした」とは言えない。

## ㋔ 何も落とさない最短の路（9/18 の C を C2 に直した）

```
out=$(~/bin/km_send.sh "$body" --to <役> --parent-seq <N>); rc=$?        # rc は $? で直に取る（管を通さない）
[ "$rc" -eq 0 ] || exit "$rc"
seq=$(printf '%s\n' "$out" | sed -n 's/.*へ送出した★ seq=\([0-9][0-9]*\).*/\1/p'); [ -n "$seq" ] || exit 2
~/bin/sb read seq "$seq"                                                  # ⑴：seq・切れていない胴・context_data・刻が全部出る
```

- 落とす物：無い。⑴ は ⒜〜⒞ を全て返し、8/8 で差0だった。
- C2 は親の有無に関わらず、「送出した★ seq=」の直後の数を拾う。
- ⑶ sent・⑷ inbox・⑦ pcid・⑹ 箱は、「今出した一通」を取り戻す路には使えない。胴が切れる、窓から落ちる、宛先で絞られる、seq を持たない、のいずれかに当たるため。

## 測っていない事（［未測］）

- sb-ashigaru-mac-1 など、他の身元で出した便が sent 路にどう出るか。今日の己の便は全て km_send.sh 経由（身元 karo-mac）で、他の身元では1便も出していない（「本番の便を新たに出すな」に従った）。
- l1send と mac_send.py の送出行の書式（出目）。走らせると本物の便を出し得るため、走らせていない。
- F1〜F6 が ⑶ sent に無い理由（resolved_at なのか窓なのか）。
- ⑹ 箱が append で回転するか（今日は測っていない）。
- ⑦ pcid の F1〜F6。

## 再現の手順（どれも読むだけ）

```
cd /Users/momizimac/wt/a1-km199b/docs/evidence/km-199-sai-census-20260926/raw
/usr/bin/python3 -B 20_jissoku.py > 20_jissoku.out 2> 20_jissoku.err; echo $? > 20_jissoku.rc   # ⑴⑵⑶⑷⑦ を実走（DB は SELECT だけ）
/usr/bin/python3 -B 30_kazoe.py > 30_kazoe.out 2> 30_kazoe.err; echo $? > 30_kazoe.rc
/usr/bin/python3 -B 40_chuushutsu.py > 40_chuushutsu.out 2> 40_chuushutsu.err; echo $? > 40_chuushutsu.rc
/usr/bin/python3 -B 41_oyanashi_shiryou.py > 41_oyanashi_shiryou.out 2> 41_oyanashi_shiryou.err; echo $? > 41_oyanashi_shiryou.rc
sh 42_sed_jissou.sh > 42_sed_jissou.out 2> 42_sed_jissou.err; echo $? > 42_sed_jissou.rc
```

- 今回の rc はどれも0（各 `*.rc`）。
- DB は動いているので、再走すると ⒟ の数（母數・落ち）は増える。
- 40 の母數も、束が増えれば増える（15:17:02 の1回目は127、15:20:53 の2回目は129。増えた2本は raw/05 の km200r6k と km200r6g）。
