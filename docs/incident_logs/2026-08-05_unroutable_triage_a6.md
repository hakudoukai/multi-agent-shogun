# _unroutable 三択判定 (足軽6号、2026-08-05・委員長殿発注)

★★台帳file(`queue/dead_letter/_unroutable/*.yaml`)は一切削除・編集していない(Read/grepのみ)。
足軽5号が閉じた3件には一切触れていない。別台帳も作らない(委員長殿=10件そのものが完全な記録)。
bats/影file/dd189/process/commit いずれも不触。★別fileのみで報告する(本file)★。

## ★受信機経路 (冒頭必須・将軍second殿令・2026-08-05T13:1x更新版)★

**【現在有効な唯一の記述】三段の状態**=
①局所経路=三段とも実証(12:52:11載・12:52:31受領、往復20秒)。
②受信機経路(code)=家老second殿が`poll.py:352`実読で「同一の`inbox_write.sh`を呼ぶ＝同一門」確認済。
③受信機経路(実便)=★委員長殿のベル無し試験便(seq140484・third_pc発・12:55:52送信)で実証済★=
`honbucho.yaml`に12:55:56着・`type: question`・**`read: True`**を当職も独立確認(下記④参照)。
残るは本部長ご本人によるBOX_OK確認のみ。増分0の測時=12:47:14→12:52:11(10件のまま)。

当職も本工区着手にあたり以下を独立に再確認した(2026-08-05T13:03:28+0900実測):
- `shim/hakudokai/hakudokai_secondpc_receiver_poll.py:108`= `"honbucho": "hermes-honbucho:0.0"`が
  `AGENT_PANES`(→`VALID_SECONDPC_TARGETS`)に実在。直上106-107行のコメントに
  「2026-08-03 委員長(canon guardian): 本部長を受信allowlistへ追加。未登録により委員長→本部長のDB配送が
  missing_or_invalid_target_agentで構造的に全通落ちしていた」と明記(=家老second殿の言う「二日前の同型事故」と一致)。
- `queue/pane_registry.yaml`にも`honbucho`(panes[].agent_id)が実在するが、file mtime=2026-08-05 12:41:25
  (家老second殿の「12:45追加」の申告とおおむね符合、数分の差は当職の探索範囲では追跡不能)。
- `scripts/inbox_write.sh:288-292`実読=canon宛先集合は`queue/pane_registry.yaml`(env上書き可)の
  `pane_registry.panes[].agent_id`。registryが読めぬ/壊れておる時はfail-closed(reject)。
∴ 家老second殿の根因説明(便は受信機側の名簿②を通り、送信側の名簿①で死ぬ)は当職の独立読解と一致する。

## 母集団 (10件、全件列挙・実測`ls`)

1. unroutable_20260805_113126_ed7db710 (target=test_agent)
2. unroutable_20260805_114016_d34362de (target=honbucho・**closed by a5**)
3. unroutable_20260805_114020_b242199a (target=hermes)
4. unroutable_20260805_114025_f4e77058 (target=hermes)
5. unroutable_20260805_114031_8954274f (target=hermes)
6. unroutable_20260805_115803_cc2fa167 (target=honbucho・**closed by a5**)
7. unroutable_20260805_120928_ddfdb0df (target=honbucho・**closed by a5**)
8. unroutable_20260805_122641_c48f2db5 (target=honbucho)
9. unroutable_20260805_122647_32aa9e13 (target=honbucho)
10. unroutable_20260805_123142_3fc9b08a (target=honbucho)

## ⒜ 第一者の証で判じ得る物 (判定・閉じてよい、4件)

### hermes宛3件 (#3,4,5・escalated 11:40:20/25/31)

**【SUPERSEDED 2026-08-05T13:1x・以下は当初の誤判定として保存のみ・現在無効】**
~~各file実読=`from: 将軍second`/`target: hermes`/`type: cross_pc_delivery`/
`reason: unroutable_target_and_unresolvable_from`、3件とも一致(実測済)。当職の独立確認=
`queue/pane_registry.yaml`grep→`hermes`という単独agent_idは0件、実在するのは`hermes-honbucho`/
`hermes-gunshi-second`という session名の接頭辞のみ。かつ将軍second殿ご自身の申告「hermesという
agent_idは当PCに存在いたし申さぬ」「hermesは貴職の宛先誤り、受け取り申した」を独立に読了、送り主
本人の証と一致。判定=「宛先誤り・要再送せず」(内容はpc_handshake seq140076経由で失われていないとされる)。~~

**【2026-08-05T13:1x訂正版・現在有効な唯一の記述】** 将軍second殿ご自身が実測の上で当初の申告を
取り下げられた(測時12:57:58、家老second殿も独立追認)。当職も同一fileを見直し独立確認=
`type: cross_pc_delivery`(★local `inbox_write`が生む型ではない★)/`from: 将軍second`(★agent_id形式
ではなく表示名=local発ならagent_idになる形と不一致★)/`content`先頭=`[SecondPC][high]
[将軍second→環境部長]`(★pc_handshakeの封筒形式そのもの★)/escalated_at=11:40:20/25/31が5秒間隔
(★人手の三連打ではなくretryの型★)——4点とも当職が直接file実読で再確認済。
∴ **判定=「既達(正路pc_handshake seq140076にて送信済)。落ちた因は受信機がcross-PC便を局所化した
事。再送不要」**。★本件は名簿の欠けではなく受信機の局所化判定に因る★——`hermes`=環境部長=MainPC
の役職ゆえSecondPCに箱が無いのは当然であり、★名簿へhermesを加えてはならない★(加えればMainPC宛の
便がSecondPCの箱に誤って溜まる)。当職の前回判定「宛先誤り」は誤りであった(家老second殿が未検証の
申告をそのまま中継した事が原因、当職の咎ではないと家老second殿が明言・当職もこれを了とする)。

