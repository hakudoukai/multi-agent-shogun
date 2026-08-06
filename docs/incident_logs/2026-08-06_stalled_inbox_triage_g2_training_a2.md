# 停滞便の仕分け（群㈡）— queue/inbox/training.yaml（6通・from=専務・type=cross_pc_delivery）

下命=家老second msg_20260806_203149_db892647（2026-08-06T20:31:49）。
読取のみ・票のみ。対象file自体は★一切変更していない★（`read`を立てず・移さず・消していない）。

測時=2026-08-06T20:38:43+09:00（`date -Iseconds`実行結果）。
git rev-parse HEAD=df6c966f935437200d8773eef3a5d4641a8223ed（実測）。

## 対象fileの実測

```
$ ls -la queue/inbox/training.yaml
-rw------- 1 hakudokai hakudokai 5290 Aug  4 18:08 queue/inbox/training.yaml

$ stat -c 'mtime=%y epoch=%Y' queue/inbox/training.yaml
mtime=2026-08-04 18:08:28.655406954 +0900 epoch=1785834508

$ wc -l queue/inbox/training.yaml
61 queue/inbox/training.yaml

$ sha256sum queue/inbox/training.yaml
856b6f11243f42ecf3452e8b44a39d855651f9a2e9bdd9607c4984305653d00d  queue/inbox/training.yaml

$ git check-ignore -q queue/inbox/training.yaml; echo exit=$?
exit=0

$ git status --short queue/inbox/training.yaml
（出力なし＝working treeとの差分なし。もっとも本fileはgitignore対象ゆえ元よりtrack対象外）
```

`yaml.safe_load`で全文構造化読了。messages配列＝★6件・悉く`read: false`★（対象6通の全数）。
測時（2026-08-06T20:35:14+09:00）における各通の齢＝50.45h〜50.56h（最古=[0]/[1] 18:01:47・
最新=[4]/[5] 18:08:28）。悉くfrom=専務・type=cross_pc_delivery・expires_at=null（TTL明記無し）。

## ③ 数の扱い（先出し）

令＝「6通」。実行の刻（2026-08-06T20:35:14+09:00）に`yaml.safe_load`で数え直した結果＝★6件・
令の数と一致・食い違い無し★。
測時＝2026-08-06T20:35:14+09:00／器＝`yaml.safe_load`の`messages`配列長＋各`read`フィールド／
範囲＝`queue/inbox/training.yaml`一file（下命指定範囲外は数えていない）。以上。

## 名簿確認（宛先の立ち位置）

```
$ /usr/bin/grep -n "training" queue/pane_registry.yaml
（0件、exit=1）

$ /usr/bin/grep -n "honbucho\|本部長" queue/pane_registry.yaml
182:  - tmux_target: hermes-honbucho:0.0
183:    agent_id: honbucho
184:    persona: honbucho
192:      /usr/bin/bash scripts/inbox_watcher.sh honbucho hermes-honbucho:0.0 codex)
193:      ②tmux pane 実在 (hermes-honbucho:0.0、@agent_id=honbucho、pane_current_command=doppler)
194:      ③queue/inbox/honbucho.yaml 実受信履歴 (24便・24既読・最終既読 2026-08-05T10:27:19、
（exit=0）

$ ls -la queue/inbox/honbucho.yaml
-rw------- 1 hakudokai hakudokai 148808 Aug  6 20:02 queue/inbox/honbucho.yaml
```

`training`（本文中の宛名「研修部長」）は`queue/pane_registry.yaml`に★存在しない★（0件）。
対して`honbucho`（本部長）は★registry記載あり・tmux pane実在・現行運用中の箱★
（honbucho.yamlは50件のmessages、shogun-second/karo-second/third_pc(委員長)との
実運用往復を当職自身が`yaml.safe_load`で読み確認済＝2026-08-06T16:12〜の直近やり取り含む）。
∴「研修部長ではなくSecondPCの本部長」という本便群内の訂正文言（下記[4][5]）は、
★registryという独立の物証と整合する★（当職が本文だけでなく名簿からも裏取りした）。

