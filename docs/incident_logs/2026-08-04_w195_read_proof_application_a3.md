# W195 — 「読まれた証」設計 (W180) を 生きた一件へ 当てる (足軽3号、2026-08-04)

★★本工区はPhase B(改ざん防止hash-chain/監査ログ整備/確定ロック/修正履歴版管理/認証/SaMD等9語)に
主題として当たらぬ。当隊自身の運用機構(inbox/task YAML/compact復旧手順)の検証のみを扱い、
hakudokai-dev(製品repo)への実装・commit・push・stage・DB接続は一切行っていない。
実施=稼働直前(委員長解釈・理事長裁定待ち)。理事長のGOはなお有効。「委員長が撤回」とは書いていない★★。

★禁則遵守★= 実装/commit/push/stage 一切行っていない・裁定していない(足軽4号への良悪判定ではなく
「W180がこの申告を判別できるか」という設計自身への問いに限定)・他者の成果物を書き換えていない・
process不触・DB/他PC実査せず・足軽4号を咎める記述をしていない。
本file自体は`docs/incident_logs/`への新規作成であり、既存fileの書換ではない
(証=下記「断面」の`git status --short`参照)。

★対工区欄★= W180(`docs/incident_logs/2026-08-04_w180_read_proof_design_a3.md`、当職自身の前工区・
本工区の直接の前身)。W180で設計したStep A〜Dをそのまま用いる。★重なる内容は再掲せず参照のみ★
(Anti-Duplication)。

断面=2026-08-04T18:31:14+0900。base_commit=502cbfe(実測=HEAD一致・`git rev-parse HEAD`確認済)。
`git status --short --branch`実測=working tree clean(本repo追跡分)、
`docs/incident_logs/`配下は本fileを含め多数`?? <path>`(untracked)状態。hakudokai-devには一切触れていない。

---

## 母集団宣言 (先に導く)

★対象=「本日、compact_recovery_read の完了を自己申告した便」★。機械抽出コマンドと実測結果=

```
$ /usr/bin/grep -l "cite_line" queue/tasks/*.yaml
(0件・該当なし)

$ /usr/bin/grep -rlE "実読|sha一致|sha256.*一致|compact_recovery_read" queue/inbox/*.yaml
_dead_letter_second.yaml, ashigaru1.yaml, ashigaru2.yaml, ashigaru3.yaml, ashigaru4.yaml,
ashigaru5.yaml, ashigaru6.yaml, ashigaru7.yaml, gunshi-second.yaml, honbucho.yaml,
karo-second.yaml, maeda.yaml, senmu_codex_second.yaml, shogun-second.yaml (14件)
```

**本工区が扱う個票 = ashigaru4 の完了申告1件**(`msg_20260804_182127_7ec12c2e`、karo-second.yaml
315-324行、from=ashigaru4、timestamp=18:21:27)。他13ファイルは母集団の広さを示す文脈のみで、
個別の当否判定は本工区の対象外(W195発令が指定した個票はashigaru4の1件)。

**陽性対照(先に置く)**= ashigaru6のCLAUDE.md実読報告(karo-second.yaml 380行付近、内容=
「CLAUDE.md:382-389を実読し一致を確認=『今やるな=電子カルテ三原則の強制/確定ロック/修正履歴・版管理/
監査ログ整備/改ざん防止(hash-chain)…』」)。★これは本工区の直接母集団(compact_recovery_readの2件)
とは対象fileが異なる(CLAUDE.md 382-389・別の読了要求)が、「T3型=逐語事実引用」が本日の corpus に
実在する事の証として用いる★(参照のみ・当職の判定対象には含めない)。

---

## §1 Step A〜D を 実際に走らせた結果 (設計のままにせず一度当てた)

### Step A (発令時・cite_line 割当) — ★未実行と実測★

```
$ /usr/bin/grep -l "cite_line" queue/tasks/*.yaml
(0件)
```