### test_agent宛1件 (#1・escalated 11:31:26)

file実読=`content: compat-check`/`from: karo`/`target: test_agent`/`type: task_assigned`/
`reason: target_non_canon_from_canon_but_inbox_stale`。

★当職の検証範囲での限界を明記★=足軽2号ご本人の「四点一致(content/from/target/type)で己のbats実行由来」
という確定申告そのものの原文は、当職の探索範囲(本file・shogun-second/ashigaru2の現行inbox・
karo-second_pruned.yaml archive)では★逐語では発見できなかった★。然れどkaro-second_pruned.yaml内に
「target_agent=test_agentは実canonに無い事そのものが原因」「TC-FR-014等、target=test_agentで実registryへ
直接ヒットする類、当職含む複数agentが本日実施」という★複数agentによる同型bats実行由来説の裏付け★は
確認できた。当職はこれを★間接証拠として妥当★と判じ、家老second殿の申告(第一者証)を採用する。

**判定=「試験の副産物・要再送せず」**。★但し「足軽2号ご本人の四点一致確定」を当職自身が逐語確認して
いない事は母集団漏れとして自己申告する★(下記参照)。

## ⒝ 第三者の申告に依る物 (判ずるな・保留、6件・不触)

- honbucho宛3件 (#2,6,7)=足軽5号の下、`closed_at: 2026-08-05T12:36:25`/`closed_by: ashigaru5 (karo-second
  下命・委員長裁定に基づく)` が既に4key付記済。★当職は一切触れず、内容も本報告に転記しない(下命通り)★。
- honbucho宛3件 (#8,9,10・12:26:41/12:26:47/12:31:42、a5の下命より後に落ちた物)=委員長殿の
  「別経路既達」申告を当職は独立に検め得ておらず、家老second殿と同じhold(保留)に服させる。
  内容には目を通したが(target/type/reason確認のみ)、判定・close操作は一切行っていない。

## 【本工区で己が直した誤り】

初稿で「四点一致」確定の原文を発見できぬまま一旦「判定=試験の副産物」と書き切ろうとしたが、
間接証拠(karo-second_pruned.yaml内の複数箇所)のみで第一者証の原文そのものではない事に気づき、
上記の通り限界を明記する形へ書き直した(判定自体は変えず、根拠の強さの表現を訂正)。

【追加・提出後発覚】hermes宛3件の判定根拠(将軍second殿の「宛先誤り」申告)そのものが誤りであった
(ご本人が実測の上13:1x前後に取り下げ)。当職は家老second殿の中継をそのまま採用し、自ら`type`/
`from`/`content`の形式まで踏み込んで検めていなかった——「第一者の証」と分類しながら、実際には
「第一者の未検証の申告」を採用していた事になる。当職なりの教訓=★送り主本人の申告であっても、
file自体の形式的整合性(type/from形式/content封筒/送信間隔)を自分の目で検めるまでは「証」と呼ぶな★。
本file該当箇所はsupersedeマーカーで是正済(旧文言は取消線で保存、削除はしていない)。

## ★母集団漏れの自己申告★

1. test_agent 1件の「足軽2号本人の四点一致確定」原文を当職は逐語では見つけられていない
   (間接証拠のみ採用、上記参照)。
2. pc_handshake seq140076(hermes宛3件の内容が実際に失われていない事の裏付けとされるseq)自体の
   中身は当職は検めていない(将軍second殿ご本人の申告を採用したのみ)。
3. `queue/pane_registry.yaml`のhonbucho追加時刻(mtime実測12:41:25)と家老second殿申告(12:45)の
   数分の差の原因は追跡していない。

## ★対になる他工区★

家老second殿が同時に③④の別工区(BOX_OK読了証・専務READY等)を進めておられる旨、下命本文に記載あり
(msg_20260805_130040引用元のshogun-second.yaml:1036)。本工区との直接の重なりは見つからず。

## ★壊れる試験の件数★

該当なし。本工区はfile読取+分類報告のみ、削除・close操作・patch・実装を一切伴わない。

## ★健全例★

【2026-08-05T13:1x更新】hermes宛3件は当初「送り主本人が己の誤りを名乗り出た」証と読んだが、
これ自体が誤りであった(上記supersede参照)。★真の健全例★=将軍second殿がご自身の申告を実測し直し
自ら取り下げられた事、その物自体——第一者証は「本人が言った事」ではなく「本人が★実測して★言った事」
でなければ強い証にならぬ、という好対照(第三者伝聞のhonbucho宛6件との対比軸は変わらず有効)。

## 監査体制

★暫定二者制(軍師+Gemini)。Codex leg停止中(2026-07-21事案)★。

以上、_unroutable三択判定(委員長殿発注)への応答。母集団=10件全数確認、うち4件判定・6件保留(不触)。
測時=2026-08-05T13:03:28+0900。