## 中身（全文読了・6通とも）

```yaml
[0] id=msg_20260804_180147_3a04ba01  ts=2026-08-04T18:01:47
    [専務→研修部長A] challenge=RESIMG-SUPABASE-FULLREAD-20260804-P1
    （Supabase予約・画像ソフト関連全記録の全文読了・重複読了回避ゲート付きの詳細指示。最長文）

[1] id=msg_20260804_180147_fac95d9b  ts=2026-08-04T18:01:47
    [専務→研修部長B] 同上・宛先違い（B）

[2] id=msg_20260804_180402_3627ed61  ts=2026-08-04T18:04:02
    [専務→研修部長A] 「Supabase正式指示 seq=138393を確認してください」短文・同一challenge

[3] id=msg_20260804_180403_62c0a40d  ts=2026-08-04T18:04:03
    [専務→研修部長B] 「Supabase正式指示 seq=138394を確認してください」短文・同一challenge（B）

[4] id=msg_20260804_180828_01315861  ts=2026-08-04T18:08:28
    [専務→研修部長A][宛先訂正・撤回] 「理事長から『研修部長ではなくSecondPCの本部長』と訂正。
    正式指示 seq=138393と短文通知は誤配送のため撤回済み。開始・継続しないでください。
    開始有無とartifact有無だけを同一parentへ返せ」challenge=…-P1-WITHDRAW

[5] id=msg_20260804_180828_2c05f257  ts=2026-08-04T18:08:28
    [専務→研修部長B][宛先訂正・撤回] 同上（B・seq=138394）
```

## 裏取り（他fileへの横断検索・己の手で実行）

```
$ /usr/bin/grep -rl "138393\|138394" queue/ docs/ config/ scripts/
queue/inbox/shogun-second.yaml   ← 家老second自身の先行報告(下記)
queue/inbox/training.yaml        ← 本file
queue/inbox/ashigaru2.yaml       ← 本下命(karo-secondが特記欄で引用)

$ /usr/bin/grep -rl "RESIMG-SUPABASE-FULLREAD" queue/ docs/ config/ scripts/
queue/inbox/training.yaml        ← 本file以外に無し

$ /usr/bin/grep -rl "NO_REREAD_ALREADY_COMPLETE" queue/ docs/ config/ scripts/
queue/inbox/training.yaml        ← 本file以外に無し（[0][1]が求めた応答markerの着信記録は他に無い）

$ /usr/bin/grep -l "RESIMG\|138393\|138394" queue/inbox/_archive/*.yaml
（0件、exit=1）← honbucho_pruned.yaml等の退避archiveにも本challengeの痕跡無し
```

`queue/inbox/shogun-second.yaml`の該当便＝karo-second自身の先行報告
（id=msg_20260806_194456_3268bfd0・ts=2026-08-06T19:44:56・宛先=将軍second）に、
「training 6通＝専務→研修部長A/B の理事長指示——而して末2通が[宛先訂正・撤回]＝
『理事長から「研修部長ではなくSecondPCの本部長」と訂正／seq=138393・138394は誤配送のため撤回済』
⇒死んでおったのは已に撤回された便∴実害無し」との記載を確認した
（当職が`yaml.safe_load`で当該file自体を開いて読んだ一次確認であり、
本下命本文の要約を鵜呑みにした二次引用ではない）。
★本票の[4][5]に関する認定は、当職が[4][5]原文を直接読んだ結果であり、
上記karo-second報告と内容が一致することを確認した、という位置づけである（引き写しではない）。★

## ①〜④ 各通の仕分け

### [0] msg_20260804_180147_3a04ba01（専務→研修部長A・P1詳細指示）

**⒜** 専務→研修部長A。challenge=RESIMG-SUPABASE-FULLREAD-20260804-P1。
Supabase上の予約・画像ソフト関連全記録の全文読了を求める詳細指示（既読ledger等の先行検索ゲート付き）。
刻＝2026-08-04T18:01:47。測時との差＝50.56h。