ashigaru4.yaml の`compact_recovery_read.files`を実読(下記)しても`cite_line`は無い=

```
files:
- path: docs/incident_logs/2026-08-04_karo-second_day_ledger.md
  lines: 163
  sha256_16: 3b4534e6b9c7c567
- path: docs/incident_logs/2026-08-04_secondpc-day-state-snapshot.md
  lines: 113
  sha256_16: 2798c91eeb5d19a6
```

**∴ Step A は当職の設計を作った本日ですら、一度も実行されなかった(自分のlaneも含め8/8lane 0件)。**
これは足軽4号個人の不備ではなく、★karo-secondが dispatch 時にW180の手順を採用しなかった★という
運用側の欠落(設計はあるが誰も使わぬ=day_ledger §2「型④」そのもの)。

### Step B (実行時・割当行の逐語引用) — ★実行不能(前提欠如)★

割当行が存在しないため、Step Bの「該当行の逐語引用」を照合する対象が無い。ashigaru4の申告文は
代わりに「sha一致確認済」という★W172/W180のどちらにも定義していない別種の主張★を行っている。

### Step C (照合・機械grep) — ★代替実行を試みた★

設計通りのStep C(`sed -n '<N>p' file | grep -F "<引用>"`)は割当行が無く実行不能。代わりに
「ashigaru4が申告した数値そのものが事実として正しいか」だけは機械照合できたので実行した=

```
$ sha256sum docs/incident_logs/2026-08-04_karo-second_day_ledger.md \
             docs/incident_logs/2026-08-04_secondpc-day-state-snapshot.md \
  | awk '{print substr($1,1,16), $2}'
3b4534e6b9c7c567 docs/incident_logs/2026-08-04_karo-second_day_ledger.md
2798c91eeb5d19a6 docs/incident_logs/2026-08-04_secondpc-day-state-snapshot.md
```

**ファイル側の事実としては両shaとも一致(実測)。** しかし★この一致は「ashigaru4が実際にsha256sumを
実行した証」ではない★——両方の値は ashigaru4.yaml の`compact_recovery_read.files[].sha256_16`に
既に平文で書かれている値と同一であり、ashigaru4はファイルを一切開かずとも自分のtask YAMLから
そのままこの2値をコピーして「sha一致確認済」と書くことが可能である(実際にそうしたかは判定不能・
下記§3)。

### Step D (既出台帳への記帳) — ★本工区では見送り★

W180 §7-2で自ら指摘した通り、台帳自体が新たな「書かれるが読み返されぬ」資産になり得るため、
本工区の成果物(本file)に判定を記載するに留め、別途`w180_cite_ledger.md`のような新規fileは
★作らなかった★(deliverable_specが本file1点を指定しているため・scope超過回避)。
これは省略であり完了ではない——次にW180を使う者への引き継ぎ事項として§6に明記する。

---

## §2 判定 — ACCEPT / REJECT / 判定不能

### ★判定不能★

理由は独立に2つあり、いずれか一方だけでも判定不能に至る。

**理由(a) 前提欠如**: W180のStep B/Cは「karo-secondが発令時に割り当てた特定行の逐語引用」を
機械照合する設計であり、その割当(Step A)が本件では一度も行われていない。存在しない割当行との
一致・不一致を判定することはできない。

**理由(b) 主張の型がW180の射程外**: 「sha一致確認済」は当職の三段(T1名/T2path/T3事実引用)の
どれにも当てはまらない別種の主張であり、かつ§3で示す通り★申告文だけでは「ファイルを開いて
sha256sumを実行した」のか「task YAML内の既知の値を書き写した」のか区別できない★
(day_ledger §2 `acknowledged_at`と同型=印の有無が両方向とも無情報)。

