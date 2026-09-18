# km-197 ―― 納鍵の「揃ひ」の census ―― 固定 ref を出す為に要る欄が何本欠けて居るか(紙のみ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `tsugi_no_tama_197_20260918T2110`(task_id km-197・家老mac 発・板外・8 桁は起票後に家老が焼く)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T21:20:40+0900 / 着手便 21:18(宣ETA 21:45)/ 測り 21:18:47〜21:19:21
- 枝 = `ashigaru-mac-1/km-197-noukagi-no-soroi-20260918`(origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から・己の樹 ~/wt/a1-km197)。押さず。
- ★帳は一字も書換へず★: 己の帳 `queue/tasks/ashigaru-mac-1.yaml` の写しを 21:18:47 に束へ取り(raw/10・sha256 8c5d78dc…)、悉く写しで数へた(測る物が動かぬ様に)。

## ㋐ 結語

1. ★母數(㋐・鍵で数へ・字面 grep でない)★: 全鍵 ★82★ / 塊(dict)★66★ / 塊でない鍵 ★16★(task_id・status・completed_at・kinshi 等 = 帳の頭の平場の欄・0 に丸めぬ)/ `status: done` の塊 = ★64★(母數)。他の status: assigned 1(km-197 自身)。
2. ★欄の揃ひ(㋑・18 欄・三値・各欄の和 = 64 悉く一致)★: 悉く「有」の done 鍵 = ★7 / 64★。固定 ref を引ける鍵(branch・tip・tree・oya 悉く有)= ★13 / 64★。欠けが多い欄(無): kansa_readback 55・tip/worktree 51・kansa_seq/kansa_parent_seq 50・tree/oya/bundle/sen_eta 49・pushed 48・branch 47・nou_bin 36・kotae 35・jitsu 33・board_task 32(+空 2)・completed_at 2。★空(None)は board_task の 2 のみ・他は空 0★(無と空を分けた)。
3. ★形と實在(㋒)★: tip 13・tree 15・oya 15 の内 40 桁 = tip 13 / tree 15 / oya 14・★非 40 桁 1★(km140_nou の oya「82f23b42… (origin/main・fetch 後)」= 40 桁の後に註が付く=形の疵・當席の物)。40 桁の 42 本は ★悉く git に在り★・型も期待通り(tip/oya = commit 27・tree = tree 15)・不在 0・測れぬ 0。対照: 陽性 origin/main = あり / 陰性 0×40 = ★不在(rc 1)★。★対照が器の疵を捕へた★: 初版は `cat-file -e <sha>^{commit}` で判じ、陰性対照が rc 128 = 「測れぬ」に落ちて「不在」に成らなかつた → peel 無しの `-e` で在/不在(rc 0/1)を判じ、在れば `-t` で型を読む二段に改めた(raw/20 初版・raw/25 取り直し)。
4. ★宣⇔實(㋓)★: sen_eta と jitsu を両方持つ鍵 = ★15 / 64★(母數)。差(実−宣・分・日付込み)= ★min −87 / median −38 / max −14★・早い 14 / 遅い 0 / 同 0・測れぬ 1(km170_nou の jitsu が刻でなく文「測り終へ 13:40:55・API 断…」= 形の疵・當席の物)。跨日は 0(悉く同日)。
5. 案は ㋔(紙のみ・帳は本弾で書換へず)。

## ㋑ 母數と欄(raw/10・20・21)

- 器 = python yaml.safe_load(写し)。塊でない 16 鍵の名: task_id・assigned_to・assigned_by・status・priority・bloom_level・issued_at・assigned_at・completed_at・evidence_bundle・saki_ni_shiraseru_koto・teki・toi・uketori_jouken・kinshi・tsuiho_20260917_1930_sai_327826(帳の頭の平場 = 家老の初期の書き方)。
- 18 欄の三値(raw/21_ran_sanchi.tsv):
  | 欄 | 有 | 空 | 無 | 和 |
  |---|---|---|---|---|
  | task_id / status | 64 | 0 | 0 | 64 |
  | completed_at | 62 | 0 | 2 | 64 |
  | branch | 17 | 0 | 47 | 64 |
  | tip | 13 | 0 | 51 | 64 |
  | tree | 15 | 0 | 49 | 64 |
  | oya | 15 | 0 | 49 | 64 |
  | worktree | 13 | 0 | 51 | 64 |
  | pushed | 16 | 0 | 48 | 64 |
  | kotae | 29 | 0 | 35 | 64 |
  | bundle | 15 | 0 | 49 | 64 |
  | nou_bin | 28 | 0 | 36 | 64 |
  | kansa_seq / kansa_parent_seq | 14 | 0 | 50 | 64 |
  | kansa_readback | 9 | 0 | 55 | 64 |
  | board_task | 30 | ★2★ | 32 | 64 |
  | sen_eta | 15 | 0 | 49 | 64 |
  | jitsu | 31 | 0 | 33 | 64 |