**⒝ なお要るか（★[2][3]ほど単純に断じられない★）**
時限（expires_at）の明記は無い。[4]は「正式指示 seq=138393と★短文通知★は誤配送のため撤回済み」
と述べるが、「短文通知」が本便[0]を指すかは★本文だけからは確定できない★。
理由＝本便[0]は6通中★最長★（詳細な多段ゲート指示）であり、「短文」と呼ぶには不自然。
一方[2]（同一宛先Aへの後続・seq=138393を名指す一文だけの便）の方が字面上「短文」に近い。
∴「短文通知」＝[2]自身を指す可能性の方が高いと当職は見るが、★断定はしない★
（[0]を指す可能性・あるいは本file外の第三の便を指す可能性も排除できない）。

**⒞ 判ずる権は誰に在るか**
★当職は「已に閉じられた物」と断じない★＝[4]の名指しが[0]まで及ぶか不確定なため。
権者＝研修部長A（実受信者・registry無のため実体不明）または専務（発信者・正誤の最終権）。
次段階で権者に「短文通知＝どの便を指すか」を明示的に問うべき、と当職は提案する（裁定はしない）。

**⒟ 己の手で為した事**
`python3`+`yaml.safe_load`でtraining.yaml全6通を構造化読了・[0][4]原文の文字数比較
（[0]=本文中で最も長い段落構成・[2]=一文のみ、を目視突合）・`queue/pane_registry.yaml`grep
（training/honbucho両方）・honbucho.yaml全50件のyaml.safe_load読了・repo横断grep4種（上記裏取り節）。

---

### [1] msg_20260804_180147_fac95d9b（専務→研修部長B・P1詳細指示）

**⒜〜⒟** [0]と同型・宛先違い（B、後続[3]がseq=138394、[5]が撤回対象）。
判断も同一＝★「短文通知」が[1]を指すか不確定・当職は「已に閉じられた物」と断じない★。
権者＝研修部長B または専務。

---

### [2] msg_20260804_180402_3627ed61（専務→研修部長A・seq=138393短文）

**⒜** 専務→研修部長A。「Supabase正式指示 seq=138393を確認してください」の一文。
刻＝2026-08-04T18:04:02。測時との差＝50.52h。同一challenge。

**⒝ なお要るか**
[4]が文字列一致で「正式指示 seq=138393…は誤配送のため撤回済み。開始・継続しないでください」
と★名指しで撤回★している。本便自体が"seq=138393"の文字列を含み、[4]が引用する
"正式指示 seq=138393"と一致することを当職が突合済み。∴★もう要らない（撤回済み）★。

**⒞ 判ずる権は誰に在るか**
★当職が「已に閉じられた物」として断じてよい範囲★＝発信者（専務）本人が同一population内
（[4]）で明示的に撤回を宣言しており、外部権者の追加判断を要さない。
下命の定める「試験の残骸」「已に閉じられた物」のうち後者に該当すると当職は判ずる。

**⒟ 己の手で為した事**
[2][4]両便の原文中の"138393"文字列を目視突合（完全一致）・上記repo横断grep（他箇所への
再配信・返信の痕跡が無いことを確認＝撤回後に別経路で再送された形跡は当職の検索範囲内では無し）。

---

### [3] msg_20260804_180403_62c0a40d（専務→研修部長B・seq=138394短文）

**⒜〜⒟** [2]と同型・宛先B（[5]が撤回）。同一の理由で★已に閉じられた物★と判ずる
（[3][5]間の"138394"文字列一致を目視突合済み）。

---

### [4] msg_20260804_180828_01315861（専務→研修部長A・宛先訂正撤回）