**明記**: 判定不能は「ashigaru4が読んでいない」という意味ではない。★足軽4号は本日の全隊と同様に
compact_recovery_read欄をtask YAML内に持ち、実際に読んだ可能性は高い(この慣行はfleet全体で
広く守られている——当職自身も本工区着手前に同じ2fileを実際にReadツールで全文読了している)★。
本工区が測っているのは「ashigaru4の行動」ではなく「★W180という機構が、この種の申告を判別する力を
持つか★」であり、答えは「持たぬ」である。

---

## §3 §8で自ら挙げた欠陥は 現に起きたか

**当職がW180 §7-1/§8で予告した「行番号だけgrepで抜けば通過してしまう」は、★字義通りの形では
起きていない★(cite_lineが無いのでgrepで抜く対象行自体が存在しない)。**

**しかし★同種でより深刻な変異形が現に起きた★**:

| 予告した穴(§7-1) | 実際に起きた事 |
|---|---|
| 割当行を`sed -n '<N>p'`で抜き出し、fileを開かず引用文だけ複製する | ★fileを一切開く必要すら無かった★——sha256_16とlines数は発令元(karo-second)がtask YAML自身に平文で既に書いており、対象fileへのアクセスなしで「一致確認済」を主張できる |

**§7-1は「アクセスはしたが理解はしていない」を捉えられぬ、という穴だったが、実際に起きたのは
一段深い「アクセスの要否自体が消えている」という穴である。** これは当職の設計が想定していなかった
新種の型であり、W180 §7には追加項目が要る(§5参照)。

---

## §4 『sha一致確認』という新しい段を どこへ置くか

★発令書の見立て(「path より強いが 中身より弱い」)は直感的には妥当に見えるが、★当職はこれに
一部異を唱える★★(Critical Thinking Rule④=過剰批判の禁を踏まえ、代案を添えて述べる)。

**発令書の見立てを支持する論拠**: sha256を計算するには対象fileの全バイトに実際にアクセスせねば
ならず、path名を書き写すだけの主張より物理的操作を要する。file の存在・破損有無を確認する効果は
path単独の主張には無い。

**当職の異論**: ★sha256_16の期待値は、cite_line(§1のStep Aで割り当てる特定行の中身)と違い、
発令元のtask YAML自身に既に平文で書かれている公開情報である★。cite_lineの強さは「発令時点で
発令者・受令者いずれも値を知らぬ疑似乱数性」に由来する(W180 §2 Step A-2)。sha256_16にはこの
性質が無い——発令された瞬間から答えが公開されている。ゆえに「sha一致確認済」という申告文単体は、
以下の二通りのどちらから生じたかを申告文だけでは区別できぬ:
  (i) 実際に`sha256sum`をfileへ実行し、その出力を確認した(真の物理アクセス証)
  (ii) 自分のtask YAML内の`sha256_16`欄を単に書き写した(fileへのアクセス皆無)

**∴ 結論**: 「段を増やすか既存へ畳むか」という問いに対し、当職は★両方を条件付きで採る★——

- ★生の実行痕跡(コマンド出力そのもの)を伴わない自己申告文のみの場合★= 新しい段(T2.5)を
  立てず、★T2(path)と同じ評価力★として畳み込む。理由=検証者(karo-second)が申告文単体から
  (i)/(ii)を区別する機械的手段を持たぬため、path単独の主張と同水準の「自己申告・無検証」でしかない。
- ★生の実行痕跡(karo-second側が同一fileへ独立に`sha256sum`を実行し、申告値と突合した記録)が
  別途存在する場合★= T2とT3の間に新しい段(T2.5)として位置づけてよい。理由=この場合に限り
  「fileが現在この内容を保持している」という事実は機械的に担保されるため(ただし★誰がそれを
  計算したかは依然として証明できぬ★=fileへの物理アクセスの証明であって、申告者本人の行動の
  証明ではない、という限界は残る)。

**本件(ashigaru4の申告)は前者(生の実行痕跡なし)に該当する。∴ T2相当として扱う。**

---

## §5 母集団漏れの自己申告