- 「無」が多い理由(判じ・数ではない): 64 の done の内 ★弾鍵(tsugi_no_tama_N・家老が書き當席が status を done にする)と納鍵(kmN_nou・當席が書く)が同じ母數に混ざる★。弾鍵には tip/tree 等を當席が書かぬ(納鍵に書く)ゆゑ「無」に立つ。納鍵だけを母數にした揃ひは本弾の命の外(数へた上で判じの註に置く・測れぬではない)。
- 18 欄悉く有 = 7(悉く 18:0x 以降の納鍵 km177〜km196 の内・kansa_readback 欄を置き始めた km-184 以降)。

## ㋒ 形と實在(raw/22・24・25)

- 40 桁の網 `^[0-9a-f]{40}$`。非 40 桁 1 = km140_nou の oya(40 桁 + 括弧の註)。
- 實在 = 二段(peel 無し `git cat-file -e <sha>` → rc 0 在 / 1 不在 / 其の他 測れぬ、在れば `-t` で型)。42 本 悉く在り・型一致(commit 27・tree 15)・不在 0・測れぬ 0。rc は管を通さず。
- 対照: 陽性 6bde7170(origin/main)= 在り(rc 0)/ 陰性 0×40 = 不在(rc 1)。★初版の `^{commit}` 付き判は陰性対照で rc 128 を返し「測れぬ」に落ちた = 対照が器の疵を捕へた(raw/20 の ㋒ 行は其の初版の出目・raw/25 が正)。

## ㋓ 宣⇔實(raw/23)

- 母數 15(両方持つ)。差は「実(jitsu の刻)− 宣(sen_eta の HH:MM を jitsu の日付に置く)」の分。宣 > 実で 12 時間を超えれば前日と読む(跨日の備え)= 該当 0。
- 出目: −87 〜 −14 分・中央 −38・★15 本の内 14 本が宣より早く・遅れ 0★。測れぬ 1(km170_nou の jitsu が文)。
- 意味せぬ事: 「早い」は宣が甘い(大きい)事を示すのみ(memory: 宣は實の 1.8〜6 倍に振れる)。今日の後半は 1 時間前後の宣に 20〜40 分の實で ★宣が 1.5〜2 倍★ の傾き。

## ㋔ 案(★紙のみ・帳は書換へず★)

1. 納鍵の型を一つに: 18 欄を悉く持つ(空なら null でなく「無し」と書く)。當席の疵 2 本(oya に註・jitsu に文)は「欄は一つの値」に直す(据ゑるのは次弾・本弾では触らず)。
2. 弾鍵と納鍵を別の母數で数へる器(家老の焼き器が読む時の型の別)。
3. 固定 ref の四点(branch・tip・tree・oya)を納鍵の必須に。今の 13/64。

## ㋕ 測れぬ物

- 板の側(板に行が在るか)は家老の測り。
- 写しは 21:18:47 の一刻。其の後に當席が km-196 補正で帳を書いた(hosei_196 done・km196 tip 改め)= 写しには入つて居らぬ(写しが凍つた刻を書く)。

## ㋖ 疵

⑴ 實在の判の初版が peel 付きで陰性対照に鳴らず(取り直し・raw/25)⑵ 己の納鍵に形の疵 2(km140 oya の註・km170 jitsu の文)。

## 宣⇔實

宣ETA 21:45。實 = 納め便の刻(紙の外・21:2x 見込み)。