**⒜** 専務→研修部長A。「理事長から『研修部長ではなくSecondPCの本部長』と訂正。
正式指示 seq=138393と短文通知は誤配送のため撤回済み。全文読了を開始・継続しないでください。
既に開始していれば安全な位置で停止し、開始有無とartifact有無だけを同一parentへ返してください」。
刻＝2026-08-04T18:08:28。測時との差＝50.45h。challenge=…-P1-WITHDRAW。

**⒝ なお要るか（★本便自体は"報告要求"を含み、単純に死んでいない★）**
撤回の宣言自体は完結済みだが、本便は末尾で「開始有無とartifact有無を同一parentへ返せ」と
★別途の報告義務★を課している。当職が`queue/inbox/honbucho.yaml`（現行50件+今回全文読了分）・
`queue/inbox/_archive/honbucho_pruned.yaml`・`queue/inbox/shogun-second.yaml`・repo全体を
challenge id/seq番号でgrepした限り、★この報告が実際に返された痕跡は見つからなかった★
（0件、上記「裏取り」節）。∴★撤回そのものは已に閉じられたが、報告義務の充足有無は
当職には確認不能＝未決の可能性が残る★。

**⒞ 判ずる権は誰に在るか**
「撤回の事実」自体は当職が已に閉じられた物と見てよいが、「報告義務が果たされたか」は
権者＝研修部長A（実受信者）または専務（発信者・要求者）に属する。当職はここを断じない。

**⒟ 己の手で為した事**
honbucho.yaml全50件・shogun-second.yaml該当便・training.yaml・_archive配下を
challenge id/seq番号/"NO_REREAD"markerでgrep（4パターン、上記「裏取り」節に全結果記載）。

---

### [5] msg_20260804_180828_2c05f257（専務→研修部長B・宛先訂正撤回）

**⒜〜⒟** [4]と同型・宛先B（seq=138394）。同一の理由で★撤回自体は已に閉じられたが、
報告義務の充足有無は未確認★。権者＝研修部長B または専務。

## 母集団の自己申告

本群㈡で当職が実測したのは`queue/inbox/training.yaml`1file・計6通のみ。裏取りのため
`honbucho.yaml`・`shogun-second.yaml`・`_archive/*.yaml`・`docs/`・`config/`・`scripts/`を
横断grepしたが、これらは★引用元の裏取りに限定★しており、当該file自体の未読便を
新規に仕分けする行為はしていない（下命①が対象を training.yaml 6通に限定しているため）。
「零」「以上」を主張できるのはこの1fileの中に限る。

## この工区が新たに開ける穴

- [4][5]が求めた「開始有無とartifact有無の報告」が実際に本部長（訂正後の正しい宛先）から
  専務へ返されたか、当職の検索範囲（queue/・docs/・config/・scripts/、及びhonbucho.yamlの
  現行+pruned archive）では★確認できなかった★。次に読む者は、本部長本人 or 専務本人に
  直接確認するか、当職が検索していない経路（cross-PC bridge の別ログ、DB側のpc_handshake
  テーブル等）を当たられたし。当職はこの点を「未決」のまま残し、断定していない。
- 「短文通知」（[4][5]の文中語）が[0][1]・[2][3]のいずれを指すかは本文だけからは一意に
  定まらない。当職は[2][3]（一文形式）の方が字面上近いと見て[2][3]のみを「已に閉じられた物」
  と判じたが、[0][1]まで含めて撤回対象とする読み方も文言上は排除できない。この語義の確定は
  当職の権限外＝発信者（専務）または研修部長A/B（実受信者）に委ねる。
- `queue/inbox/honbucho.yaml`は現行50件中さらに`_archive/honbucho_pruned.yaml`（189KBの
  multi-document YAML）を持つが、当職は`safe_load_all`での全件走査までは行っていない
  （grep一発の文字列一致のみ）。`_archive`側の構造的な全件読了は本工区の範囲を超えるため
  未実施と明記する。

## 監査体制

暫定二者制（軍師second+Gemini）。Codex leg停止中（2026-07-21事案）。

以上、本群㈡（対象1file・6通）の仕分け票。新規探索・新規判定・新規工区の拡張は行っていない。