- 本工区はashigaru4の1件のみを個票として扱った。karo-second.yaml以外の宛先(honbucho/maeda/
  senmu_codex_second等)に同種の申告が転送・複製されているかは確認していない(判定不能)。
- ashigaru1/5/6/7のcompact_recovery_read関連文言も広く検索したが(§母集団宣言参照)、
  各lane固有の完了申告文を1件ずつ精査する時間的余裕は無かった(ETA即返しの制約)。
  ★ashigaru6の1件(CLAUDE.md 382-389引用)のみ陽性対照として個別確認した。他は未精査★。

---

## §6 この工区が新たに開ける穴

1. ★§3で示した「アクセス要否自体が消える」穴は、W180のStep A設計そのものに手当てが要る★——
   Step A-4「`sha256_16`をtask YAMLへ書く」という記法自体が、本来「読了の証拠」を求める意図とは
   裏腹に「読まずに答えられる材料」を発令側が自ら配ってしまっている。★karo-second/将軍second
   自身がこの2fileのsha値を布告文へ書いた事(day_ledger断面の慣行)が、皮肉にも今回の判定不能を
   生んだ一因である★(咎ではなく構造の指摘)。
2. Step D(既出台帳)を本工区で見送ったことで、★次にW180/W195を引く者が「前回どう判定したか」を
   知る手段が無い★——本file自体が「書かれるが読み返されぬ」八件目候補になり得る。次回引く者は
   本fileをまず読むこと。
3. §4で示した「T2.5は生の実行痕跡の有無で評価が変わる」という条件分岐は、★karo-second側に
   独立検証(自らsha256sumを打つ)の実施義務を課さねば機能しない★——現状その義務は発令書に
   明記されていない。

---

## §7 健全例 (陽性対照・実測済)

- ashigaru6のCLAUDE.md 382-389実読報告は、★実際に`sed -n '386p' CLAUDE.md | grep -F`で
  逐語一致を機械確認できた★(本file §母集団宣言に実行結果あり)。「一次資料に無い言い回しでは
  再現できない特有の列挙(電子カルテ三原則の強制/確定ロック/修正履歴・版管理/監査ログ整備/
  改ざん防止(hash-chain)等9語の並び)」が申告文とfile内容の両方に一致しており、これはT3水準の
  「開いて見なければ書けない」引用の実例である。
- 当職自身が本工区着手前(compact_recovery_read gate)に2fileを実際にReadツールで全文読了した
  ことも、健全な実行例として記す(W180 §5と同型・再掲せず参照のみ)。

---

## §8 己の判定の弱点 (一節)

★当職は「判定不能」という第四値へ逃げたのではないか、という疑いに自ら答える★。

判定不能とREJECTの境界は、本来「ashigaru4が虚偽を述べた確度」で分けるべきだが、当職はそれを
測る手段(session transcript監査権限)を持たぬ。ゆえに「REJECTすべき所を判定不能で丸めた」
可能性を排除できぬ。★もし将来karo-secondがashigaru4の実行ログ(tool-call transcript)を独立に
確認できる経路を持てば、この判定は覆り得る★——本判定は「現在当職が持つ証拠の範囲内での」
判定不能であり、恒久的な無罪証明ではない。

---

参照した正本: `docs/incident_logs/2026-08-04_w180_read_proof_design_a3.md`(全文参照・再掲せず) /
`queue/tasks/ashigaru4.yaml`(latest_dispatch.compact_recovery_read節) /
`queue/inbox/karo-second.yaml:315-324`(ashigaru4申告文全文) /
`queue/inbox/karo-second.yaml`380行付近(ashigaru6 CLAUDE.md実読報告) /
`CLAUDE.md:382-389`(陽性対照として実行照合) / `queue/tasks/ashigaru3.yaml`(latest_dispatch節・W195発令本文)

成果物: 本file。ETA=本便を以て即時提出。軍師second殿への提出はkaro-second殿の合図待ち
(latest_dispatch.acceptance条項に従う)。
